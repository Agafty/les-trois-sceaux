# Plan du tileset `route_chateau` — La route de la falaise, la grotte noire et la cour du château (fin du jeu)

> Fichier généré par `tools/sprites/route_chateau.py` : modifier le script, pas ce fichier. **État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro).

- Image : `art/tilesets/route_chateau.png`, 256×768 px, 8 colonnes × 24 lignes de tuiles 32×32, sans marge ni espacement (192 cases). Tileset Tiled : `maps/tilesets/route_chateau.tsx` (collisions et terrains définis). `art/tilesets/route_chateau_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 21 à 24 (ids 160 à 191) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette finale : extérieur sous éclipse (violets froids, verts éteints), grotte brun sombre, château pierre violette ; les mêmes tuiles servent le jour (route, étapes 0 à 2) et sous la teinte d'éclipse (code).
- En PLAN, **la couleur indique la famille** (pavés de la route (gris) / herbe d'éclipse (vert froid) / dalles de la cour (violet-gris) / sol de grotte (brun) / falaise (brun clair) / roche de grotte (brun sombre) / façade (violet) / portail (mauve) / créneaux / rempart / niche de l'Œil (or) / poterne (orange-brun) / fissuré à la bombe (violet vif) / rocher / statue / brasero (orange) / rune (cyan)) ; une zone plus sombre dans une tuile = zone solide.
- Cartes : `route_falaise`, `passage_falaise`, `chateau` (cour) de `maps/chateau/plan.md`. Les salles intérieures du château utilisent le tileset `chateau`.
- **Pas de trou ni de ravin** dans ce tileset (ids 58-66 et 80-95 vides).

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

## Calques

- `Sol` : pavés de la route, herbe d'éclipse, dalles de la cour, sol de grotte, perron, seuil de poterne, alcôve à rune
- `Decor` : socles de braseros, lueurs, cailloux, ronces au pied des murs, flaques, herbe haute, poterne ouverte
- `Murs` : tout ce qui bloque (falaise, roche, rempart, façade, portail, rochers, stalagmites, statues, murs fissurés fermés). Collisions dans le tileset
- `Objets` : Sortie, Spawn, Ennemi, Porte, MurFissure, StatueCorbeau, Torche, Marqueur, Scenario… (objets Tiled, pas des tuiles)
- `Dessus` : passe devant Brann (arches, haut des statues, bannières)

## 1. Sols : pavés, herbe d'éclipse, dalles de la cour, sol de grotte

Route : pavés (0 à 4, au hasard) et herbe d'éclipse (5 à 7). Cour : dalles (8 à 11) et dalle de l'Œil (12, devant le portail, une seule fois). Grotte : sol brun (13 à 15).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `pave_a` | Pavé de la route de base (gris) | Sol | aucune |
| 1 | `pave_b` | Pavé de la route avec joints usés | Sol | aucune |
| 2 | `pave_c` | Pavé de la route avec petits cailloux | Sol | aucune |
| 3 | `pave_fissure` | Pavé fissuré de la route | Sol | aucune |
| 4 | `pave_herbe` | Pavés envahis par l'herbe (bord de route) | Sol | aucune |
| 5 | `herbe_eclipse_a` | Herbe d'éclipse de base (vert froid, éteint) | Sol | aucune |
| 6 | `herbe_eclipse_b` | Herbe d'éclipse avec touffes | Sol | aucune |
| 7 | `herbe_eclipse_fleurs` | Herbe d'éclipse avec fleurs violettes | Sol | aucune |
| 8 | `dalle_cour_a` | Dalle de la cour du château, de base (violet-gris) | Sol | aucune |
| 9 | `dalle_cour_b` | Dalle de la cour avec reflets | Sol | aucune |
| 10 | `dalle_cour_c` | Dalle de la cour en joints irréguliers | Sol | aucune |
| 11 | `dalle_cour_fissuree` | Dalle de la cour fissurée, ronces noires dans la fente | Sol | aucune |
| 12 | `dalle_cour_oeil` | Dalle gravée de l'Œil de Morvath (devant le portail, une seule fois) | Sol | aucune |
| 13 | `grotte_sol_a` | Sol de la grotte noire, de base (brun) | Sol | aucune |
| 14 | `grotte_sol_b` | Sol de la grotte avec veines claires | Sol | aucune |
| 15 | `grotte_sol_cailloux` | Sol de la grotte avec cailloux | Sol | aucune |

## 2. Falaise de la route (terrain `Falaise`, 16 à 30 ; 31 vide)

Face de falaise brun clair : arête sombre en haut, face verticale visible, pied dans l'ombre. Toutes pleines. Mêmes numéros et mêmes formes que `mine` / `sanctuaire` 16 à 30. Dans `route_falaise`, les bords nord et sud de la route sont des falaises ; l'intérieur des massifs se remplit de 28 (plein) ou de `falaise_sommet`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 16 | `falaise_haut` | Mur du haut : sol en dessous, face avant visible [falaise de la route] | Murs | pleine |
| 17 | `falaise_bas` | Mur du bas : sol au-dessus [falaise de la route] | Murs | pleine |
| 18 | `falaise_gauche` | Mur de gauche : sol à droite [falaise de la route] | Murs | pleine |
| 19 | `falaise_droite` | Mur de droite : sol à gauche [falaise de la route] | Murs | pleine |
| 20 | `falaise_coin_int_hg` | Coin intérieur haut-gauche : sol seulement en bas-droite [falaise de la route] | Murs | pleine |
| 21 | `falaise_coin_int_hd` | Coin intérieur haut-droite : sol seulement en bas-gauche [falaise de la route] | Murs | pleine |
| 22 | `falaise_coin_int_bg` | Coin intérieur bas-gauche : sol seulement en haut-droite [falaise de la route] | Murs | pleine |
| 23 | `falaise_coin_int_bd` | Coin intérieur bas-droite : sol seulement en haut-gauche [falaise de la route] | Murs | pleine |
| 24 | `falaise_coin_ext_hg` | Coin extérieur haut-gauche d'un bloc de mur : mur seulement en bas-droite [falaise de la route] | Murs | pleine |
| 25 | `falaise_coin_ext_hd` | Coin extérieur haut-droite d'un bloc de mur : mur seulement en bas-gauche [falaise de la route] | Murs | pleine |
| 26 | `falaise_coin_ext_bg` | Coin extérieur bas-gauche d'un bloc de mur : mur seulement en haut-droite [falaise de la route] | Murs | pleine |
| 27 | `falaise_coin_ext_bd` | Coin extérieur bas-droite d'un bloc de mur : mur seulement en haut-gauche [falaise de la route] | Murs | pleine |
| 28 | `falaise_plein` | Mur plein (intérieur d'un mur épais) [falaise de la route] | Murs | pleine |
| 29 | `falaise_diag_a` | Mur en diagonale (haut-gauche et bas-droite) : complète le terrain [falaise de la route] | Murs | pleine |
| 30 | `falaise_diag_b` | Mur en diagonale (haut-droite et bas-gauche) : complète le terrain [falaise de la route] | Murs | pleine |

## 4. Bouche de grotte (cadre de pierre) et alcôve à rune

Alcôve de la `Sortie` de `route_falaise` (cases (33,1) et (34,1)) : `alcove_sol_rune` sur `Sol` ×2, jambages 42/43 de chaque côté, linteau 40/41 au-dessus (rangée 0), la `Porte` mur à rune posée sur les deux cases de la rangée 2. Arche 44/45 sur `Dessus`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 40 | `bouche_linteau_g` | Linteau gauche de la bouche de grotte (pierre taillée, solide) | Murs | pleine |
| 41 | `bouche_linteau_d` | Linteau droit de la bouche de grotte (solide) | Murs | pleine |
| 42 | `bouche_jambage_g` | Jambage gauche de la bouche de grotte (solide) | Murs | pleine |
| 43 | `bouche_jambage_d` | Jambage droit de la bouche de grotte (solide) | Murs | pleine |
| 44 | `bouche_arche_g` | Arche : retombée gauche, passe devant Brann (même case que bouche_jambage_g) | Dessus | aucune |
| 45 | `bouche_arche_d` | Arche : retombée droite, passe devant Brann (même case que bouche_jambage_d) | Dessus | aucune |
| 46 | `alcove_sol_rune` | Fond d'alcôve : dalle avec rune cyan discrète (sous le mur à rune ; praticable une fois la porte ouverte) | Sol | aucune |
| 47 | `mur_rune_grave` | Mur plein avec une rune gravée très discrète (indice, solide) | Murs | pleine |

## 5. Décor sans collision, sommet de falaise

Socles de braseros (sous l'objet `Torche`), lueur de rune, cailloux, ronces et flaques. Le sommet de falaise (55 et 71) remplit les massifs inaccessibles.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `brasero_socle_route` | Socle de pierre d'un brasero extérieur (sous l'objet Torche) | Decor | aucune |
| 49 | `brasero_socle_grotte` | Socle de roche d'un brasero de grotte (sous l'objet Torche) | Decor | aucune |
| 50 | `lueur_rune` | Tache de lueur cyan au sol (semi-transparente, près des runes) | Decor | aucune |
| 51 | `cailloux` | Cailloux et gravats posés au sol | Decor | aucune |
| 52 | `ronces_pied_mur` | Ronces noires au pied d'un mur (corruption de Morvath) | Decor | aucune |
| 53 | `flaque_eclipse` | Flaque sombre reflétant le ciel d'éclipse | Decor | aucune |
| 54 | `herbe_haute_eclipse` | Herbe haute d'éclipse (touffe sans collision) | Decor | aucune |
| 55 | `falaise_sommet_a` | Sommet de falaise, rocher brun-gris (pleine, massif inaccessible) | Murs | pleine |

## 6. Perron (56/57) ; ids réservés 58 à 66 (vides)

Marches devant le portail du château (praticables). Aucune `Sortie` d'escalier prévue. 58 à 66 = trous des autres donjons : VIDES ici.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 56 | `perron_montant` | Marches du perron qui montent (vers le haut de l'écran), pierre violette | Sol | aucune |
| 57 | `perron_descendant` | Marches du perron qui descendent (vers le bas de l'écran) | Sol | aucune |

## 7. Rochers, stalagmites (solides)

Rochers de la route (`O` des aperçus de `route_falaise`), stalagmites de la grotte (`O` de `passage_falaise`). Corps solide à la base.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 67 | `rocher_a` | Rocher brun-gris posé sur la route (solide) | Murs | partielle : 4,8 24×22 |
| 68 | `rocher_b` | Rocher brun-gris, variante plus haute (solide) | Murs | partielle : 4,8 24×22 |
| 69 | `stalagmite_a` | Stalagmite de la grotte, petite (solide) | Murs | partielle : 4,8 24×22 |
| 70 | `stalagmite_b` | Stalagmite de la grotte, haute (solide) | Murs | partielle : 4,8 24×22 |
| 71 | `falaise_sommet_b` | Sommet de falaise, variante avec ronces (pleine) | Murs | pleine |

## 8. MURS FISSURÉS (bombes) : fermé -> ouvert

Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus). Ouverts : sur `Decor`, opaques (arche noire). Paires : **72->76, 73->77, 74->78, 75->79** (haut, bas, gauche, droite). Seul `haut` est utilisé (poterne). Habillage = pierre de la façade.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 72 | `poterne_fissuree` | MUR FISSURÉ haut = POTERNE FISSURÉE de la cour (face de façade fissurée, objet MurFissure dessus, la bombe l'ouvre) | Murs | pleine |
| 73 | `mur_fissure_bas` | MUR FISSURÉ bas (réservé) | Murs | pleine |
| 74 | `mur_fissure_gauche` | MUR FISSURÉ gauche (réservé) | Murs | pleine |
| 75 | `mur_fissure_droite` | MUR FISSURÉ droite (réservé) | Murs | pleine |
| 76 | `poterne_ouverte` | Mur haut OUVERT = POTERNE OUVERTE : arche noire, gravats (passage dessous) | Decor | aucune |
| 77 | `mur_fissure_bas_ouvert` | Mur bas OUVERT (réservé) | Decor | aucune |
| 78 | `mur_fissure_gauche_ouvert` | Mur gauche OUVERT (réservé) | Decor | aucune |
| 79 | `mur_fissure_droite_ouvert` | Mur droite OUVERT (réservé) | Decor | aucune |

## 10. Roche de la grotte noire (terrain `Roche de la grotte`, 96 à 110 ; 111 variante pleine)

Mêmes formes que la falaise, roche brun très sombre, quelques reflets. Toutes pleines.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `grotte_haut` | Mur du haut : sol en dessous, face avant visible [roche de la grotte] | Murs | pleine |
| 97 | `grotte_bas` | Mur du bas : sol au-dessus [roche de la grotte] | Murs | pleine |
| 98 | `grotte_gauche` | Mur de gauche : sol à droite [roche de la grotte] | Murs | pleine |
| 99 | `grotte_droite` | Mur de droite : sol à gauche [roche de la grotte] | Murs | pleine |
| 100 | `grotte_coin_int_hg` | Coin intérieur haut-gauche : sol seulement en bas-droite [roche de la grotte] | Murs | pleine |
| 101 | `grotte_coin_int_hd` | Coin intérieur haut-droite : sol seulement en bas-gauche [roche de la grotte] | Murs | pleine |
| 102 | `grotte_coin_int_bg` | Coin intérieur bas-gauche : sol seulement en haut-droite [roche de la grotte] | Murs | pleine |
| 103 | `grotte_coin_int_bd` | Coin intérieur bas-droite : sol seulement en haut-gauche [roche de la grotte] | Murs | pleine |
| 104 | `grotte_coin_ext_hg` | Coin extérieur haut-gauche d'un bloc de mur : mur seulement en bas-droite [roche de la grotte] | Murs | pleine |
| 105 | `grotte_coin_ext_hd` | Coin extérieur haut-droite d'un bloc de mur : mur seulement en bas-gauche [roche de la grotte] | Murs | pleine |
| 106 | `grotte_coin_ext_bg` | Coin extérieur bas-gauche d'un bloc de mur : mur seulement en haut-droite [roche de la grotte] | Murs | pleine |
| 107 | `grotte_coin_ext_bd` | Coin extérieur bas-droite d'un bloc de mur : mur seulement en haut-gauche [roche de la grotte] | Murs | pleine |
| 108 | `grotte_plein` | Mur plein (intérieur d'un mur épais) [roche de la grotte] | Murs | pleine |
| 109 | `grotte_diag_a` | Mur en diagonale (haut-gauche et bas-droite) : complète le terrain [roche de la grotte] | Murs | pleine |
| 110 | `grotte_diag_b` | Mur en diagonale (haut-droite et bas-gauche) : complète le terrain [roche de la grotte] | Murs | pleine |
| 111 | `grotte_plein_b` | Roche de grotte pleine, variante à veines (mélanger avec 108) | Murs | pleine |

## 11. Façade du château (calque `Murs`)

Cinq rangées en haut de la cour : créneaux (rangée 0), mur (rangées 1 à 3), pied de mur avec ronces (rangée 4, c'est là que se pose la poterne et la niche d'Œil). Toutes solides.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 112 | `facade_creneau_a` | Créneaux de la façade, merlon (solide) | Murs | pleine |
| 113 | `facade_creneau_b` | Créneaux de la façade, creux (solide) | Murs | pleine |
| 114 | `facade_mur_a` | Mur de la façade, pierre violette (solide) | Murs | pleine |
| 115 | `facade_mur_b` | Mur de la façade, variante avec fenêtre étroite (solide) | Murs | pleine |
| 116 | `facade_pied` | Pied de la façade, ronces noires (solide) | Murs | pleine |
| 117 | `facade_niche_oeil` | NICHE D'ŒIL : cavité de pierre au pied de la façade, où se place l'objet Ennemi `oeil_morvath` (solide) | Murs | pleine |
| 118 | `facade_niche_vide` | Niche de pierre vide (variante décorative, solide) | Murs | pleine |
| 119 | `facade_coin_tour` | Angle de tour de la façade (solide) | Murs | pleine |

## 12. Portail scellé du château (2×3, symbole de l'Œil)

Grand portail de 2 cases de large et 3 de haut, scellé : décor solide infranchissable. Assemblage `portail` : voir plus bas.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 120 | `portail_hg` | Portail scellé, arc du haut gauche (solide) | Murs | pleine |
| 121 | `portail_hd` | Portail scellé, arc du haut droit (solide) | Murs | pleine |
| 122 | `portail_mg` | Portail scellé, milieu avec l'Œil gauche (solide) | Murs | pleine |
| 123 | `portail_md` | Portail scellé, milieu avec l'Œil droit (solide) | Murs | pleine |
| 124 | `portail_bg` | Portail scellé, bas, seuil scellé gauche (solide) | Murs | pleine |
| 125 | `portail_bd` | Portail scellé, bas, seuil scellé droit (solide) | Murs | pleine |
| 126 | `facade_mur_ronces` | Mur de la façade couvert de ronces noires (variante, solide) | Murs | pleine |
| 127 | `facade_blason` | Mur de la façade avec blason de l'Œil (variante, solide) | Murs | pleine |

## 13. Poterne : état fermé, arche et seuil

La poterne est une porte dérobée dans le pied de la façade. États : `poterne_fermee` (murée, sans fissure ; repli), 72 `poterne_fissuree`, 76 `poterne_ouverte`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 128 | `poterne_fermee` | POTERNE FERMÉE : arche murée, sans fissure (solide ; variante de repli) | Murs | pleine |
| 129 | `poterne_arche` | Arche en pierre au-dessus de la poterne ouverte (Dessus, même case que poterne_ouverte) | Dessus | aucune |
| 130 | `poterne_seuil` | Seuil sombre sous la poterne (Sol, sous poterne_ouverte) | Sol | aucune |

## 14. Rempart de la cour (terrain `Rempart`, 136 à 150 ; 151 variante pleine)

Murs gauche, droit et bas de la cour : pierre violette, créneaux vus du dessus, face visible côté cour. Toutes pleines.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 136 | `rempart_haut` | Mur du haut : sol en dessous, face avant visible [rempart de la cour] | Murs | pleine |
| 137 | `rempart_bas` | Mur du bas : sol au-dessus [rempart de la cour] | Murs | pleine |
| 138 | `rempart_gauche` | Mur de gauche : sol à droite [rempart de la cour] | Murs | pleine |
| 139 | `rempart_droite` | Mur de droite : sol à gauche [rempart de la cour] | Murs | pleine |
| 140 | `rempart_coin_int_hg` | Coin intérieur haut-gauche : sol seulement en bas-droite [rempart de la cour] | Murs | pleine |
| 141 | `rempart_coin_int_hd` | Coin intérieur haut-droite : sol seulement en bas-gauche [rempart de la cour] | Murs | pleine |
| 142 | `rempart_coin_int_bg` | Coin intérieur bas-gauche : sol seulement en haut-droite [rempart de la cour] | Murs | pleine |
| 143 | `rempart_coin_int_bd` | Coin intérieur bas-droite : sol seulement en haut-gauche [rempart de la cour] | Murs | pleine |
| 144 | `rempart_coin_ext_hg` | Coin extérieur haut-gauche d'un bloc de mur : mur seulement en bas-droite [rempart de la cour] | Murs | pleine |
| 145 | `rempart_coin_ext_hd` | Coin extérieur haut-droite d'un bloc de mur : mur seulement en bas-gauche [rempart de la cour] | Murs | pleine |
| 146 | `rempart_coin_ext_bg` | Coin extérieur bas-gauche d'un bloc de mur : mur seulement en haut-droite [rempart de la cour] | Murs | pleine |
| 147 | `rempart_coin_ext_bd` | Coin extérieur bas-droite d'un bloc de mur : mur seulement en haut-gauche [rempart de la cour] | Murs | pleine |
| 148 | `rempart_plein` | Mur plein (intérieur d'un mur épais) [rempart de la cour] | Murs | pleine |
| 149 | `rempart_diag_a` | Mur en diagonale (haut-gauche et bas-droite) : complète le terrain [rempart de la cour] | Murs | pleine |
| 150 | `rempart_diag_b` | Mur en diagonale (haut-droite et bas-gauche) : complète le terrain [rempart de la cour] | Murs | pleine |
| 151 | `rempart_plein_b` | Rempart plein, variante avec ronces (mélanger avec 148) | Murs | pleine |

## 15. Statues de chevaliers, piliers de la cour

Statue de chevalier (`O` de la cour) : `statue_chevalier_base` (Murs, solide) + `statue_chevalier_haut` (Dessus) dans la case au-dessus. Abri contre le Chevalier corrompu.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 152 | `statue_chevalier_base` | Statue de chevalier, socle et jambes (solide, base) | Murs | partielle : 2,14 28×18 |
| 153 | `statue_chevalier_haut` | Statue de chevalier, buste et casque (Dessus, case au-dessus de la base) | Dessus | aucune |
| 154 | `statue_chevalier_b_base` | Statue de chevalier, pose de garde, socle (solide) | Murs | partielle : 2,14 28×18 |
| 155 | `statue_chevalier_b_haut` | Statue de chevalier, pose de garde, buste (Dessus) | Dessus | aucune |
| 156 | `pilier_cour` | Pilier de pierre brisé de la cour (solide) | Murs | partielle : 4,8 24×22 |
| 157 | `banniere_morvath` | Bannière noire à l'Œil doré plaquée sur un mur (Dessus) | Dessus | aucune |
| 158 | `banniere_dechiree` | Bannière déchirée plaquée sur un mur (Dessus) | Dessus | aucune |

## Assemblages (pinceau « tampon » dans Tiled)

| Assemblage | Tuiles (ligne par ligne) | Calques / usage |
| --- | --- | --- |
| **portail 2×3** | `120 121 / 122 123 / 124 125` | Murs — case (9,2) de `chateau` ; le perron (56/57) se pose devant en `Sol` |
| **bouche de grotte** | `40 41 / 42 43` | Murs — complète l'alcôve ; l'alcôve elle-même est `alcove_sol_rune` ×2 sur `Sol` |
| **statue de chevalier** | `153 / 152` | Dessus (haut) / Murs (base) |

## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain n'a qu'une couleur (le reste = vide) ; il se peint sur `Murs` (les bords montrent le sol de dessous).

| Terrain | Couleur | Tuiles | Où |
| --- | --- | --- | --- |
| `Falaise` | falaise | 16 à 30 | `route_falaise` : bords nord et sud de la route (face de falaise brun clair) |
| `Roche de la grotte` | roche | 96 à 110 (111 = variante pleine) | `passage_falaise` : parois |
| `Rempart` | rempart | 136 à 150 (151 = variante pleine) | `chateau` : murs gauche, droit et bas de la cour |

## Notes

- IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier (mur fissuré 72->76 ; aucun id de trou ni de ravin).
- Terrains Tiled : `Falaise` (16-30), `Roche de la grotte` (96-110), `Rempart` (136-150), tous sur le calque `Murs`.
- Porte `mur_rune` : l'image `art/puzzles/porte_mur_rune.png` existe déjà (64×32 : fermée, ouverte).
- Lumière : braseros et lueurs sont des objets (`Torche`) ou gérés par le code (grotte en `penombre`), pas des tuiles.
- Teinte d'éclipse (étape 3) : appliquée par le code sur toute la salle, il n'y a pas de variante de couleur dans le PNG.
- Aperçu : `art/tilesets/route_chateau_apercu.png` reconstitue les trois cartes ASCII de `maps/chateau/plan.md` avec les aplats (carrés colorés = objets Tiled).
