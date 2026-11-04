"""Château de Morvath (intérieur), dessin final des tuiles : pierre violette sombre, tapis, murs, portes, fosse de ronces, arène, cercle des sceaux.

Palette : dalles violet-gris (sol_in), dessus de mur presque noir (cap_in), faces de mur violet clair (fac_in), tapis rouge sombre (tapis),
ronces noires et violettes (ronce), or terni (or_), runes cyan (rune), arène violet clair (arene). Lumière en haut à gauche, contour
sombre d'1 px pour les objets, aucun contour sur les dalles. Chaque tuile est dessinée par REG[nom](nom, d). Les numéros sont ceux du plan.
Les bords de la fosse (81 à 94) sont ensuite fondus par fondus.py (voir main_final de chateau.py).
"""
import math
import random

from chateau_pierre import *  # noqa: F401,F403
import chateau_pierre as C
import chateau_objets as OB

REG = {}
PAL['rim_in'] = pal('#9486b6', '#8072a2', '#66598a', '#4e4470', '#382f52')
INW = Wall(PAL['cap_in'], PAL['rim_in'], masonry(PAL['fac_in'], 3), seed=7)


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


SOL = PAL['sol_in']
BR = PAL['ronce']

# ------------------------------------------------------------------ sols
REG['pierre_a'] = lambda n, d: slab_floor(SOL, 'a', 1)
REG['pierre_b'] = lambda n, d: slab_floor(SOL, 'b', 2)
REG['pierre_c'] = lambda n, d: slab_floor(SOL, 'c', 3)
REG['pierre_fissuree'] = lambda n, d: slab_floor(SOL, 'f', 4, brambles=BR)


def carpet(kind):
    """Tapis rouge sombre à bordure d'or, posé sur la dalle. Le masque M est défini en coordonnées étendues : les bords
    n'apparaissent qu'aux vrais bords du tapis, deux tuiles voisines se raccordent."""
    tp, go = PAL['tapis'], PAL['or_']

    def M(x, y):
        v = 3 <= x <= 28
        h = 3 <= y <= 28
        if kind == 'v':
            return v
        if kind == 'h':
            return h
        if kind == 'haut':
            return v and y >= 7
        if kind == 'bas':
            return v and y <= 24
        if kind == 'gauche':
            return h and x >= 7
        if kind == 'droite':
            return h and x <= 24
        return v or h
    t = slab_floor(SOL, 'a', 1)
    for y in range(T):
        for x in range(T):
            if not M(x, y):
                continue
            d = 9
            for k in range(1, 6):                                       # distance au bord du tapis
                if (not M(x - k, y)) or (not M(x + k, y)) or (not M(x, y - k)) or (not M(x, y + k)):
                    d = k
                    break
            lit = (not M(x - d, y)) or (not M(x, y - d)) if d < 9 else False
            if d == 1:
                col = tp[DP]
            elif d == 2:
                col = go[HI] if lit else go[MD]
            elif d == 3:
                col = go[MD] if lit else go[DK]
            elif d == 4:
                col = tp[DK]
            else:
                n = vnoise(x, y, 8, 61)
                col = tp[LT] if n > 0.74 else tp[DK] if n < 0.2 else tp[MD]
                if (x + y) % 16 == 0 or (x - y) % 16 == 0:               # losanges
                    col = tp[LT] if (x + y) % 32 else go[MD]
                if (x + y) % 16 == 0 and (x - y) % 16 == 0:
                    col = go[HI]
            t[y][x] = col
    # franges aux extrémités
    def fringe(side):
        for k in range(4):
            for u in range(3, 29):
                if u % 2 == 0 or k == 0:
                    col = go[HI] if (u % 4 == 0 and k < 2) else go[MD] if k < 3 else go[DK]
                    if side == 'haut':
                        put(t, u, 6 - k, col)
                    elif side == 'bas':
                        put(t, u, 25 + k, col)
                    elif side == 'gauche':
                        put(t, 6 - k, u, col)
                    else:
                        put(t, 25 + k, u, col)
    if kind in ('haut', 'bas', 'gauche', 'droite'):
        fringe(kind)
    if kind == 'x':
        for dx, dy in ((0, 0),):
            ring(t, 15.5, 15.5, 6, go[MD], 2)
            ring(t, 15.5, 15.5, 3, go[HI], 1)
            put(t, 15, 15, go[HI])
            put(t, 16, 16, go[HI])
    return t


for _n, _k in (('tapis_v', 'v'), ('tapis_h', 'h'), ('tapis_bout_haut', 'haut'), ('tapis_bout_bas', 'bas'), ('tapis_bout_gauche', 'gauche'),
               ('tapis_bout_droite', 'droite'), ('tapis_croix', 'x')):
    REG[_n] = (lambda k: (lambda n, d: carpet(k)))(_k)


def shade_tex(kind):
    t = blank()
    col = PAL['cap_in'][DP]
    for y in range(T):
        for x in range(T):
            dh = 1 - y / 9 if kind in ('haut', 'coin') else 0
            dg = 1 - x / 9 if kind in ('gauche', 'coin') else 0
            k = max(dh, dg)
            if k > 0 and (k > 0.65 or (k > 0.3 and (x + y) % 2 == 0) or (k > 0 and (x + y) % 4 == 0 and (x // 2 + y) % 2 == 0)):
                t[y][x] = col
    return t


REG['ombre_mur_haut'] = lambda n, d: shade_tex('haut')
REG['ombre_mur_gauche'] = lambda n, d: shade_tex('gauche')
REG['ombre_mur_coin'] = lambda n, d: shade_tex('coin')


def rubble(p, seed=3, n=6):
    t = blank()
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.randrange(3, 27), r.randrange(5, 27)
        w, h = r.choice((2, 3, 4)), r.choice((2, 3))
        rect(t, x, y, x + w, y + h, p[MD])
        rect(t, x, y, x + w, y, p[HI])
        rect(t, x, y, x, y + h, p[LT])
        rect(t, x, y + h, x + w, y + h, p[DK])
    outline(t, O)
    return t


REG['gravats'] = lambda n, d: rubble(PAL['sol_in'], 9, 7)


@reg('ronces_sol')
def ronces_sol(n, d):
    cv = blank()
    r = random.Random(41)
    for _ in range(5):
        x0, y0 = r.randrange(3, 29), r.randrange(6, 28)
        pts = [(x0, y0)]
        for _k in range(3):
            pts.append((pts[-1][0] + r.randrange(-6, 7), pts[-1][1] + r.randrange(-5, 6)))
        for a, b in zip(pts, pts[1:]):
            line(cv, a[0], a[1], b[0], b[1], BR[DK])
            line(cv, a[0], a[1] - 1, b[0], b[1] - 1, BR[MD])
        for a in pts:
            put(cv, a[0] + 1, a[1] - 2, BR[HI])
    outline(cv, BR[DP])
    return cv


# ------------------------------------------------------------------ murs
for _n, _i in {'mur_haut': 16, 'mur_bas': 17, 'mur_gauche': 18, 'mur_droite': 19, 'mur_coin_int_hg': 20, 'mur_coin_int_hd': 21,
               'mur_coin_int_bg': 22, 'mur_coin_int_bd': 23, 'mur_coin_ext_hg': 24, 'mur_coin_ext_hd': 25, 'mur_coin_ext_bg': 26,
               'mur_coin_ext_bd': 27, 'mur_plein': 28, 'mur_diag_a': 29, 'mur_diag_b': 30}.items():
    REG[_n] = (lambda b: (lambda n, d: INW.tile(b)))(WALLBITS[_i])


# ------------------------------------------------------------------ portes (cadre de pierre)
def post(t, x0, x1, y0, y1):
    p = PAL['fac_in']
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            col = p[MD]
            if x == x0:
                col = p[HI]
            elif x == x0 + 1:
                col = p[LT]
            elif x == x1:
                col = p[DK]
            if y % 8 == 0 and x != x0:
                col = p[DP]
            t[y][x] = col
        put(t, x0 - 1, y, O)
        put(t, x1 + 1, y, O)


def beam(t, x0, x1, y0, y1):
    p = PAL['fac_in']
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            col = p[MD]
            if y == y0:
                col = p[HI]
            elif y == y0 + 1:
                col = p[LT]
            elif y == y1:
                col = p[DK]
            if x % 10 == 0 and y not in (y0, y1):
                col = p[DP]
            t[y][x] = col
    for x in range(x0, x1 + 1):
        put(t, x, y0 - 1, O)
        put(t, x, y1 + 1, O)


FLOOR = slab_floor(SOL, 'a', 1)


def dark(t, x0, y0, x1, y1, axis, rev=False):
    """Sol de passage qui s'assombrit vers l'intérieur."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = (y1 - y) / max(1, y1 - y0) if axis == 'v' else (x1 - x) / max(1, x1 - x0)
            if rev:
                k = 1 - k
            col = SOL[DK] if k < 0.35 else SOL[DP] if k < 0.7 else PAL['vide'][MD]
            if k < 0.35 and rnd(x, y, 19) < 0.4:
                col = FLOOR[y][x]
            if k >= 0.7 and rnd(x, y, 20) < 0.3:
                col = PAL['vide'][DK]
            t[y][x] = col


@reg('porte_haut')
def porte_haut(n, d):
    t = INW.tile((1, 1, 0, 0))
    dark(t, 7, 0, 24, 31, 'v')
    post(t, 4, 6, 0, 31)
    post(t, 25, 27, 0, 31)
    return t


@reg('porte_bas')
def porte_bas(n, d):
    t = INW.tile((0, 0, 1, 1))
    for y in range(32):
        for x in range(7, 25):
            t[y][x] = SOL[DK] if y < 24 else SOL[DP]
            if rnd(x, y, 21) < 0.3:
                t[y][x] = FLOOR[y][x]
    post(t, 4, 6, 0, 31)
    post(t, 25, 27, 0, 31)
    return t


@reg('porte_gauche')
def porte_gauche(n, d):
    t = INW.tile((1, 0, 1, 0))
    for y in range(4, 28):
        for x in range(32):
            k = x / 31
            t[y][x] = PAL['vide'][DK] if k < 0.25 else SOL[DP] if k < 0.5 else SOL[DK] if k < 0.8 else FLOOR[y][x]
    beam(t, 0, 31, 0, 3)
    beam(t, 0, 31, 28, 31)
    return t


@reg('porte_droite')
def porte_droite(n, d):
    t = INW.tile((0, 1, 0, 1))
    for y in range(4, 28):
        for x in range(32):
            k = 1 - x / 31
            t[y][x] = PAL['vide'][DK] if k < 0.25 else SOL[DP] if k < 0.5 else SOL[DK] if k < 0.8 else FLOOR[y][x]
    beam(t, 0, 31, 0, 3)
    beam(t, 0, 31, 28, 31)
    return t


def lintel(t, y0, y1, key=True):
    beam(t, 2, 29, y0, y1)
    for x in (6, 25):
        t[(y0 + y1) // 2][x] = PAL['fac_in'][DP]
    if key:
        for x in range(14, 18):
            t[(y0 + y1) // 2][x] = PAL['or_'][MD]
        t[(y0 + y1) // 2 - 1][15] = PAL['or_'][HI]
        t[(y0 + y1) // 2 - 1][16] = PAL['or_'][HI]


@reg('porte_haut_dessus')
def porte_haut_dessus(n, d):
    t = blank()
    lintel(t, 1, 9)
    return t


@reg('porte_bas_dessus')
def porte_bas_dessus(n, d):
    t = blank()
    lintel(t, 5, 13)
    return t


@reg('porte_gauche_dessus')
def porte_gauche_dessus(n, d):
    t = blank()
    post(t, 2, 9, 0, 31)
    for y in (5, 26):
        t[y][5] = PAL['fac_in'][DP]
    return t


@reg('porte_droite_dessus')
def porte_droite_dessus(n, d):
    t = blank()
    post(t, 22, 29, 0, 31)
    for y in (5, 26):
        t[y][25] = PAL['fac_in'][DP]
    return t


# ------------------------------------------------------------------ arène, symboles, socle, escaliers
ARE = PAL['arene']


def arene_tex(kind):
    t = grain(ARE, 31)
    for y in range(T):
        for x in range(T):                                             # fines lignes gravées
            if kind == 0 and (y % 8 == 3 and rnd(x // 6, y, 3) < 0.9):
                t[y][x] = ARE[LT] if (x // 6) % 3 else ARE[MD]
    if kind in (0, 2, 3):
        bond(t, ARE, (0, 16), 40 + kind)
    if kind == 1:                                                      # joints en étoile
        for k in range(32):
            for pts in ((k, k), (k, 31 - k)):
                x, y = pts
                if abs(x - 16) + abs(y - 16) > 5 and k % 2 == 0:
                    t[y][x] = ARE[DK]
            if k % 3:
                t[16][k] = ARE[DK]
                t[k][16] = ARE[DK]
        ring(t, 15.5, 15.5, 6, ARE[DP], 1)
    if kind == 2:                                                      # éclats
        r = random.Random(77)
        for _ in range(9):
            x, y = r.randrange(2, 29), r.randrange(2, 29)
            put(t, x, y, ARE[HI])
            put(t, x + 1, y, ARE[LT])
            put(t, x, y + 1, ARE[DK])
            put(t, x + 1, y + 1, ARE[DP])
    if kind == 3:
        C.crack(t, ARE, [(31, 4), (25, 8), (21, 7), (17, 13), (18, 17), (11, 21), (8, 26), (2, 28)], BR)
    return t


for _i, _n in enumerate(('sol_arene_a', 'sol_arene_b', 'sol_arene_c', 'sol_arene_fissure')):
    REG[_n] = (lambda k: (lambda n, d: arene_tex(k)))(_i)

REG['symbole_arc'] = lambda n, d: _sym(OB.ARC)
REG['symbole_bombe'] = lambda n, d: _sym(OB.BOMB)
REG['symbole_lanterne'] = lambda n, d: _sym(OB.LANT)


def _sym(rows):
    t = slab_floor(SOL, 'a', 1)
    rows2 = [r.replace('>', '#') for r in rows]
    OB.engrave(t, rows2, 8, 8, PAL['or_'][LT], SOL[DP])
    ring(t, 15.5, 15.5, 13, PAL['or_'][DK], 1)
    return t


@reg('socle')
def socle(n, d):
    cv = blank()
    p = PAL['fac_in']
    OB.rect_o(cv, 5, 12, 26, 29, p, 2, 0.1)
    OB.rect_o(cv, 3, 8, 28, 14, p, 3)
    OB.rect(cv, 4, 9, 27, 9, p[HI]) if hasattr(OB, 'rect') else None
    for x in range(6, 26, 5):
        put(cv, x, 19, p[DK])
    put(cv, 15, 21, PAL['or_'][MD])
    put(cv, 16, 21, PAL['or_'][MD])
    outline(cv, O)
    for x in range(4, 28):
        if x % 2 == 0 and cv[30][x] is None:
            cv[30][x] = PAL['cap_in'][DP]
    return cv


def steps(up, fl=None, p=None):
    t = slab_floor(fl or SOL, 'a', 1)
    p = p or PAL['fac_in']
    for k in range(4):
        y0 = k * 8
        for y in range(y0, y0 + 8):
            for x in range(T):
                if up:
                    col = p[HI] if y == y0 else (p[LT] if y < y0 + 5 else p[DK])
                    if y == y0 + 7:
                        col = p[DP]
                    if y < y0 + 5 and y > y0:
                        n = vnoise(x, y, 8, 51 + k)
                        col = p[LT] if n > 0.4 else p[MD]
                else:
                    sh = 1 - k * 0.22
                    col = p[MD] if y < y0 + 5 else p[DK]
                    if y == y0:
                        col = p[LT]
                    if y >= y0 + 5:
                        col = p[DP] if k else p[DK]
                    if k >= 2:
                        col = PAL['cap_in'][HI] if y < y0 + 5 else PAL['cap_in'][DP]
                    if k == 3 and y < y0 + 5:
                        col = PAL['vide'][LT]
                    if k == 3 and y >= y0 + 5:
                        col = PAL['vide'][DK]
                t[y][x] = col
    for y in range(T):
        t[y][0] = PAL['cap_in'][DP]
        t[y][31] = PAL['cap_in'][DP]
    return t


REG['escalier_montant'] = lambda n, d: steps(True)
REG['escalier_descendant'] = lambda n, d: steps(False)


# ------------------------------------------------------------------ armures, statues, brasero
REG['armure_base'] = lambda n, d: slice_(OB.knight('a', True), 0, 1)
REG['armure_haut'] = lambda n, d: slice_(OB.knight('a', True), 0, 0)
REG['statue_base'] = lambda n, d: slice_(OB.knight('b', False), 0, 1)
REG['statue_haut'] = lambda n, d: slice_(OB.knight('b', False), 0, 0)


def brasero_socle(p, tall=False):
    cv = blank()
    OB.rect_o(cv, 6, 14, 25, 29, p, 5, 0.1)
    OB.rect_o(cv, 4, 10, 27, 16, p, 6)
    for x in range(8, 24, 5):
        put(cv, x, 22, p[DK])
    rect(cv, 10, 11, 21, 13, PAL['cap_in'][DP])                         # cuvette sombre, braises éteintes
    for x in (12, 16, 19):
        put(cv, x, 12, PAL['rouge'][DK])
    outline(cv, O)
    return cv


REG['brasero_socle'] = lambda n, d: brasero_socle(PAL['fac_in'])


# ------------------------------------------------------------------ murs fissurés fermé -> ouvert
def breach(base, orient, wallpal, floorpal=None):
    """Brèche opaque : un trou noir irrégulier, éclats de pierre et gravats devant. base = tuile de mur d'origine."""
    t = copy(base)
    floorpal = floorpal or SOL

    def uv_to_xy(u, v):
        return {'haut': (u, 31 - v), 'bas': (u, v), 'gauche': (31 - v, u), 'droite': (v, u)}[orient]
    depth = 22 if orient in ('haut', 'bas') else 20
    for v in range(depth + 1):
        hw = 10.5 - v * 0.22 + (rnd(v, 3, 8) - 0.5) * 3.4
        if v > depth - 3:
            hw -= (v - depth + 3) * 2.2
        for u in range(32):
            du = u - 15.5
            if abs(du) <= hw:
                x, y = uv_to_xy(u, v)
                k = v / depth
                col = PAL['vide'][MD] if k < 0.3 else PAL['vide'][DK] if k < 0.6 else PAL['vide'][DP]
                if k < 0.2 and rnd(u, v, 12) < 0.45:
                    col = floorpal[DP]
                if k < 0.1 and rnd(u, v, 13) < 0.5:
                    col = floorpal[DK]
                t[y][x] = col
            elif abs(du) <= hw + 1.2:                                  # bord de la brèche : contour sombre + éclats clairs en haut/gauche
                x, y = uv_to_xy(u, v)
                t[y][x] = O if rnd(u, v, 14) < 0.7 else wallpal[DP]
            elif abs(du) <= hw + 2.4 and rnd(u, v, 15) < 0.45:
                x, y = uv_to_xy(u, v)
                t[y][x] = wallpal[HI] if du < 0 else wallpal[DK]
    # bout du trou
    for u in range(8, 24):
        x, y = uv_to_xy(u, depth)
        if rnd(u, 1, 16) < 0.7:
            t[y][x] = O
    # gravats devant l'ouverture
    r = random.Random(7)
    for _ in range(6):
        u, v = r.choice((r.randrange(3, 9), r.randrange(23, 30))), r.randrange(0, 5)
        for du, dv in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)):
            x, y = uv_to_xy(u + du, v + dv)
            t[y][x] = wallpal[HI] if (du, dv) == (0, 0) else wallpal[MD] if dv == 0 else wallpal[DK]
        for du in range(-1, 4):
            x, y = uv_to_xy(u + du, v + 2)
            if t[y][x] != wallpal[DK] and du in (-1, 3):
                pass
    for _ in range(6):
        u, v = r.randrange(11, 21), r.randrange(0, 4)
        x, y = uv_to_xy(u, v)
        t[y][x] = wallpal[LT]
        x, y = uv_to_xy(u + 1, v)
        t[y][x] = wallpal[DK]
    return t


def fissure(base, orient, light=None, seed=1):
    """Fissures claires sur une tuile de mur (fermée : on voit la fissure et quelques pierres qui se détachent)."""
    t = copy(base)
    light = light or PAL['fac_in'][HI]
    glow = PAL['rune'][DK]
    r = random.Random(seed)
    vert = orient in ('haut', 'bas')
    ys = (9, 31) if orient == 'haut' else (0, 24) if orient == 'bas' else (0, 31)
    xs = (0, 31)
    pts = []
    if vert:
        y0, y1 = ys
        x = 15
        for y in range(y0, y1 + 1, 3):
            x = max(9, min(22, x + r.choice((-2, -1, 0, 1, 2))))
            pts.append((x, y))
    else:
        x0, x1 = (3, 28) if orient == 'gauche' else (3, 28)
        y = 15
        for x in range(x0, x1 + 1, 3):
            y = max(8, min(23, y + r.choice((-2, -1, 0, 1, 2))))
            pts.append((x, y))
    for a, b in zip(pts, pts[1:]):
        line(t, a[0], a[1], b[0], b[1], O)
        line(t, a[0] - 1, a[1], b[0] - 1, b[1], light)
    for (x, y) in pts[1:-1:2]:                                          # branches
        dx = r.choice((-1, 1))
        line(t, x, y, x + dx * 4, y + 3, O)
        line(t, x + dx, y, x + dx * 5, y + 3, light)
    # zone fragilisée : pierres plus sombres et éclatées autour de la fissure (se repère dès l'arrivée)
    cx0 = sum(p[0] for p in pts) // len(pts)
    cy0 = sum(p[1] for p in pts) // len(pts)
    for y in range(32):
        for x in range(32):
            dd = math.hypot((x - cx0) / 9.5, (y - cy0) / 11.5)
            if dd < 1.0 and t[y][x] not in (O, light) and rnd(x, y, seed + 40) < (1.0 - dd) * 0.8:
                t[y][x] = PAL['cap_in'][HI] if (x + y) % 3 else PAL['cap_in'][LT]
    for a, b in zip(pts, pts[1:]):
        line(t, a[0], a[1], b[0], b[1], O)
        line(t, a[0] - 1, a[1], b[0] - 1, b[1], light)
    # pierres écaillées autour
    for _ in range(9):
        x, y = pts[r.randrange(len(pts))]
        x += r.randrange(-6, 7)
        y += r.randrange(-3, 4)
        if 0 <= x < 31 and 0 <= y < 31:
            t[y][x] = PAL['fac_in'][DP]
            t[y][x + 1] = PAL['fac_in'][LT]
    return t


FIS = {'haut': (1, 1, 0, 0), 'bas': (0, 0, 1, 1), 'gauche': (1, 0, 1, 0), 'droite': (0, 1, 0, 1)}
for _k, (_s, _i) in enumerate((('haut', 72), ('bas', 73), ('gauche', 74), ('droite', 75))):
    REG[f'mur_fissure_{_s}'] = (lambda s, k: (lambda n, d: fissure(INW.tile(FIS[s]), s, None, 3 + k)))(_s, _k)
    REG[f'mur_fissure_{_s}_ouvert'] = (lambda s: (lambda n, d: breach(INW.tile(FIS[s]), s, PAL['fac_in'])))(_s)


# ------------------------------------------------------------------ fosse de ronces (80 = pierre, 95 = ronces pleines ; 81 à 94 fondus par fondus.py)
REG['fosse_base'] = lambda n, d: slab_floor(SOL, 'a', 1)
REG['fosse_plein'] = lambda n, d: brambles_tex(5)


def _fosse_bord(n, d):
    return slab_floor(SOL, 'a', 1)               # provisoire : remplacé par le fondu (fondus.py) juste après


for _k in range(1, 15):
    REG['fosse_' + format(_k, '04b')] = _fosse_bord


# ------------------------------------------------------------------ murs de décor, niches, rune
FPAL = PAL['fac_in']


def wall_variant(kind):
    t = face_tile(FPAL, 3)
    if kind == 'tenture':
        for x in range(4, 28):                                          # drap violet avec plis
            for y in range(0, 30):
                if y > 26 + int(rnd(x, 1, 2) * 3) and x % 4 != 1:
                    continue
                f = (x - 4) % 6
                col = PAL['ronce'][MD] if f in (0, 1) else PAL['ronce'][DK] if f in (2, 3) else PAL['ronce'][LT] if f == 4 else PAL['ronce'][MD]
                if y < 2:
                    col = PAL['or_'][MD]
                t[y][x] = col
        for x in range(4, 28):
            t[2][x] = PAL['or_'][HI] if x % 3 else PAL['or_'][MD]
    elif kind == 'blason':
        OB.rect_o(t, 7, 3, 24, 28, PAL['or_'], 3)
        for y in range(5, 27):
            hw = 7 if y < 22 else max(0, 7 - (y - 21) * 1.4)
            for x in range(int(15.5 - hw), int(15.5 + hw) + 1):
                t[y][x] = PAL['ronce'][DK]
        eye(t, 15, 14, PAL['or_'][HI], PAL['ronce'][DP], PAL['rouge'][LT], O)
    elif kind == 'ronces':
        t = brambles_over(t)
    elif kind in ('niche', 'niche_oeil'):
        niche(t, kind == 'niche_oeil')
    elif kind == 'vitrail':
        vitrail(t)
    elif kind == 'rune':
        for y in range(T):
            for x in range(T):
                d = math.hypot(x - 15.5, y - 15.5)
                if 6.2 <= d < 7.4 and not (11 <= x <= 20 and y < 10):
                    t[y][x] = FPAL[DK] if not (x < 15.5 and y < 15.5) else FPAL[DP]
        for y in range(8, 24):
            t[y][16] = FPAL[DK]
        for k in range(5):
            t[11 + k][12 - k // 2] = FPAL[DK]
            t[11 + k][20 + k // 2] = FPAL[DK]
    return t


def brambles_over(t):
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 66)
            if n > 0.5 and (y < 8 + n * 26):
                a = abs(vnoise(x, y, 16, 67) - 0.5)
                if a < 0.17 or n > 0.7:
                    t[y][x] = BR[DK] if a > 0.08 else BR[MD]
                    if rnd(x, y, 3) < 0.07:
                        t[y][x] = BR[HI]
    for _ in range(16):
        x, y = int(rnd(_, 1, 4) * 30) + 1, int(rnd(_, 2, 5) * 24)
        if t[y][x] in (BR[DK], BR[MD]):
            put(t, x + 1, y - 1, BR[LT])
    return t


def niche(t, eye_niche):
    p = FPAL
    OB.rect_o(t, 4, 3, 27, 29, p, 5)
    for y in range(6, 27):
        for x in range(7, 25):
            k = (y - 6) / 20
            col = PAL['vide'][MD] if y < 10 else PAL['vide'][DK] if y < 18 else PAL['vide'][DP]
            if x < 9 or y < 8:
                col = PAL['vide'][LT]
            t[y][x] = col
    for x in range(7, 25):
        t[6][x] = O
    for y in range(6, 27):
        t[y][7] = O
    if eye_niche:
        for x in range(5, 27):
            put(t, x, 4, PAL['or_'][MD])
            put(t, x, 28, PAL['or_'][DK])
        for y in range(5, 28):
            put(t, 5, y, PAL['or_'][LT])
            put(t, 26, y, PAL['or_'][DK])
        ring(t, 15.5, 16, 6, PAL['ronce'][MD], 1)
        for i in range(8):
            a = i * math.pi / 4
            put(t, round(15.5 + math.cos(a) * 8), round(16 + math.sin(a) * 8), PAL['or_'][DK])
    else:
        for y in range(24, 28):
            for x in range(8, 24):
                if rnd(x, y, 3) < 0.4:
                    t[y][x] = p[DK]


def vitrail(t):
    p = FPAL
    cols = [PAL['ronce'][LT], PAL['rune'][DK], PAL['rouge'][MD], PAL['ronce'][MD], PAL['rune'][DK], PAL['or_'][DK]]
    OB.rect_o(t, 8, 3, 23, 29, p, 5)
    for y in range(5, 28):
        for x in range(10, 22):
            if y < 12 and abs(x - 15.5) > 4 + (y - 5) * 0.5 and y < 9:
                continue
            k = ((x - 10) // 4 + (y - 5) // 6) % len(cols)
            col = cols[k]
            if (x - 10) % 4 == 0 or (y - 5) % 6 == 0:
                col = O
            t[y][x] = col
    for y in range(5, 28):
        t[y][10] = O
        t[y][21] = O
    for x in range(10, 22):
        t[27][x] = O


REG['mur_tenture'] = lambda n, d: wall_variant('tenture')
REG['mur_blason'] = lambda n, d: wall_variant('blason')
REG['mur_ronces'] = lambda n, d: wall_variant('ronces')
REG['mur_niche_oeil'] = lambda n, d: wall_variant('niche_oeil')
REG['mur_niche_vide'] = lambda n, d: wall_variant('niche')
REG['mur_vitrail'] = lambda n, d: wall_variant('vitrail')
REG['mur_rune_grave'] = lambda n, d: wall_variant('rune')


@reg('alcove_sol_rune')
def alcove(n, d):
    t = slab_floor(SOL, 'a', 1)
    R = PAL['rune']
    ring(t, 15.5, 15.5, 8, R[DK], 1)
    ring(t, 15.5, 15.5, 5, R[DK], 1)
    for k in range(6):
        a = k * math.pi / 3
        put(t, round(15.5 + math.cos(a) * 10), round(15.5 + math.sin(a) * 10), R[MD])
    for y in range(11, 21):
        put(t, 15, y, R[MD])
    put(t, 16, 14, R[LT])
    return t


# ------------------------------------------------------------------ bannières, vitrail, colonnes
REG['banniere_morvath'] = lambda n, d: OB.banner('a')
REG['banniere_dechiree'] = lambda n, d: OB.banner('b')


@reg('vitrail_dessus')
def vitrail_dessus(n, d):
    """Reflet coloré projeté sur le mur : points tramés (pas de transparence partielle)."""
    t = blank()
    cols = [PAL['ronce'][HI], PAL['rune'][LT], PAL['rouge'][HI]]
    for y in range(8, 30):
        for x in range(9, 23):
            if abs(x - 15.5) > 3.5 + (y - 8) * 0.18:
                continue
            k = (y - 8) / 22
            if (x + y) % 2 == 0 and rnd(x, y, 4) < 0.85 - k * 0.6:
                t[y][x] = cols[((x - 9) // 5 + (y - 8) // 8) % 3]
    return t


REG['colonne_haut'] = lambda n, d: OB.column_haut()
REG['colonne_base'] = lambda n, d: OB.column_base()
REG['colonne_brisee'] = lambda n, d: OB.column_brisee()

_PIL = OB.pillar()
REG['pilier_hg'] = lambda n, d: slice_(_PIL, 0, 0)
REG['pilier_hd'] = lambda n, d: slice_(_PIL, 1, 0)
REG['pilier_bg'] = lambda n, d: slice_(_PIL, 0, 1)
REG['pilier_bd'] = lambda n, d: slice_(_PIL, 1, 1)

# ------------------------------------------------------------------ cercle des sceaux
_CIR = OB.seal_circle(arene_tex(0))
for _r in range(4):
    for _c in range(4):
        REG[f'cercle_{_r}{_c}'] = (lambda cc, rr: (lambda n, d: slice_(_CIR, cc, rr)))(_c, _r)
