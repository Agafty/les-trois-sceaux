"""Tileset du lac (overworld : cascade, Sanctuaire Englouti, quai, îlot et gué) — Les Trois Sceaux.

Usage : python tools/sprites/lac.py          -> DESSIN FINAL (lac.png, lac_numeros.png, _plan.md, .tsx)
        python tools/sprites/lac.py --plan   -> PLAN (aplats par famille et numéros)
Le catalogue (numéros, collisions) est identique dans les deux cas ; le dessin est dans lac_art.py.
Ce tileset ne contient QUE ce que `village` / `foret` / `montagne` n'ont pas : l'eau peu profonde (village 63-64 + terrain Rive),
l'eau profonde (village 65-79, terrain Lac profond), le ponton (312-317), les roseaux, l'éboulis et les falaises restent ceux de `village`.
RÈGLE : on ne déplace jamais une tuile ; on ajoute dans les lignes de réserve (à la fin).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import *  # noqa: E402,F401,F403
import tsplan  # noqa: E402

tsplan.CATS.update(
    roche='#7a8498', cascade='#a8d0f0', voile='#c8e4f8', bassin='#5aa0d8', alcove='#6a7a90', fond='#2a2438',
    sanct='#8a8aa0', sanct2='#6a7088', portail='#e8782c', algue='#3a7a5a', quai='#a8a4b0', quai2='#8a8898',
    ilot='#7aaa5a', sable='#d8c890', gue='#9aa0a8', deco='#68b0c8', ruine='#7a7a90')

S = Sheet('lac', 8, 'Le lac (overworld : cascade, Sanctuaire Englouti à demi noyé, quai, îlot et gué)',
          ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px. Palette : bleus-verts froids de l\'eau, pierre gris-violet du Sanctuaire, '
           'brume. Dans le plan, la couleur indique la famille ; une zone plus sombre dans une tuile = zone solide.',
           '- **Ce tileset ne contient que ce qui manque.** À utiliser avec `village` (firstgid 1), `foret` (401) et `lac` (le troisième). '
           'Eau peu profonde : `village` 63 `rive_plein` et 64 `lac_base` (Sol), bords `rive_*` 48-62 (terrain `Rive`). Eau profonde : `village` 65-79 '
           '(terrain `Lac profond`, sur `Murs`, solide). Ponton : `village` 312-317 (Decor) + pilotis 318, bitte 319, roseaux 324-325, nénuphars 326, '
           'rocher dans l\'eau 327. Éboulis : `village` 138/139. Falaises : `village` 120-132. Buissons coupables : `village` 300, `foret` 96-99.',
           '- **Aucun terrain (Wang) nouveau** : l\'autotiling de l\'eau est celui de `village` (`Rive`, `Lac profond`). Les tuiles de ce tileset se posent à la main '
           '(ou avec le pinceau « tampon » pour les assemblages).',
           '- **Animations** (déjà dans le `.tsx`, 250 ms par image) : `cascade_chute_a` -> `_b` et `cascade_voile_a` -> `_b`. Peindre uniquement les tuiles `_a`.',
           '- **Rideau de cascade** : `cascade_voile_*` sont semi-transparentes, sur le calque `Dessus`, sans collision, au-dessus de cases libres de l\'alcôve '
           '(`alcove_sol`) : Brann passe dessous. Peindre le fond (`alcove_fond` en haut, `alcove_sol` en bas) sur `Murs` / `Sol`, puis le voile sur `Dessus`.',
           '- **Portail du Sanctuaire** : la `Sortie` (64×32) se pose sur les deux cases `sanct_portail_g` / `sanct_portail_d` (rangée du bas de la façade).'],
          ['`Sol` : eau (village), dalles du quai, herbe d\'îlot, sol d\'alcôve, bassin, marches immergées',
           '`Decor` : sans collision (ponton, pierres du gué, algues, éclaboussures, ruines basses, jonction ponton-quai)',
           '`Murs` : tout ce qui bloque (cascade et falaise, façade du Sanctuaire, colonnes, bords de quai, eau profonde de village)',
           '`Objets` : Sortie, Spawn, Porte (rocher), Interrupteur, Ennemi, StatueCorbeau… (objets Tiled, pas des tuiles)',
           '`Dessus` : rideau de cascade (semi-transparent), haut du portail'])
S.reserve = 4
ANIM = {}   # id -> [(tileid, ms), ...], rempli plus bas


def M(nom, role, coll, cat, **k):
    return (nom, role, 'Murs', coll, cat, k)


def D(nom, role, cat, **k):
    return (nom, role, 'Decor', None, cat, k)


def SO(nom, role, cat, **k):
    return (nom, role, 'Sol', None, cat, k)


def U(nom, role, cat, coll=None, **k):
    return (nom, role, 'Dessus', coll, cat, k)


# ---------------------------------------------------------------- 1. cascade et alcôve (0-15)
S.group('Cascade et alcôve (le secret d\'observation : quart de cœur derrière le rideau)',
        'La cascade tombe dans la falaise (colonnes 35-36 du lac) : `cascade_haut` en haut de la falaise, `cascade_chute_a` en dessous, '
        '`cascade_bassin` au pied (ruisseau d\'eau peu profonde). L\'alcôve (2×2) est creusée dans la falaise : `alcove_fond` (mur du fond, solide) '
        'et `alcove_sol` (sol de roche mouillée) ; le rideau `cascade_voile_*` passe devant, sur `Dessus`. '
        'Les jambages `cascade_jambage_g` / `_d` encadrent la chute avec la falaise de `village`.')
S.line([M('cascade_haut', 'CASCADE, haut : roche et eau qui déborde de la crête (solide)', FULL, 'cascade'),
        M('cascade_chute_a', 'CASCADE, chute sur la falaise, image A (à répéter ; animée A->B)', FULL, 'cascade'),
        M('cascade_chute_b', 'CASCADE, chute sur la falaise, image B (seconde image de l\'animation)', FULL, 'cascade'),
        M('cascade_jambage_g', 'Jambage de roche à gauche de la chute (solide)', FULL, 'roche'),
        M('cascade_jambage_d', 'Jambage de roche à droite de la chute (solide)', FULL, 'roche'),
        M('alcove_fond', 'Alcôve : mur du fond, roche sombre avec trouée (solide, sous le rideau)', FULL, 'fond'),
        SO('alcove_sol', 'Alcôve : sol de roche mouillée (libre, sous le rideau)', 'alcove'),
        SO('cascade_bassin', 'Bassin au pied de la cascade : eau peu profonde avec écume (libre)', 'bassin')])
S.line([U('cascade_voile_a', 'RIDEAU d\'eau semi-transparent, image A (Dessus, sans collision ; animé A->B)', 'voile'),
        U('cascade_voile_b', 'RIDEAU d\'eau semi-transparent, image B (seconde image de l\'animation)', 'voile'),
        U('cascade_voile_pied', 'Pied du rideau : écume semi-transparente (Dessus, sans collision)', 'voile'),
        D('alcove_lueur', 'Scintillement au sol de l\'alcôve (sous le quart de cœur)', 'voile', col='#f0f0a0'),
        D('cascade_ecume', 'Écume et éclaboussures au pied de la chute (à poser sur le bassin)', 'cascade', col='#d4e0f0'),
        D('ruisseau_pierres', 'Pierres plates dans le ruisseau de la cascade', 'gue'),
        None, None])
ANIM[S.id('cascade_chute_a')] = [(S.id('cascade_chute_a'), 250), (S.id('cascade_chute_b'), 250)]
ANIM[S.id('cascade_voile_a')] = [(S.id('cascade_voile_a'), 250), (S.id('cascade_voile_b'), 250)]
S.assemblage('Cascade (colonne de 1 case de large, 3 de haut)', [['cascade_haut'], ['cascade_chute_a'], ['cascade_bassin']],
             'Murs, Murs, Sol', 'chute sur 2 cases ou plus : répéter cascade_chute_a ; jambages de chaque côté')
S.assemblage('Alcôve derrière le rideau (2×2)', [['alcove_fond', 'alcove_fond'], ['alcove_sol', 'alcove_sol']],
             'Murs (rangée du haut), Sol (rangée du bas)', 'rideau cascade_voile_a sur Dessus au-dessus des 4 cases, cascade_voile_pied sur la rangée du bas')

# ---------------------------------------------------------------- 2. façade du Sanctuaire (16-39)
S.group('Façade du Sanctuaire Englouti (6×3, portail de 2 cases, mur à demi noyé)',
        'Rangée du haut = frise et fronton ; rangée du milieu = pilastres, murs et linteau ; rangée du bas = soubassement dans l\'eau et PORTAIL '
        '(`sanct_portail_g` / `_d`, ouvert : seuls les montants sont solides ; la `Sortie` 64×32 se pose dessus). Toute la façade est sur `Murs`.')
S.line([M('sanct_frise_g', 'Frise, coin gauche (solide)', FULL, 'sanct'), M('sanct_frise_a', 'Frise, pierre sculptée, variante A (solide)', FULL, 'sanct'),
        M('sanct_fronton_g', 'Fronton au-dessus du portail, moitié gauche (solide)', FULL, 'sanct2'),
        M('sanct_fronton_d', 'Fronton au-dessus du portail, moitié droite (solide)', FULL, 'sanct2'),
        M('sanct_frise_b', 'Frise, pierre sculptée, variante B (solide)', FULL, 'sanct'), M('sanct_frise_d', 'Frise, coin droit (solide)', FULL, 'sanct'),
        None, None])
S.line([M('sanct_mur_g', 'Mur, coin gauche avec pilastre (solide)', FULL, 'sanct'),
        M('sanct_mur_noye_a', 'Mur à demi noyé, algues, variante A (solide)', FULL, 'algue'),
        M('sanct_linteau_g', 'Linteau du portail, moitié gauche (solide)', FULL, 'sanct2'),
        M('sanct_linteau_d', 'Linteau du portail, moitié droite (solide)', FULL, 'sanct2'),
        M('sanct_mur_noye_b', 'Mur à demi noyé, algues, variante B (solide)', FULL, 'algue'),
        M('sanct_mur_d', 'Mur, coin droit avec pilastre (solide)', FULL, 'sanct'),
        M('sanct_pilastre', 'Pilastre intermédiaire (solide)', FULL, 'sanct'), M('sanct_pilier', 'Pilier massif isolé (solide)', OBJ, 'sanct2')])
S.line([M('sanct_pied_g', 'Soubassement dans l\'eau, coin gauche (solide)', FULL, 'sanct2'),
        M('sanct_pied_noye_a', 'Soubassement noyé, variante A (solide)', FULL, 'algue'),
        M('sanct_portail_g', 'PORTAIL, case gauche (Sortie dessus) : montant solide, centre libre', [(0, 0, 8, 32)], 'portail'),
        M('sanct_portail_d', 'PORTAIL, case droite (Sortie dessus) : montant solide, centre libre', [(24, 0, 8, 32)], 'portail'),
        M('sanct_pied_noye_b', 'Soubassement noyé, variante B (solide)', FULL, 'algue'),
        M('sanct_pied_d', 'Soubassement dans l\'eau, coin droit (solide)', FULL, 'sanct2'),
        SO('sanct_marches', 'Marches immergées devant le portail (libre)', 'sanct'), SO('sanct_seuil', 'Seuil de pierre du portail (libre)', 'sanct')])
S.line([M('sanct_colonne_a', 'Colonne brisée, variante A (solide)', OBJ, 'sanct'), M('sanct_colonne_b', 'Colonne brisée, variante B (solide)', OBJ, 'sanct'),
        M('sanct_colonne_pied', 'Base de colonne écroulée (solide)', BASE, 'ruine'),
        U('sanct_portail_haut', 'Haut du portail : rideau d\'eau qui goutte (Dessus, facultatif)', 'voile', col='#a0c0e0'),
        D('sanct_gravats', 'Gravats de la façade au pied du mur (décor)', 'ruine'),
        D('sanct_algues_mur', 'Algues accrochées au bas d\'un mur (décor)', 'algue'),
        D('sanct_lanterne_eau', 'Lueur bleue dans l\'eau, devant le portail (décor)', 'voile', col='#80d0f0'),
        None])
S.assemblage('Façade du Sanctuaire Englouti (6×3, portail aux colonnes 2-3)',
             [['sanct_frise_g', 'sanct_frise_a', 'sanct_fronton_g', 'sanct_fronton_d', 'sanct_frise_b', 'sanct_frise_d'],
              ['sanct_mur_g', 'sanct_mur_noye_a', 'sanct_linteau_g', 'sanct_linteau_d', 'sanct_mur_noye_b', 'sanct_mur_d'],
              ['sanct_pied_g', 'sanct_pied_noye_a', 'sanct_portail_g', 'sanct_portail_d', 'sanct_pied_noye_b', 'sanct_pied_d']],
             'Murs (tout) ; Sortie sur les 2 cases portail', 'pour une façade plus large, répéter frise_a / mur_noye_a / pied_noye_a ou intercaler sanct_pilastre')

# ---------------------------------------------------------------- 3. quai (40-55)
S.group('Quai de pierre devant le Sanctuaire',
        'Dalles mouillées (Sol), bords de quai (Murs, partiels : la partie extérieure est solide), '
        'bitte et jonction avec le ponton de `village` (312-317).')
S.line([SO('quai_dalle_a', 'Dalle de quai mouillée, variante A', 'quai'), SO('quai_dalle_b', 'Dalle de quai, variante B (joint fissuré)', 'quai'),
        SO('quai_dalle_c', 'Dalle de quai, variante C (flaque)', 'quai'), SO('quai_dalle_rune', 'Dalle gravée d\'un sceau effacé (devant le portail)', 'quai', col='#b0acc0'),
        M('quai_bord_bas', 'Bord de quai, côté sud (moitié basse solide)', [(0, 22, 32, 10)], 'quai2'),
        M('quai_bord_g', 'Bord de quai, côté ouest', [(0, 0, 10, 32)], 'quai2'),
        M('quai_bord_d', 'Bord de quai, côté est', [(22, 0, 10, 32)], 'quai2'),
        M('quai_bord_haut', 'Bord de quai, côté nord (moitié haute solide)', [(0, 0, 32, 10)], 'quai2')])
S.line([M('quai_coin_bg', 'Coin de quai, bas-gauche', [(0, 22, 32, 10), (0, 0, 10, 22)], 'quai2'),
        M('quai_coin_bd', 'Coin de quai, bas-droite', [(0, 22, 32, 10), (22, 0, 10, 22)], 'quai2'),
        D('quai_jonction', 'Jonction ponton-quai : planches qui finissent sur la dalle (à droite du dernier ponton_h)', 'quai2'),
        M('quai_bitte', 'Bitte d\'amarrage en pierre (solide)', POST, 'quai2'),
        M('quai_amarre', 'Anneau et corde d\'amarrage (solide, bord de quai)', [(0, 22, 32, 10)], 'quai2'),
        D('quai_flaque', 'Flaque sur le quai (décor)', 'bassin', col='#8ac0e0'), D('quai_mousse', 'Mousse et algues séchées sur une dalle (décor)', 'algue'),
        D('quai_caisse_brisee', 'Planches et caisse brisée échouées (décor)', 'quai2', col='#8a6a44')])

# ---------------------------------------------------------------- 4. îlot et gué (56-63)
S.group('Îlot et gué (quart de cœur à l\'arc)',
        'Terre de l\'îlot (Sol) : à poser sur les 3 cases entourées d\'eau profonde (`village` 65-79, qui font le rivage). '
        'Le rocher du gué est une `Porte` (`apparence`=`rocher`, image `art/puzzles/porte_rocher_eau.png`), pas une tuile. '
        '`gue_goulet` marque le goulet d\'eau peu profonde qui mène à la cible.')
S.line([SO('ilot_herbe_a', 'Herbe d\'îlot, variante A', 'ilot'), SO('ilot_herbe_b', 'Herbe d\'îlot, variante B', 'ilot'),
        SO('ilot_herbe_c', 'Herbe d\'îlot, touffes et fleurs', 'ilot'), SO('ilot_sable', 'Sable de l\'îlot', 'sable'),
        D('gue_pierres_a', 'Pierres plates du gué, variante A (sur eau peu profonde)', 'gue'),
        D('gue_pierres_b', 'Pierres plates du gué, variante B', 'gue'),
        SO('gue_goulet', 'Goulet d\'eau peu profonde, eau calme avec reflets (libre)', 'bassin'),
        D('ilot_coquillages', 'Coquillages et galets sur l\'îlot (décor)', 'sable')])

# ---------------------------------------------------------------- 5. ambiance (64-79)
S.group('Ambiance de l\'eau et ruines immergées', 'Décor sans collision à semer sur l\'eau (sauf `ruine_bloc` et `ruine_arche`, solides).')
S.line([D('algues_a', 'Algues flottantes, variante A', 'algue'), D('algues_b', 'Algues flottantes, variante B', 'algue'),
        D('eclaboussure_a', 'Éclaboussures (sillage d\'un Têtard), variante A', 'deco'), D('eclaboussure_b', 'Éclaboussures, variante B', 'deco'),
        D('reflets_a', 'Reflets brillants sur l\'eau, variante A', 'voile', col='#d8f0ff'), D('reflets_b', 'Reflets brillants, variante B', 'voile', col='#d8f0ff'),
        D('ruine_dalle', 'Dalle ancienne affleurant dans l\'eau peu profonde', 'ruine'), D('ruine_dalle_b', 'Dalle ancienne gravée, immergée', 'ruine')])
S.line([M('ruine_bloc', 'Bloc de pierre taillé qui dépasse de l\'eau (solide)', OBJ, 'ruine'),
        M('ruine_arche', 'Morceau d\'arche immergée (solide)', OBJ, 'ruine'),
        D('coquillages', 'Coquillages sur la rive', 'sable'), D('ecume_quai', 'Écume le long d\'un quai ou d\'un mur', 'cascade', col='#d4e0f0'),
        D('nenuphar_fleur', 'Nénuphar en fleur', 'ilot'), D('roseaux_c', 'Roseaux, variante C', 'algue'),
        D('bulles', 'Bulles à la surface', 'voile', col='#c8ecff'), D('brume_basse', 'Voile de brume basse sur l\'eau (décor, semi-transparent)', 'voile', col='#e8f0f8')])

S.notes += ['`cascade_chute_a` et `cascade_voile_a` portent leur animation dans le `.tsx` (250 ms par image) : peindre seulement les tuiles `_a`.',
            'Tuiles `village` à utiliser pour le lac : 63/64 (eau peu profonde), 48-62 (bords `Rive`), 65-79 (eau profonde), 312-317 (ponton), 318 (pilotis), '
            '324-327 (roseaux, nénuphars, rocher dans l\'eau), 138/139 (éboulis), 120-132 (falaise), 300 (buisson coupable).',
            'À régler dans Tiled si besoin : rien (collisions et animations sont dans le `.tsx`).']


def tsx_with_animations():
    s = Sheet.tsx(S)
    for tid, frames in ANIM.items():
        anim = '  <animation>\n' + ''.join(f'   <frame tileid="{t}" duration="{ms}"/>\n' for t, ms in frames) + '  </animation>\n'
        m = re.search(rf' <tile id="{tid}">\n.*? </tile>\n', s, re.S)
        if m:
            k = m.end() - len(' </tile>\n')
            s = s[:k] + anim + s[k:]
        else:
            k = s.find(' <wangsets>') if ' <wangsets>' in s else s.find('</tileset>')
            s = s[:k] + f' <tile id="{tid}">\n{anim} </tile>\n' + s[k:]
    return s


S.tsx = tsx_with_animations

if __name__ == '__main__':
    if '--plan' in sys.argv:
        S.save_all('lac.py')
    else:
        import final_lib
        import lac_art
        S.intro[0] = ("- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette : bleus-verts froids de l'eau, pierre gris-violet du "
                      "Sanctuaire. Les collisions sont dans le tileset (voir la colonne Collision).")
        px = final_lib.render(S, lac_art.REG)
        final_lib.save_final(S, px, 'lac.py')
