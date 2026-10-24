"""Objets utilises en jeu : bombe posee, explosion, fleche en vol, icone de fleche (HUD).

Usage : python objets_utilises.py [dossier_apercu]
Produit dans art/items/ :
  bombe.png        128x32  4 cases 32x32 : 0-1 normales (1 = bombe 1 px plus basse, etincelle differente),
                           2-3 clignotement (corps rouge puis blanc, etincelle vive)
  explosion.png    576x96  6 cases 96x96 : flash, boule de feu, pleine taille (rayon ~40), anneau, fumee, braises
  fleche.png        32x32  1 case, fleche pointant vers la droite (le jeu la tourne)
  icone_fleche.png  24x24  icone HUD
Sans Pillow : mini encodeur PNG (zlib + struct). Palette du projet (engine.PALETTE) + 3 teintes chaudes
(orange, jaune, blanc chaud) pour le feu.
"""
import math
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'art', 'items')

PAL = {
    '.': None,
    '0': '#1b1420',  # contour
    '4': '#e2342c', 'F': '#961c28',   # rouge
    '6': '#8a5a34', 'B': '#5e3a22', '7': '#b06e40',  # cuir / bois
    'g': '#d8d4cc', 'h': '#9a948c', 'k': '#5c5650',  # gris metal
    'b': '#3c5a8a', 'n': '#263a5e',   # bleu (corps de bombe, comme l'icone)
    'I': '#241a22',
    'o': '#f08a28', 'y': '#f8d848', 'w': '#fff4d0',  # feu : orange, jaune, blanc chaud
    'm': '#6a2a1c',                   # brun-rouge sombre (bord du feu)
}


def rgba(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def blank(w, h):
    return [['.'] * w for _ in range(h)]


def put(g, x, y, c):
    if 0 <= y < len(g) and 0 <= x < len(g[0]):
        g[y][x] = c


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


def background(px, color=(70, 90, 60, 255)):
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


# ------------------------------- bombe --------------------------------------
def bomb_frame(dy, mode):
    """mode 0 et 1 normal, 2 rouge, 3 blanc."""
    g = blank(32, 32)
    cx, cy, r = 15.5, 22.5 + dy, 7.4
    body = {0: 'bnI', 1: 'bnI', 2: '4Fm', 3: 'wgh'}[mode]
    for y in range(32):
        for x in range(32):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                d = (x - cx + 2) ** 2 + (y - cy + 2) ** 2
                g[y][x] = body[0] if d < 40 else body[1] if d < 100 else body[2]
    hl = 'g' if mode < 2 else 'w'
    for x, y in ((11, 19 + dy), (12, 18 + dy), (11, 20 + dy), (13, 17 + dy)):
        put(g, x, y, hl)
    top = int(round(cy - r))
    for x in range(13, 19):                      # culot metal
        put(g, x, top, 'k')
        put(g, x, top + 1, 'h' if x < 16 else 'k')
    for i, (x, y) in enumerate(((16, top - 1), (17, top - 2), (17, top - 3), (18, top - 4))):
        put(g, x, y, 'B' if i % 2 else '6')      # meche
    sx, sy = 19, top - 5
    if mode == 0:
        pts = (((sx, sy), 'y'), ((sx - 1, sy), 'o'), ((sx + 1, sy - 1), 'o'))
    elif mode == 1:
        pts = (((sx, sy), 'o'), ((sx, sy - 1), 'y'), ((sx + 1, sy), 'y'), ((sx - 1, sy - 1), 'o'))
    else:
        col = 'w' if mode == 3 else 'y'
        pts = [((sx + a, sy + b), col) for a, b in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, -1))]
        pts += [((sx + a, sy + b), 'o') for a, b in ((-2, 0), (2, 0), (0, -2))]
    for (x, y), c in pts:
        put(g, x, y, c)
    outline(g)
    return g


# ------------------------------ explosion -----------------------------------
def lumpy_radius(a, base, seed):
    return base * (1 + 0.07 * math.sin(3 * a + seed) + 0.05 * math.sin(5 * a + 2 * seed) + 0.03 * math.sin(9 * a + seed))


def blob(g, cx, cy, R, seed, bands):
    n = len(g)
    for y in range(n):
        for x in range(n):
            dx, dy = x - cx, y - cy
            rr = lumpy_radius(math.atan2(dy, dx), R, seed)
            d = math.hypot(dx, dy)
            if d <= rr:
                t = d / rr
                for lim, c in bands:
                    if t <= lim:
                        g[y][x] = c
                        break


def hole(g, cx, cy, R, seed):
    n = len(g)
    for y in range(n):
        for x in range(n):
            dx, dy = x - cx, y - cy
            if math.hypot(dx, dy) < lumpy_radius(math.atan2(dy, dx), R, seed + 1.3):
                g[y][x] = '.'


def sparks(g, cx, cy, r0, r1, count, seed, col):
    for i in range(count):
        a = i * 2 * math.pi / count + seed
        r = r0 + (r1 - r0) * (0.5 + 0.5 * math.sin(i * 2.7 + seed))
        x, y = int(cx + r * math.cos(a)), int(cy + r * math.sin(a))
        for ox, oy in ((0, 0), (1, 0), (0, 1)):
            put(g, x + ox, y + oy, col)


def explosion_frames():
    C = 48
    fire = [(0.30, 'w'), (0.55, 'y'), (0.80, 'o'), (0.93, '4'), (1.0, 'm')]
    frames = []
    g = blank(96, 96)                                           # 0 flash
    blob(g, C, C, 13, 0.3, [(0.45, 'w'), (0.8, 'y'), (1.0, 'o')])
    sparks(g, C, C, 16, 22, 8, 0.2, 'y')
    frames.append(g)
    g = blank(96, 96)                                           # 1 boule de feu naissante
    blob(g, C, C, 27, 1.1, [(0.4, 'w'), (0.7, 'y'), (0.9, 'o'), (1.0, '4')])
    sparks(g, C, C, 30, 38, 10, 0.5, 'o')
    frames.append(g)
    g = blank(96, 96)                                           # 2 pleine taille (rayon ~40)
    blob(g, C, C, 40, 2.0, fire)
    for (ox, oy, R, s) in ((-18, -14, 11, 0.4), (19, -12, 10, 1.1), (-6, 20, 12, 2.2)):
        blob(g, C + ox, C + oy, R, s, [(0.5, 'y'), (1.0, 'o')])
    frames.append(g)
    g = blank(96, 96)                                           # 3 le centre se vide
    blob(g, C, C, 40, 3.1, [(0.45, 'o'), (0.78, 'o'), (0.93, '4'), (1.0, 'm')])
    blob(g, C, C, 14, 4.0, [(0.5, 'w'), (1.0, 'y')])
    sparks(g, C, C, 36, 44, 12, 0.9, 'y')
    frames.append(g)
    g = blank(96, 96)                                           # 4 anneau mince + fumee
    blob(g, C, C, 38, 4.2, [(0.7, 'k'), (0.84, 'h'), (0.93, '4'), (1.0, 'm')])
    hole(g, C, C, 28, 4.2)
    for (ox, oy, R, s) in ((-20, -18, 7, 0.4), (21, -16, 6, 1.7), (18, 20, 7, 2.5), (-22, 17, 6, 3.3)):
        blob(g, C + ox, C + oy, R, s, [(0.6, 'h'), (1.0, 'k')])
    sparks(g, C, C, 28, 44, 14, 1.3, 'o')
    frames.append(g)
    g = blank(96, 96)                                           # 5 fumee et braises
    for (ox, oy, R, s) in ((-22, -20, 8, 0.4), (23, -18, 7, 1.7), (20, 22, 8, 2.5), (-24, 18, 7, 3.3), (0, -30, 6, 4.1)):
        blob(g, C + ox, C + oy, R, s, [(0.5, 'k'), (1.0, 'I')])
    sparks(g, C, C, 20, 42, 12, 2.1, 'o')
    sparks(g, C, C, 12, 36, 6, 0.7, 'y')
    frames.append(g)
    return frames


# ------------------------------- fleche -------------------------------------
def arrow():
    g = blank(32, 32)
    for x in range(5, 25):                      # hampe 2 px (clair en haut, sombre en bas)
        g[15][x] = '7'
        g[16][x] = '6'
    for x, half in ((22, 3), (23, 3), (24, 2), (25, 2), (26, 1), (27, 1), (28, 0)):   # pointe metal
        for dy in range(-half, half + 2 if half else 2):
            g[15 + dy][x] = 'g' if dy <= 0 else 'h'
    for y in (14, 15, 16, 17):                  # empennage rouge, en V vers l'arriere
        for x in range(3, 8):
            pass
    for x, ys in ((3, (13, 18)), (4, (13, 18)), (5, (14, 17)), (6, (14, 17)), (7, (14, 17))):
        for y in ys:
            g[y][x] = '4' if y < 15 else 'F'
    for x in range(4, 9):
        g[15][x] = '4'
        g[16][x] = 'F'
    outline(g)
    return g


def icon_arrow():
    """Icone 24x24 (meme taille que art/ui/items/*.png) : fleche en diagonale, pointe en haut a droite.
    Axe : x + y = 24 ; u = x - y mesure la position le long de la fleche."""
    g = blank(24, 24)
    for y in range(24):
        for x in range(24):
            u, v = x - y, x + y - 24            # u le long de l'axe, v ecart a l'axe
            if -14 <= u <= 11 and v in (0, 1):  # hampe 2 px
                g[y][x] = '7' if v == 0 else '6'
            elif 12 <= u <= 21 and abs(v) <= (24 - u) // 4:  # pointe
                g[y][x] = 'g' if v <= 0 else 'h'
            elif -14 <= u <= -7 and 1 <= abs(v) <= 3 - (u + 14) // 4:  # plumes
                g[y][x] = '4' if v < 0 else 'F'
    put(g, 21, 3, 'w')
    outline(g)
    return g


def main():
    os.makedirs(OUT, exist_ok=True)
    bombe = sheet([to_rgba(bomb_frame(0, 0)), to_rgba(bomb_frame(1, 1)),
                   to_rgba(bomb_frame(0, 2)), to_rgba(bomb_frame(0, 3))])
    expl = sheet([to_rgba(f) for f in explosion_frames()])
    fl = to_rgba(arrow())
    ic = to_rgba(icon_arrow())
    save_png(os.path.join(OUT, 'bombe.png'), bombe)
    save_png(os.path.join(OUT, 'explosion.png'), expl)
    save_png(os.path.join(OUT, 'fleche.png'), fl)
    save_png(os.path.join(OUT, 'icone_fleche.png'), ic)
    if len(sys.argv) > 1:
        d = sys.argv[1]
        os.makedirs(d, exist_ok=True)
        save_png(os.path.join(d, 'apercu_bombe.png'), background(bombe), 8)
        save_png(os.path.join(d, 'apercu_explosion.png'), background(expl), 2)
        save_png(os.path.join(d, 'apercu_fleche.png'), background(fl), 8)
        save_png(os.path.join(d, 'apercu_icone.png'), background(ic), 16)


if __name__ == '__main__':
    main()
