"""Sylve, le Cerf des Racines (boss du donjon 1) + bulbes de corruption + icône du sceau.

Usage : python tools/sprites/sylve.py [dossier_apercu]
Produit :
  art/bosses/sylve/sylve.png          corps du cerf blanc, vue 3/4 de face, cases 96x96, planche horizontale
  art/bosses/sylve/sylve_ronces.png   calque de corruption (ronces), mêmes frames, même cadrage
  art/bosses/sylve/sylve_cote.png     charge vue de côté (cerf tourné vers la GAUCHE), 6 frames
  art/bosses/sylve/sylve_cote_ronces.png   son calque de ronces
  art/bosses/sylve/sylve_ombre.png    ombre portée (1 case 96x96, ellipse)
  art/bosses/sylve/bulbe.png          bulbe de corruption 16x16 : 2 intact, 3 éclaté
  art/bosses/sylve/sylve.json         ordre des frames + positions des bulbes + origine
  art/items/sceau_racines.png         icône du sceau de la forêt 24x24
Origine conseillée de chaque case : bas-centre (48, 94) ; le sabot avant touche y = 94.
Sans Pillow : encodeur PNG de coffres.py (zlib + struct).
"""
import json
import math
import os
import random
import sys

import coffres as CF

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'art', 'bosses', 'sylve')
ITEMS = os.path.join(ROOT, 'art', 'items')
S = 96
GROUND = 94
CX = 48

PAL = {
    '.': None, '0': '#1b1420',
    'W': '#fffaf0', 'w': '#f2eee6', 's': '#c8c6d8', 'S': '#9a98b8',      # pelage blanc, ombres lavande
    'h': '#ece0c0', 'b': '#d6c49c', 'B': '#a6926c', 'd': '#8a5a34',      # bois (os)
    'n': '#382e42', 'p': '#e8a8a0', 'P': '#cc8c68',                      # nez, intérieur d'oreille
    'o': '#4a3a40', 'O': '#2e2430',                                      # sabots
    'e': '#241a22', 'i': '#6a2a7a', 'g': '#fffaf0',                      # oeil, iris corrompu, reflet
    'G': '#5a8a3c', 'H': '#9ad060', 'r': '#e2342c', 'a': '#f08a28',      # vert, vert clair, rouge, orange
    'y': '#f8d848', 'Y': '#c89a28',                                      # étoiles
    'v': '#241a22', 'm': '#3a1a4a', 'u': '#6a2a7a', 'U': '#9a4ab0',      # ronces
    'x': '#d6c49c', 'X': '#a6926c', 'z': '#b8a8c0',                      # poussière, buée
    'F': '#ffffff',
}


def rgba(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


# ------------------------------------------------------------------ outils (couches = dict {(x,y): c})
def blank(w=S, h=S):
    return [['.'] * w for _ in range(h)]


def ell(cx, cy, rx, ry, base='w', sh='s', deep='S', hi='W', lit=(-0.45, -0.8)):
    """Ellipse ombrée, lumière en haut à gauche."""
    d = {}
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                v = -(dx * lit[0] + dy * lit[1])      # >0 : côté ombre
                c = base
                if hi and v < -0.62:
                    c = hi
                if v > 0.38:
                    c = sh
                if deep and v > 0.82:
                    c = deep
                d[(x, y)] = c
    return d


def brush(d, x, y, r, c):
    for j in range(-r, r + 1):
        for i in range(-r, r + 1):
            if i * i + j * j <= r * r + r // 2:
                d[(x + i, y + j)] = c


def seg(d, p0, p1, r0, r1, c):
    n = max(int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))), 1)
    for k in range(n + 1):
        t = k / n
        brush(d, round(p0[0] + (p1[0] - p0[0]) * t), round(p0[1] + (p1[1] - p0[1]) * t),
              round(r0 + (r1 - r0) * t), c)


def thin(d, p0, p1, c):
    n = max(int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))), 1)
    for k in range(n + 1):
        t = k / n
        d[(round(p0[0] + (p1[0] - p0[0]) * t), round(p0[1] + (p1[1] - p0[1]) * t))] = c


def limb(p0, p1, w0, w1, base='w', sh='s', hi='W', hoof=0, hoof_w=None):
    """Patte : tronçon de p0 (haut) à p1 (bas), largeur w0 -> w1, bord droit dans l'ombre, sabot en bas."""
    d = {}
    y0, y1 = int(p0[1]), int(p1[1])
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(y1 - y0, 1)
        xc = p0[0] + (p1[0] - p0[0]) * t
        w = w0 + (w1 - w0) * t
        l, r = round(xc - w / 2), round(xc + w / 2)
        for x in range(l, r):
            c = base
            if x >= r - 2:
                c = sh
            elif x == l:
                c = hi
            if hoof and y > y1 - hoof:
                c = 'o' if x < r - 1 else 'O'
            d[(x, y)] = c
    return d


OFFX = 0


def blit(g, layer, ring=None):
    """Colle une couche ; ring = couleur d'un liseré intérieur de 1 px posé sur ce qui existe déjà."""
    if OFFX:
        layer = {(x + OFFX, y): c for (x, y), c in layer.items()}
    if ring:
        for (x, y) in layer:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (x + dx, y + dy)
                if p not in layer and 0 <= p[0] < S and 0 <= p[1] < S and g[p[1]][p[0]] != '.':
                    g[p[1]][p[0]] = ring
    for (x, y), c in layer.items():
        if 0 <= x < S and 0 <= y < S:
            g[y][x] = c


def outline(g, color='0'):
    h, w = len(g), len(g[0])
    pts = [(x, y) for y in range(h) for x in range(w) if g[y][x] == '.'
           and any(0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] not in ('.', color)
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        g[y][x] = color


def px(g):
    return [[rgba(PAL[c]) if PAL[c] else (0, 0, 0, 0) for c in row] for row in g]


# ------------------------------------------------------------------ bois (face)
BEAM = [(42, 27), (38, 23), (32, 19), (26, 16), (21, 13), (17, 10)]
TINES = [[(38, 23), (41, 16), (44, 10)], [(32, 19), (31, 12), (30, 7)], [(24, 15), (22, 9), (21, 5)]]
BULB_LOCAL = [(17, 10), (48, 10), (79, 10)]          # gauche, couronne, droite (avant transformation)


def make_T(drop, sy, hx=0, hy=0):
    y0 = 27 + drop

    def T(x, y):
        return (round(x + hx), round(y0 + (y - 27) * sy + hy))
    return T


def antler_face(T, clean=False):
    """Bois : dict de pixels (os). Deux côtés symétriques autour de CX."""
    d = {}
    for side in (1, -1):
        def M(p):
            return T(CX + (p[0] - CX) * side, p[1])
        pts = [M(p) for p in BEAM]
        for a, b, r0, r1 in zip(pts, pts[1:], (3, 2, 2, 2, 1), (2, 2, 2, 1, 1)):
            seg(d, a, b, r0, r1, 'b')
        for t in TINES:
            tp = [M(p) for p in t]
            seg(d, tp[0], tp[1], 1, 1, 'b')
            seg(d, tp[1], tp[2], 1, 0, 'b')
    # ombre sous/droite, lumière dessus/gauche
    out = dict(d)
    for (x, y) in d:
        if (x + 1, y) not in d and (x, y + 1) not in d:
            out[(x, y)] = 'd'
        elif (x, y + 1) not in d or (x + 1, y) not in d:
            out[(x, y)] = 'B'
        elif (x - 1, y) not in d or (x, y - 1) not in d:
            out[(x, y)] = 'h'
    return out


def bulb_positions(T):
    return [T(*p) for p in BULB_LOCAL]


# ------------------------------------------------------------------ cerf de face
def deer_front(pose):
    """pose : dict (voir POSES). Retourne (grille corps, grille ronces, positions des bulbes)."""
    g = blank()
    by = pose.get('by', 0)
    drop, sy = pose.get('drop', 0), pose.get('sy', 1.0)
    hx, hy = pose.get('hx', 0), pose.get('hy', 0)
    fl = pose.get('legs', [(0, 0)] * 4)
    ru = pose.get('rear_up', 0)
    eyes = pose.get('eyes', 'open')
    T = make_T(drop, sy, hx, hy + by)
    # pattes arrière (derrière)
    legs_geo = [(36, 71, 8, 6, GROUND), (57, 71, 8, 6, GROUND), (67, 68, 7, 5, GROUND - 3), (78, 68, 7, 5, GROUND - 3)]
    layers = {}
    for i, (x, y, w0, w1, gy) in enumerate(legs_geo):
        dx, lift = fl[i]
        knee = pose.get('knee', {}).get(i)
        top = (x, y + by)
        foot = (x + dx, gy - lift)
        if knee:
            layers[i] = (limb(top, (x + knee[0], knee[1]), w0, w1 - 1, hoof=0), limb((x + knee[0], knee[1]), foot, w1, w1 - 1, hoof=5))
        else:
            layers[i] = (limb(top, foot, w0, w1, hoof=5),)
    # ordre : arrière d'abord
    for i in (3, 2):
        for l in layers[i]:
            blit(g, l, 'S')
    # corps arrière puis poitrail
    blit(g, ell(63, 62 + by - ru, 21, 14), 'S')
    # queue
    blit(g, ell(85, 56 + by - ru, 4, 5, 'W', 'w', 's', None), 'S')
    for i in (0, 1):
        for l in layers[i]:
            blit(g, l, 'S')
    blit(g, ell(46, 61 + by, 17, 15), 'S')
    # cou
    neck = {}
    top_y = T(0, 38)[1]
    for y in range(min(top_y, 50 + by), 58 + by):
        t = (y - 40) / 18
        l = round(41 - 7 * max(0, min(t, 1)) + hx * 0.3)
        r = round(56 + 4 * max(0, min(t, 1)) + hx * 0.3)
        for x in range(l, r):
            neck[(x, y)] = 's' if x >= r - 3 else 'w'
    blit(g, neck, 'S')
    # crinière / jabot
    for k, x in enumerate(range(37, 60, 3)):
        blit(g, ell(x, 58 + by + (k % 2) * 2, 3, 3, 'W', 'w', 's', None), None)
    ant = antler_face(T)
    if sy < 0.8:
        blit(g, ant, 'd')
    # tête
    head = {}
    hcx, hcy = T(48, 36)
    head.update(ell(hcx, hcy, 9.5, 10 * (0.55 + 0.45 * sy)))
    mz = ell(hcx, hcy + 8 * sy + (1 - sy) * 2, 6.5, 6.5 * (0.6 + 0.4 * sy), 'w', 's', 'S', 'W')
    head.update(mz)
    # oreilles
    for sd in (-1, 1):
        ear = ell(hcx + sd * 11, hcy - 6 * sy - 1, 3.2, 4.5, 'w', 's', None, 'W')
        blit(g, ear, 'S')
        blit(g, ell(hcx + sd * 11, hcy - 6 * sy - 1, 1.5, 2.5, 'p', 'P', None, None), None)
    blit(g, head, 'S')
    ny = hcy + 8 * sy + (1 - sy) * 2 + 4 * (0.6 + 0.4 * sy)
    nose = {(round(hcx) + i, round(ny) + j): 'n' for i in range(-3, 3) for j in (0, 1)}
    nose.update({(round(hcx) - 3, round(ny)): '.', (round(hcx) + 2, round(ny)): '.'})
    nose = {k: v for k, v in nose.items() if v != '.'}
    blit(g, nose, None)
    # yeux
    ey = round(hcy - 1 * sy)
    ic = {'open': 'i', 'red': 'r', 'green': 'G', 'amber': 'a'}.get(eyes, 'i')
    for sd in (-1, 1):
        ex = round(hcx + sd * 5)
        if eyes in ('closed', 'hurt', 'ko'):
            if eyes == 'hurt':
                for k in range(3):
                    g[ey - 1 + k][ex - sd * (1 - abs(k - 1))] = 'e'
                    g[ey - 1 + k][ex - sd * (1 - abs(k - 1)) + sd] = 'e'
            elif eyes == 'ko':
                for k in range(-1, 2):
                    g[ey + k][ex + k] = 'e'
                    g[ey + k][ex - k] = 'e'
            else:
                for k in range(-2, 3):
                    g[ey + (1 if abs(k) == 2 else 0)][ex + k] = 'e'
        else:
            for j in (-1, 0, 1):
                for i in (-1, 0, 1):
                    g[ey + j][ex + i] = 'e'
            g[ey][ex] = ic
            g[ey + 1][ex] = ic
            g[ey - 1][ex - 1] = 'g'
    # bois
    if sy >= 0.8:
        blit(g, ant, 'd')
    return g, T, ant


# ------------------------------------------------------------------ ronces
def vine(d, pts, rnd, thorns=0.35, c='v'):
    """Liane en 1 px suivant une polyligne ; épines sur les côtés ; reflet violet à gauche/en haut."""
    n = len(pts)
    prev = pts[0]
    cells = []
    for p in pts[1:]:
        k = max(abs(p[0] - prev[0]), abs(p[1] - prev[1]), 1)
        for s in range(k):
            t = s / k
            cells.append((round(prev[0] + (p[0] - prev[0]) * t), round(prev[1] + (p[1] - prev[1]) * t)))
        prev = p
    cells.append(pts[-1])
    for i, (x, y) in enumerate(cells):
        d[(x, y)] = c
        d[(x + 1, y)] = d.get((x + 1, y), 'm')
        if i % 3 == 0:
            d[(x - 1, y - 1)] = d.get((x - 1, y - 1), 'u')
        if i % 4 == 2 and rnd.random() < thorns * 2:
            sx = rnd.choice((-2, 2))
            d[(x + sx, y - 1)] = 'v'
            d[(x + sx // 2, y - 1)] = d.get((x + sx // 2, y - 1), 'v')


def tangle(d, x0, y0, x1, y1, rnd, n=4):
    """Fouillis de ronces : n lianes qui se croisent dans la boite, avec épines."""
    for _ in range(n):
        pts = [(rnd.randint(x0, x1), rnd.randint(y0, y1)) for _ in range(4)]
        vine(d, pts, rnd, thorns=0.6)
    for _ in range(max(2, n // 2)):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        for (a, b) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            d[(x + a, y + b)] = 'm'
        d[(x, y)] = 'u'
        d[(x - 1, y - 1)] = 'v'
        d[(x + 2, y + 2)] = 'v'


def knot(d, cx, cy, r=2):
    for j in range(-r, r + 1):
        for i in range(-r, r + 1):
            if i * i + j * j <= r * r + 1:
                d[(cx + i, cy + j)] = 'm' if i + j > 0 else 'u'
    d[(cx, cy)] = 'v'
    for sx, sy_ in ((-r - 1, -r), (r + 1, -r), (-r - 1, r), (r + 1, r), (0, -r - 1), (0, r + 1)):
        d[(cx + sx, cy + sy_)] = 'v'


def ronces_face(pose, T, drop_rank=None, density=1.0, fall=0, seed=7):
    """Calque de corruption : liane autour de chaque bois, couronne, cou, épaule, flanc, pattes.
    Chaque élément a un rang fixe ; density < 1 retire les derniers (frames de purification) et
    fall décale vers le bas ce qui reste (les ronces qui tombent)."""
    rnd = random.Random(seed)
    by = pose.get('by', 0)
    elems = []                          # (rang, dict)

    def add(d):
        elems.append(d)
    # lianes enroulées sur les bois
    for side in (1, -1):
        def M(p):
            return T(CX + (p[0] - CX) * side, p[1])
        pts = [M(p) for p in BEAM]
        d = {}
        zz = []
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            for s in range(3):
                t = s / 3
                zz.append((round(a[0] + (b[0] - a[0]) * t + (1 if s % 2 else -1)), round(a[1] + (b[1] - a[1]) * t + (-1 if s % 2 else 1))))
        zz.append(pts[-1])
        vine(d, zz, rnd)
        add(d)
        # lianes qui pendent des bois
        d3 = {}
        a = pts[-1]
        vine(d3, [(a[0] + 2, a[1] + 2), (a[0] + 1, a[1] + 7), (a[0] + 3, a[1] + 12), (a[0] + 2, a[1] + 16)], rnd)
        add(d3)
    # noeuds de ronces autour des 3 bulbes
    for (bx, by_) in bulb_positions(T):
        d = {}
        knot(d, bx, by_ + 3, 2)
        add(d)
    low = pose.get('sy', 1.0) < 0.8
    # couronne autour du front
    d = {}
    hx_, hy_ = T(48, 27)
    vine(d, [(hx_ - 10, hy_ + 3), (hx_ - 5, hy_ - 1), (hx_, hy_ + 2), (hx_ + 5, hy_ - 1), (hx_ + 10, hy_ + 3)], rnd)
    if not low:
        add(d)
    # cou : deux lianes en travers
    d = {}
    nk = by
    vine(d, [(35, 53 + nk), (42, 48 + nk), (50, 52 + nk), (58, 47 + nk)], rnd)
    vine(d, [(34, 58 + nk), (42, 54 + nk), (52, 58 + nk), (60, 53 + nk)], rnd)
    if not low:
        add(d)
    # épaule / poitrail
    d = {}
    tangle(d, 30, 64 + by, 46, 74 + by, rnd, 3)
    add(d)
    # flanc arrière : plaque d'épines
    d = {}
    ru = pose.get('rear_up', 0)
    tangle(d, 56, 52 + by - ru, 78, 70 + by - ru, rnd, 4)
    add(d)
    # pattes avant : une bague de ronces
    fl = pose.get('legs', [(0, 0)] * 4)
    for i, x in ((0, 36), (1, 57)):
        d = {}
        dx, lift = fl[i]
        yy = 84 - lift // 2
        vine(d, [(x - 4 + dx, yy), (x + dx, yy + 3), (x + 4 + dx, yy)], rnd)
        add(d)
    # sélection / chute
    n = len(elems)
    order = list(range(n))
    random.Random(3).shuffle(order)
    keep = set(order[:max(0, round(n * density))])
    out = {}
    for i, d in enumerate(elems):
        if i not in keep:
            continue
        off = 0
        if fall:
            off = fall + (i * 5) % 7
        for (x, y), c in d.items():
            yy = y + off
            if off:
                yy = min(yy, GROUND - 1 - (i % 4))
            out[(x, yy)] = c
    return out


# ------------------------------------------------------------------ effets
def dust(g, cx, cy, n=3, big=1.0, seed=1):
    r = random.Random(seed)
    for k in range(n):
        x = cx + r.randint(-9, 9)
        y = cy + r.randint(-3, 3)
        blit(g, ell(x, y, 4 * big, 3 * big, 'x', 'X', None, None), None)


def steam(g, x, y, k):
    for j in range(2):
        blit(g, ell(x + (j + k) % 2 * 2 - 1, y - 3 * j - k, 2.5 - j * 0.5, 2, 'W', 'z', None, None), None)


def star(g, cx, cy):
    for (dx, dy, c) in ((0, 0, 'y'), (-1, 0, 'y'), (1, 0, 'y'), (0, -1, 'y'), (0, 1, 'y'), (-2, 0, 'Y'), (2, 0, 'Y'), (0, -2, 'Y'), (0, 2, 'Y')):
        if 0 <= cx + dx < S and 0 <= cy + dy < S:
            g[cy + dy][cx + dx] = c


def sparkle(g, cx, cy, c='H'):
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        g[cy + dy][cx + dx] = c if (dx or dy) else 'F'


def speed_lines(g, xs, y0, y1):
    for k, x in enumerate(xs):
        yy = y0 + (k * 5) % 7
        for y in range(yy, min(yy + 5, y1)):
            g[y][x] = 'z' if (y - yy) < 5 else '.'


# ------------------------------------------------------------------ poses de face
def L(*a):
    return list(a)


POSES = {}
for i, (by, hy) in enumerate([(0, 0), (-1, -1), (-1, -1), (0, 0)]):
    POSES['idle%d' % i] = dict(by=by, hy=0 if i < 2 else -1, hx=[0, 0, 1, 1][i], legs=[(0, 0)] * 4)
WALK = [dict(by=-1, legs=[(-1, 4), (0, 0), (0, 0), (1, 3)], hx=-1),
        dict(by=0, legs=[(0, 0)] * 4, hx=0),
        dict(by=-1, legs=[(0, 0), (1, 4), (-1, 3), (0, 0)], hx=1),
        dict(by=0, legs=[(0, 0)] * 4, hx=0)]
for i, p in enumerate(WALK):
    POSES['marche%d' % i] = p
POSES['prep0'] = dict(by=2, drop=16, sy=0.7, hy=0, rear_up=3, eyes='red', hx=0,
                      legs=[(-6, 13), (0, 0), (0, 0), (0, 0)], knee={0: (-1, 80)})
POSES['prep1'] = dict(by=3, drop=16, sy=0.7, hy=1, rear_up=4, eyes='amber', hx=1,
                      legs=[(-8, 2), (0, 0), (0, 0), (0, 0)], knee={0: (-4, 82)})
for i, (by, a, b) in enumerate([(1, 3, 0), (3, 0, 3), (1, 3, 0), (3, 0, 3)]):
    POSES['charge%d' % i] = dict(by=by, drop=15, sy=0.7, hy=1, eyes='red', hx=0, rear_up=1,
                                 legs=[(-8, a * 2), (8, b * 2), (-6, b * 2), (6, a * 2)])
POSES['touche'] = dict(by=0, hy=-2, eyes='hurt', hx=-1, legs=[(0, 0)] * 4)
for i, (hx, hy) in enumerate([(0, 0), (-1, 1)]):
    POSES['ko%d' % i] = dict(by=11, drop=36, sy=0.5, hy=0, eyes='ko', hx=hx, rear_up=-2,
                             legs=[(-10, -6), (10, -6), (-3, -3), (3, -3)])
POSES['pur0'] = dict(by=0, hy=0, eyes='green', legs=[(0, 0)] * 4)
POSES['pur1'] = dict(by=1, hy=2, drop=3, sy=0.9, eyes='green', legs=[(0, 0)] * 4)
POSES['pur2'] = dict(by=-1, hy=-2, eyes='green', legs=[(0, 0)] * 4)
POSES['pur3'] = dict(by=0, hy=-1, eyes='green', legs=[(0, 0)] * 4)

ORDER = (['idle%d' % i for i in range(4)] + ['marche%d' % i for i in range(4)] + ['prep0', 'prep1']
         + ['charge%d' % i for i in range(4)] + ['ko0', 'ko1', 'touche'] + ['pur%d' % i for i in range(4)])
GROUPS = [('idle', 0, 4), ('marche', 4, 4), ('preparation_charge', 8, 2), ('charge', 10, 4),
          ('assomme', 14, 2), ('touche', 16, 1), ('purifie', 17, 4)]
PUR_RONCES = {'pur0': (0.75, 0), 'pur1': (0.45, 5), 'pur2': (0.2, 12), 'pur3': (0.0, 0)}


def render_face(name):
    pose = POSES[name]
    g, T, ant = deer_front(pose)
    r = blank()
    ko = name.startswith('ko')
    pur = name.startswith('pur')
    # effets dans le corps
    if name.startswith('prep'):
        k = int(name[-1])
        dust(g, 30, GROUND - 2, 3 + k, 1.0 + 0.4 * k, seed=4 + k)
        steam(g, 43, 62, k)
        steam(g, 53, 62, 1 - k)
    if name.startswith('charge'):
        k = int(name[-1])
        speed_lines(g, [10, 17, 24, 71, 78, 85], 20 + k * 3, 74)
        dust(g, 22, GROUND - 2, 2, 1.2, seed=9 + k)
        dust(g, 74, GROUND - 2, 2, 1.2, seed=19 + k)
    if ko:
        k = int(name[-1])
        for a in range(3):
            ang = a * 2.094 + k * 1.0
            star(g, 48 + round(math.cos(ang) * 16), 52 + round(math.sin(ang) * 4) - 8 + (0 if k else 1))
        dust(g, 48, GROUND - 1, 2, 0.8, seed=2 + k)
    if pur:
        k = int(name[-1])
        if k >= 2:
            # petites feuilles sur les bois
            for (x, y) in (T(21, 8), T(75, 8), T(48, 8)):
                for dx, dy, c in ((0, 0, 'G'), (1, -1, 'H'), (-1, -1, 'G'), (0, -2, 'H')):
                    g[y + dy][x + dx] = c
        for (x, y) in ((30, 30), (68, 24), (22, 56), (78, 54), (48, 16))[: 2 + 2 * (k >= 2) + (k == 3)]:
            sparkle(g, x + (k % 2) * 2, y - k)
    if name == 'touche':
        # flash : tout le corps en blanc pur + petites lignes d'impact
        for y in range(S):
            for x in range(S):
                if g[y][x] not in ('.', 'e', 'g'):
                    g[y][x] = 'F'
        for (x, y, dx, dy) in ((20, 22, -1, -1), (76, 22, 1, -1), (14, 50, -1, 0), (82, 50, 1, 0)):
            for k in range(1, 5):
                g[y + dy * k][x + dx * k] = 'y'
    outline(g)
    # ronces
    if pur:
        dens, fall = PUR_RONCES[name]
        rd = ronces_face(pose, T, density=dens, fall=fall) if dens > 0 else {}
    elif ko:
        rd = ronces_face(pose, T, density=0.35)          # ronces en lambeaux quand il s'effondre
    else:
        rd = ronces_face(pose, T)
    for (x, y), c in rd.items():
        if 0 <= x < S and 0 <= y < S:
            r[y][x] = c
    return g, r, T, ant


# ------------------------------------------------------------------ vue de côté (tourné vers la gauche)
def deer_side(kind, k):
    """kind 'prep' (k 0-1) ou 'charge' (k 0-3). Cerf tourné vers la gauche, tête baissée."""
    global OFFX
    OFFX = 9
    g = blank()
    r = blank()
    if kind == 'prep':
        by = 3 + k
        phases = [(-3, 12, 0), (-8, 4, 0)][k]
        gait = None
    else:
        by = [1, 3, 1, 3][k]
    ground = GROUND - 1
    # pattes : (x haut, x bas, lift)
    if kind == 'charge':
        ext = [0, 1, 2, 1][k]          # 0 étiré, 2 ramassé
        far_f = ((34, 18 + ext * 7), 0)
        legs = [  # (xtop, ytop, xfoot, lift, dark)
            (70, 66, 78 + (2 - ext) * 3 + 6, 5 * (ext == 2), True),
            (62, 66, 64 + (2 - ext) * 2 + 6, 3 * (ext > 0), False),
            (30, 66, 14 + ext * 7, 6 * (ext == 2), True),
            (38, 66, 26 + ext * 5, 4 * (ext < 1), False),
        ]
        # ordre arrière-avant, foncé derrière
        legs = [(68, 64, 78 - ext * 5, 4 * (ext == 2), True), (30, 64, 14 + ext * 6, 4 * (ext == 2), True),
                (60, 64, 68 - ext * 5, 5 * (ext == 0), False), (38, 64, 24 + ext * 7, 4 * (ext == 0), False)]
    else:
        legs = [(68, 64, 70, 0, True), (30, 64, 24, 0, True), (60, 64, 62, 0, False),
                (38, 64, 38, 0, False)]
        if k == 0:
            legs[3] = (38, 64, 20, 10, False)
        else:
            legs[3] = (38, 64, 18, 0, False)
    body_dark = {True: ('s', 'S', 'w'), False: ('w', 's', 'W')}
    for (xt, yt, xf, lift, dark) in legs:
        b, s_, h_ = body_dark[dark]
        top = (xt, yt + by)
        foot = (xf, ground - lift + (0 if dark else 2))
        mid = ((xt + xf) // 2 + (-3 if kind == 'charge' else 0), (yt + by + foot[1]) // 2)
        blit(g, limb(top, mid, 8, 6, b, s_, h_), 'S')
        blit(g, limb(mid, foot, 6, 5, b, s_, h_, hoof=5), 'S')
    # corps
    blit(g, ell(53, 58 + by, 25, 14), 'S')
    blit(g, ell(34, 60 + by, 14, 14), 'S')
    blit(g, ell(80, 55 + by, 4, 5, 'W', 'w', 's', None), 'S')       # queue
    # cou + tête baissée vers la gauche
    neck = {}
    for t in range(0, 14):
        cxn = 30 - t * 0.7
        cyn = 52 + by + t * 0.9
        brush(neck, round(cxn), round(cyn), 6, 'w')
    for (x, y), c in list(neck.items()):
        if (x + 1, y) not in neck or (x, y + 1) not in neck:
            neck[(x, y)] = 's'
    blit(g, neck, 'S')
    hxx, hyy = 16, 66 + by
    blit(g, ell(hxx, hyy, 10, 8), 'S')
    blit(g, ell(hxx - 8, hyy + 4, 6, 4.5, 'w', 's', 'S', 'W'), 'S')
    blit(g, {(hxx - 12 + i, hyy + 4 + j): 'n' for i in range(3) for j in range(2)}, None)
    blit(g, ell(hxx + 6, hyy - 7, 3.5, 3, 'w', 's', None, 'W'), 'S')   # oreille
    eyec = 'r' if kind == 'charge' or k == 0 else 'a'
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            g[hyy - 2 + j][hxx - 3 + i + OFFX] = 'e'
    g[hyy - 2][hxx - 3 + OFFX] = eyec
    g[hyy - 1][hxx - 3 + OFFX] = eyec
    g[hyy - 3][hxx - 4 + OFFX] = 'g'
    # bois vers l'avant (gauche) et en bas
    ant = {}
    bulbs = []
    for depth, (sx, sy_) in enumerate(((0, 0), (5, -3))):         # bois proche + bois lointain décalé
        base = (hxx + 4 + sx, hyy - 8 + sy_)
        pts = [base, (base[0] - 5, base[1] - 7), (base[0] - 12, base[1] - 10), (base[0] - 19, base[1] - 9), (base[0] - 26, base[1] - 5)]
        for a, b in zip(pts, pts[1:]):
            seg(ant, a, b, 2 if depth == 0 else 1, 1, 'b' if depth == 0 else 'B')
        for t in ((pts[1], (pts[1][0] - 7, pts[1][1] - 9)), (pts[2], (pts[2][0] - 9, pts[2][1] - 9)),
                  (pts[3], (pts[3][0] - 9, pts[3][1] + 4))):
            seg(ant, t[0], t[1], 1, 0, 'b' if depth == 0 else 'B')
        if depth == 0:
            bulbs.append((pts[-1][0], pts[-1][1]))
            bulbs.append((pts[2][0] - 9, pts[2][1] - 9))
        else:
            bulbs.append((pts[-1][0] + 1, pts[-1][1] + 1))
    out = dict(ant)
    for (x, y) in ant:
        if (x + 1, y) not in ant and (x, y + 1) not in ant:
            out[(x, y)] = 'd'
        elif (x - 1, y) not in ant or (x, y - 1) not in ant:
            out[(x, y)] = 'h' if ant[(x, y)] == 'b' else 'B'
    blit(g, out, 'd')
    # effets
    if kind == 'prep':
        dust(g, 22, GROUND - 1, 3 + k, 1.0 + 0.4 * k, seed=11 + k)
        steam(g, hxx - 15, hyy + 1, k)
    else:
        speed_lines(g, [72, 79, 85], 30, 70)
        dust(g, 80, GROUND - 2, 2, 1.3, seed=21 + k)
    outline(g)
    # ronces
    rnd = random.Random(5 + k)
    d = {}
    for (x, y), c in ant.items():
        if (x + y) % 4 == 0:
            d[(x, y - 1)] = 'v'
            d[(x - 1, y)] = 'u'
    for bx, by_ in bulbs[:2]:
        knot(d, bx, by_ + 3, 2)
    vine(d, [(hxx + 6, hyy - 8 + 0), (hxx + 16, hyy - 12), (hxx + 24, hyy - 10)], rnd)
    vine(d, [(30, 50 + by), (40, 46 + by), (52, 50 + by), (62, 45 + by)], rnd)
    vine(d, [(32, 58 + by), (44, 54 + by), (56, 58 + by)], rnd)
    tangle(d, 52, 52 + by, 72, 66 + by, rnd, 4)
    tangle(d, 28, 56 + by, 40, 66 + by, rnd, 2)
    for (x, y), c in d.items():
        x += OFFX
        if 0 <= x < S and 0 <= y < S:
            r[y][x] = c
    OFFX = 0
    return g, r, [(x + 9, y) for x, y in bulbs]


SIDE_ORDER = [('prep', 0), ('prep', 1), ('charge', 0), ('charge', 1), ('charge', 2), ('charge', 3)]


# ------------------------------------------------------------------ ombre
def shadow():
    g = blank()
    for y in range(S):
        for x in range(S):
            dx, dy = (x + 0.5 - 48) / 40, (y + 0.5 - 90) / 7
            if dx * dx + dy * dy <= 1:
                g[y][x] = 'sh'
    return g


# ------------------------------------------------------------------ bulbe 16x16
BPAL = dict(PAL)


def bulb(state, k):
    g = blank(16, 16)

    def P(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            g[y][x] = c
    if state == 'ok':
        cy = 8 + (0 if k == 0 else 0)
        rx = 6.0 if k == 0 else 6.6
        ry = 6.0 if k == 0 else 6.6
        d = ell(8, cy, rx, ry, 'u', 'm', 'v', 'U')
        for (x, y), c in d.items():
            P(x, y, c)
        # épines autour (pulsation : plus longues à k=1)
        sp = [(8, 0), (3, 2), (13, 2), (1, 7), (15, 7), (3, 13), (13, 13), (8, 15)]
        for (x, y) in sp:
            P(x, y, 'v')
        if k == 1:
            for (x, y) in ((8, 1), (3, 3), (12, 3), (2, 7), (14, 7)):
                P(x, y, 'U')
        # oeil de corruption
        for (x, y) in ((6, 7), (7, 7), (9, 7), (10, 7), (6, 8), (7, 8), (9, 8), (10, 8)):
            P(x, y, 'v')
        P(7, 8, 'r')
        P(9, 8, 'r')
        P(6, 6, 'U')
        P(8, 4, 'U') if k else None
    else:
        # k : 0 fissure + éclair, 1 éclats projetés, 2 poussière / cendres
        if k == 0:
            d = ell(8, 8, 6, 6, 'u', 'm', 'v', 'U')
            for (x, y), c in d.items():
                P(x, y, c)
            for (x, y) in ((8, 3), (7, 5), (9, 6), (8, 8), (7, 10), (8, 12)):
                P(x, y, 'F')
            for (x, y) in ((8, 4), (8, 7), (8, 9), (8, 11)):
                P(x, y, 'y')
        elif k == 1:
            for (cx, cy, c) in ((4, 4, 'u'), (12, 4, 'm'), (3, 11, 'm'), (12, 11, 'u'), (8, 2, 'U'), (8, 13, 'v')):
                for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    P(cx + dx, cy + dy, c)
            for (x, y) in ((8, 8), (7, 7), (9, 9), (7, 9), (9, 7)):
                P(x, y, 'y')
            P(8, 8, 'F')
        else:
            for (x, y, c) in ((3, 5, 'm'), (12, 6, 'v'), (5, 11, 'm'), (10, 12, 'v'), (8, 8, 'u'), (1, 9, 'v'), (14, 10, 'm')):
                P(x, y, c)
            for (x, y) in ((6, 3), (9, 2), (13, 8), (2, 3)):
                P(x, y, 'z')
    outline(g)
    return g


# ------------------------------------------------------------------ icône du sceau 24x24
def sceau():
    g = blank(24, 24)

    def P(x, y, c):
        if 0 <= x < 24 and 0 <= y < 24:
            g[y][x] = c
    for y in range(24):
        for x in range(24):
            dx, dy = x + 0.5 - 12, y + 0.5 - 12
            rr = math.hypot(dx, dy)
            if rr <= 11:
                v = -(dx * -0.45 + dy * -0.8) / 11
                c = 'G' if rr > 8 else 'e2'
                if rr > 8:
                    c = 'H' if v < -0.55 else 'G'
                    if v > 0.45:
                        c = 'g2'
                else:
                    c = 'in'
                    if rr > 7:
                        c = 'in2'
                P(x, y, c)
    # glyphe : arbre/racines (tronc, deux branches, racines)
    for y in range(6, 17):
        P(12, y, 'lf')
        P(11, y, 'lf2')
    for (x, y) in ((10, 8), (9, 7), (8, 6), (14, 8), (15, 7), (16, 6), (10, 11), (9, 10), (14, 11), (15, 10)):
        P(x, y, 'lf')
    for (x, y) in ((8, 5), (7, 5), (16, 5), (17, 5), (9, 9), (15, 9)):
        P(x, y, 'lf3')
    for (x, y) in ((11, 17), (10, 18), (9, 18), (13, 17), (14, 18), (15, 18), (12, 18), (12, 19), (8, 17), (16, 17)):
        P(x, y, 'lf2')
    return g


SPAL = dict(PAL)
SPAL.update({'e2': '#263a5e', 'g2': '#3a5a2c', 'in': '#2e2018', 'in2': '#43291c',
             'lf': '#9ad060', 'lf2': '#6a9a48', 'lf3': '#d8f0a0', 'sh': '#1b1420'})


def px2(g, pal):
    return [[rgba(pal[c]) if pal[c] else (0, 0, 0, 0) for c in row] for row in g]


def sheet_png(grids, pal=PAL):
    return CF.sheet([px2(g, pal) for g in grids])


# ------------------------------------------------------------------ principal
def main():
    prev = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(ITEMS, exist_ok=True)
    bodies, ronces, bulbs = [], [], {}
    for name in ORDER:
        g, r, T, ant = render_face(name)
        bodies.append(g)
        ronces.append(r)
        if not name.startswith('pur'):
            bulbs[name] = [list(p) for p in bulb_positions(T)]
    sides_b, sides_r, side_bulbs = [], [], {}
    for kind, k in SIDE_ORDER:
        g, r, bl = deer_side(kind, k)
        sides_b.append(g)
        sides_r.append(r)
        side_bulbs['%s_cote%d' % (kind, k)] = [list(p) for p in bl]
    sh = shadow()
    bgrids = [bulb('ok', 0), bulb('ok', 1), bulb('boom', 0), bulb('boom', 1), bulb('boom', 2)]
    pal_sh = dict(PAL)
    pal_sh['sh'] = '#1b1420'
    CF.save_png(os.path.join(OUT, 'sylve.png'), sheet_png(bodies))
    CF.save_png(os.path.join(OUT, 'sylve_ronces.png'), sheet_png(ronces))
    CF.save_png(os.path.join(OUT, 'sylve_cote.png'), sheet_png(sides_b))
    CF.save_png(os.path.join(OUT, 'sylve_cote_ronces.png'), sheet_png(sides_r))
    # ombre semi-transparente (seul pixel semi-transparent voulu)
    shpx = [[(27, 20, 32, 110) if c == 'sh' else (0, 0, 0, 0) for c in row] for row in sh]
    CF.save_png(os.path.join(OUT, 'sylve_ombre.png'), shpx)
    CF.save_png(os.path.join(OUT, 'bulbe.png'), sheet_png(bgrids))
    CF.save_png(os.path.join(ITEMS, 'sceau_racines.png'), px2(sceau(), SPAL))
    meta = {
        'cellule': [96, 96], 'origine': [48, 94],
        'sylve.png': {'ordre': ORDER, 'animations': {n: {'debut': a, 'nombre': c} for n, a, c in GROUPS}},
        'sylve_cote.png': {'ordre': ['%s_cote%d' % t for t in SIDE_ORDER], 'orientation': 'gauche'},
        'bulbe.png': {'cellule': [16, 16], 'ordre': ['intact0', 'intact1', 'eclate0', 'eclate1', 'eclate2']},
        'bulbes_face_xy_centre_par_frame': bulbs,
        'bulbes_cote_xy_centre_par_frame': side_bulbs,
    }
    with open(os.path.join(OUT, 'sylve.json'), 'w') as f:
        json.dump(meta, f, indent=1)
    if prev:
        os.makedirs(prev, exist_ok=True)
        floor = (138, 90, 52, 255)
        grey = (154, 148, 140, 255)

        def comp(fr_list, rs, cols, bgc, scale):
            n = len(fr_list)
            rows = (n + cols - 1) // cols
            img = [[bgc] * (cols * S) for _ in range(rows * S)]
            for i, (a, b) in enumerate(zip(fr_list, rs)):
                ox, oy = (i % cols) * S, (i // cols) * S
                for lay in (a, b):
                    for y in range(S):
                        for x in range(S):
                            c = lay[y][x]
                            if c != '.':
                                img[oy + y][ox + x] = rgba(PAL[c])
            return img
        CF.save_png(os.path.join(prev, 'sylve_apercu_x2.png'), comp(bodies, ronces, 7, grey, 2), 2)
        CF.save_png(os.path.join(prev, 'sylve_corps_seul_x2.png'), comp(bodies, [blank()] * len(bodies), 7, floor, 2), 2)
        CF.save_png(os.path.join(prev, 'sylve_cote_x2.png'), comp(sides_b, sides_r, 6, grey, 2), 2)
        CF.save_png(os.path.join(prev, 'sylve_1x_x3.png'), comp(bodies[:3] + bodies[8:11], ronces[:3] + ronces[8:11], 6, grey, 1), 3)
        CF.save_png(os.path.join(prev, 'bulbes_x8.png'), [[p if p[3] else (154, 148, 140, 255) for p in row] for row in sheet_png(bgrids)], 8)
        CF.save_png(os.path.join(prev, 'sceau_x8.png'), [[p if p[3] else (154, 148, 140, 255) for p in row] for row in px2(sceau(), SPAL)], 8)
    print('ok', len(ORDER), 'frames face,', len(SIDE_ORDER), 'frames cote')


if __name__ == '__main__':
    main()
