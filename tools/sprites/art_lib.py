"""Outils de dessin communs au village et aux intérieurs (dessin final des tilesets) — Les Trois Sceaux.

Réutilise le canevas, la palette et les textures de foret.py (même jeu, même lumière : haut gauche, contour sombre d'1 px).
Sans Pillow : encodeur PNG dans tsplan.py.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import foret as F  # noqa: E402
from foret import P, Cv, T, rnd, vnoise, shadow, mass, GRASS, PATH, SHALLOW, DEEP, rgba, terrain_tile, wset  # noqa: E402,F401

EXTRA = dict(
    # pavés (gris-violet, même famille que le temple)
    p_hi='#d4d0e0', p_lt='#b8b4cc', p_md='#9c98b4', p_dk='#6e6a88', p_jt='#54506c',
    # crépi crème
    pl_hi='#f4ead0', pl_lt='#e6d8b0', pl_md='#d0bd90', pl_dk='#a8946c',
    # toits
    ra_hi='#ea6a4c', ra_lt='#cc4a32', ra_md='#a43430', ra_dk='#6e2230',
    rb_hi='#8e9eb6', rb_lt='#6e7e98', rb_md='#566480', rb_dk='#3c4662',
    rc_hi='#f0d878', rc_lt='#d4b458', rc_md='#ac8c3c', rc_dk='#7a6030',
    # planches
    pk_hi='#c8946a', pk_lt='#a6764a', pk_md='#86583a', pk_dk='#5e3a22',
    # verre, métal, suie, feu
    gl_hi='#b8dcf0', gl_md='#78a8d0', gl_dk='#3c5a8a',
    m_hi='#c8ccd8', m_lt='#9aa0b0', m_md='#6a7080', m_dk='#3c4050',
    s_lt='#5a5460', s_md='#3e3a48', s_dk='#2a2632',
    fi_y='#ffd860', fi_o='#f08a28', fi_r='#e2342c', fi_d='#961c28',
    # ravin
    v_lt='#4a3a5c', v_md='#2a1c34', v_dk='#1c1224',
    # château lointain
    ch_hi='#b4a6c4', ch_lt='#9a8aac', ch_md='#7a6a8c', ch_dk='#5a4c6c', ch_ro='#4a4a6c', ch_rd='#34344e',
    gold_hi='#f0d070', white='#f4f0e8', pink='#e060a0', orange2='#e08830', red2='#d0402c',
    mist='#e6ecf6',
)
P.update({k: rgba(v) for k, v in EXTRA.items()})
O = P['O']


def blank():
    return Cv()


def tex(t):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = t[y][x]
    return cv


def box(cv, x0, y0, x1, y1, hi, md, dk, edge=True):
    """Bloc ombré (lumière haut gauche) : arête claire en haut et à gauche, sombre en bas et à droite."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = md
            if edge:
                if y == y0 or x == x0:
                    c = hi
                if y == y1 or x == x1:
                    c = dk
            cv.set(x, y, c)


def ell(cv, cx, cy, rx, ry, c, only=None):
    for y in range(cv.h):
        for x in range(cv.w):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                if only is None or cv.p[y][x] in only:
                    cv.p[y][x] = c


def ell_shade(cv, cx, cy, rx, ry, pal, seed=0, noise=0.2):
    """Ellipse ombrée (hi, lt, md, dk) lumière en haut à gauche."""
    hi, lt, md, dk = pal
    for y in range(cv.h):
        for x in range(cv.w):
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = nx * nx + ny * ny
            if d <= 1:
                v = -(nx + ny) * 0.5 + (rnd(x, y, seed) - 0.5) * noise - d * 0.2 + 0.1
                cv.p[y][x] = hi if v > 0.5 else lt if v > 0.12 else md if v > -0.3 else dk


def hline(cv, x0, x1, y, c):
    for x in range(x0, x1 + 1):
        cv.set(x, y, c)


def vline(cv, x, y0, y1, c):
    for y in range(y0, y1 + 1):
        cv.set(x, y, c)


def dither(cv, x0, y0, x1, y1, c, phase=0, only=None):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x + y + phase) % 2 == 0 and 0 <= x < cv.w and 0 <= y < cv.h:
                if only is None or cv.p[y][x] in only:
                    cv.p[y][x] = c


def paste(dst, src, ox, oy):
    """Colle src (Cv) sur dst (Cv) en ignorant les pixels transparents."""
    for y in range(src.h):
        for x in range(src.w):
            c = src.p[y][x]
            if c is not None:
                dst.set(ox + x, oy + y, c)


def slice_tile(cv, col, row):
    return cv.crop(col * T, row * T)


def mirror_tile(p):
    return [r[::-1] for r in p]


def outline_all(cv, c=None):
    cv.outline(c or O)


def ground_shadow(cv, cx, cy, rx, ry, c=None):
    shadow(cv, cx, cy, rx, ry, c or P['g_dk'])


def to_rgb(c):
    return c[:3]


def tint(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (c[3],)


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (a[3] if len(a) > 3 else 255,)


def haze(pix, desat=0.5, cool=(0.86, 0.93, 1.06), blend=0.22, hz=(0xa6, 0xb4, 0xcc), dim=0.95):
    """Recolore une planche (liste de lignes de tuples RGBA / None) : plus froide, désaturée, voilée (variante brume)."""
    out = []
    for row in pix:
        nr = []
        for c in row:
            if c is None:
                nr.append(None)
                continue
            r, g, b = c[:3]
            L = 0.3 * r + 0.59 * g + 0.11 * b
            r, g, b = (r + (L - r) * desat, g + (L - g) * desat, b + (L - b) * desat)
            r, g, b = r * cool[0] * dim, g * cool[1] * dim, b * cool[2] * dim
            r, g, b = (r + (hz[0] - r) * blend, g + (hz[1] - g) * blend, b + (hz[2] - b) * blend)
            nr.append((int(max(0, min(255, r))), int(max(0, min(255, g))), int(max(0, min(255, b))), c[3]))
        out.append(nr)
    return out
