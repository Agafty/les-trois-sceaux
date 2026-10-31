"""Image de la Porte `rocher` dans l'eau (gué de l'îlot du lac) — Les Trois Sceaux.

Usage : python tools/sprites/porte_rocher_eau.py
Produit art/puzzles/porte_rocher_eau.png : 64x32, 2 images de 32x32 (rocher dans l'eau, puis rien).
Même rocher que porte_rocher.png, mais sans mousse ni ombre d'herbe : base mouillée, anneau d'écume, nappe d'eau autour.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art_lib import *  # noqa: F401,F403,E402
from art_lib import P, Cv, T, mass  # noqa: E402
from tsplan import save_png, ROOT  # noqa: E402


def rocher_eau():
    cv = Cv()
    for x in range(1, 31):                                  # sillage d'eau autour de la base
        for y in range(23, 31):
            if ((x - 16) / 15.0) ** 2 + ((y - 27) / 4.0) ** 2 <= 1:
                cv.p[y][x] = P['w_lt'] if (x + y) % 3 else P['w_hi']
    mass(cv, [(16, 15, 13, 11), (9, 20, 8, 7), (23, 19, 8, 8)], (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 81, 0.35)
    for (x0, y0, x1, y1) in ((13, 8, 17, 14), (17, 14, 14, 20), (22, 11, 20, 17)):
        cv.line(x0, y0, x1, y1, P['k_dk'])
    for x in range(3, 29):                                  # ligne d'eau : le bas du rocher est mouillé
        for y in (23, 24):
            if cv.p[y][x] is not None and cv.p[y][x] not in (P['w_lt'], P['w_hi']):
                cv.p[y][x] = P['w_dk'] if y == 24 else P['w_md']
    for x in range(2, 30):
        if cv.p[26][x] is not None:
            cv.p[26][x] = P['foam'] if x % 2 else P['w_hi']
    cv.outline()
    return [r + [None] * 32 for r in cv.p]


if __name__ == '__main__':
    px = rocher_eau()
    save_png(os.path.join(ROOT, 'art', 'puzzles', 'porte_rocher_eau.png'), px)
    print('porte_rocher_eau 64 x 32')
