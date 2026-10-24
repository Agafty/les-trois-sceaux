"""DESSIN FINAL du tileset du Temple des Racines (donjon 1) — Les Trois Sceaux.

Ce module ne produit rien tout seul : `build()` renvoie {id de tuile: image 32x32} et
tools/sprites/temple_racines.py l'utilise pour remplacer les aplats du plan (python temple_racines.py ;
avec l'option --plan on regenere le plan à la place).

Regles : meme numero = meme case que le plan. Vue de dessus 3/4 (comme ALttP), lumiere en haut a gauche,
contour sombre 1 px, murs = dessus (cap) + face avant (sud) visible. Pas de Pillow : les images sont des
grilles de couleurs RGBA (tuples) ou None (transparent).
"""
import math
import random

T = 32

HEX = dict(
    O='#1b1420', I='#241a22',                                  # contours, tres sombres
    sol='#9a948c', joint='#5c5650', clair='#d8d4cc',           # dalles (palette du plan)
    sol_l='#aaa49a', sol_s='#847e76',                          # dalles : reflet, usure
    terre='#8a5a34', terre_s='#5e3a22', terre_c='#b06e40',     # terre battue / racines
    racine='#7a4628', racine_s='#4a2a1c',
    cap='#382e42', rim='#4e4058', face='#7a6a88', mur_c='#b8a8c0',   # murs violet-gris
    cap_l='#44384e', cap_d='#2e2638', face_l='#8a7a98', face_s='#645672',       # murs : reflet, ombre
    eau='#3c5a8a', prof='#263a5e',
    eau_c='#7a9ac0', eau_f='#b8d0e8', eau_d='#324d7a', prof_d='#1e2e4e',
    ronce='#241a22', ronce_m='#3a1a4a', ronce_c='#6a2a7a',     # ronces de Morvath
    vert='#5a8a3c', vert_c='#6a9a48', vert_s='#3a5a2c',        # mousse
    or_='#c8a050', orange='#f08a28',                           # feuilles
    vase='#b06e40', vase_s='#8a5a34', vase_c='#d6c49c', vase_l='#c98250',
)


def _rgba(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


C = {k: _rgba(v) for k, v in HEX.items()}


# ---------------------------------------------------------------- outils
def new(fill=None):
    return [[fill] * T for _ in range(T)]


def px(t, x, y, c):
    if 0 <= x < T and 0 <= y < T:
        t[y][x] = C[c] if isinstance(c, str) else c


def rect(t, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(T - 1, y1) + 1):
        for x in range(max(0, x0), min(T - 1, x1) + 1):
            t[y][x] = C[c] if isinstance(c, str) else c


def line(t, x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        px(t, round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)


def ellipse(t, cx, cy, rx, ry, c):
    for y in range(T):
        for x in range(T):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                t[y][x] = C[c] if isinstance(c, str) else c


def outline(t, c='O'):
    c = C[c]
    pts = [(x, y) for y in range(T) for x in range(T) if t[y][x] is None and any(
        0 <= x + dx < T and 0 <= y + dy < T and t[y + dy][x + dx] not in (None, c)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        t[y][x] = c


def sprinkle(t, seed, n, colors, x0=0, y0=0, x1=31, y1=31, only=None):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        if only is None or t[y][x] == C[only]:
            t[y][x] = C[rnd.choice(colors)]


def tube(t, pts, r0, r1, cols=('terre_c', 'terre', 'racine', 'racine_s')):
    """Tube epais (racine, liane, bois) le long d'une ligne brisee, rayon r0 -> r1, ombrage lumiere en haut a gauche."""
    samples = []
    segs = list(zip(pts, pts[1:])) if len(pts) > 1 else [(pts[0], pts[0])]
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs) or 1
    acc = 0
    for a, b in segs:
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(int(L * 2), 1)
        for i in range(n + 1):
            f = i / n
            r = r0 + (r1 - r0) * (acc + L * f) / total
            samples.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, r))
        acc += L
    for y in range(T):
        for x in range(T):
            best = None
            for sx, sy, r in samples:
                d = math.hypot(x - sx, y - sy)
                if d <= r + 0.2 and (best is None or d - r < best[0]):
                    best = (d - r, x - sx, y - sy, r)
            if best:
                _, dx, dy, r = best
                lum = -(dx + dy) / (1.414 * max(r, 1))
                t[y][x] = C[cols[0] if lum > 0.55 else cols[1] if lum > 0.0 else cols[2] if lum > -0.5 else cols[3]]


DARK = {'sol': 'sol_s', 'sol_l': 'sol', 'clair': 'sol_l', 'sol_s': 'joint', 'joint': 'I'}
DARK_RGB = {C[k]: C[v] for k, v in DARK.items()}


def darker(c):
    return DARK_RGB.get(c, c)


# ---------------------------------------------------------------- 1. sol
def slab(t, x0, y0, x1, y1, lit='sol_l'):
    """Dalle dont x0 et y0 sont les joints (haut/gauche) ; x1 et y1 sont sa derniere ligne/colonne.
    Biseau : reflet en haut et a gauche, ombre en bas et a droite."""
    for x in range(x0, x1 + 1):
        px(t, x, y0, 'joint')
    for y in range(y0, y1 + 1):
        px(t, x0, y, 'joint')
    for x in range(x0 + 1, x1 + 1):
        px(t, x, y0 + 1, lit)
        px(t, x, y1, 'sol_s')
    for y in range(y0 + 1, y1 + 1):
        px(t, x0 + 1, y, lit)
        px(t, x1, y, 'sol_s')
    px(t, x0 + 1, y0 + 1, 'clair')
    px(t, x0 + 2, y0 + 1, 'clair')
    px(t, x0 + 1, y0 + 2, 'clair')


def dalle(v):
    t = new(C['sol'])
    sprinkle(t, 100 + v, 14, ['sol_s', 'sol_l'], only='sol')
    if v == 0:      # 4 dalles carrees
        for x0, y0 in ((0, 0), (16, 0), (0, 16), (16, 16)):
            slab(t, x0, y0, x0 + 15, y0 + 15)
    elif v == 1:    # dalles longues en quinconce : 2 rangees, joints verticaux decales
        slab(t, 0, 0, 31, 15)
        px(t, 0, 0, 'joint')
        rect(t, 0, 0, 0, 15, 'joint')
        slab(t, 0, 16, 31, 31)
        rect(t, 16, 17, 16, 31, 'joint')       # joint vertical de la rangee du bas
        rect(t, 15, 17, 15, 31, 'sol_s')
        rect(t, 17, 18, 17, 31, 'sol_l')
        rect(t, 0, 0, 0, 15, 'joint')
        rect(t, 1, 2, 1, 15, 'sol_l')
    else:           # grande dalle : cadre grave discret (equerres aux 4 coins) + veines
        slab(t, 0, 0, 31, 31)
        for (x0, y0, dx, dy) in ((6, 6, 1, 1), (25, 6, -1, 1), (6, 25, 1, -1), (25, 25, -1, -1)):
            for k in range(0, 6):
                px(t, x0 + dx * k, y0, 'sol_s'); px(t, x0, y0 + dy * k, 'sol_s')
            px(t, x0 + dx, y0 + dy, 'sol_l')
        for x, y in ((14, 11), (15, 11), (16, 12), (17, 12), (12, 20), (13, 21), (14, 21), (19, 18), (20, 18)):
            px(t, x, y, 'sol_s')
    return t


def dalle_fissuree(v):
    t = dalle(0)
    pts = [(3, 5), (8, 9), (7, 14), (12, 19), (18, 21), (22, 27), (28, 29)] if v == 0 else \
          [(26, 3), (21, 8), (23, 12), (17, 15), (13, 22), (6, 25)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(t, x0 + 1, y0 + 1, x1 + 1, y1 + 1, 'sol_l')
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(t, x0, y0, x1, y1, 'I')
    if v == 1:
        line(t, 18, 16, 25, 21, 'sol_l')
        line(t, 17, 15, 24, 20, 'I')
        line(t, 21, 8, 14, 7, 'I')
    else:
        line(t, 12, 19, 8, 24, 'I')
    # eclats
    for x, y in ((9, 12), (20, 24), (14, 11)):
        px(t, x, y, 'joint')
    return t


def terre():
    t = new(C['terre'])
    rnd = random.Random(5)
    for _ in range(40):
        x, y = rnd.randrange(32), rnd.randrange(32)
        px(t, x, y, 'terre_s')
        if rnd.random() < 0.4:
            px(t, x + 1, y, 'terre_s')
    for _ in range(18):
        px(t, rnd.randrange(32), rnd.randrange(32), 'terre_c')
    for x, y in ((6, 8), (22, 5), (14, 20), (26, 24), (4, 26)):      # petits cailloux
        px(t, x, y, 'sol'); px(t, x + 1, y, 'sol_l'); px(t, x, y + 1, 'joint'); px(t, x + 1, y + 1, 'joint')
    return t


def racine(kind):
    """Decor transparent posé sur le sol. h/v : racine de 5 px de large (+ contour) qui se raccorde bord a bord."""
    t = new()

    def c(a):
        return 15 + round(3 * math.sin(2 * math.pi * a / 32))

    def put(a, d, col):         # a = position le long de la racine, d = decalage perpendiculaire
        if kind == 'h':
            px(t, a, c(a) + d, col)
        else:
            px(t, c(a) + d, a, col)

    def put_abs(a, b, col):
        if kind == 'h':
            px(t, a, b, col)
        else:
            px(t, b, a, col)

    if kind in ('h', 'v'):
        for a in range(32):
            for d, col in ((-2, 'terre_c'), (-1, 'terre'), (0, 'terre'), (1, 'racine'), (2, 'racine_s')):
                put(a, d, col)
            if a % 7 == 2:
                put(a, 0, 'racine')
            if a % 6 == 4:
                put(a, 1, 'racine_s')
            if a % 9 == 5:
                put(a, -1, 'terre_c')
        # radicelles : une vers le haut, une vers le bas
        for a0, sgn in ((6, -1), (21, 1)):
            for k in range(1, 6):
                b = c(a0 + k // 2) + sgn * (2 + k)
                put_abs(a0 + k // 2, b, 'racine' if k < 4 else 'racine_s')
    else:  # nœud : une racine qui traverse (raccord avec racine_h) et des branches qui partent
        tube(t, [(0, 15), (12, 15)], 2.6, 2.6)
        tube(t, [(20, 15), (31, 14)], 2.6, 2.6)
        for pts, r0, r1 in (([(14, 13), (10, 8), (8, 3)], 2.6, 1.0), ([(19, 17), (22, 23), (21, 29)], 2.4, 0.9),
                            ([(11, 17), (8, 22)], 1.6, 0.8)):
            tube(t, pts, r0, r1)
        tube(t, [(16, 15)], 5.2, 5.2)
        rnd = random.Random(3)
        for _ in range(16):                              # ecorce
            x, y = rnd.randrange(8, 25), rnd.randrange(9, 22)
            if t[y][x] in (C['terre'], C['racine']):
                px(t, x, y, 'racine_s')
        for x, y in ((14, 12), (15, 12), (13, 13)):
            px(t, x, y, 'terre_c')
    outline(t)
    return t


# ---------------------------------------------------------------- 2. murs
def cap_px(x, y):
    """Dessus d'un mur : dalles de pierre sombres, joints decales (se raccorde d'une tuile a l'autre)."""
    if y % 16 == 8:
        return 'cap_d'
    ru = (y % 16) < 8
    vx = 11 if ru else 27
    if x == vx:
        return 'cap_d'
    if x == vx + 1 or y % 16 == 9:
        return 'cap_l'
    return 'cap'


CAP_SPECKS = {(6, 5): 'cap_d', (22, 13): 'cap_d', (4, 20): 'cap_d', (26, 28): 'cap_d', (18, 3): 'cap_d', (14, 27): 'cap_d',
              (8, 12): 'cap_l', (24, 19): 'cap_l', (19, 29): 'cap_l', (3, 2): 'cap_l'}
FACE_CHIPS = {(5, 20): 'rim', (6, 21): 'rim', (22, 19): 'rim', (27, 28): 'rim', (13, 27): 'rim', (11, 28): 'rim',
              (10, 21): 'face_l', (25, 22): 'face_l', (3, 27): 'face_l', (19, 26): 'face_l', (30, 20): 'face_l'}


def cap_color(x, y):
    return CAP_SPECKS.get((x, y)) or cap_px(x, y)


def face_color(x, y):
    """Face avant (sud) d'un mur : 2 assises de pierres taillees, reflet en haut, ombre en bas."""
    if y == 17:
        return 'mur_c'
    if (x, y) in FACE_CHIPS:
        return FACE_CHIPS[(x, y)]
    if y == 24:
        return 'rim'
    if y == 31:
        return 'O'
    if y < 24:
        if x % 16 == 0:
            return 'rim'
        return 'face_l' if y == 18 else ('face_s' if y == 23 else 'face')
    if x % 16 == 8:
        return 'rim'
    return 'face_l' if y == 25 else ('face_s' if y == 30 else 'face')


LIT = ('O', 'mur_c', 'face', 'rim')      # bord eclaire (haut, gauche) : du bord vers l'interieur
SHD = ('O', 'rim', 'rim', 'rim')         # bord dans l'ombre (droite)


def put_cap(t, x, y):
    t[y][x] = C[cap_color(x, y)]


def wall(bits, face_rows=True):
    tl, tr, bl, br = bits
    t = [[C[cap_color(x, y)] for x in range(T)] for y in range(T)]
    n, s = not tl and not tr, not bl and not br
    w, e = not tl and not bl, not tr and not br
    if n:
        for y in range(4):
            rect(t, 0, y, 31, y, LIT[y])
    if w:
        for x in range(4):
            rect(t, x, 0, x, 31, LIT[x])
        rect(t, 0, 0, 0, 31, 'O')
    if e:
        for k in range(4):
            rect(t, 31 - k, 0, 31 - k, 31, SHD[k])
    if n and w:
        for y in range(4):
            for x in range(4):
                t[y][x] = C[LIT[min(x, y)]]
    if n and e:
        for y in range(4):
            for x in range(28, 32):
                t[y][x] = C[LIT[y] if y <= 31 - x else SHD[31 - x]]
    # coins isoles (le sol n'est que dans un coin)
    if not tr and tl and br:        # sol en haut a droite
        for y in range(4):
            for x in range(28, 32):
                t[y][x] = C[LIT[y] if y <= 31 - x else SHD[31 - x]]
    if not tl and tr and bl:        # sol en haut a gauche
        for y in range(4):
            for x in range(4):
                t[y][x] = C[LIT[min(x, y)]]
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
                t[y][x] = C[face_color(x, y)]
    if s and w:
        rect(t, 0, 17, 0, 31, 'O')
    if s and e:
        rect(t, 31, 17, 31, 31, 'O')
    return t


# ---------------------------------------------------------------- 3. portes
def floor_px(x, y):
    """Pixel de dalle (variante A) : sol de l'ouverture des portes."""
    d = DALLE_A[y][x]
    return d


def carve_floor(t, x0, y0, x1, y1, shade):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = DALLE_A[y][x]
            lv = shade(x, y)
            if lv % 1:                         # niveau fractionnaire : tramage en damier
                lv = int(lv) + (1 if (x + y) % 2 == 0 else 0)
            for _ in range(int(lv)):
                c = darker(c)
            t[y][x] = c


def porte(side):
    bits = {'haut': (1, 1, 0, 0), 'bas': (0, 0, 1, 1), 'gauche': (1, 0, 1, 0), 'droite': (0, 1, 0, 1)}[side]
    t = wall(bits)
    if side == 'haut':
        carve_floor(t, 6, 0, 25, 31, lambda x, y: 2 if y < 11 else (1 if y < 15 else 0))
        rect(t, 5, 0, 5, 31, 'O'); rect(t, 26, 0, 26, 31, 'O')
        rect(t, 4, 0, 4, 31, 'rim'); rect(t, 27, 0, 27, 31, 'rim')
        rect(t, 4, 0, 4, 0, 'O'); rect(t, 27, 0, 27, 0, 'O')
    elif side == 'bas':
        carve_floor(t, 6, 0, 25, 31, lambda x, y: 2 if y > 28 else (1 if y > 24 else 0))
        rect(t, 5, 0, 5, 31, 'O'); rect(t, 26, 0, 26, 31, 'O')
        rect(t, 4, 4, 4, 31, 'rim'); rect(t, 27, 4, 27, 31, 'rim')
    elif side == 'gauche':
        carve_floor(t, 0, 4, 31, 27, lambda x, y: 2 if x < 5 else (1 if x < 9 else 0))
        rect(t, 0, 3, 31, 3, 'O'); rect(t, 0, 28, 31, 28, 'O')
        lintel_side(t, 'gauche')
        for x in range(32):           # bord eclaire du montant bas
            px(t, x, 29, 'mur_c' if x < 28 else 'rim'); px(t, x, 30, 'face' if x < 28 else 'rim')
            px(t, x, 31, 'rim')
        rect(t, 28, 28, 31, 31, 'O') if False else None
    else:
        carve_floor(t, 0, 4, 31, 27, lambda x, y: 2 if x > 26 else (1 if x > 22 else 0))
        rect(t, 0, 3, 31, 3, 'O'); rect(t, 0, 28, 31, 28, 'O')
        lintel_side(t, 'droite')
        for x in range(32):
            px(t, x, 29, 'mur_c' if x > 3 else 'rim'); px(t, x, 30, 'face' if x > 3 else 'rim')
            px(t, x, 31, 'rim')
    return t


def lintel_side(t, side):
    """Haut de l'encadrement d'une porte laterale : cap (y0..3) + petite face sud (y4..7)."""
    for y in range(0, 4):
        for x in range(T):
            t[y][x] = C[cap_color(x, y)]
    if side == 'gauche':
        for k in range(4):
            rect(t, 31 - k, 0, 31 - k, 3, SHD[k])
    else:
        for k in range(4):
            rect(t, k, 0, k, 3, LIT[k])
    for x in range(T):
        t[4][x] = C['mur_c']
        t[5][x] = C['face_l']
        t[6][x] = C['face']
        t[7][x] = C['O']
    for x in range(T):
        if x % 16 == 0:
            t[5][x] = t[6][x] = C['rim']


def porte_dessus(side):
    """Haut de l'encadrement, sur le calque Dessus : Brann passe dessous."""
    t = new()
    if side in ('haut', 'bas'):
        if side == 'haut':
            y0, y1 = 0, 9
        else:
            y0, y1 = 22, 31
        for y in range(y0, y1 + 1):
            for x in range(4, 28):
                t[y][x] = C[cap_color(x, y)]
        if side == 'haut':       # poutre de pierre : levre eclairee en bas
            for x in range(4, 28):
                t[6][x] = C['rim']; t[7][x] = C['mur_c']; t[8][x] = C['face']; t[9][x] = C['O']
            rect(t, 4, 0, 4, 9, 'rim'); rect(t, 27, 0, 27, 9, 'rim')
            rect(t, 4, 0, 4, 0, 'O'); rect(t, 27, 0, 27, 0, 'O')
            sx, sy = 12, 1
        else:
            for x in range(4, 28):
                t[22][x] = C['O']; t[23][x] = C['mur_c']; t[24][x] = C['face']; t[25][x] = C['rim']
            rect(t, 4, 22, 4, 31, 'rim'); rect(t, 27, 22, 27, 31, 'rim')
            sx, sy = 12, 26
        # clef de voute gravee : petit arbre (racines)
        rect(t, sx, sy, sx + 7, sy + 4, 'cap_l')
        rect(t, sx, sy, sx + 7, sy, 'rim'); rect(t, sx, sy + 4, sx + 7, sy + 4, 'I')
        rect(t, sx, sy, sx, sy + 4, 'rim'); rect(t, sx + 7, sy, sx + 7, sy + 4, 'I')
        for (dx, dy) in ((3, 1), (4, 1), (3, 2), (4, 2), (2, 3), (3, 3), (4, 3), (5, 3), (1, 3), (6, 3)):
            px(t, sx + dx, sy + dy, 'terre_c' if dy < 3 else 'terre')
        outline(t)
    else:
        lintel_side(t, side)
        # l'encadrement exterieur (pas de bord eclaire sur le montant) : on garde la meme coupe que la tuile
    return t


# ---------------------------------------------------------------- 4. escaliers, trous
def escalier(montant):
    t = new(C['sol'])
    for y in range(T):
        for x in range(0, 5):
            t[y][x] = C[cap_color(x, y)]
        for x in range(27, 32):
            t[y][x] = C[cap_color(x, y)]
    rect(t, 3, 0, 3, 31, 'rim'); rect(t, 4, 0, 4, 31, 'O')
    rect(t, 27, 0, 27, 31, 'O'); rect(t, 28, 0, 28, 31, 'rim')
    rect(t, 0, 0, 0, 31, 'I')
    for k in range(6):
        y0 = k * 5
        if montant:       # on voit le dessus (clair) et la contremarche (ombre) de chaque marche
            rect(t, 5, y0, 26, y0 + 2, 'sol_l')
            rect(t, 5, y0, 26, y0, 'clair')
            rect(t, 5, y0 + 2, 26, y0 + 2, 'sol')
            rect(t, 5, y0 + 3, 26, y0 + 3, 'sol_s')
            rect(t, 5, y0 + 4, 26, y0 + 4, 'joint')
        else:             # on voit le dessus de chaque marche, de plus en plus sombre
            tc = ['sol', 'sol_s', 'joint', 'rim', 'cap', 'I'][k]
            rect(t, 5, y0, 26, y0 + 3, tc)
            rect(t, 5, y0, 26, y0, 'clair' if k < 3 else 'sol_l' if k == 3 else 'rim')
            rect(t, 5, y0 + 4, 26, y0 + 4, 'O')
    rect(t, 5, 31, 26, 31, 'sol' if montant else 'O')
    if not montant:
        rect(t, 5, 27, 26, 31, 'O')
        rect(t, 5, 25, 26, 25, 'I')
    return t


def hole_wall_color(x, y):
    """Paroi du fond d'un trou (visible quand le sol est au nord) : pierre qui s'assombrit en profondeur."""
    if y <= 3:
        base = 'rim'
    elif y <= 7:
        base = 'cap'
    elif y <= 10:
        base = 'I'
    else:
        return 'O'
    if y % 4 == 0 and y > 0 or (x + (4 if (y // 4) % 2 else 0)) % 8 == 0:
        return {'rim': 'cap', 'cap': 'I', 'I': 'O'}[base]
    return base


def trou(bits):
    """Case de trou entiere (on tombe partout dedans). bits = coins occupes par le trou."""
    tl, tr, bl, br = bits
    t = new(C['O'])
    rnd = random.Random(11)
    for _ in range(18):
        px(t, rnd.randrange(32), rnd.randrange(32), 'I')
    for x, y in ((9, 22), (21, 18), (14, 27)):
        rect(t, x, y, x + 2, y, 'I')
    n, s = not tl and not tr, not bl and not br
    w, e = not tl and not bl, not tr and not br
    if n:   # paroi du fond (face au joueur), bord de dalle clair au-dessus
        for y in range(0, 13):
            for x in range(T):
                t[y][x] = C[hole_wall_color(x, y)]
        rect(t, 0, 0, 31, 0, 'clair')
        rect(t, 0, 1, 31, 1, 'sol')
        rect(t, 0, 2, 31, 2, 'joint')
    if w:   # petit bord a gauche : levre de dalle puis paroi dans l'ombre
        rect(t, 0, 0, 0, 31, 'clair'); rect(t, 1, 0, 1, 31, 'sol'); rect(t, 2, 0, 2, 31, 'joint')
        rect(t, 3, 3, 3, 31, 'cap'); rect(t, 4, 6, 4, 31, 'I')
    if e:
        rect(t, 31, 0, 31, 31, 'sol_s'); rect(t, 30, 0, 30, 31, 'joint')
        rect(t, 29, 3, 29, 31, 'I')
    if n and w:
        rect(t, 0, 0, 0, 2, 'clair'); rect(t, 1, 1, 1, 1, 'sol')
    if s:   # bord proche : le sol commence, levre eclairee
        rect(t, 0, 25, 31, 25, 'I')
        rect(t, 0, 26, 31, 26, 'joint')
        rect(t, 0, 27, 31, 27, 'O')
        rect(t, 0, 28, 31, 28, 'clair')
        rect(t, 0, 29, 31, 29, 'sol_l')
        rect(t, 0, 30, 31, 31, 'sol')
        rect(t, 0, 31, 31, 31, 'sol')
        if w:
            rect(t, 0, 28, 0, 31, 'clair')
    return t


# ---------------------------------------------------------------- 5. ronces
def ronces_bloc(v):
    t = new()
    rnd = random.Random(10 + v)
    # masse sombre : presque toute la case (les bords se raccordent avec la case voisine)
    for y in range(T):
        for x in range(T):
            d = (abs(x - 15.5) / 16.5) ** 6 + (abs(y - 15.5) / 16.5) ** 6
            if d <= 1:
                t[y][x] = C['O'] if (x * 7 + y * 3 + v) % 5 else C['ronce']
    cols = ('ronce_c', 'ronce_m', 'ronce', 'O')
    # lianes epaisses qui traversent la case (memes hauteurs aux bords : elles se raccordent)
    for k, y0 in enumerate((7, 16, 25)):
        ph = 0.8 + 2.1 * k + 1.9 * v
        pts = [(x, y0 + 3 * math.sin(2 * math.pi * x / 32 + ph)) for x in range(0, 32, 2)] + \
              [(31, y0 + 3 * math.sin(2 * math.pi * 31 / 32 + ph))]
        tube(t, pts, 2.1, 2.1, cols)
    for k, x0 in enumerate((9, 23)):
        ph = 1.5 + 2.4 * k + 1.3 * v
        pts = [(x0 + 3 * math.sin(2 * math.pi * y / 32 + ph), y) for y in range(0, 32, 2)] + \
              [(x0 + 3 * math.sin(2 * math.pi * 31 / 32 + ph), 31)]
        tube(t, pts, 1.7, 1.7, cols)
    # epines : petits crochets clairs sur les lianes
    for _ in range(40):
        x, y = rnd.randrange(1, 31), rnd.randrange(1, 31)
        if t[y][x] in (C['ronce_m'], C['ronce_c']):
            dx, dy = rnd.choice(((1, -1), (-1, -1), (1, 1), (-1, 1)))
            for k in (1, 2):
                if 0 <= x + dx * k < T and 0 <= y + dy * k < T and t[y + dy * k][x + dx * k] in (C['O'], C['ronce']):
                    px(t, x + dx * k, y + dy * k, 'ronce_c')
    # grandes epines qui depassent dans les coins (transparents)
    spikes = [(3, 3, -1, -1), (28, 3, 1, -1), (3, 28, -1, 1), (28, 28, 1, 1), (8, 1, -1, -1), (24, 1, 1, -1),
              (1, 24, -1, 1), (30, 9, 1, -1), (9, 30, -1, 1), (22, 30, 1, 1)] if v == 0 else \
             [(4, 2, -1, -1), (27, 4, 1, -1), (2, 27, -1, 1), (29, 27, 1, 1), (12, 1, -1, -1), (26, 1, 1, -1),
              (1, 8, -1, -1), (30, 23, 1, 1), (7, 30, -1, 1), (20, 30, 1, 1)]
    for sx, sy, dx, dy in spikes:
        for k in range(0, 5):
            for w in range(0, 2 if k < 3 else 1):
                px(t, sx + dx * k + (w if dx != dy else 0), sy + dy * k + (w if dx == dy else 0),
                   'ronce_m' if k < 3 else 'ronce_c')
    outline(t)
    return t


def ronces_sol(v):
    t = new()
    tracks = [((0, 22), (9, 17), (17, 21), (25, 15), (31, 18)), ((6, 3), (12, 11), (10, 19), (16, 28))] if v == 0 else \
             [((0, 9), (8, 12), (15, 7), (23, 11), (31, 8)), ((20, 30), (22, 22), (28, 17))]
    for tr in tracks:
        for (x0, y0), (x1, y1) in zip(tr, tr[1:]):
            line(t, x0, y0 + 1, x1, y1 + 1, 'ronce')
            line(t, x0, y0, x1, y1, 'ronce_m')
        for (x, y) in tr[1:-1]:                    # epines
            px(t, x, y - 1, 'ronce_c'); px(t, x + 1, y - 2, 'ronce_c'); px(t, x - 1, y + 3, 'ronce_c')
        for (x0, y0), (x1, y1) in zip(tr, tr[1:]):
            px(t, (x0 + x1) // 2, (y0 + y1) // 2 - 1, 'ronce_c')
    outline(t, 'O')
    return t


# ---------------------------------------------------------------- 6. eau
RIPPLES = [(4, 5, 5), (18, 3, 4), (10, 12, 4), (23, 14, 5), (2, 20, 4), (14, 24, 5), (26, 27, 4), (20, 19, 3)]
RIPPLES_DEEP = [(6, 8, 4), (20, 6, 3), (12, 18, 5), (24, 22, 4), (3, 27, 3), (27, 12, 3)]


def quarter_mask(bits, r=5):
    m = [[0] * T for _ in range(T)]
    for q, b in enumerate(bits):
        if b:
            for y in range((q // 2) * 16, (q // 2) * 16 + 16):
                for x in range((q % 2) * 16, (q % 2) * 16 + 16):
                    m[y][x] = 1
    n = sum(bits)
    if n in (1, 3):                      # coin arrondi au centre de la case
        odd = [q for q, b in enumerate(bits) if b == (1 if n == 1 else 0)][0]
        qx, qy = (odd % 2) * 16, (odd // 2) * 16
        cx = 15 if qx == 0 else 16
        cy = 15 if qy == 0 else 16
        dx = -1 if qx == 0 else 1
        dy = -1 if qy == 0 else 1
        for i in range(r):
            for j in range(r):
                if (i + 0.5 - r) ** 2 + (j + 0.5 - r) ** 2 > r * r:
                    x, y = cx + dx * i, cy + dy * j
                    m[y][x] = 1 - m[y][x]
    return m


def eau(bits, profonde):
    m = quarter_mask(bits)
    t = new()

    def at(x, y):
        x = min(31, max(0, x)); y = min(31, max(0, y))
        return m[y][x]

    ripple = {}
    for (x, y, n) in RIPPLES:
        for k in range(n):
            ripple[(x + k, y)] = 'eau_c'
        ripple[(x - 1, y - 1)] = 'eau_f'
    deep_rip = {}
    for (x, y, n) in RIPPLES_DEEP:
        for k in range(n):
            deep_rip[(x + k, y)] = 'eau'
    for y in range(T):
        for x in range(T):
            if not profonde:
                if m[y][x]:       # eau peu profonde
                    c = 'eau'
                    if not at(x, y - 1) or not at(x, y - 2) or not at(x - 1, y) or not at(x - 2, y):
                        c = 'eau_d'                      # ombre portee du bord (lumiere en haut a gauche)
                    elif not at(x, y + 1) or not at(x + 1, y):
                        c = 'eau_c'                      # ecume sur le bord eclaire
                    elif (x, y) in ripple:
                        c = ripple[(x, y)]
                    t[y][x] = C[c]
                else:             # dalle
                    c = DALLE_A[y][x]
                    if at(x, y + 1) or at(x, y - 1) or at(x + 1, y) or at(x - 1, y):
                        c = C['joint']                   # bord de dalle mouille
                    t[y][x] = c
            else:
                if m[y][x]:       # eau profonde
                    c = 'prof'
                    if not at(x, y - 1) or not at(x - 1, y) or not at(x, y + 1) or not at(x + 1, y):
                        c = 'prof_d'
                    elif (x, y) in deep_rip:
                        c = deep_rip[(x, y)]
                    t[y][x] = C[c]
                else:             # eau peu profonde autour
                    c = 'eau'
                    if at(x, y + 1) or at(x + 1, y):
                        c = 'eau_c'                      # reflet du cote eclaire
                    elif (x, y) in ripple:
                        c = ripple[(x, y)]
                    t[y][x] = C[c]
    return t


# ---------------------------------------------------------------- 7. decor
def colonne(part):
    t = new()
    shade = ['clair', 'clair', 'sol_l', 'sol_l', 'sol', 'sol', 'sol_l', 'sol_l', 'sol', 'sol_s', 'joint', 'joint']
    y0, y1 = (10, 31) if part == 'haut' else (0, 23)
    for y in range(y0, y1 + 1):
        for i, col in enumerate(shade):
            px(t, 10 + i, y, col)
    if part == 'haut':
        joints = (22,)
    else:
        joints = (6, 17)
    for y in joints:
        for x in range(10, 22):
            px(t, x, y, 'sol_s' if x < 20 else 'joint')
        for x in range(10, 22):
            px(t, x, y + 1, 'clair' if x < 14 else 'sol_l') if x < 18 else None
    if part == 'haut':
        # chapiteau : tailloir (dalle) + echine
        for y in range(1, 7):
            for x in range(4, 28):
                t[y][x] = C['clair'] if y <= 2 else (C['sol_l'] if y <= 4 else C['sol'])
        rect(t, 25, 3, 27, 6, 'sol_s')
        rect(t, 4, 6, 27, 6, 'sol_s')
        rect(t, 5, 7, 26, 8, 'sol')
        rect(t, 5, 7, 12, 7, 'sol_l'); rect(t, 24, 7, 26, 8, 'sol_s'); rect(t, 5, 8, 26, 8, 'joint')
        rect(t, 8, 9, 23, 9, 'joint')
        # racine qui s'enroule autour du chapiteau
        for k in range(8):
            px(t, 21 + (k // 3), 3 + k, 'racine') if k < 5 else None
    else:
        # socle : dalle + base
        rect(t, 6, 24, 25, 25, 'clair'); rect(t, 6, 24, 6, 29, 'clair')
        rect(t, 6, 26, 25, 29, 'sol')
        rect(t, 6, 26, 12, 26, 'sol_l')
        rect(t, 24, 26, 25, 29, 'sol_s'); rect(t, 6, 29, 25, 29, 'joint')
        rect(t, 8, 22, 23, 23, 'sol'); rect(t, 8, 22, 14, 22, 'sol_l'); rect(t, 22, 22, 23, 23, 'sol_s')
        # racine qui grimpe sur le fût
        for k, (x, y) in enumerate(((21, 25), (21, 22), (20, 20), (20, 17), (21, 15), (20, 12), (21, 10))):
            rect(t, x, y, x + 1, y + 2, 'racine' if k % 2 else 'terre')
        rect(t, 22, 12, 22, 24, 'racine_s')
        for x, y in ((7, 27), (8, 27), (9, 28), (7, 28), (13, 28)):          # mousse au pied
            px(t, x, y, 'vert' if (x + y) % 3 else 'vert_c')
        px(t, 11, 21, 'vert_s')
    outline(t)
    if part == 'base':     # ombre au sol
        rect(t, 7, 30, 26, 30, 'joint'); rect(t, 10, 31, 23, 31, 'joint')
    return t


def vase():
    t = new()
    cx, cy, rx, ry = 15.5, 20.0, 9.5, 8.5
    for y in range(T):
        for x in range(T):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1:
                lum = -0.65 * nx - 0.65 * ny
                col = 'vase_l' if lum > 0.55 else ('vase' if lum > -0.15 else ('vase_s' if lum > -0.65 else 'racine'))
                t[y][x] = C[col]
    rect(t, 12, 9, 19, 12, 'vase')              # col
    rect(t, 12, 9, 13, 12, 'vase_l'); rect(t, 18, 9, 19, 12, 'vase_s')
    rect(t, 10, 6, 21, 8, 'vase'); rect(t, 10, 6, 21, 6, 'vase_c')
    rect(t, 10, 6, 11, 8, 'vase_l'); rect(t, 20, 7, 21, 8, 'vase_s')
    rect(t, 12, 7, 19, 7, 'racine_s')            # ouverture
    for x in range(8, 24):                       # frise de feuilles
        if t[17][x] is not None:
            t[17][x] = C['racine_s'] if x % 4 < 2 else C['racine']
        if t[18][x] is not None and x % 4 == 1:
            t[18][x] = C['racine_s']
    rect(t, 11, 12, 11, 12, 'vase_s')
    px(t, 10, 15, 'vase_c'); px(t, 10, 16, 'vase_c'); px(t, 11, 14, 'vase_c')
    for x, y in ((14, 22), (15, 22), (16, 23)):   # mousse sur le ventre
        px(t, x, y, 'vert')
    outline(t)
    rect(t, 9, 29, 22, 29, 'joint'); rect(t, 11, 30, 20, 30, 'joint')   # ombre au sol
    return t


STONE = ('clair', 'sol_l', 'sol', 'sol_s')


def stone_shade(t, mask_rows, cx=15.5):
    """Colorie une silhouette (dict y -> (x0, x1)) en pierre claire : reflet a gauche, ombre a droite."""
    for y, (x0, x1) in mask_rows.items():
        w = x1 - x0 + 1
        for x in range(x0, x1 + 1):
            f = (x - x0) / max(w - 1, 1)
            t[y][x] = C['clair' if f < 0.3 else 'sol_l' if f < 0.62 else 'sol' if f < 0.88 else 'sol_s']


def cerf(part):
    """Statue de cerf en pierre claire (Sylve), de face : bois et tete en haut, poitrail et pattes sur socle en bas.
    Le cou fait 8 px de large (x12..19) a la jonction des deux cases."""
    t = new()
    if part == 'haut':
        for sgn in (-1, 1):  # bois : un andouiller principal + 3 pointes, epais de 3 px
            cx = 15.5 + sgn * 0.5
            tube(t, [(cx + sgn * 3, 17), (cx + sgn * 6, 10), (cx + sgn * 9, 5), (cx + sgn * 10, 1)], 1.7, 1.0, STONE)
            tube(t, [(cx + sgn * 5, 12), (cx + sgn * 10, 11), (cx + sgn * 13, 8)], 1.2, 0.7, STONE)
            tube(t, [(cx + sgn * 8, 7), (cx + sgn * 13, 4)], 1.1, 0.6, STONE)
            tube(t, [(cx + sgn * 4, 14), (cx + sgn * 2, 9)], 1.0, 0.6, STONE)
        # oreilles
        for sgn in (-1, 1):
            cx = 15.5 + sgn * 7.5
            tube(t, [(cx, 22), (cx + sgn * 2.5, 20)], 2.0, 1.0, STONE if sgn < 0 else STONE)
        # tete : front large, museau etroit vers le bas
        widths = {16: 8, 17: 10, 18: 12, 19: 12, 20: 12, 21: 12, 22: 11, 23: 10, 24: 10, 25: 9, 26: 9, 27: 8, 28: 8,
                  29: 8, 30: 8, 31: 8}
        rows = {y: (16 - w // 2, 16 + w // 2 - 1) for y, w in widths.items()}
        stone_shade(t, rows)
        px(t, 12, 21, 'O'); px(t, 13, 21, 'O'); px(t, 18, 21, 'O'); px(t, 19, 21, 'O')       # yeux
        px(t, 12, 20, 'sol_s'); px(t, 19, 20, 'sol_s')
        rect(t, 14, 28, 15, 28, 'O'); rect(t, 16, 28, 17, 28, 'O')                           # narines
        rect(t, 14, 30, 17, 30, 'sol_s')
        px(t, 15, 17, 'clair'); px(t, 16, 17, 'sol_l')
        for x, y in ((11, 18), (12, 18), (10, 19), (12, 17)):                                # mousse
            px(t, x, y, 'vert' if (x + y) % 2 else 'vert_c')
        outline(t)
        for x in range(T):                        # pas de contour sur la ligne de jonction
            if t[31][x] == C['O']:
                t[31][x] = None
    else:
        # corps (derriere) : croupe visible de chaque cote du poitrail
        for y in range(10, 22):
            half = 10.5 * math.sqrt(max(0.0, 1 - ((y - 15.0) / 6.5) ** 2))
            if half >= 1:
                rect(t, round(15.5 - half), y, round(15.5 + half - 1), y, 'sol_s')
        rect(t, 6, 14, 8, 15, 'sol'); rect(t, 23, 14, 25, 15, 'joint')
        # pattes arriere (deux petits piliers sombres de chaque cote)
        rect(t, 7, 19, 9, 22, 'sol'); rect(t, 22, 19, 24, 22, 'joint')
        # cou (8 px) -> poitrail -> pattes avant
        rows = {y: (12, 19) for y in range(0, 9)}
        for y in range(7, 21):
            half = 6.2 * math.sqrt(max(0.0, 1 - ((y - 13.5) / 7.0) ** 2))
            if half >= 1:
                rows[y] = (round(15.5 - max(half, 4)) if y < 11 else round(15.5 - half),
                           round(15.5 + max(half, 4) - 1) if y < 11 else round(15.5 + half - 1))
        stone_shade(t, rows)
        for y in range(17, 23):                     # pattes avant
            rect(t, 11, y, 14, y, 'sol_l'); rect(t, 11, y, 11, y, 'clair'); rect(t, 14, y, 14, y, 'sol')
            rect(t, 17, y, 20, y, 'sol'); rect(t, 17, y, 17, y, 'sol_l'); rect(t, 20, y, 20, y, 'sol_s')
        rect(t, 11, 22, 14, 22, 'sol_s'); rect(t, 17, 22, 20, 22, 'joint')
        rect(t, 14, 9, 17, 9, 'sol_s')
        # socle
        rect(t, 5, 23, 26, 24, 'clair'); rect(t, 5, 25, 26, 29, 'sol'); rect(t, 5, 25, 11, 25, 'sol_l')
        rect(t, 24, 25, 26, 29, 'sol_s'); rect(t, 5, 29, 26, 29, 'joint')
        rect(t, 15, 26, 16, 29, 'sol_s')
        for x, y in ((7, 26), (8, 27), (9, 27), (22, 26), (6, 28), (23, 22), (22, 21)):     # mousse
            px(t, x, y, 'vert' if (x + y) % 2 else 'vert_c')
        outline(t)
        for x in range(T):
            if t[0][x] == C['O']:
                t[0][x] = None
        rect(t, 6, 30, 25, 30, 'joint'); rect(t, 9, 31, 22, 31, 'joint')
    return t


def mousse(v):
    t = new()
    blobs = [(9, 10, 6), (18, 8, 5), (14, 17, 7), (24, 20, 5), (6, 22, 4)] if v == 0 else \
            [(7, 24, 5), (15, 22, 6), (23, 25, 4), (22, 9, 4), (10, 9, 3)]
    for cx, cy, r in blobs:
        ellipse(t, cx, cy, r, r * 0.75, 'vert')
    for cx, cy, r in blobs:
        ellipse(t, cx + r * 0.25, cy + r * 0.3, r * 0.6, r * 0.35, 'vert_s')
        ellipse(t, cx - r * 0.25, cy - r * 0.25, r * 0.45, r * 0.3, 'vert_c')
    rnd = random.Random(70 + v)
    for _ in range(10):
        x, y = rnd.randrange(32), rnd.randrange(32)
        if t[y][x] is not None:
            px(t, x, y, 'vert_c')
    outline(t, 'vert_s')
    return t


LEAF = ["..##.", ".###.", "####.", ".##.."]
LEAF2 = ["##...", ".###.", "..###", "...##"]


def feuilles(v):
    t = new()
    rnd = random.Random(30 + v)
    cols = ['vert_c', 'or_', 'orange'] if v == 0 else ['or_', 'orange', 'terre_c']
    spots = []
    while len(spots) < 6:
        x, y = rnd.randrange(1, 26), rnd.randrange(1, 27)
        if all(abs(x - a) > 6 or abs(y - b) > 5 for a, b in spots):
            spots.append((x, y))
    for i, (x, y) in enumerate(spots):
        shape = LEAF if i % 2 == 0 else LEAF2
        c = cols[i % 3]
        for j, row in enumerate(shape):
            for k, ch in enumerate(row):
                if ch == '#':
                    px(t, x + k, y + j, c)
        # nervure sombre + bord ombre
        px(t, x + 2, y + 1, 'racine_s'); px(t, x + 1, y + 2, 'racine_s')
    outline(t, 'racine_s')
    return t


DALLE_A = dalle(0)


def build():
    out = {}
    for v in range(3):
        out[v] = dalle(v)
    out[3] = dalle_fissuree(0)
    out[4] = dalle_fissuree(1)
    out[5] = terre()
    out[6], out[7], out[8] = racine('h'), racine('v'), racine('t')
    walls = {16: (1, 1, 0, 0), 17: (0, 0, 1, 1), 18: (1, 0, 1, 0), 19: (0, 1, 0, 1), 20: (1, 1, 1, 0),
             21: (1, 1, 0, 1), 22: (1, 0, 1, 1), 23: (0, 1, 1, 1), 24: (0, 0, 0, 1), 25: (0, 0, 1, 0),
             26: (0, 1, 0, 0), 27: (1, 0, 0, 0), 28: (1, 1, 1, 1), 29: (1, 0, 0, 1), 30: (0, 1, 1, 0)}
    for i, b in walls.items():
        out[i] = wall(b)
    for k, side in enumerate(('haut', 'bas', 'gauche', 'droite')):
        out[40 + k] = porte(side)
        out[44 + k] = porte_dessus(side)
    out[56], out[57] = escalier(True), escalier(False)
    holes = {58: (1, 1, 1, 1), 59: (0, 0, 1, 1), 60: (1, 1, 0, 0), 61: (0, 1, 0, 1), 62: (1, 0, 1, 0),
             63: (0, 0, 0, 1), 64: (0, 0, 1, 0), 65: (0, 1, 0, 0), 66: (1, 0, 0, 0)}
    for i, b in holes.items():
        out[i] = trou(b)
    out[72], out[73] = ronces_bloc(0), ronces_bloc(1)
    out[74], out[75] = ronces_sol(0), ronces_sol(1)
    edges = [(1, (0, 0, 1, 1)), (2, (1, 1, 0, 0)), (3, (0, 1, 0, 1)), (4, (1, 0, 1, 0)),
             (5, (0, 1, 1, 1)), (6, (1, 0, 1, 1)), (7, (1, 1, 0, 1)), (8, (1, 1, 1, 0)),
             (9, (0, 0, 0, 1)), (10, (0, 0, 1, 0)), (11, (0, 1, 0, 0)), (12, (1, 0, 0, 0))]
    for base, prof in ((80, False), (96, True)):
        out[base] = eau((1, 1, 1, 1), prof)
        for off, b in edges:
            out[base + off] = eau(b, prof)
    out[112], out[113] = colonne('haut'), colonne('base')
    out[114] = vase()
    out[115], out[116] = cerf('haut'), cerf('base')
    out[117], out[118] = mousse(0), mousse(1)
    out[119], out[120] = feuilles(0), feuilles(1)
    return out


def bloc_poussable():
    """Bloc de pierre claire poussable (art/puzzles/bloc_poussable.png) : dessus + face avant, poignees gravees
    et racine gravee sur le dessus, plus clair et plus chaud que les dalles et les murs."""
    t = new()
    # dessus (y3..13) et face avant (y14..28)
    rect(t, 3, 3, 28, 13, 'clair')
    rect(t, 3, 14, 28, 28, 'vase_c')
    rect(t, 3, 14, 28, 14, 'clair')                       # arete eclairee
    rect(t, 25, 14, 28, 28, 'sol_l')                      # flanc dans l'ombre
    rect(t, 26, 3, 28, 13, 'sol_l')
    rect(t, 3, 26, 28, 28, 'sol_l')                       # pied
    rect(t, 3, 3, 28, 3, 'C' if False else 'clair')
    # racine gravee sur le dessus (Y)
    for x, y in ((15, 5), (15, 6), (15, 7), (15, 8), (14, 9), (13, 10), (12, 11), (16, 9), (17, 10), (18, 11), (14, 8)):
        px(t, x, y, 'terre')
    for x, y in ((16, 5), (16, 6), (16, 7), (16, 8), (15, 9), (14, 10), (13, 11), (17, 9), (18, 10), (19, 11)):
        px(t, x, y, 'terre_c')
    # poignees gravees sur la face avant : deux encoches avec fleches vers l'exterieur
    for x0 in (6, 20):
        rect(t, x0, 18, x0 + 4, 22, 'terre_s')
        rect(t, x0 + 1, 19, x0 + 3, 21, 'racine_s')
        rect(t, x0, 23, x0 + 4, 23, 'clair')
    # petite mousse
    for x, y in ((4, 27), (5, 27), (5, 26), (27, 27)):
        px(t, x, y, 'vert')
    outline(t)
    rect(t, 4, 30, 28, 30, 'joint'); rect(t, 6, 31, 26, 31, 'joint')
    return t
