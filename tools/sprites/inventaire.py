"""Inventaire : police bitmap, icones d'objets 24x24, curseur, panneau 9-patch. Palette commune (engine.PALETTE).

Usage : python inventaire.py [apercu.png]  ->  art/ui/police.png, police_caracteres.txt,
        art/ui/items/{arc,bombes,lanterne}.png, curseur_inventaire.png, panneau.png
Police : cases 8x10, 16 colonnes, glyphes 'g' sans contour, calés à gauche. Capitales sur les lignes 2..8,
minuscules (hauteur 5) sur 4..8, jambages ligne 9, accents lignes 2-3 (minuscules) ou 0-1 (capitales).
"""
import os
import sys

from hud import OUT, blank, blit, save_png, to_rgba, frame
from engine import rgba

CHARS = ''.join(chr(c) for c in range(32, 127)) + "àâäçéèêëîïôöùûüÿœæÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ«»’…"

# ---- glyphes : "lignes/..|jambages". 7 lignes = capitales (lignes 2..8), 5 lignes = minuscules (4..8) ----
G = {
    ' ': '..', '!': '#/#/#/#/#/./#', '"': '#.#/#.#/././././.', '#': '.#.#./#####/.#.#./.#.#./.#.#./#####/.#.#.',
    '$': '..#../.####/#.#../.###./..#.#/####./..#..', '%': '##..#/##..#/...#./..#../.#.../#..##/#..##',
    '&': '.##../#..#./#.#../.#.../#.#.#/#..#./.##.#', "'": '#/#/././././.',
    '(': '..#/.#./#../#../#../.#./..#', ')': '#../.#./..#/..#/..#/.#./#..',
    '*': '...../#.#.#/.###./#.#.#/.....', '+': '...../..#../#####/..#../.....', ',': '../../../.#/.#|#.',
    '-': '...../...../###../...../.....', '.': '/././././#', '/': '...#/...#/..#./..#./.#../.#../#...',
    ':': '/#//#/', ';': '/#//#/#|#',
    '<': '..#/.#./#../.#./..#', '=': '...../#####/...../#####/.....', '>': '#../.#./..#/.#./#..',
    '?': '.###./#...#/....#/...#./..#../...../..#..',
    '@': '.###./#...#/#.###/#.#.#/#.###/#..../.###.',
    '[': '###/#../#../#../#../#../###', '\\': '#.../#.../.#../.#../..#./..#./...#',
    ']': '###/..#/..#/..#/..#/..#/###', '^': '.#./#.#/././././.', '_': '.....|#####', '`': '#./.#/././././.',
    '{': '.##/.#./.#./#../.#./.#./.##', '|': '#/#/#/#/#/#/#|#', '}': '##./.#./.#./..#/.#./.#./##.',
    '~': '...../.##.#/#.##./...../.....',
    '0': '.###./#...#/#..##/#.#.#/##..#/#...#/.###.', '1': '..#../.##../..#../..#../..#../..#../.###.',
    '2': '.###./#...#/....#/...#./..#../.#.../#####', '3': '####./....#/....#/.###./....#/#...#/.###.',
    '4': '...#./..##./.#.#./#..#./#####/...#./...#.', '5': '#####/#..../####./....#/....#/#...#/.###.',
    '6': '.###./#..../#..../####./#...#/#...#/.###.', '7': '#####/....#/...#./..#../.#.../.#.../.#...',
    '8': '.###./#...#/#...#/.###./#...#/#...#/.###.', '9': '.###./#...#/#...#/.####/....#/....#/.###.',
    'A': '.###./#...#/#...#/#####/#...#/#...#/#...#', 'B': '####./#...#/#...#/####./#...#/#...#/####.',
    'C': '.###./#...#/#..../#..../#..../#...#/.###.', 'D': '####./#...#/#...#/#...#/#...#/#...#/####.',
    'E': '#####/#..../#..../####./#..../#..../#####', 'F': '#####/#..../#..../####./#..../#..../#....',
    'G': '.###./#...#/#..../#.###/#...#/#...#/.###.', 'H': '#...#/#...#/#...#/#####/#...#/#...#/#...#',
    'I': '###/.#./.#./.#./.#./.#./###', 'J': '....#/....#/....#/....#/#...#/#...#/.###.',
    'K': '#...#/#..#./#.#../##.../#.#../#..#./#...#', 'L': '#..../#..../#..../#..../#..../#..../#####',
    'M': '#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#', 'N': '#...#/##..#/#.#.#/#..##/#...#/#...#/#...#',
    'O': '.###./#...#/#...#/#...#/#...#/#...#/.###.', 'P': '####./#...#/#...#/####./#..../#..../#....',
    'Q': '.###./#...#/#...#/#...#/#.#.#/#..#./.##.#', 'R': '####./#...#/#...#/####./#.#../#..#./#...#',
    'S': '.####/#..../#..../.###./....#/....#/####.', 'T': '#####/..#../..#../..#../..#../..#../..#..',
    'U': '#...#/#...#/#...#/#...#/#...#/#...#/.###.', 'V': '#...#/#...#/#...#/#...#/#...#/.#.#./..#..',
    'W': '#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#', 'X': '#...#/#...#/.#.#./..#../.#.#./#...#/#...#',
    'Y': '#...#/#...#/.#.#./..#../..#../..#../..#..', 'Z': '#####/....#/...#./..#../.#.../#..../#####',
    'a': '.###./....#/.####/#...#/.####', 'b': '#..../#..../####./#...#/#...#/#...#/####.',
    'c': '.###/#.../#.../#.../.###', 'd': '....#/....#/.####/#...#/#...#/#...#/.####',
    'e': '.###./#...#/#####/#..../.####', 'f': '..##/.#../###./.#../.#../.#../.#..',
    'g': '.####/#...#/#...#/.####/....#|.###.', 'h': '#..../#..../####./#...#/#...#/#...#/#...#',
    'i': '.#./.../##./.#./.#./.#./###', 'j': '..#/.../..#/..#/..#/..#/..#|##.',
    'k': '#..../#..../#..#./#.#../##.../#.#../#..#.', 'l': '##./.#./.#./.#./.#./.#./.##',
    'm': '##.#./#.#.#/#.#.#/#.#.#/#.#.#', 'n': '####./#...#/#...#/#...#/#...#',
    'o': '.###./#...#/#...#/#...#/.###.', 'p': '####./#...#/#...#/#...#/####.|#....',
    'q': '.####/#...#/#...#/#...#/.####|....#', 'r': '#.##/##../#.../#.../#...',
    's': '.####/#..../.###./....#/####.', 't': '.#../###./.#../.#../.#../..##',
    'u': '#...#/#...#/#...#/#...#/.####', 'v': '#...#/#...#/#...#/.#.#./..#..',
    'w': '#...#/#...#/#.#.#/#.#.#/.#.#.', 'x': '#...#/.#.#./..#../.#.#./#...#',
    'y': '#...#/#...#/#...#/.####/....#|.###.', 'z': '#####/...#./..#../.#.../#####',
    # --- hors ASCII ---
    'œ': '.##.##./#..#..#/#..###./#..#.../.##.###', 'æ': '.##.##./...#..#/.#####./#..#.../.######',
    'Œ': '.######/#..#.../#..#.../#..####/#..#.../#..#.../.######',
    'Æ': '..#####/.#.#.../.#.#.../#..####/####.../#..#.../#..####',
    '«': '..#.#/.#.#./#.#../.#.#./..#.#', '»': '#.#../.#.#./..#.#/.#.#./#.#..',
    '’': '##/.#/#./././././.', '…': '/././././#.#.#',
    'ı': '##./.#./.#./.#./###',   # i sans point (interne, pour les accents)
}

ACC = {5: {'a': ['...#.', '..#..'], 'g': ['.#...', '..#..'], 'c': ['..#..', '.#.#.'], 'd': ['', '.#.#.']},
       3: {'a': ['..#', '.#.'], 'g': ['#..', '.#.'], 'c': ['.#.', '#.#'], 'd': ['', '#.#']}}
LOW = {'à': ('a', 'g'), 'â': ('a', 'c'), 'ä': ('a', 'd'), 'é': ('e', 'a'), 'è': ('e', 'g'), 'ê': ('e', 'c'),
       'ë': ('e', 'd'), 'î': ('ı', 'c'), 'ï': ('ı', 'd'), 'ô': ('o', 'c'), 'ö': ('o', 'd'), 'ù': ('u', 'g'),
       'û': ('u', 'c'), 'ü': ('u', 'd'), 'ÿ': ('y', 'd')}
UP = {'À': ('A', 'g'), 'Â': ('A', 'c'), 'Ä': ('A', 'd'), 'É': ('E', 'a'), 'È': ('E', 'g'), 'Ê': ('E', 'c'),
      'Ë': ('E', 'd'), 'Î': ('I', 'c'), 'Ï': ('I', 'd'), 'Ô': ('O', 'c'), 'Ö': ('O', 'd'), 'Ù': ('U', 'g'),
      'Û': ('U', 'c'), 'Ü': ('U', 'd'), 'Ÿ': ('Y', 'd')}


def glyph_rows(ch):
    """Retourne 10 lignes (str) absolues pour un caractere ('#' = pixel allume)."""
    arr = [''] * 10

    def base(spec):
        main, _, desc = spec.partition('|')
        rows = main.split('/')
        rows = [''] * (7 - len(rows)) + rows
        for i, r in enumerate(rows):
            arr[2 + i] = r
        for i, r in enumerate(desc.split('/') if desc else []):
            arr[9 + i] = r
    if ch in LOW or ch in UP:
        b, a = LOW.get(ch) or UP[ch]
        base(G[b])
        w = 3 if b in ('ı', 'I') else 5
        r0 = 0 if ch in UP else 2
        for i, r in enumerate(ACC[w][a]):
            arr[r0 + i] = r
    elif ch in ('ç', 'Ç'):
        base(G['c' if ch == 'ç' else 'C'])
        arr[9] = '.#..' if ch == 'ç' else '..#..'
    else:
        base(G[ch])
    return arr


def glyph_width(ch):
    w = max(r.rfind('#') + 1 for r in glyph_rows(ch))
    return w if w else 2


def font_sheet():
    cols = 16
    nrows = -(-len(CHARS) // cols)
    g = [[None] * (cols * 8) for _ in range(nrows * 10)]
    for n, ch in enumerate(CHARS):
        cx, cy = (n % cols) * 8, (n // cols) * 10
        for y, r in enumerate(glyph_rows(ch)):
            for x, c in enumerate(r):
                if c == '#':
                    g[cy + y][cx + x] = rgba('#d8d4cc')
    return g


# ---------------------------- icones ----------------------------
def outline(g):
    h, w = len(g), len(g[0])
    pts = []
    for y in range(h):
        for x in range(w):
            if g[y][x] == '.':
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if 0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] not in ('.', '0'):
                        pts.append((x, y))
                        break
    for x, y in pts:
        g[y][x] = '0'


def shade(g, mat):
    """mat = {couleur: (clair, sombre)} : clair si voisin haut/gauche vide, sombre si bas/droite vide."""
    h, w = len(g), len(g[0])
    src = [r[:] for r in g]

    def empty(x, y):
        return not (0 <= x < w and 0 <= y < h) or src[y][x] == '.'
    for y in range(h):
        for x in range(w):
            c = src[y][x]
            if c in mat:
                if empty(x - 1, y) or empty(x, y - 1):
                    g[y][x] = mat[c][0]
                elif empty(x + 1, y) or empty(x, y + 1):
                    g[y][x] = mat[c][1]


def line(g, x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        g[round(y0 + (y1 - y0) * i / n)][round(x0 + (x1 - x0) * i / n)] = c


def bow():
    g = blank(24, 24)
    p0, p1, p2 = (20, 3), (0, 0), (3, 20)
    for i in range(61):
        t = i / 60
        x = (1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * p1[1] + t * t * p2[1]
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            g[round(y) + dy][round(x) + dx] = '1'
    shade(g, {'1': ('7', '8')})
    for (x, y) in ((6, 9), (7, 8), (8, 7), (9, 6), (6, 10), (7, 9), (8, 8), (9, 7), (10, 6), (5, 10), (10, 5)):
        if g[y][x] != '.':
            g[y][x] = 'A'          # poignee en cuir au milieu de l'arc
    line(g, 20, 4, 4, 20, '2')     # corde
    outline(g)
    return g


def bomb():
    g = blank(24, 24)
    cx, cy, r = 11.5, 14.5, 8.2
    for y in range(24):
        for x in range(24):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                d = (x - cx + 2) ** 2 + (y - cy + 2) ** 2
                g[y][x] = 'b' if d < 20 else 'n' if d < 105 else 'I'
    for x, y in ((6, 11), (7, 10), (7, 11), (8, 9), (6, 12)):
        g[y][x] = 'g'
    for y in (5, 6):
        for x in range(9, 14):
            g[y][x] = 'k'
    for x in range(9, 14):
        g[5][x] = 'h'
    g[6][13] = 'J'
    for x, y in ((12, 4), (12, 3), (13, 3), (14, 2), (15, 2), (16, 1)):
        g[y][x] = '2'
    for x, y in ((16, 0), (18, 1), (17, 2), (15, 1)):
        g[y][x] = '4'
    g[0][18] = g[2][15] = 'K'
    g[1][17] = 'g'
    outline(g)
    return g


def lantern():
    g = blank(24, 24)
    for x in range(9, 15):
        g[1][x] = 'k'
    for y in (2, 3):
        g[y][8] = g[y][15] = 'k'
    for x in range(9, 15):
        g[4][x] = 'k'
    for x in range(6, 18):
        g[5][x] = 'h'
        g[6][x] = 'k'
    for y in range(7, 18):
        for x in range(5, 19):
            g[y][x] = 'I'
        g[y][5] = g[y][18] = 'k'
        g[y][6] = 'h'
        g[y][17] = 'J'
    for x in range(5, 19):
        g[7][x] = g[17][x] = 'k'
    flame = {9: [11], 10: [11, 12], 11: [10, 11, 12, 13], 12: [10, 11, 12, 13], 13: [9, 10, 11, 12, 13, 14],
             14: [9, 10, 11, 12, 13, 14], 15: [10, 11, 12, 13], 16: [11, 12]}
    for y, xs in flame.items():
        for x in xs:
            g[y][x] = 'K'
    for y in range(11, 16):
        g[y][11] = g[y][12] = '2'
    g[9][11] = g[10][11] = '4'
    for x in range(4, 20):
        g[18][x] = 'h'
        g[19][x] = 'k'
    for x in range(6, 18):
        g[20][x] = 'J'
    outline(g)
    return g


# ---------------------------- curseur et panneau ----------------------------
def cursor():
    n = 32
    g = blank(n, n)
    for i in range(1, n - 1):                      # filet fin de liaison
        for (x, y) in ((i, 0), (i, n - 1), (0, i), (n - 1, i)):
            g[y][x] = '6'
    L = 8
    for cx in (0, n - L):
        for cy in (0, n - L):
            for j in range(L):
                for i in range(L):
                    ex = (i < 2) if cx == 0 else (i >= L - 2)
                    ey = (j < 2) if cy == 0 else (j >= L - 2)
                    if ex or ey:
                        g[cy + j][cx + i] = 'K'
    for cx in (0, n - 2):                          # reflets aux angles
        for cy in (0, n - 2):
            g[cy][cx] = '2'
    return g


def panel():
    n = 24
    g = blank(n, n)
    for y in range(n):
        for x in range(n):
            d = min(x, y, n - 1 - x, n - 1 - y)
            g[y][x] = '0' if d in (0, 3) else '6' if d in (1, 2) else 'I'
    for x in range(1, n - 1):
        g[1][x], g[n - 2][x] = '9', 'B'
    for y in range(1, n - 1):
        g[y][1], g[y][n - 2] = '9', 'B'
    for cx, cy in ((0, 0), (n - 6, 0), (0, n - 6), (n - 6, n - 6)):
        for j in range(6):
            for i in range(6):
                g[cy + j][cx + i] = '0' if (i in (0, 5) or j in (0, 5)) else 'K'
        g[cy + 1][cx + 1] = '2'
        g[cy + 4][cx + 4] = '6'
        g[0 if cy == 0 else n - 1][0 if cx == 0 else n - 1] = '.'
    return g


# ---------------------------- apercu ----------------------------
def draw_text(dst, s, x, y):
    s = s.replace('—', '-')       # le tiret cadratin n'est pas dans la police
    for ch in s:
        rows = glyph_rows(ch)
        for (ox, oy), col in (((1, 1), rgba('#1b1420')), ((0, 0), rgba('#d8d4cc'))):
            for j, r in enumerate(rows):
                for i, c in enumerate(r):
                    if c == '#' and 0 <= y + j + oy < len(dst) and 0 <= x + i + ox < len(dst[0]):
                        dst[y + j + oy][x + i + ox] = col
        x += 3 if ch == ' ' else glyph_width(ch) + 1


def nine_patch(w, h):
    src = to_rgba(panel())
    out = [[None] * w for _ in range(h)]
    for y in range(h):
        sy = y if y < 8 else 24 - (h - y) if y >= h - 8 else 8
        for x in range(w):
            sx = x if x < 8 else 24 - (w - x) if x >= w - 8 else 8
            out[y][x] = src[sy][sx]
    return out


def preview(path):
    W, H = 300, 112
    bg = nine_patch(W, H)
    draw_text(bg, "Arc — Bombes — Lanterne, éclipse à Brumeval ! 0123", 10, 10)
    draw_text(bg, "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz", 10, 24)
    draw_text(bg, "ÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ «àâäçéèêëîïôöùûüÿœæ» l’arc… (1/2)", 10, 38)
    for i, ic in enumerate((bow(), bomb(), lantern())):
        blit(bg, to_rgba(frame()), 20 + i * 40, 62)
        blit(bg, to_rgba(ic), 24 + i * 40, 66)
    blit(bg, to_rgba(cursor()), 60, 62)
    save_png(path, bg, 4)


if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'items'), exist_ok=True)
    save_png(os.path.join(OUT, 'police.png'), font_sheet())
    with open(os.path.join(OUT, 'police_caracteres.txt'), 'w', encoding='utf-8', newline='') as f:
        f.write(CHARS)
    save_png(os.path.join(OUT, 'items', 'arc.png'), to_rgba(bow()))
    save_png(os.path.join(OUT, 'items', 'bombes.png'), to_rgba(bomb()))
    save_png(os.path.join(OUT, 'items', 'lanterne.png'), to_rgba(lantern()))
    save_png(os.path.join(OUT, 'curseur_inventaire.png'), to_rgba(cursor()))
    save_png(os.path.join(OUT, 'panneau.png'), to_rgba(panel()))
    if len(sys.argv) > 1:
        preview(sys.argv[1])
    print('ok', len(CHARS), 'caracteres')
