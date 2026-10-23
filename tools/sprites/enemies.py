"""Bestiaire des Trois Sceaux : 11 ennemis + variantes rouges, projectiles et nuage de mort.

Usage : python3 enemies.py <dossier art/enemies>
"""
import sys, os, math
import engine
from enemy_lib import *

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out_enemies'
os.makedirs(OUT, exist_ok=True)
SHEETS = {}

# Couleurs de la variante rouge (plus forte) : la corruption noire/violette devient rouge sang
RED_CORRUPTION = {'I': '#5a0e18', 'q': '#961c28', 'p': '#e2342c', 'J': '#6a1420', '5': '#961c28'}


def eyes(g, pts, c='4', glow='F'):
    for (x, y) in pts:
        put(g, x, y, c)
        put(g, x, y + 1, glow)


# ===================================================================== FORÊT
# --- Ronceau : petite boule de ronces noires (Errant)
def ronceau(squash=0, turn=0):
    g = blank()
    cx, cy, rx, ry = 16, 24.5 + squash * 0.5, 6.5 + squash * 0.7, 6 - squash * 0.6
    ellipse(g, cx, cy, rx, ry, 'I', None, 'q', hi_k=-0.35)
    for k in range(10):  # épines
        a = math.radians(k * 36 + turn)
        for r in (1.0, 2.0):
            x = round(cx - 0.5 + math.cos(a) * (rx + r))
            y = round(cy - 0.5 + math.sin(a) * (ry + r))
            if y <= 31:
                put(g, x, y, '0' if r == 2.0 else 'q')
    for k in range(5):  # reflets violets
        a = math.radians(k * 72 + 20 + turn)
        put(g, round(cx - 0.5 + math.cos(a) * 3), round(cy - 0.5 + math.sin(a) * 3), 'p')
    ey = round(cy - 1)
    eyes(g, [(13, ey), (14, ey), (17, ey), (18, ey)])
    outline(g)
    return bottom_align(g)


SHEETS['ronceau'] = build_enemy(OUT, 'ronceau', [
    ('move', [ronceau(0, 0), ronceau(1, 18)], 4.0, True),
], red=RED_CORRUPTION)


# --- Sanglier noirci : charge en ligne droite (Chasseur)
def boar_side(step=0, stunned=False):
    g = blank()
    ellipse(g, 18, 21, 10, 5.5, 'B', 'H', '6')               # corps
    ellipse(g, 8, 21.5, 5.5, 4.5, 'B', 'H', '6')             # tête
    ellipse(g, 3.5, 23.5, 2.5, 2, 'E', '6')                  # groin
    for x in range(10, 27, 2):                               # crinière de corruption
        put(g, x, 14 + (x % 4 == 0), 'I')
        put(g, x, 15, 'I')
    rect(g, 15, 17, 19, 18, 'I')                             # tache noire
    put(g, 20, 18, 'I'); put(g, 14, 18, 'I'); put(g, 17, 19, 'I')
    paint(g, 7, 14, ['8', '88'])                             # oreille
    for i, x in enumerate((10, 13, 21, 24)):                 # pattes
        up = 1 if (i % 2) == step else 0
        rect(g, x, 25, x + 1, 30 - up, 'H' if i in (1, 3) else 'B')
    if stunned:
        paint(g, 6, 19, ['0.0', '.0.', '0.0'])
        paint(g, 4, 10, ['K...K', '.K.K.'])
    else:
        paint(g, 6, 19, ['44', 'FF'])
    paint(g, 3, 24, ['g', 'gg'])                             # défense
    outline(g)
    return bottom_align(g)


def boar_front(bob=0, back=False):
    g = blank()
    ellipse(g, 16, 21, 9.5, 6, 'B', 'H', '6')                # corps derrière
    for x in range(9, 24, 2):
        put(g, x, 15, 'I')
    if back:
        ellipse(g, 16, 22, 8, 7, 'B', 'H', '6')
        rect(g, 15, 14, 16, 22, 'I')                         # crinière
        paint(g, 15, 28, ['88', '.8'])                       # queue
        for x in (10, 20):
            rect(g, x, 27, x + 2, 30, 'H')
        paint(g, 9, 13, ['88'])
        paint(g, 21, 13, ['88'])
    else:
        for x in (11, 19):
            rect(g, x, 27, x + 2, 30, 'H')
        ellipse(g, 16, 23, 6.5, 5.5, 'B', 'H', '6')          # tête
        paint(g, 9, 17, ['88', '888'])
        paint(g, 21, 17, ['88', '888'])
        ellipse(g, 16, 26.5, 3.5, 2.5, 'E', '6')             # groin
        put(g, 15, 26, '0'); put(g, 16, 26, '0')
        paint(g, 12, 21, ['44', 'FF']); paint(g, 18, 21, ['44', 'FF'])
        paint(g, 11, 27, ['g', 'g']); paint(g, 20, 27, ['g', 'g'])
    outline(g)
    g = bottom_align(g)
    return shift(g, 0, -bob) if bob else g


bs0, bs1 = boar_side(0), boar_side(1)
bf0, bf1 = boar_front(), boar_front(1)
bb0, bb1 = boar_front(back=True), boar_front(1, back=True)
SHEETS['sanglier_noirci'] = build_enemy(OUT, 'sanglier_noirci', [
    ('move_down', [bf0, bf1], 5.0, True),
    ('move_up', [bb0, bb1], 5.0, True),
    ('move_left', [bs0, bs1], 5.0, True),
    ('move_right', [mirror(bs0), mirror(bs1)], 5.0, True),
    ('charge_down', ('move_down',), 12.0, True),
    ('charge_up', ('move_up',), 12.0, True),
    ('charge_left', ('move_left',), 12.0, True),
    ('charge_right', ('move_right',), 12.0, True),
    ('stunned_left', [boar_side(0, True)], 5.0, False),
    ('stunned_right', [mirror(boar_side(0, True))], 5.0, False),
], red={'B': '#961c28', 'H': '#5a0e18', '6': '#e2342c', 'I': '#241a22'})


# --- Lutin des branches : caché dans un arbre, lance des glands (Tireur)
def bush(g):
    ellipse(g, 16, 25, 12, 6.5, 'v', 'w', None)
    for (x, y) in [(8, 21), (12, 19), (18, 19), (23, 21), (15, 22), (10, 25), (21, 25), (16, 27)]:
        put(g, x, y, 'w'); put(g, x + 1, y, 'v')
    for (x, y) in [(6, 23), (25, 23), (14, 18), (20, 20)]:
        put(g, x, y, '6')                                    # brindilles
    return g


def lutin(state):
    g = blank()
    if state != 'hidden':
        hy = 9 if state != 'throw' else 8
        ellipse(g, 16, hy + 5, 5.5, 5, 'A', 'H', '6')       # tête d'écorce
        for (x, y) in [(10, hy), (12, hy - 1), (15, hy - 2), (19, hy - 1), (21, hy)]:
            line(g, x, y, 16, hy + 3, 'v')                   # cheveux de feuilles
        put(g, 15, hy - 2, 'w'); put(g, 21, hy, 'w')
        paint(g, 12, hy + 4, ['gg..gg'])
        paint(g, 12, hy + 5, ['g0..0g'])
        put(g, 14, hy + 7, 'I'); put(g, 17, hy + 7, 'I')   # bouche noire
        put(g, 15, hy + 8, 'I'); put(g, 16, hy + 8, 'I')
        rect(g, 13, hy + 10, 18, 22, 'H')
        if state == 'throw':
            line(g, 19, hy + 11, 23, hy + 3, 'H')          # bras levé
            ellipse(g, 24.5, hy + 1.5, 2, 2.2, '6', 'B')   # gland
            paint(g, 23, hy - 1, ['A6A'])
    bush(g)
    if state == 'hidden':
        paint(g, 13, 22, ['K..K'])                          # yeux dans le feuillage
    outline(g)
    return bottom_align(g)


SHEETS['lutin_des_branches'] = build_enemy(OUT, 'lutin_des_branches', [
    ('hidden', [lutin('hidden')], 3.0, True),
    ('peek', [lutin('peek')], 3.0, False),
    ('throw', [lutin('peek'), lutin('throw')], 6.0, False),
], red={'A': '#961c28', 'H': '#5a0e18', '6': '#e2342c', 'K': '#e8c040'})


# ===================================================================== MONTAGNE
# --- Caillou rampant : Ronceau version pierre (Errant)
def caillou(squash=0):
    g = blank()
    cx, cy = 16, 25 + squash * 0.5
    ellipse(g, cx, cy, 7.5 + squash * 0.7, 6 - squash * 0.6, 'h', 'k', 'g')
    for (x, y) in [(12, 22), (13, 23), (19, 25), (20, 24), (21, 24), (15, 28)]:
        put(g, x, round(y + squash * 0.5), 'I')             # fissures de corruption
    put(g, 18, round(21 + squash), 'g'); put(g, 11, round(26 + squash * 0.5), 'g')
    ey = round(cy - 0.5)
    eyes(g, [(13, ey), (14, ey), (17, ey), (18, ey)])
    # petites pattes de pierre
    for x in (10, 21):
        put(g, x + squash, 31, 'k')
    outline(g)
    return bottom_align(g)


SHEETS['caillou_rampant'] = build_enemy(OUT, 'caillou_rampant', [
    ('move', [caillou(0), caillou(1)], 3.0, True),
], red={'h': '#961c28', 'k': '#5a0e18', 'g': '#e2342c', 'I': '#241a22'})


# --- Chauve-souris des mines : vol en zigzag (Chasseur). Volante : pas de pieds sur y=31.
def bat(up):
    g = blank()
    cy = 15
    if up:
        wing_l = [(15, cy), (6, cy - 6), (4, cy - 3), (6, cy), (8, cy + 1), (11, cy + 2)]
    else:
        wing_l = [(15, cy), (5, cy + 3), (6, cy + 6), (9, cy + 5), (11, cy + 7), (13, cy + 4)]
    # remplissage de l'aile gauche (polygone simple par lignes)
    for i in range(1, len(wing_l) - 1):
        a, b, c = wing_l[0], wing_l[i], wing_l[i + 1]
        for t in range(0, 21):
            px_ = b[0] + (c[0] - b[0]) * t / 20
            py_ = b[1] + (c[1] - b[1]) * t / 20
            line(g, a[0], a[1], round(px_), round(py_), 'q')
    for (x, y) in wing_l[1:]:
        line(g, 15, cy, x, y, 'I')                            # nervures
    g = [row[:16] + row[:16][::-1] for row in g]              # aile droite en miroir
    ellipse(g, 16, cy + 0.5, 3.5, 4, 'I', None, 'q')         # corps
    paint(g, 13, cy - 5, ['I....I', 'II..II'])                # oreilles
    put(g, 14, cy - 1, '4'); put(g, 17, cy - 1, '4')
    put(g, 15, cy + 2, 'g'); put(g, 16, cy + 2, 'g')          # crocs
    outline(g)
    return g


SHEETS['chauve_souris'] = build_enemy(OUT, 'chauve_souris', [
    ('fly', [bat(True), bat(False)], 8.0, True),
], red=RED_CORRUPTION)


# --- Mineur maudit : bouclier de pierre qui bloque l'épée (Spécial)
MINER_DOWN = [
    "................", "................", "................", "................",
    "...........00000", ".........00kkkkk", "........0khhhhKK", "........0kkkkkKK",
    ".......0kkkkkkkk", "........0hhhhhhh", "........0hh4hhhh", "........0hhFhhhk",
    "........0khhhhhh", ".........0kkkkkk", "......00AAAAAAAA", "....00AAAAAAAAAA",
    "...0AAAAAAAHAAAA", "...0AAH0AAAHAAAA", "...0AAH0AAAAAAAA", "...0AAH0AAAAAAAA",
    "...0AAH0AAAAAAAA", "...0CCG0AAAAAAAA", "...0CCG0DDDDDDDD", "...0CCG0JJJJJJJJ",
    "....0000JJJJJJJJ", "........0JJJJJJJ", "........0JJJJJ0.", "........0JJJJJ0.",
    "........0HHHHH0.", "........0HHHHH0.", ".......0HHHHHH0.", ".......00000000.",
]
MINER_UP = [
    "................", "................", "................", "................",
    "...........00000", ".........00kkkkk", "........0khhhhkk", "........0kkkkkkk",
    ".......0kkkkkkkk", "........0kkkkkkk", "........0hhhhhhh", "........0hhhhhhh",
    "........0khhhhhh", ".........0kkkkkk", "......00AAAAAAAA", "....00AAAAAAAAAA",
    "...0AAAAAAAAAAAA", "...0AAH0AAAAAAAA", "...0AAH0AAAAAAAA", "...0AAH0AAHAAAAA",
    "...0AAH0AAAHAAAA", "...0CCG0AAAAHAAA", "...0CCG0DDDDDDDD", "...0CCG0JJJJJJJJ",
    "....0000JJJJJJJJ", "........0JJJJJJJ", "........0JJJJJ0.", "........0JJJJJ0.",
    "........0HHHHH0.", "........0HHHHH0.", ".......0HHHHHH0.", ".......00000000.",
]
MINER_LEFT = [
    "................................",
    "................................",
    "................................",
    "................................",
    "...........00000................",
    "..........0kkkkk00..............",
    ".......00KKkhhhhkk0.............",
    "........0KKkkkkkkkk0............",
    "......0kkkkkkkkkkkkk0...........",
    ".......0hhhhhhkkkkkk0...........",
    ".......04hhhhhhkkkk0............",
    "......0hFhhhhhhhhhk0............",
    ".......0khhhhhhhhk0.............",
    "........0kkkkkkkk0..............",
    ".......00AAAAAAAAA00............",
    "......0AAAAAAAAAAAAA0...........",
    "......0AAAAAAAAAAAAA0...........",
    "......0AAAAA0AAH0AAA0...........",
    "......0AAAAA0AAH0AAA0...........",
    "......0AAAAA0AAH0AAA0...........",
    "......0AAAAA0AAH0AAA0...........",
    "......0AAAAA0CCG0AAA0...........",
    "......0DDDDD0CCG0DDD0...........",
    "......0JJJJJ0CCG0JJJ0...........",
    "......0JJJJJJ0000JJJ0...........",
    ".......0JJJJJJJJJJJ0............",
    "........0JJJJJ0JJJJ0............",
    "........0JJJJJ0JJJJ0............",
    "........0HHHHH0HHHH0............",
    "........0HHHHH0HHHH0............",
    ".......0HHHHHH0HHHH0............",
    ".......000000000000.............",
]
SHIELD_FRONT = [""] * 14 + [
    ".........00000000000000.........",
    "........0ghhhhhhhhhhhhk0........",
    "........0ghhhhIhhhhhhhk0........",
    "........0hhhhhhIhhhhhhk0........",
    "........0hhhhhhIIhhhhhk0........",
    "........0hhhgghhhIhhhhk0........",
    "........0hhhhhhhhhIhhhk0........",
    "........0hhhhhhhhhIhhhk0........",
    "........0hhhhhhhhIhhhhk0........",
    "........0hhhhhhhhhhhhhk0........",
    "........0hhhhhhhhhhhhhk0........",
    "........0kkkkkkkkkkkkkk0........",
    ".........00000000000000.........",
]
SHIELD_SIDE = [""] * 13 + [
    "....0000........................",
    "...0ghk0........................",
    "...0hhk0........................",
    "...0hIk0........................",
    "...0hhI0........................",
    "...0ghk0........................",
    "...0hhk0........................",
    "...0hIk0........................",
    "...0hhk0........................",
    "...0hhk0........................",
    "...0hhk00000....................",
    "...0hhk0CCG0....................",
    "...0kkk0000.....................",
    "....000.........................",
]


def humanoid_rows(views, hip, legmid, overlays=None):
    overlays = overlays or {}
    v = {'down': engine.overlay(engine.grid(views['down'], half=True), overlays.get('down')),
         'up': engine.overlay(engine.grid(views['up'], half=True), overlays.get('up')),
         'left': engine.overlay(engine.grid(views['left']), overlays.get('left'))}
    return engine.frames_for(v, hip, legmid)


def humanoid_anims(rows_with, rows_without=None, suffix='_noshield'):
    dirs = ['down', 'up', 'left', 'right']
    anims = []
    for r, d in enumerate(dirs):
        anims.append((f'idle_{d}', [rows_with[r][0]], 5.0, True))
        anims.append((f'walk_{d}', rows_with[r][1:], 8.0, True))
    if rows_without:
        for r, d in enumerate(dirs):
            anims.append((f'idle_{d}{suffix}', [rows_without[r][0]], 5.0, True))
            anims.append((f'walk_{d}{suffix}', rows_without[r][1:], 8.0, True))
    return anims


miner_views = {'down': MINER_DOWN, 'up': MINER_UP, 'left': MINER_LEFT}
m_shield = humanoid_rows(miner_views, 26, 13, {'down': SHIELD_FRONT, 'left': SHIELD_SIDE})
m_bare = humanoid_rows(miner_views, 26, 13)
SHEETS['mineur_maudit'] = build_enemy(OUT, 'mineur_maudit', humanoid_anims(m_shield, m_bare),
                                      red={'A': '#961c28', 'H': '#5a0e18', 'J': '#382e42'})


# ===================================================================== LAC
# --- Têtard d'encre : nage en eau peu profonde, éclabousse (Errant). Tourné vers la gauche.
def tetard(phase):
    g = blank()
    for x in range(17, 29):                                   # queue ondulante
        y = 25 + math.sin((x - 17) / 2.2 + phase) * 1.6
        th = 2 if x < 26 else 1
        for t in range(th):
            put(g, x, round(y) + t, 'n' if t == 0 else 'I')
    ellipse(g, 13, 25, 6, 4.5, 'n', 'I', 'b')                # tête
    paint(g, 9, 22, ['gg.gg', 'g0.g0'])                      # yeux
    put(g, 8, 26, 'I'); put(g, 9, 26, 'I')                   # bouche
    if phase > 1:                                            # gouttes d'encre
        put(g, 5, 21, 'n'); put(g, 22, 20, 'n'); put(g, 25, 29, 'b')
    outline(g)
    return bottom_align(g)


SHEETS['tetard_encre'] = build_enemy(OUT, 'tetard_encre', [
    ('move', [tetard(0), tetard(math.pi)], 6.0, True),
], red={'n': '#961c28', 'I': '#5a0e18', 'b': '#e2342c'})


# --- Crabe-armure : vulnérable seulement de dos (Chasseur)
def crab_legs(g, step, cx=16, span=(7, 9, 11)):
    for i, x in enumerate(span):
        dy = 1 if (i % 2) == step else 0
        line(g, x + 1, 26, x - 1, 30 - dy, 'k')
        line(g, 31 - x - 1, 26, 31 - x + 1, 30 - (1 - dy if True else dy), 'k')


def crab_front(step):
    g = blank()
    crab_legs(g, step)
    for (cx, s) in ((5, 1), (26, -1)):                       # pinces
        line(g, 16 - s * 6, 24, cx + s * 2, 22, 'k')
        ellipse(g, cx + 0.5, 21.5, 3.5, 3, 'h', 'k', 'g')
        put(g, cx, 19, '.'); put(g, cx, 20, '0'); put(g, cx + s, 19, '.')
    ellipse(g, 16, 24.5, 8.5, 5, 'h', 'k', 'g')               # carapace
    for (x, y) in [(11, 23), (12, 24), (19, 22), (20, 23), (16, 26)]:
        put(g, x, y, 'I')                                     # corruption
    for x in (13, 18):                                        # yeux pédonculés
        line(g, x, 20, x, 18, 'k')
        put(g, x, 17, 'g'); put(g, x, 16, 'g'); put(g, x, 17, '0')
    paint(g, 14, 27, ['IIII'])                                # bouche
    outline(g)
    return bottom_align(g)


def crab_back(step):
    g = blank()
    crab_legs(g, step)
    for cx in (6, 25):
        ellipse(g, cx + 0.5, 22, 3, 2.5, 'k', 'I')
    ellipse(g, 16, 24.5, 8.5, 5, 'h', 'k', 'g')
    ellipse(g, 16, 23.5, 4.5, 2.6, '4', 'F', None)            # point faible exposé
    put(g, 14, 22, '3'); put(g, 15, 22, '3')
    outline(g)
    return bottom_align(g)


def crab_side(step):
    g = blank()
    for i, x in enumerate((12, 15, 18, 21)):
        dy = 1 if (i % 2) == step else 0
        line(g, x, 26, x - 1 + 2 * (i % 2), 30 - dy, 'k')
    ellipse(g, 17, 24, 7.5, 5, 'h', 'k', 'g')
    ellipse(g, 23, 23.5, 1.8, 2.2, '4', 'F')                  # dos tendre, visible de côté
    line(g, 11, 24, 7, 22, 'k')
    ellipse(g, 5.5, 21.5, 3.5, 3, 'h', 'k', 'g')
    put(g, 3, 20, '0'); put(g, 2, 20, '.')
    line(g, 13, 20, 13, 18, 'k')
    put(g, 13, 17, 'g'); put(g, 12, 17, '0'); put(g, 13, 16, 'g')
    for (x, y) in [(15, 22), (16, 23), (19, 25)]:
        put(g, x, y, 'I')
    outline(g)
    return bottom_align(g)


cs = [crab_side(0), crab_side(1)]
SHEETS['crabe_armure'] = build_enemy(OUT, 'crabe_armure', [
    ('move_down', [crab_front(0), crab_front(1)], 6.0, True),
    ('move_up', [crab_back(0), crab_back(1)], 6.0, True),
    ('move_left', cs, 6.0, True),
    ('move_right', [mirror(f) for f in cs], 6.0, True),
], red={'h': '#e2342c', 'k': '#961c28', 'g': '#f2c29a', 'I': '#241a22'})


# --- Ombre noyée : invisible dans le noir, la lanterne la révèle et l'immobilise (Spécial)
def ombre(phase, bob=0):
    g = blank()
    ellipse(g, 16, 13, 7, 7, 'n', 'I', 'b')
    rect(g, 9, 13, 22, 26, 'n')
    for y in range(13, 27):
        for x in (20, 21, 22):
            put(g, x, y, 'I')
        put(g, 10, y, 'b') if y < 20 else None
    for x in range(9, 23):                                   # franges qui ondulent
        ext = 1 + ((x + phase) // 2) % 2
        for e in range(1, ext + 1):
            put(g, x, 26 + e, 'n' if x < 20 else 'I')
    for (x, y) in [(7, 18), (8, 19), (24, 18), (23, 19), (7, 20), (24, 21)]:
        put(g, x, y, 'n')                                    # bras qui dégoulinent
    rect(g, 12, 11, 13, 13, 'g'); rect(g, 18, 11, 19, 13, 'g')
    put(g, 15, 16, 'I'); put(g, 16, 16, 'I'); put(g, 15, 17, 'I'); put(g, 16, 17, 'I')
    outline(g)
    g = bottom_align(g, 30)
    return shift(g, 0, -bob) if bob else g


REVEAL = {'n': 'b', 'I': 'n', 'b': 'g', 'g': 'K'}
SHEETS['ombre_noyee'] = build_enemy(OUT, 'ombre_noyee', [
    ('float', [ombre(0), ombre(1, 1), ombre(2), ombre(3, 1)], 5.0, True),
    ('revealed', [recolor(ombre(0), REVEAL)], 5.0, True),
], red={'n': '#5a0e18', 'I': '#241a22', 'b': '#961c28'})


# ===================================================================== CHÂTEAU
# --- Chevalier corrompu : pare de face, attaque en série (Chasseur)
KNIGHT_DOWN = [
    "................", "..............00", ".............04F", "..........0000F4",
    ".........0qqqqqq", "........0qpqqqqq", "........0qpqqqqq", "........0qqqqqqq",
    "........0qI00KK0", "........0qqqqIqq", "........0qqqqIqq", ".........0qqqqqq",
    "....00000IIIIIII", "..00qqqq0pqqqqqq", ".0qpqqqq0qpqqqqq", ".0qqqqqq0qqqqqKK",
    "..0qIqq0qqqqqKII", "..0qqq0qqqqqqqKK", "..0qIq0qqqqqqqqq", "..0qqq0qqqqqqqqq",
    "..0III0IIIIIIIII", "..0kkk0qqqqqqqqq", "..0kkk0qqqpqqqqq", "..00000qqqpqqqqq",
    ".......0qqqqqqqq", ".......0qqqqqq0.", ".......0qqpqqq0.", ".......0qqqqqq0.",
    ".......0qqqqqq0.", ".......0IIIIII0.", "......0IIIIIII0.", "......000000000.",
]
KNIGHT_UP = [
    "................", "..............00", ".............04F", "..........0000F4",
    ".........0qqqqqq", "........0qpqqqqq", "........0qpqqqqq", "........0qqqqqqq",
    "........0qqqqqqq", "........0qqqqqqq", "........0qqqqqqq", ".........0qqqqqq",
    "....00000IIIIIII", "..00qqqq0FFFFFFF", ".0qpqqqq0FFFFFFF", ".0qqqqqq0FF4FFFF",
    "..0qIqq0FFF4FFFF", "..0qqq0FFFFFFFFF", "..0qIq0FFFFF4FFF", "..0qqq0FFFFFFFFF",
    "..0III0FFFFFFFFF", "..0kkk0FFFF4FFFF", "..0kkk0FFFFFFFFF", "..00000FFFFFFFFF",
    ".......0FFFFFFFF", ".......0qqqqqq0.", ".......0qqpqqq0.", ".......0qqqqqq0.",
    ".......0qqqqqq0.", ".......0IIIIII0.", "......0IIIIIII0.", "......000000000.",
]
KNIGHT_LEFT = [
    "................................",
    ".................00.............",
    "................0F40............",
    "...........000000F40............",
    "..........0qqqqqqqF40...........",
    ".........0qpqqqqqqqF0...........",
    ".........0qpqqqqqqqq0...........",
    ".........0qqqqqqqqqq0...........",
    ".........0KK0qqqqqqq0...........",
    ".........0qqqqqqqqqq0...........",
    ".........0qqIqqqqqqq0...........",
    "..........0qqqqqqqq0............",
    "...........0IIIIIII0............",
    ".........0qqqqqqqqqqFF0.........",
    ".........0qpqqqqqqqqFFF0........",
    ".........0qqqq0qqqq0qFFF0.......",
    ".........0qqqq0qpq0qqFFF0.......",
    ".........0qqqq0qqq0qqFFF0.......",
    ".........0qqqq0qqq0qqFFF0.......",
    ".........0qqqq0qqq0qqFFFF0......",
    ".........0IIII0kkk0IIFFFF0......",
    ".........0qqqq0kkk0qqFFFF0......",
    ".........0qqqq00000qqFFFF0......",
    "..........0qqqqqqqqqqFFFF0......",
    "..........0qqqqqqqqqqFFF0.......",
    "...........0qqqqq0qqqq000.......",
    "...........0qqpqq0qqqq0.........",
    "...........0qqqqq0qqqq0.........",
    "...........0qqqqq0qqqq0.........",
    "...........0IIIII0IIII0.........",
    "..........0IIIIII0IIII0.........",
    "..........00000000000000........",
]
K_SHIELD = [""] * 14 + [
    "......................00000000..",
    ".....................0qqqqqqqI0.",
    ".....................0qpqqqqqI0.",
    ".....................0qqqKKqqI0.",
    ".....................0qqKIIKqI0.",
    ".....................0qqqKKqqI0.",
    ".....................0qqqqqqqI0.",
    ".....................0qqqqqqqI0.",
    "......................0qqqqqI0..",
    ".......................0qqqI0...",
    "........................000.....",
]
K_SWORD = [""] * 19 + [
    "...000",
    "...0K0",
    "..0kkk0",
    "..0kkk0",
    ".0KKKKK0",
    "..0ghh0",
    "..0ghh0",
    "..0ghh0",
    "..0ghh0",
    "..0ghh0",
    "...0g0",
    "....0",
]
K_FRONT = [(a if len(a) > len(b) else (b + a[len(b):]) if b else a) for a, b in
           zip(K_SHIELD + [""] * (32 - len(K_SHIELD)), K_SWORD + [""] * (32 - len(K_SWORD)))]
K_FRONT = [(sw.ljust(32, '.')[:8] + sh.ljust(32, '.')[8:]) for sh, sw in
           zip(K_SHIELD + [""] * (32 - len(K_SHIELD)), K_SWORD + [""] * (32 - len(K_SWORD)))]
K_SIDE_SHIELD = [""] * 13 + [
    ".....0000",
    "....0qpq0",
    "....0qqI0",
    "....0qKI0",
    "....0qKI0",
    "....0qqI0",
    "....0qqI0",
    "....0qqI0",
    "....0qqI0kkk0",
    "....0qqI00000",
    ".....000",
]
knight_views = {'down': KNIGHT_DOWN, 'up': KNIGHT_UP, 'left': KNIGHT_LEFT}
k_rows = humanoid_rows(knight_views, 25, 16,
                       {'down': K_FRONT, 'up': [r[::-1] for r in K_FRONT], 'left': K_SIDE_SHIELD})
SHEETS['chevalier_corrompu'] = build_enemy(OUT, 'chevalier_corrompu', humanoid_anims(k_rows),
                                           red={'q': '#961c28', 'p': '#e2342c', 'I': '#5a0e18',
                                                'F': '#241a22', '4': '#3a1a4a'})


# --- Œil de Morvath : sentinelle murale, la détruire à l'arc ouvre des portes (Tireur)
def oeil(state):
    g = blank()
    rect(g, 5, 5, 26, 26, 'k')
    for i in range(5, 27):
        put(g, i, 5, 'h'); put(g, 5, i, 'h')
        put(g, i, 26, 'I'); put(g, 26, i, 'I')
    for (x, y) in [(6, 7), (7, 6), (6, 8), (24, 25), (25, 24), (23, 25), (25, 6), (24, 6), (6, 24)]:
        put(g, x, y, 'q')                                     # corruption
    ellipse(g, 16, 16, 8.5, 6.5, 'I')
    if state == 'closed':
        line(g, 9, 16, 22, 16, 'q')
        for x in (11, 14, 17, 20):
            put(g, x, 17, '0')
    else:
        ry = 2.5 if state == 'half' else 5
        ellipse(g, 16, 16, 7.5, ry, 'g', 'h')
        ellipse(g, 16, 16, 3.2, min(ry, 3.2), 'K', '6')
        if state == 'shoot':
            ellipse(g, 16, 16, 1.6, 1.6, 'g')
            for (x, y) in [(16, 7), (16, 8), (16, 24), (16, 23), (7, 16), (24, 16), (9, 9), (22, 22), (22, 9), (9, 22)]:
                put(g, x, y, 'K')
        else:
            rect(g, 16, 14 if ry > 3 else 15, 16, 17 if ry > 3 else 16, '0')
            put(g, 15, 15, 'g')
    outline(g)
    return g


SHEETS['oeil_morvath'] = build_enemy(OUT, 'oeil_morvath', [
    ('closed', [oeil('closed')], 4.0, True),
    ('open', [oeil('closed'), oeil('half'), oeil('open')], 8.0, False),
    ('idle_open', [oeil('open')], 4.0, True),
    ('shoot', [oeil('shoot'), oeil('open')], 8.0, False),
], red={'K': '#e2342c', '6': '#961c28', 'q': '#961c28'})


# ===================================================================== PROJECTILES
def gland(rot):
    g = blank()
    ellipse(g, 16, 17, 2.6, 3.2, '6', 'B', '7')
    paint(g, 14, 13, ['AAAA', '.HH.'])
    put(g, 16, 12, 'H')
    outline(g)
    return g if rot == 0 else mirror(shift(g, 0, 0))


def orbe(pulse):
    g = blank()
    r = 3.2 + pulse * 0.8
    ellipse(g, 16, 16, r, r, 'q', 'I', 'p')
    ellipse(g, 16, 16, 1.5, 1.5, 'K')
    outline(g)
    return g


def caillou_proj():
    g = blank()
    ellipse(g, 16, 16, 2.6, 2.2, 'h', 'k', 'g')
    outline(g)
    return g


build_enemy(OUT, 'projectiles', [
    ('acorn', [gland(0), gland(1)], 10.0, True),
    ('morvath_orb', [orbe(0), orbe(1)], 10.0, True),
    ('pebble', [caillou_proj()], 1.0, True),
])


# ===================================================================== NUAGE DE MORT (commun)
def puff(stage):
    g = blank()
    if stage == 0:
        ellipse(g, 16, 22, 5, 5, 'g', 'h')
    elif stage == 1:
        for (cx, cy) in [(12, 21), (20, 21), (16, 17), (16, 25)]:
            ellipse(g, cx, cy, 4, 4, 'g', 'h')
    elif stage == 2:
        for (cx, cy) in [(9, 20), (23, 20), (16, 13), (16, 27), (11, 15), (21, 15)]:
            ellipse(g, cx, cy, 2.8, 2.8, 'g', 'h')
    else:
        for (cx, cy) in [(6, 19), (26, 19), (16, 10), (9, 12), (23, 12), (16, 29)]:
            ellipse(g, cx, cy, 1.5, 1.5, 'h')
    outline(g, 'k')
    return g


build_enemy(OUT, 'enemy_death', [
    ('poof', [puff(0), puff(1), puff(2), puff(3)], 12.0, False),
])
print('bestiaire ok :', ', '.join(SHEETS))
