"""Corvan, boss du château (phase 1 : 64x64, phase 2 : 96x96), calques de corruption, Œil détaché, effets, icônes - Les Trois Sceaux.
PLACEHOLDERS a retoucher a la main.

Usage : python tools/sprites/corvan_boss.py     (sans Pillow : encodeur PNG de tsplan.py)
Produit dans art/bosses/corvan/ (voir corvan.json pour tout : cases, animations, origines, positions des bulbes) :
  corvan.png                   64x64 par case, 5 colonnes x 6 lignes : Corvan au marteau (phase 1)
  corvan_ombre.png             ombre au sol 64x64 (1 case)
  corvan_corrompu.png          96x96 par case, 11 colonnes x 1 ligne : Corvan-Morvath (phase 2)
  corvan_corrompu_ombre.png    ombre au sol 96x96
  corvan_corrompu_ronces.png / _pierre.png / _eau.png   calques 96x96, 10 colonnes : a superposer, a faire clignoter, a briser
  corvan_corrompu_ronces_liane.png   comme ronces mais SANS les 3 bulbes (a utiliser avec bulbe_ronces.png, un sprite par bulbe)
  bulbe_ronces.png             32x32 x 4 : bulbe noir (2 images de pulsation), touche, eclate
  ombre_marteau.png            128x128 x 5 : cercle d'ombre (rayon 56) qui se remplit
  poussiere.png                64x48 x 4 : nuage de l'impact du marteau
  pointes_ronces.png           32x48 x 5 : monticule (2) puis pointes (3)
  bulle_eau.png                32x32 x 4 : bulle d'eau noire (flotte A, B, revelee, eclate)
  oeil.png                     32x32 x 8 : l'Œil de Morvath detache ; oeil_anneau.png 48x48 x 4 : anneau dore d'arrivee
  conseil_fleche.png, conseil_bombe.png, conseil_lanterne.png   32x32 : icones au-dessus du boss
  *_frames.tres                SpriteFrames Godot
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import save_png, ROOT, rgba  # noqa: E402
from ondine import L, rnd  # noqa: E402

OUT = os.path.join(ROOT, 'art', 'bosses', 'corvan')


def H(*hs):
    return tuple(rgba(h) for h in hs)


OUTL = rgba('#1b1420')


# ------------------------------------------------------------------ palettes (clair, clair moyen, moyen, sombre)
class Pal:
    pass


def normal():
    p = Pal()
    p.skin = H('#fbd8b8', '#f2c29a', '#cc8c68', '#a46a50')
    p.grey = H('#f4f0e8', '#d8d4cc', '#9a948c', '#5c5650')
    p.shirt = H('#efe4c4', '#d6c49c', '#a6926c', '#80704e')
    p.apron = H('#b87848', '#8a5a34', '#5e3a22', '#43291c')
    p.pants = H('#6a5c76', '#4e4058', '#382e42', '#241a2e')
    p.boots = H('#8a5a3e', '#6a4630', '#43291c', '#2a1a12')
    p.glove = H('#7a5a44', '#4a3426', '#2e2018', '#1b1420')
    p.metal = H('#d8d4cc', '#9a948c', '#5c5650', '#3a3632')
    p.wood = H('#c8844c', '#a8683c', '#7a4a2c', '#4a2a1c')
    p.gold = rgba('#c8a050')
    p.eye = rgba('#1b1420')
    p.brow = rgba('#9a948c')
    p.crack = None
    return p


def corrupt():
    p = Pal()
    p.skin = H('#dccce0', '#b8a8c0', '#7a6a88', '#4e4058')
    p.grey = H('#b060c0', '#8a3a9c', '#5a2a6c', '#2c1038')
    p.shirt = H('#7a6c8a', '#5a4c6a', '#3e3250', '#2a2038')
    p.apron = H('#5a3068', '#3a1a4a', '#2a1832', '#18101e')
    p.pants = H('#4a4058', '#362e44', '#282032', '#1a1424')
    p.boots = H('#4a3a50', '#32263a', '#241a2a', '#14101a')
    p.glove = H('#6a3a7a', '#3a1a4a', '#241030', '#14081c')
    p.metal = H('#8a8098', '#5a5068', '#3a3248', '#241e30')
    p.wood = H('#6a4a58', '#4a3040', '#32202c', '#1e121a')
    p.gold = rgba('#e8c040')
    p.eye = rgba('#ffe060')
    p.brow = rgba('#241030')
    p.crack = rgba('#b060d8')
    return p


class Cv(L):
    """Calque dont les coordonnees sont exprimees dans une case 64x64 et agrandies de k."""

    def __init__(self, size, k=1.0):
        super().__init__(size, size)
        self.k = k

    def ell(self, cx, cy, rx, ry, pal, seed=0, noise=0.2):
        k = self.k
        L.ell(self, cx * k, cy * k, max(0.8, rx * k), max(0.8, ry * k), pal, seed, noise)

    def limb(self, a, b, r, pal, seed=0):
        k = self.k
        a = (a[0] * k, a[1] * k)
        b = (b[0] * k, b[1] * k)
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            L.ell(self, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, max(0.8, r * k), max(0.8, r * k), pal, seed)

    def rect(self, x0, y0, x1, y1, col):
        k = self.k
        for y in range(int(round(y0 * k)), int(round((y1 + 1) * k))):
            for x in range(int(round(x0 * k)), int(round((x1 + 1) * k))):
                self.set(x, y, col)

    def dot(self, x, y, col):
        self.rect(x, y, x, y, col)

    def line(self, a, b, col, w=1):
        k = self.k
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * k) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            x = (a[0] + (b[0] - a[0]) * t) * k
            y = (a[1] + (b[1] - a[1]) * t) * k
            for dx in range(w):
                for dy in range(w):
                    self.set(x + dx, y + dy, col)


# ------------------------------------------------------------------ Corvan (corps)
def hammer(c, p, a, b, head, hw=20, hh=10, lying=False):
    """Marteau de forgeron : manche de a (poignee) a b, tete centree en `head`."""
    c.limb(a, b, 1.8, p.wood, 3)
    hx, hy = head
    x0, x1 = int(hx - hw / 2), int(hx + hw / 2) - 1
    y0, y1 = int(hy - hh / 2), int(hy + hh / 2) - 1
    c.rect(x0, y0, x1, y1, p.metal[2])
    c.rect(x0, y0, x1, y0 + 1, p.metal[0])
    c.rect(x0, y0, x0 + 1, y1, p.metal[1])
    c.rect(x0, y1 - 1, x1, y1, p.metal[3])
    c.rect(x1 - 1, y0 + 2, x1, y1, p.metal[3])
    # frette sombre a la jonction, bande de frappe
    c.rect(x0 + 5, y0, x0 + 6, y1, p.metal[3])
    c.rect(x1 - 5, y0, x1 - 4, y1, p.metal[3])


class Pose:
    def __init__(self, **kw):
        self.dy = 0            # decalage vertical du corps (au-dessus des hanches)
        self.dh = 0            # decalage vertical supplementaire de la tete
        self.hx = 0            # decalage horizontal de la tete (penche)
        self.ll = 0            # jambe gauche (ecran) soulevee de n px
        self.rl = 0
        self.kneel = False
        self.hand_l = (16, 46)
        self.hand_r = (48, 46)
        self.hammer = None     # (a, b, head, hw, hh) ou None
        self.hammer_front = False   # dessine apres le corps (a terre devant lui)
        self.swing = 0         # profil : -1, 0, 1
        self.spread = 0
        self.thorns = False
        self.crack = False
        self.xoff = 0
        self.__dict__.update(kw)


def legs_front(c, p, pz):
    for sx, lift in ((-1, pz.ll), (1, pz.rl)):
        x = 32 + sx * 7 + pz.xoff
        if pz.kneel:
            c.ell(x, 57, 6, 4.5, p.pants, 5)
            c.ell(x + sx * 1, 60, 6, 3, p.boots, 6)
        else:
            c.limb((x, 47 + pz.dy * 0.3), (x, 55 - lift), 4.2, p.pants, 5)
            c.ell(x + sx * 0.5, 58 - lift, 6, 4.2, p.boots, 6)
            c.rect(int(x - 5), int(60 - lift), int(x + 5), int(60 - lift), p.boots[3])


def man_front(pz, p, k=1.0, size=64):
    c = Cv(size, k)
    dy, dh = pz.dy, pz.dh
    xo = pz.xoff
    if pz.hammer and not pz.hammer_front:
        hammer(c, p, *pz.hammer)
    legs_front(c, p, pz)
    # torse
    tcy = 38 + dy + (4 if pz.kneel else 0)
    c.ell(32 + xo, tcy, 15 + pz.spread, 13, p.shirt, 1)
    # tablier
    c.ell(32 + xo, tcy + 6, 10.5, 9.5, p.apron, 2)
    c.rect(26 + xo, tcy - 3, 38 + xo, tcy + 3, p.apron[1])
    c.rect(26 + xo, tcy - 3, 27 + xo, tcy + 3, p.apron[0])
    c.rect(22 + xo, tcy + 4, 42 + xo, tcy + 5, p.apron[3])      # ceinture
    c.rect(31 + xo, tcy + 4, 33 + xo, tcy + 5, p.gold)
    if pz.crack:
        pass
    # bras
    for sx, hand in ((-1, pz.hand_l), (1, pz.hand_r)):
        sh = (32 + sx * 15 + xo, 33 + dy + (4 if pz.kneel else 0))
        c.limb(sh, hand, 4.6, p.shirt, 7)
        c.ell(hand[0], hand[1], 4.2, 4.2, p.glove, 8)
    # tete
    hcy = 21 + dy + dh + (4 if pz.kneel else 0)
    hx = 32 + xo + pz.hx
    for sx in (-1, 1):                      # cheveux sur les cotes
        c.ell(hx + sx * 10, hcy + 3, 3, 5.5, p.grey, 9)
    c.ell(hx, hcy, 11, 10, p.skin, 3, 0.12)
    c.ell(hx - 3, hcy - 5, 4, 2, (p.skin[0],) * 4, 3)         # reflet du crane chauve
    for sx in (-1, 1):
        c.rect(int(hx + sx * 5 - 2), int(hcy - 2), int(hx + sx * 5 + 1), int(hcy - 2), p.brow)
        c.rect(int(hx + sx * 5 - 1), int(hcy), int(hx + sx * 5), int(hcy + 1), p.eye)
    c.rect(int(hx - 1), int(hcy + 3), int(hx), int(hcy + 4), p.skin[2])
    c.ell(hx, hcy + 9, 10, 8.5, p.grey, 10, 0.3)                # barbe
    c.rect(int(hx - 2), int(hcy + 6), int(hx + 2), int(hcy + 6), p.grey[3])
    if pz.crack:
        for i in range(10):
            c.dot(hx - 8 + i * 1.7, hcy - 6 + (i * 5) % 9, p.crack)
    if pz.thorns:
        for sx in (-1, 1):
            c.line((32 + sx * 17 + xo, 30 + dy), (32 + sx * 23 + xo, 22 + dy), p.glove[1], 2)
            c.line((32 + sx * 8 + xo + pz.hx, hcy - 7), (32 + sx * 11 + xo + pz.hx, hcy - 12), p.glove[1], 3)
        c.line((32 + xo + pz.hx, hcy - 9), (32 + xo + pz.hx, hcy - 15), p.glove[1], 3)
    if pz.hammer and pz.hammer_front:
        hammer(c, p, *pz.hammer)
    c.outline(OUTL)
    return c


def man_back(pz, p, k=1.0, size=64):
    c = Cv(size, k)
    dy, dh = pz.dy, pz.dh
    if pz.hammer:
        hammer(c, p, *pz.hammer)
    legs_front(c, p, pz)
    tcy = 38 + dy
    c.ell(32, tcy, 15, 13, p.shirt, 1)
    c.limb((22, 30 + dy), (38, 46 + dy), 1.4, p.apron, 2)        # bretelles croisees
    c.limb((42, 30 + dy), (26, 46 + dy), 1.4, p.apron, 2)
    c.ell(32, tcy + 8, 12, 6, p.apron, 4)
    c.rect(22, tcy + 4, 42, tcy + 5, p.apron[3])
    for sx, hand in ((-1, pz.hand_l), (1, pz.hand_r)):
        sh = (32 + sx * 15, 33 + dy)
        c.limb(sh, hand, 4.6, p.shirt, 7)
        c.ell(hand[0], hand[1], 4.2, 4.2, p.glove, 8)
    hcy = 21 + dy + dh
    c.ell(32, hcy + 7, 8, 5, p.skin, 4)                        # nuque
    c.ell(32, hcy, 11, 10, p.skin, 3, 0.12)
    for sx in (-1, 1):
        c.ell(32 + sx * 9, hcy + 3, 4, 6.5, p.grey, 9)
    c.ell(32, hcy + 6, 9, 3.5, p.grey, 11)
    c.ell(29, hcy - 5, 4, 2, (p.skin[0],) * 4, 3)
    if pz.thorns:
        for sx in (-1, 1):
            c.line((32 + sx * 17, 30 + dy), (32 + sx * 23, 22 + dy), p.glove[1], 2)
    c.outline(OUTL)
    return c


def man_side(pz, p, k=1.0, size=64):
    """Profil tourne vers la gauche, dos voute."""
    c = Cv(size, k)
    dy, dh = pz.dy, pz.dh
    if pz.hammer:
        hammer(c, p, *pz.hammer)
    # jambes : avant (gauche) et arriere (droite, plus sombre)
    for i, (x0, pal) in enumerate(((36, p.pants), (32, p.pants))):
        sw = pz.swing * (4 if i == 0 else -4)
        x = x0 + sw
        lift = pz.ll if i == 0 else pz.rl
        c.limb((x0 + 1, 47), (x, 55 - lift), 4.2, pal, 5)
        c.ell(x - 1.5, 58 - lift, 6.5, 4.2, p.boots, 6)
    tcy = 38 + dy
    c.ell(37, tcy, 13, 13, p.shirt, 1)
    c.ell(45, tcy - 6, 8, 8, p.shirt, 12)                       # bosse du dos
    c.ell(30, tcy + 6, 8, 9, p.apron, 2)
    c.rect(24, tcy + 4, 38, tcy + 5, p.apron[3])
    # bras proche
    sh = (34, 33 + dy)
    hand = pz.hand_l
    c.limb(sh, hand, 4.6, p.shirt, 7)
    c.ell(hand[0], hand[1], 4.2, 4.2, p.glove, 8)
    hcy = 22 + dy + dh
    hx = 24 + pz.hx
    c.ell(hx + 5, hcy + 1, 5, 7, p.grey, 9)
    c.ell(hx, hcy, 10, 10, p.skin, 3, 0.12)
    c.ell(hx + 3, hcy - 5, 4, 2, (p.skin[0],) * 4, 3)
    c.rect(int(hx - 8), int(hcy + 2), int(hx - 5), int(hcy + 4), p.skin[1])      # nez
    c.rect(int(hx - 7), int(hcy - 1), int(hx - 5), int(hcy - 1), p.brow)
    c.rect(int(hx - 6), int(hcy), int(hx - 5), int(hcy + 1), p.eye)
    c.ell(hx + 4, hcy + 2, 2, 3, (p.skin[2],) * 4, 3)                  # oreille
    c.ell(hx - 3, hcy + 9, 8, 7.5, p.grey, 10, 0.3)             # barbe
    c.rect(int(hx - 8), int(hcy + 5), int(hx - 5), int(hcy + 5), p.grey[3])
    c.outline(OUTL)
    return c


def mirrored(c):
    n = Cv(c.w, c.k)
    for y in range(c.h):
        for x in range(c.w):
            n.p[y][c.w - 1 - x] = c.p[y][x]
    return n


# poses du marteau : (poignee, bout du manche, centre de la tete, largeur, hauteur)
CARRY = ((47, 46), (52, 20), (53, 14), 20, 10)
CARRY_B = ((47, 46), (51, 19), (52, 13), 20, 10)


def walk_poses(view):
    base = dict(hammer=CARRY, hand_r=(47, 46))
    if view == 'side':
        base = dict(hammer=((42, 44), (47, 20), (47, 14), 20, 10), hand_l=(40, 45))
        return [Pose(**base),
                Pose(swing=1, dy=1, ll=0, **base), Pose(swing=0, dy=0, **base),
                Pose(swing=-1, dy=1, **base), Pose(swing=0, dy=0, **base)]
    return [Pose(**base),
            Pose(ll=3, dy=1, **base), Pose(dy=0, **base),
            Pose(rl=3, dy=1, **base), Pose(dy=0, **base)]


def phase1_cells():
    """Liste de (nom, Cv) dans l'ordre colonne/ligne de corvan.png."""
    rows = []
    for view, fn in (('front', man_front), ('back', man_back), ('side', man_side)):
        rows.append([fn(pz, normal()) for pz in walk_poses(view)])
    rows.append([mirrored(c) for c in rows[2]])
    p = normal()
    # ligne 4 : leve (3 images), coup (2 images)
    leve0 = Pose(dy=-1, hammer=((46, 44), (53, 16), (54, 11), 20, 10), hand_l=(40, 42), hand_r=(46, 44))
    leve1 = Pose(dy=-2, dh=-1, hammer=((43, 36), (48, 10), (48, 6), 22, 10), hand_l=(41, 32), hand_r=(45, 38))
    leve2 = Pose(dy=-3, dh=-1, hammer=((41, 30), (41, 4), (41, 5), 24, 10), hand_l=(40, 24), hand_r=(41, 31))
    coup0 = Pose(dy=2, dh=2, hammer=((36, 36), (36, 54), (36, 53), 24, 10), hand_l=(32, 38), hand_r=(38, 36), hammer_front=True)
    coup1 = Pose(dy=4, dh=3, hammer=((36, 42), (36, 58), (36, 56), 24, 10), hand_l=(32, 44), hand_r=(40, 42),
                 hammer_front=True)
    rows.append([man_front(z, p) for z in (leve0, leve1, leve2, coup0, coup1)])
    # ligne 5 : coince (2), touche, genoux (2)
    co0 = Pose(dy=5, dh=4, hx=-2, hammer=((29, 46), (38, 62), (39, 59), 24, 9), hand_l=(27, 46), hand_r=(33, 49),
               hammer_front=True)
    co1 = Pose(dy=3, dh=2, hx=1, hammer=((29, 42), (37, 59), (37, 57), 24, 9), hand_l=(27, 42), hand_r=(32, 45),
               hammer_front=True)
    touche = Pose(dy=2, dh=1, hx=3, ll=2, hand_l=(14, 40), hand_r=(50, 40), hammer=((47, 40), (57, 22), (58, 17), 20, 10))
    ge0 = Pose(kneel=True, dy=6, dh=3, hand_l=(21, 52), hand_r=(43, 52),
               hammer=((20, 60), (48, 60), (12, 59), 14, 8), hammer_front=True)
    ge1 = Pose(kneel=True, dy=7, dh=5, hand_l=(21, 53), hand_r=(43, 53),
               hammer=((20, 60), (48, 60), (12, 59), 14, 8), hammer_front=True)
    rows.append([man_front(z, p) for z in (co0, co1, touche, ge0, ge1)])
    return rows


# ------------------------------------------------------------------ Corvan-Morvath (96x96)
def phase2_poses():
    sp = dict(thorns=True, crack=True, spread=2)
    idle_a = Pose(hand_l=(8, 42), hand_r=(56, 42), **sp)
    idle_b = Pose(hand_l=(7, 40), hand_r=(57, 40), dy=-1, **sp)
    cp0 = Pose(hand_l=(10, 12), hand_r=(54, 12), dy=-2, dh=-1, **sp)
    cp1 = Pose(hand_l=(17, 56), hand_r=(47, 56), dy=4, dh=4, **sp)
    cp2 = Pose(hand_l=(14, 54), hand_r=(50, 54), dy=3, dh=3, **sp)
    touche = Pose(hand_l=(10, 34), hand_r=(55, 36), dy=2, dh=2, hx=4, **sp)
    tr0 = Pose(kneel=True, dy=6, dh=5, hand_l=(21, 53), hand_r=(43, 53), **sp)
    tr1 = Pose(dy=4, dh=4, hand_l=(14, 50), hand_r=(50, 50), **sp)
    tr2 = Pose(dy=-1, dh=0, hand_l=(5, 36), hand_r=(59, 36), **sp)
    st0 = Pose(dy=5, dh=6, hand_l=(18, 51), hand_r=(46, 51), xoff=-1, **sp)
    st1 = Pose(dy=5, dh=6, hand_l=(18, 51), hand_r=(46, 51), xoff=1, **sp)
    return [idle_a, idle_b, cp0, cp1, cp2, touche, tr0, tr1, tr2, st0, st1]


P2_NAMES = ['idle_a', 'idle_b', 'coup_leve', 'coup_frappe', 'coup_fin', 'touche',
            'transition_0', 'transition_1', 'transition_2', 'etourdi_a', 'etourdi_b']


def phase2_cells():
    return [man_front(z, corrupt(), 1.5, 96) for z in phase2_poses()]


def anchors(pz):
    """Points d'ancrage (case 64 -> 96) pour les calques."""
    k = 1.5
    kn = 4 if pz.kneel else 0
    sl = (32 - 15 + pz.xoff, 33 + pz.dy + kn)
    sr = (32 + 15 + pz.xoff, 33 + pz.dy + kn)
    return sl, sr, pz.hand_l, pz.hand_r, pz.dy + kn, k


VINE = H('#8a4aa0', '#5a2a70', '#341a44', '#1c0e28')
BULB = H('#b86ad8', '#7a3a98', '#401e58', '#1c0e2c')
STONE = H('#d8d4cc', '#a8a29c', '#726c68', '#46403e')
WATER = H('#9ae8f0', '#3e86b8', '#1e4a80', '#0e1e44')


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def bulb_positions(pz):
    sl, sr, hl, hr, dy, k = anchors(pz)
    return [lerp(sl, hl, 0.62), lerp(sr, hr, 0.62), (32 + pz.xoff, 32 + dy)]


def draw_bulb(c, x, y, r=5.2):
    c.ell(x, y, r, r, BULB, 21, 0.1)
    c.ell(x - 1.5, y - 1.8, 1.6, 1.2, (rgba('#f0c8ff'),) * 4, 1)
    c.dot(x + 1.5, y + 1.5, rgba('#e8c040'))
    for a in range(0, 360, 60):
        ax, ay = x + math.cos(math.radians(a + 20)) * (r + 1.5), y + math.sin(math.radians(a + 20)) * (r + 1.5)
        c.dot(ax, ay, VINE[3])
        c.dot((ax + x) / 2 + 0.3, (ay + y) / 2, BULB[2])


def layer_ronces(pz, bulbs=True):
    c = Cv(96, 1.5)
    sl, sr, hl, hr, dy, k = anchors(pz)
    for s, h in ((sl, hl), (sr, hr)):
        for i in range(2):
            a = lerp(s, h, 0.08 + i * 0.12)
            b = lerp(s, h, 0.8 + i * 0.05)
            mid = ((a[0] + b[0]) / 2 + (3 if i else -3), (a[1] + b[1]) / 2)
            c.limb(a, mid, 1.3, VINE, 3 + i)
            c.limb(mid, b, 1.3, VINE, 4 + i)
        for t in (0.2, 0.4, 0.6, 0.8):
            p = lerp(s, h, t)
            c.line(p, (p[0] + (3 if p[0] > 32 else -3), p[1] - 3), VINE[3], 1)
            c.line(p, (p[0] + (2 if p[0] > 32 else -2), p[1] + 3), VINE[3], 1)
    # liane sur la poitrine
    c.limb((22, 34 + dy), (42, 46 + dy), 1.2, VINE, 6)
    c.limb((42, 34 + dy), (22, 46 + dy), 1.2, VINE, 7)
    if bulbs:
        for (x, y) in bulb_positions(pz):
            draw_bulb(c, x, y)
    c.outline(OUTL)
    return c


def layer_pierre(pz):
    c = Cv(96, 1.5)
    sl, sr, hl, hr, dy, k = anchors(pz)
    c.ell(32 + pz.xoff, 39 + dy, 14, 11, STONE, 31, 0.35)         # plastron
    for s, h in ((sl, hl), (sr, hr)):
        c.ell(s[0], s[1] - 1, 8, 6.5, STONE, 32, 0.35)             # epaulieres
        c.ell(h[0], h[1], 5.5, 5.5, STONE, 33, 0.35)               # poings de roche
    # fissures violettes
    for (x0, y0, x1, y1) in ((28, 32, 33, 40), (33, 40, 31, 47), (36, 34, 40, 41)):
        c.line((x0 + pz.xoff, y0 + dy), (x1 + pz.xoff, y1 + dy), STONE[3], 1)
    c.dot(33 + pz.xoff, 41 + dy, rgba('#b060d8'))
    c.dot(37 + pz.xoff, 37 + dy, rgba('#b060d8'))
    c.outline(OUTL)
    return c


def layer_eau(pz):
    c = Cv(96, 1.5)
    sl, sr, hl, hr, dy, k = anchors(pz)
    c.ell(32 + pz.xoff, 52 + dy * 0.5, 19, 9, WATER, 41, 0.3)     # jupe d'eau
    for s, h in ((sl, hl), (sr, hr)):
        c.limb(lerp(s, h, 0.3), h, 4.8, WATER, 42)
        c.ell(h[0], h[1] + 4, 3, 4, WATER, 43)                     # goutte
    for x in range(14, 52, 6):
        c.ell(x + pz.xoff, 58 + (x // 6) % 2, 2.2, 3, WATER, 44)   # gouttes
    for x in range(16, 50, 5):
        c.dot(x + pz.xoff, 49 + dy * 0.5 + (x // 5) % 3, WATER[0])
    c.outline(OUTL)
    return c


def explode(layer, step, seed=1):
    """Eclate un calque en gros morceaux (step 1..3) : les morceaux s'ecartent du centre et se raréfient."""
    out = Cv(96, 1.5)
    cx, cy = 48, 62
    f = (0, 5, 12, 20)[step]
    keep = (1.0, 0.7, 0.4, 0.15)[step]
    B = 3
    for by in range(0, 96, B):
        for bx in range(0, 96, B):
            cells = [(x, y) for y in range(by, by + B) for x in range(bx, bx + B) if layer.p[y][x] is not None]
            if not cells:
                continue
            r = rnd(bx, by, seed)
            if r > keep:
                continue
            dx, dy = bx + 1 - cx, by + 1 - cy
            d = max(1.0, math.hypot(dx, dy))
            m = f * (0.5 + rnd(bx, by, seed + 1)) + (step * 2 if dy < 0 else 0) * 0.0
            ox = int(round(dx / d * m))
            oy = int(round(dy / d * m + step * 3))
            for (x, y) in cells:
                out.set(x + ox, y + oy, layer.p[y][x])
    return out


def flash(layer):
    out = Cv(96, 1.5)
    for y in range(96):
        for x in range(96):
            if layer.p[y][x] is not None:
                out.p[y][x] = rgba('#fff4c8') if layer.p[y][x] != OUTL else rgba('#e8c040')
    return out


def layer_sheet(fn, with_poses=(0, 1, 2, 3, 4, 5)):
    poses = phase2_poses()
    cells = [fn(poses[i]) for i in with_poses]
    base = cells[0]
    cells += [explode(base, s, 7) for s in (1, 2, 3)]
    cells.append(flash(base))
    return cells


# ------------------------------------------------------------------ ombres
def shadow(size, rx, ry, cy):
    c = Cv(size, 1)
    col = rgba('#14101e')
    for y in range(size):
        for x in range(size):
            nx, ny = (x + 0.5 - size / 2) / rx, (y + 0.5 - cy) / ry
            if nx * nx + ny * ny <= 1 and (x + y) % 2 == 0:
                c.p[y][x] = col
            elif nx * nx + ny * ny <= 0.55:
                c.p[y][x] = col
    return c


# ------------------------------------------------------------------ effets
def sheet(cells, cw, ch, cols=None, rows=1):
    cols = cols or len(cells)
    rows = max(rows, (len(cells) + cols - 1) // cols)
    s = Cv(1, 1)
    s.w, s.h = cw * cols, ch * rows
    s.p = [[None] * s.w for _ in range(s.h)]
    for i, cell in enumerate(cells):
        ox, oy = (i % cols) * cw, (i // cols) * ch
        for y in range(ch):
            for x in range(cw):
                if cell.p[y][x] is not None:
                    s.p[oy + y][ox + x] = cell.p[y][x]
    return s


def new(w, h):
    c = Cv(1, 1)
    c.w, c.h = w, h
    c.p = [[None] * w for _ in range(h)]
    return c


def ombre_marteau():
    cells = []
    DK = rgba('#1e1030')
    RING = rgba('#7a2e8c')
    RING_HI = rgba('#e84a60')
    for i, fr in enumerate((0, 14, 28, 42, 56)):
        c = new(128, 128)
        for y in range(128):
            for x in range(128):
                dx, dy = x + 0.5 - 64, (y + 0.5 - 64)
                d = math.hypot(dx, dy)
                if fr and d <= fr and (x + y) % 2 == 0:
                    c.p[y][x] = DK
                if fr and d <= fr - 6 and i >= 3:
                    c.p[y][x] = DK
                if 55 <= d <= 57:
                    on = (i == 0 and (int(math.atan2(dy, dx) * 10) % 2 == 0)) or i > 0
                    if on:
                        c.p[y][x] = RING_HI if i == 4 else RING
        cells.append(c)
    return cells


def poussiere():
    cells = []
    cols = H('#f0e4c8', '#d0c0a0', '#a89878', '#7a6c56')
    for i in range(4):
        c = new(64, 48)
        r = 8 + i * 6
        n = 7
        for j in range(n):
            a = math.pi * (0.0 + j / (n - 1))
            x = 32 + math.cos(a) * r * 1.25 * (1 if True else 0)
            y = 40 - math.sin(a) * r * 0.45 - i * 1.5
            rad = 5.5 - i * 0.6 + (j % 2)
            c.ell(x, y, rad, rad * 0.85, cols, j)
        if i < 3:
            c.ell(32, 40 - i * 2, 9 - i * 2, 5, cols, 9)
        c.outline(rgba('#5a4c3c'))
        cells.append(c)
    return cells


def pointes():
    cells = []
    EARTH = H('#6a4a7a', '#4a3258', '#32203c', '#1c1024')
    SP = H('#b86ad8', '#7a3a98', '#401e58', '#1c0e2c')
    for i in range(5):
        c = new(32, 48)
        if i < 2:
            h = 6 + i * 3
            c.ell(16, 44, 13 + i, h, EARTH, 4)
            for x in (10, 16, 22):
                c.dot(x + i, 42 - i, EARTH[3])
            if i:
                for x in (12, 20):
                    c.dot(x, 38, SP[1])
        else:
            hs = (14, 30, 26)[i - 2]
            c.ell(16, 45, 14, 5, EARTH, 4)
            for j, (x, hh) in enumerate(((7, 0.7), (16, 1.0), (25, 0.8))):
                top = 44 - hs * hh
                for y in range(int(top), 45):
                    w = (y - top) / max(1, 44 - top) * 3.2 + 0.4
                    for xx in range(int(x - w), int(x + w) + 1):
                        c.set(xx, y, SP[0] if xx < x - w * 0.3 else SP[1] if xx <= x + w * 0.3 else SP[2])
            c.line((11, 44), (11, 44 - hs * 0.4), SP[3])
        c.outline(OUTL)
        cells.append(c)
    return cells


def bulle():
    cells = []
    for i in range(4):
        c = new(32, 32)
        if i == 3:
            for a in range(0, 360, 45):
                x, y = 16 + math.cos(math.radians(a)) * 11, 16 + math.sin(math.radians(a)) * 11
                c.ell(x, y, 2.5, 2.5, WATER, a)
            c.ell(16, 16, 4, 4, WATER, 9)
        else:
            sq = (0, -1)[i % 2] if i < 2 else 0
            pal = WATER if i < 2 else H('#e8fcff', '#8ae4f4', '#3ea0d0', '#1e5898')
            c.ell(16, 16 + sq, 11 + (i % 2), 11 - (i % 2), pal, 5 + i, 0.2)
            if i < 2:
                c.ell(16, 16 + sq, 6, 6, H('#1a2a58', '#14204a', '#0e1638', '#0a0e28'), 6, 0.1)
            c.ell(11, 11 + sq, 2.5, 1.8, (rgba('#d8f8ff'),) * 4, 1)
            c.dot(21, 20 + sq, rgba('#8ae4f4'))
        c.outline(rgba('#0a0e28') if i < 3 else rgba('#1e5898'))
        cells.append(c)
    return cells


def bulbe_cells():
    cells = []
    for i in range(4):
        c = new(32, 32)
        if i < 2:
            draw_bulb(c, 16, 16 - i, 9 + i * 0.6)
        elif i == 2:
            draw_bulb(c, 16 + 1, 17, 8)
            for (x, y) in ((8, 10), (23, 11), (16, 6)):
                c.dot(x, y, rgba('#fff4c8'))
        else:
            for j, a in enumerate(range(10, 360, 50)):
                x, y = 16 + math.cos(math.radians(a)) * 10, 16 + math.sin(math.radians(a)) * 10
                c.ell(x, y, 3.2, 3.2, BULB, j)
            c.dot(16, 16, rgba('#e8c040'))
        c.outline(OUTL)
        cells.append(c)
    return cells


GOLD_EYE = H('#fff0a8', '#e8c040', '#b8862a', '#7a4e1c')
AURA = H('#8a3aa8', '#5a2a78', '#3a1a4e', '#1e0e2c')


def oeil():
    cells = []
    # 0-1 idle, 2-3 deplacement, 4-6 tir, 7 touche
    spec = [dict(open=1.0, w=0), dict(open=0.55, w=1), dict(open=0.8, stretch=4, w=0), dict(open=0.8, stretch=6, w=1),
            dict(open=1.15, glow=1, w=0), dict(open=1.2, glow=2, w=1), dict(open=1.0, glow=3, w=0),
            dict(open=0.5, hit=1, w=1)]
    for s in spec:
        c = new(32, 32)
        st = s.get('stretch', 0)
        # tentacules sombres
        for j, x in enumerate((9, 14, 18, 23)):
            off = 2 if (j + s['w']) % 2 else -2
            c.limb((x, 22), (x + off, 27 - (st > 0) * 0), 2.0, AURA, j)
            c.limb((x + off, 27), (x + off * 2 + 1, 30), 1.2, AURA, j + 4)
        c.ell(16, 16, 14 + st // 2, 11, AURA, 3, 0.2)
        if s.get('glow'):
            r = 13 + s['glow']
            c.ell(16, 16, r, r - 3, H('#fff0a8', '#ffe060', '#e8c040', '#b8862a'), 8, 0.0)
            c.ell(16, 16, 14, 11, AURA, 3, 0.2)
        op = max(1.5, 8.5 * s['open'])
        c.ell(16, 16, 11.5, op, GOLD_EYE if not s.get('hit') else H('#ffffff', '#fff0d8', '#e8c040', '#b8862a'), 6, 0.1)
        c.rect(15, int(16 - op + 1), 16, int(16 + op - 2), rgba('#1b1420'))             # pupille fendue
        if s['open'] < 0.7:
            c.rect(6, 12, 26, 12, AURA[2])
        c.outline(rgba('#14081c'))
        cells.append(c)
    return cells


def oeil_anneau():
    cells = []
    for i, r in enumerate((8, 13, 18, 22)):
        c = new(48, 48)
        for a in range(0, 720):
            x, y = 24 + math.cos(math.radians(a / 2)) * r, 24 + math.sin(math.radians(a / 2)) * r
            if i == 3 and (a // 12) % 2:
                continue
            c.set(x, y, rgba('#e8c040'))
            if i < 3:
                c.set(x + 1, y, rgba('#fff0a8') if i == 0 else rgba('#b8862a'))
        cells.append(c)
    return cells


def conseil(kind):
    c = new(32, 32)
    c.ell(16, 16, 14.5, 14.5, H('#6a4a7a', '#4a3258', '#32203c', '#1e1030'), 3, 0.1)
    ring = rgba('#e8c040')
    for a in range(0, 720):
        c.set(16 + math.cos(math.radians(a / 2)) * 14, 16 + math.sin(math.radians(a / 2)) * 14, ring)
    if kind == 'fleche':
        c.line((8, 24), (23, 9), rgba('#c8844c'), 2)
        c.rect(21, 7, 24, 8, rgba('#f4f0e8'))
        for p in ((22, 7), (23, 8), (24, 9), (24, 10), (22, 9), (21, 7), (21, 10), (25, 9)):
            c.set(*p, rgba('#f4f0e8'))
        c.line((22, 9), (25, 6), rgba('#d8d4cc'), 1)
        c.rect(23, 6, 25, 10, rgba('#d8d4cc'))
        c.line((8, 24), (6, 22), rgba('#e2342c'), 2)
        c.line((10, 24), (8, 26), rgba('#e2342c'), 2)
        c.line((8, 22), (6, 24), rgba('#961c28'), 1)
    elif kind == 'bombe':
        c.ell(15, 18, 8, 8, H('#6a6070', '#3a3448', '#241e30', '#14101e'), 2, 0.1)
        c.dot(12, 14, rgba('#d8d4cc'))
        c.dot(13, 14, rgba('#d8d4cc'))
        c.rect(14, 8, 17, 10, rgba('#5c5650'))
        c.line((17, 8), (21, 5), rgba('#c8844c'), 1)
        for p in ((22, 4), (21, 3), (23, 5), (22, 2), (24, 4)):
            c.set(*p, rgba('#ffe060'))
        c.set(22, 3, rgba('#ffffff'))
    else:
        c.rect(12, 6, 19, 7, rgba('#5c5650'))
        c.rect(14, 4, 17, 5, rgba('#5c5650'))
        c.rect(11, 8, 20, 22, rgba('#5c5650'))
        c.rect(13, 10, 18, 20, rgba('#ffe060'))
        c.rect(14, 12, 17, 18, rgba('#fff8c8'))
        c.rect(15, 11, 16, 11, rgba('#e8c040'))
        c.rect(10, 23, 21, 24, rgba('#3a3632'))
        c.rect(11, 8, 11, 22, rgba('#8a8478'))
    c.outline(OUTL)
    return c


# ------------------------------------------------------------------ export
def write_tres(path, tex, cw, ch, anims, extid, cols):
    """anims : (nom, [cases], fps, boucle). Case = indice, colonne = i % cols, ligne = i // cols."""
    subs, out, n = [], [], 0
    for name, cells, fps, loop in anims:
        fr = []
        for ci in cells:
            n += 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{n}"]\natlas = ExtResource("{extid}")\n'
                        f'region = Rect2({(ci % cols) * cw}, {(ci // cols) * ch}, {cw}, {ch})\n')
            fr.append('{"duration": 1.0, "texture": SubResource("AtlasTexture_%d")}' % n)
        out.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %s}'
                   % (', '.join(fr), 'true' if loop else 'false', name, fps))
    txt = ('[gd_resource type="SpriteFrames" format=3]\n\n'
           f'[ext_resource type="Texture2D" path="{tex}" id="{extid}"]\n\n' + '\n'.join(subs)
           + '\n[resource]\nanimations = [' + ', '.join(out) + ']\n')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(txt)


DIRS = ['down', 'up', 'left', 'right']
RES = 'res://art/bosses/corvan/'


def p1_anims():
    a = []
    for r, d in enumerate(DIRS):
        a.append((f'idle_{d}', [r * 5], 5.0, True))
    for r, d in enumerate(DIRS):
        a.append((f'walk_{d}', [r * 5 + i for i in range(1, 5)], 6.0, True))
    a.append(('leve', [20, 21, 22], 5.0, False))        # ~0,6 s ; tenir la derniere image pendant l'annonce
    a.append(('leve_tenu', [22], 1.0, True))
    a.append(('coup', [23, 24], 8.0, False))
    a.append(('coince', [25, 26], 3.0, True))
    a.append(('touche', [27], 1.0, False))
    a.append(('genoux', [28, 29], 2.0, True))
    return a


P2_ANIMS = [
    ('idle', [0, 1], 3.0, True),
    ('coup', [2, 3, 4], 5.0, False),
    ('touche', [5], 1.0, False),
    ('transition', [6, 7, 8], 3.0, False),
    ('etourdi', [9, 10], 3.0, True),
]
LAYER_ANIMS = [
    ('idle', [0, 1], 3.0, True),
    ('coup', [2, 3, 4], 5.0, False),
    ('touche', [5], 1.0, False),
    ('brise', [6, 7, 8], 8.0, False),
    ('flash', [9], 1.0, False),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}

    def png(name, cv):
        save_png(os.path.join(OUT, name), cv.p)

    # phase 1
    rows = phase1_cells()
    flat = [c for r in rows for c in r]
    png('corvan.png', sheet(flat, 64, 64, cols=5))
    png('corvan_ombre.png', shadow(64, 20, 6, 59))
    write_tres(os.path.join(OUT, 'corvan_frames.tres'), RES + 'corvan.png', 64, 64, p1_anims(), '1_corvan', 5)
    meta['corvan.png'] = {
        'cellule': [64, 64], 'colonnes': 5, 'lignes': 6, 'origine': [32, 62],
        'ordre_des_lignes': ['bas (idle, marche x4)', 'haut', 'gauche', 'droite (= miroir de gauche)',
                             'leve x3, coup x2', 'coince x2, touche, genoux x2'],
        'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in p1_anims()},
        'note': "case = ligne*5+colonne ; le marteau est a droite de l'ecran (vue de face) ; sous les pieds : corvan_ombre.png"}
    # phase 2
    cells = phase2_cells()
    png('corvan_corrompu.png', sheet(cells, 96, 96))
    png('corvan_corrompu_ombre.png', shadow(96, 30, 8, 90))
    write_tres(os.path.join(OUT, 'corvan_corrompu_frames.tres'), RES + 'corvan_corrompu.png', 96, 96, P2_ANIMS,
               '1_corvan_corrompu', 11)
    poses = phase2_poses()
    meta['corvan_corrompu.png'] = {
        'cellule': [96, 96], 'colonnes': 11, 'lignes': 1, 'origine': [48, 93], 'noms_des_cases': P2_NAMES,
        'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in P2_ANIMS},
        'note': "sans marteau, face au joueur ; 'transition' = Morvath se releve (genoux, penche, bras ecartes) ; "
                "'etourdi' = courbe, tete basse ; l'effondrement apres l'Oeil = animation 'genoux' de corvan.png (Corvan normal)"}
    # calques
    meta['calques'] = {
        'cellule': [96, 96], 'colonnes': 10, 'cases': ['idle_a', 'idle_b', 'coup_leve', 'coup_frappe', 'coup_fin', 'touche',
                                                      'brise_1', 'brise_2', 'brise_3', 'flash'],
        'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in LAYER_ANIMS},
        'note': "memes cases que corvan_corrompu.png pour les 6 premieres ; 'brise' = eclats qui s'ecartent puis disparaissent "
                "(a jouer sur le calque touche, puis le cacher) ; 'flash' = silhouette claire (alternative a modulate pour clignoter)"}
    for name, fn in (('ronces', layer_ronces), ('pierre', layer_pierre), ('eau', layer_eau)):
        png(f'corvan_corrompu_{name}.png', sheet(layer_sheet(fn), 96, 96))
        write_tres(os.path.join(OUT, f'corvan_corrompu_{name}_frames.tres'), RES + f'corvan_corrompu_{name}.png', 96, 96,
                   LAYER_ANIMS, f'1_{name}', 10)
    png('corvan_corrompu_ronces_liane.png', sheet(layer_sheet(lambda z: layer_ronces(z, False)), 96, 96))
    write_tres(os.path.join(OUT, 'corvan_corrompu_ronces_liane_frames.tres'), RES + 'corvan_corrompu_ronces_liane.png', 96, 96,
               LAYER_ANIMS, '1_liane', 10)
    meta['bulbes_ronces_centres_px'] = {
        P2_NAMES[i]: [[round(x * 1.5), round(y * 1.5)] for x, y in bulb_positions(poses[i])] for i in range(6)}
    meta['bulbes_ronces_centres_px']['note'] = ("3 centres (bras gauche ecran, bras droit, haut de la poitrine) par case, en px de la case 96x96 ; "
                                                "rayon visuel ~8 px ; une fleche sur un bulbe = toucher dans un cercle de 10 px")
    # bulbes
    bc = bulbe_cells()
    png('bulbe_ronces.png', sheet(bc, 32, 32))
    bul_an = [('idle', [0, 1], 3.0, True), ('touche', [2], 1.0, False), ('eclate', [3], 1.0, False)]
    write_tres(os.path.join(OUT, 'bulbe_ronces_frames.tres'), RES + 'bulbe_ronces.png', 32, 32, bul_an, '1_bulbe', 4)
    meta['bulbe_ronces.png'] = {'cellule': [32, 32], 'centre': [16, 16],
                                'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in bul_an}}
    # effets
    png('ombre_marteau.png', sheet(ombre_marteau(), 128, 128))
    om_an = [('remplit', [0, 1, 2, 3, 4], 4.0, False)]
    write_tres(os.path.join(OUT, 'ombre_marteau_frames.tres'), RES + 'ombre_marteau.png', 128, 128, om_an, '1_ombre', 5)
    meta['ombre_marteau.png'] = {'cellule': [128, 128], 'centre': [64, 64], 'rayon_px': 56,
                                 'cases': ['contour_pointille', 'plein_14', 'plein_28', 'plein_42', 'plein_56_alerte'],
                                 'note': "5 cases : a caler sur la duree de l'annonce (1,2 s x multiplicateur) ; tramé (damier) : "
                                         "la transparence se regle avec modulate"}
    png('poussiere.png', sheet(poussiere(), 64, 48))
    write_tres(os.path.join(OUT, 'poussiere_frames.tres'), RES + 'poussiere.png', 64, 48,
               [('impact', [0, 1, 2, 3], 10.0, False)], '1_poussiere', 4)
    meta['poussiere.png'] = {'cellule': [64, 48], 'origine': [32, 42], 'animations': {'impact': {'cases': [0, 1, 2, 3], 'fps': 10.0, 'boucle': False}}}
    png('pointes_ronces.png', sheet(pointes(), 32, 48))
    pt_an = [('monticule', [0, 1], 4.0, True), ('pointes', [2, 3, 4], 8.0, False)]
    write_tres(os.path.join(OUT, 'pointes_ronces_frames.tres'), RES + 'pointes_ronces.png', 32, 48, pt_an, '1_pointes', 5)
    meta['pointes_ronces.png'] = {'cellule': [32, 48], 'origine': [16, 44], 'une_case_de_largeur': 32,
                                  'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in pt_an},
                                  'note': "monticule 1,5 s (boucle), pointes 1 s : pointes_0 sort, pointes_1 plein, pointes_2 retombe ; une instance par case"}
    png('bulle_eau.png', sheet(bulle(), 32, 32))
    bl_an = [('flotte', [0, 1], 3.0, True), ('revelee', [2], 1.0, True), ('eclate', [3], 1.0, False)]
    write_tres(os.path.join(OUT, 'bulle_eau_frames.tres'), RES + 'bulle_eau.png', 32, 32, bl_an, '1_bulle', 4)
    meta['bulle_eau.png'] = {'cellule': [32, 32], 'centre': [16, 16],
                             'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in bl_an}}
    png('oeil.png', sheet(oeil(), 32, 32))
    oe_an = [('idle', [0, 1], 2.0, True), ('deplace', [2, 3], 8.0, True), ('tir', [4, 5, 6], 6.0, False), ('touche', [7], 1.0, False)]
    write_tres(os.path.join(OUT, 'oeil_frames.tres'), RES + 'oeil.png', 32, 32, oe_an, '1_oeil', 8)
    meta['oeil.png'] = {'cellule': [32, 32], 'centre': [16, 16],
                        'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in oe_an}}
    png('oeil_anneau.png', sheet(oeil_anneau(), 48, 48))
    write_tres(os.path.join(OUT, 'oeil_anneau_frames.tres'), RES + 'oeil_anneau.png', 48, 48,
               [('arrivee', [0, 1, 2, 3], 4.0, False)], '1_anneau', 4)
    meta['oeil_anneau.png'] = {'cellule': [48, 48], 'centre': [24, 24],
                               'animations': {'arrivee': {'cases': [0, 1, 2, 3], 'fps': 4.0, 'boucle': False}},
                               'note': "anneau dore a l'arrivee de l'Oeil : 4 images sur 1 s"}
    for k in ('fleche', 'bombe', 'lanterne'):
        png(f'conseil_{k}.png', conseil(k))
    meta['conseils'] = {'cellule': [32, 32], 'fichiers': ['conseil_fleche.png', 'conseil_bombe.png', 'conseil_lanterne.png'],
                        'note': "icone d'objet a flotter au-dessus du boss (centre-haut de la case, ~16 px au-dessus de la tete)"}
    with open(os.path.join(OUT, 'corvan.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print('ok')


if __name__ == '__main__':
    main()
