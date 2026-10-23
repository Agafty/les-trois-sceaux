"""Butin lache par les ennemis : rubis (vert/bleu/rouge) et coeur. Meme moteur/palette que les ennemis.

Usage : python pickups.py   ->  art/items/pickups.png / .json / _frames.tres
Planche de cases 32x32, une ligne par animation : rubis_vert, rubis_bleu, rubis_rouge, coeur
(objet petit et centre, bas de case = sol).
Si Pillow est absent, un mini encodeur PNG (zlib + struct) le remplace.
"""
import os
import struct
import sys
import types
import zlib

try:
    import PIL  # noqa: F401
except ImportError:
    class _Img:
        def __init__(self, size):
            self.size = size
            self.w, self.h = size
            self.data = {}

        def load(self):
            return self

        def __setitem__(self, k, v):
            self.data[k] = v

        def save(self, path):
            raw = bytearray()
            for y in range(self.h):
                raw.append(0)
                for x in range(self.w):
                    raw += bytes(self.data.get((x, y), (0, 0, 0, 0)))

            def chunk(t, d):
                c = struct.pack('>I', len(d)) + t + d
                return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
            png = (b'\x89PNG\r\n\x1a\n'
                   + chunk(b'IHDR', struct.pack('>IIBBBBB', self.w, self.h, 8, 6, 0, 0, 0))
                   + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
            with open(path, 'wb') as f:
                f.write(png)
    _m = types.ModuleType('PIL')
    _i = types.ModuleType('PIL.Image')
    _i.new = lambda mode, size, color=None: _Img(size)
    _i.NEAREST = 0
    _m.Image = _i
    sys.modules['PIL'] = _m
    sys.modules['PIL.Image'] = _i

from enemy_lib import build_enemy  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'art', 'items')

# Rubis taille en diamant 14x11 : v = teinte, w = teinte sombre, g = reflet clair (haut gauche)
GEM = ["...00000000...", "..0ggggvvvvw0.", ".0ggvwvvvvwvw0", "0gvvwvvvvwvvw0",
       "0vvvvvvvvvvvw0", ".0vvvwvvwvvw0.", "..0vvwvvwvw0..", "...0vwvvwv0...",
       "....0vwwv0....", ".....0vv0.....", "......00......"]
assert all(len(r) == 14 for r in GEM), [len(r) for r in GEM]
# Moitie gauche du coeur (12 de large une fois mise en miroir)
HEART_HALF = ["..000.", ".0gg40", "0g4444", "044444", "044444", "044444", ".04444", "..0444",
              "...044", "....04", ".....0"]


def blank():
    return [['.'] * 32 for _ in range(32)]


def put(g, rows, x0, bottom=31):
    y0 = bottom - len(rows) + 1
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c != '.':
                g[y0 + j][x0 + i] = c
    return g


def gem(base, dark, frame):
    rows = [list(r.replace('v', base).replace('w', dark)) for r in GEM]
    if frame == 1:      # eclat : reflet agrandi + etoile
        rows[3][2] = rows[4][1] = rows[2][4] = rows[5][2] = 'g'
    if frame == 2:      # terne : reflet eteint
        rows = [[base if c == 'g' else c for c in r] for r in rows]
    g = put(blank(), [''.join(r) for r in rows], 9)
    if frame == 1:
        for x, y in ((24, 21), (23, 22), (25, 22), (24, 23)):
            g[y][x] = 'g'
    if frame == 2:
        g[25][7] = 'g'
    return g


def heart(frame):
    rows = []
    for r in HEART_HALF:
        r = list(r + r[::-1].replace('g', '4'))
        for i in range(11, 0, -1):          # ombre cote droit
            if r[i] == '0' and r[i - 1] == '4':
                r[i - 1] = 'F'
        rows.append(''.join(r))
    if frame == 1:                          # battement : le coeur gonfle d'une ligne
        rows.insert(4, rows[4])
    return put(blank(), rows, 10)


def gem3(base, dark):
    return [gem(base, dark, f) for f in (0, 1, 2)]


anims = [('rubis_vert', gem3('v', 'w'), 6.0, True),
         ('rubis_bleu', gem3('b', 'n'), 6.0, True),
         ('rubis_rouge', gem3('4', 'F'), 6.0, True),
         ('coeur', [heart(0), heart(1)], 3.0, True)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    build_enemy(OUT, 'pickups', anims, folder='items')
    print('ok')
