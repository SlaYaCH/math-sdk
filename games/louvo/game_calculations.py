"""
Louvo - custom board calculations.

Implements the two signature mechanics from the reference game:

- MATCH ("M"): expands to a full wild reel, carries a duel multiplier.
- SUPER LIKE ("K"): expands to a full wild reel, carries a multiplier AND
  fires extra wild symbols onto the board based on how many likes it received.

Plus the After-Dark-only "Match Streak" sub-feature (equivalent to the
reference game's "DuelSpins"): a CUMULATIVE counter of likes received across
spins during the After Dark freegame. Every 6 likes (a full heart display)
unlocks the next streak tier and queues a forced bonus spin; any surplus
likes from the spin that completes a tier roll over immediately onto the
next tier's counter, rather than being lost or requiring a fresh spin.

UPDATE (cumulative streak): self.streak_hearts now persists across spins
within a single After Dark session (NOT reset per-spin). Reset to 0 happens
in gamestate.py at the point where a new After Dark freegame session is
triggered - NOT handled in this file, since expand_special_reels() has no
visibility into "is this the first spin of a brand-new bonus". See the
TODO at the bottom of this file for the exact reset call needed there.

Also fixed a pre-existing bug in _queue_match_streak_unlock(): the guard
around `self.pending_match_streaks = []` was missing (it was unconditionally
resetting the queue on every unlock, potentially dropping an unconsumed
forced-spin request). Restored the `if not hasattr(...)` guard.

Confirmed against the real SDK (games/template/ + live tracebacks):
- Symbol's real constructor takes a single argument, not (config, name) as
  the public docs showed - so new symbols are created via self.create_symbol
  (name), the same method the engine itself uses when drawing a board
  (confirmed by a traceback through create_board_reelstrips). This also
  means any special_symbol_functions callback registered for that symbol
  name (see game_override.py) fires automatically - no manual call needed.
- Attributes like .multiplier are set with plain assignment
  (symbol.multiplier = value), not through assign_attribute()/get_attribute().
- GameCalculations itself inherits Executables directly (matches
  games/template/game_calculations.py), with GameExecutables inheriting
  GameCalculations in turn - see game_executables.py.
- Custom book events follow the documented pattern:
  https://stakeengine.github.io/math-sdk/math_docs/gamestate_section/events_info/
  event = {"index": len(self.book.events), "type": "...", ...}
  self.book.add_event(event)
"""

import random

from src.executables.executables import Executables
from src.calculations.lines import Lines
from src.wins.multiplier_strategy import apply_mult


class GameCalculations(Executables):
    # ------------------------------------------------------------------
    # Expansion pass: turns M / K symbols on the freshly-drawn board into
    # full wild reels, respecting the reference game's stacking rules:
    #   - max 1 special symbol per reel (guaranteed by reel-strip design)
    #   - max 2 SUPER LIKE per spin
    #   - MATCH and SUPER LIKE never resolve on the same spin
    # ------------------------------------------------------------------
    def expand_special_reels(self) -> None:
        match_hits = []       # [(reel_index, symbol)]
        superlike_hits = []   # [(reel_index, symbol)]

        after_first_tier = (
            getattr(self, "tier", "basegame") == "after_dark"
            and getattr(self, "match_streak_unlocks", 0) >= 1
        )
        for reel_index, column in enumerate(self.board):
            for row_index, symbol in enumerate(column):
                if symbol.name == "M":
                    match_hits.append((reel_index, symbol))
                elif symbol.name == "K":
                    # JAMAIS 2 SUPER LIKE sur le meme rouleau (regle Duel at
                    # Dawn : 1 seul Outlaw par rouleau) - un 2e K naturel sur
                    # un rouleau deja servi est retrograde en symbole bas.
                    if any(r == reel_index for r, _ in superlike_hits):
                        self._replace_symbol(reel_index, row_index, random.choice(
                            ["L1", "L2", "L3", "L4"]))
                        continue
                    if after_first_tier and random.random() < 0.5:
                        self._replace_symbol(reel_index, row_index, random.choice(
                            ["L1", "L2", "L3", "L4"]))
                        continue
                    superlike_hits.append((reel_index, symbol))

        if match_hits and superlike_hits:
            match_hits = []  # SUPER LIKE takes priority; MATCH downgraded below

        # Regles SUPER LIKE (precisees 21/08) : jamais 2 sur le meme rouleau
        # (dedup faite plus haut) ; max 2 par spin en base game, Speed Dating
        # et Like Storm ; JAMAIS 2 en After Dark (cap 1) ; les tours MATCH
        # (match_frenzy, Match Streak) strippent deja K en amont.
        # Multiplicateurs ADDITIONNES par le moteur si 2 bannieres sur la
        # meme ligne gagnante.
        max_superlikes = 1 if getattr(self, "tier", "basegame") == "after_dark" else 2
        superlike_hits = superlike_hits[:max_superlikes]

        kept = {id(s) for _, s in match_hits + superlike_hits}
        for reel_index, column in enumerate(self.board):
            for row_index, symbol in enumerate(column):
                if symbol.name in ("M", "K") and id(symbol) not in kept:
                    self._replace_symbol(reel_index, row_index, random.choice(
                        ["L1", "L2", "L3", "L4"]))

        expanded_reels = []
        pending_duels = getattr(self, "pending_duels", {})

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

        pending = getattr(self, "pending_likes", {})
        superlike_likes = {id(sym): pending.pop(id(sym), 0) for _, sym in superlike_hits}

        for reel_index, symbol in superlike_hits:
            likes = superlike_likes[id(symbol)]
            multiplier = symbol.multiplier
            fired_positions = self._fire_likes(likes, None, occupied)

            if getattr(self, "tier", "basegame") == "after_dark":
                self.streak_hearts = getattr(self, "streak_hearts", 0) + likes
                while (
                    self.streak_hearts >= 6
                    and getattr(self, "match_streak_unlocks", 0) < self.config.match_streak_max_unlocks
                ):
                    self.streak_hearts -= 6
                    self._queue_match_streak_unlock()

            self.book.add_event({
                "index": len(self.book.events),
                "type": "superlikeReveal",
                "reelIndex": reel_index,
                "multiplier": multiplier,
                "likes": likes,
                "likePositions": fired_positions,
                "streakTier": getattr(self, "match_streak_unlocks", 0),
                "streakHearts": getattr(self, "streak_hearts", 0),
            })

    def _expand_reel_to_wild(self, reel_index: int, multiplier) -> None:
        for row_index in range(self.config.num_rows[reel_index]):
            self._replace_symbol(reel_index, row_index, "W", multiplier=multiplier)

    def _fire_likes(self, likes: int, multiplier, occupied: set) -> list:
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
        return fired_positions

    def _replace_symbol(self, reel_index: int, row_index: int, name: str, multiplier=None) -> None:
        new_symbol = self.create_symbol(name)
        if multiplier is not None:
            new_symbol.multiplier = multiplier
        self.board[reel_index][row_index] = new_symbol

    # ------------------------------------------------------------------
    # Match Streak (DuelSpin-equivalent), After Dark tier only.
    # ------------------------------------------------------------------
    def _queue_match_streak_unlock(self) -> None:
        if not hasattr(self, "match_streak_unlocks"):
            self.match_streak_unlocks = 0
        if not hasattr(self, "pending_match_streaks"):
            self.pending_match_streaks = []

        if self.match_streak_unlocks >= self.config.match_streak_max_unlocks:
            return
        self.match_streak_unlocks += 1
        guarantee = self.config.match_streak_guarantees[self.match_streak_unlocks]
        self.pending_match_streaks.append(guarantee)

    def reset_match_streak(self) -> None:
        """Called from gamestate.py at the start of a NEW After Dark
        freegame session - see TODO below. Clears the cumulative counter
        and tier so nothing carries over from a previous After Dark run."""
        self.streak_hearts = 0
        self.match_streak_unlocks = 0
        self.pending_match_streaks = []

    def force_match_streak_board(self, guarantee_count: int) -> None:
        """
        Overwrite the current board so that `guarantee_count` MATCH symbols
        appear, one per reel (max 5, matching the reference game's 4th-tier
        guarantee of 5/5 reels). self.create_symbol("M") already triggers
        assign_match_duel automatically (it's registered in
        special_symbol_functions), so no follow-up call is needed here.
        Caller is expected to run expand_special_reels() right after this
        so these actually expand into wild reels (each with its own
        matchDuelReveal event now).
        """
        # Tour de Match Streak : 100% MATCH, rien d'autre de special (ni
        # SUPER LIKE - qui annulerait les MATCH via la regle de priorite
        # dans expand_special_reels - ni scatter).
        self.strip_symbols(("S", "K"))
        reel_indices = list(range(self.config.num_reels))
        random.shuffle(reel_indices)
        chosen_reels = reel_indices[:min(guarantee_count, self.config.num_reels)]
        for reel_index in chosen_reels:
            row_index = random.randrange(self.config.num_rows[reel_index])
            self._replace_symbol(reel_index, row_index, "M")

    # ------------------------------------------------------------------
    # Match Frenzy / Like Storm (FeatureSpins-style bonus buys): every spin
    # in these modes guarantees a specific special symbol, and scatters must
    # never appear (these modes stay in base spins only).
    # ------------------------------------------------------------------
    def get_lines_louvo(self):
        """Evaluation des lignes + regle Louvo des wilds "coupes" :
        une ligne commencant par 3 ou 4 wilds SANS symbole normal payant
        derriere (coupee par un DATE) paie comme 3 ou 4 exemplaires du
        meilleur symbole H1/"Le R" (3 -> 4.00, 4 -> 10.00). Le moteur
        partage (Lines.get_lines) ignorait ces lignes : (3,W)/(4,W)
        absents du paytable et un S comme "premier symbole normal" ne paie
        rien -> W,W,W,W,S payait 0 (bug constate en jeu reel).
        Inchange : wilds suivis d'un symbole normal (la ligne paie ce
        symbole), 2 wilds seuls (rien), 5 wilds (20.00).
        Une ligne deja payee par le moteur n'est jamais retouchee - la
        regle ne s'applique qu'aux lignes a 0."""
        win_data = Lines.get_lines(self.board, self.config, global_multiplier=self.global_multiplier)
        paid_lines = {w["meta"]["lineIndex"] for w in win_data["wins"]}

        for line_index, line in self.config.paylines.items():
            if line_index in paid_lines:
                continue
            leading_wilds = 0
            for reel in range(len(line)):
                if self.board[reel][line[reel]].check_attribute("wild"):
                    leading_wilds += 1
                else:
                    break
            if leading_wilds not in (3, 4):
                continue
            base_win = self.config.paytable[(leading_wilds, "H1")]
            positions = [{"reel": idx, "row": line[idx]} for idx in range(leading_wilds)]
            line_win, applied_mult = apply_mult(
                self.board,
                "symbol",
                global_multiplier=self.global_multiplier,
                win_amount=base_win,
                positions=positions,
            )
            win_data["wins"].append(Lines.line_win_info(
                "W",
                leading_wilds,
                line_win,
                positions,
                {
                    "lineIndex": line_index,
                    "multiplier": applied_mult,
                    "winWithoutMult": base_win,
                    "globalMult": int(self.global_multiplier),
                    "lineMultiplier": int(applied_mult / self.global_multiplier),
                },
            ))
            win_data["totalWin"] += line_win

        return win_data

    def sanitize_padding(self) -> None:
        """Padding (rangees invisibles au-dessus/en-dessous du board) :
        purement cosmetique mais affiche par le frontend pendant l'animation
        des rouleaux. Le moteur le tire de la bande REELLE du spin (pas de
        config.padding_reels), donc S/M/K peuvent s'y retrouver - on les
        remplace par des symboles bas avant chaque reveal_event. Regle
        notamment : S fantome en padding (y compris en After Dark ou le
        DATE ne doit apparaitre nulle part) et M/K decoratifs trompeurs.
        Aucun impact sur les gains ni sur l'anticipation (le moteur ne
        compte que les 5 rangees visibles - verifie dans
        src/calculations/board.py)."""
        for attr in ("top_symbols", "bottom_symbols"):
            syms = getattr(self, attr, None)
            if not syms:
                continue
            for i, sym in enumerate(syms):
                if sym.name in ("S", "M", "K"):
                    syms[i] = self.create_symbol(random.choice(["L1", "L2", "L3", "L4"]))

    def strip_symbols(self, names) -> None:
        """Remplace tout symbole dont le nom est dans `names` par un symbole
        bas aleatoire. Utilise par les modes 'garantie' (match_frenzy /
        like_storm) pour qu'un symbole special tire NATURELLEMENT ne vienne
        pas parasiter la garantie - notamment un K naturel qui, via la regle
        'SUPER LIKE prioritaire sur MATCH' de expand_special_reels(),
        annulait silencieusement les 2 MATCH garantis de match_frenzy."""
        for reel_index, column in enumerate(self.board):
            for row_index, symbol in enumerate(column):
                if symbol.name in names:
                    self._replace_symbol(reel_index, row_index, random.choice(
                        ["L1", "L2", "L3", "L4"]))

    def strip_scatters(self) -> None:
        """Replace any naturally-drawn scatter with a random low symbol -
        used in FeatureSpins modes where the free-spin trigger must not
        appear at all."""
        for reel_index, column in enumerate(self.board):
            for row_index, symbol in enumerate(column):
                if symbol.name == "S":
                    self._replace_symbol(reel_index, row_index, random.choice(
                        ["L1", "L2", "L3", "L4"]))

    def force_match_frenzy_board(self) -> None:
        """Match Frenzy: guarantee at least 2 MATCH symbols this spin.
        Rien d'autre de special ne doit apparaitre : ni scatter (DATE), ni
        SUPER LIKE (qui annulerait les MATCH garantis)."""
        self.strip_symbols(("S", "K"))
        is_wincap_attempt = getattr(self, "criteria", "") == "wincap"
        reel_indices = list(range(self.config.num_reels))
        random.shuffle(reel_indices)
        for reel_index in reel_indices[:2]:
            row_index = random.randrange(self.config.num_rows[reel_index])
            self._replace_symbol(reel_index, row_index, "M")

    def force_like_storm_board(self) -> None:
        """Like Storm (refonte facon LONE OUTLAW FEATURESPINS de Duel at Dawn) :
        - garantit 1 SUPER LIKE avec au moins 2 coeurs ;
        - 1 chance sur 4 d'un 2e SUPER LIKE (autre rouleau, coeurs libres
          1-6), max 2 par spin comme le jeu de reference ;
        - rien d'autre de special (ni scatter/DATE, ni MATCH) ;
        - les wilds tires ne tombent jamais sur les memes cases ni sur les
          bannieres (set `occupied` de expand_special_reels) et restent des
          wilds simples sans multiplicateur ;
        - tentative wincap : 2 SUPER LIKE forces a 200x chacun - le moteur
          ADDITIONNE les multiplicateurs des deux bannieres sur une meme
          ligne (400x) - et le reste du plateau en H1."""
        # On retire AUSSI les K naturels de la bande : seuls les K poses par
        # cette fonction existent, donc la garantie "1er K avec 2+ coeurs"
        # ne peut jamais etre ecartee par le cap max-2 (bug : 30/3000 books
        # du run precedent avaient 3 K et perdaient le K garanti).
        self.strip_symbols(("S", "M", "K"))
        is_wincap_attempt = getattr(self, "criteria", "") == "wincap"

        reel_indices = list(range(self.config.num_reels))
        random.shuffle(reel_indices)
        first_reel, second_reel = reel_indices[0], reel_indices[1]

        row_index = random.randrange(self.config.num_rows[first_reel])
        self._replace_symbol(first_reel, row_index, "K")
        first_symbol = self.board[first_reel][row_index]
        if not hasattr(self, "pending_likes"):
            self.pending_likes = {}
        self.pending_likes[id(first_symbol)] = random.choice([2, 3, 4, 5, 6])

        second_symbol = None
        if is_wincap_attempt or random.random() < 0.25:
            row_index = random.randrange(self.config.num_rows[second_reel])
            self._replace_symbol(second_reel, row_index, "K")
            second_symbol = self.board[second_reel][row_index]

        if is_wincap_attempt:
            first_symbol.multiplier = 200
            second_symbol.multiplier = 200
            for r in range(self.config.num_reels):
                if r in (first_reel, second_reel):
                    continue
                for row in range(self.config.num_rows[r]):
                    self._replace_symbol(r, row, "H1")
