"""PLAN du tileset du Temple des Racines (donjon 1) — Les Trois Sceaux.

Usage : python tools/sprites/temple_racines.py
Produit, à partir de la liste TILES ci-dessous (seule source de vérité) :
  art/tilesets/temple_racines.png          planche 8 colonnes x 16 lignes de tuiles 32x32, sans marge
  maps/tilesets/temple_racines.tsx         tileset Tiled (collisions + terrains)
  art/tilesets/temple_racines_plan.md      tableau de chaque tuile (id, rôle, calque, collision)
  art/tilesets/temple_racines_apercu.png   salle d'exemple 20x11 agrandie x3 (contrôle des raccords)

C'est un PLAN : aplats lisibles par famille, contour sombre, flèche = côté où se trouve le sol.
RÈGLE : ne jamais déplacer une tuile. Pour redessiner, modifier la fonction de dessin d'une
tuile en gardant son id ; pour en ajouter, utiliser une case « réserve » ou ajouter des lignes.

Coins (bits) : toujours dans l'ordre (HG, HD, BG, BD) = haut-gauche, haut-droite, bas-gauche,
bas-droite ; 1 = le terrain (mur, trou, eau...) occupe ce coin.
Sans Pillow : mini encodeur PNG (zlib + struct).
"""
import math
import os
import random
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
NAME = 'temple_racines'
T, COLS, ROWS = 32, 8, 16

# Palette : reprise des sprites existants (tools/sprites/engine.py, enemies.py, coffres.py)
HEX = dict(
    O='#1b1420', I='#241a22',                                 # contour, très sombre
    sol='#9a948c', joint='#5c5650', clair='#d8d4cc',          # dalles grises
    terre='#8a5a34', terre_s='#5e3a22', terre_c='#b06e40',    # terre battue
    racine='#7a4628', racine_s='#4a2a1c',                     # racines
    cap='#382e42', rim='#4e4058', face='#7a6a88', mur_c='#b8a8c0',  # murs violet-gris
    eau='#3c5a8a', prof='#263a5e', ecume='#b8a8c0',           # eau
    ronce='#241a22', ronce_m='#3a1a4a', ronce_c='#6a2a7a',    # ronces de Morvath
    vert='#5a8a3c', vert_c='#6a9a48', vert_s='#3a5a2c',       # mousse
    or_='#c8a050', orange='#f08a28',                          # feuilles mortes
    vase='#b06e40', vase_s='#8a5a34', vase_c='#d6c49c',       # terre cuite
    trou_face='#382e42',
)


def rgba(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


C = {k: rgba(v) for k, v in HEX.items()}


# ---------------------------------------------------------------- outils de dessin
def new(fill=None):
    return [[fill] * T for _ in range(T)]


def px(t, x, y, c):
    if 0 <= x < T and 0 <= y < T:
        t[y][x] = c


def rect(t, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(T - 1, y1) + 1):
        for x in range(max(0, x0), min(T - 1, x1) + 1):
            t[y][x] = c


def outline(t, c=None):
    c = c or C['O']
    pts = [(x, y) for y in range(T) for x in range(T) if t[y][x] is None and any(
        0 <= x + dx < T and 0 <= y + dy < T and t[y + dy][x + dx] not in (None, c)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        t[y][x] = c


def ellipse(t, cx, cy, rx, ry, c):
    for y in range(T):
        for x in range(T):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                t[y][x] = c


def line(t, x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        px(t, round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)


# Flèche 7x7 : « vers le bas » et « vers le bas-droite », tournées selon le besoin.
ARROW_DOWN = ["...#...", "...#...", "...#...", "#..#..#", ".#.#.#.", "..###..", "...#..."]
ARROW_DIAG = ["#......", ".#.....", "..#...#", "...#..#", "....#.#", ".....##", "..#####"]


def arrow(t, cx, cy, sx, sy, c):
    if sx == 0 and sy == 0:
        return
    if sx == 0 or sy == 0:
        pts = [(x, y) for y, r in enumerate(ARROW_DOWN) for x, ch in enumerate(r) if ch == '#']
        if sx == 0:
            pts = [(x, 6 - y if sy < 0 else y) for x, y in pts]
        else:
            pts = [(6 - y if sx < 0 else y, x) for x, y in pts]  # transposée = vers la droite
    else:
        pts = [(x, y) for y, r in enumerate(ARROW_DIAG) for x, ch in enumerate(r) if ch == '#']
        pts = [(6 - x if sx < 0 else x, 6 - y if sy < 0 else y) for x, y in pts]
    for x, y in pts:
        px(t, cx - 3 + x, cy - 3 + y, c)


CORNER_POS = ((-1, -1), (1, -1), (-1, 1), (1, 1))  # HG, HD, BG, BD


def toward_free(bits):
    """Direction (signe) vers les coins libres (sol) : sert à orienter la flèche repère."""
    vx = sum(p[0] * (-1 if b else 1) for p, b in zip(CORNER_POS, bits))
    vy = sum(p[1] * (-1 if b else 1) for p, b in zip(CORNER_POS, bits))
    return (vx > 0) - (vx < 0), (vy > 0) - (vy < 0)


# ---------------------------------------------------------------- 1. sol
def dalle(v):
    t = new(C['sol'])
    j = C['joint']
    if v == 0:      # 4 dalles carrées
        rect(t, 0, 0, 31, 0, j); rect(t, 0, 16, 31, 16, j)
        rect(t, 0, 0, 0, 31, j); rect(t, 16, 0, 16, 31, j)
        for x0, y0 in ((1, 1), (17, 1), (1, 17), (17, 17)):
            rect(t, x0, y0, x0 + 2, y0, C['clair'])
    elif v == 1:    # dalles longues en quinconce
        rect(t, 0, 0, 31, 0, j); rect(t, 0, 16, 31, 16, j)
        rect(t, 0, 0, 0, 15, j); rect(t, 16, 17, 16, 31, j)
        rect(t, 2, 2, 5, 2, C['clair']); rect(t, 18, 18, 21, 18, C['clair'])
    else:           # grande dalle gravée
        rect(t, 0, 0, 31, 0, j); rect(t, 0, 0, 0, 31, j)
        for a, b in ((8, 23),):
            rect(t, a, a, b, a, j); rect(t, a, b, b, b, j)
            rect(t, a, a, a, b, j); rect(t, b, a, b, b, j)
        rect(t, 15, 15, 16, 16, j)
        rect(t, 2, 2, 6, 2, C['clair'])
    return t


def dalle_fissuree(v):
    t = dalle(0)
    pts = [(3, 5), (8, 9), (7, 14), (12, 19), (18, 21), (22, 27), (28, 29)] if v == 0 else \
          [(26, 3), (21, 8), (23, 12), (17, 15), (13, 22), (6, 25)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(t, x0, y0, x1, y1, C['O'])
        line(t, x0 + 1, y0, x1 + 1, y1, C['joint'])
    if v == 1:
        line(t, 17, 15, 24, 20, C['O'])
    return t


def terre():
    t = new(C['terre'])
    rnd = random.Random(5)
    for _ in range(26):
        px(t, rnd.randrange(32), rnd.randrange(32), C['terre_s'])
    for _ in range(12):
        px(t, rnd.randrange(32), rnd.randrange(32), C['terre_c'])
    return t


def racine(kind):
    """Décor transparent posé sur le sol. h/v : se raccorde bord à bord avec ses voisines."""
    t = new()
    if kind in ('h', 'v'):
        for a in range(32):
            b = 15 + round(3 * math.sin(2 * math.pi * a / 32))
            for k, col in ((0, 'racine'), (1, 'racine'), (2, 'racine_s')):
                if kind == 'h':
                    px(t, a, b + k, C[col])
                else:
                    px(t, b + k, a, C[col])
        # radicelles
        for a, d in ((6, -1), (22, 1)):
            for k in range(4):
                b = 15 + round(3 * math.sin(2 * math.pi * a / 32)) + (d * (k + 2) if d > 0 else -k - 1)
                if d > 0:
                    b = b + 1
                if kind == 'h':
                    px(t, a + k, b, C['racine'])
                else:
                    px(t, b, a + k, C['racine'])
    else:  # touffe : nœud central et racines qui partent
        for (x1, y1) in ((2, 6), (29, 9), (5, 28), (27, 26), (16, 2)):
            line(t, 16, 17, x1, y1, C['racine'])
            line(t, 16, 18, x1, y1 + 1, C['racine_s'])
        ellipse(t, 16, 17, 5, 4, C['racine'])
        rect(t, 13, 19, 19, 20, C['racine_s'])
    outline(t)
    return t


# ---------------------------------------------------------------- 2. murs
def face(t, x0, x1):
    """Face avant d'un mur (côté sud, visible depuis la salle) entre les colonnes x0..x1."""
    rect(t, x0, 18, x1, 31, C['face'])
    rect(t, x0, 17, x1, 17, C['mur_c'])
    rect(t, x0, 24, x1, 24, C['rim'])
    for x in range(x0, x1 + 1):
        if x % 8 == 4:
            rect(t, x, 18, x, 23, C['rim'])
        if x % 8 == 0:
            rect(t, x, 25, x, 30, C['rim'])
    rect(t, x0, 31, x1, 31, C['O'])


def wall(bits, mark=True):
    """Tuile de mur entière (collision pleine). bits = coins occupés par le mur."""
    tl, tr, bl, br = bits
    t = new(C['cap'])
    for x, y in ((6, 5), (22, 9), (13, 21), (26, 26), (4, 27), (18, 3), (10, 13)):
        px(t, x, y, C['I'])
    n, s = not tl and not tr, not bl and not br
    w, e = not tl and not bl, not tr and not br
    if n:
        rect(t, 0, 0, 31, 3, C['rim']); rect(t, 0, 0, 31, 0, C['O'])
    if w:
        rect(t, 0, 0, 3, 31, C['rim']); rect(t, 0, 0, 0, 31, C['O'])
    if e:
        rect(t, 28, 0, 31, 31, C['rim']); rect(t, 31, 0, 31, 31, C['O'])
    if s:
        face(t, 0, 31)
    # coins isolés (le sol n'est que dans un coin)
    if not br and bl and tr:
        face(t, 28, 31)
    if not bl and br and tl:
        face(t, 0, 3)
    if not tr and tl and br:
        rect(t, 28, 0, 31, 3, C['rim']); rect(t, 28, 0, 31, 0, C['O']); rect(t, 31, 0, 31, 3, C['O'])
    if not tl and tr and bl:
        rect(t, 0, 0, 3, 3, C['rim']); rect(t, 0, 0, 3, 0, C['O']); rect(t, 0, 0, 0, 3, C['O'])
    if s and w:
        rect(t, 0, 17, 0, 31, C['O'])
    if s and e:
        rect(t, 31, 17, 31, 31, C['O'])
    if mark:
        sx, sy = toward_free(bits)
        arrow(t, 16 - 5 * sx, 16 - 5 * sy, sx, sy, C['mur_c'])
    if all(bits):  # mur plein : petite croix de repère
        line(t, 13, 13, 18, 18, C['rim']); line(t, 13, 18, 18, 13, C['rim'])
    return t


# ---------------------------------------------------------------- 3. portes (cadre seulement)
def porte(side):
    bits = {'haut': (1, 1, 0, 0), 'bas': (0, 0, 1, 1), 'gauche': (1, 0, 1, 0), 'droite': (0, 1, 0, 1)}[side]
    t = wall(bits, mark=False)
    if side in ('haut', 'bas'):
        rect(t, 6, 0, 25, 31, C['sol'])
        rect(t, 5, 0, 5, 31, C['O']); rect(t, 26, 0, 26, 31, C['O'])
        rect(t, 7, 0, 24, 0, C['joint']) if side == 'haut' else None
        arrow(t, 16, 16, 0, -1 if side == 'haut' else 1, C['joint'])
    else:
        rect(t, 0, 4, 31, 27, C['sol'])
        rect(t, 0, 3, 31, 3, C['O']); rect(t, 0, 28, 31, 28, C['O'])
        arrow(t, 16, 16, -1 if side == 'gauche' else 1, 0, C['joint'])
    return t


def porte_dessus(side):
    """Haut de l'encadrement, sur le calque Dessus : Brann passe dessous."""
    t = new()
    if side == 'haut':
        rect(t, 0, 0, 31, 8, C['cap']); rect(t, 0, 7, 31, 8, C['rim']); rect(t, 0, 9, 31, 9, C['O'])
        rect(t, 13, 1, 18, 6, C['mur_c'])
    elif side == 'bas':
        rect(t, 0, 23, 31, 31, C['cap']); rect(t, 0, 23, 31, 24, C['rim']); rect(t, 0, 22, 31, 22, C['O'])
        rect(t, 13, 25, 18, 30, C['mur_c'])
    else:
        rect(t, 0, 0, 31, 9, C['cap']); rect(t, 0, 8, 31, 9, C['rim']); rect(t, 0, 10, 31, 10, C['O'])
        x0 = 28 if side == 'gauche' else 0
        rect(t, x0, 0, x0 + 3, 9, C['rim'])
        rect(t, 13, 2, 18, 6, C['mur_c'])
    return t


# ---------------------------------------------------------------- 4. escaliers, trous
def escalier(montant):
    t = new(C['sol'])
    rect(t, 0, 0, 3, 31, C['cap']); rect(t, 28, 0, 31, 31, C['cap'])
    rect(t, 4, 0, 4, 31, C['O']); rect(t, 27, 0, 27, 31, C['O'])
    tons = ['clair', 'sol', 'face', 'rim', 'cap', 'I']
    for i in range(6):
        y0 = i * 5 + 1
        top = 'clair' if montant else tons[i]
        rect(t, 5, y0, 26, y0 + 2, C[top])
        rect(t, 5, y0 + 3, 26, y0 + 3, C['joint'] if montant else C['O'])
        rect(t, 5, y0 + 4, 26, y0 + 4, C['O'] if montant else C['I'])
    rect(t, 5, 31, 26, 31, C['sol'] if montant else C['O'])
    arrow(t, 16, 16, 0, -1 if montant else 1, C['O'] if montant else C['clair'])
    return t


def trou(bits):
    """Case de trou entière (on tombe partout dedans). bits = coins occupés par le trou."""
    tl, tr, bl, br = bits
    t = new(C['O'])
    for x, y in ((7, 20), (22, 14), (15, 26), (25, 25), (9, 10)):
        px(t, x, y, C['I'])
    n, s = not tl and not tr, not bl and not br
    w, e = not tl and not bl, not tr and not br
    if w:
        rect(t, 0, 0, 3, 31, C['trou_face']); rect(t, 4, 0, 4, 31, C['I'])
    if e:
        rect(t, 28, 0, 31, 31, C['trou_face']); rect(t, 27, 0, 27, 31, C['I'])
    if n:  # paroi du fond, bien visible en vue 3/4
        rect(t, 0, 0, 31, 11, C['trou_face']); rect(t, 0, 0, 31, 0, C['joint'])
        rect(t, 0, 6, 31, 6, C['I'])
        for x in range(0, 32, 8):
            rect(t, x + 4, 1, x + 4, 5, C['I']); rect(t, x, 7, x, 11, C['I'])
        rect(t, 0, 12, 31, 12, C['I'])
    if s:  # lèvre du bord proche
        rect(t, 0, 29, 31, 31, C['joint']); rect(t, 0, 28, 31, 28, C['clair'])
    if not all(bits):
        sx, sy = toward_free(bits)
        arrow(t, 16 - 4 * sx, 18 - 3 * sy, sx, sy, C['rim'])
    return t


# ---------------------------------------------------------------- 5. ronces
def ronces_bloc(v):
    t = new()
    for y in range(T):
        for x in range(T):
            if (abs(x - 15.5) / 15.2) ** 4 + (abs(y - 15.5) / 15.2) ** 4 <= 1:
                t[y][x] = C['ronce']
    rnd = random.Random(10 + v)
    for k in range(5):
        ph = rnd.random() * 6.3
        y0 = 4 + k * 6
        prev = None
        for x in range(2, 30):
            y = y0 + round(2.5 * math.sin(x / (3 + v) + ph))
            if t[min(31, max(0, y))][x] is not None:
                px(t, x, y, C['ronce_m'])
                if prev and abs(prev - y) > 1:
                    px(t, x, (prev + y) // 2, C['ronce_m'])
                prev = y
                if x % 5 == (k + v) % 5:
                    px(t, x, y - 1, C['ronce_c'])
    outline(t)
    return t


def ronces_sol(v):
    t = new()
    tracks = [((1, 22), (9, 17), (17, 21), (25, 15), (31, 18)), ((6, 4), (12, 11), (10, 19), (16, 27))] if v == 0 else \
             [((0, 9), (8, 12), (15, 7), (23, 11), (31, 8)), ((20, 30), (22, 22), (28, 17))]
    for tr in tracks:
        for (x0, y0), (x1, y1) in zip(tr, tr[1:]):
            line(t, x0, y0, x1, y1, C['ronce_m'])
            line(t, x0, y0 + 1, x1, y1 + 1, C['ronce'])
        for x, y in tr[1:-1]:
            px(t, x, y - 1, C['ronce_c']); px(t, x + 1, y - 2, C['ronce_c'])
    outline(t)
    return t


# ---------------------------------------------------------------- 6. eau
def eau(bits, profonde):
    """Bord au milieu de la tuile (terrain par coins de Tiled) : chaque quart vaut 16x16.
    Eau peu profonde : quarts libres = dalles. Eau profonde : quarts libres = eau peu profonde."""
    t = dalle(0) if not profonde else new(C['eau'])
    m = [[0] * T for _ in range(T)]
    for q, b in enumerate(bits):
        qx, qy = (q % 2) * 16, (q // 2) * 16
        if b:
            rect(t, qx, qy, qx + 15, qy + 15, C['prof'] if profonde else C['eau'])
            for y in range(qy, qy + 16):
                for x in range(qx, qx + 16):
                    m[y][x] = 1
        if b or profonde:  # vaguelettes dans les quarts d'eau
            c = C['eau'] if (b and profonde) else C['ecume']
            rect(t, qx + 4, qy + 5, qx + 8, qy + 5, c)
            rect(t, qx + 9, qy + 11, qx + 12, qy + 11, c)
    edge_in, edge_out = (C['O'], C['ecume']) if profonde else (C['ecume'], C['O'])
    todo = []
    for y in range(T):
        for x in range(T):
            nb = [m[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= x + dx < T and 0 <= y + dy < T]
            if m[y][x] and 0 in nb:
                todo.append((x, y, edge_in))
            elif not m[y][x] and 1 in nb:
                todo.append((x, y, edge_out))
    for x, y, c in todo:
        t[y][x] = c
    return t


def quarter_rects(bits):
    """Rectangles de collision couvrant les quarts occupés (fusionnés)."""
    q = [[bits[0], bits[1]], [bits[2], bits[3]]]
    if all(bits):
        return [(0, 0, 32, 32)]
    out, used = [], [[0, 0], [0, 0]]
    for r in range(2):
        if q[r][0] and q[r][1]:
            out.append((0, r * 16, 32, 16)); used[r] = [1, 1]
    for c in range(2):
        if q[0][c] and q[1][c] and not used[0][c] and not used[1][c]:
            out.append((c * 16, 0, 16, 32)); used[0][c] = used[1][c] = 1
    for r in range(2):
        for c in range(2):
            if q[r][c] and not used[r][c]:
                out.append((c * 16, r * 16, 16, 16))
    return out


# ---------------------------------------------------------------- 7. décor
def pierre_colonne(t, y0, y1):
    rect(t, 9, y0, 22, y1, C['clair'])
    rect(t, 19, y0, 22, y1, C['sol'])
    rect(t, 12, y0, 12, y1, C['sol'])
    rect(t, 16, y0, 16, y1, C['sol'])


def colonne(part):
    t = new()
    if part == 'haut':
        pierre_colonne(t, 9, 31)
        rect(t, 5, 2, 26, 8, C['clair']); rect(t, 5, 7, 26, 8, C['sol']); rect(t, 22, 2, 26, 8, C['sol'])
        rect(t, 6, 3, 25, 3, C['clair'])
    else:
        pierre_colonne(t, 0, 23)
        rect(t, 5, 24, 26, 29, C['clair']); rect(t, 5, 28, 26, 29, C['sol']); rect(t, 22, 24, 26, 29, C['sol'])
    outline(t)
    if part == 'base':  # ombre au sol
        rect(t, 6, 31, 25, 31, C['joint'])
    return t


def vase():
    t = new()
    ellipse(t, 15.5, 20, 10, 9.5, C['vase'])
    ellipse(t, 19, 23, 6, 6, C['vase_s'])
    ellipse(t, 15.5, 20, 10, 9.5, None) if False else None
    rect(t, 12, 6, 19, 11, C['vase']); rect(t, 17, 6, 19, 11, C['vase_s'])
    rect(t, 10, 4, 21, 6, C['vase_c']); rect(t, 12, 5, 19, 5, C['racine_s'])
    rect(t, 9, 16, 11, 19, C['vase_c'])
    rect(t, 7, 21, 24, 21, C['racine'])
    outline(t)
    return t


def cerf(part):
    """Statue de cerf en pierre blanche (Sylve) : bois et tête en haut, corps sur socle en bas."""
    t = new()
    if part == 'haut':
        for sgn in (-1, 1):  # bois
            cx = 16
            line(t, cx + sgn * 4, 24, cx + sgn * 11, 6, C['clair'])
            line(t, cx + sgn * 5, 24, cx + sgn * 12, 6, C['sol'])
            line(t, cx + sgn * 8, 15, cx + sgn * 14, 13, C['clair'])
            line(t, cx + sgn * 10, 10, cx + sgn * 6, 3, C['clair'])
            line(t, cx + sgn * 11, 6, cx + sgn * 14, 2, C['clair'])
        ellipse(t, 15.5, 27, 6, 6, C['clair'])
        rect(t, 18, 23, 21, 31, C['sol'])
        rect(t, 9, 23, 10, 25, C['clair']); rect(t, 21, 23, 22, 25, C['sol'])  # oreilles
        px(t, 13, 27, C['O']); px(t, 18, 27, C['O'])
    else:
        ellipse(t, 15.5, 6, 5.5, 7, C['clair'])          # museau / cou
        ellipse(t, 15.5, 14, 9, 6, C['clair'])           # poitrail
        ellipse(t, 19, 15, 5, 5, C['sol'])
        rect(t, 15, 0, 16, 2, C['sol'])
        rect(t, 6, 21, 25, 29, C['joint']); rect(t, 6, 21, 25, 22, C['sol']); rect(t, 22, 23, 25, 29, C['rim'])
        rect(t, 9, 18, 11, 20, C['clair']); rect(t, 20, 18, 22, 20, C['sol'])  # pattes
        px(t, 15, 9, C['O']); px(t, 16, 9, C['O'])
    outline(t)
    return t


def mousse(v):
    t = new()
    blobs = [(9, 10, 6), (18, 8, 5), (14, 17, 7), (24, 20, 5)] if v == 0 else [(7, 24, 5), (15, 22, 6), (23, 25, 4), (22, 9, 4)]
    for cx, cy, r in blobs:
        ellipse(t, cx, cy, r, r * 0.8, C['vert'])
    for cx, cy, r in blobs:
        ellipse(t, cx - r * 0.3, cy - r * 0.3, r * 0.4, r * 0.3, C['vert_c'])
    outline(t, C['vert_s'])
    return t


def feuilles(v):
    t = new()
    rnd = random.Random(30 + v)
    cols = ['vert_c', 'or_', 'orange'] if v == 0 else ['or_', 'orange', 'terre_c']
    for i in range(7):
        x, y = rnd.randrange(3, 27), rnd.randrange(3, 27)
        c = C[cols[i % 3]]
        rect(t, x, y, x + 2, y, c); rect(t, x + 1, y + 1, x + 3, y + 1, c)
    outline(t)
    return t


# ---------------------------------------------------------------- catalogue des tuiles
FULL = [(0, 0, 32, 32)]
COINS = {'hg': 'haut-gauche', 'hd': 'haut-droite', 'bg': 'bas-gauche', 'bd': 'bas-droite'}
TILES = {}      # id -> dict(nom, role, calque, collision, img, groupe)
WANG = {}       # nom du terrain -> {'colors': [...], 'tile': id, 'tiles': {id: (hg, hd, bg, bd)}}
GROUPS = []     # (titre, premier id, dernier id)


def add(i, nom, role, calque, collision, img, terrain=None):
    assert i not in TILES and 0 <= i < COLS * ROWS, i
    TILES[i] = dict(nom=nom, role=role, calque=calque, collision=collision, img=img)
    if terrain:
        name, corners = terrain
        WANG[name]['tiles'][i] = corners


def group(titre, first, last):
    GROUPS.append((titre, first, last))


WANG['Murs'] = dict(colors=[('mur', '#7a6a88')], tile=28, tiles={})
WANG['Trous'] = dict(colors=[('sol', '#9a948c'), ('trou', '#1b1420')], tile=58, tiles={})
WANG['Eau'] = dict(colors=[('sol', '#9a948c'), ('eau', '#3c5a8a')], tile=80, tiles={})
WANG['Eau profonde'] = dict(colors=[('eau', '#3c5a8a'), ('profonde', '#263a5e')], tile=96, tiles={})


def sol_corners(name):
    return [(name, (1, 1, 1, 1))]


# 1. Sol (lignes 0-1)
group('1. Sol', 0, 15)
for v, txt in enumerate(('4 dalles carrées', 'dalles longues en quinconce', 'grande dalle gravée')):
    add(v, f'dalle_{"abc"[v]}', f'Dalle de pierre, variante {"ABC"[v]} ({txt})', 'Sol', None, dalle(v))
    for w in ('Trous', 'Eau'):
        WANG[w]['tiles'][v] = (1, 1, 1, 1)
add(3, 'dalle_fissuree_a', 'Dalle fissurée (fissure en diagonale)', 'Sol', None, dalle_fissuree(0))
add(4, 'dalle_fissuree_b', 'Dalle fissurée (fissure en étoile)', 'Sol', None, dalle_fissuree(1))
add(5, 'terre', 'Sol de terre battue', 'Sol', None, terre())
add(6, 'racine_h', 'Racine horizontale (se raccorde à gauche et à droite)', 'Decor', None, racine('h'))
add(7, 'racine_v', 'Racine verticale (se raccorde en haut et en bas)', 'Decor', None, racine('v'))
add(8, 'racine_touffe', 'Nœud de racines (départ ou fin d\'une racine)', 'Decor', None, racine('t'))

# 2. Murs (lignes 2-4) — tuiles entières, collision pleine
group('2. Murs', 16, 39)
walls = [
    (16, 'mur_haut', 'Mur du haut de la salle : sol en dessous, face avant visible', (1, 1, 0, 0)),
    (17, 'mur_bas', 'Mur du bas de la salle : sol au-dessus', (0, 0, 1, 1)),
    (18, 'mur_gauche', 'Mur de gauche de la salle : sol à droite', (1, 0, 1, 0)),
    (19, 'mur_droite', 'Mur de droite de la salle : sol à gauche', (0, 1, 0, 1)),
    (20, 'mur_coin_int_hg', 'Coin intérieur haut-gauche (angle de salle) : sol seulement en bas-droite', (1, 1, 1, 0)),
    (21, 'mur_coin_int_hd', 'Coin intérieur haut-droite (angle de salle) : sol seulement en bas-gauche', (1, 1, 0, 1)),
    (22, 'mur_coin_int_bg', 'Coin intérieur bas-gauche (angle de salle) : sol seulement en haut-droite', (1, 0, 1, 1)),
    (23, 'mur_coin_int_bd', 'Coin intérieur bas-droite (angle de salle) : sol seulement en haut-gauche', (0, 1, 1, 1)),
    (24, 'mur_coin_ext_hg', 'Coin extérieur haut-gauche d\'un bloc de mur posé dans la salle : mur seulement en bas-droite', (0, 0, 0, 1)),
    (25, 'mur_coin_ext_hd', 'Coin extérieur haut-droite d\'un bloc de mur : mur seulement en bas-gauche', (0, 0, 1, 0)),
    (26, 'mur_coin_ext_bg', 'Coin extérieur bas-gauche d\'un bloc de mur : mur seulement en haut-droite', (0, 1, 0, 0)),
    (27, 'mur_coin_ext_bd', 'Coin extérieur bas-droite d\'un bloc de mur : mur seulement en haut-gauche', (1, 0, 0, 0)),
    (28, 'mur_plein', 'Mur plein (intérieur d\'un mur épais, rien de visible autour)', (1, 1, 1, 1)),
    (29, 'mur_diag_a', 'Mur en diagonale (mur en haut-gauche et bas-droite) — complète le terrain', (1, 0, 0, 1)),
    (30, 'mur_diag_b', 'Mur en diagonale (mur en haut-droite et bas-gauche) — complète le terrain', (0, 1, 1, 0)),
]
for i, nom, role, bits in walls:
    add(i, nom, role, 'Murs', FULL, wall(bits), ('Murs', bits))

# 3. Portes (lignes 5-6)
group('3. Ouvertures de porte', 40, 55)
for k, side in enumerate(('haut', 'bas', 'gauche', 'droite')):
    if side in ('haut', 'bas'):
        col = [(0, 0, 6, 32), (26, 0, 6, 32)]
        txt = 'passage de 20 px au centre'
    else:
        col = [(0, 0, 32, 4), (0, 28, 32, 4)]
        txt = 'passage de 24 px au centre'
    add(40 + k, f'porte_{side}', f'Ouverture dans le mur {side} (remplace une tuile mur_{side}) ; {txt}, '
        f'l\'objet Porte se pose dessus', 'Murs', col, porte(side))
for k, side in enumerate(('haut', 'bas', 'gauche', 'droite')):
    add(44 + k, f'porte_{side}_dessus', f'Haut de l\'encadrement de porte_{side}, même case que porte_{side}',
        'Dessus', None, porte_dessus(side))

# 4. Escaliers et trous (lignes 7-8)
group('4. Escaliers et trous', 56, 71)
add(56, 'escalier_montant', 'Escalier qui monte (vers le haut de l\'écran) ; la transition est un objet Sortie', 'Sol', None, escalier(True))
add(57, 'escalier_descendant', 'Escalier qui descend (vers le bas de l\'écran) ; la transition est un objet Sortie', 'Sol', None, escalier(False))
holes = [
    (58, 'trou', 'Trou : on tombe dans toute la case', (1, 1, 1, 1)),
    (59, 'trou_bord_haut', 'Bord haut d\'un trou (sol au-dessus) : paroi du fond visible', (0, 0, 1, 1)),
    (60, 'trou_bord_bas', 'Bord bas d\'un trou (sol en dessous)', (1, 1, 0, 0)),
    (61, 'trou_bord_gauche', 'Bord gauche d\'un trou (sol à gauche)', (0, 1, 0, 1)),
    (62, 'trou_bord_droite', 'Bord droit d\'un trou (sol à droite)', (1, 0, 1, 0)),
    (63, 'trou_coin_hg', 'Coin haut-gauche d\'un trou rectangulaire', (0, 0, 0, 1)),
    (64, 'trou_coin_hd', 'Coin haut-droite d\'un trou rectangulaire', (0, 0, 1, 0)),
    (65, 'trou_coin_bg', 'Coin bas-gauche d\'un trou rectangulaire', (0, 1, 0, 0)),
    (66, 'trou_coin_bd', 'Coin bas-droite d\'un trou rectangulaire', (1, 0, 0, 0)),
]
for i, nom, role, bits in holes:
    add(i, nom, role, 'Sol', None, trou(bits), ('Trous', tuple(2 if b else 1 for b in bits)))

# 5. Ronces (ligne 9)
group('5. Ronces noires de Morvath', 72, 79)
add(72, 'ronces_bloc_a', 'Bloc de ronces noires (infranchissable)', 'Murs', FULL, ronces_bloc(0))
add(73, 'ronces_bloc_b', 'Bloc de ronces noires, variante', 'Murs', FULL, ronces_bloc(1))
add(74, 'ronces_sol_a', 'Ronces rampantes au sol (décor)', 'Decor', None, ronces_sol(0))
add(75, 'ronces_sol_b', 'Ronces rampantes au sol, variante', 'Decor', None, ronces_sol(1))

# 6. Eau (lignes 10-13) — bord au milieu de la tuile
group('6. Eau', 80, 111)
EDGES = [('bord_haut', 'sol au-dessus', (0, 0, 1, 1)), ('bord_bas', 'sol en dessous', (1, 1, 0, 0)),
         ('bord_gauche', 'sol à gauche', (0, 1, 0, 1)), ('bord_droite', 'sol à droite', (1, 0, 1, 0))]
CREUX = [('creux_hg', (0, 1, 1, 1)), ('creux_hd', (1, 0, 1, 1)), ('creux_bg', (1, 1, 0, 1)), ('creux_bd', (1, 1, 1, 0))]
POINTES = [('coin_hg', (0, 0, 0, 1)), ('coin_hd', (0, 0, 1, 0)), ('coin_bg', (0, 1, 0, 0)), ('coin_bd', (1, 0, 0, 0))]
for base, prefix, profonde, autre, wname in ((80, 'eau', False, 'sol', 'Eau'),
                                              (96, 'eau_profonde', True, 'eau peu profonde', 'Eau profonde')):
    label = 'Eau profonde' if profonde else 'Eau peu profonde'
    lieu = 'Murs' if profonde else 'Sol'

    def col(bits):
        return quarter_rects(bits) if profonde else None

    def put(i, nom, role, bits):
        add(i, nom, role, lieu, col(bits), eau(bits, profonde), (wname, tuple(2 if b else 1 for b in bits)))

    put(base, prefix, f'{label}, case entière' + (' (infranchissable)' if profonde else ' (Brann la traverse)'), (1, 1, 1, 1))
    for k, (n, txt, bits) in enumerate(EDGES):
        put(base + 1 + k, f'{prefix}_{n}', f'{label} : {n.replace("_", " ")} ({txt.replace("sol", autre)})', bits)
    for k, (n, bits) in enumerate(CREUX):
        put(base + 5 + k, f'{prefix}_{n}', f'{label} : coin rentrant, {autre} seulement en {COINS[n[-2:]]}', bits)
    for k, (n, bits) in enumerate(POINTES):
        put(base + 9 + k, f'{prefix}_{n}', f'{label} : coin {COINS[n[-2:]]} d\'une étendue rectangulaire '
            f'({label.lower()} seulement dans le quart opposé)', bits)
WANG['Eau profonde']['tiles'][80] = (1, 1, 1, 1)

# 7. Décor (lignes 14-15)
group('7. Décor', 112, 127)
add(112, 'colonne_haut', 'Haut de colonne (chapiteau), case au-dessus de colonne_base', 'Dessus', None, colonne('haut'))
add(113, 'colonne_base', 'Base de colonne (fût et socle)', 'Murs', FULL, colonne('base'))
add(114, 'vase', 'Vase de terre cuite (décor, ne se casse pas : un vase cassable serait un objet)', 'Murs', FULL, vase())
add(115, 'cerf_haut', 'Statue de cerf : bois et tête, case au-dessus de cerf_base', 'Dessus', None, cerf('haut'))
add(116, 'cerf_base', 'Statue de cerf : corps sur son socle', 'Murs', FULL, cerf('base'))
add(117, 'mousse_a', 'Mousse au sol', 'Decor', None, mousse(0))
add(118, 'mousse_b', 'Mousse au sol, variante', 'Decor', None, mousse(1))
add(119, 'feuilles_a', 'Feuilles tombées', 'Decor', None, feuilles(0))
add(120, 'feuilles_b', 'Feuilles mortes, variante', 'Decor', None, feuilles(1))


# ---------------------------------------------------------------- export PNG
def save_png(path, pix, scale=1):
    h, w = len(pix), len(pix[0])
    raw = bytearray()
    for y in range(h):
        row = bytearray()
        for x in range(w):
            row += bytes(pix[y][x] or (0, 0, 0, 0)) * scale
        for _ in range(scale):
            raw.append(0)
            raw += row

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(data)


def blit(dst, img, ox, oy):
    for y in range(T):
        for x in range(T):
            if img[y][x] is not None:
                dst[oy + y][ox + x] = img[y][x]


def build_sheet():
    sheet = [[None] * (COLS * T) for _ in range(ROWS * T)]
    for i, d in TILES.items():
        blit(sheet, d['img'], (i % COLS) * T, (i // COLS) * T)
    return sheet


# ---------------------------------------------------------------- export TSX
def collision_xml(rects):
    s = '  <objectgroup draworder="index" id="2">\n'
    for k, (x, y, w, h) in enumerate(rects, 1):
        s += f'   <object id="{k}" x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
    return s + '  </objectgroup>\n'


def wangid(c):
    hg, hd, bg, bd = c  # ordre Tiled : haut, HD, droite, BD, bas, BG, gauche, HG
    return f'0,{hd},0,{bd},0,{bg},0,{hg}'


def build_tsx():
    s = ('<?xml version="1.0" encoding="UTF-8"?>\n'
         f'<tileset version="1.10" tiledversion="1.12.2" name="{NAME}" tilewidth="{T}" tileheight="{T}" '
         f'tilecount="{COLS * ROWS}" columns="{COLS}">\n'
         f' <image source="../../art/tilesets/{NAME}.png" width="{COLS * T}" height="{ROWS * T}"/>\n')
    for i in sorted(TILES):
        if TILES[i]['collision']:
            s += f' <tile id="{i}">\n' + collision_xml(TILES[i]['collision']) + ' </tile>\n'
    s += ' <wangsets>\n'
    for name, w in WANG.items():
        s += f'  <wangset name="{name}" type="corner" tile="{w["tile"]}">\n'
        for cname, ccol in w['colors']:
            s += f'   <wangcolor name="{cname}" color="{ccol}" tile="-1" probability="1"/>\n'
        for i in sorted(w['tiles']):
            s += f'   <wangtile tileid="{i}" wangid="{wangid(w["tiles"][i])}"/>\n'
        s += '  </wangset>\n'
    s += ' </wangsets>\n</tileset>\n'
    return s


# ---------------------------------------------------------------- export plan.md
def collision_txt(r):
    if not r:
        return 'aucune'
    if r == FULL:
        return 'pleine'
    return 'partielle : ' + ' ; '.join(f'{x},{y} {w}×{h}' for x, y, w, h in r)


def build_md():
    out = [f'# Plan du tileset `{NAME}` — Temple des Racines (donjon 1)', '',
           '> Fichier généré par `tools/sprites/temple_racines.py` : modifier le script, pas ce fichier.', '',
           f'- Image : `art/tilesets/{NAME}.png`, {COLS * T}×{ROWS * T} px, {COLS} colonnes × {ROWS} lignes '
           f'de tuiles 32×32, sans marge ni espacement ({COLS * ROWS} cases).',
           f'- Tileset Tiled : `maps/tilesets/{NAME}.tsx` (collisions et terrains déjà définis).',
           '- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de '
           'numéro : le dessin final sera fait au même emplacement. Les cases « réserve » sont vides et '
           'serviront aux ajouts.',
           '- C\'est un **plan** : aplats par famille (gris = sol, violet-gris = murs, noir = trous, bleu = eau, '
           'noir-violet = ronces), contour sombre. La **flèche** sur les murs, portes, escaliers et trous montre '
           'le côté où se trouve le sol (ou la direction de sortie).',
           '- Collision : en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche).', '']
    for titre, a, b in GROUPS:
        out += [f'## {titre}', '', '| N° | Nom | Rôle | Calque | Collision |', '| --- | --- | --- | --- | --- |']
        reserve = []
        for i in range(a, b + 1):
            if i in TILES:
                d = TILES[i]
                out.append(f'| {i} | `{d["nom"]}` | {d["role"]} | {d["calque"]} | {collision_txt(d["collision"])} |')
            else:
                reserve.append(i)
        if reserve:
            out.append(f'| {reserve[0]}–{reserve[-1]} | — | réserve (vide) | — | — |'
                       if reserve == list(range(reserve[0], reserve[-1] + 1)) else
                       f'| {", ".join(map(str, reserve))} | — | réserve (vide) | — | — |')
        out.append('')
    out += [
        '## Terrains Tiled (autotiling)', '',
        'Quatre terrains « par coins » (*corner set*) sont définis dans le `.tsx`. Dans Tiled : panneau '
        '**Terrains**, choisir le terrain puis peindre avec le pinceau de terrain (T).', '',
        '| Terrain | Couleurs | Calque | Tuiles |', '| --- | --- | --- | --- |',
        '| `Murs` | `mur` (le reste = vide) | Murs | 16–30 |',
        '| `Trous` | `sol`, `trou` | Sol | 0–2 (sol), 58–66 |',
        '| `Eau` | `sol`, `eau` | Sol | 0–2 (sol), 80–92 |',
        '| `Eau profonde` | `eau`, `profonde` | Murs | 80 (eau), 96–108 |', '',
        '- **Murs** : une seule couleur, `mur`. Le sol n\'en fait pas partie (il est peint sur le calque Sol), '
        'pour que le pinceau ne pose jamais de dalle sur le calque Murs. Pour une salle de 20×11 entourée d\'un '
        'mur d\'une tuile, peindre `mur` sur tous les coins du pourtour : on obtient exactement l\'anneau '
        'mur_haut / mur_bas / mur_gauche / mur_droite + les 4 coins intérieurs. Un seul coin peint au milieu '
        'de la salle donne un bloc de 2×2 tuiles (les 4 coins extérieurs). Les tuiles de mur sont entières : '
        'toute la case bloque.',
        '- **Trous** : comme les murs, toutes les tuiles du terrain sont entièrement « trou » (on tombe partout '
        'dedans). Seules les formes rectangulaires sont prévues (pas de coin rentrant) ; les coins rentrants '
        'pourront être ajoutés dans la réserve 67–71 si besoin.',
        '- **Eau / Eau profonde** : le bord passe au **milieu** de la tuile (chaque quart de 16×16 est soit de '
        'l\'eau, soit l\'autre terrain). L\'eau peu profonde est sur le calque Sol, sans collision. L\'eau '
        'profonde est posée sur le calque **Murs** (par-dessus l\'eau peu profonde) car elle bloque : sa '
        'collision couvre exactement ses quarts d\'eau profonde. Il manque volontairement les deux tuiles en '
        'diagonale (deux quarts opposés) : éviter de les demander au pinceau.',
        '- Les dalles fissurées (3, 4) et la terre (5) ne sont pas dans les terrains : à poser à la main.', '',
        '## Comment assembler', '',
        '- **Porte** : remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` '
        'dans la **même case** du calque Dessus, puis l\'objet `Porte` (calque Objets) par-dessus. La porte '
        'elle-même (battant, grille, serrure) est un sprite à part dans `art/puzzles/`.',
        '- **Colonne** et **statue de cerf** : 2 cases l\'une au-dessus de l\'autre. `*_base` sur Murs '
        '(collision pleine), `*_haut` juste au-dessus sur Dessus (Brann passe derrière).',
        '- **Escaliers** : simple tuile de sol ; le changement de carte se fait avec un objet `Sortie` posé dessus.',
        '- **Trou** : la tuile ne fait rien toute seule (pas de collision). La chute est à gérer côté jeu '
        '(voir « Besoins » ci-dessous).',
        '- Hors tileset (objets de gameplay, sprites séparés dans `art/puzzles/`) : coffres, blocs poussables, '
        'interrupteurs, torches, portes, statue du corbeau.', '',
        '## Besoins et propositions', '',
        '- **Détection des trous** (développeur) : proposer une convention, par exemple une propriété de tuile '
        '`trou` (bool) dans le `.tsx`, lue en jeu via les custom data du TileSet importé, ou un objet `Trou` '
        'dans le calque Objets. Rien n\'est encore défini dans `CLAUDE.md`, donc rien n\'est mis dans le `.tsx`.',
        '- **Palette** : la palette actuelle n\'a pas de bleu clair ; l\'eau peu profonde utilise le bleu des '
        'sprites (`#3c5a8a`) et l\'eau profonde le bleu sombre (`#263a5e`). Un bleu clair serait utile au dessin final.', '',
        '## Palette utilisée', '',
        '| Rôle | Couleurs |', '| --- | --- |',
        '| Contour | `#1b1420`, `#241a22` |', '| Dalles | `#9a948c`, `#5c5650`, `#d8d4cc` |',
        '| Terre, racines | `#8a5a34`, `#5e3a22`, `#b06e40`, `#7a4628`, `#4a2a1c` |',
        '| Murs | `#382e42` (dessus), `#4e4058` (rebord), `#7a6a88` (face avant), `#b8a8c0` (arête claire) |',
        '| Eau | `#3c5a8a` (peu profonde), `#263a5e` (profonde), `#b8a8c0` (écume) |',
        '| Ronces | `#241a22`, `#3a1a4a`, `#6a2a7a` |',
        '| Mousse, feuilles | `#5a8a3c`, `#6a9a48`, `#3a5a2c`, `#c8a050`, `#f08a28` |',
        '| Vase | `#b06e40`, `#8a5a34`, `#d6c49c` |', '']
    return '\n'.join(out)


# ---------------------------------------------------------------- aperçu : salle 20x11
def corner_resolve(corners, x, y):
    return (corners.get((x, y), 0), corners.get((x + 1, y), 0), corners.get((x, y + 1), 0), corners.get((x + 1, y + 1), 0))


def by_bits(wname, bits):
    for i, c in WANG[wname]['tiles'].items():
        if c == bits and i >= 16:
            return i
    raise KeyError((wname, bits))


def build_preview():
    W, H = 20, 11
    layers = {k: {} for k in ('Sol', 'Decor', 'Murs', 'Dessus')}
    rnd = random.Random(7)
    for y in range(H):
        for x in range(W):
            layers['Sol'][(x, y)] = rnd.choice([0, 0, 0, 1, 1, 2])
    for x, y in ((6, 1), (15, 8), (3, 4), (12, 4)):
        layers['Sol'][(x, y)] = 3
    layers['Sol'][(9, 4)] = 4
    for x, y in ((13, 9), (14, 9), (15, 9), (14, 8)):
        layers['Sol'][(x, y)] = 5
    # murs : pourtour + bloc 2x2 + bloc 3x2
    mur = {}
    for x in range(W + 1):
        mur[(x, 0)] = mur[(x, H)] = 1
    for y in range(H + 1):
        mur[(0, y)] = mur[(W, y)] = 1
    mur[(5, 3)] = 1
    mur[(14, 3)] = mur[(15, 3)] = 1
    for y in range(H):
        for x in range(W):
            b = corner_resolve(mur, x, y)
            if any(b):
                layers['Murs'][(x, y)] = by_bits('Murs', b)
    # portes
    for (x, y), k in (((10, 0), 0), ((10, 10), 1), ((0, 5), 2), ((19, 5), 3)):
        layers['Murs'][(x, y)] = 40 + k
        layers['Dessus'][(x, y)] = 44 + k
    # mare : eau peu profonde en L + eau profonde au centre
    eaux = {(x, y): 1 for x in range(3, 9) for y in range(6, 10)}
    eaux.update({(x, y): 1 for x in range(9, 11) for y in range(8, 10)})
    prof = {(x, y): 1 for x in range(5, 7) for y in range(7, 9)}
    for y in range(H):
        for x in range(W):
            b = corner_resolve(eaux, x, y)
            if any(b) and (x, y) not in layers['Murs']:
                layers['Sol'][(x, y)] = by_bits('Eau', tuple(2 if v else 1 for v in b))
            b = corner_resolve(prof, x, y)
            if any(b):
                layers['Murs'][(x, y)] = by_bits('Eau profonde', tuple(2 if v else 1 for v in b))
    # trou rectangulaire
    trous = {(x, y): 1 for x in range(13, 16) for y in range(6, 8)}
    for y in range(H):
        for x in range(W):
            b = corner_resolve(trous, x, y)
            if any(b):
                layers['Sol'][(x, y)] = by_bits('Trous', tuple(2 if v else 1 for v in b))
    # décor, escaliers, ronces, colonnes, statue
    layers['Sol'][(17, 1)] = 57
    layers['Sol'][(18, 1)] = 56
    for pos, i in (((15, 4), 6), ((16, 4), 6), ((17, 4), 8), ((7, 2), 7), ((7, 3), 7), ((7, 4), 8),
                   ((12, 2), 74), ((10, 3), 75), ((1, 9), 117), ((1, 8), 118), ((2, 1), 117),
                   ((17, 6), 119), ((11, 6), 120), ((16, 9), 119)):
        layers['Decor'][pos] = i
    for pos, i in (((11, 2), 72), ((11, 3), 73), ((12, 3), 72), ((1, 1), 114), ((18, 9), 114),
                   ((2, 3), 113), ((17, 8), 113), ((8, 2), 116)):
        layers['Murs'][pos] = i
    for pos, i in (((2, 2), 112), ((17, 7), 112), ((8, 1), 115)):
        layers['Dessus'][pos] = i
    img = [[C['O']] * (W * T) for _ in range(H * T)]
    for name in ('Sol', 'Decor', 'Murs', 'Dessus'):
        for (x, y), i in layers[name].items():
            blit(img, TILES[i]['img'], x * T, y * T)
    # marge de 8 px en bas (écran 640x360)
    img += [[C['O']] * (W * T) for _ in range(8)]
    return img


def main():
    os.makedirs(os.path.join(ROOT, 'art', 'tilesets'), exist_ok=True)
    save_png(os.path.join(ROOT, 'art', 'tilesets', f'{NAME}.png'), build_sheet())
    with open(os.path.join(ROOT, 'maps', 'tilesets', f'{NAME}.tsx'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_tsx())
    with open(os.path.join(ROOT, 'art', 'tilesets', f'{NAME}_plan.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_md())
    save_png(os.path.join(ROOT, 'art', 'tilesets', f'{NAME}_apercu.png'), build_preview(), scale=3)
    print(f'{len(TILES)} tuiles dessinées sur {COLS * ROWS} cases.')


if __name__ == '__main__':
    main()
