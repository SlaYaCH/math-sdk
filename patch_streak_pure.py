path = "games/louvo/game_calculations.py"
with open(path, "r") as f:
    content = f.read()

old = '''        reel_indices = list(range(self.config.num_reels))
        random.shuffle(reel_indices)
        chosen_reels = reel_indices[:min(guarantee_count, self.config.num_reels)]'''

new = '''        # Tour de Match Streak : 100% MATCH, rien d'autre de special (ni
        # SUPER LIKE - qui annulerait les MATCH via la regle de priorite
        # dans expand_special_reels - ni scatter).
        self.strip_symbols(("S", "K"))
        reel_indices = list(range(self.config.num_reels))
        random.shuffle(reel_indices)
        chosen_reels = reel_indices[:min(guarantee_count, self.config.num_reels)]'''

if old not in content:
    print("ERREUR : ancre non trouvee, rien modifie.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : force_match_streak_board nettoie desormais S et K (100% MATCH).")
