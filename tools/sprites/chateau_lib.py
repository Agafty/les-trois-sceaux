"""Outils communs aux plans `route_chateau` et `chateau` (fin du jeu) — Les Trois Sceaux.

Fournit : un Sheet dont le tableau des terrains accepte les terrains à une seule couleur (murs), des fonctions d'ajout courtes,
le bloc de 15 murs (ids first..first+14) avec son terrain Wang, et le rendu des aperçus à partir des aperçus ASCII de maps/chateau/plan.md.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import *  # noqa: E402,F401,F403
import tsplan  # noqa: E402

PIL2 = [(2, 2, 30, 30)]
PIL2R = [(0, 2, 30, 30)]
PIL2B = [(2, 0, 30, 30)]
PIL2BR = [(0, 0, 30, 30)]
DOORH = [(0, 0, 6, 32), (26, 0, 6, 32)]
DOORV = [(0, 0, 32, 4), (0, 28, 32, 4)]

WALLS = {0: ('haut', 'Mur du haut : sol en dessous, face avant visible', (1, 1, 0, 0)),
         1: ('bas', 'Mur du bas : sol au-dessus', (0, 0, 1, 1)),
         2: ('gauche', 'Mur de gauche : sol à droite', (1, 0, 1, 0)),
         3: ('droite', 'Mur de droite : sol à gauche', (0, 1, 0, 1)),
         4: ('coin_int_hg', 'Coin intérieur haut-gauche : sol seulement en bas-droite', (1, 1, 1, 0)),
         5: ('coin_int_hd', 'Coin intérieur haut-droite : sol seulement en bas-gauche', (1, 1, 0, 1)),
         6: ('coin_int_bg', 'Coin intérieur bas-gauche : sol seulement en haut-droite', (1, 0, 1, 1)),
         7: ('coin_int_bd', 'Coin intérieur bas-droite : sol seulement en haut-gauche', (0, 1, 1, 1)),
         8: ('coin_ext_hg', 'Coin extérieur haut-gauche d\'un bloc de mur : mur seulement en bas-droite', (0, 0, 0, 1)),
         9: ('coin_ext_hd', 'Coin extérieur haut-droite d\'un bloc de mur : mur seulement en bas-gauche', (0, 0, 1, 0)),
         10: ('coin_ext_bg', 'Coin extérieur bas-gauche d\'un bloc de mur : mur seulement en haut-droite', (0, 1, 0, 0)),
         11: ('coin_ext_bd', 'Coin extérieur bas-droite d\'un bloc de mur : mur seulement en haut-gauche', (1, 0, 0, 0)),
         12: ('plein', 'Mur plein (intérieur d\'un mur épais)', (1, 1, 1, 1)),
         13: ('diag_a', 'Mur en diagonale (haut-gauche et bas-droite) : complète le terrain', (1, 0, 0, 1)),
         14: ('diag_b', 'Mur en diagonale (haut-droite et bas-gauche) : complète le terrain', (0, 1, 1, 0))}


class PSheet(Sheet):
    dev = ''
    terrains_txt = ''

    def md(self, script):
        w, self.wang = self.wang, {}
        try:
            o = super().md(script)
        finally:
            self.wang = w
        o = o.replace('\n## Calques', self.dev + '\n## Calques', 1)
        if self.terrains_txt:
            o = o.replace('## Notes', self.terrains_txt + '## Notes', 1)
        return o


class Adder:
    """Raccourcis d'ajout (numéro explicite)."""

    def __init__(self, S):
        self.S = S

    def grp(self, first, titre, note='', align=None):
        self.S.cur = first
        self.S.group(titre, note, align=align)

    def at(self, i, nom, role, calque, coll, cat, **k):
        self.S.cur = i
        return self.S.add(nom, role, calque, coll, cat, **k)

    def so(self, i, nom, role, cat, **k):
        return self.at(i, nom, role, 'Sol', None, cat, **k)

    def de(self, i, nom, role, cat, **k):
        return self.at(i, nom, role, 'Decor', None, cat, **k)

    def mu(self, i, nom, role, coll, cat, **k):
        return self.at(i, nom, role, 'Murs', coll, cat, **k)

    def du(self, i, nom, role, cat, coll=None, **k):
        return self.at(i, nom, role, 'Dessus', coll, cat, **k)

    def walls(self, first, prefix, cat, wname, label, skin=''):
        """15 murs (terrain Wang à une couleur) aux ids first..first+14."""
        tiles = {}
        for k, (n, r, b) in WALLS.items():
            self.mu(first + k, f'{prefix}_{n}', r + (f' [{skin}]' if skin else ''), FULL, cat)
            tiles[first + k] = tuple(1 if c else 0 for c in b)
        self.S.wang[wname] = dict(colors=[(label, tsplan.CATS[cat])], tile=first + 12, tiles=tiles, fam='')
        return first


def terrain_table(S, extra=()):
    rows = ['## Terrains (Wang, par coins)', '',
            'Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Les terrains de murs n\'ont qu\'une couleur '
            '(le reste de la case = vide) ; ils se peignent sur le calque `Murs` et la collision est dans les tuiles.', '',
            '| Terrain | Couleurs | Tuiles | Calque |', '| --- | --- | --- | --- |']
    for n, w in S.wang.items():
        ids = sorted(w['tiles'])
        cols = ' / '.join(c[0] for c in w['colors'])
        rows.append(f'| `{n}` | {cols} | {ids[0]} à {ids[-1]} | {"Murs" if len(w["colors"]) == 1 else "Sol (base) + Murs (bords)"} |')
    return '\n'.join(rows) + '\n\n'


# ---------------------------------------------------------------- aperçus
def parse_maps(path):
    txt = open(path, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'<!-- (\w+) -->\s*```text\n(.*?)```', txt, re.S):
        out[m.group(1)] = m.group(2).strip('\n').split('\n')
    return out


def tile_img(S, nom):
    return S.plan_tile(S.tiles[S.names[nom]])


def blit(px, img, ox, oy):
    for y in range(T):
        for x in range(T):
            if img[y][x] is not None:
                px[oy + y][ox + x] = img[y][x]


def marker(px, ox, oy, color, label=None):
    c = rgba(color)
    d = shade(c, 0.4)
    for y in range(9, 23):
        for x in range(9, 23):
            px[oy + y][ox + x] = d if x in (9, 22) or y in (9, 22) else c


def render(S, rows, cell, markers):
    """cell(x, y, ch, rows) -> liste de noms de tuiles (du bas vers le haut) ; markers : ch -> couleur."""
    H, W = len(rows), len(rows[0])
    px = [[None] * (W * T) for _ in range(H * T)]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            for n in cell(x, y, ch, rows):
                blit(px, tile_img(S, n), x * T, y * T)
            if ch in markers:
                marker(px, x * T, y * T, markers[ch])
    return px


def stack(images, gap=8):
    W = max(len(i[0]) for i in images)
    H = sum(len(i) for i in images) + gap * (len(images) - 1)
    px = [[(14, 12, 24, 255)] * W for _ in range(H)]
    y0 = 0
    for im in images:
        for y, row in enumerate(im):
            for x, c in enumerate(row):
                if c is not None:
                    px[y0 + y][x] = c
        y0 += len(im) + gap
    return px


def wall_face(rows, x, y, floor_chars, names):
    """Choisit la face de mur visible d'après le voisinage (aperçu seulement, pas un vrai autotile)."""
    def f(dx, dy):
        xx, yy = x + dx, y + dy
        return 0 <= yy < len(rows) and 0 <= xx < len(rows[yy]) and rows[yy][xx] in floor_chars
    if f(0, 1):
        return names['haut']
    if f(0, -1):
        return names['bas']
    if f(1, 0):
        return names['gauche']
    if f(-1, 0):
        return names['droite']
    return names['plein']
