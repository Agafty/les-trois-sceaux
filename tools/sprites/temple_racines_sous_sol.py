"""Tileset du SOUS-SOL du Temple des Racines (salles 11 a 15) — Les Trois Sceaux.

Meme numerotation, memes collisions et memes terrains que temple_racines : l'image est recoloree (pierre bleu-vert
sombre, murs bleu nuit) et les racines sont plus epaisses (tuiles 6 a 8 redessinees, grosses racines sur des dalles).
Reserve utilisee : 9, 10, 11 = fresque_ordre_a/b/c (gland, racine, feuille), tuiles de mur nord (collision pleine).

Usage : python tools/sprites/temple_racines_sous_sol.py [dossier_apercu]
Produit art/tilesets/temple_racines_sous_sol.png et maps/tilesets/temple_racines_sous_sol.tsx.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import temple_racines as TR
import temple_racines_final as F
from symboles import SYMBOLS, NATUREL

NAME = 'temple_racines_sous_sol'
T = 32


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


# ancien -> nouveau (pierre froide bleu-vert, murs bleu nuit, terre et racines plus sombres)
RECOLOR = {
    'sol': '#56746f', 'joint': '#213a3e', 'clair': '#8aaaa4', 'sol_l': '#658480', 'sol_s': '#445c5c',
    'cap': '#22344a', 'rim': '#2e4a5e', 'face': '#4a7488', 'mur_c': '#8ab8c4',
    'cap_l': '#2a4258', 'cap_d': '#18263a', 'face_l': '#5a8498', 'face_s': '#3a5c70',
    'O': '#0e1820', 'I': '#14202a',
    'terre': '#6e4a30', 'terre_s': '#4a3022', 'terre_c': '#946440',
    'racine': '#5e3a24', 'racine_s': '#3a2218',
    'vert': '#3f8a5a', 'vert_c': '#52a46c', 'vert_s': '#245a3c',
}
MAP = {F.C[k]: rgb(v) for k, v in RECOLOR.items()}


def recolor(img):
    return [[MAP.get(p, p) if p else p for p in row] for row in img]


def blit(dst, src, ox=0, oy=0):
    for y in range(len(src)):
        for x in range(len(src[0])):
            if src[y][x] is not None:
                dst[oy + y][ox + x] = src[y][x]


def racine_epaisse(kind):
    """Racines de 8 px de large (au lieu de 5) qui se raccordent bord a bord comme racine_h / racine_v."""
    t = F.new()
    if kind in ('h', 'v'):
        pts = [(x, 15 + round(2.5 * math.sin(2 * math.pi * x / 32))) for x in range(-2, 35, 2)]
        if kind == 'v':
            pts = [(b, a) for a, b in pts]
        F.tube(t, pts, 3.9, 3.9)
        rnd = random.Random(21)
        for _ in range(26):                                 # ecorce
            x, y = rnd.randrange(32), rnd.randrange(32)
            if t[y][x] in (F.C['terre'], F.C['racine']):
                F.px(t, x, y, 'racine_s')
        for a0, sgn in ((5, -1), (22, 1)):                  # radicelles
            for k in range(1, 7):
                a, b = a0 + k // 2, 15 + sgn * (4 + k)
                if kind == 'h':
                    F.px(t, a, b, 'racine_s')
                else:
                    F.px(t, b, a, 'racine_s')
    else:
        F.tube(t, [(0, 15), (12, 15)], 3.8, 3.8)
        F.tube(t, [(20, 15), (31, 14)], 3.8, 3.8)
        for pts, r0, r1 in (([(14, 13), (10, 8), (8, 2)], 3.6, 1.4), ([(19, 17), (22, 23), (21, 30)], 3.4, 1.3),
                            ([(11, 17), (7, 23)], 2.4, 1.0)):
            F.tube(t, pts, r0, r1)
        F.tube(t, [(16, 15)], 6.6, 6.6)
        for x, y in ((13, 11), (14, 11), (12, 12), (15, 10)):
            F.px(t, x, y, 'terre_c')
    F.outline(t)
    return t


def grosse_racine_coin(img, variant):
    """Pose une grosse racine qui rampe sur la dalle (a l'interieur : elle ne touche pas les bords)."""
    t = [r[:] for r in img]
    over = F.new()
    pts = ([(5, 26), (9, 23), (14, 24), (20, 21)] if variant == 0 else
           [(26, 6), (23, 10), (21, 14), (24, 19)] if variant == 1 else [(6, 7), (10, 10), (13, 15)])
    F.tube(over, pts, 3.4, 2.0)
    F.outline(over)
    blit(t, over)
    return t


def fresque(k):
    """Mur nord avec un cadre de pierre pale et un symbole lumineux (12x12 agrandi x2 = 24 px)."""
    t = F.wall((1, 1, 0, 0))
    F.rect(t, 1, 1, 30, 30, 'O')
    F.rect(t, 2, 2, 29, 29, 'mur_c')
    F.rect(t, 3, 3, 28, 28, 'cap_d')
    F.rect(t, 28, 3, 28, 28, 'face_s')
    F.rect(t, 3, 28, 28, 28, 'face_s')
    t = recolor(t)
    name = ('gland', 'racine', 'feuille')[k]
    cols = [rgb(c) for c in NATUREL[name]]
    ch = {'l': cols[0], 'm': cols[1], 'd': cols[2]}
    halo, fond, noir = rgb(RECOLOR['cap_l']), rgb(RECOLOR['cap_d']), rgb(RECOLOR['O'])
    for y in range(3, 28):                                 # halo derriere le symbole
        for x in range(3, 28):
            if math.hypot(x - 15.5, y - 15.5) < 12.5:
                t[y][x] = halo
    ox, oy = 4, 4
    for y, row in enumerate(SYMBOLS[name]):
        for x, c in enumerate(row):
            if c in ch:
                for dy in (0, 1):
                    for dx in (0, 1):
                        t[oy + y * 2 + dy][ox + x * 2 + dx] = ch[c]
    vals = set(ch.values())
    for y in range(3, 28):                                 # contour sombre fin autour du symbole
        for x in range(3, 28):
            if t[y][x] == halo and any(t[y + dy][x + dx] in vals for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                t[y][x] = noir
    return t


# Tuiles reprises de temple_racines_final.py sans retexture v2 : recolorees en sous-sol
F_DECOR = list(range(31, 40)) + [56, 57, 112, 113, 114, 115, 116]


def build_images():
    TR.apply_final('sous_sol', thick_roots=True)        # dessin v2, theme sous-sol (pierre bleu-vert, racines epaisses)
    out = {i: d['img'] for i, d in TR.TILES.items()}
    for i in F_DECOR:
        out[i] = recolor(out[i])
    out[9], out[10], out[11] = fresque(0), fresque(1), fresque(2)   # deja recolorees
    return out


def main():
    imgs = build_images()
    sheet = [[None] * (TR.COLS * T) for _ in range(TR.ROWS * T)]
    for i, im in imgs.items():
        blit(sheet, im, (i % TR.COLS) * T, (i // TR.COLS) * T)
    root = TR.ROOT
    TR.save_png(os.path.join(root, 'art', 'tilesets', NAME + '.png'), sheet)
    for i, nom in ((9, 'fresque_ordre_a'), (10, 'fresque_ordre_b'), (11, 'fresque_ordre_c')):
        TR.TILES[i] = dict(nom=nom, role='', calque='Murs', collision=TR.FULL, img=imgs[i])
    TR.NAME = NAME
    with open(os.path.join(root, 'maps', 'tilesets', NAME + '.tsx'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(TR.build_tsx())
    if len(sys.argv) > 1:
        d = sys.argv[1]
        os.makedirs(d, exist_ok=True)
        for i, im in imgs.items():
            if i in TR.TILES:
                TR.TILES[i]['img'] = im
        TR.save_png(os.path.join(d, 'sous_sol_apercu.png'), TR.build_preview(), 2)
        row = [[None] * 96 for _ in range(32)]
        for k, i in enumerate((9, 10, 11)):
            blit(row, imgs[i], k * 32, 0)
        TR.save_png(os.path.join(d, 'fresque_x8.png'), [[p or (56, 46, 66, 255) for p in r] for r in row], 8)


if __name__ == '__main__':
    main()
