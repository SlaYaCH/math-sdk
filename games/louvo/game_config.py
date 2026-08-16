"""
Louvo - Math SDK game configuration.

Theme: parody dating-app slot ("Louvo"), mechanics inspired by Hacksaw Gaming's
"Duel at Dawn" (expanding wild reel + duel multiplier system).

IMPORTANT — please read before running:
This file is written to match the Config base class as documented at
https://stakeengine.github.io/math-sdk/ (field names: game_id, provider_number,
working_name, wincap, win_type, rtp, num_reels, num_rows, paytable,
include_padding, special_symbols, freespin_triggers, reels, bet_modes,
reels_path, basegame_type/freegame_type). This environment has no network
access, so this was written from the published docs rather than by running it
against the real src/ package. Once you `git clone` the official
StakeEngine/math-sdk repo and drop this games/louvo/ folder in, do a quick
diff against games/0_0_expwilds/game_config.py (closest official example —
it's the "expanding wild reel" sample game) and fix any field-name drift.

Symbol map
----------
W   Wild            - Louvo heart logo. Pays on 5-of-a-kind only.
S   Scatter          - "DATE" icon. Free spin trigger.
M   Expand-duel      - "MATCH" symbol (equivalent to Duel at Dawn's "VS").
                       Expands into a full wild reel + duel multiplier.
K   Expand-likes    - "SUPER LIKE" symbol.
                       Expands into a full wild reel + shoots 1-6 extra wilds.
H1..H6              - portrait symbols, best to weakest:
                       H1 Le R, H2 Inso, H3 Shanna, H4 Manu, H5 Indigo, H6 Coca Cherry
L1..L4              - basic symbols: L1 Verifie, L2 Message, L3 Flamme, L4 Coeur
"""

import os

from src.config.config import Config
from src.config.betmode import BetMode
from src.config.distributions import Distribution


class GameConfig(Config):
    def __init__(self):
        super().__init__()

        # --- identity -----------------------------------------------------
        self.game_id = "louvo"
        self.provider_number = 0  # TODO: set to your assigned Stake Engine provider number
        self.working_name = "Louvo"
        self.win_type = "lines"

        # --- math shell -----------------------------------------------------
        self.wincap = 15000.0   # same max-win multiplier as the reference game
        self.rtp = 0.965        # target RTP - tune with the optimizer once sims run
        self.construct_paths()  # sets self.reels_path and other engine-internal paths

        self.num_reels = 5
        self.num_rows = [5, 5, 5, 5, 5]  # 5x5 grid, like the reference game

        # --- paytable ---------------------------------------------------
        # (kind, symbol): payout as a multiplier of bet
        self.paytable = {
            (5, "W"): 20.0,

            (5, "H1"): 20.0, (4, "H1"): 10.0, (3, "H1"): 4.0,    # Le R
            (5, "H2"): 16.0, (4, "H2"): 8.0,  (3, "H2"): 2.0,    # Inso
            (5, "H3"): 12.0, (4, "H3"): 6.0,  (3, "H3"): 1.5,    # Shanna
            (5, "H4"): 8.0,  (4, "H4"): 4.0,  (3, "H4"): 1.0,    # Manu
            (5, "H5"): 6.0,  (4, "H5"): 3.0,  (3, "H5"): 0.7,    # Indigo
            (5, "H6"): 4.0,  (4, "H6"): 2.0,  (3, "H6"): 0.5,    # Coca Cherry

            (5, "L1"): 2.0, (4, "L1"): 1.0, (3, "L1"): 0.2,      # Verifie
            (5, "L2"): 2.0, (4, "L2"): 1.0, (3, "L2"): 0.2,      # Message
            (5, "L3"): 2.0, (4, "L3"): 1.0, (3, "L3"): 0.2,      # Flamme
            (5, "L4"): 2.0, (4, "L4"): 1.0, (3, "L4"): 0.2,      # Coeur
        }

        self.include_padding = True

        # --- special symbols ---------------------------------------------
        # NOTE: "multiplier" must be registered here for Symbol to accept it
        # (confirmed by a real AttributeError otherwise). "likes" is NOT
        # registered - Symbol rejected it even when registered, so that
        # value is tracked separately on self.pending_likes instead (see
        # game_override.py / game_calculations.py).
        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["M", "K", "W"],  # M/K carry it first, W after expansion
        }

        # --- free spin triggers -------------------------------------------
        # 3 scatters -> "Speed Dating" tier (10 FS) / 4+ scatters -> "After
        # Dark" tier (10 FS). Both start with 10 spins; which tier is active
        # is decided from the scatter count in gamestate.py, since the two
        # tiers use different reel-sets and different bonus logic.
        # Retrigger during the bonus only has two designed tiers: 2 extra
        # scatters = +2 spins, 3 extra = +4 spins - nothing beyond that is
        # defined, so 4+ stays capped at the same +4 as the top tier rather
        # than inventing an escalating +6/+8/etc.
        # NOTE: a single reel can show 2 "S" symbols within its 5-row
        # visible window (reel strips only have ~48-50 stops), so the total
        # scatter count across 5 reels can exceed 5 - both dicts cover up to
        # 10 defensively so a rare high count never crashes with a KeyError,
        # it just resolves as equivalent to the top designed tier.
        self.freespin_triggers = {
            self.basegame_type: {3: 10, **{n: 10 for n in range(4, 11)}},
            self.freegame_type: {2: 2, 3: 4, **{n: 4 for n in range(4, 11)}},
        }

        # --- paylines -------------------------------------------------------
        # 19 lines on the 5x5 grid (row index 0-4 per reel, top to bottom).
        # Custom layout provided by the user, replacing the earlier placeholder.
        self.paylines = {
            0: [0, 0, 0, 0, 0],
            1: [1, 1, 1, 1, 1],
            2: [2, 2, 2, 2, 2],
            3: [3, 3, 3, 3, 3],
            4: [4, 4, 4, 4, 4],
            5: [0, 1, 0, 1, 0],
            6: [1, 2, 1, 2, 1],
            7: [2, 3, 2, 3, 2],
            8: [3, 4, 3, 4, 3],
            9: [1, 0, 1, 0, 1],
            10: [2, 1, 2, 1, 2],
            11: [3, 2, 3, 2, 3],
            12: [4, 3, 4, 3, 4],
            13: [0, 1, 2, 3, 4],
            14: [1, 2, 3, 2, 1],
            15: [2, 3, 4, 3, 2],
            16: [4, 3, 2, 1, 0],
            17: [3, 2, 1, 2, 3],
            18: [2, 1, 0, 1, 2],
        }

        # --- reels ------------------------------------------------------------
        reels = {
            "BR0": "BR0.csv",   # basegame
            "FR0": "FR0.csv",   # Speed Dating freegame (3-scatter tier)
            "FR1": "FR1.csv",   # After Dark freegame (4-scatter tier) - no "M" here
        }
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        # padding_reels: symbols shown in the rows just above/below the visible
        # board (used for the reveal animation) - one per gametype. FR0 is used
        # for both freegame tiers here since padding is cosmetic only.
        self.padding_reels = {
            self.basegame_type: self.reels["BR0"],
            self.freegame_type: self.reels["FR0"],
        }

        # anticipation_triggers: how many scatters-minus-one before the reel
        # reveal gets a delay/anticipation hint (matches the official sample's
        # pattern: one less than the minimum trigger count).
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        # --- multiplier / like pools --------------------------------------
        # Indexed by a custom `self.tier` string maintained in gamestate.py
        # ("basegame" / "speed_dating" / "after_dark"), NOT by self.gametype,
        # since we need three distinct weightings, not just basegame/freegame.
        # Ladder values match the reference game: 2x-200x.
        self.duel_multiplier_values = {
            "basegame": {2: 1000, 3: 600, 4: 400, 5: 250, 6: 150, 7: 100, 8: 70,
                         9: 50, 10: 40, 15: 20, 20: 10, 25: 5, 50: 2, 75: 1,
                         100: 1, 200: 1},
            "speed_dating": {2: 700, 3: 500, 4: 400, 5: 300, 6: 220, 7: 160,
                              8: 120, 9: 90, 10: 70, 15: 40, 20: 22, 25: 12,
                              50: 6, 75: 3, 100: 2, 200: 1},
            "after_dark": {2: 400, 3: 400, 4: 380, 5: 320, 6: 260, 7: 200,
                            8: 160, 9: 130, 10: 100, 15: 60, 20: 35, 25: 20,
                            50: 10, 75: 5, 100: 3, 200: 2},
        }
        self.superlike_like_values = {
            "basegame": {1: 500, 2: 300, 3: 150, 4: 70, 5: 25, 6: 5},
            "speed_dating": {1: 400, 2: 300, 3: 180, 4: 90, 5: 40, 6: 10},
            "after_dark": {1: 250, 2: 280, 3: 220, 4: 150, 5: 70, 6: 30},
        }

        # --- Match Streak (DuelSpin-equivalent) sub-feature, After Dark only --
        # Guaranteed minimum MATCH ("M") symbols per streak unlock (1st..4th),
        # unlocked by landing a full 6-like SUPER LIKE during After Dark.
        self.match_streak_guarantees = {1: 2, 2: 3, 3: 4, 4: 5}
        self.match_streak_bonus_spins = 3   # extra spins awarded per unlock
        self.match_streak_max_unlocks = 4

        # --- bet modes --------------------------------------------------------
        # NOTE: bonus-buy costs below are placeholders. The correct cost is
        # (bonus mode RTP contribution / bonus mode hit probability) - only
        # the optimizer + real simulation data can tell you the right number.
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.0001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FR1": 3},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.10,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FR1": 1},
                            },
                            "scatter_triggers": {3: 20, 4: 10, 5: 2},
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 200, 1: 40, 2: 8},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.4995,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FR1": 1},
                            },
                            "scatter_triggers": {0: 200, 1: 40, 2: 8},
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus_speed_dating",
                cost=80.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 1},
                            "force_freegame": True,
                            "force_tier": "speed_dating",
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus_after_dark",
                cost=150.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR1": 1},
                            },
                            "scatter_triggers": {4: 1},
                            "force_freegame": True,
                            "force_tier": "after_dark",
                        },
                    ),
                ],
            ),
            # --- Match Boost: 5x higher chance of a natural bonus trigger,
            # not guaranteed - just plays like base with better odds. ---
            BetMode(
                name="match_boost",
                cost=3.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.0001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FR1": 3},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FR1": 1},
                            },
                            "scatter_triggers": {3: 15, 4: 8, 5: 2},
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.2,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 100, 1: 30, 2: 8},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.2995,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FR1": 1},
                            },
                            "scatter_triggers": {0: 100, 1: 30, 2: 8},
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            # --- Match Frenzy: every spin guarantees 2+ MATCH reels, stays
            # in base spins only (scatters stripped - can't trigger freegame,
            # matching the reference's "FS symbols cannot appear here"). ---
            BetMode(
                name="match_frenzy",
                cost=60.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.0001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": True,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.15,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.8495,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            # --- Like Storm: every spin guarantees 1+ SUPER LIKE with at
            # least 2 likes, stays in base spins only (scatters stripped). ---
            BetMode(
                name="like_storm",
                cost=60.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.0001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": True,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.15,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.8495,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]
