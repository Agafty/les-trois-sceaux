"""Mine Effondrée, dessin final, partie 1 : sols, terrains, murs, portes, escaliers, trous, eau, rails.

Palette : roche brun-gris chaude (sol), poussière de charbon sombre, murs bruns (dessus sombre, face claire), bois d'étais,
rails gris, cristaux cyan. Lumière en haut à gauche, contour sombre d'1 px. Les fonctions sont enregistrées par nom de tuile (REG).
La suite (décor, cristaux, arène, murs fissurés) est dans mine_art2.py.
"""
import math
import random

import art_lib as AL
from art_lib import P, O, Cv, T, rnd, vnoise, wset, rgba, mass, box, ell, hline, vline, dither, paste, mix, tint
from foret import SHALLOW, corners

EXTRA = dict(
    fl_hi='#a8946e', fl_lt='#8e7a62', fl_md='#76664f', fl_dk='#5c4e40', fl_dp='#40362e',            # sol de roche
    du_lt='#4e444c', du_md='#3c343c', du_dk='#2c262e',                                             # poussière de charbon
    cp_lt='#52434a', cp_md='#3e3238', cp_dk='#2c2429',                                             # dessus de mur
    wf_hi='#c0a888', wf_lt='#9a806c', wf_md='#80695a', wf_dk='#5e4c46', wf_dp='#463a3c',            # face de mur
    wd_hi='#c8946a', wd_lt='#a6764a', wd_md='#86583a', wd_dk='#5e3a22', wd_dp='#3e2616',            # bois d'étais
    mt_hi='#c8ccd8', mt_lt='#9aa0b0', mt_md='#6a7080', mt_dk='#3c4050',                            # métal, rails
    cy_w='#e4fcff', cy_hi='#8aeaf8', cy_lt='#4ac8e8', cy_md='#2a88c8', cy_dk='#1a4c8a', cy_dp='#14305e',  # cristaux cyan
    rd_hi='#ff9a84', rd_lt='#f0483c', rd_md='#c8242c', rd_dk='#8a1428',                            # cristal rouge
    ge_hi='#f8e070', ge_md='#d0a030', ge_dk='#8a6420',                                             # minerai d'or
    tl_hi='#c8fff0', tl_lt='#7fe8d0', tl_md='#3fc0a8', tl_dk='#2a9a9c', tl_dp='#1d7488', tl_dd='#14566a',   # passage
    hl_0='#0e0a14', hl_1='#1b1420', hl_2='#2a2030',                                               # trou
    ar_hi='#c4b4cc', ar_lt='#a494b4', ar_md='#84749a', ar_dk='#62547a', ar_dp='#463a5a',           # arène
    lamp_y='#f8d848', lamp_o='#e8a030',
)
P.update({k: rgba(v) for k, v in EXTRA.items()})
REG = {}


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


def raw(t):
    """Canevas Cv -> tuile (liste de lignes)."""
    return t.p if isinstance(t, Cv) else t


def blank_tile():
    return [[None] * T for _ in range(T)]


# ------------------------------------------------------------------ textures de sol
def floor_tex(kind='a'):
    hi, lt, md, dk = P['fl_hi'], P['fl_lt'], P['fl_md'], P['fl_dk']
    t = [[md] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 1) * 0.55 + vnoise(x, y, 16, 6) * 0.45
            t[y][x] = lt if n > 0.62 else dk if n < 0.34 else md
            if rnd(x, y, 8) < 0.045:
                t[y][x] = dk if rnd(x, y, 3) < 0.55 else lt
    r = random.Random({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}.get(kind, 9))
    if kind == 'b':
        for _ in range(8):
            x, y = r.randrange(1, 30), r.randrange(1, 30)
            wset(t, x, y, hi)
            wset(t, x + 1, y, lt)
            wset(t, x, y + 1, dk)
            wset(t, x + 1, y + 1, dk)
    if kind == 'c':                                   # dalles irrégulières
        for y in range(T):
            for x in range(T):
                if y % 11 == 5 or (x + 7 * (y // 11)) % 15 == 6:
                    t[y][x] = P['fl_dp']
                elif y % 11 == 4 or (x + 7 * (y // 11)) % 15 == 5:
                    t[y][x] = hi if rnd(x, y, 2) < 0.6 else lt
    if kind in ('d', 'e'):                            # fissures
        pts = ([(3, 5), (9, 11), (13, 10), (19, 17), (24, 20), (29, 28)] if kind == 'd'
               else [(16, 15), (8, 6), (16, 15), (25, 8), (16, 15), (22, 27), (16, 15), (6, 24)])
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            if kind == 'e' and (xa, ya) != (16, 15) and (xb, yb) != (16, 15):
                continue
            n = max(abs(xb - xa), abs(yb - ya))
            for i in range(n + 1):
                x, y = round(xa + (xb - xa) * i / n), round(ya + (yb - ya) * i / n)
                wset(t, x, y, P['fl_dp'])
                wset(t, x - 1, y - 1, hi) if (x + y) % 2 == 0 else None
    return t


FLOOR = floor_tex('a')


def dust_tex():
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 21) * 0.5 + vnoise(x, y, 4, 22) * 0.5
            t[y][x] = P['du_lt'] if n > 0.66 else P['du_dk'] if n < 0.32 else P['du_md']
            if rnd(x, y, 23) < 0.05:
                t[y][x] = P['du_lt'] if rnd(x, y, 24) < 0.5 else P['du_dk']
    return t


DUST = dust_tex()


@reg('sol_a')
def sol_a(n, d):
    return floor_tex('a')


@reg('sol_b')
def sol_b(n, d):
    return floor_tex('b')


@reg('sol_c')
def sol_c(n, d):
    return floor_tex('c')


@reg('sol_fissure_a')
def sol_fa(n, d):
    return floor_tex('d')


@reg('sol_fissure_b')
def sol_fb(n, d):
    return floor_tex('e')


@reg('poussiere')
def poussiere(n, d):
    return DUST


# ------------------------------------------------------------------ masques de terrain (même bruit que foret.terrain_tile)
def qmask(b, seed, amp=0.09):
    hg, hd, bg, bd = corners(b)
    m = [[False] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            u, v = (x + 0.5) / T, (y + 0.5) / T
            f = (hg * (1 - u) + hd * u) * (1 - v) + (bg * (1 - u) + bd * u) * v
            f += (vnoise(x, y, 8, seed) - 0.5) * amp * 2 + (vnoise(x, y, 16, seed + 1) - 0.5) * amp
            m[y][x] = f > 0.5
    return m


def dist_to_other(m, x, y, rmax=4):
    me = m[y][x]
    best = rmax + 1
    for dy in range(-rmax, rmax + 1):
        for dx in range(-rmax, rmax + 1):
            xx, yy = x + dx, y + dy
            if 0 <= xx < T and 0 <= yy < T and m[yy][xx] != me:
                best = min(best, max(abs(dx), abs(dy)))
    return best


def bits_of_name(d):
    plan = d['plan']
    return plan[1] if plan and plan[0] == 'terrain' else 0


@reg(*[f'poussiere_{s}' for s in ('bord_haut', 'bord_bas', 'bord_gauche', 'bord_droite', 'creux_hg', 'creux_hd', 'creux_bg', 'creux_bd',
                                  'coin_hg', 'coin_hd', 'coin_bg', 'coin_bd', 'diag')])
def poussiere_edge(n, d):
    b = bits_of_name(d)
    m = qmask(b, 31)
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            dd = dist_to_other(m, x, y, 2)
            if m[y][x]:
                t[y][x] = P['du_dk'] if dd <= 1 and rnd(x, y, 5) < 0.5 else DUST[y][x]
            else:
                t[y][x] = P['fl_dk'] if dd <= 1 and rnd(x, y, 6) < 0.45 else FLOOR[y][x]
    return t


# ------------------------------------------------------------------ eau souterraine
def eau_px(x, y):
    t = SHALLOW[y][x]
    return t


@reg(*[n for n in ['eau', 'eau_bord_haut', 'eau_bord_bas', 'eau_bord_gauche', 'eau_bord_droite', 'eau_creux_hg', 'eau_creux_hd',
                   'eau_creux_bg', 'eau_creux_bd', 'eau_coin_hg', 'eau_coin_hd', 'eau_coin_bg', 'eau_coin_bd']])
def eau(n, d):
    b = bits_of_name(d)
    m = qmask(b, 41)
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            dd = dist_to_other(m, x, y, 3)
            if m[y][x]:
                c = eau_px(x, y)
                if dd <= 1:
                    c = P['w_hi'] if rnd(x, y, 7) < 0.7 else P['foam']
                elif dd == 2 and rnd(x, y, 8) < 0.35:
                    c = P['w_lt']
                t[y][x] = c
            else:
                c = FLOOR[y][x]
                if dd <= 1:
                    c = P['fl_dp']
                elif dd == 2:
                    c = P['fl_dk']
                t[y][x] = c
    return t


# ------------------------------------------------------------------ trous
def pit_color(x, y, m):
    """Pixel dans un trou : paroi du fond visible sous le bord haut, ombre au centre."""
    for k in range(1, 5):
        if y - k >= 0 and not m[y - k][x]:
            return [P['wf_dk'], P['wf_dp'], P['cp_md'], P['hl_2']][k - 1] if k > 0 else None
    dd = dist_to_other(m, x, y, 2)
    if dd <= 1:
        return P['hl_1']
    return P['hl_1'] if rnd(x, y, 12) < 0.12 else P['hl_0']


@reg('trou', 'trou_bord_haut', 'trou_bord_bas', 'trou_bord_gauche', 'trou_bord_droite', 'trou_coin_hg', 'trou_coin_hd', 'trou_coin_bg', 'trou_coin_bd')
def trou(n, d):
    m = qmask(bits_of_name(d), 51, 0.07)
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            if m[y][x]:
                t[y][x] = pit_color(x, y, m)
            else:
                dd = dist_to_other(m, x, y, 2)
                c = FLOOR[y][x]
                if dd == 1:
                    c = P['fl_dp']
                elif dd == 2:
                    c = P['fl_dk'] if rnd(x, y, 13) < 0.6 else c
                if dd == 1 and ((x > 0 and m[y][x - 1]) is False) and y + 1 < T and m[y + 1][x]:
                    c = P['fl_hi']                           # lèvre éclairée au-dessus du trou
                t[y][x] = c
    return t


@reg('trou_passage', 'trou_passage_bord_haut', 'trou_passage_bord_bas', 'trou_passage_bord_gauche', 'trou_passage_bord_droite',
     'trou_passage_coin_hg', 'trou_passage_coin_hd', 'trou_passage_coin_bg', 'trou_passage_coin_bd')
def trou_passage(n, d):
    m = qmask(bits_of_name(d), 61, 0.05)
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            dd = dist_to_other(m, x, y, 4)
            if m[y][x]:
                if dd <= 1:
                    c = P['tl_dd']
                elif dd == 2:
                    c = P['tl_dp']
                elif dd == 3:
                    c = P['tl_dk']
                else:
                    c = P['tl_md'] if vnoise(x, y, 4, 71) < 0.55 else P['tl_lt']
                    if rnd(x, y, 14) < 0.05:
                        c = P['tl_hi']
                t[y][x] = c
            else:
                c = FLOOR[y][x]
                if dd == 1:
                    c = P['wd_dk']                             # cadre de planches
                elif dd == 2:
                    c = P['wd_md'] if (x // 3 + y // 3) % 2 else P['wd_lt']
                elif dd == 3:
                    c = P['wd_dk'] if rnd(x, y, 15) < 0.4 else c
                t[y][x] = c
    return t


# ------------------------------------------------------------------ murs
def cap_color(x, y):
    n = vnoise(x, y, 8, 5) * 0.6 + vnoise(x, y, 16, 9) * 0.4
    c = P['cp_lt'] if n > 0.64 else P['cp_dk'] if n < 0.36 else P['cp_md']
    r = rnd(x, y, 11)
    if r < 0.035:
        return P['cp_dk']
    if r > 0.975:
        return P['cp_lt']
    return c


def face_color(x, y):
    """Face avant : deux assises de roche taillée, reflet en haut, ombre en bas."""
    if y == 17:
        return P['wf_hi']
    if y == 31:
        return O
    if y == 24:
        return P['wf_dp']
    off = 0 if y < 24 else 9
    if (x + off) % 14 == 0 and y not in (18, 25):
        return P['wf_dp']
    n = vnoise(x, y, 8, 3) * 0.6 + rnd(x, y, 4) * 0.4
    if y in (18, 25):
        return P['wf_hi'] if n > 0.5 else P['wf_lt']
    if y in (23, 30):
        return P['wf_dk']
    return P['wf_lt'] if n > 0.66 else P['wf_dk'] if n < 0.27 else P['wf_md']


LIT = ('O', 'wf_hi', 'wf_lt', 'wf_md')
SHD = ('O', 'cp_dk', 'cp_dk', 'cp_md')


def wall(bits):
    tl, tr, bl, br = bits
    t = [[cap_color(x, y) for x in range(T)] for y in range(T)]
    n, s = not tl and not tr, not bl and not br
    w, e = not tl and not bl, not tr and not br

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t[y][x] = P[c] if isinstance(c, str) and c != 'O' else (O if c == 'O' else c)

    if n:
        for y in range(4):
            rect(0, y, 31, y, LIT[y])
    if w:
        for x in range(4):
            rect(x, 0, x, 31, LIT[x])
        rect(0, 0, 0, 31, 'O')
    if e:
        for k in range(4):
            rect(31 - k, 0, 31 - k, 31, SHD[k])
    if n and w:
        for y in range(4):
            for x in range(4):
                t[y][x] = P[LIT[min(x, y)]] if LIT[min(x, y)] != 'O' else O
    corner_hd = (n and e) or (not tr and tl and br)
    corner_hg = (not tl and tr and bl)
    if corner_hd:
        for y in range(4):
            for x in range(28, 32):
                k = LIT[y] if y <= 31 - x else SHD[31 - x]
                t[y][x] = O if k == 'O' else P[k]
    if corner_hg:
        for y in range(4):
            for x in range(4):
                k = LIT[min(x, y)]
                t[y][x] = O if k == 'O' else P[k]
    cols = []
    if s:
        cols.append((0, 31))
    if not br and bl and tr:
        cols.append((28, 31))
    if not bl and br and tl:
        cols.append((0, 3))
    for x0, x1 in cols:
        for y in range(17, 32):
            for x in range(x0, x1 + 1):
                t[y][x] = face_color(x, y)
    if s and w:
        for y in range(17, 32):
            t[y][0] = O
    if s and e:
        for y in range(17, 32):
            t[y][31] = O
    return t


WALLBITS = {16: (1, 1, 0, 0), 17: (0, 0, 1, 1), 18: (1, 0, 1, 0), 19: (0, 1, 0, 1), 20: (1, 1, 1, 0), 21: (1, 1, 0, 1), 22: (1, 0, 1, 1),
            23: (0, 1, 1, 1), 24: (0, 0, 0, 1), 25: (0, 0, 1, 0), 26: (0, 1, 0, 0), 27: (1, 0, 0, 0), 28: (1, 1, 1, 1), 29: (1, 0, 0, 1),
            30: (0, 1, 1, 0)}
WALLNAMES = {'mur_haut': 16, 'mur_bas': 17, 'mur_gauche': 18, 'mur_droite': 19, 'mur_coin_int_hg': 20, 'mur_coin_int_hd': 21,
             'mur_coin_int_bg': 22, 'mur_coin_int_bd': 23, 'mur_coin_ext_hg': 24, 'mur_coin_ext_hd': 25, 'mur_coin_ext_bg': 26,
             'mur_coin_ext_bd': 27, 'mur_plein': 28, 'mur_diag_a': 29, 'mur_diag_b': 30}
for _n, _i in WALLNAMES.items():
    REG[_n] = (lambda b: (lambda n, d: wall(b)))(WALLBITS[_i])


# ------------------------------------------------------------------ ombres sous les murs (trame, calque Decor)
def shade_tex(kind):
    t = blank_tile()
    for y in range(T):
        for x in range(T):
            dh = 1 - y / 9 if kind in ('haut', 'coin') else 0
            dg = 1 - x / 9 if kind in ('gauche', 'coin') else 0
            k = max(dh, dg)
            if k > 0 and (k > 0.65 or (k > 0.3 and (x + y) % 2 == 0) or (k > 0 and (x + y) % 4 == 0 and (x // 2 + y) % 2 == 0)):
                t[y][x] = (27, 20, 32, 255)
    return t


REG['ombre_mur_haut'] = lambda n, d: shade_tex('haut')
REG['ombre_mur_gauche'] = lambda n, d: shade_tex('gauche')
REG['ombre_mur_coin'] = lambda n, d: shade_tex('coin')


# ------------------------------------------------------------------ portes
def wood_post(t, x0, x1, y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = P['wd_md']
            if x == x0:
                c = P['wd_hi']
            elif x == x0 + 1:
                c = P['wd_lt']
            elif x == x1:
                c = P['wd_dk']
            if rnd(x, y, 17) < 0.08:
                c = P['wd_dk']
            t[y][x] = c
    for y in range(y0, y1 + 1):
        if x0 - 1 >= 0:
            t[y][x0 - 1] = O
        if x1 + 1 < T:
            t[y][x1 + 1] = O


def wood_beam(t, x0, x1, y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = P['wd_md']
            if y == y0:
                c = P['wd_hi']
            elif y == y0 + 1:
                c = P['wd_lt']
            elif y == y1:
                c = P['wd_dk']
            if rnd(x, y, 18) < 0.07:
                c = P['wd_dk']
            t[y][x] = c
    for x in range(x0, x1 + 1):
        if y0 - 1 >= 0:
            t[y0 - 1][x] = O
        if y1 + 1 < T:
            t[y1 + 1][x] = O


def dark_floor(t, x0, y0, x1, y1, vertical=True):
    """Sol de l'ouverture : de plus en plus sombre vers le fond."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = ((y1 - y) / max(1, y1 - y0)) if vertical else ((x1 - x) / max(1, x1 - x0))
            c = FLOOR[y][x]
            c = P['fl_dk'] if k < 0.35 else P['fl_dp'] if k < 0.7 else P['hl_1']
            if k < 0.35 and rnd(x, y, 19) < 0.4:
                c = FLOOR[y][x]
            t[y][x] = c


@reg('porte_haut')
def porte_haut(n, d):
    t = wall((1, 1, 0, 0))
    dark_floor(t, 7, 0, 24, 31, True)
    wood_post(t, 4, 6, 0, 31)
    wood_post(t, 25, 27, 0, 31)
    return t


@reg('porte_bas')
def porte_bas(n, d):
    t = wall((0, 0, 1, 1))
    dark_floor(t, 7, 0, 24, 31, False)
    for y in range(32):
        for x in range(7, 25):
            t[y][x] = P['fl_dk'] if y < 24 else P['fl_dp']
            if rnd(x, y, 20) < 0.3:
                t[y][x] = FLOOR[y][x]
    wood_post(t, 4, 6, 0, 31)
    wood_post(t, 25, 27, 0, 31)
    return t


@reg('porte_gauche')
def porte_gauche(n, d):
    t = wall((1, 0, 1, 0))
    for y in range(4, 28):
        for x in range(0, 32):
            k = x / 31
            t[y][x] = P['hl_1'] if k < 0.25 else P['fl_dp'] if k < 0.5 else P['fl_dk'] if k < 0.8 else FLOOR[y][x]
    wood_beam(t, 0, 31, 0, 3)
    wood_beam(t, 0, 31, 28, 31)
    return t


@reg('porte_droite')
def porte_droite(n, d):
    t = wall((0, 1, 0, 1))
    for y in range(4, 28):
        for x in range(0, 32):
            k = 1 - x / 31
            t[y][x] = P['hl_1'] if k < 0.25 else P['fl_dp'] if k < 0.5 else P['fl_dk'] if k < 0.8 else FLOOR[y][x]
    wood_beam(t, 0, 31, 0, 3)
    wood_beam(t, 0, 31, 28, 31)
    return t


@reg('porte_haut_dessus')
def porte_haut_dessus(n, d):
    t = blank_tile()
    wood_beam(t, 2, 29, 1, 9)
    for x in (6, 25):
        t[5][x] = P['mt_lt']
    return t


@reg('porte_bas_dessus')
def porte_bas_dessus(n, d):
    t = blank_tile()
    wood_beam(t, 2, 29, 5, 13)
    for x in (6, 25):
        t[9][x] = P['mt_lt']
    return t


@reg('porte_gauche_dessus')
def porte_gauche_dessus(n, d):
    t = blank_tile()
    wood_post(t, 2, 9, 0, 31)
    for y in (5, 26):
        t[y][5] = P['mt_lt']
    return t


@reg('porte_droite_dessus')
def porte_droite_dessus(n, d):
    t = blank_tile()
    wood_post(t, 22, 29, 0, 31)
    for y in (5, 26):
        t[y][25] = P['mt_lt']
    return t


# ------------------------------------------------------------------ escaliers
def stairs(up):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            t[y][x] = FLOOR[y][x]
    steps = 6
    for i in range(steps):
        y0 = 2 + i * 5
        for y in range(y0, min(31, y0 + 5)):
            for x in range(5, 27):
                k = (i / steps) if not up else 1 - i / steps          # montant : le haut est plus clair
                if y - y0 < 3:                                       # marche
                    if up:
                        c = [P['fl_dk'], P['fl_md'], P['fl_lt'], P['fl_lt'], P['fl_hi'], P['fl_hi']][i]
                    else:
                        c = [P['fl_hi'], P['fl_lt'], P['fl_md'], P['fl_dk'], P['fl_dp'], P['hl_1']][i]
                else:                                                # contremarche
                    c = P['fl_dp'] if not up else P['fl_dk']
                    if i == steps - 1 and y - y0 >= 3:
                        c = P['hl_1']
                t[y][x] = c
    for y in range(T):                                               # parois de roche
        for x in list(range(0, 5)) + list(range(27, 32)):
            c = cap_color(x, y)
            t[y][x] = c
        t[y][4] = P['cp_dk']
        t[y][27] = P['cp_dk']
        t[y][5] = O if y % 5 else O
        t[y][26] = O
    for x in range(5, 27):
        t[1][x] = O
        t[0][x] = P['hl_1'] if not up else P['fl_dp']
    return t


REG['escalier_montant'] = lambda n, d: stairs(True)
REG['escalier_descendant'] = lambda n, d: stairs(False)


# ------------------------------------------------------------------ rails
def rail_lines(t, horizontal=True):
    for off in (10, 20):
        for x in range(T):
            ya = off if horizontal else x
            xa = x if horizontal else off
            for k in (0, 1):
                xx, yy = (xa, ya + k) if horizontal else (xa + k, ya)
                t[yy][xx] = P['mt_hi'] if k == 0 else P['mt_md']
            xx, yy = (xa, ya + 2) if horizontal else (xa + 2, ya)
            t[yy][xx] = P['mt_dk']


def sleepers(t, horizontal=True, skip=()):
    for k in range(4):
        pos = 3 + k * 8
        if pos in skip:
            continue
        for a in range(7, 25):
            for b in range(pos, pos + 3):
                x, y = (b, a) if horizontal else (a, b)
                c = P['wd_lt'] if b == pos else P['wd_md'] if b == pos + 1 else P['wd_dk']
                t[y][x] = c
        for a in (6, 25):
            for b in range(pos, pos + 3):
                x, y = (b, a) if horizontal else (a, b)
                t[y][x] = O


def rail_straight(horizontal, skip=(), gap=None):
    t = blank_tile()
    sleepers(t, horizontal, skip)
    rail_lines(t, horizontal)
    if gap:
        for y in range(T):
            for x in range(T):
                v = x if horizontal else y
                if gap[0] <= v <= gap[1] and (t[y][x] in (P['mt_hi'], P['mt_md'], P['mt_dk'])):
                    t[y][x] = None
    return t


def rail_arc(cx, cy, a0, a1):
    """Virage : centre (cx, cy) en coin de tuile, angles en degrés (y vers le bas)."""
    t = blank_tile()
    for k in range(0, 91, 15):
        ang = math.radians(a0 + (a1 - a0) * (k / 90) + (7.5 * (a1 - a0) / 90 * 0))
        for r in range(8, 25):
            for w in range(3):
                aa = ang + math.radians((w - 1) * 2.4 * 16 / max(r, 8) * 1.0)
                x, y = int(cx + math.cos(aa) * (r - 5 + 5) * 1.0 + 0.0), int(cy + math.sin(aa) * (r - 5 + 5))
                rr = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if 0 <= x < T and 0 <= y < T and 8 <= rr <= 24:
                    t[y][x] = P['wd_md'] if w == 1 else P['wd_lt'] if w == 0 else P['wd_dk']
    for y in range(T):
        for x in range(T):
            rr = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            ang = math.degrees(math.atan2(y + 0.5 - cy, x + 0.5 - cx)) % 360
            lo, hi = a0 % 360, a1 % 360
            inside = (lo <= ang <= hi) if lo <= hi else (ang >= lo or ang <= hi)
            for r0 in (11, 21):
                if inside and abs(rr - r0) < 1.0:
                    t[y][x] = P['mt_hi'] if (x + 0.5 < cx and y + 0.5 < cy) or (abs(rr - r0) < 0.5) else P['mt_md']
                elif inside and abs(rr - r0 - 1.0) < 0.7 and t[y][x] is None:
                    t[y][x] = P['mt_dk']
    return t


REG['rail_h'] = lambda n, d: rail_straight(True)
REG['rail_v'] = lambda n, d: rail_straight(False)
REG['rail_bd'] = lambda n, d: rail_arc(32, 32, 180, 270)
REG['rail_bg'] = lambda n, d: rail_arc(0, 32, 270, 360)
REG['rail_hd'] = lambda n, d: rail_arc(32, 0, 90, 180)
REG['rail_hg'] = lambda n, d: rail_arc(0, 0, 0, 90)


@reg('rail_croix')
def rail_croix(n, d):
    t = rail_straight(True)
    v = rail_straight(False)
    for y in range(T):
        for x in range(T):
            if v[y][x] is not None and not (7 <= x <= 24 and 6 <= y <= 25 and v[y][x] in (P['wd_lt'], P['wd_md'], P['wd_dk'])):
                t[y][x] = v[y][x]
    return t


def butoir(side):
    t = blank_tile()
    full = rail_straight(side in ('gauche', 'droite'))
    for y in range(T):
        for x in range(T):
            keep = {'haut': y >= 8, 'bas': y <= 23, 'gauche': x >= 8, 'droite': x <= 23}[side]
            if keep:
                t[y][x] = full[y][x]
    # bloc d'arrêt
    if side in ('haut', 'bas'):
        y0 = 4 if side == 'haut' else 21
        for y in range(y0, y0 + 6):
            for x in range(7, 25):
                c = P['rd_lt'] if y in (y0, y0 + 1) else P['rd_md'] if y < y0 + 5 else P['rd_dk']
                if (x - 7) % 6 < 3 and y in (y0 + 1, y0 + 2):
                    c = P['lamp_y']
                t[y][x] = c
        for x in range(6, 26):
            t[y0 - 1][x] = O
            t[y0 + 6][x] = O
        for y in range(y0, y0 + 6):
            t[y][6] = O
            t[y][25] = O
    else:
        x0 = 4 if side == 'gauche' else 21
        for y in range(7, 25):
            for x in range(x0, x0 + 6):
                c = P['rd_lt'] if x in (x0, x0 + 1) else P['rd_md'] if x < x0 + 5 else P['rd_dk']
                if (y - 7) % 6 < 3 and x in (x0 + 1, x0 + 2):
                    c = P['lamp_y']
                t[y][x] = c
        for y in range(6, 26):
            t[y][x0 - 1] = O
            t[y][x0 + 6] = O
        for x in range(x0, x0 + 6):
            t[6][x] = O
            t[25][x] = O
    return t


for _s in ('haut', 'bas', 'gauche', 'droite'):
    REG[f'rail_butoir_{_s}'] = (lambda s: (lambda n, d: butoir(s)))(_s)
REG['rail_casse_h'] = lambda n, d: rail_straight(True, skip=(11,), gap=(12, 19))
REG['rail_casse_v'] = lambda n, d: rail_straight(False, skip=(11,), gap=(12, 19))


@reg('traverses')
def traverses(n, d):
    t = blank_tile()
    sleepers(t, True)
    for k, y in ((0, 12), (1, 22)):                                   # planches de travers
        for x in range(2, 30):
            t[y][x] = P['wd_md'] if (x // 4) % 2 else P['wd_lt']
    return t


@reg('gravats')
def gravats(n, d):
    cv = Cv()
    mass(cv, [(10, 22, 6, 4), (18, 24, 5, 3.5), (23, 21, 4, 3), (14, 19, 3.5, 3)], (P['fl_hi'], P['fl_lt'], P['fl_md'], P['fl_dk']), 5)
    cv.outline(O)
    for x, y in ((8, 20), (21, 20), (16, 17)):
        cv.set(x, y, P['du_lt'])
    return cv.p
