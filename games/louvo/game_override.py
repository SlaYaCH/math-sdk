"""
Louvo - symbol-level overrides.

This is where a fresh "M" (MATCH) or "K" (SUPER LIKE) symbol gets its duel
multiplier / received-likes count attached, the moment it's created on the
board.

Confirmed against games/template/game_override.py: attributes are set with
plain assignment (symbol.multiplier = value), not assign_attribute(). Also
carries the template's default check_game_repeat() override, needed so
simulations actually re-roll until they match their assigned distribution's
win_criteria.

`self.tier` (see gamestate.py) is one of "basegame" / "speed_dating" /
"after_dark" and picks which multiplier ladder / like-count ladder to draw
from - this is a game-specific attribute we maintain ourselves, not part of
the base engine.
"""

import random

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    def assign_special_sym_function(self) -> None:
        """Called once when the GameState is created (see GeneralGameState)."""
        self.special_symbol_functions = {
            "M": [self.assign_match_duel],
            "K": [self.assign_superlike_likes],
        }

    def assign_match_duel(self, symbol) -> None:
        """
        MATCH symbol: two "duelists" are drawn (Boyfriend Material vs Red
        Flag), each with a random multiplier from the ladder. The higher
        value doesn't automatically win - the winner is picked with a fair
        coin flip, so either the bigger or the smaller value can end up as
        the multiplier applied to the reel.
        """
        tier = getattr(self, "tier", "basegame")
        ladder = self.config.duel_multiplier_values[tier]
        contender_a = get_random_outcome(ladder)
        contender_b = get_random_outcome(ladder)
        symbol.multiplier = contender_a if random.random() < 0.5 else contender_b

        # Frontend needs both duel values (not just the winner) to animate
        # the actual duel - Symbol only accepts a fixed attribute set (see
        # note below on pending_likes), so stash on self.pending_duels
        # (keyed by symbol id), same pattern as self.pending_likes.
        if not hasattr(self, "pending_duels"):
            self.pending_duels = {}
        self.pending_duels[id(symbol)] = (contender_a, contender_b)

    def assign_superlike_likes(self, symbol) -> None:
        """
        SUPER LIKE symbol: expands to a full wild reel AND fires `likes`
        (1-6) extra wilds onto the board. Also carries its own multiplier,
        same ladder as MATCH.

        NOTE: likes is kept on self.pending_likes (keyed by symbol id),
        not on the symbol itself - Symbol only accepts a fixed set of
        attribute names (name, wild, scatter, multiplier, prize...) no
        matter what config.special_symbols says, confirmed by a persistent
        AttributeError on 'likes' even after registering it there.
        """
        tier = getattr(self, "tier", "basegame")
        if not hasattr(self, "pending_likes"):
            self.pending_likes = {}
        self.pending_likes[id(symbol)] = get_random_outcome(
            self.config.superlike_like_values[tier]
        )
        # Banniere SUPER LIKE : ladder complet 2-200x, comme les duels
        # MATCH (regle Duel at Dawn).
        symbol.multiplier = get_random_outcome(self.config.duel_multiplier_values[tier])

    def check_game_repeat(self):
        """Default from games/template/game_override.py - re-roll a
        simulation until it matches its assigned distribution's win_criteria."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
