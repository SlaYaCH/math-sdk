path = "games/louvo/game_config.py"
with open(path, "r") as f:
    content = f.read()

old = '''                    Distribution(
                        criteria="0",
                        quota=0.15,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.8495,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_freegame": False,
                        },
                    ),
                ],
            ),'''

new = '''                    Distribution(
                        criteria="0",
                        quota=0.02,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.9295,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "scatter_triggers": {0: 1},
                            "force_freegame": False,
                        },
                    ),
                ],
            ),'''

if old not in content:
    print("ERREUR : bloc non trouve tel quel, rien modifie.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : quota 'zero gain' de like_storm reduit de 15% a 2%.")
