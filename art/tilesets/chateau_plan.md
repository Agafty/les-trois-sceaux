# Plan du tileset `chateau` — Le château de Morvath, intérieur (pierre sombre, tapis, armures, fosse de ronces, arène de Corvan)

> Fichier généré par `tools/sprites/chateau.py` : modifier le script, pas ce fichier. **État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro).

- Image : `art/tilesets/chateau.png`, 256×704 px, 8 colonnes × 22 lignes de tuiles 32×32, sans marge ni espacement (176 cases). Tileset Tiled : `maps/tilesets/chateau.tsx` (collisions et terrains définis). `art/tilesets/chateau_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 19 à 22 (ids 144 à 175) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette finale : pierre violette sombre (comme la façade de `route_chateau`), tapis rouge sombre, ronces noires, symboles dorés.
- En PLAN, **la couleur indique la famille** (pierre sombre violette / tapis (rouge sombre) / mur (violet foncé) / porte (orange) / sol d'arène (violet clair) / symboles (or) / socle / escalier (beige) / armure / colonne / fissuré à la bombe (violet vif) / ronces (noir-violet) / rune (cyan) / niche d'Œil (or) / tenture (magenta) / blason / cercle des sceaux (mauve)) ; une zone plus sombre dans une tuile = zone solide.
- **Pas de trou mortel** (ids 58-66 vides) ; la **fosse de ronces** (80-95) est un ravin : on ne la franchit pas, les flèches passent.
- Salles : `salle_01` à `salle_04` (20×11) et `salle_boss` (20×22) de `maps/chateau/plan.md` ; la cour et la façade sont dans `route_chateau`.

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

## Calques

- `Sol` : pierre, tapis, sol d'arène, symboles au sol, cercle des sceaux, sol de la fosse (80), alcôve à rune
- `Decor` : ombres sous les murs, gravats, ronces au sol, socle de brasero, murs fissurés ouverts
- `Murs` : tout ce qui bloque (murs, fosse de ronces, piliers, armures, statues, socle, murs fissurés fermés). Collisions dans le tileset
- `Objets` : Sortie, Spawn, Ennemi, Coffre, Porte, Interrupteur, MurFissure, Torche, boss_corvan, pilier, Marqueur… (objets Tiled, pas des tuiles)
- `Dessus` : passe devant Brann (haut des armures, statues, colonnes, bannières, encadrement des portes)

## 1. Sols : pierre, tapis, ombres, gravats

Pierre sombre violette (0 à 3, au hasard). Tapis rouge sombre (4 à 10) : bandes verticale/horizontale, bouts et croisement. Ombres 11 à 13 sous les murs (`Decor`).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `pierre_a` | Dalle de pierre sombre violette, de base | Sol | aucune |
| 1 | `pierre_b` | Dalle de pierre avec reflets | Sol | aucune |
| 2 | `pierre_c` | Dalle de pierre en joints irréguliers | Sol | aucune |
| 3 | `pierre_fissuree` | Dalle fissurée, ronces noires dans la fente | Sol | aucune |
| 4 | `tapis_v` | Tapis rouge sombre, bande verticale (bordures à gauche et à droite) | Sol | aucune |
| 5 | `tapis_h` | Tapis rouge sombre, bande horizontale (bordures en haut et en bas) | Sol | aucune |
| 6 | `tapis_bout_haut` | Tapis : extrémité haute (franges) | Sol | aucune |
| 7 | `tapis_bout_bas` | Tapis : extrémité basse (franges) | Sol | aucune |
| 8 | `tapis_bout_gauche` | Tapis : extrémité gauche (franges) | Sol | aucune |
| 9 | `tapis_bout_droite` | Tapis : extrémité droite (franges) | Sol | aucune |
| 10 | `tapis_croix` | Tapis : croisement (motif central) | Sol | aucune |
| 11 | `ombre_mur_haut` | Ombre portée d'un mur du haut sur le sol (trame), sous un mur haut | Decor | aucune |
| 12 | `ombre_mur_gauche` | Ombre portée d'un mur de gauche sur le sol | Decor | aucune |
| 13 | `ombre_mur_coin` | Ombre portée dans un angle haut-gauche (mur en haut et à gauche) | Decor | aucune |
| 14 | `gravats` | Gravats et éclats de pierre posés au sol | Decor | aucune |
| 15 | `ronces_sol` | Ronces noires qui rampent au sol (corruption de Morvath) | Decor | aucune |

## 2. Murs du château (terrain `Murs`)

Pierre violette très sombre, dessus noir, face avant plus claire visible. Toutes pleines. Mêmes numéros et mêmes formes que `mine` / `sanctuaire` (16 à 30).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 16 | `mur_haut` | Mur du haut : sol en dessous, face avant visible [mur du château] | Murs | pleine |
| 17 | `mur_bas` | Mur du bas : sol au-dessus [mur du château] | Murs | pleine |
| 18 | `mur_gauche` | Mur de gauche : sol à droite [mur du château] | Murs | pleine |
| 19 | `mur_droite` | Mur de droite : sol à gauche [mur du château] | Murs | pleine |
| 20 | `mur_coin_int_hg` | Coin intérieur haut-gauche : sol seulement en bas-droite [mur du château] | Murs | pleine |
| 21 | `mur_coin_int_hd` | Coin intérieur haut-droite : sol seulement en bas-gauche [mur du château] | Murs | pleine |
| 22 | `mur_coin_int_bg` | Coin intérieur bas-gauche : sol seulement en haut-droite [mur du château] | Murs | pleine |
| 23 | `mur_coin_int_bd` | Coin intérieur bas-droite : sol seulement en haut-gauche [mur du château] | Murs | pleine |
| 24 | `mur_coin_ext_hg` | Coin extérieur haut-gauche d'un bloc de mur : mur seulement en bas-droite [mur du château] | Murs | pleine |
| 25 | `mur_coin_ext_hd` | Coin extérieur haut-droite d'un bloc de mur : mur seulement en bas-gauche [mur du château] | Murs | pleine |
| 26 | `mur_coin_ext_bg` | Coin extérieur bas-gauche d'un bloc de mur : mur seulement en haut-droite [mur du château] | Murs | pleine |
| 27 | `mur_coin_ext_bd` | Coin extérieur bas-droite d'un bloc de mur : mur seulement en haut-gauche [mur du château] | Murs | pleine |
| 28 | `mur_plein` | Mur plein (intérieur d'un mur épais) [mur du château] | Murs | pleine |
| 29 | `mur_diag_a` | Mur en diagonale (haut-gauche et bas-droite) : complète le terrain [mur du château] | Murs | pleine |
| 30 | `mur_diag_b` | Mur en diagonale (haut-droite et bas-gauche) : complète le terrain [mur du château] | Murs | pleine |

## 4. Ouvertures de salle (cadre de pierre)

Remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` dans la même case du calque `Dessus`, puis l'objet `Porte` par-dessus. Mêmes numéros et collisions que `sanctuaire`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 40 | `porte_haut` | Ouverture dans le mur haut (remplace une tuile mur_haut) ; passage de 20 px au centre, l'objet Porte se pose dessus | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 41 | `porte_bas` | Ouverture dans le mur bas (remplace une tuile mur_bas) ; passage de 20 px au centre, l'objet Porte se pose dessus | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 42 | `porte_gauche` | Ouverture dans le mur gauche (remplace une tuile mur_gauche) ; passage de 24 px au centre, l'objet Porte se pose dessus | Murs | partielle : 0,0 32×4 ; 0,28 32×4 |
| 43 | `porte_droite` | Ouverture dans le mur droite (remplace une tuile mur_droite) ; passage de 24 px au centre, l'objet Porte se pose dessus | Murs | partielle : 0,0 32×4 ; 0,28 32×4 |
| 44 | `porte_haut_dessus` | Haut de l'encadrement de porte_haut, même case que porte_haut | Dessus | aucune |
| 45 | `porte_bas_dessus` | Haut de l'encadrement de porte_bas, même case que porte_bas | Dessus | aucune |
| 46 | `porte_gauche_dessus` | Haut de l'encadrement de porte_gauche, même case que porte_gauche | Dessus | aucune |
| 47 | `porte_droite_dessus` | Haut de l'encadrement de porte_droite, même case que porte_droite | Dessus | aucune |

## 5. Sol d'arène, symboles au sol (arc, bombe, lanterne), socle

Arène de Corvan : dalles plus claires gravées (48 à 51). Salle 03 : trois petits symboles au sol qui rappellent les trois sceaux : arc (Racines), bombe (Montagne), lanterne (Lac) ; décor sans effet. Socle de pierre solide (55).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `sol_arene_a` | Dalle d'arène, violet clair gravé de lignes fines | Sol | aucune |
| 49 | `sol_arene_b` | Dalle d'arène avec joints en étoile | Sol | aucune |
| 50 | `sol_arene_c` | Dalle d'arène usée, éclats | Sol | aucune |
| 51 | `sol_arene_fissure` | Dalle d'arène fissurée, ronces noires | Sol | aucune |
| 52 | `symbole_arc` | Symbole au sol : ARC (sceau des Racines), gravé en or pâle sur dalle de pierre | Sol | aucune |
| 53 | `symbole_bombe` | Symbole au sol : BOMBE (sceau de la Montagne) | Sol | aucune |
| 54 | `symbole_lanterne` | Symbole au sol : LANTERNE (sceau du Lac) | Sol | aucune |
| 55 | `socle` | Socle de pierre (solide, 1 case) | Murs | partielle : 4,8 24×22 |

## 6. Escaliers (56/57) ; ids réservés 58 à 66 (vides)

Réservés par cohérence avec les autres donjons (le château n'a pas d'escalier dans le plan). 58 à 66 = trous mortels : VIDES ici.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 56 | `escalier_montant` | Escalier qui monte (vers le haut de l'écran), pierre sombre ; la transition serait un objet Sortie | Sol | aucune |
| 57 | `escalier_descendant` | Escalier qui descend (vers le bas de l'écran), pierre sombre | Sol | aucune |

## 7. Armures, statues, socle de brasero

Armure vide (`armure_base` solide + `armure_haut` en `Dessus` dans la case au-dessus) ; statue de chevalier idem. Socle de brasero : décor sous l'objet `Torche`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 67 | `armure_base` | Armure vide sur son support, jambes et socle (solide, base) | Murs | partielle : 2,14 28×18 |
| 68 | `armure_haut` | Armure vide : buste, casque à plume (Dessus, case au-dessus de la base) | Dessus | aucune |
| 69 | `statue_base` | Statue de chevalier, socle et jambes (solide, base) | Murs | partielle : 2,14 28×18 |
| 70 | `statue_haut` | Statue de chevalier, buste et casque (Dessus, case au-dessus de la base) | Dessus | aucune |
| 71 | `brasero_socle` | Socle de pierre d'un brasero (sous l'objet Torche) | Decor | aucune |

## 8. MURS FISSURÉS (bombes) : fermé -> ouvert

Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus, fissures claires). Ouverts : sur `Decor`, opaques (trou noir dans la pierre). Paires : **72->76, 73->77, 74->78, 75->79** (haut, bas, gauche, droite). La salle 03 n'utilise qu'une orientation (mur vertical : 74 ou 75).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 72 | `mur_fissure_haut` | MUR FISSURÉ haut (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l'ouvre) | Murs | pleine |
| 73 | `mur_fissure_bas` | MUR FISSURÉ bas (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l'ouvre) | Murs | pleine |
| 74 | `mur_fissure_gauche` | MUR FISSURÉ gauche (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l'ouvre) | Murs | pleine |
| 75 | `mur_fissure_droite` | MUR FISSURÉ droite (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l'ouvre) | Murs | pleine |
| 76 | `mur_fissure_haut_ouvert` | Mur haut OUVERT : trou noir dans la pierre, gravats (passage dessous) | Decor | aucune |
| 77 | `mur_fissure_bas_ouvert` | Mur bas OUVERT : trou noir dans la pierre, gravats (passage dessous) | Decor | aucune |
| 78 | `mur_fissure_gauche_ouvert` | Mur gauche OUVERT : trou noir dans la pierre, gravats (passage dessous) | Decor | aucune |
| 79 | `mur_fissure_droite_ouvert` | Mur droite OUVERT : trou noir dans la pierre, gravats (passage dessous) | Decor | aucune |

## 9. FOSSE DE RONCES = RAVIN (terrain `Fosse`, 80 à 95)

Fossé de ronces noires et d'épines au fond d'un trou sombre (salle 01 : deux fosses de 5 cases de large devant les Œils). **Infranchissable ; les flèches passent** (comme le ravin de `village` / `montagne`, mêmes ids). 80 = sol de base (`Sol`) ; 81 à 94 = bords et coins (`Murs`, collision par quarts de case) ; 95 = ronces pleines.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 80 | `fosse_base` | Pierre (base du terrain Fosse) | Sol | aucune |
| 81 | `fosse_0001` | Fosse : coin bas-droite seulement (ronces dans ce coin) | Murs | partielle : 16,16 16×16 |
| 82 | `fosse_0010` | Fosse : coin bas-gauche seulement (ronces dans ce coin) | Murs | partielle : 0,16 16×16 |
| 83 | `fosse_0011` | Fosse : ronces en bas (bord bas) | Murs | partielle : 0,16 32×16 |
| 84 | `fosse_0100` | Fosse : coin haut-droite seulement (ronces dans ce coin) | Murs | partielle : 16,0 16×16 |
| 85 | `fosse_0101` | Fosse : ronces à droite (bord droit) | Murs | partielle : 16,0 16×32 |
| 86 | `fosse_0110` | Fosse : deux coins opposés (haut-droite et bas-gauche) | Murs | partielle : 16,0 16×16 ; 0,16 16×16 |
| 87 | `fosse_0111` | Fosse : ronces partout sauf le coin haut-gauche (coin rentrant) | Murs | partielle : 16,0 16×16 ; 0,16 32×16 |
| 88 | `fosse_1000` | Fosse : coin haut-gauche seulement (ronces dans ce coin) | Murs | partielle : 0,0 16×16 |
| 89 | `fosse_1001` | Fosse : deux coins opposés (haut-gauche et bas-droite) | Murs | partielle : 0,0 16×16 ; 16,16 16×16 |
| 90 | `fosse_1010` | Fosse : ronces à gauche (bord gauche) | Murs | partielle : 0,0 16×32 |
| 91 | `fosse_1011` | Fosse : ronces partout sauf le coin haut-droite (coin rentrant) | Murs | partielle : 0,0 16×16 ; 0,16 32×16 |
| 92 | `fosse_1100` | Fosse : ronces en haut (bord haut) | Murs | partielle : 0,0 32×16 |
| 93 | `fosse_1101` | Fosse : ronces partout sauf le coin bas-gauche (coin rentrant) | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 94 | `fosse_1110` | Fosse : ronces partout sauf le coin bas-droite (coin rentrant) | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 95 | `fosse_plein` | Fosse de ronces, case entière (infranchissable) | Murs | pleine |

## 10. Murs de décor et niche d'Œil (solides, calque `Murs`)

Variantes pleines des murs : tenture, blason, ronces, vitrail. 99 = niche où se pose l'objet `Ennemi` `oeil_morvath` (salle 01). Mur à rune : 102/103.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `mur_tenture` | Mur plein avec tenture violette pendante (variante, solide) | Murs | pleine |
| 97 | `mur_blason` | Mur plein avec blason de l'Œil de Morvath (variante, solide) | Murs | pleine |
| 98 | `mur_ronces` | Mur plein couvert de ronces noires (variante, solide) | Murs | pleine |
| 99 | `mur_niche_oeil` | NICHE D'ŒIL : cavité de pierre dans le mur du haut, où se place l'objet Ennemi `oeil_morvath` (solide) | Murs | pleine |
| 100 | `mur_niche_vide` | Niche vide dans le mur (variante décorative, solide) | Murs | pleine |
| 101 | `mur_vitrail` | Mur plein avec vitrail sombre (variante, solide) | Murs | pleine |
| 102 | `alcove_sol_rune` | Fond d'alcôve : dalle avec rune cyan discrète (sous le mur à rune ; praticable une fois la porte ouverte) | Sol | aucune |
| 103 | `mur_rune_grave` | Mur plein avec une rune gravée très discrète (indice, solide) | Murs | pleine |

## 11. Colonnes, bannières

Colonne de 1 case = `colonne_base` (Murs, solide) + `colonne_haut` (Dessus) dans la case au-dessus (`O` des salles 01 et 02). Bannières et vitrail plaqués sur une face de mur (Dessus).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 112 | `colonne_haut` | Haut de colonne (chapiteau), case au-dessus de colonne_base | Dessus | aucune |
| 113 | `colonne_base` | Base de colonne de pierre sombre (solide) | Murs | partielle : 2,14 28×18 |
| 114 | `colonne_brisee` | Colonne brisée, tronc coupé (solide, 1 seule case) | Murs | partielle : 4,8 24×22 |
| 115 | `banniere_morvath` | Bannière noire à l'Œil doré plaquée sur un mur (Dessus) | Dessus | aucune |
| 116 | `banniere_dechiree` | Bannière déchirée plaquée sur un mur (Dessus) | Dessus | aucune |
| 117 | `vitrail_dessus` | Reflet de vitrail violet plaqué sur un mur (Dessus) | Dessus | aucune |

## 12. Piliers 2×2 (arène du boss)

Pilier de 4 cases (quatre piliers 2×2 dans l'arène) : `pilier_hg` `pilier_hd` / `pilier_bg` `pilier_bd`, tous sur `Murs`, solides. Les rectangles Tiled nommés `pilier` restent la référence du boss.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 120 | `pilier_hg` | Pilier 2×2 : haut-gauche (solide) | Murs | partielle : 2,2 30×30 |
| 121 | `pilier_hd` | Pilier 2×2 : haut-droite (solide) | Murs | partielle : 0,2 30×30 |
| 122 | `pilier_bg` | Pilier 2×2 : bas-gauche (solide) | Murs | partielle : 2,0 30×30 |
| 123 | `pilier_bd` | Pilier 2×2 : bas-droite (solide) | Murs | partielle : 0,0 30×30 |

## 13. Cercle des sceaux (arène, 4×4, décor)

Grand cercle gravé au centre de l'arène (3 cercles entrelacés : arc, bombe, lanterne), 4×4 cases, sur `Sol`, sans collision. Ids dans l'ordre ligne par ligne : 128-131 / 132-135 / 136-139 / 140-143 (assemblage `cercle des sceaux`). À poser sur du sol d'arène 48 à 51.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 128 | `cercle_00` | Cercle des sceaux, ligne 1 colonne 1 (anneau) | Sol | aucune |
| 129 | `cercle_01` | Cercle des sceaux, ligne 1 colonne 2 (anneau) | Sol | aucune |
| 130 | `cercle_02` | Cercle des sceaux, ligne 1 colonne 3 (anneau) | Sol | aucune |
| 131 | `cercle_03` | Cercle des sceaux, ligne 1 colonne 4 (anneau) | Sol | aucune |
| 132 | `cercle_10` | Cercle des sceaux, ligne 2 colonne 1 (anneau) | Sol | aucune |
| 133 | `cercle_11` | Cercle des sceaux, ligne 2 colonne 2 (centre : les trois sceaux) | Sol | aucune |
| 134 | `cercle_12` | Cercle des sceaux, ligne 2 colonne 3 (centre : les trois sceaux) | Sol | aucune |
| 135 | `cercle_13` | Cercle des sceaux, ligne 2 colonne 4 (anneau) | Sol | aucune |
| 136 | `cercle_20` | Cercle des sceaux, ligne 3 colonne 1 (anneau) | Sol | aucune |
| 137 | `cercle_21` | Cercle des sceaux, ligne 3 colonne 2 (centre : les trois sceaux) | Sol | aucune |
| 138 | `cercle_22` | Cercle des sceaux, ligne 3 colonne 3 (centre : les trois sceaux) | Sol | aucune |
| 139 | `cercle_23` | Cercle des sceaux, ligne 3 colonne 4 (anneau) | Sol | aucune |
| 140 | `cercle_30` | Cercle des sceaux, ligne 4 colonne 1 (anneau) | Sol | aucune |
| 141 | `cercle_31` | Cercle des sceaux, ligne 4 colonne 2 (anneau) | Sol | aucune |
| 142 | `cercle_32` | Cercle des sceaux, ligne 4 colonne 3 (anneau) | Sol | aucune |
| 143 | `cercle_33` | Cercle des sceaux, ligne 4 colonne 4 (anneau) | Sol | aucune |

## Assemblages (pinceau « tampon » dans Tiled)

| Assemblage | Tuiles (ligne par ligne) | Calques / usage |
| --- | --- | --- |
| **cercle des sceaux 4×4** | `128 129 130 131 / 132 133 134 135 / 136 137 138 139 / 140 141 142 143` | Sol — centre de `salle_boss` (par exemple cases (8,8) à (11,11)) ; arène en `sol_arene_*` |
| **colonne** | `112 / 113` | Dessus (haut) / Murs (base) |
| **armure vide** | `68 / 67` | Dessus (haut) / Murs (base) |
| **pilier 2×2** | `120 121 / 122 123` | Murs |

## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T).

| Terrain | Couleurs | Calque | Tuiles |
| --- | --- | --- | --- |
| `Murs` | `mur` (le reste = vide) | Murs | 16 à 30 |
| `Fosse` | `sol`, `ronces` | `Sol` (80) + `Murs` (81 à 95) | 80 à 95 (même méthode que `Ravin` de `village`) |

## Notes

- IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier (fosse = ravin 80-95 ; mur fissuré 72->76 ; aucun id de trou).
- Terrains Tiled (Wang par coins) : `Murs` (16 à 30), `Fosse` (80 à 95 : 80 sur `Sol`, 81 à 95 sur `Murs`).
- Porte : remplacer la tuile de mur par `porte_<côté>`, poser `porte_<côté>_dessus` dans la même case de `Dessus`, puis l'objet `Porte`.
- Grille de la salle 03 (`chateau_porte_03`) : c'est une `Porte` dont l'image `art/puzzles/porte_*_chateau.png` est à dessiner ; sous elle, du sol (`pierre_*`).
- Lumière : braseros et torches sont des objets (`Torche`) ; teinte d'éclipse appliquée par le code.
- Aperçu : `art/tilesets/chateau_apercu.png` reconstitue `salle_01`, `salle_03` et `salle_boss` (carrés colorés = objets Tiled).
