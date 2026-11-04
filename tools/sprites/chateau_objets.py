"""Objets de décor du château (statues, armures, colonnes, piliers, bannières, portail, cercle des sceaux, symboles) — Les Trois Sceaux.

Dessinés sur de grands canevas puis découpés en tuiles de 32×32 (les tuiles gardent leur numéro du plan). Contour sombre d'1 px,
lumière en haut à gauche, aucun pixel semi-transparent.
"""
import math
import random

from chateau_pierre import *  # noqa: F401,F403
import chateau_pierre as C


def rect_shaded(t, x0, y0, x1, y1, p, seed=1, noise=0.0, vertical=False):
    """Bloc ombré : arête claire en haut/gauche, sombre en bas/droite."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            col = p[MD]
            if noise and rnd(x, y, seed) < noise:
                col = p[LT]
            if y == y0 or x == x0:
                col = p[HI] if (y == y0 or x == x0) and rnd(x, y, seed) < 0.9 else p[LT]
            if y == y1 or x == x1:
                col = p[DK]
            if y == y1 and x == x0:
                col = p[DK]
            put(t, x, y, col)


def rect_o(t, x0, y0, x1, y1, p, seed=1, noise=0.0):
    rect_shaded(t, x0 + 1, y0 + 1, x1 - 1, y1 - 1, p, seed, noise)
    for x in range(x0, x1 + 1):
        put(t, x, y0, O)
        put(t, x, y1, O)
    for y in range(y0, y1 + 1):
        put(t, x0, y, O)
        put(t, x1, y, O)


# ------------------------------------------------------------------ chevaliers (statue de pierre, armure vide)
def knight(kind, metal):
    """Canevas 32×64 : tuile du haut = rangées 0-31 (buste, casque), tuile du bas = rangées 32-63 (jambes, socle)."""
    cv = canvas(32, 64)
    p = PAL['metal'] if metal else PAL['fac_in']
    base = PAL['sol_in'] if metal else PAL['fac_in']
    trim = PAL['or_']
    # socle
    rect_o(cv, 4, 52, 27, 63, PAL['fac_in'] if not metal else PAL['cour'], 4, 0.15)
    for x in range(5, 27):
        put(cv, x, 56, PAL['fac_in'][DK] if not metal else PAL['cour'][DK])
    rect(cv, 6, 53, 25, 53, PAL['fac_in'][HI] if not metal else PAL['cour'][HI])
    # jambes (solerets)
    for x0 in (10, 17):
        rect_o(cv, x0, 40, x0 + 5, 52, p, 5)
        rect_o(cv, x0 - 1, 49, x0 + 6, 53, p, 6)
    # jupe de mailles / tassettes
    rect_o(cv, 9, 33, 22, 42, p, 7)
    for x in range(10, 22, 3):
        put(cv, x, 41, p[DP])
        put(cv, x + 1, 38, p[DK])
    # torse
    rect_o(cv, 9, 19, 22, 35, p, 8)
    for y in range(21, 33):
        put(cv, 15, y, p[LT])
        put(cv, 16, y, p[DK])
    rect(cv, 10, 33, 21, 33, trim[MD])                                  # ceinture
    put(cv, 15, 33, trim[HI])
    put(cv, 16, 33, trim[HI])
    # bras
    rect_o(cv, 5, 22, 9, 38, p, 9)
    rect_o(cv, 22, 22, 26, 38, p, 10)
    # épaulières
    ball(cv, 7, 21, 5, 4, p, 11, 0.2)
    ball(cv, 24, 21, 5, 4, p, 12, 0.2)
    # tête : heaume
    ball(cv, 15.5, 10, 6.8, 7.2, p, 13, 0.15)
    rect(cv, 11, 9, 20, 9, O)                                           # fente de visière
    rect(cv, 11, 12, 20, 12, p[DP])
    for y in range(9, 15):
        put(cv, 15, y, O)
        put(cv, 16, y, O)
    rect(cv, 13, 15, 18, 16, p[DK])                                     # gorgerin
    if metal:                                                           # panache rouge
        for i in range(9):
            put(cv, 14 + i // 3, 3 - i // 3, PAL['rouge'][LT])
        for y in range(1, 9):
            for x in range(11, 21):
                if ((x - 15.5) / 3.5) ** 2 + ((y - 4) / 4.0) ** 2 <= 1 and y < 7:
                    put(cv, x, y, PAL['rouge'][LT] if (x + y) % 3 else PAL['rouge'][HI])
        for y in range(4, 9):
            put(cv, 20 + (y - 4) // 2, y, PAL['rouge'][MD])
        rect(cv, 12, 9, 19, 9, O)
        put(cv, 13, 10, PAL['rune'][MD])                                # lueur froide dans la visière
        put(cv, 18, 10, PAL['rune'][MD])
    else:
        put(cv, 15, 3, p[HI])
    # arme
    if kind == 'a':                                                     # épée plantée devant le corps
        rect(cv, 15, 29, 16, 57, PAL['metal'][LT] if not metal else PAL['metal'][HI])
        rect(cv, 16, 29, 16, 57, PAL['metal'][DK])
        rect(cv, 11, 33, 20, 34, trim[MD])
        rect(cv, 11, 33, 20, 33, trim[HI])
        rect(cv, 14, 28, 17, 30, trim[MD])
        put(cv, 14, 28, trim[HI])
        rect(cv, 13, 31, 18, 32, p[DP])                                 # poings
        for x in (15, 16):
            put(cv, x, 57, O)
    else:                                                               # écu à gauche, lance à droite
        for y in range(25, 46):
            hw = 5 if y < 38 else max(0, 5 - (y - 37) * 0.7)
            for x in range(int(8 - hw), int(8 + hw) + 1):
                col = PAL['rouge'][MD] if x < 8 else PAL['rouge'][DK]
                if y < 27 or abs(x - 8) >= hw - 0.6:
                    col = trim[MD]
                put(cv, x, y, col)
        put(cv, 7, 31, trim[HI])
        put(cv, 8, 31, trim[HI])
        rect(cv, 6, 32, 9, 32, trim[HI])
        rect(cv, 7, 33, 8, 36, trim[LT])
        rect(cv, 27, 6, 27, 59, PAL['cap_in'][HI] if not metal else PAL['metal'][DK])
        rect(cv, 26, 6, 26, 59, PAL['fac_in'][DK] if not metal else PAL['metal'][MD])
        for i in range(6):
            put(cv, 26 + (1 if i % 2 else 0), 5 - i, PAL['metal'][HI])
        rect(cv, 25, 6, 28, 7, trim[MD])
    outline(cv, O)
    return cv


def column_haut():
    cv = blank()
    p = PAL['sol_in']
    rect_o(cv, 6, 18, 25, 31, p, 3)                                     # fût (bas du chapiteau jusqu'en bas de la tuile)
    rect_o(cv, 3, 8, 28, 17, p, 4)                                      # chapiteau
    rect(cv, 4, 9, 27, 9, p[HI])
    for x in range(8, 24, 4):
        put(cv, x, 13, p[DK])
        put(cv, x, 14, p[DP])
    rect(cv, 7, 18, 24, 19, p[DP])
    outline(cv, O)
    return cv


def column_base():
    cv = blank()
    p = PAL['sol_in']
    rect_o(cv, 6, 0, 25, 15, p, 3)                                      # fût qui descend du haut de la tuile
    for y in range(2, 15):
        put(cv, 10, y, p[HI] if y % 4 else p[LT])
        put(cv, 21, y, p[DK])
    rect_o(cv, 3, 16, 28, 23, p, 5)                                     # base moulurée
    rect_o(cv, 1, 24, 30, 30, p, 6)                                     # plinthe
    rect(cv, 2, 25, 29, 25, p[HI])
    outline(cv, O)
    # ombre portée
    for x in range(3, 30):
        if (x % 2 == 0) and cv[31][x] is None:
            cv[31][x] = PAL['sol_in'][DP]
    return cv


def column_brisee():
    cv = blank()
    p = PAL['sol_in']
    rect_o(cv, 6, 10, 25, 23, p, 3)
    pts = [(6, 10), (9, 7), (12, 9), (15, 5), (18, 8), (21, 6), (25, 9)]                 # sommet brisé en dents
    for x in range(6, 26):
        top = min(pts, key=lambda q: abs(q[0] - x))[1] + (abs(x - min(pts, key=lambda q: abs(q[0] - x))[0]) * 0)
        for y in range(top, 11):
            cv[y][x] = p[HI] if (y == top) else p[LT] if x < 14 else p[MD]
    for y in range(11, 24):
        put(cv, 10, y, p[HI] if y % 5 else p[LT])
        put(cv, 21, y, p[DK])
    rect_o(cv, 3, 24, 28, 30, p, 6)
    rect(cv, 4, 25, 27, 25, p[HI])
    outline(cv, O)
    for (x, y, w) in ((2, 27, 3), (26, 28, 2), (28, 21, 2)):             # éclats au sol
        rect(cv, x, y, x + w, y + 1, p[LT])
        put(cv, x, y, p[HI])
        put(cv, x + w, y + 1, p[DK])
    outline(cv, O)
    return cv


# ------------------------------------------------------------------ piliers 2×2 (64×64, marge de 2 px à gauche/haut, collision 30×30)
def pillar():
    cv = canvas(64, 64)
    p = PAL['sol_in']
    top = PAL['cap_in']
    # dessus (coiffe) : on voit le haut du pilier
    rect_o(cv, 2, 2, 61, 33, [top[HI] if False else PAL['fac_in'][LT], PAL['fac_in'][MD], PAL['fac_in'][DK], top[LT], top[MD]][:5], 1)
    for y in range(3, 33):
        for x in range(3, 61):
            n = vnoise(x, y, 8, 21)
            col = PAL['sol_in'][LT] if n > 0.7 else PAL['sol_in'][DK] if n < 0.28 else PAL['sol_in'][MD]
            if y < 5 or x < 5:
                col = PAL['sol_in'][HI]
            elif y > 30 or x > 58:
                col = PAL['sol_in'][DK]
            cv[y][x] = col
    for y in range(8, 28):                                              # cadre gravé du dessus
        for x in (10, 53):
            cv[y][x] = PAL['sol_in'][DK]
    for x in range(10, 54):
        for y in (8, 27):
            cv[y][x] = PAL['sol_in'][DK]
    for x in range(11, 53):
        cv[9][x] = PAL['sol_in'][LT]
    ring(cv, 32, 18, 5, PAL['or_'][MD])
    put(cv, 32, 18, PAL['or_'][HI])
    # face avant
    for y in range(34, 62):
        for x in range(2, 62):
            col = PAL['fac_in'][MD]
            if y == 34:
                col = PAL['fac_in'][HI]
            elif y in (35,):
                col = PAL['fac_in'][LT]
            elif x < 5:
                col = PAL['fac_in'][LT]
            elif x > 58:
                col = PAL['fac_in'][DK]
            elif x % 16 == 8 and 36 <= y < 56:
                col = PAL['fac_in'][DP]
            elif y >= 56:
                col = PAL['fac_in'][DK]
            else:
                n = vnoise(x, y, 8, 25)
                col = PAL['fac_in'][LT] if n > 0.74 else PAL['fac_in'][DK] if n < 0.2 else PAL['fac_in'][MD]
            cv[y][x] = col
    for x in range(2, 62):
        cv[56][x] = PAL['fac_in'][DP]
        cv[61][x] = O
    for x in range(2, 62):
        cv[2][x] = O
    for y in range(2, 62):
        cv[y][2] = O
        cv[y][61] = O
    for y in range(40, 50):                                             # petite rune gravée sur la face
        cv[y][31] = PAL['rune'][DK]
        cv[y][32] = PAL['rune'][DK]
    for x in range(28, 36):
        cv[44][x] = PAL['rune'][DK]
    return cv


# ------------------------------------------------------------------ bannières (Dessus, plaquées sur un mur)
def banner(kind):
    cv = blank()
    cloth = [PAL['ronce'][MD], PAL['ronce'][DK], PAL['ronce'][DK], PAL['ronce'][DP], PAL['ronce'][DP]]
    gold = PAL['or_']
    pole = PAL['or_']
    rect(cv, 4, 1, 27, 2, pole[MD])
    rect(cv, 4, 1, 27, 1, pole[HI])
    for x in (3, 28):
        rect(cv, x, 0, x, 3, pole[LT])
    ball(cv, 3, 1, 2, 2, pole, 3, 0)
    ball(cv, 28, 1, 2, 2, pole, 4, 0)
    top, bot, x0, x1 = 3, 28, 8, 23
    for y in range(top, bot + 1):
        for x in range(x0, x1 + 1):
            tip = max(0, (y - 20)) if kind == 'a' else 0
            if kind == 'a' and abs(x - 15.5) > (x1 - x0) / 2 - tip * 0.85:
                continue
            col = cloth[1]
            if x in (x0, x0 + 1) or x == x1:
                col = gold[MD] if x != x0 else gold[HI]
            if (x - x0) % 5 == 3:
                col = PAL['ronce'][MD]
            if y == top or y == top + 1:
                col = gold[MD]
            if kind == 'b':                                              # déchirée : fente en biais et bas en lambeaux
                if (y - 9) * 1.0 > (x - 12) * 1.6 and (y - 9) < (x - 12) * 1.6 + 5 and y > 9:
                    continue
                if y > 21 + int(rnd(x, 1, 5) * 7):
                    continue
                if x > 19 and y > 15 and rnd(x, y, 6) < 0.5:
                    continue
                col = PAL['ronce'][DK] if col == cloth[1] else col
            put(cv, x, y, col)
    if kind == 'a':
        eye(cv, 15, 12, gold[HI], PAL['ronce'][DP], PAL['rouge'][LT], O)
        rect(cv, 12, 18, 19, 18, gold[MD])
    else:
        eye(cv, 14, 8, gold[MD], PAL['ronce'][DP])
    outline(cv, O)
    return cv


# ------------------------------------------------------------------ symboles au sol (arc, bombe, lanterne) : 16×16 or pâle gravé
ARC = ['................',
       '......###.......',
       '.......###......',
       '.........##.....',
       '..........##....',
       '.#.........#....',
       '.##........##...',
       '.#.#########>>>.',
       '.##........##...',
       '.#.........#....',
       '..........##....',
       '.........##.....',
       '.......###......',
       '......###.......',
       '................',
       '................']
BOMB = ['............#...',
        '...........###..',
        '............#...',
        '...........#....',
        '..........#.....',
        '.....#####......',
        '....#######.....',
        '...#########....',
        '...#########....',
        '...#########....',
        '...#########....',
        '....#######.....',
        '.....#####......',
        '................',
        '................',
        '................']
LANT = ['................',
        '......####......',
        '.....#....#.....',
        '....########....',
        '....#..##..#....',
        '....#.####.#....',
        '....#.####.#....',
        '....#..##..#....',
        '....########....',
        '.....######.....',
        '......####......',
        '................',
        '................',
        '................',
        '................',
        '................']


def symbol(rows, fill=None):
    t = blank()
    rows2 = [r.replace('>', '#') for r in rows]
    engrave(t, rows2, 8, 8, PAL['or_'][LT], PAL['or_'][DP])
    return t


# ------------------------------------------------------------------ cercle des sceaux (4×4 = 128×128)
def seal_circle(floor_tile):
    cv = canvas(128, 128)
    for y in range(128):
        for x in range(128):
            cv[y][x] = floor_tile[y % 32][x % 32]
    cx = cy = 63.5
    gl, gd, gh = PAL['arene'][DP], PAL['or_'][MD], PAL['or_']

    def dring(x, y, r, col=None, hi=True):
        ring(cv, x + 1, y + 1, r, gl)
        ring(cv, x, y, r, col or gd)
        if hi:
            ring(cv, x - 0.5, y - 0.5, r, gh[LT]) if False else None
    for r in (60, 58):
        dring(cx, cy, r)
    ring(cv, cx, cy, 59, gh[DK])
    dring(cx, cy, 51)
    for k in range(48):                                                  # runes entre les deux anneaux
        a = k * math.pi / 24
        r0 = 53.5
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0
        for j in range(3 + (k % 2)):
            xx, yy = round(x0 + math.cos(a) * j), round(y0 + math.sin(a) * j)
            put(cv, xx + 1, yy + 1, gl)
            put(cv, xx, yy, gh[MD])
        put(cv, round(x0 + math.cos(a + 0.05) * 2 + (1 if k % 3 == 0 else 0)), round(y0 + math.sin(a + 0.05) * 2), gh[LT])
    # trois cercles entrelacés
    centers = [(cx + math.cos(math.radians(a)) * 15, cy + math.sin(math.radians(a)) * 15) for a in (-90, 30, 150)]
    for (ax, ay) in centers:
        dring(ax, ay, 25, gh[LT])
    # triangle et centre
    pts = [(cx + math.cos(math.radians(a)) * 20, cy + math.sin(math.radians(a)) * 20) for a in (-90, 30, 150)]
    for i in range(3):
        a, b = pts[i], pts[(i + 1) % 3]
        line(cv, round(a[0]), round(a[1]), round(b[0]), round(b[1]), gh[MD])
        line(cv, round(a[0]) - 1, round(a[1]) - 1, round(b[0]) - 1, round(b[1]) - 1, gh[HI])
    ball(cv, cx, cy, 4.5, 4.5, gh, 9, 0)
    # petits symboles : arc, bombe, lanterne à l'extérieur de chaque cercle
    for (ax, ay), rows in zip(centers, (ARC, BOMB, LANT)):
        px, py = round(cx + (ax - cx) * 2.3) - 8, round(cy + (ay - cy) * 2.3) - 8
        engrave(cv, [r.replace('>', '#') for r in rows], px, py, gh[LT], PAL['arene'][DP])
    return cv
