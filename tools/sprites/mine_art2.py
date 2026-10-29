"""Mine Effondrée, dessin final, partie 2 : wagonnets, minerai, étais, mobilier, cristaux, arène, murs fissurés, éboulis.

Même palette et mêmes outils que mine_art.py (les fonctions s'enregistrent dans le même REG).
"""
import math

from mine_art import *  # noqa: F401,F403
from mine_art import (REG, reg, P, O, Cv, T, rnd, vnoise, wall, floor_tex, FLOOR, cap_color, face_color, mass, wood_beam, wood_post,
                      blank_tile)

WALLP = (P['wf_hi'], P['wf_lt'], P['wf_md'], P['wf_dk'])
FLP = (P['fl_hi'], P['fl_lt'], P['fl_md'], P['fl_dk'])
COAL = ((106, 94, 108, 255), (78, 68, 82, 255), (56, 48, 60, 255), (40, 34, 44, 255))
ARP = (P['ar_hi'], P['ar_lt'], P['ar_md'], P['ar_dk'])
CYP = dict(w=P['cy_w'], hi=P['cy_hi'], lt=P['cy_lt'], md=P['cy_md'], dk=P['cy_dk'])
RDP = dict(w=P['rd_hi'], hi=P['rd_hi'], lt=P['rd_lt'], md=P['rd_md'], dk=P['rd_dk'])


# ------------------------------------------------------------------ outils
def rocks(cv, specs, pal, seed=0, edge=O):
    """Plusieurs blocs de roche (cx, cy, rx, ry), chacun ombré et cerné séparément (du fond vers l'avant)."""
    for i, (cx, cy, rx, ry) in enumerate(specs):
        t = Cv(cv.w, cv.h)
        mass(t, [(cx, cy, rx, ry)], pal, seed + i * 7, 0.3)
        t.outline(edge)
        for y in range(cv.h):
            for x in range(cv.w):
                if t.p[y][x] is not None:
                    cv.p[y][x] = t.p[y][x]


def polyfill(cv, pts, fn):
    def inside(px, py):
        c = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                c = not c
            j = i
        return c
    for y in range(int(min(p[1] for p in pts)) - 1, int(max(p[1] for p in pts)) + 2):
        for x in range(int(min(p[0] for p in pts)) - 1, int(max(p[0] for p in pts)) + 2):
            if 0 <= x < cv.w and 0 <= y < cv.h and inside(x + 0.5, y + 0.5):
                cv.p[y][x] = fn(x, y)


def line(cv, pts, c):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(n + 1):
            cv.set(round(xa + (xb - xa) * i / n), round(ya + (yb - ya) * i / n), c)


def split(cv, n=2, vertical=False):
    """Découpe un canevas large (ou haut) en tuiles 32x32."""
    out = []
    for k in range(n):
        out.append([row[k * 32:(k + 1) * 32] for row in cv.p] if not vertical else [row[:32] for row in cv.p[k * 32:(k + 1) * 32]])
    return out


def flecks(cv, specs, cols):
    for (x, y) in specs:
        cv.set(x, y, cols[(x + y) % len(cols)])


GOLD = (P['ge_hi'], P['ge_md'], P['ge_dk'])


def tex_in(t, fn):
    for y in range(T):
        for x in range(T):
            v = fn(x, y)
            if v is not None:
                t[y][x] = v


# ------------------------------------------------------------------ wagonnets
def wagon(w, rim_y, face_y0, face_y1, x0, x1, wheels, heap=None, bands=()):
    cv = Cv(w, 32)
    # roues derrière
    for wx in wheels:
        for y in range(32):
            for x in range(w):
                if (x + 0.5 - wx) ** 2 + (y + 0.5 - 28) ** 2 <= 11:
                    cv.p[y][x] = P['mt_md'] if (x + 0.5 - wx) ** 2 + (y + 0.5 - 28) ** 2 > 3 else P['mt_dk']
    # intérieur sombre visible
    for y in range(rim_y, face_y0 + 1):
        for x in range(x0 + 1, x1):
            cv.p[y][x] = P['hl_1'] if y > rim_y + 1 else P['mt_dk']
    if heap:
        rocks(cv, heap, COAL, 11)
    # face avant en planches
    for y in range(face_y0, face_y1 + 1):
        for x in range(x0 + (1 if y > face_y1 - 3 else 0), x1 + 1 - (1 if y > face_y1 - 3 else 0)):
            c = P['wd_md']
            if (y - face_y0) % 5 == 4:
                c = P['wd_dp']
            elif (y - face_y0) % 5 == 0:
                c = P['wd_lt']
            if rnd(x, y, 31) < 0.06:
                c = P['wd_dk']
            cv.p[y][x] = c
    for bx in bands:                                                 # sangles de fer
        for y in range(face_y0, face_y1 + 1):
            for x in (bx, bx + 1, bx + 2):
                cv.p[y][x] = P['mt_lt'] if x == bx else P['mt_md'] if x == bx + 1 else P['mt_dk']
        cv.p[face_y0 + 2][bx + 1] = P['mt_hi']
        cv.p[face_y1 - 2][bx + 1] = P['mt_hi']
    # bord supérieur en fer
    for x in range(x0, x1 + 1):
        cv.p[face_y0 - 1][x] = P['mt_hi'] if x < x0 + 4 or x % 7 else P['mt_lt']
        cv.p[face_y0][x] = P['mt_md']
    cv.outline(O)
    return cv


@reg('wagonnet_g', 'wagonnet_d')
def wagonnet_h(n, d):
    key = '_wagon_h'
    if key not in REG:
        REG[key] = wagon(64, 10, 13, 25, 4, 59, (13, 25, 39, 51),
                         heap=[(14, 10, 8, 4), (26, 9, 8, 4.5), (38, 10, 8, 4), (50, 10, 7, 4)], bands=(9, 31, 53))
        flecks(REG[key], [(12, 8), (25, 7), (37, 8), (47, 8), (30, 9)], GOLD)
    a, b = split(REG[key])
    return a if n == 'wagonnet_g' else b


@reg('wagonnet_v')
def wagonnet_v(n, d):
    cv = wagon(32, 11, 14, 26, 6, 25, (10, 22), heap=[(11, 11, 6, 3.5), (20, 11, 6, 3.5)], bands=(9, 20))
    flecks(cv, [(11, 9), (19, 9)], GOLD)
    return cv.p


@reg('wagonnet_minerai')
def wagonnet_minerai(n, d):
    cv = wagon(32, 11, 14, 26, 6, 25, (10, 22), heap=[(10, 10, 6, 5), (16, 7, 7, 6), (22, 10, 6, 5), (16, 11, 8, 4)], bands=(9, 20))
    flecks(cv, [(9, 8), (15, 4), (21, 7), (13, 9), (19, 10), (24, 9)], GOLD)
    return cv.p


@reg('wagonnet_renverse')
def wagonnet_renverse(n, d):
    cv = Cv()
    rocks(cv, [(22, 24, 8, 5), (26, 27, 5, 3), (18, 27, 6, 3.5), (28, 22, 3, 3)], COAL, 3)
    flecks(cv, [(20, 21), (24, 24), (17, 26), (27, 26)], GOLD)
    for y in range(14, 28):                                          # caisse couchée
        for x in range(3, 20):
            c = P['wd_md']
            if (x - 3) % 5 == 4:
                c = P['wd_dp']
            elif (x - 3) % 5 == 0:
                c = P['wd_lt']
            cv.p[y][x] = c
    for y in range(14, 28):
        for x in (7, 8):
            cv.p[y][x] = P['mt_md'] if x == 8 else P['mt_lt']
        for x in (15, 16):
            cv.p[y][x] = P['mt_md'] if x == 16 else P['mt_lt']
    for y in range(13, 29):                                          # ouverture sombre côté droit
        for x in range(18, 22):
            if (x - 18) < 3 and abs(y - 21) < 7 - (x - 18):
                cv.p[y][x] = P['hl_1']
    for k in range(2):                                               # roue en l'air
        for y in range(32):
            for x in range(32):
                if (x + 0.5 - (7 + k * 9)) ** 2 + (y + 0.5 - 10) ** 2 <= 10:
                    cv.p[y][x] = P['mt_md'] if (x + 0.5 - (7 + k * 9)) ** 2 + (y + 0.5 - 10) ** 2 > 3 else P['mt_dk']
    cv.outline(O)
    return cv.p


@reg('minerai_tas_a', 'minerai_tas_b')
def tas(n, d):
    cv = Cv()
    cv.p = [[None] * T for _ in range(T)]
    if n.endswith('_a'):
        rocks(cv, [(16, 24, 13, 5), (9, 20, 7, 6), (23, 20, 7, 6), (16, 16, 9, 8), (12, 12, 5, 5), (21, 13, 5, 5)], COAL, 5)
        flecks(cv, [(9, 19), (22, 18), (15, 13), (12, 11), (20, 12), (17, 22), (6, 22), (26, 23)], GOLD)
    else:
        rocks(cv, [(16, 24, 13, 5), (10, 20, 8, 6), (22, 21, 7, 5), (14, 15, 8, 7), (21, 14, 6, 6)], COAL, 9)
        flecks(cv, [(10, 19), (14, 13), (22, 13), (20, 20)], GOLD)
        for (x, y) in ((16, 11), (17, 12), (16, 12), (8, 21), (24, 20), (25, 20)):
            cv.set(x, y, P['cy_lt'] if (x + y) % 2 else P['cy_hi'])
    return cv.p


@reg('minerai_sol')
def minerai_sol(n, d):
    cv = Cv()
    rocks(cv, [(9, 22, 3.5, 2.5), (18, 25, 4, 3), (24, 19, 3, 2.5), (13, 15, 2.5, 2)], COAL, 2)
    flecks(cv, [(9, 21), (18, 24), (24, 18), (13, 14)], GOLD)
    return cv.p


# ------------------------------------------------------------------ étais, poutres, mobilier
@reg('etai_base')
def etai_base(n, d):
    t = blank_tile()
    wood_post(t, 12, 19, 0, 24)
    for y in range(24, 31):                                          # socle de pierre
        for x in range(8, 24):
            t[y][x] = P['fl_hi'] if y == 24 else P['fl_md'] if y < 29 else P['fl_dk']
            if x in (8, 23) or y == 30:
                t[y][x] = O
    for x in range(8, 24):
        t[23][x] = O if x < 12 or x > 19 else t[23][x]
    return t


@reg('etai_haut')
def etai_haut(n, d):
    t = blank_tile()
    wood_post(t, 12, 19, 12, 31)
    wood_beam(t, 0, 31, 3, 11)
    for k in range(5):                                               # jambes de force
        for x in (7 - k, 24 + k):
            if 0 <= x < 32 and 12 + k < 32:
                t[12 + k][x] = P['wd_lt'] if x < 16 else P['wd_dk']
                t[12 + k][x + 1 if x < 16 else x - 1] = P['wd_md']
    t[7][16] = P['mt_lt']
    return t


@reg('poutre_h')
def poutre_h(n, d):
    t = blank_tile()
    wood_beam(t, 0, 31, 3, 11)
    for x in (5, 26):
        t[7][x] = P['mt_lt']
    return t


@reg('poutre_g')
def poutre_g(n, d):
    t = blank_tile()
    wood_beam(t, 10, 31, 3, 11)
    wood_post(t, 11, 18, 12, 31)
    for k in range(5):
        t[12 + k][19 + k] = P['wd_dk']
        t[12 + k][18 + k] = P['wd_md']
    return t


@reg('poutre_d')
def poutre_d(n, d):
    t = blank_tile()
    wood_beam(t, 0, 21, 3, 11)
    wood_post(t, 13, 20, 12, 31)
    for k in range(5):
        t[12 + k][12 - k] = P['wd_lt']
        t[12 + k][13 - k] = P['wd_md']
    return t


@reg('etai_mur')
def etai_mur(n, d):
    t = blank_tile()
    wood_post(t, 11, 20, 0, 31)
    for y in (6, 23):
        for x in range(9, 23):
            t[y][x] = P['mt_md']
            t[y + 1][x] = P['mt_dk']
        t[y][12] = P['mt_hi']
        t[y][19] = P['mt_hi']
    return t


@reg('planches_sol')
def planches_sol(n, d):
    t = blank_tile()
    for y in range(T):
        for x in range(T):
            row = y // 8
            c = P['wd_md'] if (row + (x + row * 11) // 14) % 2 else P['wd_lt']
            if y % 8 == 7:
                c = P['wd_dp']
            elif y % 8 == 0:
                c = P['wd_hi'] if rnd(x, y, 5) < 0.5 else c
            if (x + row * 11) % 14 == 13:
                c = P['wd_dk']
            if rnd(x, y, 33) < 0.05:
                c = P['wd_dk']
            t[y][x] = c
    for row in range(4):
        for nx in (2, 29):
            t[row * 8 + 3][nx] = P['mt_lt']
    return t


@reg('lanterne')
def lanterne(n, d):
    cv = Cv()
    for y in range(0, 9):
        cv.set(16, y, P['mt_lt'] if y % 2 else P['mt_dk'])
    for y in range(8, 23):
        for x in range(11, 22):
            if y in (8, 9):
                c = P['mt_dk']
            elif y >= 21:
                c = P['mt_dk']
            elif x in (11, 21):
                c = P['mt_md']
            else:
                c = P['lamp_y'] if abs(x - 16) < 3 and 12 <= y <= 18 else P['lamp_o']
            cv.set(x, y, c)
    cv.set(15, 13, P['cy_w'])
    cv.set(16, 13, P['cy_w'])
    for x in (13, 19):
        for y in range(10, 21):
            cv.set(x, y, P['mt_dk'])
    cv.outline(O)
    for y in range(18, 31):                                          # halo chaud
        for x in range(6, 27):
            if (x + y) % 2 == 0 and cv.p[y][x] is None and math.hypot((x - 16) / 1.0, (y - 14) / 1.1) < 11 and math.hypot(x - 16, y - 14) > 7.5:
                cv.p[y][x] = (200, 140, 60, 255)
    return cv.p


@reg('pioche_sol')
def pioche_sol(n, d):
    cv = Cv()
    line(cv, [(7, 27), (24, 10)], P['wd_md'])
    line(cv, [(7, 26), (24, 9)], P['wd_lt'])
    line(cv, [(8, 27), (25, 10)], P['wd_dk'])
    for (x, y) in ((19, 4), (20, 4), (21, 4), (22, 5), (23, 5), (24, 6), (25, 7), (26, 8), (27, 10), (28, 12), (18, 5), (17, 6), (29, 14)):
        cv.set(x, y, P['mt_lt'])
        cv.set(x, y + 1, P['mt_md'])
    cv.set(19, 3, P['mt_hi'])
    cv.set(21, 3, P['mt_hi'])
    cv.set(17, 7, P['mt_dk'])
    cv.set(29, 15, P['mt_dk'])
    cv.outline(O)
    for x in range(6, 26):
        y = 29 - (x - 6) * 17 // 19 + 3
        if cv.get(x, y) is None and x % 2 == 0:
            cv.set(x, y, (27, 20, 32, 255))
    return cv.p


@reg('tonneau')
def tonneau(n, d):
    cv = Cv()
    for y in range(7, 29):
        for x in range(6, 26):
            dx = (x - 15.5) / 10
            edge = 1 - dx * dx
            if y < 12:
                if ((x - 15.5) / 9.5) ** 2 + ((y - 9.5) / 4.0) ** 2 > 1 and y < 9:
                    continue
            if y > 26 and ((x - 15.5) / 9.5) ** 2 > 1 - (y - 26) * 0.2:
                continue
            k = -dx * 0.9 + (rnd(x, y, 41) - 0.5) * 0.2
            c = P['wd_hi'] if k > 0.62 else P['wd_lt'] if k > 0.2 else P['wd_md'] if k > -0.4 else P['wd_dk']
            if (x - 6) % 5 == 0:
                c = P['wd_dp']
            cv.set(x, y, c)
    for y in range(4, 12):                                           # couvercle
        for x in range(6, 26):
            if ((x - 15.5) / 9.5) ** 2 + ((y - 8.5) / 4.2) ** 2 <= 1:
                cv.set(x, y, P['wd_lt'] if (x + y) % 5 else P['wd_md'])
    for yb in (12, 23):                                              # cerclages
        for x in range(6, 26):
            cv.set(x, yb, P['mt_lt'])
            cv.set(x, yb + 1, P['mt_dk'])
    cv.outline(O)
    return cv.p


@reg('caisse')
def caisse(n, d):
    cv = Cv()
    for y in range(8, 29):
        for x in range(5, 27):
            if y < 14:
                c = P['wd_hi'] if (x // 4) % 2 else P['wd_lt']
                if y == 13:
                    c = P['wd_dk']
            else:
                c = P['wd_md'] if (y - 14) % 7 < 6 else P['wd_dp']
                if x in (5, 6, 25, 26):
                    c = P['wd_dk'] if x > 20 else P['wd_lt']
            cv.set(x, y, c)
    for k in range(13):                                              # croix de renfort
        cv.set(7 + k, 16 + k, P['wd_dk'])
        cv.set(8 + k, 16 + k, P['wd_lt'])
        cv.set(24 - k, 16 + k, P['wd_dk'])
    cv.outline(O)
    return cv.p


@reg('toile_araignee')
def toile(n, d):
    cv = Cv()
    c1, c2 = (216, 212, 220, 255), (170, 166, 178, 255)
    for ang in (0, 22, 45, 68, 90):
        a = math.radians(ang)
        line(cv, [(0, 0), (round(math.cos(a) * 17), round(math.sin(a) * 17))], c1)
    for r in (5, 9, 13):
        pts = [(round(math.cos(math.radians(a)) * r), round(math.sin(math.radians(a)) * r)) for a in range(0, 91, 15)]
        line(cv, pts, c2)
    return cv.p


@reg('sol_filon')
def sol_filon(n, d):
    t = floor_tex('b')
    cv = Cv()
    cv.p = t
    pts = [(2, 24), (8, 18), (13, 19), (19, 12), (24, 9), (30, 3)]
    line(cv, pts, P['ge_dk'])
    line(cv, [(x, y - 1) for x, y in pts], P['ge_md'])
    for (x, y) in ((8, 17), (19, 11), (13, 18), (25, 8)):
        cv.set(x, y, P['ge_hi'])
    return cv.p


@reg('sol_reflet_cristal')
def sol_reflet(n, d):
    t = floor_tex('a')
    for y in range(T):
        for x in range(T):
            dd = math.hypot((x - 16) / 14, (y - 16) / 12)
            if dd < 1 and (x + y) % 2 == 0 and dd > 0.35:
                t[y][x] = P['cy_dk'] if dd > 0.7 else P['cy_md']
            elif dd <= 0.35 and (x + y) % 3 == 0:
                t[y][x] = P['cy_lt']
    for (x, y) in ((12, 12), (20, 18), (15, 20)):
        t[y][x] = P['cy_w']
    return t


@reg('ossements')
def ossements(n, d):
    cv = Cv()
    bone, bd = (222, 214, 190, 255), (170, 158, 134, 255)
    for y in range(32):
        for x in range(32):
            if ((x + 0.5 - 11) / 5) ** 2 + ((y + 0.5 - 20) / 4.5) ** 2 <= 1:
                cv.p[y][x] = bone if x + y < 31 else bd
    cv.set(9, 20, P['hl_1'])
    cv.set(10, 20, P['hl_1'])
    cv.set(13, 20, P['hl_1'])
    cv.set(14, 20, P['hl_1'])
    cv.set(11, 22, P['hl_1'])
    line(cv, [(17, 25), (28, 21)], bone)
    line(cv, [(18, 26), (27, 23)], bd)
    line(cv, [(14, 27), (24, 28)], bone)
    for (x, y) in ((29, 20), (28, 20), (29, 22), (13, 26), (13, 28), (25, 27), (25, 29)):
        cv.set(x, y, bone)
    cv.outline(O)
    return cv.p


@reg('casque_mineur')
def casque(n, d):
    cv = Cv()
    for y in range(32):
        for x in range(32):
            if ((x + 0.5 - 16) / 9) ** 2 + ((y + 0.5 - 20) / 7) ** 2 <= 1 and y < 24:
                k = -((x - 16) / 9) - ((y - 20) / 7) * 0.8
                cv.p[y][x] = P['lamp_o'] if k > 0.5 else P['ge_md'] if k > -0.1 else P['ge_dk']
    for x in range(6, 27):
        cv.set(x, 24, P['ge_dk'])
        cv.set(x, 25, P['wd_dp'])
    for x in range(14, 19):
        for y in range(15, 19):
            cv.set(x, y, P['mt_md'])
    cv.set(15, 16, P['lamp_y'])
    cv.set(16, 16, P['lamp_y'])
    cv.outline(O)
    return cv.p


# ------------------------------------------------------------------ cristaux
def crystal(cv, cx, base, h, w, pal, tilt=0):
    """Prisme de cristal : pointe en haut, 3 facettes (clair à gauche), reflet."""
    x0, x1 = cx - w / 2, cx + w / 2
    top = base - h
    pts = [(cx + tilt, top), (x1, top + h * 0.28), (x1, base), (x0, base), (x0, top + h * 0.28)]

    def fn(x, y):
        u = (x + 0.5 - x0) / w
        if u < 0.34:
            return pal['hi'] if (y - top) < h * 0.45 else pal['lt']
        if u < 0.66:
            return pal['lt'] if (y - top) < h * 0.5 else pal['md']
        return pal['md'] if (y - top) < h * 0.5 else pal['dk']
    polyfill(cv, pts, fn)
    cv.set(round(x0 + 1), round(top + h * 0.35), pal['w'])
    cv.set(round(x0 + 1), round(top + h * 0.35) + 1, pal['w'])
    cv.set(round(cx + tilt) - 1, round(top) + 2, pal['w'])


def glow(cv, cx, cy, rx, ry, c1, c2):
    for y in range(cv.h):
        for x in range(cv.w):
            dd = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if dd < 1 and cv.p[y][x] is None and (x + y) % 2 == 0:
                cv.p[y][x] = c2 if dd > 0.6 else c1


def cluster(pal, shapes, gl=(16, 27, 12, 5)):
    cv = Cv()
    for (cx, base, h, w, tilt) in shapes:
        crystal(cv, cx, base, h, w, pal, tilt)
    cv.outline(O)
    glow(cv, *gl, pal['md'], pal['dk'])
    return cv.p


REG['cristal_a'] = lambda n, d: cluster(CYP, [(11, 27, 13, 6, -1), (19, 27, 17, 8, 1), (25, 28, 9, 5, 0)])
REG['cristal_b'] = lambda n, d: cluster(CYP, [(8, 27, 10, 5, -1), (14, 28, 15, 7, 0), (21, 27, 19, 8, 1), (27, 28, 11, 5, 1), (17, 28, 8, 5, 0)])
REG['cristal_rouge'] = lambda n, d: cluster(RDP, [(12, 27, 12, 6, -1), (19, 28, 16, 8, 1), (25, 27, 8, 5, 0)])


def big_crystal():
    cv = Cv(32, 64)
    rocks(cv, [(16, 59, 13, 4), (7, 57, 6, 5), (25, 57, 6, 5)], FLP, 4)
    crystal(cv, 16, 56, 48, 16, CYP, 0)
    crystal(cv, 7, 57, 18, 7, CYP, -1)
    crystal(cv, 26, 57, 22, 8, CYP, 1)
    cv.outline(O)
    return cv


@reg('cristal_gros_base', 'cristal_gros_haut')
def gros(n, d):
    if '_gros' not in REG:
        REG['_gros'] = big_crystal()
    a, b = split(REG['_gros'], 2, True)
    return a if n.endswith('haut') else b


@reg('cristal_mur')
def cristal_mur(n, d):
    cv = Cv()
    for y in range(32):
        for x in range(32):
            if ((x + 0.5 - 16) / 11) ** 2 + ((y + 0.5 - 22) / 6) ** 2 <= 1 and (x + y) % 2 == 0:
                cv.p[y][x] = P['hl_1']
    for (cx, base, h, w, tilt) in ((10, 25, 12, 6, -2), (17, 27, 19, 9, 0), (24, 25, 12, 6, 2)):
        crystal(cv, cx, base, h, w, CYP, tilt)
    cv.outline(O)
    glow(cv, 16, 18, 15, 12, P['cy_md'], P['cy_dk'])
    return cv.p


@reg('lueur_cristal')
def lueur(n, d):
    cv = Cv()
    for y in range(32):
        for x in range(32):
            dd = math.hypot((x + 0.5 - 16) / 15, (y + 0.5 - 16) / 13)
            if dd < 1 and (x + y) % 2 == 0 and dd > 0.3:
                cv.p[y][x] = P['cy_dk'] if dd > 0.72 else P['cy_md']
            elif dd <= 0.3 and (x + y) % 4 == 0:
                cv.p[y][x] = P['cy_lt']
    for (x, y) in ((13, 13), (19, 17), (16, 19), (11, 18)):
        cv.set(x, y, P['cy_w'])
    return cv.p


@reg('veine_mur')
def veine(n, d):
    cv = Cv()
    pts = [(2, 8), (8, 13), (11, 11), (17, 19), (22, 17), (29, 25)]
    line(cv, pts, P['ge_dk'])
    line(cv, [(x, y - 1) for x, y in pts], P['ge_md'])
    for (x, y) in ((8, 12), (17, 18), (22, 16), (28, 24), (5, 10)):
        cv.set(x, y, P['ge_hi'])
    line(cv, [(11, 11), (13, 6), (16, 4)], P['ge_dk'])
    cv.set(14, 5, P['ge_hi'])
    return cv.p


# ------------------------------------------------------------------ arène de Gorm
def arena_tex(kind):
    t = [[None] * T for _ in range(T)]
    hi, lt, md, dk = ARP
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 91) * 0.6 + vnoise(x, y, 16, 92) * 0.4
            t[y][x] = lt if n > 0.63 else dk if n < 0.35 else md
            if rnd(x, y, 93) < 0.04:
                t[y][x] = dk
    for y in range(T):
        for x in range(T):
            if y % 16 == 15 or x % 16 == 15:
                t[y][x] = P['ar_dp']
            elif y % 16 == 0 or x % 16 == 0:
                t[y][x] = hi if rnd(x, y, 94) < 0.6 else lt
    if kind == 'b':
        for k in range(4, 12):                                       # gravure en losange
            for x, y in ((8 + k - 4, 8 - (k - 4)), (8 - (k - 4), 8 + (k - 4))):
                pass
        for i in range(-4, 5):
            for (px, py) in ((8 + i, 8 + abs(i) - 4), (24 + i, 24 + abs(i) - 4)):
                if 0 <= px < T and 0 <= py < T:
                    t[py][px] = P['ar_dp']
    if kind == 'fissure':
        pts = [(2, 3), (9, 9), (12, 8), (18, 15), (23, 19), (30, 27)]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            n = max(abs(xb - xa), abs(yb - ya))
            for i in range(n + 1):
                x, y = round(xa + (xb - xa) * i / n), round(ya + (yb - ya) * i / n)
                t[y][x] = O
                if y > 0:
                    t[y - 1][x] = hi if (x + y) % 2 == 0 else t[y - 1][x]
        for (x, y) in ((12, 9), (13, 9), (18, 16), (19, 16)):
            t[y][x] = O
    if kind == 'centre':
        for y in range(T):
            for x in range(T):
                r = math.hypot(x + 0.5 - 16, y + 0.5 - 16)
                if 12.2 <= r < 14.2 or 7.0 <= r < 8.0:
                    t[y][x] = P['ar_dp']
                elif 14.2 <= r < 15.0 or 8.0 <= r < 8.8:
                    t[y][x] = P['ar_hi']
        for a in (90, 210, 330):                                     # les trois sceaux
            cx, cy = 16 + math.cos(math.radians(a)) * 4.2, 16 + math.sin(math.radians(a)) * 4.2
            for y in range(T):
                for x in range(T):
                    if math.hypot(x + 0.5 - cx, y + 0.5 - cy) < 1.6:
                        t[y][x] = P['rd_lt'] if a == 90 else P['ar_dp']
        t[16][16] = P['rd_hi']
    return t


REG['arene_a'] = lambda n, d: arena_tex('a')
REG['arene_b'] = lambda n, d: arena_tex('b')
REG['arene_centre'] = lambda n, d: arena_tex('centre')
REG['arene_fissure'] = lambda n, d: arena_tex('fissure')


@reg('arene_gravats')
def arene_gravats(n, d):
    cv = Cv()
    rocks(cv, [(8, 22, 4, 2.5), (20, 25, 5, 3), (24, 15, 3, 2.5), (13, 13, 2.5, 2)], ARP, 6)
    return cv.p


@reg('arene_cratere')
def cratere(n, d):
    cv = Cv()
    for y in range(32):
        for x in range(32):
            dd = ((x + 0.5 - 16) / 12) ** 2 + ((y + 0.5 - 17) / 8) ** 2
            if dd <= 1:
                if dd < 0.5:
                    cv.p[y][x] = P['hl_1'] if (x + y) % 3 else P['ar_dp']
                elif (x + y) % 2 == 0:
                    cv.p[y][x] = P['ar_dp']
                elif dd > 0.8:
                    cv.p[y][x] = P['ar_hi'] if (x < 16 and y > 17) is False and y > 17 else P['ar_dk']
    for pts in (((4, 17), (0, 15)), ((27, 17), (31, 19)), ((16, 25), (18, 29)), ((10, 10), (7, 6))):
        line(cv, list(pts), P['ar_dp'])
    return cv.p


def column(name_hi):
    cv = Cv(32, 64)
    for y in range(14, 57):                                          # fût
        for x in range(9, 24):
            k = (x - 9) / 14
            c = P['ar_hi'] if k < 0.15 else P['ar_lt'] if k < 0.4 else P['ar_md'] if k < 0.75 else P['ar_dk']
            if y % 9 == 0:
                c = P['ar_dp']
            if rnd(x, y, 95) < 0.05:
                c = P['ar_dk'] if k < 0.5 else P['ar_dp']
            cv.p[y][x] = c
    for y in range(6, 15):                                           # chapiteau
        for x in range(6, 27):
            if y < 9 and (x < 7 or x > 25):
                continue
            k = (x - 6) / 20
            cv.p[y][x] = P['ar_hi'] if (y == 6 or k < 0.1) else P['ar_lt'] if k < 0.45 else P['ar_md'] if k < 0.8 else P['ar_dk']
            if y >= 13:
                cv.p[y][x] = P['ar_dk'] if k > 0.45 else P['ar_md']
    for y in range(55, 64):                                          # socle
        for x in range(6, 27):
            k = (x - 6) / 20
            cv.p[y][x] = P['ar_hi'] if y == 55 else P['ar_lt'] if k < 0.35 else P['ar_md'] if k < 0.8 else P['ar_dk']
    for y in range(24, 40):                                          # gravure rouge (rune)
        cv.p[y][16] = P['ar_dp']
    cv.set(16, 31, P['rd_lt'])
    cv.set(16, 32, P['rd_lt'])
    cv.outline(O)
    return cv


@reg('pilier_haut', 'pilier_base')
def pilier(n, d):
    if '_pilier' not in REG:
        REG['_pilier'] = column(None)
    a, b = split(REG['_pilier'], 2, True)
    return a if n.endswith('haut') else b


# ------------------------------------------------------------------ murs fissurés
def crack(t, pts, light=True):
    cv = Cv()
    cv.p = t
    line(cv, pts, O)
    if light:
        for (x, y) in pts[1:-1]:
            cv.set(x + 1, y, P['wf_hi'])
    return t


def lighten_patch(t, cx, cy, rx, ry):
    for y in range(T):
        for x in range(T):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and t[y][x] not in (O, P['wf_hi']) and (x + y) % 3 == 0:
                t[y][x] = P['wf_lt'] if t[y][x] in (P['wf_md'], P['wf_dk']) else P['cp_lt']


CRACKS = {
    'haut': [[(17, 4), (15, 9), (18, 14), (15, 19), (17, 24), (14, 30)], [(15, 19), (10, 21), (7, 26)], [(17, 24), (22, 25), (25, 30)]],
    'bas': [[(16, 2), (13, 8), (17, 13), (14, 20), (16, 27)], [(17, 13), (23, 15), (27, 21)], [(14, 20), (8, 22), (4, 27)]],
    'gauche': [[(3, 16), (9, 13), (13, 18), (19, 14), (24, 19), (29, 15)], [(13, 18), (11, 24), (7, 28)], [(19, 14), (21, 8), (25, 4)]],
    'droite': [[(2, 15), (7, 19), (12, 14), (18, 18), (23, 13), (28, 17)], [(12, 14), (10, 8), (6, 4)], [(18, 18), (20, 24), (24, 28)]],
}
WSIDE = {'haut': (1, 1, 0, 0), 'bas': (0, 0, 1, 1), 'gauche': (1, 0, 1, 0), 'droite': (0, 1, 0, 1)}


def cracked(side):
    t = wall(WSIDE[side])
    lighten_patch(t, 16, 18 if side == 'haut' else 16, 13, 12)
    for pts in CRACKS[side]:
        crack(t, pts)
    return t


def opened(side):
    t = wall(WSIDE[side])
    cv = Cv()
    cv.p = t
    if side == 'haut':
        pts = [(6, 31), (7, 21), (10, 15), (14, 12), (19, 13), (24, 16), (26, 22), (26, 31)]
    elif side == 'bas':
        pts = [(5, 24), (6, 12), (11, 5), (19, 4), (25, 8), (27, 16), (26, 25)]
    elif side == 'gauche':
        pts = [(4, 5), (14, 4), (24, 6), (28, 12), (27, 22), (17, 27), (5, 26)]
    else:
        pts = [(27, 5), (17, 4), (7, 6), (3, 12), (4, 22), (14, 27), (26, 26)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cy0, cy1 = min(ys), max(ys)
    polyfill(cv, pts, lambda x, y: P['hl_1'] if (y - cy0) / max(1, cy1 - cy0) > 0.35 or rnd(x, y, 3) < 0.4 else P['hl_0'] if rnd(x, y, 4) < 0.5 else P['hl_2'])
    # bords éclatés (éclats clairs à gauche et en haut, ombre à droite)
    for i in range(len(pts)):
        xa, ya = pts[i]
        xb, yb = pts[(i + 1) % len(pts)]
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for k in range(n + 1):
            x, y = round(xa + (xb - xa) * k / n), round(ya + (yb - ya) * k / n)
            if 0 <= x < T and 0 <= y < T:
                cv.set(x, y, O)
                lit = (xb < xa or yb < ya) or (xb == xa and yb < ya)
                if lit and cv.get(x - 1, y) not in (None, O) and rnd(x, y, 6) < 0.8:
                    cv.set(x - 1, y, P['wf_hi'])
                elif lit and cv.get(x, y - 1) not in (None, O):
                    cv.set(x, y - 1, P['wf_hi'])
    # gravats au pied de l'ouverture
    gx = (16, 24) if side == 'haut' else (16, 23) if side == 'bas' else (14, 22)
    rocks(cv, [(gx[0] - 6, 28 if side != 'bas' else 21, 4, 3), (gx[0] + 4, 29 if side != 'bas' else 22, 5, 3), (gx[0] - 1, 30 if side != 'bas' else 23, 3, 2.5)],
          WALLP, 13)
    return cv.p


for _s in WSIDE:
    REG[f'mur_fissure_{_s}'] = (lambda s: (lambda n, d: cracked(s)))(_s)
    REG[f'mur_fissure_{_s}_ouvert'] = (lambda s: (lambda n, d: opened(s)))(_s)


@reg('mur_craquele')
def craquele(n, d):
    t = wall(WSIDE['haut'])
    crack(t, [(22, 19), (20, 23), (23, 27)], light=False)
    crack(t, [(7, 3), (9, 7)], light=False)
    return t


@reg('rocher_fissure')
def rocher_fissure(n, d):
    cv = Cv()
    rocks(cv, [(16, 24, 13, 6), (16, 17, 13, 11)], WALLP, 21)
    mass(cv, [(14, 14, 7, 6)], (P['wf_hi'], P['wf_hi'], P['wf_lt'], P['wf_md']), 3, 0.3) if False else None
    for pts in (((17, 6), (15, 11), (18, 16), (15, 21), (17, 27)), ((15, 11), (10, 13), (7, 18)), ((18, 16), (23, 17), (26, 22))):
        line(cv, list(pts), O)
        for (x, y) in pts[1:-1]:
            cv.set(x + 1, y, P['wf_hi'])
    for (x, y) in ((11, 8), (12, 8), (22, 12)):
        cv.set(x, y, P['wf_hi'])
    return cv.p


@reg('rocher_fissure_ouvert')
def rocher_ouvert(n, d):
    cv = Cv()
    for y in range(32):
        for x in range(32):
            dd = ((x + 0.5 - 16) / 10) ** 2 + ((y + 0.5 - 20) / 7) ** 2
            if dd <= 1:
                cv.p[y][x] = P['hl_1'] if dd < 0.6 or (x + y) % 3 else P['hl_0']
    cv.outline(O)
    rocks(cv, [(5, 25, 4.5, 4), (27, 24, 4.5, 4.5), (11, 29, 5, 3), (22, 29, 5, 3), (16, 14, 4, 3.5)], WALLP, 31)
    return cv.p


# ------------------------------------------------------------------ éboulis
def heap(cv, ox=0, specs=None, pal=WALLP, seed=0):
    rocks(cv, [(cx + ox, cy, rx, ry) for (cx, cy, rx, ry) in specs], pal, seed)


HEAP_A = [(16, 27, 14, 5), (8, 22, 7, 7), (24, 22, 7, 7), (16, 19, 9, 8), (11, 12, 5.5, 5.5), (21, 13, 6, 5.5), (16, 8, 4.5, 4)]
HEAP_B = [(16, 27, 14, 5), (11, 21, 9, 7), (22, 22, 8, 6), (14, 13, 7, 7), (23, 12, 5, 5), (18, 7, 4, 3.5)]


@reg('eboulis_a')
def eboulis_a(n, d):
    cv = Cv()
    heap(cv, 0, HEAP_A, seed=3)
    flecks(cv, [(9, 21), (22, 20), (15, 17)], [P['wf_hi']])
    return cv.p


@reg('eboulis_b')
def eboulis_b(n, d):
    cv = Cv()
    heap(cv, 0, HEAP_B, seed=8)
    flecks(cv, [(11, 20), (23, 21), (14, 12)], [P['wf_hi']])
    return cv.p


@reg('eboulis_g', 'eboulis_d')
def eboulis_large(n, d):
    if '_eb' not in REG:
        cv = Cv(64, 32)
        specs = [(32, 27, 30, 5), (10, 23, 8, 7), (22, 22, 8, 8), (33, 21, 9, 8), (45, 22, 8, 8), (55, 23, 8, 7), (16, 14, 6, 6),
                 (28, 11, 7, 7), (40, 12, 7, 7), (51, 14, 5, 5), (34, 5, 5, 4)]
        heap(cv, 0, specs, seed=5)
        flecks(cv, [(10, 21), (28, 9), (44, 20), (54, 21)], [P['wf_hi']])
        REG['_eb'] = cv
    a, b = split(REG['_eb'])
    return a if n.endswith('_g') else b


def cleared(kind):
    t = floor_tex('a' if kind == 'a' else 'c')
    cv = Cv()
    cv.p = t
    specs = [(9, 10, 3, 2.2), (22, 8, 2.5, 2), (14, 23, 4, 2.8), (25, 24, 3, 2.4), (5, 26, 2.5, 2)] if kind == 'a' else \
        [(8, 22, 3.5, 2.5), (20, 12, 3, 2.4), (26, 26, 3.5, 2.5), (12, 8, 2.5, 2), (16, 27, 2.5, 2)]
    for i, (cx, cy, rx, ry) in enumerate(specs):
        tmp = Cv()
        mass(tmp, [(cx, cy, rx, ry)], WALLP, 40 + i, 0.2)
        tmp.outline(P['fl_dp'])
        for y in range(T):
            for x in range(T):
                if tmp.p[y][x] is not None:
                    t[y][x] = tmp.p[y][x]
    for y in range(T):
        for x in range(T):
            if vnoise(x, y, 4, 77) > 0.7 and (x + y) % 2 == 0 and t[y][x] in FLP:
                t[y][x] = P['fl_hi']
    return t


REG['eboulis_degage_a'] = lambda n, d: cleared('a')
REG['eboulis_degage_b'] = lambda n, d: cleared('b')


@reg('eboulis_poussiere')
def eb_pous(n, d):
    cv = Cv()
    for y in range(32):
        for x in range(32):
            dd = math.hypot((x + 0.5 - 16) / 15, (y + 0.5 - 18) / 11)
            if dd < 1 and (x + y) % 2 == 0 and vnoise(x, y, 4, 15) > 0.35 + dd * 0.35:
                cv.p[y][x] = P['du_lt'] if rnd(x, y, 2) < 0.5 else P['fl_dk']
    rocks(cv, [(8, 24, 2.5, 1.8), (24, 12, 2, 1.6), (20, 27, 2.2, 1.6)], FLP, 3)
    return cv.p


@reg('cailloux')
def cailloux(n, d):
    cv = Cv()
    rocks(cv, [(10, 12, 3, 2.2), (22, 20, 3.5, 2.6), (13, 25, 2.2, 1.8), (26, 9, 2, 1.6)], FLP, 7)
    return cv.p
