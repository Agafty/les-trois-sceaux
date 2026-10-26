"""Village, dessin final, partie 1 : sols, terrains, pont-levis, falaise, blocages."""
import random

from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, GRASS, PATH, SHALLOW, DEEP, F, wset

REG = {}


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


# ------------------------------------------------------------------ textures
def paves_tex(seed=1, kind='a'):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            r = y // 8
            off = 8 if r % 2 else 0
            xx = x + off
            k = (xx // 16) % 2
            yy, xo = y % 8, xx % 16
            v = rnd(k, r, seed)
            base = P['p_hi'] if v > 0.93 else P['p_md'] if v < 0.4 else P['p_lt']
            if kind == 'c':
                base = P['p_hi'] if v > 0.6 else P['p_md'] if v < 0.4 else P['p_lt']
            c = base
            if yy == 7 or xo == 15:
                c = P['p_jt']
            elif yy == 0 or xo == 0:
                c = P['p_hi'] if base != P['p_hi'] else P['white']
            elif yy == 6 or xo == 14:
                c = P['p_md'] if base != P['p_md'] else P['p_dk']
            elif rnd(x, y, seed + 3) < 0.07:
                c = P['p_md'] if base != P['p_md'] else P['p_lt']
            t[y][x] = c
    if kind == 'usees':
        for (x0, y0, x1, y1) in ((3, 1, 9, 6), (20, 10, 26, 14), (6, 17, 10, 22), (24, 25, 29, 29)):
            cv = Cv()
            cv.p = t
            cv.line(x0, y0, x1, y1, P['p_jt'])
            cv.line(x0 + 1, y0, x1 + 1, y1 - 1, P['p_dk'])
    if kind == 'mousse':
        for y in range(T):
            for x in range(T):
                n = vnoise(x, y, 4, seed + 9)
                if n > 0.62 and t[y][x] != P['p_jt']:
                    t[y][x] = P['g_md'] if rnd(x, y, 5) < 0.6 else P['g_dk'] if rnd(x, y, 6) < 0.5 else P['g_lt']
    return t


PAV = paves_tex(1)


def ravin_tex(seed=41):
    t = [[P['v_md']] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, seed) * 0.7 + vnoise(x, y, 8, seed + 2) * 0.3
            t[y][x] = P['v_lt'] if n > 0.68 else P['v_dk'] if n < 0.34 else P['v_md']
            if y % 8 == 3 and rnd(x, y, 7) < 0.5:
                t[y][x] = P['v_dk']
    r = random.Random(seed)
    for _ in range(5):
        wset(t, r.randrange(T), r.randrange(T), P['ch_dk'])
    return t


RAVIN = ravin_tex()


def blend_alpha(c, a):
    return c[:3] + (a,)


# ------------------------------------------------------------------ terrains


@reg(*[f'{p}_{s}' for p in ('paves', 'terre', 'rive', 'lac', 'ravin') for s in ['base', 'plein'] + [f'{b >> 3 & 1}{b >> 2 & 1}{b >> 1 & 1}{b & 1}' for b in range(1, 15)]])
def terrain_family(name, tile):
    fam, suf = name.split('_', 1)
    b = 0 if suf == 'base' else 15 if suf == 'plein' else int(suf, 2)
    if fam == 'paves':
        return terrain_tile(b, GRASS['plain'], PAV, P['g_dk'], P['p_dk'], 7)[0]
    if fam == 'terre':
        return terrain_tile(b, GRASS['plain'], PATH, P['g_dk'], P['t_dk'], 11)[0]
    if fam == 'rive':
        return terrain_tile(b, GRASS['plain'], SHALLOW, P['g_dk'], P['foam'], 21, pb=0.55)[0]
    if fam == 'lac':
        return terrain_tile(b, SHALLOW, DEEP, P['foam'], P['d_dk'], 31, 0.07, pb=1.0)[0]
    return terrain_tile(b, GRASS['plain'], RAVIN, P['g_dk'], P['c_md'], 43, pb=0.9)[0]


# ------------------------------------------------------------------ herbe
@reg('herbe_a', 'herbe_b', 'herbe_c', 'herbe_d', 'herbe_fleurs_blanches', 'herbe_fleurs_jaunes', 'herbe_fleurs_rouges', 'herbe_sombre')
def herbe(name, tile):
    k = dict(herbe_a='plain', herbe_b='tufts', herbe_c='clover', herbe_d='stones', herbe_fleurs_blanches='fl_white',
             herbe_fleurs_jaunes='fl_yel', herbe_fleurs_rouges='fl_red', herbe_sombre='dark')[name]
    return GRASS[k]


# ------------------------------------------------------------------ variantes de pavés
@reg('paves_b', 'paves_c', 'paves_usees', 'paves_mousse')
def paves_var(name, tile):
    return {'paves_b': paves_tex(2, 'b'), 'paves_c': paves_tex(3, 'c'), 'paves_usees': paves_tex(4, 'usees'),
            'paves_mousse': paves_tex(5, 'mousse')}[name]


@reg('paves_rond')
def paves_rond(name, tile):
    cv = tex(paves_tex(6, 'c'))
    for y in range(T):
        for x in range(T):
            d = ((x + 0.5 - 16) ** 2 + (y + 0.5 - 16) ** 2) ** 0.5
            if d < 12:
                cv.p[y][x] = P['p_hi'] if (x + y) % 7 else P['white']
                if x > 16 and y > 16:
                    cv.p[y][x] = P['p_lt']
            if 11.2 <= d < 12.6:
                cv.p[y][x] = P['p_dk']
            if 12.6 <= d < 13.6 and x + y < 32:
                cv.p[y][x] = P['p_hi']
    return cv.p


@reg('paves_blason')
def paves_blason(name, tile):
    cv = tex(paves_tex(8, 'c'))
    for y in range(T):
        for x in range(T):
            if abs(x - 15.5) < 11.5 and abs(y - 15.5) < 11.5:
                cv.p[y][x] = P['p_hi']
                if abs(x - 15.5) > 10.5 or abs(y - 15.5) > 10.5:
                    cv.p[y][x] = P['p_dk']
    for cx, cy in ((16, 11), (11, 20), (21, 20)):          # les trois sceaux
        for y in range(T):
            for x in range(T):
                d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
                if 3.0 <= d < 4.4:
                    cv.p[y][x] = P['p_jt']
                elif d < 3.0:
                    cv.p[y][x] = P['gold_hi'] if (x < cx and y < cy) else P['or_']
    return cv.p


@reg('paves_seuil')
def paves_seuil(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            c = P['p_md']
            if y in (0, 1) or x in (0, 1):
                c = P['p_lt']
            if y >= 29 or x >= 29:
                c = P['p_dk']
            if y == 31 or x == 31:
                c = P['p_jt']
            if rnd(x, y, 12) < 0.06:
                c = P['p_dk']
            cv.p[y][x] = c
    for x in range(3, 29):                       # fente centrale
        if x % 6 != 0:
            cv.p[16][x] = P['p_dk']
    return cv.p


@reg('paves_escalier_h')
def paves_escalier(name, tile):
    cv = Cv()
    for y in range(T):
        step = y // 8
        yy = y % 8
        for x in range(T):
            c = P['p_hi'] if yy == 0 else P['p_lt'] if yy < 4 else P['p_md'] if yy < 7 else P['p_jt']
            if rnd(x, y, 14) < 0.05:
                c = P['p_md']
            cv.p[y][x] = c
    for y in range(T):
        cv.p[y][0] = P['p_dk']
        cv.p[y][31] = P['p_dk']
    return cv.p


# ------------------------------------------------------------------ terre, gravier, sable
def dirt_var(seed, extra=None):
    t = F.path_tex(seed)
    r = random.Random(seed)
    if extra == 'orn_h':
        for yy in (9, 22):
            for x in range(T):
                t[yy][x] = P['t_dk']
                t[yy + 1][x] = P['t_md'] if x % 5 else P['t_dk']
                t[yy - 1][x] = P['t_hi'] if x % 3 == 0 else t[yy - 1][x]
    if extra == 'orn_v':
        for xx in (9, 22):
            for y in range(T):
                t[y][xx] = P['t_dk']
                t[y][xx + 1] = P['t_md'] if y % 5 else P['t_dk']
                t[y][xx - 1] = P['t_hi'] if y % 3 == 0 else t[y][xx - 1]
    if extra == 'flaque':
        for y in range(T):
            for x in range(T):
                if ((x - 15) / 10.0) ** 2 + ((y - 17) / 6.0) ** 2 < 1 + (rnd(x, y, 3) - 0.5) * 0.4:
                    t[y][x] = P['b_dk'] if (x + y) % 5 else P['b_md']
                if ((x - 14) / 7.0) ** 2 + ((y - 16) / 3.5) ** 2 < 1:
                    t[y][x] = P['w_dk'] if (x + y) % 4 else P['w_md']
        for x in (11, 12, 13):
            t[15][x] = P['w_hi']
    if extra == 'cailloux':
        for _ in range(9):
            x, y = r.randrange(1, 30), r.randrange(1, 29)
            wset(t, x, y, P['k_hi'])
            wset(t, x + 1, y, P['k_lt'])
            wset(t, x, y + 1, P['k_md'])
            wset(t, x + 1, y + 1, P['k_dk'])
    return t


@reg('terre_b', 'terre_c', 'terre_ornieres_h', 'terre_ornieres_v', 'terre_flaque', 'terre_cailloux')
def terre_var(name, tile):
    return dict(terre_b=dirt_var(12), terre_c=dirt_var(13), terre_ornieres_h=dirt_var(14, 'orn_h'),
                terre_ornieres_v=dirt_var(15, 'orn_v'), terre_flaque=dirt_var(16, 'flaque'), terre_cailloux=dirt_var(17, 'cailloux'))[name]


@reg('gravier', 'sable_rive')
def gravier(name, tile):
    if name == 'gravier':
        cols = ['#c8c0a8', '#b4ac94', '#d8d0b8', '#9a927c']
    else:
        cols = ['#d8c090', '#c8ae7c', '#e4d0a4', '#b49a68']
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 77) * 0.6 + rnd(x, y, 2) * 0.4
            cv.p[y][x] = rgba_(cols[2] if n > 0.72 else cols[3] if n < 0.2 else cols[0] if n > 0.42 else cols[1])
    if name == 'gravier':
        r = random.Random(5)
        for _ in range(14):
            x, y = r.randrange(31), r.randrange(30)
            cv.set(x, y, P['k_hi'])
            cv.set(x + 1, y, P['k_lt'])
            cv.set(x, y + 1, P['k_md'])
    else:
        for x in range(T):                       # sable humide : ondulations sombres
            cv.p[(x * 3 + 5) % 29][x] = rgba_(cols[3])
            cv.p[(x * 5 + 17) % 31][x] = rgba_(cols[3])
    return cv.p


def rgba_(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


# ------------------------------------------------------------------ falaise et rochers
@reg('falaise_crete', 'falaise_crete_g', 'falaise_crete_d', 'falaise_face', 'falaise_face_g', 'falaise_face_d',
     'falaise_pied', 'falaise_pied_g', 'falaise_pied_d')
def falaise(name, tile):
    kind = name.split('_')[1]
    end = name.split('_')[2] if name.count('_') == 2 else ''
    return F.cliff_tile(kind, end)


def cliff_pixels(p):
    return {(x, y) for y in range(T) for x in range(T) if p[y][x] in (P['c_md'], P['c_lt'], P['c_dk'])}


@reg('falaise_face_lierre', 'falaise_face_mousse')
def falaise_ornee(name, tile):
    p = F.cliff_tile('face', '')
    cv = Cv()
    cv.p = [r[:] for r in p]
    lierre = name.endswith('lierre')
    for y in range(T):
        for x in range(T):
            if (x, y) in cliff_pixels(p) and p[y][x] != P['O']:
                n = vnoise(x, y, 4, 91 if lierre else 92)
                if lierre:
                    if n > 0.58:
                        cv.p[y][x] = P['g_lt'] if rnd(x, y, 1) < 0.3 else P['g_md'] if n < 0.78 else P['g_dk']
                else:
                    if y < 14 and n > 0.5:
                        cv.p[y][x] = P['g_md'] if rnd(x, y, 1) < 0.7 else P['g_lt']
    if lierre:
        for x in (6, 15, 24):                    # tiges
            for y in range(T):
                if rnd(x, y, 3) < 0.7:
                    cv.p[y][x + (y // 5) % 2] = P['g_dk']
    return cv.p


@reg('falaise_sommet', 'falaise_sommet_pierre')
def falaise_sommet(name, tile):
    if name == 'falaise_sommet':
        mp = {P['g_md']: rgba_('#78a858'), P['g_lt']: rgba_('#98c070'), P['g_dk']: rgba_('#5a8a3c'), P['g_hi']: rgba_('#a8cc80')}
        return [[mp.get(c, c) for c in row] for row in GRASS['plain']]
    t = paves_tex(21, 'b')
    mp = {P['p_hi']: P['c_lt'], P['p_lt']: P['c_md'], P['p_md']: rgba_('#6a5e54'), P['p_jt']: P['c_dk'], P['p_dk']: P['c_dk'], P['white']: P['c_lt']}
    return [[mp.get(c, c) for c in row] for row in t]


@reg('rocher_a', 'rocher_b')
def rochers(name, tile):
    return F.rock(0 if name == 'rocher_a' else 1)


@reg('cailloux_village')
def cailloux(name, tile):
    return F.pebbles()


# ------------------------------------------------------------------ pont-levis
def wood_planks_v(cv, x0, y0, x1, y1, seed=0):
    """Planches verticales (tablier vu de dessus, planches dans le sens de la marche = haut-bas)."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            k = (x - x0) // 5
            c = P['pk_lt'] if k % 2 else P['pk_hi']
            if (x - x0) % 5 == 4:
                c = P['pk_dk']
            elif (x - x0) % 5 == 0:
                c = P['pk_hi']
            if rnd(k, (y + 7 * k) // 9, seed) < 0.2 and (x - x0) % 5 in (1, 2, 3):
                c = P['pk_md']
            if (y - y0) % 13 == 6 and (x - x0) % 5 == 2:
                c = P['pk_dk']             # clou
            cv.set(x, y, c)


def raised_bridge():
    cv = Cv(64, 64)
    # panneau debout (le tablier relevé) : planches verticales, 3 bandes de fer, charnière en bas
    for y in range(2, 58):
        for x in range(5, 59):
            k = (x - 5) // 6
            c = P['pk_lt'] if k % 2 else P['pk_hi']
            if (x - 5) % 6 == 5:
                c = P['pk_dk']
            elif (x - 5) % 6 == 0:
                c = P['pk_hi']
            if y < 6:
                c = P['pk_md'] if (x + y) % 2 else P['pk_lt']
            if rnd(k, y // 7, 4) < 0.15 and (x - 5) % 6 in (2, 3):
                c = P['pk_md']
            cv.p[y][x] = c
    for yb in (12, 28, 44):
        box(cv, 5, yb, 58, yb + 3, P['m_lt'], P['m_md'], P['m_dk'])
        for x in range(8, 58, 9):
            cv.set(x, yb + 1, P['m_hi'])
    for x in (5, 58):
        for y in range(2, 58):
            cv.p[y][x] = P['pk_dk']
    # anneaux de chaîne en haut
    for x in (16, 47):
        ell(cv, x, 5, 4, 4, P['m_md'])
        ell(cv, x, 5, 2, 2, P['pk_md'])
        cv.set(x - 2, 3, P['m_hi'])
    # charnière / seuil du bas
    box(cv, 2, 56, 61, 61, P['pk_hi'], P['pk_md'], P['pk_dk'])
    for x in range(6, 60, 12):
        box(cv, x, 56, x + 3, 61, P['m_hi'], P['m_lt'], P['m_dk'])
    cv.outline()
    return cv


def lowered_bridge(h=96):
    cv = Cv(64, h)
    for y in range(0, h):
        for x in range(4, 60):
            c = P['pk_lt']
            if (x - 4) % 7 == 6:
                c = P['pk_dk']
            elif (x - 4) % 7 == 0:
                c = P['pk_hi']
            if rnd((x - 4) // 7, y // 11, 6) < 0.18 and (x - 4) % 7 in (1, 2, 3, 4, 5):
                c = P['pk_md']
            cv.p[y][x] = c
    for y in range(0, h, 11):                       # traverses
        hline(cv, 4, 59, y, P['pk_dk'])
    for y in range(0, h, 11):
        hline(cv, 4, 59, y + 1, P['pk_md'] if y else P['pk_lt'])
    # garde-corps : poteaux tous les 24 px + lisses
    for x0, x1 in ((0, 5), (58, 63)):
        for y in range(0, h):
            c = P['b_lt'] if x0 == 0 else P['b_dk']
            cv.p[y][x0] = P['b_lt']
            for x in range(x0, x1 + 1):
                cv.p[y][x] = P['b_md'] if x not in (x0, x1) else (P['b_lt'] if x == x0 else P['b_dk'])
        for y in range(8, h, 24):
            box(cv, x0 - 1 if x0 else 0, y, x1 + 1 if x1 < 63 else 63, y + 3, P['b_lt'], P['b_md'], P['b_dk'])
            ell(cv, (x0 + x1) / 2.0 + 0.5, y - 1, 3, 3, P['m_md'])
            cv.set(int((x0 + x1) / 2.0), y - 2, P['m_hi'])
    # articulation en haut : grosse poutre et charnières de fer
    box(cv, 0, 0, 63, 5, P['b_lt'], P['b_md'], P['b_dk'])
    for x in (10, 52):
        box(cv, x, 0, x + 5, 7, P['m_hi'], P['m_lt'], P['m_dk'])
    # extrémité sud : planche d'appui + ombre
    box(cv, 0, h - 6, 63, h - 1, P['pk_hi'], P['pk_md'], P['pk_dk'])
    cv.outline()
    return cv


_RB, _LB = raised_bridge(), lowered_bridge()


@reg('pl_releve_haut_g', 'pl_releve_haut_d', 'pl_releve_bas_g', 'pl_releve_bas_d')
def pl_releve(name, tile):
    c, r = (0 if name.endswith('_g') else 1), (0 if 'haut' in name else 1)
    return _RB.crop(c * T, r * T)


@reg('pl_abaisse_haut_g', 'pl_abaisse_haut_d', 'pl_abaisse_mil_g', 'pl_abaisse_mil_d', 'pl_abaisse_bas_g', 'pl_abaisse_bas_d')
def pl_abaisse(name, tile):
    c = 0 if name.endswith('_g') else 1
    r = 0 if 'haut' in name else 1 if 'mil' in name else 2
    return _LB.crop(c * T, r * T)


def stone_blocks(cv, x0, y0, x1, y1, seed=0, pal=None, h=8, w=16):
    hi, lt, md, dk = pal or (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk'])
    for y in range(y0, y1 + 1):
        r = (y - y0) // h
        off = (w // 2) if r % 2 else 0
        for x in range(x0, x1 + 1):
            xx = x - x0 + off
            yy = (y - y0) % h
            xo = xx % w
            v = rnd(xx // w, r, seed)
            base = lt if v > 0.3 else md
            c = base
            if yy == h - 1 or xo == w - 1:
                c = dk
            elif yy == 0 or xo == 0:
                c = hi if v > 0.15 else lt
            elif rnd(x, y, seed + 1) < 0.06:
                c = md if base == lt else dk
            cv.set(x, y, c)


@reg('pl_pilier_g', 'pl_pilier_d')
def pilier(name, tile):
    cv = Cv()
    stone_blocks(cv, 5, 2, 26, 31, 3 if name.endswith('g') else 4, w=11, h=8)
    box(cv, 3, 0, 28, 5, P['k_hi'], P['k_lt'], P['k_dk'])        # chapiteau
    ell(cv, 16, 3, 4, 2, P['m_md'])                              # anneau de chaîne
    cv.set(14, 2, P['m_hi'])
    for y in range(6, 32):
        cv.p[y][26] = P['k_dk']
        cv.p[y][25] = P['k_md']
    cv.outline()
    return cv.p


@reg('pl_tour_mur')
def tour_mur(name, tile):
    cv = Cv()
    stone_blocks(cv, 0, 0, 31, 31, 31, (P['ch_hi'], P['ch_lt'], P['ch_md'], P['ch_dk']), 8, 16)
    return cv.p


@reg('pl_tour_porte')
def tour_porte(name, tile):
    cv = Cv()
    stone_blocks(cv, 0, 0, 31, 31, 33, (P['ch_hi'], P['ch_lt'], P['ch_md'], P['ch_dk']), 8, 16)
    for y in range(6, 32):                      # arche et porte de bois
        for x in range(5, 27):
            ar = ((x - 15.5) / 10.5) ** 2 + ((y - 16) / 10.0) ** 2
            if (y >= 16 and 5 <= x <= 26) or ar <= 1:
                if y >= 16 or ar <= 1:
                    cv.p[y][x] = P['v_dk']
    for y in range(8, 32):
        for x in range(7, 25):
            ar = ((x - 15.5) / 8.5) ** 2 + ((y - 16) / 8.0) ** 2
            if (y >= 16 or ar <= 1) and cv.p[y][x] == P['v_dk']:
                c = P['pk_md'] if (x - 7) % 5 else P['pk_dk']
                if y > 28:
                    c = P['pk_dk']
                cv.p[y][x] = c
    for y in range(10, 31, 7):
        hline(cv, 8, 23, y, P['m_dk'])
    cv.set(21, 20, P['gold_hi'])
    return cv.p


@reg('pl_chaine_g', 'pl_chaine_d')
def chaine(name, tile):
    cv = Cv()
    pts = []
    for i in range(9):
        t = i / 8.0
        pts.append((3 + 25 * t, 30 - 28 * t))
    for k, (x, y) in enumerate(pts):
        ell(cv, x, y, 2.3, 1.7 if k % 2 else 2.3, P['m_lt'] if k % 2 else P['m_md'])
        cv.set(int(x) - 1, int(y) - 1, P['m_hi'])
    cv.outline()
    return mirror_tile(cv.p) if name.endswith('_d') else cv.p


def mirror_tile(p):
    return [r[::-1] for r in p]


# ------------------------------------------------------------------ blocages
def rubble_circles(seed, wide=False):
    r = random.Random(seed)
    cs = []
    w = 64 if wide else 32
    n = 16 if wide else 8
    for i in range(n):
        cs.append(((i + 0.5) * w / n + r.uniform(-2, 2), r.uniform(15, 24), r.uniform(6, 10), r.uniform(5, 8)))
    for i in range(n // 2):
        cs.append((r.uniform(4, w - 4), r.uniform(9, 14), r.uniform(5, 8), r.uniform(4, 6)))
    return cs


def rubble(w, seed):
    cv = Cv(w, T)
    r = random.Random(seed)
    ground_shadow(cv, w / 2, 28, w / 2 - 1, 3, P['t_dk'])
    pal = (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk'])
    for (cx, cy, rx, ry) in sorted(rubble_circles(seed, w == 64), key=lambda c: c[1]):
        sub = Cv(w, T)
        ell_shade(sub, cx, cy, rx, ry, pal, seed + int(cx), 0.3)
        sub.outline()
        paste(cv, sub, 0, 0)
    for y in range(T):
        for x in range(w):
            if cv.p[y][x] in (None,):
                continue
    return cv


@reg('eboulis_a', 'eboulis_b')
def eboulis_ab(name, tile):
    return rubble(32, 5 if name.endswith('a') else 8).p


_EW = rubble(64, 12)


@reg('eboulis_g', 'eboulis_d')
def eboulis_gd(name, tile):
    return _EW.crop(0 if name.endswith('_g') else 32, 0)


@reg('eboulis_degage_a', 'eboulis_degage_b')
def eboulis_degage(name, tile):
    t = F.path_tex(23 if name.endswith('a') else 24)
    cv = tex(t)
    r = random.Random(3 if name.endswith('a') else 4)
    for _ in range(10):
        x, y = r.randrange(1, 29), r.randrange(1, 29)
        w = r.choice((2, 3, 4))
        for dy in range(2):
            for dx in range(w):
                cv.set(x + dx, y + dy, P['k_lt'] if dy == 0 else P['k_md'])
        cv.set(x, y, P['k_hi'])
        hline(cv, x, x + w - 1, y + 2, P['t_dk'])
    return cv.p


@reg('mur_fissure')
def mur_fissure(name, tile):
    cv = Cv()
    stone_blocks(cv, 0, 0, 31, 31, 51, (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 8, 16)
    pts = [(14, 0), (16, 5), (13, 9), (17, 14), (14, 19), (18, 24), (16, 31)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], P['O'])
        cv.line(a[0] + 1, a[1], b[0] + 1, b[1], P['s_md'])
    for (x0, y0, x1, y1) in ((16, 9, 24, 12), (14, 19, 7, 22)):
        cv.line(x0, y0, x1, y1, P['k_dk'])
    return cv.p


@reg('mur_fissure_ouvert')
def mur_ouvert(name, tile):
    cv = Cv()
    stone_blocks(cv, 0, 0, 31, 31, 51, (P['k_hi'], P['k_lt'], P['k_md'], P['k_dk']), 8, 16)
    for y in range(4, 32):
        for x in range(4, 28):
            e = ((x - 15.5) / 11.0) ** 2 + ((y - 20) / 16.0) ** 2
            if e <= 1 + (rnd(x, y, 8) - 0.5) * 0.25 and y >= 5:
                cv.p[y][x] = P['v_dk'] if e > 0.35 else P['O']
    for y in range(4, 32):
        for x in range(3, 29):
            if cv.p[y][x] in (P['v_dk'], P['O']):
                for dx, dy in ((-1, 0), (0, -1), (-1, -1)):
                    n = cv.get(x + dx, y + dy)
                    if n is not None and n not in (P['v_dk'], P['O']):
                        cv.p[y + dy][x + dx] = P['k_dk']
    return cv.p


@reg('mur_fissure_gravats')
def mur_gravats(name, tile):
    cv = Cv()
    ground_shadow(cv, 16, 26, 13, 4, P['t_dk'])
    r = random.Random(77)
    for _ in range(9):
        x, y = r.randrange(3, 27), r.randrange(14, 27)
        s = r.choice((2, 3, 3, 4))
        for dy in range(s - 1):
            for dx in range(s):
                cv.set(x + dx, y + dy, P['k_lt'] if dy == 0 else P['k_md'])
        cv.set(x, y, P['k_hi'])
        hline(cv, x, x + s - 1, y + s - 1, P['k_dk'])
    cv.outline()
    return cv.p


@reg('eboulis_poussiere')
def poussiere(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 61)
            if n > 0.55 and (x + y) % 2 == 0:
                cv.p[y][x] = P['t_hi'][:3] + (150,)
            elif n > 0.7:
                cv.p[y][x] = P['t_lt'][:3] + (110,)
    r = random.Random(61)
    for _ in range(6):
        x, y = r.randrange(2, 29), r.randrange(4, 28)
        cv.set(x, y, P['k_lt'])
        cv.set(x + 1, y, P['k_md'])
        cv.set(x, y + 1, P['k_dk'])
    return cv.p
