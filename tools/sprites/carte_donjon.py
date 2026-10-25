"""Icônes de la carte du donjon (menu pause) — Les Trois Sceaux.

Usage : python tools/sprites/carte_donjon.py
Produit dans art/ui/carte/ (PNG RGBA, sans Pillow : mini encodeur zlib + struct) :
  cadre.png              360x250  fond parchemin sombre + bordure dorée (bords de 8 px : 9-slice, marges 8)
  salle_visitee.png      36x22    case pleine (parchemin clair)
  salle_inconnue.png     36x22    case en contour seul (salle pas encore visitée)
  icone_brann.png        8x8      marqueur de Brann (une image ; le code le fait clignoter)
  icone_boss.png         10x10    tête de cerf (Sylve) : salle du boss
  icone_escalier.png     12x12     escalier entre deux étages
  icone_chute.png        8x8      trou de passage vers l'étage du dessous
"""
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'art', 'ui', 'carte'))

HEX = {'0': '#1b1420', 'I': '#241a22', 'P': '#3a2a20', 'p': '#4a3426', 'q': '#2e2018',
       'K': '#c8a050', 'k': '#8a6a30', 'L': '#e8d090',
       'c': '#d6c49c', 'C': '#a6926c', 'h': '#f2e4c0',
       'o': '#8a7060',
       '1': '#7a4628', '7': '#b06e40', '3': '#f2c29a', '4': '#e2342c', 'F': '#961c28',
       'b': '#d8d4cc', 'g': '#9a948c', 'd': '#5c5650', 'S': '#382e42', 'R': '#4e4058',
       'v': '#6a2a7a', 'e': '#e2342c'}
DARK = {'1': 'I', '7': '1', '3': 'C', '4': 'F', 'F': 'q', '0': '0'}


def rgba(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def grid(rows):
    return [[None if ch == '.' else rgba(HEX[ch]) for ch in r] for r in rows]


def save_png(path, pix):
    h, w = len(pix), len(pix[0])
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw += bytes(pix[y][x] or (0, 0, 0, 0))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def frame():
    w, h = 360, 250
    g = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            if d == 0:
                c = '0'
            elif d in (1, 2, 3):
                c = 'K' if d == 1 else 'L' if d == 2 else 'k'
            elif d == 4:
                c = '0'
            elif d in (5, 6):
                c = 'q'
            elif d == 7:
                c = 'P'
            else:
                n = (x * 7 + y * 13 + (x * y) % 5) % 23
                c = 'p' if n == 0 else 'q' if n in (1, 2) and (x + y) % 3 == 0 else 'P'
            g[y][x] = rgba(HEX[c])
    for cx, cy in ((0, 0), (w - 8, 0), (0, h - 8), (w - 8, h - 8)):      # coins : rivets dorés
        for j in range(8):
            for i in range(8):
                edge = i in (0, 7) or j in (0, 7)
                g[cy + j][cx + i] = rgba(HEX['0' if edge else 'K'])
        g[cy + 2][cx + 2] = rgba(HEX['L'])
        g[cy + 3][cx + 3] = rgba(HEX['L'])
        g[cy + 5][cx + 5] = rgba(HEX['k'])
    for (x, y) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        g[y][x] = None
    return g


def room_full():
    w, h = 36, 22
    rows = []
    for y in range(h):
        r = ''
        for x in range(w):
            if x in (0, w - 1) or y in (0, h - 1):
                r += '0'
            elif x == 1 or y == 1:
                r += 'h'
            elif x == w - 2 or y == h - 2:
                r += 'C'
            else:
                r += 'c'
        rows.append(r)
    return grid(rows)


def room_unknown():
    w, h = 36, 22
    rows = []
    for y in range(h):
        r = ''
        for x in range(w):
            if x in (0, w - 1) or y in (0, h - 1):
                r += 'o'
            else:
                r += '.'
        rows.append(r)
    return grid(rows)


BRANN = ['..0000..',
         '.017710.',
         '01333310',
         '03033030',
         '.033330.',
         '04444440',
         '0F4444F0',
         '.000000.']


def darker(rows):
    return [''.join(DARK.get(ch, ch) for ch in r) for r in rows]


def boss():
    n = 10
    g = [['.'] * n for _ in range(n)]

    def s(x, y, c):
        if 0 <= x < n and 0 <= y < n:
            g[y][x] = c
    for (x, y) in ((3, 4), (3, 3), (2, 2), (1, 1), (1, 0), (2, 1), (0, 3), (0, 4)):       # bois gauche
        s(x, y, 'c')
        s(n - 1 - x, y, 'c')
    for y in range(3, 10):                                                                 # crâne
        hw = 3 if y < 7 else 2 if y < 9 else 1
        for x in range(5 - hw, 5 + hw):
            s(x, y, 'b')
    for y in range(3, 9):
        s(4, y, 'b')
        s(5, y, 'b')
    s(3, 5, 'e')
    s(6, 5, 'e')
    s(4, 8, 'd')
    s(5, 8, 'd')
    s(3, 3, 'c')
    s(6, 3, 'c')
    rows = [''.join(r) for r in g]
    img = grid(rows)
    for y in range(n):                       # contour sombre
        for x in range(n):
            if img[y][x] is None and any(0 <= x + dx < n and 0 <= y + dy < n and img[y + dy][x + dx] not in (None, rgba(HEX['0']))
                                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                img[y][x] = 'O'
    return [[rgba(HEX['0']) if c == 'O' else c for c in r] for r in img]


STAIRS = ['000000000000',
          '0SSSSSSSSSS0',
          '0bbbbbbbbbb0',
          '0gggggggggg0',
          '0SSbbbbbbbb0',
          '0SSggggggg00'[:11] + '0',
          '0SSSSbbbbbb0',
          '0SSSSggggg00'[:11] + '0',
          '0SSSSSSbbbb0',
          '0SSSSSSgggg0',
          '0SSSSSSSSSS0',
          '000000000000']

HOLE = ['..0000..',
        '.0bbbb0.',
        '0bIIIIb0',
        '0bI00Ib0',
        '0bI00Ib0',
        '0bIIIIb0',
        '.0gggg0.',
        '..0000..']


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, img in (('cadre', frame()), ('salle_visitee', room_full()), ('salle_inconnue', room_unknown()),
                      ('icone_brann', grid(BRANN)), ('icone_boss', boss()),
                      ('icone_escalier', grid(STAIRS)), ('icone_chute', grid(HOLE))):
        save_png(os.path.join(OUT, name + '.png'), img)
        print(name, len(img[0]), 'x', len(img))


if __name__ == '__main__':
    main()
