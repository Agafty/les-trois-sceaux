# Plan du tileset `sanctuaire` — Le Sanctuaire Englouti (donjon 3 : pierre à demi noyée, eau, passerelles, cryptes, arène d'Ondine)

> Fichier généré par `tools/sprites/sanctuaire.py` : modifier le script, pas ce fichier. **État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro).

- Image : `art/tilesets/sanctuaire.png`, 256×736 px, 8 colonnes × 23 lignes de tuiles 32×32, sans marge ni espacement (184 cases). Tileset Tiled : `maps/tilesets/sanctuaire.tsx` (collisions et terrains définis). `art/tilesets/sanctuaire_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 20 à 23 (ids 152 à 183) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette finale : pierre gris-violet et bleus-verts froids (comme la façade du Sanctuaire dans `lac`). En PLAN, **la couleur indique la famille** (dalle (bleu-gris) / crypte (bleu sombre) / mur (violet-gris) / eau peu profonde (bleu clair) / eau profonde (bleu foncé) / planches (brun) / chaussée (gris clair) / escalier (beige) / colonne (gris-bleu) / rune (cyan) / fissuré à la bombe (violet) / porte (orange) / algues lumineuses (vert) / balcon (rose) / estrade (or) / bassin (turquoise)) ; une zone plus sombre dans une tuile = zone solide.
- DEUX planches de même numérotation : `sanctuaire.png` (rez-de-chaussée, clair) et `sanctuaire_crypte.png` (cryptes : recoloration plus sombre ; tileset `sanctuaire_crypte.tsx` identique). Dans le dessin final, la crypte aura des algues lumineuses aux murs.
- **Aucune fosse ni trou** dans ce donjon : les ids 31 à 39 et 58 à 66 sont volontairement vides.

## POUR LE DÉVELOPPEUR ET LE LEVEL-DESIGNER : ids à connaître

Tilesets `sanctuaire` (rez-de-chaussée) ET `sanctuaire_crypte` (sous-sol) : **mêmes ids, mêmes collisions**, 8 colonnes, id local Tiled = ligne × 8 + colonne.

| Famille | Ids | Calque | À savoir |
| --- | --- | --- | --- |
| **MURS FISSURÉS** fermé -> ouvert (`TileRules`, salle 03) | **72 -> 76** (haut), **73 -> 77** (bas), **74 -> 78** (gauche), **75 -> 79** (droite) | fermés `Murs`, ouverts `Decor` | Comme `mine` 144 -> 148 : la bombe retire la tuile fermée de `Murs`, le code pose la version ouverte sur `Decor` (ou elle est déjà posée dessous). Les versions ouvertes sont opaques (fond noir). La salle 03 n'utilise qu'une orientation (le mur de l'alcôve est vertical : 74 ou 75). |
| **Escaliers** | 56 (montant), 57 (descendant) | `Sol` | Posent une `Sortie` `transition=escalier`, comme les autres donjons. |
| **Ids VIDES** | 31 à 39 et 58 à 66 | — | Réservés (trous de passage / trous mortels des autres donjons). Aucun trou dans ce donjon : **`HoleRules` / `HoleWatcher` n'ont rien à reconnaître ici** (ne pas y ajouter les tilesets `sanctuaire*`). |
| **EAU PROFONDE (solide)** | 96 à 111 | `Murs` | Terrain `Eau profonde` : collision par quarts de case (la moitié « rive » d'un bord reste praticable), flèches arrêtées comme par un mur. Se peint sur `Murs` ; dessous, mettre du sol. |
| **EAU PEU PROFONDE (praticable)** | 80 à 95 | `Sol` | Terrain `Eau`, sans collision, comme `mine`. |
| **PASSERELLES / CHAUSSÉE** | 48 à 55 | `Sol` | Praticables, sans collision. Posées sur `Sol` aux cases où l'on ne peint pas d'eau profonde sur `Murs` : la passerelle de 3 cases de large coupe le fossé. |
| **BALCON** de Corvan (salle 08) | 67 à 69, garde-corps 70 | `Murs` (67-69), `Dessus` (70) | Solide, inaccessible. |
| **MUR À RUNE** (`Porte` type `lanterne`) | tuile dessous : 144 `alcove_sol_rune` | `Sol` | L'image `art/puzzles/porte_mur_rune.png` (64×32 : fermée, ouverte) est posée par la `Porte`. Mur autour : 145 `mur_rune_grave` (indice discret, solide). |
| Piliers 2×2 du boss | 120 à 123 | `Murs` | Solides ; les rectangles `pilier` restent la référence du boss. |
| Bassins d'Ondine (3×3) | 128 à 136 (+ anneau 137/138 sur `Decor`) | `Sol` | Eau peu profonde, praticable. |

Tout le reste est géré par les collisions du `.tsx` (murs 16-30, portes 40-43, 67-69, 72-75, 96-110 et 111, 113-116, 120-123, 145-149, 151) : aucun code.

## Calques

- `Sol` : dalles, sol de crypte, eau peu profonde, passerelles et chaussée, escaliers, estrade, bassins d'Ondine
- `Decor` : algues lumineuses, coquillages, ombres, lueurs, anneaux d'ondes, ouvertures de mur fissuré (version ouverte)
- `Murs` : tout ce qui bloque (murs, eau profonde, colonnes, piliers, vasques, balcon, murs fissurés fermés). Collisions dans le tileset
- `Objets` : Sortie, Spawn, Ennemi, Coffre, Porte, MurFissure, Torche, boss_ondine, pilier… (objets Tiled, pas des tuiles)
- `Dessus` : passe devant Brann (haut de colonne, algues et fresques plaquées sur les murs, garde-corps du balcon)

## 1. Sols, algues, ombres

Rez-de-chaussée : dalles de pierre mouillée (0 à 3, au hasard), dalle gravée du sceau effacé (4, décor du Parvis), dalle à algues (5). Cryptes : sol bleu-gris (6 à 9). Algues lumineuses et coquillages sur `Decor`. Ombres 12 à 14 sous les murs (`Decor`).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `dalle_a` | Dalle de pierre mouillée, de base (bleu-gris) | Sol | aucune |
| 1 | `dalle_b` | Dalle de pierre mouillée avec reflets | Sol | aucune |
| 2 | `dalle_c` | Dalle de pierre en joints irréguliers | Sol | aucune |
| 3 | `dalle_fissuree` | Dalle fissurée (fissure en diagonale) | Sol | aucune |
| 4 | `dalle_sceau` | Dalle gravée d'un sceau effacé (centre du Parvis, une seule fois) | Sol | aucune |
| 5 | `dalle_algues` | Dalle recouverte d'algues vertes (variante de sol) | Sol | aucune |
| 6 | `crypte_a` | Sol de crypte bleu-gris, de base | Sol | aucune |
| 7 | `crypte_b` | Sol de crypte avec petits cailloux | Sol | aucune |
| 8 | `crypte_c` | Sol de crypte en dalles brisées | Sol | aucune |
| 9 | `crypte_d` | Sol de crypte avec algues lumineuses discrètes | Sol | aucune |
| 10 | `algues_lum_a` | Algues lumineuses au sol (guide visuel, décor) | Decor | aucune |
| 11 | `algues_lum_b` | Algues lumineuses au sol, variante (décor) | Decor | aucune |
| 12 | `ombre_mur_haut` | Ombre portée d'un mur du haut sur le sol (trame), sous un mur_haut | Decor | aucune |
| 13 | `ombre_mur_gauche` | Ombre portée d'un mur de gauche sur le sol | Decor | aucune |
| 14 | `ombre_mur_coin` | Ombre portée dans un angle haut-gauche (mur en haut et à gauche) | Decor | aucune |
| 15 | `coquillages` | Coquillages et petits cailloux posés au sol | Decor | aucune |

## 2. Murs de pierre à demi noyée (terrain `Murs`)

Pierre taillée, dessus sombre + face avant plus claire visible (algues au pied). Toutes les tuiles sont pleines. Mêmes numéros et mêmes formes que `mine` / `temple_racines` (16 à 30).

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

## 4. Ouvertures de salle (cadre de pierre)

Remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` dans la même case du calque `Dessus`, puis l'objet `Porte` par-dessus. Mêmes numéros et mêmes collisions que `mine`.

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

## 5. Passerelles de planches et chaussée de pierre

Praticables, calque `Sol`, sans collision. La passerelle (3 cases de large dans la salle 07) et la chaussée (salle 08) traversent un fossé d'eau profonde : ne PAS peindre l'eau profonde (`Murs`) sur ces cases. Extrémités pour finir proprement.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `planches_h` | Passerelle de planches horizontale (planches dans le sens est-ouest) | Sol | aucune |
| 49 | `planches_v` | Passerelle de planches verticale (planches dans le sens nord-sud) | Sol | aucune |
| 50 | `chaussee_pierre` | Chaussée de pierre, dalles larges (traverse un fossé) | Sol | aucune |
| 51 | `chaussee_pierre_b` | Chaussée de pierre, variante usée | Sol | aucune |
| 52 | `planches_h_g` | Passerelle horizontale : extrémité gauche (poteaux) | Sol | aucune |
| 53 | `planches_h_d` | Passerelle horizontale : extrémité droite (poteaux) | Sol | aucune |
| 54 | `planches_v_haut` | Passerelle verticale : extrémité haute (poteaux) | Sol | aucune |
| 55 | `planches_v_bas` | Passerelle verticale : extrémité basse (poteaux) | Sol | aucune |

## 6. Escaliers (56/57) ; ids réservés 58 à 66 (vides)

La transition est un objet `Sortie` (`transition=escalier`). 58 à 66 = trous mortels des autres donjons : VIDES ici (aucune fosse dans le Sanctuaire).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 56 | `escalier_montant` | Escalier qui monte (vers le haut de l'écran), pierre noyée ; la transition est un objet Sortie | Sol | aucune |
| 57 | `escalier_descendant` | Escalier qui descend (vers le bas de l'écran), pierre noyée ; la transition est un objet Sortie | Sol | aucune |

## 8. MURS FISSURÉS (bombes) : fermé -> ouvert

Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus, fissures claires). Ouverts : sur `Decor`, opaques (trou noir dans la pierre). Paires : **72->76, 73->77, 74->78, 75->79** (haut, bas, gauche, droite). La salle 03 n'utilise qu'une orientation.

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

## 9. Eau peu profonde (terrain `Eau`)

Praticable, calque `Sol`, sans collision, sans ralentissement. Le bord passe au milieu de la tuile. 93 et 94 : eau pleine avec dalles affleurantes (se mélangent à 80) ; 95 : reflets (variante à animer).

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
| 90 | `eau_coin_hd` | Eau peu profonde : coin haut-droite d'une étendue rectangulaire | Sol | aucune |
| 91 | `eau_coin_bg` | Eau peu profonde : coin bas-gauche d'une étendue rectangulaire | Sol | aucune |
| 92 | `eau_coin_bd` | Eau peu profonde : coin bas-droite d'une étendue rectangulaire | Sol | aucune |
| 93 | `eau_dalles_a` | Eau peu profonde pleine avec dalles affleurantes (variante, mélanger avec 80) | Sol | aucune |
| 94 | `eau_dalles_b` | Eau peu profonde pleine avec dalles affleurantes, variante | Sol | aucune |
| 95 | `eau_reflets` | Eau peu profonde à reflets brillants (à animer plus tard ; pas dans le terrain) | Sol | aucune |

## 10. Eau profonde SOLIDE (terrain `Eau profonde`, calque `Murs`)

Fossés des salles 07 et 08. Collision par quarts de case : la partie « rive » d'une tuile de bord reste praticable, la partie eau est solide (flèches arrêtées comme par un mur). Se peint sur `Murs` ; sous les cases de rive, mettre du sol. Les passerelles/chaussée (48 à 55) se posent sur `Sol` aux cases où l'on ne peint pas d'eau profonde.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `eau_profonde` | EAU PROFONDE : case entière (solide) | Murs | pleine |
| 97 | `eau_profonde_bord_haut` | EAU PROFONDE : bord haut (rive au-dessus) (solide sur la partie eau) | Murs | partielle : 0,16 32×16 |
| 98 | `eau_profonde_bord_bas` | EAU PROFONDE : bord bas (rive en dessous) (solide sur la partie eau) | Murs | partielle : 0,0 32×16 |
| 99 | `eau_profonde_bord_gauche` | EAU PROFONDE : bord gauche (rive à gauche) (solide sur la partie eau) | Murs | partielle : 16,0 16×32 |
| 100 | `eau_profonde_bord_droite` | EAU PROFONDE : bord droite (rive à droite) (solide sur la partie eau) | Murs | partielle : 0,0 16×32 |
| 101 | `eau_profonde_creux_hg` | EAU PROFONDE : coin rentrant, rive seulement en haut-gauche (solide sur la partie eau) | Murs | partielle : 16,0 16×16 ; 0,16 32×16 |
| 102 | `eau_profonde_creux_hd` | EAU PROFONDE : coin rentrant, rive seulement en haut-droite (solide sur la partie eau) | Murs | partielle : 0,0 16×16 ; 0,16 32×16 |
| 103 | `eau_profonde_creux_bg` | EAU PROFONDE : coin rentrant, rive seulement en bas-gauche (solide sur la partie eau) | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 104 | `eau_profonde_creux_bd` | EAU PROFONDE : coin rentrant, rive seulement en bas-droite (solide sur la partie eau) | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 105 | `eau_profonde_coin_hg` | EAU PROFONDE : coin haut-gauche d'un fossé rectangulaire (eau seulement dans le quart bas-droite) (solide sur la partie eau) | Murs | partielle : 16,16 16×16 |
| 106 | `eau_profonde_coin_hd` | EAU PROFONDE : coin haut-droite d'un fossé rectangulaire (eau seulement dans le quart bas-gauche) (solide sur la partie eau) | Murs | partielle : 0,16 16×16 |
| 107 | `eau_profonde_coin_bg` | EAU PROFONDE : coin bas-gauche d'un fossé rectangulaire (eau seulement dans le quart haut-droite) (solide sur la partie eau) | Murs | partielle : 16,0 16×16 |
| 108 | `eau_profonde_coin_bd` | EAU PROFONDE : coin bas-droite d'un fossé rectangulaire (eau seulement dans le quart haut-gauche) (solide sur la partie eau) | Murs | partielle : 0,0 16×16 |
| 109 | `eau_profonde_diag_a` | EAU PROFONDE : deux quarts opposés (eau en haut-gauche et bas-droite) (solide sur la partie eau) | Murs | partielle : 0,0 16×16 ; 16,16 16×16 |
| 110 | `eau_profonde_diag_b` | EAU PROFONDE : deux quarts opposés (eau en haut-droite et bas-gauche) (solide sur la partie eau) | Murs | partielle : 16,0 16×16 ; 0,16 16×16 |
| 111 | `eau_profonde_b` | EAU PROFONDE pleine, variante à reflets (mélanger avec 96 ; à animer plus tard) | Murs | pleine |

## 11. Colonnes, vasques, statues, fresques

Une colonne de 1 case = `colonne_base` (Murs, solide) + `colonne_haut` (Dessus) juste au-dessus. Algues et fresques se plaquent sur une tuile de mur (calque `Dessus`).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 112 | `colonne_haut` | Haut de colonne (chapiteau), case au-dessus de colonne_base | Dessus | aucune |
| 113 | `colonne_base` | Base de colonne de pierre, pieds dans l'eau (solide) | Murs | partielle : 2,14 28×18 |
| 114 | `colonne_brisee` | Colonne brisée, tronc coupé (solide, 1 seule case) | Murs | partielle : 4,8 24×22 |
| 115 | `vasque` | Vasque de pierre pleine d'eau (solide) | Murs | partielle : 4,8 24×22 |
| 116 | `statue_brisee` | Statue de gardien brisée (solide) | Murs | partielle : 4,8 24×22 |
| 117 | `fresque_mur` | Fresque effacée plaquée sur une face de mur (Dessus) | Dessus | aucune |
| 118 | `algues_mur` | Algues pendantes sur une face de mur (Dessus) | Dessus | aucune |
| 119 | `algues_mur_lum` | Algues LUMINEUSES sur une face de mur (Dessus, cryptes surtout) | Dessus | aucune |

## 12. Piliers 2×2 (arène du boss), estrade, divers

Pilier de 4 cases (le boss : 4 piliers de 2×2) : `pilier_hg` `pilier_hd` / `pilier_bg` `pilier_bd`, tous sur `Murs`, solides. Les rectangles Tiled nommés `pilier` restent ceux du boss. Estrade : sol surélevé de la chapelle et d'Ondine (praticable).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 120 | `pilier_hg` | Pilier 2×2 : haut-gauche (solide) | Murs | partielle : 2,2 30×30 |
| 121 | `pilier_hd` | Pilier 2×2 : haut-droite (solide) | Murs | partielle : 0,2 30×30 |
| 122 | `pilier_bg` | Pilier 2×2 : bas-gauche (solide) | Murs | partielle : 2,0 30×30 |
| 123 | `pilier_bd` | Pilier 2×2 : bas-droite (solide) | Murs | partielle : 0,0 30×30 |
| 124 | `estrade_dalle` | Estrade de pierre (chapelle de la lanterne, estrade d'Ondine) : dalle dorée | Sol | aucune |
| 125 | `estrade_marches` | Marches d'estrade (bord bas de l'estrade, praticable) | Sol | aucune |
| 126 | `lueur_bleue` | Tache de lueur bleue au sol (semi-transparente) | Decor | aucune |
| 127 | `debris` | Débris de pierre et gravats noyés | Decor | aucune |

## 13. Bassin rond d'Ondine (arène, 6 bassins de 3×3)

Bassin de 3×3 cases, eau peu profonde praticable avec margelle de pierre : `bassin_hg bassin_h bassin_hd / bassin_g bassin_c bassin_d / bassin_bg bassin_b bassin_bd` sur `Sol`, sans collision. Le `Marqueur` `ondine_surgit_N` va sur `bassin_c`. L'anneau d'ondes (137/138, deux images) se pose sur `Decor`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 128 | `bassin_hg` | Bassin d'Ondine : margelle hg | Sol | aucune |
| 129 | `bassin_h` | Bassin d'Ondine : margelle h | Sol | aucune |
| 130 | `bassin_hd` | Bassin d'Ondine : margelle hd | Sol | aucune |
| 131 | `bassin_g` | Bassin d'Ondine : margelle g | Sol | aucune |
| 132 | `bassin_c` | Bassin d'Ondine : centre (eau) | Sol | aucune |
| 133 | `bassin_d` | Bassin d'Ondine : margelle d | Sol | aucune |
| 134 | `bassin_bg` | Bassin d'Ondine : margelle bg | Sol | aucune |
| 135 | `bassin_b` | Bassin d'Ondine : margelle b | Sol | aucune |
| 136 | `bassin_bd` | Bassin d'Ondine : margelle bd | Sol | aucune |
| 137 | `anneau_ondes_a` | Anneau d'ondes qui annonce le surgissement d'Ondine, image A (Decor, semi-transparent) | Decor | aucune |
| 138 | `anneau_ondes_b` | Anneau d'ondes, image B (plus large) | Decor | aucune |

## 14. Mur à rune, chapelle

Le mur à rune est une `Porte` (type `lanterne`, `apparence=mur_rune`) dont l'image `art/puzzles/porte_mur_rune.png` couvre l'alcôve ; dessous : `alcove_sol_rune`. Le mur autour est un mur ordinaire (16-30) ou `mur_rune_grave`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 144 | `alcove_sol_rune` | Fond d'alcôve : dalle avec rune bleue discrète (sous le mur à rune ; praticable une fois la porte ouverte) | Sol | aucune |
| 145 | `mur_rune_grave` | Mur plein avec une rune gravée très discrète (indice, solide) | Murs | pleine |
| 146 | `mur_algues` | Mur plein couvert d'algues (variante, solide) | Murs | pleine |
| 147 | `mur_fresque` | Mur plein avec fresque (variante, solide) | Murs | pleine |
| 148 | `mur_eau` | Mur plein dont le pied baigne dans l'eau (variante, solide) | Murs | pleine |
| 149 | `mur_lumineux` | Mur plein aux algues lumineuses (cryptes, solide) | Murs | pleine |
| 150 | `dalle_lanterne` | Dalle gravée d'une lanterne (piédestal de la chapelle 04, texte d'indice) | Sol | aucune |
| 151 | `piedestal` | Piédestal de pierre (solide) | Murs | partielle : 4,8 24×22 |

## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T).

| Terrain | Couleurs | Calque | Tuiles |
| --- | --- | --- | --- |
| `Murs` | `mur` (le reste = vide) | Murs | 16 à 30 |
| `Eau` | `sol`, `eau` | Sol | 0 à 2 (sol), 80 à 94 (93-94 = pleines, au hasard avec 80) |
| `Eau profonde` | `profonde` (le reste = vide) | **Murs** | 96 à 110 (111 = variante pleine) |

## Notes

- IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier (mur fissuré 72->76… ; aucun id de trou).
- Terrains Tiled (Wang par coins) : `Murs` (16 à 30), `Eau` (0-2, 80 à 94), `Eau profonde` (96 à 111, calque `Murs`). Pas de terrain de trou.
- Eau profonde : se peint sur `Murs` ; les tuiles de rive ont une collision par quarts. Une passerelle (48-55) ou la chaussée (50-51) se pose sur `Sol` à la place de l'eau.
- Porte : remplacer la tuile de mur par `porte_<côté>`, poser `porte_<côté>_dessus` dans la même case de `Dessus`, puis l'objet `Porte`.
- Lumière : braseros, torches et lueurs sont des objets (`Torche`) ou gérés par le code, pas des tuiles.
- À régler dans Tiled/Godot après livraison : animations de tuiles (eau, reflets, anneaux d'ondes 137/138).
