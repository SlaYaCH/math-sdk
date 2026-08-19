path = "games/louvo/gamestate.py"
with open(path, "r") as f:
    content = f.read()

old = "self.pending_likes = {}"
new = "self.pending_likes = {}\n        self.pending_duels = {}"

count = content.count(old)
if count == 0:
    print("ERREUR : ancre introuvable dans gamestate.py")
else:
    content = content.replace(old, new)
    with open(path, "w") as f:
        f.write(content)
    print(f"OK : pending_duels reinitialise a cote de pending_likes ({count} occurrence(s)).")
