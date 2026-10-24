"""Objets du donjon 1 : portes (4 types), interrupteur a fleche, icones 16x16.

Usage : python donjon_objets.py [dossier_apercu]
Portes et interrupteur : planches 64x32 = 2 cases 32x32 (0 = ferme/inactif, 1 = ouvert/active).
Icones : 16x16 dans art/ui/. Sans Pillow : encodeur PNG de coffres.py (zlib + struct).
"""
import os
import sys
import coffres as C
from coffres import blank, put, rect, outline, sheet, background, save_png

ROOT = os.path.join(C.HERE, '..', '..')
PUZ = os.path.join(ROOT, 'art', 'puzzles')
UI = os.path.join(ROOT, 'art', 'ui')

C.PAL.update({
    'W': '#7a6a88', 'V': '#4e4058', 'U': '#382e42', 'X': '#b8a8c0',      # pierre du temple
    'T': '#241a22', 'S': '#3a1a4a', 'R': '#6a2a7a',                       # ronces
    'e': '#d6c49c', 'E': '#b09468',                                       # parchemin
    'B': '#263a5e', 'b': '#3c5a8a', 'c': '#7a9ac0', 'd': '#b8d0e8',       # plume bleutee
})


def grid(rows):
    g = blank(16, 16)
    for y, r in enumerate(rows):
        assert len(r) == 16, r
        for x, ch in enumerate(r):
            g[y][x] = ch
    assert len(rows) == 16
    return g


# ---------------------------------------------------------------- portes
X0, X1, Y0, Y1 = 3, 28, 3, 30      # emprise : couvre le passage (20 px haut/bas, 24 px cotes)


def hinges(g, metal=('h', 'k')):
    """Frame ouverte : seulement les gonds (4 petites pattes) pour laisser voir le passage."""
    for (x, y) in ((X0, 7), (X0, 24), (X1 - 1, 7), (X1 - 1, 24)):
        rect(g, x, y, x + 1, y + 2, metal[0])
        rect(g, x + 1, y, x + 1, y + 2, metal[1])
    outline(g)
    return g


def planks(g, cols):
    """Battant de bois : planches verticales, lumiere a gauche."""
    rect(g, X0, Y0, X1, Y1, 'M')
    rect(g, X0, Y0, X1, Y0, 'L')
    rect(g, X0, Y1, X1, Y1, 'D')
    rect(g, X1, Y0, X1, Y1, 'D')
    rect(g, X0, Y0, X0, Y1, 'L')
    for x in cols:
        rect(g, x, Y0 + 1, x, Y1 - 1, 'D')
        rect(g, x + 1, Y0 + 1, x + 1, Y1 - 1, 'L')


def lock(g, cx, cy, fer, orne=False):
    """Grosse serrure : plaque + trou de serrure."""
    mc, mm, md = fer
    rect(g, cx - 5, cy - 6, cx + 5, cy + 6, md)
    rect(g, cx - 4, cy - 5, cx + 4, cy + 5, mm)
    rect(g, cx - 4, cy - 5, cx + 4, cy - 5, mc)
    rect(g, cx - 4, cy - 5, cx - 4, cy + 5, mc)
    rect(g, cx - 1, cy - 3, cx + 1, cy - 1, 'I')
    rect(g, cx, cy, cx, cy + 3, 'I')
    rect(g, cx - 1, cy + 3, cx + 1, cy + 3, 'I')
    if orne:
        for (x, y) in ((cx - 3, cy - 4), (cx + 3, cy - 4), (cx - 3, cy + 4), (cx + 3, cy + 4)):
            put(g, x, y, 'p')


def door_cle():
    c = blank(32, 32)
    planks(c, (9, 15, 21))
    for y in (8, 24):                                  # sangles de fer
        rect(c, X0 + 1, y, X1 - 1, y + 2, 'h')
        rect(c, X0 + 1, y, X1 - 1, y, 'g')
        rect(c, X0 + 1, y + 2, X1 - 1, y + 2, 'k')
        for x in (X0 + 3, X1 - 3):
            put(c, x, y + 1, 'k')
    lock(c, 16, 16, ('g', 'h', 'k'))
    outline(c)
    return [c, hinges(blank(32, 32))]


def door_grande_cle():
    c = blank(32, 32)
    planks(c, (10, 21))
    for (a, b, c2, d) in ((X0, Y0, X1, Y0 + 2), (X0, Y1 - 2, X1, Y1), (X0, Y0, X0 + 2, Y1), (X1 - 2, Y0, X1, Y1)):
        rect(c, a, b, c2, d, 'o')                      # cadre dore
    rect(c, X0, Y0, X1, Y0, 'y')
    rect(c, X0, Y0, X0, Y1, 'y')
    rect(c, X0, Y1, X1, Y1, 'p')
    rect(c, X1, Y0, X1, Y1, 'p')
    rect(c, X0 + 3, 8, X1 - 3, 9, 'o')
    rect(c, X0 + 3, 23, X1 - 3, 24, 'o')
    for (x, y) in ((6, 6), (25, 6), (6, 27), (25, 27), (6, 16), (25, 16)):   # clous dores
        put(c, x, y, 'y')
        put(c, x + 1, y + 1, 'p')
    lock(c, 16, 17, ('y', 'o', 'p'), True)
    rect(c, 15, 7, 17, 9, 'F')                         # gemme rouge au-dessus de la serrure
    put(c, 15, 7, 'w')
    put(c, 16, 8, '4')
    outline(c)
    return [c, hinges(blank(32, 32), ('y', 'p'))]


def door_ennemis():
    c = blank(32, 32)
    rect(c, X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, 'I')       # fond sombre entre les barreaux
    for bx in (6, 12, 18, 24):                         # barreaux de ronces noires
        rect(c, bx, Y0, bx + 2, Y1, 'T')
        rect(c, bx, Y0, bx, Y1, 'R')
        rect(c, bx + 1, Y0 + 2, bx + 1, Y1 - 2, 'S')
        rect(c, bx, Y0 + 1, bx + 2, Y0 + 1, 'R')
        put(c, bx, 10, 'R')
        put(c, bx + 1, 20, 'R')
        put(c, bx, 25, 'R')
        put(c, bx - 1, 8, 'T'); put(c, bx - 2, 7, 'T')     # epines alternees
        put(c, bx + 3, 14, 'T'); put(c, bx + 4, 13, 'T')
        put(c, bx - 1, 21, 'T'); put(c, bx - 2, 20, 'T')
        put(c, bx + 3, 27, 'T'); put(c, bx + 4, 26, 'T')
    for y in (9, 22):                                  # traverses
        rect(c, X0, y, X1, y + 1, 'T')
        rect(c, X0, y, X1, y, 'S')
        put(c, 9, y, 'R'); put(c, 21, y, 'R')
    rect(c, X0, Y0, X1, Y0, 'T')
    rect(c, X0, Y1, X1, Y1, 'T')
    for (x, y) in ((15, 15), (16, 15), (15, 16), (16, 16)):   # tache de corruption
        put(c, x, y, 'R')
    outline(c, 'T')
    return [c, hinges(blank(32, 32), ('S', 'T'))]


def eye(g, cx, cy, r=5):
    """Oeil / cible de cristal : anneau dore, blanc, rouge, pupille."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= r * r + 1:
                put(g, x, y, 'p')
            if d <= (r - 1) ** 2 + 1:
                put(g, x, y, 'w')
            if d <= (r - 2) ** 2 + 1:
                put(g, x, y, 'F')
    rect(g, cx - 1, cy - 1, cx + 1, cy + 1, '4')
    put(g, cx - 1, cy - 1, 'w')
    put(g, cx + 1, cy + 1, 'I')


def door_interrupteur():
    c = blank(32, 32)
    rect(c, X0, Y0, X1, Y1, 'I')
    rect(c, X0, Y0, X1, Y0 + 1, 'W')                   # linteau
    rect(c, X0, Y0, X1, Y0, 'X')
    rect(c, X0, Y1 - 1, X1, Y1, 'U')
    for bx in (5, 10, 15, 20, 24):                     # barreaux de pierre
        rect(c, bx, Y0 + 2, bx + 2, Y1 - 1, 'V')
        rect(c, bx, Y0 + 2, bx, Y1 - 1, 'W')
        rect(c, bx + 2, Y0 + 2, bx + 2, Y1 - 1, 'U')
    rect(c, X0, 11, X1, 21, 'V')                       # bandeau central
    rect(c, X0, 11, X1, 11, 'W')
    rect(c, X0, 21, X1, 21, 'U')
    eye(c, 16, 16, 5)
    outline(c)
    return [c, hinges(blank(32, 32), ('X', 'V'))]


# ---------------------------------------------------------------- interrupteur a fleche
def target(active):
    g = blank(32, 32)
    rect(g, 6, 9, 25, 29, 'W')                         # socle de pierre pose au sol
    rect(g, 6, 9, 25, 10, 'X')
    rect(g, 6, 9, 6, 29, 'X')
    rect(g, 25, 10, 25, 29, 'U')
    rect(g, 6, 29, 25, 29, 'U')
    rect(g, 7, 27, 24, 28, 'V')
    for (x, y) in ((9, 12), (22, 12), (9, 26), (22, 26)):
        put(g, x, y, 'V')
    cx, cy = 16, 19
    for y in range(cy - 7, cy + 8):
        for x in range(cx - 7, cx + 8):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= 50:
                if active:
                    col = 'o' if d > 36 else ('F' if d > 20 else ('4' if d > 6 else 'y'))
                else:
                    col = 'k' if d > 36 else ('V' if d > 20 else ('h' if d > 6 else 'g'))
                put(g, x, y, col)
    if active:
        for (x, y) in ((14, 17), (15, 18), (16, 18), (15, 19)):
            put(g, x, y, 'w')
        for (x, y) in ((16, 11), (16, 27), (8, 19), (24, 19), (11, 14), (21, 14)):   # eclats
            put(g, x, y, 'y')
    else:
        put(g, 14, 17, 'X'); put(g, 15, 18, 'X')
        put(g, 16, 19, 'k'); put(g, 17, 20, 'k')
    outline(g)
    return g


# ---------------------------------------------------------------- icones 16x16
ICONS = {}

ICONS['icone_carte_donjon'] = grid([
    "................",
    "................",
    "..EeeeeeeeeeeE..",
    ".EeEEEEEEEEEEeE.",
    "..EwwwwwwwwwwE..",
    "..EwDwwwwwwwwE..",
    "..EwDDDDwwwDwE..",
    "..EwwwwwDwwDwE..",
    "..EwwwwwDDDDwE..",
    "..EwwwwwwwwD4E..",
    "..EwwDDDDDDDwE..",
    "..EwwwwwwwwwwE..",
    ".EeEEEEEEEEEEeE.",
    "..EeeeeeeeeeeE..",
    "................",
    "................",
])

ICONS['icone_boussole'] = grid([
    "................",
    ".....oyyyo......",
    "......ooo.......",
    "....yyyyyyy.....",
    "...yooooooop....",
    "..yowwwFwwwop...",
    "..yowwwFwwwop...",
    "..yowwFFFwwop...",
    "..yowkhhhhwop...",
    "..yowwkhhwwop...",
    "..yowwwkwwwop...",
    "...ypooooopp....",
    "....pppppp......",
    "................",
    "................",
    "................",
])

ICONS['icone_grande_cle'] = grid([
    "................",
    ".....yyyyyy.....",
    "....yooooopy....",
    "...yoy4444ypy...",
    "...yoy4ww4ypy...",
    "...yoy4444ypy...",
    "...yoyyyyyypy...",
    "....yoyyyypy....",
    ".....ypoopp.....",
    "......yop.......",
    "......yop.......",
    "......yoyyy.....",
    "......yop.......",
    "......yoyyyy....",
    "......ypp.......",
    "................",
])

ICONS['icone_plume_corbeau'] = grid([
    "................",
    "............BB..",
    "..........BBbcB.",
    "........BBbbbcB.",
    ".......BbbbbcdB.",
    "......BbbbbbccB.",
    ".....BBbbbbcbB..",
    "....BBbbbbbbBB..",
    "...BBBbbbbbBB...",
    "..BBbBBbbbBB....",
    ".BBbbbBBBBB.....",
    ".BTbbBBB........",
    "..TBBB..........",
    ".TT.............",
    "T...............",
    "................",
])


def icon_px(g):
    g = [r[:] for r in g]
    outline(g)
    return C.to_rgba(g)


def strip(pxs, w, h):
    out = [[(0, 0, 0, 0)] * (w * len(pxs)) for _ in range(h)]
    for i, px in enumerate(pxs):
        for y in range(h):
            for x in range(w):
                out[y][i * w + x] = px[y][x]
    return out


def main():
    outs = {}
    for nom, f in (('porte_cle', door_cle()), ('porte_grande_cle', door_grande_cle()),
                   ('porte_ennemis', door_ennemis()), ('porte_interrupteur', door_interrupteur()),
                   ('interrupteur_fleche', [target(False), target(True)])):
        outs[nom] = sheet([C.to_rgba(x) for x in f])
        save_png(os.path.join(PUZ, nom + '.png'), outs[nom])
    for nom, g in ICONS.items():
        outs[nom] = icon_px(g)
        save_png(os.path.join(UI, nom + '.png'), outs[nom])
    if len(sys.argv) > 1:
        d = sys.argv[1]
        os.makedirs(d, exist_ok=True)
        wall = (56, 46, 66, 255)       # fond du tileset du temple
        noms = ('porte_cle', 'porte_grande_cle', 'porte_ennemis', 'porte_interrupteur', 'interrupteur_fleche')
        save_png(os.path.join(d, 'apercu_portes_x8.png'),
                 background(strip([outs[n] for n in noms[:3]], 64, 32), wall), 8)
        save_png(os.path.join(d, 'apercu_portes2_x8.png'),
                 background(strip([outs[n] for n in noms[3:]], 64, 32), wall), 8)
        save_png(os.path.join(d, 'apercu_portes_x3.png'),
                 background(strip([outs[n] for n in noms], 64, 32), wall), 3)
        save_png(os.path.join(d, 'apercu_icones_x8.png'),
                 background(strip([outs[n] for n in ICONS], 16, 16), wall), 8)


if __name__ == '__main__':
    main()
