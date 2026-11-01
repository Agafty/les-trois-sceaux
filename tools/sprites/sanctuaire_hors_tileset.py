"""Images hors tileset du Sanctuaire Englouti (donjon 3) — PLACEHOLDERS lisibles, à retoucher.

Usage : python tools/sprites/sanctuaire_hors_tileset.py
Produit (PNG RGBA, sans Pillow) :
  art/puzzles/porte_mur_rune.png        64x32 : fermée (rune bleue lumineuse) | ouverte (alcôve noire), 32 px par image
  art/items/sceau_lac.png               24x24 : icône du sceau du lac (comme sceau_montagne.png)
  art/enemies/crabe_armure_charge.png   64x128 : pose de CHARGE (carapace d'acier bleu, lignes de vitesse), même grille que
                                        crabe_armure.png (2 images par direction ; lignes : bas, haut, gauche, droite)
  art/enemies/morceau_armure.png        96x96 : 3 pièces (lignes : casque, plastron, gantelet) ; colonnes : flotte A, flotte B, révélée
  art/characters/corvan_ombre.png       64x32 : silhouette drapée de Corvan (2 images : repos A, repos B), de face
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngview import read_png  # noqa: E402
from tsplan import save_png, ROOT, rgba  # noqa: E402

ART = os.path.join(ROOT, 'art')
CL = (0, 0, 0, 0)


def canvas(w, h):
    return [[CL] * w for _ in range(h)]


def put(px, x, y, c):
    if 0 <= y < len(px) and 0 <= x < len(px[0]):
        px[y][x] = rgba(c) if isinstance(c, str) else c


def rect(px, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(px, x, y, c)


def ellipse(px, cx, cy, rx, ry, base, dark=None, light=None):
    for y in range(len(px)):
        for x in range(len(px[0])):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1:
                v = dx * 0.5 + dy * 0.85
                c = dark if (dark and v > 0.5) else light if (light and v < -0.55) else base
                put(px, x, y, c)


def outline(px, c):
    pts = [(x, y) for y in range(len(px)) for x in range(len(px[0])) if px[y][x][3] == 0 and any(
        0 <= y + dy < len(px) and 0 <= x + dx < len(px[0]) and px[y + dy][x + dx][3] and px[y + dy][x + dx] != rgba(c)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        put(px, x, y, c)


def blit(dst, src, ox, oy):
    for y, row in enumerate(src):
        for x, c in enumerate(row):
            if c[3]:
                put(dst, ox + x, oy + y, c)


# ------------------------------------------------------------------ porte_mur_rune (64x32)
def rune(px, ox, cx, cy, col, glow=None):
    """Glyphe : cercle ouvert, barre verticale, deux traits."""
    pts = []
    for a in range(0, 360, 6):
        if 30 < a < 150:
            continue
        pts.append((round(cx + 6 * math.cos(math.radians(a))), round(cy + 6 * math.sin(math.radians(a)))))
    pts += [(cx, y) for y in range(cy - 8, cy + 9)] + [(cx - 3 + k, cy - 3 + k) for k in range(0, 4)] + [(cx + 3 - k, cy + 3 + k) for k in range(0, 4)]
    if glow:
        for (x, y) in pts:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if px[y + dy][ox + x + dx][3] and px[y + dy][ox + x + dx] != rgba(col):
                    put(px, ox + x + dx, y + dy, glow)
    for (x, y) in pts:
        put(px, ox + x, y, col)


def porte_mur_rune():
    px = canvas(64, 32)
    # fermée : bloc de pierre violet-gris à joints, rune cyan
    rect(px, 0, 0, 31, 31, '#5e6290')
    rect(px, 0, 0, 31, 2, '#7a7eb0')
    rect(px, 0, 29, 31, 31, '#3c3e66')
    for y in (10, 21):
        rect(px, 1, y, 30, y, '#3c3e66')
    for (x, y0, y1) in ((10, 0, 9), (22, 11, 20), (14, 22, 31)):
        rect(px, x, y0, x, y1, '#3c3e66')
    for y in range(32):
        put(px, 0, y, '#2a2a4a'), put(px, 31, y, '#2a2a4a')
    rect(px, 8, 6, 23, 25, '#404478')            # cartouche sombre pour que la rune ressorte
    rune(px, 0, 15, 15, '#a8f4ff', '#40c8e8')
    # ouverte : alcôve noire, montants de pierre, rune éteinte au linteau
    rect(px, 32, 0, 63, 31, '#14101c')
    rect(px, 32, 0, 35, 31, '#5e6290')
    rect(px, 60, 0, 63, 31, '#3c3e66')
    rect(px, 32, 0, 63, 3, '#7a7eb0')
    rect(px, 36, 4, 59, 4, '#26264a')
    for x in range(40, 56, 4):
        put(px, x, 8, '#3a5878')
    rect(px, 47, 12, 48, 14, '#2a4868')
    return px


# ------------------------------------------------------------------ sceau_lac (24x24)
def sceau_lac():
    S = 24
    px = canvas(S, S)
    C = dict(hi='#c8e4f0', lt='#8ab4d0', dk='#4a6486', in1='#1c2c4c', in2='#26406a', g1='#e8f8ff', g2='#9ad4ee', g3='#5a9cc8', ore='#f0c040')
    for y in range(S):
        for x in range(S):
            dx, dy = x + 0.5 - 12, y + 0.5 - 12
            rr = math.hypot(dx, dy)
            if rr <= 11:
                if rr > 8:
                    v = -(dx * -0.45 + dy * -0.8) / 11
                    c = 'hi' if v < -0.55 else ('dk' if v > 0.45 else 'lt')
                else:
                    c = 'in2' if rr > 7 else 'in1'
                put(px, x, y, C[c])
    # goutte
    for y in range(5, 15):
        w = 0 if y < 6 else (y - 5) * 5 // 9 if y < 11 else round(math.sqrt(max(0, 4.6 ** 2 - (y - 10.6) ** 2)))
        w = max(w, 0)
        for x in range(12 - w, 12 + w + 1):
            c = 'g1' if (x < 12 and y < 12) else ('g3' if x - 12 >= w - 1 and y > 9 else 'g2')
            put(px, x, y, C[c])
    # vagues
    for x in range(6, 19):
        put(px, x, 16 + round(math.sin((x - 6) * 0.9) * 1.0), C['g2'])
        put(px, x, 19 + round(math.sin((x - 5) * 0.9) * 1.0), C['g3'])
    put(px, 12, 12, C['ore'])
    return px


# ------------------------------------------------------------------ crabe_armure_charge (64x128)
def is_red(c):
    return c[3] and c[0] > 150 and c[1] < 100 and c[2] < 100


def steel(c):
    r, g, b, a = c
    if not a:
        return c
    if is_red(c):
        return (110, 130, 170, 255)                       # la tache rouge disparait sous la carapace
    L = 0.3 * r + 0.59 * g + 0.11 * b
    if L < 40:
        return c                                          # contour sombre conserve
    return (min(255, int(L * 0.72 + 14)), min(255, int(L * 0.9 + 28)), min(255, int(L * 1.12 + 60)), a)


def steel_red(c):
    """Variante rouge : la carapace d'acier prend une teinte rouille-rose (le contour sombre reste)."""
    r, g, b, a = c
    if not a:
        return c
    L = 0.3 * r + 0.59 * g + 0.11 * b
    if L < 40:
        return c
    if is_red(c):
        L = 130
    return (min(255, int(L * 1.05 + 50)), min(255, int(L * 0.62 + 26)), min(255, int(L * 0.72 + 40)), a)


def crabe_charge(red=False):
    src = read_png(os.path.join(ART, 'enemies', 'crabe_armure_red.png' if red else 'crabe_armure.png'))
    steel_fn = steel_red if red else steel
    out = canvas(64, 128)
    for row in range(4):                                  # bas, haut, gauche, droite
        for col in range(2):
            ox, oy = col * 32, row * 32
            cell = [[steel_fn(src[oy + y][ox + x]) for x in range(32)] for y in range(32)]
            xs = [x for y in range(32) for x in range(32) if cell[y][x][3]]
            ys = [y for y in range(32) for x in range(32) if cell[y][x][3]]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            dx = 1 if row == 3 else -1 if row == 2 else 0
            dy = 1 if row == 0 else -1 if row == 1 else 0
            # la charge : le crabe s'abaisse d'un pixel, bouclier lumineux sur le bord avant
            blit(out, cell, ox, oy)
            # liseré brillant sur le dessus de la carapace (haut-gauche) : "dur comme l'acier"
            for y in range(32):
                for x in range(32):
                    c = out[oy + y][ox + x]
                    if c[3] and ((not red and c[2] > 150 and c[0] > 130) or (red and c[0] > 245)):
                        put(out, ox + x, oy + y, (255, 232, 236, 255) if red else (230, 245, 255, 255))
            # lignes de vitesse derrière (côté opposé au déplacement)
            for k in range(3):
                off = (col * 2 + k * 3) % 5
                if dx:
                    ex = x0 - 2 - off if dx > 0 else x1 + 2 + off
                    ey = y0 + 3 + k * 4
                    for s in range(4):
                        put(out, ox + ex - dx * s, oy + ey, (255, 206, 212, 255) if red else (200, 232, 255, 255))
                else:
                    ey = y0 - 2 - off if dy > 0 else y1 + 2 + off
                    ex = x0 + 4 + k * 8
                    for s in range(4):
                        put(out, ox + ex, oy + ey - dy * s, (255, 206, 212, 255) if red else (200, 232, 255, 255))
    return out


# ------------------------------------------------------------------ morceau_armure (96x96)
def piece(kind, phase, lit):
    cv = canvas(32, 32)
    if lit:
        A = dict(b='#8a94b8', d='#4e5878', h='#d8e4f8', e='#f4e8a0', o='#20243c')
    else:
        A = dict(b='#3a3452', d='#1e1a2c', h='#5a4e7a', e='#8a1c28', o='#120e1c')
    cy = 15 + (1 if phase else 0)
    if kind == 'casque':
        ellipse(cv, 16, cy, 9, 9, A['b'], A['d'], A['h'])
        rect(cv, 8, cy, 24, cy + 8, A['b'])
        rect(cv, 22, cy, 24, cy + 8, A['d'])
        rect(cv, 9, cy + 1, 23, cy + 3, A['o'])             # fente de la visière
        put(cv, 12, cy + 2, A['e']), put(cv, 13, cy + 2, A['e']), put(cv, 19, cy + 2, A['e']), put(cv, 20, cy + 2, A['e'])
        rect(cv, 15, cy - 9, 17, cy - 5, A['h'])             # cimier
        rect(cv, 15, cy + 4, 17, cy + 8, A['d'])
    elif kind == 'plastron':
        rect(cv, 8, cy - 8, 24, cy + 8, A['b'])
        rect(cv, 6, cy - 9, 10, cy - 3, A['h'])              # épaulières
        rect(cv, 22, cy - 9, 26, cy - 3, A['d'])
        rect(cv, 22, cy - 6, 24, cy + 8, A['d'])
        rect(cv, 15, cy - 5, 17, cy + 7, A['o'])             # arête centrale
        rect(cv, 9, cy + 4, 23, cy + 5, A['d'])              # ceinture
        put(cv, 12, cy - 3, A['e']), put(cv, 20, cy - 3, A['e'])
        for x in range(9, 24, 3):
            put(cv, x, cy + 9, A['d'])
    else:                                                    # gantelet
        rect(cv, 10, cy - 2, 21, cy + 8, A['b'])
        rect(cv, 10, cy - 2, 12, cy + 8, A['h'])
        rect(cv, 19, cy - 2, 21, cy + 8, A['d'])
        for k in range(4):                                   # doigts
            rect(cv, 10 + k * 3, cy - 8, 11 + k * 3, cy - 3, A['b'])
            put(cv, 10 + k * 3, cy - 8, A['h'])
        rect(cv, 4, cy - 2, 9, cy + 1, A['b'])               # pouce
        rect(cv, 9, cy + 9, 22, cy + 11, A['d'])             # poignet
        put(cv, 15, cy + 3, A['e']), put(cv, 16, cy + 3, A['e'])
    outline(cv, A['o'])
    return cv


def morceaux():
    out = canvas(96, 96)
    for r, kind in enumerate(('casque', 'plastron', 'gantelet')):
        for c, (ph, lit) in enumerate(((0, False), (1, False), (0, True))):
            blit(out, piece(kind, ph, lit), c * 32, r * 32)
    return out


# ------------------------------------------------------------------ corvan_ombre (64x32)
def corvan_ombre(phase):
    cv = canvas(32, 32)
    base, dark, light, o = '#1e1c34', '#0e0c1e', '#3a3860', '#08060f'
    ellipse(cv, 16, 20, 11, 9, base, dark, light)            # manteau, dos voûté
    for y in range(20, 31):                                  # pan de manteau jusqu'au sol
        w = 11 - (y - 20) // 4
        for x in range(16 - w, 16 + w + 1):
            put(cv, x, y, dark if x > 16 + w - 4 else (light if (x < 16 - w + 2 and y < 26) else base))
    for x in range(5, 28):                                   # ourlet déchiré
        if (x + phase) % 3 == 0:
            put(cv, x, 30, CL)
        if (x + phase) % 5 == 0:
            put(cv, x, 29, CL)
    ellipse(cv, 16, 10, 7, 7, base, dark, light)             # capuche
    rect(cv, 12, 8, 20, 14, dark)                            # visage dans l'ombre
    put(cv, 13, 11, '#f4eab0'), put(cv, 14, 11, '#f4eab0'), put(cv, 18, 11, '#f4eab0'), put(cv, 19, 11, '#f4eab0')
    rect(cv, 9, 21, 12, 24, dark)                            # mains jointes sous le manteau
    for k in range(3):
        put(cv, 4 - k, 14 + k * 3 + phase, base)             # cape qui flotte
    outline(cv, o)
    return cv


def corvan_sheet():
    out = canvas(64, 32)
    for ph in (0, 1):
        blit(out, corvan_ombre(ph), ph * 32, 0)
    return out


def main():
    save_png(os.path.join(ART, 'puzzles', 'porte_mur_rune.png'), porte_mur_rune())
    save_png(os.path.join(ART, 'items', 'sceau_lac.png'), sceau_lac())
    save_png(os.path.join(ART, 'enemies', 'crabe_armure_charge.png'), crabe_charge())
    save_png(os.path.join(ART, 'enemies', 'crabe_armure_red_charge.png'), crabe_charge(True))
    save_png(os.path.join(ART, 'enemies', 'morceau_armure.png'), morceaux())
    save_png(os.path.join(ART, 'characters', 'corvan_ombre.png'), corvan_sheet())
    print('ok')


if __name__ == '__main__':
    main()
