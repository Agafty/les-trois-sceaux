# Plan du tileset `foret` — forêt (overworld nord-ouest et abords du Temple des Racines)

> Fichier généré par `tools/sprites/foret.py` : modifier le script, pas ce fichier.

- Image : `art/tilesets/foret.png`, 256×768 px, 8 colonnes × 24 lignes de tuiles 32×32, sans marge ni espacement (192 cases). Tileset Tiled : `maps/tilesets/foret.tsx` (collisions et terrains définis).
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro : le dessin remplace le plan au même emplacement. Lignes 17 à 24 (ids 136 à 191) : réserve vide, pour les ajouts. La planche `art/tilesets/foret_numeros.png` montre le numéro de chaque tuile.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche).
- Calques : `Sol` = herbe, chemin, eau ; `Decor` = petits décors sans collision ; `Murs` = tout ce qui bloque ; `Dessus` = cimes des gros arbres (passent devant Brann).

## 1. Herbe

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `herbe_a` | Herbe de base | Sol | aucune |
| 1 | `herbe_b` | Herbe avec touffes | Sol | aucune |
| 2 | `herbe_c` | Herbe avec trèfles | Sol | aucune |
| 3 | `herbe_d` | Herbe avec petits cailloux | Sol | aucune |
| 4 | `herbe_fleurs_blanches` | Herbe parsemée de fleurs blanches | Sol | aucune |
| 5 | `herbe_fleurs_jaunes` | Herbe parsemée de fleurs jaunes | Sol | aucune |
| 6 | `herbe_fleurs_rouges` | Herbe parsemée de fleurs rouges | Sol | aucune |
| 7 | `herbe_sombre` | Herbe sombre de sous-bois (près des grands arbres et du temple) | Sol | aucune |

## 2. Chemin de terre

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 8 | `herbe_chemin` | Herbe (même dessin que herbe_a, sert de base au terrain Chemin) | Sol | aucune |
| 9 | `chemin_0001` | Chemin : coin bas-droite seulement (terre dans ce coin) | Sol | aucune |
| 10 | `chemin_0010` | Chemin : coin bas-gauche seulement (terre dans ce coin) | Sol | aucune |
| 11 | `chemin_0011` | Chemin : terre en bas (bord bas) | Sol | aucune |
| 12 | `chemin_0100` | Chemin : coin haut-droite seulement (terre dans ce coin) | Sol | aucune |
| 13 | `chemin_0101` | Chemin : terre à droite (bord droit) | Sol | aucune |
| 14 | `chemin_0110` | Chemin : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 15 | `chemin_0111` | Chemin : terre partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 16 | `chemin_1000` | Chemin : coin haut-gauche seulement (terre dans ce coin) | Sol | aucune |
| 17 | `chemin_1001` | Chemin : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 18 | `chemin_1010` | Chemin : terre à gauche (bord gauche) | Sol | aucune |
| 19 | `chemin_1011` | Chemin : terre partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 20 | `chemin_1100` | Chemin : terre en haut (bord haut) | Sol | aucune |
| 21 | `chemin_1101` | Chemin : terre partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 22 | `chemin_1110` | Chemin : terre partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 23 | `chemin_plein` | Terre battue, case entière | Sol | aucune |

## 3. Eau peu profonde (rivière, mare)

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 24 | `herbe_rive` | Herbe (base du terrain Eau) | Sol | aucune |
| 25 | `eau_0001` | Rive : coin bas-droite seulement (eau dans ce coin) | Sol | aucune |
| 26 | `eau_0010` | Rive : coin bas-gauche seulement (eau dans ce coin) | Sol | aucune |
| 27 | `eau_0011` | Rive : eau en bas (bord bas) | Sol | aucune |
| 28 | `eau_0100` | Rive : coin haut-droite seulement (eau dans ce coin) | Sol | aucune |
| 29 | `eau_0101` | Rive : eau à droite (bord droit) | Sol | aucune |
| 30 | `eau_0110` | Rive : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 31 | `eau_0111` | Rive : eau partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 32 | `eau_1000` | Rive : coin haut-gauche seulement (eau dans ce coin) | Sol | aucune |
| 33 | `eau_1001` | Rive : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 34 | `eau_1010` | Rive : eau à gauche (bord gauche) | Sol | aucune |
| 35 | `eau_1011` | Rive : eau partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 36 | `eau_1100` | Rive : eau en haut (bord haut) | Sol | aucune |
| 37 | `eau_1101` | Rive : eau partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 38 | `eau_1110` | Rive : eau partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 39 | `eau` | Eau peu profonde, case entière (Brann la traverse) | Sol | aucune |

## 4. Eau profonde (infranchissable)

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 40 | `eau_pour_profonde` | Eau peu profonde (base du terrain Eau profonde) | Sol | aucune |
| 41 | `eau_profonde_0001` | Eau profonde : coin bas-droite seulement (eau profonde dans ce coin) | Murs | partielle : 16,16 16×16 |
| 42 | `eau_profonde_0010` | Eau profonde : coin bas-gauche seulement (eau profonde dans ce coin) | Murs | partielle : 0,16 16×16 |
| 43 | `eau_profonde_0011` | Eau profonde : eau profonde en bas (bord bas) | Murs | partielle : 0,16 32×16 |
| 44 | `eau_profonde_0100` | Eau profonde : coin haut-droite seulement (eau profonde dans ce coin) | Murs | partielle : 16,0 16×16 |
| 45 | `eau_profonde_0101` | Eau profonde : eau profonde à droite (bord droit) | Murs | partielle : 16,0 16×32 |
| 46 | `eau_profonde_0110` | Eau profonde : deux coins opposés (haut-droite et bas-gauche) | Murs | partielle : 16,0 16×16 ; 0,16 16×16 |
| 47 | `eau_profonde_0111` | Eau profonde : eau profonde partout sauf le coin haut-gauche (coin rentrant) | Murs | partielle : 16,0 16×16 ; 0,16 32×16 |
| 48 | `eau_profonde_1000` | Eau profonde : coin haut-gauche seulement (eau profonde dans ce coin) | Murs | partielle : 0,0 16×16 |
| 49 | `eau_profonde_1001` | Eau profonde : deux coins opposés (haut-gauche et bas-droite) | Murs | partielle : 0,0 16×16 ; 16,16 16×16 |
| 50 | `eau_profonde_1010` | Eau profonde : eau profonde à gauche (bord gauche) | Murs | partielle : 0,0 16×32 |
| 51 | `eau_profonde_1011` | Eau profonde : eau profonde partout sauf le coin haut-droite (coin rentrant) | Murs | partielle : 0,0 16×16 ; 0,16 32×16 |
| 52 | `eau_profonde_1100` | Eau profonde : eau profonde en haut (bord haut) | Murs | partielle : 0,0 32×16 |
| 53 | `eau_profonde_1101` | Eau profonde : eau profonde partout sauf le coin bas-gauche (coin rentrant) | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 54 | `eau_profonde_1110` | Eau profonde : eau profonde partout sauf le coin bas-droite (coin rentrant) | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 55 | `eau_profonde` | Eau profonde, case entière (infranchissable) | Murs | pleine |

## 5. Falaise, talus, pont

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 56 | `falaise_crete` | Haut de falaise : herbe du plateau + arête (la moitié basse est solide) | Murs | partielle : 0,16 32×16 |
| 57 | `falaise_crete_g` | Haut de falaise, extrémité gauche | Murs | partielle : 3,16 29×16 |
| 58 | `falaise_crete_d` | Haut de falaise, extrémité droite | Murs | partielle : 0,16 29×16 |
| 59 | `falaise_face` | Face de falaise (roche verticale) | Murs | pleine |
| 60 | `falaise_face_g` | Face de falaise, extrémité gauche | Murs | partielle : 3,0 29×32 |
| 61 | `falaise_face_d` | Face de falaise, extrémité droite | Murs | partielle : 0,0 29×32 |
| 62 | `falaise_pied` | Pied de falaise (ombre + herbe en bas) | Murs | partielle : 0,0 32×24 |
| 63 | `falaise_pied_g` | Pied de falaise, extrémité gauche | Murs | partielle : 3,0 29×24 |
| 64 | `falaise_pied_d` | Pied de falaise, extrémité droite | Murs | partielle : 0,0 29×24 |
| 65 | `falaise_cote_g` | Falaise verticale vue de côté : roche à gauche, plateau/herbe à droite | Murs | partielle : 0,0 12×32 |
| 66 | `falaise_cote_d` | Falaise verticale vue de côté : roche à droite, herbe à gauche | Murs | partielle : 20,0 12×32 |
| 67 | `falaise_escalier` | Escalier taillé dans la falaise (à poser à la place de falaise_face ; passage libre) | Sol | aucune |
| 68 | `pont_h` | Pont de planches horizontal (au-dessus de l'eau profonde : poser sur Decor et effacer la tuile solide du calque Murs dessous) | Decor | aucune |
| 69 | `pont_v` | Pont de planches vertical (même remarque) | Decor | aucune |

## 6. Arbres, souches

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 72 | `arbre_petit_a` | Arbre 1×1 (tronc + cime ronde), solide | Murs | partielle : 5,8 22×22 |
| 73 | `arbre_petit_b` | Arbre 1×1, variante (cime plus large) | Murs | partielle : 5,8 22×22 |
| 74 | `arbre_dense_a` | Feuillage dense case pleine (bordure de forêt infranchissable, se pose côte à côte) | Murs | pleine |
| 75 | `arbre_dense_b` | Feuillage dense case pleine, variante | Murs | pleine |
| 76 | `arbre_noirci` | Arbre 1×1 corrompu par les ronces noires de Morvath (abords du temple), solide | Murs | partielle : 5,8 22×22 |
| 77 | `souche` | Souche d'arbre, solide | Murs | partielle : 6,12 20×16 |
| 78 | `souche_creuse` | Souche creuse (cachette : à cacher derrière des buissons ; l'objet est un Ramassable posé dessus) | Murs | partielle : 6,12 20×16 |
| 79 | `tronc_couche` | Tronc couché horizontal, solide | Murs | partielle : 2,10 28×16 |

## 7. Gros arbres 2×2

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 80 | `gros_arbre_a_cime_hg` | Gros arbre vert, cime gauche (Dessus) | Dessus | aucune |
| 81 | `gros_arbre_a_cime_hd` | Gros arbre vert, cime droite (Dessus) | Dessus | aucune |
| 82 | `gros_arbre_b_cime_hg` | Gros arbre vert (variante), cime gauche (Dessus) | Dessus | aucune |
| 83 | `gros_arbre_b_cime_hd` | Gros arbre vert (variante), cime droite (Dessus) | Dessus | aucune |
| 84 | `gros_arbre_noirci_cime_hg` | Gros arbre corrompu (ronces noires), cime gauche (Dessus) | Dessus | aucune |
| 85 | `gros_arbre_noirci_cime_hd` | Gros arbre corrompu (ronces noires), cime droite (Dessus) | Dessus | aucune |
| 86 | `gros_arbre_mort_cime_hg` | Gros arbre mort, sans feuilles, cime gauche (Dessus) | Dessus | aucune |
| 87 | `gros_arbre_mort_cime_hd` | Gros arbre mort, sans feuilles, cime droite (Dessus) | Dessus | aucune |
| 88 | `gros_arbre_a_tronc_g` | Gros arbre vert, tronc gauche (Murs, solide) | Murs | partielle : 14,4 18×28 |
| 89 | `gros_arbre_a_tronc_d` | Gros arbre vert, tronc droit (Murs, solide) | Murs | partielle : 0,4 18×28 |
| 90 | `gros_arbre_b_tronc_g` | Gros arbre vert (variante), tronc gauche (Murs, solide) | Murs | partielle : 14,4 18×28 |
| 91 | `gros_arbre_b_tronc_d` | Gros arbre vert (variante), tronc droit (Murs, solide) | Murs | partielle : 0,4 18×28 |
| 92 | `gros_arbre_noirci_tronc_g` | Gros arbre corrompu (ronces noires), tronc gauche (Murs, solide) | Murs | partielle : 14,4 18×28 |
| 93 | `gros_arbre_noirci_tronc_d` | Gros arbre corrompu (ronces noires), tronc droit (Murs, solide) | Murs | partielle : 0,4 18×28 |
| 94 | `gros_arbre_mort_tronc_g` | Gros arbre mort, sans feuilles, tronc gauche (Murs, solide) | Murs | partielle : 14,4 18×28 |
| 95 | `gros_arbre_mort_tronc_d` | Gros arbre mort, sans feuilles, tronc droit (Murs, solide) | Murs | partielle : 0,4 18×28 |

## 8. Buissons, rochers

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `buisson_a` | Buisson, solide (coupable plus tard) | Murs | partielle : 2,6 28×24 |
| 97 | `buisson_b` | Buisson, variante | Murs | partielle : 2,6 28×24 |
| 98 | `buisson_fleuri` | Buisson à fleurs blanches et violettes | Murs | partielle : 2,6 28×24 |
| 99 | `buisson_baies` | Buisson sombre à baies rouges | Murs | partielle : 2,6 28×24 |
| 100 | `rocher_a` | Rocher gris, solide | Murs | partielle : 2,6 28×24 |
| 101 | `rocher_b` | Gros rocher en deux blocs, solide | Murs | partielle : 2,6 28×24 |
| 102 | `rocher_mousse` | Rocher couvert de mousse, solide | Murs | partielle : 2,6 28×24 |

## 9. Entrée du Temple des Racines (5×3), ronces, racines

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 104 | `entree_toit_g` | Toit de la façade, extrémité gauche | Murs | pleine |
| 105 | `entree_toit` | Toit de la façade (pierre sombre en écailles, corniche) | Murs | pleine |
| 106 | `entree_toit_centre` | Toit, centre : médaillon à bois de cerf | Murs | pleine |
| 107 | `entree_toit` | Toit de la façade | Murs | pleine |
| 108 | `entree_toit_d` | Toit de la façade, extrémité droite | Murs | pleine |
| 109 | `ronces_a` | Bloc de ronces noires (infranchissable), comme dans le temple | Murs | pleine |
| 110 | `ronces_b` | Bloc de ronces noires, variante | Murs | pleine |
| 111 | `ronces_epaisses` | Ronces noires épaisses, case pleine | Murs | pleine |
| 112 | `entree_mur_haut_g` | Façade haute, extrémité gauche (racines) | Murs | pleine |
| 113 | `entree_mur_haut` | Façade haute en pierre taillée | Murs | pleine |
| 114 | `entree_linteau` | Linteau : arche au-dessus de la porte (solide ; Brann n'y entre pas) | Murs | pleine |
| 115 | `entree_mur_haut` | Façade haute en pierre taillée | Murs | pleine |
| 116 | `entree_mur_haut_d` | Façade haute, extrémité droite | Murs | pleine |
| 117 | `ronces_sol` | Ronces rampantes au sol (décor, sans collision) | Decor | aucune |
| 118 | `racine_h` | Racine horizontale sur l'herbe (se raccorde à gauche et à droite) | Decor | aucune |
| 119 | `racine_v` | Racine verticale sur l'herbe | Decor | aucune |
| 120 | `entree_mur_bas_g` | Façade basse + socle, extrémité gauche | Murs | pleine |
| 121 | `entree_mur_bas` | Façade basse + socle | Murs | pleine |
| 122 | `entree_porte` | PORTE d'ENTRÉE (1 case) : ouverture de 20 px, marches ; l'objet Sortie se pose dessus | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 123 | `entree_mur_bas` | Façade basse + socle | Murs | pleine |
| 124 | `entree_mur_bas_d` | Façade basse + socle, extrémité droite | Murs | pleine |
| 125 | `racine_noeud` | Nœud de racines (départ ou fin d'une racine) | Decor | aucune |
| 126 | `perron` | Dalles de pierre devant la porte du temple (sol) | Sol | aucune |
| 127 | `dalle_chemin` | Dalle de pierre isolée sur l'herbe (sentier vers le temple) | Sol | aucune |

## 10. Petits décors (calque Decor, sans collision)

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 128 | `fleurs_blanches` | Fleurs blanches (posées sur l'herbe) | Decor | aucune |
| 129 | `fleurs_jaunes` | Fleurs jaunes | Decor | aucune |
| 130 | `fleurs_rouges` | Fleurs rouges | Decor | aucune |
| 131 | `fleurs_violettes` | Fleurs violettes | Decor | aucune |
| 132 | `herbes_hautes` | Touffes d'herbe haute | Decor | aucune |
| 133 | `champignons` | Champignons rouges | Decor | aucune |
| 134 | `cailloux` | Petits cailloux | Decor | aucune |
| 135 | `feuilles_mortes` | Feuilles mortes | Decor | aucune |

## Assemblages à connaître (à poser avec le pinceau « tampon »)

| Assemblage | Tuiles (ligne par ligne) | Calques |
| --- | --- | --- |
| **Entrée du Temple des Racines**, 5×3 cases | `104 105 106 107 108` / `112 113 114 115 116` / `120 121 122 123 124` | Murs (tout) ; l'objet `Sortie` sur la case 122 (porte), le Spawn d'arrivée juste en dessous sur `126` (perron) |
| Gros arbre vert 2×2 | `80 81` / `88 89` | cime (80, 81) sur `Dessus`, tronc (88, 89) sur `Murs` |
| Gros arbre vert, variante | `82 83` / `90 91` | idem |
| Gros arbre corrompu | `84 85` / `92 93` | idem |
| Gros arbre mort | `86 87` / `94 95` | idem |
| Falaise de 3 cases de haut | `56` / `59` / `62` (+ `57 60 63` extrémité gauche, `58 61 64` extrémité droite) | Murs |
| Rivière traversable en pont | eau profonde (terrain) puis `68` ou `69` sur `Decor` | pont sur Decor ; retirer la tuile de Murs sous le pont |

## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain est un bloc de 16 tuiles : id = base + (HG×8 + HD×4 + BG×2 + BD) avec 1 = terrain secondaire dans ce coin.

| Terrain | Couleurs (1 / 2) | Calque | Tuiles |
| --- | --- | --- | --- |
| `Chemin` | herbe / terre | Sol | 0–6 (herbe), 8–23 |
| `Eau` | herbe / eau peu profonde | Sol | 0–6 (herbe), 24–39 |
| `Eau profonde` | eau peu profonde / eau profonde | Murs (sauf la tuile 40) | 39 ou 40 (eau), 41–55 |

Astuce : peindre d'abord l'herbe (tuiles 0 à 7 au hasard), puis le terrain Chemin ou Eau dessus, puis Eau profonde au milieu de l'eau.
