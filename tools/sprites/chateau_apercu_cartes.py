"""Aperçus des vraies cartes (.tmx) recomposées avec les tuiles finales : vérifie les raccords en situation.

Usage : python tools/sprites/chateau_apercu_cartes.py
Produit : art/tilesets/chateau_apercu.png (salles 01 à 04 et arène) et art/tilesets/route_chateau_apercu.png
(route_falaise, passage_falaise, cour). Calques Sol, Decor, Murs, Dessus ; les objets Tiled ne sont pas dessinés.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fondus_lib import read_png, save_png, ROOT, T  # noqa: E402


def load_map(path):
    s = open(path, encoding='utf-8').read()
    w, h = (int(v) for v in re.search(r'<map [^>]*width="(\d+)" height="(\d+)"', s).groups())
    src = re.search(r'<tileset firstgid="(\d+)" source="[^"]*?([^/"]+)\.tsx"', s)
    layers = {}
    for m in re.finditer(r'<layer [^>]*name="(\w+)".*?<data encoding="csv">(.*?)</data>', s, re.S):
        vals = [int(v) for v in re.split(r'[,\s]+', m.group(2).strip()) if v]
        layers[m.group(1)] = [vals[y * w:(y + 1) * w] for y in range(h)]
    return w, h, int(src.group(1)), src.group(2), layers


def render_map(path, sheets):
    w, h, first, ts, layers = load_map(path)
    if ts not in sheets:
        sheets[ts] = read_png(os.path.join(ROOT, 'art', 'tilesets', ts + '.png'))
    sheet = sheets[ts]
    cols = len(sheet[0]) // T
    img = [[(14, 12, 24, 255)] * (w * T) for _ in range(h * T)]
    for name in ('Sol', 'Decor', 'Murs', 'Dessus'):
        for y, row in enumerate(layers.get(name, [])):
            for x, g in enumerate(row):
                if not g:
                    continue
                fh, fv = bool(g & 0x80000000), bool(g & 0x40000000)
                i = (g & 0x1FFFFFFF) - first
                cx, cy = (i % cols) * T, (i // cols) * T
                for j in range(T):
                    for k in range(T):
                        p = sheet[cy + (T - 1 - j if fv else j)][cx + (T - 1 - k if fh else k)]
                        if p[3]:
                            img[y * T + j][x * T + k] = p
    return img


def stack(images, gap=8):
    W = max(len(i[0]) for i in images)
    H = sum(len(i) for i in images) + gap * (len(images) - 1)
    out = [[(0, 0, 0, 255)] * W for _ in range(H)]
    y0 = 0
    for im in images:
        for y, row in enumerate(im):
            out[y0 + y][:len(row)] = row
        y0 += len(im) + gap
    return out


def side(images, gap=8):
    H = max(len(i) for i in images)
    W = sum(len(i[0]) for i in images) + gap * (len(images) - 1)
    out = [[(0, 0, 0, 255)] * W for _ in range(H)]
    x0 = 0
    for im in images:
        for y, row in enumerate(im):
            out[y][x0:x0 + len(row)] = row
        x0 += len(im[0]) + gap
    return out


def main():
    sheets = {}
    m = os.path.join(ROOT, 'maps')
    t = os.path.join(ROOT, 'art', 'tilesets')
    ch = [render_map(os.path.join(m, 'chateau', f), sheets) for f in ('salle_01.tmx', 'salle_02.tmx', 'salle_03.tmx', 'salle_04.tmx', 'salle_boss.tmx')]
    save_png(os.path.join(t, 'chateau_apercu.png'), side([stack(ch[:4]), ch[4]]))
    rt = [render_map(os.path.join(m, 'overworld', 'route_falaise.tmx'), sheets)]
    cour = render_map(os.path.join(m, 'overworld', 'chateau.tmx'), sheets)
    gro = render_map(os.path.join(m, 'interieurs', 'passage_falaise.tmx'), sheets)
    save_png(os.path.join(t, 'route_chateau_apercu.png'), stack([rt[0], side([gro, cour])]))
    print('aperçus de cartes écrits.')


if __name__ == '__main__':
    main()
