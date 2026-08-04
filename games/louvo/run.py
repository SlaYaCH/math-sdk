"""
Louvo - simulation runner.

Wired to match games/0_0_expwilds/run.py exactly (pasted by the user from
their real Codespace): create_books() runs every simulation, generate_configs()
writes the frontend/backend/optimization config JSON, OptimizationExecution
tunes reel weights to hit the RTP targets defined in game_optimization.py,
create_stat_sheet() produces the PAR-sheet analysis, and execute_all_tests()
runs the RGS format verification checks.
"""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 1
    rust_threads = 1
    batching_size = 500
    compression = True
    profiling = False

    num_sim_args = {
        "base": 20000,
        "bonus_speed_dating": 3000,
        "bonus_after_dark": 3000,
        "match_boost": 5000,
        "match_frenzy": 3000,
        "like_storm": 3000,
    }

    run_conditions = {
        # Books already exist on disk with the current game_config.py (the
        # last run generated them successfully) - leave False. Only flip to
        # True again if you change reels, paytable, or any BetMode/
        # Distribution in game_config.py.
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = [
        "base",
        "bonus_speed_dating",
        "bonus_after_dark",
        "match_boost",
        "match_frenzy",
        "like_storm",
    ]

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    failed_modes = []
    if run_conditions["run_optimization"]:
        max_attempts_per_mode = 25
        for mode in target_modes:
            succeeded = False
            for attempt in range(1, max_attempts_per_mode + 1):
                try:
                    OptimizationExecution.run_opt_single_mode(config, mode, rust_threads)
                    succeeded = True
                    break
                except Exception as exc:
                    print(f"[{mode}] attempt {attempt}/{max_attempts_per_mode} failed ({exc})")
            if succeeded:
                print(f"[{mode}] succeeded" + (f" on attempt {attempt}" if attempt > 1 else ""))
            else:
                failed_modes.append(mode)
        generate_configs(gamestate)
        if failed_modes:
            print(f"\n=== Modes still needing a retry: {failed_modes} ===\n")
        else:
            print("\n=== All modes optimized successfully! ===\n")

    if run_conditions["run_analysis"] and not failed_modes:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"] and not failed_modes:
        execute_all_tests(config)