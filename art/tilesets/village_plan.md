# Plan du tileset `village` — Brumeval, le village (overworld : place, maisons, lac, ravin, falaise)

> Fichier généré par `tools/sprites/village.py` : modifier le script, pas ce fichier. **État : PLAN** (aplats de couleur par famille, le dessin final remplacera chaque tuile au même numéro).

- Image : `art/tilesets/village.png`, 256×1600 px, 8 colonnes × 50 lignes de tuiles 32×32, sans marge ni espacement (400 cases). Tileset Tiled : `maps/tilesets/village.tsx` (collisions et terrains définis). `art/tilesets/village_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 47 à 50 (ids 368 à 399) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px (dessin final). Le plan est en aplats : **la couleur indique la famille** (vert herbe, gris-bleu pavés, brun terre, bleu eau, rouge/gris/jaune toits, orange portes et blocages…) ; une zone plus sombre dans une tuile = zone solide.
- **Arbres, buissons, rochers, falaises de forêt, fleurs et chemin de forêt** : on réutilise le tileset `foret` dans la même carte (Tiled accepte plusieurs tilesets par carte).
- **Variantes jour / brume** : un seul jeu de numéros. Le dessin final fournira `village.png` (jour) et une copie recolorée par teinte `village_brume.png` ; le jeu choisit la texture selon l'avancement. Le calque `Dessus` contient en plus des tuiles **semi-transparentes** de brume (groupe « Brume ») qu'on peut masquer à mesure que la brume se lève.

## Calques

- `Sol` : herbe, pavés, terre, rive, eau, ravin (le fond), sols de décor
- `Decor` : petits décors sans collision (fleurs, seau, ponton, nénuphars, tablier du pont-levis abaissé…)
- `Murs` : tout ce qui bloque (façades, toits, falaise, ravin, éboulis, objets). Les collisions sont dans le tileset
- `Objets` : Sortie, Spawn, PNJ, Coffre, MurFissure, Ramassable… (objets Tiled, pas des tuiles)
- `Dessus` : passe devant Brann (auvents, cime des lampadaires, enseignes, brume)

## 1. Herbe

Même famille que `foret` (vert 5a8a3c). Les tuiles 0 à 6 servent aussi de base aux terrains Pavés, Terre et Rive.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `herbe_a` | Herbe de base | Sol | aucune |
| 1 | `herbe_b` | Herbe avec touffes | Sol | aucune |
| 2 | `herbe_c` | Herbe avec trèfles | Sol | aucune |
| 3 | `herbe_d` | Herbe avec petits cailloux | Sol | aucune |
| 4 | `herbe_fleurs_blanches` | Herbe parsemée de fleurs blanches | Sol | aucune |
| 5 | `herbe_fleurs_jaunes` | Herbe parsemée de fleurs jaunes | Sol | aucune |
| 6 | `herbe_fleurs_rouges` | Herbe parsemée de fleurs rouges | Sol | aucune |
| 7 | `herbe_sombre` | Herbe sombre (au pied de la falaise et des murs) | Sol | aucune |

## 2. Variantes de pavés (hors terrain)

À semer au hasard sur les cases pleines pour casser la répétition.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 8 | `paves_b` | Pavés, variante B | Sol | aucune |
| 9 | `paves_c` | Pavés, variante C | Sol | aucune |
| 10 | `paves_usees` | Pavés usés et fendus | Sol | aucune |
| 11 | `paves_mousse` | Pavés moussus | Sol | aucune |
| 12 | `paves_rond` | Dalle ronde claire (cercle autour du puits ; poser en 3×3 avec les pavés) | Sol | aucune |
| 13 | `paves_blason` | Dalle gravée du blason de Brumeval (centre de la place) | Sol | aucune |
| 14 | `paves_seuil` | Seuil de pierre devant une porte | Sol | aucune |
| 15 | `paves_escalier_h` | Marches de pierre (passables) pour monter d'une terrasse | Sol | aucune |

## 3. Pavés de la place (terrain `Paves`)

Pavés sur herbe : peindre l'herbe, puis le terrain Paves.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 16 | `paves_base` | Herbe (base du terrain Paves) | Sol | aucune |
| 17 | `paves_0001` | Sol : coin bas-droite seulement (paves dans ce coin) | Sol | aucune |
| 18 | `paves_0010` | Sol : coin bas-gauche seulement (paves dans ce coin) | Sol | aucune |
| 19 | `paves_0011` | Sol : paves en bas (bord bas) | Sol | aucune |
| 20 | `paves_0100` | Sol : coin haut-droite seulement (paves dans ce coin) | Sol | aucune |
| 21 | `paves_0101` | Sol : paves à droite (bord droit) | Sol | aucune |
| 22 | `paves_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 23 | `paves_0111` | Sol : paves partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 24 | `paves_1000` | Sol : coin haut-gauche seulement (paves dans ce coin) | Sol | aucune |
| 25 | `paves_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 26 | `paves_1010` | Sol : paves à gauche (bord gauche) | Sol | aucune |
| 27 | `paves_1011` | Sol : paves partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 28 | `paves_1100` | Sol : paves en haut (bord haut) | Sol | aucune |
| 29 | `paves_1101` | Sol : paves partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 30 | `paves_1110` | Sol : paves partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 31 | `paves_plein` | Pavés, case entière | Sol | aucune |

## 4. Terre battue (terrain `Terre`)

Chemins de village. Terre sur herbe.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 32 | `terre_base` | Herbe (base du terrain Terre) | Sol | aucune |
| 33 | `terre_0001` | Sol : coin bas-droite seulement (terre dans ce coin) | Sol | aucune |
| 34 | `terre_0010` | Sol : coin bas-gauche seulement (terre dans ce coin) | Sol | aucune |
| 35 | `terre_0011` | Sol : terre en bas (bord bas) | Sol | aucune |
| 36 | `terre_0100` | Sol : coin haut-droite seulement (terre dans ce coin) | Sol | aucune |
| 37 | `terre_0101` | Sol : terre à droite (bord droit) | Sol | aucune |
| 38 | `terre_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 39 | `terre_0111` | Sol : terre partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 40 | `terre_1000` | Sol : coin haut-gauche seulement (terre dans ce coin) | Sol | aucune |
| 41 | `terre_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 42 | `terre_1010` | Sol : terre à gauche (bord gauche) | Sol | aucune |
| 43 | `terre_1011` | Sol : terre partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 44 | `terre_1100` | Sol : terre en haut (bord haut) | Sol | aucune |
| 45 | `terre_1101` | Sol : terre partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 46 | `terre_1110` | Sol : terre partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 47 | `terre_plein` | Terre battue, case entière | Sol | aucune |

## 5. Rive du lac (terrain `Rive`, eau peu profonde)

Herbe / eau peu profonde : Brann la traverse (ralentissement possible plus tard).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `rive_base` | Herbe (base du terrain Rive) | Sol | aucune |
| 49 | `rive_0001` | Sol : coin bas-droite seulement (eau dans ce coin) | Sol | aucune |
| 50 | `rive_0010` | Sol : coin bas-gauche seulement (eau dans ce coin) | Sol | aucune |
| 51 | `rive_0011` | Sol : eau en bas (bord bas) | Sol | aucune |
| 52 | `rive_0100` | Sol : coin haut-droite seulement (eau dans ce coin) | Sol | aucune |
| 53 | `rive_0101` | Sol : eau à droite (bord droit) | Sol | aucune |
| 54 | `rive_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 55 | `rive_0111` | Sol : eau partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 56 | `rive_1000` | Sol : coin haut-gauche seulement (eau dans ce coin) | Sol | aucune |
| 57 | `rive_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 58 | `rive_1010` | Sol : eau à gauche (bord gauche) | Sol | aucune |
| 59 | `rive_1011` | Sol : eau partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 60 | `rive_1100` | Sol : eau en haut (bord haut) | Sol | aucune |
| 61 | `rive_1101` | Sol : eau partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 62 | `rive_1110` | Sol : eau partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 63 | `rive_plein` | Eau peu profonde, case entière (traversable) | Sol | aucune |

## 6. Eau profonde du lac (terrain `Lac profond`, infranchissable)

Eau peu profonde / eau profonde. La case pleine et les bords sont sur `Murs` (solides).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 64 | `lac_base` | Eau peu profonde (base du terrain Lac profond) | Sol | aucune |
| 65 | `lac_0001` | Sol : coin bas-droite seulement (profonde dans ce coin) | Murs | partielle : 16,16 16×16 |
| 66 | `lac_0010` | Sol : coin bas-gauche seulement (profonde dans ce coin) | Murs | partielle : 0,16 16×16 |
| 67 | `lac_0011` | Sol : profonde en bas (bord bas) | Murs | partielle : 0,16 32×16 |
| 68 | `lac_0100` | Sol : coin haut-droite seulement (profonde dans ce coin) | Murs | partielle : 16,0 16×16 |
| 69 | `lac_0101` | Sol : profonde à droite (bord droit) | Murs | partielle : 16,0 16×32 |
| 70 | `lac_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Murs | partielle : 16,0 16×16 ; 0,16 16×16 |
| 71 | `lac_0111` | Sol : profonde partout sauf le coin haut-gauche (coin rentrant) | Murs | partielle : 16,0 16×16 ; 0,16 32×16 |
| 72 | `lac_1000` | Sol : coin haut-gauche seulement (profonde dans ce coin) | Murs | partielle : 0,0 16×16 |
| 73 | `lac_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Murs | partielle : 0,0 16×16 ; 16,16 16×16 |
| 74 | `lac_1010` | Sol : profonde à gauche (bord gauche) | Murs | partielle : 0,0 16×32 |
| 75 | `lac_1011` | Sol : profonde partout sauf le coin haut-droite (coin rentrant) | Murs | partielle : 0,0 16×16 ; 0,16 32×16 |
| 76 | `lac_1100` | Sol : profonde en haut (bord haut) | Murs | partielle : 0,0 32×16 |
| 77 | `lac_1101` | Sol : profonde partout sauf le coin bas-gauche (coin rentrant) | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 78 | `lac_1110` | Sol : profonde partout sauf le coin bas-droite (coin rentrant) | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 79 | `lac_plein` | Eau profonde, case entière (infranchissable) | Murs | pleine |

## 7. Ravin au nord du village (terrain `Ravin`)

Herbe / vide du ravin. Les cases de ravin sont solides (`Murs`) ; le pont-levis s'y pose (groupe « Pont-levis »).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 80 | `ravin_base` | Herbe (base du terrain Ravin) | Sol | aucune |
| 81 | `ravin_0001` | Sol : coin bas-droite seulement (ravin dans ce coin) | Murs | partielle : 16,16 16×16 |
| 82 | `ravin_0010` | Sol : coin bas-gauche seulement (ravin dans ce coin) | Murs | partielle : 0,16 16×16 |
| 83 | `ravin_0011` | Sol : ravin en bas (bord bas) | Murs | partielle : 0,16 32×16 |
| 84 | `ravin_0100` | Sol : coin haut-droite seulement (ravin dans ce coin) | Murs | partielle : 16,0 16×16 |
| 85 | `ravin_0101` | Sol : ravin à droite (bord droit) | Murs | partielle : 16,0 16×32 |
| 86 | `ravin_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Murs | partielle : 16,0 16×16 ; 0,16 16×16 |
| 87 | `ravin_0111` | Sol : ravin partout sauf le coin haut-gauche (coin rentrant) | Murs | partielle : 16,0 16×16 ; 0,16 32×16 |
| 88 | `ravin_1000` | Sol : coin haut-gauche seulement (ravin dans ce coin) | Murs | partielle : 0,0 16×16 |
| 89 | `ravin_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Murs | partielle : 0,0 16×16 ; 16,16 16×16 |
| 90 | `ravin_1010` | Sol : ravin à gauche (bord gauche) | Murs | partielle : 0,0 16×32 |
| 91 | `ravin_1011` | Sol : ravin partout sauf le coin haut-droite (coin rentrant) | Murs | partielle : 0,0 16×16 ; 0,16 32×16 |
| 92 | `ravin_1100` | Sol : ravin en haut (bord haut) | Murs | partielle : 0,0 32×16 |
| 93 | `ravin_1101` | Sol : ravin partout sauf le coin bas-gauche (coin rentrant) | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 94 | `ravin_1110` | Sol : ravin partout sauf le coin bas-droite (coin rentrant) | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 95 | `ravin_plein` | Ravin, case entière (vide, infranchissable) | Murs | pleine |

## 8. Variantes de terre, gravier et sable (hors terrain)

À semer au hasard sur les cases pleines.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `terre_b` | Terre battue, variante B | Sol | aucune |
| 97 | `terre_c` | Terre battue, variante C | Sol | aucune |
| 98 | `terre_ornieres_h` | Ornières de charrette horizontales | Sol | aucune |
| 99 | `terre_ornieres_v` | Ornières de charrette verticales | Sol | aucune |
| 100 | `terre_flaque` | Flaque de boue | Sol | aucune |
| 101 | `terre_cailloux` | Terre et cailloux | Sol | aucune |
| 102 | `gravier` | Gravier clair de la rive | Sol | aucune |
| 103 | `sable_rive` | Sable humide de la rive | Sol | aucune |

## 9. Pont-levis (relevé / abaissé)

Le ravin est large de 3 cases (peint avec le terrain Ravin) ; le pont fait **2 cases de large**. Relevé : un panneau debout contre le pied de la tour, côté nord, qui barre le passage. Abaissé : un tablier de 3 cases de haut posé sur le ravin. L'état est piloté par le code (cible à flèche) ; la carte contient la version relevée, le jeu remplace par la version abaissée (voir le rapport).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 104 | `pl_releve_haut_g` | Pont-levis RELEVÉ, haut gauche (panneau debout, chaînes) | Murs | pleine |
| 105 | `pl_releve_haut_d` | Pont-levis RELEVÉ, haut droite | Murs | pleine |
| 106 | `pl_releve_bas_g` | Pont-levis RELEVÉ, bas gauche (pied du panneau) | Murs | pleine |
| 107 | `pl_releve_bas_d` | Pont-levis RELEVÉ, bas droite | Murs | pleine |
| 108 | `pl_abaisse_haut_g` | Pont-levis ABAISSÉ, bout nord gauche (articulation) | Decor | aucune |
| 109 | `pl_abaisse_haut_d` | Pont-levis ABAISSÉ, bout nord droite | Decor | aucune |
| 110 | `pl_abaisse_mil_g` | Pont-levis ABAISSÉ, milieu gauche (planches + garde-corps) | Decor | aucune |
| 111 | `pl_abaisse_mil_d` | Pont-levis ABAISSÉ, milieu droite | Decor | aucune |
| 112 | `pl_abaisse_bas_g` | Pont-levis ABAISSÉ, bout sud gauche (rejoint le chemin du village) | Decor | aucune |
| 113 | `pl_abaisse_bas_d` | Pont-levis ABAISSÉ, bout sud droite | Decor | aucune |
| 114 | `pl_pilier_g` | Pilier de pierre qui porte les chaînes, côté gauche du pont | Murs | pleine |
| 115 | `pl_pilier_d` | Pilier de pierre qui porte les chaînes, côté droit du pont | Murs | pleine |
| 116 | `pl_tour_porte` | Porte de la tour du pont (ferme le nord, solide ; le pont relevé est devant) | Murs | pleine |
| 117 | `pl_tour_mur` | Mur de la tour du pont | Murs | pleine |
| 118 | `pl_chaine_g` | Chaîne du pont (haut, passe devant Brann), côté gauche | Dessus | aucune |
| 119 | `pl_chaine_d` | Chaîne du pont (haut), côté droit | Dessus | aucune |

## 10. Falaise et rochers

Falaise brun-gris de la montagne (est du village, fond du ravin). Haut de falaise = arête, la moitié basse est solide.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 120 | `falaise_crete` | Haut de falaise : arête (moitié basse solide) | Murs | partielle : 0,16 32×16 |
| 121 | `falaise_crete_g` | Haut de falaise, extrémité gauche | Murs | partielle : 3,16 29×16 |
| 122 | `falaise_crete_d` | Haut de falaise, extrémité droite | Murs | partielle : 0,16 29×16 |
| 123 | `falaise_face` | Face de falaise (solide) | Murs | pleine |
| 124 | `falaise_face_g` | Face de falaise, extrémité gauche | Murs | pleine |
| 125 | `falaise_face_d` | Face de falaise, extrémité droite | Murs | pleine |
| 126 | `falaise_pied` | Pied de falaise avec éboulis (solide) | Murs | pleine |
| 127 | `falaise_pied_g` | Pied de falaise, extrémité gauche | Murs | pleine |
| 128 | `falaise_pied_d` | Pied de falaise, extrémité droite | Murs | pleine |
| 129 | `falaise_face_lierre` | Face de falaise couverte de lierre | Murs | pleine |
| 130 | `falaise_face_mousse` | Face de falaise moussue | Murs | pleine |
| 131 | `falaise_sommet` | Sommet de falaise en herbe rase (plateau du château, inaccessible) | Sol | aucune |
| 132 | `falaise_sommet_pierre` | Sommet de falaise, dalle de pierre | Sol | aucune |
| 133 | `rocher_a` | Gros rocher isolé (solide) | Murs | partielle : 4,8 24×22 |
| 134 | `rocher_b` | Gros rocher isolé, variante | Murs | partielle : 4,8 24×22 |
| 135 | `cailloux_village` | Petits cailloux | Decor | aucune |

## 11. Blocages de progression (éboulis, mur fissuré)

Éboulis : solide, à détruire à la bombe plus tard (le code retire la tuile de `Murs` et pose la version dégagée). Mur fissuré : tuile de pierre fissurée ; l'objet `MurFissure` (id) se pose dessus, la bombe l'ouvre.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 136 | `eboulis_a` | ÉBOULIS : tas de rochers, case pleine (solide) | Murs | pleine |
| 137 | `eboulis_b` | ÉBOULIS : variante B (solide) | Murs | pleine |
| 138 | `eboulis_g` | ÉBOULIS large, moitié gauche (2×1, solide) | Murs | pleine |
| 139 | `eboulis_d` | ÉBOULIS large, moitié droite (2×1, solide) | Murs | pleine |
| 140 | `eboulis_degage_a` | Éboulis DÉGAGÉ : gravats au sol (passable), remplace eboulis_a/b | Sol | aucune |
| 141 | `eboulis_degage_b` | Éboulis DÉGAGÉ : gravats, variante | Sol | aucune |
| 142 | `mur_fissure` | MUR FISSURÉ de la cave de Garrick : pierre fissurée (solide ; objet MurFissure dessus) | Murs | pleine |
| 143 | `mur_fissure_ouvert` | Mur fissuré OUVERT : trou noir dans le mur (Sortie vers la cave de Garrick posée dessus) | Decor | aucune |
| 144 | `mur_fissure_gravats` | Gravats devant le mur ouvert (décor) | Decor | aucune |
| 145 | `eboulis_poussiere` | Poussière et cailloux autour de l'éboulis (décor) | Decor | aucune |

## 12. Toit A (tuiles rouges)

Toit en 3 rangées (haut, milieu, bas = avant-toit) sur `Murs` (solide : on ne marche pas sur un toit). Largeur minimale 3 cases ; répéter `_m` et la rangée du milieu pour agrandir.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 160 | `toit_a_haut_g` | Toit A, rangée haute, bord gauche (faîtage) | Murs | pleine |
| 161 | `toit_a_haut_m` | Toit A, rangée haute (faîtage) | Murs | pleine |
| 162 | `toit_a_haut_d` | Toit A, rangée haute, bord droit | Murs | pleine |
| 163 | `toit_a_mil_g` | Toit A, rangée du milieu, bord gauche | Murs | pleine |
| 164 | `toit_a_mil_m` | Toit A, rangée du milieu | Murs | pleine |
| 165 | `toit_a_mil_d` | Toit A, rangée du milieu, bord droit | Murs | pleine |
| 166 | `toit_a_bas_g` | Toit A, avant-toit, bord gauche | Murs | pleine |
| 167 | `toit_a_bas_m` | Toit A, avant-toit (au-dessus de la façade) | Murs | pleine |
| 168 | `toit_a_bas_d` | Toit A, avant-toit, bord droit | Murs | pleine |
| 169 | `toit_a_cheminee` | Toit A, rangée du milieu avec CHEMINÉE de pierre (remplace _mil_m) | Murs | pleine |
| 170 | `toit_a_lucarne` | Toit A, rangée du milieu avec lucarne (remplace _mil_m) | Murs | pleine |
| 171 | `toit_a_mil_m2` | Toit A, rangée du milieu, variante | Murs | pleine |
| 172 | `toit_a_haut_m2` | Toit A, faîtage, variante | Murs | pleine |
| 173 | `toit_a_flanc_g` | Toit A, flanc gauche en pignon (maison plus étroite) | Murs | pleine |
| 174 | `toit_a_flanc_d` | Toit A, flanc droit en pignon | Murs | pleine |

## 13. Toit B (ardoise grise)

Toit en 3 rangées (haut, milieu, bas = avant-toit) sur `Murs` (solide : on ne marche pas sur un toit). Largeur minimale 3 cases ; répéter `_m` et la rangée du milieu pour agrandir.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 176 | `toit_b_haut_g` | Toit B, rangée haute, bord gauche (faîtage) | Murs | pleine |
| 177 | `toit_b_haut_m` | Toit B, rangée haute (faîtage) | Murs | pleine |
| 178 | `toit_b_haut_d` | Toit B, rangée haute, bord droit | Murs | pleine |
| 179 | `toit_b_mil_g` | Toit B, rangée du milieu, bord gauche | Murs | pleine |
| 180 | `toit_b_mil_m` | Toit B, rangée du milieu | Murs | pleine |
| 181 | `toit_b_mil_d` | Toit B, rangée du milieu, bord droit | Murs | pleine |
| 182 | `toit_b_bas_g` | Toit B, avant-toit, bord gauche | Murs | pleine |
| 183 | `toit_b_bas_m` | Toit B, avant-toit (au-dessus de la façade) | Murs | pleine |
| 184 | `toit_b_bas_d` | Toit B, avant-toit, bord droit | Murs | pleine |
| 185 | `toit_b_cheminee` | Toit B, rangée du milieu avec CHEMINÉE de pierre (remplace _mil_m) | Murs | pleine |
| 186 | `toit_b_lucarne` | Toit B, rangée du milieu avec lucarne (remplace _mil_m) | Murs | pleine |
| 187 | `toit_b_mil_m2` | Toit B, rangée du milieu, variante | Murs | pleine |
| 188 | `toit_b_haut_m2` | Toit B, faîtage, variante | Murs | pleine |
| 189 | `toit_b_flanc_g` | Toit B, flanc gauche en pignon (maison plus étroite) | Murs | pleine |
| 190 | `toit_b_flanc_d` | Toit B, flanc droit en pignon | Murs | pleine |

## 14. Toit C (chaume)

Toit en 3 rangées (haut, milieu, bas = avant-toit) sur `Murs` (solide : on ne marche pas sur un toit). Largeur minimale 3 cases ; répéter `_m` et la rangée du milieu pour agrandir.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 192 | `toit_c_haut_g` | Toit C, rangée haute, bord gauche (faîtage) | Murs | pleine |
| 193 | `toit_c_haut_m` | Toit C, rangée haute (faîtage) | Murs | pleine |
| 194 | `toit_c_haut_d` | Toit C, rangée haute, bord droit | Murs | pleine |
| 195 | `toit_c_mil_g` | Toit C, rangée du milieu, bord gauche | Murs | pleine |
| 196 | `toit_c_mil_m` | Toit C, rangée du milieu | Murs | pleine |
| 197 | `toit_c_mil_d` | Toit C, rangée du milieu, bord droit | Murs | pleine |
| 198 | `toit_c_bas_g` | Toit C, avant-toit, bord gauche | Murs | pleine |
| 199 | `toit_c_bas_m` | Toit C, avant-toit (au-dessus de la façade) | Murs | pleine |
| 200 | `toit_c_bas_d` | Toit C, avant-toit, bord droit | Murs | pleine |
| 201 | `toit_c_cheminee` | Toit C, rangée du milieu avec CHEMINÉE de pierre (remplace _mil_m) | Murs | pleine |
| 202 | `toit_c_lucarne` | Toit C, rangée du milieu avec lucarne (remplace _mil_m) | Murs | pleine |
| 203 | `toit_c_mil_m2` | Toit C, rangée du milieu, variante | Murs | pleine |
| 204 | `toit_c_haut_m2` | Toit C, faîtage, variante | Murs | pleine |
| 205 | `toit_c_flanc_g` | Toit C, flanc gauche en pignon (maison plus étroite) | Murs | pleine |
| 206 | `toit_c_flanc_d` | Toit C, flanc droit en pignon | Murs | pleine |

## 15. Façades modulaires (1 rangée sous le toit)

Porte d'1 case : les montants sont solides, le centre est libre ; l'objet `Sortie` se pose sur la case de la porte (Brann y entre par le sud). Style A = colombages crème (toit A), B = pierre grise (toit B, forge), C = planches (toit C).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 208 | `fac_a_coin_g` | Façade A (colombages crème), coin gauche | Murs | pleine |
| 209 | `fac_a_plein` | Façade A, mur plein | Murs | pleine |
| 210 | `fac_a_fenetre` | Façade A, fenêtre | Murs | pleine |
| 211 | `fac_a_volets` | Façade A, fenêtre à volets | Murs | pleine |
| 212 | `fac_a_coin_d` | Façade A, coin droit | Murs | pleine |
| 213 | `fac_a_porte` | PORTE d'1 case, façade A (Sortie dessus) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 214 | `fac_a_porte_enseigne` | PORTE d'1 case avec enseigne suspendue, façade A (boutiques) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 215 | `fac_a_plein_b` | Façade A, mur plein variante (lierre / tonneau) | Murs | pleine |
| 216 | `fac_b_coin_g` | Façade B (pierre grise), coin gauche | Murs | pleine |
| 217 | `fac_b_plein` | Façade B, mur plein | Murs | pleine |
| 218 | `fac_b_fenetre` | Façade B, fenêtre | Murs | pleine |
| 219 | `fac_b_volets` | Façade B, fenêtre à volets | Murs | pleine |
| 220 | `fac_b_coin_d` | Façade B, coin droit | Murs | pleine |
| 221 | `fac_b_porte` | PORTE d'1 case, façade B (Sortie dessus) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 222 | `fac_b_porte_enseigne` | PORTE d'1 case avec enseigne suspendue, façade B (boutiques) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 223 | `fac_b_plein_b` | Façade B, mur plein variante (lierre / tonneau) | Murs | pleine |
| 224 | `fac_c_coin_g` | Façade C (planches de bois), coin gauche | Murs | pleine |
| 225 | `fac_c_plein` | Façade C, mur plein | Murs | pleine |
| 226 | `fac_c_fenetre` | Façade C, fenêtre | Murs | pleine |
| 227 | `fac_c_volets` | Façade C, fenêtre à volets | Murs | pleine |
| 228 | `fac_c_coin_d` | Façade C, coin droit | Murs | pleine |
| 229 | `fac_c_porte` | PORTE d'1 case, façade C (Sortie dessus) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 230 | `fac_c_porte_enseigne` | PORTE d'1 case avec enseigne suspendue, façade C (boutiques) | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 231 | `fac_c_plein_b` | Façade C, mur plein variante (lierre / tonneau) | Murs | pleine |

## 16. Forge de Corvan (reconnaissable : suie, grande cheminée, enclume dehors)

Façade de pierre B noircie + grande cheminée de forge rouge sur le toit B. L'enclume est dehors, devant la porte : c'est là que se pose l'objet `StatueCorbeau` (point de sauvegarde, id `village_statue_forge`).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 232 | `enclume` | ENCLUME (dehors, devant la forge) : solide, perchoir du corbeau | Murs | partielle : 4,10 24×20 |
| 233 | `meule` | Meule à aiguiser | Murs | partielle : 4,8 24×22 |
| 234 | `bac_trempe` | Bac de trempe (eau noire) | Murs | partielle : 4,8 24×22 |
| 235 | `tas_charbon` | Tas de charbon | Murs | partielle : 4,8 24×22 |
| 236 | `rateliers_armes` | Râtelier d'armes et d'outils contre le mur | Murs | partielle : 4,8 24×22 |
| 237 | `forge_enseigne` | Enseigne de forge (marteau et enclume) suspendue au-dessus de la porte | Dessus | aucune |
| 238 | `forge_facade_foyer` | Façade de la forge, ouverture du foyer qui rougeoie (solide) | Murs | pleine |
| 239 | `forge_toit_cheminee` | Toit B avec GRANDE CHEMINÉE de forge (remplace toit_b_mil_m ; fumée possible au-dessus) | Murs | pleine |
| 240 | `forge_porte` | PORTE de la forge (1 case, fer à cheval) : Sortie vers l'intérieur de la forge | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 241 | `forge_facade_suie` | Façade de la forge, pierre noircie de suie | Murs | pleine |
| 242 | `forge_auvent_g` | Auvent de la forge, bord gauche (poutres ; on passe dessous) | Dessus | aucune |
| 243 | `forge_auvent_m` | Auvent de la forge, milieu | Dessus | aucune |
| 244 | `forge_auvent_d` | Auvent de la forge, bord droit | Dessus | aucune |
| 245 | `fumee_a` | Fumée de cheminée (semi-transparente, sur Dessus) | Dessus | aucune |
| 246 | `fumee_b` | Fumée de cheminée, variante | Dessus | aucune |
| 247 | `billot_forge` | Billot et marteaux | Murs | partielle : 4,8 24×22 |

## 17. Puits (2×2), abreuvoir, bancs, charrette

Le puits est au centre de la place. Assemblage 2×2 : haut (poulie, toit) + bas (margelle). Les bords hauts passent derrière Brann.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 248 | `puits_haut_g` | PUITS 2×2, haut gauche (poulie et petit toit) | Murs | partielle : 0,16 32×16 |
| 249 | `puits_haut_d` | PUITS 2×2, haut droite | Murs | partielle : 0,16 32×16 |
| 250 | `seau` | Seau en bois posé au sol | Decor | aucune |
| 251 | `auge_g` | Abreuvoir en pierre, moitié gauche | Murs | partielle : 4,8 24×22 |
| 252 | `auge_d` | Abreuvoir en pierre, moitié droite | Murs | partielle : 4,8 24×22 |
| 253 | `banc_g` | Banc de la place, bout gauche | Murs | partielle : 2,14 30×14 |
| 254 | `banc_m` | Banc de la place, milieu | Murs | partielle : 0,14 32×14 |
| 255 | `banc_d` | Banc de la place, bout droit | Murs | partielle : 0,14 30×14 |
| 256 | `puits_bas_g` | PUITS 2×2, bas gauche (margelle) | Murs | pleine |
| 257 | `puits_bas_d` | PUITS 2×2, bas droite | Murs | pleine |
| 258 | `foin_botte` | Botte de foin | Murs | partielle : 4,8 24×22 |
| 259 | `foin_tas` | Tas de foin (décor solide) | Murs | partielle : 4,8 24×22 |
| 260 | `charrette_g` | Charrette à bras, moitié gauche | Murs | partielle : 4,8 24×22 |
| 261 | `charrette_d` | Charrette à bras, moitié droite | Murs | partielle : 4,8 24×22 |
| 262 | `tas_bois` | Tas de bois de chauffage | Murs | partielle : 4,8 24×22 |
| 263 | `billot_bois` | Billot avec hache | Murs | partielle : 4,8 24×22 |

## 18. Clôtures et murets

Clôtures de bois (jardins, enclos) et murets de pierre (terrasses). Le portillon est solide fermé.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 264 | `cloture_h` | Clôture horizontale | Murs | partielle : 0,12 32×12 |
| 265 | `cloture_v` | Clôture verticale | Murs | partielle : 10,0 12×32 |
| 266 | `cloture_c_hg` | Clôture, coin haut-gauche | Murs | partielle : 10,12 22×20 |
| 267 | `cloture_c_hd` | Clôture, coin haut-droite | Murs | partielle : 0,12 22×20 |
| 268 | `cloture_c_bg` | Clôture, coin bas-gauche | Murs | partielle : 10,0 22×24 |
| 269 | `cloture_c_bd` | Clôture, coin bas-droite | Murs | partielle : 0,0 22×24 |
| 270 | `cloture_portillon` | Portillon fermé (solide) | Murs | partielle : 0,12 32×12 |
| 271 | `cloture_portillon_ouvert` | Portillon ouvert (décor, passable) | Decor | aucune |
| 272 | `muret_h` | Muret de pierre horizontal | Murs | partielle : 0,12 32×16 |
| 273 | `muret_v` | Muret de pierre vertical | Murs | partielle : 8,0 16×32 |
| 274 | `muret_c_hg` | Muret, coin haut-gauche | Murs | partielle : 8,12 24×20 |
| 275 | `muret_c_hd` | Muret, coin haut-droite | Murs | partielle : 0,12 24×20 |
| 276 | `muret_c_bg` | Muret, coin bas-gauche | Murs | partielle : 8,0 24×28 |
| 277 | `muret_c_bd` | Muret, coin bas-droite | Murs | partielle : 0,0 24×28 |
| 278 | `muret_poteau` | Pilier de muret | Murs | partielle : 11,14 10×18 |
| 279 | `escalier_rampe` | Rampe de terre entre deux niveaux (passable) | Sol | aucune |

## 19. Étals, tonneaux, caisses

Auvents sur `Dessus` : on passe dessous ; les étals sont solides.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 280 | `etal_g` | Étal de marché, bout gauche (marchandises) | Murs | partielle : 0,8 32×22 |
| 281 | `etal_m` | Étal de marché, milieu | Murs | partielle : 0,8 32×22 |
| 282 | `etal_d` | Étal de marché, bout droit | Murs | partielle : 0,8 32×22 |
| 283 | `auvent_g` | Auvent de toile rayée, bord gauche (Dessus) | Dessus | aucune |
| 284 | `auvent_m` | Auvent de toile rayée, milieu (Dessus) | Dessus | aucune |
| 285 | `auvent_d` | Auvent de toile rayée, bord droit (Dessus) | Dessus | aucune |
| 286 | `tonneau` | Tonneau | Murs | partielle : 4,8 24×22 |
| 287 | `tonneaux` | Deux tonneaux | Murs | partielle : 4,8 24×22 |
| 288 | `caisse` | Caisse de bois | Murs | partielle : 4,8 24×22 |
| 289 | `caisses_empilees` | Caisses empilées | Murs | partielle : 4,8 24×22 |
| 290 | `sacs` | Sacs de grain | Murs | partielle : 4,8 24×22 |
| 291 | `jarre` | Grande jarre | Murs | partielle : 4,8 24×22 |
| 292 | `panier` | Panier de pommes | Murs | partielle : 4,8 24×22 |
| 293 | `citrouilles` | Citrouilles | Murs | partielle : 4,8 24×22 |
| 294 | `bois_fendu` | Bois fendu en pile | Murs | partielle : 4,8 24×22 |
| 295 | `ruche` | Ruche | Murs | partielle : 4,8 24×22 |

## 20. Fleurs et potagers

Parterres sans collision sur `Decor` ; pot de fleurs et buisson fleuri solides.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 296 | `parterre_rouge` | Parterre de fleurs rouges | Decor | aucune |
| 297 | `parterre_jaune` | Parterre de fleurs jaunes | Decor | aucune |
| 298 | `parterre_blanc` | Parterre de fleurs blanches | Decor | aucune |
| 299 | `pot_fleurs` | Pot de fleurs (devant une porte) | Murs | partielle : 4,8 24×22 |
| 300 | `buisson_fleuri` | Buisson fleuri | Murs | partielle : 4,8 24×22 |
| 301 | `rosier_mur` | Rosier grimpant (à poser sur la façade, Decor) | Decor | aucune |
| 302 | `potager_a` | Rangs de légumes | Decor | aucune |
| 303 | `potager_b` | Rangs de choux | Decor | aucune |

## 21. Lampadaires, panneaux, bornes

Panneaux : objet `PNJ`/`Indice` posé dessus pour le texte. Haut du lampadaire sur `Dessus`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 304 | `lampadaire_bas` | Lampadaire, pied (solide) | Murs | partielle : 11,14 10×18 |
| 305 | `lampadaire_haut` | Lampadaire, lanterne (passe devant Brann ; se pose au-dessus du pied) | Dessus | aucune |
| 306 | `lanterne_murale` | Lanterne accrochée au mur (Dessus) | Dessus | aucune |
| 307 | `panneau_bois` | Panneau de bois (texte) | Murs | partielle : 11,14 10×18 |
| 308 | `panneau_g` | Panneau directionnel vers la gauche | Murs | partielle : 11,14 10×18 |
| 309 | `panneau_d` | Panneau directionnel vers la droite | Murs | partielle : 11,14 10×18 |
| 310 | `borne` | Borne de pierre | Murs | partielle : 11,14 10×18 |
| 311 | `stele_gardiens` | Stèle des anciens gardiens (indice de l'histoire) | Murs | partielle : 4,8 24×22 |

## 22. Quai, ponton, barques, rive

Ponton sur `Decor`, au-dessus de l'eau. Si l'eau dessous est profonde (Murs), retirer la collision sous le ponton.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 312 | `ponton_h` | Ponton, planches horizontales (se raccorde à gauche/droite) | Decor | aucune |
| 313 | `ponton_v` | Ponton, planches verticales | Decor | aucune |
| 314 | `ponton_bout_g` | Ponton, extrémité gauche | Decor | aucune |
| 315 | `ponton_bout_d` | Ponton, extrémité droite | Decor | aucune |
| 316 | `ponton_bout_haut` | Ponton, extrémité haute | Decor | aucune |
| 317 | `ponton_bout_bas` | Ponton, extrémité basse (côté berge) | Decor | aucune |
| 318 | `pilotis` | Pilotis dans l'eau | Murs | partielle : 11,14 10×18 |
| 319 | `bollard` | Bitte d'amarrage | Murs | partielle : 11,14 10×18 |
| 320 | `barque_g` | Barque amarrée, moitié gauche | Murs | partielle : 0,8 32×22 |
| 321 | `barque_d` | Barque amarrée, moitié droite | Murs | partielle : 0,8 32×22 |
| 322 | `filet` | Filet de pêche séchant | Murs | partielle : 4,8 24×22 |
| 323 | `poisson_seche` | Séchoir à poissons | Murs | partielle : 4,8 24×22 |
| 324 | `roseaux_a` | Roseaux | Decor | aucune |
| 325 | `roseaux_b` | Roseaux, variante | Decor | aucune |
| 326 | `nenuphars` | Nénuphars (sur l'eau) | Decor | aucune |
| 327 | `rocher_eau` | Rocher dans l'eau | Murs | partielle : 4,8 24×22 |

## 23. Château lointain (silhouette sur la falaise, 8×3)

Visible dès le premier écran au nord-est. À poser sur le sommet de falaise, derrière la falaise, **hors de portée** (calque Murs pour être sûr). Version brume = teintée bleu-gris dans `village_brume.png`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 328 | `chateau_00` | Château : Tour gauche, sommet | Murs | pleine |
| 329 | `chateau_01` | Château : Créneaux | Murs | pleine |
| 330 | `chateau_02` | Château : Tourelle | Murs | pleine |
| 331 | `chateau_03` | Château : Donjon, sommet | Murs | pleine |
| 332 | `chateau_04` | Château : Donjon, drapeau | Murs | pleine |
| 333 | `chateau_05` | Château : Tourelle | Murs | pleine |
| 334 | `chateau_06` | Château : Créneaux | Murs | pleine |
| 335 | `chateau_07` | Château : Tour droite, sommet | Murs | pleine |
| 336 | `chateau_10` | Château : Tour gauche, milieu | Murs | pleine |
| 337 | `chateau_11` | Château : Mur d'enceinte | Murs | pleine |
| 338 | `chateau_12` | Château : Mur et tourelle | Murs | pleine |
| 339 | `chateau_13` | Château : Donjon, milieu (fenêtres) | Murs | pleine |
| 340 | `chateau_14` | Château : Donjon, milieu | Murs | pleine |
| 341 | `chateau_15` | Château : Mur et tourelle | Murs | pleine |
| 342 | `chateau_16` | Château : Mur d'enceinte | Murs | pleine |
| 343 | `chateau_17` | Château : Tour droite, milieu | Murs | pleine |
| 344 | `chateau_20` | Château : Tour gauche, pied | Murs | pleine |
| 345 | `chateau_21` | Château : Mur d'enceinte, pied | Murs | pleine |
| 346 | `chateau_22` | Château : Poterne | Murs | pleine |
| 347 | `chateau_23` | Château : Donjon, pied | Murs | pleine |
| 348 | `chateau_24` | Château : Grande porte du château | Murs | pleine |
| 349 | `chateau_25` | Château : Poterne | Murs | pleine |
| 350 | `chateau_26` | Château : Mur d'enceinte, pied | Murs | pleine |
| 351 | `chateau_27` | Château : Tour droite, pied | Murs | pleine |

## 24. Brume (semi-transparente, calque `Dessus`)

Tuiles à demi transparentes qui donnent la brume épaisse du début. Les poser en nappes sur `Dessus` ; le code (ou un second calque de brume) les masque quand la brume se lève.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 352 | `brume_dense_a` | Brume dense, nappe A | Dessus | aucune |
| 353 | `brume_dense_b` | Brume dense, nappe B | Dessus | aucune |
| 354 | `brume_dense_c` | Brume dense, nappe C | Dessus | aucune |
| 355 | `brume_dense_d` | Brume dense, nappe D | Dessus | aucune |
| 356 | `brume_bord_haut` | Brume, dégradé : dense en bas, claire en haut | Dessus | aucune |
| 357 | `brume_bord_bas` | Brume, dégradé : dense en haut, claire en bas | Dessus | aucune |
| 358 | `brume_bord_g` | Brume, dégradé : dense à droite | Dessus | aucune |
| 359 | `brume_bord_d` | Brume, dégradé : dense à gauche | Dessus | aucune |
| 360 | `brume_legere_a` | Brume légère, voile A | Dessus | aucune |
| 361 | `brume_legere_b` | Brume légère, voile B | Dessus | aucune |
| 362 | `brume_legere_c` | Brume légère, voile C | Dessus | aucune |
| 363 | `brume_legere_d` | Brume légère, voile D | Dessus | aucune |
| 364 | `brume_trouee_a` | Brume trouée (volutes) | Dessus | aucune |
| 365 | `brume_trouee_b` | Brume trouée, variante | Dessus | aucune |
| 366 | `brume_sol_a` | Brume rasante au sol (Decor, semi-transparente) | Decor | aucune |
| 367 | `brume_sol_b` | Brume rasante au sol, variante | Decor | aucune |

## Assemblages (pinceau « tampon » dans Tiled)

| Assemblage | Tuiles (ligne par ligne) | Calques / usage |
| --- | --- | --- |
| **Pont-levis relevé (2×2)** | `104 105 / 106 107` | Murs — posé sur la rive nord, contre la tour ; ravin peint (Murs) devant |
| **Pont-levis abaissé (2×3)** | `108 109 / 110 111 / 112 113` | Decor (+ retirer les Murs du ravin dessous) — le code supprime la collision en dessous à l'abaissement |
| **Falaise de 3 cases de haut** | `120 / 123 / 126` | Murs — extrémités : _g / _d |
| **Éboulis large (2×1)** | `138 139` | Murs — ferme un passage de 2 cases sur la rive sud |
| **Maison type A : toit + façade (largeur 4)** | `160 161 161 162 / 163 169 164 165 / 166 167 167 168 / 208 210 213 212` | Murs (tout) ; Sortie sur la case porte — même principe pour B et C |
| **Forge de Corvan (façade 5 de large)** | `176 177 177 177 178 / 179 239 180 180 181 / 182 183 183 183 184 / 216 238 240 218 220` | Murs ; auvent (Dessus) sur la rangée d'avant-toit si voulu — enclume à poser sur la case devant la porte à gauche (Decor/Murs), StatueCorbeau dessus |
| **Puits 2×2** | `248 249 / 256 257` | Murs — entouré de paves_rond en 4×4 ; les deux rangées sont solides |
| **Château lointain (8×3)** | `328 329 330 331 332 333 334 335 / 336 337 338 339 340 341 342 343 / 344 345 346 347 348 349 350 351` | Murs — au-dessus de la falaise, tuiles 0 à 7 de chaque rangée |

## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain est un bloc de 16 tuiles : id = base + (HG×8 + HD×4 + BG×2 + BD), 1 = terrain secondaire dans ce coin.

| Terrain | Couleurs (1 / 2) | Tuiles | Calque |
| --- | --- | --- | --- |
| `Paves` | herbe / paves | 16–31 (+ herbe 0–6 si herbe) | Sol |
| `Terre` | herbe / terre | 32–47 (+ herbe 0–6 si herbe) | Sol |
| `Rive` | herbe / eau | 48–63 (+ herbe 0–6 si herbe) | Sol |
| `Lac profond` | eau / profonde | 64–79 (+ herbe 0–6 si herbe) | Sol |
| `Ravin` | herbe / ravin | 80–95 (+ herbe 0–6 si herbe) | Sol |

## Notes

- Pas de tuile de porte « escalier » : les maisons n'ont pas de marches, l'entrée est de plain-pied (la Sortie est sur la tuile de porte).
- À régler dans Tiled après livraison du dessin : propriétés, éventuelles animations (fumée, drapeau, eau).
