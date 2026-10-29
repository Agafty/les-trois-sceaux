"""Images hors tileset de la Mine Effondrée : bloc_mine, grilles rouillées, icônes (marteau de Corvan, minerai d'étoile, paquet de bombes).

Usage : python tools/sprites/mine_hors_tileset.py
Produit :
  art/puzzles/bloc_mine.png               32x32, bloc poussable = wagonnet-caisse de minerai (même taille que bloc_poussable.png)
  art/puzzles/grille_h_rouille.png        128x32, 4 images comme grille_h.png (recoloration fer rouillé)
  art/puzzles/grille_v_rouille.png        idem pour grille_v.png
  art/ui/icone_marteau_corvan.png         24x24
  art/ui/icone_minerai_etoile.png         24x24
  art/ui/icone_bombes_paquet.png          24x24
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mine_art  # noqa: F401,E402  (ajoute la palette de la mine à P)
from mine_art import P, O  # noqa: E402
from mine_art2 import wagon, rocks, line, GOLD, COAL, flecks, crystal, CYP, polyfill  # noqa: E402
from foret import Cv  # noqa: E402
from tsplan import save_png, ROOT  # noqa: E402


def load_png(path):
    d = open(path, 'rb').read()
    i, idat = 8, b''
    while i < len(d):
        n, = struct.unpack('>I', d[i:i + 4])
        t = d[i + 4:i + 8]
        if t == b'IHDR':
            w, h = struct.unpack('>II', d[i + 8:i + 16])
        if t == b'IDAT':
            idat += d[i + 8:i + 8 + n]
        i += 12 + n
    raw = zlib.decompress(idat)
    st = w * 4 + 1
    return [[tuple(raw[y * st + 1 + x * 4:y * st + 5 + x * 4]) for x in range(w)] for y in range(h)]


def bloc_mine():
    cv = wagon(32, 11, 14, 27, 3, 28, (9, 23),
               heap=[(9, 10, 6, 5), (16, 7, 7, 6), (23, 10, 6, 5), (16, 11, 9, 4)], bands=(7, 22))
    flecks(cv, [(9, 8), (15, 4), (21, 7), (13, 9), (19, 10), (24, 9)], GOLD)
    for k in range(4):                                       # chevron jaune peint sur la face
        for dx in (-1, 0):
            cv.set(15 + dx + 0, 18 + k, P['lamp_y'])
            cv.set(16 + dx + 1, 18 + k, P['lamp_y'])
    cv.set(15, 22, P['lamp_y'])
    cv.set(16, 22, P['lamp_y'])
    cv.outline(O)
    return cv.p


def rust(px):
    out = []
    for row in px:
        nr = []
        for c in row:
            if c[3] == 0:
                nr.append(None)
                continue
            r, g, b, a = c
            L = 0.3 * r + 0.59 * g + 0.11 * b
            if max(r, g, b) - min(r, g, b) < 40 and L > 25:
                nr.append((min(255, int(L * 1.05 + 28)), int(L * 0.68 + 6), int(L * 0.42 + 2), a))
            else:
                nr.append(tuple(c))
        out.append(nr)
    return out


def marteau():
    cv = Cv(24, 24)
    line(cv, [(5, 20), (16, 9)], P['wd_dk'])
    line(cv, [(4, 20), (15, 9)], P['wd_md'])
    line(cv, [(4, 19), (15, 8)], P['wd_lt'])
    for (x, y) in ((6, 17), (7, 16), (8, 15)):              # lanière de cuir
        cv.set(x, y, P['wd_dp'])
    poly = [(11, 3), (20, 3), (21, 12), (14, 13)]
    polyfill(cv, poly, lambda x, y: P['mt_hi'] if y < 5 else P['mt_lt'] if x < 16 else P['mt_md'] if y < 11 else P['mt_dk'])
    cv.set(13, 4, P['cy_w'])
    cv.set(14, 4, P['cy_w'])
    cv.outline(O)
    return cv.p


def minerai_etoile():
    cv = Cv(24, 24)
    rocks(cv, [(12, 17, 9, 4), (8, 13, 5, 5), (16, 13, 6, 6), (12, 9, 6, 6)], COAL, 14)
    for (x, y, k) in ((12, 7, 'cy_w'), (12, 8, 'cy_hi'), (12, 9, 'cy_hi'), (12, 10, 'cy_lt'), (12, 11, 'cy_md'),
                      (10, 9, 'cy_lt'), (11, 9, 'cy_hi'), (13, 9, 'cy_hi'), (14, 9, 'cy_lt'),
                      (8, 13, 'cy_lt'), (16, 14, 'cy_lt'), (11, 16, 'cy_md'), (17, 11, 'cy_hi'), (7, 11, 'cy_hi')):
        cv.set(x, y, P[k])
    cv.set(12, 6, P['cy_lt'])
    cv.set(12, 12, P['cy_lt'])
    for (x, y) in ((8, 6), (17, 7), (5, 15), (19, 16)):     # éclats de lumière
        cv.set(x, y, P['cy_w'])
    return cv.p


def bombes_paquet():
    cv = Cv(24, 24)
    for (cx, cy) in ((7, 15), (16, 15), (11.5, 11)):
        t = Cv(24, 24)
        for y in range(24):
            for x in range(24):
                dx, dy = (x + 0.5 - cx) / 5.2, (y + 0.5 - cy) / 5.2
                if dx * dx + dy * dy <= 1:
                    k = -(dx + dy) * 0.6
                    t.p[y][x] = (96, 90, 112, 255) if k > 0.55 else (56, 50, 70, 255) if k > 0 else (36, 32, 48, 255) if k > -0.5 else (24, 20, 32, 255)
        t.outline(O)
        for y in range(24):
            for x in range(24):
                if t.p[y][x] is not None:
                    cv.p[y][x] = t.p[y][x]
        cv.set(round(cx) - 2, round(cy) - 3, (200, 200, 220, 255))
        line(cv, [(round(cx) + 1, round(cy) - 6), (round(cx) + 3, round(cy) - 9)], P['wd_lt'])
        cv.set(round(cx) + 3, round(cy) - 10, P['lamp_y'])
        cv.set(round(cx) + 4, round(cy) - 11, P['rd_lt'])
    for x in range(5, 19):                                   # corde
        cv.set(x, 14 + (1 if 8 < x < 15 else 0), P['wd_hi'])
    return cv.p


def main():
    puz = os.path.join(ROOT, 'art', 'puzzles')
    ui = os.path.join(ROOT, 'art', 'ui')
    save_png(os.path.join(puz, 'bloc_mine.png'), bloc_mine())
    for s in ('h', 'v'):
        save_png(os.path.join(puz, f'grille_{s}_rouille.png'), rust(load_png(os.path.join(puz, f'grille_{s}.png'))))
    save_png(os.path.join(ui, 'icone_marteau_corvan.png'), marteau())
    save_png(os.path.join(ui, 'icone_minerai_etoile.png'), minerai_etoile())
    save_png(os.path.join(ui, 'icone_bombes_paquet.png'), bombes_paquet())
    print('ok')


if __name__ == '__main__':
    main()
