"""PNJ du village (phase 6) : poule, villageois apeuré, villageois mineur.

Sans Pillow : un petit « faux PIL » (Image.new / load / save) encode les PNG avec zlib+struct,
ce qui permet de réutiliser engine.py (marche dérivée de l'idle, .tres, .json) tel quel.
Les sprites sont dessinés avec de petites formes (rectangles), le contour est ajouté automatiquement.

Usage : python3 pnj_village.py [dossier art/characters] [dossier d'aperçus]
"""
import sys, os, types, zlib, struct, json


# ---------- PNG sans bibliothèque ----------
def write_png(path, w, h, pix):
    raw = b''.join(b'\x00' + b''.join(bytes(pix[y][x]) for x in range(w)) for y in range(h))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
    open(path, 'wb').write(data)


class _Img:
    def __init__(self, size):
        self.width, self.height = size
        self.p = [[(0, 0, 0, 0)] * self.width for _ in range(self.height)]

    def load(self):
        outer = self

        class A:
            def __setitem__(s, k, v): outer.p[k[1]][k[0]] = v
        return A()

    def save(self, path): write_png(path, self.width, self.height, self.p)


_pil = types.ModuleType('PIL')
_im = types.ModuleType('PIL.Image')
_im.new = lambda mode, size, color=(0, 0, 0, 0): _Img(size)
_pil.Image = _im
sys.modules['PIL'] = _pil
sys.modules['PIL.Image'] = _im
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'art', 'characters')
PREV = sys.argv[2] if len(sys.argv) > 2 else None


# ---------- dessin par formes ----------
class Canvas:
    def __init__(self):
        self.g = [['.'] * 32 for _ in range(32)]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < 32 and 0 <= y < 32:
                    self.g[y][x] = c

    def px(self, x, y, c):
        self.rect(x, y, x, y, c)

    def round(self, x0, y0, x1, y1, c):
        self.rect(x0, y0, x1, y1, c)
        for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            self.px(x, y, '.')

    def outline(self):
        src = [r[:] for r in self.g]
        for y in range(32):
            for x in range(32):
                if src[y][x] != '.':
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 32 and 0 <= ny < 32 and src[ny][nx] not in ('.', '0'):
                        self.g[y][x] = '0'
                        break
        return self

    def rows(self):
        return [''.join(r) for r in self.g]


def sym(cv, x0, y0, x1, y1, c, rnd=False):
    """Forme symétrique autour de l'axe (colonnes 15|16)."""
    f = cv.round if rnd else cv.rect
    f(x0, y0, x1, y1, c)
    f(31 - x1, y0, 31 - x0, y1, c)


# ---------- villageois ----------
def villager(kind, view):
    cv = Canvas()
    apeure = kind == 'apeure'
    body = '2' if apeure else '6'
    shade = '9' if apeure else 'B'
    belt = '6' if apeure else 'D'
    if view == 'left':
        cv.rect(12, 27, 15, 28, '5'); cv.rect(17, 27, 20, 28, 'J')
        cv.rect(10, 29, 15, 30, 'A'); cv.rect(17, 29, 21, 30, 'H')
        cv.round(11, 17, 21, 26, body); cv.rect(11, 24, 21, 26, shade); cv.rect(11, 23, 21, 23, belt)
        cv.round(9, 8, 21, 17, '3'); cv.rect(8, 12, 8, 14, '3'); cv.rect(20, 10, 21, 17, 'E')
        if apeure:
            cv.rect(11, 11, 12, 13, 'g'); cv.px(11, 12, 'e')
            cv.rect(10, 10, 12, 10, '1')
            cv.rect(10, 15, 11, 16, 'I')
            cv.round(8, 4, 22, 10, 'b'); cv.rect(8, 9, 22, 10, 'n')
            cv.rect(20, 7, 24, 11, 'b'); cv.rect(18, 2, 21, 5, 'b')
            cv.round(12, 18, 16, 22, body); cv.rect(11, 22, 14, 23, '3')
            cv.px(7, 10, 'b')
        else:
            cv.px(11, 12, 'e'); cv.rect(10, 11, 12, 11, '8')
            cv.rect(14, 15, 18, 15, 'E')
            cv.round(8, 4, 22, 10, 'h'); cv.rect(8, 9, 22, 10, 'k'); cv.rect(10, 5, 12, 6, 'g')
            cv.rect(6, 6, 8, 8, 'K'); cv.px(7, 7, 'Y')
            cv.round(12, 18, 16, 22, body); cv.rect(11, 22, 14, 23, '3')
            for i in range(10):                      # pioche dans le dos
                cv.px(22 + i // 2, 24 - i, 'A')
            cv.rect(24, 12, 28, 13, 'k'); cv.rect(26, 11, 30, 11, 'h')
        return cv.outline().rows()
    sym(cv, 11, 27, 14, 28, '5'); sym(cv, 10, 29, 14, 30, 'A')
    sym(cv, 9, 17, 22, 26, body, True); sym(cv, 9, 24, 22, 26, shade); sym(cv, 9, 23, 22, 23, belt)
    if view == 'down':
        cv.rect(15, 23, 16, 23, 'K')
        sym(cv, 9, 8, 22, 17, '3', True); sym(cv, 9, 15, 10, 17, 'E')
        if apeure:
            sym(cv, 10, 11, 12, 13, 'g'); sym(cv, 12, 12, 12, 13, 'e')
            sym(cv, 10, 9, 13, 9, '1')
            cv.rect(14, 15, 17, 16, 'I')
            sym(cv, 8, 4, 23, 10, 'b', True); sym(cv, 8, 9, 23, 10, 'n'); cv.rect(13, 2, 18, 4, 'b')
            sym(cv, 6, 18, 8, 22, body); sym(cv, 6, 21, 8, 22, '3')
            cv.px(25, 9, 'b')
        else:
            sym(cv, 11, 12, 12, 12, 'e'); sym(cv, 11, 11, 13, 11, '8')
            cv.rect(14, 15, 17, 15, 'E')
            sym(cv, 8, 4, 23, 10, 'h', True); sym(cv, 8, 9, 23, 10, 'k')
            cv.rect(14, 5, 17, 7, 'K'); cv.rect(15, 6, 16, 6, 'Y')
            sym(cv, 6, 18, 8, 25, body); sym(cv, 6, 24, 8, 25, '3')
            sym(cv, 11, 17, 12, 22, 'C')
            for i in range(7):                       # manche de pioche derrière l'épaule
                cv.px(22 + i // 2, 17 - i, 'A')
            cv.rect(23, 7, 28, 8, 'k'); cv.rect(25, 6, 29, 6, 'h')
        return cv.outline().rows()
    # up : de dos
    sym(cv, 9, 8, 22, 17, '1', True); sym(cv, 9, 15, 22, 17, '8')
    sym(cv, 6, 18, 8, 25, body); sym(cv, 6, 24, 8, 25, '3')
    if apeure:
        sym(cv, 8, 4, 23, 12, 'b', True); sym(cv, 8, 11, 23, 12, 'n'); cv.rect(13, 2, 18, 4, 'b')
    else:
        sym(cv, 8, 4, 23, 12, 'h', True); sym(cv, 8, 11, 23, 12, 'k'); cv.rect(10, 5, 12, 6, 'g')
        for i in range(14):                          # pioche en travers du dos
            cv.px(10 + i, 24 - i, 'A')
        cv.rect(21, 8, 26, 9, 'k'); cv.rect(23, 7, 27, 7, 'h')
    return cv.outline().rows()


def build_villagers():
    engine.PALETTE['Y'] = '#f4d85a'
    for kind, name in (('apeure', 'villageois_apeure'), ('mineur', 'villageois_mineur')):
        v = {d: villager(kind, d) for d in ('down', 'up', 'left')}
        engine.build(name, v, 27, 16, OUT, hip_side=27)


# ---------- poule ----------
CPAL = {'.': None, '0': '#1b1420', 'W': '#e8e2d6', 'w': '#b4ac9c', 'R': '#b4552c', 'r': '#7e3a22',
        'T': '#d8342c', 'O': '#d89a3c', 'e': '#1b1420'}


def chicken(view, step=0, peck=0):
    """16x16 centré dans la case (8..23). step 1..4 : marche ; peck 0..2 : tête vers le sol."""
    cv = Canvas()
    ox, oy = 8, 8
    bob = 1 if step in (2, 4) else 0

    def R(x0, y0, x1, y1, c): cv.rect(ox + x0, oy + y0, ox + x1, oy + y1, c)
    def P(x, y, c): cv.px(ox + x, oy + y, c)
    ph = (0, 2, 3)[peck]
    if view in ('down', 'up'):
        ll = 13 + (1 if step == 1 else 0)
        rl = 13 + (1 if step == 3 else 0)
        R(5, ll, 6, 14, 'O'); R(9, rl, 10, 14, 'O')
        R(4, 6 - bob, 11, 12 - bob, 'W'); R(5, 5 - bob, 10, 5 - bob, 'W'); R(4, 11 - bob, 11, 12 - bob, 'w')
        R(3, 8 - bob, 4, 10 - bob, 'R'); R(11, 8 - bob, 12, 10 - bob, 'R')
        if view == 'down':
            hy = 2 + ph - bob
            R(6, hy, 9, hy + 3, 'W'); R(7, hy - 1, 8, hy, 'T')
            P(6, hy + 1, 'e'); P(9, hy + 1, 'e')
            R(7, hy + 2, 8, hy + 3, 'O'); R(7, hy + 4, 8, hy + 4, 'T')
        else:
            R(5, 9 - bob, 10, 13 - bob, 'R'); R(6, 11 - bob, 9, 13 - bob, 'r')
            hy = 3 + ph - bob
            R(6, hy, 9, hy + 3, 'W'); R(7, hy - 1, 8, hy, 'T')
    else:
        sx = 1 if step == 1 else (-1 if step == 3 else 0)
        R(6 + sx, 13, 6 + sx, 14, 'O'); R(9 - sx, 13, 9 - sx, 14, 'O')
        R(3, 6 - bob, 12, 12 - bob, 'W'); R(4, 5 - bob, 11, 5 - bob, 'W'); R(3, 11 - bob, 12, 12 - bob, 'w')
        R(11, 3 - bob, 14, 7 - bob, 'R'); R(13, 2 - bob, 14, 3 - bob, 'r')
        R(6, 7 - bob, 10, 10 - bob, 'R'); R(7, 10 - bob, 10, 10 - bob, 'r')
        hx, hy = 1 - ph // 2, 2 + ph - bob
        if ph:
            R(3, 6 - bob, 4, hy + 2, 'W')
        R(hx + 1, hy, hx + 4, hy + 3, 'W')
        R(hx + 2, hy - 1, hx + 3, hy - 1, 'T')
        P(hx + 1, hy + 1, 'e')
        P(hx, hy + 2, 'O')
        P(hx + 1, hy + 4, 'T')
    return cv.outline().rows()


def build_chicken():
    img = _Img((8 * 32, 4 * 32))
    px = img.load()

    def put(c, r, rows, mirror):
        for y in range(32):
            row = rows[y][::-1] if mirror else rows[y]
            for x in range(32):
                col = CPAL[row[x]]
                if col:
                    px[c * 32 + x, r * 32 + y] = engine.rgba(col) if False else tuple(int(col[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    for r, d in enumerate(engine.DIRS):
        base = 'left' if d in ('left', 'right') else d
        m = d == 'right'
        put(0, r, chicken(base), m)
        for s in range(1, 5):
            put(s, r, chicken(base, s), m)
        for k in range(3):
            put(5 + k, r, chicken(base, 0, k), m)
    img.save(os.path.join(OUT, 'poule.png'))
    write_tres_chicken(OUT)
    return img


def write_tres_chicken(path):
    subs, anims, n = [], [], 0

    def frame(c, r):
        nonlocal n
        n += 1
        subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{n}"]\natlas = ExtResource("1_poule")\n'
                    f'region = Rect2({c * 32}, {r * 32}, 32, 32)\n')
        return '{"duration": 1.0, "texture": SubResource("AtlasTexture_%d")}' % n

    def anim(name, cells, fps):
        anims.append('{"frames": [%s], "loop": true, "name": &"%s", "speed": %s}'
                     % (', '.join(frame(c, r) for c, r in cells), name, fps))
    for r, d in enumerate(engine.DIRS): anim(f'idle_{d}', [(0, r)], 5.0)
    for r, d in enumerate(engine.DIRS): anim(f'walk_{d}', [(c, r) for c in range(1, 5)], 8.0)
    for r, d in enumerate(engine.DIRS): anim(f'peck_{d}', [(5, r), (6, r), (7, r), (6, r)], 6.0)
    open(os.path.join(path, 'poule_frames.tres'), 'w').write(
        '[gd_resource type="SpriteFrames" format=3]\n\n'
        '[ext_resource type="Texture2D" path="res://art/characters/poule.png" id="1_poule"]\n\n'
        + '\n'.join(subs) + '\n[resource]\nanimations = [' + ', '.join(anims) + ']\n')
    json.dump({"image": "poule.png", "frame_size": [32, 32], "feet_y": 23,
               "rows": {d: i for i, d in enumerate(engine.DIRS)},
               "animations": {"idle": {"column": 0, "frames": 1, "fps": 5}, "walk": {"column": 1, "frames": 4, "fps": 8},
                              "peck": {"column": 5, "frames": 4, "fps": 6}}},
              open(os.path.join(path, 'poule.json'), 'w'), indent=2)


# ---------- aperçus ----------
def preview(img, path, scale, bg=(106, 146, 88, 255)):
    out = []
    for y in range(img.height):
        row = []
        for x in range(img.width):
            a = img.p[y][x]
            row.extend([a if a[3] == 255 else bg] * scale)
        out.extend([row] * scale)
    write_png(path, img.width * scale, img.height * scale, out)


def read_png(path):
    d = open(path, 'rb').read()
    w, h = struct.unpack('>II', d[16:24])
    i, idat = 8, b''
    while i < len(d):
        n = struct.unpack('>I', d[i:i + 4])[0]
        if d[i + 4:i + 8] == b'IDAT':
            idat += d[i + 8:i + 8 + n]
        i += 12 + n
    raw = zlib.decompress(idat)
    img = _Img((w, h))
    for y in range(h):
        base = y * (w * 4 + 1) + 1
        img.p[y] = [tuple(raw[base + x * 4:base + x * 4 + 4]) for x in range(w)]
    return img


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    build_villagers()
    build_chicken()
    if PREV:
        os.makedirs(PREV, exist_ok=True)
        for n in ('poule', 'villageois_apeure', 'villageois_mineur'):
            im = read_png(os.path.join(OUT, n + '.png'))
            preview(im, os.path.join(PREV, n + '_x4.png'), 4)
