"""Objets de cÅ“ur : rÃ©ceptacle de cÅ“ur et quart de cÅ“ur (+ icÃ´ne HUD de quart de cÅ“ur).
MÃªme moteur/palette que pickups.py et hud.py.

Usage : python heart_items.py  ->  art/items/heart_items.png / .json / _frames.tres
                                   art/ui/quart_coeur_hud.png
Planche de cases 32x32, une ligne par animation : receptacle, quart_coeur (3 images chacune).
Objet centrÃ© en x, bas de case = sol.
"""
import os

import pickups  # noqa: F401  (installe l'encodeur PNG de secours si Pillow est absent)
from enemy_lib import build_enemy
import hud

ITEMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'art', 'items')

# MoitiÃ© gauche (interieur) du grand coeur : 8 colonnes x 14 lignes -> 16 de large en miroir
HALF = ["..#####.", ".#######", "########", "########", "########", "########", "########",
        ".#######", "..######", "...#####", "....####", ".....###", "......##", ".......#"]
FULL = [r + r[::-1] for r in HALF]


def shade(mask, rim_all):
    """mask : liste de listes de bool. Retourne une grille de caracteres avec contour,
    liserÃ© dorÃ© (haut/gauche), ombre (bas/droite) et reflet."""
    h, w = len(mask), len(mask[0])
    g = [['.'] * (w + 2) for _ in range(h + 2)]

    def m(x, y):
        return 0 <= x < w and 0 <= y < h and mask[y][x]
    for y in range(-1, h + 1):
        for x in range(-1, w + 1):
            if m(x, y):
                if not m(x - 1, y) or not m(x, y - 1):
                    c = 'K'
                elif not m(x + 1, y) or not m(x, y + 1):
                    c = 'F'
                else:
                    c = '4'
                if rim_all and c == 'F':
                    c = 'K'
                g[y + 1][x + 1] = c
            elif any(m(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                g[y + 1][x + 1] = '0'
    return g


def to_mask(rows):
    return [[c != '.' for c in r] for r in rows]


def place(g, x0, bottom=31):
    out = [['.'] * 32 for _ in range(32)]
    y0 = bottom - len(g) + 1
    for j, r in enumerate(g):
        for i, c in enumerate(r):
            if c != '.':
                out[y0 + j][x0 + i] = c
    return out


def sparkle(o, cx, cy, big):
    pts = [(0, 0)] + ([(-1, 0), (1, 0), (0, -1), (0, 1)] if big else [])
    for dx, dy in pts:
        o[cy + dy][cx + dx] = '2' if (dx, dy) == (0, 0) else 'K'


def highlight(g, x, y, size):
    for j in range(size):
        for i in range(size - j):
            if g[y + j][x + i] in '4K':
                g[y + j][x + i] = 'g'


def receptacle(frame):
    g = shade(to_mask(FULL), frame == 1)
    # reflet (haut gauche) : plus large a l'image 1, petit a l'image 2
    highlight(g, 2, 3, (2, 3, 2)[frame])
    if frame == 1:
        g[3][3] = '2'
    o = place(g, 7)
    top = 31 - len(g) + 1
    if frame == 1:
        sparkle(o, 5, top + 1, True)
        sparkle(o, 27, top + 9, False)
    if frame == 2:
        sparkle(o, 26, top + 2, False)
        sparkle(o, 4, top + 9, True)
    return o


# quart superieur gauche : 8 colonnes x 7 lignes de l'interieur, bords internes nets
QUART = [r for r in HALF[:10]]


def quart(frame):
    g = shade(to_mask(QUART), frame == 1)
    h, w = len(QUART), len(QUART[0])
    for j in range(h):                      # bords de coupe : liseré clair
        if QUART[j][w - 1] == '#':
            g[j + 1][w] = 'K'
    for i in range(w):
        if QUART[h - 1][i] == '#':
            g[h][i + 1] = '2'
    highlight(g, 2, 3, (2, 3, 2)[frame])
    o = place(g, 11)
    top = 31 - len(g) + 1
    if frame == 1:
        sparkle(o, 8, top - 2, True)
        sparkle(o, 23, top + 5, False)
    if frame == 2:
        sparkle(o, 22, top - 1, False)
        sparkle(o, 7, top + 4, True)
    return o


def quart_hud():
    """Coeur 16x16 divise en 4, quart superieur gauche rempli."""
    rows = hud.heart_rows(hud.FULL, hud.EMPTY)       # 14 x 12, a (1, 2)
    g = hud.blank(16, 16)
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c == '.':
                continue
            full = i < 7 and j < 6
            if c == '0':
                c = '0' if full else 'k'
            elif not full:
                c = hud.EMPTY.get(c, c)
            g[j + 2][i + 1] = c
    for j, r in enumerate(rows):                    # croix de separation
        for i, c in enumerate(r):
            if c in '4gFJI5' and (i == 6 or j == 5):
                g[j + 2][i + 1] = 'k' if not (i < 6 and j < 5) else '0'
    return g


anims = [('receptacle', [receptacle(f) for f in range(3)], 6.0, True),
         ('quart_coeur', [quart(f) for f in range(3)], 6.0, True)]

if __name__ == '__main__':
    os.makedirs(ITEMS, exist_ok=True)
    build_enemy(ITEMS, 'heart_items', anims, folder='items')
    hud.save_png(os.path.join(hud.OUT, 'quart_coeur_hud.png'), hud.to_rgba(quart_hud()))
    print('ok')
