path = "games/louvo/gamestate.py"
with open(path, "r") as f:
    content = f.read()

old = '''        if self.betmode == "bonus_after_dark":
            self.tier = "after_dark"
        elif self.betmode == "bonus_speed_dating":
            self.tier = "speed_dating"
        else:
            scatters_seen = self.count_special_symbols("scatter")
            self.tier = "after_dark" if scatters_seen >= 4 else "speed_dating"'''

new = '''        if self.betmode == "bonus_after_dark":
            self.tier = "after_dark"
        elif self.betmode == "bonus_speed_dating":
            self.tier = "speed_dating"
        else:
            scatters_seen = self.count_special_symbols("scatter")
            self.tier = "after_dark" if scatters_seen >= 4 else "speed_dating"

        # Louvo : freeSpinTrigger/freeSpinRetrigger (src/events/events.py,
        # partage entre tous les jeux) est ajoute AVANT que self.tier ne soit
        # calcule ici - on complete retroactivement le dernier evenement
        # correspondant deja present dans le book avec le vrai palier.
        for event in reversed(self.book.events):
            if event.get("type") in ("freeSpinTrigger", "freeSpinRetrigger"):
                event["tier"] = self.tier
                break'''

if old not in content:
    print("ERREUR : bloc non trouve tel quel, rien modifie.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : champ tier ajoute retroactivement a freeSpinTrigger/freeSpinRetrigger.")
