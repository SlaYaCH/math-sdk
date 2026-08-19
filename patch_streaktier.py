path = "games/louvo/game_calculations.py"
with open(path, "r") as f:
    content = f.read()

old_block = '''        for reel_index, symbol in superlike_hits:
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
            })
        if getattr(self, "tier", "basegame") == "after_dark":
            for _, symbol in superlike_hits:
                if superlike_likes[id(symbol)] == 6:
                    self._queue_match_streak_unlock()'''

new_block = '''        for reel_index, symbol in superlike_hits:
            likes = superlike_likes[id(symbol)]
            multiplier = symbol.multiplier
            fired_positions = self._fire_likes(likes, multiplier, occupied)
            if getattr(self, "tier", "basegame") == "after_dark" and likes == 6:
                self._queue_match_streak_unlock()
            self.book.add_event({
                "index": len(self.book.events),
                "type": "superlikeReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
                "likes": likes,
                "likePositions": fired_positions,
                "streakTier": getattr(self, "match_streak_unlocks", 0),
            })'''

if old_block not in content:
    print("ERREUR : bloc non trouve tel quel, rien modifie.")
else:
    content = content.replace(old_block, new_block)
    with open(path, "w") as f:
        f.write(content)
    print("OK : streakTier ajoute, ordre corrige.")
