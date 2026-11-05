"""Outils de dessin communs aux tilesets `route_chateau` et `chateau` (fin du jeu) : palettes, textures de sol, murs, personnages de pierre.

Vue 3/4, lumière en haut à gauche, contour sombre d'1 px pour les objets, PAS de contour sur les dalles de sol (pas de quadrillage).
Toutes les textures de sol sont périodiques (32 px) : deux tuiles côte à côte se raccordent. Aucun pixel semi-transparent.
Les fonctions de dessin reçoivent/renvoient des tuiles = listes de 32 lignes de 32 tuples RGBA (None = transparent).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foret import P, Cv, T, rnd, vnoise, rgba  # noqa: E402,F401

O = P['O']


def pal(*hexes):
    return tuple(rgba(h) for h in hexes)


# (hi, lt, md, dk, dp)
PAL = dict(
    # --- château intérieur
    sol_in=pal('#6e6090', '#5c5080', '#4b416a', '#3b3358', '#2a2442'),
    cap_in=pal('#4a3e66', '#3c3258', '#2e2644', '#231d36', '#181327'),
    fac_in=pal('#a898c8', '#8c7cae', '#716490', '#574c74', '#3e3556'),
    arene=pal('#a496c4', '#8878b0', '#6e6098', '#584c80', '#413762'),
    tapis=pal('#c84a5c', '#a43048', '#842640', '#641c34', '#461226'),
    # --- cour et façade (extérieur, un peu plus claire)
    cour=pal('#9d90b8', '#8a7ca6', '#766a92', '#5f547a', '#483f60'),
    cap_cr=pal('#5a4c78', '#4a3e68', '#3a3054', '#2c2442', '#1e182f'),
    fac_cr=pal('#b6a8d2', '#9a8cba', '#7f7099', '#645880', '#4a4064'),
    # --- route
    pave=pal('#b4b0c8', '#9c98b2', '#84809c', '#686480', '#4e4a68'),
    herbe=pal('#7c9c70', '#628466', '#4c6c58', '#385246', '#2a3e3c'),
    # --- falaise brune, grotte
    falaise=pal('#bca48a', '#a08870', '#80694f', '#5f4d3c', '#40332c'),
    cap_fa=pal('#7e6e5e', '#6a5c4e', '#584c42', '#463c36', '#352d2c'),
    grot_sol=pal('#7e6852', '#68523f', '#54423a', '#41342f', '#2c2424'),
    roche=pal('#7a6662', '#62504f', '#4c3e41', '#392f35', '#272028'),
    cap_ro=pal('#463a42', '#392f37', '#2d252d', '#221c23', '#17121a'),
    # --- or, ronces, runes
    or_=pal('#f6e08a', '#dcb454', '#b08a34', '#7c5e24', '#503c18'),
    ronce=pal('#7a3a8a', '#5a2a6a', '#3a1a4a', '#241a22', '#150f18'),
    rune=pal('#c8f4ff', '#8ae0f8', '#4ac0e8', '#2a88c8', '#1c5a96'),
    vide=pal('#2a2036', '#1c1428', '#120c1e', '#0c0814', '#06040c'),
    metal=pal('#d4d8e4', '#a8aec0', '#7a8196', '#505870', '#343a50'),
    rouge=pal('#e86a58', '#c8383c', '#98242e', '#681a28', '#44101c'),
)
HI, LT, MD, DK, DP = range(5)


def c(name, k):
    return PAL[name][k]


# ------------------------------------------------------------------ primitives
def blank():
    return [[None] * T for _ in range(T)]


def canvas(w, h):
    return [[None] * w for _ in range(h)]


def put(t, x, y, col):
    if 0 <= y < len(t) and 0 <= x < len(t[0]):
        t[y][x] = col


def rect(t, x0, y0, x1, y1, col):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(t, x, y, col)


def line(t, x0, y0, x1, y1, col):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        put(t, round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), col)


def copy(t):
    return [r[:] for r in t]


def paste(dst, src, ox=0, oy=0):
    for y, row in enumerate(src):
        for x, col in enumerate(row):
            if col is not None:
                put(dst, x + ox, y + oy, col)


def outline(t, col=None):
    col = col or O
    h, w = len(t), len(t[0])
    pts = []
    for y in range(h):
        for x in range(w):
            if t[y][x] is None:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and t[yy][xx] not in (None, col):
                        pts.append((x, y))
                        break
    for x, y in pts:
        t[y][x] = col


def slice_(img, col, row):
    return [r[col * T:(col + 1) * T] for r in img[row * T:(row + 1) * T]]


def ell_fill(t, cx, cy, rx, ry, fn):
    """Remplit une ellipse ; fn(nx, ny, d) -> couleur (ou None pour ne pas toucher)."""
    for y in range(len(t)):
        for x in range(len(t[0])):
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = nx * nx + ny * ny
            if d <= 1:
                col = fn(nx, ny, d, x, y)
                if col is not None:
                    t[y][x] = col


def shaded(p, nx, ny, d, x, y, seed=0, noise=0.2):
    v = -(nx + ny) * 0.5 + (rnd(x, y, seed) - 0.5) * noise - d * 0.2 + 0.1
    return p[HI] if v > 0.5 else p[LT] if v > 0.12 else p[MD] if v > -0.3 else p[DK]


def ball(t, cx, cy, rx, ry, p, seed=0, noise=0.25):
    ell_fill(t, cx, cy, rx, ry, lambda nx, ny, d, x, y: shaded(p, nx, ny, d, x, y, seed, noise))


# ------------------------------------------------------------------ textures de sol
def grain(p, seed, lo=0.34, hi=0.63):
    """Fond bruité périodique en trois tons (md dominant)."""
    t = blank()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, seed) * 0.55 + vnoise(x, y, 16, seed + 5) * 0.45
            col = p[LT] if n > hi else p[DK] if n < lo else p[MD]
            r = rnd(x, y, seed + 9)
            if r < 0.04:
                col = p[DK]
            elif r > 0.975:
                col = p[LT]
            t[y][x] = col
    return t


SLAB_H = (5, 15, 26)                                                # joints horizontaux (jamais sur le bord de la tuile)
SLAB_V = {'a': ((7, 22), (14, 28), (3, 20)), 'c': ((11, 26), (4, 19), (9, 24))}


def bond(t, p, offsets=None, seed=3, layout='a'):
    """Dalles en appareil irrégulier : trois rangées de hauteur inégale, joints décalés d'une rangée à l'autre, joints un peu
    ondulés, ton légèrement différent d'une dalle à l'autre. Aucun joint sur le bord de la tuile (pas de quadrillage) et motif
    périodique sur 32 px : les tuiles se raccordent sans coupure, quelle que soit la variante."""
    V = SLAB_V[layout]
    hj = [[SLAB_H[k] + (1 if rnd(x // 3, k, seed) < 0.28 else 0) for k in range(3)] for x in range(T)]
    base = [row[:] for row in t]
    for y in range(T):
        band = 2 if (y < SLAB_H[0] or y > SLAB_H[2]) else 0 if y < SLAB_H[1] else 1
        vs = V[band]
        for x in range(T):
            vj = [vs[i] + (1 if rnd(y // 3, band * 2 + i + 7, seed) < 0.28 else 0) for i in range(2)]
            seg = 0 if vj[0] < x <= vj[1] else 1
            tone = rnd(band, seg, seed + 21)
            col = base[y][x]
            if band != 2 and col == p[MD]:                           # ton propre à chaque dalle (la rangée qui boucle reste neutre)
                if tone < 0.3 and rnd(x, y, seed + 3) < 0.3:
                    col = p[DK]
                elif tone > 0.7 and rnd(x, y, seed + 4) < 0.3:
                    col = p[LT]
            below = any(y == hj[x][k] + 1 for k in range(3))
            above = any(y == hj[x][k] - 1 for k in range(3))
            if any(y == hj[x][k] for k in range(3)) or x in vj:
                col = p[DP] if rnd(x, y, seed + 5) < 0.35 else p[DK]
            elif below or x - 1 in vj:                                # arête éclairée (haut et gauche de la dalle)
                if rnd(x, y, seed + 6) < 0.4:
                    col = p[LT]
            elif above or x + 1 in vj:                                # bord dans l'ombre (bas et droite)
                if rnd(x, y, seed + 8) < 0.4:
                    col = p[DK]
            t[y][x] = col


def crack(t, p, pts, brambles=None):
    line_pts = list(zip(pts, pts[1:]))
    for (xa, ya), (xb, yb) in line_pts:
        line(t, xa, ya, xb, yb, p[DP])
        line(t, xa + 1, ya - 1, xb + 1, yb - 1, p[HI])
    if brambles:
        for (xa, ya), (xb, yb) in line_pts:
            line(t, xa, ya, xb, yb, brambles[3])
        for i, (x, y) in enumerate(pts):
            put(t, x + 1, y - 1, brambles[0])
            if i % 2:
                put(t, x - 1, y + 1, brambles[1])


def slab_floor(p, kind='a', seed=1, brambles=None):
    t = grain(p, seed)
    bond(t, p, None, seed + 2, 'c' if kind == 'c' else 'a')
    if kind == 'b':                                                  # reflets
        r = random.Random(11 + seed)
        for _ in range(6):
            x, y = r.randrange(2, 28), r.randrange(2, 30)
            for i in range(r.choice((2, 3))):
                put(t, x + i, y, p[HI])
            put(t, x + 1, y + 1, p[DK])
    if kind == 'e':                                                  # éclats
        r = random.Random(23 + seed)
        for _ in range(8):
            x, y = r.randrange(2, 29), r.randrange(2, 29)
            put(t, x, y, p[HI])
            put(t, x + 1, y, p[LT])
            put(t, x, y + 1, p[DK])
            put(t, x + 1, y + 1, p[DP])
    if kind == 'f':
        crack(t, p, [(2, 3), (7, 8), (10, 8), (14, 14), (13, 17), (19, 21), (23, 25), (28, 30)], brambles)
    return t


_STONES = None


def _stones():
    """Pierres de la route : 5×5 points jittés (périodique sur 32 px), rayons inégaux -> pierres de tailles et de formes variées."""
    global _STONES
    if _STONES is None:
        n, cell = 5, 32 / 5
        _STONES = [((i + 0.5 + (rnd(i, j, 61) - 0.5) * 1.1) * cell, (j + 0.5 + (rnd(i, j, 62) - 0.5) * 1.1) * cell,
                    (rnd(i, j, 63) - 0.5) * 2.6, rnd(i, j, 64), i * n + j) for j in range(n) for i in range(n)]
    return _STONES


def cobbles(p, kind='a'):
    """Pavés de la route : pierres irrégulières (cellules de Voronoï décalées, tailles inégales), joints fins sombres, arête éclairée
    en haut à gauche, ombre en bas à droite, ton propre à chaque pierre. Le motif est le même pour toutes les variantes et périodique
    sur 32 px : les tuiles se raccordent sans couture."""
    t = blank()
    st = _stones()
    for Y in range(T):
        for x in range(T):
            best = []
            for sx, sy, w, tone, k in st:
                dx = (x + 0.5 - sx + 16) % 32 - 16
                dy = (Y + 0.5 - sy + 16) % 32 - 16
                best.append(((dx * dx + dy * dy) ** 0.5 - w, dx, dy, tone, k))
            best.sort()
            (s1, dx, dy, tone, k), s2 = best[0], best[1][0]
            e = s2 - s1
            if e < 1.15:
                col = p[DP] if rnd(x, Y, 5) < 0.7 else p[DK]
            elif e < 2.3:
                col = (p[HI] if rnd(x, Y, 5) < 0.3 else p[LT]) if dx + dy < 0 else p[DK]
            else:
                n = vnoise(x, Y, 8, 14)
                lit = -(dx + dy) / 8.0
                lo, hi = 0.24 + (0.12 if tone < 0.3 else -0.1 if tone > 0.75 else 0), 0.68 + (0.12 if tone < 0.3 else -0.1 if tone > 0.75 else 0)
                col = p[LT] if (n > hi or lit > 0.5 and rnd(x, Y, 6) < 0.6) else p[DK] if (n < lo or lit < -0.55 and rnd(x, Y, 7) < 0.6) else p[MD]
                if rnd(x, Y, 6) < 0.04:
                    col = p[LT]
            t[Y][x] = col
    if kind == 'b':                                                  # joints usés
        for _ in range(10):
            x, y = int(rnd(_, 1, 41) * 32), int(rnd(_, 2, 42) * 32)
            put(t, x, y, p[DK])
            put(t, x + 1, y + 1, p[LT])
    if kind == 'c':                                                  # petits cailloux
        r = random.Random(8)
        for _ in range(7):
            x, y = r.randrange(2, 29), r.randrange(2, 29)
            put(t, x, y, p[HI])
            put(t, x + 1, y, p[LT])
            put(t, x, y + 1, p[DK])
            put(t, x + 1, y + 1, p[DP])
    if kind == 'f':
        crack(t, p, [(3, 2), (8, 7), (12, 7), (15, 13), (14, 18), (20, 22), (25, 28)])
    return t


# ------------------------------------------------------------------ murs (même logique que sanctuaire / mine : coiffe + face + liseré)
WALLBITS = {16: (1, 1, 0, 0), 17: (0, 0, 1, 1), 18: (1, 0, 1, 0), 19: (0, 1, 0, 1), 20: (1, 1, 1, 0), 21: (1, 1, 0, 1), 22: (1, 0, 1, 1),
            23: (0, 1, 1, 1), 24: (0, 0, 0, 1), 25: (0, 0, 1, 0), 26: (0, 1, 0, 0), 27: (1, 0, 0, 0), 28: (1, 1, 1, 1), 29: (1, 0, 0, 1),
            30: (0, 1, 1, 0)}


class Wall:
    """Style de mur. cap(x,y), face(x,y) -> couleur ; rim = (hi, lt, md) des liserés éclairés ; shd = liserés d'ombre."""

    def __init__(self, cap_pal, rim_pal, face, seed=7, cap_kind='slab', rough=True, face_h=15):
        self.cp, self.rp, self.face, self.seed, self.cap_kind, self.rough = cap_pal, rim_pal, face, seed, cap_kind, rough
        self.cache = {}
        self.face_h = face_h

    def cap(self, x, y):
        p = self.cp
        n = vnoise(x, y, 8, self.seed)
        col = p[LT] if n > 0.72 else p[DK] if n < 0.25 else p[MD]
        if self.cap_kind == 'slab':
            jx = 0 if (y // 16) % 2 == 0 else 8
            if y % 16 == 0 or (x - jx) % 16 == 0:
                return p[DK]
            if (y % 16 == 1 or (x - jx) % 16 == 1) and rnd(x, y, self.seed + 1) < 0.5:
                return p[LT]
        elif self.cap_kind == 'crag':                                # roche en blocs anguleux : facettes, fissures, éclats (pas de courbes de niveau)
            return self.crag(x % 32, y % 32)
        else:                                                        # roche brute : paliers de relief (courbes de niveau claires/sombres)
            def q(xx, yy):
                return int((vnoise(xx % 32, yy % 32, 8, self.seed + 3) * 0.6 + vnoise(xx % 32, yy % 32, 16, self.seed + 4) * 0.4) * 5.2)
            k = q(x, y)
            col = (p[DK], p[DK], p[MD], p[MD], p[LT], p[LT], p[LT])[min(k, 6)]
            if k > q(x + 1, y) or k > q(x, y + 1):
                col = p[DP] if rnd(x, y, self.seed + 5) < 0.75 else p[DK]
            elif k > q(x - 1, y) or k > q(x, y - 1):
                col = p[HI] if k >= 3 and rnd(x, y, self.seed + 6) < 0.6 else p[LT]
            if rnd(x, y, self.seed + 2) < 0.03:
                col = p[LT]
            return col
        if rnd(x, y, self.seed + 2) < 0.02:
            return p[LT]
        return col

    def crag(self, x, y):
        k = (x, y)
        cc = self.__dict__.setdefault('_crag', {})
        if k in cc:
            return cc[k]
        p, sd = self.cp, self.seed
        pts = [((i + 0.5 + (rnd(i, j, sd + 31) - 0.5) * 1.0) * 32 / 3, (j + 0.5 + (rnd(i, j, sd + 32) - 0.5) * 1.0) * 32 / 3,
                rnd(i, j, sd + 33)) for j in range(3) for i in range(3)]
        best = []
        for sx, sy, tn in pts:
            dx, dy = (x + 0.5 - sx + 16) % 32 - 16, (y + 0.5 - sy + 16) % 32 - 16
            best.append(((dx * dx + dy * dy) ** 0.5, dx, dy, tn))
        best.sort()
        (d1, dx, dy, tn), d2 = best[0], best[1][0]
        e = d2 - d1
        n = vnoise(x, y, 4, sd + 7)
        if e < 0.9 and rnd(x, y, sd + 8) < 0.85:
            col = p[DP]
        elif e < 2.0:
            col = (p[LT] if rnd(x, y, sd + 9) < 0.7 else p[MD]) if dx + dy < 0 else (p[DK] if rnd(x, y, sd + 9) < 0.7 else p[MD])
        else:
            base = p[LT] if tn > 0.72 else p[DK] if tn < 0.22 else p[MD]
            col = base
            if n > 0.72 and base != p[LT]:
                col = p[LT]
            elif n < 0.22 and base != p[DK]:
                col = p[DK]
            if rnd(x, y, sd + 2) < 0.05:
                col = p[LT] if rnd(x, y, sd + 4) < 0.5 else p[DK]
        cc[k] = col
        return col

    def th(self, v, seed):
        """Épaisseur du liseré le long d'un bord (3 à 5 px), périodique, 4 aux extrémités (raccord des angles)."""
        if v < 5 or v > 26 or not self.rough:
            return 4
        n = vnoise(v, 3, 8, self.seed + seed)
        return 3 if n < 0.3 else 5 if n > 0.74 else 4

    def band(self, k, th, x, y, shade=False):
        """Couleur du liseré à la profondeur k (0 = bord de tuile)."""
        rp, cp = self.rp, self.cp
        if k == 0:
            return O
        if shade:
            return cp[DP] if k == 1 else cp[DK] if k == 2 else (cp[DK] if (x + y) % 2 == 0 else cp[MD]) if k >= th - 1 else cp[MD]
        if k == 1:
            return rp[HI]
        if k == 2:
            return rp[LT]
        if k >= th - 1:                                              # fondu : tramage entre le liseré et la coiffe
            return rp[MD] if (x + y) % 2 == 0 else self.cap(x, y)
        return rp[MD]

    def tile(self, bits):
        if bits in self.cache:
            return copy(self.cache[bits])
        tl, tr, bl, br = bits
        t = [[self.cap(x, y) for x in range(T)] for y in range(T)]
        n, s = not tl and not tr, not bl and not br
        w, e = not tl and not bl, not tr and not br
        corner_hd = (n and e) or (not tr and tl and br)
        corner_hg = (not tl and tr and bl)
        for y in range(T):
            for x in range(T):
                best = None
                if n:
                    th = self.th(x, 11)
                    if y < th:
                        best = (y, th, False)
                if w:
                    th = self.th(y, 13)
                    if x < th and (best is None or x < best[0]):
                        best = (x, th, False)
                if e:
                    th = self.th(y, 17)
                    if 31 - x < th and (best is None or best[2] or 31 - x < best[0]):
                        best = (31 - x, th, True) if (best is None or best[2] or 31 - x < best[0]) else best
                if best:
                    t[y][x] = self.band(best[0], best[1], x, y, best[2])
        if n and e:                                                  # angle haut-droite : lumière en haut, ombre à droite
            for y in range(4):
                for x in range(28, 32):
                    t[y][x] = self.band(y, 4, x, y) if y <= 31 - x else self.band(31 - x, 4, x, y, True)
        if corner_hd and not (n and e):
            for y in range(4):
                for x in range(28, 32):
                    t[y][x] = self.band(y, 4, x, y) if y <= 31 - x else self.band(31 - x, 4, x, y, True)
        if corner_hg:
            for y in range(4):
                for x in range(4):
                    t[y][x] = self.band(min(x, y), 4, x, y)
        cols = []
        if s:
            cols.append((0, 31))
        if not br and bl and tr:
            cols.append((28, 31))
        if not bl and br and tl:
            cols.append((0, 3))
        y0 = 32 - self.face_h
        for x0, x1 in cols:
            for y in range(y0, 32):
                for x in range(x0, x1 + 1):
                    t[y][x] = self.face(x, y)
        if s and w:
            for y in range(y0, 32):
                t[y][0] = O
        if s and e:
            for y in range(y0, 32):
                t[y][31] = O
        self.cache[bits] = t
        return copy(t)


def masonry(p, seed=3, courses=(17, 24), moss=None):
    """Face de mur en pierre taillée : deux assises, reflet en haut, base sombre. Retourne face(x, y)."""
    def face(x, y):
        if y == 17:
            return p[HI]
        if y == 31:
            return O
        if y == 24:
            return p[DP]
        off = 0 if y < 24 else 11
        if (x + off) % 16 == 0 and y not in (18, 25):
            return p[DP]
        if y in (18, 25):
            return p[LT]
        if y in (23, 30):
            return p[DK]
        n = vnoise(x, y, 8, seed)
        if y >= 28 and n < 0.45:
            return p[DK]
        return p[LT] if n > 0.72 else p[DK] if n < 0.2 else p[MD]
    return face


def strata(p, seed=3):
    """Face de falaise / de roche : paroi verticale en colonnes de roche (flancs éclairés à gauche), fissures, pied d'éboulis sombre."""
    def tone(x):
        v = vnoise(x, 7, 8, seed) * 0.6 + vnoise(x, 7, 16, seed + 1) * 0.4
        return 3 if v > 0.62 else 1 if v < 0.38 else 2

    def face(x, y):
        if y == 17:
            return p[HI]
        if y == 31:
            return O
        t = tone(x)
        col = {1: p[DK], 2: p[MD], 3: p[LT]}[t]
        if tone(x - 1) < t and y > 18:                                # flanc éclairé (gauche)
            col = p[HI] if y < 27 else p[LT]
        elif tone(x + 1) < t and y > 18:                              # flanc dans l'ombre (droite)
            col = p[DK]
        if y == 18:
            col = p[LT] if rnd(x, y, seed + 2) < 0.8 else p[HI]
        if y == 19 and rnd(x, y, seed + 5) < 0.5:
            col = p[DK]
        seg = rnd(x // 3, y // 5, seed + 6)                           # courts ressauts horizontaux
        if seg < 0.16 and y % 5 == 0 and y > 19:
            col = p[DP]
        if abs(vnoise(x, 5, 16, seed + 9) - 0.5) < 0.03 and 19 < y < 29:   # fissure verticale
            col = p[DP]
        if y >= 24:                                                   # pied dans l'ombre, éboulis tramés
            k = (y - 23) / 7
            if rnd(x, y, seed + 4) < k * k * 0.95:
                col = p[DK] if y < 29 else p[DP]
        return col
    return face


def full_face(p, seed=3, step=16):
    """Face de mur sur toute la tuile (variantes pleines 96-103, 112-119) : deux assises de pierre."""
    def face(x, y):
        yy = y % step
        off = 0 if y < step else 11
        if yy == 0:
            return p[DP]
        if yy == 1:
            return p[HI] if y < 4 else p[LT]
        if (x + off) % 16 == 0:
            return p[DP]
        if yy == step - 1:
            return p[DK]
        n = vnoise(x, y, 8, seed)
        return p[LT] if n > 0.72 else p[DK] if n < 0.2 else p[MD]
    return face


def face_tile(p, seed=3, step=16):
    f = full_face(p, seed, step)
    t = [[f(x, y) for x in range(T)] for y in range(T)]
    for y in range(T):
        if t[y][0] != p[DP]:
            t[y][0] = p[DP]
    return t


# ------------------------------------------------------------------ ronces
def brambles_tex(seed=5, dark=True):
    """Fond de ronces noires (périodique) : tiges tordues violettes, épines, trous sombres."""
    p = PAL['ronce']
    t = blank()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, seed)
            m = vnoise(x, y, 16, seed + 1)
            col = PAL['vide'][MD] if n < 0.45 else PAL['vide'][DK]
            a = abs(n - 0.55)
            b = abs(m - 0.5)
            if a < 0.07:
                col = p[DK] if a < 0.035 else p[LT] if (x + y) % 3 == 0 else p[MD]
            if b < 0.045:
                col = p[MD] if b < 0.025 else p[DK]
            if a < 0.07 and n > 0.55 and (x * 3 + y * 5) % 4 == 0 and rnd(x, y, seed + 2) < 0.45:
                col = p[HI]
            t[y][x] = col
    for _ in range(26):                                              # épines
        x, y = int(rnd(_, 1, seed + 7) * 32), int(rnd(_, 2, seed + 8) * 32)
        if t[y][x] in (p[MD], p[LT], p[DK]):
            t[(y - 1) % 32][(x + 1) % 32] = p[HI]
            t[(y - 2) % 32][(x + 2) % 32] = p[LT]
    return t


def bramble_sprite(w=T, h=T, seed=3, density=8, base_y=None):
    """Ronces posées (objet, avec contour) dans un canevas w×h."""
    r = random.Random(seed)
    cv = canvas(w, h)
    p = PAL['ronce']
    for _ in range(density):
        x0, y0 = r.randrange(2, w - 2), r.randrange(h // 2, h - 2) if base_y is None else base_y
        x1, y1 = x0 + r.randrange(-9, 10), y0 - r.randrange(3, 12)
        line(cv, x0, y0, x1, y1, p[MD] if r.random() < 0.5 else p[LT])
        put(cv, x1 + 1, y1 - 1, p[HI])
        put(cv, (x0 + x1) // 2 + 1, (y0 + y1) // 2, p[HI])
    outline(cv, p[DP])
    return cv


# ------------------------------------------------------------------ runes et symboles
def glyph(t, rows, ox, oy, col):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.':
                put(t, ox + i, oy + j, col)


def engrave(t, rows, ox, oy, lt, dk):
    """Symbole gravé : ombre en bas à droite (creux), couleur claire dessus."""
    glyph(t, rows, ox + 1, oy + 1, dk)
    glyph(t, rows, ox, oy, lt)


EYE = ['................',
       '.....######.....',
       '...##......##...',
       '..#....##....#..',
       '.#....####....#.',
       '#....##..##....#',
       '.#....####....#.',
       '..#....##....#..',
       '...##......##...',
       '.....######.....',
       '................']


def eye(t, cx, cy, lt, dk, iris=None, pupil=None):
    """Œil de Morvath (16×11) centré en (cx, cy)."""
    ox, oy = cx - 8, cy - 5
    engrave(t, EYE, ox, oy, lt, dk)
    if iris is not None:
        for y in range(oy + 3, oy + 8):
            for x in range(ox + 5, ox + 11):
                if ((x - cx + 0.5) / 3.2) ** 2 + ((y - cy) / 2.6) ** 2 <= 1:
                    put(t, x, y, iris)
        for y in range(cy - 2, cy + 3):
            put(t, cx - 1, y, pupil)
            put(t, cx, y, pupil)


def circle_pts(cx, cy, r, step=0.01):
    a = 0.0
    out = set()
    while a < 6.2832:
        out.add((round(cx + math.cos(a) * r), round(cy + math.sin(a) * r)))
        a += step
    return out


def ring(t, cx, cy, r, col, width=1):
    for k in range(width):
        for x, y in circle_pts(cx, cy, r + k - (width - 1) / 2, 0.5 / max(r, 4)):
            put(t, x, y, col)
