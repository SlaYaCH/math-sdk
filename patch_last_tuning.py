path = "apps/louvo/src/components/SuperlikeBarilletDisplay.svelte"
with open(path, "r") as f:
    content = f.read()

old_hub = "const HUB_Y = 152.5;"
new_hub = "const HUB_Y = 149;"

old_size = "const HEART_SIZE = 50;"
new_size = "const HEART_SIZE = 57;"

missing = [n for n, o in [("hub", old_hub), ("size", old_size)] if o not in content]
if missing:
    print("ERREUR : ancre(s) introuvable(s) :", missing)
else:
    content = content.replace(old_hub, new_hub, 1)
    content = content.replace(old_size, new_size, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : HUB_Y=149, coeurs a 57px.")
