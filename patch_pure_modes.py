path = "games/louvo/game_calculations.py"
with open(path, "r") as f:
    content = f.read()

changes = 0

# 1. Nouvelle fonction de nettoyage generique, inseree juste avant strip_scatters
old_strip = '''    def strip_scatters(self) -> None:'''
new_strip = '''    def strip_symbols(self, names) -> None:
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

    def strip_scatters(self) -> None:'''

if old_strip in content:
    content = content.replace(old_strip, new_strip, 1)
    changes += 1
    print("OK 1/3 : fonction strip_symbols ajoutee")
else:
    print("ERREUR 1/3 : ancre strip_scatters non trouvee")

# 2. match_frenzy : retirer scatters ET super likes avant de poser les M
old_frenzy = '''        """Match Frenzy: guarantee at least 2 MATCH symbols this spin."""
        self.strip_scatters()'''
new_frenzy = '''        """Match Frenzy: guarantee at least 2 MATCH symbols this spin.
        Rien d'autre de special ne doit apparaitre : ni scatter (DATE), ni
        SUPER LIKE (qui annulerait les MATCH garantis)."""
        self.strip_symbols(("S", "K"))'''

if old_frenzy in content:
    content = content.replace(old_frenzy, new_frenzy, 1)
    changes += 1
    print("OK 2/3 : match_frenzy nettoie desormais S et K")
else:
    print("ERREUR 2/3 : ancre match_frenzy non trouvee")

# 3. like_storm : retirer scatters ET matchs avant de poser le K
old_storm = '''        """Like Storm: guarantee 1 SUPER LIKE symbol with at least 2 likes."""
        self.strip_scatters()'''
new_storm = '''        """Like Storm: guarantee 1 SUPER LIKE symbol with at least 2 likes.
        Rien d'autre de special ne doit apparaitre : ni scatter (DATE), ni
        MATCH."""
        self.strip_symbols(("S", "M"))'''

if old_storm in content:
    content = content.replace(old_storm, new_storm, 1)
    changes += 1
    print("OK 3/3 : like_storm nettoie desormais S et M")
else:
    print("ERREUR 3/3 : ancre like_storm non trouvee")

if changes == 3:
    with open(path, "w") as f:
        f.write(content)
    print("Fichier sauvegarde.")
else:
    print(f"RIEN SAUVEGARDE - seulement {changes}/3 ancres trouvees.")
