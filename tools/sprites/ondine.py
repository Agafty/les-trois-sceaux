"""Ondine, la Gardienne du Lac (boss du donjon 3) + anneau d'ondes du bassin - Les Trois Sceaux.  PLACEHOLDERS a retoucher.

Usage : python tools/sprites/ondine.py
Produit dans art/bosses/ondine/ (sans Pillow : encodeur PNG de tsplan.py) :
  ondine.png          planche 96x96 par case, 19 colonnes x 1 ligne : le CORPS d'Ondine (sirene sans armure, eau comprise)
  ondine_armure.png   calque d'ARMURE noire + corruption, memes cases : a superposer et a faire clignoter (vide hors phase 1)
  ondine_ombre.png    ombre au sol (1 case 96x96), pour la phase 2 (a genoux hors de l'eau)
  anneau.png          anneau d'ondes du bassin, 6 cases 96x32 (annonce du surgissement ; voir ondine.json)
  ondine.json         ordre des cases, animations, origine
  ondine_frames.tres  SpriteFrames Godot (ondine.png) ; ondine_armure_frames.tres (calque) ; anneau_frames.tres
Colonnes : 0 vide (sous l'eau) | 1-3 surgit | 4-5 idle expose | 6-8 attaque | 9 touche | 10-12 armure qui eclate |
           13-14 a genoux (phase 2) | 15-18 liberee (victoire).  "Plonge" = surgit a l'envers (3,2,1,0).
Origine : bas-centre (48, 94) ; le centre du bassin est au centre de la case horizontalement, la ligne d'eau est a y=84.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import save_png, ROOT, rgba  # noqa: E402

OUT = os.path.join(ROOT, 'art', 'bosses', 'ondine')
S = 96
CX = 48
WATER_Y = 84
NCOL = 19


def H(*hs):
    return tuple(rgba(h) for h in hs)


SKIN = H('#fbe2d0', '#ecbca2', '#c88e84', '#96667c')
HAIR = H('#8adcf0', '#4a9cd4', '#2e60a8', '#203a7c')
TAIL = H('#88f0d8', '#3cbcb4', '#248492', '#18546c')
WATER = H('#e4f8ff', '#8cd4f4', '#4e9cd6', '#2e64a4')
ARM = H('#7a7298', '#544e76', '#38324f', '#241e38')
ARM_FLASH = H('#fffaff', '#e8e0f8', '#b8b0d8', '#8a82ac')
OUTL = rgba('#14101e')
OUTL_BODY = rgba('#1c2850')
EYE = rgba('#ff4a60')
VIOLET = rgba('#7a2e8c')
VIOLET_D = rgba('#3e1a50')
DARK_EYE = rgba('#20243c')


def rnd(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


class L:
    def __init__(self, w=S, h=S):
        self.w, self.h = w, h
        self.p = [[None] * w for _ in range(h)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def ell(self, cx, cy, rx, ry, pal, seed=0, noise=0.2):
        hi, lt, md, dk = pal
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d = nx * nx + ny * ny
                if d <= 1 and 0 <= x < self.w and 0 <= y < self.h:
                    v = -(nx + ny) * 0.55 + (rnd(x, y, seed) - 0.5) * noise - d * 0.12 + 0.08
                    self.p[y][x] = hi if v > 0.52 else lt if v > 0.12 else md if v > -0.36 else dk

    def limb(self, a, b, r, pal, seed=0):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            self.ell(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, r, r, pal, seed)

    def clip_below(self, y0):
        for y in range(int(y0), self.h):
            for x in range(self.w):
                self.p[y][x] = None

    def shift(self, dx, dy):
        n = L(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                if self.p[y][x] is not None and 0 <= x + dx < self.w and 0 <= y + dy < self.h:
                    n.p[y + dy][x + dx] = self.p[y][x]
        return n

    def outline(self, c):
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.p[y][x] is None and any(
                        0 <= y + dy < self.h and 0 <= x + dx < self.w and self.p[y + dy][x + dx] is not None
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    add.append((x, y))
        for x, y in add:
            self.p[y][x] = c

    def paste(self, o):
        for y in range(self.h):
            for x in range(self.w):
                if o.p[y][x] is not None:
                    self.p[y][x] = o.p[y][x]


# ------------------------------------------------------------------ pose
class Pose:
    def __init__(self, **k):
        self.hx = 0            # decalage de la tete
        self.hy = 0
        self.arms = ((33, 64), (63, 64))   # mains (gauche, droite) en px de case
        self.kneel = False
        self.no_armor = False
        self.spread = 0        # ecartement des pieces d'armure (eclatement)
        self.__dict__.update(k)


def figure(pz):
    """Retourne (corps, armure) sans eau, avant decalage."""
    b, a = L(), L()
    hx, hy = pz.hx, pz.hy
    if pz.kneel:
        ty = 80
        b.ell(48, ty, 24, 9, TAIL, 3)                       # queue lovee
        b.ell(68, ty - 3, 7, 6, TAIL, 4)
        for k in range(3):                                   # nageoire
            b.limb((70, ty - 4), (80 + k * 2, ty - 10 + k * 5), 2, TAIL, 5)
        for x in range(30, 66, 5):                           # ecailles
            b.set(x, ty - 1 + (x // 5) % 2, TAIL[0])
        tor_y = 64
    else:
        tor_y = 66
    # cheveux (derriere)
    b.ell(48 + hx, 44 + hy, 17, 20, HAIR, 7, 0.3)
    for sx in (-1, 1):
        b.limb((48 + sx * 16 + hx, 50 + hy), (48 + sx * 19, tor_y + 8), 4, HAIR, 8)
    # torse
    b.ell(48, tor_y, 13, 15, SKIN, 1)
    b.ell(48, tor_y + 9, 12, 7, TAIL, 2)
    # cou, tete
    b.ell(48 + hx * 0.5, 53 + hy * 0.5, 5, 5, SKIN, 2)
    b.ell(48 + hx, 40 + hy, 12, 12, SKIN, 3, 0.12)
    b.ell(48 + hx, 31 + hy, 12, 5, HAIR, 9)                 # frange
    # bras
    for sx, hand in ((-1, pz.arms[0]), (1, pz.arms[1])):
        b.limb((48 + sx * 15, tor_y - 8), hand, 4, SKIN, 6)
        b.ell(hand[0], hand[1], 4, 4, SKIN, 6)
    # visage (visible une fois l'armure brisee)
    for sx in (-1, 1):
        ex = 48 + hx + sx * 5
        b.set(ex, 42 + hy, DARK_EYE)
        b.set(ex, 43 + hy, DARK_EYE)
        b.set(ex - sx, 42 + hy, rgba('#ffffff'))
    b.set(48 + hx, 47 + hy, SKIN[3])
    b.set(47 + hx, 47 + hy, SKIN[3])
    if not pz.no_armor:
        sp = pz.spread
        a.ell(48 + hx, 37 + hy - sp * 0.4, 14, 13, ARM, 11, 0.15)          # casque
        for y in range(47 + hy, S):
            for x in range(S):
                if abs(x - 48 - hx) < 20 and y < 80:
                    a.p[y][x] = None
        for x in range(36 + hx, 61 + hx):                    # fente de visiere
            for y in (41 + hy, 42 + hy):
                a.set(x, y, OUTL)
        for sx in (-1, 1):
            for k in (0, 1):
                a.set(48 + hx + sx * 5 + k * sx, 42 + hy, EYE)
        for k in range(7):                                    # cimier
            a.set(47 + hx, 25 + hy + k, ARM[0])
            a.set(48 + hx, 25 + hy + k, ARM[1])
        a.ell(48, tor_y - 2 - sp * 0.2, 14, 11, ARM, 12)     # plastron
        for y in range(tor_y + 10, S):
            for x in range(S):
                a.p[y][x] = None
        for y in range(tor_y - 12, tor_y + 10):
            a.set(48, y, OUTL)
        a.ell(33 - sp * 0.8, tor_y - 10, 7, 6, ARM, 13)      # epaulieres
        a.ell(63 + sp * 0.8, tor_y - 10, 7, 6, ARM, 14)
        for sx, hand in ((-1, pz.arms[0]), (1, pz.arms[1])):  # gantelets
            a.limb((hand[0] + sx * sp, hand[1] - 5), (48 + sx * 15 + sx * sp * 0.7, tor_y - 12), 3, ARM, 16)
            a.ell(hand[0] + sx * sp, hand[1], 6, 6, ARM, 15)
        for (x0, y0, ln) in ((40, tor_y - 4, 6), (56, tor_y, 5), (44, 33 + hy, 4), (34, tor_y - 11, 3), (62, tor_y - 12, 3)):
            for k in range(ln):                               # corruption : veines violettes
                a.set(x0 + k, y0 + (k % 2) + k // 3, VIOLET if k % 2 == 0 else VIOLET_D)
        a.outline(OUTL)
    b.outline(OUTL_BODY)
    return b, a


def water_front(rx, ry, splash=0, phase=0):
    """Avant de la surface de l'eau : ellipse plate, liseré clair et eclaboussures."""
    w = L()
    w.ell(CX, WATER_Y + 4, rx, ry, WATER, 21, 0.1)
    for a_ in range(0, 360, 6):
        s = math.sin(math.radians(a_))
        if s > 0.1:
            w.set(CX + (rx + 3) * math.cos(math.radians(a_)), WATER_Y + 4 + (ry + 2) * s, WATER[0])
    for k in range(splash):                                   # gouttes
        a_ = math.radians(200 + k * (140 / max(1, splash - 1)) + phase * 9)
        r = rx * 0.7 + (k % 3) * 3
        w.set(CX + r * math.cos(a_), WATER_Y - 4 + (k % 4) * 3 + 6 * math.sin(a_), WATER[0])
        w.set(CX + r * math.cos(a_), WATER_Y - 5 + (k % 4) * 3 + 6 * math.sin(a_), WATER[1])
    return w


def compose(pz, water=True, rx=24, ry=7, splash=0, phase=0, dy=0, flash=False, armor=True):
    body, arm = figure(pz)
    if dy:
        body, arm = body.shift(0, dy), arm.shift(0, dy)
    if water:
        body.clip_below(WATER_Y)
        arm.clip_below(WATER_Y)
        bl = L()
        bl.ell(CX, WATER_Y + 3, rx, ry, WATER, 22, 0.1)
        bl.paste(body)
        for x in range(S):                                    # ligne d'eau : rangee claire a la jonction
            if body.p[WATER_Y - 1][x] is not None:
                bl.p[WATER_Y][x] = WATER[1]
        bl.paste(water_front(rx, ry, splash, phase))
        body = bl
    if flash:
        for y in range(S):
            for x in range(S):
                c = arm.p[y][x]
                if c in ARM:
                    arm.p[y][x] = ARM_FLASH[ARM.index(c)]
    if not armor:
        arm = L()
    return body, arm


def sparkles(layer, t, n=10, rad=30, cy=52):
    for k in range(n):
        a_ = (k / n) * 6.283 + t * 0.7
        r = rad - ((k * 7 + t * 5) % 12)
        x, y = CX + r * math.cos(a_), cy + r * 0.8 * math.sin(a_)
        layer.set(x, y, WATER[0])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            layer.set(x + dx, y + dy, WATER[1])


def build():
    cells = [(L(), L())]                                       # 0 : sous l'eau
    for i, (dy, sp, rx) in enumerate(((40, 5, 18), (22, 9, 26), (6, 12, 28))):   # 1-3 surgit
        cells.append(compose(Pose(arms=((34, 66), (62, 66))), dy=dy, splash=sp, phase=i, rx=rx, ry=8))
    for i in range(2):                                         # 4-5 idle
        cells.append(compose(Pose(arms=((34, 66 + i), (62, 66 + i)), hy=i), dy=i, rx=24 + i, ry=7))
    # 6-8 attaque : recul, jaillissement, retour
    cells.append(compose(Pose(arms=((28, 52), (68, 52)), hy=-1), dy=-2, rx=26, ry=8, splash=4))
    cells.append(compose(Pose(arms=((22, 74), (74, 74)), hy=3), dy=2, rx=36, ry=11, splash=12, phase=1))
    cells.append(compose(Pose(arms=((30, 68), (66, 68))), dy=0, rx=30, ry=9, splash=6, phase=2))
    # 9 touche
    cells.append(compose(Pose(arms=((36, 62), (60, 62)), hx=-2, hy=2), dy=2, rx=24, ry=7, flash=True))
    # 10-12 l'armure eclate (le corps descend, les pieces s'ecartent puis s'effacent)
    for i, (sp, dy) in enumerate(((3, 0), (9, 4), (16, 10))):
        pz = Pose(arms=((34, 66), (62, 66)), spread=sp, hy=i)
        body, arm = compose(pz, dy=dy, rx=24, ry=7, splash=6 if i == 0 else 3)
        if i == 2:
            for y in range(S):
                for x in range(S):
                    if arm.p[y][x] is not None and (x + y) % 2 == 0:
                        arm.p[y][x] = None
        cells.append((body, arm))
    # 13-14 a genoux
    for i in range(2):
        cells.append(compose(Pose(kneel=True, no_armor=True, arms=((40, 76 + i), (56, 76 + i)), hy=3 + i), water=False, armor=False))
    # 15-18 liberee
    arms = [((40, 76), (56, 76)), ((36, 70), (60, 70)), ((28, 62), (68, 62)), ((26, 56), (70, 56))]
    for i in range(4):
        body, _ = compose(Pose(kneel=True, no_armor=True, hy=[2, 0, -1, -1][i], arms=arms[i]), water=False, armor=False)
        sparkles(body, i, n=6 + i * 2, rad=26 + i * 3)
        cells.append((body, L()))
    return cells


def sheet(layers):
    out = L(S * NCOL, S)
    for i, c in enumerate(layers):
        for y in range(S):
            for x in range(S):
                if c.p[y][x] is not None:
                    out.p[y][i * S + x] = c.p[y][x]
    return out


def shadow():
    s = L()
    for y in range(S):
        for x in range(S):
            nx, ny = (x + 0.5 - CX) / 30, (y + 0.5 - 86) / 7
            d = nx * nx + ny * ny
            if d <= 0.6 or (d <= 1 and (x + y) % 2 == 0):
                s.p[y][x] = (20, 16, 40, 110)
    return s


def ring_sheet():
    """6 cases 96x32 : l'anneau d'ondes s'ouvre (annonce) puis pulse. Centre (48,16), vu de dessus (ellipse aplatie)."""
    out = L(96 * 6, 32)
    radii = [6, 12, 18, 24, 30, 36]
    for i in range(6):
        r = radii[i] if i < 4 else [27, 33][i - 4]
        for a_ in range(0, 360, 2):
            s = math.sin(math.radians(a_))
            x = 48 + i * 96 + r * math.cos(math.radians(a_))
            y = 16 + r * 0.36 * s
            out.set(x, y, WATER[0] if s > 0 else WATER[1])
            if i >= 2 and s > 0 and (a_ // 2) % 5 != 0:
                out.set(x, y + 1, WATER[2])
        if i >= 1:                                              # second anneau, plus petit
            for a_ in range(0, 360, 4):
                out.set(48 + i * 96 + r * 0.55 * math.cos(math.radians(a_)), 16 + r * 0.2 * math.sin(math.radians(a_)), WATER[1])
    return out


def write_tres(path, tex, cw, ch, anims, extid):
    subs, out, n = [], [], 0
    for name, cells, fps, loop in anims:
        fr = []
        for c in cells:
            n += 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{n}"]\natlas = ExtResource("{extid}")\n'
                        f'region = Rect2({c * cw}, 0, {cw}, {ch})\n')
            fr.append('{"duration": 1.0, "texture": SubResource("AtlasTexture_%d")}' % n)
        out.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %s}' % (', '.join(fr), 'true' if loop else 'false', name, fps))
    txt = ('[gd_resource type="SpriteFrames" format=3]\n\n'
           f'[ext_resource type="Texture2D" path="{tex}" id="{extid}"]\n\n' + '\n'.join(subs)
           + '\n[resource]\nanimations = [' + ', '.join(out) + ']\n')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(txt)


ANIMS = [  # nom, cases, fps, boucle
    ('cache', [0], 1.0, False),
    ('surgit', [1, 2, 3], 8.0, False),
    ('plonge', [3, 2, 1, 0], 8.0, False),
    ('idle', [4, 5], 3.0, True),
    ('attaque', [6, 7, 8], 6.0, False),
    ('touche', [9], 1.0, False),
    ('eclate', [10, 11, 12], 5.0, False),
    ('agenouillee', [13, 14], 2.0, True),
    ('liberee', [15, 16, 17, 18], 4.0, False),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    cells = build()
    save_png(os.path.join(OUT, 'ondine.png'), sheet([c[0] for c in cells]).p)
    save_png(os.path.join(OUT, 'ondine_armure.png'), sheet([c[1] for c in cells]).p)
    save_png(os.path.join(OUT, 'ondine_ombre.png'), shadow().p)
    save_png(os.path.join(OUT, 'anneau.png'), ring_sheet().p)
    write_tres(os.path.join(OUT, 'ondine_frames.tres'), 'res://art/bosses/ondine/ondine.png', S, S, ANIMS, '1_ondine')
    write_tres(os.path.join(OUT, 'ondine_armure_frames.tres'), 'res://art/bosses/ondine/ondine_armure.png', S, S,
               [a for a in ANIMS if a[0] in ('surgit', 'plonge', 'idle', 'attaque', 'touche', 'eclate')], '1_armure')
    write_tres(os.path.join(OUT, 'anneau_frames.tres'), 'res://art/bosses/ondine/anneau.png', 96, 32,
               [('annonce', [0, 1, 2, 3], 5.0, False), ('pulse', [4, 5], 4.0, True)], '1_anneau')
    meta = {'cellule': [S, S], 'origine': [CX, 94], 'ligne_d_eau_y': WATER_Y,
            'ondine.png': {'colonnes': NCOL, 'animations': {n: {'cases': c, 'fps': f, 'boucle': l} for n, c, f, l in ANIMS}},
            'ondine_armure.png': 'memes cases : calque a superposer et a faire clignoter (vide pour cache, agenouillee, liberee)',
            'ondine_ombre.png': 'ombre au sol 96x96 (phase 2)',
            'anneau.png': {'cellule': [96, 32], 'centre': [48, 16], 'annonce': [0, 1, 2, 3], 'pulse': [4, 5],
                           'note': "anneau d'ondes du bassin : 'annonce' une fois (1,5 s), puis 'pulse' en boucle jusqu'au surgissement"}}
    with open(os.path.join(OUT, 'ondine.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print('ok')


if __name__ == '__main__':
    main()
