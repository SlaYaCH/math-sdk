path = "games/louvo/game_calculations.py"
with open(path, "r") as f:
    content = f.read()

old = '''    def force_like_storm_board(self) -> None:
        """Like Storm: guarantee 1 SUPER LIKE symbol with at least 2 likes."""
        self.strip_scatters()
        reel_index = random.randrange(self.config.num_reels)
        row_index = random.randrange(self.config.num_rows[reel_index])
        self._replace_symbol(reel_index, row_index, "K")
        new_symbol = self.board[reel_index][row_index]
        if not hasattr(self, "pending_likes"):
            self.pending_likes = {}
        # override whatever assign_superlike_likes drew - this mode
        # guarantees at least 2, regardless of the normal random outcome.
        self.pending_likes[id(new_symbol)] = random.choice([2, 3, 4, 5, 6])'''

new = '''    def force_like_storm_board(self) -> None:
        """Like Storm: guarantee 1 SUPER LIKE symbol with at least 2 likes.
        When this spin is specifically the forced 'wincap' distribution
        attempt (self.criteria == 'wincap'), also force a generous
        multiplier and fill every other reel with H1 - verified by hand
        calculation that this configuration clears the 15000x wincap
        (~76000x theoretical at 200x mult + all-H1 elsewhere). The normal
        Like Storm experience (criteria '0'/'basegame') is untouched."""
        self.strip_scatters()
        is_wincap_attempt = getattr(self, "criteria", "") == "wincap"

        reel_index = random.randrange(self.config.num_reels)
        row_index = random.randrange(self.config.num_rows[reel_index])
        self._replace_symbol(reel_index, row_index, "K")
        new_symbol = self.board[reel_index][row_index]
        if not hasattr(self, "pending_likes"):
            self.pending_likes = {}
        # override whatever assign_superlike_likes drew - this mode
        # guarantees at least 2, regardless of the normal random outcome.
        self.pending_likes[id(new_symbol)] = random.choice([2, 3, 4, 5, 6])

        if is_wincap_attempt:
            new_symbol.multiplier = 200
            for r in range(self.config.num_reels):
                if r == reel_index:
                    continue
                for row in range(self.config.num_rows[r]):
                    self._replace_symbol(r, row, "H1")'''

if old not in content:
    print("ERREUR : bloc non trouve tel quel, rien modifie.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : force_like_storm_board force desormais reellement le wincap quand criteria=='wincap'.")
