"""Village, dessin final, partie 3 : puits, mobilier, clôtures, étals, fleurs, lampadaires, quai, château, brume."""
import math
import random

from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, F, GRASS, mass, ell_shade
from village_art1 import REG, reg, stone_blocks, rgba_

KP = (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk'])
WP = (P['b_lt'], P['b_lt'], P['b_md'], P['b_dk'])


# ------------------------------------------------------------------ puits 2x2
def well():
    cv = Cv(64, 64)
    # margelle : ellipse de pierre, intérieur d'eau noire
    ell_shade(cv, 32, 47, 29, 15, KP, 3, 0.25)
    for y in range(64):
        for x in range(64):
            d = ((x + 0.5 - 32) / 29.0) ** 2 + ((y + 0.5 - 47) / 15.0) ** 2
            if d <= 1 and (x // 6 + y // 5) % 3 == 0 and d > 0.55:
                cv.p[y][x] = P['k_md']
    ell(cv, 32, 45, 21, 9.5, P['k_dk'])
    ell(cv, 32, 46, 19.5, 8, P['s_dk'])
    ell(cv, 32, 46, 16, 6, P['d_dk'])
    for x in range(22, 30):
        cv.p[44][x] = P['w_lt']
    # montants de bois et petit toit
    for x0 in (8, 51):
        box(cv, x0, 12, x0 + 4, 44, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 8, 14, 55, 17, P['b_lt'], P['b_md'], P['b_dk'])          # traverse
    for y in range(1, 14):
        w = 30 - (13 - y) * 0.2
        for x in range(2, 62):
            c = P['ra_hi'] if y < 3 else P['ra_lt'] if y < 9 else P['ra_md']
            if (x + y // 4 * 4) % 8 == 7 or y % 4 == 3:
                c = P['ra_md'] if y < 9 else P['ra_dk']
            cv.p[y][x] = c
    for x in range(2, 62):
        cv.p[12][x] = P['ra_dk']
        cv.p[13][x] = P['O']
    for y in range(1, 13):
        cv.p[y][2] = P['ra_dk']
        cv.p[y][61] = P['ra_dk']
    # corde, poulie et seau
    vline(cv, 32, 17, 38, P['pk_md'])
    ell(cv, 32, 18, 3, 3, P['m_md'])
    cv.set(31, 17, P['m_hi'])
    box(cv, 29, 36, 35, 42, P['b_lt'], P['b_md'], P['b_dk'])
    hline(cv, 29, 35, 38, P['m_md'])
    cv.outline()
    return cv


_WELL = well()
for _n, (_c, _r) in dict(puits_haut_g=(0, 0), puits_haut_d=(1, 0), puits_bas_g=(0, 1), puits_bas_d=(1, 1)).items():
    REG[_n] = (lambda n, t, c=_c, r=_r: _WELL.crop(c * T, r * T))


@reg('seau')
def seau(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 26, 8, 3)
    for y in range(15, 26):
        for x in range(10, 23):
            f = 1 - (y - 15) / 10.0 * 0.2
            if abs(x - 16) < 6.5 * f + 0.5:
                cv.p[y][x] = P['b_lt'] if x < 13 else P['b_dk'] if x > 19 else P['b_md']
    ell(cv, 16, 15, 6.5, 2.5, P['b_md'])
    ell(cv, 16, 15, 5, 1.6, P['d_dk'])
    for y in (18, 23):
        hline(cv, 10, 22, y, P['m_md'])
    for x in range(10, 23):
        pass
    cv.outline()
    return cv.p


def trough():
    cv = Cv(64, 32)
    ground_shadow(cv, 32, 27, 29, 3)
    for y in range(11, 28):
        for x in range(2, 62):
            cv.p[y][x] = KP[1] if y < 15 else KP[2] if y < 24 else KP[3]
    stone_blocks(cv, 2, 15, 61, 27, 7, KP, 6, 14)
    for y in range(8, 17):
        for x in range(2, 62):
            cv.p[y][x] = KP[0] if y < 10 else KP[1]
    for y in range(10, 15):
        for x in range(5, 59):
            cv.p[y][x] = P['w_md'] if y > 11 else P['w_dk']
    for x in (10, 11, 12, 30, 31, 44, 45):
        cv.p[12][x] = P['w_hi']
    cv.outline()
    return cv


_TR = trough()
REG['auge_g'] = lambda n, t: _TR.crop(0, 0)
REG['auge_d'] = lambda n, t: _TR.crop(32, 0)


def bench(pos):
    cv = Cv()
    ground_shadow(cv, 16, 28, 16, 2)
    x0 = 2 if pos == 'g' else 0
    x1 = 31 if pos == 'd' else 31
    x1 = 29 if pos == 'd' else 31
    for y in range(12, 18):                                            # dossier
        for x in range(x0, x1 + 1):
            cv.p[y][x] = P['b_lt'] if y == 12 else P['b_md'] if y < 16 else P['b_dk']
    for y in range(18, 23):                                            # assise
        for x in range(x0, x1 + 1):
            cv.p[y][x] = P['pk_hi'] if y == 18 else P['pk_lt'] if y < 21 else P['pk_dk']
    legs = {'g': (4, 24), 'm': (6, 26), 'd': (6, 26)}[pos]
    for lx in legs:
        if x0 <= lx <= x1 - 2:
            box(cv, lx, 23, lx + 2, 28, P['b_lt'], P['b_md'], P['b_dk'])
    if pos == 'g':
        for y in range(12, 28):
            cv.p[y][2] = O
    if pos == 'd':
        for y in range(12, 28):
            cv.p[y][29] = O
    for x in range(x0, x1 + 1):
        cv.p[11][x] = O
        cv.p[23][x] = P['pk_dk'] if cv.p[23][x] is None else cv.p[23][x]
    cv.outline()
    return cv.p


for _p in 'gmd':
    REG[f'banc_{_p}'] = (lambda n, t, p=_p: bench(p))


def hay_colors():
    return ('#f0dc7c', '#d8c060', '#b09a40', '#7e6a2a')


@reg('foin_botte')
def foin_botte(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 27, 13, 3)
    for y in range(11, 27):
        for x in range(5, 27):
            c = rgba_('#f0dc7c') if y < 15 else rgba_('#d8c060') if y < 22 else rgba_('#b09a40')
            if (x * 3 + y * 5) % 7 == 0:
                c = rgba_('#b09a40') if y >= 15 else rgba_('#d8c060')
            cv.p[y][x] = c
    for x in (10, 21):
        for y in range(11, 27):
            cv.p[y][x] = P['pk_md']
    for x in range(5, 27):
        cv.p[15][x] = rgba_('#f0dc7c') if x % 2 else rgba_('#d8c060')
    cv.outline()
    return cv.p


@reg('foin_tas')
def foin_tas(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 27, 13, 3)
    mass(cv, [(16, 20, 12, 8), (11, 22, 8, 6), (22, 22, 8, 6), (15, 15, 8, 6)],
         (rgba_('#f6e48c'), rgba_('#e0c864'), rgba_('#b89c44'), rgba_('#7e6a2a')), 4, 0.5)
    for i in range(10):
        x, y = 8 + (i * 7) % 17, 12 + (i * 5) % 12
        cv.set(x, y, rgba_('#7e6a2a'))
        cv.set(x + 1, y - 1, rgba_('#f6e48c'))
    cv.outline()
    return cv.p


def cart():
    cv = Cv(64, 32)
    ground_shadow(cv, 32, 29, 28, 2)
    for y in range(9, 22):                                             # caisse
        for x in range(8, 62):
            cv.p[y][x] = P['pk_hi'] if y == 9 else P['pk_lt'] if y < 17 else P['pk_dk']
            if (x - 8) % 9 == 8 and y > 9:
                cv.p[y][x] = P['pk_dk']
    for y in range(9, 11):
        for x in range(8, 62):
            cv.p[y][x] = P['b_lt']
    for x in range(10, 60, 4):                                         # chargement de foin
        for y in range(5, 9):
            cv.p[y][x] = rgba_('#d8c060') if (x + y) % 3 else rgba_('#f0dc7c')
    for x in range(2, 10):                                             # brancards
        cv.p[18 + (x // 4)][x] = P['b_md']
        cv.p[19 + (x // 4)][x] = P['b_dk']
    for cx in (22, 48):                                                # roues
        ell(cv, cx, 23, 6, 6, P['b_dk'])
        ell(cv, cx, 23, 4.3, 4.3, P['b_md'])
        ell(cv, cx, 23, 1.5, 1.5, P['m_md'])
        for a in range(0, 180, 45):
            for t in range(-4, 5):
                cv.set(int(cx + t * math.cos(math.radians(a))), int(23 + t * math.sin(math.radians(a))), P['b_lt'])
    cv.outline()
    return cv


_CART = cart()
REG['charrette_g'] = lambda n, t: _CART.crop(0, 0)
REG['charrette_d'] = lambda n, t: _CART.crop(32, 0)


@reg('tas_bois')
def tas_bois(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 27, 13, 3)
    pos = [(9, 22), (16, 22), (23, 22), (12, 16), (20, 16), (16, 10)]
    for (cx, cy) in pos:
        ell(cv, cx, cy, 4.2, 4.2, P['b_md'])
        ell(cv, cx, cy, 3.2, 3.2, P['pk_hi'])
        ell(cv, cx, cy, 1.6, 1.6, P['pk_lt'])
        cv.set(cx, cy, P['pk_dk'])
        cv.outline()
    return cv.p


@reg('billot_bois')
def billot_bois(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 11, 3)
    for y in range(15, 27):
        for x in range(8, 24):
            cv.p[y][x] = P['b_lt'] if x < 12 else P['b_dk'] if x > 20 else P['b_md']
    ell(cv, 16, 15, 8, 4, P['pk_hi'])
    ell(cv, 16, 15, 5, 2.4, P['pk_lt'])
    ell(cv, 16, 15, 2, 1, P['pk_dk'])
    for i in range(12):                                                # hache plantée
        cv.set(19 + i // 4, 9 + i // 2 + 2, P['b_md'])
    box(cv, 14, 8, 19, 12, P['m_hi'], P['m_lt'], P['m_dk'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ clôtures et murets
def fence(arms, gate=None):
    cv = Cv()
    cx = 16
    N, E, S, W = arms
    rails = ((12, 14), (19, 21))
    def hrail(x0, x1):
        for (a, b) in rails:
            for y in range(a, b + 1):
                for x in range(x0, x1 + 1):
                    cv.set(x, y, P['b_lt'] if y == a else P['b_dk'] if y == b else P['b_md'])
    if E:
        hrail(cx, 31)
    if W:
        hrail(0, cx)
    def vrail(y0, y1):
        for x0 in (11, 18):
            for x in range(x0, x0 + 3):
                for y in range(y0, y1 + 1):
                    cv.set(x, y, P['b_lt'] if x == x0 else P['b_dk'] if x == x0 + 2 else P['b_md'])
    if N:
        vrail(0, 18)
    if S:
        vrail(14, 31)
    if gate == 'closed':
        hrail(0, 31)
        for i in range(0, 32):
            y = 14 + int(i * 6 / 31)
            cv.set(i, y, P['b_lt'])
            cv.set(i, 26 - int(i * 6 / 31), P['b_lt'])
    # poteau central (ou poteaux d'extrémité pour la clôture droite)
    posts = [cx]
    if (E and W and not (N or S)):
        posts = [3, 28]
    if (N and S and not (E or W)):
        posts = [cx]
    if gate == 'closed':
        posts = [2, 29]
    for px in posts:
        for y in range(7, 26):
            for x in range(px - 2, px + 2):
                cv.set(x, y, P['pk_hi'] if x == px - 2 else P['pk_dk'] if x == px + 1 else P['pk_lt'])
        for x in range(px - 2, px + 2):
            cv.set(x, 6, P['b_lt'])
    if (N or S) and not (E or W):
        for y in range(6, 8):
            pass
    ground_shadow(cv, 16, 27, 13, 2)
    cv.outline()
    return cv.p


REG['cloture_h'] = lambda n, t: fence((0, 1, 0, 1))
REG['cloture_v'] = lambda n, t: fence((1, 0, 1, 0))
REG['cloture_c_hg'] = lambda n, t: fence((0, 1, 1, 0))
REG['cloture_c_hd'] = lambda n, t: fence((0, 0, 1, 1))
REG['cloture_c_bg'] = lambda n, t: fence((1, 1, 0, 0))
REG['cloture_c_bd'] = lambda n, t: fence((1, 0, 0, 1))
REG['cloture_portillon'] = lambda n, t: fence((0, 1, 0, 1), 'closed')


@reg('cloture_portillon_ouvert')
def portillon_ouvert(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 27, 13, 2)
    for px in (2, 29):
        for y in range(7, 26):
            for x in range(px - 2, px + 2):
                cv.set(x, y, P['pk_hi'] if x == px - 2 else P['pk_dk'] if x == px + 1 else P['pk_lt'])
        for x in range(px - 2, px + 2):
            cv.set(x, 6, P['b_lt'])
    for x in range(5, 9):                                              # battant ouvert vu de côté
        for y in range(10, 25):
            cv.set(x, y, P['b_lt'] if x == 5 else P['b_dk'] if x == 8 else P['b_md'])
    cv.outline()
    return cv.p


def wall_low(arms, pillar=False):
    """Muret de pierre : dessus clair, face dessous."""
    cv = Cv()
    N, E, S, W = arms
    cx = 16
    def seg(x0, y0, x1, y1, face=True):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = P['k_hi'] if y == y0 or x == x0 else P['k_lt']
                if y >= y1 - 9 and face and y > y0 + 4:
                    c = P['k_md'] if (y - y1) % 5 else P['k_dk']
                    if (x + (y // 5) * 7) % 12 == 0:
                        c = P['k_dk']
                if x == x1:
                    c = P['k_dk']
                cv.set(x, y, c)
    if E:
        seg(cx - 8, 12, 31, 28)
    if W:
        seg(0, 12, cx + 8, 28)
    if N:
        seg(8, 0, 23, 19, False)
        for y in range(0, 20):
            for x in range(8, 24):
                cv.set(x, y, P['k_hi'] if x < 10 else P['k_dk'] if x > 21 else P['k_lt'] if y % 7 else P['k_md'])
    if S:
        for y in range(14, 32):
            for x in range(8, 24):
                cv.set(x, y, P['k_hi'] if x < 10 else P['k_dk'] if x > 21 else P['k_lt'] if y % 7 else P['k_md'])
    if (N or S) and (E or W):
        seg(8, 12, 23, 28)
    ground_shadow(cv, 16, 29, 13, 2)
    cv.outline()
    return cv.p


REG['muret_h'] = lambda n, t: wall_low((0, 1, 0, 1))
REG['muret_v'] = lambda n, t: wall_low((1, 0, 1, 0))
REG['muret_c_hg'] = lambda n, t: wall_low((0, 1, 1, 0))
REG['muret_c_hd'] = lambda n, t: wall_low((0, 0, 1, 1))
REG['muret_c_bg'] = lambda n, t: wall_low((1, 1, 0, 0))
REG['muret_c_bd'] = lambda n, t: wall_low((1, 0, 0, 1))


@reg('muret_poteau')
def muret_poteau(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 9, 2)
    stone_blocks(cv, 11, 12, 20, 30, 5, KP, 6, 10)
    box(cv, 9, 8, 22, 13, P['k_hi'], P['k_lt'], P['k_dk'])
    cv.outline()
    return cv.p


@reg('escalier_rampe')
def rampe(name, tile):
    cv = tex(F.path_tex(11))
    for y0 in (3, 14, 25):
        for x in range(T):
            cv.p[y0][x] = P['b_lt']
            cv.p[y0 + 1][x] = P['b_md']
            cv.p[y0 + 2][x] = P['b_dk']
            if (x + y0) % 2 == 0 and y0 + 3 < T:
                cv.p[y0 + 3][x] = P['t_dk']
    for y in range(T):
        cv.p[y][0] = P['t_dk']
        cv.p[y][31] = P['t_dk']
    return cv.p


# ------------------------------------------------------------------ étals, tonneaux, caisses
def stall(pos):
    cv = Cv()
    ground_shadow(cv, 16, 29, 15, 2)
    x0 = 2 if pos == 'g' else 0
    x1 = 29 if pos == 'd' else 31
    for y in range(8, 30):
        for x in range(x0, x1 + 1):
            if y < 12:
                c = P['b_lt']
            elif y < 18:                                               # nappe rayée
                c = P['ra_lt'] if (x // 4) % 2 == 0 else P['pl_lt']
                if y == 12:
                    c = P['ra_hi'] if (x // 4) % 2 == 0 else P['white']
            else:
                c = P['pk_lt'] if (x - x0) % 8 else P['pk_dk']
                if y > 25:
                    c = P['pk_dk']
            cv.p[y][x] = c
    for y in range(18, 24):
        pass
    r = random.Random(ord(pos))
    for x in range(x0 + 2, x1 - 2, 5):                                 # marchandises sur le plateau
        col = r.choice([P['f_red'], P['orange2'], P['f_yel'], P['g_lt'], P['f_vio']])
        ell(cv, x + 1.5, 8.5, 2.6, 2.4, col)
        cv.set(x, 7, P['white'])
    if pos == 'g':
        for y in range(5, 30):
            cv.p[y][2] = O
    if pos == 'd':
        for y in range(5, 30):
            cv.p[y][29] = O
    cv.outline()
    return cv.p


for _p in 'gmd':
    REG[f'etal_{_p}'] = (lambda n, t, p=_p: stall(p))


def awning(pos):
    cv = Cv()
    x0 = 1 if pos == 'g' else 0
    x1 = 30 if pos == 'd' else 31
    for y in range(0, 17):
        for x in range(x0, x1 + 1):
            if y > 12 and (x % 8) not in (0, 1, 2, 3, 4, 5, 6) and False:
                continue
            stripe = (x // 4) % 2 == 0
            c = (P['ra_lt'] if stripe else P['pl_lt'])
            if y < 3:
                c = P['ra_hi'] if stripe else P['white']
            elif y > 13:
                c = P['ra_md'] if stripe else P['pl_dk']
            cv.p[y][x] = c
    for x in range(x0, x1 + 1):                                        # bord festonné
        k = x % 4
        if k in (0, 3):
            cv.p[16][x] = None
            cv.p[15][x] = None if k == 0 and (x // 4) % 2 == 1 else cv.p[15][x]
    for x in range(x0, x1 + 1):
        for y in range(17, 22):
            if (x + y) % 2 == 0 and y < 20 and cv.p[16][x] is not None:
                cv.p[y][x] = (0x1b, 0x14, 0x20, 100)
    if pos == 'g':
        for y in range(0, 22):
            cv.p[y][0] = None
    cv.outline()
    return cv.p


for _p in 'gmd':
    REG[f'auvent_{_p}'] = (lambda n, t, p=_p: awning(p))


def barrel_obj(cx, cy, w=8, h=9):
    cv = Cv()
    return cv


@reg('tonneau', 'tonneaux')
def tonneaux(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 13, 3)
    spots = [(16, 0)] if name == 'tonneau' else [(10, 3), (22, -2)]
    for cx, dy in spots:
        for y in range(10 + dy + 4, 26 + dy + 1):
            for x in range(cx - 7, cx + 8):
                bulge = 1 - abs((y - (18 + dy)) / 8.0) ** 2 * 0.15
                if abs(x - cx) < 6.8 * bulge + 0.6:
                    cv.set(x, y, P['b_lt'] if x < cx - 3 else P['b_dk'] if x > cx + 3 else P['b_md'])
        for y in (14 + dy, 22 + dy):
            for x in range(cx - 7, cx + 8):
                if cv.get(x, y) is not None:
                    cv.set(x, y, P['m_md'])
        ell(cv, cx, 12 + dy + 3, 6.5, 2.4, P['pk_hi'])
        ell(cv, cx, 12 + dy + 3, 4.5, 1.4, P['pk_lt'])
        cv.outline()
    return cv.p


def crate(x0, y0, w, h, cv):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            c = P['pk_lt']
            if y < y0 + 4:
                c = P['pk_hi']
            if (x in (x0, x0 + w - 1)) or y == y0 + h - 1 or y in (y0 + 3,):
                c = P['b_dk']
            cv.set(x, y, c)
    for i in range(0, min(w, h) - 3):                                  # croix
        cv.set(x0 + 1 + i, y0 + 4 + i * (h - 6) // max(1, w - 3), P['pk_md'])
        cv.set(x0 + w - 2 - i, y0 + 4 + i * (h - 6) // max(1, w - 3), P['pk_md'])


@reg('caisse', 'caisses_empilees')
def caisses(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 13, 3)
    if name == 'caisse':
        crate(7, 12, 18, 16, cv)
    else:
        crate(5, 15, 14, 13, cv)
        crate(17, 15, 12, 13, cv)
        crate(9, 4, 14, 12, cv)
    cv.outline()
    return cv.p


@reg('sacs')
def sacs(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 13, 3)
    for (cx, cy, r) in ((10, 22, 7), (22, 22, 7), (16, 14, 7)):
        ell_shade(cv, cx, cy + 1, r, r - 0.5, (P['pl_hi'], P['pl_lt'], P['pl_md'], P['pl_dk']), cx, 0.15)
        for x in range(cx - 2, cx + 3):
            cv.set(x, cy - r + 2, P['pl_dk'])
        cv.set(cx, cy - r + 1, P['b_md'])
        cv.outline()
    return cv.p


@reg('jarre')
def jarre(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 10, 3)
    cl = (rgba_('#d88a5a'), rgba_('#b86a4a'), rgba_('#8e4a36'), rgba_('#5e3024'))
    for y in range(8, 28):
        t = (y - 8) / 19.0
        wd = 4 + 8 * math.sin(math.pi * min(1, t * 0.9 + 0.1)) if y > 10 else 4
        for x in range(int(16 - wd), int(16 + wd) + 1):
            cv.set(x, y, cl[0] if x < 16 - wd * 0.4 else cl[3] if x > 16 + wd * 0.5 else cl[1])
    for x in range(11, 22):
        cv.set(x, 14, cl[3])
        cv.set(x, 15, cl[2]) if x > 15 else None
    ell(cv, 16, 8, 5, 2, cl[2])
    ell(cv, 16, 8, 3.5, 1.2, P['s_dk'])
    cv.outline()
    return cv.p


@reg('panier')
def panier(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 11, 3)
    for y in range(16, 27):
        for x in range(7, 26):
            if abs(x - 16) < 9.5 - (y - 16) * 0.2:
                cv.set(x, y, P['pk_hi'] if (x + y) % 4 < 2 else P['pk_lt'])
    for y in (19, 23):
        for x in range(7, 26):
            if cv.get(x, y) is not None:
                cv.set(x, y, P['pk_md'])
    for (cx, cy) in ((11, 14), (16, 12), (21, 14), (14, 16), (19, 16)):
        ell(cv, cx, cy, 3.2, 3, P['f_red'])
        cv.set(cx - 1, cy - 1, P['white'])
        cv.set(cx + 1, cy + 1, P['fi_d'])
    cv.outline()
    return cv.p


@reg('citrouilles')
def citrouilles(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 13, 3)
    for (cx, cy, rx, ry) in ((10, 21, 8, 6), (22, 22, 7, 5.5), (16, 16, 7, 5.5)):
        ell_shade(cv, cx, cy, rx, ry, (P['fi_y'], P['orange2'], P['orange'], P['fi_d']), cx, 0.1)
        for k in (-1, 1):
            for y in range(int(cy - ry), int(cy + ry)):
                cv.set(int(cx + k * rx * 0.45), y, P['fi_d']) if rnd(y, cx, 1) < 0.8 else None
        cv.set(cx, int(cy - ry) - 1, P['g_dk'])
        cv.set(cx + 1, int(cy - ry) - 2, P['g_md'])
        cv.outline()
    return cv.p


@reg('bois_fendu')
def bois_fendu(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 13, 3)
    for row in range(4):
        y = 25 - row * 5
        for x in range(6 + (row % 2) * 2, 27, 5):
            for yy in range(y - 4, y + 1):
                for xx in range(x, x + 5):
                    cv.set(xx, yy, P['pk_hi'] if yy == y - 4 else P['pk_dk'] if xx == x + 4 or yy == y else P['pk_lt'])
    cv.outline()
    return cv.p


@reg('ruche')
def ruche(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 10, 3)
    for y in (24, 25, 26, 27):                                         # pieds
        pass
    box(cv, 8, 25, 10, 28, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 22, 25, 24, 28, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 6, 22, 25, 25, P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(6, 23):
        wd = 9 * math.sin(math.pi * (y - 4) / 22.0) + 1
        for x in range(int(16 - wd), int(16 + wd) + 1):
            band = (y - 6) // 4
            c = rgba_('#f0dc7c') if x < 16 - wd * 0.3 else rgba_('#b09a40') if x > 16 + wd * 0.4 else rgba_('#d8c060')
            if (y - 6) % 4 == 3:
                c = rgba_('#7e6a2a')
            cv.set(x, y, c)
    ell(cv, 16, 18, 2.2, 2.2, P['O'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ fleurs et potagers
def flowers_tile(col, seed, mid=None):
    cv = Cv()
    r = random.Random(seed)
    for _ in range(14):                                                # feuillage
        x, y = r.randrange(2, 30), r.randrange(10, 29)
        cv.set(x, y, P['g_dk'])
        cv.set(x, y - 1, P['g_md'])
        cv.set(x + 1, y - 1, P['g_lt'])
    for _ in range(11):
        x, y = r.randrange(3, 29), r.randrange(8, 27)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.set(x + dx, y + dy, col)
        cv.set(x, y, mid or P['f_yel'])
        cv.set(x, y + 2, P['g_dk'])
    return cv.p


REG['parterre_rouge'] = lambda n, t: flowers_tile(P['f_red'], 1)
REG['parterre_jaune'] = lambda n, t: flowers_tile(P['f_yel'], 2, P['orange'])
REG['parterre_blanc'] = lambda n, t: flowers_tile(P['f_white'], 3)


@reg('pot_fleurs')
def pot_fleurs(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 9, 2)
    cl = (rgba_('#d88a5a'), rgba_('#b86a4a'), rgba_('#8e4a36'))
    for y in range(18, 28):
        for x in range(10, 23):
            if abs(x - 16) < 6.5 - (y - 18) * 0.25:
                cv.set(x, y, cl[0] if x < 13 else cl[2] if x > 19 else cl[1])
    box(cv, 9, 16, 23, 19, cl[0], cl[1], cl[2])
    r = random.Random(9)
    for (cx, cy, col) in ((11, 11, P['f_red']), (16, 8, P['f_yel']), (21, 11, P['pink']), (14, 13, P['f_white']), (19, 14, P['f_red'])):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.set(cx + dx, cy + dy, col)
        cv.set(cx, cy, P['f_yel'])
        cv.set(cx, cy + 2, P['g_dk'])
        cv.set(cx, cy + 3, P['g_md'])
    cv.outline()
    return cv.p


@reg('buisson_fleuri')
def buisson_fleuri(name, tile):
    return F.bush(2)


@reg('rosier_mur')
def rosier(name, tile):
    cv = Cv()
    for x in (6, 15, 24):
        for y in range(2, 30):
            if rnd(x, y, 5) < 0.8:
                cv.set(x + (y // 5) % 2, y, P['g_dk'])
    for (cx, cy) in ((6, 6), (10, 12), (18, 8), (24, 15), (8, 21), (20, 22), (15, 17), (27, 5), (13, 4)):
        ell(cv, cx, cy, 3, 2.6, P['g_md'])
        cv.set(cx - 1, cy - 1, P['g_lt'])
        cv.set(cx, cy, P['pink'])
        cv.set(cx + 1, cy, P['f_red'])
        cv.set(cx, cy + 1, P['fi_d'])
    return cv.p


@reg('potager_a', 'potager_b')
def potager(name, tile):
    cv = tex(F.path_tex(30))
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = P['b_md'] if (y % 8) in (0, 1, 2, 3) else P['b_dk'] if y % 8 == 7 else P['t_dk']
            if rnd(x, y, 3) < 0.1:
                cv.p[y][x] = P['t_dk']
    for row in range(4):
        y0 = row * 8 + 2
        for x in range(2, 31, 6 if name == 'potager_b' else 4):
            if name == 'potager_a':
                cv.set(x, y0, P['g_lt'])
                cv.set(x - 1, y0 + 1, P['g_md'])
                cv.set(x + 1, y0 + 1, P['g_md'])
                cv.set(x, y0 + 2, P['g_dk'])
                if row % 2:
                    cv.set(x, y0 + 3, P['orange2'])
            else:
                ell(cv, x + 1, y0 + 1, 2.7, 2.4, P['g_lt'])
                ell(cv, x + 1, y0 + 1, 1.4, 1.2, P['g_hi'])
                cv.set(x - 1, y0 + 3, P['g_dk'])
    return cv.p


# ------------------------------------------------------------------ lampadaires, panneaux
@reg('lampadaire_bas')
def lampadaire_bas(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 7, 2)
    box(cv, 12, 26, 20, 30, P['m_lt'], P['m_md'], P['m_dk'])
    box(cv, 14, 0, 17, 26, P['m_lt'], P['m_md'], P['m_dk'])
    for y in (6, 16):
        box(cv, 13, y, 18, y + 1, P['m_hi'], P['m_lt'], P['m_dk'])
    cv.outline()
    return cv.p


@reg('lampadaire_haut')
def lampadaire_haut(name, tile):
    cv = Cv()
    box(cv, 14, 20, 17, 31, P['m_lt'], P['m_md'], P['m_dk'])
    box(cv, 9, 18, 22, 21, P['m_lt'], P['m_md'], P['m_dk'])
    for y in range(6, 18):
        for x in range(10, 22):
            cv.p[y][x] = P['fi_y'] if 12 <= x <= 19 and 8 <= y <= 15 else P['fi_o'] if 11 <= x <= 20 else P['m_md']
    for x in (10, 21):
        vline(cv, x, 6, 17, P['m_dk'])
    box(cv, 9, 4, 22, 6, P['m_lt'], P['m_md'], P['m_dk'])
    for x in range(12, 20):
        cv.p[3][x] = P['m_md']
    cv.set(15, 2, P['m_hi'])
    cv.set(16, 2, P['m_hi'])
    cv.set(15, 11, P['white'])
    cv.set(16, 11, P['white'])
    cv.outline()
    for (cx, cy) in ((6, 12), (25, 12)):                              # halo léger
        for y in range(cy - 3, cy + 4):
            for x in range(cx - 2, cx + 3):
                if cv.get(x, y) is None and (x + y) % 2 == 0:
                    cv.p[y][x] = (0xf0, 0xe0, 0x60, 70)
    return cv.p


@reg('lanterne_murale')
def lanterne_murale(name, tile):
    cv = Cv()
    hline(cv, 15, 31, 7, P['m_dk'])
    hline(cv, 15, 31, 8, P['m_md'])
    vline(cv, 22, 9, 11, P['m_md'])
    box(cv, 17, 11, 27, 13, P['m_lt'], P['m_md'], P['m_dk'])
    for y in range(13, 24):
        for x in range(18, 27):
            cv.p[y][x] = P['fi_y'] if 20 <= x <= 24 and 15 <= y <= 21 else P['fi_o']
    for x in (18, 26):
        vline(cv, x, 13, 23, P['m_dk'])
    box(cv, 17, 23, 27, 25, P['m_lt'], P['m_md'], P['m_dk'])
    cv.set(22, 17, P['white'])
    cv.outline()
    return cv.p


def post_sign(kind):
    cv = Cv()
    ground_shadow(cv, 16, 29, 7, 2)
    box(cv, 14, 12, 17, 30, P['b_lt'], P['b_md'], P['b_dk'])
    if kind == 'bois':
        box(cv, 6, 3, 25, 15, P['pk_hi'], P['pk_lt'], P['b_dk'])
        for y in (6, 9, 12):
            hline(cv, 9, 22, y, P['b_dk'])
        hline(cv, 9, 16, 9, P['pk_md'])
    else:
        pts = []
        for y in range(4, 16):
            d = abs(y - 9.5)
            if kind == 'g':
                x0, x1 = 5 + int(d * 0.9), 26
            else:
                x0, x1 = 5, 26 - int(d * 0.9)
            for x in range(x0, x1 + 1):
                cv.set(x, y, P['pk_hi'] if y == 4 else P['b_dk'] if y == 15 else P['pk_lt'])
        for x in range(10, 21):
            cv.set(x, 9, P['b_dk'])
            cv.set(x, 10, P['b_dk']) if kind == 'g' else None
        hline(cv, 10, 20, 9, P['b_dk'])
        hline(cv, 8, 22, 7, P['pk_md'])
    cv.outline()
    return cv.p


REG['panneau_bois'] = lambda n, t: post_sign('bois')
REG['panneau_g'] = lambda n, t: post_sign('g')
REG['panneau_d'] = lambda n, t: post_sign('d')


@reg('borne')
def borne(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 8, 2)
    for y in range(12, 30):
        for x in range(11, 22):
            c = P['k_lt'] if x < 15 else P['k_dk'] if x > 18 else P['k_md']
            if y > 26:
                c = P['k_dk']
            cv.p[y][x] = c
    ell(cv, 16, 13, 5.5, 2.5, P['k_hi'])
    ell(cv, 16, 13, 3.5, 1.4, P['k_lt'])
    cv.set(14, 12, P['white'])
    cv.outline()
    return cv.p


@reg('stele_gardiens')
def stele(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 11, 3)
    vi = (P['ch_hi'], P['ch_lt'], P['ch_md'], P['ch_dk'])
    for y in range(5, 29):
        wd = 8 - max(0, (7 - (y - 3)) // 2)
        for x in range(int(16 - wd), int(16 + wd) + 1):
            cv.set(x, y, vi[0] if x < 16 - wd + 2 else vi[3] if x > 16 + wd - 2 else vi[1])
    for cx, cy in ((16, 11), (12, 18), (20, 18)):                      # trois sceaux gravés
        for y in range(T):
            for x in range(T):
                d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
                if 2.0 <= d < 3.2 and cv.p[y][x] is not None:
                    cv.p[y][x] = P['p_jt']
                elif d < 2.0 and cv.p[y][x] is not None:
                    cv.p[y][x] = P['ronce_c']
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ quai
def planks(cv, x0, y0, x1, y1, vertical):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) if vertical else (y - y0)
            w = (y - y0) if vertical else (x - x0)
            k = w // 6
            c = P['pk_lt'] if k % 2 else P['pk_hi']
            if w % 6 == 5:
                c = P['pk_dk']
            elif u % 7 == 3 and w % 6 == 2:
                c = P['pk_md']
            cv.set(x, y, c)


def pier(kind):
    cv = Cv()
    if kind in ('h', 'bout_g', 'bout_d'):
        x0 = 4 if kind == 'bout_g' else 0
        x1 = 27 if kind == 'bout_d' else 31
        planks(cv, x0, 5, x1, 26, False)
        # planches posées sur deux longerons
        for x in range(x0, x1 + 1):
            for y in range(5, 27):
                if x % 6 == 5:
                    cv.p[y][x] = P['pk_dk']
        for y in (6, 24):
            for x in range(x0, x1 + 1):
                cv.p[y][x] = P['b_md']
                cv.p[y + 1][x] = P['b_dk']
        for x in range(x0, x1 + 1):
            cv.p[5][x] = P['b_lt']
            cv.p[26][x] = P['b_dk']
        if kind == 'bout_g':
            box(cv, 4, 5, 8, 27, P['b_lt'], P['b_md'], P['b_dk'])
            for y in (6, 24):
                box(cv, 1, y - 1, 6, y + 3, P['b_lt'], P['b_md'], P['b_dk'])
        if kind == 'bout_d':
            box(cv, 23, 5, 27, 27, P['b_lt'], P['b_md'], P['b_dk'])
            for y in (6, 24):
                box(cv, 25, y - 1, 30, y + 3, P['b_lt'], P['b_md'], P['b_dk'])
    else:
        y0 = 4 if kind == 'bout_haut' else 0
        y1 = 31
        for y in range(y0, y1 + 1):
            for x in range(5, 27):
                k = y // 6
                c = P['pk_lt'] if k % 2 else P['pk_hi']
                if y % 6 == 5:
                    c = P['pk_dk']
                elif x % 7 == 3 and y % 6 == 2:
                    c = P['pk_md']
                cv.p[y][x] = c
        for x in (6, 24):
            for y in range(y0, y1 + 1):
                cv.p[y][x] = P['b_md']
                cv.p[y][x + 1] = P['b_dk']
                cv.p[y][x - 1] = P['b_lt']
        if kind == 'bout_haut':
            box(cv, 4, 4, 27, 8, P['b_lt'], P['b_md'], P['b_dk'])
        if kind == 'bout_bas':
            for x in range(5, 27):
                cv.p[28][x] = P['b_dk']
    cv.outline()
    if kind in ('h', 'bout_g', 'bout_d'):
        for x in range(0 if kind != 'bout_g' else 4, 32 if kind != 'bout_d' else 28):
            if cv.p[4][x] == O and x % 2:
                cv.p[4][x] = O
    return cv.p


REG['ponton_h'] = lambda n, t: pier('h')
REG['ponton_v'] = lambda n, t: pier('v')
REG['ponton_bout_g'] = lambda n, t: pier('bout_g')
REG['ponton_bout_d'] = lambda n, t: pier('bout_d')
REG['ponton_bout_haut'] = lambda n, t: pier('bout_haut')
REG['ponton_bout_bas'] = lambda n, t: pier('bout_bas')


@reg('pilotis')
def pilotis(name, tile):
    cv = Cv()
    for y in range(8, 29):
        for x in range(12, 20):
            cv.p[y][x] = P['b_lt'] if x < 14 else P['b_dk'] if x > 17 else P['b_md']
    ell(cv, 16, 8, 4, 2, P['pk_hi'])
    ell(cv, 16, 8, 2, 1, P['pk_lt'])
    for y in range(19, 29):
        for x in range(12, 20):
            if y > 22 or (x + y) % 2 == 0:
                cv.p[y][x] = P['w_dk'] if y > 24 else P['b_dk']
    for x in range(8, 24):
        if (x + 1) % 2:
            cv.set(x, 26, P['foam'])
    cv.outline()
    for x in (7, 8, 23, 24):
        cv.set(x, 27, P['foam'])
    return cv.p


@reg('bollard')
def bollard(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 8, 2)
    for y in range(14, 29):
        for x in range(12, 20):
            cv.p[y][x] = P['b_lt'] if x < 14 else P['b_dk'] if x > 17 else P['b_md']
    ell(cv, 16, 14, 5, 2.5, P['pk_hi'])
    ell(cv, 16, 14, 3, 1.3, P['pk_lt'])
    for i in range(7):                                                 # corde enroulée
        hline(cv, 11, 20, 17 + i * 2 if i < 4 else 24 + i, P['rc_lt'] if i % 2 else P['rc_md'])
    cv.outline()
    return cv.p


def boat():
    cv = Cv(64, 32)
    ground_shadow(cv, 32, 27, 28, 3, P['w_dk'])
    for y in range(9, 27):
        t = (y - 9) / 17.0
        hw = 29 * (0.72 + 0.28 * math.sin(math.pi * min(1, t + 0.1))) if t < 0.85 else 24
        for x in range(int(32 - hw), int(32 + hw) + 1):
            cv.set(x, y, P['pk_lt'])
    # coque : dessus intérieur sombre, flancs
    for y in range(9, 27):
        for x in range(64):
            c = cv.p[y][x]
            if c is None:
                continue
            if y < 12:
                cv.p[y][x] = P['b_lt']
            elif y < 21:
                cv.p[y][x] = P['pk_md'] if (x // 5) % 2 else P['b_dk']
            else:
                cv.p[y][x] = P['b_md'] if y < 25 else P['b_dk']
    for x in range(8, 58, 6):
        for y in range(13, 20):
            cv.p[y][x] = P['b_dk']
    for x in (22, 42):                                                 # bancs
        box(cv, x, 14, x + 3, 19, P['b_lt'], P['pk_lt'], P['b_dk'])
    for x in range(1, 12):                                             # rame
        cv.set(40 + x * 1, 7 - x // 5, P['pk_hi'])
    cv.outline()
    return cv


_BOAT = boat()
REG['barque_g'] = lambda n, t: _BOAT.crop(0, 0)
REG['barque_d'] = lambda n, t: _BOAT.crop(32, 0)


@reg('filet')
def filet(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 12, 2)
    for x in (4, 26):
        box(cv, x, 5, x + 2, 29, P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(8, 24):
        for x in range(6, 26):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                cv.set(x, y, P['gl_md'] if (x + y) % 8 else P['gl_hi'])
    for x in range(5, 27):
        cv.set(x, 7, P['rc_md'])
        cv.set(x, 24, P['rc_dk'])
    for (x, y) in ((9, 12), (17, 17), (21, 11)):
        cv.set(x, y, P['gold_hi'])
    cv.outline()
    return cv.p


@reg('poisson_seche')
def poisson_seche(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 12, 2)
    for x in (4, 26):
        box(cv, x, 5, x + 2, 29, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 4, 6, 28, 8, P['b_lt'], P['b_md'], P['b_dk'])
    for x in (9, 14, 19, 24):
        vline(cv, x, 9, 10, P['rc_md'])
        for y in range(11, 22):
            wd = 2.5 * math.sin(math.pi * (y - 10) / 12.0) + 0.5
            for xx in range(int(x - wd), int(x + wd) + 1):
                cv.set(xx, y, P['m_hi'] if xx < x else P['m_lt'])
        cv.set(x, 12, P['O'])
        for (dx, dy) in ((-1, 21), (1, 21), (0, 22)):
            cv.set(x + dx, dy, P['m_md'])
    cv.outline()
    return cv.p


@reg('roseaux_a', 'roseaux_b')
def roseaux(name, tile):
    cv = Cv()
    r = random.Random(4 if name.endswith('a') else 7)
    for _ in range(8):
        x = r.randrange(3, 29)
        h = r.randrange(11, 24)
        for y in range(30 - h, 30):
            cv.set(x + (y // 7) % 2 * (1 if x % 2 else -1), y, P['g_md'] if y % 3 else P['g_lt'])
        for y in range(30 - h, 30 - h + 4):
            cv.set(x, y, P['b_md'])
            cv.set(x + 1, y, P['b_dk'])
    return cv.p


@reg('nenuphars')
def nenuphars(name, tile):
    cv = Cv()
    for (cx, cy, r) in ((9, 11, 4.5), (22, 20, 5), (14, 25, 3.3)):
        ell(cv, cx, cy, r, r * 0.7, P['g_md'])
        ell(cv, cx - 1, cy - 1, r * 0.7, r * 0.45, P['g_lt'])
        for x in range(int(cx), int(cx + r) + 1):
            cv.set(x, int(cy), P['w_md'])
    for (cx, cy) in ((22, 19), (9, 10)):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.set(cx + dx, cy + dy, P['pink'])
        cv.set(cx, cy, P['f_yel'])
    return cv.p


@reg('rocher_eau')
def rocher_eau(name, tile):
    cv = Cv()
    for x in range(3, 29):
        if x % 2 == 0:
            cv.set(x, 27, P['foam'])
            cv.set(x + 1, 28, P['foam'])
    mass(cv, [(16, 20, 12, 8), (11, 22, 8, 5)], (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 61, 0.35)
    for y in range(22, 27):
        for x in range(T):
            if cv.p[y][x] is not None and (x + y) % 2 == 0 and y > 24:
                cv.p[y][x] = P['w_dk']
    for x in range(2, 30):
        if cv.p[26][x] is not None:
            cv.p[26][x] = P['foam'] if x % 2 else P['k_dk']
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ château lointain (8x3 tuiles = 256x96)
def chateau():
    W, H = 256, 96
    cv = Cv(W, H)
    hi, lt, md, dk, ro, rd = P['ch_hi'], P['ch_lt'], P['ch_md'], P['ch_dk'], P['ch_ro'], P['ch_rd']

    def wall(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = lt
                if x - x0 < 3:
                    c = hi
                if x1 - x < 3:
                    c = md
                if (y - y0) % 7 == 6 and (x + y) % 3:
                    c = md if c != md else dk
                cv.p[y][x] = c

    def crenel(x0, x1, y):
        for x in range(x0, x1 + 1):
            if (x - x0) % 6 < 3:
                for yy in range(y - 4, y):
                    cv.p[yy][x] = hi if (x - x0) % 6 == 0 else lt

    def cone(cx, y0, y1, hw):
        for y in range(y0, y1 + 1):
            w = hw * (y - y0) / max(1, (y1 - y0))
            for x in range(int(cx - w), int(cx + w) + 1):
                cv.p[y][x] = ro if x < cx else rd

    def window(x, y):
        for yy in range(y, y + 6):
            for xx in range(x, x + 3):
                cv.p[yy][xx] = P['s_dk']
        cv.p[y][x + 1] = P['s_dk']
        cv.set(x, y + 5, dk)

    # murs d'enceinte (bas)
    wall(0, 52, 255, 95)
    crenel(0, 255, 52)
    for x in range(0, 256):
        cv.p[95][x] = dk
    # tours gauche et droite (colonne 0 et 7)
    for (x0, x1) in ((3, 28), (227, 252)):
        wall(x0, 18, x1, 95)
        crenel(x0 - 1, x1 + 1, 24)
        cone((x0 + x1) // 2, 3, 20, (x1 - x0) // 2 + 3)
        for yy in (36, 58):
            window((x0 + x1) // 2 - 1, yy)
    # tourelles (colonnes 2 et 5)
    for cx in (80, 176):
        wall(cx - 10, 34, cx + 10, 95)
        crenel(cx - 11, cx + 11, 40)
        cone(cx, 18, 36, 13)
        window(cx - 1, 54)
    # donjon (colonnes 3-4)
    wall(100, 12, 156, 95)
    crenel(98, 158, 20)
    for yy in (30, 50):
        for xx in (110, 126, 142):
            window(xx, yy)
    # drapeau
    vline(cv, 128, 0, 12, P['O'])
    for y in range(1, 7):
        for x in range(129, 129 + 9 - y):
            cv.p[y][x] = P['red2'] if y < 5 else P['fi_d']
    # poternes (colonnes 2 et 5) et grande porte
    for (x0, x1) in ((66, 78), (178, 190)):
        for y in range(72, 96):
            for x in range(x0, x1 + 1):
                ar = ((x - (x0 + x1) / 2.0) / ((x1 - x0) / 2.0)) ** 2 + ((y - 78) / 6.0) ** 2
                if y >= 78 or ar <= 1:
                    cv.p[y][x] = P['s_dk']
    for y in range(60, 96):
        for x in range(129, 159):
            ar = ((x - 144.0) / 15.0) ** 2 + ((y - 72) / 12.0) ** 2
            if y >= 72 or ar <= 1:
                cv.p[y][x] = P['v_dk']
    for y in range(64, 96):
        for x in range(133, 156):
            ar = ((x - 144.0) / 11.0) ** 2 + ((y - 72) / 8.0) ** 2
            if y >= 72 or ar <= 1:
                cv.p[y][x] = P['pk_md'] if (x - 133) % 5 else P['pk_dk']
    cv.outline()
    return cv


_CH = chateau()
for _r in range(3):
    for _c in range(8):
        REG[f'chateau_{_r}{_c}'] = (lambda n, t, c=_c, r=_r: _CH.crop(c * T, r * T))


# ------------------------------------------------------------------ brume (tuiles semi-transparentes)
def mist(seed, amp=1.0, bias=0.55, grad=None, holes=False, step=4):
    cv = Cv()
    col = P['mist'][:3]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, seed) * 0.6 + vnoise(x, y, 8, seed + 3) * 0.4
            v = n * amp
            if grad == 'haut':
                v = v * (y / 31.0)
            elif grad == 'bas':
                v = v * (1 - y / 31.0)
            elif grad == 'g':
                v = v * (x / 31.0)
            elif grad == 'd':
                v = v * (1 - x / 31.0)
            if holes:
                v = v if n > 0.5 else v * 0.0
            a = int(max(0, min(1, v * bias * 1.9)) * 255)
            a = (a // 40) * 40
            if a > 0:
                cv.p[y][x] = col + (min(a, 200),)
    return cv.p


REG['brume_dense_a'] = lambda n, t: mist(1, 1.2, 0.8)
REG['brume_dense_b'] = lambda n, t: mist(2, 1.2, 0.8)
REG['brume_dense_c'] = lambda n, t: mist(3, 1.2, 0.8)
REG['brume_dense_d'] = lambda n, t: mist(4, 1.2, 0.8)
REG['brume_bord_haut'] = lambda n, t: mist(5, 1.4, 0.8, 'haut')
REG['brume_bord_bas'] = lambda n, t: mist(6, 1.4, 0.8, 'bas')
REG['brume_bord_g'] = lambda n, t: mist(7, 1.4, 0.8, 'g')
REG['brume_bord_d'] = lambda n, t: mist(8, 1.4, 0.8, 'd')
REG['brume_legere_a'] = lambda n, t: mist(11, 1.0, 0.4)
REG['brume_legere_b'] = lambda n, t: mist(12, 1.0, 0.4)
REG['brume_legere_c'] = lambda n, t: mist(13, 1.0, 0.4)
REG['brume_legere_d'] = lambda n, t: mist(14, 1.0, 0.4)
REG['brume_trouee_a'] = lambda n, t: mist(15, 1.3, 0.75, None, True)
REG['brume_trouee_b'] = lambda n, t: mist(16, 1.3, 0.75, None, True)
REG['brume_sol_a'] = lambda n, t: mist(17, 1.4, 0.7, 'haut')
REG['brume_sol_b'] = lambda n, t: mist(18, 1.4, 0.7, 'haut')
