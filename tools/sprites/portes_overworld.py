"""Images des `Porte` d'overworld — Les Trois Sceaux.

Usage : python tools/sprites/portes_overworld.py
Produit dans art/puzzles/ (comme porte_cle.png : une planche, fermée puis ouverte) :
  porte_pont_levis.png  128x64   2 images de 64x64 : pont-levis relevé, puis abaissé (2x2 cases)
  porte_tronc.png       128x32   2 images de 64x32 : tronc en travers avec la hache de Tobias, puis rien (passage libre)
  porte_rocher.png       64x32   2 images de 32x32 : rocher, puis rien
  porte_eboulis.png      64x32   2 images de 32x32 : éboulis de rochers, puis rien
Même style que le village et la forêt (palette de foret.py / village_art*.py).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art_lib import *  # noqa: F401,F403,E402
from art_lib import P, O, Cv, T, rnd, mass, F  # noqa: E402
import village_art1 as V  # noqa: E402
from tsplan import save_png, ROOT  # noqa: E402

OUT = os.path.join(ROOT, 'art', 'puzzles')


def hstack(images):
    h = len(images[0])
    return [sum((im[y] for im in images), []) for y in range(h)]


def empty(w, h):
    return [[None] * w for _ in range(h)]


def pont_levis():
    raised = V.raised_bridge().p
    lowered = V.lowered_bridge(64).p
    return hstack([raised, lowered])


def tronc():
    cv = Cv(64, 32)
    for x in range(4, 60):                                        # ombre au sol
        for y in range(26, 30):
            if (x + y) % 2 == 0 and ((x - 32) / 28.0) ** 2 + ((y - 28) / 3.0) ** 2 <= 1:
                cv.p[y][x] = P['g_dk']
    for y in range(8, 27):                                        # fût
        for x in range(4, 60):
            v = y - 8
            c = P['b_lt'] if v < 4 else P['b_md'] if v < 13 else P['b_dk']
            if (x * 5 + y * 3) % 17 == 0 and 4 < v < 14:
                c = P['b_dk']
            if (x + 3) % 9 == 0 and v > 2 and v % 5 != 0:
                c = P['b_md'] if c != P['b_md'] else P['b_dk']
            cv.p[y][x] = c
    for y in range(9, 26):                                        # bout coupé à gauche
        for x in range(2, 9):
            if ((x - 7) / 5.0) ** 2 + ((y - 17) / 9.0) ** 2 <= 1:
                cv.p[y][x] = P['pl_lt'] if ((x - 7) ** 2 + (y - 17) ** 2) % 7 else P['pk_lt']
    for r in (2, 4, 6):
        for a in range(0, 360, 20):
            import math
            cv.set(int(6 + r * 0.7 * math.cos(math.radians(a))), int(17 + r * 1.3 * math.sin(math.radians(a))), P['pk_md'])
    for x in range(16, 30):                                       # mousse
        cv.set(x, 8, P['g_md'])
        cv.set(x + 1, 9, P['g_lt'])
    for x in range(40, 52):
        cv.set(x, 8, P['g_md'])
    for y in range(3, 15):                                        # manche de la hache plantée
        cv.set(41 + (y - 3) // 5, y, P['b_lt'] if y % 2 else P['pk_md'])
        cv.set(42 + (y - 3) // 5, y, P['b_dk'])
    for y in range(3, 10):                                        # fer de la hache
        for x in range(34, 41):
            if abs(x - 38) <= 3 - (y - 3) * 0.3:
                cv.set(x, y, P['m_hi'] if x < 38 else P['m_lt'] if y < 7 else P['m_md'])
    cv.outline()
    return hstack([cv.p, empty(64, 32)])


def rocher():
    cv = Cv()
    for x in range(2, 30):
        for y in range(26, 30):
            if (x + y) % 2 == 0 and ((x - 16) / 14.0) ** 2 + ((y - 28) / 3.0) ** 2 <= 1:
                cv.p[y][x] = P['g_dk']
    mass(cv, [(16, 16, 13, 12), (9, 21, 8, 7), (23, 20, 8, 8)], (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 81, 0.35)
    for (x0, y0, x1, y1) in ((13, 9, 17, 15), (17, 15, 14, 21), (22, 12, 20, 18)):
        cv.line(x0, y0, x1, y1, P['k_dk'])
    for x in range(8, 22):                                        # mousse sur le dessus
        if rnd(x, 1, 4) < 0.6:
            cv.set(x, 6 + (x % 3), P['g_md'])
    cv.outline()
    return hstack([cv.p, empty(32, 32)])


def eboulis():
    cv = V.rubble(32, 31)
    # base plus dense : on ajoute une rangée de pierres au sol
    for (cx, cy, rx, ry) in ((6, 26, 6, 4), (16, 27, 7, 4), (26, 26, 6, 4)):
        sub = Cv()
        F.mass(sub, [(cx, cy, rx, ry)], (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), int(cx), 0.3)
        sub.outline()
        for y in range(T):
            for x in range(T):
                if sub.p[y][x] is not None:
                    cv.p[y][x] = sub.p[y][x]
    return hstack([cv.p, empty(32, 32)])


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, px in (('porte_pont_levis', pont_levis()), ('porte_tronc', tronc()), ('porte_rocher', rocher()), ('porte_eboulis', eboulis())):
        save_png(os.path.join(OUT, name + '.png'), px)
        print(name, len(px[0]), 'x', len(px))


if __name__ == '__main__':
    main()
