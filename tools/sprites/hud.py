"""Elements du HUD : coeurs, icones rubis/cle, cadre d'objet, chiffres. Palette commune (engine.PALETTE).

Usage : python hud.py [apercu.png]  ->  art/ui/*.png  (+ maquette x4 optionnelle)
Pillow absent : encodeur PNG maison (zlib + struct). Le moteur n'est utilise que pour sa palette.
"""
import os
import struct
import sys
import types
import zlib

try:
    import PIL  # noqa: F401
except ImportError:
    _m = types.ModuleType('PIL')
    _m.Image = types.ModuleType('PIL.Image')
    sys.modules['PIL'] = _m
    sys.modules['PIL.Image'] = _m.Image

from engine import PALETTE, rgba  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'art', 'ui')


def save_png(path, g, scale=1):
    """g = liste de lignes de pixels RGBA (tuple ou None)."""
    h, w = len(g), len(g[0])
    raw = bytearray()
    for y in range(h * scale):
        raw.append(0)
        for x in range(w * scale):
            raw += bytes(g[y // scale][x // scale] or (0, 0, 0, 0))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n'
                + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def blank(w, h):
    return [['.'] * w for _ in range(h)]


def put(g, rows, x0, y0):
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c != '.':
                g[y0 + j][x0 + i] = c
    return g


def to_rgba(g):
    return [[(rgba(PALETTE[c]) if PALETTE.get(c) else None) for c in row] for row in g]


# --- Coeur : moitie gauche, 7 colonnes x 12 lignes (14 de large une fois en miroir) ---
HALF = ["..000..", ".0gg440", "0gg4444", "0g44444", "0444444", "0444444",
        ".044444", "..04444", "...0444", "....044", ".....04", "......0"]
FULL = {}
# vide : contour gris sombre, interieur violet-gris desature
EMPTY = {'0': 'k', '4': 'J', 'F': 'I', 'g': '5'}


def heart_rows(left_style, right_style):
    out = []
    for r in HALF:
        left = list(r)
        right = list(r[::-1].replace('g', '4'))
        for i in range(6, 0, -1):            # ombre cote droit
            if right[i] == '0' and right[i - 1] == '4':
                right[i - 1] = 'F'
        left = [left_style.get(c, c) for c in left]
        right = [right_style.get(c, c) for c in right]
        out.append(''.join(left + right))
    return out


def heart(kind):
    ls = FULL if kind in ('plein', 'moitie') else EMPTY
    rs = FULL if kind == 'plein' else EMPTY
    return put(blank(16, 16), heart_rows(ls, rs), 1, 2)


# --- Rubis (meme dessin que pickups.py, rubis_vert image 1) ---
GEM = ["...00000000...", "..0ggggvvvvw0.", ".0ggvwvvvvwvw0", "0gvvwvvvvwvvw0",
       "0vvvvvvvvvvvw0", ".0vvvwvvwvvw0.", "..0vvwvvwvw0..", "...0vwvvwv0...",
       "....0vwwv0....", ".....0vv0.....", "......00......"]


def ruby():
    rows = [list(r) for r in GEM]
    rows[3][2] = rows[4][1] = rows[2][4] = rows[5][2] = 'g'
    return put(blank(16, 16), [''.join(r) for r in rows], 1, 2)


# --- Cle de donjon : anneau en haut, tige, dents ---
KEY = ["..0000..", ".02KKK0.", "02K00K60", "0K0..060", "02K00K60", ".0K66K0.", "..0K60..",
       "..0K60..", "..0K600.", "..0K6K60", "..0K600.", "..0K6K60", "..0K660.", "...000.."]


def key():
    return put(blank(16, 16), KEY, 4, 1)


# --- Cadre d'objet 32x32 ---
def frame():
    n = 32
    g = blank(n, n)
    for y in range(n):
        for x in range(n):
            d = min(x, y, n - 1 - x, n - 1 - y)
            g[y][x] = '0' if d in (0, 3) else '6' if d in (1, 2) else 'I'
    for x in range(1, n - 1):               # biseau : haut/gauche clair, bas/droite sombre
        g[1][x] = '9'
        g[n - 2][x] = 'B'
    for y in range(1, n - 1):
        g[y][1] = '9'
        g[y][n - 2] = 'B'
    for cx, cy in ((0, 0), (n - 6, 0), (0, n - 6), (n - 6, n - 6)):   # plaques d'angle dorees
        for j in range(6):
            for i in range(6):
                edge = i in (0, 5) or j in (0, 5)
                g[cy + j][cx + i] = '0' if edge else 'K'
        g[cy + 1][cx + 1] = '2'
        g[cy + 4][cx + 4] = '6'
        g[0 if cy == 0 else n - 1][0 if cx == 0 else n - 1] = '.'     # coin arrondi
    return g


# --- Chiffres 8x8 : glyphe 5x6 clair + contour sombre ---
DIGITS = [
    [".###.", "#...#", "#...#", "#...#", "#...#", ".###."],
    ["..#..", ".##..", "..#..", "..#..", "..#..", ".###."],
    [".###.", "#...#", "...#.", "..#..", ".#...", "#####"],
    ["####.", "....#", ".###.", "....#", "#...#", ".###."],
    ["..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    ["#####", "#....", "####.", "....#", "#...#", ".###."],
    [".###.", "#....", "####.", "#...#", "#...#", ".###."],
    ["#####", "....#", "...#.", "..#..", ".#...", ".#..."],
    [".###.", "#...#", ".###.", "#...#", "#...#", ".###."],
    [".###.", "#...#", "#...#", ".####", "....#", ".###."],
]


def digit(d):
    g = blank(8, 8)
    on = {(i + 1, j + 1) for j, r in enumerate(DIGITS[d]) for i, c in enumerate(r) if c == '#'}
    for (x, y) in on:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= x + dx < 8 and 0 <= y + dy < 8:
                    g[y + dy][x + dx] = '0'
    for (x, y) in on:
        g[y][x] = 'g'
    return g


def digits_strip():
    g = blank(80, 8)
    for d in range(10):
        put(g, [''.join(r) for r in digit(d)], d * 8, 0)
    return g


def blit(dst, src, x0, y0):
    for y, row in enumerate(src):
        for x, p in enumerate(row):
            if p and 0 <= y0 + y < len(dst) and 0 <= x0 + x < len(dst[0]):
                dst[y0 + y][x0 + x] = p


def preview(path):
    W, H = 128, 56
    bg = [[rgba('#5a8a3c') if (x // 8 + y // 8) % 2 else rgba('#6a9a48') for x in range(W)] for y in range(H)]
    for i, k in enumerate(['plein'] * 3 + ['moitie', 'vide', 'vide']):
        blit(bg, to_rgba(heart(k)), 4 + i * 14, 3)
    blit(bg, to_rgba(frame()), 92, 4)
    blit(bg, to_rgba(ruby()), 4, 24)
    for i, c in enumerate('042'):
        blit(bg, to_rgba(digit(int(c))), 22 + i * 7, 28)
    blit(bg, to_rgba(key()), 4, 40)
    blit(bg, to_rgba(digit(3)), 22, 44)
    save_png(path, bg, 4)


def sheet_x8(path):
    items = [heart('plein'), heart('moitie'), heart('vide'), ruby(), key(), frame(), digits_strip()]
    W = sum(len(i[0]) + 2 for i in items) + 1
    sh = [[rgba('#6a9a48')] * W for _ in range(34)]
    x = 1
    for g in items:
        blit(sh, to_rgba(g), x, 1)
        x += len(g[0]) + 2
    save_png(path, sh, 8)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k in ('plein', 'moitie', 'vide'):
        save_png(os.path.join(OUT, f'coeur_{k}.png'), to_rgba(heart(k)))
    save_png(os.path.join(OUT, 'icone_rubis.png'), to_rgba(ruby()))
    save_png(os.path.join(OUT, 'icone_cle.png'), to_rgba(key()))
    save_png(os.path.join(OUT, 'cadre_objet.png'), to_rgba(frame()))
    save_png(os.path.join(OUT, 'chiffres.png'), to_rgba(digits_strip()))
    if len(sys.argv) > 1:
        preview(sys.argv[1])
    if len(sys.argv) > 2:
        sheet_x8(sys.argv[2])
    print('ok')
