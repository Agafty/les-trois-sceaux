"""Route de l'est, falaise, grotte noire, façade et cour du château : dessin final des tuiles de `route_chateau`.

Palette : pavés gris-violet, herbe d'éclipse vert froid éteint, dalles de la cour violet-gris, falaise brun clair, grotte brun très sombre,
façade et rempart pierre violette (même famille que l'intérieur), portail mauve, niches d'Œil cerclées d'or, runes cyan, ronces noires.
Les mêmes tuiles servent de jour (étapes 0 à 2) et sous la teinte d'éclipse appliquée par le code. Lumière en haut à gauche, contour sombre
d'1 px pour les objets, pas de contour sur les sols. Chaque tuile est dessinée par REG[nom](nom, d). Réutilise chateau_pierre / chateau_objets /
chateau_art (mêmes fonctions de mur, de brèche, de chevalier...).
"""
import math
import random

from chateau_pierre import *  # noqa: F401,F403
import chateau_pierre as C
import chateau_objets as OB
import chateau_art as CA
import foret as F

REG = {}
PAL['rim_fa'] = PAL['falaise']
PAL['rim_ro'] = pal('#94807a', '#76625f', '#5c4c4d', '#3e3338', '#2a2128')
PAL['rim_re'] = pal('#b6a8d2', '#9a8cba', '#7a6c9e', '#5c5082', '#403662')
PAL['pierre_roc'] = pal('#a89a8a', '#8c8074', '#6e645c', '#524a46', '#3a3434')
PAL['stalag'] = pal('#9a8272', '#7a6458', '#5e4c44', '#463a36', '#322a2a')

FAL = Wall(PAL['cap_fa'], PAL['rim_fa'], strata(PAL['falaise'], 5), seed=15, cap_kind='crag')
ROC = Wall(PAL['cap_ro'], PAL['rim_ro'], strata(PAL['roche'], 9), seed=25, cap_kind='rock')
REM = Wall(PAL['cap_cr'], PAL['rim_re'], masonry(PAL['fac_cr'], 3), seed=35)
FC = PAL['fac_cr']
COUR = PAL['cour']


def reg(*names):
    def deco(fn):
        for n in names:
            REG[n] = fn
        return fn
    return deco


def recolor(t, mp):
    return [[(mp.get(c, c) if c is not None else None) for c in row] for row in t]


GMAP = {P['g_hi']: PAL['herbe'][HI], P['g_lt']: PAL['herbe'][LT], P['g_md']: PAL['herbe'][MD], P['g_dk']: PAL['herbe'][DK],
        P['g_dp']: PAL['herbe'][DP]}

# ------------------------------------------------------------------ 1. sols
REG['pave_a'] = lambda n, d: cobbles(PAL['pave'], 'a')
REG['pave_b'] = lambda n, d: cobbles(PAL['pave'], 'b')
REG['pave_c'] = lambda n, d: cobbles(PAL['pave'], 'c')
REG['pave_fissure'] = lambda n, d: cobbles(PAL['pave'], 'f')


def eclipse_grass(seed=1, kind='plain'):
    return recolor(F.grass(seed, kind), GMAP)


@reg('pave_herbe')
def pave_herbe(n, d):
    t = cobbles(PAL['pave'], 'a')
    g = eclipse_grass(4, 'tufts')
    for y in range(T):
        for x in range(T):
            v = vnoise(x, y, 8, 33) * 0.6 + vnoise(x, y, 4, 34) * 0.4
            if v > 0.6 + (0.1 if (x + y) % 2 else 0):
                t[y][x] = g[y][x]
            elif v > 0.55 and rnd(x, y, 3) < 0.5:
                t[y][x] = PAL['herbe'][DK]
    return t


REG['herbe_eclipse_a'] = lambda n, d: eclipse_grass(1, 'plain')
REG['herbe_eclipse_b'] = lambda n, d: eclipse_grass(2, 'tufts')


@reg('herbe_eclipse_fleurs')
def herbe_fleurs(n, d):
    t = eclipse_grass(3, 'plain')
    r = random.Random(12)
    for _ in range(6):
        x, y = r.randrange(2, 30), r.randrange(2, 30)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            put(t, x + dx, y + dy, (0x8c, 0x6e, 0xb8, 255))
        put(t, x, y, (0xd8, 0xc8, 0x78, 255))
        put(t, x, y + 2, PAL['herbe'][DK])
    return t


REG['dalle_cour_a'] = lambda n, d: slab_floor(COUR, 'a', 11)
REG['dalle_cour_b'] = lambda n, d: slab_floor(COUR, 'b', 12)
REG['dalle_cour_c'] = lambda n, d: slab_floor(COUR, 'c', 13)
REG['dalle_cour_fissuree'] = lambda n, d: slab_floor(COUR, 'f', 14, brambles=PAL['ronce'])


@reg('dalle_cour_oeil')
def dalle_oeil(n, d):
    t = slab_floor(COUR, 'a', 11)
    ring(t, 15.5, 15.5, 14, PAL['or_'][DK], 1)
    eye(t, 16, 16, PAL['or_'][LT], COUR[DP], PAL['rouge'][LT], O)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        put(t, round(15.5 + math.cos(a) * 12), round(15.5 + math.sin(a) * 12), PAL['or_'][MD])
    return t


def cave_floor(kind):
    p = PAL['grot_sol']
    t = grain(p, 71 + kind, 0.3, 0.66)
    r = random.Random(5 + kind)
    if kind == 1:                                                       # veines claires
        for _ in range(3):
            x, y = r.randrange(0, 32), r.randrange(0, 32)
            for i in range(r.randrange(8, 14)):
                x += r.choice((1, 1, 1, 0))
                y += r.choice((0, 0, 1, -1))
                put(t, x % 32, y % 32, p[HI])
                put(t, x % 32, (y + 1) % 32, p[DK])
    if kind == 2:                                                       # cailloux
        for _ in range(8):
            x, y = r.randrange(2, 29), r.randrange(2, 29)
            put(t, x, y, p[HI])
            put(t, x + 1, y, p[LT])
            put(t, x, y + 1, p[DK])
            put(t, x + 1, y + 1, p[DP])
    return t


for _i, _n in enumerate(('grotte_sol_a', 'grotte_sol_b', 'grotte_sol_cailloux')):
    REG[_n] = (lambda k: (lambda n, d: cave_floor(k)))(_i)

# transitions pavés / herbe (160 à 175) : 160 = herbe, 175 = pavés ; les 14 autres sont des repères redessinés par fondus.py
for _b in range(16):
    _n = 'paves_herbe_base' if _b == 0 else 'paves_herbe_plein' if _b == 15 else 'paves_herbe_%d%d%d%d' % ((_b >> 3) & 1, (_b >> 2) & 1, (_b >> 1) & 1, _b & 1)
    REG[_n] = (lambda b: (lambda n, d: eclipse_grass(1, 'plain') if b == 0 else cobbles(PAL['pave'], 'a')))(_b)

# ------------------------------------------------------------------ 2. murs (falaise, roche, rempart)
for _prefix, _w in (('falaise', FAL), ('grotte', ROC), ('rempart', REM)):
    for _n, _i in {'haut': 16, 'bas': 17, 'gauche': 18, 'droite': 19, 'coin_int_hg': 20, 'coin_int_hd': 21, 'coin_int_bg': 22,
                   'coin_int_bd': 23, 'coin_ext_hg': 24, 'coin_ext_hd': 25, 'coin_ext_bg': 26, 'coin_ext_bd': 27, 'plein': 28,
                   'diag_a': 29, 'diag_b': 30}.items():
        REG[f'{_prefix}_{_n}'] = (lambda w, b: (lambda n, d: w.tile(b)))(_w, WALLBITS[_i])


def cap_tile(w, extra=None):
    t = [[w.cap(x, y) for x in range(T)] for y in range(T)]
    if extra:
        extra(t)
    return t


def sommet_a(t):
    p = PAL['cap_fa']
    r = random.Random(3)
    for _ in range(5):                                                  # éclats clairs
        x, y = r.randrange(2, 28), r.randrange(2, 28)
        rect(t, x, y, x + 2, y + 1, p[LT])
        put(t, x, y, p[HI])
        rect(t, x + 1, y + 2, x + 3, y + 2, p[DP])


def sommet_b(t):
    p = PAL['ronce']
    rr = random.Random(9)
    for _ in range(4):                                                  # quelques tiges de ronces rampantes
        x, y = rr.randrange(2, 30), rr.randrange(4, 28)
        for i in range(rr.randrange(9, 16)):
            x += rr.choice((1, 1, 0, -1))
            y += rr.choice((1, 0, 0, -1))
            put(t, x % 32, y % 32, p[MD])
            put(t, x % 32, (y + 1) % 32, p[DK])
            if i % 4 == 2:
                put(t, (x + 1) % 32, (y - 1) % 32, p[HI])
                put(t, (x + 2) % 32, (y - 2) % 32, p[LT])


REG['falaise_sommet_a'] = lambda n, d: cap_tile(FAL, sommet_a)
REG['falaise_sommet_b'] = lambda n, d: cap_tile(FAL, sommet_b)
REG['grotte_plein_b'] = lambda n, d: cap_tile(ROC, lambda t: [put(t, x, y, PAL['roche'][LT]) for x in range(32) for y in range(32)
                                                              if abs(vnoise(x, y, 4, 91) - 0.5) < 0.03])
REG['rempart_plein_b'] = lambda n, d: cap_tile(REM, sommet_b)

# ------------------------------------------------------------------ 3. bouche de grotte
FA = PAL['falaise']


def dressed(kind):
    t = face_tile(FA, 17, 16)
    if kind == 'lg' or kind == 'ld':                                    # linteau : ombre vers l'ouverture (bas)
        for y in range(25, 32):
            for x in range(T):
                if rnd(x, y, 7) < (y - 24) / 7 * 0.9:
                    t[y][x] = FA[DP] if y > 28 else FA[DK]
        for x in range(T):
            t[31][x] = O
        if kind == 'lg':
            for y in range(32):
                t[y][0] = O
        else:
            for y in range(32):
                t[y][31] = O
    else:                                                               # jambage : ombre côté ouverture
        inner = range(26, 32) if kind == 'jg' else range(0, 6)
        for y in range(T):
            for x in inner:
                k = (x - 25) / 6 if kind == 'jg' else (5 - x) / 6
                if rnd(x, y, 8) < k * 0.9:
                    t[y][x] = FA[DP] if k > 0.5 else FA[DK]
        for y in range(T):
            t[y][31 if kind == 'jg' else 0] = FA[DP]
            t[y][0 if kind == 'jg' else 31] = O
    return t


REG['bouche_linteau_g'] = lambda n, d: dressed('lg')
REG['bouche_linteau_d'] = lambda n, d: dressed('ld')
REG['bouche_jambage_g'] = lambda n, d: dressed('jg')
REG['bouche_jambage_d'] = lambda n, d: dressed('jd')


def arch_piece(left):
    cv = blank()
    for y in range(0, 12):
        for x in range(32):
            xx = x if left else 31 - x
            # retombée : bande de pierre qui descend en courbe depuis le haut vers le jambage (côté extérieur)
            edge = 11 + int((xx / 31) ** 1.6 * 0) + 0
            top = 0
            bot = 5 + int(max(0, (xx - 10)) * 0.35)
            if xx >= 6 and top <= y <= bot:
                col = FA[LT]
                if y == top or y == top + 1:
                    col = FA[HI]
                if y == bot:
                    col = FA[DK]
                if y > bot - 2 and xx > 20:
                    col = FA[DK]
                cv[y][x] = col
    outline(cv, O)
    return cv


REG['bouche_arche_g'] = lambda n, d: arch_piece(True)
REG['bouche_arche_d'] = lambda n, d: arch_piece(False)


@reg('alcove_sol_rune')
def alcove_route(n, d):
    t = slab_floor(PAL['grot_sol'], 'a', 21)
    R = PAL['rune']
    ring(t, 15.5, 15.5, 8, R[DK], 1)
    ring(t, 15.5, 15.5, 5, R[DK], 1)
    for k in range(6):
        a = k * math.pi / 3
        put(t, round(15.5 + math.cos(a) * 10), round(15.5 + math.sin(a) * 10), R[MD])
    for y in range(11, 21):
        put(t, 15, y, R[MD])
    put(t, 16, 14, R[LT])
    return t


@reg('mur_rune_grave')
def mur_rune_route(n, d):
    CA.FPAL = FA
    t = CA.wall_variant('rune')
    CA.FPAL = PAL['fac_in']
    return t


# ------------------------------------------------------------------ 4. décor
REG['brasero_socle_route'] = lambda n, d: CA.brasero_socle(FC)
REG['brasero_socle_grotte'] = lambda n, d: CA.brasero_socle(PAL['roche'])


@reg('lueur_rune')
def lueur(n, d):
    """Lueur cyan : points tramés plus serrés au centre (aucune transparence partielle)."""
    t = blank()
    R = PAL['rune']
    for y in range(T):
        for x in range(T):
            dd = math.hypot(x - 15.5, y - 15.5) / 13.0
            if dd < 1:
                k = (1 - dd)
                if k > 0.7 and (x + y) % 2 == 0:
                    t[y][x] = R[HI]
                elif k > 0.4 and x % 2 == 0 and y % 2 == 0:
                    t[y][x] = R[LT]
                elif k > 0.1 and x % 3 == 0 and y % 3 == 0:
                    t[y][x] = R[MD]
    return t


REG['cailloux'] = lambda n, d: CA.rubble(PAL['pierre_roc'], 5, 7)


@reg('ronces_pied_mur')
def ronces_pied(n, d):
    cv = canvas(32, 32)
    r = random.Random(17)
    p = PAL['ronce']
    for _ in range(9):
        x0 = r.randrange(1, 31)
        y0 = 31
        x1, y1 = x0 + r.randrange(-8, 9), 31 - r.randrange(6, 15)
        line(cv, x0, y0, x1, y1, p[DK])
        line(cv, x0, y0 - 1, x1, y1 - 1, p[MD])
        put(cv, x1 + 1, y1 - 2, p[HI])
        put(cv, (x0 + x1) // 2 + 1, (y0 + y1) // 2 - 1, p[HI])
        put(cv, (x0 + x1) // 2 - 1, (y0 + y1) // 2 + 1, p[LT])
    for x in range(32):
        for y in range(27, 32):
            if rnd(x, y, 4) < 0.55:
                cv[y][x] = p[DK]
    outline(cv, p[DP])
    return cv


@reg('flaque_eclipse')
def flaque(n, d):
    t = blank()
    c0, c1, c2, c3 = (0x1c, 0x1c, 0x38, 255), (0x2a, 0x2a, 0x54, 255), (0x3e, 0x3e, 0x72, 255), (0x9a, 0x58, 0x86, 255)
    for y in range(T):
        for x in range(T):
            nx, ny = (x + 0.5 - 16) / 12.5, (y + 0.5 - 17) / 6.5
            wob = (vnoise(x, y, 8, 91) - 0.5) * 0.55
            dd = nx * nx + ny * ny + wob
            if dd <= 1:
                col = c1
                if dd > 0.78:
                    col = c0
                if ny < -0.1 and dd < 0.55 and nx < 0.3:
                    col = c2
                t[y][x] = col
    for k in range(6):                                                  # reflet de l'éclipse : petit arc orangé
        put(t, 11 + k, 14 - (1 if 1 < k < 4 else 0), c3)
    put(t, 12, 13, (0xf0, 0xb8, 0x68, 255))
    return t


@reg('herbe_haute_eclipse')
def herbe_haute(n, d):
    return recolor(F.tall_grass(), {**GMAP})


# ------------------------------------------------------------------ 5. perron
REG['perron_montant'] = lambda n, d: CA.steps(True, COUR, FC)
REG['perron_descendant'] = lambda n, d: CA.steps(False, COUR, FC)


# ------------------------------------------------------------------ 6. rochers, stalagmites
def boulder(circles, seed, pal_=None):
    p = pal_ or PAL['pierre_roc']
    cv = canvas(32, 32)
    for y in range(32):                                                 # ombre portée tramée
        for x in range(32):
            if ((x - 16) / 13) ** 2 + ((y - 27) / 3.2) ** 2 <= 1 and (x + y) % 2 == 0:
                cv[y][x] = PAL['cap_ro'][DP]
    c2 = Cv()
    F.mass(c2, circles, (p[HI], p[LT], p[MD], p[DK]), seed, 0.35)
    paste(cv, c2.p)
    r = random.Random(seed)
    for _ in range(3):                                                  # fissures
        x0, y0 = r.randrange(8, 24), r.randrange(10, 22)
        line(cv, x0, y0, x0 + r.randrange(-3, 4), y0 + r.randrange(2, 5), p[DP])
    outline(cv, O)
    return cv


REG['rocher_a'] = lambda n, d: boulder([(16, 19, 12, 9), (9, 22, 7, 5)], 60)
REG['rocher_b'] = lambda n, d: boulder([(11, 20, 9, 7), (22, 18, 8, 9), (17, 13, 7, 7)], 61)


def stalagmite(heights, seed):
    p = PAL['stalag']
    cv = canvas(32, 32)
    for y in range(32):
        for x in range(32):
            if ((x - 16) / 12) ** 2 + ((y - 27) / 3.2) ** 2 <= 1 and (x + y) % 2 == 0:
                cv[y][x] = PAL['roche'][DP]
    for (cx, h, w) in heights:
        base = 28
        for y in range(base - h, base + 1):
            k = (y - (base - h)) / h
            hw = w * k ** 0.85
            for x in range(int(cx - hw), int(cx + hw) + 1):
                u = (x - cx) / max(hw, 0.5)
                col = p[MD]
                if u < -0.35:
                    col = p[HI] if k < 0.6 and u < -0.6 else p[LT]
                elif u > 0.45:
                    col = p[DK]
                if rnd(x, y, seed) < 0.1:
                    col = p[DK] if col != p[DK] else p[LT]
                cv[y][x] = col
    outline(cv, O)
    return cv


REG['stalagmite_a'] = lambda n, d: stalagmite([(16, 17, 8), (9, 9, 4), (23, 8, 4)], 71)
REG['stalagmite_b'] = lambda n, d: stalagmite([(15, 26, 9), (24, 14, 5), (7, 11, 4)], 72)

# ------------------------------------------------------------------ 7. murs fissurés (poterne haut ; autres réservés)
FP = dict(zip(('haut', 'bas', 'gauche', 'droite'), ((1, 1, 0, 0), (0, 0, 1, 1), (1, 0, 1, 0), (0, 1, 0, 1))))


def facade_pied():
    t = face_tile(FC, 3)
    for y in range(T):
        for x in range(T):
            v = vnoise(x, y, 8, 55)
            if y > 20 + (1 - v) * 7 and v > 0.4:                       # ronces qui montent du pied
                a = abs(vnoise(x, y, 16, 56) - 0.5)
                if a < 0.2 or y > 27:
                    t[y][x] = PAL['ronce'][DK] if a > 0.08 else PAL['ronce'][MD]
                    if rnd(x, y, 3) < 0.08:
                        t[y][x] = PAL['ronce'][HI]
    for _ in range(10):
        x, y = int(rnd(_, 1, 6) * 30) + 1, 21 + int(rnd(_, 2, 7) * 9)
        if t[y][x] in (PAL['ronce'][DK], PAL['ronce'][MD]):
            put(t, x + 1, y - 1, PAL['ronce'][LT])
    return t


_POT = {}


def pied():
    if 'p' not in _POT:
        _POT['p'] = facade_pied()
    return copy(_POT['p'])


REG['poterne_fissuree'] = lambda n, d: CA.fissure(pied(), 'haut', FC[HI], 3)
REG['poterne_ouverte'] = lambda n, d: CA.breach(pied(), 'haut', FC)
for _k, _s in enumerate(('bas', 'gauche', 'droite')):
    REG[f'mur_fissure_{_s}'] = (lambda s, k: (lambda n, d: CA.fissure(REM.tile(FP[s]), s, FC[HI], 5 + k)))(_s, _k)
    REG[f'mur_fissure_{_s}_ouvert'] = (lambda s: (lambda n, d: CA.breach(REM.tile(FP[s]), s, FC, COUR)))(_s)

# ------------------------------------------------------------------ 10. façade
def crenel(merlon):
    t = [[None] * T for _ in range(T)]
    walk = PAL['cap_cr']
    for y in range(T):
        for x in range(T):
            n = vnoise(x, y, 8, 45)
            t[y][x] = walk[LT] if n > 0.72 else walk[DK] if n < 0.25 else walk[MD]
    f = full_face(FC, 3)
    top = 6 if merlon else 20
    for y in range(top, T):
        for x in range(T):
            t[y][x] = f(x, y - top + (0 if merlon else 0) + (0 if (y - top) >= 0 else 0))
    for x in range(T):
        t[top][x] = FC[HI]
        t[top + 1][x] = FC[LT]
    if merlon:
        for y in range(top, T):
            t[y][0] = O
            t[y][31] = O
        for x in range(T):
            t[top - 1][x] = O
            t[top - 1][x] = O
        for y in range(top + 2, T):
            t[y][1] = FC[HI] if y % 3 else FC[LT]
            t[y][30] = FC[DK]
    else:
        for x in range(T):
            t[top - 1][x] = O
        for y in range(0, top):                                          # ombre des merlons voisins sur le chemin de ronde
            for x in (0, 1, 2, 29, 30, 31):
                if rnd(x, y, 3) < 0.6:
                    t[y][x] = PAL['cap_cr'][DP]
    return t


REG['facade_creneau_a'] = lambda n, d: crenel(True)
REG['facade_creneau_b'] = lambda n, d: crenel(False)
REG['facade_mur_a'] = lambda n, d: face_tile(FC, 3)


@reg('facade_mur_b')
def facade_fenetre(n, d):
    t = face_tile(FC, 3)
    for y in range(6, 27):                                              # meurtrière : encadrement et fond sombre
        for x in range(13, 19):
            t[y][x] = FC[DK] if x in (13, 18) or y in (6, 26) else PAL['vide'][DK]
    for y in range(8, 25):
        t[y][15] = PAL['vide'][DP]
        t[y][16] = PAL['vide'][DP]
    for y in range(5, 28):
        t[y][12] = FC[HI] if y < 14 else FC[LT]
        t[y][19] = FC[DP]
    for x in range(12, 20):
        t[5][x] = FC[HI]
        t[27][x] = FC[DP]
    return t


REG['facade_pied'] = lambda n, d: pied()


def with_pal(fp, fn, *a):
    old = CA.FPAL
    CA.FPAL = fp
    try:
        return fn(*a)
    finally:
        CA.FPAL = old


REG['facade_niche_oeil'] = lambda n, d: with_pal(FC, CA.wall_variant, 'niche_oeil')
REG['facade_niche_vide'] = lambda n, d: with_pal(FC, CA.wall_variant, 'niche')
REG['facade_mur_ronces'] = lambda n, d: with_pal(FC, CA.wall_variant, 'ronces')
REG['facade_blason'] = lambda n, d: with_pal(FC, CA.wall_variant, 'blason')


@reg('facade_coin_tour')
def coin_tour(n, d):
    t = face_tile(FC, 3)
    for y in range(T):
        for x in range(T):
            if x >= 20:
                k = (x - 19) / 12
                if rnd(x, y, 9) < k * 0.9 or x > 27:
                    t[y][x] = FC[DK] if x < 28 else FC[DP]
        t[y][31] = O
        t[y][0] = FC[HI]
    for y in range(T):                                                   # arêtes de pierres d'angle (harpage)
        if (y // 8) % 2 == 0:
            for x in range(18, 22):
                t[y][x] = FC[LT] if y % 8 else FC[HI]
    return t


# ------------------------------------------------------------------ 11. portail scellé 2×3
def portail():
    W, H = 64, 96
    cv = canvas(W, H)
    f = full_face(FC, 3)
    for y in range(H):
        for x in range(W):
            cv[y][x] = f(x % 32, y)
    cx = 32
    PI = PAL['cap_cr']
    ME = PAL['metal']

    def hw(y, r):
        """demi-largeur de l'arc brisé à la hauteur y (haut de l'arc en y = 6)."""
        if y >= 36:
            return r
        k = (36 - y) / 30.0
        return r * math.sqrt(max(0.0, 1 - k * k)) if k < 1 else 0

    for y in range(6, H):                                               # cadre de pierre
        h1 = hw(y, 28)
        for x in range(int(cx - h1), int(cx + h1) + 1):
            if abs(x - cx + 0.5) <= h1:
                u = (x - (cx - h1)) / max(1, 2 * h1)
                col = FC[HI] if x - (cx - h1) < 2 else FC[LT] if u < 0.4 else FC[MD] if u < 0.8 else FC[DK]
                if y % 6 == 0:
                    col = FC[DP]
                cv[y][x] = col
    for y in range(11, H):                                              # vantaux sombres
        h2 = hw(y, 22) if y > 11 else 0
        h2 = hw(y + 5, 23) if y < 36 else 22
        for x in range(int(cx - h2), int(cx + h2) + 1):
            if abs(x - cx + 0.5) <= h2:
                col = PI[MD] if (x // 5) % 2 else PI[DK]
                if (x - cx) % 11 == 0:
                    col = PI[DP]
                if rnd(x, y, 5) < 0.06:
                    col = PI[LT]
                cv[y][x] = col
    for x in range(cx - 1, cx + 1):                                     # joint central
        for y in range(11, H):
            cv[y][x] = O
    for yb in (36, 58, 78):                                             # bandes de fer
        for x in range(10, 54):
            if cv[yb][x] is not None and cv[yb][x] not in (FC[LT], FC[HI]):
                cv[yb][x] = ME[MD]
                cv[yb + 1][x] = ME[DK]
                cv[yb - 1][x] = ME[LT] if x < 32 else ME[MD]
        for x in range(12, 53, 6):
            put(cv, x, yb, ME[HI])
    # Œil de Morvath, grand, doré, au milieu
    ey = 48
    for y in range(ey - 12, ey + 13):
        for x in range(cx - 20, cx + 20):
            nx, ny = (x + 0.5 - cx) / 19.0, (y + 0.5 - ey) / 11.0
            if abs(ny) < 1 - nx * nx * 0.95 and nx * nx + ny * ny * 0.4 <= 1.0 and abs(ny) <= (1 - nx * nx) ** 0.9 * 1.0:
                col = PAL['or_'][MD]
                if abs(abs(ny) - (1 - nx * nx) ** 0.9) < 0.14:
                    col = PAL['or_'][HI] if ny < 0 else PAL['or_'][DK]
                cv[y][x] = col
    for y in range(ey - 8, ey + 9):                                     # iris rouge, pupille noire
        for x in range(cx - 8, cx + 8):
            dd = ((x + 0.5 - cx) / 8.0) ** 2 + ((y + 0.5 - ey) / 8.0) ** 2
            if dd <= 1:
                cv[y][x] = PAL['rouge'][LT] if dd > 0.35 else PAL['rouge'][DP]
                if dd > 0.85:
                    cv[y][x] = PAL['rouge'][DK]
    for y in range(ey - 6, ey + 7):
        for x in (cx - 1, cx):
            cv[y][x] = O
    put(cv, cx - 5, ey - 4, PAL['rouge'][HI])
    for k in range(9):                                                  # rayons
        a = math.radians(-160 + k * 40)
        x0, y0 = cx + math.cos(a) * 21, ey + math.sin(a) * 13
        x1, y1 = cx + math.cos(a) * 26, ey + math.sin(a) * 17
        line(cv, round(x0), round(y0), round(x1), round(y1), PAL['or_'][MD])
    # ronces et chaînes qui scellent le bas
    for y in range(80, H):
        for x in range(8, 56):
            v = vnoise(x, y, 8, 77)
            if y > 84 + (1 - v) * 6 or (v > 0.62 and y > 80):
                a = abs(vnoise(x, y, 16, 78) - 0.5)
                if a < 0.22 or y > 91:
                    cv[y][x] = PAL['ronce'][DK] if a > 0.09 else PAL['ronce'][MD]
                    if rnd(x, y, 3) < 0.07:
                        cv[y][x] = PAL['ronce'][HI]
    for ch in ((14, 62, 30, 88), (50, 62, 34, 88)):                     # chaînes en croix
        x0, y0, x1, y1 = ch
        n = 14
        for i in range(n + 1):
            x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
            col = ME[HI] if i % 2 == 0 else ME[DK]
            rect(cv, x, y, x + 1, y + 1, col)
            put(cv, x - 1, y, O) if i % 2 == 0 else None
    # seuil
    for x in range(4, 60):
        for y in range(91, 96):
            cv[y][x] = FC[HI] if y == 91 else FC[LT] if y == 92 else FC[DK] if y < 95 else O
    # contour
    for y in range(6, H):
        h1 = hw(y, 28)
        xa, xb = int(cx - h1) - 1, int(cx + h1)
        for xx in (xa, xb + 1):
            if 0 <= xx < W and cv[y][xx] not in (None,):
                cv[y][xx] = O
    for x in range(W):
        cv[0][x] = cv[0][x]
    return cv


_POR = portail()
for _i, _n in enumerate(('portail_hg', 'portail_hd', 'portail_mg', 'portail_md', 'portail_bg', 'portail_bd')):
    REG[_n] = (lambda c, r: (lambda n, d: slice_(_POR, c, r)))(_i % 2, _i // 2)


# ------------------------------------------------------------------ 13. poterne : fermée, arche, seuil
@reg('poterne_fermee')
def poterne_fermee(n, d):
    t = pied()
    for y in range(10, 32):
        h = 10 if y > 19 else math.sqrt(max(0, 1 - ((19 - y) / 9.0) ** 2)) * 10
        for x in range(int(16 - h), int(16 + h) + 1):
            if abs(x - 15.5) <= h:
                col = FC[LT]
                if (y // 5) % 2 == 0 and (x + 3) % 8 == 0 or (y // 5) % 2 == 1 and x % 8 == 0 or y % 5 == 0:
                    col = FC[DP]
                elif y % 5 == 1:
                    col = FC[HI]
                t[y][x] = col
    for y in range(10, 32):
        h = 10 if y > 19 else math.sqrt(max(0, 1 - ((19 - y) / 9.0) ** 2)) * 10
        for xx in (int(15.5 - h) - 1, int(15.5 + h) + 1):
            if 0 <= xx < 32:
                t[y][xx] = O
    for x in range(8, 24):
        h = int(round(math.sqrt(max(0, 1 - ((x - 15.5) / 10.5) ** 2)) * 9))
        put(t, x, 10 + (9 - h), O) if 10 + (9 - h) < 20 else None
    return t


@reg('poterne_arche')
def poterne_arche(n, d):
    cv = blank()
    for y in range(0, 24):
        for x in range(32):
            dx, dy = (x - 15.5) / 11.0, (y - 12.0) / 11.0
            rr = dx * dx + dy * dy
            inside_arch = rr <= 1.0 and y <= 12
            outer = ((x - 15.5) / 14.5) ** 2 + ((y - 12.0) / 14.5) ** 2
            if y <= 12 and outer <= 1.0 and not inside_arch:
                col = FC[LT]
                ang = math.atan2(y - 12, x - 15.5)
                if int((ang + math.pi) * 6) % 2 == 0:
                    col = FC[MD]
                if outer > 0.82:
                    col = FC[HI] if x < 16 else FC[DK]
                cv[y][x] = col
            elif y > 12 and (abs(x - 15.5) > 11 and abs(x - 15.5) <= 14.5):
                cv[y][x] = FC[HI] if x < 16 else FC[DK]
                if y > 12 and (x - 3) % 11 == 0:
                    cv[y][x] = FC[DP]
    outline(cv, O)
    return cv


@reg('poterne_seuil')
def poterne_seuil(n, d):
    t = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            k = 1 - y / 31
            col = PAL['vide'][MD] if k < 0.4 else PAL['vide'][LT] if k < 0.7 else PAL['cap_cr'][DK]
            if rnd(x, y, 6) < 0.18:
                col = PAL['vide'][DK]
            t[y][x] = col
    for x in range(T):
        t[28][x] = FC[DK]
        t[29][x] = FC[LT] if x % 7 else FC[HI]
        t[30][x] = FC[MD]
        t[31][x] = FC[DK]
    return t


# ------------------------------------------------------------------ 14. statues, pilier, bannières
_KA, _KB = OB.knight('a', False), OB.knight('b', False)
REG['statue_chevalier_base'] = lambda n, d: slice_(_KA, 0, 1)
REG['statue_chevalier_haut'] = lambda n, d: slice_(_KA, 0, 0)
REG['statue_chevalier_b_base'] = lambda n, d: slice_(_KB, 0, 1)
REG['statue_chevalier_b_haut'] = lambda n, d: slice_(_KB, 0, 0)
REG['pilier_cour'] = lambda n, d: OB.column_brisee()
REG['banniere_morvath'] = lambda n, d: OB.banner('a')
REG['banniere_dechiree'] = lambda n, d: OB.banner('b')
