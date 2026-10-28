"""Montagne, dessin final, partie 2 : abords du pont-levis, rails, étais, minerai, lanternes, panneaux, entrée de la Mine Effondrée."""
import math
import random

import village_art1 as VA
from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, wset, F, rgba, mass, shadow, box, ell, hline, vline, paste, mix, tint
from montagne_art import REG, reg, ROCK_MT, cliff_face_px, ground_tex, cv_from, mrock


# ------------------------------------------------------------------ pont-levis
@reg('pl_pilier_g', 'pl_pilier_d', 'pl_chaine_g', 'pl_chaine_d')
def pl_from_village(name, tile):
    return VA.REG[name](name, tile)


@reg('pl_palier', 'pl_palier_nord')
def palier(name, tile):
    t = VA.paves_tex(41 if name.endswith('nord') else 40, 'b')
    mp = {P['p_hi']: P['gr_hi'], P['p_lt']: P['gr_lt'], P['p_md']: P['gr_md'], P['p_dk']: P['gr_dk'], P['p_jt']: P['mt_dk'], P['white']: P['gr_hi']}
    return [[mp.get(c, c) for c in row] for row in t]


@reg('pl_butee')
def butee(name, tile):
    cv = Cv()
    box(cv, 0, 10, 31, 20, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    box(cv, 0, 20, 31, 27, P['pk_lt'], P['pk_md'], P['pk_dk'])
    for x in (4, 14, 24):
        box(cv, x, 12, x + 3, 17, P['m_hi'], P['m_lt'], P['m_dk'])
    for x in range(0, 32, 8):
        cv.set(x, 23, P['pk_dk'])
    cv.outline()
    return cv.p


@reg('garde_corps_h')
def garde_corps(name, tile):
    cv = Cv()
    shadow(cv, 16, 26, 14, 2, P['gr_dk'])
    box(cv, 0, 13, 31, 16, P['b_lt'], P['b_md'], P['b_dk'])
    for x in (2, 15, 28):
        box(cv, x, 8, x + 2, 25, P['b_lt'], P['b_md'], P['b_dk'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ rails
def rail_tile(kind):
    cv = Cv()
    steel = (P['m_hi'], P['m_lt'], P['m_dk'])
    tie = (P['pk_lt'], P['pk_dk'])

    def draw_straight(horiz):
        for i in range(2, T, 7):                       # traverses
            for k in range(4, 28):
                x, y = (i, k) if horiz else (k, i)
                for w in range(3):
                    xx, yy = (x + w, y) if horiz else (x, y + w)
                    cv.set(xx, yy, tie[0] if w == 0 else tie[1])
        for off in (11, 20):
            for i in range(T):
                x, y = (i, off) if horiz else (off, i)
                cv.set(x, y, steel[0])
                x2, y2 = (i, off + 1) if horiz else (off + 1, i)
                cv.set(x2, y2, steel[1])
                x3, y3 = (i, off + 2) if horiz else (off + 2, i)
                cv.set(x3, y3, steel[2])

    if kind in ('h', 'v'):
        draw_straight(kind == 'h')
    elif kind == 'croisement':
        draw_straight(True)
        for i in range(2, T, 7):
            for k in range(4, 28):
                if not (9 <= k <= 22 and False):
                    pass
        draw_straight(False)
    elif kind.startswith('coin_'):
        cx = 0 if 'g' in kind[5:] else 32
        cy = 0 if 'h' in kind[5:] else 32
        for y in range(T):
            for x in range(T):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                ang = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
                if 12.5 <= d <= 19.5:
                    ang2 = abs(ang) if cy == 0 else abs(ang)
                    q = (abs(ang) if cx == 0 else math.pi - abs(ang))
                    if cy == 0:
                        q = abs(ang) if cx == 0 else math.pi - abs(ang)
                    else:
                        q = abs(ang) if cx == 0 else math.pi - abs(ang)
                    frac = (q / (math.pi / 2) * 5) % 1
                    if cy == 32:
                        q = abs(ang) if cx == 0 else math.pi - abs(ang)
                    if frac < 0.33:
                        cv.p[y][x] = tie[0] if frac < 0.12 else tie[1]
        for y in range(T):
            for x in range(T):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if 11 <= d < 12:
                    cv.p[y][x] = steel[0]
                elif 12 <= d < 13:
                    cv.p[y][x] = steel[1]
                elif 13 <= d < 14:
                    cv.p[y][x] = steel[2]
                elif 19 <= d < 20:
                    cv.p[y][x] = steel[0]
                elif 20 <= d < 21:
                    cv.p[y][x] = steel[1]
                elif 21 <= d < 22:
                    cv.p[y][x] = steel[2]
    elif kind.startswith('buttoir'):
        side = kind.split('_')[1]
        horiz = side in ('g', 'd')
        draw_straight(horiz)
        blk = 3
        if side == 'g':
            box(cv, 1, 8, 6, 24, P['pk_hi'], P['pk_md'], P['pk_dk'])
        elif side == 'd':
            box(cv, 25, 8, 30, 24, P['pk_hi'], P['pk_md'], P['pk_dk'])
        elif side == 'haut':
            box(cv, 8, 1, 24, 6, P['pk_hi'], P['pk_md'], P['pk_dk'])
        else:
            box(cv, 8, 25, 24, 30, P['pk_hi'], P['pk_md'], P['pk_dk'])
        cv.outline()
    elif kind == 'casse':
        draw_straight(True)
        for x in range(10, 20):                       # trou : les rails manquent, traverses cassées
            for y in range(9, 24):
                cv.set(x, y, None)
        cv.line(9, 11, 14, 8, steel[0])
        cv.line(21, 21, 17, 24, steel[1])
        cv.line(10, 20, 16, 16, P['pk_dk'])
        cv.line(14, 12, 20, 16, P['pk_lt'])
        cv.outline()
    return cv.p


@reg('rail_h', 'rail_v', 'rail_coin_hg', 'rail_coin_hd', 'rail_coin_bg', 'rail_coin_bd', 'rail_buttoir_g', 'rail_buttoir_d',
     'rail_buttoir_haut', 'rail_buttoir_bas', 'rail_croisement', 'rail_casse')
def rails(name, tile):
    k = name[5:]
    return rail_tile(k)


def cart(orient, state):
    cv = Cv()
    shadow(cv, 16, 27, 14, 3, P['gr_dk'])
    if orient == 'h':
        for x in (6, 24):
            ell(cv, x, 24, 3, 3.5, P['O'])
            ell(cv, x, 24, 2, 2.5, P['m_lt'])
        box(cv, 2, 9, 29, 23, P['m_hi'], P['m_md'], P['m_dk'])
        box(cv, 4, 12, 27, 22, P['pk_hi'], P['pk_md'], P['pk_dk'])
        for x in (8, 15, 22):
            cv.rect(x, 9, x, 23, P['m_dk'])
            cv.set(x - 1, 9, P['m_hi'])
        rx0, rx1, ry = 3, 28, 9
    else:
        for y in (8, 22):
            ell(cv, 3, y, 2.5, 3, P['O'])
            ell(cv, 28, y, 2.5, 3, P['O'])
        box(cv, 5, 3, 26, 28, P['m_hi'], P['m_md'], P['m_dk'])
        box(cv, 7, 6, 24, 26, P['pk_hi'], P['pk_md'], P['pk_dk'])
        for y in (10, 17, 24):
            cv.rect(5, y, 26, y, P['m_dk'])
        rx0, rx1, ry = 6, 25, 4
    if state == 'plein':
        if orient == 'h':
            mass(cv, [(10, 8, 8, 5), (20, 7, 8, 5), (16, 10, 12, 4)], ROCK_MT, 17, 0.5)
            cv.rect(4, 9, 27, 11, P['m_md'])
        else:
            mass(cv, [(12, 9, 7, 6), (19, 15, 7, 7), (13, 21, 7, 5)], ROCK_MT, 18, 0.5)
        r = random.Random(14)
        for _ in range(7):
            x, y = r.randrange(6, 26), r.randrange(4, 16) if orient == 'h' else r.randrange(5, 26)
            if cv.get(x, y) not in (None, P['m_md'], P['m_dk']):
                cv.set(x, y, P['ore_y'])
                cv.set(x + 1, y, P['ore_o'])
        for (x, y) in ((8, 7), (22, 6)) if orient == 'h' else ((11, 12), (20, 20)):
            cv.set(x, y, P['ore_b'])
            cv.set(x + 1, y, P['ore_bd'])
    cv.outline()
    return cv


@reg('wagonnet_h', 'wagonnet_v', 'wagonnet_vide')
def wagonnet(name, tile):
    return cart('v' if name.endswith('_v') else 'h', 'vide' if name.endswith('vide') else 'plein').p


@reg('wagonnet_renverse')
def wagonnet_renverse(name, tile):
    cv = Cv()
    shadow(cv, 16, 27, 14, 3, P['gr_dk'])
    r = random.Random(41)
    mass(cv, [(20, 24, 9, 4), (25, 26, 5, 3), (14, 26, 5, 3)], ROCK_MT, 19, 0.5)
    for _ in range(11):
        x, y = r.randrange(11, 29), r.randrange(21, 28)
        if cv.get(x, y) not in (None, P['O']):
            cv.set(x, y, P['ore_y'] if r.random() < 0.5 else P['ore_b'])
    # caisse couchée
    for y in range(8, 24):
        for x in range(2, 16):
            if (x - 2) + (y - 8) * 0.35 < 18:
                cv.p[y][x] = P['m_md']
    box(cv, 2, 8, 14, 22, P['m_hi'], P['m_md'], P['m_dk'])
    box(cv, 4, 11, 12, 21, P['O'], P['v_dk'], P['v_dk'], edge=False)
    ell(cv, 6, 5, 3, 3, P['O'])
    ell(cv, 6, 5, 2, 2, P['m_lt'])
    ell(cv, 16, 7, 2.5, 2.5, P['m_lt'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ étais, minerai, outils
def beam(cv, x0, y0, x1, y1):
    box(cv, x0, y0, x1, y1, P['pk_hi'], P['pk_md'], P['pk_dk'])


@reg('etai_poteau')
def etai_poteau(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 8, 2.5, P['gr_dk'])
    beam(cv, 12, 2, 19, 29)
    for y in range(4, 28, 7):
        cv.set(14, y, P['pk_dk'])
        cv.set(15, y + 1, P['pk_dk'])
    box(cv, 9, 26, 22, 30, P['mt_hi'], P['mt_md'], P['mt_dk'])
    cv.outline()
    return cv.p


@reg('etai_poutre_g', 'etai_poutre_m', 'etai_poutre_d')
def etai_poutre(name, tile):
    cv = Cv()
    x0 = 6 if name.endswith('g') else 0
    x1 = 25 if name.endswith('d') else 31
    beam(cv, x0, 8, x1, 17)
    for x in range(x0 + 3, x1, 6):
        cv.set(x, 12, P['pk_dk'])
    if name.endswith('g'):
        box(cv, 3, 4, 10, 22, P['pk_hi'], P['pk_md'], P['pk_dk'])
    if name.endswith('d'):
        box(cv, 21, 4, 28, 22, P['pk_hi'], P['pk_md'], P['pk_dk'])
    if name.endswith('m'):
        for x in (3, 4, 5):
            pass
    cv.outline()
    return cv.p


@reg('etai_cadre_g', 'etai_cadre_d')
def etai_cadre(name, tile):
    cv = Cv()
    left = name.endswith('g')
    x0 = 0 if left else 24
    box(cv, x0, 0, x0 + 7, 31, P['pk_hi'], P['pk_md'], P['pk_dk'])
    for y in range(5, 31, 8):
        cv.set(x0 + 3, y, P['pk_dk'])
    # roche contre le montant
    xs = range(8, 14) if left else range(18, 24)
    for y in range(32):
        for x in xs:
            if rnd(x, y, 3) < 0.55 - abs(x - (8 if left else 23)) * 0.07:
                cv.p[y][x] = P['mt_md'] if rnd(x, y, 4) < 0.6 else P['mt_dk']
    cv.outline()
    return cv.p


@reg('barriere_h', 'barriere_v')
def barriere(name, tile):
    cv = Cv()
    if name.endswith('h'):
        shadow(cv, 16, 26, 14, 2, P['gr_dk'])
        for x in (2, 15, 28):
            box(cv, x, 7, x + 2, 25, P['b_lt'], P['b_md'], P['b_dk'])
        beam(cv, 0, 11, 31, 15)
        beam(cv, 0, 18, 31, 22)
        for x in (3, 16, 29):
            cv.set(x, 13, P['m_hi'])
            cv.set(x, 20, P['m_hi'])
    else:
        for y in (3, 16, 29):
            box(cv, 10, y, 21, y + 2, P['b_lt'], P['b_md'], P['b_dk'])
        beam(cv, 11, 0, 14, 31)
        beam(cv, 17, 0, 20, 31)
    cv.outline()
    return cv.p


def ore_heap(v):
    cv = Cv()
    shadow(cv, 16, 27, 13, 3, P['gr_dk'])
    mass(cv, [(16, 19, 12, 8), (9, 22, 7, 5)] if v == 0 else [(11, 20, 9, 7), (22, 19, 8, 8), (17, 14, 7, 6)], ROCK_MT, 200 + v, 0.45)
    r = random.Random(30 + v)
    for _ in range(16):
        x, y = r.randrange(5, 27), r.randrange(10, 26)
        if cv.get(x, y) not in (None, P['O']):
            if r.random() < 0.6:
                cv.set(x, y, P['ore_y'])
                cv.set(x + 1, y, P['ore_o'])
                cv.set(x, y + 1, P['ore_o'])
            else:
                cv.set(x, y, P['ore_b'])
                cv.set(x + 1, y, P['ore_bd'])
    cv.outline()
    return cv.p


@reg('minerai_tas_a', 'minerai_tas_b')
def minerai_tas(name, tile):
    return ore_heap(0 if name.endswith('a') else 1)


@reg('minerai_filon')
def minerai_filon(name, tile):
    cv = Cv()
    g = ground_tex(1, 'sombre')
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = g[y][x]
    mass(cv, [(9, 9, 10, 8), (24, 9, 9, 8), (16, 21, 14, 9), (5, 26, 8, 6), (27, 26, 8, 6)], (P['mt_lt'], P['mt_md'], P['mt_dk'], P['mt_dp']), 211, 0.4)
    r = random.Random(212)
    for _ in range(9):
        x, y = r.randrange(4, 27), r.randrange(4, 27)
        col = (P['ore_y'], P['ore_o']) if r.random() < 0.6 else (P['ore_b'], P['ore_bd'])
        for dx, dy, c in ((0, 0, col[0]), (1, 0, col[0]), (0, 1, col[1]), (1, 1, col[1]), (-1, 1, col[1])):
            if cv.get(x + dx, y + dy) not in (None, P['O']):
                cv.set(x + dx, y + dy, c)
        cv.set(x, y - 1, P['white'])
    cv.outline()
    return cv.p


def crate(kind):
    cv = Cv()
    shadow(cv, 16, 27, 12, 3, P['gr_dk'])
    if kind == 'tonneau':
        ell(cv, 16, 17, 9, 10, P['b_dk'])
        for y in range(7, 27):
            for x in range(7, 25):
                if ((x - 15.5) / 8.5) ** 2 + ((y - 16.5) / 9.5) ** 2 <= 1:
                    cv.p[y][x] = P['pk_hi'] if x < 11 else P['pk_lt'] if x < 18 else P['pk_md']
        for y in (11, 22):
            for x in range(7, 25):
                if cv.p[y][x] is not None:
                    cv.p[y][x] = P['m_md'] if x > 11 else P['m_lt']
        ell(cv, 16, 8, 7, 2.5, P['pk_md'])
        ell(cv, 16, 7.5, 5, 1.5, P['pk_dk'])
    else:
        box(cv, 4, 8, 27, 26, P['pk_hi'], P['pk_lt'], P['pk_dk'])
        box(cv, 4, 8, 27, 13, P['pk_hi'], P['pk_hi'], P['pk_md'])
        cv.line(5, 14, 26, 25, P['pk_md'])
        cv.line(26, 14, 5, 25, P['pk_md'])
        for (x, y) in ((6, 10), (25, 10), (6, 24), (25, 24)):
            cv.set(x, y, P['m_hi'])
        # éclats de minerai dépassant
        cv.set(10, 9, P['ore_y'])
        cv.set(11, 10, P['ore_o'])
    cv.outline()
    return cv.p


@reg('caisse_mine', 'tonneau_mine')
def caisses(name, tile):
    return crate('tonneau' if name.startswith('tonneau') else 'caisse')


@reg('outils_mine')
def outils(name, tile):
    cv = Cv()
    shadow(cv, 16, 27, 14, 3, P['gr_dk'])
    box(cv, 2, 12, 29, 22, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    for x in (4, 25):
        box(cv, x, 22, x + 2, 28, P['b_lt'], P['b_md'], P['b_dk'])
    # deux pioches posées + une masse
    cv.line(6, 10, 16, 18, P['b_lt'])
    cv.line(6, 11, 16, 19, P['b_dk'])
    for (x0, y0, x1, y1) in ((13, 6, 18, 7), (4, 9, 9, 8)):
        cv.line(x0, y0, x1, y1, P['m_hi'])
    cv.line(17, 8, 26, 17, P['b_lt'])
    cv.line(17, 9, 26, 18, P['b_dk'])
    box(cv, 22, 9, 29, 13, P['m_hi'], P['m_lt'], P['m_dk'])
    cv.outline()
    return cv.p


@reg('pioche_sol')
def pioche_sol(name, tile):
    cv = Cv()
    cv.line(7, 25, 22, 10, P['b_lt'])
    cv.line(8, 25, 23, 10, P['b_dk'])
    cv.line(17, 6, 26, 8, P['m_hi'])
    cv.line(17, 7, 27, 12, P['m_lt'])
    cv.line(18, 8, 26, 13, P['m_dk'])
    cv.set(17, 6, P['m_hi'])
    cv.outline()
    return cv.p


@reg('tas_planches')
def tas_planches(name, tile):
    cv = Cv()
    shadow(cv, 16, 27, 14, 3, P['gr_dk'])
    for i, (y0, x0, x1) in enumerate(((20, 2, 29), (15, 4, 27), (10, 3, 24), (6, 8, 28))):
        box(cv, x0, y0, x1, y0 + 4, P['pk_hi'], P['pk_lt'] if i % 2 else P['pk_md'], P['pk_dk'])
        cv.set(x0 + 5, y0 + 2, P['pk_dk'])
    box(cv, 11, 3, 14, 26, P['b_lt'], P['b_md'], P['b_dk'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ lanternes
def lantern(cv, cx, top, glow=True, lit=True):
    """Lanterne de mineur : anneau, cage de fer, flamme."""
    cv.rect(cx - 1, top, cx + 1, top, P['m_md'])
    cv.set(cx, top - 1, P['m_lt'])
    box(cv, cx - 4, top + 1, cx + 4, top + 3, P['m_hi'], P['m_lt'], P['m_dk'])
    for y in range(top + 4, top + 11):
        for x in range(cx - 4, cx + 5):
            if x in (cx - 4, cx + 4):
                cv.p[y][x] = P['m_dk'] if x > cx else P['m_lt']
            else:
                cv.p[y][x] = (P['fi_y'] if abs(x - cx) < 2 and y < top + 9 else P['fi_o']) if lit else P['m_md']
    if lit:
        cv.set(cx, top + 6, P['white'])
    box(cv, cx - 4, top + 11, cx + 4, top + 13, P['m_hi'], P['m_lt'], P['m_dk'])
    if glow and lit:
        for (dx, dy) in ((-6, 8), (6, 8), (0, 15), (-5, 13), (5, 13)):
            if cv.get(cx + dx, top + dy) is None:
                cv.set(cx + dx, top + dy, mix(P['fi_o'], P['O'], 0.2)[:3] + (110,))


@reg('lanterne_poteau_bas')
def lanterne_pied(name, tile):
    cv = Cv()
    shadow(cv, 16, 28, 7, 2.5, P['gr_dk'])
    beam(cv, 14, 0, 18, 28)
    box(cv, 11, 25, 21, 29, P['mt_hi'], P['mt_md'], P['mt_dk'])
    cv.outline()
    return cv.p


@reg('lanterne_poteau_haut')
def lanterne_haut(name, tile):
    cv = Cv()
    beam(cv, 14, 21, 18, 31)
    lantern(cv, 16, 6)
    cv.outline()
    # le haut du poteau se raccorde au pied (même colonne)
    return cv.p


@reg('lanterne_murale')
def lanterne_murale(name, tile):
    cv = Cv()
    beam(cv, 6, 3, 25, 6)
    lantern(cv, 16, 7)
    cv.outline()
    return cv.p


@reg('lanterne_suspendue')
def lanterne_susp(name, tile):
    cv = Cv()
    for y in range(0, 8):
        cv.set(16, y, P['m_lt'] if y % 2 else P['m_dk'])
    lantern(cv, 16, 8)
    cv.outline()
    return cv.p


@reg('lanterne_sol')
def lanterne_sol(name, tile):
    cv = Cv()
    ell(cv, 16, 25, 11, 4, mix(P['fi_o'], P['O'], 0.2)[:3] + (80,))
    ell(cv, 16, 25, 8, 3, mix(P['fi_y'], P['O'], 0.2)[:3] + (90,))
    lantern(cv, 16, 11, glow=False)
    cv.outline()
    return cv.p


@reg('lanterne_eteinte')
def lanterne_eteinte(name, tile):
    cv = Cv()
    shadow(cv, 16, 26, 7, 2, P['gr_dk'])
    lantern(cv, 16, 12, glow=False, lit=False)
    cv.outline()
    return cv.p


@reg('lueur_sol')
def lueur_sol(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            d = math.hypot((x - 15.5) / 15.5, (y - 15.5) / 15.5)
            if d < 1 and (x + y) % 2 == 0 or d < 0.45:
                a = int(120 * (1 - d))
                if a > 12:
                    cv.p[y][x] = (P['fi_y'][0], P['fi_y'][1], P['fi_y'][2], a if d < 0.45 else min(a, 70))
    return cv.p


@reg('torche_support')
def torche(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 7, 2, P['gr_dk'])
    beam(cv, 14, 12, 17, 29)
    box(cv, 11, 8, 20, 13, P['m_hi'], P['m_lt'], P['m_dk'])
    for (x, y, c) in ((14, 7, 'fi_r'), (15, 5, 'fi_o'), (16, 6, 'fi_o'), (15, 3, 'fi_y'), (16, 2, 'fi_y'), (15, 6, 'fi_y'), (17, 7, 'fi_r'), (13, 8, 'fi_r')):
        cv.set(x, y, P[c])
    cv.set(15, 4, P['white'])
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ panneaux
def sign_post(board_col, kind):
    cv = Cv()
    shadow(cv, 16, 28, 8, 2.5, P['gr_dk'])
    beam(cv, 14, 12, 17, 29)
    if kind == 'bois':
        box(cv, 4, 4, 27, 15, P['pk_hi'], P['pk_lt'], P['pk_dk'])
        for y in (7, 10, 12):
            cv.rect(8, y, 23, y, P['pk_dk'])
    elif kind in ('g', 'd'):
        pts = [(2, 8), (22, 4), (28, 9), (22, 14), (2, 14)] if kind == 'd' else [(29, 8), (9, 4), (3, 9), (9, 14), (29, 14)]
        for y in range(4, 15):
            for x in range(2, 30):
                inside = ((x >= 2 and x <= 23 and 5 <= y <= 13) if kind == 'd' else (x >= 8 and x <= 29 and 5 <= y <= 13))
                tip = (abs(y - 9) <= (5 - (x - 22 if kind == 'd' else 10 - x)) and ((22 <= x <= 28) if kind == 'd' else (4 <= x <= 10)))
                if inside or tip:
                    cv.p[y][x] = P['pk_lt'] if y > 5 else P['pk_hi']
        cv.rect(7 if kind == 'd' else 12, 9, 20 if kind == 'd' else 25, 9, P['pk_dk'])
    elif kind == 'danger':
        box(cv, 4, 3, 27, 16, P['ore_y'], P['ore_o'], P['pk_dk'])
        for x in range(5, 27, 6):
            for y in range(4, 16):
                cv.set(x + (y // 3) % 3, y, P['O'])
        ell(cv, 16, 9, 4, 4, P['white'])
        cv.set(14, 8, P['O'])
        cv.set(18, 8, P['O'])
        cv.rect(15, 11, 17, 11, P['O'])
    elif kind == 'mine':
        box(cv, 4, 3, 27, 16, P['pk_hi'], P['pk_lt'], P['pk_dk'])
        cv.line(8, 6, 23, 13, P['m_hi'])
        cv.line(8, 13, 23, 6, P['m_hi'])
        cv.line(8, 7, 23, 14, P['m_dk'])
        cv.line(9, 6, 14, 5, P['m_lt'])
        cv.line(22, 6, 18, 5, P['m_lt'])
    cv.outline()
    return cv.p


@reg('panneau_bois', 'panneau_g', 'panneau_d', 'panneau_danger', 'panneau_mine')
def panneaux(name, tile):
    return sign_post(None, name.split('_')[1])


@reg('borne_col')
def borne(name, tile):
    cv = Cv()
    shadow(cv, 16, 28, 8, 2.5, P['gr_dk'])
    box(cv, 10, 8, 21, 28, P['mt_hi'], P['mt_lt'], P['mt_dk'])
    box(cv, 9, 5, 22, 11, P['mt_hi'], P['mt_hi'], P['mt_md'])
    cv.set(15, 17, P['mt_dk'])
    cv.rect(13, 16, 18, 16, P['mt_dk'])
    cv.rect(15, 15, 16, 21, P['mt_dk'])
    cv.outline()
    return cv.p


@reg('stele_gardiens')
def stele(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 11, 3, P['gr_dk'])
    box(cv, 7, 4, 24, 28, P['ch_hi'], P['ch_lt'], P['ch_dk'])
    for x in range(7, 25):
        cv.set(x, 4, P['ch_hi'])
    # trois sceaux gravés
    for (cx, cy) in ((15, 10), (11, 19), (20, 19)):
        for y in range(cy - 3, cy + 4):
            for x in range(cx - 3, cx + 4):
                d = math.hypot(x - cx, y - cy)
                if 2.0 <= d < 3.2:
                    cv.set(x, y, P['ch_dk'])
    cv.outline()
    return cv.p


@reg('fanions')
def fanions(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 7, 2.5, P['gr_dk'])
    beam(cv, 14, 3, 17, 29)
    cols = (rgba('#d8584c'), rgba('#e8c048'), rgba('#5c88c8'), rgba('#f0ece0'))
    for i, c in enumerate(cols):
        x0 = 18 if i % 2 == 0 else 4
        y = 5 + i * 5
        w = 9
        for k in range(w):
            for j in range(4 - k // 3):
                xx = x0 + k if x0 == 18 else x0 + 9 - k + 1
                cv.set(xx, y + j + (k // 4), c)
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ entrée de la Mine Effondrée (160 x 96)
def mine_facade():
    W, H = 160, 96
    cv = Cv(W, H)
    # 1. fond : roche sombre (la montagne au-dessus)
    for y in range(0, 16):
        for x in range(W):
            cv.p[y][x] = cliff_face_px(x, y, 'bas', 9)
    VA.stone_blocks(cv, 0, 0, W - 1, 15, 17, (P['mt_lt'], P['mt_md'], P['mt_dk'], P['mt_dp']), 8, 14)
    # 2. façade de planches (x 14..145, y 24..87)
    for y in range(24, 90):
        for x in range(10, 150):
            k = (x - 10) // 7
            c = P['pk_lt'] if k % 2 else P['pk_md']
            if (x - 10) % 7 == 6:
                c = P['pk_dk']
            elif (x - 10) % 7 == 0:
                c = P['pk_hi']
            if rnd(k, y // 9, 6) < 0.16 and (x - 10) % 7 in (2, 3, 4):
                c = P['pk_dk']
            if (y - 24) % 17 == 8 and (x - 10) % 7 == 3:
                c = P['m_dk']
            cv.p[y][x] = c
    # poutres horizontales d'étai
    for yb in (40, 64):
        box(cv, 10, yb, 149, yb + 3, P['pk_hi'], P['pk_md'], P['pk_dk'])
        for x in range(14, 148, 11):
            cv.set(x, yb + 1, P['m_hi'])
    # 3. linteau principal (grosse poutre sur toute la largeur)
    box(cv, 0, 16, W - 1, 27, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    for x in range(6, W - 4, 14):
        cv.set(x, 20, P['pk_dk'])
        cv.set(x + 1, 21, P['pk_dk'])
    for x in range(2, W, 20):
        box(cv, x, 17, x + 2, 26, P['m_hi'], P['m_lt'], P['m_dk'])
    # 4. piliers de pierre aux deux coins
    for x0, x1 in ((0, 11), (148, 159)):
        VA.stone_blocks(cv, x0, 0, x1, H - 1, 41 + x0, (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk']), 8, 12)
        cv.rect(x0, 0, x0, H - 1, P['O'])
        cv.rect(x1, 0, x1, H - 1, P['O'])
    # 5. effondrement côté droit : planches arrachées, trou noir, poutres cassées
    for y in range(30, 86):
        for x in range(104, 146):
            if (x - 104) * 1.1 + (y - 30) * 0.5 < 45 and x > 112 + (y % 5) and y > 33 and ((x - 120) / 20.0) ** 2 + ((y - 55) / 20.0) ** 2 < 1.1:
                cv.p[y][x] = P['v_dk'] if (x + y) % 11 else P['O']
    cv.line(104, 35, 128, 62, P['pk_dk'])
    cv.line(104, 36, 128, 63, P['pk_md'])
    cv.line(134, 32, 112, 70, P['pk_dk'])
    cv.line(133, 32, 111, 70, P['pk_lt'])
    for (x, y) in ((118, 52), (126, 48), (121, 61)):
        cv.set(x, y, P['pk_hi'])
        cv.set(x + 1, y, P['pk_dk'])
    # côté gauche : quelques planches manquantes
    for (x0, y0, x1, y1) in ((26, 46, 33, 63), (40, 70, 47, 86)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                cv.p[y][x] = P['v_dk'] if (x + y) % 13 else P['O']
    # 6. porte : ouverture x 70..89, arche de bois
    for y in range(28, 96):
        for x in range(62, 98):
            cv.p[y][x] = P['pk_lt'] if y < 64 else cv.p[y][x]
    # linteau au-dessus de la porte et trou noir sous le toit
    box(cv, 60, 28, 99, 36, P['pk_hi'], P['pk_md'], P['pk_dk'])
    for y in range(37, 64):
        for x in range(64, 96):
            cv.p[y][x] = P['v_dk'] if (x + y) % 9 else P['O']
    for x in (66, 93):
        box(cv, x - 1, 36, x + 3, 63, P['pk_hi'], P['pk_md'], P['pk_dk'])
    # ouverture de la porte (case du bas, col 2)
    for y in range(64, 96):
        for x in range(64, 96):
            cv.p[y][x] = P['v_dk']
    for x in range(64, 70):
        box(cv, 64, 64, 69, 95, P['pk_hi'], P['pk_md'], P['pk_dk'])
    box(cv, 90, 64, 95, 95, P['pk_hi'], P['pk_md'], P['pk_dk'])
    for y in range(64, 96):
        for x in range(70, 90):
            d = abs(x - 79.5) / 10.0
            cv.p[y][x] = P['O'] if y < 90 else P['v_dk']
            if y > 70 and d < 0.6 and (y + x) % 7 == 0:
                cv.p[y][x] = P['v_lt']
    # petits rails qui disparaissent dans le noir
    for y in range(78, 96, 6):
        cv.rect(73, y, 74, y, P['m_dk'])
        cv.rect(85, y, 86, y, P['m_dk'])
    # 7. socle de pierre (rangée du bas)
    VA.stone_blocks(cv, 12, 84, 63, 95, 51, (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk']), 6, 12)
    VA.stone_blocks(cv, 96, 84, 147, 95, 52, (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk']), 6, 12)
    cv.rect(12, 84, 63, 84, P['O'])
    cv.rect(96, 84, 147, 84, P['O'])
    # 8. décombres : gros blocs tombés devant la case 1
    mass(cv, [(38, 80, 12, 9), (52, 86, 9, 7), (26, 86, 8, 6)], ROCK_MT, 71, 0.45)
    r = random.Random(81)
    for _ in range(22):
        x, y = r.randrange(14, 62), r.randrange(70, 94)
        if cv.p[y][x] in (P['mt_md'], P['mt_lt']):
            cv.set(x, y, P['mt_dk'])
    # 9. enseigne centrale (sur la grosse poutre)
    box(cv, 62, 14, 97, 28, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    cv.line(70, 17, 89, 25, P['m_hi'])
    cv.line(70, 25, 89, 17, P['m_hi'])
    cv.line(70, 18, 89, 26, P['m_dk'])
    cv.line(72, 16, 80, 16, P['m_lt'])
    cv.line(88, 16, 82, 16, P['m_lt'])
    for (x, y) in ((64, 16), (95, 16), (64, 26), (95, 26)):
        cv.set(x, y, P['m_hi'])
    # corde / chaîne cassée
    cv.line(63, 28, 61, 40, P['m_dk'])
    # 10. contour
    for x in range(W):
        cv.p[0][x] = P['O']
    for y in range(H):
        cv.p[y][0] = P['O']
        cv.p[y][W - 1] = P['O']
    cv.rect(0, 95, W - 1, 95, P['O'])
    return cv


_MF = None


def mf():
    global _MF
    if _MF is None:
        _MF = mine_facade()
    return _MF


_MINE_MAP = {'mine_toit_g': (0, 0), 'mine_toit_m': (1, 0), 'mine_toit_enseigne': (2, 0), 'mine_toit_m2': (3, 0), 'mine_toit_d': (4, 0),
             'mine_mur_g': (0, 1), 'mine_mur_planches': (1, 1), 'mine_linteau': (2, 1), 'mine_mur_effondre': (3, 1), 'mine_mur_d': (4, 1),
             'mine_pied_g': (0, 2), 'mine_pied_decombres': (1, 2), 'mine_porte': (2, 2), 'mine_pied_pierre': (3, 2), 'mine_pied_d': (4, 2)}


@reg(*_MINE_MAP)
def mine_tile(name, tile):
    c, r = _MINE_MAP[name]
    p = mf().crop(c * T, r * T)
    if name == 'mine_toit_m2':                     # variante : pas de même planche cassée que m
        p = mf().crop(3 * T, 0)
    return p


def planks_fill(seed, damage=0, cross=False):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            k = x // 7
            c = P['pk_lt'] if k % 2 else P['pk_md']
            if x % 7 == 6:
                c = P['pk_dk']
            elif x % 7 == 0:
                c = P['pk_hi']
            if rnd(k, y // 9, seed) < 0.16 and x % 7 in (2, 3, 4):
                c = P['pk_dk']
            cv.p[y][x] = c
    for yb in (4, 24):
        box(cv, 0, yb, 31, yb + 3, P['pk_hi'], P['pk_md'], P['pk_dk'])
        for x in range(3, 31, 10):
            cv.set(x, yb + 1, P['m_hi'])
    if cross:
        cv.line(2, 2, 29, 29, P['pk_dk'])
        cv.line(2, 3, 29, 30, P['pk_md'])
        cv.line(2, 29, 29, 2, P['pk_dk'])
        cv.line(2, 28, 29, 1, P['pk_md'])
    return cv


@reg('mine_mur_pierre')
def mine_mur_pierre(name, tile):
    cv = Cv()
    VA.stone_blocks(cv, 0, 0, 31, 31, 61, (P['mt_hi'], P['mt_lt'], P['mt_md'], P['mt_dk']), 8, 12)
    return cv.p


@reg('mine_planches_b')
def mine_planches_b(name, tile):
    return planks_fill(77).p


@reg('mine_poutre_tombee_m')
def poutre_tombee(name, tile):
    cv = planks_fill(78)
    for y in range(6, 24):
        for x in range(8, 28):
            if (x - 8) + (y - 6) * 1.0 < 22:
                cv.p[y][x] = P['v_dk'] if (x + y) % 7 else P['O']
    cv.line(2, 26, 30, 4, P['pk_dk'])
    cv.line(2, 27, 30, 5, P['pk_md'])
    cv.line(2, 28, 30, 6, P['pk_lt'])
    cv.line(2, 29, 30, 7, P['pk_dk'])
    return cv.p


@reg('mine_porte_barree')
def porte_barree(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = P['v_dk']
    for x in range(0, 6):
        box(cv, 0, 0, 5, 31, P['pk_hi'], P['pk_md'], P['pk_dk'])
    box(cv, 26, 0, 31, 31, P['pk_hi'], P['pk_md'], P['pk_dk'])
    p = planks_fill(79, cross=True)
    for y in range(T):
        for x in range(6, 26):
            cv.p[y][x] = p.p[y][x]
    cv.line(6, 6, 25, 25, P['pk_dk'])
    box(cv, 7, 12, 24, 15, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    box(cv, 7, 22, 24, 25, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    for (x, y) in ((9, 13), (22, 13), (9, 23), (22, 23)):
        cv.set(x, y, P['m_hi'])
    return cv.p


@reg('mine_porte_ouverte')
def porte_ouverte(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = P['v_dk'] if x > 5 and x < 26 else (P['pk_md'])
    box(cv, 0, 0, 5, 31, P['pk_hi'], P['pk_md'], P['pk_dk'])
    box(cv, 26, 0, 31, 31, P['pk_hi'], P['pk_md'], P['pk_dk'])
    for y in range(0, 32):
        for x in range(6, 26):
            cv.p[y][x] = P['O']
            if y > 14 and (x + y) % 11 == 0:
                cv.p[y][x] = P['v_dk']
    for y in range(4, 32, 6):
        cv.rect(10, y, 11, y, P['m_dk'])
        cv.rect(20, y, 21, y, P['m_dk'])
    return cv.p


@reg('mine_enseigne_dessus')
def enseigne_dessus(name, tile):
    cv = Cv()
    for y in range(0, 5):
        cv.set(9, y, P['m_dk'])
        cv.set(22, y, P['m_dk'])
    box(cv, 4, 5, 27, 17, P['pk_hi'], P['pk_lt'], P['pk_dk'])
    cv.line(9, 8, 22, 15, P['m_hi'])
    cv.line(9, 15, 22, 8, P['m_hi'])
    cv.line(9, 9, 22, 16, P['m_dk'])
    cv.outline()
    return cv.p


@reg('mine_decombres_g', 'mine_decombres_d')
def decombres(name, tile):
    cv = Cv()
    left = name.endswith('g')
    r = random.Random(91 if left else 92)
    mass(cv, [(10 if left else 21, 20, 8, 6), (22 if left else 9, 24, 6, 4), (15, 14, 5, 4)], ROCK_MT, 93 if left else 94, 0.45)
    for _ in range(9):
        x, y = r.randrange(2, 30), r.randrange(6, 30)
        if cv.get(x, y) is None:
            cv.set(x, y, P['mt_lt'])
            cv.set(x + 1, y, P['mt_md'])
            cv.set(x, y + 1, P['mt_dk'])
    cv.line(4, 28, 14, 22, P['pk_dk'])
    cv.line(4, 27, 14, 21, P['pk_lt'])
    cv.outline()
    return cv.p


@reg('mine_seuil')
def mine_seuil(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(4, 28):
            c = P['pk_lt'] if y % 8 else P['pk_dk']
            if y % 8 == 1:
                c = P['pk_hi']
            if rnd(x // 6, y // 8, 5) < 0.12:
                c = P['pk_md']
            cv.p[y][x] = c
    for x in (5, 26):
        cv.rect(x, 0, x + 1, 31, P['pk_dk'])
    for off in (11, 20):
        for y in range(T):
            cv.set(off, y, P['m_hi'])
            cv.set(off + 1, y, P['m_lt'])
            cv.set(off + 2, y, P['m_dk'])
    return cv.p
