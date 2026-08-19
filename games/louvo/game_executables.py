"""
Louvo - game-specific executable overrides.

Un seul override : update_fs_retrigger_amt(). Le moteur partage
(src/executables + src/events/events.py) ajoute les tours a tot_fs ET
emet un event 'freeSpinRetrigger' que le frontend Louvo ne connait pas
("Missing bookEventHandler"). On garde le calcul du moteur mais on purge
cet event du book : le compteur de tours du frontend se met a jour via
l'event 'updateFreeSpin' standard emis au debut du tour suivant.
"""

from game_calculations import GameCalculations


class GameExecutables(GameCalculations):
    def update_fs_retrigger_amt(self):
        super().update_fs_retrigger_amt()
        events = self.book.events
        events[:] = [e for e in events if e.get("type") != "freeSpinRetrigger"]
        for i, e in enumerate(events):
            if "index" in e:
                e["index"] = i
