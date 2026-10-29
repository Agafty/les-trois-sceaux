"""Ouverture : icones charbon, epee en bois, epee de Corvan (24x24) + traces de pas (32x64).
Usage : python ouverture.py -> art/ui/icone_{charbon,epee_bois,epee_corvan}.png, art/cinematiques/traces_pas.png"""
import os
from hud import OUT, blank, save_png, to_rgba
from inventaire import line, outline, shade

ROOT = os.path.join(OUT, '..', '..')


def charbon():
    g = blank(24, 24)
    # bloc irregulier (rangees: y -> (x0, x1))
    rows = {5: (9, 14), 6: (7, 16), 7: (5, 18), 8: (4, 19), 9: (3, 19), 10: (3, 20), 11: (3, 20), 12: (4, 20),
            13: (4, 19), 14: (5, 19), 15: (6, 18), 16: (7, 16), 17: (9, 14)}
    for y, (a, b) in rows.items():
        for x in range(a, b + 1):
            g[y][x] = 'I'
    # facettes plus claires en haut a gauche, plus sombres en bas a droite
    for y, (a, b) in rows.items():
        if y < 11:
            for x in range(a, min(a + 3, b)):
                g[y][x] = 'J'
        if y > 13:
            g[y][b] = 'D' if b else 'I'
    for x, y in ((9, 6), (10, 6), (8, 7), (9, 7), (7, 8), (6, 9), (5, 10)):
        g[y][x] = 'k'
    for x, y in ((9, 7), (6, 9)):
        g[y][x] = 'h'
    line(g, 12, 8, 15, 11, 'J'); line(g, 15, 11, 14, 15, 'J')   # fissures
    for x, y in ((13, 9), (16, 9), (11, 13)):
        g[y][x] = 'k'
    g[11][16] = 'h'
    outline(g)
    return g


def epee_bois():
    g = blank(24, 24)
    line(g, 7, 16, 19, 4, '2'); line(g, 8, 17, 20, 5, '2'); line(g, 8, 16, 20, 4, '2')
    line(g, 8, 15, 19, 4, '9')   # veine
    for x, y in ((19, 3), (20, 3), (21, 4), (21, 5)):
        g[y][x] = '2'
    line(g, 6, 13, 12, 19, 'B'); line(g, 7, 13, 13, 19, '6'); line(g, 5, 14, 11, 20, '6')  # garde
    line(g, 5, 18, 3, 20, '6'); line(g, 6, 18, 4, 20, 'A'); line(g, 7, 17, 4, 20, 'A')       # poignee
    line(g, 5, 17, 2, 20, '6')
    g[21][2] = '6'; g[21][3] = '6'; g[20][2] = 'B'
    for x, y in ((12, 11), (14, 9), (17, 6)):
        g[y][x] = '9'
    outline(g)
    return g


def epee_corvan():
    g = blank(24, 24)
    # lame d'acier, 3 px de large, clair a gauche
    line(g, 10, 13, 20, 3, 'g'); line(g, 11, 13, 21, 3, 'g'); line(g, 11, 14, 21, 4, 'h')
    line(g, 12, 14, 21, 5, 'k')
    g[3][20] = 'g'; g[3][21] = 'g'; g[4][21] = 'g'
    for x, y in ((12, 11), (14, 9), (16, 7)):
        g[y][x] = 'g'
    # garde doree transversale
    line(g, 6, 11, 12, 17, 'K'); line(g, 7, 11, 13, 17, 'K'); line(g, 5, 12, 11, 18, '6')
    g[10][6] = 'K'; g[12][5] = 'K'; g[17][12] = 'K'; g[18][11] = '6'; g[16][13] = '6'
    # petit corbeau sombre pose au centre de la garde (tete + bec + oeil dore)
    for x, y in ((8, 13), (9, 13), (9, 14), (8, 14), (10, 15), (9, 15)):
        g[y][x] = 'I'
    g[12][8] = 'I'; g[12][7] = 'I'; g[13][7] = 'K'
    # poignee en cuir
    line(g, 8, 16, 5, 19, 'B'); line(g, 9, 16, 6, 19, '6'); line(g, 7, 16, 4, 19, 'B')
    for x, y in ((3, 20), (4, 20), (3, 21), (2, 20)):
        g[y][x] = 'K'
    g[21][4] = 'K'
    outline(g)
    return g


def traces():
    g = blank(32, 64)
    # pied vu de dessus : avant large (5 lignes), vide d'1 ligne, talon rond (3 lignes) ; pointe vers le haut (la porte)
    foot = [".###.", "#####", "#####", "#####", ".###.", ".....", ".###.", ".###.", "..#.."]
    steps = [(7, 53, 'L'), (19, 44, 'R'), (8, 34, 'L'), (20, 25, 'R'), (9, 15, 'L'), (21, 6, 'R')]
    for i, (x, y, side) in enumerate(steps):
        for j, row in enumerate(foot):
            for a, c in enumerate(row):
                if c != '#':
                    continue
                if i >= 4 and (a + j) % 3 == 0:
                    continue   # traces qui s'estompent vers la porte
                g[y + j][x + a] = 'J' if (a + j) % 4 else 'I'
    return g


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'art', 'cinematiques'), exist_ok=True)
    save_png(os.path.join(OUT, 'icone_charbon.png'), to_rgba(charbon()))
    save_png(os.path.join(OUT, 'icone_epee_bois.png'), to_rgba(epee_bois()))
    save_png(os.path.join(OUT, 'icone_epee_corvan.png'), to_rgba(epee_corvan()))
    save_png(os.path.join(ROOT, 'art', 'cinematiques', 'traces_pas.png'), to_rgba(traces()))
