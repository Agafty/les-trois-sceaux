# Plan du tileset `temple_racines` — Temple des Racines (donjon 1)

> Fichier généré par `tools/sprites/temple_racines.py` : modifier le script, pas ce fichier.

- Image : `art/tilesets/temple_racines.png`, 256×512 px, 8 colonnes × 16 lignes de tuiles 32×32, sans marge ni espacement (128 cases).
- Tileset Tiled : `maps/tilesets/temple_racines.tsx` (collisions et terrains déjà définis).
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro : le dessin est fait au même emplacement que le plan d'origine. Les cases « réserve » sont vides et serviront aux ajouts.
- **Dessin final** (vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px) : dalles de pierre grises usées, murs de pierre taillée violet-gris (dessus sombre + face avant claire visible), racines brunes, ronces noires-violettes épineuses, trous avec bord de dalle clair, eau bleue, mousse et feuilles. Le dessin est dans `tools/sprites/temple_racines_final.py` ; `python tools/sprites/temple_racines.py --plan` régénère l'ancien plan à flèches.
- Collision : en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche).

## 1. Sol

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `dalle_a` | Dalle de pierre, variante A (4 dalles carrées) | Sol | aucune |
| 1 | `dalle_b` | Dalle de pierre, variante B (dalles longues en quinconce) | Sol | aucune |
| 2 | `dalle_c` | Dalle de pierre, variante C (grande dalle gravée) | Sol | aucune |
| 3 | `dalle_fissuree_a` | Dalle fissurée (fissure en diagonale) | Sol | aucune |
| 4 | `dalle_fissuree_b` | Dalle fissurée (fissure en étoile) | Sol | aucune |
| 5 | `terre` | Sol de terre battue | Sol | aucune |
| 6 | `racine_h` | Racine horizontale (se raccorde à gauche et à droite) | Decor | aucune |
| 7 | `racine_v` | Racine verticale (se raccorde en haut et en bas) | Decor | aucune |
| 8 | `racine_touffe` | Nœud de racines (départ ou fin d'une racine) | Decor | aucune |
| 9–15 | — | réserve (vide) | — | — |

## 2. Murs

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

## 2b. Trous de passage

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 31 | `trou_passage` | Trou de passage : case entière (fond vert-bleu lumineux, sans anneau) | Sol | aucune |
| 32 | `trou_passage_bord_haut` | Bord haut d'un trou de passage (sol au-dessus) | Sol | aucune |
| 33 | `trou_passage_bord_bas` | Bord bas d'un trou de passage (sol en dessous) | Sol | aucune |
| 34 | `trou_passage_bord_gauche` | Bord gauche d'un trou de passage (sol à gauche) | Sol | aucune |
| 35 | `trou_passage_bord_droite` | Bord droit d'un trou de passage (sol à droite) | Sol | aucune |
| 36 | `trou_passage_coin_hg` | Coin haut-gauche d'un trou de passage rectangulaire | Sol | aucune |
| 37 | `trou_passage_coin_hd` | Coin haut-droite d'un trou de passage rectangulaire | Sol | aucune |
| 38 | `trou_passage_coin_bg` | Coin bas-gauche d'un trou de passage rectangulaire | Sol | aucune |
| 39 | `trou_passage_coin_bd` | Coin bas-droite d'un trou de passage rectangulaire | Sol | aucune |

## 3. Ouvertures de porte

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
| 48–55 | — | réserve (vide) | — | — |

## 4. Escaliers et trous

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 56 | `escalier_montant` | Escalier qui monte (vers le haut de l'écran) ; la transition est un objet Sortie | Sol | aucune |
| 57 | `escalier_descendant` | Escalier qui descend (vers le bas de l'écran) ; la transition est un objet Sortie | Sol | aucune |
| 58 | `trou` | Trou : on tombe dans toute la case | Sol | aucune |
| 59 | `trou_bord_haut` | Bord haut d'un trou (sol au-dessus) : paroi du fond visible | Sol | aucune |
| 60 | `trou_bord_bas` | Bord bas d'un trou (sol en dessous) | Sol | aucune |
| 61 | `trou_bord_gauche` | Bord gauche d'un trou (sol à gauche) | Sol | aucune |
| 62 | `trou_bord_droite` | Bord droit d'un trou (sol à droite) | Sol | aucune |
| 63 | `trou_coin_hg` | Coin haut-gauche d'un trou rectangulaire | Sol | aucune |
| 64 | `trou_coin_hd` | Coin haut-droite d'un trou rectangulaire | Sol | aucune |
| 65 | `trou_coin_bg` | Coin bas-gauche d'un trou rectangulaire | Sol | aucune |
| 66 | `trou_coin_bd` | Coin bas-droite d'un trou rectangulaire | Sol | aucune |
| 67–71 | — | réserve (vide) | — | — |

## 5. Ronces noires de Morvath

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 72 | `ronces_bloc_a` | Bloc de ronces noires (infranchissable) | Murs | pleine |
| 73 | `ronces_bloc_b` | Bloc de ronces noires, variante | Murs | pleine |
| 74 | `ronces_sol_a` | Ronces rampantes au sol (décor) | Decor | aucune |
| 75 | `ronces_sol_b` | Ronces rampantes au sol, variante | Decor | aucune |
| 76–79 | — | réserve (vide) | — | — |

## 6. Eau

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
| 89 | `eau_coin_hg` | Eau peu profonde : coin haut-gauche d'une étendue rectangulaire (eau peu profonde seulement dans le quart opposé) | Sol | aucune |
| 90 | `eau_coin_hd` | Eau peu profonde : coin haut-droite d'une étendue rectangulaire (eau peu profonde seulement dans le quart opposé) | Sol | aucune |
| 91 | `eau_coin_bg` | Eau peu profonde : coin bas-gauche d'une étendue rectangulaire (eau peu profonde seulement dans le quart opposé) | Sol | aucune |
| 92 | `eau_coin_bd` | Eau peu profonde : coin bas-droite d'une étendue rectangulaire (eau peu profonde seulement dans le quart opposé) | Sol | aucune |
| 96 | `eau_profonde` | Eau profonde, case entière (infranchissable) | Murs | pleine |
| 97 | `eau_profonde_bord_haut` | Eau profonde : bord haut (eau peu profonde au-dessus) | Murs | partielle : 0,16 32×16 |
| 98 | `eau_profonde_bord_bas` | Eau profonde : bord bas (eau peu profonde en dessous) | Murs | partielle : 0,0 32×16 |
| 99 | `eau_profonde_bord_gauche` | Eau profonde : bord gauche (eau peu profonde à gauche) | Murs | partielle : 16,0 16×32 |
| 100 | `eau_profonde_bord_droite` | Eau profonde : bord droite (eau peu profonde à droite) | Murs | partielle : 0,0 16×32 |
| 101 | `eau_profonde_creux_hg` | Eau profonde : coin rentrant, eau peu profonde seulement en haut-gauche | Murs | partielle : 0,16 32×16 ; 16,0 16×16 |
| 102 | `eau_profonde_creux_hd` | Eau profonde : coin rentrant, eau peu profonde seulement en haut-droite | Murs | partielle : 0,16 32×16 ; 0,0 16×16 |
| 103 | `eau_profonde_creux_bg` | Eau profonde : coin rentrant, eau peu profonde seulement en bas-gauche | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 104 | `eau_profonde_creux_bd` | Eau profonde : coin rentrant, eau peu profonde seulement en bas-droite | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 105 | `eau_profonde_coin_hg` | Eau profonde : coin haut-gauche d'une étendue rectangulaire (eau profonde seulement dans le quart opposé) | Murs | partielle : 16,16 16×16 |
| 106 | `eau_profonde_coin_hd` | Eau profonde : coin haut-droite d'une étendue rectangulaire (eau profonde seulement dans le quart opposé) | Murs | partielle : 0,16 16×16 |
| 107 | `eau_profonde_coin_bg` | Eau profonde : coin bas-gauche d'une étendue rectangulaire (eau profonde seulement dans le quart opposé) | Murs | partielle : 16,0 16×16 |
| 108 | `eau_profonde_coin_bd` | Eau profonde : coin bas-droite d'une étendue rectangulaire (eau profonde seulement dans le quart opposé) | Murs | partielle : 0,0 16×16 |
| 93, 94, 95, 109, 110, 111 | — | réserve (vide) | — | — |

## 7. Décor

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 112 | `colonne_haut` | Haut de colonne (chapiteau), case au-dessus de colonne_base | Dessus | aucune |
| 113 | `colonne_base` | Base de colonne (fût et socle) | Murs | pleine |
| 114 | `vase` | Vase de terre cuite (décor, ne se casse pas : un vase cassable serait un objet) | Murs | pleine |
| 115 | `cerf_haut` | Statue de cerf : bois et tête, case au-dessus de cerf_base | Dessus | aucune |
| 116 | `cerf_base` | Statue de cerf : corps sur son socle | Murs | pleine |
| 117 | `mousse_a` | Mousse au sol | Decor | aucune |
| 118 | `mousse_b` | Mousse au sol, variante | Decor | aucune |
| 119 | `feuilles_a` | Feuilles tombées | Decor | aucune |
| 120 | `feuilles_b` | Feuilles mortes, variante | Decor | aucune |
| 121–127 | — | réserve (vide) | — | — |

## Terrains Tiled (autotiling)

Cinq terrains « par coins » (*corner set*) sont définis dans le `.tsx`. Dans Tiled : panneau **Terrains**, choisir le terrain puis peindre avec le pinceau de terrain (T).

| Terrain | Couleurs | Calque | Tuiles |
| --- | --- | --- | --- |
| `Murs` | `mur` (le reste = vide) | Murs | 16–30 |
| `Trous` | `sol`, `trou` | Sol | 0–2 (sol), 58–66 |
| `Trous de passage` | `sol`, `passage` | Sol | 0–2 (sol), 31–39 |
| `Eau` | `sol`, `eau` | Sol | 0–2 (sol), 80–92 |
| `Eau profonde` | `eau`, `profonde` | Murs | 80 (eau), 96–108 |

- **Murs** : une seule couleur, `mur`. Le sol n'en fait pas partie (il est peint sur le calque Sol), pour que le pinceau ne pose jamais de dalle sur le calque Murs. Pour une salle de 20×11 entourée d'un mur d'une tuile, peindre `mur` sur tous les coins du pourtour : on obtient exactement l'anneau mur_haut / mur_bas / mur_gauche / mur_droite + les 4 coins intérieurs. Un seul coin peint au milieu de la salle donne un bloc de 2×2 tuiles (les 4 coins extérieurs). Les tuiles de mur sont entières : toute la case bloque.
- **Trous** : comme les murs, toutes les tuiles du terrain sont entièrement « trou » (on tombe partout dedans). Seules les formes rectangulaires sont prévues (pas de coin rentrant) ; les coins rentrants pourront être ajoutés dans la réserve 67–71 si besoin.
- **Trous de passage** : tuiles 31 à 39, même logique que les trous mortels (rectangles seulement), mais décoratives : anneau de racines brunes, fond vert-bleu lumineux avec un petit sol de dalles très bas, étincelles. Elles sont à peindre sur le calque Sol, sans collision, avec l'objet `Chute` par-dessus ; `HoleRules` ne les reconnaît pas (seules les tuiles 58 à 66 tuent). Pour un trou 2×2 : coin_hg, coin_hd sur la ligne du haut, coin_bg, coin_bd sur celle du bas (ou le pinceau du terrain `Trous de passage`).
- **Eau / Eau profonde** : le bord passe au **milieu** de la tuile (chaque quart de 16×16 est soit de l'eau, soit l'autre terrain). L'eau peu profonde est sur le calque Sol, sans collision. L'eau profonde est posée sur le calque **Murs** (par-dessus l'eau peu profonde) car elle bloque : sa collision couvre exactement ses quarts d'eau profonde. Il manque volontairement les deux tuiles en diagonale (deux quarts opposés) : éviter de les demander au pinceau.
- Les dalles fissurées (3, 4) et la terre (5) ne sont pas dans les terrains : à poser à la main.

## Comment assembler

- **Porte** : remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` dans la **même case** du calque Dessus, puis l'objet `Porte` (calque Objets) par-dessus. La porte elle-même (battant, grille, serrure) est un sprite à part dans `art/puzzles/`.
- **Colonne** et **statue de cerf** : 2 cases l'une au-dessus de l'autre. `*_base` sur Murs (collision pleine), `*_haut` juste au-dessus sur Dessus (Brann passe derrière).
- **Escaliers** : simple tuile de sol ; le changement de carte se fait avec un objet `Sortie` posé dessus.
- **Trou** : la tuile ne fait rien toute seule (pas de collision). La chute est à gérer côté jeu (voir « Besoins » ci-dessous).
- Hors tileset (objets de gameplay, sprites séparés dans `art/puzzles/`) : coffres, blocs poussables, interrupteurs, torches, portes, statue du corbeau.

## Besoins et propositions

- **Détection des trous** (développeur) : proposer une convention, par exemple une propriété de tuile `trou` (bool) dans le `.tsx`, lue en jeu via les custom data du TileSet importé, ou un objet `Trou` dans le calque Objets. Rien n'est encore défini dans `CLAUDE.md`, donc rien n'est mis dans le `.tsx`.
- **Palette** : le dessin final ajoute quelques nuances (reflets et ombres de dalle et de mur, bleus clairs de l'eau, voir « Palette utilisée ») ; à reporter dans `art/palette.png` quand la palette du jeu sera figée.
- **Murs** : `mur_plein` (28) n'a pas de bord clair ; à utiliser à l'intérieur d'un mur épais, pas au contact du sol (utiliser les tuiles de bord via le terrain `Murs`).

## Palette utilisée

| Rôle | Couleurs |
| --- | --- |
| Contour | `#1b1420`, `#241a22` |
| Dalles | `#9a948c`, `#5c5650`, `#d8d4cc` |
| Terre, racines | `#8a5a34`, `#5e3a22`, `#b06e40`, `#7a4628`, `#4a2a1c` |
| Murs | `#382e42` (dessus), `#4e4058` (rebord), `#7a6a88` (face avant), `#b8a8c0` (arête claire) |
| Eau | `#3c5a8a` (peu profonde), `#263a5e` (profonde), `#b8a8c0` (écume) |
| Ronces | `#241a22`, `#3a1a4a`, `#6a2a7a` |
| Mousse, feuilles | `#5a8a3c`, `#6a9a48`, `#3a5a2c`, `#c8a050`, `#f08a28` |
| Vase | `#b06e40`, `#8a5a34`, `#d6c49c` |
| Trou de passage | `#c8fff0`, `#7fe8d0`, `#3fc0a8`, `#2a9a9c`, `#1d7488`, `#14566a`, `#58cdb4`, `#2a8a96` |
| Nuances ajoutées (dessin final) | dalles `#aaa49a`, `#847e76` ; murs `#44384e`, `#2e2638`, `#8a7a98`, `#645672` ; eau `#7a9ac0`, `#b8d0e8`, `#324d7a`, `#1e2e4e` ; vase `#c98250` |
