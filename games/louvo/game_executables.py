"""
Louvo - game-specific executable overrides.

Most of the reusable spin logic (drawing boards, emitting line-win events,
handling free-spin triggers) is inherited transitively through
GameCalculations -> Executables. This file is where you'd override any of
those default behaviours if Louvo needed something different from the
standard flow - for now it's a thin placeholder.

NOTE: inherits GameCalculations (not Executables directly) - this matches
the single-inheritance chain used throughout the real SDK: Executables ->
GameCalculations -> GameExecutables -> GameStateOverride -> GameState.
"""

from game_calculations import GameCalculations


class GameExecutables(GameCalculations):
    pass
