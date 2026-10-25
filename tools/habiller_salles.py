"""Habillage automatique des salles du Temple des Racines (dessin v2 du tileset).

Ne modifie QUE les calques de tuiles Sol, Decor et Dessus. Les calques Murs et Objets, les collisions,
les ids d'objets et le reste du fichier .tmx sont recopiés tels quels.

1. Terre : chaque zone de tuiles « terre » (5) reçoit ses tuiles de bord (terrain Terre, 48–55 et 67–71)
   sur les dalles voisines : bord irrégulier et fondu au lieu d'un carré net.
2. Ombres (calque Decor, case vide) : sous un mur du haut (12), à droite d'un mur de gauche (13), dans
   l'angle (14).
3. Décor semé au hasard (graine fixe par salle, donc relancer le script donne le même résultat) sur les
   dalles libres du calque Decor : gravats, cailloux, herbe, champignons, flaque, vase brisé ; toile
   d'araignée dans les angles ; quelques dalles remplacées par les variantes 124 (racine) et 125 (mousse).
   Jamais sous un objet du calque Objets ni à côté d'une porte.
4. Racines pendantes (121) et lierre (122) sur quelques murs du haut (calque Dessus).

Usage : python tools/habiller_salles.py maps/donjon1/salle_01.tmx [...]
        python tools/habiller_salles.py --tout            (toutes les salles de maps/donjon1)
Idempotent : les tuiles déjà posées par une passe précédente sont reconnues et retirées avant la passe.
"""
import glob
import os
import random
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))

FLOOR = {0, 1, 2, 3, 4}
FLOOR_VARIANTS = {124, 125}
TERRE = 5
TERRE_TILES = {(0, 0, 1, 1): 48, (1, 1, 0, 0): 49, (0, 1, 0, 1): 50, (1, 0, 1, 0): 51,
               (0, 1, 1, 1): 52, (1, 0, 1, 1): 53, (1, 1, 0, 1): 54, (1, 1, 1, 0): 55,
               (0, 0, 0, 1): 67, (0, 0, 1, 0): 68, (0, 1, 0, 0): 69, (1, 0, 0, 0): 70, (1, 0, 0, 1): 71}
TERRE_EDGES = set(TERRE_TILES.values())
SHADOW_HAUT, SHADOW_GAUCHE, SHADOW_COIN = 12, 13, 14
SHADOWS = {SHADOW_HAUT, SHADOW_GAUCHE, SHADOW_COIN}
SPRINKLE = [(15, 0.02), (76, 0.018), (77, 0.026), (78, 0.008), (79, 0.007), (127, 0.005)]
TOILE = 123
HANGING = [(121, 0.13), (122, 0.10)]
AUTO_DECOR = {t for t, _ in SPRINKLE} | SHADOWS | {TOILE}
AUTO_DESSUS = {t for t, _ in HANGING}
WALL_TOP_FACE = {16, 26, 27}          # murs dont la face avant touche le sol en dessous
WALL_LEFT = {18}                      # murs de gauche (le sol est a leur droite)
WALL_TOP_FOR_HANGING = {16}
DOORS = {40, 41, 42, 43}
FLIP = 0xF0000000


def read_layers(text):
    """{nom: (debut, fin, largeur, valeurs)} pour chaque calque de tuiles CSV."""
    out = {}
    for m in re.finditer(r'<layer [^>]*name="([^"]+)"[^>]*width="(\d+)"[^>]*>\s*<data encoding="csv">(.*?)</data>',
                         text, re.S):
        vals = [int(v) for v in m.group(3).replace('\n', '').split(',') if v.strip()]
        out[m.group(1)] = (m.start(3), m.end(3), int(m.group(2)), vals)
    return out


def csv(vals, w):
    rows = [','.join(str(v) for v in vals[i:i + w]) for i in range(0, len(vals), w)]
    return '\n' + ',\n'.join(rows) + '\n'


def object_cells(root, W, H):
    cells = set()
    for og in root.iter('objectgroup'):
        for o in og.iter('object'):
            x, y = float(o.get('x', 0)), float(o.get('y', 0))
            w, h = float(o.get('width', 0)), float(o.get('height', 0))
            if o.get('gid'):
                y -= h
            x0, y0 = int(x // 32), int(y // 32)
            x1, y1 = int((x + max(w, 1) - 0.01) // 32), int((y + max(h, 1) - 0.01) // 32)
            for cy in range(y0, y1 + 1):
                for cx in range(x0, x1 + 1):
                    if 0 <= cx < W and 0 <= cy < H:
                        cells.add((cx, cy))
    return cells


def habiller(path):
    text = open(path, encoding='utf-8').read()
    root = ET.fromstring(text)
    W, H = int(root.get('width')), int(root.get('height'))
    ts = root.find('tileset')
    if ts is None or 'temple_racines' not in ts.get('source', '') or int(ts.get('firstgid')) != 1:
        print(f'  {os.path.basename(path)} : tileset inattendu, ignorée')
        return False
    L = read_layers(text)
    sol, decor, murs, dessus = (list(L[n][3]) for n in ('Sol', 'Decor', 'Murs', 'Dessus'))

    def tid(v):
        return (v & ~FLIP) - 1 if v else None

    def at(layer, x, y):
        if 0 <= x < W and 0 <= y < H:
            return tid(layer[y * W + x])
        return None

    def setv(layer, x, y, t):
        layer[y * W + x] = (t + 1) if t is not None else 0

    # --- 0. retirer ce qu'une passe precedente a pose (idempotence)
    for k in range(W * H):
        if tid(sol[k]) in TERRE_EDGES or tid(sol[k]) in FLOOR_VARIANTS:
            sol[k] = 1                                   # redevient une dalle
        if tid(decor[k]) in AUTO_DECOR:
            decor[k] = 0
        if tid(dessus[k]) in AUTO_DESSUS:
            dessus[k] = 0
    # La premiere passe a pu remplacer des dalles variees par la dalle 0 : on garde une variante stable
    rnd_v = random.Random(path.rsplit(os.sep, 1)[-1] + 'v')

    rnd = random.Random(os.path.basename(path))
    blocked = object_cells(root, W, H)
    near_door = set()
    for y in range(H):
        for x in range(W):
            if at(murs, x, y) in DOORS:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        near_door.add((x + dx, y + dy))

    def is_floor(x, y):
        return at(sol, x, y) in FLOOR and at(murs, x, y) is None

    def sol_visible(x, y):          # dalle visible autour d'un decor pose sur Murs (colonne, vase, statue)
        return at(sol, x, y) in FLOOR and at(murs, x, y) in (None, 113, 114, 116)

    # --- 1. terre : terrain par coins
    dirt = {(x, y) for y in range(H) for x in range(W) if at(sol, x, y) == TERRE}
    corner = lambda cx, cy: any((cx - dx, cy - dy) in dirt for dx in (0, 1) for dy in (0, 1))
    n_terre = 0
    for y in range(H):
        for x in range(W):
            if (x, y) in dirt or not sol_visible(x, y):
                continue
            bits = (corner(x, y), corner(x + 1, y), corner(x, y + 1), corner(x + 1, y + 1))
            bits = tuple(int(b) for b in bits)
            if any(bits) and bits in TERRE_TILES:
                setv(sol, x, y, TERRE_TILES[bits])
                n_terre += 1

    # --- 2. ombres
    n_ombre = 0
    for y in range(H):
        for x in range(W):
            if at(murs, x, y) is not None or at(decor, x, y) is not None:
                continue
            if at(sol, x, y) not in FLOOR | {TERRE} | TERRE_EDGES:
                continue
            haut = at(murs, x, y - 1) in WALL_TOP_FACE
            gauche = at(murs, x - 1, y) in WALL_LEFT
            if haut or gauche:
                setv(decor, x, y, SHADOW_COIN if haut and gauche else SHADOW_HAUT if haut else SHADOW_GAUCHE)
                n_ombre += 1

    # --- 3. decor seme, toiles, variantes de dalles
    n_decor = 0
    for y in range(H):
        for x in range(W):
            if not is_floor(x, y) or (x, y) in blocked or (x, y) in near_door:
                continue
            if at(decor, x, y) is not None:
                continue
            angle = at(murs, x - 1, y) is not None and at(murs, x, y - 1) is not None
            if angle and rnd.random() < 0.6:
                setv(decor, x, y, TOILE); n_decor += 1
                continue
            r = rnd.random()
            acc = 0
            for t, p in SPRINKLE:
                acc += p
                if r < acc:
                    setv(decor, x, y, t); n_decor += 1
                    break
            else:
                r2 = rnd_v.random()
                if r2 < 0.035:
                    setv(sol, x, y, 125)
                elif r2 < 0.05:
                    setv(sol, x, y, 124)

    # --- 4. racines pendantes et lierre sur les murs du haut
    for y in range(H):
        for x in range(W):
            if at(murs, x, y) in WALL_TOP_FOR_HANGING and at(dessus, x, y) is None and (x, y + 1) not in near_door:
                r = rnd.random()
                acc = 0
                for t, p in HANGING:
                    acc += p
                    if r < acc:
                        setv(dessus, x, y, t)
                        break

    # --- ecriture : on ne remplace que le contenu CSV des 3 calques
    new = text
    for name, vals in sorted((('Sol', sol), ('Decor', decor), ('Dessus', dessus)),
                             key=lambda kv: -L[kv[0]][0]):
        a, b, w, _ = L[name]
        new = new[:a] + csv(vals, w) + new[b:]
    ET.fromstring(new)                                       # le fichier reste du XML valide
    if new != text:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
    print(f'  {os.path.basename(path)} : {n_terre} bords de terre, {n_ombre} ombres, {n_decor} décors')
    return True


def main():
    args = sys.argv[1:]
    paths = sorted(glob.glob(os.path.join(ROOT, 'maps', 'donjon1', '*.tmx'))) if args == ['--tout'] else args
    for p in paths:
        habiller(p)


if __name__ == '__main__':
    main()
