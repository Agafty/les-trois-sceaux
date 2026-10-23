"""Moteur de génération des sprites placeholder — Les Trois Sceaux.

Chaque personnage est décrit en ASCII (une lettre = une couleur de la palette).
- Vues face (down) et dos (up) : on écrit la moitié gauche (16 colonnes), le reste est mis en miroir.
- Vue de profil (left) : 32 colonnes ; la vue droite est le miroir de la gauche.
La marche (4 frames) est dérivée automatiquement de la pose idle, comme pour Brann :
  pas gauche, rebond (+1 px), pas droit, rebond.
Format de sortie identique à brann.png : 160x128, une ligne par direction
(down, up, left, right), colonne 0 = idle, colonnes 1-4 = marche.
"""
from PIL import Image
import json, os

PALETTE = {
    '.': None,
    '0': '#1b1420',  # contour
    '1': '#7a4628', '7': '#b06e40', '8': '#4a2a1c',            # cheveux bruns
    '3': '#f2c29a', 'E': '#cc8c68',                           # peau
    '4': '#e2342c', 'F': '#961c28',                           # rouge
    '2': '#d6c49c', '9': '#a6926c',                           # tissu crème
    '6': '#8a5a34', 'B': '#5e3a22',                           # cuir
    '5': '#4e4058', 'J': '#382e42',                           # pantalon
    'A': '#6a4630', 'H': '#43291c',                           # bottes
    'C': '#4a3426', 'G': '#2e2018', 'D': '#3a2a20',           # gants, ceinture
    'K': '#c8a050', 'I': '#241a22',                           # or, détail sombre
    'g': '#d8d4cc', 'h': '#9a948c', 'k': '#5c5650',           # gris (cheveux, métal)
    'v': '#5a8a3c', 'w': '#3a5a2c',                           # vert
    'b': '#3c5a8a', 'n': '#263a5e',                           # bleu
    'p': '#6a2a7a', 'q': '#3a1a4a',                           # violet (corruption)
    'e': '#1b1420',  # yeux (contour, sauf variante corrompue)
}
DARKER = {'5': 'J', 'A': 'H', '2': '9', '6': 'B', 'b': 'n', 'v': 'w', '3': 'E',
          '1': '8', 'g': 'h', 'h': 'k', 'p': 'q', '4': 'F', 'K': '6'}
DIRS = ['down', 'up', 'left', 'right']


def rgba(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def grid(rows, half=False):
    rows = [r.rstrip('\n') for r in rows]
    assert len(rows) == 32, f'{len(rows)} lignes au lieu de 32'
    out = []
    for i, r in enumerate(rows):
        if half:
            assert len(r) == 16, f'ligne {i}: {len(r)} car. au lieu de 16 : {r!r}'
            r = r + r[::-1]
        assert len(r) == 32, f'ligne {i}: {len(r)} car. au lieu de 32 : {r!r}'
        out.append(list(r))
    return out


def mirror(g):
    return [row[::-1] for row in g]


def shift_up_body(g, hip):
    """Rebond : tout ce qui est au-dessus de la hanche monte d'un pixel, la jambe s'allonge."""
    n = [row[:] for row in g]
    for y in range(hip):
        n[y] = g[y + 1][:]
    return n


def lift_foot(g, hip, left=True):
    """Pas en vue face/dos : un pied remonte d'un pixel."""
    n = [row[:] for row in g]
    xs = range(0, 16) if left else range(16, 32)
    for y in range(hip, 32):
        for x in xs:
            n[y][x] = g[y + 1][x] if y < 31 else '.'
    return n


def stride(g, hip, legmid, swap=False):
    """Pas en vue de profil (tourné à gauche) : jambe avant à gauche, jambe arrière à droite, assombrie."""
    n = [row[:] for row in g]
    for y in range(hip, 32):
        for x in range(32):
            n[y][x] = '.'
    for y in range(hip, 32):
        for x in range(32):
            c = g[y][x]
            if c == '.':
                continue
            front = x <= legmid
            nx = x - 1 if front else x + 2
            dark = (not front) != swap
            if dark:
                c = DARKER.get(c, c)
            if 0 <= nx < 32 and (n[y][nx] == '.' or front):
                n[y][nx] = c
    return n


def frames_for(views, hip, legmid, hip_side=None):
    hip_side = hip if hip_side is None else hip_side
    down, up, left = views['down'], views['up'], views['left']
    rows = []
    for g in (down, up):
        rows.append([g, lift_foot(g, hip, True), shift_up_body(g, hip),
                     lift_foot(g, hip, False), shift_up_body(g, hip)])
    side = [left, stride(left, hip_side, legmid), shift_up_body(left, hip_side),
            stride(left, hip_side, legmid, swap=True), shift_up_body(left, hip_side)]
    rows.append(side)
    rows.append([mirror(f) for f in side])
    return rows


def render(rows, remap=None):
    pal = dict(PALETTE)
    if remap:
        pal.update(remap)
    img = Image.new('RGBA', (160, 128), (0, 0, 0, 0))
    px = img.load()
    for r, frames in enumerate(rows):
        for c, g in enumerate(frames):
            for y in range(32):
                for x in range(32):
                    col = pal[g[y][x]]
                    if col:
                        px[c * 32 + x, r * 32 + y] = rgba(col)
    return img


def write_tres(name, path):
    subs, anims, n = [], [], 0

    def frame(c, r):
        nonlocal n
        n += 1
        sid = f'AtlasTexture_{n}'
        subs.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("1_{name}")\n'
                     f'region = Rect2({c * 32}, {r * 32}, 32, 32)\n')
        return '{"duration": 1.0, "texture": SubResource("%s")}' % sid

    for r, d in enumerate(DIRS):
        anims.append('{"frames": [%s], "loop": true, "name": &"idle_%s", "speed": 5.0}' % (frame(0, r), d))
    for r, d in enumerate(DIRS):
        fr = ', '.join(frame(c, r) for c in range(1, 5))
        anims.append('{"frames": [%s], "loop": true, "name": &"walk_%s", "speed": 8.0}' % (fr, d))
    tres = (f'[gd_resource type="SpriteFrames" format=3]\n\n'
            f'[ext_resource type="Texture2D" path="res://art/characters/{name}.png" id="1_{name}"]\n\n'
            + '\n'.join(subs) + '\n[resource]\nanimations = [' + ', '.join(anims) + ']\n')
    open(os.path.join(path, f'{name}_frames.tres'), 'w').write(tres)
    json.dump({"image": f"{name}.png", "frame_size": [32, 32], "feet_y": 31,
               "rows": {d: i for i, d in enumerate(DIRS)},
               "animations": {"idle": {"column": 0, "frames": 1, "fps": 5},
                              "walk": {"column": 1, "frames": 4, "fps": 8}}},
              open(os.path.join(path, f'{name}.json'), 'w'), indent=2)


def overlay(g, rows):
    """Détails asymétriques posés après le miroir ('.' = inchangé, '_' = transparent)."""
    if not rows:
        return g
    rows = (list(rows) + ['.' * 32] * 32)[:32]
    for y, r in enumerate(rows):
        for x, c in enumerate(r.ljust(32, '.')):
            if c == '_':
                g[y][x] = '.'
            elif c != '.':
                g[y][x] = c
    return g


def build(name, views, hip, legmid, out, remap=None, hip_side=None, overlays=None):
    overlays = overlays or {}
    v = {'down': overlay(grid(views['down'], half=len(views['down'][0]) == 16), overlays.get('down')),
         'up': overlay(grid(views['up'], half=len(views['up'][0]) == 16), overlays.get('up')),
         'left': overlay(grid(views['left']), overlays.get('left'))}
    img = render(frames_for(v, hip, legmid, hip_side), remap)
    img.save(os.path.join(out, f'{name}.png'))
    write_tres(name, out)
    return img


def preview(img, path, scale=4, bg=(106, 146, 88, 255)):
    big = Image.new('RGBA', img.size, bg)
    big.alpha_composite(img)
    big.resize((img.width * scale, img.height * scale), Image.NEAREST).save(path)
