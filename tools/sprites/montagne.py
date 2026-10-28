"""Tileset de la montagne (overworld nord-est : ravin, sentiers, col, entrée de la Mine Effondrée) — Les Trois Sceaux.

Usage : python tools/sprites/montagne.py          -> DESSIN FINAL (montagne.png, montagne_numeros.png, _plan.md, .tsx)
        python tools/sprites/montagne.py --plan   -> PLAN (aplats par famille et numéros)
Le catalogue (numéros, collisions, terrains) est identique dans les deux cas ; le dessin est dans montagne_art.py.
Le RAVIN (terrain `Ravin`) est aux mêmes numéros que dans `village` (80 à 95) : le code le reconnaît par (tileset, id).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import *  # noqa: E402,F401,F403
import tsplan  # noqa: E402

tsplan.CATS.update(
    roche='#8a94a4', roche2='#a8a090', sentier='#b89458', herbe='#5a8a4a', neige='#e4eef8', eau='#4a78c0', profonde='#24407a',
    ravin='#2a1c34', falaise='#7a8498', falaise_h='#667088', rocher='#9a9aa8', bloc='#d040c0', secret='#a040e0',
    sapin='#1f5a3a', rabougri='#7a8a3a', mort='#8a7a68', bois='#8a5a34', rail='#6a6a78', mine='#a8764a', porte='#e8782c',
    panneau='#c8a060', lampe='#f0e060', minerai='#d8b840', fleur='#e060a0', pierre='#b0b0a8', escalier='#d0c090',
    cascade='#a8d0f0', metal='#6a6a78', gris='#808090', etai='#9a6a3a', toit='#6a5a4a')

S = Sheet('montagne', 8, 'La montagne (overworld : ravin et pont-levis, sentiers, falaises, col, entrée de la Mine Effondrée)',
          ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px (dessin final). Le plan est en aplats : **la couleur indique la '
           'famille** (gris-bleu roche, brun sentier, vert herbe de montagne, blanc neige, bleu eau, violet sombre ravin, vert sombre sapins, '
           'orange portes et blocages…) ; une zone plus sombre dans une tuile = zone solide.',
           '- **Le RAVIN (terrain `Ravin`, ids 80 à 95) est aux mêmes numéros que le ravin de `village`** : Brann et les ennemis sont bloqués, '
           'les flèches passent au-dessus (le code reconnaît (tileset `montagne`, ids 80 à 95)). Les tuiles de ravin sont sur `Murs`.',
           '- **Buissons coupables** : `buisson_montagne_a` et `_b` (un coup d\'épée les retire, comme les buissons de `foret`). '
           '**Eboulis et rocher fissuré** : mêmes noms que dans `village`.',
           '- Ce tileset ne contient pas l\'herbe de plaine, les maisons ni les arbres de forêt : on mélange avec `foret` et `village` dans la même carte '
           '(Tiled accepte plusieurs tilesets par carte). Le pont-levis lui-même est une `Porte` d\'apparence `pont_levis` (image dans `art/puzzles/`).'],
          ['`Sol` : roche, gravier, sentier, herbe de montagne, neige, ruisseau (peu profond), ravin et torrent (le fond), sols de décor',
           '`Decor` : petits décors sans collision (fleurs, cailloux, rails, ponts, écume, éboulis dégagé…)',
           '`Murs` : tout ce qui bloque (falaises, ravin, torrent, rochers, arbres, mine, wagonnets). Les collisions sont dans le tileset',
           '`Objets` : Sortie, Spawn, PNJ, Coffre, MurFissure, StatueCorbeau, Interrupteur… (objets Tiled, pas des tuiles)',
           '`Dessus` : passe devant Brann (cimes des gros arbres, poutres d\'étai, lanternes, chaînes)'])
S.reserve = 4


def M(nom, role, coll, cat, **k):
    return (nom, role, 'Murs', coll, cat, k)


def D(nom, role, cat, **k):
    return (nom, role, 'Decor', None, cat, k)


def SO(nom, role, cat, **k):
    return (nom, role, 'Sol', None, cat, k)


def U(nom, role, cat, coll=None, **k):
    return (nom, role, 'Dessus', coll, cat, k)


# ---------------------------------------------------------------- 1. sols (0-15)
S.group('Sols de montagne', 'Les tuiles 0 à 6 (roche) servent de base à tous les terrains : peindre la roche d\'abord, puis le terrain par-dessus. '
        'Semer les variantes au hasard pour casser la répétition.')
S.line([SO('roche_a', 'Sol rocheux gris-bleu, de base', 'roche'), SO('roche_b', 'Sol rocheux avec petits cailloux', 'roche'),
        SO('roche_c', 'Sol rocheux fissuré', 'roche'), SO('roche_d', 'Sol rocheux avec mousse', 'roche'),
        SO('roche_e', 'Sol rocheux avec touffes d\'herbe', 'roche'), SO('roche_f', 'Dalles de roche', 'roche'),
        SO('roche_sombre', 'Sol rocheux sombre (au pied des falaises)', 'roche', col='#6a7488'),
        SO('roche_claire', 'Sol rocheux clair (sommets, ensoleillé)', 'roche', col='#a8b2c0')])
S.line([SO('gravier_a', 'Gravier gris', 'roche', col='#a8a8b0'), SO('gravier_b', 'Gros gravier et cailloux', 'roche', col='#a8a8b0'),
        SO('schiste', 'Schiste en strates grises et ocre', 'roche2'), SO('roche_ocre', 'Sol rocheux ocre (col, abords de la mine)', 'roche2'),
        SO('roche_minerai', 'Sol rocheux avec éclats de minerai', 'minerai'), SO('roche_cendre', 'Sol sombre de poussière de mine', 'roche', col='#58586a'),
        SO('herbe_seche', 'Herbe sèche de montagne', 'herbe', col='#8a9a50'), SO('tapis_mousse', 'Tapis de mousse', 'herbe', col='#4a7a4a')])

# ---------------------------------------------------------------- 2-7 terrains
S.group('Sentier de terre (terrain `Sentier`)', 'Sentier ocre sur roche : peindre la roche, puis le terrain Sentier.', align=16)
S.terrain('Sentier', 'sentier', 'roche', 'sentier', 'Roche (base du terrain Sentier)', 'Sentier de terre', False,
          'Roche (base du terrain Sentier)', 'Sentier de terre, case entière', 'Sol')
S.group('Herbe rase de montagne (terrain `HerbeM`)', 'Herbe rase vert sombre sur roche.', align=16)
S.terrain('HerbeM', 'herbem', 'roche', 'herbe', 'Roche (base du terrain HerbeM)', 'Herbe de montagne', False,
          'Roche (base du terrain HerbeM)', 'Herbe de montagne, case entière', 'Sol')
S.group('Neige et givre (terrain `Neige`)', 'Neige légère sur roche (sommets). Facultatif.', align=16)
S.terrain('Neige', 'neige', 'roche', 'neige', 'Roche (base du terrain Neige)', 'Neige', False,
          'Roche (base du terrain Neige)', 'Neige, case entière', 'Sol')
S.group('Ruisseau (terrain `Ruisseau`, eau peu profonde)', 'Eau peu profonde sur roche : Brann la traverse à gué.', align=16)
S.terrain('Ruisseau', 'ruisseau', 'roche', 'eau', 'Roche (base du terrain Ruisseau)', 'Eau peu profonde', False,
          'Roche (base du terrain Ruisseau)', 'Eau peu profonde, case entière (traversable)', 'Sol')
S.group('RAVIN (terrain `Ravin`, ids 80 à 95, comme dans `village`)', 'Roche / vide du ravin. Les cases de ravin sont solides (`Murs`) ; '
        'les flèches passent au-dessus (le code reconnaît ces ids). Le pont-levis est une `Porte` posée sur le ravin.', align=16)
S.terrain('Ravin', 'ravin', 'roche', 'ravin', 'Roche (base du terrain Ravin)', 'Ravin', True,
          'Roche (base du terrain Ravin)', 'Ravin, case entière (vide, infranchissable)', 'Sol', layer='Murs')
S.group('Torrent (terrain `Torrent`, eau profonde infranchissable)', 'Eau peu profonde / eau profonde. Les bords et la case pleine sont sur `Murs`.', align=16)
S.terrain('Torrent', 'torrent', 'eau', 'profonde', 'Eau peu profonde (base du terrain Torrent)', 'Eau profonde', True,
          'Eau peu profonde (base du terrain Torrent)', 'Eau profonde, case entière (infranchissable)', 'Sol', layer='Murs')
S.grass_into(['Sentier', 'HerbeM', 'Neige', 'Ruisseau', 'Ravin'], range(0, 7))
S.wang['Torrent']['tiles'][S.id('ruisseau_plein')] = (1, 1, 1, 1)

# ---------------------------------------------------------------- 8. variantes de sol (112-127)
S.group('Variantes de sentier, neige et franchissements (hors terrain)', 'À semer au hasard sur les cases pleines. '
        '`gue_pierres` se pose sur le ruisseau ; les escaliers et la rampe sont passables.')
S.line([SO('sentier_b', 'Sentier, variante B', 'sentier'), SO('sentier_c', 'Sentier, variante C', 'sentier'),
        SO('sentier_cailloux', 'Sentier et cailloux', 'sentier'), SO('sentier_ornieres_h', 'Ornières de wagon horizontales', 'sentier'),
        SO('sentier_ornieres_v', 'Ornières de wagon verticales', 'sentier'), SO('sentier_boue', 'Flaque de boue gelée', 'sentier'),
        SO('neige_b', 'Neige, variante B', 'neige'), SO('neige_traces', 'Neige avec traces de pas', 'neige')])
S.line([SO('neige_givre', 'Roche givrée', 'neige', col='#c0ccdc'), SO('gue_pierres', 'Gué : pierres plates dans le ruisseau (passable)', 'eau', col='#7898c0'),
        SO('dalle_ancienne', 'Dalle ancienne gravée (vieille route du col)', 'pierre'), SO('escalier_pierre_h', 'Marches de pierre (montée vers le haut)', 'escalier'),
        SO('escalier_pierre_v', 'Marches de pierre (montée de côté)', 'escalier'), SO('rampe_terre', 'Rampe de terre entre deux niveaux (passable)', 'sentier', col='#c09060'),
        SO('galets', 'Galets de la rive', 'roche', col='#b0b0b8'), SO('sable_ruisseau', 'Sable humide du ruisseau', 'sentier', col='#d8c090')])

# ---------------------------------------------------------------- 9. falaise basse (3 cases de haut)
S.group('Falaise basse (3 cases : crête, face, pied)', 'Falaise gris-bleu. Haut de falaise = arête (la moitié basse est solide) ; '
        'les extrémités `_g` / `_d` ferment le bout d\'un tronçon ; `cote_*` sont les falaises vues de côté (virages). '
        'Le plateau se peint avec le sol de votre choix au-dessus de la crête.')
S.line([M('falaise_crete', 'Haut de falaise : arête (moitié basse solide)', HALF_BOT, 'falaise'),
        M('falaise_crete_g', 'Haut de falaise, extrémité gauche', [(3, 16, 29, 16)], 'falaise'),
        M('falaise_crete_d', 'Haut de falaise, extrémité droite', [(0, 16, 29, 16)], 'falaise'),
        M('falaise_face', 'Face de falaise (roche verticale, solide)', FULL, 'falaise'),
        M('falaise_face_g', 'Face de falaise, extrémité gauche', [(3, 0, 29, 32)], 'falaise'),
        M('falaise_face_d', 'Face de falaise, extrémité droite', [(0, 0, 29, 32)], 'falaise'),
        M('falaise_pied', 'Pied de falaise (éboulis, ombre ; on longe le bas)', [(0, 0, 32, 24)], 'falaise'),
        M('falaise_pied_g', 'Pied de falaise, extrémité gauche', [(3, 0, 29, 24)], 'falaise')])
S.line([M('falaise_pied_d', 'Pied de falaise, extrémité droite', [(0, 0, 29, 24)], 'falaise'),
        M('falaise_cote_g', 'Falaise vue de côté : roche à gauche, plateau à droite', [(0, 0, 12, 32)], 'falaise'),
        M('falaise_cote_d', 'Falaise vue de côté : roche à droite, plateau à gauche', [(20, 0, 12, 32)], 'falaise'),
        M('falaise_cote_pied_g', 'Falaise de côté, pied gauche (jonction avec le pied)', [(0, 0, 12, 24)], 'falaise'),
        M('falaise_cote_pied_d', 'Falaise de côté, pied droit', [(20, 0, 12, 24)], 'falaise'),
        M('falaise_coin_int_g', 'Coin rentrant gauche (la crête tourne vers le bas)', [(0, 0, 14, 32), (0, 16, 32, 16)], 'falaise'),
        M('falaise_coin_int_d', 'Coin rentrant droite', [(18, 0, 14, 32), (0, 16, 32, 16)], 'falaise'),
        M('falaise_veine', 'Face de falaise avec veine de minerai', FULL, 'minerai')])
S.assemblage('Falaise basse de 3 cases de haut', [['falaise_crete'], ['falaise_face'], ['falaise_pied']], 'Murs', 'extrémités : _g / _d')

# ---------------------------------------------------------------- 10. falaise haute (5 cases)
S.group('Falaise haute (5 cases : crête, haut, milieu, bas, pied)', 'Pour les grandes parois : crête, `fh_haut`, `fh_mil` (à répéter), `fh_bas`, pied. '
        'Mêmes extrémités `_g` / `_d`. Variantes neigeuse, avec grotte et avec étais de mine.')
S.line([M('fh_haut', 'Falaise haute, face haute (sous la crête, éclairée)', FULL, 'falaise_h'),
        M('fh_haut_g', 'Falaise haute, face haute, extrémité gauche', [(3, 0, 29, 32)], 'falaise_h'),
        M('fh_haut_d', 'Falaise haute, face haute, extrémité droite', [(0, 0, 29, 32)], 'falaise_h'),
        M('fh_mil', 'Falaise haute, face du milieu (à répéter)', FULL, 'falaise_h'),
        M('fh_mil_g', 'Falaise haute, milieu, extrémité gauche', [(3, 0, 29, 32)], 'falaise_h'),
        M('fh_mil_d', 'Falaise haute, milieu, extrémité droite', [(0, 0, 29, 32)], 'falaise_h'),
        M('fh_bas', 'Falaise haute, face basse (sombre, strates)', FULL, 'falaise_h'),
        M('fh_bas_g', 'Falaise haute, face basse, extrémité gauche', [(3, 0, 29, 32)], 'falaise_h')])
S.line([M('fh_bas_d', 'Falaise haute, face basse, extrémité droite', [(0, 0, 29, 32)], 'falaise_h'),
        M('falaise_neige_crete', 'Crête de falaise enneigée (moitié basse solide)', HALF_BOT, 'neige'),
        M('falaise_neige_face', 'Face de falaise givrée', FULL, 'neige', col='#a8b4c8'),
        M('falaise_etais', 'Face de falaise renforcée d\'étais de mine', FULL, 'etai'),
        M('falaise_fissure', 'FACE FISSURÉE : roche fendue (solide ; objet MurFissure dessus, la bombe l\'ouvre)', FULL, 'secret'),
        D('falaise_fissure_ouvert', 'Face fissurée OUVERTE : trou noir dans la roche (Sortie dessus)', 'secret', col='#201830'),
        M('falaise_grotte', 'ENTRÉE DE GROTTE d\'1 case dans la face (Sortie dessus) : trou noir, montants solides', DOORC, 'porte'),
        M('falaise_grotte_haut', 'Linteau de grotte : roche au-dessus de l\'ouverture', FULL, 'falaise')])
S.line([SO('escalier_crete', 'ESCALIER taillé, case de crête (remplace falaise_crete ; passable)', 'escalier'),
        SO('escalier_face', 'ESCALIER taillé, case de face (remplace falaise_face ; passable)', 'escalier'),
        SO('escalier_pied', 'ESCALIER taillé, case de pied (remplace falaise_pied ; passable)', 'escalier'),
        SO('escalier_fh_haut', 'ESCALIER taillé, falaise haute : haut', 'escalier'), SO('escalier_fh_mil', 'ESCALIER taillé, falaise haute : milieu', 'escalier'),
        SO('escalier_fh_bas', 'ESCALIER taillé, falaise haute : bas', 'escalier'),
        SO('escalier_cote_g', 'Escalier taillé le long d\'une paroi, montée vers la gauche', 'escalier'),
        SO('escalier_cote_d', 'Escalier taillé le long d\'une paroi, montée vers la droite', 'escalier')])
S.assemblage('Falaise haute de 5 cases', [['falaise_crete'], ['fh_haut'], ['fh_mil'], ['fh_bas'], ['falaise_pied']], 'Murs', 'répéter fh_mil pour plus haut')
S.assemblage('Escalier à travers une falaise basse', [['escalier_crete'], ['escalier_face'], ['escalier_pied']], 'Murs (remplace la falaise, sans collision)',
             'ouvre un passage d\'une case de large')

# ---------------------------------------------------------------- 11. rochers
S.group('Rochers, éboulis, rocher fissuré', 'Les rochers sont solides. ÉBOULIS : à détruire à la bombe (le code retire la tuile et pose la version dégagée). '
        'ROCHER FISSURÉ : l\'objet `MurFissure` se pose dessus.')
S.line([M('rocher_a', 'Rocher gris-bleu, solide', OBJ, 'rocher'), M('rocher_b', 'Gros rocher en deux blocs, solide', OBJ, 'rocher'),
        M('rocher_mousse', 'Rocher moussu, solide', OBJ, 'rocher'), M('rocher_neige', 'Rocher enneigé, solide', OBJ, 'neige', col='#c8d4e4'),
        M('rocher_fissure', 'ROCHER FISSURÉ : bloc craquelé (solide ; objet MurFissure dessus)', FULL, 'secret'),
        D('rocher_fissure_ouvert', 'Rocher fissuré OUVERT : cavité noire entre des blocs (Sortie dessus)', 'secret', col='#201830'),
        M('rocher_eau', 'Rocher dans l\'eau, solide', OBJ, 'rocher'), D('cailloux_montagne', 'Petits cailloux', 'rocher')])
S.line([M('eboulis_a', 'ÉBOULIS : tas de rochers, case pleine (solide)', FULL, 'bloc'), M('eboulis_b', 'ÉBOULIS : variante B (solide)', FULL, 'bloc'),
        M('eboulis_g', 'ÉBOULIS large, moitié gauche (2×1, solide)', FULL, 'bloc'), M('eboulis_d', 'ÉBOULIS large, moitié droite (2×1, solide)', FULL, 'bloc'),
        SO('eboulis_degage_a', 'Éboulis DÉGAGÉ : gravats au sol (passable), remplace eboulis_a/b', 'roche', col='#c8c0b0'),
        SO('eboulis_degage_b', 'Éboulis DÉGAGÉ : gravats, variante', 'roche', col='#c8c0b0'),
        D('eboulis_poussiere', 'Poussière et cailloux autour de l\'éboulis (décor)', 'rocher'), D('gravats', 'Gravats devant une ouverture (décor)', 'rocher')])
S.line([M('gros_rocher_hg', 'GROS ROCHER 2×2, haut gauche (solide)', [(4, 8, 28, 24)], 'rocher'),
        M('gros_rocher_hd', 'GROS ROCHER 2×2, haut droite', [(0, 8, 28, 24)], 'rocher'),
        M('gros_rocher_bg', 'GROS ROCHER 2×2, bas gauche', [(4, 0, 28, 24)], 'rocher'),
        M('gros_rocher_bd', 'GROS ROCHER 2×2, bas droite', [(0, 0, 28, 24)], 'rocher'),
        M('cairn', 'Cairn : pierres empilées (balise de sentier)', OBJ, 'pierre'),
        M('socle_corbeau', 'Socle de pierre (perchoir pour l\'objet StatueCorbeau)', OBJ, 'pierre', col='#c0b8d0'),
        M('bloc_taille', 'Bloc de pierre taillé (vestige du col)', OBJ, 'pierre'), M('colonne_brisee', 'Colonne brisée', POST, 'pierre')])
S.assemblage('Gros rocher 2×2', [['gros_rocher_hg', 'gros_rocher_hd'], ['gros_rocher_bg', 'gros_rocher_bd']], 'Murs')
S.assemblage('Éboulis large (2×1)', [['eboulis_g', 'eboulis_d']], 'Murs', 'ferme un passage de 2 cases')

# ---------------------------------------------------------------- 12. arbres
S.group('Arbres 1×1 : sapins, arbres rabougris, pins morts, buissons', 'Les tuiles `buisson_montagne_*` sont coupables à l\'épée (comme les buissons de `foret`). '
        '`sapin_dense_*` : feuillage case pleine pour les forêts de sapins.')
S.line([M('sapin_petit_a', 'Sapin 1×1, solide', [(8, 12, 16, 18)], 'sapin'), M('sapin_petit_b', 'Sapin 1×1, variante plus large', [(8, 12, 16, 18)], 'sapin'),
        M('sapin_dense_a', 'Sapins serrés, case pleine (lisière infranchissable)', FULL, 'sapin'), M('sapin_dense_b', 'Sapins serrés, variante', FULL, 'sapin'),
        M('arbre_rabougri_a', 'Arbre rabougri tordu 1×1, solide', [(8, 12, 16, 18)], 'rabougri'),
        M('arbre_rabougri_b', 'Arbre rabougri, variante', [(8, 12, 16, 18)], 'rabougri'),
        M('pin_mort', 'Pin mort 1×1, solide', [(10, 10, 12, 20)], 'mort'), M('souche_montagne', 'Souche, solide', [(6, 12, 20, 16)], 'mort')])
S.line([M('sapin_neige_petit', 'Sapin enneigé 1×1, solide', [(8, 12, 16, 18)], 'neige', col='#7a9a98'),
        M('sapin_dense_neige', 'Sapins enneigés serrés, case pleine', FULL, 'neige', col='#7a9a98'),
        M('tronc_couche', 'Tronc couché horizontal, solide', [(2, 10, 28, 16)], 'mort'),
        M('buisson_montagne_a', 'Arbuste de montagne coupable (1 coup d\'épée)', [(2, 6, 28, 24)], 'herbe'),
        M('buisson_montagne_b', 'Arbuste de montagne coupable, variante', [(2, 6, 28, 24)], 'herbe'),
        M('genevrier', 'Genévrier épineux, solide (non coupable)', [(2, 6, 28, 24)], 'sapin'),
        M('buisson_neige', 'Buisson enneigé, solide', [(2, 6, 28, 24)], 'neige', col='#a8c0b8'),
        D('fougeres', 'Fougères de sous-bois', 'herbe')])
S.group('Gros arbres 2×2 (cime sur `Dessus`, tronc sur `Murs`)', 'Poser le tronc (2 cases du bas) sur `Murs` et la cime (2 cases du haut) sur `Dessus`, '
        'au-dessus du tronc : Brann passe derrière la cime.')
S.line([U('sapin_a_cime_hg', 'Grand sapin, cime gauche (Dessus)', 'sapin'), U('sapin_a_cime_hd', 'Grand sapin, cime droite (Dessus)', 'sapin'),
        U('sapin_b_cime_hg', 'Grand sapin (variante), cime gauche (Dessus)', 'sapin'), U('sapin_b_cime_hd', 'Grand sapin (variante), cime droite (Dessus)', 'sapin'),
        U('sapin_neige_cime_hg', 'Grand sapin enneigé, cime gauche (Dessus)', 'neige', col='#7a9a98'),
        U('sapin_neige_cime_hd', 'Grand sapin enneigé, cime droite (Dessus)', 'neige', col='#7a9a98'),
        U('rabougri_cime_hg', 'Grand arbre rabougri, cime gauche (Dessus)', 'rabougri'), U('rabougri_cime_hd', 'Grand arbre rabougri, cime droite (Dessus)', 'rabougri')])
S.line([U('pin_mort_cime_hg', 'Grand pin mort, branches gauche (Dessus)', 'mort'), U('pin_mort_cime_hd', 'Grand pin mort, branches droite (Dessus)', 'mort'),
        M('sapin_a_tronc_g', 'Grand sapin, tronc gauche (Murs)', [(14, 4, 18, 28)], 'sapin'), M('sapin_a_tronc_d', 'Grand sapin, tronc droit (Murs)', [(0, 4, 18, 28)], 'sapin'),
        M('sapin_b_tronc_g', 'Grand sapin (variante), tronc gauche (Murs)', [(14, 4, 18, 28)], 'sapin'),
        M('sapin_b_tronc_d', 'Grand sapin (variante), tronc droit (Murs)', [(0, 4, 18, 28)], 'sapin'),
        M('sapin_neige_tronc_g', 'Grand sapin enneigé, tronc gauche (Murs)', [(14, 4, 18, 28)], 'neige', col='#7a9a98'),
        M('sapin_neige_tronc_d', 'Grand sapin enneigé, tronc droit (Murs)', [(0, 4, 18, 28)], 'neige', col='#7a9a98')])
S.line([M('rabougri_tronc_g', 'Grand arbre rabougri, tronc gauche (Murs)', [(14, 4, 18, 28)], 'rabougri'),
        M('rabougri_tronc_d', 'Grand arbre rabougri, tronc droit (Murs)', [(0, 4, 18, 28)], 'rabougri'),
        M('pin_mort_tronc_g', 'Grand pin mort, tronc gauche (Murs)', [(14, 4, 18, 28)], 'mort'),
        M('pin_mort_tronc_d', 'Grand pin mort, tronc droit (Murs)', [(0, 4, 18, 28)], 'mort')])
S.assemblage('Grand sapin 2×2', [['sapin_a_cime_hg', 'sapin_a_cime_hd'], ['sapin_a_tronc_g', 'sapin_a_tronc_d']], 'cime sur Dessus, tronc sur Murs', 'variantes : sapin_b_, sapin_neige_, rabougri_, pin_mort_')

# ---------------------------------------------------------------- 13. petits décors
S.group('Petits décors (calque Decor, sans collision)', 'Fleurs de montagne, herbes, mousse, ossements.')
S.line([D('fleurs_alpines_a', 'Fleurs alpines bleues et blanches', 'fleur', col='#8090e0'), D('fleurs_alpines_b', 'Fleurs alpines jaunes', 'fleur', col='#f0c840'),
        D('bruyere', 'Bruyère violette', 'fleur', col='#a06ad0'), D('edelweiss', 'Edelweiss', 'fleur', col='#f0ece0'),
        D('touffes_seches', 'Touffes d\'herbe sèche', 'herbe', col='#9aa050'), D('herbe_haute_m', 'Herbe haute de montagne', 'herbe'),
        D('mousse', 'Mousse sur la roche', 'herbe', col='#4a7a4a'), D('ossements', 'Ossements d\'animal', 'pierre', col='#e0d8c0')])

# ---------------------------------------------------------------- 14. eau, cascade
S.group('Cascade et sources', 'Cascade de 1 case de large : haut, milieu (répéter ; deux images à alterner pour l\'animation Tiled), pied, écume. '
        'La cascade se pose sur une face de falaise (`Murs`).')
S.line([M('cascade_haut', 'CASCADE, bord de chute : l\'eau déborde de la crête (solide en bas)', HALF_BOT, 'cascade'),
        M('cascade_milieu_a', 'CASCADE, milieu, image A (à répéter)', FULL, 'cascade'), M('cascade_milieu_b', 'CASCADE, milieu, image B (animation)', FULL, 'cascade'),
        M('cascade_pied', 'CASCADE, pied : bassin et écume (infranchissable)', FULL, 'profonde'),
        D('cascade_ecume', 'Écume et éclaboussures (décor, à poser sur le bassin)', 'cascade', col='#d4e0f0'),
        M('source_rocher', 'SOURCE : l\'eau sort d\'un rocher (origine d\'un ruisseau)', OBJ, 'rocher'),
        D('ecume_rive', 'Écume sur une rive', 'cascade', col='#d4e0f0'), D('flaque_gel', 'Flaque gelée', 'neige', col='#b8d4f0')])

# ---------------------------------------------------------------- 15. ponts
S.group('Ponts de bois', 'Sur `Decor`, au-dessus de l\'eau. Sur un TORRENT (solide), effacer le torrent de `Murs` sous le pont et peindre l\'eau peu profonde '
        'sur `Sol` (le pont n\'enlève pas la collision tout seul). Sur un ruisseau, rien à faire.')
S.line([D('pont_h', 'Pont de bois horizontal (milieu, à répéter)', 'bois'), D('pont_h_bout_g', 'Pont horizontal, bout gauche (appui sur la rive)', 'bois'),
        D('pont_h_bout_d', 'Pont horizontal, bout droit', 'bois'), D('pont_v', 'Pont de bois vertical (milieu, à répéter)', 'bois'),
        D('pont_v_bout_haut', 'Pont vertical, bout haut', 'bois'), D('pont_v_bout_bas', 'Pont vertical, bout bas', 'bois'),
        M('pont_pilotis', 'Pilotis sous un pont (dans l\'eau)', POST, 'bois'), D('pont_planches', 'Planches posées au sol (réparation)', 'bois')])

# ---------------------------------------------------------------- 16. ravin et pont-levis
S.group('Abords du ravin et du pont-levis', 'Le pont-levis est une `Porte` d\'apparence `pont_levis` (2 cases de large) posée sur le ravin ; ces tuiles décorent ses abords. '
        'Piliers de pierre qui portent les chaînes, chaînes sur `Dessus`, palier et butée de chaque berge.')
S.line([M('pl_pilier_g', 'Pilier de pierre qui porte les chaînes, côté gauche du pont', FULL, 'pierre'),
        M('pl_pilier_d', 'Pilier de pierre qui porte les chaînes, côté droit du pont', FULL, 'pierre'),
        U('pl_chaine_g', 'Chaîne du pont (haut, passe devant Brann), côté gauche', 'metal'),
        U('pl_chaine_d', 'Chaîne du pont (haut), côté droit', 'metal'),
        SO('pl_palier', 'Palier de dalles devant le pont (rive sud)', 'pierre'),
        SO('pl_palier_nord', 'Palier de dalles de la berge nord (après le pont)', 'pierre'),
        M('pl_butee', 'Butée de bois du pont (poutre au bord du ravin)', [(0, 8, 32, 24)], 'bois'),
        M('garde_corps_h', 'Garde-corps de bois au bord du ravin (horizontal)', [(0, 12, 32, 12)], 'bois')])

# ---------------------------------------------------------------- 17. rails
S.group('Rails et wagonnets de mine', 'Rails sur `Decor` (sans collision) ; wagonnets sur `Murs` (solides). Courbes : le coin indiqué est celui que le rail relie.')
S.line([D('rail_h', 'Rail horizontal', 'rail'), D('rail_v', 'Rail vertical', 'rail'),
        D('rail_coin_hg', 'Rail courbe : relie le haut et la gauche', 'rail'), D('rail_coin_hd', 'Rail courbe : relie le haut et la droite', 'rail'),
        D('rail_coin_bg', 'Rail courbe : relie le bas et la gauche', 'rail'), D('rail_coin_bd', 'Rail courbe : relie le bas et la droite', 'rail'),
        D('rail_buttoir_g', 'Rail horizontal, buttoir à gauche (fin de voie)', 'rail'), D('rail_buttoir_d', 'Rail horizontal, buttoir à droite', 'rail')])
S.line([D('rail_buttoir_haut', 'Rail vertical, buttoir en haut', 'rail'), D('rail_buttoir_bas', 'Rail vertical, buttoir en bas', 'rail'),
        D('rail_croisement', 'Croisement de rails', 'rail'), D('rail_casse', 'Rail brisé et traverses arrachées', 'rail'),
        M('wagonnet_h', 'Wagonnet plein de minerai, vu de côté (sur rail horizontal)', [(2, 8, 28, 20)], 'rail'),
        M('wagonnet_v', 'Wagonnet plein de minerai, sur rail vertical', [(4, 4, 24, 26)], 'rail'),
        M('wagonnet_vide', 'Wagonnet vide', [(2, 8, 28, 20)], 'rail'), M('wagonnet_renverse', 'Wagonnet renversé, minerai répandu', [(2, 8, 28, 20)], 'rail')])

# ---------------------------------------------------------------- 18. étais, minerai
S.group('Étais en bois, minerai, outils', 'Poutres d\'étai : les poteaux sont solides, la poutre du haut est sur `Dessus` (on passe dessous).')
S.line([M('etai_poteau', 'Poteau d\'étai de bois (solide)', POST, 'etai'), U('etai_poutre_g', 'Poutre d\'étai, bout gauche (Dessus)', 'etai'),
        U('etai_poutre_m', 'Poutre d\'étai, milieu (Dessus)', 'etai'), U('etai_poutre_d', 'Poutre d\'étai, bout droit (Dessus)', 'etai'),
        M('etai_cadre_g', 'Cadre d\'étai : montant gauche contre la roche', THIN_L, 'etai'), M('etai_cadre_d', 'Cadre d\'étai : montant droit', THIN_R, 'etai'),
        M('barriere_h', 'Barrière de planches horizontale (chantier, solide)', [(0, 12, 32, 12)], 'bois'),
        M('barriere_v', 'Barrière de planches verticale', [(10, 0, 12, 32)], 'bois')])
S.line([M('minerai_tas_a', 'Tas de minerai, solide', OBJ, 'minerai'), M('minerai_tas_b', 'Tas de minerai, variante', OBJ, 'minerai'),
        M('minerai_filon', 'Bloc de roche à filon de minerai brillant (décor solide)', FULL, 'minerai'),
        M('caisse_mine', 'Caisse de mine', OBJ, 'bois'), M('tonneau_mine', 'Tonneau de mine', OBJ, 'bois'),
        M('outils_mine', 'Établi de mineur : pioches et masses', OBJ, 'bois'), D('pioche_sol', 'Pioche oubliée au sol', 'metal', col='#8a8a98'),
        M('tas_planches', 'Tas de planches et de poutres', OBJ, 'etai')])

# ---------------------------------------------------------------- 19. lanternes et panneaux
S.group('Lanternes de mineur, panneaux, bornes', 'Haut de lanterne sur `Dessus`. Les panneaux portent un texte via un objet `Indice`/`PNJ` posé dessus.')
S.line([M('lanterne_poteau_bas', 'Poteau de lanterne de mineur, pied (solide)', POST, 'lampe', col='#8a6a30'),
        U('lanterne_poteau_haut', 'Lanterne de mineur au sommet du poteau (Dessus ; au-dessus du pied)', 'lampe'),
        U('lanterne_murale', 'Lanterne accrochée à un étai ou une paroi (Dessus)', 'lampe'),
        D('lanterne_sol', 'Lanterne posée au sol (lueur)', 'lampe'), D('lanterne_eteinte', 'Lanterne éteinte au sol', 'metal', col='#8a7a60'),
        U('lanterne_suspendue', 'Lanterne suspendue à une poutre (Dessus)', 'lampe'),
        M('torche_support', 'Torche plantée dans le sol (support ; décor solide)', POST, 'lampe', col='#c07030'),
        D('lueur_sol', 'Tache de lueur chaude au sol (sous une lanterne)', 'lampe', col='#f0d070')])
S.line([M('panneau_bois', 'Panneau de bois (texte)', POST, 'panneau'), M('panneau_g', 'Panneau directionnel vers la gauche', POST, 'panneau'),
        M('panneau_d', 'Panneau directionnel vers la droite', POST, 'panneau'), M('panneau_danger', 'Panneau « danger » (éboulement, tête de mort)', POST, 'panneau', col='#e0a040'),
        M('panneau_mine', 'Panneau de la Mine (pioche croisée)', POST, 'panneau', col='#c8a060'), M('borne_col', 'Borne de pierre du col', POST, 'pierre'),
        M('stele_gardiens', 'Stèle des anciens gardiens (indice de l\'histoire)', OBJ, 'pierre', col='#c0b8d0'),
        M('fanions', 'Mât de fanions fanés du col', POST, 'panneau', col='#e06060')])

# ---------------------------------------------------------------- 20. entrée de la mine
S.group('ENTRÉE DE LA MINE EFFONDRÉE (5×3 : toit de roche et poutres, façade de planches et de pierre, porte d\'1 case)',
        'À adosser à la falaise : poser la façade à la place d\'une face de falaise (crête de falaise au-dessus). La porte est la case du bas au centre '
        '(`mine_porte`) : l\'objet `Sortie` se pose dessus (Brann entre par le sud). L\'effondrement est visible (poutres cassées, décombres).')
S.line([M('mine_toit_g', 'Façade de la Mine, rangée du haut : roche et poutre, coin gauche', FULL, 'toit'),
        M('mine_toit_m', 'Façade de la Mine, rangée du haut : roche et poutres', FULL, 'toit'),
        M('mine_toit_enseigne', 'Façade de la Mine, rangée du haut au centre : poutre maîtresse et enseigne', FULL, 'toit', col='#8a6a30'),
        M('mine_toit_m2', 'Façade de la Mine, rangée du haut : roche, variante', FULL, 'toit'),
        M('mine_toit_d', 'Façade de la Mine, rangée du haut : coin droit', FULL, 'toit'),
        M('mine_mur_pierre', 'Mur de pierre de la façade (variante pleine)', FULL, 'pierre'),
        M('mine_planches_b', 'Planches clouées (variante pleine)', FULL, 'mine'),
        M('mine_poutre_tombee_m', 'Poutre effondrée en travers du mur', FULL, 'etai')])
S.line([M('mine_mur_g', 'Façade de la Mine, rangée du milieu : coin de pierre et poteau, gauche', FULL, 'pierre'),
        M('mine_mur_planches', 'Façade de la Mine, rangée du milieu : planches clouées', FULL, 'mine'),
        M('mine_linteau', 'Façade de la Mine, linteau au-dessus de la porte (poutre, trou noir sous le toit)', FULL, 'etai'),
        M('mine_mur_effondre', 'Façade de la Mine, rangée du milieu : planches arrachées et poutre cassée', FULL, 'etai'),
        M('mine_mur_d', 'Façade de la Mine, rangée du milieu : coin de pierre et poteau, droite', FULL, 'pierre'),
        M('mine_porte_barree', 'Porte condamnée (planches en croix, solide)', FULL, 'mine'),
        D('mine_porte_ouverte', 'Porte ouverte : noir de la galerie (décor, à poser sur la porte)', 'secret', col='#201830'),
        U('mine_enseigne_dessus', 'Enseigne de la Mine suspendue (Dessus)', 'panneau')])
S.line([M('mine_pied_g', 'Façade de la Mine, rangée du bas : socle de pierre, gauche', FULL, 'pierre'),
        M('mine_pied_decombres', 'Façade de la Mine, rangée du bas : décombres', FULL, 'bloc'),
        M('mine_porte', 'PORTE de la Mine, case du bas au centre (Sortie dessus) : montants solides, centre libre', DOORC, 'porte'),
        M('mine_pied_pierre', 'Façade de la Mine, rangée du bas : socle de pierre', FULL, 'pierre'),
        M('mine_pied_d', 'Façade de la Mine, rangée du bas : socle de pierre, droite', FULL, 'pierre'),
        D('mine_decombres_g', 'Décombres répandus devant la façade (gauche)', 'rocher'), D('mine_decombres_d', 'Décombres répandus devant la façade (droite)', 'rocher'),
        D('mine_seuil', 'Seuil de planches devant la porte (avec rails qui sortent)', 'bois')])
S.assemblage('Entrée de la Mine Effondrée (5×3)',
             [['mine_toit_g', 'mine_toit_m', 'mine_toit_enseigne', 'mine_toit_m2', 'mine_toit_d'],
              ['mine_mur_g', 'mine_mur_planches', 'mine_linteau', 'mine_mur_effondre', 'mine_mur_d'],
              ['mine_pied_g', 'mine_pied_decombres', 'mine_porte', 'mine_pied_pierre', 'mine_pied_d']],
             'Murs (tout) ; Sortie sur la case mine_porte', 'seuil, rails (rail_v) et décombres à poser devant sur Decor')

S.notes += ['Statue du corbeau : c\'est un objet (`StatueCorbeau`), pas une tuile ; `socle_corbeau` est un décor de pierre où la poser.',
            'Cascade : `cascade_milieu_a` et `_b` sont les deux images d\'une animation (à régler dans Tiled : éditeur d\'animation de tuile).',
            'À régler dans Tiled après livraison du dessin : propriétés, animations (cascade, lanternes).']

if __name__ == '__main__':
    if '--plan' in sys.argv:
        S.save_all('montagne.py')
    else:
        import final_lib
        S.intro[0] = ("- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette : pierre gris-bleu, ocre, verts sombres. "
                      "Les collisions sont dans le tileset (voir la colonne Collision).")
        import montagne_art
        import montagne_art2  # noqa: F401
        px = final_lib.render(S, montagne_art.REG)
        final_lib.save_final(S, px, 'montagne.py')
