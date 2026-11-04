"""Tileset `route_chateau` — route de l'est, falaise, grotte noire, façade et cour du château — Les Trois Sceaux. ÉTAT : PLAN.

Usage : python tools/sprites/route_chateau.py
Produit : art/tilesets/route_chateau.png, route_chateau_numeros.png, route_chateau_apercu.png, route_chateau_plan.md,
          maps/tilesets/route_chateau.tsx.
Cartes qui l'utilisent (maps/chateau/plan.md §4) : route_falaise (40×11), passage_falaise (20×22, grotte), chateau (20×22, la cour).
DISPOSITION : ids reconnus par le code comme `mine` / `sanctuaire` : murs 16-30, escaliers 56/57, murs fissurés 72-75 -> 76-79 ;
ids 31-39, 58-66 et 80-95 VIDES (pas de trou ni de ravin ici). RÈGLE : ne jamais déplacer une tuile ; on ajoute dans les lignes de réserve.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chateau_lib import *  # noqa: E402,F401,F403
import chateau_lib as L  # noqa: E402

tsplan.CATS.update(
    pave='#9a96a8', herbe='#5a7a5a', dalle='#6e6288', grotte='#6a5448', falaise='#8a7460', roche='#4a4038', sommet='#5a4e44',
    facade='#6a5a80', portail='#8a50b0', creneau='#7a6a90', rempart='#605078', niche='#e0b830', poterne='#c07040', secret='#a040e0',
    rocher='#8a8078', stalag='#6a5e58', statue='#a090b8', deco='#b0a0c0', brasero='#e8782c', rune='#40e0f0', escalier='#d0c090',
    bouche='#8a7060', ombre='#3a3050', seuil='#2a2038')

FAMILLES = ('pavés de la route (gris) / herbe d\'éclipse (vert froid) / dalles de la cour (violet-gris) / sol de grotte (brun) / '
            'falaise (brun clair) / roche de grotte (brun sombre) / façade (violet) / portail (mauve) / créneaux / rempart / '
            'niche de l\'Œil (or) / poterne (orange-brun) / fissuré à la bombe (violet vif) / rocher / statue / brasero (orange) / rune (cyan)')

DEV = """
## POUR LE DÉVELOPPEUR ET LE LEVEL-DESIGNER : ids à connaître

Tileset `route_chateau` : 8 colonnes, id local Tiled = ligne × 8 + colonne. Un seul PNG pour trois cartes : `route_falaise` (falaise), `passage_falaise` (grotte), `chateau` (cour).

| Famille | Ids | Calque | À savoir |
| --- | --- | --- | --- |
| **MURS FISSURÉS** fermé -> ouvert (`TileRules`) | **72 -> 76** (haut, **utilisé : la poterne de la cour**), 73 -> 77 (bas), 74 -> 78 (gauche), 75 -> 79 (droite) | fermés `Murs`, ouverts `Decor` | Comme `sanctuaire` 72 -> 76 : la bombe retire la tuile fermée de `Murs`, le code pose la version ouverte sur `Decor` (ou elle est déjà posée dessous). Les versions ouvertes sont opaques (arche noire). Seule l'orientation `haut` sert dans le plan ; les trois autres sont réservées et peuvent rester en aplat. La poterne se peint en 72 (fissurée) sur la dernière rangée de la façade, case (4,4) de `chateau`. |
| **Poterne** (famille) | 128 `poterne_fermee` (murée sans fissure), 72 `poterne_fissuree`, 76 `poterne_ouverte`, 129 arche (Dessus), 130 seuil (Sol) | voir tableau | `poterne_fermee` n'est pas dans le plan (la fissure se voit dès l'arrivée) : variante de repli. |
| **Escaliers** | 56 `perron_montant`, 57 `perron_descendant` | `Sol` | Marches du perron devant le portail. **Aucune `Sortie` `transition=escalier` prévue dans ce tileset** (réservés pour la cohérence avec les autres donjons). |
| **Ids VIDES** | 31 à 39, 58 à 66, **80 à 95** | — | Réservés (trous de passage / trous mortels / **ravin**). Ce tileset n'a ni trou ni ravin : **ne PAS ajouter `route_chateau` à `HoleRules`, `HoleWatcher` ni `TileRules.IsRavine`** (le fossé de ronces est dans `chateau`). |
| **Mur à rune** (`Porte` `apparence=mur_rune`, type `lanterne`) | tuile dessous : 46 `alcove_sol_rune` | `Sol` | L'image `art/puzzles/porte_mur_rune.png` (64×32) est posée par la `Porte` sur 2 cases de 46. Mur autour : 47 `mur_rune_grave` (solide, indice discret). |
| **Braseros** | 48 (route), 49 (grotte) | `Decor` | Socle décoratif sans collision, **sous** l'objet `Torche` (`permanente`) qui porte le vrai brasero et sa collision. |
| **Portail scellé** 2×3 | 120 à 125 | `Murs` | Décor solide (symbole de l'Œil), voir assemblage. |

Tout le reste est géré par les collisions du `.tsx` (murs 16-30, 96-111, 136-151, façade 112-127, rochers 67-70, statues 152-155, 40-43, 47, 55, 71, 128) : aucun code.
"""

TERRAINS_NOTE = """## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain n'a qu'une couleur (le reste = vide) ; il se peint sur `Murs` (les bords montrent le sol de dessous).

| Terrain | Couleur | Tuiles | Où |
| --- | --- | --- | --- |
| `Falaise` | falaise | 16 à 30 | `route_falaise` : bords nord et sud de la route (face de falaise brun clair) |
| `Roche de la grotte` | roche | 96 à 110 (111 = variante pleine) | `passage_falaise` : parois |
| `Rempart` | rempart | 136 à 150 (151 = variante pleine) | `chateau` : murs gauche, droit et bas de la cour |

"""

S = PSheet('route_chateau', 8, 'La route de la falaise, la grotte noire et la cour du château (fin du jeu)',
           ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px. Palette finale : extérieur sous éclipse (violets froids, '
            'verts éteints), grotte brun sombre, château pierre violette ; les mêmes tuiles servent le jour (route, étapes 0 à 2) et sous la teinte d\'éclipse (code).',
            '- En PLAN, **la couleur indique la famille** (' + FAMILLES + ') ; une zone plus sombre dans une tuile = zone solide.',
            '- Cartes : `route_falaise`, `passage_falaise`, `chateau` (cour) de `maps/chateau/plan.md`. Les salles intérieures du château utilisent le tileset `chateau`.',
            '- **Pas de trou ni de ravin** dans ce tileset (ids 58-66 et 80-95 vides).'],
           ['`Sol` : pavés de la route, herbe d\'éclipse, dalles de la cour, sol de grotte, perron, seuil de poterne, alcôve à rune',
            '`Decor` : socles de braseros, lueurs, cailloux, ronces au pied des murs, flaques, herbe haute, poterne ouverte',
            '`Murs` : tout ce qui bloque (falaise, roche, rempart, façade, portail, rochers, stalagmites, statues, murs fissurés fermés). Collisions dans le tileset',
            '`Objets` : Sortie, Spawn, Ennemi, Porte, MurFissure, StatueCorbeau, Torche, Marqueur, Scenario… (objets Tiled, pas des tuiles)',
            '`Dessus` : passe devant Brann (arches, haut des statues, bannières)'])
S.reserve = 4
S.dev, S.terrains_txt = DEV, TERRAINS_NOTE
A = Adder(S)

# ------------------------------------------------------------------ 1. sols
A.grp(0, 'Sols : pavés, herbe d\'éclipse, dalles de la cour, sol de grotte',
      'Route : pavés (0 à 4, au hasard) et herbe d\'éclipse (5 à 7). Cour : dalles (8 à 11) et dalle de l\'Œil (12, devant le portail, une seule fois). '
      'Grotte : sol brun (13 à 15).')
A.so(0, 'pave_a', 'Pavé de la route de base (gris)', 'pave')
A.so(1, 'pave_b', 'Pavé de la route avec joints usés', 'pave')
A.so(2, 'pave_c', 'Pavé de la route avec petits cailloux', 'pave')
A.so(3, 'pave_fissure', 'Pavé fissuré de la route', 'pave')
A.so(4, 'pave_herbe', 'Pavés envahis par l\'herbe (bord de route)', 'pave')
A.so(5, 'herbe_eclipse_a', 'Herbe d\'éclipse de base (vert froid, éteint)', 'herbe')
A.so(6, 'herbe_eclipse_b', 'Herbe d\'éclipse avec touffes', 'herbe')
A.so(7, 'herbe_eclipse_fleurs', 'Herbe d\'éclipse avec fleurs violettes', 'herbe')
A.so(8, 'dalle_cour_a', 'Dalle de la cour du château, de base (violet-gris)', 'dalle')
A.so(9, 'dalle_cour_b', 'Dalle de la cour avec reflets', 'dalle')
A.so(10, 'dalle_cour_c', 'Dalle de la cour en joints irréguliers', 'dalle')
A.so(11, 'dalle_cour_fissuree', 'Dalle de la cour fissurée, ronces noires dans la fente', 'dalle')
A.so(12, 'dalle_cour_oeil', 'Dalle gravée de l\'Œil de Morvath (devant le portail, une seule fois)', 'rune')
A.so(13, 'grotte_sol_a', 'Sol de la grotte noire, de base (brun)', 'grotte')
A.so(14, 'grotte_sol_b', 'Sol de la grotte avec veines claires', 'grotte')
A.so(15, 'grotte_sol_cailloux', 'Sol de la grotte avec cailloux', 'grotte')

# ------------------------------------------------------------------ 2. falaise
A.grp(16, 'Falaise de la route (terrain `Falaise`, 16 à 30 ; 31 vide)',
      'Face de falaise brun clair : arête sombre en haut, face verticale visible, pied dans l\'ombre. Toutes pleines. Mêmes numéros et mêmes formes que `mine` / `sanctuaire` 16 à 30. '
      'Dans `route_falaise`, les bords nord et sud de la route sont des falaises ; l\'intérieur des massifs se remplit de 28 (plein) ou de `falaise_sommet`.')
A.walls(16, 'falaise', 'falaise', 'Falaise', 'falaise', 'falaise de la route')
A.grp(31, 'Ids réservés : 31 à 39 (vides)',
      'Trous de passage des donjons : ce tileset n\'en a pas, ces cases restent VIDES (ne rien y dessiner).')

# ------------------------------------------------------------------ 3. bouche de grotte
A.grp(40, 'Bouche de grotte (cadre de pierre) et alcôve à rune',
      'Alcôve de la `Sortie` de `route_falaise` (cases (33,1) et (34,1)) : `alcove_sol_rune` sur `Sol` ×2, jambages 42/43 de chaque côté, linteau 40/41 au-dessus (rangée 0), '
      'la `Porte` mur à rune posée sur les deux cases de la rangée 2. Arche 44/45 sur `Dessus`.')
A.mu(40, 'bouche_linteau_g', 'Linteau gauche de la bouche de grotte (pierre taillée, solide)', FULL, 'bouche')
A.mu(41, 'bouche_linteau_d', 'Linteau droit de la bouche de grotte (solide)', FULL, 'bouche')
A.mu(42, 'bouche_jambage_g', 'Jambage gauche de la bouche de grotte (solide)', FULL, 'bouche')
A.mu(43, 'bouche_jambage_d', 'Jambage droit de la bouche de grotte (solide)', FULL, 'bouche')
A.du(44, 'bouche_arche_g', 'Arche : retombée gauche, passe devant Brann (même case que bouche_jambage_g)', 'bouche')
A.du(45, 'bouche_arche_d', 'Arche : retombée droite, passe devant Brann (même case que bouche_jambage_d)', 'bouche')
A.so(46, 'alcove_sol_rune', 'Fond d\'alcôve : dalle avec rune cyan discrète (sous le mur à rune ; praticable une fois la porte ouverte)', 'rune')
A.mu(47, 'mur_rune_grave', 'Mur plein avec une rune gravée très discrète (indice, solide)', FULL, 'rune')

# ------------------------------------------------------------------ 4. décor
A.grp(48, 'Décor sans collision, sommet de falaise',
      'Socles de braseros (sous l\'objet `Torche`), lueur de rune, cailloux, ronces et flaques. Le sommet de falaise (55 et 71) remplit les massifs inaccessibles.')
A.de(48, 'brasero_socle_route', 'Socle de pierre d\'un brasero extérieur (sous l\'objet Torche)', 'brasero')
A.de(49, 'brasero_socle_grotte', 'Socle de roche d\'un brasero de grotte (sous l\'objet Torche)', 'brasero')
A.de(50, 'lueur_rune', 'Tache de lueur cyan au sol (semi-transparente, près des runes)', 'rune')
A.de(51, 'cailloux', 'Cailloux et gravats posés au sol', 'deco')
A.de(52, 'ronces_pied_mur', 'Ronces noires au pied d\'un mur (corruption de Morvath)', 'ombre')
A.de(53, 'flaque_eclipse', 'Flaque sombre reflétant le ciel d\'éclipse', 'ombre')
A.de(54, 'herbe_haute_eclipse', 'Herbe haute d\'éclipse (touffe sans collision)', 'herbe')
A.mu(55, 'falaise_sommet_a', 'Sommet de falaise, rocher brun-gris (pleine, massif inaccessible)', FULL, 'sommet')

# ------------------------------------------------------------------ 5. escaliers et vides
A.grp(56, 'Perron (56/57) ; ids réservés 58 à 66 (vides)',
      'Marches devant le portail du château (praticables). Aucune `Sortie` d\'escalier prévue. 58 à 66 = trous des autres donjons : VIDES ici.')
A.so(56, 'perron_montant', 'Marches du perron qui montent (vers le haut de l\'écran), pierre violette', 'escalier')
A.so(57, 'perron_descendant', 'Marches du perron qui descendent (vers le bas de l\'écran)', 'escalier')

# ------------------------------------------------------------------ 6. rochers
A.grp(64, 'Rochers, stalagmites (solides)',
      'Rochers de la route (`O` des aperçus de `route_falaise`), stalagmites de la grotte (`O` de `passage_falaise`). Corps solide à la base.')
A.mu(67, 'rocher_a', 'Rocher brun-gris posé sur la route (solide)', OBJ, 'rocher')
A.mu(68, 'rocher_b', 'Rocher brun-gris, variante plus haute (solide)', OBJ, 'rocher')
A.mu(69, 'stalagmite_a', 'Stalagmite de la grotte, petite (solide)', OBJ, 'stalag')
A.mu(70, 'stalagmite_b', 'Stalagmite de la grotte, haute (solide)', OBJ, 'stalag')
A.mu(71, 'falaise_sommet_b', 'Sommet de falaise, variante avec ronces (pleine)', FULL, 'sommet')

# ------------------------------------------------------------------ 7. murs fissurés
A.grp(72, 'MURS FISSURÉS (bombes) : fermé -> ouvert',
      'Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus). Ouverts : sur `Decor`, opaques (arche noire). Paires : **72->76, 73->77, 74->78, 75->79** (haut, bas, gauche, droite). '
      'Seul `haut` est utilisé (poterne). Habillage = pierre de la façade.')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    A.mu(72 + k, f'mur_fissure_{s}' if k else 'poterne_fissuree',
         f'MUR FISSURÉ {s}' + (' = POTERNE FISSURÉE de la cour (face de façade fissurée, objet MurFissure dessus, la bombe l\'ouvre)' if k == 0 else ' (réservé)'),
         FULL, 'secret')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    A.de(76 + k, f'mur_fissure_{s}_ouvert' if k else 'poterne_ouverte',
         f'Mur {s} OUVERT' + (' = POTERNE OUVERTE : arche noire, gravats (passage dessous)' if k == 0 else ' (réservé)'), 'secret')

# ------------------------------------------------------------------ 8. ids 80-95 vides
A.grp(80, 'Ids réservés : 80 à 95 (vides)', 'Ravin des autres tilesets : VIDE ici (ne rien y dessiner).')

# ------------------------------------------------------------------ 9. roche de grotte
A.grp(96, 'Roche de la grotte noire (terrain `Roche de la grotte`, 96 à 110 ; 111 variante pleine)',
      'Mêmes formes que la falaise, roche brun très sombre, quelques reflets. Toutes pleines.')
A.walls(96, 'grotte', 'roche', 'Roche de la grotte', 'roche', 'roche de la grotte')
A.mu(111, 'grotte_plein_b', 'Roche de grotte pleine, variante à veines (mélanger avec 108)', FULL, 'roche')

# ------------------------------------------------------------------ 10. façade
A.grp(112, 'Façade du château (calque `Murs`)',
      'Cinq rangées en haut de la cour : créneaux (rangée 0), mur (rangées 1 à 3), pied de mur avec ronces (rangée 4, c\'est là que se pose la poterne et la niche d\'Œil). '
      'Toutes solides.')
A.mu(112, 'facade_creneau_a', 'Créneaux de la façade, merlon (solide)', FULL, 'creneau')
A.mu(113, 'facade_creneau_b', 'Créneaux de la façade, creux (solide)', FULL, 'creneau')
A.mu(114, 'facade_mur_a', 'Mur de la façade, pierre violette (solide)', FULL, 'facade')
A.mu(115, 'facade_mur_b', 'Mur de la façade, variante avec fenêtre étroite (solide)', FULL, 'facade')
A.mu(116, 'facade_pied', 'Pied de la façade, ronces noires (solide)', FULL, 'facade')
A.mu(117, 'facade_niche_oeil', 'NICHE D\'ŒIL : cavité de pierre au pied de la façade, où se place l\'objet Ennemi `oeil_morvath` (solide)', FULL, 'niche')
A.mu(118, 'facade_niche_vide', 'Niche de pierre vide (variante décorative, solide)', FULL, 'niche')
A.mu(119, 'facade_coin_tour', 'Angle de tour de la façade (solide)', FULL, 'creneau')

A.grp(120, 'Portail scellé du château (2×3, symbole de l\'Œil)',
      'Grand portail de 2 cases de large et 3 de haut, scellé : décor solide infranchissable. Assemblage `portail` : voir plus bas.')
for k, n in enumerate(('hg', 'hd', 'mg', 'md', 'bg', 'bd')):
    A.mu(120 + k, f'portail_{n}', 'Portail scellé, ' + {'h': 'arc du haut', 'm': 'milieu avec l\'Œil', 'b': 'bas, seuil scellé'}[n[0]] +
         (' gauche' if n[1] == 'g' else ' droit') + ' (solide)', FULL, 'portail')
A.mu(126, 'facade_mur_ronces', 'Mur de la façade couvert de ronces noires (variante, solide)', FULL, 'facade')
A.mu(127, 'facade_blason', 'Mur de la façade avec blason de l\'Œil (variante, solide)', FULL, 'facade')

A.grp(128, 'Poterne : état fermé, arche et seuil',
      'La poterne est une porte dérobée dans le pied de la façade. États : `poterne_fermee` (murée, sans fissure ; repli), 72 `poterne_fissuree`, 76 `poterne_ouverte`.')
A.mu(128, 'poterne_fermee', 'POTERNE FERMÉE : arche murée, sans fissure (solide ; variante de repli)', FULL, 'poterne')
A.du(129, 'poterne_arche', 'Arche en pierre au-dessus de la poterne ouverte (Dessus, même case que poterne_ouverte)', 'poterne')
A.so(130, 'poterne_seuil', 'Seuil sombre sous la poterne (Sol, sous poterne_ouverte)', 'seuil')

# ------------------------------------------------------------------ 11. rempart
A.grp(136, 'Rempart de la cour (terrain `Rempart`, 136 à 150 ; 151 variante pleine)',
      'Murs gauche, droit et bas de la cour : pierre violette, créneaux vus du dessus, face visible côté cour. Toutes pleines.', align=8)
A.walls(136, 'rempart', 'rempart', 'Rempart', 'rempart', 'rempart de la cour')
A.mu(151, 'rempart_plein_b', 'Rempart plein, variante avec ronces (mélanger avec 148)', FULL, 'rempart')

# ------------------------------------------------------------------ 12. statues, piliers
A.grp(152, 'Statues de chevaliers, piliers de la cour',
      'Statue de chevalier (`O` de la cour) : `statue_chevalier_base` (Murs, solide) + `statue_chevalier_haut` (Dessus) dans la case au-dessus. Abri contre le Chevalier corrompu.')
A.mu(152, 'statue_chevalier_base', 'Statue de chevalier, socle et jambes (solide, base)', BASE, 'statue')
A.du(153, 'statue_chevalier_haut', 'Statue de chevalier, buste et casque (Dessus, case au-dessus de la base)', 'statue')
A.mu(154, 'statue_chevalier_b_base', 'Statue de chevalier, pose de garde, socle (solide)', BASE, 'statue')
A.du(155, 'statue_chevalier_b_haut', 'Statue de chevalier, pose de garde, buste (Dessus)', 'statue')
A.mu(156, 'pilier_cour', 'Pilier de pierre brisé de la cour (solide)', OBJ, 'statue')
A.du(157, 'banniere_morvath', 'Bannière noire à l\'Œil doré plaquée sur un mur (Dessus)', 'niche')
A.du(158, 'banniere_dechiree', 'Bannière déchirée plaquée sur un mur (Dessus)', 'deco')

S.assemblage('portail 2×3', [['portail_hg', 'portail_hd'], ['portail_mg', 'portail_md'], ['portail_bg', 'portail_bd']], 'Murs',
             'case (9,2) de `chateau` ; le perron (56/57) se pose devant en `Sol`')
S.assemblage('bouche de grotte', [['bouche_linteau_g', 'bouche_linteau_d'], ['bouche_jambage_g', 'bouche_jambage_d']], 'Murs',
             'complète l\'alcôve ; l\'alcôve elle-même est `alcove_sol_rune` ×2 sur `Sol`')
S.assemblage('statue de chevalier', [['statue_chevalier_haut'], ['statue_chevalier_base']], 'Dessus (haut) / Murs (base)')

S.notes += [
    'IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier (mur fissuré 72->76 ; aucun id de trou ni de ravin).',
    'Terrains Tiled : `Falaise` (16-30), `Roche de la grotte` (96-110), `Rempart` (136-150), tous sur le calque `Murs`.',
    'Porte `mur_rune` : l\'image `art/puzzles/porte_mur_rune.png` existe déjà (64×32 : fermée, ouverte).',
    'Lumière : braseros et lueurs sont des objets (`Torche`) ou gérés par le code (grotte en `penombre`), pas des tuiles.',
    'Teinte d\'éclipse (étape 3) : appliquée par le code sur toute la salle, il n\'y a pas de variante de couleur dans le PNG.',
    'Aperçu : `art/tilesets/route_chateau_apercu.png` reconstitue les trois cartes ASCII de `maps/chateau/plan.md` avec les aplats (carrés colorés = objets Tiled).']

# ------------------------------------------------------------------ aperçus
MARK = {'P': '#40ff40', 'X': '#ffff40', 'R': '#40d0ff', 'Y': '#ff8030', 'r': '#e04040', 's': '#e04040', 'c': '#c0a060', 'u': '#6080ff',
        'k': '#ff40ff', 'o': '#ff40ff', 'f': '#ffffff', 'Z': '#ff8030'}


def pick(x, y, names):
    return names[(x * 7 + y * 13) % len(names)]


def cell_route(x, y, ch, rows):
    if ch == '#':
        return [L.wall_face(rows, x, y, '.XZPRrscO', {k: 'falaise_' + k for k in ('haut', 'bas', 'gauche', 'droite', 'plein')})]
    if ch == 'X' and y + 1 < len(rows) and rows[y + 1][x] == 'Z':
        return ['alcove_sol_rune']
    if ch == 'Z':
        return ['alcove_sol_rune']
    base = [pick(x, y, ['pave_a', 'pave_a', 'pave_b', 'pave_c', 'pave_herbe'])]
    if ch == 'O':
        base.append(pick(x, y, ['rocher_a', 'rocher_b']))
    return base


def cell_grotte(x, y, ch, rows):
    if ch == '#':
        return [L.wall_face(rows, x, y, '.XZPuYOf', {k: 'grotte_' + k for k in ('haut', 'bas', 'gauche', 'droite', 'plein')})]
    if ch == 'Z':
        return ['alcove_sol_rune']
    base = [pick(x, y, ['grotte_sol_a', 'grotte_sol_a', 'grotte_sol_b', 'grotte_sol_cailloux'])]
    if ch == 'Y':
        base.append('brasero_socle_grotte')
    if ch == 'O':
        base.append(pick(x, y, ['stalagmite_a', 'stalagmite_b']))
    return base


def cell_cour(x, y, ch, rows):
    if y <= 4:                                           # façade
        if y == 0:
            return ['facade_creneau_a' if x % 2 == 0 else 'facade_creneau_b']
        if ch == 'H':
            return ['portail_' + 'hmb'[y - 2] + ('g' if x == 9 else 'd')]
        if y == 4:
            return {'F': ['poterne_fissuree'], 'o': ['facade_niche_oeil']}.get(ch, ['facade_pied'])
        return ['facade_mur_b' if x in (4, 15) else 'facade_mur_a']
    if ch == '#':
        return [L.wall_face(rows, x, y, '.XPRkO', {k: 'rempart_' + k for k in ('haut', 'bas', 'gauche', 'droite', 'plein')})]
    base = [pick(x, y, ['dalle_cour_a', 'dalle_cour_a', 'dalle_cour_b', 'dalle_cour_c'])]
    if ch == 'O':
        base.append('statue_chevalier_base')
    return base


def apercu():
    maps = L.parse_maps(os.path.join(ROOT, 'maps', 'chateau', 'plan.md'))
    imgs = [L.render(S, maps['route_falaise'], cell_route, MARK),
            L.render(S, maps['passage_falaise'], cell_grotte, MARK),
            L.render(S, maps['chateau'], cell_cour, MARK)]
    # cour à côté de la grotte pour garder une image compacte
    g, c = imgs[1], imgs[2]
    W = len(g[0]) + 16 + len(c[0])
    H = max(len(g), len(c))
    side = [[(14, 12, 24, 255)] * W for _ in range(H)]
    for y, row in enumerate(g):
        for x, px in enumerate(row):
            if px:
                side[y][x] = px
    for y, row in enumerate(c):
        for x, px in enumerate(row):
            if px:
                side[y][len(g[0]) + 16 + x] = px
    save_png(os.path.join(ROOT, 'art', 'tilesets', 'route_chateau_apercu.png'), L.stack([imgs[0], side]))
    return maps


def final_md(md):
    md = md.replace('**État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro)',
                    '**État : FINAL** (dessin final de toutes les tuiles ; les numéros sont ceux du plan, aucune tuile n\'a bougé)')
    md = md.replace('**État : PLAN**', '**État : FINAL**')
    a = md.index('- Vue de dessus 3/4')
    b = md.index(chr(10), a)
    md = md[:a] + ('- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px sur les objets (pas sur les sols). Palette : pavés gris-violet, '
                   'herbe d\'éclipse vert froid éteint, falaise brun clair, grotte brun très sombre, façade et cour pierre violette, runes cyan, ronces noires ; '
                   'les mêmes tuiles servent le jour (route, étapes 0 à 2) et sous la teinte d\'éclipse (code). '
                   'Dessin : `tools/sprites/route_chateau_art.py` (+ `chateau_art.py`, `chateau_objets.py`, `chateau_pierre.py`).') + md[b:]
    a = md.index('- En PLAN, **la couleur')
    b = md.index(chr(10), a)
    md = md[:a] + '- Les collisions sont dans le tileset (colonne Collision de chaque tableau).' + md[b:]
    md = md.replace('Les versions ouvertes sont opaques (arche noire).', 'Les versions ouvertes sont entièrement opaques (brèche noire irrégulière, gravats devant).')
    md = md.replace('Aperçu : `art/tilesets/route_chateau_apercu.png` reconstitue les trois cartes ASCII de `maps/chateau/plan.md` avec les aplats (carrés colorés = objets Tiled).',
                    'Aperçu : `art/tilesets/route_chateau_apercu.png` reconstitue les vraies cartes (`route_falaise`, `passage_falaise`, `chateau`) avec les tuiles finales (`tools/sprites/chateau_apercu_cartes.py`) ; les objets Tiled ne sont pas dessinés.')
    return md


def main_final():
    import final_lib
    import route_chateau_art
    S.finish()
    px = final_lib.render(S, route_chateau_art.REG)
    out_t = os.path.join(ROOT, 'art', 'tilesets')
    save_png(os.path.join(out_t, 'route_chateau.png'), px)
    save_png(os.path.join(out_t, 'route_chateau_numeros.png'), final_lib.numbered(S, px))
    with open(os.path.join(out_t, 'route_chateau_plan.md'), 'w', encoding='utf-8', newline=chr(10)) as f:
        f.write(final_md(S.md('route_chateau.py')))
    print('route_chateau : dessin final,', len(S.tiles), 'tuiles.')


def main():
    S.save_all('route_chateau.py')
    apercu()


if __name__ == '__main__':
    if '--plan' in sys.argv:
        main()
    else:
        main_final()
