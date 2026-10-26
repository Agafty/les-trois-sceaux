"""Bibliothèque commune des PLANS de tilesets (village, intérieurs…) — Les Trois Sceaux.

Un plan = planche PNG d'aplats lisibles + numéro de chaque tuile, tileset .tsx (collisions + terrains Wang),
fichier <nom>_plan.md. Même organisation que foret.py : numéro = id local Tiled = ligne * colonnes + colonne.
RÈGLE : ne jamais déplacer une tuile quand une carte l'utilise ; on ajoute dans les lignes de réserve (à la fin).
Sans Pillow : mini encodeur PNG (zlib + struct).
"""
import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
T = 32

FULL = [(0, 0, 32, 32)]
HALF_BOT = [(0, 16, 32, 16)]
HALF_TOP = [(0, 0, 32, 16)]
BASE = [(2, 14, 28, 18)]
OBJ = [(4, 8, 24, 22)]
TABLE = [(0, 8, 32, 22)]
DOORC = [(0, 0, 6, 32), (26, 0, 6, 32)]
THIN_L = [(0, 0, 8, 32)]
THIN_R = [(24, 0, 8, 32)]
THIN_B = [(0, 24, 32, 8)]
POST = [(11, 14, 10, 18)]

CATS = {}          # catégorie -> couleur '#rrggbb' (définie par chaque script)


def rgba(h, a=255):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (c[3],)


def corners(b):
    return (b >> 3) & 1, (b >> 2) & 1, (b >> 1) & 1, b & 1


def quarter_rects(b):
    hg, hd, bg, bd = corners(b)
    if b == 15:
        return [(0, 0, 32, 32)]
    if hg and bg and not hd and not bd:
        return [(0, 0, 16, 32)]
    if hd and bd and not hg and not bg:
        return [(16, 0, 16, 32)]
    r = []
    if hg and hd:
        r.append((0, 0, 32, 16))
    elif hg or hd:
        r.append((0, 0, 16, 16) if hg else (16, 0, 16, 16))
    if bg and bd:
        r.append((0, 16, 32, 16))
    elif bg or bd:
        r.append((0, 16, 16, 16) if bg else (16, 16, 16, 16))
    return r


POS = ('haut-gauche', 'haut-droite', 'bas-gauche', 'bas-droite')


def describe(b, name):
    c = corners(b)
    on = [POS[i] for i in range(4) if c[i]]
    if b == 0:
        return 'case entière du terrain principal'
    if b == 15:
        return f'case entière de {name}'
    if len(on) == 1:
        return f'coin {on[0]} seulement ({name} dans ce coin)'
    if len(on) == 2:
        if c[0] and c[1]:
            return f'{name} en haut (bord haut)'
        if c[2] and c[3]:
            return f'{name} en bas (bord bas)'
        if c[0] and c[2]:
            return f'{name} à gauche (bord gauche)'
        if c[1] and c[3]:
            return f'{name} à droite (bord droit)'
        return f'deux coins opposés ({" et ".join(on)})'
    free = [POS[i] for i in range(4) if not c[i]][0]
    return f'{name} partout sauf le coin {free} (coin rentrant)'


def collision_txt(r):
    if not r:
        return 'aucune'
    if r == FULL:
        return 'pleine'
    return 'partielle : ' + ' ; '.join(f'{x},{y} {w}×{h}' for x, y, w, h in r)


class Sheet:
    def __init__(self, name, cols, titre, intro, calques):
        self.name, self.cols, self.titre, self.intro, self.calques = name, cols, titre, intro, calques
        self.tiles, self.names, self.cur = {}, {}, 0
        self.groups, self.wang, self.assemblages, self.notes = [], {}, [], []
        self.rows = None
        self.reserve = 4

    # ---------------------------------------------------------- remplissage
    def align(self, n):
        self.cur = -(-self.cur // n) * n

    def group(self, titre, note='', align=None):
        import re
        self.align(align or self.cols)
        titre = f'{len(self.groups) + 1}. ' + re.sub(r'^\d+b?\. ', '', titre)
        self.groups.append(dict(titre=titre, note=note, first=self.cur, last=self.cur))

    def add(self, nom, role, calque, coll, cat, col=None, ghost=False, plan=None):
        assert nom not in self.names, nom
        i = self.cur
        self.tiles[i] = dict(nom=nom, role=role, calque=calque, coll=coll, cat=cat, col=col, ghost=ghost, plan=plan)
        self.names[nom] = i
        self.cur += 1
        self.groups[-1]['last'] = i
        return i

    def line(self, items):
        """Une ligne de la planche (alignée) ; None = case vide."""
        self.align(self.cols)
        assert len(items) <= self.cols, items
        for it in items:
            if it is None:
                self.cur += 1
            else:
                self.add(*it[:5], **(it[5] if len(it) > 5 else {}))
        self.align(self.cols)

    def terrain(self, wname, nom, catA, catB, labelA, labelB, solid, base_role, full_role, fam,
                layer='Sol', base_layer='Sol', note_fam=''):
        """Bloc de 16 tuiles (coins) : id = base + HG*8 + HD*4 + BG*2 + BD."""
        self.align(16)
        base = self.cur
        self.wang[wname] = dict(colors=[(labelA, CATS[catA]), (labelB, CATS[catB])], tile=base + 15, tiles={}, fam=fam)
        for b in range(16):
            n = f'{nom}_plein' if b == 15 else f'{nom}_base' if b == 0 else f'{nom}_{"%d%d%d%d" % corners(b)}'
            role = base_role if b == 0 else full_role if b == 15 else f'{fam} : ' + describe(b, labelB)
            coll = quarter_rects(b) if (solid and b) else None
            self.add(n, role, base_layer if b == 0 else layer, coll, catB if b else catA,
                     plan=('terrain', b, catA, catB))
            self.wang[wname]['tiles'][base + b] = tuple(2 if k else 1 for k in corners(b))
        return base

    def grass_into(self, wnames, ids):
        for w in wnames:
            for i in ids:
                self.wang[w]['tiles'][i] = (1, 1, 1, 1)

    def id(self, nom):
        return self.names[nom]

    def assemblage(self, titre, rows, calques, note=''):
        self.assemblages.append(dict(titre=titre, rows=rows, calques=calques, note=note))

    def finish(self):
        last = max(self.tiles)
        self.rows = -(-(last + 1) // self.cols) + self.reserve

    # ---------------------------------------------------------- dessin du plan
    def plan_tile(self, d):
        img = [[None] * T for _ in range(T)]
        if d['plan'] and d['plan'][0] == 'terrain':
            _, b, ca, cb = d['plan']
            A, B = rgba(CATS[ca]), rgba(CATS[cb])
            hg, hd, bg, bd = corners(b)
            for y in range(T):
                for x in range(T):
                    u, v = (x + 0.5) / T, (y + 0.5) / T
                    f = (hg * (1 - u) + hd * u) * (1 - v) + (bg * (1 - u) + bd * u) * v
                    img[y][x] = B if f > 0.5 else A
            return img
        col = rgba(d['col'] or CATS[d['cat']], 110 if d['ghost'] else 255)
        dark = shade(col, 0.5)
        calque = d['calque']
        inset = 3 if calque in ('Decor', 'Dessus') and not d['ghost'] else 0
        for y in range(inset, T - inset):
            for x in range(inset, T - inset):
                edge = x in (inset, T - inset - 1) or y in (inset, T - inset - 1)
                img[y][x] = col if (not edge or d['ghost'] or calque == 'Sol') else dark
        if calque == 'Sol' and not d['ghost']:                          # quadrillage discret
            for k in range(T):
                img[k][T - 1] = shade(col, 0.82)
                img[T - 1][k] = shade(col, 0.82)
        if d['coll'] and d['coll'] != FULL:                              # zone solide plus sombre
            for (cx, cy, cw, ch) in d['coll']:
                for y in range(cy, min(T, cy + ch)):
                    for x in range(cx, min(T, cx + cw)):
                        if img[y][x] is not None:
                            img[y][x] = shade(col, 0.68)
        return img

    def sheet(self, numbers=True, scale=1):
        W, H = self.cols * T, self.rows * T
        px = [[None] * W for _ in range(H)]
        for i, d in self.tiles.items():
            im = self.plan_tile(d)
            ox, oy = (i % self.cols) * T, (i // self.cols) * T
            for y in range(T):
                for x in range(T):
                    if im[y][x] is not None:
                        px[oy + y][ox + x] = im[y][x]
        if scale > 1:
            px = [[px[y // scale][x // scale] for x in range(W * scale)] for y in range(H * scale)]
        if numbers:
            for i in self.tiles:
                stamp_number(px, (i % self.cols) * T * scale + 1, (i // self.cols) * T * scale + 1, i, scale)
        return px

    # ---------------------------------------------------------- exports
    def tsx(self):
        s = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             f'<tileset version="1.10" tiledversion="1.12.2" name="{self.name}" tilewidth="{T}" tileheight="{T}" '
             f'tilecount="{self.cols * self.rows}" columns="{self.cols}">\n'
             f' <image source="../../art/tilesets/{self.name}.png" width="{self.cols * T}" height="{self.rows * T}"/>\n')
        for i in sorted(self.tiles):
            c = self.tiles[i]['coll']
            if c:
                s += f' <tile id="{i}">\n  <objectgroup draworder="index" id="2">\n'
                for k, (x, y, w, h) in enumerate(c, 1):
                    s += f'   <object id="{k}" x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
                s += '  </objectgroup>\n </tile>\n'
        if self.wang:
            s += ' <wangsets>\n'
            for name, w in self.wang.items():
                s += f'  <wangset name="{name}" type="corner" tile="{w["tile"]}">\n'
                for cn, cc in w['colors']:
                    s += f'   <wangcolor name="{cn}" color="{cc}" tile="-1" probability="1"/>\n'
                for i in sorted(w['tiles']):
                    hg, hd, bg, bd = w['tiles'][i]
                    s += f'   <wangtile tileid="{i}" wangid="0,{hd},0,{bd},0,{bg},0,{hg}"/>\n'
                s += '  </wangset>\n'
            s += ' </wangsets>\n'
        return s + '</tileset>\n'

    def md(self, script):
        reserve0 = (self.rows - self.reserve) * self.cols
        o = [f'# Plan du tileset `{self.name}` — {self.titre}', '',
             f'> Fichier généré par `tools/sprites/{script}` : modifier le script, pas ce fichier. '
             '**État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro).', '',
             f'- Image : `art/tilesets/{self.name}.png`, {self.cols * T}×{self.rows * T} px, {self.cols} colonnes × {self.rows} lignes '
             f'de tuiles 32×32, sans marge ni espacement ({self.cols * self.rows} cases). Tileset Tiled : `maps/tilesets/{self.name}.tsx` '
             '(collisions et terrains définis). `art/tilesets/' + self.name + '_numeros.png` = la planche ×2 avec les numéros.',
             f'- **Numéro = id local Tiled** (ligne × {self.cols} + colonne, en partant de 0). Une tuile ne change jamais de numéro. '
             f'Lignes {self.rows - self.reserve + 1} à {self.rows} (ids {reserve0} à {self.cols * self.rows - 1}) : réserve vide, pour les ajouts. '
             'Les cases vides au bout d\'une ligne sont aussi libres.',
             '- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans '
             'le panneau Terrains de Tiled.'] + self.intro + ['', '## Calques', ''] + [f'- {c}' for c in self.calques] + ['']
        for g in self.groups:
            ids = [i for i in range(g['first'], g['last'] + 1) if i in self.tiles]
            if not ids:
                continue
            o += [f'## {g["titre"]}', '']
            if g['note']:
                o += [g['note'], '']
            o += ['| N° | Nom | Rôle | Calque | Collision |', '| --- | --- | --- | --- | --- |']
            for i in ids:
                d = self.tiles[i]
                o.append(f'| {i} | `{d["nom"]}` | {d["role"]} | {d["calque"]} | {collision_txt(d["coll"])} |')
            o.append('')
        if self.assemblages:
            o += ['## Assemblages (pinceau « tampon » dans Tiled)', '', '| Assemblage | Tuiles (ligne par ligne) | Calques / usage |',
                  '| --- | --- | --- |']
            for a in self.assemblages:
                rows = ' / '.join(' '.join(str(self.names[n]) if n else '·' for n in r) for r in a['rows'])
                o.append(f'| **{a["titre"]}** | `{rows}` | {a["calques"]}{(" — " + a["note"]) if a["note"] else ""} |')
            o.append('')
        if self.wang:
            o += ['## Terrains (Wang, par coins)', '',
                  'Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain est un bloc de 16 tuiles : '
                  'id = base + (HG×8 + HD×4 + BG×2 + BD), 1 = terrain secondaire dans ce coin.', '',
                  '| Terrain | Couleurs (1 / 2) | Tuiles | Calque |', '| --- | --- | --- | --- |']
            for n, w in self.wang.items():
                ids = sorted(w['tiles'])
                base = w['tile'] - 15
                o.append(f'| `{n}` | {w["colors"][0][0]} / {w["colors"][1][0]} | {base}–{base + 15} (+ herbe 0–6 si herbe) | {w["fam"]} |')
            o.append('')
        if self.notes:
            o += ['## Notes', ''] + [f'- {n}' for n in self.notes] + ['']
        return '\n'.join(o)

    def save_all(self, script):
        out_t = os.path.join(ROOT, 'art', 'tilesets')
        os.makedirs(out_t, exist_ok=True)
        self.finish()
        save_png(os.path.join(out_t, f'{self.name}.png'), self.sheet(numbers=True))
        save_png(os.path.join(out_t, f'{self.name}_numeros.png'), self.sheet(numbers=True, scale=2))
        with open(os.path.join(ROOT, 'maps', 'tilesets', f'{self.name}.tsx'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(self.tsx())
        with open(os.path.join(out_t, f'{self.name}_plan.md'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(self.md(script))
        print(f'{self.name} : {len(self.tiles)} tuiles sur {self.cols * self.rows} cases ({self.cols}x{self.rows}).')


# ---------------------------------------------------------------- PNG
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


DIGITS = {'0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111',
          '4': '101101111001001', '5': '111100111001111', '6': '111100111101111', '7': '111001001001001',
          '8': '111101111101111', '9': '111101111001111'}


def stamp_number(pix, ox, oy, n, scale=1):
    s = str(n)
    w = len(s) * 4 * scale + scale
    for y in range(5 * scale + 2):
        for x in range(w):
            if 0 <= oy + y < len(pix) and 0 <= ox + x < len(pix[0]):
                pix[oy + y][ox + x] = rgba('#000000')
    for k, ch in enumerate(s):
        for j in range(15):
            if DIGITS[ch][j] == '1':
                for sy in range(scale):
                    for sx in range(scale):
                        px_, py_ = ox + 1 + k * 4 * scale + (j % 3) * scale + sx, oy + 1 + (j // 3) * scale + sy
                        if 0 <= py_ < len(pix) and 0 <= px_ < len(pix[0]):
                            pix[py_][px_] = rgba('#ffff40')
