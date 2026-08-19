path = "games/louvo/game_config.py"
with open(path, "r") as f:
    content = f.read()

old_block = """        # --- paylines -------------------------------------------------------
        # 19 lines on the 5x5 grid (row index 0-4 per reel, top to bottom).
        # NOTE: this is a placeholder, symmetric 19-line layout, not extracted
        # from the reference game's line-map images. Swap in the exact
        # pattern later if 1:1 parity matters to you.
        self.paylines = {
            0: [0, 0, 0, 0, 0],
            1: [1, 1, 1, 1, 1],
            2: [2, 2, 2, 2, 2],
            3: [3, 3, 3, 3, 3],
            4: [4, 4, 4, 4, 4],
            5: [0, 1, 1, 1, 0],
            6: [4, 3, 3, 3, 4],
            7: [1, 2, 2, 2, 1],
            8: [3, 2, 2, 2, 3],
            9: [2, 1, 1, 1, 2],
            10: [2, 3, 3, 3, 2],
            11: [0, 0, 1, 0, 0],
            12: [4, 4, 3, 4, 4],
            13: [1, 1, 0, 1, 1],
            14: [3, 3, 4, 3, 3],
            15: [1, 1, 2, 1, 1],
            16: [3, 3, 2, 3, 3],
            17: [0, 1, 2, 1, 0],
            18: [4, 3, 2, 3, 4],
        }"""

new_block = """        # --- paylines -------------------------------------------------------
        # 19 lines on the 5x5 grid (row index 0-4 per reel, top to bottom).
        # Custom layout provided by the user, replacing the earlier placeholder.
        self.paylines = {
            0: [0, 0, 0, 0, 0],
            1: [1, 1, 1, 1, 1],
            2: [2, 2, 2, 2, 2],
            3: [3, 3, 3, 3, 3],
            4: [4, 4, 4, 4, 4],
            5: [0, 1, 0, 1, 0],
            6: [1, 2, 1, 2, 1],
            7: [2, 3, 2, 3, 2],
            8: [3, 4, 3, 4, 3],
            9: [1, 0, 1, 0, 1],
            10: [2, 1, 2, 1, 2],
            11: [3, 2, 3, 2, 3],
            12: [4, 3, 4, 3, 4],
            13: [0, 1, 2, 3, 4],
            14: [1, 2, 3, 2, 1],
            15: [2, 3, 4, 3, 2],
            16: [4, 3, 2, 1, 0],
            17: [3, 2, 1, 2, 3],
            18: [2, 1, 0, 1, 2],
        }"""

if old_block not in content:
    print("ERREUR : bloc non trouve tel quel, rien modifie.")
else:
    content = content.replace(old_block, new_block)
    with open(path, "w") as f:
        f.write(content)
    print("OK : 19 paylignes remplacees.")
