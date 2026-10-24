"""Coffres : coffre.png (petit, ferrures de fer) et grand_coffre.png (ferrures dorees + gemme).

Usage : python coffres.py [dossier_apercu]
Produit dans art/puzzles/ des planches horizontales de 2 cases 32x32 : 0 = ferme, 1 = ouvert.
Le coffre est pose en bas de la case. Sans Pillow : mini encodeur PNG (zlib + struct).
"""
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'art', 'puzzles')

PAL = {
    '.': None,
    '0': '#1b1420',  # contour
    'L': '#b06e40', 'M': '#8a5a34', 'D': '#5e3a22',   # bois : clair, moyen, sombre
    'g': '#d8d4cc', 'h': '#9a948c', 'k': '#5c5650',   # fer
    'y': '#f8d848', 'o': '#c89a28', 'p': '#8a5a1c',   # or : clair, moyen, sombre
    'I': '#241a22', 'J': '#3a2a30',                   # interieur sombre
    '4': '#e2342c', 'F': '#961c28', 'w': '#fff4d0',   # gemme rouge
}


def rgba(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def blank(w, h):
    return [['.'] * w for _ in range(h)]


def put(g, x, y, c):
    if 0 <= y < len(g) and 0 <= x < len(g[0]):
        g[y][x] = c


def rect(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(g, x, y, c)


def outline(g, color='0'):
    h, w = len(g), len(g[0])
    pts = [(x, y) for y in range(h) for x in range(w) if g[y][x] == '.'
           and any(0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] not in ('.', color)
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        g[y][x] = color


def to_rgba(g):
    return [[rgba(PAL[c]) if PAL[c] else (0, 0, 0, 0) for c in row] for row in g]


def sheet(frames):
    h, w = len(frames[0]), len(frames[0][0])
    out = [[(0, 0, 0, 0)] * (w * len(frames)) for _ in range(h)]
    for i, f in enumerate(frames):
        for y in range(h):
            for x in range(w):
                out[y][i * w + x] = f[y][x]
    return out


def background(px, color):
    return [[p if p[3] else color for p in row] for row in px]


def save_png(path, px, scale=1):
    h, w = len(px), len(px[0])
    raw = bytearray()
    for y in range(h):
        row = bytearray()
        for x in range(w):
            row += bytes(px[y][x]) * scale
        for _ in range(scale):
            raw.append(0)
            raw += row

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(data)


def chest(x0, x1, ytop, opened, metal, gem):
    """Dessine un coffre entre les colonnes x0..x1 ; le bas du corps est a y=28 (contour a y=29).
    metal = (clair, moyen, sombre) pour les ferrures. gem : ajoute une gemme sur la serrure."""
    g = blank(32, 32)
    mc, mm, md = metal
    bt, bb = 18, 28                                   # corps : haut et bas
    # corps (face avant)
    rect(g, x0, bt, x1, bb, 'M')
    rect(g, x0, bt, x1, bt, 'D')
    rect(g, x0, bb, x1, bb, 'D')
    rect(g, x0, bt + 1, x0, bb - 1, 'L')              # lumiere a gauche
    rect(g, x1, bt + 1, x1, bb - 1, 'D')
    rect(g, x0 + 1, 23, x1 - 1, 23, 'D')              # joint de planches
    bands = (x0 + 3, x1 - 4)
    if not opened:
        # couvercle : dessus
        top = ytop
        rect(g, x0 + 1, top, x1 - 1, bt - 1, 'M')
        rect(g, x0 + 2, top, x1 - 2, top, 'L')
        rect(g, x0 + 1, top + 1, x0 + 1, bt - 1, 'L')
        rect(g, x1 - 1, top + 1, x1 - 1, bt - 1, 'D')
        rect(g, x0 + 3, top + 3, x1 - 3, top + 3, 'L')
        rect(g, x0, bt - 1, x1, bt - 1, 'D')
        put(g, x0, bt - 1, 'D')
    else:
        # dessous du couvercle releve (derriere), puis interieur sombre
        top = ytop - 6
        rect(g, x0 + 1, top, x1 - 1, top + 5, 'D')
        rect(g, x0 + 2, top + 1, x1 - 2, top + 4, 'M')
        rect(g, x0 + 2, top + 1, x1 - 2, top + 1, 'L')
        rect(g, x0 + 2, top + 5, x1 - 2, top + 5, 'D')
        rect(g, x0, top + 6, x1, bt - 1, 'D')         # bord du coffre
        rect(g, x0 + 2, top + 7, x1 - 2, bt - 1, 'I')  # interieur
        rect(g, x0 + 2, top + 7, x1 - 2, top + 7, 'J')
        rect(g, x0 + 3, bt - 3, x1 - 3, bt - 2, 'J')   # fond visible plus clair
    # ferrures verticales
    ytop_band = top if not opened else top + 1
    for bx in bands:
        if not opened:
            rect(g, bx, top, bx + 1, bt - 1, mm)
            rect(g, bx, top, bx, bt - 1, mc)
        else:
            rect(g, bx, top + 1, bx + 1, top + 5, mm)
            rect(g, bx, top + 1, bx, top + 5, mc)
        rect(g, bx, bt, bx + 1, bb - 1, mm)
        rect(g, bx, bt, bx, bb - 1, mc)
        rect(g, bx + 1, bt + 1, bx + 1, bb - 1, md)
        put(g, bx, 20, md)                            # rivets
        put(g, bx, 26, md)
    # serrure
    cx = (x0 + x1) // 2
    ly = bt - 1 if not opened else bt
    rect(g, cx - 2, ly, cx + 2, ly + 5, mm)
    rect(g, cx - 2, ly, cx + 2, ly, mc)
    rect(g, cx - 2, ly + 5, cx + 2, ly + 5, md)
    rect(g, cx - 2, ly + 1, cx - 2, ly + 4, mc)
    if gem:
        rect(g, cx - 1, ly + 1, cx + 1, ly + 4, 'F')
        rect(g, cx - 1, ly + 1, cx, ly + 2, '4')
        put(g, cx - 1, ly + 1, 'w')
    else:
        put(g, cx, ly + 2, 'I')
        put(g, cx, ly + 3, 'I')
    # coins arrondis
    for (x, y) in ((x0, bb), (x1, bb)):
        put(g, x, y, '.')
    outline(g)
    return g


def small():
    m = ('g', 'h', 'k')
    return [chest(5, 26, 11, False, m, False), chest(5, 26, 11, True, m, False)]


def big():
    m = ('y', 'o', 'p')
    f = [chest(3, 28, 9, False, m, True), chest(3, 28, 9, True, m, True)]
    # motif dore sur le couvercle ferme : liseré
    g = f[0]
    for x in range(8, 24):
        if g[10][x] in 'LM':
            g[10][x] = 'o'
    return f


def main():
    os.makedirs(OUT, exist_ok=True)
    a, b = sheet([to_rgba(f) for f in small()]), sheet([to_rgba(f) for f in big()])
    save_png(os.path.join(OUT, 'coffre.png'), a)
    save_png(os.path.join(OUT, 'grand_coffre.png'), b)
    if len(sys.argv) > 1:
        d = sys.argv[1]
        os.makedirs(d, exist_ok=True)
        for nom, px in (('coffre', a), ('grand_coffre', b)):
            save_png(os.path.join(d, 'apercu_%s_herbe.png' % nom), background(px, (70, 110, 60, 255)), 8)
            save_png(os.path.join(d, 'apercu_%s_donjon.png' % nom), background(px, (110, 110, 120, 255)), 8)


if __name__ == '__main__':
    main()
