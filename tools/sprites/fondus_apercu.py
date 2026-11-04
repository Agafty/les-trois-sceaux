"""Apercus de controle des fondus : assemblages de transitions + extraits des vraies cartes.

Usage : python tools/sprites/fondus_apercu.py <tileset> [x y w h carte ...]
Produit art/tilesets/<tileset>_apercu_transitions.png : en haut les 16 tuiles de chaque terrain posees en grille 4x4 et
des blobs 3x3 reconstruits a la maniere de Tiled ; en bas des extraits des cartes de maps/overworld/ (x y w h en tuiles).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fondus_lib import ROOT, T, Tileset, save_png, read_png  # noqa: E402

_CACHE = {}


def sheet(name):
    if name not in _CACHE:
        _CACHE[name] = Tileset(name)
    return _CACHE[name]


def load_map(path):
    r = ET.parse(path).getroot()
    w, h = int(r.get('width')), int(r.get('height'))
    sets = []
    for ts in r.findall('tileset'):
        src = os.path.basename(ts.get('source'))
        sets.append((int(ts.get('firstgid')), src.replace('.tsx', '')))
    sets.sort()
    layers = {}
    for ly in r.findall('layer'):
        data = [int(v) & 0x1fffffff for v in re.split(r'[,\s]+', ly.find('data').text.strip()) if v]
        layers[ly.get('name')] = data
    return w, h, sets, layers


def compose(path, x0, y0, cw, ch, names=('Sol', 'Decor', 'Murs', 'Dessus'), bg=(40, 36, 48, 255)):
    w, h, sets, layers = load_map(path)
    out = [[bg for _ in range(cw * T)] for _ in range(ch * T)]
    for ln in names:
        data = layers.get(ln)
        if not data:
            continue
        for ty in range(ch):
            for tx in range(cw):
                mx, my = x0 + tx, y0 + ty
                if mx >= w or my >= h:
                    continue
                g = data[my * w + mx]
                if not g:
                    continue
                fg, nm = [s for s in sets if s[0] <= g][-1]
                t = sheet(nm).tile(g - fg)
                for y in range(T):
                    for x in range(T):
                        p = t[y][x]
                        if p[3]:
                            out[ty * T + y][tx * T + x] = p
    return out


def blit(dst, src, ox, oy):
    for y, row in enumerate(src):
        for x, p in enumerate(row):
            if 0 <= oy + y < len(dst) and 0 <= ox + x < len(dst[0]):
                dst[oy + y][ox + x] = p


def block_view(ts, base, top, grass_id):
    """Grille 4x4 des 16 tuiles du terrain, avec la tuile pleine A autour."""
    pass


def terrain_blocks(name):
    ts = sheet(name)
    res = []
    for wname, ncol, tiles in ts.wangsets:
        if ncol != 2:
            continue
        top = max(tiles)
        res.append((wname, top - 15, tiles))
    return res


def blob_assembly(name, base, tiles, gridmap):
    """gridmap : liste de chaines de '0'/'1' (coins) ; renvoie l'image des tuiles Wang correspondantes (taille (h-1) x (w-1))."""
    ts = sheet(name)
    by_pat = {}
    for i, p in tiles.items():
        if base <= i <= base + 15:
            by_pat[p] = i
    gh, gw = len(gridmap), len(gridmap[0])
    img = [[(0, 0, 0, 0)] * ((gw - 1) * T) for _ in range((gh - 1) * T)]
    for ty in range(gh - 1):
        for tx in range(gw - 1):
            pat = tuple(1 + int(gridmap[ty + a][tx + b]) for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)))
            i = by_pat[pat]
            blit(img, ts.tile(i), tx * T, ty * T)
    return img


BLOBS = [
    ['0000000', '0001100', '0011110', '0011110', '0001100', '0000000'],
    ['1111111', '1110011', '1100001', '1100011', '1110111', '1111111'],
    ['0000000', '0110000', '0111110', '0001110', '0000110', '0000000'],
]


def main():
    name = sys.argv[1]
    ts = sheet(name)
    S = 2
    panels = []
    for wname, base, tiles in terrain_blocks(name):
        row = []
        for b in BLOBS:
            row.append(blob_assembly(name, base, tiles, b))
        # grille 4x4
        g = [[(0, 0, 0, 0)] * (4 * T) for _ in range(4 * T)]
        for k in range(16):
            blit(g, ts.tile(base + k), (k % 4) * T, (k // 4) * T)
        row.append(g)
        panels.append(row)
    # assemble : une ligne par terrain
    margin = 6
    bgc = (40, 36, 48, 255)
    rows_h = [max(len(img) for img in row) for row in panels]
    width = max(sum(len(img[0]) + margin for img in row) for row in panels)
    canvas = [[bgc] * width for _ in range(sum(rows_h) + margin * len(rows_h))]
    y = margin
    for row, hh in zip(panels, rows_h):
        x = 0
        for img in row:
            blit(canvas, img, x, y)
            x += len(img[0]) + margin
        y += hh + margin
    # extraits de cartes
    args = sys.argv[2:]
    for k in range(0, len(args), 5):
        x0, y0, cw, ch = map(int, args[k:k + 4])
        mp = os.path.join(ROOT, 'maps', 'overworld', args[k + 4] + '.tmx')
        img = compose(mp, x0, y0, cw, ch)
        # agrandit la zone si besoin
        if len(img[0]) > len(canvas[0]):
            for r in canvas:
                r.extend([bgc] * (len(img[0]) - len(r)))
        canvas.extend([[bgc] * len(canvas[0]) for _ in range(margin)])
        oy = len(canvas)
        canvas.extend([[bgc] * len(canvas[0]) for _ in range(len(img))])
        blit(canvas, img, 0, oy)
    out = os.path.join(ROOT, 'art', 'tilesets', name + '_apercu_transitions.png')
    save_png(out, [[p if len(p) == 4 else p + (255,) for p in r] for r in canvas], 1)
    print(out, len(canvas[0]), len(canvas))


if __name__ == '__main__':
    main()
