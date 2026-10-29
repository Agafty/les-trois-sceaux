"""Mine Effondrée, dessin final, partie 3 : ajouts du plan du donjon 2 (155 à 169) et variante sous-sol (recoloration)."""
import math
import os

from mine_art import REG, reg, P, O, Cv, T, wall, wood_beam, wood_post, blank_tile
from mine_art2 import rocks, line, crystal, RDP, WALLP, FLP
from tsplan import save_png, ROOT


@reg('poutre_sciee')
def poutre_sciee(n, d):
    t = blank_tile()
    wood_beam(t, 0, 21, 3, 11)
    for y in range(3, 12):                                           # coupe nette : bout clair
        for x in range(22, 25):
            t[y][x] = P['wd_hi'] if (x + y) % 3 else P['wd_lt']
        t[y][25] = O
    for y in range(4, 11):
        t[y][23] = P['wd_dk'] if y % 2 else P['wd_md']
    for k in range(5):                                               # sciure
        t[13 + k % 2][23 + (k * 2) % 6] = P['wd_hi']
    return t


@reg('poutre_brisee')
def poutre_brisee(n, d):
    t = blank_tile()
    wood_beam(t, 0, 13, 3, 11)
    for k, x in enumerate(range(14, 22)):
        top, bot = 3 + (k % 3) * 2, 11 + ((k * 5) % 4)
        for y in range(top, bot + 1):
            t[y][x] = P['wd_lt'] if y < top + 2 else P['wd_md'] if y < bot else P['wd_dk']
        t[top - 1][x] = O
        t[bot + 1][x] = O
    return t


def vein_wall(kind):
    cv = Cv()
    cv.p = wall((1, 1, 0, 0))
    t = cv.p
    if kind == 'minerai':
        pts = [(3, 20), (9, 25), (14, 22), (20, 28), (28, 24)]
        line(cv, pts, P['ge_dk'])
        line(cv, [(x, y - 1) for x, y in pts], P['ge_md'])
        for (x, y) in ((9, 24), (20, 27), (14, 21), (27, 23), (6, 8), (22, 6)):
            cv.set(x, y, P['ge_hi'])
    elif kind == 'etoile':
        for y in range(T):
            for x in range(T):
                dd = math.hypot((x - 16) / 15, (y - 22) / 13)
                if dd < 1 and (x + y) % 2 == 0:
                    t[y][x] = P['cy_dk'] if dd > 0.6 else P['cy_md']
        pts = [(2, 19), (9, 24), (13, 21), (19, 27), (24, 22), (30, 26)]
        line(cv, [(x, y + 1) for x, y in pts], P['cy_dk'])
        line(cv, pts, P['cy_hi'])
        line(cv, [(x, y - 1) for x, y in pts], P['cy_lt'])
        for (x, y) in ((9, 23), (13, 20), (19, 26), (24, 21), (16, 24)):
            cv.set(x, y, P['cy_w'])
        for (x, y) in ((8, 7), (22, 10), (15, 3)):
            cv.set(x, y, P['cy_lt'])
    else:
        for (cx, base, h, w, tilt) in ((9, 31, 10, 5, -1), (17, 31, 14, 7, 0), (25, 31, 9, 5, 1)):
            crystal(cv, cx, base, h, w, RDP, tilt)
        crystal(cv, 6, 11, 6, 4, RDP, 0)
        crystal(cv, 24, 13, 6, 4, RDP, 0)
    return cv.p


REG['mur_veine_minerai'] = lambda n, d: vein_wall('minerai')
REG['mur_veine_etoile'] = lambda n, d: vein_wall('etoile')
REG['mur_cristaux_rouges'] = lambda n, d: vein_wall('rouge')


def rail_t(side):
    base = REG['rail_h' if side in ('haut', 'bas') else 'rail_v'](None, None)
    t = [row[:] for row in base]
    br = REG['rail_v' if side in ('haut', 'bas') else 'rail_h'](None, None)
    for y in range(T):
        for x in range(T):
            keep = {'haut': y < 16, 'bas': y >= 16, 'gauche': x < 16, 'droite': x >= 16}[side]
            if keep and br[y][x] is not None:
                t[y][x] = br[y][x]
    return t


for _s in ('haut', 'bas', 'gauche', 'droite'):
    REG[f'rail_t_{_s}'] = (lambda s: (lambda n, d: rail_t(s)))(_s)


def eb_ouv(horizontal):
    cv = Cv()
    cv.p = wall((1, 1, 0, 0) if horizontal else (1, 0, 1, 0))
    for y in range(T):
        for x in range(T):
            if (horizontal and 7 <= x <= 24) or (not horizontal and 4 <= y <= 27):
                cv.p[y][x] = P['hl_1']
    if horizontal:
        wood_post(cv.p, 4, 6, 0, 31)
        wood_post(cv.p, 25, 27, 0, 31)
        specs = [(16, 28, 10, 4), (10, 22, 5, 5), (22, 22, 5, 5), (16, 17, 6, 5), (13, 12, 3.5, 3.5), (20, 13, 3.5, 3.5)]
    else:
        wood_beam(cv.p, 0, 31, 0, 3)
        wood_beam(cv.p, 0, 31, 28, 31)
        specs = [(16, 26, 13, 4), (8, 20, 5, 5), (24, 20, 5, 5), (16, 15, 7, 5.5), (16, 8, 4, 3)]
    rocks(cv, specs, WALLP, 17)
    return cv.p


REG['eboulis_ouverture_h'] = lambda n, d: eb_ouv(True)
REG['eboulis_ouverture_v'] = lambda n, d: eb_ouv(False)


@reg('pelle_sol')
def pelle(n, d):
    cv = Cv()
    rocks(cv, [(18, 26, 9, 3.5), (12, 24, 5, 3.5), (24, 24, 4, 3)], FLP, 9)
    line(cv, [(14, 3), (14, 20)], P['wd_lt'])
    line(cv, [(15, 3), (15, 20)], P['wd_md'])
    for y in range(18, 25):
        for x in range(10, 20):
            if abs(x - 14.5) < 4.5 - (y - 18) * 0.5:
                cv.set(x, y, P['mt_lt'] if x < 14 else P['mt_md'])
    for x in range(12, 18):
        cv.set(x, 2, P['wd_hi'])
    cv.outline(O)
    return cv.p


@reg('etabli')
def etabli(n, d):
    cv = Cv()
    for y in range(8, 29):
        for x in range(2, 30):
            if y < 15:
                c = P['wd_hi'] if (x // 5) % 2 else P['wd_lt']
                if y == 14:
                    c = P['wd_dk']
            else:
                c = P['wd_md'] if y < 27 else P['wd_dk']
                if x in (3, 4, 27, 28):
                    c = P['wd_dp']
            cv.set(x, y, c)
    line(cv, [(6, 12), (14, 10)], P['wd_dk'])
    line(cv, [(6, 11), (14, 9)], P['wd_lt'])
    for x in range(16, 26):
        cv.set(x, 11, P['mt_lt'])
        cv.set(x, 12, P['mt_dk'])
    cv.set(26, 11, P['mt_hi'])
    cv.outline(O)
    return cv.p


@reg('panneau_bois')
def panneau(n, d):
    cv = Cv()
    for y in range(22, 31):
        for x in range(14, 18):
            cv.set(x, y, P['wd_md'] if x < 17 else P['wd_dk'])
    for y in range(7, 21):
        for x in range(6, 26):
            c = P['wd_lt'] if y < 9 or (x // 4) % 2 else P['wd_hi']
            if y == 20 or x == 25:
                c = P['wd_dk']
            cv.set(x, y, c)
    for x in range(9, 23):
        cv.set(x, 12, P['wd_dp'])
        cv.set(x, 15, P['wd_dp'])
    cv.set(7, 8, P['mt_lt'])
    cv.set(24, 8, P['mt_lt'])
    cv.outline(O)
    return cv.p


@reg('flaque')
def flaque(n, d):
    cv = Cv()
    for y in range(32):
        for x in range(32):
            dd = ((x + 0.5 - 16) / 11) ** 2 + ((y + 0.5 - 19) / 6) ** 2
            if dd <= 1:
                cv.p[y][x] = P['w_md'] if dd > 0.7 else P['w_lt'] if (x + y) % 5 else P['w_hi']
            elif dd <= 1.25 and (x + y) % 2 == 0:
                cv.p[y][x] = P['fl_dk']
    return cv.p


# ------------------------------------------------------------------ variante sous-sol (recoloration)
def save_sous_sol(S, px):
    out = []
    for row in px:
        nr = []
        for c in row:
            if c is None:
                nr.append(None)
                continue
            r, g, b, a = c
            L = 0.3 * r + 0.59 * g + 0.11 * b
            cyan = b > r + 40 and b > 150
            red = r > 170 and g < 110
            if cyan or red:
                nr.append((int(r * 0.9), int(g * 0.9), int(b * 0.95), a))
            else:
                nr.append((min(255, int(r * 0.52 + L * 0.1)), min(255, int(g * 0.58 + L * 0.1)), min(255, int(b * 0.7 + L * 0.22 + 8)), a))
        out.append(nr)
    save_png(os.path.join(ROOT, 'art', 'tilesets', 'mine_sous_sol.png'), out)
    old = S.name
    S.name = 'mine_sous_sol'
    try:
        with open(os.path.join(ROOT, 'maps', 'tilesets', 'mine_sous_sol.tsx'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(S.tsx())
    finally:
        S.name = old
