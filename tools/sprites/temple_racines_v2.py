"""DESSIN v2 du tileset du Temple des Racines — pierres irregulieres, bords fondus, plus de decor.

Remplace le dessin de temple_racines_final.py SANS deplacer aucune tuile (meme numero = meme case).
temple_racines.py et temple_racines_sous_sol.py appellent build(theme) :
    build('temple')   -> {id: image 32x32}   (salles 1 a 10 et boss)
    build('sous_sol') -> {id: image 32x32}   (salles 11 a 15, pierre bleu-vert)
Une image = liste de 32 lignes de 32 pixels RGBA (tuples) ou None (transparent). Pas de Pillow.

Principes :
- Tout est PERIODIQUE sur 32 px (bruit, motifs, tramage) : deux tuiles voisines se raccordent toujours.
- Dalles : cellules de Voronoi bruitees sur un tore. Les pierres qui touchent les bords de la tuile viennent
  de graines COMMUNES a toutes les variantes : n'importe quelle dalle se raccorde a n'importe quelle autre.
- Bords fondus (eau, terre, eau profonde) : champ bilineaire des 4 coins du terrain + bruit periodique,
  puis tramage ordonne (Bayer 4x4) dans la bande de transition. Le bord est identique des deux cotes
  d'une arete parce qu'il ne depend que des deux coins de cette arete.
- Murs, portes, escaliers, colonnes : geometrie de temple_racines_final.py (collisions inchangees),
  dessus et face avant retexturees.
"""
import math
import random

import temple_racines_final as F

T = 32
TAU = 2 * math.pi

# ------------------------------------------------------------------ palettes (temple, sous-sol)
RAMPS = {
    # pierre des dalles, du joint le plus sombre a l'arete la plus claire
    'pierre': (('#3a3436', '#5c5650', '#6f6962', '#847e76', '#9a948c', '#aaa49a', '#bfb9ae', '#d8d4cc'),
               ('#17282c', '#213a3e', '#30484a', '#445c5c', '#56746f', '#658480', '#769690', '#8aaaa4')),
    'mousse': (('#2a4224', '#3a5a2c', '#4c7434', '#5a8a3c', '#6a9a48', '#8ab45a'),
               ('#183a28', '#245a3c', '#30744a', '#3f8a5a', '#52a46c', '#6cbc80')),
    'terre': (('#3e2418', '#4a2a1c', '#5e3a22', '#74482a', '#8a5a34', '#9c6a3c', '#b06e40'),
              ('#2a1a12', '#3a2218', '#4a3022', '#5c3e2a', '#6e4a30', '#805838', '#946440')),
    'bois': (('#2e1a12', '#4a2a1c', '#5e3a22', '#7a4628', '#8a5a34', '#b06e40', '#c98250'),
             ('#1e120c', '#3a2218', '#4a2c1c', '#5e3a24', '#6e4a30', '#946440', '#a8744c')),
    'cap': (('#1b1420', '#241e2c', '#2e2638', '#382e42', '#44384e', '#4e4058'),
            ('#0e1820', '#141f2e', '#18263a', '#22344a', '#2a4258', '#2e4a5e')),
    'face': (('#1b1420', '#3a3046', '#4e4058', '#645672', '#7a6a88', '#8a7a98', '#b8a8c0'),
             ('#0e1820', '#1e3242', '#2e4a5e', '#3a5c70', '#4a7488', '#5a8498', '#8ab8c4')),
    'eau': (('#16223e', '#1e2e4e', '#263a5e', '#2e4a74', '#3c5a8a', '#4c6c9c', '#7a9ac0', '#b8d0e8'),
            ('#10203a', '#16304a', '#1e3e5a', '#285070', '#326486', '#40789a', '#70a4bc', '#b0d8e4')),
    'ronce': (('#120c16', '#1b1420', '#241a22', '#3a1a4a', '#52245e', '#6a2a7a', '#8e3c9c'),
              ('#120c16', '#1b1420', '#241a22', '#3a1a4a', '#52245e', '#6a2a7a', '#8e3c9c')),
    'feuille': (('#7a3a14', '#c8642a', '#f08a28', '#c8a050', '#e0c070'),
                ('#5e3014', '#a8542a', '#d07a30', '#a8904a', '#c8b070')),
    'champi': (('#5a0e18', '#961c28', '#e2342c', '#d6c49c', '#f2e6c8'),
               ('#3a1440', '#6a2a7a', '#9a4ab0', '#8ab8c4', '#c8f0f0')),
    'toile': (('#8a8480', '#c8c4bc', '#ece8e0'),
              ('#6a8a88', '#a0c0bc', '#d0ece8')),
}
OUTLINE = ('#1b1420', '#0e1820')


def _rgba(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


class Theme:
    def __init__(self, k):
        self.k = k
        self.r = {name: [_rgba(c) for c in pair[k]] for name, pair in RAMPS.items()}
        self.O = _rgba(OUTLINE[k])


TH = Theme(0)          # theme courant (change par build())

# ------------------------------------------------------------------ outils periodiques
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def bayer(x, y):
    return (BAYER[y % 4][x % 4] + 0.5) / 16.0


def ramp(name, v, x, y, lo=0, hi=None):
    """Couleur de la rampe `name` pour une valeur v (0..1), avec tramage ordonne entre deux teintes."""
    r = TH.r[name]
    hi = len(r) - 1 if hi is None else hi
    f = lo + max(0.0, min(1.0, v)) * (hi - lo)
    i = int(f)
    if f - i > bayer(x, y):
        i += 1
    return r[max(lo, min(hi, i))]


def col(name, i):
    r = TH.r[name]
    return r[max(0, min(len(r) - 1, i))]


def _hash(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return h


def _lattice(seed, ix, iy, n):
    return (_hash(seed, ix % n, iy % n) % 10007) / 10006.0


def vnoise(x, y, seed, period):
    """Bruit de valeur lisse, periodique sur 32 px (period = taille de maille, diviseur de 32)."""
    n = T // period
    gx, gy = x / period, y / period
    ix, iy = math.floor(gx), math.floor(gy)
    fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _lattice(seed, ix, iy, n), _lattice(seed, ix + 1, iy, n)
    c, d = _lattice(seed, ix, iy + 1, n), _lattice(seed, ix + 1, iy + 1, n)
    return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy


def fbm(x, y, seed):
    return (vnoise(x, y, seed, 16) * 0.55 + vnoise(x, y, seed + 7, 8) * 0.3 + vnoise(x, y, seed + 13, 4) * 0.15)


def new():
    return [[None] * T for _ in range(T)]


def copy(t):
    return [r[:] for r in t]


def put(t, x, y, c):
    if 0 <= x < T and 0 <= y < T and c is not None:
        t[y][x] = c


def over(dst, src):
    out = copy(dst)
    for y in range(T):
        for x in range(T):
            if src[y][x] is not None:
                out[y][x] = src[y][x]
    return out


def outline(t, c=None, diag=False):
    c = c or TH.O
    nb = ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, -1), (1, -1), (-1, 1)) if diag else ())
    pts = [(x, y) for y in range(T) for x in range(T) if t[y][x] is None and any(
        0 <= x + dx < T and 0 <= y + dy < T and t[y + dy][x + dx] not in (None, c) for dx, dy in nb)]
    for x, y in pts:
        t[y][x] = c


def drop_shadow(t, dx=1, dy=1, c=None):
    """Ombre portee d'un decor (vers le bas a droite, lumiere en haut a gauche), sous le decor."""
    c = c or col('pierre', 1)
    sh = new()
    for y in range(T):
        for x in range(T):
            if t[y][x] is not None and 0 <= x + dx < T and 0 <= y + dy < T and t[y + dy][x + dx] is None:
                sh[y + dy][x + dx] = c
    return over(sh, t)


# ------------------------------------------------------------------ dalles (Voronoi bruite sur tore)
# Graines communes : pierres a cheval sur les bords (haut/bas et gauche/droite par periodicite).
SHARED = [(4, 1), (19, 0.5), (0.5, 15), (30, 29)]
INTERIOR = {
    'a': [(12, 11), (23, 13), (11, 23), (21, 23)],
    'b': [(10, 10), (17, 12), (25, 10), (13, 19), (22, 20), (16, 26)],
    'c': [(15, 15), (25, 23)],
    'd': [(11, 12), (21, 11), (14, 22), (24, 21)],
    'e': [(13, 12), (23, 15), (11, 22), (20, 24)],
}
PEN_R = 7.0


def tdist(ax, ay, bx, by):
    dx = abs(ax - bx) % T
    dy = abs(ay - by) % T
    dx, dy = min(dx, T - dx), min(dy, T - dy)
    return math.hypot(dx, dy), dx, dy


def edge_dist(x, y):
    return min(x + 0.5, y + 0.5, T - 0.5 - x, T - 0.5 - y)


def voronoi(x, y, interior, warp_seed=101):
    """(id1, d1, d2, vx, vy) : graine la plus proche, distances F1/F2, vecteur graine -> pixel."""
    wx = x + (vnoise(x, y, warp_seed, 8) - 0.5) * 3.0
    wy = y + (vnoise(x, y, warp_seed + 1, 8) - 0.5) * 3.0
    pen = max(0.0, PEN_R - edge_dist(x, y)) * 3.2          # les graines interieures perdent pres des bords
    best = []
    for k, (sx, sy) in enumerate(SHARED):
        d, _, _ = tdist(wx, wy, sx, sy)
        best.append((d, (0, k), sx, sy))
    for k, (sx, sy) in enumerate(interior):
        d, _, _ = tdist(wx, wy, sx, sy)
        best.append((d + pen, (1, k), sx, sy))
    best.sort(key=lambda b: b[0])
    d1, id1, sx, sy = best[0]
    d2 = next(b[0] for b in best[1:] if b[1] != id1)
    vx, vy = (wx - sx), (wy - sy)
    vx -= T * round(vx / T)
    vy -= T * round(vy / T)
    return id1, d1, d2, vx, vy


def stone_tone(id1, seed):
    """Teinte de base d'une pierre : 3 niveaux de la rampe (une pierre = une couleur unie)."""
    h = _hash(id1[0], id1[1], 0 if id1[0] == 0 else seed, 17)
    return (4, 4, 5, 3, 4, 5)[h % 6]


def dalle(key, seed=0, cracks=None, moss=0.0, chips=()):
    """Une dalle complete. key = disposition interieure (a..e)."""
    t = new()
    interior = INTERIOR[key]
    info = [[voronoi(x, y, interior) for x in range(T)] for y in range(T)]
    for y in range(T):
        for x in range(T):
            id1, d1, d2, vx, vy = info[y][x]
            gap = d2 - d1
            if moss and gap < 2.2 and edge_dist(x, y) > 3 and fbm(x, y, 31 + seed) > 1 - moss * 0.8:
                t[y][x] = ramp('mousse', 0.35 + fbm(x, y, 43) * 0.5 - gap * 0.08, x, y, 1, 5)
                continue
            if gap < 1.0:                                   # joint fin
                c = col('pierre', 2)
                if gap < 0.45 and _hash(x, y, 21) % 3 == 0:
                    c = col('pierre', 1)
                if moss and edge_dist(x, y) > 3 and fbm(x, y, 31 + seed) > 1 - moss:
                    c = col('mousse', 2) if _hash(x, y, 23) % 2 else col('mousse', 3)
            else:
                base = stone_tone(id1, seed)
                lit = -(vx + vy) / (abs(vx) + abs(vy) + 0.01)
                i = base
                if gap < 2.0:                               # liseré : clair en haut a gauche, sombre en bas a droite
                    i = base + 1 if lit > 0.25 else (base - 1 if lit < -0.25 else base)
                elif id1[0] == 1 and fbm(x, y, 7 + seed) > 0.7 and bayer(x, y) < 0.5:
                    i = base - 1                            # usure : taches tramees (pierres interieures seulement)
                h = _hash(x, y, 3 if id1[0] == 0 else 3 + seed) % 97
                if h == 0:
                    i = base - 1                            # piqures
                elif h == 1:
                    i = base + 1
                c = col('pierre', max(2, min(6, i)))
            t[y][x] = c
    for (x0, y0) in chips:                                 # eclats manquants (terre apparente)
        for y in range(y0 - 2, y0 + 3):
            for x in range(x0 - 2, x0 + 3):
                if math.hypot(x - x0, (y - y0) * 1.2) < 2.3:
                    put(t, x, y, col('terre', 2) if (x - x0) + (y - y0) < 1 else col('terre', 3))
        put(t, x0 - 2, y0 - 2, col('pierre', 1)); put(t, x0 - 1, y0 - 3, col('pierre', 1))
    if cracks:
        for pts in cracks:
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                n = max(abs(bx - ax), abs(by - ay), 1)
                for i in range(n + 1):
                    x = round(ax + (bx - ax) * i / n)
                    y = round(ay + (by - ay) * i / n)
                    put(t, x, y, col('pierre', 1))
                    if 0 <= x + 1 < T and 0 <= y + 1 < T and t[y + 1][x + 1] not in (col('pierre', 1), col('pierre', 2)):
                        t[y + 1][x + 1] = col('pierre', 6)
    return t


def check_edges_equal(tiles):
    ref = tiles[0]
    for t in tiles[1:]:
        for k in range(T):
            assert t[0][k] == ref[0][k] and t[31][k] == ref[31][k] and t[k][0] == ref[k][0] and t[k][31] == ref[k][31], k


# ------------------------------------------------------------------ terre (periodique)
def terre_px(x, y):
    n = fbm(x, y, 51)
    v = 0.3 + n * 0.5
    c = ramp('terre', v, x, y, 2, 5)
    h = _hash(x, y, 77) % 131
    if h < 2:
        c = col('pierre', 2 + h)                           # gravier
    elif h < 5:
        c = col('terre', 1)
    elif h < 7:
        c = col('terre', 6)
    return c


PEBBLES = [(9, 10), (23, 22)]


def pebbles(t, pts, mask=None, size=1.6):
    for (px_, py_) in pts:
        for y in range(py_ - 2, py_ + 3):
            for x in range(px_ - 2, px_ + 3):
                if mask is not None and not mask(x % T, y % T):
                    continue
                d = math.hypot(x - px_, (y - py_) * 1.25)
                if d < size:
                    v = 0.5 - ((x - px_) + (y - py_)) * 0.22
                    put(t, x, y, ramp('pierre', v, x, y, 2, 5))
                elif d < size + 1 and y >= py_:
                    put(t, x, y, col('terre', 1))


def terre():
    t = [[terre_px(x, y) for x in range(T)] for y in range(T)]
    pebbles(t, PEBBLES)
    return t


# ------------------------------------------------------------------ champs de terrain (bords fondus)
def field(bits, x, y, seed, amp=0.32):
    """Valeur 0..1 : 1 = le terrain. Bilineaire entre les 4 coins (HG, HD, BG, BD) + bruit periodique."""
    tl, tr, bl, br = bits
    u, v = (x + 0.5) / T, (y + 0.5) / T
    f = (tl * (1 - u) + tr * u) * (1 - v) + (bl * (1 - u) + br * u) * v
    # le bruit s'annule sur les cases pleines pour garder leur texture intacte
    if all(bits) or not any(bits):
        return float(f)
    return f + (fbm(x, y, seed) - 0.5) * amp


DALLE_BASE = None        # dalle 'a' du theme courant (sol des tuiles de bord)


def terre_bord(bits):
    """Transition terre (1) / dalles (0) en coins, bord irregulier et fondu."""
    t = new()
    for y in range(T):
        for x in range(T):
            f = field(bits, x, y, 61, 0.42)
            if f > 0.56:
                c = terre_px(x, y)
                if f < 0.64:                               # pied des pierres : terre plus sombre
                    c = col('terre', 2) if bayer(x, y) < 0.6 else col('terre', 3)
            elif f > 0.5:
                c = col('pierre', 1) if bayer(x, y) < 0.7 else col('terre', 2)
            else:
                c = DALLE_BASE[y][x]
                if f > 0.38 and bayer(x, y) < (f - 0.38) * 5:   # poussiere de terre sur la pierre
                    c = col('terre', 4) if _hash(x, y, 5) % 3 else col('terre', 3)
            t[y][x] = c
    pebbles(t, PEBBLES, mask=lambda x, y: field(bits, x, y, 61, 0.42) > 0.62)
    return t


def eau_px(x, y, deep=False):
    """Eau periodique : vagues horizontales ondulees, reflets en petits traits."""
    wave = math.sin(TAU * (y / 8 + 0.22 * math.sin(TAU * x / 16) + 0.12 * math.sin(TAU * x / 32)))
    gate = math.sin(TAU * (x / 16 + y / 32)) + 0.6 * math.sin(TAU * (x / 8 - y / 16))
    n = fbm(x, y, 81 if deep else 83)
    if deep:
        v = 0.4 + wave * 0.1 + (n - 0.5) * 0.35
        c = ramp('eau', v, x, y, 0, 3)
        if wave > 0.93 and gate > 0.9:
            c = col('eau', 3)
        return c
    v = 0.5 + wave * 0.15 + (n - 0.5) * 0.3
    c = ramp('eau', v, x, y, 3, 5)
    if wave > 0.9 and gate > 0.4:
        c = col('eau', 6)
        if gate > 1.2 and _hash(x, y, 4) % 3 == 0:
            c = col('eau', 7)
    elif wave < -0.92 and gate < -0.6:
        c = col('eau', 3)
    return c


def eau(bits, profonde):
    """Eau peu profonde (sur dalles) ou eau profonde (sur eau peu profonde), bord fondu."""
    t = new()
    for y in range(T):
        for x in range(T):
            f = field(bits, x, y, 91 if not profonde else 97, 0.3)
            if not profonde:
                if f > 0.5:
                    c = eau_px(x, y)
                    if f < 0.57:                           # ecume / reflet du bord
                        c = col('eau', 7) if bayer(x, y) < 0.45 else col('eau', 6)
                    elif f < 0.66 and bayer(x, y) < 0.5:
                        c = col('eau', 5)
                else:
                    c = DALLE_BASE[y][x]
                    if f > 0.4:                           # pierre mouillee : plus sombre, tramee
                        if bayer(x, y) < (f - 0.4) * 9:
                            c = col('pierre', 2) if c not in (col('pierre', 0), col('pierre', 1)) else c
            else:
                if f > 0.5:
                    c = eau_px(x, y, True)
                    if f < 0.64 and bayer(x, y) > (f - 0.5) * 7:   # degrade vers l'eau peu profonde
                        c = col('eau', 3)
                else:
                    c = eau_px(x, y)
                    if f > 0.42 and bayer(x, y) < (f - 0.42) * 10:
                        c = col('eau', 3)
            t[y][x] = c
    return t


# ------------------------------------------------------------------ murs : nouvelle texture
CAP_SEEDS = [(4, 4), (15, 2), (26, 6), (9, 13), (21, 12), (3, 22), (14, 21), (27, 19), (8, 29), (20, 28)]


def cap_key(x, y):
    """Dessus du mur : grosses pierres irregulieres sombres, mousse par endroits (periodique)."""
    wx = x + (vnoise(x, y, 201, 8) - 0.5) * 3
    wy = y + (vnoise(x, y, 202, 8) - 0.5) * 3
    ds = sorted((tdist(wx, wy, sx, sy)[0], k) for k, (sx, sy) in enumerate(CAP_SEEDS))
    (d1, k1), (d2, _) = ds[0], ds[1]
    sx, sy = CAP_SEEDS[k1]
    vx, vy = wx - sx, wy - sy
    vx -= T * round(vx / T)
    vy -= T * round(vy / T)
    gap = d2 - d1
    n = fbm(x, y, 211)
    if gap < 1.1:
        return ('cap', 1)
    lit = -(vx + vy) / (abs(vx) + abs(vy) + 0.01)
    v = 0.45 + (k1 % 3 - 1) * 0.08 + (n - 0.5) * 0.3 + (0.25 * lit if gap < 2.4 else 0)
    f = 2 + max(0.0, min(1.0, v)) * 3
    i = int(f) + (1 if f - int(f) > bayer(x, y) else 0)
    return ('cap', max(2, min(5, i)))


FACE_JOINTS = {0: (0, 9, 21), 1: (5, 15, 26)}


def face_key(x, y):
    """Face avant du mur (y 17..31) : 2 assises de blocs de largeurs variees, coulures de mousse,
    pied assombri (ombre de contact avec le sol)."""
    if y == 17:
        return ('face', 6)
    if y == 31:
        return ('face', 0)
    row = 0 if y < 24 else 1
    if y in (24,):
        return ('face', 1)
    if x % T in FACE_JOINTS[row]:
        return ('face', 1)
    top = 18 if row == 0 else 25
    if y == top:
        return ('face', 5)
    joints = FACE_JOINTS[row]
    b = sum(1 for j in joints if x >= j)
    v = 0.55 + ((b * 37 + row * 11) % 5 - 2) * 0.05 + (fbm(x, y, 241) - 0.5) * 0.25
    if y >= 29:                                           # ombre de contact
        v -= 0.25 if y == 30 else 0.12
    f = 2 + max(0.0, min(1.0, v)) * 3
    i = int(f) + (1 if f - int(f) > bayer(x, y) else 0)
    if _hash(x, y, 9) % 53 == 0:
        i = 1
    return ('face', max(1, min(5, i)))


def install_wall_texture():
    """Branche la nouvelle texture dans les fonctions de murs de temple_racines_final (geometrie inchangee)."""
    for name in ('cap', 'face', 'mousse'):
        for i, c in enumerate(TH.r[name]):
            F.C[f'v2_{name}{i}'] = c
    F.C['mur_c'] = col('face', 6)
    F.C['face'] = col('face', 4)
    F.C['rim'] = col('face', 2)
    F.C['O'] = TH.O
    F.C['cap'] = col('cap', 3)
    F.C['cap_l'] = col('cap', 4)
    F.C['cap_d'] = col('cap', 1)
    F.C['face_l'] = col('face', 5)
    F.C['face_s'] = col('face', 3)
    F.C['I'] = col('cap', 1)
    F.cap_color = lambda x, y: 'v2_%s%d' % cap_key(x, y)
    F.face_color = lambda x, y: 'v2_%s%d' % face_key(x, y)
    # sol des ouvertures de porte et des escaliers : nouvelle dalle
    pal = {'sol': col('pierre', 4), 'sol_l': col('pierre', 5), 'sol_s': col('pierre', 3), 'clair': col('pierre', 7),
           'joint': col('pierre', 1)}
    for k, v in pal.items():
        F.C[k] = v
    F.DARK_RGB = {col('pierre', i): col('pierre', max(0, i - 1)) for i in range(8)}
    F.DALLE_A = DALLE_BASE


def mossify_wall(t, seed, amount=0.06):
    """Mousse propre a chaque tuile (loin des bords, donc sans couture) : touffes sur le dessus du mur
    et sur les aretes eclairees."""
    out = copy(t)
    lip = {col('face', 6)}
    caps = set(TH.r['cap'][2:])
    rnd = random.Random(seed)
    spots = [(rnd.randint(6, 25), rnd.randint(5, 13), rnd.uniform(2.0, 3.6)) for _ in range(rnd.randint(0, 2))]
    drips = [(rnd.randint(4, 27), rnd.randint(2, 7)) for _ in range(rnd.randint(1, 3))]
    faces = set(TH.r['face'][2:])
    for y in range(1, T - 1):
        for x in range(2, T - 2):
            c = t[y][x]
            if c in lip and fbm(x, y, seed) > 1 - amount:
                out[y][x] = col('mousse', 4)
                if y + 1 < T and t[y + 1][x] != TH.O:
                    out[y + 1][x] = col('mousse', 2)
            elif c in faces and y >= 17:
                for (dx_, L) in drips:                     # coulures de mousse sur la face avant
                    if abs(x - dx_) <= (1 if y < 18 + L // 2 else 0) and y < 18 + L:
                        out[y][x] = col('mousse', 3 if x <= dx_ else 2)
            elif c in caps:
                for (sx, sy, r) in spots:
                    d = math.hypot(x - sx, (y - sy) * 1.3) + (vnoise(x, y, seed, 4) - 0.5) * 1.6
                    if d < r and edge_dist(x, y) > 3:
                        out[y][x] = ramp('mousse', 0.6 - d / (r * 2.2) + (sx - x + sy - y) * 0.03, x, y, 1, 4)
    return out


# ------------------------------------------------------------------ racines
def tube(t, pts, r0, r1, ramp_name='bois', seed=0):
    """Tube ombre (lumiere en haut a gauche) avec ecorce striee."""
    samples = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        n = max(int(L * 2), 1)
        for i in range(n + 1):
            samples.append((ax + (bx - ax) * i / n, ay + (by - ay) * i / n))
    tot = len(samples) - 1 or 1
    for y in range(T):
        for x in range(T):
            best = None
            for k, (sx, sy) in enumerate(samples):
                r = r0 + (r1 - r0) * k / tot
                d = math.hypot(x - sx, y - sy)
                if d <= r and (best is None or d / r < best[0]):
                    best = (d / max(r, 0.5), x - sx, y - sy, r, k)
            if best:
                q, dx, dy, r, k = best
                lum = -(dx + dy) / (1.414 * max(r, 0.8))
                v = 0.5 + lum * 0.42
                if (k + (x * 3 + y) // 2) % 5 == 0:
                    v -= 0.18                               # stries de l'ecorce
                t[y][x] = ramp(ramp_name, v, x, y, 1, 6)


def racine(kind, thick=False):
    t = new()
    r = 3.6 if thick else 2.7
    if kind == 'h':
        pts = [(x, 15.5 + 2.6 * math.sin(TAU * x / 32) + 0.8 * math.sin(TAU * x / 16)) for x in range(-3, 36, 2)]
        tube(t, pts, r, r)
        tube(t, [(10, 15 + 2.6 * math.sin(TAU * 10 / 32)), (7, 22), (5, 26)], 1.4, 0.6)
        tube(t, [(23, 14), (25, 9), (28, 6)], 1.3, 0.5)
    elif kind == 'v':
        pts = [(15.5 + 2.6 * math.sin(TAU * y / 32) + 0.8 * math.sin(TAU * y / 16), y) for y in range(-3, 36, 2)]
        tube(t, pts, r, r)
        tube(t, [(15 + 2.6 * math.sin(TAU * 10 / 32), 10), (21, 7), (25, 6)], 1.3, 0.5)
        tube(t, [(14, 22), (9, 25), (6, 28)], 1.4, 0.6)
    else:                                                   # noeud : depart de racines
        tube(t, [(-2, 15.5), (8, 16), (14, 15)], r, r + 0.6)
        tube(t, [(18, 16), (25, 14), (34, 15.5)], r + 0.4, r)
        tube(t, [(15, 13), (12, 7), (9, 2)], r - 0.4, 1.0)
        tube(t, [(17, 18), (21, 24), (20, 30)], r - 0.6, 0.9)
        tube(t, [(16, 15.5)], r + 3.4, r + 3.4)
        for (x, y) in ((14, 12), (15, 12), (13, 13)):      # reflet du noeud
            put(t, x, y, col('bois', 6))
        put(t, 18, 18, col('bois', 1)); put(t, 19, 17, col('bois', 1))
    for (x, y) in ((6, 13), (24, 18), (16, 8), (13, 24)):   # mousse sur l'ecorce
        if t[y][x] is not None:
            put(t, x, y, col('mousse', 3)); put(t, x + 1, y, col('mousse', 4))
    outline(t)
    return drop_shadow(t)


# ------------------------------------------------------------------ ronces de Morvath
def ronce_curves(variant):
    cs = []
    for k, (a, ph, amp) in enumerate(((5, 0, 3), (14, 9, 4), (23, 18, 3), (29, 25, 2))):
        cs.append(('h', a + variant * 2, ph + variant * 5, amp))
    for k, (a, ph, amp) in enumerate(((8, 4, 3), (19, 14, 4), (27, 22, 3))):
        cs.append(('v', a + variant * 3, ph, amp))
    return cs


def ronces_bloc(variant):
    """Bloc de ronces (collision pleine) : enchevetrement periodique, des trous laissent voir le sol."""
    t = new()
    curves = ronce_curves(variant)
    for y in range(T):
        for x in range(T):
            best = 99
            for (o, a, ph, amp) in curves:
                if o == 'h':
                    cy = a + amp * math.sin(TAU * (x + ph) / 32)
                    d = abs(((y - cy + 16) % 32) - 16)
                else:
                    cx = a + amp * math.sin(TAU * (y + ph) / 32)
                    d = abs(((x - cx + 16) % 32) - 16)
                best = min(best, d)
            n = fbm(x, y, 301 + variant)
            if best < 1.7:
                v = 0.62 - best * 0.22 + (n - 0.5) * 0.3
                t[y][x] = ramp('ronce', v, x, y, 2, 6)
            elif n < 0.62 or best < 3.0:
                t[y][x] = ramp('ronce', 0.15 + n * 0.25, x, y, 0, 3)
    for k in range(26):                                     # epines
        h = _hash(k, variant, 333)
        x, y = h % 32, (h >> 8) % 32
        if t[y][x] is not None and t[y][x] in TH.r['ronce'][3:]:
            dx, dy = (1, -1) if k % 2 else (-1, -1)
            put(t, x + dx, y + dy, col('ronce', 6))
            put(t, x + 2 * dx, y + 2 * dy, col('ronce', 5))
    for y in range(T):                                      # quelques yeux de corruption violets
        for x in range(T):
            if _hash(x, y, 340 + variant) % 211 == 0 and t[y][x] is not None:
                put(t, x, y, col('ronce', 6))
    return t


def ronces_sol(variant):
    """Ronces rampantes (decor) : 2-3 tiges epaisses qui serpentent, epines claires."""
    t = new()
    rnd = random.Random(400 + variant)
    stems = [[(3, 20), (9, 15), (15, 18), (21, 12), (28, 14)], [(6, 27), (12, 24), (18, 27), (25, 22)],
             [(10, 6), (14, 11), (12, 15)]] if variant == 0 else \
            [[(4, 10), (10, 14), (17, 10), (24, 16), (29, 12)], [(8, 26), (14, 20), (21, 23), (27, 27)]]
    for pts in stems:
        tube(t, pts, 1.6, 1.0, 'ronce')
    for pts in stems:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            for k in (0.3, 0.7):
                x, y = round(ax + (bx - ax) * k), round(ay + (by - ay) * k)
                sgn = 1 if rnd.random() < 0.5 else -1
                put(t, x, y - 2 * sgn, col('ronce', 5)); put(t, x + 1, y - 3 * sgn, col('ronce', 6))
    outline(t)
    return drop_shadow(t)


# ------------------------------------------------------------------ decor au sol
def blob(t, cx, cy, rx, ry, ramp_name, seed, lo=0, hi=None, rough=0.35):
    for y in range(T):
        for x in range(T):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            d += (vnoise(x, y, seed, 4) - 0.5) * rough * 2
            if d < 1:
                lum = -((x - cx) / rx + (y - cy) / ry) * 0.3
                v = 0.55 + lum + (fbm(x, y, seed + 3) - 0.5) * 0.4 - d * 0.25
                c = ramp(ramp_name, v, x, y, lo, hi)
                if d > 0.82 and bayer(x, y) > 0.5:          # bord tramé (fondu)
                    continue
                t[y][x] = c


def mousse(v):
    t = new()
    if v == 0:
        blob(t, 15, 17, 10, 7, 'mousse', 501, 1, 5)
        blob(t, 8, 9, 4, 3, 'mousse', 503, 1, 5)
    else:
        blob(t, 11, 20, 7, 5, 'mousse', 511, 1, 5)
        blob(t, 22, 12, 6, 4, 'mousse', 513, 1, 5)
        blob(t, 24, 25, 3, 2.5, 'mousse', 515, 1, 5)
    for (x, y) in (((12, 12), (19, 14), (9, 19), (21, 20)) if v == 0 else ((9, 17), (13, 19), (21, 10), (24, 13))):
        if t[y][x] is not None:                             # petites pousses
            put(t, x, y - 1, col('mousse', 5)); put(t, x - 1, y - 2, col('mousse', 4)); put(t, x + 1, y - 2, col('mousse', 4))
    return t


LEAF = ["..##.", ".###.", "####.", ".##.."]


def leaf(t, x0, y0, c_main, c_dark, flip=False):
    for dy, row in enumerate(LEAF):
        for dx, ch in enumerate(row):
            if ch == '#':
                xx = x0 + (4 - dx if flip else dx)
                put(t, xx, y0 + dy, c_dark if dy == 3 or dx == (3 if not flip else 0) else c_main)
    put(t, x0 + (0 if not flip else 4), y0 + 4, c_dark)


def feuilles(v):
    t = new()
    rnd = random.Random(600 + v)
    n = 7 if v == 0 else 10
    for k in range(n):
        x, y = rnd.randint(2, 25), rnd.randint(2, 25)
        i = rnd.randint(1, 4)
        leaf(t, x, y, col('feuille', i), col('feuille', max(0, i - 2)), flip=rnd.random() < 0.5)
    return drop_shadow(t)


def gravats():
    t = new()
    rnd = random.Random(701)
    for (x, y, r) in ((14, 18, 4.2), (9, 21, 2.6), (20, 21, 3.0), (17, 13, 2.4), (24, 15, 1.8), (6, 15, 1.6), (12, 25, 1.7)):
        for yy in range(T):
            for xx in range(T):
                d = math.hypot(xx - x, (yy - y) * 1.15) + (vnoise(xx, yy, 703, 4) - 0.5) * 1.4
                if d < r:
                    v = 0.55 - ((xx - x) + (yy - y)) / (r * 2.6)
                    put(t, xx, yy, ramp('pierre', v, xx, yy, 1, 6))
        if rnd.random() < 0.5:
            put(t, x + 1, y, col('pierre', 1))
    outline(t)
    t = drop_shadow(t)
    for k in range(10):                                     # poussiere autour
        x, y = rnd.randint(4, 28), rnd.randint(8, 29)
        if t[y][x] is None:
            put(t, x, y, col('pierre', 3))
    return t


def cailloux():
    t = new()
    for (x, y, r) in ((8, 10, 2.4), (22, 8, 1.9), (17, 20, 2.8), (26, 25, 2.0), (10, 25, 1.6)):
        for yy in range(y - 4, y + 5):
            for xx in range(x - 4, x + 5):
                if math.hypot(xx - x, (yy - y) * 1.25) < r:
                    put(t, xx, yy, ramp('pierre', 0.5 - ((xx - x) + (yy - y)) * 0.16, xx, yy, 2, 6))
    outline(t)
    return drop_shadow(t)


def herbe():
    t = new()
    for (bx, by, n) in ((9, 22, 5), (20, 14, 4), (24, 25, 3), (13, 10, 3)):
        for k in range(n):
            x = bx + k * 2 - n
            h = 3 + (_hash(bx, k) % 4)
            lean = (k - n // 2) * 0.35
            for i in range(h):
                put(t, round(x + lean * i), by - i, col('mousse', 4 if i > h // 2 else 2 + (k % 2)))
            put(t, round(x + lean * h), by - h, col('mousse', 5))
        for x in range(bx - n - 1, bx + n):
            put(t, x, by + 1, col('mousse', 1))
    return t


def champignons():
    t = new()
    for (x, y, s) in ((12, 20, 3), (17, 22, 2), (20, 18, 2), (9, 24, 1)):
        for i in range(s + 1):                              # pied
            put(t, x, y - i, col('champi', 3)); put(t, x + 1, y - i, col('champi', 4) if i else col('champi', 3))
        cy = y - s - 1
        for yy in range(cy - s, cy + 1):
            for xx in range(x - s - 1, x + s + 3):
                if ((xx - x - 0.5) / (s + 1.5)) ** 2 + ((yy - cy) / (s + 0.5)) ** 2 <= 1:
                    put(t, xx, yy, col('champi', 2) if yy < cy else col('champi', 1))
        put(t, x - 1, cy - s + 1, col('champi', 4)); put(t, x + 1, cy - 1, col('champi', 4))
    outline(t)
    t = drop_shadow(t)
    for (x, y) in ((8, 13), (24, 23), (23, 12)):            # spores lumineuses
        put(t, x, y, col('champi', 4))
    return t


def flaque():
    t = new()
    for y in range(T):
        for x in range(T):
            d = math.hypot((x - 16) / 10, (y - 17) / 6) + (vnoise(x, y, 801, 4) - 0.5) * 0.5
            if d < 1:
                c = eau_px(x, y)
                if d > 0.85:
                    if bayer(x, y) > 0.55:
                        continue
                    c = col('eau', 6)
                t[y][x] = c
    for (x, y) in ((10, 15), (11, 15), (19, 19), (20, 19)):
        put(t, x, y, col('eau', 7))
    return t


def ombre(kind):
    """Ombre portee d'un mur sur le sol (calque Decor) : trame de pixels sombres qui s'eclaircit."""
    t = new()
    c = col('pierre', 1)
    for y in range(T):
        for x in range(T):
            d = 99
            if kind in ('haut', 'coin'):
                d = min(d, y)
            if kind in ('gauche', 'coin'):
                d = min(d, x)
            dens = {0: 0.85, 1: 0.7, 2: 0.55, 3: 0.4, 4: 0.28, 5: 0.17, 6: 0.08}.get(d, 0)
            if bayer(x, y) < dens:
                t[y][x] = c
    return t


def racines_pendantes():
    """Racines qui pendent du haut d'un mur (calque Dessus, posee sur une tuile de mur haut)."""
    t = new()
    for (x0, L, r) in ((7, 22, 1.6), (13, 14, 1.1), (21, 26, 1.8), (26, 12, 1.0)):
        pts = [(x0 + 1.5 * math.sin(i * 0.5 + x0), i) for i in range(-2, L)]
        tube(t, pts, r, max(0.5, r * 0.5))
    for (x, y) in ((21, 26), (22, 27), (7, 22), (8, 23)):   # radicelles au bout
        put(t, x, y, col('bois', 2))
    outline(t)
    for x in range(T):
        if t[0][x] == TH.O:
            t[0][x] = None
    return t


def lierre():
    t = new()
    for (x0, L) in ((5, 20), (11, 28), (18, 16), (25, 24)):
        for y in range(L):
            x = round(x0 + 1.2 * math.sin(y * 0.45 + x0))
            put(t, x, y, col('mousse', 1))
            if y % 4 == (x0 % 4):
                for (dx, dy) in ((-1, 0), (-2, 1), (-1, 1), (1, 0), (2, 1), (1, 1)):
                    put(t, x + dx, y + dy, col('mousse', 3 + (dx > 0)))
                put(t, x - 2, y, col('mousse', 5))
    outline(t)
    for x in range(T):
        if t[0][x] == TH.O:
            t[0][x] = None
    return t


def toile():
    t = new()
    c1, c2 = col('toile', 1), col('toile', 0)
    for a in (0.1, 0.45, 0.8, 1.2, 1.47):                  # fils rayonnants depuis le coin haut-gauche
        for r in range(0, 26):
            put(t, round(r * math.cos(a)), round(r * math.sin(a)), c2 if r > 18 else c1)
    for r in (6, 11, 16, 21):                               # fils concentriques
        for k in range(40):
            a = 0.1 + k * (1.37 / 39)
            rr = r - 1.2 * math.sin(k * 0.8)
            if _hash(r, k) % 7:
                put(t, round(rr * math.cos(a)), round(rr * math.sin(a)), c1 if r < 16 else c2)
    put(t, 9, 9, col('toile', 2))
    return t


def ronces_coupees():
    """Indice du scenario : souches de ronces tranchees net (coupe claire, comme avec un outil de forge)."""
    t = new()
    for (x, y, h) in ((9, 22, 6), (15, 25, 4), (21, 21, 7), (25, 26, 3)):
        for i in range(h):
            for dx in (-1, 0, 1):
                put(t, x + dx, y - i, col('ronce', 3 if dx < 0 else 4 if dx == 0 else 2))
        cy = y - h
        for dx in (-1, 0, 1):                               # coupe nette, claire et en biseau
            put(t, x + dx, cy, col('ronce', 6))
        put(t, x, cy, col('toile', 2))
        put(t, x - 2, y - h // 2, col('ronce', 5)); put(t, x + 2, y - h // 2 - 1, col('ronce', 5))
    for (x, y) in ((6, 27), (12, 28), (18, 28), (27, 29), (13, 17)):  # brins tombes au sol
        put(t, x, y, col('ronce', 3)); put(t, x + 1, y, col('ronce', 4)); put(t, x + 2, y - 1, col('ronce', 3))
    outline(t)
    return drop_shadow(t)


def vase_brise():
    t = new()
    shards = [((10, 20), [(0, 0), (5, -1), (6, 3), (1, 4)]), ((19, 22), [(0, 0), (4, 1), (2, 4)]),
              ((15, 14), [(0, 1), (3, 0), (4, 3), (1, 3)]), ((23, 16), [(0, 0), (3, 0), (2, 2)])]
    for (ox, oy), poly in shards:
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        for y in range(min(ys), max(ys) + 1):
            for x in range(min(xs), max(xs) + 1):
                if _inside(poly, x + 0.5, y + 0.5):
                    put(t, ox + x, oy + y, col('bois', 5) if y < (max(ys) + min(ys)) / 2 else col('bois', 4))
        put(t, ox + 1, oy + 1, col('bois', 6))
    outline(t)
    t = drop_shadow(t)
    for (x, y) in ((8, 26), (14, 27), (26, 21)):
        put(t, x, y, col('terre', 4))
    return t


def _inside(poly, x, y):
    c = False
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            c = not c
    return c


def dalle_racine():
    """Dalle soulevee par une racine qui perce entre les pierres (calque Sol)."""
    t = dalle('d', seed=3)
    o = new()
    tube(o, [(9, 25), (13, 20), (16, 16), (21, 13), (25, 8)], 3.2, 1.4)
    tube(o, [(15, 17), (11, 13), (9, 10)], 1.6, 0.6)
    outline(o)
    for y in range(T):                                     # pierres soulevees : arete sombre autour de la racine
        for x in range(T):
            if o[y][x] is None and any(0 <= x + dx < T and 0 <= y + dy < T and o[y + dy][x + dx] is not None
                                       for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)):
                if t[y][x] not in (col('pierre', 0), col('pierre', 1)) and edge_dist(x, y) > 2:
                    t[y][x] = col('terre', 2) if bayer(x, y) < 0.5 else col('pierre', 2)
    return over(t, o)


# ------------------------------------------------------------------ trous : levre irreguliere
def trou(bits):
    t = F.trou(bits)
    tl, tr, bl, br = bits
    n, s = not tl and not tr, not bl and not br
    dark = col('cap', 0)
    for x in range(T):
        jag = int(vnoise(x, 0, 901, 4) * 3)                 # levre ebrechee (periodique en x)
        if n:
            for y in range(3, 3 + jag):
                t[y][x] = col('pierre', 2) if y == 3 else col('cap', 2)
            if vnoise(x, 0, 903, 8) > 0.66:
                t[0][x] = col('mousse', 3)
        if s:
            for y in range(28 - jag, 28):
                t[y][x] = col('pierre', 5) if y == 28 - jag else col('pierre', 4)
    for y in range(T):
        for x in range(T):
            if t[y][x] == F.C['O']:
                f = fbm(x, y, 907)
                if f > 0.58 and bayer(x, y) < (f - 0.58) * 3:
                    t[y][x] = col('cap', 1)
                elif _hash(x, y, 905) % 23 == 0:
                    t[y][x] = dark
    return t


# ------------------------------------------------------------------ assemblage
NEW_TILES = [
    # (id, nom, role, calque)
    (12, 'ombre_mur_haut', 'Ombre portée d\'un mur du haut sur le sol (trame), sous un mur_haut', 'Decor'),
    (13, 'ombre_mur_gauche', 'Ombre portée d\'un mur de gauche sur le sol', 'Decor'),
    (14, 'ombre_mur_coin', 'Ombre portée dans un angle haut-gauche (mur en haut et à gauche)', 'Decor'),
    (15, 'gravats', 'Petit tas de gravats et poussière', 'Decor'),
    (76, 'cailloux', 'Quelques cailloux épars', 'Decor'),
    (77, 'herbe', 'Touffes d\'herbe entre les dalles', 'Decor'),
    (78, 'champignons', 'Champignons rouges (spores claires)', 'Decor'),
    (79, 'flaque', 'Petite flaque d\'eau (sans effet)', 'Decor'),
    (121, 'racines_pendantes', 'Racines qui pendent d\'un mur (à poser sur une tuile de mur haut)', 'Dessus'),
    (122, 'lierre', 'Lierre qui retombe sur un mur (à poser sur une tuile de mur)', 'Dessus'),
    (123, 'toile_araignee', 'Toile d\'araignée dans un angle (coin haut-gauche de la case)', 'Decor'),
    (124, 'dalle_racine', 'Dalle soulevée par une racine qui perce (variante de sol)', 'Sol'),
    (125, 'dalle_mousse', 'Dalle envahie de mousse dans les joints (variante de sol)', 'Sol'),
    (126, 'ronces_coupees', 'Souches de ronces tranchées net (indice : outil de forge)', 'Decor'),
    (127, 'vase_brise', 'Éclats d\'un vase brisé', 'Decor'),
]
TERRE_TILES = [
    # (id, nom, role, coins (HG, HD, BG, BD) : 1 = terre)
    (48, 'terre_bord_haut', 'Terre : bord haut (dalles au-dessus)', (0, 0, 1, 1)),
    (49, 'terre_bord_bas', 'Terre : bord bas (dalles en dessous)', (1, 1, 0, 0)),
    (50, 'terre_bord_gauche', 'Terre : bord gauche (dalles à gauche)', (0, 1, 0, 1)),
    (51, 'terre_bord_droite', 'Terre : bord droite (dalles à droite)', (1, 0, 1, 0)),
    (52, 'terre_creux_hg', 'Terre : coin rentrant, dalles seulement en haut-gauche', (0, 1, 1, 1)),
    (53, 'terre_creux_hd', 'Terre : coin rentrant, dalles seulement en haut-droite', (1, 0, 1, 1)),
    (54, 'terre_creux_bg', 'Terre : coin rentrant, dalles seulement en bas-gauche', (1, 1, 0, 1)),
    (55, 'terre_creux_bd', 'Terre : coin rentrant, dalles seulement en bas-droite', (1, 1, 1, 0)),
    (67, 'terre_coin_hg', 'Terre : coin haut-gauche d\'une zone de terre (terre seulement en bas-droite)', (0, 0, 0, 1)),
    (68, 'terre_coin_hd', 'Terre : coin haut-droite d\'une zone de terre (terre seulement en bas-gauche)', (0, 0, 1, 0)),
    (69, 'terre_coin_bg', 'Terre : coin bas-gauche d\'une zone de terre (terre seulement en haut-droite)', (0, 1, 0, 0)),
    (70, 'terre_coin_bd', 'Terre : coin bas-droite d\'une zone de terre (terre seulement en haut-gauche)', (1, 0, 0, 0)),
    (71, 'terre_diag', 'Terre : deux coins opposés (terre en haut-gauche et bas-droite)', (1, 0, 0, 1)),
]


def build(theme='temple', thick_roots=False):
    """{id: image}. theme = 'temple' ou 'sous_sol'."""
    global TH, DALLE_BASE
    TH = Theme(0 if theme == 'temple' else 1)
    DALLE_BASE = dalle('a')
    install_wall_texture()
    out = {}
    out[0] = DALLE_BASE
    out[1] = dalle('b', seed=1)
    out[2] = dalle('c', seed=2)
    out[3] = dalle('a', seed=4, cracks=[[(9, 9), (12, 12), (12, 15), (16, 18), (19, 18), (23, 23)]])
    out[4] = dalle('e', seed=5, cracks=[[(16, 16), (12, 11), (11, 9)], [(16, 16), (21, 13)], [(16, 16), (15, 21), (13, 24)],
                                        [(16, 16), (20, 20)]], chips=[(16, 16)])
    out[5] = terre()
    check_edges_equal([out[i] for i in range(5)])
    out[6], out[7], out[8] = racine('h', thick_roots), racine('v', thick_roots), racine('t', thick_roots)
    for i in range(16, 31):
        bits = {16: (1, 1, 0, 0), 17: (0, 0, 1, 1), 18: (1, 0, 1, 0), 19: (0, 1, 0, 1), 20: (1, 1, 1, 0),
                21: (1, 1, 0, 1), 22: (1, 0, 1, 1), 23: (0, 1, 1, 1), 24: (0, 0, 0, 1), 25: (0, 0, 1, 0),
                26: (0, 1, 0, 0), 27: (1, 0, 0, 0), 28: (1, 1, 1, 1), 29: (1, 0, 0, 1), 30: (0, 1, 1, 0)}[i]
        out[i] = mossify_wall(F.wall(bits), 950 + i)
    passages = {31: (1, 1, 1, 1), 32: (0, 0, 1, 1), 33: (1, 1, 0, 0), 34: (0, 1, 0, 1), 35: (1, 0, 1, 0),
                36: (0, 0, 0, 1), 37: (0, 0, 1, 0), 38: (0, 1, 0, 0), 39: (1, 0, 0, 0)}
    for i, b in passages.items():
        out[i] = F.trou_passage(b)
    for k, side in enumerate(('haut', 'bas', 'gauche', 'droite')):
        out[40 + k] = mossify_wall(F.porte(side), 960 + k)
        out[44 + k] = F.porte_dessus(side)
    out[56], out[57] = F.escalier(True), F.escalier(False)
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
    out[112], out[113] = F.colonne('haut'), F.colonne('base')
    out[114] = F.vase()
    out[115], out[116] = F.cerf('haut'), F.cerf('base')
    out[117], out[118] = mousse(0), mousse(1)
    out[119], out[120] = feuilles(0), feuilles(1)
    # nouvelles tuiles (cases de reserve)
    for i, _, _, bits in TERRE_TILES:
        out[i] = terre_bord(bits)
    extra = {12: ombre('haut'), 13: ombre('gauche'), 14: ombre('coin'), 15: gravats(), 76: cailloux(), 77: herbe(),
             78: champignons(), 79: flaque(), 121: racines_pendantes(), 122: lierre(), 123: toile(),
             124: dalle_racine(), 125: dalle('b', seed=9, moss=0.5), 126: ronces_coupees(), 127: vase_brise()}
    out.update(extra)
    check_edges_equal([out[0], out[124], out[125]])
    return out
