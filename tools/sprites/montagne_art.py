"""Montagne, dessin final, partie 1 : sols, terrains, falaises, escaliers, rochers, arbres, cascade, ponts.

Palette : pierre gris-bleu (falaises), sol gris-ocre, sentier ocre, herbe vert sombre bleuté, sapins vert profond.
Lumière en haut à gauche, contour sombre d'1 px, mêmes outils que foret / village.
"""
import math
import random

import village_art1 as VA
from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, wset, F, rgba, mass, shadow, terrain_tile, box, ell, hline, vline, dither, paste, mix, tint
import foret

EXTRA = dict(
    # falaise (gris-bleu)
    mt_hi='#b4bccc', mt_lt='#94a0b4', mt_md='#74809a', mt_dk='#525e78', mt_dp='#3a4260', mt_oc='#9a8e7c',
    # sol rocheux gris-ocre
    gr_hi='#b4b4ba', gr_lt='#9a9aa6', gr_md='#8c8e9c', gr_dk='#767a8e',
    # sentier ocre
    oc_hi='#dcb680', oc_lt='#c49a64', oc_md='#a8804c', oc_dk='#7a5a38',
    # herbe de montagne
    gm_hi='#80a45e', gm_lt='#66884a', gm_md='#527040', gm_dk='#3a5436', gm_dp='#2a4230',
    # sapins
    sp_hi='#4c8a62', sp_lt='#357050', sp_md='#285a42', sp_dk='#1c4236', sp_dp='#14302c',
    # neige
    sn_hi='#fcfeff', sn_lt='#e2ecf8', sn_md='#bccce2', sn_dk='#8aa0c4', sn_dp='#6680a8',
    # arbre rabougri, bois mort
    rb_hi='#9aaa50', rb_lt='#7a9040', rb_md='#5e7434', rb_dk='#434f2a',
    dw_hi='#c4b8a4', dw_lt='#a89c8c', dw_md='#7e7466', dw_dk='#544c44',
    # minerai
    ore_y='#f4d860', ore_o='#c8982c', ore_b='#7ad4f0', ore_bd='#3c88c0',
)
P.update({k: rgba(v) for k, v in EXTRA.items()})
REG = {}


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


def cv_from(t):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = t[y][x]
    return cv


def pal(prefix):
    return tuple(P[f'{prefix}_{k}'] for k in ('hi', 'lt', 'md', 'dk'))


# ------------------------------------------------------------------ textures de sol
def ground_tex(seed=1, kind='a'):
    cols = dict(a=('gr_hi', 'gr_lt', 'gr_md', 'gr_dk'), sombre=('gr_lt', 'gr_md', 'gr_dk', 'mt_dk'),
                claire=('gr_hi', 'gr_hi', 'gr_lt', 'gr_md'))
    hi, lt, md, dk = [P[c] for c in cols.get(kind, cols['a'])]
    nseed = 1 if kind in ('a', 'b', 'c', 'd', 'e', 'f') else seed
    t = [[md] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, nseed) * 0.5 + vnoise(x, y, 16, nseed + 5) * 0.5
            t[y][x] = lt if n > 0.64 else dk if n < 0.34 else md
            if rnd(x, y, nseed + 7) < 0.04:
                t[y][x] = dk if rnd(x, y, 3) < 0.5 else lt
    r = random.Random(seed * 13 + 5)
    if kind == 'b':
        for _ in range(7):
            x, y = r.randrange(1, 30), r.randrange(1, 30)
            wset(t, x, y, hi)
            wset(t, x + 1, y, lt)
            wset(t, x, y + 1, dk)
            wset(t, x + 1, y + 1, dk)
    if kind == 'c':
        for _ in range(3):
            x, y = r.randrange(2, 24), r.randrange(2, 28)
            for i in range(r.randrange(5, 9)):
                wset(t, x + i, y + (i * 2) // 3, P['mt_dk'])
                wset(t, x + i, y + (i * 2) // 3 - 1, hi)
    if kind == 'd':
        for y in range(T):
            for x in range(T):
                if vnoise(x, y, 4, 91) > 0.64:
                    t[y][x] = P['gm_md'] if rnd(x, y, 1) < 0.6 else P['gm_lt'] if rnd(x, y, 2) < 0.5 else P['gm_dk']
    if kind == 'e':
        for _ in range(8):
            x, y = r.randrange(2, 30), r.randrange(3, 30)
            wset(t, x, y, P['gm_dk'])
            wset(t, x - 1, y - 1, P['gm_lt'])
            wset(t, x + 1, y - 2, P['gm_hi'])
            wset(t, x, y - 1, P['gm_md'])
    if kind == 'f':
        for y in range(T):
            for x in range(T):
                if (y % 11 == 5 or (x + 7 * (y // 11)) % 14 == 6):
                    t[y][x] = dk
                elif (y % 11 == 4 or (x + 7 * (y // 11)) % 14 == 5):
                    t[y][x] = hi if rnd(x, y, 2) < 0.7 else lt
    return t


def recolor(t, mp):
    return [[mp.get(c, c) for c in row] for row in t]


def gravel_tex(seed, big=False):
    t = [[None] * T for _ in range(T)]
    cols = [P['gr_hi'], P['gr_lt'], P['gr_md'], P['gr_dk']]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 77 + seed) * 0.5 + rnd(x, y, 2 + seed) * 0.5
            t[y][x] = cols[0] if n > 0.78 else cols[3] if n < 0.2 else cols[1] if n > 0.55 else cols[2]
    r = random.Random(seed * 7)
    for _ in range(18 if big else 10):
        x, y = r.randrange(31), r.randrange(30)
        s = 2 if big and r.random() < 0.5 else 1
        for dx in range(s + 1):
            for dy in range(s + 1):
                wset(t, x + dx, y + dy, cols[0] if (dx, dy) == (0, 0) else cols[1] if dy == 0 else cols[3])
    return t


def schiste_tex():
    t = ground_tex(1, 'a')
    for y in range(T):
        wob = int(2 * vnoise(0, y, 4, 8))
        for x in range(T):
            yy = (y + int(2 * vnoise(x, 0, 8, 3))) % 12
            if yy < 3:
                t[y][x] = P['mt_oc'] if yy else P['oc_md']
            elif yy == 3:
                t[y][x] = P['oc_dk']
            elif yy == 7:
                t[y][x] = P['gr_lt']
    return t


def ocre_ground():
    t = ground_tex(2, 'a')
    mp = {P['gr_hi']: P['oc_hi'], P['gr_lt']: P['mt_oc'], P['gr_md']: P['oc_md'], P['gr_dk']: P['oc_dk']}
    t = recolor(t, mp)
    return t


def ore_ground():
    t = ground_tex(1, 'b')
    r = random.Random(33)
    for _ in range(8):
        x, y = r.randrange(2, 29), r.randrange(2, 29)
        wset(t, x, y, P['ore_y'])
        wset(t, x + 1, y, P['ore_o'])
        if r.random() < 0.5:
            wset(t, x, y + 1, P['ore_b'])
            wset(t, x + 1, y + 1, P['ore_bd'])
    return t


def cendre_ground():
    t = ground_tex(1, 'sombre')
    return recolor(t, {P['gr_lt']: P['gr_dk'], P['gr_md']: P['mt_dk'], P['gr_dk']: P['mt_dp'], P['mt_dk']: P['mt_dp']})


def dry_grass():
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 12) * 0.7 + vnoise(x, y, 8, 15) * 0.3
            t[y][x] = P['oc_lt'] if n > 0.62 else P['gm_dk'] if n < 0.3 else P['rb_md']
            if rnd(x, y, 4) < 0.05:
                t[y][x] = P['rb_hi']
    r = random.Random(61)
    for _ in range(14):
        x, y = r.randrange(T), r.randrange(T)
        wset(t, x, y, P['oc_md'])
        wset(t, x - 1, y - 1, P['rb_hi'])
    return t


def moss_carpet():
    t = ground_tex(4, 'a')
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 21) * 0.7 + rnd(x, y, 1) * 0.3
            t[y][x] = P['gm_hi'] if n > 0.74 else P['gm_lt'] if n > 0.5 else P['gm_md'] if n > 0.25 else P['gm_dk']
    return t


def path_ocre(seed=11, extra=None):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, seed) * 0.7 + vnoise(x, y, 8, seed + 3) * 0.3
            t[y][x] = P['oc_lt'] if n > 0.62 else P['oc_dk'] if n < 0.26 else P['oc_md']
    r = random.Random(seed)
    for _ in range(6):
        x, y = r.randrange(T), r.randrange(T)
        wset(t, x, y, P['gr_lt'])
        wset(t, x + 1, y, P['gr_md'])
        wset(t, x, y + 1, P['oc_dk'])
    for _ in range(7):
        wset(t, r.randrange(T), r.randrange(T), P['oc_hi'])
    if extra == 'orn_h':
        for yy in (9, 22):
            for x in range(T):
                t[yy][x] = P['oc_dk']
                t[yy + 1][x] = P['oc_md'] if x % 5 else P['oc_dk']
                t[yy - 1][x] = P['oc_hi'] if x % 3 == 0 else t[yy - 1][x]
    if extra == 'orn_v':
        for xx in (9, 22):
            for y in range(T):
                t[y][xx] = P['oc_dk']
                t[y][xx + 1] = P['oc_md'] if y % 5 else P['oc_dk']
                t[y][xx - 1] = P['oc_hi'] if y % 3 == 0 else t[y][xx - 1]
    if extra == 'caillou':
        for _ in range(9):
            x, y = r.randrange(1, 30), r.randrange(1, 29)
            wset(t, x, y, P['gr_hi'])
            wset(t, x + 1, y, P['gr_lt'])
            wset(t, x, y + 1, P['gr_md'])
            wset(t, x + 1, y + 1, P['mt_dk'])
    if extra == 'boue':
        for y in range(T):
            for x in range(T):
                if ((x - 15) / 10.0) ** 2 + ((y - 17) / 6.0) ** 2 < 1 + (rnd(x, y, 3) - 0.5) * 0.4:
                    t[y][x] = P['oc_dk'] if (x + y) % 5 else P['mt_dk']
                if ((x - 14) / 7.0) ** 2 + ((y - 16) / 3.5) ** 2 < 1:
                    t[y][x] = P['sn_dk'] if (x + y) % 4 else P['sn_md']
        for x in (11, 12, 13):
            t[15][x] = P['sn_lt']
    return t


def grass_m():
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 8) * 0.7 + vnoise(x, y, 8, 13) * 0.3
            t[y][x] = P['gm_lt'] if n > 0.64 else P['gm_dk'] if n < 0.3 else P['gm_md']
    r = random.Random(77)
    for _ in range(12):
        x, y = r.randrange(T), r.randrange(T)
        wset(t, x, y, P['gm_dk'])
        wset(t, x - 1, y - 1, P['gm_hi'])
        wset(t, x + 1, y - 1, P['gm_hi'])
    return t


def snow_tex(seed=3, kind='a'):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 5) * 0.7 + vnoise(x, y, 8, 9) * 0.3
            t[y][x] = P['sn_hi'] if n > 0.7 else P['sn_md'] if n < 0.32 else P['sn_lt']
    r = random.Random(seed)
    for _ in range(9):
        x, y = r.randrange(T), r.randrange(T)
        wset(t, x, y, P['sn_dk'])
        wset(t, x + 1, y, P['sn_md'])
    for _ in range(6):
        wset(t, r.randrange(T), r.randrange(T), P['white'])
    if kind == 'traces':
        for (x, y) in ((6, 6), (12, 11), (6, 17), (12, 22), (8, 27)):
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)):
                wset(t, x + dx, y + dy, P['sn_dk'] if dx == 0 else P['sn_md'])
            wset(t, x, y - 1 if False else y, P['sn_dp'])
    if kind == 'b':
        for _ in range(4):
            x, y = r.randrange(2, 26), r.randrange(2, 28)
            for i in range(5):
                wset(t, x + i, y, P['sn_md'])
                wset(t, x + i + 1, y + 1, P['sn_lt'])
    return t


def frost_rock():
    t = ground_tex(1, 'a')
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 33)
            if n > 0.55 and rnd(x, y, 8) < 0.8:
                t[y][x] = P['sn_lt'] if rnd(x, y, 9) < 0.6 else P['sn_md']
            elif rnd(x, y, 3) < 0.04:
                t[y][x] = P['sn_hi']
    return t


def terrain_for(fam, b):
    base = ground_tex(1, 'a')
    if fam == 'sentier':
        return terrain_tile(b, base, path_ocre(), P['gr_dk'], P['oc_dk'], 11)[0]
    if fam == 'herbem':
        return terrain_tile(b, base, grass_m(), P['gr_dk'], P['gm_dp'], 12)[0]
    if fam == 'neige':
        return terrain_tile(b, base, snow_tex(), P['gr_dk'], P['sn_dk'], 13, pb=0.7)[0]
    if fam == 'ruisseau':
        return terrain_tile(b, base, F.SHALLOW, P['gr_dk'], P['foam'], 21, pb=0.55)[0]
    if fam == 'ravin':
        return terrain_tile(b, base, VA.RAVIN, P['gr_dk'], P['mt_md'], 43, pb=0.9)[0]
    return terrain_tile(b, F.SHALLOW, F.DEEP, P['foam'], P['d_dk'], 31, 0.07, pb=1.0)[0]


@reg(*[f'{p}_{s}' for p in ('sentier', 'herbem', 'neige', 'ruisseau', 'ravin', 'torrent')
       for s in ['base', 'plein'] + [f'{b >> 3 & 1}{b >> 2 & 1}{b >> 1 & 1}{b & 1}' for b in range(1, 15)]])
def terrain_family(name, tile):
    fam, suf = name.split('_', 1)
    b = 0 if suf == 'base' else 15 if suf == 'plein' else int(suf, 2)
    if fam == 'torrent' and b == 0:
        return F.SHALLOW
    return terrain_for(fam, b)


@reg('roche_a', 'roche_b', 'roche_c', 'roche_d', 'roche_e', 'roche_f', 'roche_sombre', 'roche_claire')
def roche(name, tile):
    k = name.split('_')[1]
    return ground_tex(3, k if k in 'bcdef' else 'sombre' if k == 'sombre' else 'claire' if k == 'claire' else 'a')


@reg('gravier_a', 'gravier_b', 'schiste', 'roche_ocre', 'roche_minerai', 'roche_cendre', 'herbe_seche', 'tapis_mousse')
def sols2(name, tile):
    return dict(gravier_a=lambda: gravel_tex(1), gravier_b=lambda: gravel_tex(2, True), schiste=schiste_tex, roche_ocre=ocre_ground,
                roche_minerai=ore_ground, roche_cendre=cendre_ground, herbe_seche=dry_grass, tapis_mousse=moss_carpet)[name]()


@reg('sentier_b', 'sentier_c', 'sentier_cailloux', 'sentier_ornieres_h', 'sentier_ornieres_v', 'sentier_boue')
def sentier_var(name, tile):
    return dict(sentier_b=lambda: path_ocre(12), sentier_c=lambda: path_ocre(13), sentier_cailloux=lambda: path_ocre(17, 'caillou'),
                sentier_ornieres_h=lambda: path_ocre(14, 'orn_h'), sentier_ornieres_v=lambda: path_ocre(15, 'orn_v'),
                sentier_boue=lambda: path_ocre(16, 'boue'))[name]()


@reg('neige_b', 'neige_traces', 'neige_givre', 'galets', 'sable_ruisseau')
def neige_var(name, tile):
    if name == 'neige_b':
        return snow_tex(4, 'b')
    if name == 'neige_traces':
        return snow_tex(5, 'traces')
    if name == 'neige_givre':
        return frost_rock()
    if name == 'galets':
        t = ground_tex(5, 'a')
        r = random.Random(9)
        for _ in range(13):
            x, y = r.randrange(1, 29), r.randrange(1, 29)
            for dx, dy, c in ((0, 0, 'gr_hi'), (1, 0, 'gr_lt'), (2, 0, 'gr_lt'), (0, 1, 'gr_lt'), (1, 1, 'gr_md'), (2, 1, 'gr_dk'), (1, 2, 'gr_dk'), (2, 2, 'mt_dk')):
                wset(t, x + dx, y + dy, P[c])
        return t
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            t[y][x] = P['oc_hi'] if rnd(x, y, 3) < 0.08 else P['oc_lt']
    for x in range(T):
        t[(x * 3 + 5) % 29][x] = P['oc_md']
        t[(x * 5 + 17) % 31][x] = P['oc_md']
    return t


@reg('gue_pierres')
def gue(name, tile):
    t = [row[:] for row in F.SHALLOW]
    cv = cv_from(t)
    for (cx, cy, rx, ry) in ((9, 9, 6, 4), (22, 14, 6, 4), (11, 24, 6, 4)):
        for dy in (-1, 0, 1, 2):
            pass
        ell(cv, cx, cy + 1, rx, ry, P['mt_dk'])
        ell(cv, cx, cy, rx, ry, P['gr_lt'])
        ell(cv, cx - 1, cy - 1, rx - 2, ry - 1.5, P['gr_hi'])
    return cv.p


@reg('dalle_ancienne')
def dalle(name, tile):
    t = VA.paves_tex(31, 'c')
    mp = {P['p_hi']: P['gr_hi'], P['p_lt']: P['gr_lt'], P['p_md']: P['gr_md'], P['p_dk']: P['gr_dk'], P['p_jt']: P['mt_dk'], P['white']: P['gr_hi']}
    cv = cv_from(recolor(t, mp))
    for y in range(T):
        for x in range(T):
            if abs(x - 15.5) < 8 and abs(y - 15.5) < 8 and (abs(x - 15.5) > 6.5 or abs(y - 15.5) > 6.5):
                cv.p[y][x] = P['mt_dk']
    for (x, y) in ((16, 10), (16, 11), (13, 14), (19, 14), (13, 18), (16, 21), (16, 22), (19, 18)):
        cv.set(x, y, P['oc_md'])
    return cv.p


def stairs_tex(horizontal=True, light=True):
    cv = Cv()
    for y in range(T):
        step = y // 8
        yy = y % 8
        for x in range(T):
            c = P['gr_hi'] if yy == 0 else P['gr_lt'] if yy < 4 else P['gr_md'] if yy < 7 else P['mt_dk']
            if rnd(x, y, 14) < 0.05:
                c = P['gr_md']
            cv.p[y][x] = c
    for y in range(T):
        cv.p[y][0] = P['mt_dk']
        cv.p[y][31] = P['mt_dk']
    if not horizontal:
        cv.p = [[cv.p[x][y] for x in range(T)] for y in range(T)]
    return cv.p


@reg('escalier_pierre_h')
def esc_h(name, tile):
    return stairs_tex(True)


@reg('escalier_pierre_v')
def esc_v(name, tile):
    return stairs_tex(False)


@reg('rampe_terre')
def rampe(name, tile):
    t = path_ocre(19)
    for y in range(T):
        for x in range(T):
            if y % 7 == 0:
                t[y][x] = P['oc_hi'] if x % 3 else P['oc_lt']
            elif y % 7 == 6:
                t[y][x] = P['oc_dk']
    return t


# ------------------------------------------------------------------ falaises
CL = (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk'])


def cliff_face_px(x, yy, tone, seed=3):
    """Couleur d'un pixel de face (yy = ligne dans la face). tone : 'haut' clair, 'face', 'bas' sombre.
    Strates irrégulières (bandes de 8 px qui ondulent) et joints de blocs décalés ; périodique en x (raccord des tuiles voisines)."""
    hi, lt, md, dk = CL
    if tone == 'haut':
        md, lt = lt, hi
    elif tone == 'bas':
        md, lt, dk = dk, md, P['mt_dp']
    wob = int(vnoise(x, 0, 8, 5 + seed) * 3)
    band, by = divmod(yy + wob, 8)
    bw = 9 + (band * 5) % 6
    col = md
    joint = (x + band * 7) % bw
    if by == 7:
        col = dk
    elif by == 0:
        col = lt if rnd(x, band, seed) < 0.8 else md
    elif joint == 0 and by < 7:
        col = dk
    elif joint == 1 and by < 4:
        col = lt
    elif rnd(x, yy, seed + 4) < 0.07:
        col = lt if rnd(x, yy, 9) < 0.5 else dk
    if by in (3, 4) and band % 3 == 1 and rnd(x // 3, band, seed) < 0.3 and tone != 'bas':
        col = P['mt_oc']
    return col


def cliff_tile(kind, end='', tone='face'):
    """kind : crete, face, pied ; end : '', g, d."""
    cv = Cv()
    g = ground_tex(1, 'a')
    gd = ground_tex(1, 'sombre')
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    y_lip = 14 if kind == 'crete' else 0
    y_end = 31 if kind != 'pied' else 22
    ins = [[False] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            inside = y_lip <= y <= y_end
            rim = y in (y_lip, y_end)
            if end == 'g' and x < 3 + (2 if rim else 0):
                inside = False
            if end == 'd' and x > 28 - (2 if rim else 0):
                inside = False
            ins[y][x] = inside
            if not inside:
                continue
            yy = y - y_lip
            col = cliff_face_px(x, yy, tone if kind != 'crete' else 'haut')
            if kind == 'crete' and yy < 4:
                col = P['mt_hi'] if yy < 2 else P['mt_lt']
            if kind == 'crete' and yy >= 4:
                col = cliff_face_px(x, yy + 2, 'haut')
            if kind == 'pied':
                col = cliff_face_px(x, yy, 'bas')
                if y >= 17:
                    col = P['mt_dp'] if (x + y) % 3 else P['mt_dk']
                if y >= 19:
                    col = P['mt_dp']
            if end == 'g' and x < 6:
                col = P['mt_hi'] if col != P['mt_dk'] else col
            if end == 'd' and x > 25:
                col = P['mt_dk']
            cv.p[y][x] = col
    # contour sombre autour de la roche
    for y in range(T):
        for x in range(T):
            if not ins[y][x] and any(0 <= x + dx < T and 0 <= y + dy < T and ins[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                if not (kind != 'pied' and y > y_end):
                    cv.p[y][x] = P['O']
    if kind == 'crete':                        # quelques touffes et cailloux sur l'arête
        for x in range(T):
            if (end == 'g' and x < 4) or (end == 'd' and x > 27):
                continue
            if rnd(x, 1, 7) < 0.3:
                cv.p[y_lip - 2][x] = P['gm_lt']
                cv.p[y_lip - 1][x] = P['gm_dk']
            elif rnd(x, 2, 8) < 0.12:
                cv.p[y_lip - 1][x] = P['gr_hi']
    if kind == 'pied':
        for y in range(23, T):                 # sol sombre et éboulis au pied
            for x in range(T):
                cv.p[y][x] = gd[y][x]
        for x in range(T):
            if rnd(x, 2, 9) < 0.4 and not (end == 'g' and x < 4) and not (end == 'd' and x > 27):
                cv.p[23][x] = P['mt_dk']
                if rnd(x, 3, 4) < 0.5:
                    cv.p[24][x] = P['mt_md']
        for (x, y) in ((6, 20), (13, 21), (24, 19), (28, 21)):
            if not (end == 'g' and x < 7) and not (end == 'd' and x > 24):
                cv.set(x, y, P['mt_lt'])
                cv.set(x + 1, y, P['mt_md'])
                cv.set(x, y + 1, P['mt_dk'])
    return cv.p


def snowy(p, depth):
    """Pose de la neige sur le haut d'une tuile de roche."""
    out = [r[:] for r in p]
    for y in range(depth + 4):
        for x in range(T):
            lim = depth + int(3 * vnoise(x, 0, 8, 44))
            if y <= lim and out[y][x] not in (P['O'],):
                if out[y][x] in (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk'], P['mt_dp'], P['mt_oc']) or True:
                    out[y][x] = P['sn_hi'] if y < lim - 3 else P['sn_lt'] if y < lim else P['sn_md']
    return out


@reg('falaise_crete', 'falaise_crete_g', 'falaise_crete_d', 'falaise_face', 'falaise_face_g', 'falaise_face_d',
     'falaise_pied', 'falaise_pied_g', 'falaise_pied_d')
def falaise(name, tile):
    parts = name.split('_')
    return cliff_tile(parts[1], parts[2] if len(parts) > 2 else '')


@reg('fh_haut', 'fh_haut_g', 'fh_haut_d', 'fh_mil', 'fh_mil_g', 'fh_mil_d', 'fh_bas', 'fh_bas_g', 'fh_bas_d')
def falaise_haute(name, tile):
    parts = name.split('_')
    tone = dict(haut='haut', mil='face', bas='bas')[parts[1]]
    p = cliff_tile('face', parts[2] if len(parts) > 2 else '', tone)
    if parts[1] == 'haut':                      # ombre sous l'arête
        for x in range(T):
            if p[0][x] != P['O'] and p[0][x] is not None and p[0][x] in (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk']):
                p[0][x] = P['mt_dk']
                if x % 2 == 0:
                    p[1][x] = P['mt_md'] if p[1][x] != P['O'] else p[1][x]
    if parts[1] == 'bas':
        for y in range(26, T):
            for x in range(T):
                if p[y][x] in (P['mt_md'], P['mt_lt'], P['mt_dk']):
                    p[y][x] = P['mt_dp'] if (x + y) % 3 else P['mt_dk']
    return p


@reg('falaise_cote_g', 'falaise_cote_d', 'falaise_cote_pied_g', 'falaise_cote_pied_d')
def cote(name, tile):
    side = name[-1]
    pied = 'pied' in name
    cv = Cv()
    g = ground_tex(1, 'a')
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    xs = range(0, 12) if side == 'g' else range(20, 32)
    for y in range(T):
        for x in xs:
            u = x if side == 'g' else 31 - x
            col = P['mt_md']
            if u == 0:
                col = P['mt_dk']
            elif ((u - 1) // 3 + y // 5) % 3 == 0:
                col = P['mt_lt']
            if u >= 8:
                col = P['mt_dk'] if u >= 10 else P['mt_md']
            if side == 'd':
                col = P['mt_dk'] if u >= 6 else col
            if pied and y >= 22:
                col = P['mt_dp'] if (x + y) % 2 else P['mt_dk']
            if pied and y >= 24:
                col = g[y][x]
            cv.p[y][x] = col
    edge = 12 if side == 'g' else 19
    for y in range(T):
        cv.p[y][edge] = P['O']
        if rnd(y, 3, 2) < 0.3:
            cv.p[y][edge + (1 if side == 'g' else -1)] = P['gr_dk']
    return cv.p


@reg('falaise_coin_int_g', 'falaise_coin_int_d')
def coin_int(name, tile):
    side = name[-1]
    p = cliff_tile('crete', '')
    s = cote('falaise_cote_' + side, None)
    xs = range(0, 13) if side == 'g' else range(19, 32)
    for y in range(T):
        for x in xs:
            p[y][x] = s[y][x]
    return p


@reg('falaise_veine')
def falaise_veine(name, tile):
    p = cliff_tile('face', '', 'face')
    r = random.Random(4)
    for k in range(3):
        x, y = r.randrange(4, 24), r.randrange(3, 24)
        for i in range(6):
            xx, yy = x + i, y + i // 3
            p[yy][xx] = P['ore_y'] if i % 3 == 0 else P['ore_o']
            p[yy + 1][xx] = P['mt_dk']
        p[y - 1][x + 2] = P['ore_b']
        p[y - 1][x + 3] = P['ore_bd']
    return p


@reg('falaise_neige_crete')
def falaise_neige_crete(name, tile):
    p = cliff_tile('crete', '')
    for y in range(0, 20):
        for x in range(T):
            if p[y][x] != P['O']:
                lim = 12 + int(2 * vnoise(x, 0, 8, 7))
                if y < lim:
                    p[y][x] = snow_tex(3)[y][x]
                elif y < lim + 2:
                    p[y][x] = P['sn_md']
    for x in range(T):
        p[14][x] = P['sn_hi'] if x % 3 else P['sn_lt']
        p[15][x] = P['sn_md']
    return p


@reg('falaise_neige_face')
def falaise_neige_face(name, tile):
    p = cliff_tile('face', '', 'face')
    for y in range(T):
        for x in range(T):
            if p[y][x] not in (P['O'],) and vnoise(x, y, 4, 71) > 0.58 and rnd(x, y, 5) < 0.85:
                p[y][x] = P['sn_lt'] if (y + x) % 5 else P['sn_md']
            elif p[y][x] == P['mt_dk']:
                p[y][x] = P['mt_dk']
    return p


@reg('falaise_etais')
def falaise_etais(name, tile):
    cv = cv_from(cliff_tile('face', '', 'face'))
    for x0 in (3, 22):                               # deux poteaux
        box(cv, x0, 0, x0 + 5, 31, P['pk_hi'], P['pk_md'], P['pk_dk'])
        for y in range(4, 31, 9):
            cv.set(x0 + 2, y, P['m_hi'])
    box(cv, 0, 2, 31, 8, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    for x in range(2, 30, 6):
        cv.set(x, 5, P['m_lt'])
    cv.outline()
    return cv.p


@reg('falaise_fissure')
def falaise_fissure(name, tile):
    p = cliff_tile('face', '', 'face')
    cv = cv_from(p)
    pts = [(15, 0), (17, 5), (14, 10), (17, 15), (15, 20), (18, 25), (16, 31)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cv.line(x0, y0, x1, y1, P['O'])
        cv.line(x0 + 1, y0, x1 + 1, y1, P['mt_dp'])
    for (x0, y0, x1, y1) in ((17, 10, 24, 12), (14, 20, 8, 23), (17, 15, 22, 17)):
        cv.line(x0, y0, x1, y1, P['O'])
    for y in range(3, 28, 6):
        cv.set(13, y + 2, P['mt_hi'])
    return cv.p


@reg('falaise_fissure_ouvert')
def falaise_fissure_ouvert(name, tile):
    cv = cv_from(cliff_tile('face', '', 'face'))
    for y in range(8, 32):
        for x in range(7, 26):
            e = ((x - 15.5) / 9.5) ** 2 + ((y - 24) / 15.0) ** 2
            if e <= 1:
                cv.p[y][x] = P['O'] if e > 0.35 else P['v_dk']
    for (x, y) in ((6, 12), (25, 14), (7, 28), (24, 27)):
        cv.set(x, y, P['mt_hi'])
    for x in range(9, 23):
        cv.set(x, 30, P['gr_dk'])
        cv.set(x, 31, P['gr_lt'])
    return cv.p


@reg('falaise_grotte')
def falaise_grotte(name, tile):
    cv = cv_from(cliff_tile('face', '', 'face'))
    for y in range(7, 32):
        for x in range(4, 28):
            e = ((x - 15.5) / 11.5) ** 2 + ((y - 20) / 13.0) ** 2
            if e <= 1 and (y >= 20 or e <= 1):
                cv.p[y][x] = P['O'] if e > 0.5 else P['v_dk']
    for y in range(7, 32):
        for x in range(3, 29):
            e = ((x - 15.5) / 12.5) ** 2 + ((y - 20) / 14.0) ** 2
            if 0.92 < e <= 1.15 and cv.p[y][x] not in (P['O'], P['v_dk']):
                cv.p[y][x] = P['mt_dp'] if x > 15 else P['mt_lt']
    for x in range(8, 24):
        cv.set(x, 31, P['gr_dk'])
    return cv.p


@reg('falaise_grotte_haut')
def falaise_grotte_haut(name, tile):
    p = cliff_tile('face', '', 'haut')
    for x in range(T):
        if rnd(x, 1, 3) < 0.4:
            p[31][x] = P['mt_dk']
    return p


def stair_overlay(base, tone_cols, y0=0, y1=32, x0=5, x1=26):
    cv = cv_from(base)
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            step = (y - y0) % 8
            c = tone_cols[0] if step == 0 else tone_cols[1] if step < 5 else tone_cols[2]
            if x in (x0, x1):
                c = P['O']
            cv.p[y][x] = c
    return cv.p


@reg('escalier_crete', 'escalier_face', 'escalier_pied', 'escalier_fh_haut', 'escalier_fh_mil', 'escalier_fh_bas')
def escalier(name, tile):
    n = name.split('_', 1)[1]
    base = dict(crete=lambda: cliff_tile('crete', ''), face=lambda: cliff_tile('face', ''), pied=lambda: cliff_tile('pied', ''),
                fh_haut=lambda: cliff_tile('face', '', 'haut'), fh_mil=lambda: cliff_tile('face', ''), fh_bas=lambda: cliff_tile('face', '', 'bas'))[n]()
    cols = (P['gr_hi'], P['gr_lt'], P['gr_dk'])
    if n == 'crete':
        return stair_overlay(base, cols, 14, 32)
    if n == 'pied':
        return stair_overlay(base, cols, 0, 24)
    return stair_overlay(base, cols)


@reg('escalier_cote_g', 'escalier_cote_d')
def escalier_cote(name, tile):
    side = name[-1]
    s = cote('falaise_cote_' + ('d' if side == 'g' else 'g'), None)
    cv = cv_from(s)
    xs = range(0, 20) if side == 'g' else range(12, 32)
    for y in range(T):
        for x in xs:
            step = y % 8
            cv.p[y][x] = P['gr_hi'] if step == 0 else P['gr_lt'] if step < 5 else P['gr_dk']
    return cv.p


# ------------------------------------------------------------------ rochers
ROCK_MT = (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk'])


def mrock(v, snow=False, moss=False):
    cv = Cv()
    shadow(cv, 16, 27, 13, 3, P['gr_dk'])
    circles = [[(16, 19, 12, 9), (9, 22, 7, 5)], [(11, 20, 9, 7), (22, 18, 8, 9), (17, 14, 7, 6)]][v % 2]
    mass(cv, circles, ROCK_MT, 60 + v, 0.35)
    for x0, y0, x1, y1 in ((12, 17, 16, 21), (20, 15, 18, 19)):
        cv.line(x0, y0, x1, y1, P['mt_dp'])
    if moss:
        for y in range(8, 24):
            for x in range(4, 28):
                if cv.p[y][x] is not None and y < 17 and rnd(x, y, 3) < 0.65:
                    cv.p[y][x] = P['gm_md'] if rnd(x, y, 4) < 0.6 else P['gm_lt']
    if snow:
        for y in range(6, 20):
            for x in range(4, 28):
                if cv.p[y][x] is not None and y < 14 - abs(x - 14) // 4 + int(2 * rnd(x, 0, 5)):
                    cv.p[y][x] = P['sn_hi'] if y < 11 else P['sn_lt'] if (x + y) % 4 else P['sn_md']
    cv.outline()
    return cv.p


@reg('rocher_a', 'rocher_b', 'rocher_mousse', 'rocher_neige', 'rocher_eau')
def rochers(name, tile):
    if name == 'rocher_eau':
        cv = Cv()
        for dx in (-9, 9, 0):
            ell(cv, 16 + dx, 26, 5, 1.5, P['foam'])
        p = mrock(0)
        for y in range(T):
            for x in range(T):
                if p[y][x] is not None and p[y][x] != P['O']:
                    cv.p[y][x] = p[y][x]
                elif p[y][x] == P['O']:
                    cv.p[y][x] = P['O']
        cv.p[27] = [P['w_dk'] if (x % 2 == 0 and 4 < x < 28) else c for x, c in enumerate(cv.p[27])]
        return cv.p
    return dict(rocher_a=lambda: mrock(0), rocher_b=lambda: mrock(1), rocher_mousse=lambda: mrock(0, moss=True), rocher_neige=lambda: mrock(1, snow=True))[name]()


def boulders_fill(cv, seed, circles=None):
    """Remplit toute la case de blocs (rocher fissuré / éboulis)."""
    g = ground_tex(1, 'sombre')
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    circles = circles or [(9, 10, 10, 8), (23, 9, 9, 8), (16, 20, 13, 9), (6, 25, 8, 6), (27, 26, 8, 6)]
    mass(cv, circles, ROCK_MT, seed, 0.4)
    cv.outline()


@reg('rocher_fissure')
def rocher_fissure(name, tile):
    cv = Cv()
    boulders_fill(cv, 81)
    pts = [(8, 3), (11, 9), (9, 14), (13, 19), (12, 24), (15, 31)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cv.line(x0, y0, x1, y1, P['O'])
    pts = [(24, 2), (21, 9), (23, 15), (19, 21), (22, 27)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cv.line(x0, y0, x1, y1, P['O'])
    cv.line(11, 9, 19, 11, P['O'])
    cv.line(13, 19, 21, 21, P['O'])
    for y in range(3, 30, 7):
        cv.set(13, y, P['mt_hi'])
        cv.set(25, y + 3, P['mt_hi'])
    return cv.p


@reg('rocher_fissure_ouvert')
def rocher_fissure_ouvert(name, tile):
    cv = Cv()
    boulders_fill(cv, 82)
    for y in range(8, 30):
        for x in range(6, 27):
            e = ((x - 16) / 10.5) ** 2 + ((y - 22) / 11.0) ** 2
            if e <= 1:
                cv.p[y][x] = P['O'] if e > 0.4 else P['v_dk']
    for x in range(8, 25):
        cv.set(x, 30, P['gr_dk'])
        cv.set(x, 31, P['gr_lt'])
    return cv.p


@reg('cailloux_montagne')
def cailloux(name, tile):
    cv = Cv()
    for (cx, cy, rx, ry) in ((9, 20, 4, 3), (21, 14, 3, 3), (20, 24, 3, 2)):
        mass(cv, [(cx, cy, rx, ry)], ROCK_MT, cx * 3, 0.2)
    cv.outline()
    return cv.p


def pile_canvas(w, seed):
    cv = Cv(w, T)
    g = ground_tex(1, 'sombre')
    for y in range(T):
        for x in range(w):
            cv.p[y][x] = g[y][x % T]
    r = random.Random(seed)
    circles = []
    for i in range(w // 6 + 3):
        circles.append((r.uniform(2, w - 2), r.uniform(8, 28), r.uniform(5, 9), r.uniform(4, 7)))
    for cx in range(2, w, 9):
        circles.append((cx + r.uniform(-2, 2), 24 + r.uniform(-1, 3), 7, 5))
    mass(cv, circles, ROCK_MT, seed, 0.45)
    cv.outline()
    return cv


_EB = {'a': pile_canvas(T, 91), 'b': pile_canvas(T, 92), 'w': pile_canvas(64, 93)}


@reg('eboulis_a', 'eboulis_b', 'eboulis_g', 'eboulis_d')
def eboulis(name, tile):
    if name == 'eboulis_a':
        return _EB['a'].p
    if name == 'eboulis_b':
        return _EB['b'].p
    return _EB['w'].crop(0 if name.endswith('g') else T, 0)


@reg('eboulis_degage_a', 'eboulis_degage_b')
def eboulis_degage(name, tile):
    cv = cv_from(ground_tex(1, 'sombre'))
    r = random.Random(5 if name.endswith('a') else 6)
    for _ in range(11):
        x, y = r.randrange(2, 28), r.randrange(2, 28)
        cv.set(x, y, P['mt_lt'])
        cv.set(x + 1, y, P['mt_md'])
        cv.set(x, y + 1, P['mt_dk'])
        cv.set(x + 1, y + 1, P['mt_dp'])
    return cv.p


@reg('eboulis_poussiere', 'gravats')
def poussiere(name, tile):
    cv = Cv()
    r = random.Random(11 if name == 'gravats' else 12)
    for _ in range(14 if name == 'gravats' else 9):
        x, y = r.randrange(2, 29), r.randrange(3, 29)
        cv.set(x, y, P['mt_lt'])
        cv.set(x + 1, y, P['mt_md'])
        cv.set(x, y + 1, P['mt_dk'])
        if r.random() < 0.4:
            cv.set(x - 1, y + 1, P['gr_dk'])
    return cv.p


_BIG = None


def gros_rocher():
    global _BIG
    if _BIG is None:
        cv = Cv(64, 64)
        shadow(cv, 32, 56, 27, 5, P['gr_dk'])
        mass(cv, [(32, 38, 26, 20), (14, 46, 12, 10), (50, 44, 12, 10), (30, 22, 18, 13), (44, 30, 14, 12)], ROCK_MT, 71, 0.4)
        for (x0, y0, x1, y1) in ((26, 20, 32, 30), (42, 28, 38, 40), (20, 40, 28, 46), (46, 48, 52, 42)):
            cv.line(x0, y0, x1, y1, P['mt_dp'])
            cv.line(x0 - 1, y0, x1 - 1, y1, P['mt_hi'])
        cv.outline()
        _BIG = cv
    return _BIG


@reg('gros_rocher_hg', 'gros_rocher_hd', 'gros_rocher_bg', 'gros_rocher_bd')
def gros_rocher_t(name, tile):
    return gros_rocher().crop(T if name.endswith('d') else 0, T if '_b' in name else 0)


@reg('cairn')
def cairn(name, tile):
    cv = Cv()
    shadow(cv, 16, 27, 11, 3, P['gr_dk'])
    for (cx, cy, rx, ry) in ((16, 23, 10, 5), (16, 16, 7.5, 4.5), (16, 10, 5, 3.5), (16, 6, 2.5, 2.2)):
        ell(cv, cx, cy + 1, rx, ry, P['mt_dk'])
        ell(cv, cx, cy, rx, ry, P['mt_md'])
        ell(cv, cx - 1, cy - 1, rx - 2, ry - 1.5, P['mt_lt'])
        cv.set(int(cx - rx / 2), int(cy - ry / 2), P['mt_hi'])
    cv.outline()
    return cv.p


@reg('socle_corbeau')
def socle(name, tile):
    cv = Cv()
    shadow(cv, 16, 28, 12, 3, P['gr_dk'])
    box(cv, 6, 14, 25, 27, P['mt_hi'], P['mt_md'], P['mt_dk'])
    box(cv, 4, 22, 27, 28, P['mt_hi'], P['mt_lt'], P['mt_dp'])
    box(cv, 8, 8, 23, 15, P['mt_hi'], P['mt_lt'], P['mt_dk'])
    for x in (13, 18):
        for y in range(16, 22):
            cv.set(x, y, P['mt_dk'])
    cv.set(15, 10, P['ore_y'])
    cv.set(16, 10, P['ore_y'])
    cv.outline()
    return cv.p


@reg('bloc_taille')
def bloc_taille(name, tile):
    cv = Cv()
    shadow(cv, 16, 27, 12, 3, P['gr_dk'])
    box(cv, 6, 8, 25, 26, P['mt_hi'], P['mt_md'], P['mt_dk'])
    box(cv, 6, 8, 25, 14, P['mt_hi'], P['mt_hi'], P['mt_lt'])
    for (x, y) in ((11, 18), (17, 21), (21, 17)):
        cv.set(x, y, P['mt_dk'])
        cv.set(x + 1, y, P['mt_dk'])
    cv.line(9, 16, 22, 16, P['mt_dk'])
    cv.outline()
    return cv.p


@reg('colonne_brisee')
def colonne(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 9, 2.5, P['gr_dk'])
    box(cv, 10, 20, 21, 29, P['mt_hi'], P['mt_lt'], P['mt_dk'])
    for y in range(8, 21):
        c = P['mt_lt'] if (y // 3) % 2 else P['mt_md']
        cv.rect(11, y + (0 if y < 14 else 0), 20, y, c)
        cv.set(11, y, P['mt_hi'])
        cv.set(20, y, P['mt_dk'])
    for x in range(11, 21):               # cassure en dents de scie
        cv.set(x, 8 + (x % 3), P['mt_hi'])
    cv.rect(10, 9, 21, 9, None)
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ arbres
def sapin_tiers(cv, cx, top, base, width, snow=False, seed=0, pal=None):
    """Sapin vu de 3/4 : tiers de branches (ellipses empilées), éclairés à gauche."""
    hi, lt, md, dk = pal or (P['sp_hi'], P['sp_lt'], P['sp_md'], P['sp_dk'])
    n = 4 if width > 24 else 3
    h = base - top
    for i in range(n):
        yc = top + h * (i + 0.7) / n * 0.95
        w = width * (0.35 + 0.65 * (i + 1) / n) / 2
        ry = h / n * 0.8
        for y in range(cv.h):
            for x in range(cv.w):
                nx, ny = (x + 0.5 - cx) / w, (y + 0.5 - yc) / ry
                d = nx * nx + ny * ny
                if d <= 1 and (ny < 0.3 or nx * nx + (ny - 0.3) ** 2 <= 1):
                    v = -(nx + ny) * 0.5 + (rnd(x, y, seed + i) - 0.5) * 0.35 - d * 0.15
                    c = hi if v > 0.5 else lt if v > 0.12 else md if v > -0.3 else dk
                    if ny > 0.55:
                        c = dk if rnd(x, y, seed) < 0.7 else md
                    if snow and ny < -0.1 and c in (hi, lt, md):
                        c = P['sn_hi'] if nx < 0.1 else P['sn_lt']
                    elif snow and ny < 0.25 and rnd(x, y, 9) < 0.5 and c in (hi, lt):
                        c = P['sn_lt']
                    cv.p[y][x] = c


def sapin_small(v, snow=False):
    cv = Cv()
    shadow(cv, 16, 28, 9, 3, P['gr_dk'])
    cv.rect(14, 23, 17, 29, P['b_md'])
    cv.rect(14, 23, 14, 29, P['b_lt'])
    cv.rect(17, 23, 17, 29, P['b_dk'])
    sapin_tiers(cv, 16, 1, 27, 26 if v else 22, snow, 31 + v)
    cv.outline()
    return cv.p


@reg('sapin_petit_a', 'sapin_petit_b', 'sapin_neige_petit')
def sapin_petit(name, tile):
    return sapin_small(1 if name.endswith('b') else 0, snow=('neige' in name))


@reg('sapin_dense_a', 'sapin_dense_b', 'sapin_dense_neige')
def sapin_dense(name, tile):
    v = 1 if name.endswith('b') else 0
    snow = name.endswith('neige')
    cv = Cv(fill=P['sp_dp'])
    r = random.Random(210 + v)
    cs = []
    for _ in range(6):
        cx, cy, rad = r.uniform(0, 32), r.uniform(0, 32), r.uniform(6, 9)
        for ox in (-32, 0, 32):
            for oy in (-32, 0, 32):
                cs.append((cx + ox, cy + oy, rad, rad * 0.9))
    for y in range(T):
        for x in range(T):
            best = None
            for (cx, cy, rx, ry) in cs:
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d = nx * nx + ny * ny
                if d <= 1 and (best is None or d < best[0]):
                    best = (d, nx, ny)
            if best:
                d, nx, ny = best
                val = -(nx + ny) * 0.55 + (rnd(x, y, 5 + v) - 0.5) * 0.3 - d * 0.1
                cv.p[y][x] = P['sp_lt'] if val > 0.45 else P['sp_md'] if val > 0.0 else P['sp_dk']
                if snow and val > 0.3 and ny < 0.2:
                    cv.p[y][x] = P['sn_lt'] if val > 0.5 else P['sn_md']
            elif (x + y) % 3 == 0:
                cv.p[y][x] = P['sp_dk']
    return cv.p


def twisted(cv, pts, w, cols):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
            for k in range(w):
                cv.set(x + k, y, cols[0] if k == 0 else cols[2] if k == w - 1 else cols[1])


@reg('arbre_rabougri_a', 'arbre_rabougri_b')
def rabougri(name, tile):
    v = 1 if name.endswith('b') else 0
    cv = Cv()
    shadow(cv, 16, 28, 10, 3, P['gr_dk'])
    bark = (P['b_lt'], P['b_md'], P['b_dk'])
    twisted(cv, [(15, 29), (14, 24), (17, 19), (14, 14)] if not v else [(16, 29), (17, 24), (14, 19), (17, 13)], 4, bark)
    twisted(cv, [(15, 20), (9, 15), (6, 11)], 2, bark)
    twisted(cv, [(17, 17), (22, 13), (25, 10)], 2, bark)
    pal4 = (P['rb_hi'], P['rb_lt'], P['rb_md'], P['rb_dk'])
    mass(cv, [(8, 9, 5, 4), (25, 8, 5, 4), (15, 8, 7, 5)] if not v else [(7, 10, 5, 4), (24, 11, 6, 4), (16, 6, 6, 5)], pal4, 140 + v, 0.5)
    cv.outline()
    return cv.p


@reg('pin_mort')
def pin_mort(name, tile):
    cv = Cv()
    shadow(cv, 16, 28, 8, 2.5, P['gr_dk'])
    dw = (P['dw_hi'], P['dw_md'], P['dw_dk'])
    twisted(cv, [(15, 29), (15, 20), (16, 12), (15, 3)], 4, dw)
    for pts in (((15, 20), (7, 15), (4, 10)), ((17, 15), (24, 11), (28, 7)), ((15, 9), (10, 6), (8, 2)), ((17, 24), (23, 21), (26, 18))):
        twisted(cv, list(pts), 2, dw)
    cv.set(14, 24, P['dw_dk'])
    cv.set(14, 15, P['dw_dk'])
    cv.outline()
    return cv.p


@reg('souche_montagne')
def souche_m(name, tile):
    return F.stump(False)


@reg('tronc_couche')
def tronc(name, tile):
    return F.log()


GREEN_MAP = {P['g_hi']: P['gm_hi'], P['g_lt']: P['gm_lt'], P['g_md']: P['gm_md'], P['g_dk']: P['gm_dk'], P['g_dp']: P['gm_dp']}


@reg('buisson_montagne_a', 'buisson_montagne_b', 'genevrier', 'buisson_neige')
def buissons(name, tile):
    if name.startswith('buisson_montagne'):
        return recolor(F.bush(0 if name.endswith('a') else 1), GREEN_MAP)
    cv = Cv()
    shadow(cv, 16, 26, 12, 3, P['gr_dk'])
    if name == 'genevrier':
        mass(cv, [(10, 18, 8, 7), (22, 18, 8, 7), (16, 13, 10, 8), (16, 20, 12, 6)], (P['sp_hi'], P['sp_lt'], P['sp_md'], P['sp_dk']), 55, 0.5)
        r = random.Random(3)
        for _ in range(9):
            x, y = r.randrange(7, 25), r.randrange(9, 23)
            if cv.p[y][x] is not None:
                cv.set(x, y, P['ore_bd'])
                cv.set(x + 1, y, P['mt_lt'])
        for (x0, y0, x1, y1) in ((8, 12, 5, 10), (24, 12, 27, 10), (16, 6, 16, 3)):
            cv.line(x0, y0, x1, y1, P['sp_hi'])
    else:
        mass(cv, [(10, 18, 8, 7), (22, 18, 8, 7), (16, 13, 10, 8), (16, 20, 12, 6)], (P['gm_hi'], P['gm_lt'], P['gm_md'], P['gm_dk']), 56, 0.5)
        for y in range(5, 20):
            for x in range(4, 28):
                if cv.p[y][x] is not None and y < 14 - abs(x - 16) // 3 + int(2 * rnd(x, 1, 4)):
                    cv.p[y][x] = P['sn_hi'] if y < 11 else P['sn_lt']
    cv.outline()
    return cv.p


@reg('fougeres')
def fougeres(name, tile):
    cv = Cv()
    for (x0, y0) in ((9, 24), (22, 25), (15, 20)):
        for ang in range(-3, 4):
            ln = 8 - abs(ang)
            for i in range(ln):
                x = x0 + ang * i // 3
                y = y0 - i + (i * i) // 14
                cv.set(x, y, P['gm_hi'] if i > ln // 2 else P['gm_lt'])
                cv.set(x + 1, y, P['gm_dk'])
    cv.outline(P['gm_dp'])
    return cv.p


@reg('fleurs_alpines_a', 'fleurs_alpines_b', 'bruyere', 'edelweiss')
def fleurs(name, tile):
    col = dict(fleurs_alpines_a=rgba('#8090e0'), fleurs_alpines_b=P['f_yel'], bruyere=P['f_vio'], edelweiss=P['f_white'])[name]
    cv = Cv()
    r = random.Random(sum(map(ord, name)))
    for _ in range(6 if name != 'bruyere' else 9):
        x, y = r.randrange(3, 29), r.randrange(4, 28)
        cv.set(x, y + 1, P['gm_dk'])
        cv.set(x, y + 2, P['gm_dk'])
        if name == 'bruyere':
            cv.set(x, y, col)
            cv.set(x, y - 1, col)
            cv.set(x + 1, y, P['mt_dp'] if False else P['ronce_m'])
            continue
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.set(x + dx, y + dy, col)
        cv.set(x, y, P['f_yel'] if name != 'fleurs_alpines_b' else P['orange'])
    return cv.p


@reg('touffes_seches', 'herbe_haute_m')
def touffes(name, tile):
    cv = Cv()
    r = random.Random(400 if name == 'touffes_seches' else 401)
    lt, md, dk = (P['rb_hi'], P['oc_md'], P['oc_dk']) if name == 'touffes_seches' else (P['gm_lt'], P['gm_md'], P['gm_dk'])
    for _ in range(8):
        x, y = r.randrange(3, 29), r.randrange(10, 29)
        h = r.randrange(5, 10)
        for i in range(h):
            cv.set(x + (i // 4), y - i, lt if i > h // 2 else md)
            cv.set(x + 1 + (i // 4), y - i, dk)
    cv.outline(P['gm_dp'] if name == 'herbe_haute_m' else P['oc_dk'])
    return cv.p


@reg('mousse')
def mousse(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 51)
            if n > 0.62 and rnd(x, y, 1) < 0.9:
                cv.p[y][x] = P['gm_md'] if rnd(x, y, 2) < 0.5 else P['gm_lt'] if rnd(x, y, 3) < 0.6 else P['gm_dk']
    return cv.p


@reg('ossements')
def ossements(name, tile):
    cv = Cv()
    cr = (P['white'], P['dw_hi'], P['dw_lt'])
    for (x0, y0, x1, y1) in ((6, 12, 20, 9), (9, 20, 24, 24), (14, 15, 18, 25)):
        cv.line(x0, y0, x1, y1, cr[0])
        cv.line(x0, y0 + 1, x1, y1 + 1, cr[2])
        for (x, y) in ((x0, y0), (x1, y1)):
            ell(cv, x, y, 2, 1.8, cr[0])
    ell(cv, 24, 13, 3.5, 3, cr[0])
    cv.set(23, 13, P['O'])
    cv.set(25, 13, P['O'])
    cv.outline(P['dw_dk'])
    return cv.p


# ------------------------------------------------------------------ gros arbres 2x2 (64x64)
_BT = {}


def big_tree(kind):
    if kind in _BT:
        return _BT[kind]
    cv = Cv(64, 64)
    shadow(cv, 32, 58, 24, 4.5, P['gr_dk'])
    if kind == 'pin_mort':
        dw = (P['dw_hi'], P['dw_md'], P['dw_dk'])
        twisted(cv, [(32, 63), (32, 48), (33, 30), (32, 12), (31, 3)], 7, dw)
        for pts in (((32, 44), (16, 36), (6, 24)), ((34, 38), (50, 30), (58, 16)), ((32, 28), (20, 20), (12, 8)),
                    ((33, 22), (46, 14), (52, 4)), ((31, 16), (24, 10), (22, 2)), ((16, 36), (10, 38), (4, 34)), ((50, 30), (56, 32), (60, 28))):
            twisted(cv, list(pts), 3, dw)
        for (x, y) in ((30, 40), (34, 52), (31, 22)):
            for k in range(3):
                cv.set(x + k, y, P['dw_dk'])
        cv.outline()
    elif kind == 'rabougri':
        bark = (P['b_lt'], P['b_md'], P['b_dk'])
        twisted(cv, [(31, 63), (30, 52), (34, 44), (30, 36)], 9, bark)
        twisted(cv, [(30, 44), (18, 36), (10, 28)], 4, bark)
        twisted(cv, [(34, 42), (46, 34), (54, 28)], 4, bark)
        pal4 = (P['rb_hi'], P['rb_lt'], P['rb_md'], P['rb_dk'])
        mass(cv, [(12, 24, 11, 8), (52, 24, 11, 8), (32, 18, 16, 10), (22, 30, 12, 8), (42, 30, 12, 8), (32, 28, 20, 9)], pal4, 150, 0.5)
        r = random.Random(7)
        for _ in range(6):
            x, y = r.randrange(8, 56), r.randrange(10, 36)
            if cv.get(x, y) is not None and cv.get(x, y) != P['O']:
                cv.set(x, y, P['ore_o'])
        cv.outline()
    else:
        snow = kind == 'sapin_neige'
        b = 1 if kind == 'sapin_b' else 0
        cv.rect(28, 34, 35, 63, P['b_md'])
        cv.rect(28, 34, 29, 63, P['b_lt'])
        cv.rect(34, 34, 35, 63, P['b_dk'])
        for yy in range(38, 60, 6):
            cv.set(31, yy, P['b_dk'])
            cv.set(32, yy + 2, P['b_dk'])
        cv.rect(25, 60, 38, 63, P['b_md'])
        cv.rect(25, 60, 26, 63, P['b_lt'])
        cv.rect(37, 60, 38, 63, P['b_dk'])
        sapin_tiers(cv, 32, 1, 40, 60 if not b else 56, snow, 160 + b, None)
        cv.outline()
    _BT[kind] = cv
    return cv


@reg(*[f'{k}_cime_h{s}' for k in ('sapin_a', 'sapin_b', 'sapin_neige', 'rabougri', 'pin_mort') for s in 'gd'],
     *[f'{k}_tronc_{s}' for k in ('sapin_a', 'sapin_b', 'sapin_neige', 'rabougri', 'pin_mort') for s in 'gd'])
def gros_arbre(name, tile):
    kind, part = name.split('_cime_')[0] if '_cime_' in name else name.split('_tronc_')[0], 'cime' if '_cime_' in name else 'tronc'
    side = name[-1]
    return big_tree(kind).crop(T if side == 'd' else 0, 0 if part == 'cime' else T)


# ------------------------------------------------------------------ cascade, sources
def water_fall(frame, top=False):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = cliff_face_px(x, y, 'face')
    for y in range(T):
        for x in range(3, 29):
            xx, yy = x, y + frame * 3
            n = vnoise(xx * 2, yy // 2 * 1, 8, 5)
            col = P['w_lt']
            if (xx * 7 + yy * 2) % 6 < 2:
                col = P['w_hi']
            elif (xx * 5) % 7 == 0:
                col = P['w_md']
            if (xx + (yy // 3) * 5) % 9 == 0:
                col = P['white']
            if x < 6 or x > 25:
                col = P['w_md']
            cv.p[y][x] = col
        cv.p[y][2] = P['O']
        cv.p[y][29] = P['O']
        cv.p[y][3] = P['w_dk']
        cv.p[y][28] = P['w_dk']
    return cv


@reg('cascade_milieu_a', 'cascade_milieu_b')
def cascade_m(name, tile):
    return water_fall(0 if name.endswith('a') else 1).p


@reg('cascade_haut')
def cascade_haut(name, tile):
    cv = Cv()
    g = ground_tex(1, 'a')
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    wf = water_fall(0)
    for y in range(12, T):
        for x in range(T):
            cv.p[y][x] = wf.p[y][x] if y > 17 else cliff_face_px(x, y - 12, 'haut')
    for y in range(18, T):                 # eau qui déborde
        for x in range(3, 29):
            cv.p[y][x] = wf.p[y][x]
    for y in range(0, 14):                 # chenal d'eau amont
        for x in range(6, 26):
            w = 8 + (y * 5) // 14
            if abs(x - 15.5) < w:
                cv.p[y][x] = P['w_md'] if (x + y) % 4 else P['w_lt']
        cv.p[y][max(0, 15 - 8 - (y * 5) // 14)] = P['O']
        cv.p[y][min(31, 16 + 7 + (y * 5) // 14)] = P['O']
    for x in range(4, 28):
        cv.p[14][x] = P['w_hi']
        cv.p[15][x] = P['white'] if x % 3 else P['w_hi']
        cv.p[16][x] = P['w_lt']
    for x in range(1, 31):
        if cv.p[12][x] not in (P['w_hi'], P['white']):
            cv.p[12][x] = P['O']
    return cv.p


@reg('cascade_pied')
def cascade_pied(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = F.DEEP[y][x]
    wf = water_fall(0)
    for y in range(0, 12):
        for x in range(T):
            cv.p[y][x] = wf.p[y][x]
    for y in range(12, 22):
        for x in range(3, 29):
            e = (x - 15.5) / 12.5
            d = abs(e) ** 2 + ((y - 14) / 8.0) ** 2
            if d < 1:
                cv.p[y][x] = P['white'] if rnd(x, y, 3) < 0.45 else P['foam'] if rnd(x, y, 4) < 0.6 else P['w_hi']
    r = random.Random(22)
    for _ in range(14):
        x, y = r.randrange(1, 31), r.randrange(14, 31)
        cv.set(x, y, P['foam'])
        cv.set(x + 1, y, P['w_hi'])
    return cv.p


@reg('cascade_ecume')
def ecume(name, tile):
    cv = Cv()
    r = random.Random(23)
    for _ in range(11):
        x, y = r.randrange(2, 28), r.randrange(4, 28)
        ell(cv, x + 1, y + 1, 2.5, 1.7, P['foam'])
        cv.set(x, y, P['white'])
    return cv.p


@reg('ecume_rive')
def ecume_rive(name, tile):
    cv = Cv()
    for x in range(0, T):
        y = 3 + int(2 * vnoise(x, 0, 8, 61))
        for k in range(2):
            if rnd(x, k, 2) < 0.8:
                cv.set(x, y + k, P['foam'] if k == 0 else P['w_hi'])
    for x in range(0, T, 4):
        cv.set(x, 8, P['foam'])
    return cv.p


@reg('flaque_gel')
def flaque_gel(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            e = ((x - 15.5) / 12.0) ** 2 + ((y - 16.5) / 8.5) ** 2 + (rnd(x, y, 5) - 0.5) * 0.25
            if e <= 1:
                cv.p[y][x] = P['O'] if e > 0.86 else P['sn_dk'] if e > 0.7 else P['w_hi'] if (x + y) % 6 else P['white']
    cv.line(10, 14, 16, 18, P['sn_md'])
    cv.line(16, 18, 21, 15, P['sn_md'])
    return cv.p


@reg('source_rocher')
def source(name, tile):
    p = mrock(1)
    cv = cv_from(p)
    for y in range(18, 29):
        for x in range(11, 22):
            if ((x - 16) / 5.5) ** 2 + ((y - 24) / 4.0) ** 2 <= 1:
                cv.p[y][x] = P['w_lt'] if (x + y) % 3 else P['w_hi']
    for y in range(14, 20):
        cv.set(16, y, P['w_hi'])
        cv.set(15, y, P['w_lt'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ ponts de bois
def plank_h(cv, x0, x1, y0=5, y1=26):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            c = P['plank'] if x % 8 else P['plank_d']
            if (x + y) % 11 == 0:
                c = P['t_lt']
            if y == y0 or y == y0 + 1:
                c = P['pk_hi'] if x % 8 else P['plank_d']
            cv.set(x, y, c)


def bridge_h(end):
    cv = Cv()
    plank_h(cv, 0 if end != 'g' else 6, 31 if end != 'd' else 25)
    cv.rect(0 if end != 'g' else 5, 3, 31 if end != 'd' else 26, 5, P['b_md'])
    cv.rect(0 if end != 'g' else 5, 3, 31 if end != 'd' else 26, 3, P['b_lt'])
    cv.rect(0 if end != 'g' else 5, 26, 31 if end != 'd' else 26, 28, P['b_dk'])
    for x in ((1, 17) if not end else (7, 20) if end == 'g' else (4, 18)):
        cv.rect(x, 1, x + 2, 6, P['b_lt'])
        cv.rect(x, 25, x + 2, 30, P['b_md'])
    if end:
        xs = (3, 6) if end == 'g' else (25, 28)
        for x in range(xs[0] - 2, xs[1] + 1) if end == 'g' else range(xs[0], xs[1] + 3):
            for y in range(7, 25):
                cv.set(x, y, P['gr_md'] if (x + y) % 3 else P['gr_lt'])
        cv.rect(0 if end == 'g' else 26, 3, 6 if end == 'g' else 31, 4, None)
    cv.outline()
    return cv.p


def bridge_v(end):
    cv = Cv()
    y0, y1 = (0 if end != 'haut' else 6), (31 if end != 'bas' else 25)
    for y in range(y0, y1 + 1):
        for x in range(5, 27):
            cv.p[y][x] = P['plank'] if y % 8 else P['plank_d']
            if (x + y) % 11 == 0:
                cv.p[y][x] = P['t_lt']
    cv.rect(3, y0, 5, y1, P['b_md'])
    cv.rect(26, y0, 28, y1, P['b_dk'])
    cv.rect(3, y0, 3, y1, P['b_lt'])
    if end:
        for y in (range(0, 6) if end == 'haut' else range(26, 32)):
            for x in range(4, 28):
                cv.p[y][x] = P['gr_md'] if (x + y) % 3 else P['gr_lt']
    cv.outline()
    return cv.p


@reg('pont_h', 'pont_h_bout_g', 'pont_h_bout_d')
def pont_h(name, tile):
    return bridge_h('' if name == 'pont_h' else name[-1])


@reg('pont_v', 'pont_v_bout_haut', 'pont_v_bout_bas')
def pont_v(name, tile):
    return bridge_v('' if name == 'pont_v' else name.split('_')[-1])


@reg('pont_pilotis')
def pilotis(name, tile):
    cv = Cv()
    for x in (8, 22):
        cv.rect(x, 12, x + 4, 28, P['b_md'])
        cv.rect(x, 12, x + 1, 28, P['b_lt'])
        cv.rect(x + 4, 12, x + 4, 28, P['b_dk'])
        ell(cv, x + 2, 28, 5, 1.5, P['foam'])
    cv.outline()
    return cv.p


@reg('pont_planches')
def pont_planches(name, tile):
    cv = Cv()
    for (x0, y0, x1, y1, a) in ((3, 5, 26, 11, 0), (6, 14, 29, 20, 1), (2, 23, 24, 29, 0)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                cv.p[y][x] = P['plank'] if y != y1 else P['plank_d']
                if y == y0:
                    cv.p[y][x] = P['pk_hi']
                if (x - x0) % 9 == 8:
                    cv.p[y][x] = P['plank_d']
        cv.set(x0 + 4, (y0 + y1) // 2, P['m_lt'])
        cv.set(x1 - 4, (y0 + y1) // 2, P['m_lt'])
    cv.outline()
    return cv.p
