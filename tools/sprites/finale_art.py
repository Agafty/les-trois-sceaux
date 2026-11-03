"""Petits elements de la fin du jeu - Les Trois Sceaux (PLACEHOLDERS a retoucher).
Usage : python tools/sprites/finale_art.py
  art/puzzles/porte_mur_rune_v.png    64x64 : mur a rune VERTICAL 32x64 ; fermee (gauche) | ouverte (droite)
  art/items/sceau_unique.png          32x32 : les trois cercles fondus en un
  art/characters/brann_forge.png      128x32 : Brann qui forge, 4 images (leve, haut, frappe, retombe) ; brann_forge_frames.tres
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngview import read_png  # noqa: E402
from tsplan import save_png, ROOT, rgba  # noqa: E402
import sanctuaire_hors_tileset as sh  # noqa: E402

ART = os.path.join(ROOT, 'art')


def porte_v():
    px = sh.canvas(64, 64)
    # fermee : pierre violet-gris a joints, grande rune au centre
    sh.rect(px, 0, 0, 31, 63, '#5e6290')
    sh.rect(px, 0, 0, 31, 2, '#7a7eb0')
    sh.rect(px, 0, 61, 31, 63, '#3c3e66')
    for y in (16, 32, 48):
        sh.rect(px, 1, y, 30, y, '#3c3e66')
    for (x, y0, y1) in ((10, 0, 15), (22, 17, 31), (12, 33, 47), (24, 49, 60)):
        sh.rect(px, x, y0, x, y1, '#3c3e66')
    for y in range(64):
        sh.put(px, 0, y, '#2a2a4a')
        sh.put(px, 31, y, '#2a2a4a')
    sh.rect(px, 7, 18, 24, 45, '#404478')
    sh.rune(px, 0, 15, 31, '#a8f4ff', '#40c8e8')
    for cy in (8, 56):          # petites runes
        sh.rect(px, 13, cy - 2, 18, cy + 2, '#404478')
        sh.put(px, 15, cy - 1, '#40c8e8')
        sh.put(px, 16, cy - 1, '#40c8e8')
        sh.put(px, 15, cy + 1, '#a8f4ff')
    # ouverte : alcove noire, montants de pierre
    sh.rect(px, 32, 0, 63, 63, '#14101c')
    sh.rect(px, 32, 0, 35, 63, '#5e6290')
    sh.rect(px, 60, 0, 63, 63, '#3c3e66')
    sh.rect(px, 32, 0, 63, 3, '#7a7eb0')
    sh.rect(px, 36, 4, 59, 4, '#26264a')
    for y in range(12, 60, 8):
        sh.put(px, 44, y, '#3a5878')
        sh.put(px, 52, y + 4, '#3a5878')
    sh.rect(px, 47, 28, 48, 31, '#2a4868')
    save_png(os.path.join(ART, 'puzzles', 'porte_mur_rune_v.png'), px)


def sceau_unique():
    px = sh.canvas(32, 32)
    cols = {'r': ('#9ad060', '#5a8a3c', '#2e5a2c'), 'm': ('#f0a050', '#c06a30', '#7a3a20'),
            'l': ('#8adcf0', '#3c7ac0', '#203e7a')}
    cen = {'r': (16, 12), 'm': (11.5, 19.5), 'l': (20.5, 19.5)}
    GOLD, GOLD_D, GOLD_L = rgba('#e8c040'), rgba('#9a6a20'), rgba('#fff4b8')
    for y in range(32):
        for x in range(32):
            dx, dy = x + 0.5 - 16, y + 0.5 - 16
            d = math.hypot(dx, dy)
            if d > 15.2:
                continue
            if d > 13.2:
                px[y][x] = GOLD_D if (dx + dy) > 4 else GOLD
                continue
            inside = [k for k, (cx, cy) in cen.items() if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= 8]
            if len(inside) == 3 or d < 3.2:
                px[y][x] = GOLD_L if d < 2.2 else GOLD
            elif len(inside) == 2:
                px[y][x] = rgba('#f4ecd0') if (x + y) % 2 else GOLD
            elif len(inside) == 1:
                hi, md, dk = cols[inside[0]]
                cx, cy = cen[inside[0]]
                v = (x + 0.5 - cx) * 0.6 + (y + 0.5 - cy) * 0.8
                px[y][x] = rgba(hi if v < -3 else dk if v > 4 else md)
            else:
                px[y][x] = rgba('#3a2a4e') if d > 9 else rgba('#4e3a66')
    out = [[c for c in r] for r in px]
    for y in range(32):
        for x in range(32):
            if px[y][x][3] == 0 and any(0 <= y + b < 32 and 0 <= x + a < 32 and px[y + b][x + a][3]
                                        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = rgba('#1b1420')
    save_png(os.path.join(ART, 'items', 'sceau_unique.png'), out)


def brann_forge():
    src = read_png(os.path.join(ART, 'characters', 'brann.png'))
    base = [[src[y][x] for x in range(32)] for y in range(32)]      # idle_down
    GL, GLD = rgba('#4a3426'), rgba('#2e2018')
    MT = [rgba(c) for c in ('#d8d4cc', '#9a948c', '#5c5650', '#3a3632')]
    WD = [rgba(c) for c in ('#b06e40', '#8a5a34', '#5e3a22')]
    O = rgba('#1b1420')
    SP = [rgba('#fff4b8'), rgba('#ffb040'), rgba('#e2342c')]

    def blank():
        return [[(0, 0, 0, 0)] * 32 for _ in range(32)]

    def body(dy_top=0):
        f = blank()
        for y in range(32):
            for x in range(32):
                if base[y][x][3]:
                    ny = y + (dy_top if y < 24 else 0)
                    if 0 <= ny < 32:
                        f[ny][x] = base[y][x]
        if dy_top < 0:
            for x in range(32):
                f[23][x] = base[23][x]
        return f

    def box(f, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < 32 and 0 <= y < 32:
                    f[y][x] = c

    def hamr(f, hand, tip, head, hw=8, hh=5):
        (x0, y0), (x1, y1) = hand, tip
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            x, y = round(x0 + (x1 - x0) * i / max(1, n)), round(y0 + (y1 - y0) * i / max(1, n))
            box(f, x, y, x + 1, y, WD[1])
            box(f, x, y, x, y, WD[0])
        hx, hy = head
        box(f, hx - 1, hy - 1, hx + hw, hy + hh, O)
        box(f, hx, hy, hx + hw - 1, hy + hh - 1, MT[2])
        box(f, hx, hy, hx + hw - 1, hy, MT[0])
        box(f, hx, hy, hx, hy + hh - 1, MT[1])
        box(f, hx, hy + hh - 1, hx + hw - 1, hy + hh - 1, MT[3])
        box(f, x0 - 1, y0 - 1, x0 + 2, y0 + 2, GLD)
        box(f, x0, y0, x0 + 1, y0 + 1, GL)

    frames = []
    f = body(0)
    hamr(f, (25, 23), (26, 12), (22, 8))
    frames.append(f)
    f = body(-1)
    hamr(f, (25, 20), (24, 4), (20, 0))
    frames.append(f)
    f = body(2)
    hamr(f, (24, 25), (17, 29), (9, 27), 9, 4)
    for (x, y, c) in ((7, 25, 0), (5, 27, 1), (8, 23, 1), (6, 29, 2), (10, 31, 2)):
        f[y][x] = SP[c]
    frames.append(f)
    f = body(1)
    hamr(f, (25, 24), (19, 28), (11, 26), 9, 4)
    for (x, y, c) in ((6, 24, 1), (4, 27, 2)):
        f[y][x] = SP[c]
    frames.append(f)
    px = [[(0, 0, 0, 0)] * 128 for _ in range(32)]
    for i, fr in enumerate(frames):
        for y in range(32):
            for x in range(32):
                px[y][i * 32 + x] = fr[y][x]
    save_png(os.path.join(ART, 'characters', 'brann_forge.png'), px)
    subs, fr = [], []
    for i in range(4):
        subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{i + 1}"]\natlas = ExtResource("1_brann_forge")\n'
                    f'region = Rect2({i * 32}, 0, 32, 32)\n')
        fr.append('{"duration": 1.0, "texture": SubResource("AtlasTexture_%d")}' % (i + 1))
    txt = ('[gd_resource type="SpriteFrames" format=3]\n\n'
           '[ext_resource type="Texture2D" path="res://art/characters/brann_forge.png" id="1_brann_forge"]\n\n'
           + '\n'.join(subs)
           + '\n[resource]\nanimations = [{"frames": [%s], "loop": true, "name": &"forge", "speed": 4.0}]\n' % ', '.join(fr))
    with open(os.path.join(ART, 'characters', 'brann_forge_frames.tres'), 'w', newline='\n') as fh:
        fh.write(txt)


if __name__ == '__main__':
    porte_v()
    sceau_unique()
    brann_forge()
    print('ok')
