"""Village, dessin final, partie 4 : décor de fête (guirlandes, lampion, fanions, banderole) — ids 368 à 375, calque Dessus."""
import math

from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, box, vline
from village_art1 import REG, reg

# (clair, moyen, sombre) des fanions
FLAGS = [(P['ra_hi'], P['ra_lt'], P['ra_dk']), (P['rc_hi'], P['rc_lt'], P['rc_md']),
         (P['gl_hi'], P['gl_md'], P['gl_dk']), (P['g_hi'], P['g_md'], P['g_dk'])]
STR = P['pk_dk']


def pennant(cv, cx, y0, col, w=5, h=5):
    """Fanion triangulaire pendu à la ficelle en (cx, y0), pointe en bas."""
    hi, md, dk = col
    for k in range(h):
        half = (w - 1) // 2 * (h - k) // h
        for x in range(cx - half, cx + half + 1):
            c = md
            if x == cx - half or k == 0:
                c = hi
            elif x == cx + half:
                c = dk
            cv.set(x, y0 + k, c)


def garland(part):
    cv = Cv()
    flags = {'g': [(12, 0), (20, 1), (28, 2)], 'm': [(4, 3), (12, 0), (20, 1), (28, 2)], 'd': [(4, 3), (12, 0), (20, 1)]}[part]
    x0, x1, ya, yb = {'g': (4, 31, 6, 12), 'm': (0, 31, 12, 12), 'd': (0, 27, 12, 6)}[part]
    sag = 4

    def ys(x):
        t = (x - x0) / float(x1 - x0)
        return ya + (yb - ya) * t + sag * math.sin(math.pi * t)
    for x in range(x0, x1 + 1):
        cv.set(x, int(round(ys(x))), STR)
    for cx, ci in flags:
        pennant(cv, cx, int(round(ys(cx))) + 1, FLAGS[ci])
    nail = {'g': 3, 'd': 27}.get(part)
    if nail:                                  # clou dans le mur
        cv.rect(nail, 5, nail + 1, 6, P['m_md'])
        cv.set(nail, 5, P['m_hi'])
    cv.outline()
    return cv.p


for _p in 'gmd':
    REG['guirlande_' + _p] = (lambda n, t, p=_p: garland(p))


@reg('lampion')
def lampion(name, tile):
    cv = Cv()
    vline(cv, 16, 0, 5, STR)
    box(cv, 13, 5, 18, 7, P['m_lt'], P['m_md'], P['m_dk'])
    for y in range(8, 25):
        for x in range(6, 27):
            e = ((x + 0.5 - 16) / 10.5) ** 2 + ((y + 0.5 - 16) / 8.5) ** 2
            if e > 1:
                continue
            c = P['ra_lt']
            if x < 13 and y < 16:
                c = P['ra_hi']
            elif x > 20 or e > 0.8:
                c = P['ra_md']
            if abs(x - 15.5) < 1:
                c = P['fi_o']
            if e < 0.18:
                c = P['fi_y']
            cv.set(x, y, c)
    for xr in (10, 22):                      # nervures
        for y in range(9, 24):
            if cv.get(xr, y) not in (None, O):
                cv.set(xr, y, P['ra_dk'])
    box(cv, 13, 25, 18, 27, P['m_lt'], P['m_md'], P['m_dk'])
    vline(cv, 16, 28, 30, P['rc_lt'])
    cv.set(15, 30, P['rc_hi'])
    cv.set(17, 30, P['rc_md'])
    cv.outline()
    return cv.p


@reg('fanion')
def fanion(name, tile):
    """Fanions tendus : se répète à l'horizontale (ficelle de bord à bord, 2 grands fanions par case)."""
    cv = Cv()
    for x in range(T):
        cv.set(x, 4, STR)
    pennant(cv, 8, 5, FLAGS[0], w=9, h=9)
    pennant(cv, 24, 5, FLAGS[1], w=9, h=9)
    # contour sous la ficelle et autour des fanions seulement (pas au-dessus : raccord entre cases)
    pts = [(x, y) for y in range(5, T) for x in range(T) if cv.p[y][x] is None and any(
        cv.get(x + dx, y + dy) not in (None, O) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        cv.p[y][x] = O
    return cv.p


def banner(part):
    cv = Cv()
    x0 = 6 if part == 'g' else 0
    x1 = 25 if part == 'd' else 31
    top, bot = 8, 21
    for y in range(top, bot + 1):
        for x in range(x0, x1 + 1):
            c = P['ra_lt']
            if y == top:
                c = P['ra_hi']
            elif y >= bot - 1:
                c = P['ra_md']
            if y in (top + 2, bot - 3):
                c = P['rc_lt']
            elif y in (top + 3, bot - 4):
                c = P['rc_md']
            cv.set(x, y, c)
    if part == 'm':                           # losange doré
        for y in range(11, 19):
            for x in range(8, 24):
                if abs(x - 15.5) / 7.5 + abs(y - 14.5) / 3.8 <= 1.0:
                    cv.set(x, y, P['rc_hi'] if y < 14 else P['rc_lt'])
        cv.set(15, 14, P['ra_lt'])
        cv.set(16, 14, P['ra_lt'])
    else:                                     # petite étoile
        cx = 13 if part == 'g' else 14
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.set(cx + dx, 14 + dy, P['rc_hi'] if dy <= 0 else P['rc_lt'])
    for x in range(x0 if part != 'g' else 3, 26 if part == 'd' else T):   # corde de suspension
        cv.set(x, 7, STR)
    if part == 'g':                           # tige de bois à gauche, pommeau doré
        box(cv, 3, 6, 5, 24, P['pk_hi'], P['pk_lt'], P['pk_dk'])
        box(cv, 2, 4, 6, 6, P['rc_hi'], P['rc_lt'], P['rc_md'])
        for y in range(top, bot + 1):
            cv.set(6, y, P['ra_dk'])
    if part == 'd':                           # tige de bois à droite, pommeau doré
        box(cv, 26, 6, 28, 24, P['pk_hi'], P['pk_lt'], P['pk_dk'])
        box(cv, 25, 4, 29, 6, P['rc_hi'], P['rc_lt'], P['rc_md'])
    for x in range(x0 + 1, x1):               # franges dorées
        if x % 3 == 0 and cv.get(x, bot) is not None:
            cv.set(x, bot + 1, P['rc_lt'])
            cv.set(x, bot + 2, P['rc_md'])
    cv.outline()
    return cv.p


for _p in 'gmd':
    REG['banderole_' + _p] = (lambda n, t, p=_p: banner(p))
