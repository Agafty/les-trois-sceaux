"""Intérieurs, dessin final, partie 3 : foyer de forge FROID (cendres, sans flammes) — ids 200, 201 / 208, 209.

Même dessin que le foyer allumé (hotte, manteau, ouverture : interieurs_art1.foyer) ; seul le feu est remplacé par des
cendres grises, des bûches noircies et quelques braises éteintes. Même collision pleine.
"""
from art_lib import P, O, Cv, T, rnd
import interieurs_art1
from interieurs_art1 import REG

FIRE = {P['fi_d'], P['fi_r'], P['fi_o'], P['fi_y']}


def foyer_froid():
    cv = interieurs_art1.foyer()                 # copie neuve (la fonction reconstruit le canevas)
    for y in range(36, 64):
        for x in range(9, 55):
            if cv.p[y][x] not in FIRE:
                continue
            d = ((x - 31.5) / 20.0) ** 2 + ((y - 62) / 20.0) ** 2
            c = P['s_md']                          # cendre
            if d < 0.55 + 0.1 * rnd(x, y, 5):
                c = P['s_lt'] if rnd(x, y, 9) > 0.35 else P['m_md']
            if d < 0.2:
                c = P['m_lt'] if rnd(x, y, 4) > 0.5 else P['m_md']
            cv.p[y][x] = c
    # bûches noircies posées dans l'âtre
    for (x0, x1, y) in ((16, 31, 57), (28, 45, 59), (22, 38, 55)):
        for x in range(x0, x1 + 1):
            cv.p[y][x] = P['s_dk']
            cv.p[y + 1][x] = P['O']
        cv.p[y][x0] = P['b_dk']
        cv.p[y][x1] = P['b_dk']
        for x in range(x0 + 2, x1 - 1, 4):
            cv.p[y][x] = P['s_md']
    # quelques braises mortes
    for x, y in ((20, 61), (35, 56), (43, 61), (27, 53)):
        cv.p[y][x] = P['fi_d']
    return cv


_FROID = foyer_froid()
for _n, (_c, _r) in dict(foyer_froid_haut_g=(0, 0), foyer_froid_haut_d=(1, 0), foyer_froid_bas_g=(0, 1), foyer_froid_bas_d=(1, 1)).items():
    REG[_n] = (lambda n, t, c=_c, r=_r: _FROID.crop(c * T, r * T))
