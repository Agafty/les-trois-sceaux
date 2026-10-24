"""Objets des enigmes du Temple des Racines (donjon 1) — Les Trois Sceaux.

Usage : python tools/sprites/enigmes.py [dossier_apercu]
Produit, en planches horizontales de cases 32x32 (sans marge), dans art/puzzles/ :
  plaque_pression.png  2 : 0 relevee, 1 enfoncee
  levier.png           2 : 0 haut, 1 bas
  torche.png           7 : 0 eteinte, 1-4 allumee (boucle), 5-6 s'eteint (flamme qui retrecit ; 6 = presque eteinte)
  brasero.png          4 : allume (boucle)
  cible_gland.png / cible_racine.png / cible_feuille.png   3 : 0 inactive, 1 active, 2 erreur
  cible_chrono.png     5 : anneau qui se vide : 0 plein (100 %), 1 (75 %), 2 (50 %), 3 (25 %), 4 vide (inactive)
  grille_h.png / grille_v.png   4 : 0 fermee, 1 ouverture 1, 2 ouverture 2, 3 ouverte
et art/items/fleche_enflammee.png : 3 cases 32x32 (flamme + trainee, pointe vers la droite comme fleche.png).
Les symboles des cibles sont ceux de la fresque (symboles.py). Sans Pillow : encodeur PNG de coffres.py.
"""
import math
import os
import sys

import coffres as CF
import objets_utilises as OU
from symboles import SYMBOLS, NATUREL

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
PUZ = os.path.join(ROOT, 'art', 'puzzles')
ITEMS = os.path.join(ROOT, 'art', 'items')

PAL = {
    '.': None, '0': '#1b1420', 'I': '#241a22',
    'a': '#d8d4cc', 'b': '#9a948c', 'c': '#5c5650',                     # dalles
    'W': '#7a6a88', 'V': '#4e4058', 'U': '#382e42', 'X': '#b8a8c0',     # pierre du temple
    'L': '#b06e40', 'M': '#8a5a34', 'D': '#5e3a22',                     # bois
    'g': '#d8d4cc', 'h': '#9a948c', 'k': '#5c5650',                     # fer
    'r': '#e2342c', 'R': '#961c28', 'o': '#f08a28', 'y': '#f8d848', 'w': '#fff4d0',   # feu
    'Y': '#f8d848', 'O': '#c89a28', 'P': '#8a5a1c',                     # or
    'e': '#d6c49c', 'E': '#b09468', 's': '#847e76', 'S': '#aaa49a',     # sable, fumee
    'C': '#7a9ac0', 'B': '#3c5a8a', 'Z': '#b8d0e8', 'N': '#263a5e',     # glace / bleu
    'G': '#5a8a3c', 'H': '#9ad060',
}
for _k, _v in NATUREL.items():
    pass


def rgba(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def blank(w=32, h=32):
    return [['.'] * w for _ in range(h)]


def put(g, x, y, c):
    if 0 <= y < len(g) and 0 <= x < len(g[0]):
        g[y][x] = c


def rect(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(g, x, y, c)


def disc(g, cx, cy, r, c):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                put(g, x, y, c)


def outline(g, color='0'):
    CF.outline(g, color)


def px(g, pal=PAL):
    return [[rgba(pal[c]) if pal[c] else (0, 0, 0, 0) for c in row] for row in g]


def sheet(frames, pal=PAL):
    return CF.sheet([px(f, pal) for f in frames])


# ---------------------------------------------------------------- flamme
def flame(g, cx, by, h, w, ph, sway=2.0):
    """Flamme en goutte, base en (cx, by), hauteur h, demi-largeur max w. Trois couches : orange, jaune, blanc."""
    layer = blank(len(g[0]), len(g))
    for sw, sh, col in ((1.0, 1.0, 'o'), (0.62, 0.72, 'y'), (0.3, 0.42, 'w')):
        hh = h * sh
        for i in range(int(hh)):
            f = i / hh
            half = w * sw * ((1 - f) ** 0.65) * (0.8 if i == 0 else 1.0)
            c = cx + round(math.sin(ph + f * 2.6) * f * sway)
            x0, x1 = round(c - half), round(c + half)
            if x1 < x0:
                x0 = x1 = c
            for x in range(x0, x1 + 1):
                put(layer, x, by - i, col)
        put(layer, cx + round(math.sin(ph + 2.6) * sway * 0.9) if col == 'o' else cx, by - int(hh), col)
    outline(layer, 'R')
    for y in range(len(g)):
        for x in range(len(g[0])):
            if layer[y][x] != '.':
                g[y][x] = layer[y][x]


# ---------------------------------------------------------------- plaque de pression
def plaque(pressed):
    g = blank()
    rect(g, 4, 4, 27, 28, 'c')                             # cadre de pierre dans le sol
    rect(g, 5, 5, 26, 27, 'I')
    rect(g, 4, 4, 27, 4, 'b')
    if not pressed:
        rect(g, 6, 5, 25, 22, 'e')                         # dessus de la plaque
        rect(g, 6, 5, 25, 5, 'w'); rect(g, 6, 5, 6, 22, 'w')
        rect(g, 25, 6, 25, 22, 'E'); rect(g, 7, 22, 25, 22, 'E')
        rect(g, 6, 23, 25, 26, 'E')                        # tranche : la plaque depasse du sol
        rect(g, 6, 26, 25, 26, 'M')
        rect(g, 25, 23, 25, 25, 'M')
        cy, col, ring = 13, 'r', 'E'
    else:
        rect(g, 6, 9, 25, 25, 'E')                         # plaque enfoncee : plus basse, plus sombre
        rect(g, 7, 10, 24, 24, 'e')
        rect(g, 7, 10, 24, 10, 'E')
        rect(g, 7, 10, 7, 24, 'E')
        rect(g, 6, 5, 25, 8, 'I')
        cy, col, ring = 17, 'H', 'E'
    disc(g, 15.5, cy, 4.2, ring)                           # rune ronde au centre
    disc(g, 15.5, cy, 2.6, col)
    put(g, 14, cy - 1, 'w')
    outline(g)
    return g


# ---------------------------------------------------------------- levier
def levier(down):
    g = blank()
    rect(g, 5, 21, 26, 29, 'b')                            # dalle de base posee contre le mur
    rect(g, 5, 21, 26, 22, 'a')
    rect(g, 5, 21, 5, 29, 'a')
    rect(g, 26, 22, 26, 29, 'c'); rect(g, 6, 29, 26, 29, 'c')
    rect(g, 9, 24, 22, 26, 'I')                            # fente
    rect(g, 9, 24, 22, 24, '0')
    if not down:
        rect(g, 15, 8, 17, 23, 'h')                        # manche vers le haut (vers le mur)
        rect(g, 15, 8, 15, 23, 'g'); rect(g, 17, 8, 17, 23, 'k')
        disc(g, 16, 6, 3.6, 'r'); disc(g, 15, 5, 1.2, 'w')
        rect(g, 18, 6, 19, 8, 'R')
    else:
        rect(g, 15, 22, 17, 27, 'h')                       # manche rabattu vers le joueur (raccourci)
        rect(g, 15, 22, 15, 27, 'g'); rect(g, 17, 22, 17, 27, 'k')
        disc(g, 16, 26, 3.6, 'G'); disc(g, 15, 25, 1.2, 'H')
        rect(g, 18, 26, 19, 28, '0')
    rect(g, 14, 23, 18, 24, 'k'); put(g, 14, 23, 'g')      # axe
    outline(g)
    return g


# ---------------------------------------------------------------- torche et brasero
DY = 4      # la coupe est descendue de 4 px pour laisser de la place a la flamme


def torche_base(g, lit):
    rect(g, 10, 24, 21, 29, 'b')                           # socle de pierre
    rect(g, 9, 22, 22, 24, 'a')
    rect(g, 10, 24, 10, 29, 'a'); rect(g, 20, 24, 21, 29, 'c'); rect(g, 10, 29, 21, 29, 'c')
    rect(g, 13, 23, 18, 23, 'b')
    rect(g, 14, 12 + DY, 17, 22, 'M')                      # mat de bois
    rect(g, 14, 12 + DY, 14, 22, 'L'); rect(g, 17, 12 + DY, 17, 22, 'D')
    rect(g, 13, 19, 18, 19, 'k'); put(g, 13, 19, 'h')      # lien de fer
    for i, (x0, x1) in enumerate(((8, 23), (8, 23), (9, 22), (10, 21), (11, 20), (12, 19))):     # coupe de fer
        rect(g, x0, 7 + DY + i, x1, 7 + DY + i, 'h')
    rect(g, 8, 7 + DY, 23, 7 + DY, 'g')
    rect(g, 8, 8 + DY, 8, 9 + DY, 'g')
    rect(g, 23, 8 + DY, 23, 10 + DY, 'k'); rect(g, 12, 12 + DY, 19, 12 + DY, 'k')
    if lit:
        rect(g, 9, 7 + DY, 22, 7 + DY, 'o')
        rect(g, 12, 7 + DY, 19, 7 + DY, 'y')
    else:
        rect(g, 9, 7 + DY, 22, 7 + DY, 'I')                # charbon eteint
        for x in (11, 15, 19):
            put(g, x, 7 + DY, 'c')


def fumee(g, x, y, n):
    for k in range(n):
        put(g, x + (1 if k % 2 else 0), y - 2 * k, 'S' if k == 0 else 's')


def torche(state, phase=0):
    g = blank()
    torche_base(g, state != 'off')
    by = 6 + DY
    if state == 'on':
        flame(g, 16, by, 9 + (1 if phase % 2 else 0), 3.3, phase * 1.57 + 0.3)
    elif state == 'half':
        flame(g, 16, by, 5, 2.4, 1.0)
        fumee(g, 21, by - 1, 2)
    elif state == 'low':
        flame(g, 16, by, 3, 1.4, 2.0)
        fumee(g, 21, by - 1, 3)
    elif state == 'off':
        fumee(g, 21, by - 1, 4)
    outline(g)
    return g


def brasero(phase):
    g = blank()
    for x0, x1 in ((6, 9), (22, 25)):                      # pieds
        rect(g, x0, 24, x1, 29, 'k')
        rect(g, x0, 24, x0, 29, 'h')
    rect(g, 14, 24, 17, 29, 'k'); rect(g, 14, 24, 14, 29, 'h')
    for i, (x0, x1) in enumerate(((3, 28), (3, 28), (4, 27), (5, 26), (7, 24), (9, 22), (11, 20))):   # vasque
        rect(g, x0, 17 + i, x1, 17 + i, 'h')
    rect(g, 3, 17, 28, 17, 'g')
    rect(g, 4, 18, 4, 19, 'g')
    for i, x1 in enumerate((28, 28, 27, 26, 24, 22, 20)):
        put(g, x1, 17 + i, 'k')
    rect(g, 9, 21, 23, 21, 'k')
    for x in (7, 12, 17, 22):                              # rivets
        put(g, x, 19, 'k')
    rect(g, 4, 17, 27, 17, 'o')                            # braises
    rect(g, 7, 17, 24, 17, 'y')
    for x in (6, 11, 16, 21, 25):
        put(g, x, 16, 'o')
    flame(g, 16, 16, 13 + (1 if phase % 2 else 0), 5.4, phase * 1.57 + 0.6, sway=2.4)
    outline(g)
    return g


# ---------------------------------------------------------------- cibles a symbole
def symbole(g, name, cx, cy, cols):
    for y, row in enumerate(SYMBOLS[name]):
        for x, c in enumerate(row):
            if c != '.':
                put(g, cx - 6 + x, cy - 6 + y, cols[c])


def cible(name, state):
    g = blank()
    rect(g, 4, 6, 27, 29, 'W')                             # socle de pierre pose au sol
    rect(g, 4, 6, 27, 7, 'X'); rect(g, 4, 6, 4, 29, 'X')
    rect(g, 27, 7, 27, 29, 'U'); rect(g, 4, 29, 27, 29, 'U')
    rect(g, 5, 27, 26, 28, 'V')
    for x, y in ((6, 9), (25, 9), (6, 25), (25, 25)):
        put(g, x, y, 'V')
    cx, cy = 16, 17
    for y in range(cy - 10, cy + 11):
        for x in range(cx - 10, cx + 11):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= 98:
                if state == 'inactive':
                    col = 'c' if d > 82 else 'b' if d > 70 else 'U'
                elif state == 'active':
                    col = 'O' if d > 82 else 'Y' if d > 70 else 'w'
                else:
                    col = 'w' if d > 82 else 'R' if d > 70 else 'r'
                put(g, x, y, col)
    if state == 'inactive':
        cols = {'l': 'a', 'm': 'X', 'd': 'W'}
        put(g, 8, 9, 'a')
    elif state == 'active':
        names = {'l': 'H', 'm': 'G', 'd': 'D'}
        nat = {'gland': {'l': 'L', 'm': 'M', 'd': 'D'}, 'racine': {'l': 'L', 'm': 'M', 'd': 'D'},
               'feuille': {'l': 'H', 'm': 'G', 'd': 'D'}}[name]
        cols = nat
    else:
        cols = {'l': 'w', 'm': 'w', 'd': 'e'}
    if state == 'active':
        for x, y in ((16, 4), (7, 12), (25, 12), (4, 4), (27, 4)):          # etincelles
            put(g, x, y, 'y')
    symbole(g, name, cx, cy, cols)
    outline(g)
    return g


def cible_chrono(k):
    """k = 0..4 : fraction restante (4 - k) / 4 de l'anneau, qui se vide dans le sens des aiguilles d'une montre."""
    g = blank()
    rect(g, 4, 6, 27, 29, 'W')
    rect(g, 4, 6, 27, 7, 'X'); rect(g, 4, 6, 4, 29, 'X')
    rect(g, 27, 7, 27, 29, 'U'); rect(g, 4, 29, 27, 29, 'U')
    rect(g, 5, 27, 26, 28, 'V')
    for x, y in ((6, 9), (25, 9), (6, 25), (25, 25)):
        put(g, x, y, 'V')
    cx, cy = 16, 17
    remain = (4 - k) / 4
    for y in range(cy - 10, cy + 11):
        for x in range(cx - 10, cx + 11):
            d = math.hypot(x - cx + 0.0, y - cy + 0.0)
            if d > 10.2:
                continue
            ang = (math.atan2(x - cx, -(y - cy)) % (2 * math.pi)) / (2 * math.pi)   # 0 en haut, sens horaire
            if d > 7.2:
                lit = ang < remain - 1e-9 or (remain >= 1)
                if lit:
                    col = 'Z' if d < 8.4 else 'C' if d < 9.4 else 'B'
                else:
                    col = 'V' if d < 9.4 else 'U'
            elif d > 6.2:
                col = 'k'
            else:
                if k < 4:
                    col = 'w' if d < 1.6 else 'y' if d < 3.4 else 'o' if d < 5 else 'O'
                else:
                    col = 'h' if d > 3.4 else 'g'
            put(g, x, y, col)
    for i in range(4):                                     # graduations (4 quarts)
        a = i * math.pi / 2
        for r in (7.5, 8.5, 9.5):
            put(g, round(cx + math.sin(a) * r), round(cy - math.cos(a) * r), '0')
    outline(g)
    return g


# ---------------------------------------------------------------- grilles
def grille_h(stage):
    """stage 0 fermee, 1-2 ouverture, 3 ouverte. Grille posee dans un mur nord/sud : on la voit de face."""
    g = blank()
    rect(g, 2, 2, 29, 7, 'W')                              # linteau
    rect(g, 2, 2, 29, 3, 'X')
    rect(g, 2, 7, 29, 7, 'U')
    rect(g, 2, 8, 4, 29, 'W'); rect(g, 27, 8, 29, 29, 'W')            # montants
    rect(g, 2, 8, 2, 29, 'X'); rect(g, 29, 8, 29, 29, 'U'); rect(g, 4, 8, 4, 29, 'V'); rect(g, 27, 8, 27, 29, 'V')
    rect(g, 2, 28, 29, 30, 'U'); rect(g, 2, 28, 29, 28, 'V')            # seuil
    outline(g)
    end = (27, 21, 14, 7)[stage]
    if end >= 9:
        for x in (7, 11, 15, 19, 23):
            rect(g, x, 8, x + 1, end, 'h')
            rect(g, x, 8, x, end, 'g'); rect(g, x + 1, 8, x + 1, end, 'k')
            put(g, x, end + 1 if end < 27 else end, 'k')
        cy = min(16, end - 3)
        if cy >= 9:
            rect(g, 5, cy, 26, cy + 1, 'h'); rect(g, 5, cy, 26, cy, 'g'); rect(g, 5, cy + 1, 26, cy + 1, 'k')
    if stage == 3:
        for x in (7, 11, 15, 19, 23):                       # bouts des barreaux remontes dans le linteau
            put(g, x, 8, 'k'); put(g, x + 1, 8, 'k')
        rect(g, 5, 8, 26, 8, 'I')
    return g


def grille_v(stage):
    """Grille posee dans un mur est/ouest : bande etroite vue de cote, barreaux = echelons entre deux montants."""
    g = blank()
    rect(g, 9, 2, 22, 5, 'W'); rect(g, 9, 2, 22, 2, 'X'); rect(g, 9, 5, 22, 5, 'U')          # chapiteau nord
    rect(g, 9, 26, 22, 30, 'W'); rect(g, 9, 26, 22, 26, 'X'); rect(g, 9, 30, 22, 30, 'U')   # seuil sud
    rect(g, 9, 6, 10, 25, 'W'); rect(g, 21, 6, 22, 25, 'W')
    rect(g, 9, 6, 9, 25, 'X'); rect(g, 22, 6, 22, 25, 'U'); rect(g, 10, 6, 10, 25, 'V')
    outline(g)
    ys = [[7, 11, 15, 19, 23], [7, 11, 15], [7], []][stage]
    for y in ys:
        rect(g, 11, y, 20, y + 1, 'h'); rect(g, 11, y, 20, y, 'g'); rect(g, 11, y + 1, 20, y + 1, 'k')
    if stage == 3:
        rect(g, 11, 6, 20, 6, 'I')
    return g


# ---------------------------------------------------------------- fleche enflammee
def fleche_en_flammes(k):
    g = OU.arrow()
    shaft = [[g[y][x] for x in range(32)] for y in range(32)]
    ph = k * 2.1
    layer = blank()
    for x in range(7, 27):
        f = (x - 7) / 19
        hh = 3.4 * f ** 0.8 + 0.6 * math.sin(ph + x * 0.9) * f
        for y in range(15 - 4, 15 + 5):
            dy = abs(y - 15)
            if dy <= hh:
                put(layer, x, y, 'o' if dy > hh * 0.62 else 'y')
    for x in range(14, 23):                                 # coeur blanc pres de la pointe
        put(layer, x, 15, 'w')
        if x > 21:
            put(layer, x, 14 + (k % 2), 'w')
    rnd_sparks = [((5, 12), (3, 18)), ((4, 18), (7, 11)), ((6, 19), (2, 13))][k]
    for x, y in rnd_sparks:
        put(layer, x, y, 'y')
    put(layer, 9 + k * 2, 12 - (k % 2), 'o')
    put(layer, 11 + (k * 3) % 5, 19, 'o')
    for y in range(32):
        for x in range(32):
            if layer[y][x] != '.' and shaft[y][x] in ('.', '7') and not (x >= 25):
                g[y][x] = layer[y][x]
    for x in range(22, 25):                                 # pointe : un peu de feu au-dessus
        put(g, x, 13 - (k + x) % 2, 'o')
    return g


def main():
    os.makedirs(PUZ, exist_ok=True)
    out = {
        'plaque_pression': [plaque(False), plaque(True)],
        'levier': [levier(False), levier(True)],
        'torche': [torche('off')] + [torche('on', p) for p in range(4)] + [torche('half'), torche('low')],
        'brasero': [brasero(p) for p in range(4)],
        'cible_chrono': [cible_chrono(k) for k in range(5)],
        'grille_h': [grille_h(s) for s in range(4)],
        'grille_v': [grille_v(s) for s in range(4)],
    }
    for n in ('gland', 'racine', 'feuille'):
        out['cible_' + n] = [cible(n, s) for s in ('inactive', 'active', 'erreur')]
    sheets = {n: sheet(f) for n, f in out.items()}
    for n, s in sheets.items():
        CF.save_png(os.path.join(PUZ, n + '.png'), s)
    fl = sheet([fleche_en_flammes(k) for k in range(3)], OU.PAL)
    CF.save_png(os.path.join(ITEMS, 'fleche_enflammee.png'), fl)
    if len(sys.argv) > 1:
        d = sys.argv[1]
        os.makedirs(d, exist_ok=True)
        dalle = (154, 148, 140, 255)
        sol = (86, 116, 111, 255)
        for fond, tag in ((dalle, 'dalle'), (sol, 'soussol')):
            groups = [('plaque_pression', 'levier'), ('torche', 'brasero'),
                      ('cible_gland', 'cible_racine', 'cible_feuille'), ('cible_chrono', 'grille_h', 'grille_v')]
            for gi, names in enumerate(groups):
                rows = [sheets[n] for n in names]
                wmax = max(len(r[0]) for r in rows)
                img = []
                for r in rows:
                    for y in range(32):
                        img.append([p if p[3] else fond for p in r[y]] + [fond] * (wmax - len(r[0])))
                CF.save_png(os.path.join(d, f'{tag}_{gi}_x6.png'), img, 6)
        fb = [[p if p[3] else dalle for p in row] for row in fl]
        CF.save_png(os.path.join(d, 'fleche_enflammee_x8.png'), fb, 8)
        norm = [[p if p[3] else dalle for p in row] for row in rgba_sheet_arrow()]
        CF.save_png(os.path.join(d, 'fleche_normale_x8.png'), norm, 8)


def rgba_sheet_arrow():
    return OU.to_rgba(OU.arrow())


if __name__ == '__main__':
    main()
