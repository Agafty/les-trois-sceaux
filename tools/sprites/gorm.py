"""Gorm, le Golem de la Mine (boss du donjon 2) + rocher qui tombe et son ombre — Les Trois Sceaux.

Usage : python tools/sprites/gorm.py
Produit dans art/bosses/gorm/ :
  gorm.png              planche 96x96 par case, 17 colonnes x 3 lignes (une ligne par ETAT D'ARMURE)
  gorm_corruption.png   calque de corruption (veines noires), memes cases, meme cadrage : a faire clignoter par-dessus
  gorm_ombre.png        ombre portee au sol (1 case 96x96)
  rocher.png            rocher qui tombe : cases 32x32 (0 et 1 = rochers, 2 a 4 = eclats a l'impact)
  rocher_ombre.png      ombre annoncant la chute : 4 cases 32x32 qui grandissent (la derniere clignote)
  gorm.json             ordre des cases, animations, origine, plaques
  gorm_frames.tres      SpriteFrames Godot (gorm.png), animations `<nom>_<etat>`
Lignes (etats d'armure) : 0 = plein (4 plaques + ventre : cristal cache), 1 = brise (plaque gauche et epaulette gauche arrachees :
cristal a moitie visible), 2 = nu (toutes les plaques arrachees : cristal expose, il brille).
Colonnes : 0-1 idle, 2-5 marche, 6-9 frappe du sol, 10 touche, 11-12 etourdi (a genoux), 13-16 mort (ligne 2 seulement a utiliser).
Origine conseillee de chaque case : bas-centre (48, 94). Lumiere en haut a gauche, contour sombre d'1 px.
Sans Pillow : encodeur PNG de tsplan.py (zlib + struct).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import save_png, rgba  # noqa: E402
from foret import Cv as _Cv, rnd  # noqa: E402


class Cv(_Cv):
    """Canevas qui arrondit les coordonnees (les poses sont en flottants)."""

    def set(self, x, y, c):
        super().set(int(round(x)), int(round(y)), c)

    def get(self, x, y):
        return super().get(int(round(x)), int(round(y)))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'art', 'bosses', 'gorm')
S = 96
GROUND = 94
CX = 48

HEX = dict(
    O='#1b1420',
    st_hi='#c4c0cc', st_lt='#a09cac', st_md='#7c788c', st_dk='#5a566c', st_dp='#3e3a50',          # pierre gris-violet froid
    pl_hi='#e0b878', pl_lt='#c08e54', pl_md='#946a40', pl_dk='#6a4a30', pl_dp='#46301f',          # plaques d'armure : bronze ocre
    cr_w='#fff0e8', cr_hi='#ff9a84', cr_lt='#f0483c', cr_md='#c8242c', cr_dk='#8a1428', cr_dp='#5a0c24',  # cristal rouge
    ey_c='#fff0a0', ey_o='#ff9a28', ey_w='#ffffff', ey_d='#7a3a30',                               # yeux
    cor_c='#241a22', cor_m='#3a1a4a', cor_l='#6a2a7a',                                            # corruption de Morvath
    dust='#b8b0a8', dust_d='#8a8478',
)
P = {k: rgba(v) for k, v in HEX.items()}
O = P['O']
STONE = (P['st_hi'], P['st_lt'], P['st_md'], P['st_dk'])
PLATE = (P['pl_hi'], P['pl_lt'], P['pl_md'], P['pl_dk'])


# ------------------------------------------------------------------ outils
def mass(cv, circles, pal, seed=0, noise=0.28):
    """Union d'ellipses (cx, cy, rx, ry), ombrage lumiere haut-gauche propre a chaque ellipse (aspect bloc de roche)."""
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
            v = -(nx + ny) * 0.55 + (rnd(x, y, seed) - 0.5) * noise - d * 0.15 + 0.1
            cv.p[y][x] = hi if v > 0.5 else lt if v > 0.1 else md if v > -0.34 else dk


def part(circles, pal=STONE, seed=0, clip_y=None):
    """Une piece du golem : forme ombree + contour sombre, sur son propre calque."""
    t = Cv(S, S)
    mass(t, circles, pal, seed)
    if clip_y is not None:
        for y in range(clip_y + 1, S):
            for x in range(S):
                t.p[y][x] = None
    t.outline(O)
    return t


def paste(dst, src):
    for y in range(S):
        for x in range(S):
            if src.p[y][x] is not None:
                dst.p[y][x] = src.p[y][x]


def poly_fill(cv, pts, pal, seed=0, outline=True):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    hi, lt, md, dk = pal
    t = Cv(S, S)

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
    for y in range(int(y0) - 1, int(y1) + 2):
        for x in range(int(x0) - 1, int(x1) + 2):
            if 0 <= x < S and 0 <= y < S and inside(x + 0.5, y + 0.5):
                u, v = (x - x0) / max(1, x1 - x0), (y - y0) / max(1, y1 - y0)
                k = -(u + v) * 0.5 + 0.5 + (rnd(x, y, seed) - 0.5) * 0.25
                t.p[y][x] = hi if k > 0.72 else lt if k > 0.45 else md if k > 0.18 else dk
    if outline:
        t.outline(P['pl_dp'] if pal is PLATE else O)
    return t


def line(cv, pts, c, w=1):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(int(n) + 1):
            x, y = round(xa + (xb - xa) * i / n), round(ya + (yb - ya) * i / n)
            for dx in range(w):
                for dy in range(w):
                    cv.set(x + dx, y + dy, c)


def chain(a, b, r, bend=0.0, step=3.0):
    """Cercles regulierement espaces de a vers b (bras), avec un coude decale lateralement de `bend`."""
    mx, my = (a[0] + b[0]) / 2 + bend, (a[1] + b[1]) / 2
    out = []
    for p, q in ((a, (mx, my)), ((mx, my), b)):
        n = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) / step))
        for i in range(n + 1):
            out.append((p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n, r, r))
    return out


# ------------------------------------------------------------------ cristal
def crystal(cv, cx, cy, glow=1, clip=None, wobble=0):
    """Cristal rouge facette, haut 24 px : cx, cy = centre. clip(x) -> True pour les colonnes visibles (plaques)."""
    pts = [(cx, cy - 12), (cx + 6, cy - 5), (cx + 5, cy + 6), (cx, cy + 12), (cx - 5, cy + 6), (cx - 6, cy - 5)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]

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
    if glow:                                                       # halo en damier
        r = 5 + 2 * glow
        for y in range(cy - 12 - r, cy + 13 + r):
            for x in range(cx - 7 - r, cx + 8 + r):
                if (x + y) % 2 == 0 and 0 <= x < S and 0 <= y < S and not inside(x + 0.5, y + 0.5):
                    d = math.hypot((x - cx) / 1.0, (y - cy) / 1.5)
                    if d < 7 + r * 0.9 and cv.p[y][x] is not None:
                        cv.p[y][x] = P['cr_dk'] if d > 6 + r * 0.55 else P['cr_md']
    for y in range(cy - 13, cy + 14):
        for x in range(cx - 7, cx + 8):
            if 0 <= x < S and 0 <= y < S and inside(x + 0.5, y + 0.5) and (clip is None or clip(x)):
                dx = x - cx
                if dx < -2:
                    c = P['cr_hi'] if y < cy - 2 else P['cr_lt']
                elif dx > 2:
                    c = P['cr_dk'] if y > cy else P['cr_md']
                else:
                    c = P['cr_lt'] if y < cy + 4 else P['cr_md']
                cv.p[y][x] = c
    if clip is None or clip(cx - 3):
        for (dx, dy, k) in ((-3, -6, 'cr_w'), (-4, -5, 'cr_w'), (-3, -4, 'cr_hi'), (-2, 8, 'cr_lt')):
            cv.set(cx + dx, cy + dy, P[k])
    # facettes : aretes sombres
    for (xa, ya, xb, yb) in ((cx, cy - 12, cx, cy + 12), (cx - 6, cy - 5, cx, cy + 2), (cx + 6, cy - 5, cx, cy + 2)):
        n = max(abs(xb - xa), abs(yb - ya))
        for i in range(n + 1):
            x, y = round(xa + (xb - xa) * i / n), round(ya + (yb - ya) * i / n)
            if inside(x + 0.5, y + 0.5) and 0 <= x < S and (clip is None or clip(x)) and cv.p[y][x] is not None and (i + y) % 3 != 0:
                cv.p[y][x] = P['cr_md'] if x <= cx else P['cr_dk']
    # contour du cristal
    ring = []
    for y in range(cy - 14, cy + 15):
        for x in range(cx - 9, cx + 10):
            if 0 <= x < S and 0 <= y < S and not inside(x + 0.5, y + 0.5) and (clip is None or clip(x)):
                if any(inside(x + dx + 0.5, y + dy + 0.5) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    ring.append((x, y))
    for x, y in ring:
        cv.p[y][x] = P['cr_dp']


# ------------------------------------------------------------------ pose -> image
BASE = dict(by=0, lx=0, hx=0, hy=0, lf=(17, 72), rf=(79, 72), ll=0, rl=0, squat=0, eyes='o', glow=1, crack=0, dust=0, kneel=0)


def pose(**k):
    d = dict(BASE)
    d.update(k)
    return d


def render(pz, state, with_corruption=False):
    """Renvoie (corps Cv, corruption Cv) pour une pose et un etat d'armure (0 plein, 1 brise, 2 nu)."""
    by, lx = pz['by'], pz['lx']
    cv = Cv(S, S)
    body_mask_layers = []

    # --- jambes (derriere le torse)
    sq = pz['squat']
    for cxl, lift in ((38, pz['ll']), (58, pz['rl'])):
        top = 66 + by
        bot = GROUND - lift
        mid = (top + bot) / 2
        paste(cv, part([(cxl + lx * 0.3, mid + 1, 9.5, (bot - top) / 2 + 1), (cxl + lx * 0.3, bot - 4, 11.5, 5.5)], STONE, seed=cxl, clip_y=bot))

    # --- torse
    tcx = CX + lx
    torso = part([(tcx, 46 + by, 24, 20), (tcx, 66 + by - sq, 19, 12), (tcx, 36 + by, 26, 12)], STONE, seed=3)
    paste(cv, torso)
    # strates et eclats sur la pierre
    for (dx, dy, n) in ((-12, 12, 6), (8, 18, 7), (-6, 28, 5), (12, 6, 4), (-16, 22, 4)):
        line(cv, [(tcx + dx, 38 + by + dy), (tcx + dx + n, 38 + by + dy + 1)], P['st_dk'])
        cv.set(tcx + dx, 37 + by + dy, P['st_hi'])
    # --- cavite de la poitrine + cristal
    ccx, ccy = tcx, 48 + by
    sock = Cv(S, S)
    for y in range(S):
        for x in range(S):
            if ((x + 0.5 - ccx) / 11) ** 2 + ((y + 0.5 - ccy) / 15) ** 2 <= 1:
                sock.p[y][x] = P['st_dp']
    sock.outline(O)
    paste(cv, sock)
    for y in range(S):                                              # rebord eclaire en haut a gauche
        for x in range(S):
            if sock.p[y][x] == O and x < ccx - 4 and y < ccy and cv.p[y][x] is not None:
                cv.p[y][x] = P['st_hi']

    def left_clip(x):
        return True

    hidden_left = state == 0
    hidden_right = state in (0, 1)
    crystal(cv, ccx, ccy, glow=pz['glow'] + (1 if state == 2 else 0),
            clip=(lambda x: not (hidden_left and x < ccx - 1) and not (hidden_right and x > ccx + 1)))

    # --- plaques de poitrine
    if state == 0:
        pl = poly_fill(cv, [(ccx - 18, ccy - 15), (ccx - 1, ccy - 17), (ccx - 1, ccy + 16), (ccx - 13, ccy + 14), (ccx - 19, ccy)], PLATE, 11)
        paste(cv, pl)
    if state <= 1:
        pr = poly_fill(cv, [(ccx + 18, ccy - 15), (ccx + 1, ccy - 17), (ccx + 1, ccy + 16), (ccx + 13, ccy + 14), (ccx + 19, ccy)], PLATE, 12)
        paste(cv, pr)
    # rivets
    for (dx, dy, st) in ((-13, -11, 0), (-13, 9, 0), (13, -11, 1), (13, 9, 1)):
        if state <= st:
            cv.set(ccx + dx, ccy + dy, P['pl_hi'])
            cv.set(ccx + dx + 1, ccy + dy + 1, P['pl_dp'])
    if state == 0:                                                  # fente rouge entre les plaques
        for y in range(ccy - 9, ccy + 10):
            if (y + ccy) % 2 == 0 or abs(y - ccy) < 4:
                cv.set(ccx, y, P['cr_lt'] if abs(y - ccy) < 4 else P['cr_md'])
    if state == 1:                                                  # plaque gauche arrachee : moignons et fissures
        for (dx, dy, w, h) in ((-19, -14, 3, 5), (-20, -3, 2, 6), (-17, 8, 3, 6)):
            r = poly_fill(cv, [(ccx + dx, ccy + dy), (ccx + dx + w, ccy + dy - 1), (ccx + dx + w + 1, ccy + dy + h), (ccx + dx, ccy + dy + h - 1)], PLATE, 3)
            paste(cv, r)
        line(cv, [(ccx + 6, ccy - 12), (ccx + 9, ccy - 5), (ccx + 7, ccy + 1)], P['pl_dp'])
    if state == 2:                                                  # moignons des deux cotes
        for sx in (-1, 1):
            for (dy, h) in ((-14, 5), (-4, 6), (8, 6)):
                x0 = ccx + sx * 19
                r = poly_fill(cv, [(x0, ccy + dy), (x0 + sx * 3, ccy + dy - 1), (x0 + sx * 4, ccy + dy + h), (x0, ccy + dy + h - 1)], PLATE, 5)
                paste(cv, r)
    # --- plaque du ventre
    if state == 0:
        paste(cv, poly_fill(cv, [(tcx - 12, 62 + by), (tcx + 12, 62 + by), (tcx + 9, 71 + by - sq), (tcx - 9, 71 + by - sq)], PLATE, 21))

    # --- bras (epaules, bras, poings)
    arms = {}
    for side, sx_, f in ((-1, 25, pz['lf']), (1, 71, pz['rf'])):
        sh = (sx_ + lx, 38 + by)
        fist = (f[0] + lx * (0.5 if f[1] > 60 else 1), f[1] + (by if f[1] > 60 else 0))
        bend = side * 3.5
        arm = part(chain(sh, fist, 6.5, bend) + [(sh[0], sh[1], 12, 11), (fist[0], fist[1], 10, 9.5), (fist[0] - side * 3, fist[1] + 5, 6, 5)], STONE, seed=7 + side)
        paste(cv, arm)
        # jointures des phalanges
        for k in (-4, 0, 4):
            cv.set(round(fist[0] + k), round(fist[1] + 6), P['st_dp'])
        arms[side] = (sh, fist)
        # epaulette
        gone = (state >= 1 and side == -1) or state == 2
        if not gone:
            paste(cv, poly_fill(cv, [(sh[0] - 12 + (3 if side > 0 else 0), sh[1] - 2), (sh[0] - 6, sh[1] - 12), (sh[0] + 6, sh[1] - 12),
                                     (sh[0] + 12 - (3 if side < 0 else 0), sh[1] - 2), (sh[0] + 9, sh[1] + 4), (sh[0] - 9, sh[1] + 4)], PLATE, 31 + side))
            cv.set(sh[0] - 3, sh[1] - 8, P['pl_hi'])
            cv.set(sh[0] + 4, sh[1] - 6, P['pl_dp'])
        else:
            paste(cv, poly_fill(cv, [(sh[0] - 6, sh[1] - 11), (sh[0] - 1, sh[1] - 13), (sh[0] + 2, sh[1] - 9), (sh[0] - 4, sh[1] - 8)], PLATE, 4))

    # --- tete
    hcx, hcy = CX + lx + pz['hx'], 22 + by + pz['hy']
    head = part([(hcx, hcy, 12, 10.5), (hcx, hcy + 7, 8.5, 5.5), (hcx - 8, hcy - 3, 5, 5.5), (hcx + 8, hcy - 3, 5, 5.5)], STONE, seed=9)
    paste(cv, head)
    # arcade sourciliere et mâchoire
    line(cv, [(hcx - 9, hcy - 3), (hcx - 3, hcy - 1)], P['st_dp'], 1)
    line(cv, [(hcx + 9, hcy - 3), (hcx + 3, hcy - 1)], P['st_dp'], 1)
    for k in range(-5, 6):
        if k % 2 == 0:
            cv.set(hcx + k, hcy + 9, P['st_dp'])                    # dents
    cv.set(hcx - 2, hcy - 9, P['st_hi'])
    cv.set(hcx - 5, hcy - 7, P['st_hi'])
    eyes = pz['eyes']
    core = {'o': P['ey_c'], 'w': P['ey_w'], 'd': P['ey_d']}[eyes]
    rim = {'o': P['ey_o'], 'w': P['ey_w'], 'd': P['st_dp']}[eyes]
    for ex in (-5, 4):
        for dx in range(3):
            cv.set(hcx + ex + dx, hcy + 1, rim)
            cv.set(hcx + ex + dx, hcy + 2, rim)
        cv.set(hcx + ex + 1, hcy + 1, core)

    # --- fissures de degats
    if pz['crack']:
        for pts in (([tcx - 14, 40 + by], [tcx - 10, 48 + by], [tcx - 14, 56 + by]), ([tcx + 12, 36 + by], [tcx + 9, 46 + by], [tcx + 14, 58 + by]),
                    ([hcx - 3, hcy - 9], [hcx - 1, hcy - 4])):
            line(cv, pts[:pz['crack'] + 1], P['O'])
    # --- poussiere de l'impact : deux nuages de part et d'autre des poings
    if pz['dust']:
        d = pz['dust']
        for side in (-1, 1):
            for i in range(26 * d):
                x = round(CX + side * (20 + 22 * rnd(i, 1, 5 + side)) + (rnd(i, 4, 5) - 0.5) * 6)
                y = round(91 - rnd(i, 3, 5) * (5 + 3 * d))
                if cv.get(x, y) is None and (x + y) % 2 == 0:
                    cv.set(x, y, P['dust'] if rnd(i, 7, 5) > 0.35 else P['dust_d'])

    # --- calque de corruption
    cor = Cv(S, S)
    if with_corruption:
        veins = []
        for sx in (-1, 1):
            veins.append([(tcx + sx * 17, 36 + by), (tcx + sx * 13, 44 + by), (tcx + sx * 17, 52 + by), (tcx + sx * 12, 62 + by)])
            veins.append([(tcx + sx * 7, 66 + by), (tcx + sx * 10, 73 + by)])
        for side, (sh, fist) in arms.items():
            veins.append([(sh[0] - side * 2, sh[1] - 6), (sh[0] + side * 3, sh[1] + 2), (sh[0], sh[1] + 9)])
            veins.append([(fist[0] - 4, fist[1] - 4), (fist[0], fist[1] + 1), (fist[0] + 4, fist[1] + 3)])
        veins.append([(hcx - 8, hcy - 5), (hcx - 5, hcy), (hcx - 8, hcy + 5)])
        veins.append([(hcx + 8, hcy - 6), (hcx + 5, hcy - 1)])
        for pts in veins:
            line(cor, pts, P['cor_m'], 2)
            line(cor, pts, P['cor_c'], 1)
            for (x, y) in pts[1:-1]:                                # epines
                cor.set(x + 2, y - 1, P['cor_l'])
                cor.set(x - 2, y + 1, P['cor_l'])
        for y in range(S):                                          # limite a la pierre
            for x in range(S):
                if cor.p[y][x] is not None and (cv.p[y][x] is None or cv.p[y][x] == O):
                    cor.p[y][x] = None
    return cv, cor


# ------------------------------------------------------------------ mort : eboulement progressif
ROCKS = [(0, -1, 10), (-14, -2, 9), (14, -1, 9), (-26, 0, 7), (26, 0, 7), (-7, -9, 8), (8, -9, 8), (-18, -8, 6), (19, -7, 6), (0, -16, 7)]


def collapse(stage):
    cv = Cv(S, S)
    cor = Cv(S, S)
    if stage == 0:                                                  # tremblement, fissures lumineuses
        pz = pose(by=2, lx=-1, hy=3, eyes='w', glow=2, crack=2, lf=(15, 74), rf=(81, 74))
        return render(pz, 2, True)
    if stage == 1:                                                  # les pieces se separent
        pz = pose(by=7, lx=0, hy=-1, hx=0, eyes='d', glow=2, crack=2, lf=(8, 80), rf=(88, 80), squat=4, ll=0, rl=0)
        c, k = render(pz, 2, True)
        for y in range(S):                                          # eclats de lumiere qui s'echappent
            for x in range(S):
                pass
        for (x, y) in ((40, 40), (56, 36), (34, 52), (62, 50), (48, 28)):
            c.set(x, y, P['cr_w'])
        return c, k
    # stade 2 et 3 : tas de roches, cristal qui s'eteint
    scale = 1.0 if stage == 2 else 0.8
    base_y = 90 if stage == 2 else 91
    circles = []
    for (dx, dy, r) in ROCKS:
        yy = base_y + dy * scale - (6 if stage == 2 and abs(dx) < 10 else 0)
        circles.append((CX + dx * (1.1 if stage == 3 else 1.0), yy, r * 1.0, r * (0.8 if stage == 3 else 0.95)))
    if stage == 2:
        circles.append((CX - 3, 66, 12, 10))                         # la tete tombe encore
    t = Cv(S, S)
    for i, ci in enumerate(circles):
        part_ = part([ci], STONE, seed=i * 5 + 1, clip_y=GROUND)
        paste(t, part_)
    paste(cv, t)
    # cristal au milieu : s'eteint
    cy = 80 if stage == 3 else 74
    crystal(cv, CX + 1, cy + 4 if stage == 3 else cy, glow=0 if stage == 3 else 1)
    if stage == 3:
        # cristal plus petit et sombre : repeint en rouge sombre
        for y in range(S):
            for x in range(S):
                c = cv.p[y][x]
                if c in (P['cr_hi'], P['cr_w']):
                    cv.p[y][x] = P['cr_lt']
                elif c == P['cr_lt']:
                    cv.p[y][x] = P['cr_md']
    for i in range(14 if stage == 2 else 8):                         # poussiere et cailloux
        x, y = round(CX + (rnd(i, 4, 8) - 0.5) * 70), round(86 + rnd(i, 5, 8) * 7)
        if cv.get(x, y) is None:
            cv.set(x, y, P['dust'] if i % 2 else P['dust_d'])
    return cv, cor


# ------------------------------------------------------------------ poses de la planche
def walk_pose(i):
    ph = i % 4
    by = (0, 2, 0, 2)[ph]
    ll = (0, 0, 5, 0)[ph]
    rl = (5, 0, 0, 0)[ph]
    return pose(by=by, lx=(-1, 0, 1, 0)[ph], ll=ll, rl=rl, lf=(17 - (2 if ph in (0,) else 0), 72 + (3 if ph == 2 else 0)),
                rf=(79 + (2 if ph == 2 else 0), 72 + (3 if ph == 0 else 0)), glow=1)


POSES = [
    pose(by=0, glow=1), pose(by=1, glow=2, lf=(17, 73), rf=(79, 73)),                        # idle 0-1
]
POSES += [walk_pose(i) for i in range(4)]                                                       # marche 2-5
POSES += [
    pose(by=3, lx=0, hy=2, lf=(19, 26), rf=(77, 26), eyes='o', glow=1),                         # frappe 6 : poings qui montent
    pose(by=-1, hy=-1, lf=(22, 13), rf=(74, 13), glow=2, squat=-1),                               # frappe 7 : en haut
    pose(by=9, hy=5, lf=(34, 82), rf=(62, 82), glow=2, dust=2, squat=3, ll=0, rl=0),            # frappe 8 : impact
    pose(by=5, hy=3, lf=(26, 79), rf=(70, 79), glow=1, dust=1, squat=1),                        # frappe 9 : retour
    pose(by=2, lx=3, hy=-2, lf=(13, 66), rf=(83, 80), eyes='w', glow=2, crack=1),               # touche 10
    pose(by=13, hy=7, lf=(14, 83), rf=(82, 83), eyes='d', glow=2, squat=7, ll=0, rl=0),         # etourdi 11
    pose(by=14, hy=8, lf=(14, 84), rf=(82, 84), eyes='d', glow=0, squat=7),                     # etourdi 12
]
N_COLS = 17
ANIMS = [('idle', 0, 2, 3.0), ('marche', 2, 4, 6.0), ('frappe', 6, 4, 5.0), ('touche', 10, 1, 1.0), ('etourdi', 11, 2, 3.0), ('mort', 13, 4, 4.0)]
STATES = ['plein', 'brise', 'nu']


def build():
    body = Cv(S * N_COLS, S * 3)
    corr = Cv(S * N_COLS, S * 3)
    for row in range(3):
        for col in range(N_COLS):
            if col < 13:
                c, k = render(POSES[col], row, True)
            else:
                if row != 2:
                    continue
                c, k = collapse(col - 13)
            for y in range(S):
                for x in range(S):
                    if c.p[y][x] is not None:
                        body.p[row * S + y][col * S + x] = c.p[y][x]
                    if k.p[y][x] is not None:
                        corr.p[row * S + y][col * S + x] = k.p[y][x]
    return body, corr


def shadow_img():
    cv = Cv(S, S)
    for y in range(S):
        for x in range(S):
            if ((x + 0.5 - CX) / 36) ** 2 + ((y + 0.5 - 89) / 8) ** 2 <= 1:
                cv.p[y][x] = (27, 20, 32, 255) if (x + y) % 2 == 0 or ((x + 0.5 - CX) / 36) ** 2 + ((y + 0.5 - 89) / 8) ** 2 < 0.55 else None
    return cv


# ------------------------------------------------------------------ rocher qui tombe
def rock_img(v):
    cv = Cv(32, 32)
    if v == 0:
        circ = [(16, 18, 11, 10), (10, 16, 6, 6), (21, 14, 6, 6), (16, 24, 9, 5)]
    else:
        circ = [(16, 19, 10, 9), (11, 13, 6, 6), (22, 21, 6, 6), (15, 25, 9, 4.5)]
    mass(cv, circ, STONE, seed=40 + v, noise=0.34)
    cv.outline(O)
    for (x0, y0, x1, y1) in ((11, 14, 15, 17), (19, 21, 23, 22), (14, 10, 17, 9)):
        line(cv, [(x0, y0), (x1, y1)], P['st_dk'])
    cv.set(9, 11, P['st_hi'])
    cv.set(10, 11, P['st_hi'])
    cv.set(13, 8, P['st_hi'])
    return cv


def impact_img(k):
    cv = Cv(32, 32)
    n = (9, 7, 4)[k]
    for i in range(n):
        ang = 2 * math.pi * i / n + 0.4 * k
        r = (7, 11, 14)[k]
        x, y = 16 + math.cos(ang) * r, 22 + math.sin(ang) * r * 0.55 - (3 if k == 0 else 0)
        rr = (3.5, 2.5, 1.6)[k]
        t = Cv(32, 32)
        mass(t, [(x, y, rr, rr)], STONE, seed=i + 90, noise=0.2)
        t.outline(O)
        for yy in range(32):
            for xx in range(32):
                if t.p[yy][xx] is not None:
                    cv.p[yy][xx] = t.p[yy][xx]
    for i in range((10, 14, 8)[k]):                                  # poussiere
        x, y = round(16 + (rnd(i, 1, 60 + k) - 0.5) * (14, 26, 30)[k]), round(24 - rnd(i, 2, 60 + k) * (10, 7, 4)[k])
        if cv.get(x, y) is None:
            cv.set(x, y, P['dust'] if i % 2 else P['dust_d'])
    return cv


def rock_shadow(k):
    cv = Cv(32, 32)
    rx, ry = (5, 8, 11, 13)[k], (3, 5, 7, 8)[k]
    for y in range(32):
        for x in range(32):
            d = ((x + 0.5 - 16) / rx) ** 2 + ((y + 0.5 - 16) / ry) ** 2
            if d <= 1:
                solid = d < 0.45 or k == 3
                cv.p[y][x] = (27, 20, 32, 255) if solid or (x + y) % 2 == 0 else None
    if k == 3:                                                       # anneau de danger rouge qui clignote (cadre)
        for y in range(32):
            for x in range(32):
                d = ((x + 0.5 - 16) / rx) ** 2 + ((y + 0.5 - 16) / ry) ** 2
                if 0.78 < d <= 1 and (x + y) % 2 == 0:
                    cv.p[y][x] = P['cr_md']
    return cv


def strip(cvs, cell, path):
    W = cell * len(cvs)
    out = Cv(W, cell)
    for i, c in enumerate(cvs):
        for y in range(cell):
            for x in range(cell):
                if c.p[y][x] is not None:
                    out.p[y][i * cell + x] = c.p[y][x]
    save_png(path, out.p)


def write_tres(path_tres, texture_res, anims):
    """SpriteFrames : anims = [(nom, [(col, ligne)], fps, boucle)], cases 96x96."""
    subs, out, n = [], [], 0
    for name, cells, fps, loop in anims:
        fr = []
        for (c, r) in cells:
            n += 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{n}"]\natlas = ExtResource("1_gorm")\n'
                        f'region = Rect2({c * S}, {r * S}, {S}, {S})\n')
            fr.append('{"duration": 1.0, "texture": SubResource("AtlasTexture_%d")}' % n)
        out.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %s}' % (', '.join(fr), 'true' if loop else 'false', name, fps))
    txt = ('[gd_resource type="SpriteFrames" format=3]\n\n'
           f'[ext_resource type="Texture2D" path="{texture_res}" id="1_gorm"]\n\n' + '\n'.join(subs)
           + '\n[resource]\nanimations = [' + ', '.join(out) + ']\n')
    with open(path_tres, 'w', encoding='utf-8', newline='\n') as f:
        f.write(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    body, corr = build()
    save_png(os.path.join(OUT, 'gorm.png'), body.p)
    save_png(os.path.join(OUT, 'gorm_corruption.png'), corr.p)
    save_png(os.path.join(OUT, 'gorm_ombre.png'), shadow_img().p)
    strip([rock_img(0), rock_img(1), impact_img(0), impact_img(1), impact_img(2)], 32, os.path.join(OUT, 'rocher.png'))
    strip([rock_shadow(k) for k in range(4)], 32, os.path.join(OUT, 'rocher_ombre.png'))
    # animations
    anims = []
    for name, start, count, fps in ANIMS:
        loop = name in ('idle', 'marche', 'etourdi')
        if name == 'mort':
            anims.append(('mort', [(start + i, 2) for i in range(count)], fps, False))
            continue
        for r, st in enumerate(STATES):
            anims.append((f'{name}_{st}', [(start + i, r) for i in range(count)], fps, loop))
    write_tres(os.path.join(OUT, 'gorm_frames.tres'), 'res://art/bosses/gorm/gorm.png', anims)
    meta = {
        'cellule': [S, S], 'origine': [CX, GROUND - 0],
        'gorm.png': {'colonnes': N_COLS, 'lignes': STATES,
                     'animations': {n: {'debut': s, 'nombre': c, 'fps': f} for n, s, c, f in ANIMS},
                     'note': "ligne = etat d'armure (0 plein, 1 brise, 2 nu) ; 'mort' seulement sur la ligne 2 (nu)"},
        'gorm_corruption.png': 'memes cases que gorm.png : a superposer, a faire clignoter',
        'gorm_ombre.png': 'ombre au sol, 1 case 96x96, centree sur l\'origine',
        'rocher.png': {'cellule': [32, 32], 'ordre': ['rocher_a', 'rocher_b', 'impact0', 'impact1', 'impact2'],
                       'origine_rocher': [16, 26]},
        'rocher_ombre.png': {'cellule': [32, 32], 'ordre': ['ombre0', 'ombre1', 'ombre2', 'ombre3_clignote'], 'centre': [16, 16]},
        'plaques': {
            'plein': ['poitrine_gauche', 'poitrine_droite', 'epaule_gauche', 'epaule_droite', 'ventre'],
            'brise': ['poitrine_droite', 'epaule_droite'],
            'nu': [],
            'cristal_centre_px': 'x=48, y=48 (+ decalage vertical du corps selon la case)',
        },
        'zone_cristal_demi_taille': [7, 13],
    }
    with open(os.path.join(OUT, 'gorm.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print('gorm : ok', body.w, 'x', body.h)


if __name__ == '__main__':
    main()
