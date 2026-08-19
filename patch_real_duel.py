path = "games/louvo/game_override.py"
with open(path, "r") as f:
    content = f.read()

old_import = "from game_executables import GameExecutables"
new_import = "import random\n\nfrom game_executables import GameExecutables"

old_docstring = '''        value "wins the duel" and is the multiplier applied to the reel.'''
new_docstring = '''        value doesn't automatically win - the winner is picked with a fair
        coin flip, so either the bigger or the smaller value can end up as
        the multiplier applied to the reel.'''

old_logic = "        symbol.multiplier = max(contender_a, contender_b)"
new_logic = "        symbol.multiplier = contender_a if random.random() < 0.5 else contender_b"

missing = [name for name, old in [("import", old_import), ("docstring", old_docstring), ("logic", old_logic)] if old not in content]
if missing:
    print("ERREUR : ancre(s) non trouvee(s) :", missing)
else:
    content = content.replace(old_import, new_import, 1)
    content = content.replace(old_docstring, new_docstring, 1)
    content = content.replace(old_logic, new_logic, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : le duel peut maintenant faire gagner n'importe laquelle des deux valeurs (50/50).")
