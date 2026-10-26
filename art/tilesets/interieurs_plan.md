# Plan du tileset `interieurs` — intérieurs de Brumeval (forge, herboristerie, boutique, cave, archives, maisons)

> Fichier généré par `tools/sprites/interieurs.py` : modifier le script, pas ce fichier. **État : DESSIN FINAL** (les numéros sont ceux du plan, aucune tuile n'a bougé).

- Image : `art/tilesets/interieurs.png`, 256×928 px, 8 colonnes × 29 lignes de tuiles 32×32, sans marge ni espacement (232 cases). Tileset Tiled : `maps/tilesets/interieurs.tsx` (collisions et terrains définis). `art/tilesets/interieurs_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 26 à 29 (ids 200 à 231) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px (dessin final). Les collisions sont dans le tileset (voir la colonne Collision).
- Salle type 20×11 : rangée 0 = plafond, rangée 1 = face du mur du fond (les meubles hauts s'y adossent), colonnes 0 et 19 = bandes latérales, rangée 10 = bandeau du bas avec la porte de sortie (`Sortie` + Spawn d'arrivée juste au-dessus). Un meuble de 2 cases de haut a sa moitié haute au-dessus de sa moitié basse.
- Le sol des cases couvertes par un meuble reste visible : peindre le sol sur tout `Sol`, puis les meubles sur `Murs` (solides) ou `Decor`.

## Calques

- `Sol` : sols (bois, pierre, cave) ; ombres et taches en `Decor`
- `Decor` : sans collision (tapis, parchemins sur table, plantes suspendues, outils au mur, ombres)
- `Murs` : murs et meubles (collisions dans le tileset)
- `Objets` : Sortie, Spawn, PNJ, Coffre, StatueCorbeau (sur l'enclume), MurFissure, escaliers…
- `Dessus` : rarement utilisé en intérieur (haut des poutres, lustres)

## 1. Sols

Sols pleins ; poser au hasard les variantes. `ombre_*` : ombres semi-transparentes à poser en `Decor` sous le mur du fond.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `sol_bois_a` | Plancher de bois, A | Sol | aucune |
| 1 | `sol_bois_b` | Plancher de bois, B | Sol | aucune |
| 2 | `sol_bois_c` | Plancher de bois, C (clous) | Sol | aucune |
| 3 | `sol_bois_use` | Plancher usé et sombre | Sol | aucune |
| 4 | `sol_pierre_a` | Dalles de pierre, A | Sol | aucune |
| 5 | `sol_pierre_b` | Dalles de pierre, B | Sol | aucune |
| 6 | `sol_pierre_c` | Dalles de pierre, C | Sol | aucune |
| 7 | `sol_pierre_fissure` | Dalles de pierre fissurées | Sol | aucune |
| 8 | `sol_terre_cave` | Terre battue de la cave | Sol | aucune |
| 9 | `sol_cave_a` | Sol de cave, roche A | Sol | aucune |
| 10 | `sol_cave_b` | Sol de cave, roche B | Sol | aucune |
| 11 | `sol_forge_suie` | Dalles noircies de suie (forge) | Sol | aucune |
| 12 | `sol_braises` | Braises et cendres au sol (décor) | Decor | aucune |
| 13 | `sol_paille` | Paille éparse (décor) | Decor | aucune |
| 14 | `ombre_mur` | Ombre sous le mur du fond (semi-transparente) | Decor | aucune |
| 15 | `ombre_coin` | Ombre de coin (semi-transparente) | Decor | aucune |

## 2. Murs en bois (maisons, archives)

Rangée 0 = plafond (sombre), rangée 1 = face du mur. Les bandes latérales et le bandeau du bas ferment la salle.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 16 | `mur_bois_plafond` | Mur bois : plafond (bord haut de la salle) | Murs | pleine |
| 17 | `mur_bois_face` | Mur bois : face du mur du fond | Murs | pleine |
| 18 | `mur_bois_fenetre` | Mur bois : face avec fenêtre | Murs | pleine |
| 19 | `mur_bois_face_deco` | Mur bois : face avec tableau / écusson | Murs | pleine |
| 20 | `mur_bois_coin_haut_g` | Mur bois : coin haut gauche | Murs | pleine |
| 21 | `mur_bois_coin_haut_d` | Mur bois : coin haut droite | Murs | pleine |
| 22 | `mur_bois_lat_g` | Mur bois : bande latérale gauche | Murs | partielle : 0,0 8×32 |
| 23 | `mur_bois_lat_d` | Mur bois : bande latérale droite | Murs | partielle : 24,0 8×32 |
| 24 | `mur_bois_bas` | Mur bois : bandeau du bas (bord de la salle) | Murs | partielle : 0,24 32×8 |
| 25 | `mur_bois_coin_bas_g` | Mur bois : coin bas gauche | Murs | partielle : 0,0 8×32 ; 0,24 32×8 |
| 26 | `mur_bois_coin_bas_d` | Mur bois : coin bas droite | Murs | partielle : 24,0 8×32 ; 0,24 32×8 |
| 27 | `porte_sortie_bois` | PORTE DE SORTIE du mur du bas (bois) : 1 case, Sortie dessus ; Spawn d'arrivée sur la case au-dessus | Murs | partielle : 0,24 6×8 ; 26,24 6×8 |
| 28 | `mur_bois_porte_interne` | Porte intérieure sur la face du fond (bois) : mène à une pièce voisine (Sortie dessus) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 29 | `mur_bois_face_b` | Mur bois : face, variante | Murs | pleine |
| 30 | `mur_bois_vitrail` | Mur bois : face avec vitrail | Murs | pleine |

## 3. Murs en pierre (forge)

Rangée 0 = plafond (sombre), rangée 1 = face du mur. Les bandes latérales et le bandeau du bas ferment la salle.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 32 | `mur_pierre_plafond` | Mur pierre : plafond (bord haut de la salle) | Murs | pleine |
| 33 | `mur_pierre_face` | Mur pierre : face du mur du fond | Murs | pleine |
| 34 | `mur_pierre_fenetre` | Mur pierre : face avec fenêtre | Murs | pleine |
| 35 | `mur_pierre_face_deco` | Mur pierre : face avec tableau / écusson | Murs | pleine |
| 36 | `mur_pierre_coin_haut_g` | Mur pierre : coin haut gauche | Murs | pleine |
| 37 | `mur_pierre_coin_haut_d` | Mur pierre : coin haut droite | Murs | pleine |
| 38 | `mur_pierre_lat_g` | Mur pierre : bande latérale gauche | Murs | partielle : 0,0 8×32 |
| 39 | `mur_pierre_lat_d` | Mur pierre : bande latérale droite | Murs | partielle : 24,0 8×32 |
| 40 | `mur_pierre_bas` | Mur pierre : bandeau du bas (bord de la salle) | Murs | partielle : 0,24 32×8 |
| 41 | `mur_pierre_coin_bas_g` | Mur pierre : coin bas gauche | Murs | partielle : 0,0 8×32 ; 0,24 32×8 |
| 42 | `mur_pierre_coin_bas_d` | Mur pierre : coin bas droite | Murs | partielle : 24,0 8×32 ; 0,24 32×8 |
| 43 | `porte_sortie_pierre` | PORTE DE SORTIE du mur du bas (pierre) : 1 case, Sortie dessus ; Spawn d'arrivée sur la case au-dessus | Murs | partielle : 0,24 6×8 ; 26,24 6×8 |
| 44 | `mur_pierre_porte_interne` | Porte intérieure sur la face du fond (pierre) : mène à une pièce voisine (Sortie dessus) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 45 | `mur_pierre_face_b` | Mur pierre : face, variante | Murs | pleine |
| 46 | `mur_pierre_vitrail` | Mur pierre : face avec vitrail | Murs | pleine |

## 4. Murs en crépi clair (herboristerie, boutique)

Rangée 0 = plafond (sombre), rangée 1 = face du mur. Les bandes latérales et le bandeau du bas ferment la salle.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `mur_crepi_plafond` | Mur crepi : plafond (bord haut de la salle) | Murs | pleine |
| 49 | `mur_crepi_face` | Mur crepi : face du mur du fond | Murs | pleine |
| 50 | `mur_crepi_fenetre` | Mur crepi : face avec fenêtre | Murs | pleine |
| 51 | `mur_crepi_face_deco` | Mur crepi : face avec tableau / écusson | Murs | pleine |
| 52 | `mur_crepi_coin_haut_g` | Mur crepi : coin haut gauche | Murs | pleine |
| 53 | `mur_crepi_coin_haut_d` | Mur crepi : coin haut droite | Murs | pleine |
| 54 | `mur_crepi_lat_g` | Mur crepi : bande latérale gauche | Murs | partielle : 0,0 8×32 |
| 55 | `mur_crepi_lat_d` | Mur crepi : bande latérale droite | Murs | partielle : 24,0 8×32 |
| 56 | `mur_crepi_bas` | Mur crepi : bandeau du bas (bord de la salle) | Murs | partielle : 0,24 32×8 |
| 57 | `mur_crepi_coin_bas_g` | Mur crepi : coin bas gauche | Murs | partielle : 0,0 8×32 ; 0,24 32×8 |
| 58 | `mur_crepi_coin_bas_d` | Mur crepi : coin bas droite | Murs | partielle : 24,0 8×32 ; 0,24 32×8 |
| 59 | `porte_sortie_crepi` | PORTE DE SORTIE du mur du bas (crepi) : 1 case, Sortie dessus ; Spawn d'arrivée sur la case au-dessus | Murs | partielle : 0,24 6×8 ; 26,24 6×8 |
| 60 | `mur_crepi_porte_interne` | Porte intérieure sur la face du fond (crepi) : mène à une pièce voisine (Sortie dessus) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 61 | `mur_crepi_face_b` | Mur crepi : face, variante | Murs | pleine |
| 62 | `mur_crepi_vitrail` | Mur crepi : face avec vitrail | Murs | pleine |

## 5. Cave secrète de Garrick (roche)

Cave creusée dans la roche, derrière le mur fissuré du village. `mur_cave_fissure` est le mur fissuré **côté cave** (retour) ; l'escalier mène au village. Le grand carquois et le grand sac de bombes sont des `Coffre` posés sur les piédestaux.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 64 | `mur_cave_plafond` | Cave : plafond rocheux | Murs | pleine |
| 65 | `mur_cave_face` | Cave : face de roche | Murs | pleine |
| 66 | `mur_cave_face_b` | Cave : face de roche, variante (stalactites) | Murs | pleine |
| 67 | `mur_cave_fissure` | MUR FISSURÉ de la cave (solide ; objet MurFissure dessus) | Murs | pleine |
| 68 | `mur_cave_coin_haut_g` | Cave : coin haut gauche | Murs | pleine |
| 69 | `mur_cave_coin_haut_d` | Cave : coin haut droite | Murs | pleine |
| 70 | `mur_cave_lat_g` | Cave : bande latérale gauche | Murs | partielle : 0,0 8×32 |
| 71 | `mur_cave_lat_d` | Cave : bande latérale droite | Murs | partielle : 24,0 8×32 |
| 72 | `mur_cave_bas` | Cave : bandeau du bas | Murs | partielle : 0,24 32×8 |
| 73 | `mur_cave_coin_bas_g` | Cave : coin bas gauche | Murs | partielle : 0,0 8×32 ; 0,24 32×8 |
| 74 | `mur_cave_coin_bas_d` | Cave : coin bas droite | Murs | partielle : 24,0 8×32 ; 0,24 32×8 |
| 75 | `mur_cave_ouvert` | Mur de cave ouvert (trou dans la roche, décor) | Decor | aucune |
| 76 | `escalier_cave_haut` | ESCALIER de la cave vers le village (haut des marches ; Sortie `escalier`) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 77 | `escalier_cave_bas` | Escalier de la cave, marches (passables) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 78 | `piedestal` | Piédestal de pierre (le Coffre du grand carquois / grand sac de bombes se pose dessus) | Murs | partielle : 4,8 24×22 |
| 79 | `toiles_araignee` | Toiles d'araignée (coin de mur, décor) | Decor | aucune |

## 6. Forge de Corvan (intérieur)

Foyer 2×2 (flammes rouges), enclume 1×1 avec le corbeau (objet `StatueCorbeau` dessus), soufflet, établi, bac de trempe, râteliers.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 80 | `foyer_haut_g` | FOYER de forge 2×2, haut gauche (hotte et cheminée) | Murs | pleine |
| 81 | `foyer_haut_d` | FOYER de forge 2×2, haut droite | Murs | pleine |
| 82 | `foyer_bas_g` | FOYER de forge 2×2, bas gauche (braises) | Murs | pleine |
| 83 | `foyer_bas_d` | FOYER de forge 2×2, bas droite (braises) | Murs | pleine |
| 84 | `enclume_int` | ENCLUME (perchoir du corbeau : StatueCorbeau dessus) | Murs | partielle : 4,10 24×20 |
| 85 | `soufflet` | Soufflet de forge (à côté du foyer) | Murs | partielle : 4,8 24×22 |
| 86 | `etabli_g` | Établi de forgeron, bout gauche | Murs | partielle : 0,8 32×22 |
| 87 | `etabli_d` | Établi de forgeron, bout droit | Murs | partielle : 0,8 32×22 |
| 88 | `bac_trempe_int` | Bac de trempe | Murs | partielle : 4,8 24×22 |
| 89 | `rateliers_epees` | Râtelier d'épées (contre le mur du fond) | Murs | pleine |
| 90 | `outils_muraux` | Outils accrochés au mur du fond (décor) | Decor | aucune |
| 91 | `charbon_int` | Tas de charbon | Murs | partielle : 4,8 24×22 |
| 92 | `meule_int` | Meule | Murs | partielle : 4,8 24×22 |
| 93 | `armure_socle` | Armure sur socle | Murs | partielle : 4,8 24×22 |
| 94 | `lingots` | Étagère de lingots | Murs | pleine |
| 95 | `bouclier_mural` | Bouclier accroché au mur (décor) | Decor | aucune |

## 7. Herboristerie de Mère Hulda

Étagères de pots 2 cases de haut, plantes suspendues, comptoir de vente (potions et cœurs).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `etagere_pots_haut_g` | Étagère de pots, haut, bout gauche | Murs | pleine |
| 97 | `etagere_pots_haut_m` | Étagère de pots, haut, milieu | Murs | pleine |
| 98 | `etagere_pots_haut_d` | Étagère de pots, haut, bout droit | Murs | pleine |
| 99 | `etagere_pots_bas_g` | Étagère de pots, bas, bout gauche | Murs | pleine |
| 100 | `etagere_pots_bas_m` | Étagère de pots, bas, milieu | Murs | pleine |
| 101 | `etagere_pots_bas_d` | Étagère de pots, bas, bout droit | Murs | pleine |
| 102 | `plantes_suspendues_a` | Bouquets d'herbes suspendus au mur (décor) | Decor | aucune |
| 103 | `plantes_suspendues_b` | Bouquets d'herbes suspendus, variante | Decor | aucune |
| 104 | `table_herbes_g` | Table de travail aux herbes, bout gauche | Murs | partielle : 0,8 32×22 |
| 105 | `table_herbes_d` | Table de travail aux herbes, bout droit | Murs | partielle : 0,8 32×22 |
| 106 | `mortier` | Mortier et pilon sur pied | Murs | partielle : 4,8 24×22 |
| 107 | `chaudron` | Chaudron de potion (vert qui bout) | Murs | partielle : 4,8 24×22 |
| 108 | `plante_pot_a` | Grande plante en pot, A | Murs | partielle : 4,8 24×22 |
| 109 | `plante_pot_b` | Grande plante en pot, B | Murs | partielle : 4,8 24×22 |
| 110 | `plante_pot_c` | Plante fleurie en pot | Murs | partielle : 4,8 24×22 |
| 111 | `herbes_seches` | Herbes séchées sur le sol / une corde (décor) | Decor | aucune |

## 8. Boutique de Garrick

Comptoir en U possible (angles), étagères de marchandises, présentoirs (flèches, bombes, fioles d'huile, quart de cœur).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 112 | `comptoir_g` | Comptoir de boutique, bout gauche | Murs | partielle : 0,8 32×22 |
| 113 | `comptoir_m` | Comptoir de boutique, milieu | Murs | partielle : 0,8 32×22 |
| 114 | `comptoir_d` | Comptoir de boutique, bout droit | Murs | partielle : 0,8 32×22 |
| 115 | `comptoir_angle_g` | Comptoir, angle (coin arrière gauche) | Murs | partielle : 0,8 32×22 |
| 116 | `comptoir_angle_d` | Comptoir, angle (coin arrière droit) | Murs | partielle : 0,8 32×22 |
| 117 | `comptoir_v` | Comptoir vertical (retour du U) | Murs | partielle : 4,0 24×32 |
| 118 | `balance` | Balance sur le comptoir (décor solide) | Murs | partielle : 4,8 24×22 |
| 119 | `sac_pieces` | Sac de pièces sur le comptoir | Murs | partielle : 4,8 24×22 |
| 120 | `etagere_march_haut_g` | Étagère de marchandises, haut, gauche | Murs | pleine |
| 121 | `etagere_march_haut_m` | Étagère de marchandises, haut, milieu | Murs | pleine |
| 122 | `etagere_march_haut_d` | Étagère de marchandises, haut, droite | Murs | pleine |
| 123 | `etagere_march_bas_g` | Étagère de marchandises, bas, gauche | Murs | pleine |
| 124 | `etagere_march_bas_m` | Étagère de marchandises, bas, milieu | Murs | pleine |
| 125 | `etagere_march_bas_d` | Étagère de marchandises, bas, droite | Murs | pleine |
| 126 | `presentoir_fleches` | Présentoir à flèches (carquois) | Murs | partielle : 4,8 24×22 |
| 127 | `presentoir_bombes` | Présentoir à bombes | Murs | partielle : 4,8 24×22 |
| 128 | `presentoir_fioles` | Présentoir de fioles d'huile | Murs | partielle : 4,8 24×22 |
| 129 | `caisses_march` | Caisses de marchandises | Murs | partielle : 4,8 24×22 |
| 130 | `tonneau_int` | Tonneau | Murs | partielle : 4,8 24×22 |
| 131 | `sacs_int` | Sacs de grain | Murs | partielle : 4,8 24×22 |
| 132 | `caisse_int` | Caisse de bois | Murs | partielle : 4,8 24×22 |
| 133 | `jarre_int` | Jarre | Murs | partielle : 4,8 24×22 |
| 134 | `tapis_boutique_h` | Tapis de comptoir (décor) | Decor | aucune |
| 135 | `rideau_arriere` | Rideau de l'arrière-boutique (décor) | Decor | aucune |

## 9. Archives de Dame Isolde

Bibliothèques hautes (2 cases), pupitre, table de lecture, registres, rouleaux, échelle roulante.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 136 | `biblio_haut_g` | Bibliothèque haute, bout gauche (reliures) | Murs | pleine |
| 137 | `biblio_haut_m` | Bibliothèque haute, milieu | Murs | pleine |
| 138 | `biblio_haut_d` | Bibliothèque haute, bout droit | Murs | pleine |
| 139 | `biblio_bas_g` | Bibliothèque basse, bout gauche | Murs | pleine |
| 140 | `biblio_bas_m` | Bibliothèque basse, milieu | Murs | pleine |
| 141 | `biblio_bas_d` | Bibliothèque basse, bout droit | Murs | pleine |
| 142 | `biblio_rouleaux` | Casier à rouleaux (1×1) | Murs | pleine |
| 143 | `echelle` | Échelle roulante contre la bibliothèque | Murs | pleine |
| 144 | `pupitre` | Pupitre avec livre ouvert | Murs | partielle : 4,8 24×22 |
| 145 | `table_lecture_g` | Table de lecture, bout gauche | Murs | partielle : 0,8 32×22 |
| 146 | `table_lecture_m` | Table de lecture, milieu | Murs | partielle : 0,8 32×22 |
| 147 | `table_lecture_d` | Table de lecture, bout droit | Murs | partielle : 0,8 32×22 |
| 148 | `registre_ouvert` | Registre ouvert (posé sur une table, décor) | Decor | aucune |
| 149 | `parchemins` | Parchemins épars (décor) | Decor | aucune |
| 150 | `globe` | Globe / sphère des sceaux | Murs | partielle : 4,8 24×22 |
| 151 | `candelabre` | Candélabre de sol | Murs | partielle : 11,14 10×18 |

## 10. Mobilier : lits, tables, chaises, cheminée

Un lit = 2 cases de haut (tête en haut). Cheminée domestique 2×2 (autre que le foyer de forge).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 152 | `lit_a_haut` | Lit A (couverture rouge), tête | Murs | partielle : 2,8 28×24 |
| 153 | `lit_a_bas` | Lit A, pied | Murs | partielle : 2,0 28×28 |
| 154 | `lit_b_haut` | Lit B (couverture bleue), tête | Murs | partielle : 2,8 28×24 |
| 155 | `lit_b_bas` | Lit B, pied | Murs | partielle : 2,0 28×28 |
| 156 | `table_ronde` | Table ronde | Murs | partielle : 4,8 24×22 |
| 157 | `table_g` | Table rectangulaire, bout gauche | Murs | partielle : 0,8 32×22 |
| 158 | `table_m` | Table rectangulaire, milieu | Murs | partielle : 0,8 32×22 |
| 159 | `table_d` | Table rectangulaire, bout droit | Murs | partielle : 0,8 32×22 |
| 160 | `chaise_face` | Chaise vue de face (dossier au fond) | Murs | partielle : 4,8 24×22 |
| 161 | `chaise_dos` | Chaise vue de dos | Murs | partielle : 4,8 24×22 |
| 162 | `chaise_g` | Chaise tournée vers la gauche | Murs | partielle : 4,8 24×22 |
| 163 | `chaise_d` | Chaise tournée vers la droite | Murs | partielle : 4,8 24×22 |
| 164 | `tabouret` | Tabouret | Murs | partielle : 4,8 24×22 |
| 165 | `banc_int` | Banc | Murs | partielle : 0,14 32×16 |
| 166 | `buffet_g` | Buffet, moitié gauche | Murs | pleine |
| 167 | `buffet_d` | Buffet, moitié droite | Murs | pleine |
| 168 | `armoire_haut` | Armoire, haut | Murs | pleine |
| 169 | `armoire_bas` | Armoire, bas | Murs | pleine |
| 170 | `cheminee_haut_g` | CHEMINÉE domestique 2×2, haut gauche (manteau) | Murs | pleine |
| 171 | `cheminee_haut_d` | CHEMINÉE domestique 2×2, haut droite | Murs | pleine |
| 172 | `cheminee_bas_g` | CHEMINÉE domestique 2×2, bas gauche (feu) | Murs | pleine |
| 173 | `cheminee_bas_d` | CHEMINÉE domestique 2×2, bas droite | Murs | pleine |
| 174 | `horloge_haut` | Horloge à balancier, haut | Murs | pleine |
| 175 | `horloge_bas` | Horloge à balancier, bas | Murs | pleine |
| 176 | `pot_int` | Pot de terre | Murs | partielle : 4,8 24×22 |
| 177 | `vase` | Vase avec fleurs | Murs | partielle : 4,8 24×22 |
| 178 | `plante_int` | Plante verte | Murs | partielle : 4,8 24×22 |
| 179 | `bougie_table` | Bougie sur table (décor) | Decor | aucune |
| 180 | `lampe_murale` | Lampe à huile accrochée au mur (décor) | Decor | aucune |
| 181 | `tableau` | Tableau au mur (décor) | Decor | aucune |
| 182 | `trophee` | Trophée de cerf au mur (décor) | Decor | aucune |
| 183 | `chandelle_sol` | Cire fondue au sol (décor) | Decor | aucune |

## 11. Tapis (calque `Decor`)

Tapis 3×3 : coins, bords et centre ; sans collision.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 184 | `tapis_hg` | Tapis, coin haut gauche | Decor | aucune |
| 185 | `tapis_h` | Tapis, bord haut | Decor | aucune |
| 186 | `tapis_hd` | Tapis, coin haut droite | Decor | aucune |
| 187 | `tapis_g` | Tapis, bord gauche | Decor | aucune |
| 188 | `tapis_centre` | Tapis, centre | Decor | aucune |
| 189 | `tapis_d` | Tapis, bord droit | Decor | aucune |
| 190 | `tapis_bg` | Tapis, coin bas gauche | Decor | aucune |
| 191 | `tapis_b` | Tapis, bord bas | Decor | aucune |
| 192 | `tapis_bd` | Tapis, coin bas droite | Decor | aucune |
| 193 | `paillasson` | Paillasson devant la porte de sortie | Decor | aucune |
| 194 | `tapis_etroit_h` | Chemin de tapis étroit, horizontal | Decor | aucune |
| 195 | `tapis_etroit_v` | Chemin de tapis étroit, vertical | Decor | aucune |
| 196 | `peau_bete` | Peau de bête | Decor | aucune |
| 197 | `tache_encre` | Tache d'encre / de suie sur le sol | Decor | aucune |
| 198 | `rayon_lumiere` | Rayon de lumière de fenêtre (semi-transparent) | Decor | aucune |

## Assemblages (pinceau « tampon » dans Tiled)

| Assemblage | Tuiles (ligne par ligne) | Calques / usage |
| --- | --- | --- |
| **Cadre de salle (coins et bords)** | `20 16 21 / 22 17 23 / 22 · 23 / 25 24 26` | Murs — à étirer : plafond + face sur toute la largeur, bandes latérales sur toute la hauteur, bandeau du bas avec porte_sortie_<style> à la place de `bas` |
| **Foyer de forge 2×2** | `80 81 / 82 83` | Murs — adossé au mur du fond ; recharge de vie : zone Objets devant |
| **Étagère de pots 3×2** | `96 97 98 / 99 100 101` | Murs — adossée au mur du fond (la face haute peut chevaucher le mur) |
| **Bibliothèque 3×2** | `136 137 138 / 139 140 141` | Murs — adossée au mur du fond |
| **Lit 1×2** | `152 / 153` | Murs — tête contre le mur du fond ; variante bleue : lit_b |
| **Cheminée 2×2** | `170 171 / 172 173` | Murs — adossée au mur du fond |
| **Tapis 3×3** | `184 185 186 / 187 188 189 / 190 191 192` | Decor — peut s'étirer en répétant tapis_h / tapis_centre |

## Notes

- Aucun escalier d'étage : les maisons sont sur un seul niveau ; l'escalier de la cave de Garrick est `escalier_cave_haut` / `escalier_cave_bas`.
- Les coffres, PNJ, statues du corbeau, mur fissuré (objet), Sortie et Spawn sont des **objets Tiled** (calque `Objets`), pas des tuiles : le tileset ne contient que le décor.
