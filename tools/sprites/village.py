"""Tileset de Brumeval, le village — PLAN (aplats + numéros) — Les Trois Sceaux.

Usage : python tools/sprites/village.py          -> DESSIN FINAL (village.png, village_brume.png, _numeros.png, _plan.md, .tsx)
        python tools/sprites/village.py --plan   -> PLAN (aplats par famille et numéros)
Le catalogue (numéros, collisions, terrains) est identique dans les deux cas ; le dessin est dans village_art1/2/3.py.
Variante « brume » : même planche recolorée (plus froide, désaturée, voilée) : art/tilesets/village_brume.png, mêmes numéros.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import *  # noqa: E402,F401,F403
import tsplan  # noqa: E402

tsplan.CATS.update(
    herbe='#6aa04a', paves='#a8a4b8', terre='#b07a48', eau='#4a78c0', profonde='#24407a', ravin='#2a1c34',
    falaise='#8a7a6a', rocher='#9a948c',
    toit_a='#b8503c', toit_b='#5c6a7c', toit_c='#d0b050',
    fac_a='#e0d0a8', fac_b='#a8a29a', fac_c='#a8764a', porte='#e8782c',
    forge='#e0502c', metal='#6a6a78', bois='#8a5a34', etal='#e8b830', fleur='#e060a0', vert='#3f8a3a',
    lampe='#f0e060', panneau='#c8a060', quai='#b88a50', eau_deco='#78a0d0', chateau='#8a7a98', brume='#f0f0f8',
    bloc='#d040c0', secret='#a040e0', pierre='#b0b0a8', escalier='#d0c090')

S = Sheet('village', 8, 'Brumeval, le village (overworld : place, maisons, lac, ravin, falaise)',
          ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px (dessin final). Le plan est en aplats : **la couleur indique la '
           'famille** (vert herbe, gris-bleu pavés, brun terre, bleu eau, rouge/gris/jaune toits, orange portes et blocages…) ; une zone plus '
           'sombre dans une tuile = zone solide.',
           '- **Arbres, buissons, rochers, falaises de forêt, fleurs et chemin de forêt** : on réutilise le tileset `foret` dans la même carte '
           '(Tiled accepte plusieurs tilesets par carte).',
           '- **Variantes jour / brume** : un seul jeu de numéros. Le dessin final fournira `village.png` (jour) et une copie recolorée par '
           'teinte `village_brume.png` ; le jeu choisit la texture selon l\'avancement. Le calque `Dessus` contient en plus des tuiles '
           '**semi-transparentes** de brume (groupe « Brume ») qu\'on peut masquer à mesure que la brume se lève.'],
          ['`Sol` : herbe, pavés, terre, rive, eau, ravin (le fond), sols de décor',
           '`Decor` : petits décors sans collision (fleurs, seau, ponton, nénuphars, tablier du pont-levis abaissé…)',
           '`Murs` : tout ce qui bloque (façades, toits, falaise, ravin, éboulis, objets). Les collisions sont dans le tileset',
           '`Objets` : Sortie, Spawn, PNJ, Coffre, MurFissure, Ramassable… (objets Tiled, pas des tuiles)',
           '`Dessus` : passe devant Brann (auvents, cime des lampadaires, enseignes, brume)'])
S.reserve = 4


def M(nom, role, coll, cat, **k):
    return (nom, role, 'Murs', coll, cat, k)


def D(nom, role, cat, **k):
    return (nom, role, 'Decor', None, cat, k)


def SO(nom, role, cat, **k):
    return (nom, role, 'Sol', None, cat, k)


def U(nom, role, cat, coll=None, **k):
    return (nom, role, 'Dessus', coll, cat, k)


# ---------------------------------------------------------------- 1. herbe
S.group('1. Herbe', 'Même famille que `foret` (vert 5a8a3c). Les tuiles 0 à 6 servent aussi de base aux terrains Pavés, Terre et Rive.')
herbes = [('herbe_a', 'Herbe de base'), ('herbe_b', 'Herbe avec touffes'), ('herbe_c', 'Herbe avec trèfles'),
          ('herbe_d', 'Herbe avec petits cailloux'), ('herbe_fleurs_blanches', 'Herbe parsemée de fleurs blanches'),
          ('herbe_fleurs_jaunes', 'Herbe parsemée de fleurs jaunes'), ('herbe_fleurs_rouges', 'Herbe parsemée de fleurs rouges'),
          ('herbe_sombre', 'Herbe sombre (au pied de la falaise et des murs)')]
S.line([SO(n, r, 'herbe') for n, r in herbes])

# ---------------------------------------------------------------- 2-3 terrains de sol
S.group('2. Variantes de pavés (hors terrain)', 'À semer au hasard sur les cases pleines pour casser la répétition.')
S.line([SO('paves_b', 'Pavés, variante B', 'paves'), SO('paves_c', 'Pavés, variante C', 'paves'),
        SO('paves_usees', 'Pavés usés et fendus', 'paves'), SO('paves_mousse', 'Pavés moussus', 'paves'),
        SO('paves_rond', 'Dalle ronde claire (cercle autour du puits ; poser en 3×3 avec les pavés)', 'paves', col='#c8c4d8'),
        SO('paves_blason', 'Dalle gravée du blason de Brumeval (centre de la place)', 'paves', col='#c8c4d8'),
        SO('paves_seuil', 'Seuil de pierre devant une porte', 'paves', col='#8c88a0'),
        SO('paves_escalier_h', 'Marches de pierre (passables) pour monter d\'une terrasse', 'escalier')])
S.group('3. Pavés de la place (terrain `Paves`)', 'Pavés sur herbe : peindre l\'herbe, puis le terrain Paves.', align=16)
b_pav = S.terrain('Paves', 'paves', 'herbe', 'paves', 'herbe', 'paves', False, 'Herbe (base du terrain Paves)',
                  'Pavés, case entière', 'Sol')
S.group('4. Terre battue (terrain `Terre`)', 'Chemins de village. Terre sur herbe.', align=16)
b_ter = S.terrain('Terre', 'terre', 'herbe', 'terre', 'herbe', 'terre', False, 'Herbe (base du terrain Terre)',
                  'Terre battue, case entière', 'Sol')
# ---------------------------------------------------------------- 5-7 eau et ravin
S.group('5. Rive du lac (terrain `Rive`, eau peu profonde)', 'Herbe / eau peu profonde : Brann la traverse (ralentissement possible plus tard).', align=16)
b_riv = S.terrain('Rive', 'rive', 'herbe', 'eau', 'herbe', 'eau', False, 'Herbe (base du terrain Rive)',
                  'Eau peu profonde, case entière (traversable)', 'Sol')
S.group('6. Eau profonde du lac (terrain `Lac profond`, infranchissable)', 'Eau peu profonde / eau profonde. La case pleine et les bords sont sur `Murs` (solides).', align=16)
b_lac = S.terrain('Lac profond', 'lac', 'eau', 'profonde', 'eau', 'profonde', True, 'Eau peu profonde (base du terrain Lac profond)',
                  'Eau profonde, case entière (infranchissable)', 'Sol', layer='Murs')
S.group('7. Ravin au nord du village (terrain `Ravin`)', 'Herbe / vide du ravin. Les cases de ravin sont solides (`Murs`) ; le pont-levis s\'y pose (groupe « Pont-levis »).', align=16)
b_rav = S.terrain('Ravin', 'ravin', 'herbe', 'ravin', 'herbe', 'ravin', True, 'Herbe (base du terrain Ravin)',
                  'Ravin, case entière (vide, infranchissable)', 'Sol', layer='Murs')
S.grass_into(['Paves', 'Terre', 'Rive', 'Ravin'], range(0, 7))
S.wang['Lac profond']['tiles'][S.id('rive_plein')] = (1, 1, 1, 1)

S.group('8. Variantes de terre, gravier et sable (hors terrain)', 'À semer au hasard sur les cases pleines.')
S.line([SO('terre_b', 'Terre battue, variante B', 'terre'), SO('terre_c', 'Terre battue, variante C', 'terre'),
        SO('terre_ornieres_h', 'Ornières de charrette horizontales', 'terre'), SO('terre_ornieres_v', 'Ornières de charrette verticales', 'terre'),
        SO('terre_flaque', 'Flaque de boue', 'terre'), SO('terre_cailloux', 'Terre et cailloux', 'terre'),
        SO('gravier', 'Gravier clair de la rive', 'rocher', col='#c8c0a8'), SO('sable_rive', 'Sable humide de la rive', 'terre', col='#d8c090')])


# ---------------------------------------------------------------- 8 pont-levis
S.group('8. Pont-levis (relevé / abaissé)',
        'Le ravin est large de 3 cases (peint avec le terrain Ravin) ; le pont fait **2 cases de large**. Relevé : un panneau debout contre le '
        'pied de la tour, côté nord, qui barre le passage. Abaissé : un tablier de 3 cases de haut posé sur le ravin. L\'état est piloté par le code '
        '(cible à flèche) ; la carte contient la version relevée, le jeu remplace par la version abaissée (voir le rapport).')
S.line([M('pl_releve_haut_g', 'Pont-levis RELEVÉ, haut gauche (panneau debout, chaînes)', FULL, 'bloc'),
        M('pl_releve_haut_d', 'Pont-levis RELEVÉ, haut droite', FULL, 'bloc'),
        M('pl_releve_bas_g', 'Pont-levis RELEVÉ, bas gauche (pied du panneau)', FULL, 'bloc'),
        M('pl_releve_bas_d', 'Pont-levis RELEVÉ, bas droite', FULL, 'bloc'),
        D('pl_abaisse_haut_g', 'Pont-levis ABAISSÉ, bout nord gauche (articulation)', 'quai'),
        D('pl_abaisse_haut_d', 'Pont-levis ABAISSÉ, bout nord droite', 'quai'),
        D('pl_abaisse_mil_g', 'Pont-levis ABAISSÉ, milieu gauche (planches + garde-corps)', 'quai'),
        D('pl_abaisse_mil_d', 'Pont-levis ABAISSÉ, milieu droite', 'quai')])
S.line([D('pl_abaisse_bas_g', 'Pont-levis ABAISSÉ, bout sud gauche (rejoint le chemin du village)', 'quai'),
        D('pl_abaisse_bas_d', 'Pont-levis ABAISSÉ, bout sud droite', 'quai'),
        M('pl_pilier_g', 'Pilier de pierre qui porte les chaînes, côté gauche du pont', FULL, 'pierre'),
        M('pl_pilier_d', 'Pilier de pierre qui porte les chaînes, côté droit du pont', FULL, 'pierre'),
        M('pl_tour_porte', 'Porte de la tour du pont (ferme le nord, solide ; le pont relevé est devant)', FULL, 'chateau'),
        M('pl_tour_mur', 'Mur de la tour du pont', FULL, 'chateau'),
        U('pl_chaine_g', 'Chaîne du pont (haut, passe devant Brann), côté gauche', 'metal'),
        U('pl_chaine_d', 'Chaîne du pont (haut), côté droit', 'metal')])
S.assemblage('Pont-levis relevé (2×2)', [['pl_releve_haut_g', 'pl_releve_haut_d'], ['pl_releve_bas_g', 'pl_releve_bas_d']],
             'Murs', 'posé sur la rive nord, contre la tour ; ravin peint (Murs) devant')
S.assemblage('Pont-levis abaissé (2×3)', [['pl_abaisse_haut_g', 'pl_abaisse_haut_d'], ['pl_abaisse_mil_g', 'pl_abaisse_mil_d'],
                                          ['pl_abaisse_bas_g', 'pl_abaisse_bas_d']],
             'Decor (+ retirer les Murs du ravin dessous)', 'le code supprime la collision en dessous à l\'abaissement')

# ---------------------------------------------------------------- 9 falaise
S.group('9. Falaise et rochers', 'Falaise brun-gris de la montagne (est du village, fond du ravin). Haut de falaise = arête, la moitié basse est solide.')
S.line([M('falaise_crete', 'Haut de falaise : arête (moitié basse solide)', HALF_BOT, 'falaise'),
        M('falaise_crete_g', 'Haut de falaise, extrémité gauche', [(3, 16, 29, 16)], 'falaise'),
        M('falaise_crete_d', 'Haut de falaise, extrémité droite', [(0, 16, 29, 16)], 'falaise'),
        M('falaise_face', 'Face de falaise (solide)', FULL, 'falaise'),
        M('falaise_face_g', 'Face de falaise, extrémité gauche', FULL, 'falaise'),
        M('falaise_face_d', 'Face de falaise, extrémité droite', FULL, 'falaise'),
        M('falaise_pied', 'Pied de falaise avec éboulis (solide)', FULL, 'falaise'),
        M('falaise_pied_g', 'Pied de falaise, extrémité gauche', FULL, 'falaise')])
S.line([M('falaise_pied_d', 'Pied de falaise, extrémité droite', FULL, 'falaise'),
        M('falaise_face_lierre', 'Face de falaise couverte de lierre', FULL, 'falaise'),
        M('falaise_face_mousse', 'Face de falaise moussue', FULL, 'falaise'),
        SO('falaise_sommet', 'Sommet de falaise en herbe rase (plateau du château, inaccessible)', 'herbe', col='#78a858'),
        SO('falaise_sommet_pierre', 'Sommet de falaise, dalle de pierre', 'pierre'),
        M('rocher_a', 'Gros rocher isolé (solide)', OBJ, 'rocher'), M('rocher_b', 'Gros rocher isolé, variante', OBJ, 'rocher'),
        D('cailloux_village', 'Petits cailloux', 'rocher')])
S.assemblage('Falaise de 3 cases de haut', [['falaise_crete'], ['falaise_face'], ['falaise_pied']], 'Murs', 'extrémités : _g / _d')

# ---------------------------------------------------------------- 10 blocages
S.group('10. Blocages de progression (éboulis, mur fissuré)',
        'Éboulis : solide, à détruire à la bombe plus tard (le code retire la tuile de `Murs` et pose la version dégagée). '
        'Mur fissuré : tuile de pierre fissurée ; l\'objet `MurFissure` (id) se pose dessus, la bombe l\'ouvre.')
S.line([M('eboulis_a', 'ÉBOULIS : tas de rochers, case pleine (solide)', FULL, 'bloc'),
        M('eboulis_b', 'ÉBOULIS : variante B (solide)', FULL, 'bloc'),
        M('eboulis_g', 'ÉBOULIS large, moitié gauche (2×1, solide)', FULL, 'bloc'),
        M('eboulis_d', 'ÉBOULIS large, moitié droite (2×1, solide)', FULL, 'bloc'),
        SO('eboulis_degage_a', 'Éboulis DÉGAGÉ : gravats au sol (passable), remplace eboulis_a/b', 'rocher', col='#c8c0b0'),
        SO('eboulis_degage_b', 'Éboulis DÉGAGÉ : gravats, variante', 'rocher', col='#c8c0b0'),
        M('mur_fissure', 'MUR FISSURÉ de la cave de Garrick : pierre fissurée (solide ; objet MurFissure dessus)', FULL, 'secret'),
        D('mur_fissure_ouvert', 'Mur fissuré OUVERT : trou noir dans le mur (Sortie vers la cave de Garrick posée dessus)', 'secret', col='#201830')])
S.line([D('mur_fissure_gravats', 'Gravats devant le mur ouvert (décor)', 'rocher'),
        D('eboulis_poussiere', 'Poussière et cailloux autour de l\'éboulis (décor)', 'rocher')])
S.assemblage('Éboulis large (2×1)', [['eboulis_g', 'eboulis_d']], 'Murs', 'ferme un passage de 2 cases sur la rive sud')

# ---------------------------------------------------------------- 11-13 toits
roofs = [('a', 'tuiles rouges', 'toit_a'), ('b', 'ardoise grise', 'toit_b'), ('c', 'chaume', 'toit_c')]
for k, (r, matiere, cat) in enumerate(roofs, start=11):
    S.group(f'{k}. Toit {r.upper()} ({matiere})',
            'Toit en 3 rangées (haut, milieu, bas = avant-toit) sur `Murs` (solide : on ne marche pas sur un toit). '
            'Largeur minimale 3 cases ; répéter `_m` et la rangée du milieu pour agrandir.', align=16)
    S.line([M(f'toit_{r}_haut_g', f'Toit {r.upper()}, rangée haute, bord gauche (faîtage)', FULL, cat),
            M(f'toit_{r}_haut_m', f'Toit {r.upper()}, rangée haute (faîtage)', FULL, cat),
            M(f'toit_{r}_haut_d', f'Toit {r.upper()}, rangée haute, bord droit', FULL, cat),
            M(f'toit_{r}_mil_g', f'Toit {r.upper()}, rangée du milieu, bord gauche', FULL, cat),
            M(f'toit_{r}_mil_m', f'Toit {r.upper()}, rangée du milieu', FULL, cat),
            M(f'toit_{r}_mil_d', f'Toit {r.upper()}, rangée du milieu, bord droit', FULL, cat),
            M(f'toit_{r}_bas_g', f'Toit {r.upper()}, avant-toit, bord gauche', FULL, cat),
            M(f'toit_{r}_bas_m', f'Toit {r.upper()}, avant-toit (au-dessus de la façade)', FULL, cat)])
    S.line([M(f'toit_{r}_bas_d', f'Toit {r.upper()}, avant-toit, bord droit', FULL, cat),
            M(f'toit_{r}_cheminee', f'Toit {r.upper()}, rangée du milieu avec CHEMINÉE de pierre (remplace _mil_m)', FULL, cat, col='#c85a3a'),
            M(f'toit_{r}_lucarne', f'Toit {r.upper()}, rangée du milieu avec lucarne (remplace _mil_m)', FULL, cat),
            M(f'toit_{r}_mil_m2', f'Toit {r.upper()}, rangée du milieu, variante', FULL, cat),
            M(f'toit_{r}_haut_m2', f'Toit {r.upper()}, faîtage, variante', FULL, cat),
            M(f'toit_{r}_flanc_g', f'Toit {r.upper()}, flanc gauche en pignon (maison plus étroite)', FULL, cat),
            M(f'toit_{r}_flanc_d', f'Toit {r.upper()}, flanc droit en pignon', FULL, cat)])
S.assemblage('Maison type A : toit + façade (largeur 4)',
             [['toit_a_haut_g', 'toit_a_haut_m', 'toit_a_haut_m', 'toit_a_haut_d'],
              ['toit_a_mil_g', 'toit_a_cheminee', 'toit_a_mil_m', 'toit_a_mil_d'],
              ['toit_a_bas_g', 'toit_a_bas_m', 'toit_a_bas_m', 'toit_a_bas_d'],
              ['fac_a_coin_g', 'fac_a_fenetre', 'fac_a_porte', 'fac_a_coin_d']],
             'Murs (tout) ; Sortie sur la case porte', 'même principe pour B et C')

# ---------------------------------------------------------------- 14 façades
S.group('14. Façades modulaires (1 rangée sous le toit)',
        'Porte d\'1 case : les montants sont solides, le centre est libre ; l\'objet `Sortie` se pose sur la case de la porte (Brann y entre par le sud). '
        'Style A = colombages crème (toit A), B = pierre grise (toit B, forge), C = planches (toit C).')
facs = [('a', 'colombages crème', 'fac_a'), ('b', 'pierre grise', 'fac_b'), ('c', 'planches de bois', 'fac_c')]
for r, mat, cat in facs:
    S.line([M(f'fac_{r}_coin_g', f'Façade {r.upper()} ({mat}), coin gauche', FULL, cat),
            M(f'fac_{r}_plein', f'Façade {r.upper()}, mur plein', FULL, cat),
            M(f'fac_{r}_fenetre', f'Façade {r.upper()}, fenêtre', FULL, cat),
            M(f'fac_{r}_volets', f'Façade {r.upper()}, fenêtre à volets', FULL, cat),
            M(f'fac_{r}_coin_d', f'Façade {r.upper()}, coin droit', FULL, cat),
            M(f'fac_{r}_porte', f'PORTE d\'1 case, façade {r.upper()} (Sortie dessus)', DOORC, 'porte'),
            M(f'fac_{r}_porte_enseigne', f'PORTE d\'1 case avec enseigne suspendue, façade {r.upper()} (boutiques)', DOORC, 'porte', col='#f0a040'),
            M(f'fac_{r}_plein_b', f'Façade {r.upper()}, mur plein variante (lierre / tonneau)', FULL, cat)])

# ---------------------------------------------------------------- 15 forge
S.group('15. Forge de Corvan (reconnaissable : suie, grande cheminée, enclume dehors)',
        'Façade de pierre B noircie + grande cheminée de forge rouge sur le toit B. L\'enclume est dehors, devant la porte : '
        'c\'est là que se pose l\'objet `StatueCorbeau` (point de sauvegarde, id `village_statue_forge`).')
S.line([M('enclume', 'ENCLUME (dehors, devant la forge) : solide, perchoir du corbeau', [(4, 10, 24, 20)], 'metal'),
        M('meule', 'Meule à aiguiser', OBJ, 'metal', col='#8a8a98'),
        M('bac_trempe', 'Bac de trempe (eau noire)', OBJ, 'eau_deco', col='#3a5a8a'),
        M('tas_charbon', 'Tas de charbon', OBJ, 'metal', col='#3a3a48'),
        M('rateliers_armes', 'Râtelier d\'armes et d\'outils contre le mur', OBJ, 'bois'),
        U('forge_enseigne', 'Enseigne de forge (marteau et enclume) suspendue au-dessus de la porte', 'forge', col='#d8a040'),
        M('forge_facade_foyer', 'Façade de la forge, ouverture du foyer qui rougeoie (solide)', FULL, 'forge'),
        M('forge_toit_cheminee', 'Toit B avec GRANDE CHEMINÉE de forge (remplace toit_b_mil_m ; fumée possible au-dessus)', FULL, 'forge')])
S.line([M('forge_porte', 'PORTE de la forge (1 case, fer à cheval) : Sortie vers l\'intérieur de la forge', DOORC, 'porte', col='#ff9040'),
        M('forge_facade_suie', 'Façade de la forge, pierre noircie de suie', FULL, 'metal', col='#6a6068'),
        U('forge_auvent_g', 'Auvent de la forge, bord gauche (poutres ; on passe dessous)', 'bois'),
        U('forge_auvent_m', 'Auvent de la forge, milieu', 'bois'),
        U('forge_auvent_d', 'Auvent de la forge, bord droit', 'bois'),
        U('fumee_a', 'Fumée de cheminée (semi-transparente, sur Dessus)', 'brume', ghost=True),
        U('fumee_b', 'Fumée de cheminée, variante', 'brume', ghost=True),
        M('billot_forge', 'Billot et marteaux', OBJ, 'bois')])
S.assemblage('Forge de Corvan (façade 5 de large)',
             [['toit_b_haut_g', 'toit_b_haut_m', 'toit_b_haut_m', 'toit_b_haut_m', 'toit_b_haut_d'],
              ['toit_b_mil_g', 'forge_toit_cheminee', 'toit_b_mil_m', 'toit_b_mil_m', 'toit_b_mil_d'],
              ['toit_b_bas_g', 'toit_b_bas_m', 'toit_b_bas_m', 'toit_b_bas_m', 'toit_b_bas_d'],
              ['fac_b_coin_g', 'forge_facade_foyer', 'forge_porte', 'fac_b_fenetre', 'fac_b_coin_d']],
             'Murs ; auvent (Dessus) sur la rangée d\'avant-toit si voulu',
             'enclume à poser sur la case devant la porte à gauche (Decor/Murs), StatueCorbeau dessus')

# ---------------------------------------------------------------- 16 puits & mobilier de place
S.group('16. Puits (2×2), abreuvoir, bancs, charrette',
        'Le puits est au centre de la place. Assemblage 2×2 : haut (poulie, toit) + bas (margelle). Les bords hauts passent derrière Brann.')
S.line([M('puits_haut_g', 'PUITS 2×2, haut gauche (poulie et petit toit)', [(0, 16, 32, 16)], 'pierre'),
        M('puits_haut_d', 'PUITS 2×2, haut droite', [(0, 16, 32, 16)], 'pierre'),
        D('seau', 'Seau en bois posé au sol', 'bois'),
        M('auge_g', 'Abreuvoir en pierre, moitié gauche', OBJ, 'pierre'), M('auge_d', 'Abreuvoir en pierre, moitié droite', OBJ, 'pierre'),
        M('banc_g', 'Banc de la place, bout gauche', [(2, 14, 30, 14)], 'bois'),
        M('banc_m', 'Banc de la place, milieu', [(0, 14, 32, 14)], 'bois'),
        M('banc_d', 'Banc de la place, bout droit', [(0, 14, 30, 14)], 'bois')])
S.line([M('puits_bas_g', 'PUITS 2×2, bas gauche (margelle)', FULL, 'pierre'), M('puits_bas_d', 'PUITS 2×2, bas droite', FULL, 'pierre'),
        M('foin_botte', 'Botte de foin', OBJ, 'etal', col='#d8c060'), M('foin_tas', 'Tas de foin (décor solide)', OBJ, 'etal', col='#d8c060'),
        M('charrette_g', 'Charrette à bras, moitié gauche', OBJ, 'bois'), M('charrette_d', 'Charrette à bras, moitié droite', OBJ, 'bois'),
        M('tas_bois', 'Tas de bois de chauffage', OBJ, 'bois'), M('billot_bois', 'Billot avec hache', OBJ, 'bois')])
S.assemblage('Puits 2×2', [['puits_haut_g', 'puits_haut_d'], ['puits_bas_g', 'puits_bas_d']], 'Murs',
             'entouré de paves_rond en 4×4 ; les deux rangées sont solides')

# ---------------------------------------------------------------- 17 clôtures et murets
S.group('17. Clôtures et murets', 'Clôtures de bois (jardins, enclos) et murets de pierre (terrasses). Le portillon est solide fermé.')
S.line([M('cloture_h', 'Clôture horizontale', [(0, 12, 32, 12)], 'bois'), M('cloture_v', 'Clôture verticale', [(10, 0, 12, 32)], 'bois'),
        M('cloture_c_hg', 'Clôture, coin haut-gauche', [(10, 12, 22, 20)], 'bois'), M('cloture_c_hd', 'Clôture, coin haut-droite', [(0, 12, 22, 20)], 'bois'),
        M('cloture_c_bg', 'Clôture, coin bas-gauche', [(10, 0, 22, 24)], 'bois'), M('cloture_c_bd', 'Clôture, coin bas-droite', [(0, 0, 22, 24)], 'bois'),
        M('cloture_portillon', 'Portillon fermé (solide)', [(0, 12, 32, 12)], 'bois', col='#c89060'),
        D('cloture_portillon_ouvert', 'Portillon ouvert (décor, passable)', 'bois')])
S.line([M('muret_h', 'Muret de pierre horizontal', [(0, 12, 32, 16)], 'pierre'), M('muret_v', 'Muret de pierre vertical', [(8, 0, 16, 32)], 'pierre'),
        M('muret_c_hg', 'Muret, coin haut-gauche', [(8, 12, 24, 20)], 'pierre'), M('muret_c_hd', 'Muret, coin haut-droite', [(0, 12, 24, 20)], 'pierre'),
        M('muret_c_bg', 'Muret, coin bas-gauche', [(8, 0, 24, 28)], 'pierre'), M('muret_c_bd', 'Muret, coin bas-droite', [(0, 0, 24, 28)], 'pierre'),
        M('muret_poteau', 'Pilier de muret', POST, 'pierre'), SO('escalier_rampe', 'Rampe de terre entre deux niveaux (passable)', 'terre', col='#c09060')])

# ---------------------------------------------------------------- 18 marché et caisses
S.group('18. Étals, tonneaux, caisses', 'Auvents sur `Dessus` : on passe dessous ; les étals sont solides.')
S.line([M('etal_g', 'Étal de marché, bout gauche (marchandises)', TABLE, 'etal'), M('etal_m', 'Étal de marché, milieu', TABLE, 'etal'),
        M('etal_d', 'Étal de marché, bout droit', TABLE, 'etal'),
        U('auvent_g', 'Auvent de toile rayée, bord gauche (Dessus)', 'toit_a'), U('auvent_m', 'Auvent de toile rayée, milieu (Dessus)', 'toit_a'),
        U('auvent_d', 'Auvent de toile rayée, bord droit (Dessus)', 'toit_a'),
        M('tonneau', 'Tonneau', OBJ, 'bois'), M('tonneaux', 'Deux tonneaux', OBJ, 'bois')])
S.line([M('caisse', 'Caisse de bois', OBJ, 'bois'), M('caisses_empilees', 'Caisses empilées', OBJ, 'bois'),
        M('sacs', 'Sacs de grain', OBJ, 'etal', col='#d8c8a0'), M('jarre', 'Grande jarre', OBJ, 'bois', col='#b86a4a'),
        M('panier', 'Panier de pommes', OBJ, 'etal'), M('citrouilles', 'Citrouilles', OBJ, 'etal', col='#e08830'),
        M('bois_fendu', 'Bois fendu en pile', OBJ, 'bois'), M('ruche', 'Ruche', OBJ, 'etal')])

# ---------------------------------------------------------------- 19 fleurs, potagers
S.group('19. Fleurs et potagers', 'Parterres sans collision sur `Decor` ; pot de fleurs et buisson fleuri solides.')
S.line([D('parterre_rouge', 'Parterre de fleurs rouges', 'fleur', col='#e0402c'), D('parterre_jaune', 'Parterre de fleurs jaunes', 'fleur', col='#f0c840'),
        D('parterre_blanc', 'Parterre de fleurs blanches', 'fleur', col='#f0ece0'),
        M('pot_fleurs', 'Pot de fleurs (devant une porte)', OBJ, 'fleur'), M('buisson_fleuri', 'Buisson fleuri', OBJ, 'vert'),
        D('rosier_mur', 'Rosier grimpant (à poser sur la façade, Decor)', 'fleur'),
        D('potager_a', 'Rangs de légumes', 'vert'), D('potager_b', 'Rangs de choux', 'vert')])

# ---------------------------------------------------------------- 20 lampadaires, panneaux
S.group('20. Lampadaires, panneaux, bornes', 'Panneaux : objet `PNJ`/`Indice` posé dessus pour le texte. Haut du lampadaire sur `Dessus`.')
S.line([M('lampadaire_bas', 'Lampadaire, pied (solide)', POST, 'lampe', col='#706040'),
        U('lampadaire_haut', 'Lampadaire, lanterne (passe devant Brann ; se pose au-dessus du pied)', 'lampe'),
        U('lanterne_murale', 'Lanterne accrochée au mur (Dessus)', 'lampe'),
        M('panneau_bois', 'Panneau de bois (texte)', POST, 'panneau'),
        M('panneau_g', 'Panneau directionnel vers la gauche', POST, 'panneau'), M('panneau_d', 'Panneau directionnel vers la droite', POST, 'panneau'),
        M('borne', 'Borne de pierre', POST, 'pierre'), M('stele_gardiens', 'Stèle des anciens gardiens (indice de l\'histoire)', OBJ, 'pierre', col='#c0b8d0')])

# ---------------------------------------------------------------- 21 quai
S.group('21. Quai, ponton, barques, rive', 'Ponton sur `Decor`, au-dessus de l\'eau. Si l\'eau dessous est profonde (Murs), retirer la collision sous le ponton.')
S.line([D('ponton_h', 'Ponton, planches horizontales (se raccorde à gauche/droite)', 'quai'), D('ponton_v', 'Ponton, planches verticales', 'quai'),
        D('ponton_bout_g', 'Ponton, extrémité gauche', 'quai'), D('ponton_bout_d', 'Ponton, extrémité droite', 'quai'),
        D('ponton_bout_haut', 'Ponton, extrémité haute', 'quai'), D('ponton_bout_bas', 'Ponton, extrémité basse (côté berge)', 'quai'),
        M('pilotis', 'Pilotis dans l\'eau', POST, 'bois'), M('bollard', 'Bitte d\'amarrage', POST, 'bois')])
S.line([M('barque_g', 'Barque amarrée, moitié gauche', [(0, 8, 32, 22)], 'bois'), M('barque_d', 'Barque amarrée, moitié droite', [(0, 8, 32, 22)], 'bois'),
        M('filet', 'Filet de pêche séchant', OBJ, 'eau_deco'), M('poisson_seche', 'Séchoir à poissons', OBJ, 'bois'),
        D('roseaux_a', 'Roseaux', 'vert'), D('roseaux_b', 'Roseaux, variante', 'vert'),
        D('nenuphars', 'Nénuphars (sur l\'eau)', 'vert'), M('rocher_eau', 'Rocher dans l\'eau', OBJ, 'rocher')])

# ---------------------------------------------------------------- 22 château
S.group('22. Château lointain (silhouette sur la falaise, 8×3)',
        'Visible dès le premier écran au nord-est. À poser sur le sommet de falaise, derrière la falaise, **hors de portée** (calque Murs pour être sûr). '
        'Version brume = teintée bleu-gris dans `village_brume.png`.')
chateau = [['Tour gauche, sommet', 'Créneaux', 'Tourelle', 'Donjon, sommet', 'Donjon, drapeau', 'Tourelle', 'Créneaux', 'Tour droite, sommet'],
           ['Tour gauche, milieu', 'Mur d\'enceinte', 'Mur et tourelle', 'Donjon, milieu (fenêtres)', 'Donjon, milieu', 'Mur et tourelle', 'Mur d\'enceinte', 'Tour droite, milieu'],
           ['Tour gauche, pied', 'Mur d\'enceinte, pied', 'Poterne', 'Donjon, pied', 'Grande porte du château', 'Poterne', 'Mur d\'enceinte, pied', 'Tour droite, pied']]
for r, row in enumerate(chateau):
    S.line([M(f'chateau_{r}{c}', f'Château : {t}', FULL, 'chateau') for c, t in enumerate(row)])
S.assemblage('Château lointain (8×3)', [[f'chateau_{r}{c}' for c in range(8)] for r in range(3)], 'Murs', 'au-dessus de la falaise, tuiles 0 à 7 de chaque rangée')

# ---------------------------------------------------------------- 23 brume
S.group('23. Brume (semi-transparente, calque `Dessus`)',
        'Tuiles à demi transparentes qui donnent la brume épaisse du début. Les poser en nappes sur `Dessus` ; le code (ou un second calque de brume) les masque quand la brume se lève.')
S.line([U('brume_dense_a', 'Brume dense, nappe A', 'brume', ghost=True), U('brume_dense_b', 'Brume dense, nappe B', 'brume', ghost=True),
        U('brume_dense_c', 'Brume dense, nappe C', 'brume', ghost=True), U('brume_dense_d', 'Brume dense, nappe D', 'brume', ghost=True),
        U('brume_bord_haut', 'Brume, dégradé : dense en bas, claire en haut', 'brume', ghost=True),
        U('brume_bord_bas', 'Brume, dégradé : dense en haut, claire en bas', 'brume', ghost=True),
        U('brume_bord_g', 'Brume, dégradé : dense à droite', 'brume', ghost=True),
        U('brume_bord_d', 'Brume, dégradé : dense à gauche', 'brume', ghost=True)])
S.line([U('brume_legere_a', 'Brume légère, voile A', 'brume', ghost=True), U('brume_legere_b', 'Brume légère, voile B', 'brume', ghost=True),
        U('brume_legere_c', 'Brume légère, voile C', 'brume', ghost=True), U('brume_legere_d', 'Brume légère, voile D', 'brume', ghost=True),
        U('brume_trouee_a', 'Brume trouée (volutes)', 'brume', ghost=True), U('brume_trouee_b', 'Brume trouée, variante', 'brume', ghost=True),
        D('brume_sol_a', 'Brume rasante au sol (Decor, semi-transparente)', 'brume', ghost=True),
        D('brume_sol_b', 'Brume rasante au sol, variante', 'brume', ghost=True)])

S.notes += ['Pas de tuile de porte « escalier » : les maisons n\'ont pas de marches, l\'entrée est de plain-pied (la Sortie est sur la tuile de porte).',
            'À régler dans Tiled après livraison du dessin : propriétés, éventuelles animations (fumée, drapeau, eau).']

if __name__ == '__main__':
    if '--plan' in sys.argv:
        S.save_all('village.py')
    else:
        import final_lib
        import art_lib
        import village_art1
        import village_art2  # noqa: F401
        import village_art3  # noqa: F401
        px = final_lib.render(S, village_art1.REG)
        final_lib.save_final(S, px, 'village.py', brume=art_lib.haze(px))
