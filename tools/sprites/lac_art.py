"""Lac, dessin final : cascade et alcôve, façade du Sanctuaire Englouti, quai, îlot et gué, ambiance de l'eau.

Palette : eau de foret.py (w_* peu profonde, d_* profonde), pierre gris-violet des pavés du village (p_*), algues vert-bleu.
Lumière en haut à gauche, contour sombre d'1 px. Les tuiles à pixels semi-transparents (rideau de cascade, brume, lueurs) sont voulues.
"""
import random

import foret as F
from art_lib import *  # noqa: F401,F403
from art_lib import P, O, Cv, T, rnd, vnoise, wset, rgba, box, ell, ell_shade, hline, vline, dither, paste, mix, tint, shadow, GRASS

P.update({k: rgba(v) for k, v in dict(
    al_hi='#6aaa84', al_lt='#4a8a6c', al_md='#2f6a56', al_dk='#1e4a42',
    st_hi='#c4c2d8', st_lt='#a4a2c0', st_md='#8684a4', st_dk='#5e5c7c', st_jt='#46445e',
    wt_dk='#3a4a6c', glow='#8ae0f8', glow2='#c8f4ff', night='#1c2040', night2='#2a2e58').items()})
REG = {}
WALL = (P['st_hi'], P['st_lt'], P['st_md'], P['st_dk'], P['st_jt'])


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


def A(c, a):
    return c[:3] + (a,)


def cvp(t):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            cv.p[y][x] = t[y][x]
    return cv


def water(deep=False):
    return cvp(F.DEEP if deep else F.SHALLOW)


# ------------------------------------------------------------------ textures
def stone(seed, pal=WALL, bh=8, bw=16, y0=0, cv=None, x0=0, x1=T - 1, y1=T - 1):
    hi, lt, md, dk, jt = pal
    cv = cv or Cv()
    for y in range(y0, y1 + 1):
        row = (y - y0) // bh
        off = (row % 2) * (bw // 2)
        for x in range(x0, x1 + 1):
            bx, by = (x + off) % bw, (y - y0) % bh
            n = vnoise(x, y, 8, seed)
            c = lt if n > 0.62 else dk if n < 0.28 else md
            if rnd(x, y, seed + 3) < 0.04:
                c = hi
            if by == 0:
                c = hi if bx else lt
            if by == bh - 1 or bx == bw - 1:
                c = jt if (by == bh - 1 or n < 0.6) else dk
            cv.p[y][x] = c
    return cv


def flags(seed, pal=WALL, size=16):
    """Dalles carrées de quai."""
    hi, lt, md, dk, jt = pal
    cv = Cv()
    for y in range(T):
        for x in range(T):
            bx, by = x % size, y % size
            n = vnoise(x, y, 8, seed)
            c = lt if n > 0.6 else dk if n < 0.3 else md
            if by == 0 or bx == 0:
                c = hi if rnd(x, y, 1) < 0.7 else lt
            if by == size - 1 or bx == size - 1:
                c = jt
            if rnd(x, y, seed) < 0.03:
                c = dk
            cv.p[y][x] = c
    return cv


def cliff():
    return cvp(F.cliff_tile('face', ''))


def fall_px(x, y, frame):
    """Pixel de la chute (motif périodique de 8 px en hauteur : 2 images décalées de 4 px bouclent sans saut)."""
    ph = (y + frame * 4 + (x * 5) % 8) % 8
    if (x + 3) % 7 == 0 and ph in (2, 3):
        return P['white']
    return P['w_hi'] if ph < 2 else P['w_lt'] if ph < 5 else P['w_md']


def wet_edge(cv, side, frame):
    for y in range(T):
        for k in range(5):
            x = 27 + k if side == 'g' else 4 - k
            c = P['w_dk'] if (x + y + frame) % 2 else P['w_md']
            if k < 2:
                c = P['w_lt'] if (y + frame * 4) % 8 < 3 else P['w_md']
            if rnd(x, y, 9) < 0.8 - k * 0.12:
                cv.p[y][x] = c
    return cv


# ------------------------------------------------------------------ cascade
def water_fall(frame):
    cv = cliff()
    for y in range(T):
        for x in range(4, 28):
            cv.p[y][x] = fall_px(x, y, frame)
        cv.p[y][3] = P['O']
        cv.p[y][28] = P['O']
        cv.p[y][4] = P['w_dk']
        cv.p[y][27] = P['w_dk']
    return cv


@reg('cascade_chute_a', 'cascade_chute_b')
def chute(name, tile):
    return water_fall(0 if name.endswith('a') else 1).p


@reg('cascade_haut')
def cascade_haut(name, tile):
    cv = cvp(F.cliff_tile('crete', ''))
    wf = water_fall(0)
    for y in range(0, T):                   # chenal d'amont qui se resserre, puis chute
        w = 12 if y < 16 else 12
        for x in range(4, 28):
            if y >= 16:
                cv.p[y][x] = wf.p[y][x]
            elif abs(x - 15.5) <= w - (16 - y) // 4:
                cv.p[y][x] = P['w_lt'] if (x + y * 2) % 5 else P['w_hi']
                if y < 3 and abs(x - 15.5) > 9:
                    cv.p[y][x] = F.GRASS['plain'][y][x]
    for x in range(4, 28):
        cv.p[15][x] = P['white'] if x % 3 else P['w_hi']
        cv.p[16][x] = P['w_hi']
        cv.p[14][x] = P['w_lt']
    for y in range(16, T):
        cv.p[y][3] = P['O']
        cv.p[y][28] = P['O']
    return cv.p


@reg('cascade_jambage_g', 'cascade_jambage_d')
def jambage(name, tile):
    p = F.cliff_tile('face', 'g' if name.endswith('_g') else 'd')
    cv = cvp(p)
    return wet_edge(cv, 'g' if name.endswith('_g') else 'd', 0).p


@reg('alcove_fond')
def alcove_fond(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 41)
            cv.p[y][x] = P['night2'] if n > 0.62 else P['night'] if n > 0.3 else P['s_dk']
            if rnd(x, y, 5) < 0.03:
                cv.p[y][x] = P['wt_dk']
    for y in range(0, 6):                        # linteau de roche
        for x in range(T):
            cv.p[y][x] = P['c_md'] if (y + x // 5) % 3 else P['c_dk']
        if y == 5:
            for x in range(T):
                cv.p[y][x] = P['c_dk']
    for x in range(T):
        cv.p[6][x] = P['s_dk']
    for _ in range(5):                            # suintements luisants
        x = int(rnd(_, 1, 7) * 28) + 2
        cv.set(x, 12 + _ * 3, P['wt_dk'])
        cv.set(x, 13 + _ * 3, P['w_dk'])
    return cv.p


@reg('alcove_sol')
def alcove_sol(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 43) * 0.7 + rnd(x, y, 2) * 0.3
            cv.p[y][x] = P['c_lt'] if n > 0.68 else P['c_dk'] if n < 0.25 else P['c_md']
            cv.p[y][x] = mix(cv.p[y][x], P['w_md'], 0.28)
    r = random.Random(14)
    for _ in range(6):                            # flaques
        x, y = r.randrange(2, 26), r.randrange(2, 28)
        ell(cv, x + 2, y + 1, 3, 1.6, P['w_lt'])
        cv.set(x + 1, y, P['w_hi'])
        cv.set(x + 2, y, P['w_hi'])
    return cv.p


@reg('cascade_bassin')
def bassin(name, tile):
    cv = water()
    for y in range(0, 14):
        for x in range(T):
            d = rnd(x, y, 4) * 14
            if d > y * 1.1:
                cv.p[y][x] = P['white'] if rnd(x, y, 6) < 0.4 else P['foam']
    for y in range(14, 30, 4):                    # anneaux qui s'élargissent
        for x in range(3 + y // 4, 29 - y // 4):
            if (x + y) % 3 == 0:
                cv.p[y][x] = P['w_hi']
    return cv.p


@reg('cascade_voile_a', 'cascade_voile_b')
def voile(name, tile):
    frame = 0 if name.endswith('a') else 1
    cv = Cv()
    for y in range(T):
        for x in range(T):
            ph = (y + frame * 4 + (x * 5) % 8) % 8
            if ph < 2:
                cv.p[y][x] = A(P['white'], 150)
            elif ph < 4:
                cv.p[y][x] = A(P['w_hi'], 95)
            elif ph < 6 and (x % 3):
                cv.p[y][x] = A(P['w_lt'], 55)
    return cv.p


@reg('cascade_voile_pied')
def voile_pied(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            ph = (y + (x * 5) % 8) % 8
            fade = (y + 1) / T
            if ph < 2 and rnd(x, y, 3) < 0.4 + fade * 0.5:
                cv.p[y][x] = A(P['white'], int(80 + 110 * fade))
            elif ph < 4 and rnd(x, y, 5) < 0.3 + fade * 0.3:
                cv.p[y][x] = A(P['w_hi'], int(50 + 80 * fade))
    for x in range(T):
        if rnd(x, 2, 8) < 0.7:
            cv.p[30][x] = A(P['foam'], 190)
            cv.p[31][x] = A(P['white'], 210)
    return cv.p


@reg('alcove_lueur')
def alcove_lueur(name, tile):
    cv = Cv()
    for cx, cy in ((15, 17), (9, 24), (22, 24), (12, 11), (20, 12)):
        cv.set(cx, cy, P['white'])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.set(cx + dx, cy + dy, P['fi_y'])
    ell(cv, 15.5, 26, 9, 2.5, A(P['fi_y'], 90))
    return cv.p


@reg('cascade_ecume')
def ecume(name, tile):
    cv = Cv()
    r = random.Random(23)
    for _ in range(10):
        x, y = r.randrange(2, 28), r.randrange(4, 28)
        ell(cv, x + 1, y + 1, 2.5, 1.6, P['foam'])
        cv.set(x, y, P['white'])
    return cv.p


def flat_stone(cv, cx, cy, rx, ry, pal=(P['k_hi'], P['k_lt'], P['k_md'], P['k_dk'])):
    ell_shade(cv, cx, cy, rx, ry, pal, cx + cy, 0.2)
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.p[y][x] is not None and any(cv.get(x + dx, y + dy) is None for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                cv.p[y][x] = P['O']
    for x in range(int(cx - rx + 2), int(cx + rx - 1)):          # reflet d'eau sous la pierre
        if cv.get(x, int(cy + ry) + 1) is None and rnd(x, cy, 5) < 0.6:
            cv.set(x, int(cy + ry) + 1, A(P['w_hi'], 255))


@reg('ruisseau_pierres')
def ruisseau_pierres(name, tile):
    cv = Cv()
    flat_stone(cv, 9, 10, 5.5, 3.5)
    flat_stone(cv, 22, 17, 6, 3.8)
    flat_stone(cv, 11, 25, 5, 3.2)
    return cv.p


# ------------------------------------------------------------------ façade du Sanctuaire
def cornice(cv, x0=0, x1=T - 1):
    """Corniche éclairée : 5 rangées en haut."""
    for x in range(x0, x1 + 1):
        cv.p[0][x] = P['O']
        cv.p[1][x] = P['st_hi']
        cv.p[2][x] = P['st_lt']
        cv.p[3][x] = P['st_md']
        cv.p[4][x] = P['st_dk']
        cv.p[5][x] = P['st_jt']


def wave_band(cv, y0, seed=0):
    """Frise sculptée : vagues stylisées (Sanctuaire Englouti)."""
    for x in range(T):
        k = x % 8
        yy = y0 + (0, 1, 2, 3, 3, 2, 1, 0)[k]
        cv.p[yy][x] = P['st_jt']
        cv.p[yy + 1][x] = P['st_dk']
        if k in (3, 4):
            cv.p[yy + 2][x] = P['st_lt']


@reg('sanct_frise_a', 'sanct_frise_b', 'sanct_frise_g', 'sanct_frise_d')
def frise(name, tile):
    cv = stone(11 if name.endswith('a') else 12 if name.endswith('b') else 13)
    cornice(cv)
    for y in range(6, 11):
        for x in range(T):
            cv.p[y][x] = P['st_md']
    wave_band(cv, 11)
    for x in range(T):
        cv.p[18][x] = P['st_jt']
    if name.endswith('g'):
        for y in range(T):
            cv.p[y][0] = P['O']
            cv.p[y][1] = P['st_hi'] if y > 5 else cv.p[y][1]
    if name.endswith('d'):
        for y in range(T):
            cv.p[y][31] = P['O']
            cv.p[y][30] = P['st_dk']
    return cv.p


@reg('sanct_fronton_g', 'sanct_fronton_d')
def fronton(name, tile):
    left = name.endswith('g')
    cv = stone(14, pal=(P['st_lt'], P['st_md'], P['st_dk'], P['st_jt'], P['st_jt']))
    cornice(cv)
    cx = 32 if left else 0                        # anneau du sceau, centré sur le joint entre les deux moitiés
    for y in range(T):
        for x in range(T):
            d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - 17) ** 2) ** 0.5
            if 9 <= d < 11.5:
                cv.p[y][x] = P['glow'] if d < 10 else P['wt_dk']
            elif d < 9:
                cv.p[y][x] = P['night2'] if d > 5 else P['night']
            if 5.5 <= d < 7 and abs(x + 0.5 - cx) < 1.5 + (y - 17) ** 2 * 0.0:
                pass
    for dx in range(-6, 7):                       # vague gravée au centre de l'anneau
        xx = int(cx + dx)
        if 0 <= xx < T:
            for dy in (0, 1):
                cv.p[17 + (0, 1, 1, 0, -1, -1)[dx % 6] + dy][xx] = P['glow2'] if dy == 0 else P['glow']
    return cv.p


def noyer(cv, waterline, seed, heavy=1.0):
    """Algues et humidité sous `waterline` (mur à demi noyé)."""
    for y in range(waterline, T):
        for x in range(T):
            d = (y - waterline) / max(1, T - waterline)
            n = vnoise(x, y, 8, seed)
            if y == waterline:
                cv.p[y][x] = P['w_hi'] if x % 3 else P['foam']
            elif n + d * 0.5 * heavy > 0.78:
                cv.p[y][x] = P['al_md'] if rnd(x, y, 2) < 0.6 else P['al_lt']
            else:
                cv.p[y][x] = mix(cv.p[y][x], P['wt_dk'], 0.30 + 0.35 * d)
    for x in range(T):                            # filaments d'algues qui pendent
        if rnd(x, 1, seed) < 0.25 * heavy:
            for y in range(waterline - 4, waterline):
                cv.p[y][x] = P['al_lt'] if y % 2 else P['al_md']
    return cv


@reg('sanct_mur_noye_a', 'sanct_mur_noye_b')
def mur_noye(name, tile):
    a = name.endswith('a')
    cv = stone(21 if a else 22)
    return noyer(cv, 14 if a else 18, 31 if a else 32).p


@reg('sanct_mur_g', 'sanct_mur_d')
def mur_coin(name, tile):
    cv = stone(23 if name.endswith('g') else 24)
    left = name.endswith('g')
    xs = range(0, 9) if left else range(23, 32)
    for y in range(T):                           # pilastre
        for x in xs:
            e = x if left else 31 - x
            c = P['st_lt']
            if e == 0:
                c = P['O']
            elif e == 1:
                c = P['st_hi']
            elif e >= 7:
                c = P['st_jt'] if e == 8 else P['st_dk']
            elif e >= 5:
                c = P['st_md']
            cv.p[y][x] = c
        if y % 8 == 7:
            for x in xs:
                if cv.p[y][x] not in (P['O'],):
                    cv.p[y][x] = P['st_dk']
    return cv.p


@reg('sanct_pilastre')
def pilastre(name, tile):
    cv = stone(25)
    for y in range(T):
        for x in range(10, 22):
            e = x - 10
            cv.p[y][x] = P['st_hi'] if e < 2 else P['st_lt'] if e < 5 else P['st_md'] if e < 9 else P['st_dk']
        cv.p[y][9] = P['O']
        cv.p[y][22] = P['O']
    for y in (0, 1, 30, 31):
        for x in range(8, 24):
            cv.p[y][x] = P['st_hi'] if y < 2 else P['st_dk']
    return cv.p


@reg('sanct_linteau_g', 'sanct_linteau_d')
def linteau(name, tile):
    left = name.endswith('g')
    cv = stone(26 if left else 27, pal=(P['st_hi'], P['st_lt'], P['st_md'], P['st_dk'], P['st_jt']), bh=16, bw=32)
    for y in range(T):                           # bas : ombre de l'ouverture
        for x in range(T):
            if y > 22:
                cv.p[y][x] = P['st_dk'] if y < 26 else P['st_jt'] if y < 29 else P['night']
    for x in range(T):                           # claveau central
        if (left and x > 25) or (not left and x < 6):
            for y in range(0, 24):
                cv.p[y][x] = P['st_lt'] if x % 2 else P['st_md']
    return cv.p


def portail_px(left):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 51)
            cv.p[y][x] = P['night'] if y < 20 else P['night2'] if n > 0.5 else P['night']
    for x in range(T):                            # reflet bleu sur l'eau du seuil
        for y in range(24, T):
            if (x + y) % 3 == 0:
                cv.p[y][x] = P['wt_dk']
    for y in range(26, T, 3):
        for x in range(T):
            if rnd(x, y, 6) < 0.45:
                cv.p[y][x] = P['glow']
    for y in range(0, 4):
        for x in range(T):
            cv.p[y][x] = P['st_jt'] if y < 2 else P['s_dk']
    xs = range(0, 8) if left else range(24, 32)
    for y in range(T):
        for x in xs:
            e = x if left else 31 - x
            cv.p[y][x] = P['O'] if e == 0 else P['st_hi'] if e == 1 else P['st_lt'] if e < 4 else P['st_md'] if e < 6 else P['st_dk'] if e == 6 else P['st_jt']
        if y % 8 == 7:
            for x in xs:
                cv.p[y][x] = P['st_jt']
    return cv.p


@reg('sanct_portail_g')
def portail_g(name, tile):
    return portail_px(True)


@reg('sanct_portail_d')
def portail_d(name, tile):
    return portail_px(False)


@reg('sanct_pied_g', 'sanct_pied_d', 'sanct_pied_noye_a', 'sanct_pied_noye_b')
def pied(name, tile):
    cv = stone(61 + len(name))
    wl = 12 if name.endswith(('g', 'd')) and 'noye' not in name else 8
    cv = noyer(cv, wl, 62 + len(name), 0.9 if 'noye' in name else 0.35)
    for y in range(wl + 2, T, 4):                 # clapotis
        for x in range(T):
            if (x + y) % 4 == 0:
                cv.p[y][x] = P['w_md']
    if name.endswith('_g'):
        for y in range(T):
            cv.p[y][0] = P['O']
    if name.endswith('_d'):
        for y in range(T):
            cv.p[y][31] = P['O']
    return cv.p


@reg('sanct_marches')
def marches(name, tile):
    cv = Cv()
    for y in range(T):
        step = y // 8
        for x in range(T):
            base = (P['st_hi'], P['st_lt'], P['st_md'], P['st_dk'])[step]
            c = base if y % 8 else P['st_hi'] if step == 0 else P['st_lt']
            if y % 8 == 7:
                c = P['st_jt']
            c = mix(c, P['w_md'], 0.12 + step * 0.16)
            cv.p[y][x] = c
    for x in range(0, T, 5):
        cv.p[(x * 3) % 30 + 1][x] = P['glow']
    return cv.p


@reg('sanct_seuil')
def seuil(name, tile):
    cv = flags(71, size=32)
    for y in range(T):
        for x in range(T):
            d = ((x + 0.5 - 16) ** 2 + (y + 0.5 - 16) ** 2) ** 0.5
            if 8 <= d < 10 or (abs(x - 16) < 1 and abs(y - 16) < 8):
                cv.p[y][x] = P['wt_dk']
    return cv.p


def column(cv, cx, y_top, y_bot, w=11, pal=(P['st_hi'], P['st_lt'], P['st_md'], P['st_dk']), broken=True, seed=0):
    x0, x1 = cx - w // 2, cx + w // 2
    for y in range(y_top, y_bot + 1):
        for x in range(x0, x1 + 1):
            e = x - x0
            c = pal[0] if e < 2 else pal[1] if e < w // 2 else pal[2] if e < w - 2 else pal[3]
            if y > y_bot - 2:
                c = pal[3]
            cv.p[y][x] = c
        if (y - y_top) % 6 == 5:
            for x in range(x0, x1 + 1):
                cv.p[y][x] = P['st_jt']
    if broken:                                   # cassure irrégulière
        for x in range(x0, x1 + 1):
            cut = int(rnd(x, 3, seed) * 4)
            for y in range(y_top, y_top + cut):
                cv.p[y][x] = None
            cv.set(x, y_top + cut, P['st_hi'] if rnd(x, 5, seed) < 0.5 else P['st_lt'])
    return cv


@reg('sanct_colonne_a')
def colonne_a(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 11, 3, A(P['s_dk'], 255))
    column(cv, 16, 9, 29, 12, seed=3)
    cv.outline()
    return cv.p


@reg('sanct_colonne_b')
def colonne_b(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 12, 3, P['s_dk'])
    column(cv, 14, 18, 29, 12, seed=8)
    box(cv, 20, 24, 27, 29, P['st_hi'], P['st_md'], P['st_dk'])        # tambour tombé
    box(cv, 5, 26, 9, 29, P['st_lt'], P['st_md'], P['st_dk'])
    cv.outline()
    return cv.p


@reg('sanct_colonne_pied')
def colonne_pied(name, tile):
    cv = Cv()
    shadow(cv, 16, 28, 13, 3, P['s_dk'])
    ell_shade(cv, 16, 22, 12, 6.5, (P['st_hi'], P['st_lt'], P['st_md'], P['st_dk']), 9, 0.2)
    ell(cv, 16, 21, 8, 4, P['st_md'])
    ell(cv, 15, 20, 5.5, 2.7, P['st_lt'])
    box(cv, 22, 25, 27, 29, P['st_lt'], P['st_md'], P['st_dk'])
    cv.outline()
    return cv.p


@reg('sanct_pilier')
def pilier(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 12, 3, P['s_dk'])
    box(cv, 6, 4, 25, 29, P['st_hi'], P['st_md'], P['st_dk'])
    box(cv, 4, 2, 27, 7, P['st_hi'], P['st_lt'], P['st_dk'])
    box(cv, 4, 26, 27, 30, P['st_hi'], P['st_lt'], P['st_dk'])
    for y in range(9, 25, 5):
        for x in range(8, 24):
            cv.p[y][x] = P['st_jt'] if y % 10 == 9 else P['st_dk']
    for x in range(9, 13):                        # gravure du sceau
        cv.p[16][x + 4] = P['wt_dk']
    cv.p[14][16] = cv.p[15][16] = cv.p[17][16] = cv.p[18][16] = P['wt_dk']
    cv.outline()
    return cv.p


@reg('sanct_portail_haut')
def portail_haut(name, tile):
    cv = Cv()
    for x in range(2, 30, 3):
        ln = 3 + int(rnd(x, 2, 4) * 10)
        for y in range(0, ln):
            cv.p[y][x] = A(P['w_hi'], 140 if y < ln - 1 else 220)
        cv.p[ln][x] = A(P['white'], 220)
    return cv.p


@reg('sanct_gravats')
def gravats(name, tile):
    cv = Cv()
    r = random.Random(77)
    for _ in range(7):
        x, y = r.randrange(3, 26), r.randrange(10, 27)
        w, h = r.randrange(4, 8), r.randrange(3, 6)
        box(cv, x, y, x + w, y + h, P['st_hi'], P['st_md'], P['st_dk'])
    cv.outline()
    return cv.p


@reg('sanct_algues_mur')
def algues_mur(name, tile):
    cv = Cv()
    for x in range(1, 31):
        if rnd(x, 2, 12) < 0.5:
            ln = 6 + int(rnd(x, 3, 12) * 14)
            for y in range(32 - ln, 32):
                cv.p[y][x] = P['al_lt'] if (x + y) % 3 else P['al_md']
            cv.p[32 - ln][x] = P['al_hi']
    cv.outline(P['al_dk'])
    return cv.p


@reg('sanct_lanterne_eau')
def lanterne_eau(name, tile):
    cv = Cv()
    ell(cv, 15.5, 16, 12, 9, A(P['glow'], 60))
    ell(cv, 15.5, 16, 8, 6, A(P['glow'], 110))
    ell(cv, 15.5, 16, 4, 3, A(P['glow2'], 200))
    return cv.p


# ------------------------------------------------------------------ quai
def wetten(cv, seed, k=0.12):
    for y in range(T):
        for x in range(T):
            if vnoise(x, y, 4, seed) > 0.7 and cv.p[y][x] is not None:
                cv.p[y][x] = mix(cv.p[y][x], P['w_md'], 0.35)
    return cv


@reg('quai_dalle_a', 'quai_dalle_b', 'quai_dalle_c', 'quai_dalle_rune')
def dalle(name, tile):
    cv = flags({'a': 81, 'b': 82, 'c': 83, 'rune': 81}[name[len('quai_dalle_'):]])
    wetten(cv, 5)
    if name.endswith('b'):
        for k in range(14):                       # fissure
            cv.set(20 + k // 2, 3 + k, P['st_jt'])
    if name.endswith('c'):
        ell(cv, 16, 18, 7, 3, P['w_md'])
        for x in range(11, 20):
            cv.set(x, 17, P['w_hi'])
    if name.endswith('rune'):
        for y in range(T):
            for x in range(T):
                d = ((x + 0.5 - 16) ** 2 + (y + 0.5 - 16) ** 2) ** 0.5
                if 10 <= d < 11.5 or (d < 6 and abs(x - 16) < 1.2) or (d < 6 and abs(y - 16) < 1.2):
                    cv.p[y][x] = P['wt_dk']
    return cv.p


def quai_edge(sides, ring=False):
    cv = flags(84)
    wetten(cv, 6)
    for side in sides:
        for k in range(10):
            for t in range(T):
                x, y = {'b': (t, 31 - k), 'h': (t, k), 'g': (k, t), 'd': (31 - k, t)}[side]
                e = 9 - k
                cv.p[y][x] = P['st_lt'] if e == 9 else P['st_dk'] if e > 3 else P['st_jt']
                if side == 'b' and k <= 4:
                    cv.p[y][x] = P['wt_dk'] if (t + k) % 4 else P['w_md']
                if side in ('g', 'd') and k <= 2:
                    cv.p[y][x] = P['wt_dk']
        if side == 'b':
            for x in range(T):
                cv.p[21][x] = P['st_hi'] if x % 5 else P['st_lt']
                cv.p[22][x] = P['st_md']
    if ring:
        ell(cv, 16, 25, 4, 3, P['m_md'])
        ell(cv, 16, 25, 2, 1.4, P['st_dk'])
        for x in range(13, 20):
            cv.p[18][x] = P['pk_lt']
    return cv.p


REG['quai_bord_bas'] = lambda n, t: quai_edge('b')
REG['quai_bord_g'] = lambda n, t: quai_edge('g')
REG['quai_bord_d'] = lambda n, t: quai_edge('d')
REG['quai_bord_haut'] = lambda n, t: quai_edge('h')
REG['quai_coin_bg'] = lambda n, t: quai_edge('bg')
REG['quai_coin_bd'] = lambda n, t: quai_edge('bd')
REG['quai_amarre'] = lambda n, t: quai_edge('b', ring=True)


@reg('quai_jonction')
def jonction(name, tile):
    cv = Cv()
    for y in range(5, 27):
        for x in range(0, 14):
            cv.p[y][x] = P['pk_lt'] if (x // 5 + y // 11) % 2 == 0 else P['pk_md']
            if x % 6 == 5:
                cv.p[y][x] = P['pk_dk']
    for x in range(0, 14):
        cv.p[5][x] = P['b_lt']
        cv.p[26][x] = P['b_dk']
    for y in range(5, 27):                        # lisse de pierre
        cv.p[y][14] = P['st_jt']
        cv.p[y][13] = P['m_md']
    for y in (7, 24):
        for x in range(8, 13):
            cv.p[y][x] = P['m_dk']
    return cv.p


@reg('quai_bitte')
def bitte(name, tile):
    cv = Cv()
    shadow(cv, 16, 29, 9, 2.5, P['s_dk'])
    box(cv, 10, 14, 21, 28, P['st_hi'], P['st_md'], P['st_dk'])
    ell_shade(cv, 15.5, 14, 7.5, 4, (P['st_hi'], P['st_lt'], P['st_md'], P['st_dk']), 4, 0.1)
    ell(cv, 15.5, 14, 4, 2, P['st_dk'])
    for x in range(10, 22):
        cv.p[21][x] = P['m_md']
        cv.p[22][x] = P['pk_lt'] if x % 3 else P['pk_md']
    cv.outline()
    return cv.p


@reg('quai_flaque')
def flaque(name, tile):
    cv = Cv()
    ell(cv, 16, 17, 11, 6, P['w_md'])
    ell(cv, 14, 16, 8, 3.5, P['w_lt'])
    for x in range(8, 16):
        cv.set(x, 14, P['w_hi'])
    cv.outline(P['wt_dk'])
    return cv.p


@reg('quai_mousse')
def mousse(name, tile):
    cv = Cv()
    r = random.Random(33)
    for _ in range(12):
        x, y = r.randrange(2, 28), r.randrange(2, 28)
        ell(cv, x, y, r.choice((2, 3, 4)), 1.8, P['al_lt'] if r.random() < 0.5 else P['al_md'])
        cv.set(x - 1, y - 1, P['al_hi'])
    return cv.p


def plank(cv, x, y, w, h, tilt=0):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            cv.set(xx, yy + (tilt * (xx - x)) // max(1, w), P['pk_lt'] if yy == y else P['pk_md'] if yy < y + h - 1 else P['pk_dk'])


@reg('quai_caisse_brisee')
def caisse(name, tile):
    cv = Cv()
    shadow(cv, 15, 27, 12, 3, P['s_dk'])
    box(cv, 5, 12, 18, 24, P['pk_lt'], P['pk_md'], P['pk_dk'])
    for x in range(6, 18):
        cv.p[18][x] = P['pk_dk']
    cv.p[12][14] = cv.p[13][15] = None
    plank(cv, 17, 20, 11, 3, -1)
    plank(cv, 3, 25, 9, 3, 1)
    cv.outline()
    return cv.p


# ------------------------------------------------------------------ îlot et gué
@reg('ilot_herbe_a', 'ilot_herbe_b', 'ilot_herbe_c')
def ilot_herbe(name, tile):
    return cvp(GRASS[{'a': 'plain', 'b': 'tufts', 'c': 'fl_white'}[name[-1]]]).p


@reg('ilot_sable')
def ilot_sable(name, tile):
    import village_art1
    return village_art1.REG['sable_rive'](name, tile)


@reg('gue_goulet')
def goulet(name, tile):
    cv = water()
    for y in range(3, 30, 6):
        for x in range(2, 30):
            if (x * 3 + y) % 8 < 3:
                cv.p[y][x] = P['w_hi']
    for x, y in ((6, 8), (20, 20), (12, 26)):
        cv.set(x, y, P['white'])
        cv.set(x + 1, y, P['foam'])
    return cv.p


@reg('gue_pierres_a', 'gue_pierres_b')
def gue(name, tile):
    cv = Cv()
    if name.endswith('a'):
        flat_stone(cv, 8, 9, 5.5, 3.5)
        flat_stone(cv, 21, 15, 6.5, 4)
        flat_stone(cv, 10, 24, 6, 3.6)
    else:
        flat_stone(cv, 22, 8, 5.5, 3.4)
        flat_stone(cv, 10, 16, 6.5, 4)
        flat_stone(cv, 23, 25, 5.5, 3.4)
    return cv.p


@reg('ilot_coquillages', 'coquillages')
def coquillages(name, tile):
    cv = Cv()
    r = random.Random(5 if name == 'coquillages' else 6)
    for _ in range(6):
        x, y = r.randrange(3, 27), r.randrange(5, 27)
        ell(cv, x + 1.5, y + 1, 2.6, 2, P['pl_hi'] if r.random() < 0.5 else P['pink'])
        cv.set(x + 1, y + 1, P['pl_dk'])
        cv.set(x + 2, y, P['pl_dk'])
    for _ in range(5):
        x, y = r.randrange(3, 28), r.randrange(5, 28)
        ell(cv, x, y, 1.6, 1.2, P['k_lt'])
    cv.outline(P['pl_dk'])
    return cv.p


# ------------------------------------------------------------------ ambiance
def strands(seed, n):
    cv = Cv()
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.randrange(4, 28), r.randrange(6, 28)
        for k in range(r.randrange(5, 10)):
            cv.set(x + (k // 3) * (1 if r.random() < 0.5 else -1) % 2, y - k, P['al_lt'] if k % 2 else P['al_md'])
        cv.set(x, y - 9, P['al_hi'])
    return cv


@reg('algues_a', 'algues_b')
def algues(name, tile):
    cv = Cv()
    r = random.Random(10 if name.endswith('a') else 11)
    for _ in range(5):
        x, y = r.randrange(3, 27), r.randrange(4, 26)
        w = r.randrange(5, 9)
        for k in range(w):
            cv.set(x + k, y + (1 if k % 3 == 1 else 0), P['al_lt'] if k % 2 else P['al_md'])
            cv.set(x + k, y + 1 + (1 if k % 3 == 1 else 0), P['al_dk'])
        cv.set(x + 1, y - 1, P['al_hi'])
    return cv.p


@reg('eclaboussure_a', 'eclaboussure_b')
def eclaboussure(name, tile):
    cv = Cv()
    big = name.endswith('a')
    rx = 11 if big else 7
    for rr, c in ((rx, P['w_hi']), (rx - 4, P['foam'])):
        for y in range(T):
            for x in range(T):
                d = ((x + 0.5 - 16) / rr) ** 2 + ((y + 0.5 - 17) / (rr * 0.55)) ** 2
                if 0.72 < d <= 1 and (x + y) % 2 == 0 or (0.85 < d <= 1 and rr == rx):
                    cv.p[y][x] = c
    for dx, dy in ((0, -7), (-3, -9), (3, -9), (0, -11)):
        cv.set(16 + dx, 17 + dy, P['white'])
    cv.set(16, 17, P['white'])
    return cv.p


@reg('reflets_a', 'reflets_b')
def reflets(name, tile):
    cv = Cv()
    r = random.Random(12 if name.endswith('a') else 13)
    for _ in range(7):
        x, y = r.randrange(2, 27), r.randrange(2, 29)
        for k in range(r.choice((2, 3, 4))):
            cv.set(x + k, y, P['white'] if k == 0 else P['glow2'])
    return cv.p


@reg('ruine_dalle', 'ruine_dalle_b')
def ruine_dalle(name, tile):
    cv = Cv()
    box(cv, 4, 8, 27, 24, P['st_hi'], P['st_md'], P['st_dk'])
    for y in range(8, 25):
        for x in range(4, 28):
            if vnoise(x, y, 4, 9) > 0.7:
                cv.p[y][x] = P['st_lt']
    for x in range(5, 27):                         # eau qui lèche la dalle
        cv.p[22][x] = P['w_lt'] if x % 2 else P['wt_dk']
        cv.p[23][x] = P['w_md']
    for y in range(24, 27):
        for x in range(4, 28):
            if rnd(x, y, 4) < 0.35:
                cv.p[y][x] = P['w_hi'] if y == 24 else P['w_md']
    if name.endswith('_b'):
        for y in range(11, 20):
            cv.p[y][15] = cv.p[y][16] = P['wt_dk']
        for x in range(10, 22):
            cv.p[15][x] = P['wt_dk']
    cv.outline()
    return cv.p


@reg('ruine_bloc')
def ruine_bloc(name, tile):
    cv = Cv()
    shadow(cv, 16, 28, 12, 3, P['wt_dk'])
    box(cv, 5, 8, 26, 26, P['st_hi'], P['st_md'], P['st_dk'])
    box(cv, 5, 8, 26, 12, P['st_hi'], P['st_lt'], P['st_md'])
    for x in range(6, 26):
        cv.p[22][x] = P['w_lt'] if x % 2 else P['wt_dk']
        cv.p[23][x] = cv.p[24][x] = P['al_md'] if rnd(x, 2, 3) < 0.5 else P['wt_dk']
    for x in range(4, 28):
        cv.set(x, 27, P['w_hi'] if x % 2 else P['foam'])
    cv.outline()
    return cv.p


@reg('ruine_arche')
def ruine_arche(name, tile):
    cv = Cv()
    box(cv, 3, 6, 11, 27, P['st_hi'], P['st_md'], P['st_dk'])
    for y in range(6, 16):                          # départ d'arc brisé
        w = 8 - (y - 6) // 2
        for x in range(12, 12 + w):
            cv.p[y][x] = P['st_lt'] if y - 6 < 2 else P['st_md']
        cv.p[y][11 + w] = P['st_dk']
    for x in range(3, 27):
        cv.set(x, 25, P['w_lt'] if x % 2 else P['wt_dk'])
        cv.set(x, 26, P['w_md'])
    for x in range(20, 27):
        cv.set(x, 27, P['w_hi'])
    cv.outline()
    return cv.p


@reg('ecume_quai')
def ecume_quai(name, tile):
    cv = Cv()
    for x in range(T):
        y = 24 + int(vnoise(x, 0, 8, 61) * 3)
        for k in range(3):
            if rnd(x, k, 2) < 0.85:
                cv.set(x, y + k, P['foam'] if k == 0 else P['w_hi'])
    for x in range(1, T, 4):
        cv.set(x, 20, P['white'])
    return cv.p


@reg('nenuphar_fleur')
def nenuphar_fleur(name, tile):
    cv = Cv()
    ell_shade(cv, 16, 17, 10, 6.5, (P['al_hi'], P['al_lt'], P['al_md'], P['al_dk']), 5, 0.2)
    for x in range(16, 27):                         # encoche de la feuille
        cv.p[17][x] = None
    cv.set(16, 17, None)
    for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        cv.set(14 + dx, 15 + dy, P['pink'])
    cv.set(14, 15, P['fi_y'])
    cv.outline(P['al_dk'])
    return cv.p


@reg('roseaux_c')
def roseaux_c(name, tile):
    cv = Cv()
    shadow(cv, 16, 28, 11, 2.5, P['wt_dk'])
    for i, x in enumerate((6, 10, 14, 18, 22, 26)):
        top = 3 + (i * 7) % 9
        for y in range(top, 28):
            cv.set(x, y, P['g_lt'] if y % 3 else P['g_md'])
            cv.set(x + 1, y, P['g_dk'])
        if i % 2 == 0:
            for y in range(top, top + 5):
                cv.set(x, y, P['b_lt'])
                cv.set(x + 1, y, P['b_dk'])
    cv.outline()
    return cv.p


@reg('bulles')
def bulles(name, tile):
    cv = Cv()
    for cx, cy, r in ((9, 20, 2), (14, 14, 1.4), (21, 9, 2.4), (22, 22, 1.2), (6, 8, 1.2)):
        for y in range(T):
            for x in range(T):
                d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
                if r - 0.9 <= d <= r + 0.2:
                    cv.p[y][x] = P['glow2']
    return cv.p


@reg('brume_basse')
def brume_basse(name, tile):
    cv = Cv()
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 4, 91) * 0.6 + vnoise(x, y, 8, 92) * 0.4
            if n > 0.5:
                cv.p[y][x] = A(P['mist'], int(40 + (n - 0.5) * 220))
    return cv.p
