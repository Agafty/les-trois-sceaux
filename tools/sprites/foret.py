"""Tileset de la forêt (overworld nord-ouest + abords du Temple des Racines) — Les Trois Sceaux.

Usage : python tools/sprites/foret.py          -> DESSIN FINAL
        python tools/sprites/foret.py --plan   -> PLAN (aplats par famille + numéro de chaque tuile)
Le catalogue (ids, collisions, terrains) est identique dans les deux cas : seule l'image change.
Produit :
  art/tilesets/foret.png          planche 8 colonnes x 24 lignes de tuiles 32x32, sans marge ni espacement
  art/tilesets/foret_numeros.png  la même planche x2 avec le numéro de chaque tuile (aide au level design)
  art/tilesets/foret_apercu.png   scène d'exemple 20x11 agrandie x3 (contrôle des raccords)
  art/tilesets/foret_plan.md      tableau de chaque tuile (id, rôle, calque, collision)
  maps/tilesets/foret.tsx         tileset Tiled (collisions + terrains)

RÈGLE : ne jamais déplacer une tuile (les cartes mémorisent les numéros). Pour redessiner, modifier la
fonction de dessin en gardant l'id ; pour ajouter, utiliser une case « réserve » ou ajouter des lignes à la fin.

Terrains « par coins » (bits dans l'ordre HG, HD, BG, BD ; 1 = le terrain secondaire occupe ce coin).
Chaque terrain à deux couleurs a un bloc de 16 tuiles : id = base + (HG*8 + HD*4 + BG*2 + BD).
Sans Pillow : mini encodeur PNG (zlib + struct).
"""
import math
import os
import random
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
NAME = 'foret'
T, COLS, ROWS = 32, 8, 24
PLAN = '--plan' in sys.argv


def rgba(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


HEX = dict(
    O='#1b1420',
    # herbe
    g_hi='#8aba5c', g_lt='#6a9a48', g_md='#5a8a3c', g_dk='#3a5a2c', g_dp='#2c4a2c',
    # terre du chemin
    t_hi='#c88a58', t_lt='#b06e40', t_md='#8a5a34', t_dk='#5e3a22',
    # eau
    w_hi='#9ab8dc', w_lt='#6a8ec0', w_md='#3c5a8a', w_dk='#2c466e', d_md='#263a5e', d_dk='#1c2c4c', d_lt='#34507e',
    foam='#d4e0f0',
    # écorce / bois
    b_lt='#8a5a34', b_md='#6a4630', b_dk='#43291c', r_md='#7a4628', r_dk='#4a2a1c',
    # roche
    k_hi='#d8d4cc', k_lt='#b4aea4', k_md='#9a948c', k_dk='#5c5650',
    # falaise brun-gris
    c_lt='#a89a88', c_md='#7a6e62', c_dk='#524840',
    # pierre du temple (même famille que temple_racines)
    cap='#382e42', rim='#4e4058', face='#7a6a88', mur_c='#b8a8c0',
    # ronces de Morvath
    ronce='#241a22', ronce_m='#3a1a4a', ronce_c='#6a2a7a',
    # fleurs et divers
    f_white='#f0ece0', f_yel='#f0c840', f_red='#e2342c', f_vio='#a06ad0', orange='#f08a28', or_='#c8a050',
    cream='#d6c49c', plank='#a6764a', plank_d='#6a4630',
)
P = {k: rgba(v) for k, v in HEX.items()}


# ---------------------------------------------------------------- outils
class Cv:
    """Petit canevas RGBA (liste de lignes, None = transparent)."""

    def __init__(self, w=T, h=T, fill=None):
        self.w, self.h = w, h
        self.p = [[fill] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.p[y][x] = c

    def line(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.set(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def outline(self, c=None):
        c = c or P['O']
        pts = [(x, y) for y in range(self.h) for x in range(self.w) if self.p[y][x] is None and any(
            (self.get(x + dx, y + dy) not in (None, c)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in pts:
            self.p[y][x] = c

    def crop(self, ox, oy, w=T, h=T):
        return [row[ox:ox + w] for row in self.p[oy:oy + h]]


def rnd(x, y, seed=0):
    h = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffff) / 65535.0


def vnoise(x, y, period, seed):
    """Bruit de valeur périodique (période 32 px, donc raccord d'une tuile à sa voisine)."""
    cs = T / period
    gx, gy = (x + 0.5) / cs, (y + 0.5) / cs
    x0, y0 = int(math.floor(gx)), int(math.floor(gy))
    fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def v(i, j):
        return rnd(i % period, j % period, seed)
    a = v(x0, y0) * (1 - fx) + v(x0 + 1, y0) * fx
    b = v(x0, y0 + 1) * (1 - fx) + v(x0 + 1, y0 + 1) * fx
    return a * (1 - fy) + b * fy


def wset(t, x, y, c):
    t[y % T][x % T] = c


def mass(cv, circles, pal, seed=0, own_noise=0.30):
    """Remplit l'union d'ellipses (cx, cy, rx, ry) avec un ombrage lumière haut-gauche par ellipse (effet touffe)."""
    hi, lt, md, dk = pal
    for y in range(cv.h):
        for x in range(cv.w):
            best = None
            for (cx, cy, rx, ry) in circles:
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d = nx * nx + ny * ny
                if d <= 1 and (best is None or d < best[0]):
                    best = (d, nx, ny)
            if best is None:
                continue
            d, nx, ny = best
            v = -(nx + ny) * 0.55 + (rnd(x, y, seed) - 0.5) * own_noise - d * 0.15 + 0.1
            cv.p[y][x] = hi if v > 0.52 else lt if v > 0.12 else md if v > -0.32 else dk


def shadow(cv, cx, cy, rx, ry, c):
    for y in range(cv.h):
        for x in range(cv.w):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1 and (x + y) % 2 == 0:
                cv.p[y][x] = c


GRASS_PAL = (P['g_hi'], P['g_lt'], P['g_md'], P['g_dk'])
DARK_PAL = (P['g_lt'], P['g_md'], P['g_dk'], P['g_dp'])
BLACK_PAL = (P['ronce_c'], P['ronce_m'], P['ronce'], P['O'])
ROCK_PAL = (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk'])
BARK_PAL = (P['b_lt'], P['b_md'], P['b_dk'], P['O'])


# ---------------------------------------------------------------- textures périodiques 32x32
def grass(seed, kind='plain'):
    nseed = seed if kind == 'dark' else 1          # même fond pour toutes les variantes : pas de raccord visible
    t = [[P['g_md']] * T for _ in range(T)]
    lo, hi_ = (0.30, 0.64) if kind != 'dark' else (0.45, 0.80)
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, nseed) * 0.7 + vnoise(x, y, 8, nseed + 5) * 0.3
            if kind == 'dark':
                t[y][x] = P['g_dk'] if n < 0.62 else P['g_md']
            else:
                t[y][x] = P['g_lt'] if n > hi_ else P['g_dk'] if n < lo else P['g_md']
    r = random.Random(seed * 31 + 7)
    nblades = {'plain': 8, 'tufts': 16, 'clover': 7, 'stones': 6, 'dark': 10}.get(kind, 8)
    for _ in range(nblades):
        x, y = r.randrange(T), r.randrange(T)
        wset(t, x, y, P['g_dk'])
        wset(t, x - 1, y - 1, P['g_hi'])
        wset(t, x + 1, y - 1, P['g_hi'])
    if kind == 'clover':
        for _ in range(6):
            x, y = r.randrange(T), r.randrange(T)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                wset(t, x + dx, y + dy, P['g_hi'] if (dx + dy) % 2 == 0 else P['g_lt'])
    if kind == 'stones':
        for _ in range(4):
            x, y = r.randrange(T), r.randrange(T)
            wset(t, x, y, P['k_lt'])
            wset(t, x + 1, y, P['k_md'])
            wset(t, x, y + 1, P['k_dk'])
    if kind.startswith('fl_'):
        col = {'fl_white': P['f_white'], 'fl_yel': P['f_yel'], 'fl_red': P['f_red']}[kind]
        for _ in range(5):
            x, y = r.randrange(T), r.randrange(T)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                wset(t, x + dx, y + dy, col)
            wset(t, x, y, P['f_yel'] if kind != 'fl_yel' else P['orange'])
    return t


def path_tex(seed=11):
    t = [[P['t_md']] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, seed) * 0.7 + vnoise(x, y, 8, seed + 3) * 0.3
            t[y][x] = P['t_lt'] if n > 0.62 else P['t_dk'] if n < 0.26 else P['t_md']
    r = random.Random(seed)
    for _ in range(6):                      # petits cailloux
        x, y = r.randrange(T), r.randrange(T)
        wset(t, x, y, P['k_lt'])
        wset(t, x + 1, y, P['k_md'])
        wset(t, x, y + 1, P['t_dk'])
    for _ in range(7):                      # grains
        wset(t, r.randrange(T), r.randrange(T), P['t_hi'])
    return t


def water_tex(deep, seed=21):
    base, dk, lt = (P['d_md'], P['d_dk'], P['d_lt']) if deep else (P['w_md'], P['w_dk'], P['w_lt'])
    t = [[base] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, seed)
            if n < 0.3 and (x + y) % 2 == 0:
                t[y][x] = dk
    r = random.Random(seed)
    for _ in range(5 if deep else 7):       # petites vagues claires
        x, y = r.randrange(T), r.randrange(T)
        ln = r.choice((3, 4, 5))
        for i in range(ln):
            wset(t, x + i, y, lt if deep else P['w_hi'])
        wset(t, x - 1, y + 1, lt)
        wset(t, x + ln, y - 1, lt)
    return t


GRASS = {k: grass(s, k) for k, s in (('plain', 1), ('tufts', 2), ('clover', 3), ('stones', 4), ('dark', 5),
                                       ('fl_white', 6), ('fl_yel', 7), ('fl_red', 8))}
PATH = path_tex()
SHALLOW = water_tex(False)
DEEP = water_tex(True)


# ---------------------------------------------------------------- blocs de terrain (16 tuiles)
def corners(b):
    return (b >> 3) & 1, (b >> 2) & 1, (b >> 1) & 1, b & 1


def terrain_tile(b, A, B, rimA, rimB, seed, amp=0.085, pb=0.85):
    """Renvoie (image, masque) : masque True = terrain secondaire (B)."""
    hg, hd, bg, bd = corners(b)
    m = [[False] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            u, v = (x + 0.5) / T, (y + 0.5) / T
            f = (hg * (1 - u) + hd * u) * (1 - v) + (bg * (1 - u) + bd * u) * v
            f += (vnoise(x, y, 8, seed) - 0.5) * amp * 2 + (vnoise(x, y, 16, seed + 1) - 0.5) * amp
            m[y][x] = f > 0.5
    img = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            near = any(0 <= x + dx < T and 0 <= y + dy < T and m[y + dy][x + dx] != m[y][x]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if m[y][x]:
                c = B[y][x]
                if near and rimB:
                    c = rimB if (rimB and (rimA is None or rnd(x, y, seed) < pb)) else c
            else:
                c = A[y][x]
                if near and rimA and rnd(x, y, seed + 9) < 0.55:
                    c = rimA
            img[y][x] = c
    ms = [[False] * T for _ in range(T)]            # masque lisse pour le plan
    for y in range(T):
        for x in range(T):
            u, v = (x + 0.5) / T, (y + 0.5) / T
            ms[y][x] = (hg * (1 - u) + hd * u) * (1 - v) + (bg * (1 - u) + bd * u) * v > 0.5
    return img, ms


def quarter_rects(b):
    hg, hd, bg, bd = corners(b)
    if b == 15:
        return [(0, 0, 32, 32)]
    r = []
    if hg and hd:
        r.append((0, 0, 32, 16))
    elif hg or hd:
        r.append((0, 0, 16, 16) if hg else (16, 0, 16, 16))
    if bg and bd:
        r.append((0, 16, 32, 16))
    elif bg or bd:
        r.append((0, 16, 16, 16) if bg else (16, 16, 16, 16))
    if hg and bg and not hd and not bd:
        return [(0, 0, 16, 32)]
    if hd and bd and not hg and not bg:
        return [(16, 0, 16, 32)]
    return r


# ---------------------------------------------------------------- objets
def tree_small(v):
    cv = Cv()
    shadow(cv, 16, 28, 11, 3, P['g_dk'])
    cv.rect(13, 20, 18, 28, P['b_md'])
    cv.rect(13, 20, 14, 28, P['b_lt'])
    cv.rect(17, 20, 18, 28, P['b_dk'])
    cv.rect(11, 27, 20, 28, P['b_md'])
    cv.rect(11, 28, 12, 28, P['b_lt'])
    cv.rect(19, 28, 20, 28, P['b_dk'])
    if v == 0:
        circles = [(11, 10, 8, 7), (21, 10, 8, 7), (16, 7, 9, 7), (16, 15, 11, 8)]
    else:
        circles = [(16, 8, 11, 9), (10, 14, 8, 7), (22, 14, 8, 7)]
    mass(cv, circles, GRASS_PAL, 31 + v)
    cv.outline()
    return cv.p


def tree_dense(v):
    cv = Cv(fill=P['g_dp'])
    r = random.Random(100 + v)
    circles = []
    for _ in range(7):
        cx, cy, rad = r.uniform(0, 32), r.uniform(0, 32), r.uniform(6, 9)
        for ox in (-32, 0, 32):
            for oy in (-32, 0, 32):
                circles.append((cx + ox, cy + oy, rad, rad * 0.85))
    for y in range(T):
        for x in range(T):
            best = None
            for (cx, cy, rx, ry) in circles:
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d = nx * nx + ny * ny
                if d <= 1 and (best is None or d < best[0]):
                    best = (d, nx, ny)
            if best:
                d, nx, ny = best
                val = -(nx + ny) * 0.55 + (rnd(x, y, 5 + v) - 0.5) * 0.3 - d * 0.1
                cv.p[y][x] = P['g_lt'] if val > 0.45 else P['g_md'] if val > 0.0 else P['g_dk']
            elif (x + y) % 3 == 0:
                cv.p[y][x] = P['g_dk']
    return cv.p


def tree_black():
    cv = Cv()
    shadow(cv, 16, 28, 11, 3, P['ronce_m'])
    cv.rect(13, 18, 18, 28, P['ronce'])
    cv.rect(13, 18, 14, 28, P['ronce_m'])
    cv.rect(11, 27, 20, 28, P['ronce'])
    mass(cv, [(10, 11, 6, 6), (22, 10, 7, 6), (16, 8, 8, 6), (16, 15, 9, 6)], BLACK_PAL, 77, 0.5)
    for (x0, y0, x1, y1) in ((6, 14, 12, 20), (24, 13, 20, 19), (16, 4, 14, 10)):   # ronces tordues
        cv.line(x0, y0, x1, y1, P['ronce_c'])
    cv.outline(P['O'])
    return cv.p


def stump(hollow):
    cv = Cv()
    shadow(cv, 16, 26, 11, 3, P['g_dk'])
    cv.rect(8, 15, 23, 26, P['b_md'])
    for y in range(15, 27):
        cv.set(8, y, P['b_lt'])
        cv.set(9, y, P['b_lt'])
        cv.set(22, y, P['b_dk'])
        cv.set(23, y, P['b_dk'])
        if y % 3 == 0:
            cv.set(14, y, P['b_dk'])
            cv.set(18, y, P['b_lt'])
    for y in range(8, 20):
        for x in range(6, 26):
            if ((x - 15.5) / 9.5) ** 2 + ((y - 14) / 6) ** 2 <= 1:
                cv.p[y][x] = P['cream']
    for y in range(8, 20):
        for x in range(6, 26):
            d = ((x - 15.5) / 9.5) ** 2 + ((y - 14) / 6) ** 2
            if 0.62 < d <= 0.78:
                cv.p[y][x] = P['or_']
            if d > 0.92 and d <= 1:
                cv.p[y][x] = P['t_lt']
    if hollow:
        for y in range(10, 18):
            for x in range(9, 23):
                if ((x - 15.5) / 6.2) ** 2 + ((y - 14) / 3.4) ** 2 <= 1:
                    cv.p[y][x] = P['O']
        for x in range(11, 21):
            cv.set(x, 11, P['b_dk'])
    else:
        for x, y in ((13, 13), (14, 13), (15, 13), (16, 13), (17, 13), (13, 15), (18, 15), (15, 12), (16, 12)):
            cv.set(x, y, P['or_'])
    cv.outline()
    return cv.p


def log():
    cv = Cv()
    shadow(cv, 16, 26, 14, 3, P['g_dk'])
    for y in range(11, 25):
        for x in range(2, 30):
            if ((x - 15.5) / 14.5) ** 2 + ((y - 17.5) / 7.5) ** 2 <= 1.15 or 4 <= x <= 27:
                v = y - 11
                cv.p[y][x] = P['b_lt'] if v < 3 else P['b_md'] if v < 9 else P['b_dk']
    for x in range(6, 27, 5):
        cv.set(x, 14, P['b_dk'])
        cv.set(x + 1, 16, P['b_lt'])
    for y in range(12, 24):                     # bout coupé à gauche
        for x in range(2, 7):
            if ((x - 5) / 3.0) ** 2 + ((y - 17.5) / 6.2) ** 2 <= 1:
                cv.p[y][x] = P['cream']
    for y in range(14, 22):
        cv.set(4, y, P['or_'])
    for x in range(14, 20):                     # mousse
        cv.set(x, 11, P['g_md'])
        cv.set(x + 1, 12, P['g_lt'])
    cv.outline()
    return cv.p


def bush(v):
    cv = Cv()
    shadow(cv, 16, 26, 12, 3, P['g_dk'])
    mass(cv, [(10, 18, 8, 7), (22, 18, 8, 7), (16, 13, 10, 8), (16, 20, 12, 6)],
         DARK_PAL if v == 3 else GRASS_PAL, 41 + v, 0.5)
    r = random.Random(50 + v)
    if v == 2:                       # buisson fleuri
        for _ in range(7):
            x, y = r.randrange(7, 25), r.randrange(10, 23)
            if cv.p[y][x] is not None:
                cv.set(x, y, P['f_white'])
                cv.set(x + 1, y, P['f_vio'])
    if v == 3:                       # buisson à baies
        for _ in range(7):
            x, y = r.randrange(7, 25), r.randrange(10, 23)
            if cv.p[y][x] is not None:
                cv.set(x, y, P['f_red'])
                cv.set(x + 1, y + 1, P['ronce_m'])
    cv.outline()
    return cv.p


def rock(v):
    cv = Cv()
    shadow(cv, 16, 27, 13, 3, P['g_dk'])
    if v == 0:
        circles = [(16, 19, 12, 9), (9, 22, 7, 5)]
    elif v == 1:
        circles = [(11, 20, 9, 7), (22, 18, 8, 9), (17, 14, 7, 6)]
    else:
        circles = [(16, 19, 12, 9), (22, 21, 7, 5)]
    mass(cv, circles, ROCK_PAL, 60 + v, 0.35)
    for x0, y0, x1, y1 in ((12, 17, 16, 21), (20, 15, 18, 19)):     # fissures
        cv.line(x0, y0, x1, y1, P['k_dk'])
    if v == 2:                        # mousse sur le dessus
        for y in range(8, 24):
            for x in range(4, 28):
                if cv.p[y][x] is not None and y < 16 and rnd(x, y, 3) < 0.65:
                    cv.p[y][x] = P['g_md'] if rnd(x, y, 4) < 0.6 else P['g_lt']
    cv.outline()
    return cv.p


def brambles(v):
    cv = Cv()
    r = random.Random(200 + v)
    n = (7, 7, 12)[v]
    mass(cv, [(16, 16, 14, 13), (9, 12, 8, 8), (23, 20, 8, 8)] if v < 2 else [(16, 16, 15, 15)], BLACK_PAL, 90 + v, 0.6)
    for _ in range(n):               # tiges tordues
        x0, y0 = r.randrange(2, 30), r.randrange(2, 30)
        x1, y1 = x0 + r.randrange(-9, 10), y0 + r.randrange(-9, 10)
        cv.line(x0, y0, x1, y1, P['ronce_c'] if r.random() < 0.55 else P['ronce_m'])
        cv.set(x1 + 1, y1 - 1, P['ronce_c'])          # épine
    cv.outline()
    return cv.p


def bramble_floor():
    cv = Cv()
    r = random.Random(300)
    for _ in range(5):
        x0, y0 = r.randrange(3, 29), r.randrange(6, 28)
        x1, y1 = x0 + r.randrange(-10, 11), y0 + r.randrange(-6, 7)
        cv.line(x0, y0, x1, y1, P['ronce'])
        cv.set(x1, y1 - 1, P['ronce_c'])
        cv.set((x0 + x1) // 2, (y0 + y1) // 2 - 1, P['ronce_m'])
    return cv.p


def root(kind):
    cv = Cv()
    c, d = P['r_md'], P['r_dk']
    if kind == 'h':
        pts = [(0, 17), (6, 15), (12, 18), (19, 15), (25, 18), (31, 16)]
        for a, b in zip(pts, pts[1:]):
            for k in range(-1, 2):
                cv.line(a[0], a[1] + k, b[0], b[1] + k, c if k <= 0 else d)
    elif kind == 'v':
        pts = [(16, 0), (14, 6), (18, 12), (14, 19), (18, 25), (16, 31)]
        for a, b in zip(pts, pts[1:]):
            for k in range(-1, 2):
                cv.line(a[0] + k, a[1], b[0] + k, b[1], c if k <= 0 else d)
    else:
        cv.line(0, 16, 15, 16, c)
        cv.line(0, 17, 15, 17, c)
        cv.line(0, 18, 15, 18, d)
        cv.line(15, 0, 15, 15, c)
        cv.line(16, 0, 16, 15, c)
        cv.line(17, 0, 17, 15, d)
        for y in range(14, 22):
            for x in range(12, 22):
                if ((x - 16) / 5.0) ** 2 + ((y - 18) / 4.0) ** 2 <= 1:
                    cv.p[y][x] = c if (x + y) % 5 else d
        cv.line(16, 20, 26, 26, c)
        cv.line(16, 21, 26, 27, d)
        cv.line(15, 21, 8, 28, c)
    cv.outline()
    return cv.p


def flowers(color, seed):
    cv = Cv()
    r = random.Random(seed)
    for _ in range(5):
        x, y = r.randrange(3, 29), r.randrange(4, 28)
        cv.set(x, y + 1, P['g_dk'])
        cv.set(x, y + 2, P['g_dk'])
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.set(x + dx, y + dy, color)
        cv.set(x, y, P['f_yel'] if color != P['f_yel'] else P['orange'])
    return cv.p


def tall_grass():
    cv = Cv()
    r = random.Random(400)
    for _ in range(7):
        x, y = r.randrange(3, 29), r.randrange(10, 29)
        h = r.randrange(5, 10)
        for i in range(h):
            cv.set(x + (i // 4), y - i, P['g_lt'] if i > h // 2 else P['g_md'])
            cv.set(x + 1 + (i // 4), y - i, P['g_dk'])
    cv.outline(P['g_dp'])
    return cv.p


def mushrooms():
    cv = Cv()
    for (cx, cy, rr) in ((11, 20, 5), (22, 16, 4)):
        cv.rect(cx - 1, cy, cx + 1, cy + 5, P['cream'])
        cv.rect(cx + 1, cy + 1, cx + 1, cy + 5, P['or_'])
        for y in range(cy - rr, cy + 2):
            for x in range(cx - rr, cx + rr + 1):
                if ((x - cx) / rr) ** 2 + ((y - cy + 1) / (rr * 0.7)) ** 2 <= 1 and y <= cy + 1:
                    cv.p[y][x] = P['f_red'] if x < cx + rr - 1 else P['ronce_m']
        cv.set(cx - 1, cy - 2, P['f_white'])
        cv.set(cx + 2, cy - 1, P['f_white'])
    cv.outline()
    return cv.p


def pebbles():
    cv = Cv()
    for (cx, cy, rx, ry) in ((9, 20, 4, 3), (21, 14, 3, 3), (20, 24, 3, 2)):
        mass(cv, [(cx, cy, rx, ry)], ROCK_PAL, cx * 3, 0.2)
    cv.outline()
    return cv.p


def dead_leaves():
    cv = Cv()
    r = random.Random(500)
    for _ in range(12):
        x, y = r.randrange(2, 30), r.randrange(2, 30)
        c = r.choice((P['orange'], P['or_'], P['t_lt'], P['t_md']))
        cv.set(x, y, c)
        cv.set(x + 1, y, c)
        cv.set(x + 1, y + 1, P['t_dk'])
    return cv.p


# ---------------------------------------------------------------- grands arbres 2x2 (64x64)
def big_tree(kind, seed):
    cv = Cv(64, 64)
    black = kind == 'noir'
    dead = kind == 'mort'
    shadow(cv, 32, 58, 28, 5, P['ronce_m'] if black else P['g_dk'])
    bark = (P['ronce_m'], P['ronce'], P['O']) if black else (P['b_lt'], P['b_md'], P['b_dk'])
    for y in range(28 if not dead else 6, 64):
        hw = 8 + max(0, (y - 54)) * 2.0
        if dead:
            hw = 7 + max(0, (y - 54)) * 2.0
        for x in range(int(32 - hw), int(32 + hw) + 1):
            f = (x - (32 - hw)) / (2 * hw)
            col = bark[0] if f < 0.25 else bark[1] if f < 0.7 else bark[2]
            if (x * 5 + y * 3 + seed) % 11 == 0 and f > 0.2:
                col = bark[2]
            cv.set(x, y, col)
    if dead:
        r = random.Random(seed)
        for (x0, y0, x1, y1) in ((32, 22, 14, 8), (32, 22, 50, 6), (30, 30, 8, 20), (34, 28, 56, 18),
                                 (24, 14, 20, 4), (40, 12, 46, 2), (14, 8, 6, 4), (50, 6, 58, 8)):
            for k in (0, 1):
                cv.line(x0 + k, y0, x1 + k, y1, bark[0] if k == 0 else bark[1])
        for _ in range(7):
            x, y = r.randrange(6, 58), r.randrange(2, 28)
            if cv.get(x, y) is None:
                cv.set(x, y, P['or_'])
                cv.set(x + 1, y, P['orange'])
        cv.outline()
        return cv
    circles = [(14, 20, 13, 12), (50, 20, 13, 12), (32, 12, 17, 11), (24, 24, 15, 12), (42, 24, 15, 12),
               (32, 25, 25, 12), (10, 28, 8, 7), (54, 28, 8, 7)]
    if kind == 'b':
        circles = [(16, 18, 13, 12), (48, 18, 13, 12), (32, 11, 16, 10), (22, 26, 14, 11), (42, 26, 14, 11),
                   (32, 24, 26, 13), (32, 33, 14, 5)]
    pal = BLACK_PAL if black else GRASS_PAL if kind == 'a' else (P['g_hi'], P['g_lt'], P['g_md'], P['g_dk'])
    mass(cv, circles, pal, seed, 0.5)
    if black:
        r = random.Random(seed)
        for _ in range(9):
            x0, y0 = r.randrange(6, 58), r.randrange(4, 34)
            cv.line(x0, y0, x0 + r.randrange(-8, 9), y0 + r.randrange(-6, 7), P['ronce_c'])
    else:
        r = random.Random(seed)
        for _ in range(10):                  # petites fleurs / fruits dans le feuillage
            x, y = r.randrange(8, 56), r.randrange(8, 32)
            if cv.get(x, y) is not None and cv.get(x, y) != P['O']:
                cv.set(x, y, P['f_white'] if kind == 'a' else P['f_red'])
    cv.outline()
    return cv


# ---------------------------------------------------------------- falaise
def cliff_tile(kind, end):
    """kind : crete, face, pied ; end : '', 'g', 'd'."""
    cv = Cv(fill=None)
    g = GRASS['plain']
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    y_lip = 14 if kind == 'crete' else 0
    y_end = 31 if kind != 'pied' else 22
    for y in range(T):
        for x in range(T):
            inside = y_lip <= y <= y_end
            if end == 'g' and x < 3 + (1 if y in (y_lip, y_end) else 0) * 2:
                inside = False
            if end == 'd' and x > 28 - (1 if y in (y_lip, y_end) else 0) * 2:
                inside = False
            if not inside:
                continue
            yy = y - y_lip
            col = P['c_md']
            if kind == 'crete' and yy < 5:
                col = P['c_lt']                       # arête éclairée
            elif yy % 8 == 7 and kind != 'crete':
                col = P['c_dk']
            elif (x * 3 + yy * 7) % 17 == 0:
                col = P['c_lt']
            if (x + 5) % 9 == 0 and yy % 8 > 2 and yy % 8 < 6:
                col = P['c_dk']                       # fissures verticales
            if kind == 'pied' and y >= 19:
                col = P['c_dk']
            if end == 'g' and x < 6:
                col = P['c_lt'] if col != P['c_dk'] else col
            if end == 'd' and x > 25:
                col = P['c_dk']
            cv.p[y][x] = col
    # contour sombre autour de la roche
    ins = [[False] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            ins[y][x] = cv.p[y][x] in (P['c_md'], P['c_lt'], P['c_dk'])
    for y in range(T):
        for x in range(T):
            if not ins[y][x] and any(0 <= x + dx < T and 0 <= y + dy < T and ins[y + dy][x + dx]
                                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                if not (kind != 'pied' and y > y_end) and not (kind == 'face' and False):
                    cv.p[y][x] = P['O']
    if kind == 'crete':                                 # herbe qui déborde sur l'arête
        for x in range(T):
            if (end == 'g' and x < 4) or (end == 'd' and x > 27):
                continue
            if rnd(x, 1, 7) < 0.45:
                cv.p[y_lip - 2][x] = P['g_lt']
                cv.p[y_lip - 1][x] = P['g_dk']
    if kind == 'pied':
        for x in range(T):                              # touffes au pied
            if rnd(x, 2, 9) < 0.35 and not (end == 'g' and x < 4) and not (end == 'd' and x > 27):
                cv.p[23][x] = P['g_dk']
    return cv.p


def cliff_side(side):
    cv = Cv()
    g = GRASS['plain']
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    xs = range(0, 10) if side == 'g' else range(22, 32)
    for y in range(T):
        for x in xs:
            col = P['c_md']
            if (x == 0 and side == 'g') or (x == 31 and side == 'd'):
                col = P['c_dk']
            elif ((x - 2) // 3 + y // 5) % 3 == 0:
                col = P['c_lt']
            if (side == 'g' and x >= 7) or (side == 'd' and x <= 24):
                col = P['c_dk'] if (side == 'g' and x == 9) or (side == 'd' and x == 22) else P['c_md']
            cv.p[y][x] = col
    edge = 10 if side == 'g' else 21
    for y in range(T):
        cv.p[y][edge] = P['O']
    for y in range(T):
        if rnd(y, 3, 2) < 0.4:
            cv.p[y][edge + (1 if side == 'g' else -1)] = P['g_dk']
    return cv.p


def cliff_stairs():
    cv = Cv()
    g = GRASS['plain']
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    for y in range(T):
        for x in range(T):
            if x < 4 or x > 27:
                cv.p[y][x] = P['c_md'] if (x + y // 4) % 3 else P['c_lt']
            else:
                step = y % 8
                cv.p[y][x] = P['k_hi'] if step == 0 else P['k_lt'] if step < 5 else P['k_dk']
    for y in range(T):
        cv.p[y][3] = P['O']
        cv.p[y][28] = P['O']
    return cv.p


def bridge(horizontal):
    cv = Cv()
    if horizontal:
        for x in range(T):
            for y in range(5, 27):
                cv.p[y][x] = P['plank'] if x % 8 else P['plank_d']
                if (x + y) % 11 == 0:
                    cv.p[y][x] = P['t_lt']
        cv.rect(0, 3, 31, 5, P['b_md'])
        cv.rect(0, 26, 31, 28, P['b_dk'])
        cv.rect(0, 3, 31, 3, P['b_lt'])
        for x in (1, 17):
            cv.rect(x, 1, x + 2, 6, P['b_lt'])
            cv.rect(x, 25, x + 2, 30, P['b_md'])
    else:
        for y in range(T):
            for x in range(5, 27):
                cv.p[y][x] = P['plank'] if y % 8 else P['plank_d']
                if (x + y) % 11 == 0:
                    cv.p[y][x] = P['t_lt']
        cv.rect(3, 0, 5, 31, P['b_md'])
        cv.rect(26, 0, 28, 31, P['b_dk'])
        cv.rect(3, 0, 3, 31, P['b_lt'])
    cv.outline()
    return cv.p


# ---------------------------------------------------------------- entrée du temple (5x3 cases = 160x96)
def temple_entrance():
    W, H = 160, 96
    cv = Cv(W, H)
    # toit : pierre sombre en écailles
    for y in range(0, 24):
        for x in range(W):
            sc = (x + (6 if (y // 6) % 2 else 0)) % 12
            col = P['cap'] if sc != 0 and y % 6 != 0 else P['O']
            if (sc in (1, 2)) and y % 6 == 1:
                col = P['rim']
            cv.p[y][x] = col
    # corniche
    cv.rect(0, 24, W - 1, 25, P['mur_c'])
    cv.rect(0, 26, W - 1, 29, P['rim'])
    cv.rect(0, 30, W - 1, 31, P['cap'])
    # façade : briques
    for y in range(32, 96):
        for x in range(W):
            row = (y - 32) // 8
            off = 8 if row % 2 else 0
            yy = (y - 32) % 8
            xx = (x + off) % 16
            col = P['face']
            if yy == 7 or xx == 15:
                col = P['rim']
            elif yy == 0 or xx == 0:
                col = P['mur_c'] if (x * 3 + y) % 5 else P['face']
            cv.p[y][x] = col
    # ombre sous la corniche
    for x in range(W):
        cv.p[32][x] = P['cap']
        if x % 2 == 0:
            cv.p[33][x] = P['cap']
    # socle
    cv.rect(0, 88, W - 1, 95, P['rim'])
    for x in range(0, W, 16):
        cv.rect(x, 88, x, 95, P['cap'])
    cv.rect(0, 88, W - 1, 88, P['mur_c'])
    cv.rect(0, 95, W - 1, 95, P['O'])
    # médaillon central : disque de pierre clair avec bois de cerf
    cx, cy = 80, 12
    for y in range(0, 24):
        for x in range(68, 93):
            d = ((x - cx) / 11.5) ** 2 + ((y - cy) / 10.5) ** 2
            if d <= 1:
                cv.p[y][x] = P['O'] if d > 0.82 else P['mur_c'] if (x + y) % 7 else P['face']
    for (x0, y0, x1, y1) in ((80, 17, 80, 8), (80, 11, 74, 5), (80, 11, 86, 5), (77, 8, 74, 8), (83, 8, 86, 8),
                             (76, 7, 75, 3), (84, 7, 85, 3)):
        cv.line(x0, y0, x1, y1, P['cap'])
    # arche de l'entrée (ouverture de 20 px, centrée sur x = 80)
    for y in range(36, 96):
        for x in range(60, 101):
            hw_in = 10
            if y < 48:
                hw_in = math.sqrt(max(0, 100 - (48 - y) ** 2)) if 48 - y <= 10 else -1
            hw_fr = hw_in + 3 if hw_in >= 0 else (math.sqrt(max(0, 169 - (48 - y) ** 2)) if 48 - y <= 13 else -1)
            dx = abs(x + 0.5 - 80)
            if hw_fr >= 0 and dx <= hw_fr:
                cv.p[y][x] = P['mur_c'] if (x + y) % 6 else P['face']
                if dx > hw_fr - 1:
                    cv.p[y][x] = P['O']
            if hw_in >= 0 and dx <= hw_in:
                cv.p[y][x] = P['O']
    # clef de voûte
    cv.rect(77, 33, 82, 37, P['mur_c'])
    cv.rect(77, 33, 82, 33, P['O'])
    # intérieur : fond très sombre avec lueur verte au loin
    for y in range(52, 80):
        for x in range(72, 88):
            if abs(x - 80) < 4 and y < 70:
                cv.p[y][x] = P['cap'] if (x + y) % 2 else P['O']
    # marches devant la porte
    for (y0, y1, c) in ((82, 84, P['k_hi']), (85, 87, P['k_lt']), (89, 91, P['k_hi']), (92, 94, P['k_md'])):
        for y in range(y0, y1 + 1):
            for x in range(70, 90):
                cv.p[y][x] = c
    for y in range(82, 95):
        cv.p[y][69] = P['O']
        cv.p[y][90] = P['O']
    cv.rect(70, 88, 89, 88, P['O'])
    # racines qui descendent sur la façade, mousse
    r = random.Random(808)
    for x0 in (6, 22, 40, 56, 108, 124, 142, 152):
        y = 24
        x = x0
        length = r.randrange(26, 58)
        for i in range(length):
            cv.set(x, 26 + i, P['r_md'])
            cv.set(x + 1, 26 + i, P['r_dk'])
            if i % 7 == 6:
                x += r.choice((-1, 1))
        cv.set(x, 26 + length, P['r_dk'])
    for (x0, y0, x1, y1) in ((0, 54, 14, 62), (18, 62, 36, 66), (124, 60, 148, 56), (140, 68, 159, 78)):
        cv.line(x0, y0, x1, y1, P['r_md'])
        cv.line(x0, y0 + 1, x1, y1 + 1, P['r_dk'])
    for _ in range(60):          # mousse sur le toit et le socle
        x = r.randrange(W)
        y = r.choice((r.randrange(0, 23), r.randrange(84, 88)))
        if abs(x - 80) > 13 or y < 24:
            if cv.p[y][x] in (P['cap'], P['rim']):
                cv.p[y][x] = P['g_md'] if r.random() < 0.6 else P['g_dk']
    for _ in range(26):
        x, y = r.randrange(W), r.randrange(33, 86)
        if abs(x - 80) > 14 and cv.p[y][x] in (P['face'], P['mur_c']):
            cv.p[y][x] = P['g_md']
            cv.set(x + 1, y, P['g_dk'])
    # contour extérieur : bords haut, gauche et droite
    for x in range(W):
        cv.p[0][x] = P['O']
    for y in range(H):
        cv.p[y][0] = P['O']
        cv.p[y][W - 1] = P['O']
    return cv


def perron():
    cv = Cv(fill=P['k_md'])
    for y in range(T):
        for x in range(T):
            if y % 16 == 0 or (x + (8 if y >= 16 else 0)) % 16 == 0:
                cv.p[y][x] = P['k_dk']
            elif y % 16 == 1 or (x + (8 if y >= 16 else 0)) % 16 == 1:
                cv.p[y][x] = P['k_lt']
    for x, y in ((5, 6), (22, 24), (12, 21)):
        cv.set(x, y, P['g_md'])
        cv.set(x + 1, y, P['g_dk'])
    return cv.p


def dalle_chemin():
    """Dalle de pierre posée sur l'herbe (sentier vers le temple), tuile isolée sur fond d'herbe."""
    cv = Cv()
    g = GRASS['plain']
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    for (x0, y0, x1, y1) in ((3, 3, 28, 13), (3, 17, 14, 29), (18, 17, 29, 28)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                cv.p[y][x] = P['k_md']
                if y == y0 or x == x0:
                    cv.p[y][x] = P['k_hi']
                if y == y1 or x == x1:
                    cv.p[y][x] = P['k_dk']
        cv.p[y0][x0] = P['k_hi']
    return cv.p


# ---------------------------------------------------------------- catalogue
FULL = [(0, 0, 32, 32)]
TILES = {}
WANG = {}
GROUPS = []


def add(i, nom, role, calque, collision, img, cat, terrain=None, plan=None):
    assert i not in TILES and 0 <= i < COLS * ROWS, i
    TILES[i] = dict(nom=nom, role=role, calque=calque, collision=collision, img=img, cat=cat, plan=plan)
    if terrain:
        name, c = terrain
        WANG[name]['tiles'][i] = c


def group(titre, first, last):
    GROUPS.append((titre, first, last))


WANG['Chemin'] = dict(colors=[('herbe', '#5a8a3c'), ('terre', '#8a5a34')], tile=23, tiles={})
WANG['Eau'] = dict(colors=[('herbe', '#5a8a3c'), ('eau', '#3c5a8a')], tile=39, tiles={})
WANG['Eau profonde'] = dict(colors=[('eau', '#3c5a8a'), ('profonde', '#263a5e')], tile=55, tiles={})

POS = ('haut-gauche', 'haut-droite', 'bas-gauche', 'bas-droite')


def describe(b, name):
    c = corners(b)
    on = [POS[i] for i in range(4) if c[i]]
    if b == 0:
        return 'case entière du terrain principal'
    if b == 15:
        return f'case entière de {name}'
    if len(on) == 1:
        return f'coin {on[0]} seulement ({name} dans ce coin)'
    if len(on) == 2:
        if c[0] and c[1]:
            return f'{name} en haut (bord haut)'
        if c[2] and c[3]:
            return f'{name} en bas (bord bas)'
        if c[0] and c[2]:
            return f'{name} à gauche (bord gauche)'
        if c[1] and c[3]:
            return f'{name} à droite (bord droit)'
        return f'deux coins opposés ({" et ".join(on)})'
    free = [POS[i] for i in range(4) if not c[i]][0]
    return f'{name} partout sauf le coin {free} (coin rentrant)'


def NAME_SUFFIX(b):
    return '%d%d%d%d' % corners(b)


def build_blocks():
    # Herbe (ligne 0)
    herbes = [('herbe_a', 'plain', 'Herbe de base'), ('herbe_b', 'tufts', 'Herbe avec touffes'),
              ('herbe_c', 'clover', 'Herbe avec trèfles'), ('herbe_d', 'stones', 'Herbe avec petits cailloux'),
              ('herbe_fleurs_blanches', 'fl_white', 'Herbe parsemée de fleurs blanches'),
              ('herbe_fleurs_jaunes', 'fl_yel', 'Herbe parsemée de fleurs jaunes'),
              ('herbe_fleurs_rouges', 'fl_red', 'Herbe parsemée de fleurs rouges'),
              ('herbe_sombre', 'dark', 'Herbe sombre de sous-bois (près des grands arbres et du temple)')]
    group('1. Herbe', 0, 7)
    for i, (nom, kind, role) in enumerate(herbes):
        add(i, nom, role, 'Sol', None, GRASS[kind], 'herbe')
        if i <= 6:
            for w in ('Chemin', 'Eau'):
                WANG[w]['tiles'][i] = (1, 1, 1, 1)
    # Chemin
    group('2. Chemin de terre', 8, 23)
    for b in range(16):
        img, m = terrain_tile(b, GRASS['plain'], PATH, P['g_dk'], P['t_dk'], 11)
        add(8 + b, 'herbe_chemin' if b == 0 else 'chemin_plein' if b == 15 else f'chemin_{NAME_SUFFIX(b)}',
            'Herbe (même dessin que herbe_a, sert de base au terrain Chemin)' if b == 0
            else 'Terre battue, case entière' if b == 15 else 'Chemin : ' + describe(b, 'terre'),
            'Sol', None, img, 'terre', ('Chemin', tuple(2 if k else 1 for k in corners(b))), plan=(m, P['g_md'], P['t_md']))
    # Eau peu profonde
    group('3. Eau peu profonde (rivière, mare)', 24, 39)
    for b in range(16):
        img, m = terrain_tile(b, GRASS['plain'], SHALLOW, P['g_dk'], P['foam'], 21, pb=0.55)
        add(24 + b, 'herbe_rive' if b == 0 else 'eau' if b == 15 else f'eau_{NAME_SUFFIX(b)}',
            'Herbe (base du terrain Eau)' if b == 0 else 'Eau peu profonde, case entière (Brann la traverse)' if b == 15
            else 'Rive : ' + describe(b, 'eau'),
            'Sol', None, img, 'eau', ('Eau', tuple(2 if k else 1 for k in corners(b))), plan=(m, P['g_md'], P['w_md']))
    # Eau profonde
    group('4. Eau profonde (infranchissable)', 40, 55)
    for b in range(16):
        img, m = terrain_tile(b, SHALLOW, DEEP, P['foam'], P['d_dk'], 31, 0.07, pb=1.0)
        add(40 + b, 'eau_pour_profonde' if b == 0 else 'eau_profonde' if b == 15 else f'eau_profonde_{NAME_SUFFIX(b)}',
            'Eau peu profonde (base du terrain Eau profonde)' if b == 0 else 'Eau profonde, case entière (infranchissable)'
            if b == 15 else 'Eau profonde : ' + describe(b, 'eau profonde'),
            'Sol' if b == 0 else 'Murs', quarter_rects(b) if b else None, img, 'profonde',
            ('Eau profonde', tuple(2 if k else 1 for k in corners(b))), plan=(m, P['w_md'], P['d_md']))


def build_objects():
    # Falaise (lignes 7-8)
    group('5. Falaise, talus, pont', 56, 71)
    for k, (nom, kind, end, role, col) in enumerate([
            ('falaise_crete', 'crete', '', 'Haut de falaise : herbe du plateau + arête (la moitié basse est solide)', [(0, 16, 32, 16)]),
            ('falaise_crete_g', 'crete', 'g', 'Haut de falaise, extrémité gauche', [(3, 16, 29, 16)]),
            ('falaise_crete_d', 'crete', 'd', 'Haut de falaise, extrémité droite', [(0, 16, 29, 16)]),
            ('falaise_face', 'face', '', 'Face de falaise (roche verticale)', FULL),
            ('falaise_face_g', 'face', 'g', 'Face de falaise, extrémité gauche', [(3, 0, 29, 32)]),
            ('falaise_face_d', 'face', 'd', 'Face de falaise, extrémité droite', [(0, 0, 29, 32)]),
            ('falaise_pied', 'pied', '', 'Pied de falaise (ombre + herbe en bas)', [(0, 0, 32, 24)]),
            ('falaise_pied_g', 'pied', 'g', 'Pied de falaise, extrémité gauche', [(3, 0, 29, 24)]),
            ('falaise_pied_d', 'pied', 'd', 'Pied de falaise, extrémité droite', [(0, 0, 29, 24)])]):
        add(56 + k, nom, role, 'Murs', col, cliff_tile(kind, end), 'falaise')
    add(65, 'falaise_cote_g', 'Falaise verticale vue de côté : roche à gauche, plateau/herbe à droite', 'Murs', [(0, 0, 12, 32)], cliff_side('g'), 'falaise')
    add(66, 'falaise_cote_d', 'Falaise verticale vue de côté : roche à droite, herbe à gauche', 'Murs', [(20, 0, 12, 32)], cliff_side('d'), 'falaise')
    add(67, 'falaise_escalier', 'Escalier taillé dans la falaise (à poser à la place de falaise_face ; passage libre)', 'Sol', None, cliff_stairs(), 'falaise')
    add(68, 'pont_h', 'Pont de planches horizontal (au-dessus de l\'eau profonde : poser sur Decor et effacer la tuile solide du calque Murs dessous)', 'Decor', None, bridge(True), 'pont')
    add(69, 'pont_v', 'Pont de planches vertical (même remarque)', 'Decor', None, bridge(False), 'pont')
    # Arbres (ligne 9, grands arbres lignes 10-11)
    group('6. Arbres, souches', 72, 79)
    tr = [(5, 8, 22, 22)]
    add(72, 'arbre_petit_a', 'Arbre 1×1 (tronc + cime ronde), solide', 'Murs', tr, tree_small(0), 'arbre')
    add(73, 'arbre_petit_b', 'Arbre 1×1, variante (cime plus large)', 'Murs', tr, tree_small(1), 'arbre')
    add(74, 'arbre_dense_a', 'Feuillage dense case pleine (bordure de forêt infranchissable, se pose côte à côte)', 'Murs', FULL, tree_dense(0), 'arbre')
    add(75, 'arbre_dense_b', 'Feuillage dense case pleine, variante', 'Murs', FULL, tree_dense(1), 'arbre')
    add(76, 'arbre_noirci', 'Arbre 1×1 corrompu par les ronces noires de Morvath (abords du temple), solide', 'Murs', tr, tree_black(), 'ronce')
    add(77, 'souche', 'Souche d\'arbre, solide', 'Murs', [(6, 12, 20, 16)], stump(False), 'arbre')
    add(78, 'souche_creuse', 'Souche creuse (cachette : à cacher derrière des buissons ; l\'objet est un Ramassable posé dessus)', 'Murs', [(6, 12, 20, 16)], stump(True), 'arbre')
    add(79, 'tronc_couche', 'Tronc couché horizontal, solide', 'Murs', [(2, 10, 28, 16)], log(), 'arbre')
    group('7. Gros arbres 2×2', 80, 95)
    for (c0, kind, seed, nom, txt) in ((0, 'a', 3, 'gros_arbre_a', 'Gros arbre vert'), (2, 'b', 4, 'gros_arbre_b', 'Gros arbre vert (variante)'),
                                       (4, 'noir', 5, 'gros_arbre_noirci', 'Gros arbre corrompu (ronces noires)'),
                                       (6, 'mort', 6, 'gros_arbre_mort', 'Gros arbre mort, sans feuilles')):
        big = big_tree(kind, seed)
        names = (('cime_hg', 'cime gauche (Dessus)'), ('cime_hd', 'cime droite (Dessus)'),
                 ('tronc_g', 'tronc gauche (Murs, solide)'), ('tronc_d', 'tronc droit (Murs, solide)'))
        for k, (suf, desc) in enumerate(names):
            cx_, cy_ = k % 2, k // 2
            i = 80 + c0 + cx_ + cy_ * 8
            top = cy_ == 0
            col = None if top else ([(14, 4, 18, 28)] if cx_ == 0 else [(0, 4, 18, 28)])
            add(i, f'{nom}_{suf}', f'{txt}, {desc}', 'Dessus' if top else 'Murs', col, big.crop(cx_ * 32, cy_ * 32), 'arbre' if kind != 'noir' else 'ronce')
    # Buissons, rochers, ronces
    group('8. Buissons, rochers', 96, 103)
    bc = [(2, 6, 28, 24)]
    for v, (nom, txt) in enumerate((('buisson_a', 'Buisson, solide (coupable plus tard)'), ('buisson_b', 'Buisson, variante'),
                                    ('buisson_fleuri', 'Buisson à fleurs blanches et violettes'), ('buisson_baies', 'Buisson sombre à baies rouges'))):
        add(96 + v, nom, txt, 'Murs', bc, bush(v), 'buisson')
    add(100, 'rocher_a', 'Rocher gris, solide', 'Murs', bc, rock(0), 'rocher')
    add(101, 'rocher_b', 'Gros rocher en deux blocs, solide', 'Murs', bc, rock(1), 'rocher')
    add(102, 'rocher_mousse', 'Rocher couvert de mousse, solide', 'Murs', bc, rock(2), 'rocher')
    add(103, 'reserve_103', 'Réserve (vide)', 'Murs', None, None, None)
    # Entrée du temple + ronces + racines + dalles
    group('9. Entrée du Temple des Racines (5×3), ronces, racines', 104, 127)
    ent = temple_entrance()
    full = FULL
    door = [(0, 0, 6, 32), (26, 0, 6, 32)]
    en_names = [['toit_g', 'toit', 'toit_centre', 'toit', 'toit_d'],
                ['mur_haut_g', 'mur_haut', 'linteau', 'mur_haut', 'mur_haut_d'],
                ['mur_bas_g', 'mur_bas', 'porte', 'mur_bas', 'mur_bas_d']]
    en_roles = [['Toit de la façade, extrémité gauche', 'Toit de la façade (pierre sombre en écailles, corniche)',
                 'Toit, centre : médaillon à bois de cerf', 'Toit de la façade', 'Toit de la façade, extrémité droite'],
                ['Façade haute, extrémité gauche (racines)', 'Façade haute en pierre taillée',
                 'Linteau : arche au-dessus de la porte (solide ; Brann n\'y entre pas)', 'Façade haute en pierre taillée',
                 'Façade haute, extrémité droite'],
                ['Façade basse + socle, extrémité gauche', 'Façade basse + socle',
                 'PORTE d\'ENTRÉE (1 case) : ouverture de 20 px, marches ; l\'objet Sortie se pose dessus',
                 'Façade basse + socle', 'Façade basse + socle, extrémité droite']]
    for ry in range(3):
        for rx in range(5):
            col = door if (ry == 2 and rx == 2) else full
            add(104 + rx + ry * 8, f'entree_{en_names[ry][rx]}' if (ry, rx) != (2, 2) else 'entree_porte',
                en_roles[ry][rx], 'Murs', col, ent.crop(rx * 32, ry * 32), 'facade')
    add(109, 'ronces_a', 'Bloc de ronces noires (infranchissable), comme dans le temple', 'Murs', full, brambles(0), 'ronce')
    add(110, 'ronces_b', 'Bloc de ronces noires, variante', 'Murs', full, brambles(1), 'ronce')
    add(111, 'ronces_epaisses', 'Ronces noires épaisses, case pleine', 'Murs', full, brambles(2), 'ronce')
    add(117, 'ronces_sol', 'Ronces rampantes au sol (décor, sans collision)', 'Decor', None, bramble_floor(), 'ronce')
    add(118, 'racine_h', 'Racine horizontale sur l\'herbe (se raccorde à gauche et à droite)', 'Decor', None, root('h'), 'racine')
    add(119, 'racine_v', 'Racine verticale sur l\'herbe', 'Decor', None, root('v'), 'racine')
    add(125, 'racine_noeud', 'Nœud de racines (départ ou fin d\'une racine)', 'Decor', None, root('n'), 'racine')
    add(126, 'perron', 'Dalles de pierre devant la porte du temple (sol)', 'Sol', None, perron(), 'facade')
    add(127, 'dalle_chemin', 'Dalle de pierre isolée sur l\'herbe (sentier vers le temple)', 'Sol', None, dalle_chemin(), 'facade')
    for i in (112 + 5 - 5 - 0,):
        pass
    # Décor (ligne 16-17)
    group('10. Petits décors (calque Decor, sans collision)', 128, 135)
    add(128, 'fleurs_blanches', 'Fleurs blanches (posées sur l\'herbe)', 'Decor', None, flowers(P['f_white'], 1), 'decor')
    add(129, 'fleurs_jaunes', 'Fleurs jaunes', 'Decor', None, flowers(P['f_yel'], 2), 'decor')
    add(130, 'fleurs_rouges', 'Fleurs rouges', 'Decor', None, flowers(P['f_red'], 3), 'decor')
    add(131, 'fleurs_violettes', 'Fleurs violettes', 'Decor', None, flowers(P['f_vio'], 4), 'decor')
    add(132, 'herbes_hautes', 'Touffes d\'herbe haute', 'Decor', None, tall_grass(), 'decor')
    add(133, 'champignons', 'Champignons rouges', 'Decor', None, mushrooms(), 'decor')
    add(134, 'cailloux', 'Petits cailloux', 'Decor', None, pebbles(), 'decor')
    add(135, 'feuilles_mortes', 'Feuilles mortes', 'Decor', None, dead_leaves(), 'decor')


# ---------------------------------------------------------------- export PNG
def save_png(path, pix, scale=1):
    h, w = len(pix), len(pix[0])
    raw = bytearray()
    for y in range(h):
        row = bytearray()
        for x in range(w):
            row += bytes(pix[y][x] or (0, 0, 0, 0)) * scale
        for _ in range(scale):
            raw.append(0)
            raw += row

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(data)


DIGITS = {'0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111',
          '4': '101101111001001', '5': '111100111001111', '6': '111100111101111', '7': '111001001001001',
          '8': '111101111101111', '9': '111101111001111'}


def stamp_number(pix, ox, oy, n, scale=1):
    s = str(n)
    w = len(s) * 4 * scale + scale
    for y in range(5 * scale + 2):
        for x in range(w):
            if 0 <= oy + y < len(pix) and 0 <= ox + x < len(pix[0]):
                pix[oy + y][ox + x] = rgba('#000000')
    for k, ch in enumerate(s):
        for j in range(15):
            if DIGITS[ch][j] == '1':
                for sy in range(scale):
                    for sx in range(scale):
                        px_, py_ = ox + 1 + k * 4 * scale + (j % 3) * scale + sx, oy + 1 + (j // 3) * scale + sy
                        if 0 <= py_ < len(pix) and 0 <= px_ < len(pix[0]):
                            pix[py_][px_] = rgba('#ffff40')


CAT_COL = dict(herbe='#6aa04a', terre='#b07a48', eau='#4a78c0', profonde='#24407a', arbre='#2f6a30', buisson='#4a8a3a',
               rocher='#9a948c', falaise='#8a7a6a', facade='#8a78a0', ronce='#6a2a7a', racine='#7a4628',
               decor='#e8c040', pont='#a6764a')


def plan_image(d):
    if d['plan']:
        m, ca, cb = d['plan']
        return [[cb if m[y][x] else ca for x in range(T)] for y in range(T)]
    col = rgba(CAT_COL[d['cat']])
    if d['nom'] == 'entree_porte':
        col = rgba('#1b1420')
    elif d['nom'] == 'entree_linteau':
        col = rgba('#5a4a70')
    dark = tuple(int(c * 0.55) for c in col[:3]) + (255,)
    img = [[(col if (x + y) % 2 or d['calque'] == 'Murs' else col) if d['img'][y][x] is not None else None
            for x in range(T)] for y in range(T)]
    for y in range(T):
        for x in range(T):
            if img[y][x] and any(not (0 <= x + dx < T and 0 <= y + dy < T) or d['img'][y + dy][x + dx] is None
                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                img[y][x] = dark
    return img


def build_sheet(plan=False, numbers=False, scale=1):
    sheet = [[None] * (COLS * T) for _ in range(ROWS * T)]
    for i, d in TILES.items():
        if d['img'] is None:
            continue
        img = plan_image(d) if plan else d['img']
        for y in range(T):
            for x in range(T):
                if img[y][x] is not None:
                    sheet[(i // COLS) * T + y][(i % COLS) * T + x] = img[y][x]
    if scale > 1:
        out = [[None] * (COLS * T * scale) for _ in range(ROWS * T * scale)]
        for y in range(ROWS * T * scale):
            for x in range(COLS * T * scale):
                out[y][x] = sheet[y // scale][x // scale]
        sheet = out
    if plan or numbers:
        for i, d in TILES.items():
            if d['img'] is not None:
                stamp_number(sheet, (i % COLS) * T * scale + 1, (i // COLS) * T * scale + 1, i, scale if not plan else 1)
    return sheet


# ---------------------------------------------------------------- export TSX
def collision_xml(rects):
    s = '  <objectgroup draworder="index" id="2">\n'
    for k, (x, y, w, h) in enumerate(rects, 1):
        s += f'   <object id="{k}" x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
    return s + '  </objectgroup>\n'


def wangid(c):
    hg, hd, bg, bd = c
    return f'0,{hd},0,{bd},0,{bg},0,{hg}'


def build_tsx():
    s = ('<?xml version="1.0" encoding="UTF-8"?>\n'
         f'<tileset version="1.10" tiledversion="1.12.2" name="{NAME}" tilewidth="{T}" tileheight="{T}" '
         f'tilecount="{COLS * ROWS}" columns="{COLS}">\n'
         f' <image source="../../art/tilesets/{NAME}.png" width="{COLS * T}" height="{ROWS * T}"/>\n')
    for i in sorted(TILES):
        if TILES[i]['collision']:
            s += f' <tile id="{i}">\n' + collision_xml(TILES[i]['collision']) + ' </tile>\n'
    s += ' <wangsets>\n'
    for name, w in WANG.items():
        s += f'  <wangset name="{name}" type="corner" tile="{w["tile"]}">\n'
        for cname, ccol in w['colors']:
            s += f'   <wangcolor name="{cname}" color="{ccol}" tile="-1" probability="1"/>\n'
        for i in sorted(w['tiles']):
            s += f'   <wangtile tileid="{i}" wangid="{wangid(w["tiles"][i])}"/>\n'
        s += '  </wangset>\n'
    s += ' </wangsets>\n</tileset>\n'
    return s


def collision_txt(r):
    if not r:
        return 'aucune'
    if r == FULL:
        return 'pleine'
    return 'partielle : ' + ' ; '.join(f'{x},{y} {w}×{h}' for x, y, w, h in r)


def build_md():
    o = [f'# Plan du tileset `{NAME}` — forêt (overworld nord-ouest et abords du Temple des Racines)', '',
         '> Fichier généré par `tools/sprites/foret.py` : modifier le script, pas ce fichier.', '',
         f'- Image : `art/tilesets/{NAME}.png`, {COLS * T}×{ROWS * T} px, {COLS} colonnes × {ROWS} lignes de tuiles 32×32, '
         f'sans marge ni espacement ({COLS * ROWS} cases). Tileset Tiled : `maps/tilesets/{NAME}.tsx` (collisions et terrains définis).',
         '- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro : '
         'le dessin remplace le plan au même emplacement. Lignes 17 à 24 (ids 136 à 191) : réserve vide, pour les ajouts. '
         'La planche `art/tilesets/foret_numeros.png` montre le numéro de chaque tuile.',
         '- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px. Collisions en pixels dans la tuile '
         '(x,y largeur×hauteur, origine en haut à gauche).',
         '- Calques : `Sol` = herbe, chemin, eau ; `Decor` = petits décors sans collision ; `Murs` = tout ce qui bloque ; '
         '`Dessus` = cimes des gros arbres (passent devant Brann).', '']
    for titre, a, b in GROUPS:
        o += [f'## {titre}', '', '| N° | Nom | Rôle | Calque | Collision |', '| --- | --- | --- | --- | --- |']
        for i in range(a, b + 1):
            if i in TILES and TILES[i]['img'] is not None:
                d = TILES[i]
                o.append(f'| {i} | `{d["nom"]}` | {d["role"]} | {d["calque"]} | {collision_txt(d["collision"])} |')
        o.append('')
    o += ['## Assemblages à connaître (à poser avec le pinceau « tampon »)', '',
          '| Assemblage | Tuiles (ligne par ligne) | Calques |', '| --- | --- | --- |',
          '| **Entrée du Temple des Racines**, 5×3 cases | `104 105 106 107 108` / `112 113 114 115 116` / `120 121 122 123 124` | Murs (tout) ; l\'objet `Sortie` sur la case 122 (porte), le Spawn d\'arrivée juste en dessous sur `126` (perron) |',
          '| Gros arbre vert 2×2 | `80 81` / `88 89` | cime (80, 81) sur `Dessus`, tronc (88, 89) sur `Murs` |',
          '| Gros arbre vert, variante | `82 83` / `90 91` | idem |',
          '| Gros arbre corrompu | `84 85` / `92 93` | idem |',
          '| Gros arbre mort | `86 87` / `94 95` | idem |',
          '| Falaise de 3 cases de haut | `56` / `59` / `62` (+ `57 60 63` extrémité gauche, `58 61 64` extrémité droite) | Murs |',
          '| Rivière traversable en pont | eau profonde (terrain) puis `68` ou `69` sur `Decor` | pont sur Decor ; retirer la tuile de Murs sous le pont |', '',
          '## Terrains (Wang, par coins)', '',
          'Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain est un bloc de 16 tuiles : '
          'id = base + (HG×8 + HD×4 + BG×2 + BD) avec 1 = terrain secondaire dans ce coin.', '',
          '| Terrain | Couleurs (1 / 2) | Calque | Tuiles |', '| --- | --- | --- | --- |',
          '| `Chemin` | herbe / terre | Sol | 0–6 (herbe), 8–23 |',
          '| `Eau` | herbe / eau peu profonde | Sol | 0–6 (herbe), 24–39 |',
          '| `Eau profonde` | eau peu profonde / eau profonde | Murs (sauf la tuile 40) | 39 ou 40 (eau), 41–55 |', '',
          'Astuce : peindre d\'abord l\'herbe (tuiles 0 à 7 au hasard), puis le terrain Chemin ou Eau dessus, puis Eau profonde au milieu de l\'eau.', '']
    return '\n'.join(o)


# ---------------------------------------------------------------- aperçu 20x11 x3
def preview():
    """Scène d'exemple 20x11 : herbe, chemin, rivière avec pont, falaise, arbres, entrée du temple."""
    W, H = 20, 11
    layers = {'sol': [[None] * W for _ in range(H)], 'deco': [[None] * W for _ in range(H)],
              'murs': [[None] * W for _ in range(H)], 'dessus': [[None] * W for _ in range(H)]}
    for y in range(H):
        for x in range(W):
            layers['sol'][y][x] = [0, 1, 0, 2, 3, 0, 1, 0, 0, 7, 0, 6][(x * 7 + y * 3) % 12] if (x * 5 + y) % 11 else 4

    def terrain(base, cells, key='sol'):
        g = [[False] * (W + 1) for _ in range(H + 1)]
        for (x0, y0, x1, y1) in cells:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    g[y][x] = True
        for y in range(H):
            for x in range(W):
                b = g[y][x] * 8 + g[y][x + 1] * 4 + g[y + 1][x] * 2 + g[y + 1][x + 1]
                if b:
                    layers[key][y][x] = base + b
    terrain(8, [(9, 4, 11, 11), (2, 8, 11, 10)])                      # chemin (coins du maillage)
    terrain(24, [(14, 0, 19, 4), (15, 5, 19, 11)])                     # rivière
    terrain(40, [(15, 1, 18, 3), (16, 6, 19, 9)], 'murs')              # eau profonde
    for x in range(15, 20):
        layers['deco'][4][x] = 68
    for x in (1, 2, 3):                                                 # falaise basse en bas à gauche
        layers['murs'][2][x] = 59 if x not in (1, 3) else (60 if x == 1 else 61)
    layers['murs'][1][1], layers['murs'][1][2], layers['murs'][1][3] = 57, 56, 58
    layers['murs'][3][1], layers['murs'][3][2], layers['murs'][3][3] = 63, 62, 64
    layers['murs'][2][2] = 67
    for ry in range(3):                                                 # entrée du temple
        for rx in range(5):
            layers['murs'][ry][5 + rx] = 104 + rx + ry * 8
    layers['sol'][3][7] = 126
    layers['sol'][3][8] = 126 if False else layers['sol'][3][8]
    for x in range(0, 5):
        layers['murs'][0][x] = 74 if x % 2 else 75
    for x in range(10, 14):
        layers['murs'][0][x] = 75 if x % 2 else 74
    layers['murs'][1][10] = 76
    layers['murs'][2][4] = 76
    layers['murs'][2][10] = 109
    layers['deco'][3][4] = 117
    layers['deco'][3][9] = 118
    layers['deco'][3][10] = 119
    for i, (x, y) in {72: (12, 3), 73: (6, 6), 96: (7, 5), 97: (8, 5), 100: (13, 7), 101: (4, 6), 102: (12, 9), 77: (13, 6), 78: (14, 6),
                      98: (1, 6), 99: (5, 9), 79: (7, 9)}.items():
        layers['murs'][y][x] = i
    for i, (x, y) in {133: (3, 4), 129: (12, 4), 128: (6, 5), 130: (7, 8), 132: (8, 7), 131: (1, 9), 135: (11, 8), 134: (6, 3)}.items():
        layers['deco'][y][x] = i
    for c, (gx, gy) in ((80, (1, 4)), (82, (12, 5)), (84, (15, 9))):    # gros arbres 2x2 (cime sur Dessus)
        layers['dessus'][gy][gx], layers['dessus'][gy][gx + 1] = c, c + 1
        layers['murs'][gy + 1][gx], layers['murs'][gy + 1][gx + 1] = c + 8, c + 9
    px_ = [[None] * (W * T) for _ in range(H * T)]
    for key in ('sol', 'deco', 'murs', 'dessus'):
        for gy in range(H):
            for gx in range(W):
                i = layers[key][gy][gx]
                if i is None or TILES[i]['img'] is None:
                    continue
                d = TILES[i]['img']
                for y in range(T):
                    for x in range(T):
                        if d[y][x] is not None:
                            px_[gy * T + y][gx * T + x] = d[y][x]
    return px_


def main():
    build_blocks()
    build_objects()
    out_t = os.path.join(ROOT, 'art', 'tilesets')
    os.makedirs(out_t, exist_ok=True)
    save_png(os.path.join(out_t, f'{NAME}.png'), build_sheet(plan=PLAN))
    save_png(os.path.join(out_t, f'{NAME}_numeros.png'), build_sheet(plan=PLAN, numbers=True, scale=2))
    with open(os.path.join(ROOT, 'maps', 'tilesets', f'{NAME}.tsx'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_tsx())
    with open(os.path.join(out_t, f'{NAME}_plan.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_md())
    pv = preview()
    save_png(os.path.join(out_t, f'{NAME}_apercu.png'), pv, scale=3)
    print(f'{sum(1 for d in TILES.values() if d["img"] is not None)} tuiles ({"plan" if PLAN else "final"}) sur {COLS * ROWS} cases.')


if __name__ == '__main__':
    main()
