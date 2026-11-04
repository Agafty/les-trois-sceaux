"""Images du générique — Les Trois Sceaux (PLACEHOLDERS à retoucher).

Usage : python tools/sprites/generique.py
  art/ui/generique_logo.png    128x128 : le corbeau et les trois cercles (forêt, montagne, lac) réunis dans un anneau d'or unique
  art/ui/generique_fin.png     96x64   : l'enclume de la forge de Corvan, le corbeau posé dessus
  art/items/sceau_unique_24.png 24x24  : le sceau unique à la taille des autres icônes d'objets (sceau_*.png)
Réutilise le corbeau de corbeau.py (raven_logo) et le mini encodeur PNG de coffres.py (pas de Pillow).
"""
import math
import os

import corbeau as C
from corbeau import PAL, shaded, ell, poly, raven_logo
from coffres import blank, put, rect, outline, save_png, background
from corbeau import to_rgba

PAL.update({'Y': '#fff0a0', 'y': '#e8c040', 'z': '#9a6a20', 'Z': '#6a4418',
            'k': '#8a8e9c', 'K': '#5c6070', 'L': '#3a3c4c', 'J': '#c8ccd8'})
OUT = os.path.join(C.ROOT, 'ui')


def ring(g, cx, cy, r, cols, th):
    h, w = len(g), len(g[0])
    for y in range(h):
        for x in range(w):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if abs(d - r) <= th:
                l = -((x + .5 - cx) * .6 + (y + .5 - cy) * .8) / r
                g[y][x] = cols[0] if l > .55 else cols[1] if l > -.45 else cols[2]


def logo():
    g = blank(128, 128)
    ring(g, 64, 64, 58, 'Yyz', 3.2)                         # anneau d'or : les trois n'en font plus qu'un
    for cx, cy, c in ((64, 40, 'Ggf'), (44, 76, 'Rrq'), (84, 76, 'Wvu')):
        ring(g, cx, cy, 26, c, 2.3)
    # étincelles d'or là où les trois cercles se rejoignent
    for x, y in ((64, 58), (53, 64), (75, 64), (64, 84), (64, 70)):
        put(g, x, y, 'Y')
    outline(g)
    r = raven_logo()
    for y in range(128):
        for x in range(128):
            if r[y][x] != '.':
                g[y][x] = r[y][x]
    return g


def fin():
    g = blank(96, 64)
    # enclume : pied, taille, table avec bigorne à gauche (lumière en haut à gauche)
    rect(g, 26, 56, 70, 62, 'K')
    rect(g, 26, 56, 70, 57, 'k')
    rect(g, 32, 48, 64, 55, 'K')
    rect(g, 32, 48, 33, 55, 'k')
    rect(g, 36, 40, 60, 47, 'K')
    rect(g, 36, 40, 37, 47, 'k')
    for y in range(34, 40):                                  # table
        rect(g, 22 + (y - 34) * 0, y, 74, y, 'k' if y == 34 else 'K')
    rect(g, 22, 34, 74, 34, 'J')
    for i in range(0, 14):                                   # bigorne
        rect(g, 8 + i, 34 + i // 5, 22, 34 + i // 5 + (1 if i > 6 else 3 - i // 4), 'k')
    rect(g, 10, 34, 22, 35, 'J')
    rect(g, 74, 34, 80, 37, 'K')
    rect(g, 74, 34, 80, 34, 'k')
    for x, y in ((30, 36), (44, 37), (58, 36), (66, 38)):    # marques de frappe
        put(g, x, y, 'L')
    # corbeau perché sur la table (3/4 de face, tourné vers la gauche)
    shaded(g, ell(52, 24, 12, 11), 52, 24, 12, 11, 'dbaa')                 # corps
    shaded(g, poly([(60, 28), (74, 40 - 6), (70, 36), (56, 34)]), 66, 32, 8, 6, 'bbaa')   # queue
    shaded(g, ell(46, 12, 7, 7), 46, 12, 7, 7, 'dbba')                      # tête
    for i in range(6):                                                      # bec
        rect(g, 38 - i // 2, 12 + i // 2, 39 - i // 2 + 1, 12 + i // 2, 'o')
    put(g, 38, 11, 'p')
    rect(g, 43, 10, 44, 11, 'e')                                            # oeil
    shaded(g, ell(56, 24, 7, 8), 56, 24, 7, 8, 'bbaa')                      # aile repliée
    for x in (47, 52):                                                      # pattes
        rect(g, x, 34, x, 33, 'p')
        put(g, x - 1, 33, 'p')
    # petit éclat d'or : le sceau unique posé devant lui
    rect(g, 60, 26, 60, 26, 'y')
    outline(g)
    return g


def sceau_24():
    """Même dessin que finale_art.sceau_unique, redessiné en 24x24."""
    N = 24
    k = N / 32.0
    cols = {'r': ('#9ad060', '#5a8a3c', '#2e5a2c'), 'm': ('#f0a050', '#c06a30', '#7a3a20'),
            'l': ('#8adcf0', '#3c7ac0', '#203e7a')}
    cen = {'r': (16 * k, 12 * k), 'm': (11.5 * k, 19.5 * k), 'l': (20.5 * k, 19.5 * k)}

    def c(h):
        return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    px = [[(0, 0, 0, 0)] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - N / 2.0, y + 0.5 - N / 2.0
            d = math.hypot(dx, dy)
            if d > 15.2 * k:
                continue
            if d > 13.2 * k:
                px[y][x] = c('#9a6a20') if (dx + dy) > 3 else c('#e8c040')
                continue
            inside = [n for n, (cx, cy) in cen.items() if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= 8 * k]
            if len(inside) == 3 or d < 3.2 * k:
                px[y][x] = c('#fff4b8') if d < 2.0 * k else c('#e8c040')
            elif len(inside) == 2:
                px[y][x] = c('#f4ecd0') if (x + y) % 2 else c('#e8c040')
            elif len(inside) == 1:
                hi, md, dk = cols[inside[0]]
                cx, cy = cen[inside[0]]
                v = (x + 0.5 - cx) * 0.6 + (y + 0.5 - cy) * 0.8
                px[y][x] = c(hi if v < -2.2 else dk if v > 3 else md)
            else:
                px[y][x] = c('#3a2a4e') if d > 9 * k else c('#4e3a66')
    out = [row[:] for row in px]
    for y in range(N):
        for x in range(N):
            if px[y][x][3] == 0 and any(0 <= y + b < N and 0 <= x + a < N and px[y + b][x + a][3]
                                        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = c('#1b1420')
    return out


def main():
    lg, fn = to_rgba(logo()), to_rgba(fin())
    save_png(os.path.join(OUT, 'generique_logo.png'), lg)
    save_png(os.path.join(OUT, 'generique_fin.png'), fn)
    save_png(os.path.join(C.ROOT, 'items', 'sceau_unique_24.png'), sceau_24())
    import sys
    if len(sys.argv) > 1:
        d = sys.argv[1]
        os.makedirs(d, exist_ok=True)
        for nom, px, s in (('logo', lg, 4), ('fin', fn, 6)):
            save_png(os.path.join(d, 'apercu_%s.png' % nom), background(px, (40, 34, 60, 255)), s)


if __name__ == '__main__':
    main()
