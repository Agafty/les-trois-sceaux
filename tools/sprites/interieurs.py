"""Tileset des intérieurs de Brumeval — PLAN (aplats + numéros) — Les Trois Sceaux.

Usage : python tools/sprites/interieurs.py
Produit art/tilesets/interieurs.png (+ _numeros.png, _plan.md) et maps/tilesets/interieurs.tsx.
Intérieurs : forge de Corvan, herboristerie de Hulda, boutique de Garrick (+ sa cave), archives d'Isolde, maisons.
Une salle = 20×11 cases (un écran). Murs vus de face : plafond + face en haut, bandes latérales, bandeau en bas avec la porte de sortie.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import *  # noqa: E402,F401,F403
import tsplan  # noqa: E402

tsplan.CATS.update(
    bois='#b08050', bois_s='#7a5230', pierre='#a8a29a', pierre_s='#6c6870', cave='#6a5a50', terre='#8a6a48', suie='#3a3640',
    mur_bois='#a8764a', mur_pierre='#8c8a96', mur_crepi='#d8c8a8', mur_cave='#5a4c48', plafond='#4a3a30', porte='#e8782c',
    forge='#e0502c', metal='#7a7a88', eau_deco='#4a78c0', herbo='#58a048', fiole='#a060d0', etal='#e8b830', livre='#8a4a6a',
    parchemin='#e8dcb0', lit='#d05060', tapis='#b03a3a', tissu='#6080c0', lampe='#f0e060', ombre='#201830', secret='#a040e0',
    escalier='#d0c090', deco='#e060a0')

S = Sheet('interieurs', 8, 'intérieurs de Brumeval (forge, herboristerie, boutique, cave, archives, maisons)',
          ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px (dessin final). Le plan est en aplats : **la couleur indique la famille** ; '
           'une zone plus sombre dans une tuile = zone solide.',
           '- Salle type 20×11 : rangée 0 = plafond, rangée 1 = face du mur du fond (les meubles hauts s\'y adossent), colonnes 0 et 19 = bandes latérales, '
           'rangée 10 = bandeau du bas avec la porte de sortie (`Sortie` + Spawn d\'arrivée juste au-dessus). Un meuble de 2 cases de haut a sa moitié haute '
           'au-dessus de sa moitié basse.',
           '- Le sol des cases couvertes par un meuble reste visible : peindre le sol sur tout `Sol`, puis les meubles sur `Murs` (solides) ou `Decor`.'],
          ['`Sol` : sols (bois, pierre, cave) ; ombres et taches en `Decor`',
           '`Decor` : sans collision (tapis, parchemins sur table, plantes suspendues, outils au mur, ombres)',
           '`Murs` : murs et meubles (collisions dans le tileset)',
           '`Objets` : Sortie, Spawn, PNJ, Coffre, StatueCorbeau (sur l\'enclume), MurFissure, escaliers…',
           '`Dessus` : rarement utilisé en intérieur (haut des poutres, lustres)'])
S.reserve = 4


def M(nom, role, coll, cat, **k):
    return (nom, role, 'Murs', coll, cat, k)


def D(nom, role, cat, **k):
    return (nom, role, 'Decor', None, cat, k)


def SO(nom, role, cat, **k):
    return (nom, role, 'Sol', None, cat, k)


def U(nom, role, cat, **k):
    return (nom, role, 'Dessus', None, cat, k)


# ---------------------------------------------------------------- sols
S.group('Sols', 'Sols pleins ; poser au hasard les variantes. `ombre_*` : ombres semi-transparentes à poser en `Decor` sous le mur du fond.')
S.line([SO('sol_bois_a', 'Plancher de bois, A', 'bois'), SO('sol_bois_b', 'Plancher de bois, B', 'bois'), SO('sol_bois_c', 'Plancher de bois, C (clous)', 'bois'),
        SO('sol_bois_use', 'Plancher usé et sombre', 'bois_s'), SO('sol_pierre_a', 'Dalles de pierre, A', 'pierre'),
        SO('sol_pierre_b', 'Dalles de pierre, B', 'pierre'), SO('sol_pierre_c', 'Dalles de pierre, C', 'pierre'),
        SO('sol_pierre_fissure', 'Dalles de pierre fissurées', 'pierre_s')])
S.line([SO('sol_terre_cave', 'Terre battue de la cave', 'terre'), SO('sol_cave_a', 'Sol de cave, roche A', 'cave'), SO('sol_cave_b', 'Sol de cave, roche B', 'cave'),
        SO('sol_forge_suie', 'Dalles noircies de suie (forge)', 'suie'), D('sol_braises', 'Braises et cendres au sol (décor)', 'forge'),
        D('sol_paille', 'Paille éparse (décor)', 'etal'), D('ombre_mur', 'Ombre sous le mur du fond (semi-transparente)', 'ombre', ghost=True),
        D('ombre_coin', 'Ombre de coin (semi-transparente)', 'ombre', ghost=True)])

# ---------------------------------------------------------------- murs
styles = [('bois', 'bois (maisons, archives)', 'mur_bois'), ('pierre', 'pierre (forge)', 'mur_pierre'), ('crepi', 'crépi clair (herboristerie, boutique)', 'mur_crepi')]
for r, mat, cat in styles:
    S.group(f'Murs en {mat}', 'Rangée 0 = plafond (sombre), rangée 1 = face du mur. Les bandes latérales et le bandeau du bas ferment la salle.', align=16)
    S.line([M(f'mur_{r}_plafond', f'Mur {r} : plafond (bord haut de la salle)', FULL, 'plafond'),
            M(f'mur_{r}_face', f'Mur {r} : face du mur du fond', FULL, cat),
            M(f'mur_{r}_fenetre', f'Mur {r} : face avec fenêtre', FULL, cat, col='#a8d0f0'),
            M(f'mur_{r}_face_deco', f'Mur {r} : face avec tableau / écusson', FULL, cat, col='#c8a0b8'),
            M(f'mur_{r}_coin_haut_g', f'Mur {r} : coin haut gauche', FULL, 'plafond'), M(f'mur_{r}_coin_haut_d', f'Mur {r} : coin haut droite', FULL, 'plafond'),
            M(f'mur_{r}_lat_g', f'Mur {r} : bande latérale gauche', THIN_L, cat), M(f'mur_{r}_lat_d', f'Mur {r} : bande latérale droite', THIN_R, cat)])
    S.line([M(f'mur_{r}_bas', f'Mur {r} : bandeau du bas (bord de la salle)', THIN_B, 'plafond'),
            M(f'mur_{r}_coin_bas_g', f'Mur {r} : coin bas gauche', [(0, 0, 8, 32), (0, 24, 32, 8)], 'plafond'),
            M(f'mur_{r}_coin_bas_d', f'Mur {r} : coin bas droite', [(24, 0, 8, 32), (0, 24, 32, 8)], 'plafond'),
            M(f'porte_sortie_{r}', f'PORTE DE SORTIE du mur du bas ({r}) : 1 case, Sortie dessus ; Spawn d\'arrivée sur la case au-dessus',
              [(0, 24, 6, 8), (26, 24, 6, 8)], 'porte'),
            M(f'mur_{r}_porte_interne', f'Porte intérieure sur la face du fond ({r}) : mène à une pièce voisine (Sortie dessus)', DOORC, 'porte', col='#c0602c'),
            M(f'mur_{r}_face_b', f'Mur {r} : face, variante', FULL, cat), M(f'mur_{r}_vitrail', f'Mur {r} : face avec vitrail', FULL, cat, col='#80a0e0'),
            None])
S.assemblage('Cadre de salle (coins et bords)',
             [['mur_bois_coin_haut_g', 'mur_bois_plafond', 'mur_bois_coin_haut_d'], ['mur_bois_lat_g', 'mur_bois_face', 'mur_bois_lat_d'],
              ['mur_bois_lat_g', None, 'mur_bois_lat_d'], ['mur_bois_coin_bas_g', 'mur_bois_bas', 'mur_bois_coin_bas_d']],
             'Murs', 'à étirer : plafond + face sur toute la largeur, bandes latérales sur toute la hauteur, bandeau du bas avec porte_sortie_<style> à la place de `bas`')

# ---------------------------------------------------------------- cave
S.group('Cave secrète de Garrick (roche)', 'Cave creusée dans la roche, derrière le mur fissuré du village. `mur_cave_fissure` est le mur fissuré **côté cave** (retour) ; '
        'l\'escalier mène au village. Le grand carquois et le grand sac de bombes sont des `Coffre` posés sur les piédestaux.', align=16)
S.line([M('mur_cave_plafond', 'Cave : plafond rocheux', FULL, 'plafond'), M('mur_cave_face', 'Cave : face de roche', FULL, 'mur_cave'),
        M('mur_cave_face_b', 'Cave : face de roche, variante (stalactites)', FULL, 'mur_cave'),
        M('mur_cave_fissure', 'MUR FISSURÉ de la cave (solide ; objet MurFissure dessus)', FULL, 'secret'),
        M('mur_cave_coin_haut_g', 'Cave : coin haut gauche', FULL, 'plafond'), M('mur_cave_coin_haut_d', 'Cave : coin haut droite', FULL, 'plafond'),
        M('mur_cave_lat_g', 'Cave : bande latérale gauche', THIN_L, 'mur_cave'), M('mur_cave_lat_d', 'Cave : bande latérale droite', THIN_R, 'mur_cave')])
S.line([M('mur_cave_bas', 'Cave : bandeau du bas', THIN_B, 'plafond'), M('mur_cave_coin_bas_g', 'Cave : coin bas gauche', [(0, 0, 8, 32), (0, 24, 32, 8)], 'plafond'),
        M('mur_cave_coin_bas_d', 'Cave : coin bas droite', [(24, 0, 8, 32), (0, 24, 32, 8)], 'plafond'),
        D('mur_cave_ouvert', 'Mur de cave ouvert (trou dans la roche, décor)', 'secret', col='#201830'),
        M('escalier_cave_haut', 'ESCALIER de la cave vers le village (haut des marches ; Sortie `escalier`)', [(0, 0, 6, 32), (26, 0, 6, 32)], 'escalier'),
        M('escalier_cave_bas', 'Escalier de la cave, marches (passables)', DOORC, 'escalier'),
        M('piedestal', 'Piédestal de pierre (le Coffre du grand carquois / grand sac de bombes se pose dessus)', OBJ, 'pierre'),
        D('toiles_araignee', 'Toiles d\'araignée (coin de mur, décor)', 'pierre', ghost=True)])

# ---------------------------------------------------------------- forge
S.group('Forge de Corvan (intérieur)', 'Foyer 2×2 (flammes rouges), enclume 1×1 avec le corbeau (objet `StatueCorbeau` dessus), soufflet, établi, bac de trempe, râteliers.')
S.line([M('foyer_haut_g', 'FOYER de forge 2×2, haut gauche (hotte et cheminée)', FULL, 'forge'), M('foyer_haut_d', 'FOYER de forge 2×2, haut droite', FULL, 'forge'),
        M('foyer_bas_g', 'FOYER de forge 2×2, bas gauche (braises)', FULL, 'forge'), M('foyer_bas_d', 'FOYER de forge 2×2, bas droite (braises)', FULL, 'forge'),
        M('enclume_int', 'ENCLUME (perchoir du corbeau : StatueCorbeau dessus)', [(4, 10, 24, 20)], 'metal'),
        M('soufflet', 'Soufflet de forge (à côté du foyer)', OBJ, 'bois_s'), M('etabli_g', 'Établi de forgeron, bout gauche', TABLE, 'bois'),
        M('etabli_d', 'Établi de forgeron, bout droit', TABLE, 'bois')])
S.line([M('bac_trempe_int', 'Bac de trempe', OBJ, 'eau_deco', col='#3a5a8a'), M('rateliers_epees', 'Râtelier d\'épées (contre le mur du fond)', FULL, 'metal'),
        D('outils_muraux', 'Outils accrochés au mur du fond (décor)', 'metal'), M('charbon_int', 'Tas de charbon', OBJ, 'suie'),
        M('meule_int', 'Meule', OBJ, 'metal'), M('armure_socle', 'Armure sur socle', OBJ, 'metal', col='#9aa0b0'),
        M('lingots', 'Étagère de lingots', FULL, 'metal', col='#b8b8c8'), D('bouclier_mural', 'Bouclier accroché au mur (décor)', 'metal')])
S.assemblage('Foyer de forge 2×2', [['foyer_haut_g', 'foyer_haut_d'], ['foyer_bas_g', 'foyer_bas_d']], 'Murs', 'adossé au mur du fond ; recharge de vie : zone Objets devant')

# ---------------------------------------------------------------- herboristerie
S.group('Herboristerie de Mère Hulda', 'Étagères de pots 2 cases de haut, plantes suspendues, comptoir de vente (potions et cœurs).')
S.line([M('etagere_pots_haut_g', 'Étagère de pots, haut, bout gauche', FULL, 'fiole'), M('etagere_pots_haut_m', 'Étagère de pots, haut, milieu', FULL, 'fiole'),
        M('etagere_pots_haut_d', 'Étagère de pots, haut, bout droit', FULL, 'fiole'),
        M('etagere_pots_bas_g', 'Étagère de pots, bas, bout gauche', FULL, 'herbo'), M('etagere_pots_bas_m', 'Étagère de pots, bas, milieu', FULL, 'herbo'),
        M('etagere_pots_bas_d', 'Étagère de pots, bas, bout droit', FULL, 'herbo'),
        D('plantes_suspendues_a', 'Bouquets d\'herbes suspendus au mur (décor)', 'herbo'), D('plantes_suspendues_b', 'Bouquets d\'herbes suspendus, variante', 'herbo')])
S.line([M('table_herbes_g', 'Table de travail aux herbes, bout gauche', TABLE, 'herbo'), M('table_herbes_d', 'Table de travail aux herbes, bout droit', TABLE, 'herbo'),
        M('mortier', 'Mortier et pilon sur pied', OBJ, 'metal'), M('chaudron', 'Chaudron de potion (vert qui bout)', OBJ, 'herbo', col='#3a8a5a'),
        M('plante_pot_a', 'Grande plante en pot, A', OBJ, 'herbo'), M('plante_pot_b', 'Grande plante en pot, B', OBJ, 'herbo'),
        M('plante_pot_c', 'Plante fleurie en pot', OBJ, 'deco'), D('herbes_seches', 'Herbes séchées sur le sol / une corde (décor)', 'herbo')])
S.assemblage('Étagère de pots 3×2', [['etagere_pots_haut_g', 'etagere_pots_haut_m', 'etagere_pots_haut_d'], ['etagere_pots_bas_g', 'etagere_pots_bas_m', 'etagere_pots_bas_d']],
             'Murs', 'adossée au mur du fond (la face haute peut chevaucher le mur)')

# ---------------------------------------------------------------- boutique
S.group('Boutique de Garrick', 'Comptoir en U possible (angles), étagères de marchandises, présentoirs (flèches, bombes, fioles d\'huile, quart de cœur).')
S.line([M('comptoir_g', 'Comptoir de boutique, bout gauche', TABLE, 'bois'), M('comptoir_m', 'Comptoir de boutique, milieu', TABLE, 'bois'),
        M('comptoir_d', 'Comptoir de boutique, bout droit', TABLE, 'bois'), M('comptoir_angle_g', 'Comptoir, angle (coin arrière gauche)', TABLE, 'bois'),
        M('comptoir_angle_d', 'Comptoir, angle (coin arrière droit)', TABLE, 'bois'),
        M('comptoir_v', 'Comptoir vertical (retour du U)', [(4, 0, 24, 32)], 'bois'),
        M('balance', 'Balance sur le comptoir (décor solide)', OBJ, 'metal', col='#d8c060'), M('sac_pieces', 'Sac de pièces sur le comptoir', OBJ, 'etal')])
S.line([M('etagere_march_haut_g', 'Étagère de marchandises, haut, gauche', FULL, 'etal'), M('etagere_march_haut_m', 'Étagère de marchandises, haut, milieu', FULL, 'etal'),
        M('etagere_march_haut_d', 'Étagère de marchandises, haut, droite', FULL, 'etal'),
        M('etagere_march_bas_g', 'Étagère de marchandises, bas, gauche', FULL, 'bois'), M('etagere_march_bas_m', 'Étagère de marchandises, bas, milieu', FULL, 'bois'),
        M('etagere_march_bas_d', 'Étagère de marchandises, bas, droite', FULL, 'bois'),
        M('presentoir_fleches', 'Présentoir à flèches (carquois)', OBJ, 'bois', col='#c8a050'), M('presentoir_bombes', 'Présentoir à bombes', OBJ, 'bois', col='#706080')])
S.line([M('presentoir_fioles', 'Présentoir de fioles d\'huile', OBJ, 'fiole'), M('caisses_march', 'Caisses de marchandises', OBJ, 'bois'),
        M('tonneau_int', 'Tonneau', OBJ, 'bois_s'), M('sacs_int', 'Sacs de grain', OBJ, 'etal', col='#d8c8a0'),
        M('caisse_int', 'Caisse de bois', OBJ, 'bois'), M('jarre_int', 'Jarre', OBJ, 'bois', col='#b86a4a'),
        D('tapis_boutique_h', 'Tapis de comptoir (décor)', 'tapis'), D('rideau_arriere', 'Rideau de l\'arrière-boutique (décor)', 'tissu')])

# ---------------------------------------------------------------- archives
S.group('Archives de Dame Isolde', 'Bibliothèques hautes (2 cases), pupitre, table de lecture, registres, rouleaux, échelle roulante.')
S.line([M('biblio_haut_g', 'Bibliothèque haute, bout gauche (reliures)', FULL, 'livre'), M('biblio_haut_m', 'Bibliothèque haute, milieu', FULL, 'livre'),
        M('biblio_haut_d', 'Bibliothèque haute, bout droit', FULL, 'livre'),
        M('biblio_bas_g', 'Bibliothèque basse, bout gauche', FULL, 'bois'), M('biblio_bas_m', 'Bibliothèque basse, milieu', FULL, 'bois'),
        M('biblio_bas_d', 'Bibliothèque basse, bout droit', FULL, 'bois'),
        M('biblio_rouleaux', 'Casier à rouleaux (1×1)', FULL, 'parchemin'), M('echelle', 'Échelle roulante contre la bibliothèque', FULL, 'bois_s')])
S.line([M('pupitre', 'Pupitre avec livre ouvert', OBJ, 'livre', col='#a86a8a'), M('table_lecture_g', 'Table de lecture, bout gauche', TABLE, 'bois'),
        M('table_lecture_m', 'Table de lecture, milieu', TABLE, 'bois'), M('table_lecture_d', 'Table de lecture, bout droit', TABLE, 'bois'),
        D('registre_ouvert', 'Registre ouvert (posé sur une table, décor)', 'parchemin'), D('parchemins', 'Parchemins épars (décor)', 'parchemin'),
        M('globe', 'Globe / sphère des sceaux', OBJ, 'metal', col='#c8a050'), M('candelabre', 'Candélabre de sol', POST, 'lampe')])
S.assemblage('Bibliothèque 3×2', [['biblio_haut_g', 'biblio_haut_m', 'biblio_haut_d'], ['biblio_bas_g', 'biblio_bas_m', 'biblio_bas_d']], 'Murs', 'adossée au mur du fond')

# ---------------------------------------------------------------- mobilier
S.group('Mobilier : lits, tables, chaises, cheminée', 'Un lit = 2 cases de haut (tête en haut). Cheminée domestique 2×2 (autre que le foyer de forge).')
S.line([M('lit_a_haut', 'Lit A (couverture rouge), tête', [(2, 8, 28, 24)], 'lit'), M('lit_a_bas', 'Lit A, pied', [(2, 0, 28, 28)], 'lit'),
        M('lit_b_haut', 'Lit B (couverture bleue), tête', [(2, 8, 28, 24)], 'tissu'), M('lit_b_bas', 'Lit B, pied', [(2, 0, 28, 28)], 'tissu'),
        M('table_ronde', 'Table ronde', OBJ, 'bois'), M('table_g', 'Table rectangulaire, bout gauche', TABLE, 'bois'),
        M('table_m', 'Table rectangulaire, milieu', TABLE, 'bois'), M('table_d', 'Table rectangulaire, bout droit', TABLE, 'bois')])
S.line([M('chaise_face', 'Chaise vue de face (dossier au fond)', OBJ, 'bois_s'), M('chaise_dos', 'Chaise vue de dos', OBJ, 'bois_s'),
        M('chaise_g', 'Chaise tournée vers la gauche', OBJ, 'bois_s'), M('chaise_d', 'Chaise tournée vers la droite', OBJ, 'bois_s'),
        M('tabouret', 'Tabouret', OBJ, 'bois_s'), M('banc_int', 'Banc', [(0, 14, 32, 16)], 'bois_s'),
        M('buffet_g', 'Buffet, moitié gauche', FULL, 'bois'), M('buffet_d', 'Buffet, moitié droite', FULL, 'bois')])
S.line([M('armoire_haut', 'Armoire, haut', FULL, 'bois_s'), M('armoire_bas', 'Armoire, bas', FULL, 'bois_s'),
        M('cheminee_haut_g', 'CHEMINÉE domestique 2×2, haut gauche (manteau)', FULL, 'pierre'), M('cheminee_haut_d', 'CHEMINÉE domestique 2×2, haut droite', FULL, 'pierre'),
        M('cheminee_bas_g', 'CHEMINÉE domestique 2×2, bas gauche (feu)', FULL, 'forge'), M('cheminee_bas_d', 'CHEMINÉE domestique 2×2, bas droite', FULL, 'forge'),
        M('horloge_haut', 'Horloge à balancier, haut', FULL, 'bois'), M('horloge_bas', 'Horloge à balancier, bas', FULL, 'bois')])
S.line([M('pot_int', 'Pot de terre', OBJ, 'bois'), M('vase', 'Vase avec fleurs', OBJ, 'deco'), M('plante_int', 'Plante verte', OBJ, 'herbo'),
        D('bougie_table', 'Bougie sur table (décor)', 'lampe'), D('lampe_murale', 'Lampe à huile accrochée au mur (décor)', 'lampe'),
        D('tableau', 'Tableau au mur (décor)', 'deco'), D('trophee', 'Trophée de cerf au mur (décor)', 'bois'),
        D('chandelle_sol', 'Cire fondue au sol (décor)', 'lampe')])
S.assemblage('Lit 1×2', [['lit_a_haut'], ['lit_a_bas']], 'Murs', 'tête contre le mur du fond ; variante bleue : lit_b')
S.assemblage('Cheminée 2×2', [['cheminee_haut_g', 'cheminee_haut_d'], ['cheminee_bas_g', 'cheminee_bas_d']], 'Murs', 'adossée au mur du fond')

# ---------------------------------------------------------------- tapis
S.group('Tapis (calque `Decor`)', 'Tapis 3×3 : coins, bords et centre ; sans collision.')
S.line([D('tapis_hg', 'Tapis, coin haut gauche', 'tapis'), D('tapis_h', 'Tapis, bord haut', 'tapis'), D('tapis_hd', 'Tapis, coin haut droite', 'tapis'),
        D('tapis_g', 'Tapis, bord gauche', 'tapis'), D('tapis_centre', 'Tapis, centre', 'tapis', col='#d05050'), D('tapis_d', 'Tapis, bord droit', 'tapis'),
        D('tapis_bg', 'Tapis, coin bas gauche', 'tapis'), D('tapis_b', 'Tapis, bord bas', 'tapis')])
S.line([D('tapis_bd', 'Tapis, coin bas droite', 'tapis'), D('paillasson', 'Paillasson devant la porte de sortie', 'tapis', col='#8a6a3a'),
        D('tapis_etroit_h', 'Chemin de tapis étroit, horizontal', 'tapis'), D('tapis_etroit_v', 'Chemin de tapis étroit, vertical', 'tapis'),
        D('peau_bete', 'Peau de bête', 'terre'), D('tache_encre', 'Tache d\'encre / de suie sur le sol', 'ombre', ghost=True),
        D('rayon_lumiere', 'Rayon de lumière de fenêtre (semi-transparent)', 'lampe', ghost=True), None])
S.assemblage('Tapis 3×3', [['tapis_hg', 'tapis_h', 'tapis_hd'], ['tapis_g', 'tapis_centre', 'tapis_d'], ['tapis_bg', 'tapis_b', 'tapis_bd']], 'Decor', 'peut s\'étirer en répétant tapis_h / tapis_centre')

S.notes += ['Aucun escalier d\'étage : les maisons sont sur un seul niveau ; l\'escalier de la cave de Garrick est `escalier_cave_haut` / `escalier_cave_bas`.',
            'Les coffres, PNJ, statues du corbeau, mur fissuré (objet), Sortie et Spawn sont des **objets Tiled** (calque `Objets`), pas des tuiles : le tileset ne contient que le décor.']

if __name__ == '__main__':
    S.save_all('interieurs.py')
