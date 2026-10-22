"""Brann, idle dans les 4 directions, case 32x32, cheveux bruns.

Usage : python3 tools/sprites/brann.py [dossier_sortie]
Produit brann_idle_{bas,haut,gauche,droite}.png (cases de 32x32), la planche brann_idle.png
(128x32, ordre : bas, haut, gauche, droite) et des aperçus agrandis (x3 = taille réelle en 1080p, x8 = détail).
Face et dos : grille décrite par moitié gauche (16 colonnes) puis copiée en miroir ;
les détails asymétriques sont ajoutés ensuite. Profil gauche dessiné en entier, profil droit = miroir.
"""
import sys
from pathlib import Path
from PIL import Image

# --- Palette -----------------------------------------------------------------
BASE = {
    ".": (0, 0, 0, 0),          # transparent
    "O": (27, 20, 32, 255),     # contour
    "S": (242, 194, 154, 255),  # peau
    "s": (204, 140, 104, 255),  # peau ombre
    "E": (27, 20, 32, 255),     # yeux
    "R": (226, 52, 44, 255),    # écharpe rouge vif (seule couleur saturée)
    "r": (150, 28, 40, 255),    # écharpe ombre
    "W": (214, 196, 156, 255),  # chemise écrue
    "w": (166, 146, 108, 255),  # chemise ombre
    "A": (138, 90, 52, 255),    # tablier de cuir
    "a": (94, 58, 34, 255),     # tablier ombre
    "K": (36, 26, 34, 255),     # corbeau
    "G": (74, 52, 38, 255),     # gants de forge
    "g": (46, 32, 24, 255),     # gants ombre
    "B": (58, 42, 32, 255),     # ceinture
    "Y": (200, 160, 80, 255),   # boucle / bec
    "P": (78, 64, 88, 255),     # pantalon
    "p": (56, 46, 66, 255),     # pantalon ombre (jambe arrière)
    "T": (106, 70, 48, 255),    # bottes
    "t": (67, 41, 28, 255),     # bottes ombre
}
HAIR = {
    "bleu": {"H": (88, 160, 255, 255), "h": (42, 98, 216, 255), "d": (27, 58, 138, 255)},
    "brun": {"H": (176, 110, 64, 255), "h": (122, 70, 40, 255), "d": (74, 42, 28, 255)},
}

# --- Moitié gauche (colonnes 0 à 15) ------------------------------------------
LEFT = [
    "................",  # 0
    "..........O...O.",  # 1  mèches
    ".........OHO.OHO",  # 2
    "........OHhHOHHh",  # 3
    ".......OhHhHHhHh",  # 4
    ".......OhhHhhhhh",  # 5
    "......OdhhhhhHhh",  # 6
    "......OdhdhhhhhH",  # 7
    "......OddSdhSSdh",  # 8  frange
    "......OdSSSSSSSS",  # 9
    "......OdSSSSESSS",  # 10 yeux
    "......OsSSSSESSS",  # 11
    "......OsSSSSSSSs",  # 12 bouche
    ".......OsSSSSSSS",  # 13
    "........OOsSSSSS",  # 14 menton
    "........ORRRRRRR",  # 15 écharpe
    ".......ORrRRRrRR",  # 16
    ".....OWWWWWOAAAA",  # 17 épaules + bavette du tablier
    "....OwWWWWWOAaAA",  # 18
    "....OwWWWwWOAAAA",  # 19
    "....OwWWOwWOAAAA",  # 20
    "....OwWWOwWOAAAA",  # 21
    "....OGGgOwWOAAAA",  # 22 gants
    "....OGGgOwBBBBBB",  # 23 ceinture
    "....OGGgOwWOAAAA",  # 24
    ".....OOOOwwOAAaA",  # 25
    "........OPPOAAaA",  # 26
    "........OPPOaaaa",  # 27 bas du tablier
    "........OPPPPPO.",  # 28 jambes
    "........OTTTTTO.",  # 29 bottes
    ".......OTTtTTTO.",  # 30
    ".......OOOOOOOO.",  # 31
]

# Détails asymétriques : (ligne, colonne, code)
DETAILS = [
    # corbeau sur la bavette
    (19, 14, "K"), (19, 15, "K"), (19, 13, "Y"),
    (20, 14, "K"), (20, 15, "K"), (20, 16, "K"), (20, 17, "K"), (20, 18, "K"),
    (21, 15, "K"), (21, 17, "K"),
    # boucle de ceinture
    (23, 17, "Y"),
    # pan d'écharpe qui tombe sur l'épaule droite (côté gauche de l'image pour le joueur)
    (16, 22, "R"), (17, 21, "R"), (17, 22, "r"), (18, 22, "R"), (19, 22, "r"),
]


# Haut des cheveux réécrit en entier : mèches irrégulières (sinon on dirait une couronne)
HAIR_TOP = {
    0: "................................",
    1: "..........O...OO...O.....O......",
    2: ".........OHO.OHHO.OHO...OHO.....",
    3: "........OHhHOHhHHOHhHOOOHhO.....",
}

# --- Vue de dos (moitié gauche, puis miroir) ----------------------------------
LEFT_BACK = LEFT[:8] + [
    "......Odhhhhhhhh",  # 8  arrière de la tête
    "......Odhhhhhhhh",  # 9
    "......Odhhhhhhhh",  # 10
    "......Osdhhhhhhh",  # 11 oreille
    "......Osddhhhhhh",  # 12
    ".......Oddhhdhhh",  # 13
    "........OOddhdhh",  # 14 nuque
    "........ORRRRRRR",  # 15 écharpe
    ".......ORrRRRrRR",  # 16
    ".....OWWWaWWWWWW",  # 17 bretelles du tablier en croix
    "....OwWWWWaWWWWW",  # 18
    "....OwWWWwWaWWWW",  # 19
    "....OwWWOwWWaWWW",  # 20
    "....OwWWOwWWWaWW",  # 21
    "....OGGgOwWWWWaW",  # 22
    "....OGGgOwBBBBBa",  # 23 ceinture
    "....OGGgOwWWWWWW",  # 24
    ".....OOOOwwwWWWW",  # 25
    "........OPPPPPPP",  # 26
    "........OPPPPPPP",  # 27
    "........OPPPPPO.",  # 28
    "........OTTTTTO.",  # 29
    ".......OTTtTTTO.",  # 30
    ".......OOOOOOOO.",  # 31
]
DETAILS_BACK = [
    # noeud de l'écharpe et ses deux pans dans le dos
    (16, 15, "r"), (16, 16, "r"),
    (17, 14, "R"), (17, 15, "R"), (17, 16, "R"), (17, 17, "R"),
    (18, 14, "R"), (18, 15, "r"), (18, 17, "R"),
    (19, 14, "r"), (19, 15, "R"), (19, 17, "r"),
    (20, 15, "R"), (21, 15, "r"),
    # noeud du tablier à la taille
    (23, 14, "a"), (23, 15, "A"), (23, 16, "A"), (23, 17, "a"),
    (24, 14, "a"), (24, 17, "a"),
]

# --- Vue de profil, tourné vers la gauche (la droite = miroir) ----------------
SIDE = [
    (0, ""),                            # 0
    (11, "O..OO..O"),                   # 1
    (10, "OHO.OHHOOHO"),                # 2
    (9, "OHhHOHhHHhHhO"),               # 3
    (8, "OhHhHHhHhhHhHhO"),             # 4
    (8, "OhhHhhhhhhhHhhhO"),            # 5
    (7, "OdhhhhhHhhhhhhhdO"),           # 6
    (7, "OhhhhhhhhHhhhhhdO"),           # 7
    (7, "OSddhhhhhhhhhhhdO"),           # 8  frange
    (6, "OSSSShdhhhhhhhhhdO"),          # 9
    (6, "OSESSSSshhhhhhhhdO"),          # 10 oeil + oreille
    (5, "OSSESSSSsshhhhhhhdO"),         # 11 nez
    (6, "OSSSSSSshhhhhhhhdO"),          # 12
    (7, "OsSSSSshhhhhhhdO"),            # 13
    (8, "OOsSSOdhhhddO"),               # 14 menton, nuque
    (8, "ORRRRRRRRRO"),                 # 15 écharpe
    (8, "ORrRRRrRRRRRO"),               # 16 le pan part en arrière
    (8, "OAAWWWWWWWWOrRO"),             # 17 tablier devant, chemise
    (8, "OAAWWwWWWWWO.rRO"),            # 18
    (8, "OAAWOwWWOWwO..rO"),            # 19 bras
    (8, "OAAWOwWWOWwO"),                # 20
    (8, "OAAWOwWWOWwO"),                # 21
    (8, "OAAWOGGgOWwO"),                # 22 gant
    (8, "OBBBOGGgOBBO"),                # 23 ceinture
    (8, "OAAWOGGgOWwO"),                # 24
    (8, "OAAAWOOOOwwO"),                # 25
    (8, "OAAAaPPPPPPO"),                # 26
    (8, "OaaaaPPPPPPO"),                # 27
    (9, "OPPPPOPPPO"),                  # 28 jambes
    (9, "OTTTTOTTTO"),                  # 29
    (8, "OTTTTtOTTtO"),                 # 30
    (8, "OOOOOOOOOOO"),                 # 31
]


def mirror_grid(left, details):
    assert len(left) == 32 and all(len(r) == 16 for r in left)
    grid = [list(r + r[::-1]) for r in left]
    for y, row in HAIR_TOP.items():
        assert len(row) == 32, y
        grid[y] = list(row)
    grid[4][24], grid[4][25] = "h", "O"  # raccord de la mèche de droite
    for y, x, c in details:
        grid[y][x] = c
    return grid


def build_grids():
    side = []
    for off, content in SIDE:
        row = "." * off + content
        assert len(row) <= 32, row
        side.append(list(row.ljust(32, ".")))
    assert len(side) == 32
    return {
        "bas": mirror_grid(LEFT, DETAILS),
        "haut": mirror_grid(LEFT_BACK, DETAILS_BACK),
        "gauche": side,
        "droite": [r[::-1] for r in side],
    }


def render(grid, hair):
    pal = {**BASE, **HAIR[hair]}
    img = Image.new("RGBA", (32, 32))
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            img.putpixel((x, y), pal[c])
    return img


def preview(img, scale, bg=None):
    big = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    if bg is None:
        return big
    out = Image.new("RGBA", big.size, bg)
    out.alpha_composite(big)
    return out


ORDER = ("bas", "haut", "gauche", "droite")


def main(hair="brun"):
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    grids = build_grids()
    imgs = {d: render(grids[d], hair) for d in ORDER}
    for d, img in imgs.items():
        img.save(out / f"brann_idle_{d}.png")
    # planche : une case de 32x32 par direction, dans l'ordre bas, haut, gauche, droite
    sheet = Image.new("RGBA", (32 * len(ORDER), 32))
    for i, d in enumerate(ORDER):
        sheet.alpha_composite(imgs[d], (32 * i, 0))
    sheet.save(out / "brann_idle.png")
    preview(sheet, 8, (110, 150, 90, 255)).save(out / "brann_idle_apercu_x8.png")
    preview(sheet, 3, (110, 150, 90, 255)).save(out / "brann_idle_apercu_x3.png")
    save_walk(out, hair)


# --- Marche : 4 images par direction -------------------------------------------
# Ordre des images : pas (jambe A levée / en avant), passage (corps 1 px plus haut),
# pas (jambe B), passage. Les bras ne bougent pas : à affiner à la main si besoin.

def _put(grid, y, off, content):
    for i, c in enumerate(content):
        if c != " ":
            grid[y][off + i] = c


def _clear(grid, y0, y1, x0, x1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grid[y][x] = "."


def _bob(grid):
    """Passage : tout le haut du corps monte d'un pixel, les jambes s'allongent d'autant."""
    g = [r[:] for r in grid]
    for y in range(0, 28):
        g[y] = grid[y + 1][:]
    return g


def _front_step(grid, lifted):
    """Face ou dos : une jambe levée d'un pixel ('gauche' ou 'droite' de l'image)."""
    g = [r[:] for r in grid]
    x0 = 7 if lifted == "gauche" else 17
    _clear(g, 28, 31, x0, x0 + 7)
    leg = [".OTTTTTO", "OTTtTTTO", "OOOOOOOO"]
    if lifted == "droite":
        leg = [r[::-1] for r in leg]
    for i, row in enumerate(leg):
        _put(g, 28 + i, x0, row.replace(".", " "))
    return g


def _side_stride(grid, back_dark):
    """Profil gauche : jambes écartées ; back_dark inverse l'ombre pour suggérer l'autre jambe."""
    g = [r[:] for r in grid]
    _clear(g, 28, 31, 4, 22)
    front, back = ("p", "P") if back_dark else ("P", "p")
    ft, bt = ("t", "T") if back_dark else ("T", "t")
    rows = [
        (7, f"O{front*3}O   O{back*3}O"),
        (6, f"O{ft*3}O     O{bt*3}O"),
        (5, f"O{ft*3}tO     O{bt*2}tO"),
        (5, "OOOOOO     OOOOO"),
    ]
    for i, (off, row) in enumerate(rows):
        _put(g, 28 + i, off, row)
    return g


def build_walk(grids):
    bas, haut, gauche = grids["bas"], grids["haut"], grids["gauche"]
    walk = {
        "bas": [_front_step(bas, "gauche"), _bob(bas), _front_step(bas, "droite"), _bob(bas)],
        "haut": [_front_step(haut, "droite"), _bob(haut), _front_step(haut, "gauche"), _bob(haut)],
        "gauche": [_side_stride(gauche, False), _bob(gauche), _side_stride(gauche, True), _bob(gauche)],
    }
    walk["droite"] = [[r[::-1] for r in f] for f in walk["gauche"]]
    return walk


def save_walk(out, hair="brun"):
    walk = build_walk(build_grids())
    # planche 128x128 : une ligne par direction (bas, haut, gauche, droite), 4 images par ligne
    sheet = Image.new("RGBA", (32 * 4, 32 * len(ORDER)))
    for j, d in enumerate(ORDER):
        for i, f in enumerate(walk[d]):
            sheet.alpha_composite(render(f, hair), (32 * i, 32 * j))
    sheet.save(out / "brann_marche.png")
    preview(sheet, 8, (110, 150, 90, 255)).save(out / "brann_marche_apercu_x8.png")
    # GIF animé : les 4 directions côte à côte, à la taille du jeu en 1080p (x3), 8 images/s
    frames = []
    for i in range(4):
        fr = Image.new("RGBA", (32 * 4, 32), (110, 150, 90, 255))
        for j, d in enumerate(ORDER):
            fr.alpha_composite(render(walk[d][i], hair), (32 * j, 0))
        frames.append(preview(fr, 3).convert("RGB"))
    frames[0].save(out / "brann_marche_apercu.gif", save_all=True, append_images=frames[1:],
                   duration=125, loop=0)


if __name__ == "__main__":
    main()
