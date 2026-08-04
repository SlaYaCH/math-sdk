"""
Louvo - custom board calculations.

Implements the two signature mechanics from the reference game:

- MATCH ("M"): expands to a full wild reel, carries a duel multiplier.
- SUPER LIKE ("K"): expands to a full wild reel, carries a multiplier AND
  fires extra wild symbols onto the board based on how many likes it received.

Plus the After-Dark-only "Match Streak" sub-feature (equivalent to the
reference game's "DuelSpins"): landing a SUPER LIKE with the maximum of 6
likes during the After Dark freegame queues a forced bonus spin with a
guaranteed number of MATCH symbols on the board.

UPDATE: expand_special_reels() now emits a dedicated "matchDuelReveal" /
"superlikeReveal" book event for each expanding reel, right before the M/K
symbol gets overwritten by the wild expansion - the frontend needs this,
since M/K never survive on the final board (confirmed: they get fully
replaced across the whole reel, so a board-scanning heuristic can't
distinguish "this came from MATCH" vs "this came from SUPER LIKE" vs "this
is just a naturally-drawn wild"). Also removed the old "max 1 MATCH per
spin" cap - the reference game only caps at 1 special symbol per REEL
(already guaranteed by the reel-strip design), not per spin, so multiple
MATCH duels can now resolve on the same spin.

Confirmed against the real SDK (games/template/ + live tracebacks):
- Symbol's real constructor takes a single argument, not (config, name) as
  the public docs showed - so new symbols are created via self.create_symbol
  (name), the same method the engine itself uses when drawing a board
  (confirmed by a traceback through create_board_reelstrips). This also
  means any special_symbol_functions callback registered for that symbol
  name (see game_override.py) fires automatically - no manual call needed.
- Attributes like .multiplier are set with plain assignment
  (symbol.multiplier = value), not through assign_attribute()/get_attribute().
- GameCalculations itself inherits Executables directly (matches
  games/template/game_calculations.py), with GameExecutables inheriting
  GameCalculations in turn - see game_executables.py.
- Custom book events follow the documented pattern:
  https://stakeengine.github.io/math-sdk/math_docs/gamestate_section/events_info/
  event = {"index": len(self.book.events), "type": "...", ...}
  self.book.add_event(event)
"""

import random

from src.executables.executables import Executables


class GameCalculations(Executables):
    # ------------------------------------------------------------------
    # Expansion pass: turns M / K symbols on the freshly-drawn board into
    # full wild reels, respecting the reference game's stacking rules:
    #   - max 1 special symbol per reel (guaranteed by reel-strip design)
    #   - max 2 SUPER LIKE per spin
    #   - MATCH and SUPER LIKE never resolve on the same spin
    # ------------------------------------------------------------------
    def expand_special_reels(self) -> None:
        match_hits = []       # [(reel_index, symbol)]
        superlike_hits = []   # [(reel_index, symbol)]

        for reel_index, column in enumerate(self.board):
            for symbol in column:
                if symbol.name == "M":
                    match_hits.append((reel_index, symbol))
                elif symbol.name == "K":
                    superlike_hits.append((reel_index, symbol))

        if match_hits and superlike_hits:
            match_hits = []  # SUPER LIKE takes priority; MATCH downgraded below

        superlike_hits = superlike_hits[:2]

        kept = {id(s) for _, s in match_hits + superlike_hits}
        for reel_index, column in enumerate(self.board):
            for row_index, symbol in enumerate(column):
                if symbol.name in ("M", "K") and id(symbol) not in kept:
                    self._replace_symbol(reel_index, row_index, random.choice(
                        ["L1", "L2", "L3", "L4"]))

        expanded_reels = []

        for reel_index, symbol in match_hits:
            multiplier = symbol.multiplier
            self.book.add_event({
                "index": len(self.book.events),
                "type": "matchDuelReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
            })
            self._expand_reel_to_wild(reel_index, multiplier)
            expanded_reels.append(reel_index)

        pending = getattr(self, "pending_likes", {})
        likes_preview = {id(sym): pending.get(id(sym), 0) for _, sym in superlike_hits}

        for reel_index, symbol in superlike_hits:
            multiplier = symbol.multiplier
            self.book.add_event({
                "index": len(self.book.events),
                "type": "superlikeReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
                "likes": likes_preview[id(symbol)],
            })
            self._expand_reel_to_wild(reel_index, multiplier)
            expanded_reels.append(reel_index)

        occupied = set()
        for reel_index in expanded_reels:
            for row_index in range(self.config.num_rows[reel_index]):
                occupied.add((reel_index, row_index))

        # Likes-received counts were stashed on self.pending_likes (keyed by
        # symbol id) when the SUPER LIKE symbol was created - see
        # game_override.py.
        superlike_likes = {id(sym): pending.pop(id(sym), 0) for _, sym in superlike_hits}

        for reel_index, symbol in superlike_hits:
            likes = superlike_likes[id(symbol)]
            multiplier = symbol.multiplier
            self._fire_likes(likes, multiplier, occupied)

        if getattr(self, "tier", "basegame") == "after_dark":
            for _, symbol in superlike_hits:
                if superlike_likes[id(symbol)] == 6:
                    self._queue_match_streak_unlock()

    def _expand_reel_to_wild(self, reel_index: int, multiplier) -> None:
        for row_index in range(self.config.num_rows[reel_index]):
            self._replace_symbol(reel_index, row_index, "W", multiplier=multiplier)

    def _fire_likes(self, likes: int, multiplier, occupied: set) -> None:
        candidates = [
            (r, row)
            for r in range(self.config.num_reels)
            for row in range(self.config.num_rows[r])
            if (r, row) not in occupied
        ]
        random.shuffle(candidates)
        for reel_index, row_index in candidates[:likes]:
            self._replace_symbol(reel_index, row_index, "W", multiplier=multiplier)
            occupied.add((reel_index, row_index))

    def _replace_symbol(self, reel_index: int, row_index: int, name: str, multiplier=None) -> None:
        new_symbol = self.create_symbol(name)
        if multiplier is not None:
            new_symbol.multiplier = multiplier
        self.board[reel_index][row_index] = new_symbol

    # ------------------------------------------------------------------
    # Match Streak (DuelSpin-equivalent), After Dark tier only.
    # ------------------------------------------------------------------
    def _queue_match_streak_unlock(self) -> None:
        if not hasattr(self, "match_streak_unlocks"):
            self.match_streak_unlocks = 0
        if not hasattr(self, "pending_match_streaks"):
            self.pending_match_streaks = []

        if self.match_streak_unlocks >= self.config.match_streak_max_unlocks:
            return
        self.match_streak_unlocks += 1
        guarantee = self.config.match_streak_guarantees[self.match_streak_unlocks]
        self.pending_match_streaks.append(guarantee)

    def force_match_streak_board(self, guarantee_count: int) -> None:
        """
        Overwrite the current board so that `guarantee_count` MATCH symbols
        appear, one per reel (max 5, matching the reference game's 4th-tier
        guarantee of 5/5 reels). self.create_symbol("M") already triggers
        assign_match_duel automatically (it's registered in
        special_symbol_functions), so no follow-up call is needed here.
        Caller is expected to run expand_special_reels() right after this
        so these actually expand into wild reels (each with its own
        matchDuelReveal event now).
        """
        reel_indices = list(range(self.config.num_reels))
        random.shuffle(reel_indices)
        chosen_reels = reel_indices[:min(guarantee_count, self.config.num_reels)]
        for reel_index in chosen_reels:
            row_index = random.randrange(self.config.num_rows[reel_index])
            self._replace_symbol(reel_index, row_index, "M")

    # ------------------------------------------------------------------
    # Match Frenzy / Like Storm (FeatureSpins-style bonus buys): every spin
    # in these modes guarantees a specific special symbol, and scatters must
    # never appear (these modes stay in base spins only).
    # ------------------------------------------------------------------
    def strip_scatters(self) -> None:
        """Replace any naturally-drawn scatter with a random low symbol -
        used in FeatureSpins modes where the free-spin trigger must not
        appear at all."""
        for reel_index, column in enumerate(self.board):
            for row_index, symbol in enumerate(column):
                if symbol.name == "S":
                    self._replace_symbol(reel_index, row_index, random.choice(
                        ["L1", "L2", "L3", "L4"]))

    def force_match_frenzy_board(self) -> None:
        """Match Frenzy: guarantee at least 2 MATCH symbols this spin."""
        self.strip_scatters()
        reel_indices = list(range(self.config.num_reels))
        random.shuffle(reel_indices)
        for reel_index in reel_indices[:2]:
            row_index = random.randrange(self.config.num_rows[reel_index])
            self._replace_symbol(reel_index, row_index, "M")

    def force_like_storm_board(self) -> None:
        """Like Storm: guarantee 1 SUPER LIKE symbol with at least 2 likes."""
        self.strip_scatters()
        reel_index = random.randrange(self.config.num_reels)
        row_index = random.randrange(self.config.num_rows[reel_index])
        self._replace_symbol(reel_index, row_index, "K")
        new_symbol = self.board[reel_index][row_index]
        if not hasattr(self, "pending_likes"):
            self.pending_likes = {}
        # override whatever assign_superlike_likes drew - this mode
        # guarantees at least 2, regardless of the normal random outcome.
        self.pending_likes[id(new_symbol)] = random.choice([2, 3, 4, 5, 6])
