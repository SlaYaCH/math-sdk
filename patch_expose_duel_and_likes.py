path = "games/louvo/game_calculations.py"
with open(path, "r") as f:
    content = f.read()

old_events_block = '''        for reel_index, symbol in match_hits:
            multiplier = symbol.multiplier
            self.book.add_event({
                "index": len(self.book.events),
                "type": "matchDuelReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
            })
            self._expand_reel_to_wild(reel_index, multiplier)
            expanded_reels.append(reel_index)

        pending = getattr(self, "pending_likes", {})
        likes_preview = {id(sym): pending.get(id(sym), 0) for _, sym in superlike_hits}

        for reel_index, symbol in superlike_hits:
            multiplier = symbol.multiplier
            self.book.add_event({
                "index": len(self.book.events),
                "type": "superlikeReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
                "likes": likes_preview[id(symbol)],
            })
            self._expand_reel_to_wild(reel_index, multiplier)
            expanded_reels.append(reel_index)

        occupied = set()
        for reel_index in expanded_reels:
            for row_index in range(self.config.num_rows[reel_index]):
                occupied.add((reel_index, row_index))

        # Likes-received counts were stashed on self.pending_likes (keyed by
        # symbol id) when the SUPER LIKE symbol was created - see
        # game_override.py.
        superlike_likes = {id(sym): pending.pop(id(sym), 0) for _, sym in superlike_hits}

        for reel_index, symbol in superlike_hits:
            likes = superlike_likes[id(symbol)]
            multiplier = symbol.multiplier
            self._fire_likes(likes, multiplier, occupied)'''

new_events_block = '''        pending_duels = getattr(self, "pending_duels", {})

        for reel_index, symbol in match_hits:
            multiplier = symbol.multiplier
            contender_a, contender_b = pending_duels.pop(id(symbol), (multiplier, multiplier))
            self.book.add_event({
                "index": len(self.book.events),
                "type": "matchDuelReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
                "duelValues": [contender_a, contender_b],
            })
            self._expand_reel_to_wild(reel_index, multiplier)
            expanded_reels.append(reel_index)

        for reel_index, symbol in superlike_hits:
            self._expand_reel_to_wild(reel_index, symbol.multiplier)
            expanded_reels.append(reel_index)

        occupied = set()
        for reel_index in expanded_reels:
            for row_index in range(self.config.num_rows[reel_index]):
                occupied.add((reel_index, row_index))

        # Likes-received counts were stashed on self.pending_likes (keyed by
        # symbol id) when the SUPER LIKE symbol was created - see
        # game_override.py.
        pending = getattr(self, "pending_likes", {})
        superlike_likes = {id(sym): pending.pop(id(sym), 0) for _, sym in superlike_hits}

        for reel_index, symbol in superlike_hits:
            likes = superlike_likes[id(symbol)]
            multiplier = symbol.multiplier
            fired_positions = self._fire_likes(likes, multiplier, occupied)
            self.book.add_event({
                "index": len(self.book.events),
                "type": "superlikeReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
                "likes": likes,
                "likePositions": fired_positions,
            })'''

old_fire_likes = '''    def _fire_likes(self, likes: int, multiplier, occupied: set) -> None:
        candidates = [
            (r, row)
            for r in range(self.config.num_reels)
            for row in range(self.config.num_rows[r])
            if (r, row) not in occupied
        ]
        random.shuffle(candidates)
        for reel_index, row_index in candidates[:likes]:
            self._replace_symbol(reel_index, row_index, "W", multiplier=multiplier)
            occupied.add((reel_index, row_index))'''

new_fire_likes = '''    def _fire_likes(self, likes: int, multiplier, occupied: set) -> list:
        candidates = [
            (r, row)
            for r in range(self.config.num_reels)
            for row in range(self.config.num_rows[r])
            if (r, row) not in occupied
        ]
        random.shuffle(candidates)
        fired_positions = []
        for reel_index, row_index in candidates[:likes]:
            self._replace_symbol(reel_index, row_index, "W", multiplier=multiplier)
            occupied.add((reel_index, row_index))
            fired_positions.append({"reelIndex": reel_index, "rowIndex": row_index})
        return fired_positions'''

missing = [name for name, old in [("events_block", old_events_block), ("fire_likes", old_fire_likes)] if old not in content]
if missing:
    print("ERREUR : bloc(s) non trouve(s) tel quel :", missing)
else:
    content = content.replace(old_events_block, new_events_block, 1)
    content = content.replace(old_fire_likes, new_fire_likes, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : game_calculations.py mis a jour (positions likes + valeurs duel exposees).")
