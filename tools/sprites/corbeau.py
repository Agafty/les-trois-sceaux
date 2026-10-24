"""Corbeau : statue_corbeau.png (art/puzzles), icone_sauvegarde.png et logo.png (art/ui).

Usage : python corbeau.py [dossier_apercu]
- statue_corbeau.png : 2 cases 32x64 (0 = normale, 1 = active : yeux, gemme et halo).
  Ancrage conseille : bas-centre de la case (16, 63).
- icone_sauvegarde.png : 2 cases 16x16 (0 = ailes hautes, 1 = ailes basses).
- logo.png : 128x128, corbeau et trois cercles (foret, montagne, lac).
Sans Pillow : mini encodeur PNG reutilise depuis coffres.py.
"""
import math
import os
import sys

from coffres import blank, put, rect, outline, sheet, background, save_png

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', 'art')

PAL = {
    '.': None,
    '0': '#1b1420',                                   # contour (commun au jeu)
    # pierre grise legerement bleutee
    's': '#cfd0d6', 'S': '#9a9eaa', 'T': '#686c7e', 'U': '#464a5c',
    'm': '#6a8a52', 'n': '#4a6a40',                   # mousse
    # lueur de la statue active
    'w': '#f4ffff', 'c': '#8fe8ff', 'C': '#3aa0dc', 'B': '#2a60a8',
    'h': '#8fe8ff60',                                 # halo (semi-transparent voulu)
    # plumes du corbeau
    'a': '#2c2536', 'b': '#463c58', 'd': '#6c5f84', 'e': '#e8e4f0',
    'o': '#d8a030', 'p': '#8a5a1c',                   # bec
    # sceaux : foret, montagne, lac (clair, moyen, sombre)
    'G': '#5ab45a', 'g': '#2e7a3e', 'f': '#1e5030',
    'R': '#d89a48', 'r': '#a8682c', 'q': '#6e4020',
    'W': '#5ab8f0', 'v': '#2e78c4', 'u': '#1c4a8c',
}


def rgba(c):
    v = [int(c[i:i + 2], 16) for i in range(1, len(c), 2)]
    return tuple(v) + ((255,) if len(v) == 3 else ())


def to_rgba(g):
    return [[rgba(PAL[c]) if PAL[c] else (0, 0, 0, 0) for c in row] for row in g]


def shaded(g, test, cx, cy, rx, ry, cols):
    """Remplit les pixels ou test(x,y) est vrai ; teinte selon la lumiere venant d'en haut a gauche."""
    for y in range(len(g)):
        for x in range(len(g[0])):
            if test(x, y):
                l = -((x - cx) / rx * 0.6 + (y - cy) / ry * 0.8)
                i = 0 if l > 0.45 else 1 if l > -0.2 else 2 if l > -0.65 else 3
                g[y][x] = cols[i]


def ell(cx, cy, rx, ry):
    return lambda x, y: ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1.0


def poly(pts):
    def f(x, y):
        x += .5
        y += .5
        ins = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                ins = not ins
            j = i
        return ins
    return f


# ---------------------------------------------------------------- statue
def statue(active):
    g = blank(32, 64)
    st = 'sSTU'
    # socle : base, fut, dalle superieure
    rect(g, 3, 57, 28, 62, 'S'); rect(g, 3, 57, 28, 57, 's'); rect(g, 3, 62, 28, 62, 'U')
    rect(g, 3, 58, 3, 61, 's'); rect(g, 28, 58, 28, 61, 'T')
    rect(g, 6, 44, 25, 56, 'S'); rect(g, 6, 44, 6, 56, 's'); rect(g, 22, 44, 25, 56, 'T')
    rect(g, 25, 44, 25, 56, 'U'); rect(g, 6, 56, 25, 56, 'T')
    rect(g, 4, 38, 27, 41, 's'); rect(g, 4, 42, 27, 44, 'S')   # dessus puis face avant de la dalle
    rect(g, 4, 44, 27, 44, 'T'); rect(g, 27, 39, 27, 43, 'T')
    # joints, fissures, mousse
    for x in range(8, 22):
        put(g, x, 50, 'T')
    put(g, 11, 47, 'T'); put(g, 12, 48, 'T'); put(g, 19, 53, 'T'); put(g, 20, 54, 'U')
    for x, y in ((4, 61), (5, 61), (5, 60), (9, 56), (10, 56), (4, 58)):
        put(g, x, y, 'm')
    put(g, 6, 61, 'n'); put(g, 11, 56, 'n')
    # gemme sur la face du socle
    gem = ('w', 'c', 'C', 'B') if active else ('S', 'T', 'U', 'U')
    rect(g, 14, 47, 17, 51, gem[2])
    rect(g, 14, 47, 15, 49, gem[1]); put(g, 14, 47, gem[0])
    rect(g, 17, 50, 17, 51, gem[3]); rect(g, 14, 51, 16, 51, gem[3])
    # queue (derriere, visible sous le corps)
    shaded(g, poly([(12, 33), (20, 33), (22, 40), (16, 38), (10, 40)]), 16, 36, 6, 5, st)
    # corps, ailes repliees, tete
    shaded(g, ell(16, 27, 9, 11), 16, 27, 9, 11, st)
    shaded(g, ell(8.5, 28, 3.5, 9), 8.5, 28, 3.5, 9, st)
    shaded(g, ell(23.5, 28, 3.5, 9), 23.5, 28, 3.5, 9, st)
    shaded(g, ell(16, 13, 7, 6), 16, 13, 7, 6, st)
    # plumes : traits sur les ailes et le poitrail
    for y in (24, 28, 32):
        for x in (7, 8, 24, 25):
            put(g, x, y, 'T')
    for x, y in ((14, 26), (17, 26), (15, 29), (18, 29), (13, 32), (16, 32)):
        put(g, x, y, 'T')
    # pattes sur la dalle
    rect(g, 12, 36, 13, 37, 'T'); rect(g, 19, 36, 20, 37, 'T')
    # bec epais pointant vers le bas-avant, plus clair que la tete
    rect(g, 14, 14, 18, 16, 's'); rect(g, 15, 17, 17, 19, 'S'); put(g, 16, 20, 'T')
    rect(g, 18, 14, 18, 17, 'T'); rect(g, 17, 18, 17, 19, 'T'); rect(g, 14, 16, 18, 16, 'S')
    rect(g, 12, 9, 20, 9, 'U')                        # arcade sourciliere
    # pointes des ailes et plumes de queue qui depassent sur la dalle
    for x0 in (7, 24):
        rect(g, x0, 37, x0 + 1, 38, 'U'); rect(g, x0 - 1, 36, x0, 36, 'T')
    for x in (13, 16, 19):
        rect(g, x, 38, x + 1, 40, 'T'); rect(g, x + 1, 38, x + 1, 40, 'U')
    # yeux
    for x in (11, 20):
        if active:
            rect(g, x, 11, x + 1, 12, 'c'); put(g, x, 11, 'w')
        else:
            rect(g, x, 11, x + 1, 12, 'U')
    outline(g)
    if active:
        # halo : damier translucide autour de la silhouette
        for y in range(1, 44):
            for x in range(32):
                if g[y][x] == '.' and (x + y) % 2 == 0:
                    near = any(0 <= x + dx < 32 and 0 <= y + dy < 64 and g[y + dy][x + dx] not in ('.', 'h')
                               for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))
                    if near:
                        g[y][x] = 'h'
    return g


# ---------------------------------------------------------------- icone
UP = ["#............#",
      "##..........##",
      "###...##...###",
      "####.####.####",
      ".###.####.###.",
      "..#########.#.",
      "...#######....",
      "....#####.....",
      ".....####.....",
      ".....####.....",
      "......##......"]
DOWN = ["..............",
        ".....####.....",
        "....######....",
        "....######....",
        "..##########..",
        ".############.",
        "###.######.###",
        "##...####...##",
        "#....####....#",
        ".....####.....",
        "......##......"]


def icon(rows):
    g = blank(16, 16)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == '#':
                put(g, x + 1, y + 2, 'a')
    outline(g, 'e')
    put(g, 7, 5, 'e')                                 # oeil
    return g


# ---------------------------------------------------------------- logo
def ring(g, cx, cy, r, cols, th=2.6):
    for y in range(128):
        for x in range(128):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if abs(d - r) <= th:
                l = -((x + .5 - cx) * .6 + (y + .5 - cy) * .8) / r
                g[y][x] = cols[0] if l > .55 else cols[1] if l > -.45 else cols[2]


def raven_logo():
    g = blank(128, 128)
    wing = [(57, 58), (46, 48), (34, 42), (22, 40), (26, 47), (14, 50), (22, 56), (12, 62),
            (23, 66), (18, 74), (30, 73), (36, 80), (44, 74), (52, 76), (58, 72)]
    right = [(128 - x, y) for x, y in wing]
    for pts in (wing, right):
        shaded(g, poly(pts), 64, 60, 52, 24, 'dbaa')
    for x0, y0 in ((46, 52), (38, 58), (32, 64), (28, 70)):
        for i in range(8):
            put(g, x0 - i, y0 + i // 3, 'a'); put(g, 127 - (x0 - i), y0 + i // 3, 'a')
    shaded(g, poly([(57, 84), (71, 84), (76, 100), (64, 96), (52, 100)]), 64, 90, 12, 10, 'bbaa')
    for x in (60, 64, 68):
        for y in range(88, 94):
            put(g, x, y, 'a')
    shaded(g, ell(64, 68, 11, 19), 64, 68, 11, 19, 'dbaa')
    for x, y in ((60, 66), (68, 66), (62, 72), (66, 72), (60, 78), (68, 78), (64, 70), (64, 76)):
        put(g, x, y, 'a')
    shaded(g, ell(64, 50, 10, 9), 64, 50, 10, 9, 'dbba')
    # bec ocre qui pointe vers le bas
    for i in range(9):
        w = 4 - i // 2
        rect(g, 64 - w, 53 + i, 63 + w, 53 + i, 'o')
        put(g, 63 + w, 53 + i, 'p')
    # yeux
    for x in (58, 68):
        rect(g, x, 46, x + 1, 47, 'e')
    outline(g)
    return g


def logo():
    g = blank(128, 128)
    for cx, cy, c in ((64, 40, 'Ggf'), (38, 84, 'Rrq'), (90, 84, 'Wvu')):
        ring(g, cx, cy, 30, c)
    outline(g)
    r = raven_logo()
    for y in range(128):
        for x in range(128):
            if r[y][x] != '.':
                g[y][x] = r[y][x]
    return g


def main():
    sp = sheet([to_rgba(statue(False)), to_rgba(statue(True))])
    ic = sheet([to_rgba(icon(UP)), to_rgba(icon(DOWN))])
    lg = to_rgba(logo())
    os.makedirs(os.path.join(ROOT, 'puzzles'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'ui'), exist_ok=True)
    save_png(os.path.join(ROOT, 'puzzles', 'statue_corbeau.png'), sp)
    save_png(os.path.join(ROOT, 'ui', 'icone_sauvegarde.png'), ic)
    save_png(os.path.join(ROOT, 'ui', 'logo.png'), lg)
    if len(sys.argv) > 1:
        d = sys.argv[1]
        os.makedirs(d, exist_ok=True)
        for nom, px, s in (('statue', sp, 8), ('icone', ic, 16), ('logo', lg, 5)):
            save_png(os.path.join(d, 'apercu_%s_herbe.png' % nom), background(px, (70, 110, 60, 255)), s)
            save_png(os.path.join(d, 'apercu_%s_sombre.png' % nom), background(px, (30, 30, 40, 255)), s)


if __name__ == '__main__':
    main()
