"""Écrit les SpriteFrames Godot (.tres) de tous les personnages, animations spéciales comprises.

Usage : python3 tres.py <dossier art/characters>
"""
import sys, os

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
DIRS = ['down', 'up', 'left', 'right']


def base_anims(tex):
    a = []
    for r, d in enumerate(DIRS):
        a.append((f'idle_{d}', tex, [(0, r)], 5.0, True))
    for r, d in enumerate(DIRS):
        a.append((f'walk_{d}', tex, [(c, r) for c in range(1, 5)], 8.0, True))
    return a


def write(name, textures, anims):
    ext = [f'[ext_resource type="Texture2D" path="res://art/characters/{t}.png" id="{i + 1}_{t}"]'
           for i, t in enumerate(textures)]
    tid = {t: f'{i + 1}_{t}' for i, t in enumerate(textures)}
    subs, out, n = [], [], 0
    for aname, tex, cells, fps, loop in anims:
        frames = []
        for (c, r) in cells:
            n += 1
            sid = f'AtlasTexture_{n}'
            subs.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("{tid[tex]}")\n'
                        f'region = Rect2({c * 32}, {r * 32}, 32, 32)\n')
            frames.append('{"duration": 1.0, "texture": SubResource("%s")}' % sid)
        out.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %s}'
                   % (', '.join(frames), 'true' if loop else 'false', aname, fps))
    txt = ('[gd_resource type="SpriteFrames" format=3]\n\n' + '\n'.join(ext) + '\n\n' + '\n'.join(subs)
           + '\n[resource]\nanimations = [' + ', '.join(out) + ']\n')
    open(os.path.join(OUT, f'{name}_frames.tres'), 'w').write(txt)


# Brann
a = base_anims('brann')
for r, d in enumerate(DIRS):
    a.append((f'attack_{d}', 'brann_actions', [(0, r), (1, r), (2, r)], 15.0, False))
for r, d in enumerate(DIRS):
    a.append((f'hurt_{d}', 'brann_actions', [(3, r)], 5.0, False))
a.append(('lift', 'brann_actions', [(4, 0)], 5.0, False))
a.append(('death', 'brann_actions', [(4, 1), (4, 2)], 3.0, False))
write('brann', ['brann', 'brann_actions'], a)

# Effet de coup d'épée
write('sword_slash', ['sword_slash'],
      [(f'slash_{d}', 'sword_slash', [(0, r), (1, r), (2, r)], 15.0, False) for r, d in enumerate(DIRS)])

# Corvan (normal et corrompu)
for n in ('corvan', 'corvan_corrupted'):
    a = base_anims(n)
    a.append(('hammer', f'{n}_actions', [(0, 0), (1, 0), (2, 0)], 6.0, False))
    a.append(('wounded', f'{n}_actions', [(3, 0)], 5.0, False))
    write(n, [n, f'{n}_actions'], a)

# Pip
a = base_anims('pip')
a.append(('crouch', 'pip_actions', [(0, 0)], 5.0, False))
write('pip', ['pip', 'pip_actions'], a)

# PNJ sans animation spéciale
for n in ('hulda', 'tobias', 'isolde', 'garrick'):
    write(n, [n], base_anims(n))
print('ok')
