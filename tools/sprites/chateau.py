"""Tileset `chateau` — intérieur du château de Morvath (salles 01 à 04 et arène de Corvan) — Les Trois Sceaux. ÉTAT : PLAN.

Usage : python tools/sprites/chateau.py
Produit : art/tilesets/chateau.png, chateau_numeros.png, chateau_apercu.png, chateau_plan.md, maps/tilesets/chateau.tsx.
Cartes (maps/chateau/plan.md) : salle_01 à salle_04 (20×11) et salle_boss (20×22).
DISPOSITION : comme `mine` / `sanctuaire` pour ce que le code reconnaît : murs 16-30, portes 40-47, escaliers 56/57, murs fissurés 72-75 -> 76-79,
FOSSE DE RONCES 80-95 (= ravin de `village` / `montagne`). Ids 31-39 et 58-66 VIDES (pas de trou).
RÈGLE : ne jamais déplacer une tuile ; on ajoute dans les lignes de réserve.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chateau_lib import *  # noqa: E402,F401,F403
import chateau_lib as L  # noqa: E402

tsplan.CATS.update(
    pierre='#5a4a7a', tapis='#a02848', mur='#3e3260', porte='#e8782c', arene='#7a6aa0', symbole='#e0c040', socle='#a090b8',
    escalier='#d0c090', armure='#9a9ab0', colonne='#8a7aaa', secret='#a040e0', ronces='#1e1530', rune='#40e0f0', deco='#b0a0c0',
    ombre='#2e2848', niche='#e0b830', tenture='#903070', blason='#c0a030', cercle='#d0a0e8', vitrail='#6080d0')

FAMILLES = ('pierre sombre violette / tapis (rouge sombre) / mur (violet foncé) / porte (orange) / sol d\'arène (violet clair) / '
            'symboles (or) / socle / escalier (beige) / armure / colonne / fissuré à la bombe (violet vif) / ronces (noir-violet) / '
            'rune (cyan) / niche d\'Œil (or) / tenture (magenta) / blason / cercle des sceaux (mauve)')

DEV = """
## POUR LE DÉVELOPPEUR ET LE LEVEL-DESIGNER : ids à connaître

Tileset `chateau` : 8 colonnes, id local Tiled = ligne × 8 + colonne. Salles 01 à 04 et arène du boss.

| Famille | Ids | Calque | À savoir |
| --- | --- | --- | --- |
| **FOSSE DE RONCES = RAVIN** (`TileFeatures`, `TileRules.IsRavine`) | **80 à 95** (80 = sol de base, 81 à 94 bords, 95 = ronces pleines) | `Murs` (bords, 81 à 95) ; `Sol` (80) | **Mêmes ids que le ravin de `village` et `montagne` : ajouter le tileset `chateau` à `TileRules.IsRavine`** (aujourd'hui limité à `village` / `montagne`). Collision par quarts de case dans le `.tsx`, déplacée par le code dans la couche physique « ravin » : Brann et les ennemis ne passent pas, **les flèches passent** (salle 01 : les Œils sont derrière deux fosses). Aucun trou mortel : `HoleRules` ne doit pas reconnaître `chateau`. |
| **MURS FISSURÉS** fermé -> ouvert (`TileRules`, salle 03) | **72 -> 76** (haut), **73 -> 77** (bas), **74 -> 78** (gauche), **75 -> 79** (droite) | fermés `Murs`, ouverts `Decor` | Comme `sanctuaire` : la bombe retire la tuile fermée de `Murs`, le code pose la version ouverte sur `Decor` (ou elle est déjà posée dessous). Ouverts opaques (trou noir). La salle 03 n'utilise qu'une orientation : le mur de la cellule est vertical (74 ou 75). |
| **Escaliers** | 56 (montant), 57 (descendant) | `Sol` | Réservés par cohérence : le château n'a pas d'escalier dans le plan (pas de `Sortie` `transition=escalier`). |
| **Ids VIDES** | 31 à 39 et 58 à 66 | — | Réservés (trous de passage / trous mortels). **Aucun trou : `HoleRules` / `HoleWatcher` n'ont rien à reconnaître ici.** |
| **Mur à rune** (`Porte` `apparence=mur_rune`, type `lanterne`) | tuile dessous : 102 `alcove_sol_rune` | `Sol` | Salle 03 : la `Porte` `chateau_porte_04` (64×32, image `porte_mur_rune.png`) couvre 2 cases de 102 dans la ligne du mur. Mur autour : 103 `mur_rune_grave`. |
| **Cadres de porte** | 40 (haut), 41 (bas), 42 (gauche), 43 (droite) ; 44 à 47 en `Dessus` | `Murs` / `Dessus` | Pour les `Sortie` + `Porte` des salles (9,0) et (9,10), comme `sanctuaire`. |
| **Niche d'Œil** | 99 `mur_niche_oeil` | `Murs` | Case de mur où se pose l'objet `Ennemi` `oeil_morvath` (salle 01 : (3,0) et (16,0)). |
| Piliers 2×2 de l'arène | 120 à 123 | `Murs` | Solides ; les rectangles `pilier` restent la référence du boss. |
| Cercle des sceaux (arène) | 128 à 143 (4×4) | `Sol` | Décor, sans collision, au centre de l'arène. |

Tout le reste est géré par les collisions du `.tsx` (murs 16-30, portes 40-43, 67-70, 72-75, 81-95, 96-101, 103, 113-114, 120-123, 55) : aucun code.
"""

TERRAINS_NOTE = """## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T).

| Terrain | Couleurs | Calque | Tuiles |
| --- | --- | --- | --- |
| `Murs` | `mur` (le reste = vide) | Murs | 16 à 30 |
| `Fosse` | `sol`, `ronces` | `Sol` (80) + `Murs` (81 à 95) | 80 à 95 (même méthode que `Ravin` de `village`) |

"""

S = PSheet('chateau', 8, 'Le château de Morvath, intérieur (pierre sombre, tapis, armures, fosse de ronces, arène de Corvan)',
           ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px. Palette finale : pierre violette sombre (comme la façade de `route_chateau`), '
            'tapis rouge sombre, ronces noires, symboles dorés.',
            '- En PLAN, **la couleur indique la famille** (' + FAMILLES + ') ; une zone plus sombre dans une tuile = zone solide.',
            '- **Pas de trou mortel** (ids 58-66 vides) ; la **fosse de ronces** (80-95) est un ravin : on ne la franchit pas, les flèches passent.',
            '- Salles : `salle_01` à `salle_04` (20×11) et `salle_boss` (20×22) de `maps/chateau/plan.md` ; la cour et la façade sont dans `route_chateau`.'],
           ['`Sol` : pierre, tapis, sol d\'arène, symboles au sol, cercle des sceaux, sol de la fosse (80), alcôve à rune',
            '`Decor` : ombres sous les murs, gravats, ronces au sol, socle de brasero, murs fissurés ouverts',
            '`Murs` : tout ce qui bloque (murs, fosse de ronces, piliers, armures, statues, socle, murs fissurés fermés). Collisions dans le tileset',
            '`Objets` : Sortie, Spawn, Ennemi, Coffre, Porte, Interrupteur, MurFissure, Torche, boss_corvan, pilier, Marqueur… (objets Tiled, pas des tuiles)',
            '`Dessus` : passe devant Brann (haut des armures, statues, colonnes, bannières, encadrement des portes)'])
S.reserve = 4
S.dev, S.terrains_txt = DEV, TERRAINS_NOTE
A = Adder(S)

# ------------------------------------------------------------------ 1. sols
A.grp(0, 'Sols : pierre, tapis, ombres, gravats',
      'Pierre sombre violette (0 à 3, au hasard). Tapis rouge sombre (4 à 10) : bandes verticale/horizontale, bouts et croisement. Ombres 11 à 13 sous les murs (`Decor`).')
A.so(0, 'pierre_a', 'Dalle de pierre sombre violette, de base', 'pierre')
A.so(1, 'pierre_b', 'Dalle de pierre avec reflets', 'pierre')
A.so(2, 'pierre_c', 'Dalle de pierre en joints irréguliers', 'pierre')
A.so(3, 'pierre_fissuree', 'Dalle fissurée, ronces noires dans la fente', 'pierre')
A.so(4, 'tapis_v', 'Tapis rouge sombre, bande verticale (bordures à gauche et à droite)', 'tapis')
A.so(5, 'tapis_h', 'Tapis rouge sombre, bande horizontale (bordures en haut et en bas)', 'tapis')
A.so(6, 'tapis_bout_haut', 'Tapis : extrémité haute (franges)', 'tapis')
A.so(7, 'tapis_bout_bas', 'Tapis : extrémité basse (franges)', 'tapis')
A.so(8, 'tapis_bout_gauche', 'Tapis : extrémité gauche (franges)', 'tapis')
A.so(9, 'tapis_bout_droite', 'Tapis : extrémité droite (franges)', 'tapis')
A.so(10, 'tapis_croix', 'Tapis : croisement (motif central)', 'tapis')
A.de(11, 'ombre_mur_haut', 'Ombre portée d\'un mur du haut sur le sol (trame), sous un mur haut', 'ombre')
A.de(12, 'ombre_mur_gauche', 'Ombre portée d\'un mur de gauche sur le sol', 'ombre')
A.de(13, 'ombre_mur_coin', 'Ombre portée dans un angle haut-gauche (mur en haut et à gauche)', 'ombre')
A.de(14, 'gravats', 'Gravats et éclats de pierre posés au sol', 'deco')
A.de(15, 'ronces_sol', 'Ronces noires qui rampent au sol (corruption de Morvath)', 'ronces')

# ------------------------------------------------------------------ 2. murs
A.grp(16, 'Murs du château (terrain `Murs`)',
      'Pierre violette très sombre, dessus noir, face avant plus claire visible. Toutes pleines. Mêmes numéros et mêmes formes que `mine` / `sanctuaire` (16 à 30).')
A.walls(16, 'mur', 'mur', 'Murs', 'mur', 'mur du château')

A.grp(31, 'Ids réservés : 31 à 39 (vides)', 'Trous de passage des autres donjons : VIDES ici.')

# ------------------------------------------------------------------ 3. portes
A.grp(40, 'Ouvertures de salle (cadre de pierre)',
      'Remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` dans la même case du calque `Dessus`, puis l\'objet `Porte` par-dessus. Mêmes numéros et collisions que `sanctuaire`.')
A.mu(40, 'porte_haut', 'Ouverture dans le mur haut (remplace une tuile mur_haut) ; passage de 20 px au centre, l\'objet Porte se pose dessus', DOORH, 'porte')
A.mu(41, 'porte_bas', 'Ouverture dans le mur bas (remplace une tuile mur_bas) ; passage de 20 px au centre, l\'objet Porte se pose dessus', DOORH, 'porte')
A.mu(42, 'porte_gauche', 'Ouverture dans le mur gauche (remplace une tuile mur_gauche) ; passage de 24 px au centre, l\'objet Porte se pose dessus', DOORV, 'porte')
A.mu(43, 'porte_droite', 'Ouverture dans le mur droite (remplace une tuile mur_droite) ; passage de 24 px au centre, l\'objet Porte se pose dessus', DOORV, 'porte')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    A.du(44 + k, f'porte_{s}_dessus', f'Haut de l\'encadrement de porte_{s}, même case que porte_{s}', 'porte')

# ------------------------------------------------------------------ 4. arène, symboles
A.grp(48, 'Sol d\'arène, symboles au sol (arc, bombe, lanterne), socle',
      'Arène de Corvan : dalles plus claires gravées (48 à 51). Salle 03 : trois petits symboles au sol qui rappellent les trois sceaux : arc (Racines), bombe (Montagne), lanterne (Lac) ; décor sans effet. '
      'Socle de pierre solide (55).')
A.so(48, 'sol_arene_a', 'Dalle d\'arène, violet clair gravé de lignes fines', 'arene')
A.so(49, 'sol_arene_b', 'Dalle d\'arène avec joints en étoile', 'arene')
A.so(50, 'sol_arene_c', 'Dalle d\'arène usée, éclats', 'arene')
A.so(51, 'sol_arene_fissure', 'Dalle d\'arène fissurée, ronces noires', 'arene')
A.so(52, 'symbole_arc', 'Symbole au sol : ARC (sceau des Racines), gravé en or pâle sur dalle de pierre', 'symbole')
A.so(53, 'symbole_bombe', 'Symbole au sol : BOMBE (sceau de la Montagne)', 'symbole')
A.so(54, 'symbole_lanterne', 'Symbole au sol : LANTERNE (sceau du Lac)', 'symbole')
A.mu(55, 'socle', 'Socle de pierre (solide, 1 case)', OBJ, 'socle')

# ------------------------------------------------------------------ 5. escaliers, vides
A.grp(56, 'Escaliers (56/57) ; ids réservés 58 à 66 (vides)',
      'Réservés par cohérence avec les autres donjons (le château n\'a pas d\'escalier dans le plan). 58 à 66 = trous mortels : VIDES ici.')
A.so(56, 'escalier_montant', 'Escalier qui monte (vers le haut de l\'écran), pierre sombre ; la transition serait un objet Sortie', 'escalier')
A.so(57, 'escalier_descendant', 'Escalier qui descend (vers le bas de l\'écran), pierre sombre', 'escalier')

# ------------------------------------------------------------------ 6. armures, statues
A.grp(64, 'Armures, statues, socle de brasero',
      'Armure vide (`armure_base` solide + `armure_haut` en `Dessus` dans la case au-dessus) ; statue de chevalier idem. Socle de brasero : décor sous l\'objet `Torche`.')
A.mu(67, 'armure_base', 'Armure vide sur son support, jambes et socle (solide, base)', BASE, 'armure')
A.du(68, 'armure_haut', 'Armure vide : buste, casque à plume (Dessus, case au-dessus de la base)', 'armure')
A.mu(69, 'statue_base', 'Statue de chevalier, socle et jambes (solide, base)', BASE, 'socle')
A.du(70, 'statue_haut', 'Statue de chevalier, buste et casque (Dessus, case au-dessus de la base)', 'socle')
A.de(71, 'brasero_socle', 'Socle de pierre d\'un brasero (sous l\'objet Torche)', 'niche')

# ------------------------------------------------------------------ 7. murs fissurés
A.grp(72, 'MURS FISSURÉS (bombes) : fermé -> ouvert',
      'Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus, fissures claires). Ouverts : sur `Decor`, opaques (trou noir dans la pierre). '
      'Paires : **72->76, 73->77, 74->78, 75->79** (haut, bas, gauche, droite). La salle 03 n\'utilise qu\'une orientation (mur vertical : 74 ou 75).')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    A.mu(72 + k, f'mur_fissure_{s}', f'MUR FISSURÉ {s} (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l\'ouvre)', FULL, 'secret')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    A.de(76 + k, f'mur_fissure_{s}_ouvert', f'Mur {s} OUVERT : trou noir dans la pierre, gravats (passage dessous)', 'secret')

# ------------------------------------------------------------------ 8. fosse de ronces
A.grp(80, 'FOSSE DE RONCES = RAVIN (terrain `Fosse`, 80 à 95)',
      'Fossé de ronces noires et d\'épines au fond d\'un trou sombre (salle 01 : deux fosses de 5 cases de large devant les Œils). **Infranchissable ; les flèches passent** '
      '(comme le ravin de `village` / `montagne`, mêmes ids). 80 = sol de base (`Sol`) ; 81 à 94 = bords et coins (`Murs`, collision par quarts de case) ; 95 = ronces pleines.', align=16)
S.terrain('Fosse', 'fosse', 'pierre', 'ronces', 'sol', 'ronces', True, 'Pierre (base du terrain Fosse)',
          'Fosse de ronces, case entière (infranchissable)', 'Fosse', layer='Murs')

# ------------------------------------------------------------------ 9. murs de décor
A.grp(96, 'Murs de décor et niche d\'Œil (solides, calque `Murs`)',
      'Variantes pleines des murs : tenture, blason, ronces, vitrail. 99 = niche où se pose l\'objet `Ennemi` `oeil_morvath` (salle 01). Mur à rune : 102/103.')
A.mu(96, 'mur_tenture', 'Mur plein avec tenture violette pendante (variante, solide)', FULL, 'tenture')
A.mu(97, 'mur_blason', 'Mur plein avec blason de l\'Œil de Morvath (variante, solide)', FULL, 'blason')
A.mu(98, 'mur_ronces', 'Mur plein couvert de ronces noires (variante, solide)', FULL, 'ronces')
A.mu(99, 'mur_niche_oeil', 'NICHE D\'ŒIL : cavité de pierre dans le mur du haut, où se place l\'objet Ennemi `oeil_morvath` (solide)', FULL, 'niche')
A.mu(100, 'mur_niche_vide', 'Niche vide dans le mur (variante décorative, solide)', FULL, 'niche')
A.mu(101, 'mur_vitrail', 'Mur plein avec vitrail sombre (variante, solide)', FULL, 'vitrail')
A.so(102, 'alcove_sol_rune', 'Fond d\'alcôve : dalle avec rune cyan discrète (sous le mur à rune ; praticable une fois la porte ouverte)', 'rune')
A.mu(103, 'mur_rune_grave', 'Mur plein avec une rune gravée très discrète (indice, solide)', FULL, 'rune')

# ------------------------------------------------------------------ 10. colonnes, bannières
A.grp(112, 'Colonnes, bannières',
      'Colonne de 1 case = `colonne_base` (Murs, solide) + `colonne_haut` (Dessus) dans la case au-dessus (`O` des salles 01 et 02). Bannières et vitrail plaqués sur une face de mur (Dessus).')
A.du(112, 'colonne_haut', 'Haut de colonne (chapiteau), case au-dessus de colonne_base', 'colonne')
A.mu(113, 'colonne_base', 'Base de colonne de pierre sombre (solide)', BASE, 'colonne')
A.mu(114, 'colonne_brisee', 'Colonne brisée, tronc coupé (solide, 1 seule case)', OBJ, 'colonne')
A.du(115, 'banniere_morvath', 'Bannière noire à l\'Œil doré plaquée sur un mur (Dessus)', 'niche')
A.du(116, 'banniere_dechiree', 'Bannière déchirée plaquée sur un mur (Dessus)', 'deco')
A.du(117, 'vitrail_dessus', 'Reflet de vitrail violet plaqué sur un mur (Dessus)', 'vitrail')

# ------------------------------------------------------------------ 11. piliers 2×2
A.grp(120, 'Piliers 2×2 (arène du boss)',
      'Pilier de 4 cases (quatre piliers 2×2 dans l\'arène) : `pilier_hg` `pilier_hd` / `pilier_bg` `pilier_bd`, tous sur `Murs`, solides. '
      'Les rectangles Tiled nommés `pilier` restent la référence du boss.')
A.mu(120, 'pilier_hg', 'Pilier 2×2 : haut-gauche (solide)', PIL2, 'colonne')
A.mu(121, 'pilier_hd', 'Pilier 2×2 : haut-droite (solide)', PIL2R, 'colonne')
A.mu(122, 'pilier_bg', 'Pilier 2×2 : bas-gauche (solide)', PIL2B, 'colonne')
A.mu(123, 'pilier_bd', 'Pilier 2×2 : bas-droite (solide)', PIL2BR, 'colonne')

# ------------------------------------------------------------------ 12. cercle des sceaux
A.grp(128, 'Cercle des sceaux (arène, 4×4, décor)',
      'Grand cercle gravé au centre de l\'arène (3 cercles entrelacés : arc, bombe, lanterne), 4×4 cases, sur `Sol`, sans collision. '
      'Ids dans l\'ordre ligne par ligne : 128-131 / 132-135 / 136-139 / 140-143 (assemblage `cercle des sceaux`). À poser sur du sol d\'arène 48 à 51.')
for r in range(4):
    for c in range(4):
        A.so(128 + r * 4 + c, f'cercle_{r}{c}', f'Cercle des sceaux, ligne {r + 1} colonne {c + 1}' +
             (' (centre : les trois sceaux)' if r in (1, 2) and c in (1, 2) else ' (anneau)'), 'cercle')

S.assemblage('cercle des sceaux 4×4', [[f'cercle_{r}{c}' for c in range(4)] for r in range(4)], 'Sol',
             'centre de `salle_boss` (par exemple cases (8,8) à (11,11)) ; arène en `sol_arene_*`')
S.assemblage('colonne', [['colonne_haut'], ['colonne_base']], 'Dessus (haut) / Murs (base)')
S.assemblage('armure vide', [['armure_haut'], ['armure_base']], 'Dessus (haut) / Murs (base)')
S.assemblage('pilier 2×2', [['pilier_hg', 'pilier_hd'], ['pilier_bg', 'pilier_bd']], 'Murs')

S.notes += [
    'IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier (fosse = ravin 80-95 ; mur fissuré 72->76 ; aucun id de trou).',
    'Terrains Tiled (Wang par coins) : `Murs` (16 à 30), `Fosse` (80 à 95 : 80 sur `Sol`, 81 à 95 sur `Murs`).',
    'Porte : remplacer la tuile de mur par `porte_<côté>`, poser `porte_<côté>_dessus` dans la même case de `Dessus`, puis l\'objet `Porte`.',
    'Grille de la salle 03 (`chateau_porte_03`) : c\'est une `Porte` dont l\'image `art/puzzles/porte_*_chateau.png` est à dessiner ; sous elle, du sol (`pierre_*`).',
    'Lumière : braseros et torches sont des objets (`Torche`) ; teinte d\'éclipse appliquée par le code.',
    'Aperçu : `art/tilesets/chateau_apercu.png` reconstitue `salle_01`, `salle_03` et `salle_boss` (carrés colorés = objets Tiled).']

# ------------------------------------------------------------------ aperçus
MARK = {'P': '#40ff40', 'X': '#ffff40', 'N': '#ff8030', 'G': '#ff8030', 'I': '#ff8030', 'C': '#ffd040', 'l': '#40d0ff', 'S': '#40d0ff',
        'R': '#40d0ff', 'Y': '#ff8030', 'k': '#ff40ff', 'o': '#ff40ff', 'm': '#ffffff', 'b': '#ffffff', 'h': '#ff6080', 'g': '#ff40ff',
        '1': '#ffff80', '2': '#ffff80', '3': '#ffff80', 'Z': '#ff8030'}


def pick(x, y, names):
    return names[(x * 7 + y * 13) % len(names)]


def cell_sallle(arene):
    floor = ('arene' if arene else 'pierre')

    def cell(x, y, ch, rows):
        names = {k: 'mur_' + k for k in ('haut', 'bas', 'gauche', 'droite', 'plein')}
        if ch == '#':
            return [L.wall_face(rows, x, y, '.PXNGIOYCSlfmbhk~123gZR', names)]
        if ch == 'o':
            return ['mur_niche_oeil'] if y == 0 else [floor + '_a']
        if ch == 'F':
            return ['mur_fissure_gauche']
        if ch == 'Z':
            return ['alcove_sol_rune']
        if ch == '~':
            return ['fosse_plein']
        if ch in 'NGX' and (y in (0, 10, 21)):
            return ['porte_haut' if y == 0 else 'porte_bas']
        if arene:
            base = [pick(x, y, ['sol_arene_a', 'sol_arene_a', 'sol_arene_b', 'sol_arene_c'])]
        else:
            base = [pick(x, y, ['pierre_a', 'pierre_a', 'pierre_b', 'pierre_c'])]
        if ch == 'O':
            base.append('colonne_base')
        if ch == 'Y':
            base.append('brasero_socle')
        return base
    return cell


def apercu():
    maps = L.parse_maps(os.path.join(ROOT, 'maps', 'chateau', 'plan.md'))

    def boss_cell(x, y, ch, rows):
        # piliers 2x2 : OO/OO ; cercle des sceaux 4x4 au centre (cases 8..11, 9..12 de l'arène)
        if ch == 'O':
            up = y > 0 and rows[y - 1][x] == 'O'
            left = x > 0 and rows[y][x - 1] == 'O'
            return ['pierre_a', 'pilier_' + ('b' if up else 'h') + ('d' if left else 'g')]
        if 9 <= y <= 12 and 8 <= x <= 11:
            return ['sol_arene_a', f'cercle_{y - 9}{x - 8}']
        return cell_sallle(True)(x, y, ch, rows)

    a = L.render(S, maps['salle_01'], cell_sallle(False), MARK)
    b = L.render(S, maps['salle_03'], cell_sallle(False), MARK)
    c = L.render(S, maps['salle_boss'], boss_cell, MARK)
    W = len(a[0]) + 16 + len(c[0])
    left = L.stack([a, b])
    H = max(len(left), len(c))
    img = [[(14, 12, 24, 255)] * W for _ in range(H)]
    for y, row in enumerate(left):
        for x, px in enumerate(row):
            img[y][x] = px
    for y, row in enumerate(c):
        for x, px in enumerate(row):
            if px:
                img[y][len(a[0]) + 16 + x] = px
    save_png(os.path.join(ROOT, 'art', 'tilesets', 'chateau_apercu.png'), img)
    return maps


def final_md(md):
    md = md.replace('**État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro)',
                    '**État : FINAL** (dessin final de toutes les tuiles ; les numéros sont ceux du plan, aucune tuile n\'a bougé)')
    md = md.replace('**État : PLAN**', '**État : FINAL**')
    a = md.index('- Vue de dessus 3/4')
    b = md.index(chr(10), a)
    b2 = md.index(chr(10), b + 1)
    md = md[:a] + ('- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px sur les objets (pas sur les dalles de sol). Palette : pierre violette '
                   'sombre (dalles, murs presque noirs, faces violet clair), tapis rouge sombre à bordure d\'or, ronces noires et violettes, '
                   'runes cyan, symboles dorés. Dessin : `tools/sprites/chateau_art.py` (+ `chateau_objets.py`, `chateau_pierre.py`) ; '
                   'les bords de la fosse (81 à 94) sont fondus par `tools/sprites/fondus.py chateau`.') + md[b:]
    a = md.index('- En PLAN, **la couleur')
    b = md.index(chr(10), a)
    md = md[:a] + '- Les collisions sont dans le tileset (colonne Collision de chaque tableau).' + md[b:]
    md = md.replace('Ouverts opaques (trou noir).', 'Ouverts entièrement opaques (brèche noire irrégulière, gravats devant).')
    md = md.replace('aplats colorés', 'dessin final')
    md = md.replace('Aperçu : `art/tilesets/chateau_apercu.png` reconstitue `salle_01`, `salle_03` et `salle_boss` (carrés colorés = objets Tiled).',
                    'Aperçu : `art/tilesets/chateau_apercu.png` reconstitue les vraies cartes (`salle_01` à `salle_04` et `salle_boss`) avec les tuiles finales (`tools/sprites/chateau_apercu_cartes.py`) ; les objets Tiled ne sont pas dessinés.')
    return md


def main_final():
    import final_lib
    import chateau_art
    import fondus
    import fondus_lib
    S.finish()
    px = final_lib.render(S, chateau_art.REG)
    out_t = os.path.join(ROOT, 'art', 'tilesets')
    save_png(os.path.join(out_t, 'chateau.png'), px)
    fondus.STYLES['chateau'] = {'Fosse': fondus.ravin}
    fondus.patch('chateau')
    px2 = fondus_lib.read_png(os.path.join(out_t, 'chateau.png'))
    px2 = [[None if p[3] == 0 else tuple(p) for p in row] for row in px2]
    save_png(os.path.join(out_t, 'chateau_numeros.png'), final_lib.numbered(S, px2))
    with open(os.path.join(out_t, 'chateau_plan.md'), 'w', encoding='utf-8', newline=chr(10)) as f:
        f.write(final_md(S.md('chateau.py')))
    print('chateau : dessin final,', len(S.tiles), 'tuiles.')


def main():
    S.save_all('chateau.py')
    apercu()


if __name__ == '__main__':
    if '--plan' in sys.argv:
        main()
    else:
        main_final()
