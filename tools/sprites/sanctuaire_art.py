"""Sanctuaire Englouti (donjon 3), dessin final des tuiles : sols, murs, portes, eau, colonnes, bassins, murs fissurés...

Palette : pierre gris-violet (famille de la façade du Sanctuaire dans `lac`), eaux bleu-vert froides, algues vertes, algues lumineuses
turquoise (cryptes), runes cyan, bois mouillé des passerelles, or terni de l'estrade. Lumière en haut à gauche, contour sombre d'1 px.
Chaque tuile est dessinée par REG[nom](nom, d). Les numéros sont ceux du plan (rien ne bouge) ; la crypte est la même planche
recolorée plus sombre + algues lumineuses sur les murs (voir `crypte_px` / `crypt_glow` en bas de fichier).
Aucun pixel semi-transparent, sauf 126 `lueur_bleue`, 137/138 `anneau_ondes` (effets voulus).
"""
import math
import random

from foret import P, Cv, T, rnd, vnoise, wset, rgba
from mine_art import qmask, dist_to_other, bits_of_name

EXTRA = dict(
    fl_hi='#9496b8', fl_lt='#7f81a6', fl_md='#6a6c92', fl_dk='#55577b', fl_dp='#42435f',               # dalles du rez-de-chaussée
    cr_hi='#6c7ea4', cr_lt='#5a6c92', cr_md='#4a5a7e', cr_dk='#3a486a', cr_dp='#2c3856',               # dalles de crypte
    cp_lt='#4e4c6e', cp_md='#3e3c5a', cp_dk='#2e2c46',                                                 # dessus de mur
    wf_hi='#c4c2d8', wf_lt='#a4a2c0', wf_md='#8684a4', wf_dk='#5e5c7c', wf_dp='#46445e',               # face de mur (façade du lac)
    ag_hi='#6ab890', ag_lt='#4a8a6c', ag_md='#2f6a56', ag_dk='#1f4a42',                                # algues
    gl_w='#e0fff0', gl_hi='#8affd8', gl_lt='#4ae8b8', gl_md='#28b890', gl_dk='#1a7a6c',                # algues lumineuses
    rn_hi='#c8f4ff', rn_lt='#8ae0f8', rn_md='#4ac0e8', rn_dk='#2a88c8',                                # runes
    sh_hi='#b4e4ec', sh_lt='#78bcd6', sh_md='#4a90b8', sh_dk='#386c9c', sh_dp='#2c5482',               # eau peu profonde
    dw_lt='#34589a', dw_md='#26437c', dw_dk='#1b3262', dw_dd='#12234a',                                # eau profonde
    wd_hi='#a88260', wd_lt='#8a6444', wd_md='#6c4a34', wd_dk='#4c3326', wd_dd='#34221a',               # planches mouillées
    go_hi='#e0cc90', go_lt='#c4ac6c', go_md='#a08a54', go_dk='#7a6640', go_dp='#584a2e',               # estrade
    cz_hi='#d0cee2', cz_lt='#b0aecb', cz_md='#908eae', cz_dk='#68667f',                                # chaussée
    hl_0='#0e0c1c', hl_1='#181530', hl_2='#242240',                                                    # fond sombre des ouvertures
    sd_y='#d8c8a0', sd_k='#b49c80', sd_p='#d8a8b0',                                                    # coquillages
)
P.update({k: rgba(v) for k, v in EXTRA.items()})
O = P['O']
REG = {}
GLOW = {P[k] for k in ('gl_w', 'gl_hi', 'gl_lt', 'gl_md', 'gl_dk')}
RUNE = {P[k] for k in ('rn_hi', 'rn_lt', 'rn_md', 'rn_dk')}


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


def blank():
    return [[None] * T for _ in range(T)]


def put(t, x, y, c):
    if 0 <= x < len(t[0]) and 0 <= y < len(t):
        t[y][x] = c


def rect(t, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(t, x, y, c)


def copy(t):
    return [row[:] for row in t]


def paste(dst, src, ox=0, oy=0):
    for y, row in enumerate(src):
        for x, c in enumerate(row):
            if c is not None:
                put(dst, x + ox, y + oy, c)


def line(t, pts, c):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(n + 1):
            put(t, round(xa + (xb - xa) * i / n), round(ya + (yb - ya) * i / n), c)


def outline(t, c=None, only_transparent=True):
    c = c or O
    h, w = len(t), len(t[0])
    pts = []
    for y in range(h):
        for x in range(w):
            if t[y][x] is None:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and t[yy][xx] not in (None, c):
                        pts.append((x, y))
                        break
    for x, y in pts:
        t[y][x] = c


# ------------------------------------------------------------------ sols
def base_noise(pal, seed, kind='fl'):
    hi, lt, md, dk = P[kind + '_hi'], P[kind + '_lt'], P[kind + '_md'], P[kind + '_dk']
    t = blank()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, seed) * 0.55 + vnoise(x, y, 16, seed + 5) * 0.45
            c = lt if n > 0.63 else dk if n < 0.34 else md
            r = rnd(x, y, seed + 9)
            if r < 0.04:
                c = dk
            elif r > 0.975:
                c = lt
            t[y][x] = c
    return t


def bond(t, kind='fl', offsets=(0, 16), seed=3):
    """Dalles en appareil décalé : joints sombres, arête éclairée en haut et à gauche."""
    dp, hi = P[kind + '_dp'], P[kind + '_hi']
    for y in range(T):
        row = y // 16
        jx = offsets[row % 2]
        for x in range(T):
            if y % 16 == 0 or x == jx or x == (jx + 32) % 32:
                t[y][x] = dp
            elif (y % 16 == 1 or x == (jx + 1) % 32) and rnd(x, y, seed) < 0.7:
                t[y][x] = hi


def floor_tex(kind):
    t = base_noise(None, 1 + {'a': 0, 'b': 1, 'c': 2}.get(kind, 0))
    if kind in ('a', 'b', 'f', 's', 'g'):
        bond(t)
    if kind == 'c':                                                  # joints irréguliers
        bands = ((0, 10, (6, 22)), (10, 22, (14, 30)), (22, 32, (3, 19)))
        for y0, y1, xs in bands:
            for y in range(y0, y1):
                for x in range(T):
                    if y == y0:
                        t[y][x] = P['fl_dp']
                    elif y == y0 + 1 and rnd(x, y, 2) < 0.65:
                        t[y][x] = P['fl_hi']
                    if x in xs:
                        t[y][x] = P['fl_dp']
                    elif x in ((xs[0] + 1) % 32, (xs[1] + 1) % 32) and rnd(x, y, 4) < 0.6 and y > y0:
                        t[y][x] = P['fl_hi']
    if kind == 'b':                                                  # reflets d'humidité
        r = random.Random(11)
        for _ in range(5):
            x, y = r.randrange(2, 28), r.randrange(2, 30)
            ln = r.choice((2, 3))
            for i in range(ln):
                put(t, x + i, y, P['sh_lt'] if i % 2 == 0 else P['fl_hi'])
            put(t, x + 1, y + 1, P['fl_dk'])
    if kind == 'f':                                                  # fissure en diagonale
        pts = [(2, 3), (7, 8), (10, 8), (14, 14), (13, 17), (19, 21), (23, 25), (28, 30)]
        line(t, pts, P['fl_dp'])
        line(t, [(x + 1, y - 1) for x, y in pts], P['fl_hi'])
        for x, y in ((11, 9), (18, 20), (8, 6), (24, 26)):
            put(t, x, y, P['O'])
    if kind == 's':                                                  # sceau effacé
        cx, cy = 15.5, 15.5
        for y in range(T):
            for x in range(T):
                d = math.hypot(x - cx, y - cy)
                a = math.degrees(math.atan2(y - cy, x - cx))
                worn = rnd(x, y, 17) < 0.28 or vnoise(x, y, 4, 7) < 0.28
                if 11.0 <= d < 12.3 and not worn:
                    t[y][x] = P['fl_dp']
                elif 12.3 <= d < 13.3 and not worn and x >= cx - 4 and y >= cy - 4:
                    t[y][x] = P['fl_hi']
                elif 5 <= d < 6.0 and not worn:
                    t[y][x] = P['fl_dp']
        for k in range(3):                                           # trois branches, effacées par endroits
            ang = math.radians(-90 + k * 120)
            for r in range(6, 12):
                if rnd(r, k, 5) < 0.75:
                    x, y = round(cx + math.cos(ang) * r), round(cy + math.sin(ang) * r)
                    put(t, x, y, P['fl_dp'])
                    put(t, x + 1, y + 1, P['fl_hi'])
    if kind == 'g':                                                  # algues
        for y in range(T):
            for x in range(T):
                n = vnoise(x, y, 8, 31) * 0.6 + vnoise(x, y, 16, 33) * 0.4
                if n > 0.58:
                    t[y][x] = P['ag_lt'] if n > 0.72 else P['ag_md'] if rnd(x, y, 3) < 0.8 else P['ag_dk']
                    if n > 0.8 and rnd(x, y, 5) < 0.5:
                        t[y][x] = P['ag_hi']
                elif n > 0.5 and rnd(x, y, 6) < 0.4:
                    t[y][x] = P['ag_dk']
    return t


FLOOR = floor_tex('a')
for _n, _k in (('dalle_a', 'a'), ('dalle_b', 'b'), ('dalle_c', 'c'), ('dalle_fissuree', 'f'), ('dalle_sceau', 's'), ('dalle_algues', 'g')):
    REG[_n] = (lambda k: (lambda n, d: floor_tex(k)))(_k)


def crypt_tex(kind):
    t = base_noise(None, 40 + 'abcd'.index(kind), 'cr')
    if kind in ('a', 'd'):
        bond(t, 'cr', (8, 24), 12)
    if kind == 'b':                                                  # cailloux
        bond(t, 'cr', (16, 0), 13)
        r = random.Random(5)
        for _ in range(9):
            x, y = r.randrange(1, 29), r.randrange(1, 29)
            put(t, x, y, P['cr_hi'])
            put(t, x + 1, y, P['cr_lt'])
            put(t, x, y + 1, P['cr_dk'])
            put(t, x + 1, y + 1, P['cr_dp'])
    if kind == 'c':                                                  # dalles brisées
        bond(t, 'cr', (10, 26), 14)
        for pts in ([(0, 9), (6, 12), (9, 18), (15, 20)], [(31, 4), (24, 8), (20, 6), (16, 11)], [(20, 24), (24, 28), (30, 29)]):
            line(t, pts, P['cr_dp'])
            line(t, [(x + 1, y - 1) for x, y in pts], P['cr_hi'])
    if kind == 'd':                                                  # algues lumineuses discrètes
        for cx, cy in ((7, 22), (24, 9)):
            for k, (dx, dy) in enumerate(((0, 0), (1, -1), (2, 0), (-1, 1), (1, 1))):
                put(t, cx + dx, cy + dy, P['gl_lt'] if k else P['gl_hi'])
            put(t, cx, cy - 1, P['gl_md'])
            put(t, cx + 1, cy - 2, P['gl_w'])
    return t


for _k in 'abcd':
    REG['crypte_' + _k] = (lambda k: (lambda n, d: crypt_tex(k)))(_k)


# ------------------------------------------------------------------ décors de sol
def tuft(t, x, y, h, lean=0, glow=True, seed=0):
    """Touffe d'algues : lames qui partent de (x, y) vers le haut."""
    hi, lt, md, dk = ((P['gl_w'], P['gl_lt'], P['gl_md'], P['gl_dk']) if glow else (P['ag_hi'], P['ag_lt'], P['ag_md'], P['ag_dk']))
    for k, (dx, hh) in enumerate(((-2, h - 3), (-1, h - 1), (0, h), (1, h - 2), (2, h - 4))):
        for i in range(max(2, hh)):
            xx = x + dx + round(lean * i / max(h, 1) + dx * i * 0.12)
            c = md if i < 2 else lt
            if i >= hh - 1:
                c = hi if glow else lt
            put(t, xx, y - i, c)
            if i == 0:
                put(t, xx, y + 1, dk)


def algae_decor(variant):
    t = blank()
    if variant == 0:
        tuft(t, 9, 22, 9, -2, seed=1)
        tuft(t, 22, 12, 7, 2, seed=2)
        tuft(t, 18, 28, 5, 0, seed=3)
    else:
        tuft(t, 22, 24, 10, 2, seed=4)
        tuft(t, 8, 12, 6, -1, seed=5)
        tuft(t, 13, 29, 4, 0, seed=6)
        tuft(t, 27, 8, 4, 1, seed=7)
    return t


REG['algues_lum_a'] = lambda n, d: algae_decor(0)
REG['algues_lum_b'] = lambda n, d: algae_decor(1)


def shade_tex(kind):
    t = blank()
    for y in range(T):
        for x in range(T):
            dh = 1 - y / 9 if kind in ('haut', 'coin') else 0
            dg = 1 - x / 9 if kind in ('gauche', 'coin') else 0
            k = max(dh, dg)
            if k > 0 and (k > 0.65 or (k > 0.3 and (x + y) % 2 == 0) or (k > 0 and (x + y) % 4 == 0 and (x // 2 + y) % 2 == 0)):
                t[y][x] = (20, 18, 40, 255)
    return t


REG['ombre_mur_haut'] = lambda n, d: shade_tex('haut')
REG['ombre_mur_gauche'] = lambda n, d: shade_tex('gauche')
REG['ombre_mur_coin'] = lambda n, d: shade_tex('coin')


@reg('coquillages')
def coquillages(n, d):
    t = blank()

    def shell(x, y, big):
        r = 3 if big else 2
        for yy in range(-r, r + 1):
            for xx in range(-r - 1, r + 2):
                if (xx / (r + 1)) ** 2 + (yy / r) ** 2 <= 1:
                    c = P['sd_y'] if xx + yy < 0 else P['sd_k']
                    put(t, x + xx, y + yy, c)
        put(t, x, y, P['sd_p'])
        put(t, x + 1, y + 1, P['sd_k'])
        outline_local(t, x - r - 2, y - r - 1, x + r + 2, y + r + 1)

    def pebble(x, y):
        rect(t, x, y, x + 2, y + 1, P['fl_lt'])
        put(t, x, y, P['fl_hi'])
        put(t, x + 2, y + 1, P['fl_dk'])
        outline_local(t, x - 1, y - 1, x + 3, y + 2)
    shell(10, 20, True)
    shell(22, 11, False)
    pebble(20, 24)
    pebble(5, 9)
    pebble(15, 14)
    return t


def outline_local(t, x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < len(t[0]) and 0 <= y < len(t) and t[y][x] is None:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < len(t[0]) and 0 <= yy < len(t) and t[yy][xx] not in (None, O):
                        t[y][x] = O
                        break


# ------------------------------------------------------------------ murs
def cap_color(x, y):
    """Dessus de mur : grandes dalles de 16 px en appareil décalé, bruit doux."""
    n = vnoise(x, y, 8, 5)
    c = P['cp_lt'] if n > 0.72 else P['cp_dk'] if n < 0.25 else P['cp_md']
    jx = 0 if (y // 16) % 2 == 0 else 8
    if y % 16 == 0 or (x - jx) % 16 == 0:
        return P['cp_dk']
    if (y % 16 == 1 or (x - jx) % 16 == 1) and rnd(x, y, 12) < 0.55:
        return P['cp_lt']
    if rnd(x, y, 11) < 0.02:
        return P['cp_lt']
    return c


def face_color(x, y):
    """Face avant : deux assises de pierre taillée, reflet en haut, base mouillée."""
    if y == 17:
        return P['wf_hi']
    if y == 31:
        return O
    if y == 24:
        return P['wf_dp']
    off = 0 if y < 24 else 11
    if (x + off) % 16 == 0 and y not in (18, 25):
        return P['wf_dp']
    if y in (18, 25):
        return P['wf_lt']
    if y in (23, 30):
        return P['wf_dk']
    n = vnoise(x, y, 8, 3)
    if y >= 28 and n < 0.45:
        return P['wf_dk']
    return P['wf_lt'] if n > 0.72 else P['wf_dk'] if n < 0.2 else P['wf_md']


def algae_foot(t, cols=None):
    """Algues au pied de la face (rangées 26 à 30) et quelques gouttes de suintement."""
    for x in range(T):
        r = rnd(x // 2, 3, 77)
        if r < 0.38:
            h = 2 + int(rnd(x, 1, 78) * 4)
            for i in range(h):
                y = 30 - i
                t[y][x] = P['ag_md'] if i < h - 1 else P['ag_lt']
            if rnd(x, 2, 79) < 0.4:
                t[30][x] = P['ag_dk']
    for x in (5, 20, 27):
        for y in (19, 20, 21):
            if rnd(x, y, 80) < 0.7:
                t[y][x] = P['wf_dk']


LIT = ('O', 'wf_hi', 'wf_lt', 'wf_md')
SHD = ('O', 'cp_dk', 'cp_dk', 'cp_md')


def wall(bits, algae=True):
    tl, tr, bl, br = bits
    t = [[cap_color(x, y) for x in range(T)] for y in range(T)]
    n, s = not tl and not tr, not bl and not br
    w, e = not tl and not bl, not tr and not br

    def rc(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t[y][x] = O if c == 'O' else P[c]

    if n:
        for y in range(4):
            rc(0, y, 31, y, LIT[y])
    if w:
        for x in range(4):
            rc(x, 0, x, 31, LIT[x])
        rc(0, 0, 0, 31, 'O')
    if e:
        for k in range(4):
            rc(31 - k, 0, 31 - k, 31, SHD[k])
    if n and w:
        for y in range(4):
            for x in range(4):
                k = LIT[min(x, y)]
                t[y][x] = O if k == 'O' else P[k]
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
        if algae:
            sub = [row[:] for row in t]
            algae_foot(sub)
            for y in range(19, 31):
                for x in range(x0, x1 + 1):
                    t[y][x] = sub[y][x]
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


def full_face(kind):
    """Mur plein vu de face (146 à 149, 145) : deux assises de pierre sur toute la tuile."""
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            yy = y % 16
            off = 0 if y < 16 else 11
            n = vnoise(x, y, 8, 3)
            if yy == 0:
                c = P['wf_dp']
            elif yy == 1:
                c = P['wf_hi'] if yy == 1 and y < 4 else P['wf_lt']
            elif (x + off) % 16 == 0:
                c = P['wf_dp']
            elif yy == 15:
                c = P['wf_dk']
            else:
                c = P['wf_lt'] if n > 0.72 else P['wf_dk'] if n < 0.2 else P['wf_md']
            t[y][x] = c
    for y in range(T):
        t[y][0] = P['wf_dp'] if t[y][0] != P['wf_dp'] else t[y][0]
    if kind == 'rune':
        cx, cy = 15.5, 15.5
        for y in range(T):
            for x in range(T):
                d = math.hypot(x - cx, y - cy)
                if 6.2 <= d < 7.4 and not (11 <= x <= 20 and y < 10):
                    t[y][x] = P['wf_dk']
                    if x < cx and y < cy:
                        t[y][x] = P['wf_dp']
        for y in range(8, 24):                                       # trait vertical + deux branches, à peine plus sombres
            t[y][16] = P['wf_dk']
        for k in range(5):
            t[11 + k][12 - k // 2] = P['wf_dk']
            t[11 + k][20 + k // 2] = P['wf_dk']
    elif kind == 'algues':
        for x in range(T):
            r = rnd(x // 2, 5, 91)
            if r < 0.7:
                h = 6 + int(rnd(x, 2, 92) * 18)
                for i in range(h):
                    t[i][x] = P['ag_md'] if i < h - 2 else P['ag_lt']
                    if rnd(x, i, 93) < 0.12:
                        t[i][x] = P['ag_dk']
    elif kind == 'fresque':
        fresco(t, 3, 4, 28, 27)
    elif kind == 'eau':
        for y in range(16, 32):
            for x in range(T):
                k = (y - 16) / 15
                if k > 0.15 and rnd(x, y, 95) < k * 1.1:
                    t[y][x] = P['dw_md'] if k < 0.6 else P['dw_dk']
                elif k > 0.1:
                    t[y][x] = P['wf_dk']
        for x in range(T):
            if rnd(x, 1, 96) < 0.5:
                t[18 + x % 3][x] = P['sh_lt']
    elif kind == 'lum':
        glow_face(t, 0, 31)
    return t


def fresco(t, x0, y0, x1, y1):
    """Fresque effacée : cadre d'or terni et silhouettes bleutées."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1) or y in (y0, y1)
            if edge:
                t[y][x] = O if (x in (x0, x1) and y in (y0, y1)) else P['go_dk']
            elif x in (x0 + 1, x1 - 1) or y in (y0 + 1, y1 - 1):
                t[y][x] = P['go_md']
            else:
                n = vnoise(x, y, 8, 61)
                t[y][x] = P['wf_md'] if n < 0.5 else P['wf_lt']
    cx = (x0 + x1) // 2
    for dy in range(-3, 4):                                          # silhouette : tête, corps, bras
        for dx in range(-1, 2):
            if abs(dx) + abs(dy) * 0.4 < 2.0 and rnd(cx + dx, dy, 62) < 0.85:
                put(t, cx + dx, (y0 + y1) // 2 + dy - 3, P['rn_dk'] if dy < 0 else P['sh_dp'])
    for x in range(cx - 4, cx + 5):
        for y in range((y0 + y1) // 2 + 1, y1 - 3):
            if abs(x - cx) < 4 - (y - (y0 + y1) // 2) * 0.25 and rnd(x, y, 63) < 0.8:
                put(t, x, y, P['sh_dp'])
    for k in range(7):                                                # usure : éclats clairs
        put(t, x0 + 2 + (k * 7) % (x1 - x0 - 3), y0 + 2 + (k * 5) % (y1 - y0 - 3), P['wf_hi'])


def glow_face(t, y0, y1, density=1.0):
    """Algues lumineuses pendantes ou montantes sur une face de mur."""
    for x in range(1, T - 1):
        r = rnd(x // 2, 9, 101)
        if r < 0.45 * density:
            h = 3 + int(rnd(x, 3, 102) * 8)
            base = y1 - 1
            for i in range(h):
                y = base - i
                c = P['gl_md'] if i < h * 0.4 else P['gl_lt'] if i < h - 1 else P['gl_hi']
                if rnd(x, i, 103) < 0.12:
                    c = P['gl_w']
                put(t, x, y, c)
                if rnd(x, i, 104) < 0.2:
                    put(t, x + 1, y, P['gl_dk'])


for _n, _k in (('mur_rune_grave', 'rune'), ('mur_algues', 'algues'), ('mur_fresque', 'fresque'), ('mur_eau', 'eau'), ('mur_lumineux', 'lum')):
    REG[_n] = (lambda k: (lambda n, d: full_face(k)))(_k)


@reg('fresque_mur')
def fresque_mur(n, d):
    t = blank()
    fresco(t, 4, 18, 27, 30)
    return t


def hang_algae(glow):
    t = blank()
    hi, lt, md, dk = ((P['gl_hi'], P['gl_lt'], P['gl_md'], P['gl_dk']) if glow else (P['ag_hi'], P['ag_lt'], P['ag_md'], P['ag_dk']))
    for x in range(2, 30):
        r = rnd(x // 2, 4, 111)
        if r < 0.55:
            h = 5 + int(rnd(x, 6, 112) * 12)
            for i in range(h):
                y = 17 + i
                c = md if i < h - 3 else lt
                if i == h - 1:
                    c = hi if glow else lt
                if rnd(x, i, 113) < 0.1:
                    c = dk
                put(t, x, y, c)
                if i < 3:
                    put(t, x, y - 0, md)
    outline(t, dk if True else O)
    return t


REG['algues_mur'] = lambda n, d: hang_algae(False)
REG['algues_mur_lum'] = lambda n, d: hang_algae(True)


# ------------------------------------------------------------------ portes (cadre de pierre)
def stone_post(t, x0, x1, y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = P['wf_md']
            if x == x0:
                c = P['wf_hi']
            elif x == x0 + 1:
                c = P['wf_lt']
            elif x == x1:
                c = P['wf_dk']
            if y % 8 == 0 and x not in (x0,):
                c = P['wf_dp']
            t[y][x] = c
    for y in range(y0, y1 + 1):
        put(t, x0 - 1, y, O)
        put(t, x1 + 1, y, O)


def stone_beam(t, x0, x1, y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = P['wf_md']
            if y == y0:
                c = P['wf_hi']
            elif y == y0 + 1:
                c = P['wf_lt']
            elif y == y1:
                c = P['wf_dk']
            if x % 10 == 0 and y not in (y0, y1):
                c = P['wf_dp']
            t[y][x] = c
    for x in range(x0, x1 + 1):
        put(t, x, y0 - 1, O)
        put(t, x, y1 + 1, O)


def dark_floor(t, x0, y0, x1, y1, vertical=True, rev=False):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = ((y1 - y) / max(1, y1 - y0)) if vertical else ((x1 - x) / max(1, x1 - x0))
            if rev:
                k = 1 - k
            c = P['fl_dk'] if k < 0.35 else P['fl_dp'] if k < 0.7 else P['hl_2']
            if k < 0.35 and rnd(x, y, 19) < 0.4:
                c = FLOOR[y][x]
            if k >= 0.7 and rnd(x, y, 20) < 0.3:
                c = P['hl_1']
            t[y][x] = c


@reg('porte_haut')
def porte_haut(n, d):
    t = wall((1, 1, 0, 0), algae=False)
    dark_floor(t, 7, 0, 24, 31, True)
    stone_post(t, 4, 6, 0, 31)
    stone_post(t, 25, 27, 0, 31)
    return t


@reg('porte_bas')
def porte_bas(n, d):
    t = wall((0, 0, 1, 1))
    for y in range(32):
        for x in range(7, 25):
            t[y][x] = P['fl_dk'] if y < 24 else P['fl_dp']
            if rnd(x, y, 21) < 0.3:
                t[y][x] = FLOOR[y][x]
    stone_post(t, 4, 6, 0, 31)
    stone_post(t, 25, 27, 0, 31)
    return t


@reg('porte_gauche')
def porte_gauche(n, d):
    t = wall((1, 0, 1, 0))
    for y in range(4, 28):
        for x in range(0, 32):
            k = x / 31
            t[y][x] = P['hl_1'] if k < 0.25 else P['fl_dp'] if k < 0.5 else P['fl_dk'] if k < 0.8 else FLOOR[y][x]
    stone_beam(t, 0, 31, 0, 3)
    stone_beam(t, 0, 31, 28, 31)
    return t


@reg('porte_droite')
def porte_droite(n, d):
    t = wall((0, 1, 0, 1))
    for y in range(4, 28):
        for x in range(0, 32):
            k = 1 - x / 31
            t[y][x] = P['hl_1'] if k < 0.25 else P['fl_dp'] if k < 0.5 else P['fl_dk'] if k < 0.8 else FLOOR[y][x]
    stone_beam(t, 0, 31, 0, 3)
    stone_beam(t, 0, 31, 28, 31)
    return t


@reg('porte_haut_dessus')
def porte_haut_dessus(n, d):
    t = blank()
    stone_beam(t, 2, 29, 1, 9)
    for x in (6, 25):
        t[5][x] = P['wf_dp']
    for x in range(14, 18):                                          # clef de voûte
        t[5][x] = P['rn_dk']
    t[4][15] = P['rn_lt']
    t[4][16] = P['rn_lt']
    return t


@reg('porte_bas_dessus')
def porte_bas_dessus(n, d):
    t = blank()
    stone_beam(t, 2, 29, 5, 13)
    for x in (6, 25):
        t[9][x] = P['wf_dp']
    for x in range(14, 18):
        t[9][x] = P['rn_dk']
    return t


@reg('porte_gauche_dessus')
def porte_gauche_dessus(n, d):
    t = blank()
    stone_post(t, 2, 9, 0, 31)
    for y in (5, 26):
        t[y][5] = P['wf_dp']
    return t


@reg('porte_droite_dessus')
def porte_droite_dessus(n, d):
    t = blank()
    stone_post(t, 22, 29, 0, 31)
    for y in (5, 26):
        t[y][25] = P['wf_dp']
    return t


# ------------------------------------------------------------------ passerelles et chaussée
def planks(horizontal, end=None):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            a, b = (y, x) if horizontal else (x, y)             # a : travers (largeur de planche), b : le long
            pl = a // 8
            la = a % 8
            lb = (b + (pl % 2) * 13) % 32 if False else (b + pl * 11) % 32
            if la == 0:
                c = P['wd_dd']
            elif la == 1:
                c = P['wd_hi'] if rnd(b, pl, 120) < 0.8 else P['wd_lt']
            elif la == 7:
                c = P['wd_dk']
            else:
                n = vnoise(x, y, 8, 123)
                c = P['wd_lt'] if n > 0.55 else P['wd_md'] if n > 0.25 else P['wd_dk']
                if rnd(b // 3, a, 124) < 0.18:
                    c = P['wd_md']
            if lb in (0,) and la not in (0,):
                c = P['wd_dd']                                      # joint d'about
            elif lb == 1 and la > 1 and la < 7:
                c = P['wd_hi'] if rnd(a, b, 125) < 0.5 else c
            if lb in (4, 17) and la in (3, 4):                      # clous
                c = P['wf_lt'] if (lb == 4) else P['wf_dk']
            if horizontal:
                t[y][x] = c
            else:
                t[y][x] = c
    if end:
        beam_cross(t, horizontal, end)
    return t


def beam_cross(t, horizontal, end):
    """Extrémité : traverse épaisse + poteaux, sur le bord extérieur (g, d, haut, bas)."""
    if end in ('g', 'd'):
        x0, x1 = (0, 4) if end == 'g' else (27, 31)
        for y in range(T):
            for x in range(x0, x1 + 1):
                c = P['wd_md']
                if x == (x0 if end == 'g' else x0 + 1):
                    c = P['wd_hi']
                if x == x1 or (end == 'd' and x == x0):
                    c = P['wd_dk']
                t[y][x] = c
        for y in (2, 3, 4, 27, 28, 29):                              # poteaux
            for x in range(x0 - (1 if end == 'd' else 0), x1 + 1 + (0 if end == 'd' else 1)):
                if 0 <= x < T:
                    t[y][x] = P['wd_hi'] if y in (2, 27) else P['wd_lt'] if y in (3, 28) else P['wd_dk']
        for y in (1, 5, 26, 30):
            for x in range(max(0, x0 - 1), min(T, x1 + 2)):
                t[y][x] = O
    else:
        y0, y1 = (0, 4) if end == 'haut' else (27, 31)
        for x in range(T):
            for y in range(y0, y1 + 1):
                c = P['wd_md']
                if y == (y0 if end == 'haut' else y0 + 1):
                    c = P['wd_hi']
                if y == y1 or (end == 'bas' and y == y0):
                    c = P['wd_dk']
                t[y][x] = c
        for x in (2, 3, 4, 27, 28, 29):
            for y in range(max(0, y0 - (1 if end == 'bas' else 0)), min(T, y1 + 1 + (0 if end == 'bas' else 1))):
                t[y][x] = P['wd_hi'] if x in (2, 27) else P['wd_lt'] if x in (3, 28) else P['wd_dk']
        for x in (1, 5, 26, 30):
            for y in range(max(0, y0 - 1), min(T, y1 + 2)):
                t[y][x] = O


REG['planches_h'] = lambda n, d: planks(True)
REG['planches_v'] = lambda n, d: planks(False)
REG['planches_h_g'] = lambda n, d: planks(True, 'g')
REG['planches_h_d'] = lambda n, d: planks(True, 'd')
REG['planches_v_haut'] = lambda n, d: planks(False, 'haut')
REG['planches_v_bas'] = lambda n, d: planks(False, 'bas')


def causeway(worn):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 71 + worn) * 0.6 + rnd(x, y, 72) * 0.4
            c = P['cz_lt'] if n > 0.6 else P['cz_dk'] if n < 0.25 else P['cz_md']
            yy = y % 16
            off = 0 if y < 16 else 16
            if yy == 0 or (x + off) % 32 == 0:
                c = P['wf_dk']
            elif yy == 1 or (x + off) % 32 == 1:
                c = P['cz_hi']
            t[y][x] = c
    if worn:
        line(t, [(5, 3), (9, 8), (8, 12)], P['wf_dp'])
        line(t, [(22, 20), (19, 24), (21, 29)], P['wf_dp'])
        for x, y in ((24, 6), (12, 22), (27, 12)):
            for dx, dy in ((0, 0), (1, 0), (0, 1)):
                put(t, x + dx, y + dy, P['ag_md'])
            put(t, x, y, P['ag_lt'])
    else:
        for x, y in ((8, 8), (24, 24)):
            put(t, x, y, P['cz_hi'])
            put(t, x + 1, y, P['cz_hi'])
    return t


REG['chaussee_pierre'] = lambda n, d: causeway(0)
REG['chaussee_pierre_b'] = lambda n, d: causeway(1)


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
                if y - y0 < 3:
                    if up:
                        c = [P['wf_dk'], P['wf_md'], P['wf_lt'], P['wf_lt'], P['wf_hi'], P['wf_hi']][i]
                    else:
                        c = [P['wf_hi'], P['wf_lt'], P['wf_md'], P['wf_dk'], P['wf_dp'], P['hl_2']][i]
                    if y == y0 and 5 < x < 26:
                        c = P['wf_hi'] if i < 4 or up else c
                else:
                    c = P['wf_dp'] if not up else P['wf_dk']
                    if i == steps - 1 and y - y0 >= 3:
                        c = P['hl_1']
                t[y][x] = c
    if not up:                                                       # marches du bas noyées
        for y in range(22, 31):
            for x in range(6, 26):
                if rnd(x, y, 131) < (y - 21) / 9 * 0.8:
                    t[y][x] = P['dw_md'] if y > 26 else P['sh_dp']
        for x in range(6, 26):
            if rnd(x, 1, 132) < 0.5:
                t[21 + x % 2][x] = P['sh_lt']
    for y in range(T):
        for x in list(range(0, 5)) + list(range(27, 32)):
            t[y][x] = cap_color(x, y)
        t[y][4] = P['cp_dk']
        t[y][27] = P['cp_dk']
        t[y][5] = O
        t[y][26] = O
    for x in range(5, 27):
        t[1][x] = O
        t[0][x] = P['hl_1'] if not up else P['wf_dp']
    return t


REG['escalier_montant'] = lambda n, d: stairs(True)
REG['escalier_descendant'] = lambda n, d: stairs(False)


# ------------------------------------------------------------------ balcon
def balcon(side):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            if y < 21:                                              # dessus de la plate-forme, éclairé
                n = vnoise(x, y, 8, 81) * 0.6 + rnd(x, y, 82) * 0.4
                c = P['wf_lt'] if n > 0.62 else P['wf_md'] if n > 0.25 else P['wf_dk']
                if y == 0:
                    c = P['wf_hi']
                elif y == 20:
                    c = P['wf_dk']
                if y % 10 == 9 and y < 20 or x % 16 == 7 and y < 20 and y % 10 > 0:
                    c = P['wf_dp']
                elif (y % 10 == 0 and y > 0) and y < 20:
                    c = P['wf_hi'] if rnd(x, y, 83) < 0.7 else c
            else:                                                    # face avant sombre
                n = vnoise(x, y, 8, 84) * 0.6 + rnd(x, y, 85) * 0.4
                c = P['wf_dk'] if n > 0.4 else P['wf_dp']
                if y == 21:
                    c = P['wf_dp']
                if (x + 9) % 16 == 0:
                    c = P['wf_dp']
                if y >= 28 and rnd(x, y, 86) < 0.5:
                    c = P['dw_md']
                if y == 31:
                    c = O
            t[y][x] = c
    for x in range(T):
        if rnd(x, 0, 87) < 0.3:                                      # algues qui pendent sur la face
            for i in range(2 + int(rnd(x, 1, 88) * 5)):
                t[22 + i][x] = P['ag_md'] if i < 3 else P['ag_dk']
    if side == 'g':
        for y in range(32):
            t[y][0] = O
            if y < 21:
                t[y][1] = P['wf_hi']
    if side == 'd':
        for y in range(32):
            t[y][31] = O
            if y < 21:
                t[y][30] = P['wf_dk']
    return t


REG['balcon_g'] = lambda n, d: balcon('g')
REG['balcon_m'] = lambda n, d: balcon('m')
REG['balcon_d'] = lambda n, d: balcon('d')


@reg('balcon_garde_corps')
def garde_corps(n, d):
    t = blank()
    for x in range(T):                                               # lisse haute
        for y in range(9, 15):
            c = P['wf_md']
            if y == 9:
                c = P['wf_hi']
            elif y == 10:
                c = P['wf_lt']
            elif y == 14:
                c = P['wf_dk']
            t[y][x] = c
    for x0 in (2, 10, 18, 26):                                       # balustres
        for y in range(15, 27):
            w = 4 - (1 if 19 < y < 24 else 0)
            for x in range(x0, x0 + 4):
                if y in (19, 20) and x in (x0, x0 + 3):
                    continue
                t[y][x] = P['wf_hi'] if x == x0 else P['wf_lt'] if x == x0 + 1 else P['wf_dk'] if x == x0 + 3 else P['wf_md']
    for x in range(T):                                               # lisse basse
        for y in range(27, 30):
            t[y][x] = P['wf_lt'] if y == 27 else P['wf_md'] if y == 28 else P['wf_dk']
    outline(t)
    return t


@reg('balcon_ombre')
def balcon_ombre(n, d):
    t = blank()
    for y in range(T):
        for x in range(T):
            k = 1 - y / 14
            if k > 0 and (k > 0.6 or ((x + y) % 2 == 0 and k > 0.25)):
                t[y][x] = (12, 22, 52, 255)
    return t


# ------------------------------------------------------------------ murs fissurés
def crack_line(t, pts, hi_side=True):
    line(t, pts, O)
    line(t, [(x + 1, y) for x, y in pts], P['wf_dp'])
    if hi_side:
        line(t, [(x - 1, y) for x, y in pts], P['wf_hi'])


def cracked(side):
    if side == 'haut':
        t = wall((1, 1, 0, 0))
        pts = [(12, 17), (14, 20), (13, 23), (17, 26), (16, 29), (19, 31)]
        crack_line(t, pts)
        crack_line(t, [(13, 22), (9, 24), (7, 27)])
        crack_line(t, [(17, 26), (22, 25), (25, 28)])
        for x, y in ((9, 21), (20, 22), (22, 29), (10, 28), (15, 19)):  # éclats
            t[y][x] = P['wf_hi']
    elif side == 'bas':
        t = wall((0, 0, 1, 1))
        crack_line(t, [(10, 4), (13, 8), (12, 12), (16, 16), (15, 22), (18, 27), (17, 31)])
        crack_line(t, [(12, 12), (7, 15), (5, 20)])
        crack_line(t, [(16, 16), (22, 18), (26, 23)])
        for x, y in ((9, 9), (20, 14), (21, 24), (11, 20)):
            t[y][x] = P['cp_lt']
    elif side == 'gauche':
        t = wall((1, 0, 1, 0))
        crack_line(t, [(4, 8), (8, 11), (12, 10), (15, 14), (20, 13), (24, 17), (28, 16), (31, 20)])
        crack_line(t, [(15, 14), (14, 20), (17, 25)])
        for x, y in ((9, 15), (18, 18), (23, 10), (26, 22)):
            t[y][x] = P['cp_lt']
    else:
        t = wall((0, 1, 0, 1))
        crack_line(t, [(0, 16), (4, 15), (8, 19), (12, 18), (16, 22), (20, 21), (24, 24), (27, 23)])
        crack_line(t, [(16, 22), (15, 28), (18, 31)])
        for x, y in ((6, 11), (14, 12), (20, 27), (9, 25)):
            t[y][x] = P['cp_lt']
    return t


for _s in ('haut', 'bas', 'gauche', 'droite'):
    REG['mur_fissure_' + _s] = (lambda s: (lambda n, d: cracked(s)))(_s)


def rubble(t, cells, seed):
    """Gravats : blocs de pierre éclairés en haut à gauche avec contour."""
    r = random.Random(seed)
    for cx, cy, rx, ry in cells:
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                dd = ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2
                if dd <= 1:
                    k = (x - cx) / (rx + 0.5) + (y - cy) / (ry + 0.5)
                    c = P['wf_hi'] if k < -0.9 else P['wf_lt'] if k < -0.2 else P['wf_md'] if k < 0.6 else P['wf_dk']
                    put(t, x, y, c)
        for y in range(cy - ry - 1, cy + ry + 2):
            for x in range(cx - rx - 1, cx + rx + 2):
                if 0 <= x < T and 0 <= y < T:
                    dd = ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2
                    if 1 < dd <= 1.6 and t[y][x] not in (P['wf_hi'], P['wf_lt'], P['wf_md'], P['wf_dk']):
                        t[y][x] = O
    for _ in range(6):
        put(t, r.randrange(2, 30), r.randrange(2, 30), P['wf_lt'])


def jagged(a, b, amp, seed):
    """Bord irrégulier : valeur entière entre a et b +/- amp, pour chaque indice."""
    return [round(a + (b - a) * 0 + (rnd(i, 0, seed) - 0.5) * 2 * amp) for i in range(T)]


def opened(side):
    if side == 'haut':
        t = wall((1, 1, 0, 0))
        j = [(rnd(y, 3, 141) - 0.5) * 3 for y in range(T)]
        for y in range(0, 32):
            xl, xr = round(7 + j[y]), round(24 + j[(y + 7) % 32])
            for x in range(xl, xr + 1):
                k = (31 - y) / 31
                t[y][x] = P['hl_2'] if k > 0.7 and rnd(x, y, 142) > 0.2 else P['hl_1'] if k > 0.35 else P['hl_0']
                if y > 22:
                    t[y][x] = P['fl_dp'] if rnd(x, y, 143) < 0.5 else P['fl_dk']
            t[y][xl - 1] = O
            t[y][xr + 1] = O
            for x in range(xl - 3, xl - 1):
                if t[y][x] in (P['wf_md'], P['wf_lt'], P['wf_hi'], P['wf_dk']):
                    t[y][x] = P['wf_dk']
        for x in range(8, 24):                                       # linteau éclaté
            for y in range(0, 4):
                t[y][x] = P['hl_0'] if rnd(x, y, 144) < 0.6 else P['cp_dk']
        rubble(t, [(11, 28, 3, 2), (19, 29, 4, 2), (15, 26, 2, 1), (24, 27, 2, 2), (7, 29, 2, 1)], 5)
    elif side == 'bas':
        t = wall((0, 0, 1, 1))
        for y in range(4, 32):
            xl = round(7 + (rnd(y, 4, 145) - 0.5) * 3)
            xr = round(24 + (rnd(y, 5, 146) - 0.5) * 3)
            for x in range(xl, xr + 1):
                k = (y - 4) / 27
                t[y][x] = P['hl_0'] if k > 0.2 else P['hl_1']
            t[y][xl - 1] = O
            t[y][xr + 1] = O
        for x in range(7, 25):
            t[4][x] = P['wf_dp']
        rubble(t, [(12, 6, 3, 2), (19, 5, 4, 2), (16, 3, 2, 1), (9, 8, 2, 1), (23, 8, 2, 2)], 6)
    elif side == 'gauche':
        t = wall((1, 0, 1, 0))
        for x in range(0, 32):
            yl = round(5 + (rnd(x, 6, 147) - 0.5) * 3)
            yh = round(26 + (rnd(x, 7, 148) - 0.5) * 3)
            for y in range(yl, yh + 1):
                k = 1 - x / 31
                t[y][x] = P['hl_0'] if k > 0.5 else P['hl_1'] if k > 0.25 else P['fl_dp']
                if x > 24:
                    t[y][x] = P['fl_dp'] if rnd(x, y, 149) < 0.5 else P['fl_dk']
            t[yl - 1][x] = O
            t[yh + 1][x] = O
        rubble(t, [(26, 14, 3, 3), (28, 21, 3, 2), (22, 18, 2, 2), (29, 9, 2, 2), (24, 24, 2, 1)], 7)
    else:
        t = wall((0, 1, 0, 1))
        for x in range(0, 32):
            yl = round(5 + (rnd(x, 8, 150) - 0.5) * 3)
            yh = round(26 + (rnd(x, 9, 151) - 0.5) * 3)
            for y in range(yl, yh + 1):
                k = x / 31
                t[y][x] = P['hl_0'] if k > 0.5 else P['hl_1'] if k > 0.25 else P['fl_dp']
                if x < 7:
                    t[y][x] = P['fl_dp'] if rnd(x, y, 152) < 0.5 else P['fl_dk']
            t[yl - 1][x] = O
            t[yh + 1][x] = O
        rubble(t, [(5, 14, 3, 3), (3, 21, 3, 2), (9, 18, 2, 2), (2, 9, 2, 2), (7, 24, 2, 1)], 8)
    return t


for _s in ('haut', 'bas', 'gauche', 'droite'):
    REG[f'mur_fissure_{_s}_ouvert'] = (lambda s: (lambda n, d: opened(s)))(_s)


# ------------------------------------------------------------------ eau
def water_tex(deep, seed=21, streaks=False):
    if deep:
        base, dk, lt = P['dw_md'], P['dw_dk'], P['dw_lt']
    else:
        base, dk, lt = P['sh_md'], P['sh_dk'], P['sh_lt']
    t = [[base] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, seed) * 0.6 + vnoise(x, y, 16, seed + 2) * 0.4
            if n < 0.32:
                t[y][x] = dk
            elif n > 0.7 and (x + y) % 2 == 0 and not deep:
                t[y][x] = P['sh_lt']
    r = random.Random(seed)
    for _ in range(5 if deep else 8):
        x, y = r.randrange(T), r.randrange(T)
        ln = r.choice((3, 4, 5))
        for i in range(ln):
            wset(t, x + i, y, lt if deep else P['sh_hi'])
        wset(t, x - 1, y + 1, lt)
        wset(t, x + ln, y - 1, lt)
    if streaks:
        for _ in range(4):
            x, y = r.randrange(T), r.randrange(T)
            for i in range(7):
                wset(t, x + i, y, P['sh_hi'] if not deep else P['dw_lt'])
            wset(t, x + 2, y + 1, P['sh_lt'] if not deep else P['dw_md'])
    return t


SHALLOW = water_tex(False)
DEEPT = water_tex(True, 31)


@reg('eau', 'eau_bord_haut', 'eau_bord_bas', 'eau_bord_gauche', 'eau_bord_droite', 'eau_creux_hg', 'eau_creux_hd', 'eau_creux_bg',
     'eau_creux_bd', 'eau_coin_hg', 'eau_coin_hd', 'eau_coin_bg', 'eau_coin_bd')
def eau(n, d):
    b = bits_of_name(d)
    if b == 15:
        return [row[:] for row in SHALLOW]
    m = qmask(b, 41, 0.055)
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            dd = dist_to_other(m, x, y, 3)
            if m[y][x]:
                c = SHALLOW[y][x]
                if dd <= 1:
                    c = P['sh_hi'] if rnd(x, y, 7) < 0.75 else P['gl_w'] if False else P['sh_lt']
                elif dd == 2 and rnd(x, y, 8) < 0.4:
                    c = P['sh_lt']
                t[y][x] = c
            else:
                c = FLOOR[y][x]
                if dd <= 1:
                    c = P['fl_dp']
                elif dd == 2:
                    c = P['fl_dk']
                t[y][x] = c
    return t


@reg('eau_dalles_a', 'eau_dalles_b')
def eau_dalles(n, d):
    t = [row[:] for row in SHALLOW]
    spots = ([(3, 5, 12, 9), (19, 17, 11, 10)] if n.endswith('_a') else [(15, 2, 12, 8), (3, 18, 10, 10)])
    for x0, y0, w, h in spots:                                       # dalles de pierre affleurantes
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                c = P['fl_md']
                if y == y0 or x == x0:
                    c = P['fl_hi']
                elif y == y0 + h - 1 or x == x0 + w - 1:
                    c = P['fl_dk']
                elif rnd(x, y, 160) < 0.25:
                    c = P['fl_lt']
                t[y][x] = c
        for x in range(x0 - 1, x0 + w + 1):
            for y in (y0 - 1, y0 + h):
                put(t, x, y, P['sh_dp'])
        for y in range(y0 - 1, y0 + h + 1):
            for x in (x0 - 1, x0 + w):
                put(t, x, y, P['sh_dp'])
        for x in range(x0, x0 + w):                                  # écume le long du bas
            if rnd(x, 3, 161) < 0.6:
                put(t, x, y0 + h + 1, P['sh_hi'])
    return t


REG['eau_reflets'] = lambda n, d: water_tex(False, 21, True)


@reg(*[f'eau_profonde{s}' for s in ('', '_bord_haut', '_bord_bas', '_bord_gauche', '_bord_droite', '_creux_hg', '_creux_hd', '_creux_bg',
                                    '_creux_bd', '_coin_hg', '_coin_hd', '_coin_bg', '_coin_bd', '_diag_a', '_diag_b')])
def eau_profonde(n, d):
    b = bits_of_name(d)
    if b == 15:
        return [row[:] for row in DEEPT]
    m = qmask(b, 51, 0.03)
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            dd = dist_to_other(m, x, y, 3)
            if m[y][x]:
                c = DEEPT[y][x]
                if dd <= 1:
                    c = P['dw_dd']
                elif dd == 2 and rnd(x, y, 9) < 0.5:
                    c = P['dw_dk']
                t[y][x] = c
            else:
                c = FLOOR[y][x]
                if dd <= 1:
                    c = O
                elif dd == 2:
                    c = P['fl_dp']
                elif dd == 3 and rnd(x, y, 10) < 0.4:
                    c = P['fl_dk']
                t[y][x] = c
    for y in range(T):                                               # lèvre éclairée au-dessus de l'eau
        for x in range(T):
            if not m[y][x] and dist_to_other(m, x, y, 3) == 2 and y + 1 < T and m[min(T - 1, y + 2)][x]:
                t[y][x] = P['fl_hi']
    return t


REG['eau_profonde_b'] = lambda n, d: water_tex(True, 33, True)


# ------------------------------------------------------------------ colonnes, vasque, statue
def column_shaft(t, y0, y1, x0=9, x1=22):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            c = P['wf_hi'] if u < 0.14 else P['wf_lt'] if u < 0.42 else P['wf_md'] if u < 0.72 else P['wf_dk'] if u < 0.92 else P['wf_dp']
            if (y % 11 == 5) and 0.1 < u < 0.95:
                c = P['wf_dk'] if u < 0.7 else P['wf_dp']
            t[y][x] = c
    for y in range(y0, y1 + 1):
        put(t, x0 - 1, y, O)
        put(t, x1 + 1, y, O)


def band(t, x0, x1, y0, y1, hi='wf_hi', lt='wf_lt', md='wf_md', dk='wf_dk'):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) / max(1, x1 - x0)
            c = P[hi] if y == y0 else P[dk] if y == y1 else P[lt] if u < 0.25 else P[md] if u < 0.75 else P[dk]
            t[y][x] = c
    for x in range(x0 - 1, x1 + 2):
        put(t, x, y0 - 1, O)
        put(t, x, y1 + 1, O)
    for y in range(y0, y1 + 1):
        put(t, x0 - 1, y, O)
        put(t, x1 + 1, y, O)


@reg('colonne_haut')
def colonne_haut(n, d):
    t = blank()
    column_shaft(t, 11, 31)
    band(t, 5, 26, 3, 7)                                             # chapiteau
    band(t, 7, 24, 8, 10, 'wf_lt', 'wf_md', 'wf_dk', 'wf_dp')
    for x in (9, 15, 21):
        put(t, x, 5, P['wf_dp'])
    return t


@reg('colonne_base')
def colonne_base(n, d):
    t = blank()
    column_shaft(t, 0, 19)
    band(t, 5, 26, 20, 23, 'wf_hi', 'wf_lt', 'wf_md', 'wf_dk')
    band(t, 3, 28, 24, 28, 'wf_lt', 'wf_md', 'wf_dk', 'wf_dp')
    for x in range(1, 31):                                           # clapotis au pied
        if rnd(x, 1, 171) < 0.45:
            put(t, x, 30 + x % 2, P['sh_lt'] if x % 3 else P['sh_hi'])
    for x in range(4, 28):
        if rnd(x, 2, 172) < 0.2:
            put(t, x, 29, P['ag_md'])
    return t


@reg('colonne_brisee')
def colonne_brisee(n, d):
    t = blank()
    # tronc : ellipse de pierre, dessus irrégulier, éclats au pied
    for y in range(8, 28):
        for x in range(6, 26):
            top = 9 + round((rnd(x, 0, 173) - 0.5) * 5) + (3 if x > 17 else 0)
            if y < top:
                continue
            u = (x - 6) / 19
            c = P['wf_hi'] if u < 0.14 else P['wf_lt'] if u < 0.42 else P['wf_md'] if u < 0.72 else P['wf_dk']
            if y == top:
                c = P['wf_hi']
            elif y == top + 1 and u > 0.3:
                c = P['wf_lt']
            if y % 11 == 6:
                c = P['wf_dp']
            t[y][x] = c
    for x in range(8, 24):                                           # cassure : dessus plat sombre
        t[9 + (x % 3)][x] = t[9 + (x % 3)][x] or P['wf_hi']
    rubble(t, [(5, 27, 3, 2), (26, 28, 3, 1), (13, 29, 2, 1)], 9)
    for x in range(8, 24):
        put(t, x, 28, P['sh_lt'] if x % 2 else P['sh_md'])
    outline(t)
    return t


@reg('vasque')
def vasque(n, d):
    t = blank()
    # pied
    band(t, 11, 20, 20, 27, 'wf_lt', 'wf_md', 'wf_dk', 'wf_dp')
    band(t, 7, 24, 27, 29, 'wf_lt', 'wf_md', 'wf_dk', 'wf_dp')
    # coupe : ellipse vue de dessus
    cx, cy = 16, 13
    for y in range(4, 23):
        for x in range(3, 29):
            dd = ((x + 0.5 - cx) / 13) ** 2 + ((y + 0.5 - cy) / 8) ** 2
            if dd <= 1:
                inner = dd <= 0.5
                if inner:
                    c = P['sh_md'] if (x + y) % 5 else P['sh_hi']
                    if y < cy - 2:
                        c = P['sh_dp']
                else:
                    c = P['wf_hi'] if (x < cx and y < cy) else P['wf_lt'] if y < cy + 3 else P['wf_dk']
                t[y][x] = c
    for y in range(4, 24):                                           # tranche de la coupe
        for x in range(3, 29):
            if t[y][x] is None and t[y - 1][x] is not None and (((x + 0.5 - cx) / 13) ** 2 + ((y - 3 + 0.5 - cy) / 8) ** 2) <= 1:
                t[y][x] = P['wf_dk'] if y < 22 else P['wf_dp']
    outline(t)
    return t


@reg('statue_brisee')
def statue_brisee(n, d):
    t = blank()
    band(t, 5, 26, 24, 29, 'wf_lt', 'wf_md', 'wf_dk', 'wf_dp')      # socle
    band(t, 8, 23, 20, 23, 'wf_hi', 'wf_lt', 'wf_md', 'wf_dk')
    # corps drapé, sans tête, un bras cassé
    for y in range(9, 20):
        half = 6 + (y - 9) // 3
        for x in range(16 - half, 16 + half):
            u = (x - (16 - half)) / (2 * half)
            c = P['wf_hi'] if u < 0.18 else P['wf_lt'] if u < 0.45 else P['wf_md'] if u < 0.75 else P['wf_dk']
            if (x + y) % 7 == 0 and 0.2 < u < 0.9:
                c = P['wf_dk']
            t[y][x] = c
    for y in range(6, 9):                                            # moignon de cou et épaules
        for x in range(12, 20):
            t[y][x] = P['wf_lt'] if x < 15 else P['wf_md'] if x < 18 else P['wf_dk']
    for x in range(12, 20):
        put(t, x, 7 + (x % 3 == 0), P['wf_hi'])
    for y in range(11, 17):                                          # bras gauche manquant : cassure
        for x in range(7, 10):
            t[y][x] = None
    for x in range(8, 11):
        put(t, x, 12 + x % 2, P['wf_hi'])
    for k in range(5):                                               # lance brisée de bronze doré
        put(t, 23, 10 + k, P['go_md'])
        put(t, 24, 10 + k, P['go_dk'])
    for y in range(10, 19):
        t[y][11] = t[y][11] if t[y][11] else P['wf_lt']
    for x, y in ((9, 22), (21, 22), (14, 22)):
        put(t, x, y, P['ag_md'])
    outline(t)
    return t


# ------------------------------------------------------------------ piliers 2x2 et bassins 3x3 : grands canevas découpés
def pillar():
    W = 64
    t = [[None] * W for _ in range(W)]
    x0, x1, ytop, yfront, ybot = 3, 61, 3, 42, 62
    for y in range(ytop, ybot + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            if y < yfront:                                           # dessus du pilier : dalle
                n = vnoise(x % 32, y % 32, 8, 91) * 0.6 + rnd(x, y, 92) * 0.4
                c = P['wf_lt'] if n > 0.55 else P['wf_md']
                if y == ytop or x == x0:
                    c = P['wf_hi']
                elif y == yfront - 1 or x == x1:
                    c = P['wf_dk']
                dd = max(abs(x - 32) / 24, abs(y - 22) / 15)
                if 0.78 < dd < 0.88:
                    c = P['wf_dk'] if (x + y) % 2 == 0 else P['wf_md']
            else:                                                    # face avant : fût cannelé
                c = P['wf_hi'] if u < 0.05 else P['wf_lt'] if u < 0.3 else P['wf_md'] if u < 0.65 else P['wf_dk'] if u < 0.93 else P['wf_dp']
                if (x - x0) % 8 == 0:
                    c = P['wf_dp'] if u > 0.3 else P['wf_dk']
                if y == yfront:
                    c = P['wf_dp']
                if y >= 58:
                    c = P['wf_dk'] if (x + y) % 3 else P['dw_md']
            t[y][x] = c
    # rune au centre du dessus
    for y in range(7, 38):
        for x in range(12, 53):
            d = math.hypot((x - 32) / 1.15, (y - 22) / 0.75)
            if 8.5 <= d < 9.5:
                t[y][x] = P['rn_dk'] if rnd(x, y, 93) < 0.8 else P['wf_md']
    for y in range(14, 31):
        t[y][32] = P['rn_dk']
    for k in range(5):
        put(t, 32, 22, P['rn_lt'])
    # algues au pied
    for x in range(x0 + 1, x1):
        if rnd(x // 2, 9, 94) < 0.45:
            h = 2 + int(rnd(x, 3, 95) * 5)
            for i in range(h):
                put(t, x, ybot - 1 - i, P['ag_md'] if i < h - 1 else P['ag_lt'])
    for x in range(x0, x1 + 1):
        put(t, x, ybot + 1 if ybot + 1 < W else ybot, O)
    for y in range(ytop, ybot + 1):
        put(t, x0 - 1, y, O)
        put(t, x1 + 1, y, O)
    for x in range(x0 - 1, x1 + 2):
        put(t, x, ytop - 1, O)
    return t


PILLAR = pillar()
for _n, (_ox, _oy) in (('pilier_hg', (0, 0)), ('pilier_hd', (32, 0)), ('pilier_bg', (0, 32)), ('pilier_bd', (32, 32))):
    REG[_n] = (lambda ox, oy: (lambda n, d: [row[ox:ox + 32] for row in PILLAR[oy:oy + 32]]))(_ox, _oy)


def basin():
    W = 96
    t = [[None] * W for _ in range(W)]
    cx = cy = 47.5
    for y in range(W):
        for x in range(W):
            t[y][x] = FLOOR[y % 32][x % 32]
    for y in range(W):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if d <= 45:
                if d <= 36:                                         # eau
                    c = SHALLOW[y % 32][x % 32]
                    if 34 <= d <= 36:
                        c = P['sh_dp']
                    if 30 <= d < 34 and rnd(x, y, 181) < 0.25:
                        c = P['sh_dk']
                    if d < 9 or (d > 12 and d < 13.2 and rnd(x, y, 182) < 0.8) or (d > 19 and d < 20 and rnd(x, y, 183) < 0.5):
                        c = P['sh_hi'] if d > 9 else P['sh_lt']
                else:                                               # margelle
                    a = math.degrees(math.atan2(y - cy, x - cx))
                    u = (d - 36) / 9
                    c = P['wf_hi'] if u < 0.2 and (x < cx or y < cy) else P['wf_lt'] if u < 0.5 else P['wf_md'] if u < 0.8 else P['wf_dk']
                    if abs((a % 20) - 10) < 0.8:                     # joints rayonnants
                        c = P['wf_dp']
                    if x > cx and y > cy and u > 0.5:
                        c = P['wf_dk']
                t[y][x] = c
    for y in range(W):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if 45 < d <= 46.3:
                t[y][x] = O
            elif 36 < d <= 37 and False:
                t[y][x] = O
    # ombre portée de la margelle sur le sol (bas-droite)
    for y in range(W):
        for x in range(W):
            d = math.hypot(x - cx - 1.5, y - cy - 1.5)
            if 46.3 < math.hypot(x - cx, y - cy) and d <= 47.8 and x > cx and y > cy and (x + y) % 2 == 0:
                t[y][x] = P['fl_dp']
    return t


BASIN = basin()
for _k, _n in enumerate(('hg', 'h', 'hd', 'g', 'c', 'd', 'bg', 'b', 'bd')):
    REG[f'bassin_{_n}'] = (lambda ox, oy: (lambda n, d: [row[ox:ox + 32] for row in BASIN[oy:oy + 32]]))((_k % 3) * 32, (_k // 3) * 32)


def ring(r0, r1, alpha):
    t = blank()
    for y in range(T):
        for x in range(T):
            d = math.hypot(x - 15.5, (y - 15.5) * 1.25)
            if r0 <= d < r0 + 1.2:
                t[y][x] = (200, 245, 255, alpha)
            elif r1 <= d < r1 + 1.2 and rnd(x, y, 191) < 0.6:
                t[y][x] = (138, 224, 248, alpha)
    return t


REG['anneau_ondes_a'] = lambda n, d: ring(5, 9, 200)
REG['anneau_ondes_b'] = lambda n, d: ring(9, 13.5, 170)


@reg('lueur_bleue')
def lueur_bleue(n, d):
    t = blank()
    for y in range(T):
        for x in range(T):
            dd = math.hypot((x - 15.5) / 13, (y - 15.5) / 10)
            if dd < 1:
                a = 70 if dd > 0.66 else 110 if dd > 0.33 else 150
                t[y][x] = (138, 224, 248, a)
    return t


@reg('debris')
def debris(n, d):
    t = blank()
    rubble(t, [(10, 22, 4, 3), (20, 24, 5, 3), (15, 18, 3, 2), (25, 17, 2, 2), (6, 14, 2, 2)], 12)
    for x in range(4, 28):
        if rnd(x, 4, 195) < 0.25:
            put(t, x, 28 + x % 2, P['sh_lt'])
    return t


@reg('piedestal')
def piedestal(n, d):
    t = blank()
    band(t, 4, 27, 24, 29, 'wf_lt', 'wf_md', 'wf_dk', 'wf_dp')
    for y in range(13, 24):
        for x in range(7, 25):
            u = (x - 7) / 17
            c = P['wf_lt'] if u < 0.2 else P['wf_md'] if u < 0.7 else P['wf_dk']
            if y == 13:
                c = P['wf_hi']
            t[y][x] = c
    band(t, 5, 26, 9, 13, 'wf_hi', 'wf_lt', 'wf_md', 'wf_dk')
    for x in range(10, 22):                                          # plateau : petite dalle gravée
        put(t, x, 11, P['wf_md'])
    for x in (15, 16):
        put(t, x, 11, P['rn_md'])
    outline(t)
    return t


# ------------------------------------------------------------------ alcôve, lanterne
@reg('alcove_sol_rune')
def alcove_sol_rune(n, d):
    t = floor_tex('a')
    cx, cy = 15.5, 15.5
    for y in range(T):
        for x in range(T):
            d_ = math.hypot(x - cx, y - cy)
            if 8.5 <= d_ < 9.6:
                t[y][x] = P['rn_dk'] if rnd(x, y, 201) < 0.85 else t[y][x]
            elif d_ < 8.5 and (abs(x - 15) <= 0 or abs(x - 16) <= 0 or abs(y - 15) <= 0 and abs(x - 15.5) < 5):
                t[y][x] = P['rn_md']
    for (x, y) in ((15, 15), (16, 15), (15, 16), (16, 16)):
        t[y][x] = P['rn_hi']
    for k in range(6):
        x, y = round(cx + math.cos(k * 1.047) * 9.5), round(cy + math.sin(k * 1.047) * 9.5)
        t[y][x] = P['rn_lt']
    return t


@reg('dalle_lanterne')
def dalle_lanterne(n, d):
    t = floor_tex('a')
    # lanterne gravée : anneau, cage, flamme
    for y in range(6, 27):
        for x in range(9, 23):
            dx = abs(x - 15.5)
            if y == 6 or y == 7:
                if dx < 2.5:
                    t[y][x] = P['go_md']
            elif 8 <= y <= 9:
                if dx < 6 - (y - 8) * 0:
                    t[y][x] = P['go_lt'] if y == 8 else P['go_md']
            elif 10 <= y <= 22:
                if abs(dx - 6) < 1 or (y in (16,) and dx < 6):
                    t[y][x] = P['go_md'] if x < 16 else P['go_dk']
                elif dx < 5 and y > 11:
                    k = ((x - 9.5) / 12)
                    if dx < 2.2 and 14 <= y <= 20:
                        t[y][x] = P['rn_lt'] if dx < 1.2 else P['rn_md']
            elif 23 <= y <= 25:
                if dx < 6.5:
                    t[y][x] = P['go_lt'] if y == 23 else P['go_dk']
    for (x, y) in ((15, 16), (16, 16), (15, 17), (16, 17)):
        t[y][x] = P['rn_hi']
    t[14][15] = P['rn_lt']
    t[14][16] = P['rn_lt']
    for y in range(6, 27):
        for x in range(9, 23):
            pass
    return t


# ------------------------------------------------------------------ estrade
def estrade(front):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 211) * 0.6 + rnd(x, y, 212) * 0.4
            c = P['go_lt'] if n > 0.6 else P['go_dk'] if n < 0.26 else P['go_md']
            yy = y % 16
            off = 0 if y < 16 else 16
            if yy == 0 or (x + off) % 32 == 0:
                c = P['go_dp']
            elif yy == 1 or (x + off) % 32 == 1:
                c = P['go_hi'] if rnd(x, y, 213) < 0.75 else c
            t[y][x] = c
    if front:                                                        # marches : contremarche sombre sur le bas
        for y in range(16, 32):
            for x in range(T):
                k = y - 16
                if k < 4:
                    c = P['go_hi'] if k == 0 else P['go_lt']
                elif k < 14:
                    c = P['go_dk'] if k < 12 else P['go_dp']
                    if (x + 7) % 16 == 0:
                        c = P['go_dp']
                else:
                    c = P['go_dp']
                t[y][x] = c
        for x in range(T):
            t[31][x] = O
            t[26][x] = P['go_dp'] if x % 2 else t[26][x]
    return t


REG['estrade_dalle'] = lambda n, d: estrade(False)
REG['estrade_marches'] = lambda n, d: estrade(True)


# ------------------------------------------------------------------ variante crypte : recoloration + algues lumineuses aux murs
def crypte_px(px, S):
    """px : planche finale du rez-de-chaussée -> planche des cryptes (même cases)."""
    keep = GLOW | RUNE
    out = []
    for row in px:
        nr = []
        for c in row:
            if c is None:
                nr.append(None)
                continue
            if c in keep:
                nr.append(c)
                continue
            r, g, b, a = c
            L = 0.3 * r + 0.59 * g + 0.11 * b
            nr.append((int(r * 0.52 + L * 0.08), int(g * 0.58 + L * 0.1), min(255, int(b * 0.74 + L * 0.2 + 8)), a))
        out.append(nr)
    # algues lumineuses : au pied des faces de mur, et sur les murs latéraux
    W = len(out[0])
    for i, dd in S.tiles.items():
        nom = dd['nom']
        ox, oy = (i % S.cols) * T, (i // S.cols) * T
        tile = [row[ox:ox + T] for row in out[oy:oy + T]]
        if nom in ('mur_haut', 'mur_fissure_haut', 'mur_coin_int_hg', 'mur_coin_int_hd', 'mur_bas', 'mur_gauche', 'mur_droite',
                   'mur_coin_int_bg', 'mur_coin_int_bd', 'mur_coin_ext_hg', 'mur_coin_ext_hd', 'mur_coin_ext_bg', 'mur_coin_ext_bd',
                   'porte_haut', 'porte_bas', 'porte_gauche', 'porte_droite', 'mur_algues', 'mur_eau', 'colonne_base', 'pilier_bg', 'pilier_bd'):
            crypt_glow(tile, nom)
            for y in range(T):
                for x in range(T):
                    out[oy + y][ox + x] = tile[y][x]
    return out


def crypt_glow(t, nom):
    """Algues lumineuses posées sur les faces de mur d'une tuile déjà recolorée."""
    if nom in ('mur_haut', 'mur_fissure_haut', 'mur_algues', 'mur_eau', 'mur_coin_int_hg', 'mur_coin_int_hd', 'porte_haut'):
        tmp = [row[:] for row in t]
        glow_face(tmp, 17, 31, 0.8)
        for y in range(17, 31):
            for x in range(T):
                if tmp[y][x] in GLOW and (nom != 'porte_haut' or not 7 <= x <= 24):
                    t[y][x] = tmp[y][x]
    elif nom in ('mur_bas', 'porte_bas'):                            # dessus de mur : mousse lumineuse en bordure basse
        for x in range(2, 30):
            if rnd(x, 4, 221) < 0.15 and not (nom == 'porte_bas' and 7 <= x <= 24):
                for i in range(2 + int(rnd(x, 5, 222) * 3)):
                    put(t, x, 12 - i, P['gl_md'] if i < 2 else P['gl_lt'])
    elif nom in ('mur_gauche', 'mur_droite', 'porte_gauche', 'porte_droite'):
        xs = 6 if nom.endswith('gauche') else 25
        for y in range(5, 28):
            if rnd(y, 6, 223) < 0.14 and not (nom.startswith('porte') and 4 <= y <= 27):
                for i in range(3):
                    put(t, xs + (i if nom.endswith('gauche') else -i), y, P['gl_md'] if i == 0 else P['gl_lt'] if i == 1 else P['gl_hi'])
    elif nom == 'colonne_base':
        for x in (7, 24):
            for i in range(3):
                put(t, x, 22 - i, P['gl_lt'])
    elif nom in ('pilier_bg', 'pilier_bd'):
        for x in range(2, 31):
            if rnd(x, 7, 224) < 0.35:
                for i in range(2 + int(rnd(x, 8, 225) * 3)):
                    put(t, x, 27 - i, P['gl_md'] if i < 2 else P['gl_lt'])
