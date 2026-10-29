"""Donjon 2 (la Mine) : icône du sceau de la montagne (24x24) et variantes d'images de porte *_donjon2.png.
Recolorations par échange de palette à partir des portes existantes ; sans Pillow (pngview.read_png, coffres.save_png).
Usage : python mine_portes_sceau.py"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngview import read_png  # noqa: E402
from coffres import save_png  # noqa: E402

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'art')
PZ = os.path.join(ART, 'puzzles')


def rgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def recolor(path, mapping):
    m = {rgb(k): rgb(v) for k, v in mapping.items()}
    return [[m.get(p, p) for p in row] for row in read_png(path)]


def sceau():
    S = 24
    px = [[(0, 0, 0, 0)] * S for _ in range(S)]
    C = dict(hi='#c8c4d4', lt='#9c98b0', dk='#5c5870', ink='#2a2430', in1='#3a3040', in2='#4e4054',
             pk='#ece8f4', pk2='#b4b0c8', pk3='#78748c', ore='#f0c040')
    def P(x, y, c):
        if 0 <= x < S and 0 <= y < S:
            px[y][x] = rgb(C[c])
    for y in range(S):
        for x in range(S):
            dx, dy = x + 0.5 - 12, y + 0.5 - 12
            rr = math.hypot(dx, dy)
            if rr <= 11:
                if rr > 8:
                    v = -(dx * -0.45 + dy * -0.8) / 11
                    c = 'hi' if v < -0.55 else ('dk' if v > 0.45 else 'lt')
                else:
                    c = 'in2' if rr > 7 else 'in1'
                P(x, y, c)
    # glyphe : deux pics enneigés
    def peak(cx, top, base, half):
        for y in range(top, base + 1):
            w = ((y - top) * 2 * half + (base - top)) // (2 * (base - top))
            for x in range(cx - w, cx + w + 1):
                c = 'pk2' if x > cx else 'pk'
                if y - top >= 4:
                    c = 'pk3' if x > cx else 'pk2'
                if x - cx >= w - 1 and w > 1:
                    c = 'pk3'
                P(x, y, c)
    peak(9, 8, 17, 5)
    peak(15, 6, 17, 4)
    for x in range(7, 18):
        P(x, 18, 'pk3')
    # veine de minerai
    P(12, 14, 'ore'); P(13, 15, 'ore'); P(12, 16, 'ore')
    return px


PORTES = [
    ('porte_cle', 'porte_cle_donjon2', {'8a5a34': '6e4a30', 'b06e40': '8a6240', '5e3a22': '44301e',
                                         '9a948c': 'a8683c', '5c5650': '6e3a22', 'd8d4cc': 'e09860'}),
    ('porte_grande_cle', 'porte_grande_cle_donjon2', {'8a5a34': '6e4a30', 'b06e40': '8a6240', '5e3a22': '44301e'}),
    ('porte_ennemis', 'porte_ennemis_donjon2', {'3a1a4a': '4a1a14', '6a2a7a': '8a3a22'}),
]


def main():
    save_png(os.path.join(ART, 'items', 'sceau_montagne.png'), sceau())
    for src, dst, m in PORTES:
        save_png(os.path.join(PZ, dst + '.png'), recolor(os.path.join(PZ, src + '.png'), m))
    # porte à interrupteur : grille rouillée fermée (+ gemme de l'original) | moitié ouverte de l'original
    grille = read_png(os.path.join(PZ, 'grille_h_rouille.png'))
    orig = read_png(os.path.join(PZ, 'porte_interrupteur.png'))
    out = [[(0, 0, 0, 0)] * 64 for _ in range(32)]
    for y in range(32):
        for x in range(32):
            out[y][x] = grille[y][x]
            out[y][x + 32] = orig[y][x + 32]
    gem = {rgb(c) for c in ('8a5a1c', '961c28', 'fff4d0', 'e2342c')}
    for y in range(32):
        for x in range(32):
            if orig[y][x] in gem:
                out[y][x] = orig[y][x]
    save_png(os.path.join(PZ, 'porte_interrupteur_donjon2.png'), out)


if __name__ == '__main__':
    main()
