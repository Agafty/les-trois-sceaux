# Plan du tileset `mine` — La Mine Effondrée (donjon 2 : galeries, rails, éboulis, cristaux, arène de Gorm)

> Fichier généré par `tools/sprites/mine.py` : modifier le script, pas ce fichier. **État : DESSIN FINAL** (les numéros sont ceux du plan, aucune tuile n'a bougé).

- Image : `art/tilesets/mine.png`, 256×832 px, 8 colonnes × 26 lignes de tuiles 32×32, sans marge ni espacement (208 cases). Tileset Tiled : `maps/tilesets/mine.tsx` (collisions et terrains définis). `art/tilesets/mine_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 23 à 26 (ids 176 à 207) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette : roche brun-gris chaude, bois d'étais, rails gris, cristaux cyan, cristal rouge de Gorm. En PLAN, **la couleur indique la famille** (sol (brun-gris) / poussière (sombre) / arène (violet-gris) / mur (brun) / rail et métal (gris clair) / bois (brun) / trou (noir) / passage (turquoise) / eau (bleu) / cristal (cyan) / cristal rouge / minerai (jaune) / éboulis et blocage (magenta) / fissuré à la bombe (violet) / porte (orange) / escalier (beige)) ; une zone plus sombre dans une tuile = zone solide.
- DEUX planches de même numérotation : `mine.png` (rez-de-chaussée) et `mine_sous_sol.png` (recoloration plus sombre et bleutée, tileset `mine_sous_sol.tsx` identique).

## POUR LE DÉVELOPPEUR : ids à reconnaître par le code

Tileset `mine` (8 colonnes, id local Tiled = ligne × 8 + colonne). Une tuile reconnue = le tileset ET l'id.

| Famille | Ids | Calque | Ce que le code doit faire |
| --- | --- | --- | --- |
| **TROUS MORTELS** | **58 à 66** (même bloc 3×3 que `temple_racines` 58 à 66) | `Sol` | Comme `HoleRules` : toute la case fait tomber (-1 PV sans mourir, retour au Spawn de la salle). `HoleWatcher` doit aussi accepter le tileset `mine` (fichier `mine.png`). Les autres tuiles ne tuent pas. |
| **Trous de passage** (vers l'étage du dessous) | 31 à 39 (comme `temple_racines`) | `Sol` | Décoratif, jamais mortel : l'objet `Chute` fait le travail. Ne PAS les confondre avec 58-66. |
| **Escaliers** | 56 (montant), 57 (descendant) | `Sol` | Posent une `Sortie` `transition=escalier` (comme le temple). |
| **MURS FISSURÉS** fermé -> ouvert | 144 -> 148 (haut), 145 -> 149 (bas), 146 -> 150 (gauche), 147 -> 151 (droite) ; 152 -> 153 (rocher fissuré) | fermés `Murs`, ouverts `Decor` | Comme `TileRules` pour `montagne` 156 -> 157 et 172 -> 173 : la bombe retire la tuile fermée de `Murs` et le code pose la version ouverte sur `Decor` (ou elle est déjà posée dessous). Les versions ouvertes sont opaques. |
| **ÉBOULIS bloquants** fermé -> dégagé | 72 -> 76, 73 -> 77, 74 -> 76 (moitié gauche), 75 -> 77 (moitié droite) | fermés `Murs`, dégagés `Sol` | Comme `montagne` 176/178 -> 180 et 177/179 -> 181. |
| ÉBOULIS dans une ouverture | 164 -> 76, 165 -> 77 | fermés `Murs`, dégagés `Sol` | Même règle que les éboulis ; à poser à la place d'une tuile de porte. |
| Indice visuel | 154 `mur_craquele` | `Murs` | Rien : simple décor solide (aucun id à reconnaître). |

Tilesets : `mine` ET `mine_sous_sol` (mêmes ids, mêmes collisions) : `HoleWatcher` doit accepter les deux fichiers.
Les éboulis ont d'autres numéros que `montagne` (72 à 77, pas 176 à 181) : à déclarer dans `TileRules` pour `mine`.

Tout le reste est géré par les collisions du `.tsx` (murs 16 à 30, 40 à 43 portes, 72 à 75, 104 à 110, 113, 121, 122, 131, 143, 144 à 147, 152, 154) : aucun code.
Les ids 0 à 5, 16 à 57, 58 à 71 et 80 à 92 ont **les mêmes numéros que `temple_racines`** pour le sol, les murs, les portes, la poussière (= la terre du temple), les escaliers et l'eau.

## Calques

- `Sol` : sol, poussière, eau peu profonde, trous (mortels et de passage), escaliers, arène, éboulis dégagé
- `Decor` : rails, gravats, cristaux au sol, ossements, ouvertures de mur fissuré (version ouverte)
- `Murs` : tout ce qui bloque (murs, éboulis, wagonnets, tas de minerai, tonneaux, murs fissurés fermés). Collisions dans le tileset
- `Objets` : Sortie, Spawn, Ennemi, Coffre, Porte, MurFissure, Chute, boss_gorm, pilier… (objets Tiled, pas des tuiles)
- `Dessus` : passe devant Brann (linteaux et poutres, haut d'étai, lanternes, cristaux de paroi, haut de pilier)

## 1. Sol, rails, ombres

Sol de la mine : peindre les variantes 0 à 4 au hasard. Rails sur `Decor` (jamais de collision) : droits, quatre virages (nommés par les deux côtés qu'ils relient). Les ombres 12 à 14 se posent sous les murs (`Decor`).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `sol_a` | Sol de roche brun-gris, de base | Sol | aucune |
| 1 | `sol_b` | Sol de roche avec petits cailloux | Sol | aucune |
| 2 | `sol_c` | Sol de roche en dalles irrégulières | Sol | aucune |
| 3 | `sol_fissure_a` | Sol fissuré (fissure en diagonale) | Sol | aucune |
| 4 | `sol_fissure_b` | Sol fissuré (fissure en étoile) | Sol | aucune |
| 5 | `poussiere` | Poussière de charbon, sol sombre (base du terrain Poussiere) | Sol | aucune |
| 6 | `rail_h` | Rail horizontal (se raccorde à gauche et à droite) | Decor | aucune |
| 7 | `rail_v` | Rail vertical (se raccorde en haut et en bas) | Decor | aucune |
| 8 | `rail_bd` | Rail en virage : relie le BAS et la DROITE | Decor | aucune |
| 9 | `rail_bg` | Rail en virage : relie le BAS et la GAUCHE | Decor | aucune |
| 10 | `rail_hd` | Rail en virage : relie le HAUT et la DROITE | Decor | aucune |
| 11 | `rail_hg` | Rail en virage : relie le HAUT et la GAUCHE | Decor | aucune |
| 12 | `ombre_mur_haut` | Ombre portée d'un mur du haut sur le sol (trame), sous un mur_haut | Decor | aucune |
| 13 | `ombre_mur_gauche` | Ombre portée d'un mur de gauche sur le sol | Decor | aucune |
| 14 | `ombre_mur_coin` | Ombre portée dans un angle haut-gauche (mur en haut et à gauche) | Decor | aucune |
| 15 | `gravats` | Petit tas de gravats et poussière | Decor | aucune |

## 2. Murs de galerie (terrain `Murs`)

Roche taillée : dessus sombre + face avant plus claire visible. Toutes les tuiles sont pleines. Mêmes numéros et mêmes formes que `temple_racines` (16 à 30).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 16 | `mur_haut` | Mur du haut de la salle : sol en dessous, face avant visible | Murs | pleine |
| 17 | `mur_bas` | Mur du bas de la salle : sol au-dessus | Murs | pleine |
| 18 | `mur_gauche` | Mur de gauche de la salle : sol à droite | Murs | pleine |
| 19 | `mur_droite` | Mur de droite de la salle : sol à gauche | Murs | pleine |
| 20 | `mur_coin_int_hg` | Coin intérieur haut-gauche (angle de salle) : sol seulement en bas-droite | Murs | pleine |
| 21 | `mur_coin_int_hd` | Coin intérieur haut-droite (angle de salle) : sol seulement en bas-gauche | Murs | pleine |
| 22 | `mur_coin_int_bg` | Coin intérieur bas-gauche (angle de salle) : sol seulement en haut-droite | Murs | pleine |
| 23 | `mur_coin_int_bd` | Coin intérieur bas-droite (angle de salle) : sol seulement en haut-gauche | Murs | pleine |
| 24 | `mur_coin_ext_hg` | Coin extérieur haut-gauche d'un bloc de mur posé dans la salle : mur seulement en bas-droite | Murs | pleine |
| 25 | `mur_coin_ext_hd` | Coin extérieur haut-droite d'un bloc de mur : mur seulement en bas-gauche | Murs | pleine |
| 26 | `mur_coin_ext_bg` | Coin extérieur bas-gauche d'un bloc de mur : mur seulement en haut-droite | Murs | pleine |
| 27 | `mur_coin_ext_bd` | Coin extérieur bas-droite d'un bloc de mur : mur seulement en haut-gauche | Murs | pleine |
| 28 | `mur_plein` | Mur plein (intérieur d'un mur épais, rien de visible autour) | Murs | pleine |
| 29 | `mur_diag_a` | Mur en diagonale (mur en haut-gauche et bas-droite) — complète le terrain | Murs | pleine |
| 30 | `mur_diag_b` | Mur en diagonale (mur en haut-droite et bas-gauche) — complète le terrain | Murs | pleine |

## 3. Trous de passage (vers l'étage du dessous)

IDS 31 à 39 : trou de passage rectangulaire (bord de planches, lueur turquoise). Décoratif, calque `Sol`, sans collision ; l'objet `Chute` se pose par-dessus. Jamais mortel : à ne pas confondre avec les trous 58 à 66.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 32 | `trou_passage_bord_haut` | Bord haut d'un trou de passage (sol au-dessus) | Sol | aucune |
| 33 | `trou_passage_bord_bas` | Bord bas d'un trou de passage (sol en dessous) | Sol | aucune |
| 34 | `trou_passage_bord_gauche` | Bord gauche d'un trou de passage (sol à gauche) | Sol | aucune |
| 35 | `trou_passage_bord_droite` | Bord droit d'un trou de passage (sol à droite) | Sol | aucune |
| 36 | `trou_passage_coin_hg` | Coin haut-gauche d'un trou de passage rectangulaire | Sol | aucune |
| 37 | `trou_passage_coin_hd` | Coin haut-droite d'un trou de passage rectangulaire | Sol | aucune |
| 38 | `trou_passage_coin_bg` | Coin bas-gauche d'un trou de passage rectangulaire | Sol | aucune |
| 39 | `trou_passage_coin_bd` | Coin bas-droite d'un trou de passage rectangulaire | Sol | aucune |

## 4. Ouvertures de porte (cadre d'étais)

Remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` dans la même case du calque `Dessus`, puis l'objet `Porte` par-dessus. Mêmes numéros et mêmes collisions que `temple_racines`.

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

## 5. Poussière de charbon (terrain `Poussiere`)

Peindre la poussière avec ce terrain plutôt que la tuile 5 seule : les bords (48 à 55, 67 à 71) font une transition irrégulière vers le sol.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `poussiere_bord_haut` | Poussière : bord haut (sol en dessous) | Sol | aucune |
| 49 | `poussiere_bord_bas` | Poussière : bord bas (sol au-dessus) | Sol | aucune |
| 50 | `poussiere_bord_gauche` | Poussière : bord gauche (sol à droite) | Sol | aucune |
| 51 | `poussiere_bord_droite` | Poussière : bord droite (sol à gauche) | Sol | aucune |
| 52 | `poussiere_creux_hg` | Poussière : coin rentrant, sol seulement en haut-gauche | Sol | aucune |
| 53 | `poussiere_creux_hd` | Poussière : coin rentrant, sol seulement en haut-droite | Sol | aucune |
| 54 | `poussiere_creux_bg` | Poussière : coin rentrant, sol seulement en bas-gauche | Sol | aucune |
| 55 | `poussiere_creux_bd` | Poussière : coin rentrant, sol seulement en bas-droite | Sol | aucune |

## 6. Escaliers et TROUS MORTELS (58 à 66)

Les escaliers 56/57 : la transition est un objet `Sortie` (`transition=escalier`). Les trous 58 à 66 sont à la même place que dans `temple_racines` : toute la case fait tomber (-1 PV, retour au Spawn de la salle).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 56 | `escalier_montant` | Escalier qui monte (vers le haut de l'écran) ; la transition est un objet Sortie | Sol | aucune |
| 57 | `escalier_descendant` | Escalier qui descend (vers le bas de l'écran) ; la transition est un objet Sortie | Sol | aucune |
| 58 | `trou` | TROU MORTEL : on tombe dans toute la case | Sol | aucune |
| 59 | `trou_bord_haut` | TROU MORTEL : Bord haut d'un trou (sol au-dessus) : paroi du fond visible | Sol | aucune |
| 60 | `trou_bord_bas` | TROU MORTEL : Bord bas d'un trou (sol en dessous) | Sol | aucune |
| 61 | `trou_bord_gauche` | TROU MORTEL : Bord gauche d'un trou (sol à gauche) | Sol | aucune |
| 62 | `trou_bord_droite` | TROU MORTEL : Bord droit d'un trou (sol à droite) | Sol | aucune |
| 63 | `trou_coin_hg` | TROU MORTEL : Coin haut-gauche d'un trou rectangulaire | Sol | aucune |
| 64 | `trou_coin_hd` | TROU MORTEL : Coin haut-droite d'un trou rectangulaire | Sol | aucune |
| 65 | `trou_coin_bg` | TROU MORTEL : Coin bas-gauche d'un trou rectangulaire | Sol | aucune |
| 66 | `trou_coin_bd` | TROU MORTEL : Coin bas-droite d'un trou rectangulaire | Sol | aucune |
| 67 | `poussiere_coin_hg` | Poussière : coin haut-gauche d'une zone de poussière (poussière seulement en bas-droite) | Sol | aucune |
| 68 | `poussiere_coin_hd` | Poussière : coin haut-droite d'une zone de poussière (poussière seulement en bas-gauche) | Sol | aucune |
| 69 | `poussiere_coin_bg` | Poussière : coin bas-gauche d'une zone de poussière (poussière seulement en haut-droite) | Sol | aucune |
| 70 | `poussiere_coin_bd` | Poussière : coin bas-droite d'une zone de poussière (poussière seulement en haut-gauche) | Sol | aucune |
| 71 | `poussiere_diag` | Poussière : deux coins opposés (poussière en haut-gauche et bas-droite) | Sol | aucune |

## 7. ÉBOULIS bloquants et cailloux

Éboulis fermé -> dégagé (même logique que `montagne` 176 à 181) : la bombe retire la tuile fermée de `Murs` et le code pose la version dégagée. 72 et 74 -> 76 ; 73 et 75 -> 77. Un éboulis 2×1 se pose avec 74 puis 75.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 72 | `eboulis_a` | ÉBOULIS : tas de rochers, case pleine (solide) | Murs | pleine |
| 73 | `eboulis_b` | ÉBOULIS : variante B (solide) | Murs | pleine |
| 74 | `eboulis_g` | ÉBOULIS large, moitié gauche (2×1, solide) | Murs | pleine |
| 75 | `eboulis_d` | ÉBOULIS large, moitié droite (2×1, solide) | Murs | pleine |
| 76 | `eboulis_degage_a` | Éboulis DÉGAGÉ : gravats au sol (passable), remplace eboulis_a et eboulis_g | Sol | aucune |
| 77 | `eboulis_degage_b` | Éboulis DÉGAGÉ : gravats, variante, remplace eboulis_b et eboulis_d | Sol | aucune |
| 78 | `eboulis_poussiere` | Poussière et cailloux autour d'un éboulis (décor) | Decor | aucune |
| 79 | `cailloux` | Quelques cailloux épars | Decor | aucune |

## 8. Eau souterraine peu profonde (terrain `Eau`)

Eau peu profonde, calque `Sol`, sans collision (Brann la traverse). Le bord passe au milieu de la tuile. Il manque volontairement les deux tuiles en diagonale.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 80 | `eau` | Eau peu profonde, case entière (Brann la traverse) | Sol | aucune |
| 81 | `eau_bord_haut` | Eau peu profonde : bord haut (sol au-dessus) | Sol | aucune |
| 82 | `eau_bord_bas` | Eau peu profonde : bord bas (sol en dessous) | Sol | aucune |
| 83 | `eau_bord_gauche` | Eau peu profonde : bord gauche (sol à gauche) | Sol | aucune |
| 84 | `eau_bord_droite` | Eau peu profonde : bord droite (sol à droite) | Sol | aucune |
| 85 | `eau_creux_hg` | Eau peu profonde : coin rentrant, sol seulement en haut-gauche | Sol | aucune |
| 86 | `eau_creux_hd` | Eau peu profonde : coin rentrant, sol seulement en haut-droite | Sol | aucune |
| 87 | `eau_creux_bg` | Eau peu profonde : coin rentrant, sol seulement en bas-gauche | Sol | aucune |
| 88 | `eau_creux_bd` | Eau peu profonde : coin rentrant, sol seulement en bas-droite | Sol | aucune |
| 89 | `eau_coin_hg` | Eau peu profonde : coin haut-gauche d'une étendue rectangulaire (eau seulement dans le quart opposé) | Sol | aucune |
| 90 | `eau_coin_hd` | Eau peu profonde : coin haut-droite d'une étendue rectangulaire (eau seulement dans le quart opposé) | Sol | aucune |
| 91 | `eau_coin_bg` | Eau peu profonde : coin bas-gauche d'une étendue rectangulaire (eau seulement dans le quart opposé) | Sol | aucune |
| 92 | `eau_coin_bd` | Eau peu profonde : coin bas-droite d'une étendue rectangulaire (eau seulement dans le quart opposé) | Sol | aucune |

## 9. Rails (suite), wagonnets, minerai

Les butoirs ferment un rail (nommés par le côté où le rail s'arrête). Le wagonnet 2×1 = `wagonnet_g` puis `wagonnet_d` (solide à la base, on le contourne).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `rail_croix` | Croisement de rails (haut, bas, gauche, droite) | Decor | aucune |
| 97 | `rail_butoir_haut` | Butoir : le rail s'arrête en HAUT de la case (il arrive par le bas) | Decor | aucune |
| 98 | `rail_butoir_bas` | Butoir : le rail s'arrête en BAS de la case (il arrive par le haut) | Decor | aucune |
| 99 | `rail_butoir_gauche` | Butoir : le rail s'arrête à GAUCHE de la case (il arrive par la droite) | Decor | aucune |
| 100 | `rail_butoir_droite` | Butoir : le rail s'arrête à DROITE de la case (il arrive par la gauche) | Decor | aucune |
| 101 | `rail_casse_h` | Rail horizontal brisé (traverses arrachées) | Decor | aucune |
| 102 | `rail_casse_v` | Rail vertical brisé (traverses arrachées) | Decor | aucune |
| 103 | `traverses` | Traverses de bois sans rail (voie arrachée) | Decor | aucune |
| 104 | `wagonnet_g` | Wagonnet de mine sur rail, moitié gauche (2×1, solide) | Murs | partielle : 0,10 32×20 |
| 105 | `wagonnet_d` | Wagonnet de mine sur rail, moitié droite (2×1, solide) | Murs | partielle : 0,10 32×20 |
| 106 | `wagonnet_v` | Wagonnet vu de face, vide (1×1, solide) | Murs | partielle : 4,8 24×22 |
| 107 | `wagonnet_renverse` | Wagonnet renversé, minerai répandu (1×1, solide) | Murs | partielle : 4,8 24×22 |
| 108 | `wagonnet_minerai` | Wagonnet de face plein de minerai (1×1, solide) | Murs | partielle : 4,8 24×22 |
| 109 | `minerai_tas_a` | Tas de minerai (solide) | Murs | partielle : 4,8 24×22 |
| 110 | `minerai_tas_b` | Tas de minerai, variante (solide) | Murs | partielle : 4,8 24×22 |
| 111 | `minerai_sol` | Éclats de minerai épars au sol | Decor | aucune |

## 10. Étais, poutres, lanternes, mobilier

Un étai = 2 cases : `etai_base` (Murs, solide) + `etai_haut` (Dessus) juste au-dessus. Une galerie étayée = `poutre_g`, `poutre_h` (autant que nécessaire), `poutre_d` sur `Dessus`, au-dessus d'un couloir.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 112 | `etai_haut` | Haut d'étai (poutre transversale), case au-dessus de etai_base | Dessus | aucune |
| 113 | `etai_base` | Base d'étai : poteau de bois (solide, étroit) | Murs | partielle : 11,14 10×18 |
| 114 | `poutre_h` | Poutre horizontale en travers d'un couloir (Dessus ; Brann passe dessous) | Dessus | aucune |
| 115 | `poutre_g` | Extrémité gauche d'une poutre sur son poteau (Dessus) | Dessus | aucune |
| 116 | `poutre_d` | Extrémité droite d'une poutre sur son poteau (Dessus) | Dessus | aucune |
| 117 | `etai_mur` | Étai plaqué contre une face de mur (à poser sur une tuile de mur, Dessus) | Dessus | aucune |
| 118 | `planches_sol` | Planches de bois au sol (plancher de mine) | Decor | aucune |
| 119 | `lanterne` | Lanterne accrochée (Dessus) | Dessus | aucune |
| 120 | `pioche_sol` | Pioche oubliée au sol | Decor | aucune |
| 121 | `tonneau` | Tonneau de mine (solide) | Murs | partielle : 4,8 24×22 |
| 122 | `caisse` | Caisse de mine (solide) | Murs | partielle : 4,8 24×22 |
| 123 | `toile_araignee` | Toile d'araignée dans un angle (coin haut-gauche de la case) | Decor | aucune |
| 124 | `sol_filon` | Sol avec un filon de minerai brillant (variante de sol) | Sol | aucune |
| 125 | `sol_reflet_cristal` | Sol baigné d'un reflet de cristaux (variante de sol) | Sol | aucune |
| 126 | `ossements` | Ossements d'un mineur | Decor | aucune |
| 127 | `casque_mineur` | Casque de mineur abandonné | Decor | aucune |

## 11. Cristaux lumineux (décor)

Cristaux cyan de la mine ; le cristal rouge évoque celui de Gorm. Les petits sont du décor sans collision. Un gros cristal = `cristal_gros_base` (Murs) + `cristal_gros_haut` (Dessus) au-dessus.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 128 | `cristal_a` | Petits cristaux cyan au sol (décor) | Decor | aucune |
| 129 | `cristal_b` | Amas de cristaux cyan au sol, variante (décor) | Decor | aucune |
| 130 | `cristal_rouge` | Petit cristal rouge au sol (décor, traces de corruption) | Decor | aucune |
| 131 | `cristal_gros_base` | Gros cristal cyan : pied (solide) | Murs | partielle : 2,14 28×18 |
| 132 | `cristal_gros_haut` | Gros cristal cyan : pointe, case au-dessus de cristal_gros_base | Dessus | aucune |
| 133 | `cristal_mur` | Cristaux qui percent une face de mur (à poser sur une tuile de mur, Dessus) | Dessus | aucune |
| 134 | `lueur_cristal` | Tache de lueur cyan au sol (semi-transparente, sous un cristal) | Decor | aucune |
| 135 | `veine_mur` | Veine de minerai dans une face de mur (à poser sur une tuile de mur, Dessus) | Dessus | aucune |

## 12. Arène de Gorm

Sol de l'arène (dalles gravées, plus claires et violettes que le reste de la mine), cratères des rochers tombés et pilier. Le pilier = `pilier_base` (Murs) + `pilier_haut` (Dessus) ; les rectangles Tiled nommés `pilier` restent les piliers du boss.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 136 | `arene_a` | Sol de l'arène : dalles gravées | Sol | aucune |
| 137 | `arene_b` | Sol de l'arène : dalles gravées, variante | Sol | aucune |
| 138 | `arene_centre` | Sol de l'arène : sceau gravé du centre | Sol | aucune |
| 139 | `arene_fissure` | Sol de l'arène fissuré par les coups de Gorm | Sol | aucune |
| 140 | `arene_gravats` | Éclats de roche sur le sol de l'arène (décor) | Decor | aucune |
| 141 | `arene_cratere` | Cratère laissé par un rocher tombé (décor) | Decor | aucune |
| 142 | `pilier_haut` | Haut de pilier de pierre, case au-dessus de pilier_base | Dessus | aucune |
| 143 | `pilier_base` | Base de pilier de pierre (solide) | Murs | partielle : 2,14 28×18 |

## 13. MURS FISSURÉS (bombes) : fermé -> ouvert

Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus). Ouverts : sur `Decor`, opaques (ils couvrent tout le mur : trou noir dans la roche, la `Sortie` se pose dessus). Paires : 144->148, 145->149, 146->150, 147->151, 152->153. `mur_craquele` (154) est un simple indice visuel sans fonction.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 144 | `mur_fissure_haut` | MUR FISSURÉ du haut (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l'ouvre) | Murs | pleine |
| 145 | `mur_fissure_bas` | MUR FISSURÉ du bas (solide) | Murs | pleine |
| 146 | `mur_fissure_gauche` | MUR FISSURÉ de gauche (solide) | Murs | pleine |
| 147 | `mur_fissure_droite` | MUR FISSURÉ de droite (solide) | Murs | pleine |
| 148 | `mur_fissure_haut_ouvert` | Mur du haut OUVERT : trou noir dans la roche, gravats (Sortie dessus) | Decor | aucune |
| 149 | `mur_fissure_bas_ouvert` | Mur du bas OUVERT (Sortie dessus) | Decor | aucune |
| 150 | `mur_fissure_gauche_ouvert` | Mur de gauche OUVERT (Sortie dessus) | Decor | aucune |
| 151 | `mur_fissure_droite_ouvert` | Mur de droite OUVERT (Sortie dessus) | Decor | aucune |
| 152 | `rocher_fissure` | ROCHER FISSURÉ : bloc craquelé posé au sol (solide ; objet MurFissure dessus) | Murs | pleine |
| 153 | `rocher_fissure_ouvert` | Rocher fissuré OUVERT : cavité noire entre des blocs (Sortie dessus) | Decor | aucune |
| 154 | `mur_craquele` | Mur du haut craquelé (indice discret, sans fonction ; solide) | Murs | pleine |

## 14. Ajouts : poutres, veines, rails en T, mobilier

Demandés par `maps/donjon2/plan.md` §7. `poutre_sciee` = décor de la salle 08. `mur_veine_etoile` = mur lumineux bleu-blanc de la salle 13. `eboulis_ouverture_h/v` : éboulis dans l encadrement d une porte (fermé -> 76/77).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 160 | `rail_t_haut` | Rail en T : rail horizontal + branche vers le HAUT | Decor | aucune |
| 161 | `rail_t_bas` | Rail en T : rail horizontal + branche vers le BAS | Decor | aucune |
| 162 | `rail_t_gauche` | Rail en T : rail vertical + branche vers la GAUCHE | Decor | aucune |
| 163 | `rail_t_droite` | Rail en T : rail vertical + branche vers la DROITE | Decor | aucune |
| 164 | `eboulis_ouverture_h` | Éboulis dans une ouverture horizontale (porte haut/bas) (solide ; se dégage comme 72 -> 76) | Murs | pleine |
| 165 | `eboulis_ouverture_v` | Éboulis dans une ouverture verticale (porte gauche/droite) (solide ; se dégage comme 73 -> 77) | Murs | pleine |
| 166 | `pelle_sol` | Pelle plantée dans un tas de gravats | Decor | aucune |
| 167 | `etabli` | Établi de mineur : outils posés (solide) | Murs | partielle : 4,8 24×22 |
| 168 | `panneau_bois` | Panneau de bois (support d un indice ; solide, étroit) | Murs | partielle : 11,14 10×18 |
| 169 | `flaque` | Flaque d eau sur le sol (sans effet) | Decor | aucune |

## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain a une couleur « sol » (tuiles 0 à 2) et une couleur de terrain.

| Terrain | Couleurs | Calque | Tuiles |
| --- | --- | --- | --- |
| `Murs` | `mur` (le reste = vide) | Murs | 16 à 30 |
| `Trous` | `sol`, `trou` | Sol | 0 à 2 (sol), 58 à 66 |
| `Trous de passage` | `sol`, `passage` | Sol | 0 à 2 (sol), 31 à 39 |
| `Eau` | `sol`, `eau` | Sol | 0 à 2 (sol), 80 à 92 |
| `Poussiere` | `sol`, `poussiere` | Sol | 0 à 2 (sol), 5, 48 à 55, 67 à 71 |

## Notes

- IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier.
- Terrains Tiled (Wang par coins) : `Murs` (16 à 30), `Trous` (0-2, 58 à 66), `Trous de passage` (0-2, 31 à 39), `Eau` (0-2, 80 à 92), `Poussiere` (0-2, 5, 48 à 55, 67 à 71). Même organisation que `temple_racines` : une couleur « sol » (0 à 2) et une couleur de terrain.
- Murs : une seule couleur `mur`. Peindre `mur` sur les coins du pourtour d'une salle de 20×11 donne l'anneau mur_haut / mur_bas / mur_gauche / mur_droite + les 4 coins intérieurs. Un seul coin peint au milieu de la salle donne un bloc de 2×2 tuiles. Les tuiles de mur sont entières.
- Trous mortels et trous de passage : rectangles seulement. Pour un trou 2×2 : coin_hg, coin_hd (ligne du haut), coin_bg, coin_bd (ligne du bas).
- Eau : le bord passe au milieu de la tuile (chaque quart de 16×16 est du sol ou de l'eau). Pas d'eau profonde dans ce tileset (réserve 93 à 95).
- Porte : remplacer la tuile de mur par `porte_<côté>`, poser `porte_<côté>_dessus` dans la même case de `Dessus`, puis l'objet `Porte`.
- À régler dans Tiled/Godot après livraison : animations de tuiles (cristaux qui brillent, eau), éventuelle propriété de tuile pour les trous.
