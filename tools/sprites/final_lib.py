"""Assemblage du dessin final d'un tileset décrit par tsplan.Sheet : chaque tuile est dessinée par REG[nom](nom, tuile).

Les numéros ne bougent pas (le catalogue est celui du plan). Une tuile sans fonction de dessin garde son aplat de plan
et est signalée.
"""
import os

import tsplan
from tsplan import T, ROOT, save_png, stamp_number


def render(S, REG, missing_ok=False):
    S.finish()
    W, H = S.cols * T, S.rows * T
    px = [[None] * W for _ in range(H)]
    missing = []
    for i, d in S.tiles.items():
        fn = REG.get(d['nom'])
        if fn is None:
            missing.append(d['nom'])
            img = S.plan_tile(d)
        else:
            img = fn(d['nom'], d)
            assert len(img) == T and all(len(r) == T for r in img), (d['nom'], len(img), len(img[0]))
        ox, oy = (i % S.cols) * T, (i // S.cols) * T
        for y in range(T):
            for x in range(T):
                px[oy + y][ox + x] = img[y][x]
    if missing:
        print('SANS DESSIN :', len(missing), missing[:40])
    return px


def numbered(S, px, scale=2):
    W, H = len(px[0]), len(px)
    big = [[px[y // scale][x // scale] for x in range(W * scale)] for y in range(H * scale)]
    for i in S.tiles:
        stamp_number(big, (i % S.cols) * T * scale + 1, (i // S.cols) * T * scale + 1, i, scale)
    return big


def save_final(S, px, script, brume=None):
    out_t = os.path.join(ROOT, 'art', 'tilesets')
    save_png(os.path.join(out_t, f'{S.name}.png'), px)
    save_png(os.path.join(out_t, f'{S.name}_numeros.png'), numbered(S, px))
    if brume is not None:
        save_png(os.path.join(out_t, f'{S.name}_brume.png'), brume)
    with open(os.path.join(ROOT, 'maps', 'tilesets', f'{S.name}.tsx'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(S.tsx())
    md = S.md(script)
    md = md.replace('**État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro)',
                    '**État : DESSIN FINAL** (les numéros sont ceux du plan, aucune tuile n\'a bougé)')
    md = md.replace('Le plan est en aplats : **la couleur indique la famille** (vert herbe, gris-bleu pavés, brun terre, bleu eau, rouge/gris/jaune toits, orange portes et blocages…) ; une zone plus sombre dans une tuile = zone solide.',
                    'Les collisions sont dans le tileset (voir la colonne Collision).')
    md = md.replace('Le plan est en aplats : **la couleur indique la famille** ; une zone plus sombre dans une tuile = zone solide.',
                    'Les collisions sont dans le tileset (voir la colonne Collision).')
    with open(os.path.join(out_t, f'{S.name}_plan.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(md)
    print(f'{S.name} : {len(S.tiles)} tuiles dessinées sur {S.cols * S.rows} cases.')


def sheet_crop(px, c0, r0, c1, r1):
    return [row[c0 * T:c1 * T] for row in px[r0 * T:r1 * T]]
