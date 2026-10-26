"""Intérieurs, dessin final, partie 2 : herboristerie, boutique, archives, mobilier, tapis."""
import math
import random

from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, F, mass, ell_shade
from village_art1 import stone_blocks, rgba_
from interieurs_art1 import REG, reg, fshadow, fix_shadow, reuse, face_cv, face_finish

REG['tonneau_int'] = reuse('tonneau')
REG['sacs_int'] = reuse('sacs')
REG['caisse_int'] = reuse('caisse')
REG['jarre_int'] = reuse('jarre')
REG['caisses_march'] = reuse('caisses_empilees')


# ------------------------------------------------------------------ étagères (FULL)
POTS = [P['f_vio'], P['g_lt'], P['f_red'], P['gl_md'], P['f_yel'], P['pink']]


def shelf_frame(pos):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = P['wd_dk']
    for x in range(T):
        cv.p[0][x] = P['b_md']
    if pos == 'g':
        box(cv, 0, 0, 2, 31, P['b_lt'], P['b_md'], P['b_dk'])
    if pos == 'd':
        box(cv, 29, 0, 31, 31, P['b_lt'], P['b_md'], P['b_dk'])
    return cv


def plank_shelf(cv, y):
    box(cv, 0, y, 31, y + 2, P['pk_hi'], P['pk_lt'], P['pk_dk'])


def jar(cv, x, y, col, h=8):
    box(cv, x, y - h, x + 5, y - 1, P['white'], col, P['b_dk'])
    box(cv, x + 1, y - h - 1, x + 4, y - h, P['b_lt'], P['b_md'], P['b_dk'])
    cv.set(x + 1, y - h + 2, P['white'])


def shelf(kind, pos, seed):
    cv = shelf_frame(pos)
    r = random.Random(seed)
    if kind == 'pots_haut':
        for y in (11, 22):
            plank_shelf(cv, y + 1)
        for row, y in ((0, 11), (1, 22)):
            for x in range(4, 28, 7):
                jar(cv, x + r.randrange(0, 2), y, r.choice(POTS), 8 if row == 0 else 7)
    elif kind == 'pots_bas':
        plank_shelf(cv, 11)
        for x in range(4, 28, 8):                                    # paniers d'herbes
            for yy in range(3, 11):
                for xx in range(x, x + 6):
                    cv.p[yy][xx] = P['g_md'] if (xx + yy) % 3 else P['g_lt']
            box(cv, x - 1, 8, x + 6, 11, P['pk_hi'], P['pk_lt'], P['pk_dk'])
        for x in (5, 17):                                            # tiroirs étiquetés
            box(cv, x, 15, x + 9, 27, P['b_lt'], P['pk_lt'], P['b_dk'])
            hline(cv, x + 3, x + 6, 20, P['m_lt'])
            cv.set(x + 4, 18, P['parchemin'] if 'parchemin' in P else P['pl_hi'])
        plank_shelf(cv, 29)
    elif kind == 'march_haut':
        for y in (11, 22):
            plank_shelf(cv, y + 1)
        for x in range(4, 28, 6):
            col = r.choice([P['f_red'], P['f_yel'], P['gl_md'], P['g_lt'], P['orange2']])
            box(cv, x, 3, x + 4, 10, P['white'], col, P['b_dk'])
        for x in range(4, 28, 8):
            box(cv, x, 14, x + 6, 21, P['pk_hi'], P['pk_lt'], P['b_dk'])
            hline(cv, x + 1, x + 5, 17, P['b_dk'])
    elif kind == 'march_bas':
        plank_shelf(cv, 10)
        for x in range(3, 29, 9):                                    # sacs, fioles et caisses
            ell_shade(cv, x + 4, 6, 4.5, 4.5, (P['pl_hi'], P['pl_lt'], P['pl_md'], P['pl_dk']), x, 0.1)
        for x in range(4, 28, 8):
            box(cv, x, 14, x + 6, 28, P['pk_hi'], P['pk_lt'], P['b_dk'])
            hline(cv, x + 1, x + 5, 20, P['b_dk'])
        plank_shelf(cv, 29)
    elif kind == 'biblio_haut':
        for y in (11, 22):
            plank_shelf(cv, y + 1)
        for row, y in ((0, 11), (1, 22)):
            x = 3
            while x < 29:
                w = r.choice((2, 3, 3, 4))
                h = r.choice((7, 8, 9))
                col = r.choice([P['ra_lt'], P['gl_dk'], P['g_md'], P['f_vio'], P['or_'], P['b_lt'], P['pink']])
                box(cv, x, y - h, x + w - 1, y - 1, tint(col, 1.25), col, tint(col, 0.6))
                if r.random() < 0.5:
                    hline(cv, x, x + w - 1, y - h + 2, P['gold_hi'])
                x += w
    else:                                                            # biblio_bas : livres + portes
        plank_shelf(cv, 10)
        x = 3
        while x < 29:
            w = r.choice((2, 3, 4))
            h = r.choice((5, 6, 7))
            col = r.choice([P['ra_lt'], P['gl_dk'], P['g_md'], P['f_vio'], P['or_']])
            box(cv, x, 9 - h, x + w - 1, 9, tint(col, 1.25), col, tint(col, 0.6))
            x += w
        for x in (4, 17):
            box(cv, x, 14, x + 10, 28, P['pk_hi'], P['pk_lt'], P['b_dk'])
            box(cv, x + 3, 17, x + 7, 24, P['pk_md'], P['pk_md'], P['b_dk'], edge=False)
            cv.set(x + 8, 20, P['gold_hi'])
        plank_shelf(cv, 29)
    for x in range(T):
        cv.p[31][x] = P['O']
    return cv.p


for _k, _names in (('pots_haut', 'etagere_pots_haut'), ('pots_bas', 'etagere_pots_bas'), ('march_haut', 'etagere_march_haut'),
                   ('march_bas', 'etagere_march_bas'), ('biblio_haut', 'biblio_haut'), ('biblio_bas', 'biblio_bas')):
    for _i, _p in enumerate('gmd'):
        REG[f'{_names}_{_p}'] = (lambda n, t, k=_k, p=_p, i=_i: shelf(k, p, 10 + i * 3 + len(k)))


@reg('biblio_rouleaux')
def biblio_rouleaux(name, tile):
    cv = shelf_frame('m')
    box(cv, 0, 0, 31, 31, P['b_lt'], P['wd_dk'], P['O'])
    for r_ in range(3):
        for c in range(3):
            x, y = 4 + c * 9, 3 + r_ * 9
            ell(cv, x + 3.5, y + 3.5, 4, 4, P['O'])
            ell(cv, x + 3.5, y + 3.5, 3.3, 3.3, P['pl_lt'])
            ell(cv, x + 3.5, y + 3.5, 1.5, 1.5, P['pl_dk'])
    return cv.p


@reg('echelle')
def echelle(name, tile):
    cv = shelf_frame('m')
    for x in range(T):
        for y in range(T):
            cv.p[y][x] = P['wd_dk']
    for x in (7, 22):
        box(cv, x, 0, x + 3, 31, P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(4, 31, 6):
        box(cv, 10, y, 21, y + 2, P['pk_hi'], P['pk_lt'], P['b_dk'])
    return cv.p


# ------------------------------------------------------------------ herboristerie
@reg('plantes_suspendues_a', 'plantes_suspendues_b')
def plantes_suspendues(name, tile):
    cv = Cv()
    hline(cv, 1, 30, 3, P['rc_md'])
    for k, x in enumerate((6, 14, 22) if name.endswith('a') else (8, 18, 27)):
        vline(cv, x, 4, 9, P['rc_lt'])
        for y in range(10, 26):
            wd = 4 - abs(y - 12) * 0.2 if y < 14 else 5 - (y - 14) * 0.38
            for xx in range(int(x - wd), int(x + wd) + 1):
                cv.set(xx, y, [P['g_lt'], P['g_md'], P['f_vio']][(k + y // 4 + xx) % 3] if (xx + y) % 5 else P['g_dk'])
        cv.set(x, 24 + k % 2, P['g_dk'])
    cv.outline()
    return cv.p


def table_top(pos, items):
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
    items(cv)
    if pos == 'g':
        for y in range(8, 29):
            cv.p[y][x0] = O
    if pos == 'd':
        for y in range(8, 29):
            cv.p[y][x1] = O
    cv.outline()
    return cv.p


def herbs_items(pos):
    def f(cv):
        r = random.Random(4 if pos == 'g' else 9)
        for _ in range(6):
            x, y = r.randrange(5, 27), r.randrange(8, 14)
            cv.set(x, y, P['g_lt'])
            cv.set(x + 1, y, P['g_md'])
            cv.set(x, y + 1, P['g_dk'])
        if pos == 'g':
            ell(cv, 22, 11, 3.2, 2, P['k_lt'])
            ell(cv, 22, 11, 2, 1.1, P['g_md'])
        else:
            box(cv, 6, 6, 11, 11, P['white'], P['gl_md'], P['b_dk'])
            box(cv, 7, 4, 10, 6, P['b_lt'], P['b_md'], P['b_dk'])
    return f


REG['table_herbes_g'] = lambda n, t: table_top('g', herbs_items('g'))
REG['table_herbes_d'] = lambda n, t: table_top('d', herbs_items('d'))


@reg('mortier')
def mortier(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 10, 3)
    box(cv, 11, 20, 20, 29, P['b_lt'], P['b_md'], P['b_dk'])
    ell_shade(cv, 16, 17, 9, 6, (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 3, 0.1)
    ell(cv, 16, 13, 7.5, 3, P['k_lt'])
    ell(cv, 16, 13.5, 6, 2.2, P['g_md'])
    for t in range(12):                                              # pilon
        cv.set(18 + t // 2, 12 - t, P['b_md'] if t > 3 else P['k_hi'])
        cv.set(19 + t // 2, 12 - t, P['b_dk'] if t > 3 else P['k_md'])
    cv.outline()
    return cv.p


@reg('chaudron')
def chaudron(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 12, 3)
    for x in (9, 16, 22):
        for y in range(25, 29):
            cv.set(x, y, P['b_dk'])
    for x in range(9, 24):                                           # petit feu dessous
        cv.set(x, 27, P['fi_r'] if x % 3 else P['fi_o'])
        cv.set(x, 26, P['fi_o'] if x % 2 else P['fi_y'])
    ell_shade(cv, 16, 17, 11, 9, (P['m_hi'], P['m_lt'], P['m_md'], P['m_dk']), 6, 0.1)
    ell(cv, 16, 11, 10, 3.5, P['m_dk'])
    ell(cv, 16, 11.5, 8.6, 2.6, rgba_('#3a8a5a'))
    for (x, y) in ((13, 11), (18, 12), (16, 10)):
        cv.set(x, y, rgba_('#a8e8a0'))
        cv.set(x + 1, y, rgba_('#5cc06a'))
    cv.set(15, 6, (0xc8, 0xe8, 0xc8, 255))
    cv.set(17, 4, (0xc8, 0xe8, 0xc8, 255))
    cv.outline()
    return cv.p


def potted(kind):
    cv = Cv()
    fshadow(cv, 16, 29, 9, 2)
    cl = (rgba_('#d88a5a'), rgba_('#b86a4a'), rgba_('#8e4a36'))
    for y in range(20, 29):
        for x in range(10, 23):
            if abs(x - 16) < 6.5 - (y - 20) * 0.3:
                cv.p[y][x] = cl[0] if x < 13 else cl[2] if x > 19 else cl[1]
    box(cv, 9, 18, 23, 21, cl[0], cl[1], cl[2])
    if kind == 'a':
        mass(cv, [(16, 9, 9, 8), (10, 13, 6, 5), (22, 13, 6, 5)], (P['g_hi'], P['g_lt'], P['g_md'], P['g_dk']), 3, 0.5)
    elif kind == 'b':
        for k in range(7):                                           # fougère
            a = math.radians(-160 + k * 22)
            for t in range(13):
                x, y = int(16 + t * math.cos(a)), int(18 + t * math.sin(a) * 1.0 + t * t * 0.03)
                cv.set(x, y, P['g_lt'] if t % 3 else P['g_hi'])
                cv.set(x, y + 1, P['g_dk'])
    else:
        mass(cv, [(16, 11, 8, 6), (11, 14, 5, 4), (21, 14, 5, 4)], (P['g_hi'], P['g_lt'], P['g_md'], P['g_dk']), 4, 0.5)
        for (x, y, c) in ((12, 8, P['pink']), (19, 9, P['f_red']), (16, 6, P['f_yel']), (21, 13, P['pink']), (11, 13, P['f_white'])):
            cv.set(x, y, c)
            cv.set(x + 1, y, c)
            cv.set(x, y - 1, c)
    cv.outline()
    return cv.p


REG['plante_pot_a'] = lambda n, t: potted('a')
REG['plante_pot_b'] = lambda n, t: potted('b')
REG['plante_pot_c'] = lambda n, t: potted('c')
REG['plante_int'] = lambda n, t: potted('a')


@reg('herbes_seches')
def herbes_seches(name, tile):
    cv = Cv()
    r = random.Random(6)
    for k in range(4):
        x, y = 5 + k * 6, 6 + (k % 2) * 8
        for t in range(14):
            cv.set(x + t // 3, y + t, rgba_('#a8a050') if t % 2 else rgba_('#7e7a38'))
            cv.set(x + 1 + t // 3, y + t, rgba_('#c8c070'))
        cv.set(x + 2, y + 6, P['pk_md'])
        cv.set(x + 3, y + 6, P['pk_md'])
    return cv.p


# ------------------------------------------------------------------ boutique
def counter(pos, corner=False):
    return table_top(pos if pos in 'gd' else 'm', lambda cv: None) if not corner else None


for _p in 'gmd':
    REG[f'comptoir_{_p}'] = (lambda n, t, p=_p: table_top(p, lambda cv: None))


def counter_items(kind):
    def f(cv):
        if kind == 'sac':
            ell_shade(cv, 16, 9, 6, 6, (P['gold_hi'], P['or_'], P['b_md'], P['b_dk']), 3, 0.1)
            for (x, y) in ((8, 11), (22, 11), (12, 12)):
                ell(cv, x, y, 2.2, 1.6, P['gold_hi'])
        else:                                                        # balance
            vline(cv, 16, 3, 10, P['m_md'])
            hline(cv, 8, 24, 3, P['m_lt'])
            for x in (8, 24):
                vline(cv, x, 4, 7, P['m_md'])
                ell(cv, x, 8, 4, 1.6, P['gold_hi'])
            box(cv, 13, 10, 19, 11, P['m_lt'], P['m_md'], P['m_dk'])
    return f


REG['comptoir_angle_g'] = lambda n, t: table_top('g', lambda cv: counter_items('sac')(cv) if False else None)
REG['comptoir_angle_d'] = lambda n, t: table_top('d', lambda cv: None)
REG['balance'] = lambda n, t: table_top('m', counter_items('bal'))
REG['sac_pieces'] = lambda n, t: table_top('m', counter_items('sac'))


@reg('comptoir_v')
def comptoir_v(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(4, 28):
            cv.p[y][x] = P['pk_hi'] if x < 7 else P['b_dk'] if x > 24 else P['pk_lt'] if (x + y // 8) % 9 else P['pk_md']
    for y in range(T):
        cv.p[y][3] = O
        cv.p[y][28] = O
    for x in range(4, 28):
        if x % 8 == 0:
            for y in range(T):
                cv.p[y][x] = P['pk_md']
    return cv.p


@reg('presentoir_fleches', 'presentoir_bombes', 'presentoir_fioles')
def presentoir(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 12, 3)
    for x in (5, 24):
        box(cv, x, 12, x + 2, 28, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 5, 22, 26, 25, P['pk_hi'], P['pk_lt'], P['b_dk'])
    box(cv, 5, 13, 26, 15, P['pk_hi'], P['pk_lt'], P['b_dk'])
    if name.endswith('fleches'):
        for x in (9, 14, 19):                                        # carquois de flèches
            box(cv, x, 8, x + 3, 14, P['pk_hi'], P['pk_md'], P['b_dk'])
            for t in range(3):
                cv.set(x + t, 6 - t % 2, P['white'] if t % 2 else P['f_red'])
                cv.set(x + t, 5, P['m_lt'])
        for x in range(8, 24, 4):
            for y in range(16, 22):
                cv.set(x, y, P['pk_md'])
            cv.set(x, 16, P['white'])
    elif name.endswith('bombes'):
        for (x, y) in ((11, 11), (19, 11), (15, 19), (22, 19), (8, 19)):
            ell_shade(cv, x, y, 3.8, 3.8, (P['m_hi'], P['m_lt'], P['m_md'], P['m_dk']), x, 0.1)
            cv.set(x + 1, y - 4, P['pk_md'])
            cv.set(x + 2, y - 5, P['fi_o'])
    else:
        for (x, y, c) in ((9, 14, P['f_yel']), (14, 14, P['f_yel']), (19, 14, P['orange2']), (11, 22, P['f_yel']), (17, 22, P['orange2']), (22, 22, P['f_yel'])):
            jar(cv, x, y, c, 7)
    cv.outline()
    return cv.p


@reg('tapis_boutique_h')
def tapis_comptoir(name, tile):
    cv = Cv()
    for y in range(9, 23):
        for x in range(T):
            c = P['ra_md'] if (y in (9, 10, 21, 22)) else P['ra_lt']
            if y in (12, 19) and x % 4 < 2:
                c = P['gold_hi']
            if y in (13, 14, 17, 18) and x % 8 == 4:
                c = P['gold_hi']
            cv.p[y][x] = c
    for x in range(T):
        cv.p[8][x] = P['ra_dk']
        cv.p[23][x] = P['ra_dk']
    return cv.p


@reg('rideau_arriere')
def rideau(name, tile):
    cv = Cv()
    box(cv, 0, 0, 31, 3, P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(4, 31):
        for x in range(1, 31):
            f = (x % 8)
            c = rgba_('#6a8ad0') if f in (1, 2) else rgba_('#5070b8') if f in (3, 4, 5) else rgba_('#38508c')
            if y > 24:
                c = tint(c, 0.85) if (x + y) % 2 else c
            cv.p[y][x] = c
    for x in range(1, 31):
        cv.p[30][x] = rgba_('#263a5e')
    for x in (8, 24):
        for y in range(4, 8):
            cv.p[y][x] = P['gold_hi']
    return cv.p


# ------------------------------------------------------------------ archives
@reg('pupitre')
def pupitre(name, tile):
    cv = Cv()
    fshadow(cv, 16, 29, 11, 3)
    box(cv, 12, 18, 19, 29, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 8, 27, 23, 29, P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(7, 19):                                           # plan incliné et livre
        for x in range(6, 26):
            cv.p[y][x] = P['pk_hi'] if y < 9 else P['pk_lt'] if y < 16 else P['b_dk']
    for y in range(8, 15):
        for x in range(8, 24):
            cv.p[y][x] = P['pl_hi'] if x < 16 else P['pl_lt']
    vline(cv, 16, 8, 14, P['pl_dk'])
    for y in (10, 12):
        hline(cv, 9, 14, y, P['p_jt'])
        hline(cv, 18, 22, y, P['p_jt'])
    box(cv, 5, 7, 6, 15, P['ra_lt'], P['ra_md'], P['ra_dk'])
    cv.outline()
    return cv.p


for _p in 'gmd':
    REG[f'table_lecture_{_p}'] = (lambda n, t, p=_p: table_top(p, (lambda cv, p=p: lecture_items(cv, p))))


def lecture_items(cv, pos):
    if pos == 'm':
        box(cv, 6, 6, 12, 11, P['pl_hi'], P['pl_lt'], P['pl_dk'])
        box(cv, 19, 5, 25, 11, P['ra_lt'], P['ra_md'], P['ra_dk'])
    elif pos == 'g':
        box(cv, 12, 6, 18, 11, P['gl_md'], P['gl_dk'], P['O'])
    else:
        box(cv, 8, 6, 14, 11, P['pl_hi'], P['pl_lt'], P['pl_dk'])
        ell(cv, 20, 8, 2.5, 3, P['f_white'])
        for t in range(8):
            cv.set(22 + t // 2, 5 - t, P['white'])


@reg('registre_ouvert')
def registre_ouvert(name, tile):
    cv = Cv()
    for y in range(11, 22):
        for x in range(5, 27):
            cv.p[y][x] = P['pl_hi'] if x < 16 else P['pl_lt']
    vline(cv, 16, 11, 21, P['pl_dk'])
    for y in (13, 15, 17, 19):
        hline(cv, 7, 14, y, P['p_jt'])
        hline(cv, 18, 24, y, P['p_jt'])
    for x in range(5, 27):
        cv.p[22][x] = P['ra_dk']
        cv.p[10][x] = P['ra_md']
    cv.outline()
    return cv.p


@reg('parchemins')
def parchemins(name, tile):
    cv = Cv()
    for (x, y, w, h, a) in ((5, 8, 10, 6, 0), (14, 15, 12, 7, 1), (6, 20, 9, 5, 0)):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                cv.set(xx + (yy - y) * a // 3, yy, P['pl_hi'] if yy < y + 2 else P['pl_lt'])
        hline(cv, x + 2, x + w - 3, y + 2, P['p_jt'])
        hline(cv, x + 2, x + w - 5, y + 4, P['p_jt'])
        for yy in range(y, y + h):
            cv.set(x - 1, yy, P['pl_dk'])
    cv.outline()
    return cv.p


@reg('globe')
def globe(name, tile):
    cv = Cv()
    fshadow(cv, 16, 29, 10, 3)
    box(cv, 10, 26, 22, 29, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 14, 21, 17, 26, P['gold_hi'], P['or_'], P['b_dk'])
    ell_shade(cv, 16, 13, 9, 9, (P['gl_hi'], P['gl_md'], P['gl_dk'], P['d_dk']), 2, 0.1)
    for (x, y) in ((13, 10), (18, 12), (15, 16)):                    # continents
        ell(cv, x, y, 2.5, 2, P['g_md'])
    for a in range(0, 360, 6):                                       # anneau d'or
        r = math.radians(a)
        cv.set(int(16 + 11 * math.cos(r)), int(13 + 4 * math.sin(r)), P['gold_hi'])
    cv.outline()
    return cv.p


@reg('candelabre')
def candelabre(name, tile):
    cv = Cv()
    fshadow(cv, 16, 29, 8, 2)
    box(cv, 12, 27, 20, 29, P['gold_hi'], P['or_'], P['b_dk'])
    box(cv, 15, 12, 16, 27, P['gold_hi'], P['or_'], P['b_dk'])
    box(cv, 7, 12, 24, 13, P['gold_hi'], P['or_'], P['b_dk'])
    for x in (7, 15, 23):
        box(cv, x, 7, x + 1, 12, P['white'], P['pl_lt'], P['pl_dk'])
        cv.set(x, 5, P['fi_y'])
        cv.set(x, 6, P['fi_o'])
        cv.set(x + 1, 6, P['fi_o'])
        cv.set(x, 4, (0xf0, 0xe0, 0x60, 120))
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ mobilier
def bed(part, blanket):
    cv = Cv()
    cols = {'r': (P['ra_hi'], P['ra_lt'], P['ra_md'], P['ra_dk']), 'b': (P['gl_hi'], rgba_('#5a7ac8'), P['gl_dk'], P['d_dk'])}[blanket]
    if part == 'haut':
        for y in range(8, 32):
            for x in range(2, 30):
                cv.p[y][x] = P['b_lt'] if y < 10 or x < 4 else P['b_dk'] if x > 27 else P['b_md']
        box(cv, 4, 12, 27, 22, P['pl_hi'], P['pl_lt'], P['pl_dk'])
        box(cv, 6, 14, 25, 20, P['white'], P['pl_hi'], P['pl_md'])
        for y in range(23, 32):
            for x in range(4, 28):
                cv.p[y][x] = cols[0] if y == 23 else cols[1] if x < 14 else cols[2]
        box(cv, 2, 8, 29, 11, P['b_lt'], P['b_md'], P['b_dk'])
    else:
        for y in range(0, 28):
            for x in range(2, 30):
                cv.p[y][x] = cols[1] if x < 16 else cols[2]
                if y % 7 == 3:
                    cv.p[y][x] = cols[0] if x < 16 else cols[1]
        for y in range(0, 28):
            cv.p[y][2] = P['b_lt']
            cv.p[y][3] = cols[0]
            cv.p[y][29] = P['b_dk']
            cv.p[y][28] = cols[3]
        box(cv, 2, 24, 29, 28, P['b_lt'], P['b_md'], P['b_dk'])
        fshadow(cv, 16, 30, 14, 2)
    cv.outline()
    return cv.p


REG['lit_a_haut'] = lambda n, t: bed('haut', 'r')
REG['lit_a_bas'] = lambda n, t: bed('bas', 'r')
REG['lit_b_haut'] = lambda n, t: bed('haut', 'b')
REG['lit_b_bas'] = lambda n, t: bed('bas', 'b')


@reg('table_ronde')
def table_ronde(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 13, 3)
    box(cv, 14, 17, 17, 28, P['b_lt'], P['b_md'], P['b_dk'])
    box(cv, 9, 26, 22, 28, P['b_lt'], P['b_md'], P['b_dk'])
    ell_shade(cv, 16, 14, 13, 8, (P['pk_hi'], P['pk_hi'], P['pk_lt'], P['pk_md']), 3, 0.15)
    ell(cv, 16, 15, 12, 6.8, P['pk_lt'])
    ell(cv, 14, 13, 8, 4, P['pk_hi'])
    for x in range(5, 12):
        cv.set(x, 20, P['pk_dk'])
    cv.outline()
    return cv.p


def chair(kind):
    cv = Cv()
    fshadow(cv, 16, 29, 9, 2)
    seat = (P['pk_hi'], P['pk_lt'], P['pk_dk'])
    if kind == 'face':
        for (x, y) in ((9, 22), (21, 22)):
            box(cv, x, y, x + 2, 29, P['b_lt'], P['b_md'], P['b_dk'])
        box(cv, 8, 9, 23, 20, P['b_lt'], P['b_md'], P['b_dk'])      # dossier vu de face
        for x in (11, 15, 19):
            vline(cv, x, 11, 18, P['b_dk'])
        box(cv, 8, 20, 23, 24, *seat)
    elif kind == 'dos':
        box(cv, 8, 12, 23, 24, P['b_lt'], P['b_md'], P['b_dk'])
        for x in (12, 16, 20):
            vline(cv, x, 14, 22, P['b_dk'])
        for (x, y) in ((9, 25), (21, 25)):
            box(cv, x, y, x + 2, 29, P['b_lt'], P['b_md'], P['b_dk'])
    else:
        gauche = kind == 'g'
        xb = 7 if gauche else 22
        box(cv, xb, 10, xb + 2, 24, P['b_lt'], P['b_md'], P['b_dk'])   # dossier de profil
        box(cv, 7, 20, 24, 24, *seat)
        for x in (8, 21):
            box(cv, x, 24, x + 2, 29, P['b_lt'], P['b_md'], P['b_dk'])
    cv.outline()
    return cv.p


for _k in ('face', 'dos', 'g', 'd'):
    REG[f'chaise_{_k}'] = (lambda n, t, k=_k: chair(k))


@reg('tabouret')
def tabouret(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 9, 2)
    for x in (10, 20):
        box(cv, x, 19, x + 2, 28, P['b_lt'], P['b_md'], P['b_dk'])
    ell_shade(cv, 16, 18, 8, 4, (P['pk_hi'], P['pk_hi'], P['pk_lt'], P['pk_md']), 1, 0.1)
    cv.outline()
    return cv.p


@reg('banc_int')
def banc_int(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 16, 2)
    for y in range(14, 20):
        for x in range(T):
            cv.p[y][x] = P['pk_hi'] if y == 14 else P['pk_lt'] if y < 18 else P['pk_dk']
    for x in (3, 26):
        box(cv, x, 20, x + 3, 29, P['b_lt'], P['b_md'], P['b_dk'])
    cv.outline()
    return cv.p


def cabinet(kind, pos=None):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = P['wd_dk']
    if kind == 'buffet':
        box(cv, 0, 4, 31, 31, P['b_lt'], P['b_md'], P['O'])
        box(cv, 0, 2, 31, 6, P['pk_hi'], P['pk_lt'], P['b_dk'])
        box(cv, 3, 9, 28, 27, P['pk_lt'], P['pk_md'], P['b_dk'])
        vline(cv, 16, 9, 27, P['b_dk'])
        box(cv, 13 if pos == 'g' else 18, 16, 14 if pos == 'g' else 19, 19, P['gold_hi'], P['or_'], P['b_dk'])
        box(cv, 18 if pos == 'g' else 13, 16, 19 if pos == 'g' else 14, 19, P['gold_hi'], P['or_'], P['b_dk'])
    elif kind == 'armoire_h':
        box(cv, 1, 0, 30, 31, P['b_lt'], P['b_md'], P['O'])
        box(cv, 4, 6, 27, 31, P['pk_lt'], P['pk_md'], P['b_dk'])
        vline(cv, 16, 6, 31, P['b_dk'])
        for y in range(8, 14):
            cv.p[y][8] = P['pk_hi']
        box(cv, 13, 18, 14, 22, P['gold_hi'], P['or_'], P['b_dk'])
        box(cv, 18, 18, 19, 22, P['gold_hi'], P['or_'], P['b_dk'])
        box(cv, 0, 0, 31, 3, P['b_lt'], P['b_md'], P['b_dk'])
    else:
        box(cv, 1, 0, 30, 31, P['b_lt'], P['b_md'], P['O'])
        box(cv, 4, 0, 27, 24, P['pk_lt'], P['pk_md'], P['b_dk'])
        vline(cv, 16, 0, 24, P['b_dk'])
        box(cv, 13, 6, 14, 10, P['gold_hi'], P['or_'], P['b_dk'])
        box(cv, 18, 6, 19, 10, P['gold_hi'], P['or_'], P['b_dk'])
        box(cv, 1, 27, 30, 31, P['b_lt'], P['b_md'], P['b_dk'])
    return cv.p


REG['buffet_g'] = lambda n, t: cabinet('buffet', 'g')
REG['buffet_d'] = lambda n, t: cabinet('buffet', 'd')
REG['armoire_haut'] = lambda n, t: cabinet('armoire_h')
REG['armoire_bas'] = lambda n, t: cabinet('armoire_b')


def fireplace():
    cv = Cv(64, 64)
    for y in range(0, 36):                                           # manteau et conduit
        for x in range(8, 56):
            c = P['k_lt'] if (x + y // 2) % 9 else P['k_md']
            if y % 8 == 7:
                c = P['k_dk']
            if x < 11:
                c = P['k_hi']
            if x > 52:
                c = P['k_dk']
            cv.p[y][x] = c
    box(cv, 4, 24, 59, 31, P['pk_hi'], P['pk_lt'], P['b_dk'])
    box(cv, 2, 22, 61, 25, P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(32, 64):                                          # foyer
        for x in range(8, 56):
            cv.p[y][x] = P['k_md'] if (x < 12 or x > 51) else P['s_dk']
    for y in range(34, 64):
        for x in range(13, 51):
            e = ((x - 31.5) / 19.0) ** 2 + ((y - 63) / 28.0) ** 2
            if e <= 1:
                d = ((x - 31.5) / 16.0) ** 2 + ((y - 63) / 22.0) ** 2
                c = P['fi_d']
                if d < 0.8:
                    c = P['fi_r']
                if d < 0.5 + 0.1 * rnd(x, y, 2):
                    c = P['fi_o']
                if d < 0.2:
                    c = P['fi_y']
                cv.p[y][x] = c
    for x in range(12, 52, 5):                                       # bûches
        box(cv, x, 59, x + 4, 62, P['b_lt'], P['b_md'], P['b_dk'])
    cv.outline()
    return cv


_FP = fireplace()
for _n, (_c, _r) in dict(cheminee_haut_g=(0, 0), cheminee_haut_d=(1, 0), cheminee_bas_g=(0, 1), cheminee_bas_d=(1, 1)).items():
    REG[_n] = (lambda n, t, c=_c, r=_r: _FP.crop(c * T, r * T))


def clock(part):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = None
    if part == 'haut':
        box(cv, 7, 3, 24, 31, P['b_lt'], P['b_md'], P['O'])
        ell(cv, 16, 4, 8, 3, P['b_lt'])
        ell(cv, 16, 15, 7.2, 7.2, P['gold_hi'])
        ell(cv, 16, 15, 6, 6, P['pl_hi'])
        for a in range(0, 360, 30):
            r = math.radians(a)
            cv.set(int(16 + 5 * math.cos(r)), int(15 + 5 * math.sin(r)), P['p_jt'])
        vline(cv, 16, 11, 15, P['O'])
        hline(cv, 16, 19, 15, P['O'])
    else:
        box(cv, 8, 0, 23, 28, P['b_lt'], P['b_md'], P['O'])
        box(cv, 11, 3, 20, 18, P['b_dk'], P['b_dk'], P['b_dk'], edge=False)
        vline(cv, 16, 4, 14, P['gold_hi'])
        ell(cv, 16, 15, 3, 3, P['gold_hi'])
        box(cv, 6, 28, 25, 31, P['b_lt'], P['b_md'], P['b_dk'])
        fshadow(cv, 16, 31, 12, 1.5)
    cv.outline()
    return cv.p


REG['horloge_haut'] = lambda n, t: clock('haut')
REG['horloge_bas'] = lambda n, t: clock('bas')


@reg('pot_int')
def pot_int(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 9, 2)
    cl = (rgba_('#d88a5a'), rgba_('#b86a4a'), rgba_('#8e4a36'))
    for y in range(12, 28):
        t = (y - 12) / 15.0
        wd = 4 + 6 * math.sin(math.pi * min(1, t * 0.9 + 0.15))
        for x in range(int(16 - wd), int(16 + wd) + 1):
            cv.set(x, y, cl[0] if x < 16 - wd * 0.3 else cl[2] if x > 16 + wd * 0.4 else cl[1])
    ell(cv, 16, 12, 5, 2, cl[2])
    ell(cv, 16, 12, 3.5, 1.2, P['s_dk'])
    cv.outline()
    return cv.p


@reg('vase')
def vase(name, tile):
    cv = Cv()
    fshadow(cv, 16, 28, 8, 2)
    cl = (P['gl_hi'], P['gl_md'], P['gl_dk'])
    for y in range(15, 28):
        t = (y - 15) / 12.0
        wd = 3 + 4 * math.sin(math.pi * min(1, t * 0.8 + 0.1))
        for x in range(int(16 - wd), int(16 + wd) + 1):
            cv.set(x, y, cl[0] if x < 16 - wd * 0.3 else cl[2] if x > 16 + wd * 0.4 else cl[1])
    for (x, y, c) in ((12, 8, P['pink']), (17, 6, P['f_yel']), (20, 10, P['f_red']), (15, 11, P['f_white'])):
        cv.set(x, y, c)
        cv.set(x + 1, y, c)
        cv.set(x, y - 1, c)
        vline(cv, x, y + 1, 15, P['g_md'])
    cv.outline()
    return cv.p


@reg('bougie_table')
def bougie_table(name, tile):
    cv = Cv()
    box(cv, 13, 14, 18, 17, P['gold_hi'], P['or_'], P['b_dk'])
    box(cv, 14, 8, 17, 14, P['white'], P['pl_lt'], P['pl_dk'])
    cv.set(15, 5, P['fi_y'])
    cv.set(15, 6, P['fi_o'])
    cv.set(16, 6, P['fi_o'])
    cv.set(15, 7, P['fi_r'])
    for (x, y) in ((11, 4), (19, 4), (15, 2), (12, 8), (19, 8)):
        cv.set(x, y, (0xf0, 0xe0, 0x60, 90))
    cv.outline()
    return cv.p


@reg('lampe_murale')
def lampe_murale(name, tile):
    cv = Cv()
    box(cv, 13, 6, 18, 9, P['m_lt'], P['m_md'], P['m_dk'])
    for y in range(9, 21):
        for x in range(10, 22):
            e = ((x - 15.5) / 6.0) ** 2 + ((y - 15) / 6.5) ** 2
            if e <= 1:
                cv.p[y][x] = P['fi_y'] if e < 0.4 else P['fi_o']
    box(cv, 12, 21, 19, 23, P['m_lt'], P['m_md'], P['m_dk'])
    cv.outline()
    for y in range(4, 28):
        for x in range(4, 28):
            if cv.p[y][x] is None and (x + y) % 3 == 0 and ((x - 15.5) ** 2 + (y - 15) ** 2) < 120:
                cv.p[y][x] = (0xf0, 0xe0, 0x60, 55)
    return cv.p


@reg('tableau')
def tableau(name, tile):
    cv = Cv()
    box(cv, 4, 6, 27, 25, P['gold_hi'], P['or_'], P['b_dk'])
    for y in range(9, 23):
        for x in range(7, 25):
            cv.p[y][x] = rgba_('#7ab0d8') if y < 15 else P['g_md']
    for x in range(7, 25):
        if (x - 7) % 6 < 3:
            cv.p[14][x] = P['ch_lt']
            cv.p[13][x] = P['ch_hi']
    ell(cv, 19, 11, 2, 2, P['f_yel'])
    cv.outline()
    return cv.p


@reg('trophee')
def trophee(name, tile):
    cv = Cv()
    box(cv, 9, 20, 22, 27, P['pk_hi'], P['pk_lt'], P['b_dk'])
    ell_shade(cv, 16, 17, 6, 6, (P['wd_hi'], P['wd_lt'], P['wd_md'], P['wd_dk']), 5, 0.2)
    ell(cv, 13, 15, 1, 1, P['O'])
    ell(cv, 19, 15, 1, 1, P['O'])
    for (cx, dx) in ((11, -1), (21, 1)):                             # bois
        for t in range(10):
            cv.set(cx + dx * (t // 2), 12 - t, P['pl_dk'])
            cv.set(cx + dx * (t // 2) + 1, 12 - t, P['pl_lt'])
        cv.set(cx + dx * 3, 8, P['pl_lt'])
        cv.set(cx + dx * 4, 7, P['pl_lt'])
    cv.set(16, 20, P['O'])
    cv.outline()
    return cv.p


@reg('chandelle_sol')
def chandelle_sol(name, tile):
    cv = Cv()
    for (cx, cy, rx, ry) in ((15, 22, 9, 4), (20, 20, 5, 3)):
        ell(cv, cx, cy, rx, ry, P['pl_lt'])
        ell(cv, cx - 1, cy - 1, rx - 2, ry - 1.5, P['pl_hi'])
    box(cv, 14, 16, 17, 22, P['white'], P['pl_hi'], P['pl_dk'])
    cv.set(15, 14, P['fi_y'])
    cv.set(15, 15, P['fi_o'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ tapis
def rug(w, h, base, border, motif):
    cv = Cv(w, h)
    for y in range(h):
        for x in range(w):
            e = min(x, y, w - 1 - x, h - 1 - y)
            if e < 2:
                c = P['ra_dk']
            elif e < 5:
                c = P['gold_hi'] if (x + y) % 6 < 2 else P['ra_md']
            elif e < 8:
                c = P['ra_dk'] if e == 5 else P['ra_md']
            else:
                c = base
                if (x + y) % 10 == 0 or (x - y) % 10 == 0:
                    c = border
            cv.p[y][x] = c
    for y in range(h):                                               # franges sur les bords gauche et droit
        if y % 3 == 0:
            cv.set(0, y, P['pl_lt'])
            cv.set(w - 1, y, P['pl_lt'])
    cx, cy = w / 2.0, h / 2.0
    for y in range(h):
        for x in range(w):
            d = abs(x - cx) / (w * 0.22) + abs(y - cy) / (h * 0.22)
            if d < 1:
                cv.p[y][x] = P['gold_hi'] if d < 0.5 else P['or_']
            elif d < 1.2:
                cv.p[y][x] = P['ra_dk']
    return cv


_RUG = rug(96, 96, P['ra_lt'], P['ra_hi'], None)
for _n, (_c, _r) in dict(tapis_hg=(0, 0), tapis_h=(1, 0), tapis_hd=(2, 0), tapis_g=(0, 1), tapis_centre=(1, 1), tapis_d=(2, 1),
                         tapis_bg=(0, 2), tapis_b=(1, 2), tapis_bd=(2, 2)).items():
    REG[_n] = (lambda n, t, c=_c, r=_r: _RUG.crop(c * T, r * T))


@reg('paillasson')
def paillasson(name, tile):
    cv = Cv()
    for y in range(8, 25):
        for x in range(3, 29):
            cv.p[y][x] = rgba_('#a8803a') if (x + y) % 3 else rgba_('#8a6a3a')
            if (x - 3) % 4 == 0:
                cv.p[y][x] = rgba_('#c8a050')
    for x in range(3, 29):
        cv.p[8][x] = rgba_('#c8a050')
        cv.p[24][x] = rgba_('#5e3a22')
    for y in range(8, 25):
        cv.p[y][3] = rgba_('#5e3a22')
        cv.p[y][28] = rgba_('#5e3a22')
    for x in range(8, 24):
        cv.p[16][x] = rgba_('#5e3a22')
    cv.outline()
    return cv.p


@reg('tapis_etroit_h', 'tapis_etroit_v')
def tapis_etroit(name, tile):
    cv = Cv()
    h = name.endswith('h')
    for a in range(0, 32):
        for b in range(8, 24):
            x, y = (a, b) if h else (b, a)
            e = min(b - 8, 23 - b)
            c = P['ra_dk'] if e == 0 else P['gold_hi'] if e == 1 else P['ra_lt'] if e > 2 else P['ra_md']
            if e > 3 and (a % 8 == 4):
                c = P['gold_hi']
            cv.p[y][x] = c
    return cv.p


@reg('peau_bete')
def peau_bete(name, tile):
    cv = Cv()
    pal = (rgba_('#c8a074'), rgba_('#a47a50'), rgba_('#7a5636'), rgba_('#5a3e28'))
    ell_shade(cv, 16, 16, 12, 8, pal, 4, 0.4)
    for (x, y, rx, ry) in ((5, 10, 4, 3), (27, 10, 4, 3), (5, 22, 4, 3), (27, 22, 4, 3), (4, 16, 4, 3)):
        ell_shade(cv, x, y, rx, ry, pal, x, 0.4)
    ell(cv, 29, 16, 3, 3, pal[1])
    for (x, y) in ((12, 14), (18, 18), (22, 13)):
        cv.set(x, y, pal[3])
        cv.set(x + 1, y, pal[3])
    cv.outline()
    return cv.p


@reg('tache_encre')
def tache(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            e = ((x - 15) / 10.0) ** 2 + ((y - 17) / 7.0) ** 2 + (vnoise(x, y, 4, 22) - 0.5) * 0.8
            if e < 1:
                cv.p[y][x] = (0x1b, 0x14, 0x20, 150 if e < 0.45 else 90)
    return cv.p


@reg('rayon_lumiere')
def rayon(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            if 6 + y * 0.2 < x < 22 + y * 0.2 and 4 < y < 30:
                a = 70 if ((x - 6 - y * 0.2) % 8) < 5 else 40
                cv.p[y][x] = (0xf8, 0xf0, 0xb0, a)
    for x in range(8, 24, 8):                                        # croisillon de la fenêtre
        for y in range(T):
            if 6 + y * 0.2 < x < 22 + y * 0.2 and y in (12, 13):
                cv.p[y][x] = (0x1b, 0x14, 0x20, 40)
    return cv.p


def table_items(pos):
    def f(cv):
        if pos == 'm':
            ell(cv, 16, 11, 4, 2.5, P['pl_hi'])
            ell(cv, 16, 11, 2.5, 1.4, P['pl_lt'])
        elif pos == 'g':
            box(cv, 12, 6, 15, 12, P['gl_hi'], P['gl_md'], P['gl_dk'])
        else:
            ell(cv, 14, 11, 4, 2.5, P['k_lt'])
            ell(cv, 14, 11, 2.7, 1.5, P['f_red'])
    return f


for _p in 'gmd':
    REG[f'table_{_p}'] = (lambda n, t, p=_p: table_top(p, table_items(p)))
