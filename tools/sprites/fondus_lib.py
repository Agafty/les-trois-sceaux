"""Fondus des transitions de terrain (Wang par coins) - Les Trois Sceaux.

Redessine UNIQUEMENT les tuiles de transition d'un tileset, a leur emplacement, a partir des tuiles pleines du meme terrain
(meme texture au bord => raccord sans couture). Sans Pillow : lecture/ecriture PNG avec zlib + struct.

Principe : pour chaque tuile, un champ continu (interpolation bilineaire entre les 4 centres de quarts de case, bruit periodique
de 32 px) donne un bord organique irregulier qui traverse les quarts ; comme le champ et le bruit sont les memes pour toutes
les tuiles, deux tuiles voisines qui partagent les memes coins se raccordent. Les liseres (contour, lumiere haut-gauche, ombre
portee, ecume, tramage) sont calcules sur une zone elargie de 4 px pour rester continus d'une tuile a l'autre.
Terrains "solides" (ravin, eau profonde) : le bord ne fait que grignoter la zone solide (jamais au-dela du quart de collision).
"""
import os
import struct
import zlib
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = 32
PAD = 4


# ------------------------------------------------------------------ PNG
def read_png(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n'
    i, idat = 8, b''
    while i < len(d):
        n, t = struct.unpack('>I4s', d[i:i + 8])
        body = d[i + 8:i + 8 + n]
        if t == b'IHDR':
            w, h, bd, ct = struct.unpack('>IIBB', body[:10])
            assert bd == 8 and ct == 6
        elif t == b'IDAT':
            idat += body
        i += 12 + n
    raw = zlib.decompress(idat)
    bpp, stride, rows, prev = 4, w * 4, [], bytearray(w * 4)
    for y in range(h):
        f = raw[y * (stride + 1)]
        cur = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = cur[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                cur[x] = (cur[x] + a) & 255
            elif f == 2:
                cur[x] = (cur[x] + b) & 255
            elif f == 3:
                cur[x] = (cur[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                cur[x] = (cur[x] + pr) & 255
        rows.append([tuple(cur[x * 4:x * 4 + 4]) for x in range(w)])
        prev = cur
    return rows


def save_png(path, pix, scale=1):
    h, w = len(pix), len(pix[0])
    raw = bytearray()
    for y in range(h):
        row = bytearray()
        for x in range(w):
            row += bytes(pix[y][x]) * scale
        for _ in range(scale):
            raw.append(0)
            raw += row

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


# ------------------------------------------------------------------ tileset
class Tileset:
    def __init__(self, name):
        self.name = name
        self.png = os.path.join(ROOT, 'art', 'tilesets', name + '.png')
        self.pix = read_png(self.png)
        self.h, self.w = len(self.pix), len(self.pix[0])
        self.cols = self.w // T
        root = ET.parse(os.path.join(ROOT, 'maps', 'tilesets', name + '.tsx')).getroot()
        self.wangsets = []
        for ws in root.iter('wangset'):
            ncol = len(ws.findall('wangcolor'))
            tiles = {}
            for t in ws.findall('wangtile'):
                w = [int(x) for x in t.get('wangid').split(',')]
                tiles[int(t.get('tileid'))] = (w[7], w[1], w[5], w[3])  # HG, HD, BG, BD
            self.wangsets.append((ws.get('name'), ncol, tiles))

    def tile(self, i):
        cx, cy = (i % self.cols) * T, (i // self.cols) * T
        return [row[cx:cx + T] for row in self.pix[cy:cy + T]]

    def put(self, i, t):
        cx, cy = (i % self.cols) * T, (i // self.cols) * T
        for y in range(T):
            for x in range(T):
                self.pix[cy + y][cx + x] = t[y][x]

    def save(self):
        save_png(self.png, self.pix)


# ------------------------------------------------------------------ bruit periodique
def _h(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def _vn(x, y, g, s):
    n = T // g
    fx, fy = x / g, y / g
    x0, y0 = int(fx) % n, int(fy) % n
    tx, ty = fx - int(fx), fy - int(fy)
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    x1, y1 = (x0 + 1) % n, (y0 + 1) % n
    a = _h(x0, y0, s) * (1 - tx) + _h(x1, y0, s) * tx
    b = _h(x0, y1, s) * (1 - tx) + _h(x1, y1, s) * tx
    return a * (1 - ty) + b * ty


_NOISE = {}


def noise(x, y):
    """Bruit periodique (32 px) dans [-1, 1]."""
    x, y = x % T, y % T
    k = (x, y)
    if k not in _NOISE:
        v = (0.30 * _vn(x + .5, y + .5, 16, 4) + 0.38 * _vn(x + .5, y + .5, 8, 1) + 0.22 * _vn(x + .5, y + .5, 4, 2)
             + 0.10 * _vn(x + .5, y + .5, 2, 3))
        _NOISE[k] = max(-1.0, min(1.0, (v - 0.5) * 4.2))
    return _NOISE[k]


def shade(c, k):
    return (int(c[0] * k * 0.97), int(c[1] * k * 0.98), min(255, int(c[2] * k + (1 - k) * 26)), c[3])


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def quant(tile, q):
    cols = sorted({p for row in tile for p in row if p[3] == 255}, key=lum)
    return cols[max(0, min(len(cols) - 1, int(round(q * (len(cols) - 1)))))]


# ------------------------------------------------------------------ rendu d'une transition
AMP = 0.42


def field_mask(pat, solid, amp=AMP):
    """Masque (padde) : 1 = terrain secondaire (B)."""
    n = T + 2 * PAD
    cv = [1 if c == 2 else 0 for c in pat]  # HG, HD, BG, BD
    M = [[0] * n for _ in range(n)]
    for j in range(n):
        for i in range(n):
            x, y = i - PAD, j - PAD
            u = min(1.0, max(0.0, (x + .5 - 8) / 16))
            v = min(1.0, max(0.0, (y + .5 - 8) / 16))
            w = cv[0] * (1 - u) * (1 - v) + cv[1] * u * (1 - v) + cv[2] * (1 - u) * v + cv[3] * u * v
            nz = noise(x, y)
            if solid:
                nz = (nz - 1) * 0.5  # grignote seulement : jamais au-dela du quart de collision
            M[j][i] = 1 if w + amp * nz > 0.5 else 0
            if w >= 0.999:
                M[j][i] = 1
            if w <= 0.001:
                M[j][i] = 0
    return M


def render(pat, texA, texB, st):
    """st : dict de style (voir fondus.py). Renvoie une tuile 32x32 de tuples RGBA."""
    M = field_mask(pat, st.get('solid', False), st.get('amp', AMP))
    Rm = 1 if st['raised'] == 'B' else 0
    texR = texB if Rm else texA   # terrain "au-dessus"
    texL = texA if Rm else texB   # terrain "dessous"

    def isR(x, y):
        return M[y + PAD][x + PAD] == Rm

    def dist(x, y):
        me = isR(x, y)
        for d in range(1, 5):
            for dx in range(-d, d + 1):
                dy = d - abs(dx)
                for sy in ((dy, -dy) if dy else (0,)):
                    xx, yy = x + dx, y + sy
                    if -PAD <= xx < T + PAD and -PAD <= yy < T + PAD and isR(xx, yy) != me:
                        return d
        return 9

    out = [[None] * T for _ in range(T)]
    seed = st.get('seed', 0)
    for y in range(T):
        for x in range(T):
            me = isR(x, y)
            c = (texB if M[y + PAD][x + PAD] else texA)[y][x]
            d = dist(x, y)

            def hv(s):
                return _h(x, y, s + seed)
            if me:
                if d == 1:
                    lit = (not isR(x - 1, y)) or (not isR(x, y - 1))
                    c = st['lip'] if (lit and st.get('lip')) else st['out']
                    if st.get('out_alt') and not lit and hv(5) < st.get('out_alt_p', 0.25):
                        c = st['out_alt']
                else:
                    rb = st.get('rbleed')
                    if rb and 2 <= d <= 4 and hv(7) < rb[d - 2]:
                        c = texL[y][x]
                    elif st.get('r2') and d == 2 and hv(9) < st['r2'][1]:
                        c = st['r2'][0]
            else:
                sh1 = isR(x - 1, y) or isR(x, y - 1)
                sh2 = isR(x - 2, y) or isR(x, y - 2) or isR(x - 1, y - 1)
                if d == 1 and sh1 and st.get('shadow'):
                    c = shade(c, st['shadow'][0])
                elif d == 2 and (sh2 or sh1) and st.get('shadow') and st['shadow'][1]:
                    c = shade(c, st['shadow'][1])
                elif d == 1 and st.get('l1'):
                    p = st['l1'][1]
                    if (p == 'c' and (x + y) % 2 == 0) or (p != 'c' and hv(11) < p):
                        c = st['l1'][0]
                    elif st.get('l1b'):
                        c = st['l1b']
                elif d == 2 and st.get('l2') and hv(13) < st['l2'][1]:
                    c = st['l2'][0]
                elif d == 3 and st.get('l3') and hv(15) < st['l3'][1]:
                    c = st['l3'][0]
                bl = st.get('bleed')
                if bl and d <= 3 and hv(17 + d) < bl[d - 1]:
                    c = st['bleed_col'] if st.get('bleed_col') else texR[y][x]
            out[y][x] = c
    return out


def transitions(ts):
    """[(id, pattern, nom_wangset, texA, texB)] pour les wangsets a 2 terrains (tuiles mixtes seulement)."""
    res = []
    for name, ncol, tiles in ts.wangsets:
        if ncol != 2:
            continue
        top = max(tiles)
        base = top - 15
        ta, tb = ts.tile(base), ts.tile(top)
        for i, pat in sorted(tiles.items()):
            if base <= i <= top and len(set(pat)) == 2:
                res.append((i, pat, name, ta, tb))
    return res
