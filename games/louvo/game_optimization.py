"""
Louvo - optimization setup.

Tells the optimization algorithm how the 96.5% target RTP should be split
across each bet mode's criteria (win_criteria labels defined in
game_config.py's BetMode/Distribution objects), plus some search-tuning
parameters. Structure confirmed against games/0_0_expwilds/game_optimization.py
(pasted by the user from their real Codespace).

IMPORTANT - these RTP/hit-rate numbers are a first-pass design choice, not a
verified fact:
- "base" mode: 0.001 RTP from the (near-impossible) wincap, 0 from "0"
  (zero-win) outcomes, 0.62 from the freegame (both Speed Dating and After
  Dark triggers share this one bucket), and the remaining 0.344 from plain
  basegame line wins. That's a rough 64/36 split of RTP between freegame and
  basegame, which is typical for this style of high-volatility, expanding-
  wild game - but it's a starting point, not a measured fact.
- "bonus_speed_dating" / "bonus_after_dark": both are pure buy-bonus modes
  (100% forced freegame), so their entire target RTP comes from the single
  "freegame" criteria - hr="x" marks it as guaranteed/deterministic rather
  than a real hit-rate, matching the reference sample's own bonus mode.

Once real simulation results come back, expect to revisit these numbers -
that's the normal iterative part of balancing a slot, not a mistake to fix
now.

UPDATE: min_m2m/max_m2m (a volatility-shape constraint copied verbatim from
the reference sample) was too strict for Louvo's actual win distribution -
out of thousands of attempts, too few candidates satisfied it, and the Rust
optimizer's hardcoded "top 10" results list crashed trying to read past the
handful that qualified. Widened to 1-50 and raised num_show so there's a much
larger pool to draw a full top-10 from.

UPDATE 2: match_boost's freegame hr was set to 30 (~5x more frequent than
base's 150) while keeping the same ~93x average win per session (same
underlying reels) - that combination alone would need ~3.1 RTP just from
freegame, blowing the 96.5% budget. Raised hr to 80 (a more modest ~1.9x
boost) so the implied average win (rtp/hr ~ 40x) stays achievable. Genuinely
offering "5x more frequent, same average size" isn't sustainable without
either a separately-tuned (smaller-average) reel set for this mode or a much
less generous base mechanic - a real design tradeoff, not just a numbers tweak.
"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    ConstructFenceBias,
    verify_optimization_input,
)


class OptimizationSetup:
    """Handle all game mode optimization parameters."""

    def __init__(self, game_config):
        self.game_config = game_config
        wincaps = {}
        for bm in game_config.bet_modes:
            wincaps[bm.get_name()] = bm.get_wincap()

        # Shared search-tuning parameters (how hard/wide the optimizer
        # searches) - reused as-is from the official sample; these are about
        # the search algorithm itself, not Louvo-specific design choices.
        default_parameters = ConstructParameters(
            num_show=20000,
            num_per_fence=10000,
            min_m2m=0.1,
            max_m2m=200,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[50, 100, 200],
            test_weights=[0.3, 0.4, 0.3],
            score_type="rtp",
        ).return_dict()

        buybonus_parameters = ConstructParameters(
            num_show=20000,
            num_per_fence=10000,
            min_m2m=0.1,
            max_m2m=200,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[10, 20, 50],
            test_weights=[0.6, 0.2, 0.2],
            score_type="rtp",
        ).return_dict()

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.001, av_win=wincaps["base"], search_conditions=wincaps["base"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.62, hr=150, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.0, rtp=0.344).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.2,
                            "win_range": (1, 2),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.5,
                            "win_range": (10, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (3000, 6000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (9000, 12000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": default_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame", "freegame"],
                    bias_ranges=[(2.5, 5.5), (200.0, 500.0)],
                    bias_weights=[0.7, 0.2],
                ).return_dict(),
            },
            "bonus_speed_dating": {
                "conditions": {
                    "freegame": ConstructConditions(rtp=self.game_config.rtp, hr="x").return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.9,
                            "win_range": (20, 50),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (3000, 6000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (9000, 12000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": buybonus_parameters,
            },
            "bonus_after_dark": {
                "conditions": {
                    "freegame": ConstructConditions(rtp=self.game_config.rtp, hr="x").return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.9,
                            "win_range": (20, 50),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (3000, 6000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (9000, 12000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": buybonus_parameters,
            },
            "match_boost": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.001, av_win=wincaps["match_boost"], search_conditions=wincaps["match_boost"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.5, hr=80, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=2.0, rtp=0.464).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.2,
                            "win_range": (1, 2),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": default_parameters,
            },
            "match_frenzy": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.001, av_win=wincaps["match_frenzy"], search_conditions=wincaps["match_frenzy"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(hr=1.3, rtp=0.964).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": buybonus_parameters,
            },
            "like_storm": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.001, av_win=wincaps["like_storm"], search_conditions=wincaps["like_storm"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(hr=1.5, rtp=0.964).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": buybonus_parameters,
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
