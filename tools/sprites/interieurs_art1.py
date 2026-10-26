"""Intérieurs, dessin final, partie 1 : sols, murs, cave, forge."""
import math
import random

import village_art1
import village_art2  # noqa: F401  (réutilise enclume, meule, bac, charbon…)
import village_art3  # noqa: F401
from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, F, mass, ell_shade
from village_art1 import stone_blocks, rgba_

REG = {}
VREG = village_art1.REG


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


EX = dict(
    ce_hi='#7a6250', ce_lt='#5a4636', ce_md='#3e2e24', ce_dk='#261a16',
    cv_hi='#7a6a60', cv_lt='#66564e', cv_md='#4c3e3a', cv_dk='#32282a',
    wd_hi='#c8946a', wd_lt='#a6764a', wd_md='#86583a', wd_dk='#5e3a22',
    day='#f4ecc8', day2='#e0d4a0',
)
P.update({k: rgba(v) for k, v in EX.items()})
SHADOW = (0x1b, 0x14, 0x20, 85)
WPAL = (P['pk_hi'], P['pk_lt'], P['pk_md'], P['pk_dk'])
DPAL = (P['b_lt'], P['b_md'], P['b_dk'], P['O'])


def fshadow(cv, cx, cy, rx, ry, a=85):
    for y in range(cv.h):
        for x in range(cv.w):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1 and cv.p[y][x] is None:
                cv.p[y][x] = (0x1b, 0x14, 0x20, a)


def fix_shadow(p):
    """Remplace l'ombre d'herbe (g_dk) des objets du village par une ombre de sol d'intérieur."""
    out = []
    for row in p:
        out.append([SHADOW if (c is not None and c == P['g_dk']) else c for c in row])
    return out


def reuse(name):
    return lambda n, t: fix_shadow(VREG[name](name, t))


# ------------------------------------------------------------------ sols
def planks_floor(seed, kind='a'):
    t = [[None] * T for _ in range(T)]
    seams = [rnd(r, 0, seed) for r in range(4)]
    for y in range(T):
        r, yy = y // 8, y % 8
        sx = int(seams[r] * 28) + 2
        for x in range(T):
            xs = (x - sx) % 32
            part = 0 if xs < 16 else 1
            v = rnd(r, part, seed + 4)
            base = P['pk_lt'] if v < 0.55 else P['pk_md'] if v < 0.8 else P['pk_hi']
            if kind == 'use':
                base = P['pk_md'] if v < 0.6 else P['pk_dk']
            c = base
            if yy == 7:
                c = P['pk_dk'] if kind != 'use' else P['wd_dk']
            elif yy == 0:
                c = P['pk_hi'] if kind != 'use' else P['pk_lt']
            elif rnd(x // 2, y, seed + 7) < 0.07 and yy in (2, 3, 4):
                c = P['pk_md'] if base != P['pk_md'] else P['pk_dk']
            if xs in (0, 16) and yy < 7:
                c = P['pk_dk']
            t[y][x] = c
    if kind == 'c':
        for r in range(4):
            sx = int(seams[r] * 28) + 2
            for off in (3, 19):
                cv_x = (sx + off) % 32
                t[r * 8 + 3][cv_x] = P['m_dk']
                t[r * 8 + 3][(cv_x + 10) % 32] = P['m_md']
    return t


def slab_floor(seed, kind='a'):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        r = y // 16
        off = 8 if r % 2 else 0
        yy = y % 16
        for x in range(T):
            xx = (x + off) % 32
            k = xx // 16
            xo = xx % 16
            v = rnd(k, r, seed)
            base = P['k_lt'] if v < 0.5 else P['k_md'] if v < 0.96 else P['k_hi']
            if kind == 'c':
                base = P['k_md'] if v < 0.6 else P['k_lt']
            c = base
            if yy == 15 or xo == 15:
                c = P['k_dk']
            elif yy == 0 or xo == 0:
                c = P['k_lt'] if base != P['k_lt'] else P['k_hi']
            elif rnd(x, y, seed + 2) < 0.06:
                c = P['k_dk'] if base != P['k_dk'] else P['k_md']
            t[y][x] = c
    if kind == 'fissure':
        cv = Cv()
        cv.p = t
        for a, b in (((4, 2), (12, 13)), ((12, 13), (9, 22)), ((9, 22), (18, 30)), ((20, 4), (26, 12))):
            cv.line(a[0], a[1], b[0], b[1], P['O'])
    return t


def cave_floor(seed, dirt=False):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, seed) * 0.6 + vnoise(x, y, 8, seed + 3) * 0.4
            if dirt:
                c = rgba_('#8a6a48') if n > 0.62 else rgba_('#5e4630') if n < 0.28 else rgba_('#745a3c')
            else:
                c = P['cv_hi'] if n > 0.72 else P['cv_dk'] if n < 0.3 else P['cv_lt'] if n > 0.5 else P['cv_md']
            t[y][x] = c
    r = random.Random(seed)
    for _ in range(7):
        x, y = r.randrange(T), r.randrange(T)
        t[y][x] = P['cv_hi'] if not dirt else rgba_('#a88a60')
        t[(y + 1) % T][x] = P['cv_dk'] if not dirt else rgba_('#4a3624')
        t[y][(x + 1) % T] = P['cv_lt'] if not dirt else rgba_('#745a3c')
    return t


def suie_floor():
    t = slab_floor(55, 'c')
    mp = {P['k_lt']: P['s_lt'], P['k_md']: P['s_md'], P['k_hi']: rgba_('#6e6874'), P['k_dk']: P['O'], P['white']: P['s_lt']}
    return [[mp.get(c, c) for c in row] for row in t]


REG['sol_bois_a'] = lambda n, t: planks_floor(1)
REG['sol_bois_b'] = lambda n, t: planks_floor(2)
REG['sol_bois_c'] = lambda n, t: planks_floor(3, 'c')
REG['sol_bois_use'] = lambda n, t: planks_floor(4, 'use')
REG['sol_pierre_a'] = lambda n, t: slab_floor(1)
REG['sol_pierre_b'] = lambda n, t: slab_floor(2)
REG['sol_pierre_c'] = lambda n, t: slab_floor(3, 'c')
REG['sol_pierre_fissure'] = lambda n, t: slab_floor(4, 'fissure')
REG['sol_terre_cave'] = lambda n, t: cave_floor(7, True)
REG['sol_cave_a'] = lambda n, t: cave_floor(8)
REG['sol_cave_b'] = lambda n, t: cave_floor(9)
REG['sol_forge_suie'] = lambda n, t: suie_floor()


@reg('sol_braises')
def braises(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 33)
            if n > 0.6:
                cv.p[y][x] = (0x3e, 0x3a, 0x48, 150) if (x + y) % 2 else (0x2a, 0x26, 0x32, 150)
    r = random.Random(5)
    for _ in range(9):
        x, y = r.randrange(2, 30), r.randrange(2, 30)
        cv.set(x, y, P['fi_r'])
        if r.random() < 0.4:
            cv.set(x + 1, y, P['fi_o'])
    return cv.p


@reg('sol_paille')
def paille(name, tile):
    cv = Cv()
    r = random.Random(12)
    for _ in range(26):
        x, y = r.randrange(1, 28), r.randrange(2, 30)
        ln = r.randrange(3, 6)
        sl = r.choice((-1, 0, 1))
        for i in range(ln):
            cv.set(x + i, y + (i * sl) // 3, rgba_('#e0c864') if i % 2 else rgba_('#b89c44'))
    return cv.p


def shade_grad(kind):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            if kind == 'mur':
                a = int(max(0, 130 - y * 8))
            else:
                a = int(max(0, 130 - (x + y) * 4))
            a = (a // 26) * 26
            if a > 0:
                cv.p[y][x] = (0x1b, 0x14, 0x20, a)
    return cv.p


REG['ombre_mur'] = lambda n, t: shade_grad('mur')
REG['ombre_coin'] = lambda n, t: shade_grad('coin')


# ------------------------------------------------------------------ murs
STYLES = ('bois', 'pierre', 'crepi', 'cave')


def face_cv(style, var=0):
    cv = Cv()
    if style == 'bois':
        for y in range(T):
            for x in range(T):
                k = x // 8
                v = rnd(k, 0, 3 + var)
                base = P['pk_lt'] if v < 0.5 else P['pk_md']
                c = base
                if x % 8 == 7:
                    c = P['pk_dk']
                elif x % 8 == 0:
                    c = P['pk_hi'] if base == P['pk_lt'] else P['pk_lt']
                elif rnd(x, y // 3, 5 + var) < 0.04:
                    c = P['pk_dk'] if base == P['pk_md'] else P['pk_md']
                cv.p[y][x] = c
    elif style == 'pierre':
        stone_blocks(cv, 0, 0, 31, 31, 21 + var, (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 8, 16)
    elif style == 'crepi':
        for y in range(T):
            for x in range(T):
                n = vnoise(x, y, 8, 41 + var)
                c = P['pl_hi'] if n > 0.72 else P['pl_md'] if n < 0.25 else P['pl_lt']
                if rnd(x, y, 7) < 0.03:
                    c = P['pl_md']
                cv.p[y][x] = c
    else:
        for y in range(T):
            for x in range(T):
                n = vnoise(x // 2, y, 8, 61 + var) * 0.6 + rnd(x // 3, 0, 4) * 0.4
                cv.p[y][x] = P['cv_hi'] if n > 0.78 else P['cv_dk'] if n < 0.3 else P['cv_lt'] if n > 0.55 else P['cv_md']
    return cv


def face_finish(cv, style):
    # ombre sous le plafond, plinthe en bas
    for x in range(T):
        cv.p[0][x] = P['ce_dk']
        cv.p[1][x] = P['ce_md'] if x % 2 == 0 else cv.p[1][x]
        cv.p[2][x] = cv.p[2][x] if x % 2 else P['ce_md'] if False else cv.p[2][x]
    for y in (1, 2):
        for x in range(T):
            if (x + y) % 2 == 0:
                cv.p[y][x] = tint(cv.p[y][x], 0.7)
    if style == 'crepi':
        for x in range(T):
            cv.p[19][x] = P['wd_hi']
            cv.p[20][x] = P['wd_md']
            for y in range(21, 31):
                k = x // 8
                cv.p[y][x] = P['pk_dk'] if x % 8 == 7 or y in (21,) else P['pk_lt'] if (k % 2) else P['pk_md']
        for x in range(T):
            cv.p[31][x] = P['wd_dk']
    elif style == 'cave':
        for x in range(T):
            for y in range(29, 32):
                cv.p[y][x] = P['cv_dk']
    else:
        for x in range(T):
            cv.p[26][x] = P['wd_hi'] if style == 'bois' else P['k_hi']
            for y in range(27, 31):
                cv.p[y][x] = P['wd_md'] if style == 'bois' else P['k_md']
            cv.p[30][x] = P['wd_dk'] if style == 'bois' else P['k_dk']
            cv.p[31][x] = O
    return cv.p


def window_face(cv, style, stained=False):
    box(cv, 8, 5, 23, 23, P['wd_hi'], P['wd_md'], P['wd_dk'])
    if stained:
        cols = [P['gl_md'], P['f_red'], P['f_yel'], P['g_lt'], P['f_vio'], P['gl_hi']]
        for y in range(7, 22):
            for x in range(10, 22):
                if y < 11 and ((x - 15.5) ** 2 + (y - 11) ** 2) > 30:
                    continue
                cv.p[y][x] = cols[((x - 10) // 4 + (y - 7) // 4 * 2) % len(cols)]
        for x in range(10, 22):
            cv.p[14][x] = P['m_dk']
        for y in range(7, 22):
            cv.p[y][13] = P['m_dk']
            cv.p[y][18] = P['m_dk']
        return
    for y in range(7, 22):
        for x in range(10, 22):
            cv.p[y][x] = P['day'] if y < 12 else P['gl_hi'] if y < 17 else P['gl_md']
    for y in range(7, 22):
        cv.p[y][15] = P['wd_dk']
        cv.p[y][16] = P['wd_md']
    for x in range(10, 22):
        cv.p[14][x] = P['wd_dk']
    box(cv, 6, 23, 25, 25, P['wd_hi'], P['wd_lt'], P['wd_dk'])


def deco_face(cv, style):
    if style == 'pierre':                        # écusson : blason sur fond de pierre
        for y in range(6, 24):
            for x in range(9, 23):
                if abs(x - 15.5) < 6.5 - max(0, (y - 14)) * 0.7:
                    cv.p[y][x] = P['ra_lt'] if x < 16 else P['ra_md']
        for y in range(6, 24):
            for x in range(9, 23):
                if cv.p[y][x] in (P['ra_lt'], P['ra_md']) and (x in (9, 10, 21, 22) or y == 6):
                    cv.p[y][x] = P['gold_hi']
        for y in range(10, 18):
            cv.p[y][15] = P['gold_hi']
            cv.p[y][16] = P['or_']
        for x in range(12, 20):
            cv.p[13][x] = P['gold_hi']
    else:                                        # tableau encadré
        box(cv, 7, 6, 24, 20, P['gold_hi'], P['or_'], P['b_dk'])
        for y in range(8, 19):
            for x in range(9, 23):
                cv.p[y][x] = rgba_('#8ac0e0') if y < 14 else P['g_md']
        for x in range(9, 23):
            if (x - 9) % 5 < 2:
                cv.p[13][x] = P['k_lt']
        ell(cv, 17, 10, 2, 2, P['f_yel'])


def door_face(cv, style):
    box(cv, 4, 2, 27, 31, P['wd_hi'], P['wd_dk'], P['wd_dk'])
    for y in range(4, 31):
        for x in range(6, 26):
            k = (x - 6) // 5
            ar = ((x - 15.5) / 10.0) ** 2 + ((y - 15) / 12.0) ** 2
            if y < 15 and ar > 1:
                continue
            c = P['pk_hi'] if (x - 6) % 5 == 0 else P['pk_dk'] if (x - 6) % 5 == 4 else (P['pk_lt'] if k % 2 else P['pk_md'])
            cv.p[y][x] = c
    for y in (12, 24):
        for x in range(6, 26):
            cv.p[y][x] = P['m_dk']
    box(cv, 20, 17, 22, 19, P['gold_hi'], P['or_'], P['b_dk'])
    for x in range(4, 28):
        cv.p[31][x] = P['k_dk']


def reg_walls():
    for st in STYLES:
        ce = (lambda n, t, st=st: ceiling(st))
        REG[f'mur_{st}_plafond'] = ce
        REG[f'mur_{st}_coin_haut_g'] = (lambda n, t, st=st: ceiling(st, 'g'))
        REG[f'mur_{st}_coin_haut_d'] = (lambda n, t, st=st: ceiling(st, 'd'))
        REG[f'mur_{st}_face'] = (lambda n, t, st=st: face_finish(face_cv(st), st))
        REG[f'mur_{st}_face_b'] = (lambda n, t, st=st: face_finish(face_cv(st, 3), st))

        def fen(n, t, st=st):
            cv = face_cv(st)
            window_face(cv, st)
            return face_finish(cv, st)
        REG[f'mur_{st}_fenetre'] = fen

        def dec(n, t, st=st):
            cv = face_cv(st)
            deco_face(cv, st)
            return face_finish(cv, st)
        REG[f'mur_{st}_face_deco'] = dec

        def vit(n, t, st=st):
            cv = face_cv(st)
            window_face(cv, st, True)
            return face_finish(cv, st)
        REG[f'mur_{st}_vitrail'] = vit

        def pint(n, t, st=st):
            cv = face_cv(st)
            door_face(cv, st)
            for x in range(T):
                cv.p[0][x] = P['ce_dk']
            return cv.p
        REG[f'mur_{st}_porte_interne'] = pint
        REG[f'mur_{st}_lat_g'] = (lambda n, t, st=st: side('g'))
        REG[f'mur_{st}_lat_d'] = (lambda n, t, st=st: side('d'))
        REG[f'mur_{st}_bas'] = (lambda n, t, st=st: bottom())
        REG[f'mur_{st}_coin_bas_g'] = (lambda n, t, st=st: corner_bas('g'))
        REG[f'mur_{st}_coin_bas_d'] = (lambda n, t, st=st: corner_bas('d'))
        if st != 'cave':
            REG[f'porte_sortie_{st}'] = (lambda n, t, st=st: exit_door(st))


def ceiling(style, side_=None):
    cv = Cv()
    cave = style == 'cave'
    for y in range(T):
        for x in range(T):
            r = y // 8
            yy = y % 8
            if cave:
                n = vnoise(x, y, 4, 71) * 0.6 + vnoise(x, y, 8, 72) * 0.4
                c = P['cv_dk'] if n < 0.55 else P['cv_md']
                if n > 0.8:
                    c = P['cv_lt']
            else:
                seam = (x + (11 * r)) % 32 == 0
                c = P['ce_lt'] if rnd(r, x // 16, 8) < 0.5 else P['ce_md']
                if yy == 7:
                    c = P['ce_dk']
                elif yy == 0:
                    c = P['ce_hi'] if c == P['ce_lt'] else P['ce_lt']
                if seam:
                    c = P['ce_dk']
            cv.p[y][x] = c
    for x in range(T):                                              # corniche en bas (bord de la salle)
        cv.p[27][x] = P['ce_dk']
        cv.p[28][x] = P['ce_hi'] if not cave else P['cv_hi']
        cv.p[29][x] = P['ce_lt'] if not cave else P['cv_lt']
        cv.p[30][x] = P['ce_md'] if not cave else P['cv_md']
        cv.p[31][x] = P['ce_dk']
    if side_ == 'g':
        vline(cv, 0, 0, 31, O)
        vline(cv, 1, 0, 28, P['ce_hi'] if not cave else P['cv_hi'])
    if side_ == 'd':
        vline(cv, 31, 0, 31, O)
        vline(cv, 30, 0, 28, P['ce_dk'])
    if side_ is None:
        for x in range(T):
            cv.p[0][x] = P['ce_dk'] if rnd(x, 0, 2) < 2 else cv.p[0][x]
    return cv.p


def wall_top_color(x, y):
    return P['ce_lt'] if (y // 8) % 2 else P['ce_md']


def side(which):
    cv = Cv()
    xs = range(0, 8) if which == 'g' else range(24, 32)
    for y in range(T):
        for x in xs:
            c = P['ce_lt'] if (y // 8) % 2 == 0 else P['ce_md']
            if y % 8 == 7:
                c = P['ce_dk']
            cv.p[y][x] = c
    edge_out, edge_hi, edge_in = (0, 1, 7) if which == 'g' else (31, 30, 24)
    for y in range(T):
        cv.p[y][edge_out] = O
        cv.p[y][edge_in] = P['ce_hi']
        cv.p[y][edge_in + (1 if which == 'g' else -1)] = None
    for y in range(T):                                               # ombre portée sur le sol
        xx = [8, 9, 10] if which == 'g' else [23, 22, 21]
        for k, x in enumerate(xx):
            if (x + y) % 2 == 0 or k == 0:
                cv.p[y][x] = (0x1b, 0x14, 0x20, 100 - k * 30)
    return cv.p


def bottom():
    cv = Cv()
    for y in range(24, 32):
        for x in range(T):
            c = P['ce_lt'] if (x // 8) % 2 == 0 else P['ce_md']
            if x % 8 == 7:
                c = P['ce_dk']
            cv.p[y][x] = c
    for x in range(T):
        cv.p[24][x] = P['ce_hi']
        cv.p[31][x] = O
        for k, y in enumerate((23, 22, 21)):
            if (x + y) % 2 == 0 or k == 0:
                cv.p[y][x] = (0x1b, 0x14, 0x20, 100 - k * 30)
    return cv.p


def corner_bas(which):
    a = side(which)
    b = bottom()
    return [[(b[y][x] if b[y][x] is not None and (y >= 24 or a[y][x] is None) else a[y][x]) for x in range(T)] for y in range(T)]


def exit_door(style):
    p = bottom()
    cv = Cv()
    cv.p = p
    for y in range(21, 24):
        for x in range(6, 26):
            cv.p[y][x] = None
    for y in range(24, 32):                                          # ouverture sur l'extérieur
        for x in range(6, 26):
            cv.p[y][x] = P['day'] if y < 28 else P['day2']
    for y in range(24, 32):
        cv.p[y][5] = P['wd_dk']
        cv.p[y][26] = P['wd_dk']
        cv.p[y][6] = P['wd_hi'] if y > 24 else None
    for x in range(6, 26):
        cv.p[24][x] = P['wd_md']
        cv.p[25][x] = P['wd_dk']
    for x in range(6, 26):
        cv.p[30][x] = P['k_lt']
        cv.p[31][x] = P['k_dk']
    for y in range(24, 32):                                          # battant ouvert contre le montant
        cv.p[y][7] = P['pk_md']
        cv.p[y][8] = P['pk_dk']
    return cv.p


reg_walls()


# ------------------------------------------------------------------ cave
@reg('mur_cave_face_b')
def cave_face_b(name, tile):
    cv = face_cv('cave', 3)
    for (x0, w, h) in ((4, 5, 8), (13, 6, 11), (24, 4, 7)):          # stalactites
        for y in range(2, 2 + h):
            hw = w * (1 - (y - 2) / float(h)) / 2.0
            for x in range(int(x0 + w / 2 - hw), int(x0 + w / 2 + hw) + 1):
                cv.p[y][x] = P['cv_hi'] if x < x0 + w / 2 else P['cv_dk']
        cv.set(x0 + w // 2, 2 + h, P['cv_dk'])
    return face_finish(cv, 'cave')


@reg('mur_cave_fissure')
def cave_fissure(name, tile):
    cv = face_cv('cave')
    pts = [(14, 3), (17, 8), (13, 13), (18, 19), (14, 25), (16, 29)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], P['O'])
        cv.line(a[0] + 1, a[1], b[0] + 1, b[1], P['cv_hi'])
    for (x0, y0, x1, y1) in ((17, 8, 24, 10), (13, 19, 7, 22)):
        cv.line(x0, y0, x1, y1, P['cv_dk'])
    return face_finish(cv, 'cave')


@reg('mur_cave_ouvert')
def cave_ouvert(name, tile):
    cv = Cv()
    for y in range(3, 32):
        for x in range(3, 29):
            e = ((x - 15.5) / 12.0) ** 2 + ((y - 22) / 18.0) ** 2
            if e <= 1 + (rnd(x, y, 8) - 0.5) * 0.3:
                cv.p[y][x] = P['v_dk'] if e > 0.5 else P['O']
    cv.outline(P['cv_dk'])
    return cv.p


@reg('escalier_cave_haut', 'escalier_cave_bas')
def escalier_cave(name, tile):
    cv = Cv()
    haut = name.endswith('haut')
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = P['cv_md'] if (x < 6 or x > 25) else None
    for x in list(range(0, 6)) + list(range(26, 32)):
        for y in range(T):
            cv.p[y][x] = P['cv_hi'] if x in (1, 26) else P['cv_dk'] if x in (5, 31) else P['cv_lt'] if rnd(x, y, 3) > 0.3 else P['cv_md']
    for y in range(T):
        step = y // 8
        yy = y % 8
        for x in range(6, 26):
            if haut:
                lum = [P['k_dk'], P['k_md'], P['k_lt'], P['k_hi']][step]
                c = lum if yy > 1 else P['O'] if yy == 0 else P['k_hi']
            else:
                lum = [P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']][step]
                c = P['k_hi'] if yy == 0 else lum
                if yy == 7:
                    c = P['k_dk']
            cv.p[y][x] = c
    if haut:
        for x in range(6, 26):
            cv.p[0][x] = P['v_dk']
            cv.p[1][x] = P['v_dk']
    return cv.p


@reg('piedestal')
def piedestal(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 12, 3)
    box(cv, 7, 24, 25, 29, P['k_hi'], P['k_lt'], P['k_dk'])
    for y in range(13, 24):
        for x in range(9, 23):
            cv.p[y][x] = P['k_hi'] if x < 11 else P['k_dk'] if x > 20 else P['k_lt']
    box(cv, 6, 8, 25, 13, P['k_hi'], P['k_lt'], P['k_dk'])
    ell(cv, 16, 10, 5, 1.5, P['k_hi'])
    cv.outline()
    return cv.p


@reg('toiles_araignee')
def toiles(name, tile):
    cv = Cv()
    W = (0xe6, 0xe6, 0xf0, 150)
    for a in range(0, 91, 15):
        r = math.radians(a)
        for t in range(0, 22):
            cv.set(int(t * math.cos(r)), int(t * math.sin(r)), W)
    for rr in (6, 11, 16, 21):
        for a in range(0, 91, 6):
            r = math.radians(a)
            cv.set(int(rr * math.cos(r) * 0.98), int(rr * math.sin(r) * 0.98), W)
    cv.set(14, 17, P['O'])
    cv.set(14, 18, P['O'])
    return cv.p


# ------------------------------------------------------------------ forge
def foyer():
    cv = Cv(64, 64)
    # hotte de pierre qui se resserre vers le haut
    for y in range(0, 34):
        hw = 12 + (y / 33.0) * 20
        for x in range(int(32 - hw), int(32 + hw)):
            c = P['s_lt'] if (x + y // 2) % 11 else P['s_md']
            if (y % 8) == 7:
                c = P['s_dk']
            if x < 32 - hw + 3:
                c = P['k_md']
            cv.p[y][x] = c
    box(cv, 18, 0, 46, 5, P['s_lt'], P['s_md'], P['O'])             # conduit
    # manteau
    box(cv, 2, 30, 61, 36, P['b_lt'], P['b_md'], P['b_dk'])
    # ouverture
    for y in range(36, 64):
        for x in range(4, 60):
            cv.p[y][x] = P['s_md'] if (x < 8 or x > 55) else P['s_dk']
    for y in range(38, 64):
        for x in range(9, 55):
            e = ((x - 31.5) / 23.0) ** 2 + ((y - 62) / 25.0) ** 2
            if e <= 1:
                d = ((x - 31.5) / 20.0) ** 2 + ((y - 62) / 20.0) ** 2
                c = P['fi_d']
                if d < 0.85:
                    c = P['fi_r']
                if d < 0.55 + 0.12 * rnd(x, y, 5):
                    c = P['fi_o']
                if d < 0.25:
                    c = P['fi_y']
                cv.p[y][x] = c
    for x in range(10, 54, 6):                                       # braises en bas
        for y in (60, 61, 62):
            cv.p[y][x] = P['fi_y'] if rnd(x, y, 2) > 0.5 else P['fi_o']
    for x in range(4, 60):
        cv.p[63][x] = P['s_dk']
        cv.p[62][x] = P['s_lt'] if x % 2 else P['s_md'] if (x < 9 or x > 54) else cv.p[62][x]
    cv.outline()
    return cv


_FOYER = foyer()
for _n, (_c, _r) in dict(foyer_haut_g=(0, 0), foyer_haut_d=(1, 0), foyer_bas_g=(0, 1), foyer_bas_d=(1, 1)).items():
    REG[_n] = (lambda n, t, c=_c, r=_r: _FOYER.crop(c * T, r * T))

REG['enclume_int'] = reuse('enclume')
REG['bac_trempe_int'] = reuse('bac_trempe')
REG['charbon_int'] = reuse('tas_charbon')
REG['meule_int'] = reuse('meule')


@reg('soufflet')
def soufflet(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 12, 3)
    for y in range(8, 24):                                           # corps en accordéon
        t = (y - 8) / 15.0
        hw = 4 + 8 * t
        for x in range(int(14 - hw / 1.3), int(14 + hw * 1.1) + 1):
            c = P['pk_hi'] if y % 4 == 0 else P['b_md'] if x < 14 else P['b_dk']
            cv.set(x + 4, y, c)
    for y in range(9, 23, 4):
        for x in range(6, 28):
            if cv.get(x, y) is not None:
                cv.set(x, y, P['b_lt'])
    box(cv, 6, 24, 26, 28, P['b_lt'], P['b_md'], P['b_dk'])
    for x in range(1, 10):                                           # tuyau et manche
        cv.set(1 + x, 22 + x // 4, P['m_md'])
        cv.set(1 + x, 21 + x // 4, P['m_lt'])
    for y in range(3, 10):
        cv.set(24 + (y - 3) // 4, y, P['b_md'])
        cv.set(25 + (y - 3) // 4, y, P['b_dk'])
    cv.outline()
    return cv.p


def workbench(pos):
    cv = Cv()
    fshadow(cv, 16, 30, 16, 2, 80)
    x0 = 2 if pos == 'g' else 0
    x1 = 29 if pos == 'd' else 31
    for y in range(8, 17):
        for x in range(x0, x1 + 1):
            cv.p[y][x] = P['pk_hi'] if y == 8 else P['pk_lt'] if y < 15 else P['pk_md']
            if (x + 3) % 8 == 0 and 9 <= y < 15:
                cv.p[y][x] = P['pk_md']
    for y in range(17, 21):
        for x in range(x0, x1 + 1):
            cv.p[y][x] = P['pk_md'] if y < 20 else P['pk_dk']
    for lx in ((x0 + 1,) if pos == 'g' else (x1 - 3,) if pos == 'd' else ()):
        box(cv, lx, 21, lx + 2, 29, P['b_lt'], P['b_md'], P['b_dk'])
    if pos == 'g':                                                   # tenailles et marteau sur l'établi
        for t in range(10):
            cv.set(8 + t, 12 - t // 4, P['m_lt'])
            cv.set(8 + t, 13 - t // 4, P['m_dk'])
        box(cv, 20, 10, 24, 12, P['m_hi'], P['m_lt'], P['m_dk'])
        vline(cv, 23, 12, 15, P['b_md'])
    else:
        box(cv, 8, 9, 14, 13, P['k_hi'], P['k_lt'], P['k_dk'])       # lingot
        for x in range(18, 28):
            cv.set(x, 12, P['m_hi'])
            cv.set(x, 13, P['m_md'])
    if pos == 'g':
        for y in range(8, 29):
            cv.p[y][x0] = O
    if pos == 'd':
        for y in range(8, 29):
            cv.p[y][x1] = O
    cv.outline()
    return cv.p


REG['etabli_g'] = lambda n, t: workbench('g')
REG['etabli_d'] = lambda n, t: workbench('d')


def wall_rack_bg(style='pierre'):
    return face_cv(style)


@reg('rateliers_epees')
def rateliers_epees(name, tile):
    cv = face_cv('pierre')
    for x0 in (3, 25):
        box(cv, x0, 4, x0 + 3, 31, P['b_lt'], P['b_md'], P['b_dk'])
    for y in (8, 22):
        box(cv, 3, y, 28, y + 2, P['b_lt'], P['b_md'], P['b_dk'])
    for x in (9, 14, 19, 24 - 1):
        for y in range(10, 22):
            cv.p[y][x] = P['m_hi'] if y % 3 else P['white']
            cv.p[y][x + 1] = P['m_md']
        for xx in range(x - 2, x + 4):
            cv.p[10][xx] = P['or_']
        cv.p[9][x] = P['b_dk']
        cv.p[22][x] = P['m_dk']
    for x in range(T):
        cv.p[0][x] = P['ce_dk']
    return cv.p


@reg('outils_muraux')
def outils_muraux(name, tile):
    cv = Cv()
    hline(cv, 3, 29, 7, P['b_dk'])
    hline(cv, 3, 29, 8, P['b_md'])
    for x in (6, 15, 24):
        cv.set(x, 6, P['m_dk'])
    for y in range(9, 24):                                           # marteau
        cv.set(7, y, P['b_md'])
        cv.set(8, y, P['b_dk'])
    box(cv, 4, 9, 11, 12, P['m_hi'], P['m_lt'], P['m_dk'])
    for t in range(15):                                              # tenailles
        cv.set(14 + t // 6, 9 + t, P['m_lt'])
        cv.set(17 - t // 6, 9 + t, P['m_md'])
    cv.set(16, 9, P['m_dk'])
    for y in range(9, 24):                                           # scie : lame dentelée
        cv.set(24, y, P['m_hi'])
        cv.set(25 + (y % 2), y, P['m_lt'])
    box(cv, 22, 20, 27, 25, P['b_lt'], P['b_md'], P['b_dk'])
    cv.outline()
    return cv.p


@reg('armure_socle')
def armure_socle(name, tile):
    cv = Cv()
    fshadow(cv, 16, 29, 11, 3)
    box(cv, 7, 25, 25, 29, P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(12, 25):                                          # cuirasse
        for x in range(10, 23):
            if abs(x - 16) < 6.5 - (y - 12) * 0.12:
                cv.p[y][x] = P['m_hi'] if x < 13 else P['m_dk'] if x > 19 else P['m_lt']
    for x in range(10, 23):
        cv.p[18][x] = P['m_dk']
    for x in range(14, 19):
        cv.p[14][x] = P['m_dk']
    ell_shade(cv, 16, 8, 5, 5, (P['m_hi'], P['m_lt'], P['m_md'], P['m_dk']), 2, 0.1)   # heaume
    for x in range(12, 21):
        cv.p[9][x] = P['O']
    vline(cv, 16, 4, 6, P['f_red'])
    box(cv, 5, 13, 9, 19, P['m_hi'], P['m_lt'], P['m_dk'])           # épaulières
    box(cv, 23, 13, 27, 19, P['m_hi'], P['m_lt'], P['m_dk'])
    cv.outline()
    return cv.p


@reg('lingots')
def lingots(name, tile):
    cv = face_cv('pierre')
    box(cv, 2, 3, 29, 31, P['b_lt'], P['b_dk'], P['O'])
    for y0 in (6, 16, 26):
        box(cv, 3, y0 + 3, 28, y0 + 5, P['b_lt'], P['b_md'], P['b_dk'])
    r = random.Random(3)
    for y0 in (6, 16):
        x = 5
        while x < 25:
            w = r.choice((5, 6, 7))
            box(cv, x, y0 - 1 + 1, x + w, y0 + 2, P['white'] if r.random() < 0.3 else P['m_hi'], P['m_lt'], P['m_dk'])
            x += w + 1
    return cv.p


@reg('bouclier_mural')
def bouclier(name, tile):
    cv = Cv()
    ell_shade(cv, 16, 16, 10, 10, (P['m_hi'], P['m_lt'], P['m_md'], P['m_dk']), 4, 0.1)
    ell(cv, 16, 16, 7, 7, P['ra_md'])
    for y in range(9, 24):
        for x in range(9, 23):
            if cv.p[y][x] == P['ra_md'] and (x < 16):
                cv.p[y][x] = P['ra_lt']
    ell(cv, 16, 16, 2.5, 2.5, P['gold_hi'])
    vline(cv, 16, 9, 23, P['m_dk'])
    hline(cv, 9, 23, 16, P['m_dk'])
    ell(cv, 16, 16, 2.5, 2.5, P['gold_hi'])
    cv.outline()
    return cv.p
