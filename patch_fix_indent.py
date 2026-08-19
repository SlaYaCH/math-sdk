path = "games/louvo/gamestate.py"
with open(path, "r") as f:
    content = f.read()

old = """            self.pending_likes = {}
        self.pending_duels = {}
            self.global_multiplier = 1"""

new = """            self.pending_likes = {}
            self.pending_duels = {}
            self.global_multiplier = 1"""

if old not in content:
    print("ERREUR : bloc introuvable tel quel.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : indentation corrigee dans run_spin.")
