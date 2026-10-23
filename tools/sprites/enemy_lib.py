"""Outils de dessin des ennemis : formes, contour automatique, planches et SpriteFrames Godot.

Une planche = une ligne par animation, une colonne par frame (cases 32x32).
Les ennemis au sol ont le bas du corps sur la ligne y = 31 (même règle que les personnages).
"""
import math, os, json, copy
from PIL import Image
from engine import PALETTE, rgba


def blank():
    return [['.'] * 32 for _ in range(32)]


def cp(g):
    return copy.deepcopy(g)


def put(g, x, y, c):
    if 0 <= x < 32 and 0 <= y < 32:
        g[y][x] = c


def paint(g, x, y, rows):
    """Colle un bloc ASCII en (x, y). '.' = inchangé, '_' = transparent."""
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c != '.':
                put(g, x + i, y + j, '.' if c == '_' else c)


def ellipse(g, cx, cy, rx, ry, fill, shade=None, hi=None, shade_k=0.55, hi_k=-0.55):
    for y in range(32):
        for x in range(32):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                c = fill
                v = dx * 0.5 + dy * 0.85
                if shade and v > shade_k:
                    c = shade
                if hi and v < hi_k:
                    c = hi
                g[y][x] = c


def rect(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(g, x, y, c)


def line(g, x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        put(g, round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)


def outline(g, color='0'):
    """Contour de 1 px autour de tout ce qui n'est pas transparent (4-voisinage)."""
    src = cp(g)
    for y in range(32):
        for x in range(32):
            if src[y][x] != '.':
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 32 and 0 <= ny < 32 and src[ny][nx] not in '.0':
                    g[y][x] = color
                    break
    return g


def mirror(g):
    return [row[::-1] for row in g]


def shift(g, dx=0, dy=0):
    n = blank()
    for y in range(32):
        for x in range(32):
            if g[y][x] != '.':
                put(n, x + dx, y + dy, g[y][x])
    return n


def recolor(g, mapping):
    return [[mapping.get(c, c) for c in row] for row in g]


def bottom_align(g, bottom=31):
    ys = [y for y in range(32) if any(c != '.' for c in g[y])]
    return shift(g, 0, bottom - ys[-1]) if ys else g


def render(rows, remap=None, cell=32):
    pal = dict(PALETTE)
    if remap:
        pal.update(remap)
    w = max(len(r) for r in rows) * cell
    img = Image.new('RGBA', (w, len(rows) * cell), (0, 0, 0, 0))
    px = img.load()
    for r, frames in enumerate(rows):
        for c, g in enumerate(frames):
            for y in range(cell):
                for x in range(cell):
                    col = pal[g[y][x]]
                    if col:
                        px[c * cell + x, r * cell + y] = rgba(col)
    return img


def write_tres(out, folder, name, textures, anims, cell=32):
    """anims : liste de (nom, texture, [(col, ligne)...], fps, boucle)."""
    ext = [f'[ext_resource type="Texture2D" path="res://art/{folder}/{t}.png" id="{i + 1}_{t}"]'
           for i, t in enumerate(textures)]
    tid = {t: f'{i + 1}_{t}' for i, t in enumerate(textures)}
    subs, out_a, n = [], [], 0
    for aname, tex, cells, fps, loop in anims:
        frames = []
        for (c, r) in cells:
            n += 1
            sid = f'AtlasTexture_{n}'
            subs.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("{tid[tex]}")\n'
                        f'region = Rect2({c * cell}, {r * cell}, {cell}, {cell})\n')
            frames.append('{"duration": 1.0, "texture": SubResource("%s")}' % sid)
        out_a.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %s}'
                     % (', '.join(frames), 'true' if loop else 'false', aname, fps))
    txt = ('[gd_resource type="SpriteFrames" format=3]\n\n' + '\n'.join(ext) + '\n\n' + '\n'.join(subs)
           + '\n[resource]\nanimations = [' + ', '.join(out_a) + ']\n')
    open(os.path.join(out, f'{name}_frames.tres'), 'w').write(txt)


def build_enemy(out, name, anims, red=None, folder='enemies'):
    """anims : liste de (nom, [grilles], fps, boucle). Une ligne de planche par animation,
    sauf les animations qui réutilisent une ligne existante via ('=ligne', fps, boucle)."""
    rows, specs = [], []
    for aname, frames, fps, loop in anims:
        if isinstance(frames, tuple):        # réutilise les cases d'une autre animation
            src = [s for s in specs if s[0] == frames[0]][0]
            specs.append((aname, src[1], fps, loop))
            continue
        r = len(rows)
        rows.append(frames)
        specs.append((aname, [(c, r) for c in range(len(frames))], fps, loop))
    variants = [(name, None)] + ([(name + '_red', red)] if red else [])
    for vname, remap in variants:
        render(rows, remap).save(os.path.join(out, f'{vname}.png'))
        write_tres(out, folder, vname, [vname], [(a, vname, cells, f, l) for a, cells, f, l in specs])
        json.dump({'image': f'{vname}.png', 'frame_size': [32, 32],
                   'animations': {a: {'cells': cells, 'fps': f, 'loop': l} for a, cells, f, l in specs}},
                  open(os.path.join(out, f'{vname}.json'), 'w'), indent=1)
    return rows
