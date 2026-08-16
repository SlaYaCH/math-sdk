"""
Louvo - main simulation state.

Rewritten to match the exact pattern shown in the official
games/0_0_expwilds/gamestate.py sample (pasted by the user from their real
Codespace, running the current SDK) - notably:

  - GameState only needs to inherit GameStateOverride (which itself chains
    up through GameExecutables -> Executables -> ... -> GeneralGameState).
    GameCalculations is mixed in separately as a plain-methods mixin.
  - run_spin() takes (self, sim, simulation_seed=None) - the engine calls it
    with two positional args beyond self.
  - Lines.get_lines()/record_lines_wins()/emit_linewin_events() are called as
    Lines.<method>(self, ...) - NOT self.<method>() as the public docs implied.
  - draw_board(emit_event=False) first, mutate the board (our MATCH/SUPER
    LIKE expansion), THEN manually call reveal_event(self) - this is how the
    official sample reveals the *final* board instead of the pre-expansion one.
  - imprint_wins() is called once, after the `while self.repeat:` loop ends -
    not inside it (a bug in the previous draft, now fixed).
  - update_freespin_amount() is NOT called here - it's already called by the
    engine's own run_freespin_from_base() right before run_freespin() runs.
"""

from game_override import GameStateOverride
from src.calculations.lines import Lines
from src.events.events import reveal_event


class GameState(GameStateOverride):
    def run_spin(self, sim, simulation_seed=None) -> None:
        self.reset_seed(sim)
        self.repeat = True

        while self.repeat:
            self.reset_book()
            self.tier = "basegame"
            self.match_streak_unlocks = 0
            self.pending_match_streaks = []
            self.pending_likes = {}
            self.pending_duels = {}
            self.global_multiplier = 1

            self.draw_board(emit_event=False)

            # Match Frenzy / Like Storm: FeatureSpins-style bonus buys where
            # every spin guarantees a specific special symbol and scatters
            # never appear (so these never enter freegame).
            if self.betmode == "match_frenzy":
                self.in_match_streak = True  # bypass the max-1-MATCH cap
                self.force_match_frenzy_board()
            elif self.betmode == "like_storm":
                self.force_like_storm_board()

            self.expand_special_reels()
            self.in_match_streak = False
            reveal_event(self)

            self.win_data = Lines.get_lines(self.board, self.config, global_multiplier=self.global_multiplier)
            Lines.record_lines_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            Lines.emit_linewin_events(self)
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    # ------------------------------------------------------------------
    def run_freespin(self) -> None:
        self.reset_fs_spin()

        # Which tier are we in? Bonus-buy modes force it directly; a natural
        # trigger from the basegame decides it from the scatter count.
        if self.betmode == "bonus_after_dark":
            self.tier = "after_dark"
        elif self.betmode == "bonus_speed_dating":
            self.tier = "speed_dating"
        else:
            scatters_seen = self.count_special_symbols("scatter")
            self.tier = "after_dark" if scatters_seen >= 4 else "speed_dating"

        self.match_streak_unlocks = 0
        self.pending_match_streaks = []
        self.pending_likes = {}
        self.pending_duels = {}

        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()

            self.draw_board(emit_event=False)
            self.expand_special_reels()
            reveal_event(self)

            self.win_data = Lines.get_lines(self.board, self.config, global_multiplier=self.global_multiplier)
            Lines.record_lines_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            Lines.emit_linewin_events(self)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            # After Dark only: resolve any Match Streak (DuelSpin-equivalent)
            # unlocks right away, in sequence, before the next normal spin.
            if self.tier == "after_dark":
                while self.pending_match_streaks:
                    guarantee = self.pending_match_streaks.pop(0)
                    self.tot_fs += self.config.match_streak_bonus_spins

                    self.draw_board(emit_event=False)
                    self.in_match_streak = True
                    self.force_match_streak_board(guarantee)
                    self.expand_special_reels()
                    self.in_match_streak = False
                    reveal_event(self)

                    self.win_data = Lines.get_lines(self.board, self.config, global_multiplier=self.global_multiplier)
                    Lines.record_lines_wins(self)
                    self.win_manager.update_spinwin(self.win_data["totalWin"])
                    Lines.emit_linewin_events(self)

            self.win_manager.update_gametype_wins(self.gametype)

        self.end_freespin()
