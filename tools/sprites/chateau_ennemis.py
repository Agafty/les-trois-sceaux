"""Ennemis du château (Chevalier corrompu, Œil de Morvath) + orbe sombre et son éclat — Les Trois Sceaux.  PLACEHOLDERS à retoucher.

Usage : python tools/sprites/chateau_ennemis.py        (sans Pillow : encodeur PNG de tsplan.py)
Produit dans art/enemies/ (cases 32x32, une ligne par animation) :
  chevalier_corrompu.png / .json / _frames.tres
  oeil_morvath.png / .json / _frames.tres
  projectiles.png / .json / _frames.tres   (acorn, morvath_orb, pebble inchangés + morvath_orb_burst)
Les 8 premières lignes du chevalier (idle_* / walk_*, 4 directions) viennent de enemies.py (mêmes grilles ASCII, relues
dans ce fichier) : seul le DOS est éclairci (gambison crème, « dos nu et plus clair »). Les lignes suivantes sont ajoutées à la fin.
Pas de variante rouge (décision validée).
Lumière en haut à gauche, contour sombre d'1 px, bas du corps sur la ligne y = 31.
"""
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'art', 'enemies')
sys.path.insert(0, HERE)

# enemy_lib / engine importent Pillow pour leurs rendus ; ici on n'en a pas besoin (rendu par save_png).
_pil = types.ModuleType('PIL')
_pil.Image = types.ModuleType('PIL.Image')
sys.modules.setdefault('PIL', _pil)
sys.modules.setdefault('PIL.Image', _pil.Image)

import engine  # noqa: E402
from enemy_lib import *  # noqa: E402,F401
from enemy_lib import write_tres, blank, put, paint, ellipse, rect, line, outline, mirror, shift, cp, recolor  # noqa: E402
from tsplan import save_png  # noqa: E402

# --- grilles du chevalier de base : relues dans enemies.py (une seule source de dessin)
_src = open(os.path.join(HERE, 'enemies.py'), encoding='utf-8').read()
_a = _src.index('def humanoid_rows')
_b = _src.index('def humanoid_anims')
_c = _src.index('KNIGHT_DOWN = [')
_d = _src.index("SHEETS['chevalier_corrompu']")
NS = {'engine': engine, 'blank': blank}
exec(_src[_a:_b] + '\n' + _src[_c:_d], NS)  # noqa: S102

PAL = engine.PALETTE


def render(rows):
    w = max(len(r) for r in rows) * 32
    pix = [[None] * w for _ in range(len(rows) * 32)]
    for r, frames in enumerate(rows):
        for c, g in enumerate(frames):
            for y in range(32):
                for x in range(32):
                    col = PAL[g[y][x]]
                    if col:
                        pix[r * 32 + y][c * 32 + x] = engine.rgba(col)
    return pix


def build(name, anims):
    """anims : liste de (nom, [grilles], fps, boucle). Une ligne de planche par animation."""
    rows, specs = [], []
    for aname, frames, fps, loop in anims:
        r = len(rows)
        rows.append(frames)
        specs.append((aname, [(c, r) for c in range(len(frames))], fps, loop))
    save_png(os.path.join(OUT, f'{name}.png'), render(rows))
    write_tres(OUT, 'enemies', name, [name], [(a, name, cells, f, l) for a, cells, f, l in specs])
    with open(os.path.join(OUT, f'{name}.json'), 'w') as f:
        json.dump({'image': f'{name}.png', 'frame_size': [32, 32],
                   'animations': {a: {'cells': cells, 'fps': fp, 'loop': lp} for a, cells, fp, lp in specs}}, f, indent=1)
    return rows


# =============================================================== CHEVALIER CORROMPU
K_FRONT, K_SHIELD, K_SWORD, K_SIDE_SHIELD = NS['K_FRONT'], NS['K_SHIELD'], NS['K_SWORD'], NS['K_SIDE_SHIELD']


def _lighten_back(rows):
    """Dos clair : sous les épaules, le dos nu est en gambison crème (rouge sombre dans enemies.py)."""
    return [r.replace('F', '2').replace('4', '9') if y >= 13 else r for y, r in enumerate(rows)]


VIEWS = {'down': NS['KNIGHT_DOWN'], 'up': _lighten_back(NS['KNIGHT_UP']), 'left': NS['KNIGHT_LEFT']}
BASE = {'down': engine.grid(VIEWS['down'], half=True), 'up': engine.grid(VIEWS['up'], half=True),
        'left': engine.grid(VIEWS['left'])}
FRONT_SWORD = [('' if r == '' else r[:8].ljust(8, '.') + '.' * 24) for r in K_SWORD]
FRONT_SHIELD = [('' if r == '' else '.' * 8 + r[8:].ljust(24, '.')) for r in K_SHIELD]


def ov(g, rows):
    """Pose des lignes ASCII (32 colonnes) sur la grille g ('.' = inchangé, '_' = transparent)."""
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != '.':
                put(g, x, y, '.' if c == '_' else c)
    return g


def drop_top(g, n=1, top=24):
    """Fente : le haut du corps descend de n px, les pieds ne bougent pas."""
    g = cp(g)
    for _ in range(n):
        for y in range(top, 0, -1):
            g[y] = g[y - 1][:]
        g[0] = ['.'] * 32
    return g


def blade(g, x0, y0, x1, y1, glow=None):
    """Lame de 2 px de large, claire à gauche, reflet sombre à droite ; glow = lueur sur les bords."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
        put(g, x, y, 'g')
        put(g, x + 1, y, 'h')
        if glow and i % 2 == 0:
            put(g, x - 1, y, glow)
            put(g, x + 2, y, glow)


def guard(g, x, y, w=5):
    for i in range(w):
        put(g, x + i, y, 'K')
    put(g, x + w // 2, y + 1, '6')


def arc(g, pts, c='g', c2='h'):
    for i, (x, y) in enumerate(pts):
        put(g, x, y, c if i % 2 == 0 else c2)


def shield_rows(view, lowered=False):
    rows = FRONT_SHIELD if view == 'down' else [r[::-1] for r in FRONT_SHIELD] if view == 'up' else K_SIDE_SHIELD
    if not lowered:
        return rows
    top = 13 if view == 'left' else 14      # bouclier baissé : raccourci de 2 lignes, posé contre la jambe
    body = [r for i, r in enumerate(rows[top:]) if i not in (3, 6)]
    return [''] * (top + 7) + body


def sword_rows(view):
    return FRONT_SWORD if view == 'down' else [r[::-1].ljust(32, '.') for r in FRONT_SWORD] if view == 'up' else []


def knight(view, shield='up', sword=True, drop=0):
    g = cp(BASE[view])
    if sword:
        ov(g, sword_rows(view))
    if shield:
        ov(g, shield_rows(view, shield == 'low'))
    return drop_top(g, drop) if drop else g


def windup(view, beat):
    """Annonce : épée dressée au-dessus de la tête, lueur rouge qui bat (2 images), bouclier levé."""
    g = knight(view, 'up', False)
    glow = '4' if beat == 0 else 'F'
    x = {'down': 3, 'up': 27, 'left': 5}[view]
    blade(g, x, 1, x, 11, glow)
    guard(g, x - 2, 12)
    return outline(g)


def attack(view, step):
    """Coup (3 images) : armé, frappe avec croissant de lumière (le haut du corps plonge), retour."""
    g = knight(view, 'up', False, drop=1 if step == 1 else 0)
    if view == 'down':
        if step == 0:
            blade(g, 3, 12, 11, 2, '4'); guard(g, 1, 12)
        elif step == 1:
            blade(g, 3, 17, 12, 29); guard(g, 1, 16)
            arc(g, [(1, 9), (0, 12), (0, 15), (0, 18), (1, 21), (2, 24), (4, 27), (7, 29), (10, 30)])
        else:
            blade(g, 3, 20, 6, 30); guard(g, 1, 19)
            arc(g, [(1, 24), (3, 27), (6, 29)], 'h', 'k')
    elif view == 'up':
        if step == 0:
            blade(g, 27, 12, 20, 2, '4'); guard(g, 25, 12)
        elif step == 1:
            blade(g, 27, 8, 14, 1); guard(g, 25, 9)
            arc(g, [(30, 12), (31, 9), (29, 6), (26, 3), (22, 1), (18, 0), (14, 0)])
        else:
            blade(g, 27, 4, 22, 0); guard(g, 25, 5)
            arc(g, [(29, 7), (27, 4), (24, 2)], 'h', 'k')
    else:
        if step == 0:
            blade(g, 7, 12, 3, 2, '4'); guard(g, 5, 12)
        elif step == 1:
            blade(g, 9, 15, 0, 15)
            for i in range(3):
                put(g, 9, 14 + i, 'K')
            arc(g, [(2, 7), (0, 9), (0, 12), (0, 17), (0, 19), (1, 22), (3, 25)])
        else:
            blade(g, 9, 19, 2, 26)
            for i in range(3):
                put(g, 9, 18 + i, 'K')
            arc(g, [(1, 20), (1, 23), (3, 26)], 'h', 'k')
    return outline(g)


def recover(view, step):
    """Récupération : bouclier baissé contre la jambe, tête penchée, épée qui traîne (2 images : souffle)."""
    return outline(knight(view, 'low', True, drop=1 + step))


def fallen(back, step):
    """Renversé : à terre, sonné ; 2 images (étoiles dorées). back = vu de dos (gambison clair)."""
    g = blank()
    torso = ('2', '9', 'g') if back else ('q', 'I', 'p')
    ellipse(g, 17, 23, 8.5, 5.5, *torso)                        # buste
    ellipse(g, 7, 22, 5, 5, 'q', 'I', 'p')                       # casque
    if not back:
        for (x, y) in ((3, 21), (3, 22), (4, 23)):
            put(g, x, y, 'K' if x == 3 else 'I')                 # fente de visière
    ellipse(g, 26, 23, 5, 3.6, 'q', 'I', 'p')                    # jambes
    rect(g, 28, 21, 30, 25, 'I')                                 # bottes
    ellipse(g, 12, 17, 3.2, 2.2, 'q', 'I', 'p')                  # bras
    ellipse(g, 15, 28, 6, 2.6, 'k', 'I', 'h')                    # bouclier à plat
    put(g, 15, 28, 'K'); put(g, 16, 28, 'K')
    if not back:
        paint(g, 15, 21, ['.pp.', 'pFp.', '.pp.'])               # tache de corruption sur le plastron
    blade(g, 21, 14, 29, 9)                                      # épée tombée
    guard(g, 19, 15, 3)
    for (x, y) in [[(5, 11), (11, 8), (8, 14)], [(8, 10), (3, 13), (13, 11)]][step]:
        put(g, x, y, 'K'); put(g, x, y - 1, 'K')
    return outline(g)


def knight_anims():
    rows = NS['humanoid_rows'](VIEWS, 25, 16, {'down': K_FRONT, 'up': [r[::-1] for r in K_FRONT],
                                               'left': K_SIDE_SHIELD})
    dirs = ['down', 'up', 'left', 'right']
    anims = []
    for r, d in enumerate(dirs):
        anims.append((f'idle_{d}', [rows[r][0]], 5.0, True))
        anims.append((f'walk_{d}', rows[r][1:], 8.0, True))

    def four(make, n):
        out = {v: [make(v, i) for i in range(n)] for v in ('down', 'up', 'left')}
        out['right'] = [mirror(g) for g in out['left']]
        return out
    sets = [('windup', four(windup, 2), 6.0, True), ('attack', four(attack, 3), 14.0, False),
            ('recover', four(recover, 2), 3.0, True)]
    fl = {'down': [fallen(False, i) for i in range(2)], 'up': [fallen(True, i) for i in range(2)]}
    fl['left'] = fl['down']
    fl['right'] = [mirror(g) for g in fl['down']]
    sets.append(('fallen', fl, 4.0, True))
    for name, per_dir, fps, loop in sets:
        for d in dirs:
            anims.append((f'{name}_{d}', per_dir[d], fps, loop))
    return anims


# =============================================================== ŒIL DE MORVATH
def oeil(state, glint=0):
    """Œil doré dans un cadre de pierre (niche) : paupière fermée, mi-ouverte, ouverte, tir."""
    g = blank()
    rect(g, 3, 3, 28, 28, 'h')                                   # pierre
    for i in range(3, 29):
        put(g, i, 3, 'g'); put(g, 3, i, 'g')
        put(g, i, 28, 'k'); put(g, 28, i, 'k')
    for i in range(4, 15):
        put(g, i, 4, 'g')
    for i in range(16, 28):
        put(g, i, 27, 'k')
    for x in range(4, 28):
        put(g, x, 9, 'k'); put(g, x, 22, 'k')                    # joints de la maçonnerie
    for y in (4, 5, 6, 7, 8):
        put(g, 9, y, 'k'); put(g, 22, y, 'k')
    for y in (23, 24, 25, 26, 27):
        put(g, 15, y, 'k'); put(g, 24, y, 'k')
    for (x, y) in [(5, 5), (26, 5), (5, 26), (26, 26)]:
        put(g, x, y, 'k')                                        # rivets
    for (x, y) in [(4, 5), (4, 6), (5, 7), (5, 4), (6, 4), (27, 26), (26, 27), (27, 25), (25, 27)]:
        put(g, x, y, 'q')                                        # corruption dans les coins
    put(g, 4, 6, 'p'); put(g, 26, 27, 'p')
    ellipse(g, 16, 16, 10.5, 9, 'I')                             # niche sombre
    if state == 'closed':
        ellipse(g, 16, 16, 8.5, 4.2, 'q', 'I', 'p', 0.6, -0.6)   # paupière violette
        line(g, 8, 16, 24, 16, 'I')
        for x in (10, 13, 16, 19, 22):
            put(g, x, 17, '0')
        put(g, 14, 14, 'p'); put(g, 15, 14, 'p')
    else:
        ry = 2.6 if state == 'half' else 5.5
        ellipse(g, 16, 16, 8.8, ry + 0.8, 'q')                   # paupières
        ellipse(g, 16, 16, 7.8, ry, 'K', '6', 'g', 0.55, -0.6)   # œil doré
        pr = 1.3 if state != 'shoot' else 2.4
        ellipse(g, 16 + (glint if state == 'open' else 0), 16, pr, min(ry - 0.4, 4.2), 'I')   # pupille fendue
        if ry > 4:
            put(g, 12, 13, 'g'); put(g, 13, 13, 'g'); put(g, 12, 14, 'g')   # reflet
        if state == 'shoot':
            for (x, y) in [(16, 7), (16, 8), (16, 24), (16, 25), (7, 16), (6, 16), (25, 16), (26, 16),
                           (9, 9), (22, 22), (22, 9), (9, 22)]:
                put(g, x, y, 'g')
    return outline(g)


def eclat(step):
    """Éclat doré (3 images) : l'œil lance une gerbe d'étincelles dorées qui grossit puis se disperse."""
    g = oeil('shoot')
    r0 = [7, 9, 11][step]
    dirs8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    for k, (dx, dy) in enumerate(dirs8):
        for rr in range(r0, r0 + 3 - step):
            x, y = 16 + dx * rr, 16 + dy * rr
            if 0 <= x < 32 and 0 <= y < 32:
                put(g, x, y, 'g' if (rr + k) % 2 == 0 else 'K')
    if step < 2:
        ellipse(g, 16, 16, 2.2 - step, 2.2 - step, 'g')
    return g


def eye_anims():
    return [('closed', [oeil('closed')], 4.0, True),
            ('open', [oeil('closed'), oeil('half'), oeil('open')], 8.0, False),
            ('idle_open', [oeil('open', 0), oeil('open', 1)], 3.0, True),
            ('shoot', [oeil('shoot'), oeil('open')], 8.0, False),
            ('flash', [eclat(0), eclat(1), eclat(2)], 12.0, False)]


# =============================================================== PROJECTILES
def burst(step):
    """Éclat de l'orbe sombre à l'impact (3 images) : noyau doré, éclats violets qui s'écartent."""
    g = blank()
    if step == 0:
        ellipse(g, 16, 16, 5, 5, 'q', 'I', 'p')
        ellipse(g, 16, 16, 2.4, 2.4, 'K', None, 'g')
        for (x, y) in [(16, 8), (16, 24), (8, 16), (24, 16)]:
            put(g, x, y, 'p')
    elif step == 1:
        ellipse(g, 16, 16, 2.2, 2.2, 'K', None, 'g')
        for (dx, dy) in [(6, 0), (-6, 0), (0, 6), (0, -6), (4, 4), (-4, 4), (4, -4), (-4, -4)]:
            ellipse(g, 16 + dx, 16 + dy, 1.6, 1.6, 'p', 'q')
    else:
        for (dx, dy) in [(9, 0), (-9, 0), (0, 9), (0, -9), (6, 6), (-6, 6), (6, -6), (-6, -6)]:
            put(g, 16 + dx, 16 + dy, 'p')
        for (dx, dy) in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
            put(g, 16 + dx, 16 + dy, 'K')
    return outline(g) if step < 2 else g


def projectile_anims():
    ns = {'blank': blank, 'ellipse': ellipse, 'put': put, 'paint': paint, 'outline': outline, 'mirror': mirror,
          'shift': shift}
    a = _src.index('def gland')
    b = _src.index("build_enemy(OUT, 'projectiles'")
    exec(_src[a:b], ns)  # noqa: S102
    return [('acorn', [ns['gland'](0), ns['gland'](1)], 10.0, True),
            ('morvath_orb', [ns['orbe'](0), ns['orbe'](1)], 10.0, True),
            ('pebble', [ns['caillou_proj']()], 1.0, True),
            ('morvath_orb_burst', [burst(0), burst(1), burst(2)], 14.0, False)]


if __name__ == '__main__':
    build('chevalier_corrompu', knight_anims())
    build('oeil_morvath', eye_anims())
    build('projectiles', projectile_anims())
    print('chateau_ennemis : chevalier_corrompu, oeil_morvath, projectiles ok')
