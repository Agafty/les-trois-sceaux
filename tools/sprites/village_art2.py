"""Village, dessin final, partie 2 : toits, façades, forge."""
import random

from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, F, GRASS
from village_art1 import REG, reg, stone_blocks, rgba_

RP = {  # (hi, lt, md, dk) par style de toit
    'a': (P['ra_hi'], P['ra_lt'], P['ra_md'], P['ra_dk']),
    'b': (P['rb_hi'], P['rb_lt'], P['rb_md'], P['rb_dk']),
    'c': (P['rc_hi'], P['rc_lt'], P['rc_md'], P['rc_dk']),
}
WALL = {'a': P['pl_lt'], 'b': P['k_lt'], 'c': P['pk_lt']}
WALL_SH = {'a': P['pl_dk'], 'b': P['k_dk'], 'c': P['pk_dk']}
WALL_MD = {'a': P['pl_md'], 'b': P['k_md'], 'c': P['pk_md']}


def roof_px(style, x, y, var=0):
    hi, lt, md, dk = RP[style]
    if style in ('a', 'b'):
        r = y // 8
        off = 4 if r % 2 else 0
        xx = x + off
        xo, yy = xx % 8, y % 8
        j = rnd(xx // 8, r, 5 + var * 11)
        base = md if j < (0.16 + 0.12 * var) else lt
        if style == 'a':
            if yy == 7:
                return md if xo in (0, 7) else dk
            if xo == 7:
                return md
            if yy == 0 or (xo == 0 and yy < 6):
                return hi
            if yy == 6 and 2 <= xo <= 5:
                return md if base == lt else dk
            return base
        if yy == 7 or xo == 7:
            return dk
        if yy == 0 or xo == 0:
            return hi if base == lt else lt
        if rnd(x, y, 2 + var) < 0.05:
            return md if base == lt else dk
        return base
    sx = x // 2
    yy = (y + sx * 5 + var * 3) % 9
    if y % 16 == 15:
        return dk
    if y % 16 == 0:
        return hi
    if yy == 0:
        return dk if x % 2 == 0 else md
    if yy == 1:
        return hi if x % 2 == 0 else lt
    return md if x % 2 else lt


def roof_cv(style, var=0):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = roof_px(style, x, y, var)
    return cv


def roof_edges(cv, style, pos):
    hi, lt, md, dk = RP[style]
    if pos == 'g':
        for y in range(T):
            cv.p[y][0] = O
            cv.p[y][1] = md
            cv.p[y][2] = dk
    if pos == 'd':
        for y in range(T):
            cv.p[y][31] = O
            cv.p[y][30] = md
            cv.p[y][29] = dk


def roof_row(style, row, pos='m', var=0):
    hi, lt, md, dk = RP[style]
    cv = roof_cv(style, 1 if var == 2 else 0)
    if row == 'haut':
        for x in range(T):
            cv.p[0][x] = O
            cv.p[1][x] = hi
            cv.p[2][x] = hi if style != 'b' else lt
            cv.p[3][x] = lt
            cv.p[4][x] = md
            cv.p[5][x] = dk
            seg = 8 if var != 2 else 6
            if x % seg == seg - 1:
                for yy in (1, 2, 3):
                    cv.p[yy][x] = md
            if var == 2 and x % 12 == 5:
                cv.p[1][x] = P['white'] if style != 'c' else P['rc_hi']
        cv.p[6][0] = cv.p[6][0]
    if row == 'bas':
        for y in range(24, T):
            for x in range(T):
                cv.p[y][x] = None
        for x in range(T):
            cv.p[24][x] = md
            cv.p[25][x] = hi
            cv.p[26][x] = lt
            cv.p[27][x] = md
            cv.p[28][x] = dk
            cv.p[29][x] = O
            cv.p[30][x] = WALL_SH[style]
            cv.p[31][x] = WALL_SH[style] if x % 2 == 0 else WALL_MD[style]
        for x in range(0, T, 8):
            cv.p[25][x] = md
    roof_edges(cv, style, pos)
    if row == 'haut' and pos == 'g':
        cv.p[0][0] = None
        cv.p[0][1] = O
    if row == 'haut' and pos == 'd':
        cv.p[0][31] = None
        cv.p[0][30] = O
    if row == 'bas' and pos == 'g':
        for y in range(24, 29):
            cv.p[y][0] = O
        cv.p[29][0] = None
        cv.p[29][1] = O
    if row == 'bas' and pos == 'd':
        for y in range(24, 29):
            cv.p[y][31] = O
        cv.p[29][31] = None
        cv.p[29][30] = O
    return cv


def reg_roofs():
    for st in 'abc':
        for pos in ('g', 'm', 'd'):
            for row in ('haut', 'mil', 'bas'):
                nm = f'toit_{st}_{row}_{pos}'
                REG[nm] = (lambda n, t, st=st, row=row, pos=pos: roof_row(st, row, pos).p)
        REG[f'toit_{st}_mil_m2'] = (lambda n, t, st=st: roof_row(st, 'mil', 'm', 2).p)
        REG[f'toit_{st}_haut_m2'] = (lambda n, t, st=st: roof_row(st, 'haut', 'm', 2).p)
        REG[f'toit_{st}_cheminee'] = (lambda n, t, st=st: chimney(st))
        REG[f'toit_{st}_lucarne'] = (lambda n, t, st=st: dormer(st))
        REG[f'toit_{st}_flanc_g'] = (lambda n, t, st=st: flank(st, 'g'))
        REG[f'toit_{st}_flanc_d'] = (lambda n, t, st=st: flank(st, 'd'))


def roof_shadow(cv, x0, y0, x1, y1, style):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x + y) % 2 == 0 and cv.p[y][x] is not None:
                cv.p[y][x] = RP[style][3]


def chimney(style):
    cv = roof_cv(style)
    roof_shadow(cv, 23, 8, 29, 25, style)
    box(cv, 9, 9, 21, 23, P['k_hi'], P['k_lt'], P['k_dk'])
    for y in range(10, 23):                                  # briques
        for x in range(10, 21):
            if (y - 10) % 4 == 3:
                cv.p[y][x] = P['k_md']
            elif (x - 10 + ((y - 10) // 4) * 3) % 6 == 5:
                cv.p[y][x] = P['k_md']
    box(cv, 7, 3, 23, 9, P['k_hi'], P['k_lt'], P['k_dk'])    # couronnement
    box(cv, 10, 5, 20, 8, P['s_dk'], P['s_dk'], P['s_dk'], edge=False)
    hline(cv, 11, 18, 5, P['s_md'])
    cv.outline()
    return cv.p


def dormer(style):
    hi, lt, md, dk = RP[style]
    cv = roof_cv(style)
    roof_shadow(cv, 24, 14, 29, 28, style)
    for y in range(12, 27):                                  # façade de la lucarne
        for x in range(8, 24):
            cv.p[y][x] = WALL[style]
            if x in (8, 9):
                cv.p[y][x] = P['pl_hi'] if style == 'a' else P['k_hi'] if style == 'b' else P['pk_hi']
            if x in (22, 23):
                cv.p[y][x] = WALL_MD[style]
    box(cv, 12, 15, 19, 23, P['b_lt'], P['gl_md'], P['b_dk'])
    vline(cv, 15, 16, 22, P['b_md'])
    hline(cv, 13, 18, 19, P['b_md'])
    cv.p[16][13] = P['gl_hi']
    cv.p[17][13] = P['gl_hi']
    hline(cv, 11, 20, 24, P['b_lt'])
    for y in range(3, 12):                                   # petit toit à deux pans
        w = (y - 3) * 1.9 + 1
        for x in range(int(16 - w), int(16 + w) + 1):
            if 6 <= x <= 25:
                cv.p[y][x] = hi if x < 16 else lt if (x + y) % 5 else md
        cv.set(int(16 + w), y, dk)
    hline(cv, 6, 25, 11, dk)
    cv.outline()
    return cv.p


def flank(style, side):
    hi, lt, md, dk = RP[style]
    cv = roof_cv(style)
    for y in range(T):
        for x in range(T):
            xx = x if side == 'g' else 31 - x
            lim = 10 - y * 0.18
            if xx < lim:
                cv.p[y][x] = md if (x + y) % 2 == 0 or y % 8 == 7 else dk
            elif abs(xx - lim) < 1.2:
                cv.p[y][x] = hi
    roof_edges(cv, style, side)
    return cv.p


# ------------------------------------------------------------------ façades
def wall_cv(style, var=0):
    cv = Cv()
    if style == 'a':
        for y in range(T):
            for x in range(T):
                c = P['pl_lt']
                n = vnoise(x, y, 8, 15 + var)
                if n > 0.72:
                    c = P['pl_hi']
                elif n < 0.22:
                    c = P['pl_md']
                if rnd(x, y, 1 + var) < 0.03:
                    c = P['pl_md']
                cv.p[y][x] = c
    elif style == 'b':
        stone_blocks(cv, 0, 0, 31, 31, 9 + var)
    else:
        for y in range(T):
            for x in range(T):
                k = x // 4
                c = P['pk_lt'] if k % 2 == 0 else P['pk_hi'] if rnd(k, y // 9, 3 + var) > 0.7 else P['pk_lt']
                if x % 4 == 3:
                    c = P['pk_dk']
                elif x % 4 == 0:
                    c = P['pk_hi']
                elif rnd(x, y, var + 2) < 0.04:
                    c = P['pk_md']
                if (y + k * 7) % 24 == 11 and x % 4 == 1:
                    c = P['pk_dk']
                cv.p[y][x] = c
    return cv


def wall_finish(cv, style):
    """Ombre sous l'avant-toit en haut, socle en bas."""
    sh, md = WALL_SH[style], WALL_MD[style]
    for x in range(T):
        cv.p[0][x] = sh if style != 'b' else sh
        cv.p[1][x] = sh if x % 2 == 0 else md
        cv.p[2][x] = md
        cv.p[3][x] = md if x % 2 == 0 else cv.p[3][x]
    if style == 'a':
        for x in range(T):                                    # lisse de bois et socle de pierre
            cv.p[24][x] = P['b_lt']
            cv.p[25][x] = P['b_md']
            cv.p[26][x] = P['b_dk']
        for y in range(27, 31):
            for x in range(T):
                r = (y - 27) // 2
                xx = x + (8 if r % 2 else 0)
                cv.p[y][x] = P['k_dk'] if (y - 27) % 2 == 1 or xx % 16 == 15 else P['k_lt'] if (xx % 16) < 3 else P['k_md']
    elif style == 'b':
        for y in range(27, 31):
            for x in range(T):
                cv.p[y][x] = P['k_dk'] if y == 30 or x % 16 == 15 else P['k_md']
    else:
        for x in range(T):
            cv.p[26][x] = P['b_md']
            cv.p[27][x] = P['b_lt'] if x % 2 else P['b_md']
            for y in range(28, 31):
                cv.p[y][x] = P['b_dk'] if x % 6 else P['b_md']
    for x in range(T):
        cv.p[31][x] = O


def corner(cv, style, side):
    xs = range(0, 5) if side == 'g' else range(27, 32)
    for y in range(0, 31):
        for x in xs:
            e = x == (0 if side == 'g' else 31)
            lit = x == (1 if side == 'g' else 27)
            dark = x == (4 if side == 'g' else 31)
            if style == 'a':
                c = P['b_lt'] if lit else P['b_dk'] if dark else P['b_md']
            elif style == 'b':
                blk = (y // 8) % 2
                c = P['k_hi'] if lit else P['k_dk'] if (dark or y % 8 == 7) else P['k_lt'] if (blk == 0 or x not in (xs.start, xs.start + 1)) else P['k_md']
            else:
                c = P['b_lt'] if lit else P['b_dk'] if dark else P['b_md']
            cv.p[y][x] = c
    vline(cv, 0 if side == 'g' else 31, 0, 31, O)


def finish_fac(cv, style, side=None):
    wall_finish(cv, style)
    if side:
        corner(cv, style, side)
    return cv.p


def timber_brace(cv):
    for x in range(14, 18):
        for y in range(4, 24):
            cv.p[y][x] = P['b_lt'] if x == 14 else P['b_dk'] if x == 17 else P['b_md']
    for i in range(0, 12):
        for t in range(2):
            cv.set(14 - i + 0, 22 - i - t, P['b_md'] if t else P['b_lt'])
            cv.set(17 + i, 22 - i - t, P['b_md'] if t else P['b_dk'])


def window_px(cv, style, shutters=False):
    if shutters:
        cols = {'a': (P['ra_hi'], P['ra_md'], P['ra_dk']), 'b': (P['pk_hi'], P['pk_lt'], P['pk_dk']),
                'c': (P['g_lt'], P['g_md'], P['g_dk'])}[style]
        for x0 in (5, 16):
            box(cv, x0, 6, x0 + 10, 23, cols[0], cols[1], cols[2])
            for y in range(9, 22, 3):
                hline(cv, x0 + 1, x0 + 9, y, cols[2])
            for y in (8, 20):
                cv.p[y][x0 + 5] = P['O']
        vline(cv, 15, 6, 23, P['b_dk'])
        for x in (4, 27):
            vline(cv, x, 6, 23, P['O'])
        hline(cv, 4, 27, 5, O)
        hline(cv, 4, 27, 24, P['b_dk'])
        for y in (9, 20):
            cv.set(5, y, P['m_hi'])
            cv.set(25, y, P['m_hi'])
        return
    fr = (P['b_lt'], P['b_md'], P['b_dk']) if style != 'b' else (P['k_hi'], P['k_lt'], P['k_dk'])
    box(cv, 7, 6, 24, 22, *fr)
    box(cv, 9, 8, 22, 20, P['gl_dk'], P['gl_md'], P['gl_hi'], edge=False)
    for i in range(6):
        cv.set(10 + i, 9 + i, P['gl_hi'])
        cv.set(14 + i, 9 + i, P['gl_hi']) if i < 3 else None
    for y in range(9, 20):
        cv.p[y][15] = fr[1]
        cv.p[y][16] = fr[2]
    hline(cv, 9, 22, 14, fr[1])
    for x in range(9, 23):
        cv.p[19][x] = P['gl_dk']
    box(cv, 5, 22, 26, 24, fr[0], fr[1], fr[2])
    if style == 'b':
        hline(cv, 7, 24, 5, P['k_hi'])
        hline(cv, 6, 25, 4, P['k_lt'])
        hline(cv, 6, 25, 3, P['k_dk'])
    if style == 'a':                                          # bac à fleurs sous la fenêtre
        for x in range(8, 24):
            cv.p[24][x] = P['b_dk']
            if rnd(x, 1, 33) < 0.6:
                cv.p[23][x] = [P['f_red'], P['f_white'], P['g_lt'], P['f_yel']][x % 4]


def door_px(cv, style, sign=False):
    # montants solides (x 0-5 et 26-31) et linteau
    for y in range(0, 31):
        for x in list(range(0, 6)) + list(range(26, 32)):
            if style == 'b':
                c = P['k_dk'] if (x in (5, 31) or y % 8 == 7) else P['k_hi'] if x in (1, 26) else P['k_lt'] if (y // 8 + x // 3) % 2 else P['k_md']
            else:
                c = P['b_lt'] if x in (1, 26) else P['b_dk'] if x in (5, 31) else P['b_md']
            cv.p[y][x] = c
    vline(cv, 0, 0, 31, O)
    vline(cv, 31, 0, 31, O)
    top = 11 if sign else 4
    for y in range(top, top + 4):
        for x in range(6, 26):
            cv.p[y][x] = (P['b_lt'] if style != 'b' else P['k_hi']) if y == top else (P['b_dk'] if style != 'b' else P['k_dk']) if y == top + 3 else (P['b_md'] if style != 'b' else P['k_lt'])
    for y in range(0, top):
        for x in range(6, 26):
            if not sign:
                pass
    for y in range(top + 4, 31):
        for x in range(6, 26):
            k = (x - 6) // 5
            c = P['pk_hi'] if k % 2 == 0 else P['pk_lt']
            if (x - 6) % 5 == 4:
                c = P['pk_dk']
            elif (x - 6) % 5 == 0:
                c = P['pk_hi']
            cv.p[y][x] = c
    for y in (top + 8, 26):                                    # ferrures
        hline(cv, 6, 25, y, P['m_dk'])
        hline(cv, 6, 25, y + 1, P['m_md'])
    box(cv, 18, 17, 20, 19, P['gold_hi'], P['or_'], P['b_dk'])   # poignée
    for y in range(31, 32):
        pass
    for x in range(4, 28):                                     # seuil de pierre
        cv.p[30][x] = P['k_lt']
        cv.p[31][x] = O
    for y in range(top + 4, top + 7):                          # ombre du linteau
        for x in range(6, 26):
            if (x + y) % 2 == 0:
                cv.p[y][x] = P['pk_dk']


def sign_px(cv):
    hline(cv, 22, 31, 6, P['m_dk'])
    box(cv, 21, 8, 29, 17, P['gold_hi'], P['or_'], P['b_dk'])
    ell(cv, 25, 12, 2.2, 2.2, P['b_dk'])
    ell(cv, 24.5, 11.5, 1.2, 1.2, P['gold_hi'])
    cv.p[7][23] = P['m_dk']
    cv.p[7][28] = P['m_dk']


def ivy(cv, seed):
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, seed)
            if n > 0.6 and cv.p[y][x] not in (O,) and 3 < y < 27 and 6 < x < 31:
                cv.p[y][x] = P['g_lt'] if rnd(x, y, 1) < 0.25 else P['g_md'] if n < 0.78 else P['g_dk']


def barrel_px(cv):
    ell(cv, 16, 26, 8, 3, P['b_dk'])
    for y in range(11, 27):
        for x in range(9, 24):
            bulge = 1 - abs((y - 18.5) / 8.0) ** 2 * 0.15
            if abs(x - 16) < 7.2 * bulge + 0.6:
                c = P['b_lt'] if x < 12 else P['b_dk'] if x > 19 else P['b_md']
                cv.p[y][x] = c
    for y in (13, 23):
        for x in range(9, 24):
            if cv.p[y][x] is not None:
                cv.p[y][x] = P['m_md']
    ell(cv, 16, 11, 7, 2.2, P['b_lt'])
    cv.outline()


def reg_facades():
    for st in 'abc':
        def mk(st=st):
            REG[f'fac_{st}_coin_g'] = lambda n, t: finish_fac(wall_cv(st), st, 'g')
            REG[f'fac_{st}_coin_d'] = lambda n, t: finish_fac(wall_cv(st), st, 'd')

            def plein(n, t):
                cv = wall_cv(st)
                if st == 'a':
                    timber_brace(cv)
                if st == 'c':
                    for x, y in ((9, 8), (22, 17)):
                        ell(cv, x, y, 1.6, 2.2, P['pk_dk'])
                return finish_fac(cv, st)
            REG[f'fac_{st}_plein'] = plein

            def fen(n, t):
                cv = wall_cv(st)
                window_px(cv, st)
                return finish_fac(cv, st)
            REG[f'fac_{st}_fenetre'] = fen

            def vol(n, t):
                cv = wall_cv(st)
                window_px(cv, st, True)
                return finish_fac(cv, st)
            REG[f'fac_{st}_volets'] = vol

            def porte(n, t):
                cv = wall_cv(st)
                door_px(cv, st)
                return finish_fac_door(cv, st)
            REG[f'fac_{st}_porte'] = porte

            def porte_e(n, t):
                cv = wall_cv(st)
                door_px(cv, st)
                sign_px(cv)
                return finish_fac_door(cv, st, True)
            REG[f'fac_{st}_porte_enseigne'] = porte_e

            def pb(n, t):
                cv = wall_cv(st, 1)
                if st in ('a', 'b'):
                    ivy(cv, 31 + ord(st))
                    wall_finish(cv, st)
                    return cv.p
                wall_finish(cv, st)
                barrel_px(cv)
                return cv.p
            REG[f'fac_{st}_plein_b'] = pb
        mk()


def finish_fac_door(cv, st, sign=False):
    # ombre sous l'avant-toit sur les montants et la partie haute
    for x in range(T):
        if not (6 <= x < 26) or not sign:
            cv.p[0][x] = WALL_SH[st] if (x < 6 or x >= 26) else cv.p[0][x]
    return cv.p


# ------------------------------------------------------------------ forge
def soot(c, k=0.55):
    return tuple(int(v * k) for v in c[:3]) + (c[3],)


def soot_wall(var=0):
    cv = Cv()
    stone_blocks(cv, 0, 0, 31, 31, 70 + var, (P['s_lt'], P['s_md'], P['s_dk'], P['O']))
    for y in range(T):
        for x in range(T):
            if cv.p[y][x] == P['s_dk'] and rnd(x, y, 4) < 0.3:
                cv.p[y][x] = P['s_md']
    return cv


@reg('forge_facade_suie')
def forge_suie(name, tile):
    cv = soot_wall(0)
    for x in range(T):
        cv.p[0][x] = O
        cv.p[1][x] = O if x % 2 == 0 else P['s_dk']
        cv.p[31][x] = O
    for y in range(27, 31):
        for x in range(T):
            cv.p[y][x] = P['s_dk'] if y == 30 or x % 16 == 15 else P['s_md']
    return cv.p


@reg('forge_facade_foyer')
def forge_foyer(name, tile):
    cv = soot_wall(1)
    for y in range(5, 29):
        for x in range(4, 28):
            e = ((x - 15.5) / 11.5) ** 2 + ((y - 20) / 15.0) ** 2
            if e <= 1 and not (y < 13 and abs(x - 15.5) > (y - 4) * 1.6 + 1):
                dist = ((x - 15.5) / 10.0) ** 2 + ((y - 24) / 11.0) ** 2
                c = P['s_dk']
                if dist < 1.0:
                    c = P['fi_d']
                if dist < 0.65:
                    c = P['fi_r']
                if dist < 0.4 + 0.15 * rnd(x, y, 3):
                    c = P['fi_o']
                if dist < 0.16:
                    c = P['fi_y']
                cv.p[y][x] = c
    for y in range(4, 29):                                    # pierre autour de l'ouverture
        for x in range(2, 30):
            e = ((x - 15.5) / 11.5) ** 2 + ((y - 20) / 15.0) ** 2
            if 1 < e <= 1.25 and not (y > 27):
                cv.p[y][x] = P['k_md'] if (x + y) % 3 else P['k_lt']
    for x in range(5, 27):
        cv.p[29][x] = P['s_dk']
        cv.p[28][x] = P['fi_d'] if x % 3 else P['fi_r']
    for x in range(T):
        cv.p[0][x] = O
        cv.p[31][x] = O
    return cv.p


@reg('forge_porte')
def forge_porte(name, tile):
    cv = soot_wall(2)
    door_px(cv, 'b')
    for y in range(0, 31):
        for x in list(range(0, 6)) + list(range(26, 32)):
            cv.p[y][x] = soot(cv.p[y][x], 0.7)
    cv.p[0] = [O] * T
    # fer à cheval sur la porte
    for ang in range(0, 181, 12):
        import math
        a = math.radians(ang)
        cv.set(int(16 + 4.5 * math.cos(a)), int(14 + 4.5 * math.sin(a)) - 2, P['m_hi'])
    for y in range(13, 18):
        cv.set(11, y - 1, P['m_hi'])
        cv.set(21, y - 1, P['m_hi'])
    for x in range(T):
        cv.p[31][x] = O
    return cv.p


@reg('forge_toit_cheminee')
def forge_toit(name, tile):
    cv = roof_cv('b')
    roof_shadow(cv, 24, 8, 30, 26, 'b')
    box(cv, 8, 9, 23, 25, P['s_lt'], P['s_md'], P['s_dk'])
    for y in range(10, 24):
        for x in range(9, 23):
            if (y - 10) % 4 == 3 or (x - 9 + ((y - 10) // 4) * 4) % 8 == 7:
                cv.p[y][x] = P['s_dk']
    box(cv, 5, 2, 26, 9, P['k_lt'], P['k_md'], P['s_dk'])
    box(cv, 8, 4, 23, 8, P['s_dk'], P['s_dk'], P['s_dk'], edge=False)
    for x in range(9, 23):
        if rnd(x, 1, 8) < 0.6:
            cv.p[7][x] = P['fi_r'] if rnd(x, 2, 8) < 0.7 else P['fi_o']
    cv.outline()
    return cv.p


@reg('enclume')
def enclume(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 12, 3, P['g_dk'])
    box(cv, 10, 24, 22, 29, P['m_lt'], P['m_md'], P['m_dk'])           # pied
    box(cv, 12, 18, 20, 24, P['m_lt'], P['m_md'], P['m_dk'])           # taille
    for y in range(11, 19):                                            # table
        for x in range(4, 28):
            c = P['m_hi'] if y < 13 else P['m_lt'] if y < 15 else P['m_md'] if y < 17 else P['m_dk']
            if x > 24:
                c = P['m_dk'] if y > 12 else P['m_md']
            cv.p[y][x] = c
    for i in range(7):                                                 # corne
        for y in range(12 + i // 2, 17 - i // 2):
            cv.set(3 - i // 3, y, P['m_lt'] if y < 14 else P['m_md'])
    for x in range(6, 22):
        cv.p[11][x] = P['white']
    cv.outline()
    return cv.p


@reg('meule')
def meule(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 12, 3, P['g_dk'])
    for x0 in (5, 23):                                                 # montants
        box(cv, x0, 12, x0 + 3, 29, P['b_lt'], P['b_md'], P['b_dk'])
    ell_shade(cv, 16, 17, 10, 10, (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 5, 0.3)
    ell(cv, 16, 17, 3, 3, P['m_md'])
    cv.set(15, 16, P['m_hi'])
    for a in range(0, 360, 45):
        import math
        cv.set(int(16 + 7 * math.cos(math.radians(a))), int(17 + 7 * math.sin(math.radians(a))), P['k_dk'])
    box(cv, 8, 27, 24, 30, P['b_lt'], P['b_md'], P['b_dk'])           # auge
    for x in range(10, 22):
        cv.p[27][x] = P['w_dk']
    cv.outline()
    return cv.p


@reg('bac_trempe')
def bac(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 13, 3, P['g_dk'])
    for y in range(9, 29):
        for x in range(4, 28):
            if y < 16:
                continue
            k = (x - 4) // 5
            cv.p[y][x] = P['b_dk'] if (x - 4) % 5 == 4 else P['b_md'] if k % 2 else P['b_lt']
    ell_shade(cv, 16, 14, 12, 6, (P['b_lt'], P['b_lt'], P['b_md'], P['b_dk']), 1, 0)
    ell(cv, 16, 14, 10, 4.3, P['s_dk'])
    ell(cv, 16, 14.5, 8.5, 3, P['d_dk'])
    for x in (11, 12, 13):
        cv.p[13][x] = P['w_lt']
    for y in (19, 25):
        for x in range(4, 28):
            if cv.p[y][x] is not None:
                cv.p[y][x] = P['m_md']
    cv.outline()
    return cv.p


@reg('tas_charbon')
def charbon(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 27, 13, 3, P['g_dk'])
    mass(cv, [(10, 21, 8, 6), (22, 21, 8, 6), (16, 16, 9, 7), (16, 22, 12, 5)],
         (P['s_lt'], P['s_md'], P['s_dk'], P['O']), 12, 0.6)
    for x, y in ((12, 14), (19, 16), (9, 21), (23, 22), (16, 19)):
        cv.set(x, y, P['m_lt'])
    cv.set(15, 12, P['fi_r'])
    cv.outline()
    return cv.p


@reg('rateliers_armes')
def rateliers(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 29, 12, 2, P['g_dk'])
    for x0 in (4, 25):
        box(cv, x0, 3, x0 + 2, 29, P['b_lt'], P['b_md'], P['b_dk'])
    for y in (7, 21):
        box(cv, 4, y, 27, y + 2, P['b_lt'], P['b_md'], P['b_dk'])
    for x in (10, 16, 22):                                             # épées
        for y in range(9, 21):
            cv.set(x, y, P['m_hi'] if y % 2 else P['m_lt'])
            cv.set(x + 1, y, P['m_md'])
        for xx in range(x - 2, x + 4):
            cv.set(xx, 9, P['or_'])
        cv.set(x, 8, P['b_dk'])
        cv.set(x, 21, P['m_dk'])
    box(cv, 8, 24, 13, 27, P['m_hi'], P['m_lt'], P['m_dk'])           # marteau posé
    vline(cv, 17, 23, 28, P['b_md'])
    vline(cv, 18, 23, 28, P['b_dk'])
    cv.outline()
    return cv.p


@reg('forge_enseigne')
def forge_enseigne(name, tile):
    cv = Cv()
    hline(cv, 0, 31, 3, P['m_dk'])
    hline(cv, 0, 31, 4, P['m_md'])
    for x in (9, 22):
        vline(cv, x, 5, 8, P['m_lt'])
    box(cv, 5, 9, 26, 24, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 7, 11, 24, 22, P['s_lt'], P['s_md'], P['s_dk'], edge=False)
    # enclume et marteau en or
    for x in range(10, 22):
        cv.p[17][x] = P['gold_hi']
        cv.p[18][x] = P['or_']
    box(cv, 13, 19, 18, 21, P['or_'], P['or_'], P['b_dk'])
    for x in range(7, 11):
        cv.p[16][x] = P['or_']
    for y in range(13, 17):
        cv.set(20, y, P['or_'])
        cv.set(21, y, P['gold_hi'])
    box(cv, 18, 12, 23, 14, P['gold_hi'], P['or_'], P['b_dk'])
    cv.outline()
    return cv.p


def auvent(pos):
    cv = Cv()
    for y in range(0, 16):
        for x in range(T):
            c = P['b_lt'] if y % 5 == 0 else P['b_md'] if x % 11 else P['b_dk']
            cv.p[y][x] = c
    box(cv, 0, 16, 31, 21, P['b_lt'], P['b_md'], P['b_dk'])
    for x in range(T):
        for y in range(22, 27):
            if (x + y) % 2 == 0 and y < 22 + (5 if x % 4 else 3):
                cv.p[y][x] = (0x1b, 0x14, 0x20, 110)
    if pos == 'g':
        for y in range(0, 28):
            for x in range(0, 3):
                cv.p[y][x] = None
        vline(cv, 3, 0, 22, O)
    if pos == 'd':
        for y in range(0, 28):
            for x in range(29, 32):
                cv.p[y][x] = None
        vline(cv, 28, 0, 22, O)
    for x in range(T):
        if cv.p[0][x] is not None:
            cv.p[0][x] = O
    return cv.p


REG['forge_auvent_g'] = lambda n, t: auvent('g')
REG['forge_auvent_m'] = lambda n, t: auvent('m')
REG['forge_auvent_d'] = lambda n, t: auvent('d')


def smoke(seed):
    cv = Cv()
    r = random.Random(seed)
    puffs = [(16 + r.uniform(-5, 5), 28 - i * 7, 5 + i * 1.2, 4 + i * 0.8) for i in range(4)]
    for (cx, cy, rx, ry) in puffs:
        for y in range(T):
            for x in range(T):
                d = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                if d <= 1:
                    v = -(x - cx) / rx * 0.4 - (y - cy) / ry * 0.4 + (rnd(x, y, seed) - 0.5) * 0.4
                    cv.p[y][x] = (0xd8, 0xd4, 0xe0, 150) if v > 0.2 else (0xa8, 0xa4, 0xb4, 135) if v > -0.25 else (0x6c, 0x68, 0x7c, 120)
    return cv.p


REG['fumee_a'] = lambda n, t: smoke(3)
REG['fumee_b'] = lambda n, t: smoke(9)


@reg('billot_forge')
def billot_forge(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 28, 12, 3, P['g_dk'])
    for y in range(15, 28):
        for x in range(7, 25):
            cv.p[y][x] = P['b_lt'] if x < 11 else P['b_dk'] if x > 21 else P['b_md']
    ell(cv, 16, 15, 9, 4.5, P['b_lt'])
    ell(cv, 16, 15, 5, 2.3, P['b_md'])
    ell(cv, 16, 15, 2, 1, P['b_lt'])
    for x0, y0 in ((9, 10), (15, 8)):                                   # deux marteaux
        for y in range(y0, y0 + 9):
            cv.set(x0 + (y - y0) // 3, y, P['b_md'])
        box(cv, x0 - 2, y0 - 2, x0 + 3, y0 + 1, P['m_hi'], P['m_lt'], P['m_dk'])
    cv.outline()
    return cv.p


reg_roofs()
reg_facades()
