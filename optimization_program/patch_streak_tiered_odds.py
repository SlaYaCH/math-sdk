path = "games/louvo/game_calculations.py"
with open(path, "r") as f:
    content = f.read()

old = '''        for reel_index, column in enumerate(self.board):
            for symbol in column:
                if symbol.name == "M":
                    match_hits.append((reel_index, symbol))
                elif symbol.name == "K":
                    superlike_hits.append((reel_index, symbol))'''

new = '''        # Louvo : apres le 1er palier du Match Streak, on freine la cascade -
        # 50% de chance qu'un K tire au sort soit annule (redevient un symbole
        # bas) avant meme d'etre traite. Le tout premier palier (celui qui
        # rend le mecanisme excitant et atteignable) garde ses pleines
        # chances (2 K/colonne, FR1.csv) - seule la progression AU-DELA du
        # 1er palier ralentit, pour contenir le RTP en cascade.
        after_first_tier = (
            getattr(self, "tier", "basegame") == "after_dark"
            and getattr(self, "match_streak_unlocks", 0) >= 1
        )
        for reel_index, column in enumerate(self.board):
            for row_index, symbol in enumerate(column):
                if symbol.name == "M":
                    match_hits.append((reel_index, symbol))
                elif symbol.name == "K":
                    if after_first_tier and random.random() < 0.5:
                        self._replace_symbol(reel_index, row_index, random.choice(
                            ["L1", "L2", "L3", "L4"]))
                        continue
                    superlike_hits.append((reel_index, symbol))'''

if old not in content:
    print("ERREUR : bloc non trouve tel quel, rien modifie.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : cascade du Match Streak freinee (50% de chance en moins par K, apres le 1er palier).")
