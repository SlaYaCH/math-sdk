path = "games/louvo/game_calculations.py"
with open(path, "r") as f:
    content = f.read()

changes = 0

old1 = "        superlike_hits = superlike_hits[:2]"
new1 = "        superlike_hits = superlike_hits[:1]"
if old1 in content:
    content = content.replace(old1, new1)
    changes += 1
    print("OK 1/2 : max 1 SUPER LIKE par tour (au lieu de 2)")
else:
    print("ERREUR 1/2 : ligne non trouvee")

old2 = "            fired_positions = self._fire_likes(likes, multiplier, occupied)"
new2 = "            fired_positions = self._fire_likes(likes, None, occupied)"
if old2 in content:
    content = content.replace(old2, new2)
    changes += 1
    print("OK 2/2 : les balles ne portent plus de multiplicateur (la colonne, elle, garde le sien)")
else:
    print("ERREUR 2/2 : ligne non trouvee")

if changes == 2:
    with open(path, "w") as f:
        f.write(content)
    print("Fichier sauvegarde.")
else:
    print("RIEN SAUVEGARDE - au moins une ligne n'a pas matche, verifiez le fichier.")
