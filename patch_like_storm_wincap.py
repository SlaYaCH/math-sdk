path = "games/louvo/game_config.py"
with open(path, "r") as f:
    content = f.read()

old = '''                    Distribution(
                        criteria="wincap",
                        quota=0.0001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": True,
                            "force_freegame": False,
                        },
                    ),'''

new = '''                    Distribution(
                        criteria="wincap",
                        quota=0.00001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": True,
                            "force_freegame": False,
                        },
                    ),'''

if old not in content:
    print("ERREUR : bloc non trouve tel quel.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : quota wincap de like_storm reduit de 0.0001 a 0.00001 (10x plus tolerant).")
