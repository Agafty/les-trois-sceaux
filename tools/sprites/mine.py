"""Tileset de la Mine Effondrée (donjon 2) — Les Trois Sceaux.

Usage : python tools/sprites/mine.py          -> DESSIN FINAL (mine_art.py) si disponible, sinon plan
        python tools/sprites/mine.py --plan   -> PLAN (aplats par famille et numéros)
Produit : art/tilesets/mine.png, mine_numeros.png, mine_plan.md, maps/tilesets/mine.tsx.

Le catalogue (numéros, collisions, terrains) est identique dans les deux cas ; le dessin est dans mine_art.py.
DISPOSITION : les ids 0-5, 16-39, 40-47, 48-71, 80-92 reprennent EXACTEMENT ceux de `temple_racines` (sol, murs, trous de passage,
portes, bords de poussière, escaliers 56/57, trous mortels 58-66, eau) : le code des trous et des escaliers s'applique tel quel.
RÈGLE : ne jamais déplacer une tuile ; on ajoute dans les lignes de réserve (à la fin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import *  # noqa: E402,F401,F403
import tsplan  # noqa: E402

tsplan.CATS.update(
    sol='#8a7060', sol2='#7a6a5a', poussiere='#4a4048', mur='#6e5a50', rail='#9a9aa8', bois='#8a5a34', trou='#14101c',
    passage='#3fc0a8', eau='#4a78c0', cristal='#4ac8e8', cristal_r='#e2342c', minerai='#d8b840', bloc='#d040c0',
    secret='#a040e0', porte='#e8782c', escalier='#d0c090', arene='#9a6a8a', lampe='#f0e060', rocher='#9a9aa8',
    metal='#6a6a78', deco='#b0a090', ombre='#3a3038')

FAMILLES = ('sol (brun-gris) / poussière (sombre) / arène (violet-gris) / mur (brun) / rail et métal (gris clair) / bois (brun) / '
            'trou (noir) / passage (turquoise) / eau (bleu) / cristal (cyan) / cristal rouge / minerai (jaune) / '
            'éboulis et blocage (magenta) / fissuré à la bombe (violet) / porte (orange) / escalier (beige)')


class MineSheet(Sheet):
    def md(self, script):
        w, self.wang = self.wang, {}
        try:
            o = super().md(script)
        finally:
            self.wang = w
        o = o.replace('\n## Calques', DEV + '\n## Calques', 1)
        o = o.replace('## Notes', TERRAINS + '## Notes', 1)
        return o


DEV = """
## POUR LE DÉVELOPPEUR : ids à reconnaître par le code

Tileset `mine` (8 colonnes, id local Tiled = ligne × 8 + colonne). Une tuile reconnue = le tileset ET l'id.

| Famille | Ids | Calque | Ce que le code doit faire |
| --- | --- | --- | --- |
| **TROUS MORTELS** | **58 à 66** (même bloc 3×3 que `temple_racines` 58 à 66) | `Sol` | Comme `HoleRules` : toute la case fait tomber (-1 PV sans mourir, retour au Spawn de la salle). `HoleWatcher` doit aussi accepter le tileset `mine` (fichier `mine.png`). Les autres tuiles ne tuent pas. |
| **Trous de passage** (vers l'étage du dessous) | 31 à 39 (comme `temple_racines`) | `Sol` | Décoratif, jamais mortel : l'objet `Chute` fait le travail. Ne PAS les confondre avec 58-66. |
| **Escaliers** | 56 (montant), 57 (descendant) | `Sol` | Posent une `Sortie` `transition=escalier` (comme le temple). |
| **MURS FISSURÉS** fermé -> ouvert | 144 -> 148 (haut), 145 -> 149 (bas), 146 -> 150 (gauche), 147 -> 151 (droite) ; 152 -> 153 (rocher fissuré) | fermés `Murs`, ouverts `Decor` | Comme `TileRules` pour `montagne` 156 -> 157 et 172 -> 173 : la bombe retire la tuile fermée de `Murs` et le code pose la version ouverte sur `Decor` (ou elle est déjà posée dessous). Les versions ouvertes sont opaques. |
| **ÉBOULIS bloquants** fermé -> dégagé | 72 -> 76, 73 -> 77, 74 -> 76 (moitié gauche), 75 -> 77 (moitié droite) | fermés `Murs`, dégagés `Sol` | Comme `montagne` 176/178 -> 180 et 177/179 -> 181. |
| ÉBOULIS dans une ouverture | 164 -> 76, 165 -> 77 | fermés `Murs`, dégagés `Sol` | Même règle que les éboulis ; à poser à la place d'une tuile de porte. |
| Indice visuel | 154 `mur_craquele` | `Murs` | Rien : simple décor solide (aucun id à reconnaître). |

Tilesets : `mine` ET `mine_sous_sol` (mêmes ids, mêmes collisions) : `HoleWatcher` doit accepter les deux fichiers.
Les éboulis ont d'autres numéros que `montagne` (72 à 77, pas 176 à 181) : à déclarer dans `TileRules` pour `mine`.

Tout le reste est géré par les collisions du `.tsx` (murs 16 à 30, 40 à 43 portes, 72 à 75, 104 à 110, 113, 121, 122, 131, 143, 144 à 147, 152, 154) : aucun code.
Les ids 0 à 5, 16 à 57, 58 à 71 et 80 à 92 ont **les mêmes numéros que `temple_racines`** pour le sol, les murs, les portes, la poussière (= la terre du temple), les escaliers et l'eau.
"""

TERRAINS = """## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain a une couleur « sol » (tuiles 0 à 2) et une couleur de terrain.

| Terrain | Couleurs | Calque | Tuiles |
| --- | --- | --- | --- |
| `Murs` | `mur` (le reste = vide) | Murs | 16 à 30 |
| `Trous` | `sol`, `trou` | Sol | 0 à 2 (sol), 58 à 66 |
| `Trous de passage` | `sol`, `passage` | Sol | 0 à 2 (sol), 31 à 39 |
| `Eau` | `sol`, `eau` | Sol | 0 à 2 (sol), 80 à 92 |
| `Poussiere` | `sol`, `poussiere` | Sol | 0 à 2 (sol), 5, 48 à 55, 67 à 71 |

"""


S = MineSheet('mine', 8, 'La Mine Effondrée (donjon 2 : galeries, rails, éboulis, cristaux, arène de Gorm)',
              ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px. Palette : roche brun-gris chaude, bois d\'étais, rails gris, '
               'cristaux cyan, cristal rouge de Gorm. En PLAN, **la couleur indique la famille** (' + FAMILLES + ') ; une zone plus sombre '
               'dans une tuile = zone solide.',
               '- DEUX planches de même numérotation : `mine.png` (rez-de-chaussée) et `mine_sous_sol.png` (recoloration plus sombre et bleutée, '
               'tileset `mine_sous_sol.tsx` identique).'],
              ['`Sol` : sol, poussière, eau peu profonde, trous (mortels et de passage), escaliers, arène, éboulis dégagé',
               '`Decor` : rails, gravats, cristaux au sol, ossements, ouvertures de mur fissuré (version ouverte)',
               '`Murs` : tout ce qui bloque (murs, éboulis, wagonnets, tas de minerai, tonneaux, murs fissurés fermés). Collisions dans le tileset',
               '`Objets` : Sortie, Spawn, Ennemi, Coffre, Porte, MurFissure, Chute, boss_gorm, pilier… (objets Tiled, pas des tuiles)',
               '`Dessus` : passe devant Brann (linteaux et poutres, haut d\'étai, lanternes, cristaux de paroi, haut de pilier)'])
S.reserve = 4

BASE = [(2, 14, 28, 18)]
OBJ = [(4, 8, 24, 22)]
POSTC = [(11, 14, 10, 18)]
WAGON = [(0, 10, 32, 20)]
DOORH = [(0, 0, 6, 32), (26, 0, 6, 32)]
DOORV = [(0, 0, 32, 4), (0, 28, 32, 4)]


def at(i, nom, role, calque, coll, cat, **k):
    S.cur = i
    return S.add(nom, role, calque, coll, cat, **k)


def grp(first, titre, note=''):
    S.cur = first
    S.group(titre, note)


def so(i, nom, role, cat='sol', **k):
    at(i, nom, role, 'Sol', None, cat, **k)


def de(i, nom, role, cat='deco', **k):
    at(i, nom, role, 'Decor', None, cat, **k)


def mu(i, nom, role, coll, cat, **k):
    at(i, nom, role, 'Murs', coll, cat, **k)


def du(i, nom, role, cat='bois', coll=None, **k):
    at(i, nom, role, 'Dessus', coll, cat, **k)


def edge(i, nom, role, catA, catB, bits, calque='Sol', coll=None):
    bi = bits[0] * 8 + bits[1] * 4 + bits[2] * 2 + bits[3]
    at(i, nom, role, calque, coll, catB, plan=('terrain', bi, catA, catB))


def wang(name, tile, labelA, colA, labelB, colB, base_ids, tiles):
    """tiles : {id: bits (HG,HD,BG,BD)}, 1 = terrain secondaire dans ce coin."""
    d = {i: (1, 1, 1, 1) for i in base_ids}
    for i, b in tiles.items():
        d[i] = tuple(2 if k else 1 for k in b)
    S.wang[name] = dict(colors=[(labelA, colA), (labelB, colB)], tile=tile, tiles=d, fam='')


def bits_of(b):
    return corners(b)


# bits (HG,HD,BG,BD) pour les tuiles de bord/coin du temple (1 = terrain spécial dans le coin)
EDGES9 = {'haut': (0, 0, 1, 1), 'bas': (1, 1, 0, 0), 'gauche': (0, 1, 0, 1), 'droite': (1, 0, 1, 0),
          'coin_hg': (0, 0, 0, 1), 'coin_hd': (0, 0, 1, 0), 'coin_bg': (0, 1, 0, 0), 'coin_bd': (1, 0, 0, 0)}
FULL4 = (1, 1, 1, 1)
CREUX = {'creux_hg': (0, 1, 1, 1), 'creux_hd': (1, 0, 1, 1), 'creux_bg': (1, 1, 0, 1), 'creux_bd': (1, 1, 1, 0)}
POSN = {'haut': 'haut', 'bas': 'bas', 'gauche': 'gauche', 'droite': 'droite'}

# ------------------------------------------------------------------ 1. sols, rails, décor de sol
grp(0, 'Sol, rails, ombres', 'Sol de la mine : peindre les variantes 0 à 4 au hasard. Rails sur `Decor` (jamais de collision) : droits, quatre virages '
    '(nommés par les deux côtés qu\'ils relient). Les ombres 12 à 14 se posent sous les murs (`Decor`).')
so(0, 'sol_a', 'Sol de roche brun-gris, de base')
so(1, 'sol_b', 'Sol de roche avec petits cailloux')
so(2, 'sol_c', 'Sol de roche en dalles irrégulières')
so(3, 'sol_fissure_a', 'Sol fissuré (fissure en diagonale)')
so(4, 'sol_fissure_b', 'Sol fissuré (fissure en étoile)')
so(5, 'poussiere', 'Poussière de charbon, sol sombre (base du terrain Poussiere)', 'poussiere')
de(6, 'rail_h', 'Rail horizontal (se raccorde à gauche et à droite)', 'rail')
de(7, 'rail_v', 'Rail vertical (se raccorde en haut et en bas)', 'rail')
de(8, 'rail_bd', 'Rail en virage : relie le BAS et la DROITE', 'rail')
de(9, 'rail_bg', 'Rail en virage : relie le BAS et la GAUCHE', 'rail')
de(10, 'rail_hd', 'Rail en virage : relie le HAUT et la DROITE', 'rail')
de(11, 'rail_hg', 'Rail en virage : relie le HAUT et la GAUCHE', 'rail')
de(12, 'ombre_mur_haut', 'Ombre portée d\'un mur du haut sur le sol (trame), sous un mur_haut', 'ombre')
de(13, 'ombre_mur_gauche', 'Ombre portée d\'un mur de gauche sur le sol', 'ombre')
de(14, 'ombre_mur_coin', 'Ombre portée dans un angle haut-gauche (mur en haut et à gauche)', 'ombre')
de(15, 'gravats', 'Petit tas de gravats et poussière', 'rocher')

# ------------------------------------------------------------------ 2. murs
grp(16, 'Murs de galerie (terrain `Murs`)', 'Roche taillée : dessus sombre + face avant plus claire visible. Toutes les tuiles sont pleines. '
    'Mêmes numéros et mêmes formes que `temple_racines` (16 à 30).')
WALLS = {16: ('mur_haut', 'Mur du haut de la salle : sol en dessous, face avant visible', (1, 1, 0, 0)),
         17: ('mur_bas', 'Mur du bas de la salle : sol au-dessus', (0, 0, 1, 1)),
         18: ('mur_gauche', 'Mur de gauche de la salle : sol à droite', (1, 0, 1, 0)),
         19: ('mur_droite', 'Mur de droite de la salle : sol à gauche', (0, 1, 0, 1)),
         20: ('mur_coin_int_hg', 'Coin intérieur haut-gauche (angle de salle) : sol seulement en bas-droite', (1, 1, 1, 0)),
         21: ('mur_coin_int_hd', 'Coin intérieur haut-droite (angle de salle) : sol seulement en bas-gauche', (1, 1, 0, 1)),
         22: ('mur_coin_int_bg', 'Coin intérieur bas-gauche (angle de salle) : sol seulement en haut-droite', (1, 0, 1, 1)),
         23: ('mur_coin_int_bd', 'Coin intérieur bas-droite (angle de salle) : sol seulement en haut-gauche', (0, 1, 1, 1)),
         24: ('mur_coin_ext_hg', 'Coin extérieur haut-gauche d\'un bloc de mur posé dans la salle : mur seulement en bas-droite', (0, 0, 0, 1)),
         25: ('mur_coin_ext_hd', 'Coin extérieur haut-droite d\'un bloc de mur : mur seulement en bas-gauche', (0, 0, 1, 0)),
         26: ('mur_coin_ext_bg', 'Coin extérieur bas-gauche d\'un bloc de mur : mur seulement en haut-droite', (0, 1, 0, 0)),
         27: ('mur_coin_ext_bd', 'Coin extérieur bas-droite d\'un bloc de mur : mur seulement en haut-gauche', (1, 0, 0, 0)),
         28: ('mur_plein', 'Mur plein (intérieur d\'un mur épais, rien de visible autour)', (1, 1, 1, 1)),
         29: ('mur_diag_a', 'Mur en diagonale (mur en haut-gauche et bas-droite) — complète le terrain', (1, 0, 0, 1)),
         30: ('mur_diag_b', 'Mur en diagonale (mur en haut-droite et bas-gauche) — complète le terrain', (0, 1, 1, 0))}
for i, (n, r, b) in WALLS.items():
    mu(i, n, r, FULL, 'mur')
S.S_WALLS = WALLS
S.wang['Murs'] = dict(colors=[('mur', '#6e5a50')], tile=28, fam='',
                      tiles={i: tuple(1 if k else 0 for k in b) for i, (n, r, b) in WALLS.items()})

# ------------------------------------------------------------------ 3. trous de passage
grp(31, 'Trous de passage (vers l\'étage du dessous)', 'IDS 31 à 39 : trou de passage rectangulaire (bord de planches, lueur turquoise). Décoratif, calque `Sol`, '
    'sans collision ; l\'objet `Chute` se pose par-dessus. Jamais mortel : à ne pas confondre avec les trous 58 à 66.')
at(31, 'trou_passage', 'Trou de passage : case entière (fond turquoise lumineux, sans anneau)', 'Sol', None, 'passage',
   plan=('terrain', 15, 'sol', 'passage'))
PASS = {}
for k, (suf, b) in enumerate([('bord_haut', EDGES9['haut']), ('bord_bas', EDGES9['bas']), ('bord_gauche', EDGES9['gauche']),
                              ('bord_droite', EDGES9['droite']), ('coin_hg', EDGES9['coin_hg']), ('coin_hd', EDGES9['coin_hd']),
                              ('coin_bg', EDGES9['coin_bg']), ('coin_bd', EDGES9['coin_bd'])]):
    txt = {'bord_haut': 'Bord haut d\'un trou de passage (sol au-dessus)', 'bord_bas': 'Bord bas d\'un trou de passage (sol en dessous)',
           'bord_gauche': 'Bord gauche d\'un trou de passage (sol à gauche)', 'bord_droite': 'Bord droit d\'un trou de passage (sol à droite)',
           'coin_hg': 'Coin haut-gauche d\'un trou de passage rectangulaire', 'coin_hd': 'Coin haut-droite d\'un trou de passage rectangulaire',
           'coin_bg': 'Coin bas-gauche d\'un trou de passage rectangulaire', 'coin_bd': 'Coin bas-droite d\'un trou de passage rectangulaire'}[suf]
    edge(32 + k, f'trou_passage_{suf}', txt, 'sol', 'passage', b)
    PASS[32 + k] = b
PASS[31] = FULL4
wang('Trous de passage', 31, 'sol', '#8a7060', 'passage', '#3fc0a8', [0, 1, 2], PASS)

# ------------------------------------------------------------------ 4. portes
grp(40, 'Ouvertures de porte (cadre d\'étais)', 'Remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` dans la même case du calque '
    '`Dessus`, puis l\'objet `Porte` par-dessus. Mêmes numéros et mêmes collisions que `temple_racines`.')
mu(40, 'porte_haut', 'Ouverture dans le mur haut (remplace une tuile mur_haut) ; passage de 20 px au centre, l\'objet Porte se pose dessus', DOORH, 'porte')
mu(41, 'porte_bas', 'Ouverture dans le mur bas (remplace une tuile mur_bas) ; passage de 20 px au centre, l\'objet Porte se pose dessus', DOORH, 'porte')
mu(42, 'porte_gauche', 'Ouverture dans le mur gauche (remplace une tuile mur_gauche) ; passage de 24 px au centre, l\'objet Porte se pose dessus', DOORV, 'porte')
mu(43, 'porte_droite', 'Ouverture dans le mur droite (remplace une tuile mur_droite) ; passage de 24 px au centre, l\'objet Porte se pose dessus', DOORV, 'porte')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    du(44 + k, f'porte_{s}_dessus', f'Haut de l\'encadrement de porte_{s}, même case que porte_{s}', 'porte')

# ------------------------------------------------------------------ 5. poussière
grp(48, 'Poussière de charbon (terrain `Poussiere`)', 'Peindre la poussière avec ce terrain plutôt que la tuile 5 seule : les bords (48 à 55, 67 à 71) '
    'font une transition irrégulière vers le sol.')
POUS = {}
for k, (suf, b) in enumerate([('haut', EDGES9['haut']), ('bas', EDGES9['bas']), ('gauche', EDGES9['gauche']), ('droite', EDGES9['droite'])]):
    edge(48 + k, f'poussiere_bord_{suf}', f'Poussière : bord {suf} (sol {"au-dessus" if suf == "bas" else "en dessous" if suf == "haut" else "à droite" if suf == "gauche" else "à gauche"})',
         'sol', 'poussiere', b)
    POUS[48 + k] = b
for k, (suf, txt) in enumerate([('creux_hg', 'sol seulement en haut-gauche'), ('creux_hd', 'sol seulement en haut-droite'),
                                ('creux_bg', 'sol seulement en bas-gauche'), ('creux_bd', 'sol seulement en bas-droite')]):
    b = CREUX[suf]
    edge(52 + k, f'poussiere_{suf}', f'Poussière : coin rentrant, {txt}', 'sol', 'poussiere', b)
    POUS[52 + k] = b
POUS[5] = FULL4

# ------------------------------------------------------------------ 6. escaliers et trous mortels
grp(56, 'Escaliers et TROUS MORTELS (58 à 66)', 'Les escaliers 56/57 : la transition est un objet `Sortie` (`transition=escalier`). '
    'Les trous 58 à 66 sont à la même place que dans `temple_racines` : toute la case fait tomber (-1 PV, retour au Spawn de la salle).')
so(56, 'escalier_montant', 'Escalier qui monte (vers le haut de l\'écran) ; la transition est un objet Sortie', 'escalier')
so(57, 'escalier_descendant', 'Escalier qui descend (vers le bas de l\'écran) ; la transition est un objet Sortie', 'escalier')
at(58, 'trou', 'TROU MORTEL : on tombe dans toute la case', 'Sol', None, 'trou', plan=('terrain', 15, 'sol', 'trou'))
HOLES = {58: FULL4}
for k, (suf, txt) in enumerate([('bord_haut', 'Bord haut d\'un trou (sol au-dessus) : paroi du fond visible'),
                                ('bord_bas', 'Bord bas d\'un trou (sol en dessous)'), ('bord_gauche', 'Bord gauche d\'un trou (sol à gauche)'),
                                ('bord_droite', 'Bord droit d\'un trou (sol à droite)'), ('coin_hg', 'Coin haut-gauche d\'un trou rectangulaire'),
                                ('coin_hd', 'Coin haut-droite d\'un trou rectangulaire'), ('coin_bg', 'Coin bas-gauche d\'un trou rectangulaire'),
                                ('coin_bd', 'Coin bas-droite d\'un trou rectangulaire')]):
    key = suf.replace('bord_', '')
    b = EDGES9[key] if suf.startswith('bord') else EDGES9[suf]
    edge(59 + k, f'trou_{suf}', 'TROU MORTEL : ' + txt, 'sol', 'trou', b)
    HOLES[59 + k] = b
wang('Trous', 58, 'sol', '#8a7060', 'trou', '#14101c', [0, 1, 2], HOLES)
for k, (suf, b, txt) in enumerate([('coin_hg', EDGES9['coin_hg'], 'coin haut-gauche d\'une zone de poussière (poussière seulement en bas-droite)'),
                                   ('coin_hd', EDGES9['coin_hd'], 'coin haut-droite d\'une zone de poussière (poussière seulement en bas-gauche)'),
                                   ('coin_bg', EDGES9['coin_bg'], 'coin bas-gauche d\'une zone de poussière (poussière seulement en haut-droite)'),
                                   ('coin_bd', EDGES9['coin_bd'], 'coin bas-droite d\'une zone de poussière (poussière seulement en haut-gauche)')]):
    edge(67 + k, f'poussiere_{suf}', 'Poussière : ' + txt, 'sol', 'poussiere', b)
    POUS[67 + k] = b
edge(71, 'poussiere_diag', 'Poussière : deux coins opposés (poussière en haut-gauche et bas-droite)', 'sol', 'poussiere', (1, 0, 0, 1))
POUS[71] = (1, 0, 0, 1)
wang('Poussiere', 5, 'sol', '#8a7060', 'poussiere', '#4a4048', [0, 1, 2], POUS)

# ------------------------------------------------------------------ 7. éboulis
grp(72, 'ÉBOULIS bloquants et cailloux', 'Éboulis fermé -> dégagé (même logique que `montagne` 176 à 181) : la bombe retire la tuile fermée de `Murs` et le code pose '
    'la version dégagée. 72 et 74 -> 76 ; 73 et 75 -> 77. Un éboulis 2×1 se pose avec 74 puis 75.')
mu(72, 'eboulis_a', 'ÉBOULIS : tas de rochers, case pleine (solide)', FULL, 'bloc')
mu(73, 'eboulis_b', 'ÉBOULIS : variante B (solide)', FULL, 'bloc')
mu(74, 'eboulis_g', 'ÉBOULIS large, moitié gauche (2×1, solide)', FULL, 'bloc')
mu(75, 'eboulis_d', 'ÉBOULIS large, moitié droite (2×1, solide)', FULL, 'bloc')
so(76, 'eboulis_degage_a', 'Éboulis DÉGAGÉ : gravats au sol (passable), remplace eboulis_a et eboulis_g', 'rocher')
so(77, 'eboulis_degage_b', 'Éboulis DÉGAGÉ : gravats, variante, remplace eboulis_b et eboulis_d', 'rocher')
de(78, 'eboulis_poussiere', 'Poussière et cailloux autour d\'un éboulis (décor)', 'rocher')
de(79, 'cailloux', 'Quelques cailloux épars', 'rocher')

# ------------------------------------------------------------------ 8. eau
grp(80, 'Eau souterraine peu profonde (terrain `Eau`)', 'Eau peu profonde, calque `Sol`, sans collision (Brann la traverse). Le bord passe au milieu de la tuile. '
    'Il manque volontairement les deux tuiles en diagonale.')
at(80, 'eau', 'Eau peu profonde, case entière (Brann la traverse)', 'Sol', None, 'eau', plan=('terrain', 15, 'sol', 'eau'))
EAU = {80: FULL4}
names = [('eau_bord_haut', 'Eau peu profonde : bord haut (sol au-dessus)', EDGES9['haut']),
         ('eau_bord_bas', 'Eau peu profonde : bord bas (sol en dessous)', EDGES9['bas']),
         ('eau_bord_gauche', 'Eau peu profonde : bord gauche (sol à gauche)', EDGES9['gauche']),
         ('eau_bord_droite', 'Eau peu profonde : bord droite (sol à droite)', EDGES9['droite']),
         ('eau_creux_hg', 'Eau peu profonde : coin rentrant, sol seulement en haut-gauche', CREUX['creux_hg']),
         ('eau_creux_hd', 'Eau peu profonde : coin rentrant, sol seulement en haut-droite', CREUX['creux_hd']),
         ('eau_creux_bg', 'Eau peu profonde : coin rentrant, sol seulement en bas-gauche', CREUX['creux_bg']),
         ('eau_creux_bd', 'Eau peu profonde : coin rentrant, sol seulement en bas-droite', CREUX['creux_bd']),
         ('eau_coin_hg', 'Eau peu profonde : coin haut-gauche d\'une étendue rectangulaire (eau seulement dans le quart opposé)', EDGES9['coin_hg']),
         ('eau_coin_hd', 'Eau peu profonde : coin haut-droite d\'une étendue rectangulaire (eau seulement dans le quart opposé)', EDGES9['coin_hd']),
         ('eau_coin_bg', 'Eau peu profonde : coin bas-gauche d\'une étendue rectangulaire (eau seulement dans le quart opposé)', EDGES9['coin_bg']),
         ('eau_coin_bd', 'Eau peu profonde : coin bas-droite d\'une étendue rectangulaire (eau seulement dans le quart opposé)', EDGES9['coin_bd'])]
for k, (n, r, b) in enumerate(names):
    edge(81 + k, n, r, 'sol', 'eau', b)
    EAU[81 + k] = b
wang('Eau', 80, 'sol', '#8a7060', 'eau', '#4a78c0', [0, 1, 2], EAU)

# ------------------------------------------------------------------ 9. rails (suite) et wagonnets
grp(96, 'Rails (suite), wagonnets, minerai', 'Les butoirs ferment un rail (nommés par le côté où le rail s\'arrête). Le wagonnet 2×1 = `wagonnet_g` puis `wagonnet_d` '
    '(solide à la base, on le contourne).')
de(96, 'rail_croix', 'Croisement de rails (haut, bas, gauche, droite)', 'rail')
de(97, 'rail_butoir_haut', 'Butoir : le rail s\'arrête en HAUT de la case (il arrive par le bas)', 'rail')
de(98, 'rail_butoir_bas', 'Butoir : le rail s\'arrête en BAS de la case (il arrive par le haut)', 'rail')
de(99, 'rail_butoir_gauche', 'Butoir : le rail s\'arrête à GAUCHE de la case (il arrive par la droite)', 'rail')
de(100, 'rail_butoir_droite', 'Butoir : le rail s\'arrête à DROITE de la case (il arrive par la gauche)', 'rail')
de(101, 'rail_casse_h', 'Rail horizontal brisé (traverses arrachées)', 'rail')
de(102, 'rail_casse_v', 'Rail vertical brisé (traverses arrachées)', 'rail')
de(103, 'traverses', 'Traverses de bois sans rail (voie arrachée)', 'bois')
mu(104, 'wagonnet_g', 'Wagonnet de mine sur rail, moitié gauche (2×1, solide)', WAGON, 'metal')
mu(105, 'wagonnet_d', 'Wagonnet de mine sur rail, moitié droite (2×1, solide)', WAGON, 'metal')
mu(106, 'wagonnet_v', 'Wagonnet vu de face, vide (1×1, solide)', OBJ, 'metal')
mu(107, 'wagonnet_renverse', 'Wagonnet renversé, minerai répandu (1×1, solide)', OBJ, 'metal')
mu(108, 'wagonnet_minerai', 'Wagonnet de face plein de minerai (1×1, solide)', OBJ, 'metal')
mu(109, 'minerai_tas_a', 'Tas de minerai (solide)', OBJ, 'minerai')
mu(110, 'minerai_tas_b', 'Tas de minerai, variante (solide)', OBJ, 'minerai')
de(111, 'minerai_sol', 'Éclats de minerai épars au sol', 'minerai')

# ------------------------------------------------------------------ 10. étais et mobilier
grp(112, 'Étais, poutres, lanternes, mobilier', 'Un étai = 2 cases : `etai_base` (Murs, solide) + `etai_haut` (Dessus) juste au-dessus. Une galerie étayée = `poutre_g`, '
    '`poutre_h` (autant que nécessaire), `poutre_d` sur `Dessus`, au-dessus d\'un couloir.')
du(112, 'etai_haut', 'Haut d\'étai (poutre transversale), case au-dessus de etai_base')
mu(113, 'etai_base', 'Base d\'étai : poteau de bois (solide, étroit)', POSTC, 'bois')
du(114, 'poutre_h', 'Poutre horizontale en travers d\'un couloir (Dessus ; Brann passe dessous)')
du(115, 'poutre_g', 'Extrémité gauche d\'une poutre sur son poteau (Dessus)')
du(116, 'poutre_d', 'Extrémité droite d\'une poutre sur son poteau (Dessus)')
du(117, 'etai_mur', 'Étai plaqué contre une face de mur (à poser sur une tuile de mur, Dessus)')
de(118, 'planches_sol', 'Planches de bois au sol (plancher de mine)', 'bois')
du(119, 'lanterne', 'Lanterne accrochée (Dessus)', 'lampe')
de(120, 'pioche_sol', 'Pioche oubliée au sol', 'metal')
mu(121, 'tonneau', 'Tonneau de mine (solide)', OBJ, 'bois')
mu(122, 'caisse', 'Caisse de mine (solide)', OBJ, 'bois')
de(123, 'toile_araignee', 'Toile d\'araignée dans un angle (coin haut-gauche de la case)', 'deco')
so(124, 'sol_filon', 'Sol avec un filon de minerai brillant (variante de sol)', 'minerai')
so(125, 'sol_reflet_cristal', 'Sol baigné d\'un reflet de cristaux (variante de sol)', 'cristal')
de(126, 'ossements', 'Ossements d\'un mineur', 'deco')
de(127, 'casque_mineur', 'Casque de mineur abandonné', 'deco')

# ------------------------------------------------------------------ 11. cristaux
grp(128, 'Cristaux lumineux (décor)', 'Cristaux cyan de la mine ; le cristal rouge évoque celui de Gorm. Les petits sont du décor sans collision. '
    'Un gros cristal = `cristal_gros_base` (Murs) + `cristal_gros_haut` (Dessus) au-dessus.')
de(128, 'cristal_a', 'Petits cristaux cyan au sol (décor)', 'cristal')
de(129, 'cristal_b', 'Amas de cristaux cyan au sol, variante (décor)', 'cristal')
de(130, 'cristal_rouge', 'Petit cristal rouge au sol (décor, traces de corruption)', 'cristal_r')
mu(131, 'cristal_gros_base', 'Gros cristal cyan : pied (solide)', BASE, 'cristal')
du(132, 'cristal_gros_haut', 'Gros cristal cyan : pointe, case au-dessus de cristal_gros_base', 'cristal')
du(133, 'cristal_mur', 'Cristaux qui percent une face de mur (à poser sur une tuile de mur, Dessus)', 'cristal')
de(134, 'lueur_cristal', 'Tache de lueur cyan au sol (semi-transparente, sous un cristal)', 'cristal')
du(135, 'veine_mur', 'Veine de minerai dans une face de mur (à poser sur une tuile de mur, Dessus)', 'minerai')

# ------------------------------------------------------------------ 12. arène de Gorm
grp(136, 'Arène de Gorm', 'Sol de l\'arène (dalles gravées, plus claires et violettes que le reste de la mine), cratères des rochers tombés et pilier. '
    'Le pilier = `pilier_base` (Murs) + `pilier_haut` (Dessus) ; les rectangles Tiled nommés `pilier` restent les piliers du boss.')
so(136, 'arene_a', 'Sol de l\'arène : dalles gravées', 'arene')
so(137, 'arene_b', 'Sol de l\'arène : dalles gravées, variante', 'arene')
so(138, 'arene_centre', 'Sol de l\'arène : sceau gravé du centre', 'arene')
so(139, 'arene_fissure', 'Sol de l\'arène fissuré par les coups de Gorm', 'arene')
de(140, 'arene_gravats', 'Éclats de roche sur le sol de l\'arène (décor)', 'rocher')
de(141, 'arene_cratere', 'Cratère laissé par un rocher tombé (décor)', 'ombre')
du(142, 'pilier_haut', 'Haut de pilier de pierre, case au-dessus de pilier_base', 'rocher')
mu(143, 'pilier_base', 'Base de pilier de pierre (solide)', BASE, 'rocher')

# ------------------------------------------------------------------ 13. murs fissurés
grp(144, 'MURS FISSURÉS (bombes) : fermé -> ouvert', 'Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus). Ouverts : sur `Decor`, opaques (ils couvrent '
    'tout le mur : trou noir dans la roche, la `Sortie` se pose dessus). Paires : 144->148, 145->149, 146->150, 147->151, 152->153. '
    '`mur_craquele` (154) est un simple indice visuel sans fonction.')
mu(144, 'mur_fissure_haut', 'MUR FISSURÉ du haut (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l\'ouvre)', FULL, 'secret')
mu(145, 'mur_fissure_bas', 'MUR FISSURÉ du bas (solide)', FULL, 'secret')
mu(146, 'mur_fissure_gauche', 'MUR FISSURÉ de gauche (solide)', FULL, 'secret')
mu(147, 'mur_fissure_droite', 'MUR FISSURÉ de droite (solide)', FULL, 'secret')
de(148, 'mur_fissure_haut_ouvert', 'Mur du haut OUVERT : trou noir dans la roche, gravats (Sortie dessus)', 'secret')
de(149, 'mur_fissure_bas_ouvert', 'Mur du bas OUVERT (Sortie dessus)', 'secret')
de(150, 'mur_fissure_gauche_ouvert', 'Mur de gauche OUVERT (Sortie dessus)', 'secret')
de(151, 'mur_fissure_droite_ouvert', 'Mur de droite OUVERT (Sortie dessus)', 'secret')
mu(152, 'rocher_fissure', 'ROCHER FISSURÉ : bloc craquelé posé au sol (solide ; objet MurFissure dessus)', FULL, 'secret')
de(153, 'rocher_fissure_ouvert', 'Rocher fissuré OUVERT : cavité noire entre des blocs (Sortie dessus)', 'secret')
mu(154, 'mur_craquele', 'Mur du haut craquelé (indice discret, sans fonction ; solide)', FULL, 'mur')


# ------------------------------------------------------------------ 14. ajouts demandés par le plan du donjon 2
grp(155, 'Ajouts : poutres, veines, rails en T, mobilier', 'Demandés par `maps/donjon2/plan.md` §7. `poutre_sciee` = décor de la salle 08. '
    '`mur_veine_etoile` = mur lumineux bleu-blanc de la salle 13. `eboulis_ouverture_h/v` : éboulis dans l encadrement d une porte (fermé -> 76/77).')
du(155, 'poutre_sciee', 'POUTRE SCIÉE : poutre en travers dont une extrémité est coupée net (décor, Dessus)')
du(156, 'poutre_brisee', 'Poutre brisée : éclats de bois pendants (décor, Dessus)')
mu(157, 'mur_veine_minerai', 'Mur plein avec veine de minerai doré (solide)', FULL, 'minerai')
mu(158, 'mur_veine_etoile', 'Mur plein avec VEINE D ÉTOILE lumineuse bleu-blanc (solide)', FULL, 'cristal')
mu(159, 'mur_cristaux_rouges', 'Mur plein incrusté de cristaux rouges (sous-sol, solide)', FULL, 'cristal_r')
de(160, 'rail_t_haut', 'Rail en T : rail horizontal + branche vers le HAUT', 'rail')
de(161, 'rail_t_bas', 'Rail en T : rail horizontal + branche vers le BAS', 'rail')
de(162, 'rail_t_gauche', 'Rail en T : rail vertical + branche vers la GAUCHE', 'rail')
de(163, 'rail_t_droite', 'Rail en T : rail vertical + branche vers la DROITE', 'rail')
mu(164, 'eboulis_ouverture_h', 'Éboulis dans une ouverture horizontale (porte haut/bas) (solide ; se dégage comme 72 -> 76)', FULL, 'bloc')
mu(165, 'eboulis_ouverture_v', 'Éboulis dans une ouverture verticale (porte gauche/droite) (solide ; se dégage comme 73 -> 77)', FULL, 'bloc')
de(166, 'pelle_sol', 'Pelle plantée dans un tas de gravats', 'metal')
mu(167, 'etabli', 'Établi de mineur : outils posés (solide)', OBJ, 'bois')
mu(168, 'panneau_bois', 'Panneau de bois (support d un indice ; solide, étroit)', POSTC, 'bois')
de(169, 'flaque', 'Flaque d eau sur le sol (sans effet)', 'eau')

PAIRES = [('mur_fissure_haut', 'mur_fissure_haut_ouvert'), ('mur_fissure_bas', 'mur_fissure_bas_ouvert'),
          ('mur_fissure_gauche', 'mur_fissure_gauche_ouvert'), ('mur_fissure_droite', 'mur_fissure_droite_ouvert'),
          ('rocher_fissure', 'rocher_fissure_ouvert'), ('eboulis_a', 'eboulis_degage_a'), ('eboulis_g', 'eboulis_degage_a'),
          ('eboulis_b', 'eboulis_degage_b'), ('eboulis_d', 'eboulis_degage_b'),
          ('eboulis_ouverture_h', 'eboulis_degage_a'), ('eboulis_ouverture_v', 'eboulis_degage_b')]

S.notes += [
    'IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier.',
    'Terrains Tiled (Wang par coins) : `Murs` (16 à 30), `Trous` (0-2, 58 à 66), `Trous de passage` (0-2, 31 à 39), `Eau` (0-2, 80 à 92), '
    '`Poussiere` (0-2, 5, 48 à 55, 67 à 71). Même organisation que `temple_racines` : une couleur « sol » (0 à 2) et une couleur de terrain.',
    'Murs : une seule couleur `mur`. Peindre `mur` sur les coins du pourtour d\'une salle de 20×11 donne l\'anneau mur_haut / mur_bas / mur_gauche / mur_droite + '
    'les 4 coins intérieurs. Un seul coin peint au milieu de la salle donne un bloc de 2×2 tuiles. Les tuiles de mur sont entières.',
    'Trous mortels et trous de passage : rectangles seulement. Pour un trou 2×2 : coin_hg, coin_hd (ligne du haut), coin_bg, coin_bd (ligne du bas).',
    'Eau : le bord passe au milieu de la tuile (chaque quart de 16×16 est du sol ou de l\'eau). Pas d\'eau profonde dans ce tileset (réserve 93 à 95).',
    'Porte : remplacer la tuile de mur par `porte_<côté>`, poser `porte_<côté>_dessus` dans la même case de `Dessus`, puis l\'objet `Porte`.',
    'À régler dans Tiled/Godot après livraison : animations de tuiles (cristaux qui brillent, eau), éventuelle propriété de tuile pour les trous.']

if __name__ == '__main__':
    if '--plan' in sys.argv or not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mine_art.py')):
        S.save_all('mine.py')
    else:
        import final_lib
        import mine_art
        import mine_art2  # noqa: F401
        import mine_art3  # noqa: F401
        px = final_lib.render(S, mine_art.REG)
        final_lib.save_final(S, px, 'mine.py')
        import mine_art3
        mine_art3.save_sous_sol(S, px)
