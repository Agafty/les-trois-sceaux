# Plan du tileset `montagne` — La montagne (overworld : ravin et pont-levis, sentiers, falaises, col, entrée de la Mine Effondrée)

> Fichier généré par `tools/sprites/montagne.py` : modifier le script, pas ce fichier. **État : DESSIN FINAL** (les numéros sont ceux du plan, aucune tuile n'a bougé).

- Image : `art/tilesets/montagne.png`, 256×1472 px, 8 colonnes × 46 lignes de tuiles 32×32, sans marge ni espacement (368 cases). Tileset Tiled : `maps/tilesets/montagne.tsx` (collisions et terrains définis). `art/tilesets/montagne_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 43 à 46 (ids 336 à 367) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette : pierre gris-bleu, ocre, verts sombres. Les collisions sont dans le tileset (voir la colonne Collision).
- **Le RAVIN (terrain `Ravin`, ids 80 à 95) est aux mêmes numéros que le ravin de `village`** : Brann et les ennemis sont bloqués, les flèches passent au-dessus (le code reconnaît (tileset `montagne`, ids 80 à 95)). Les tuiles de ravin sont sur `Murs`.
- **Buissons coupables** : `buisson_montagne_a` et `_b` (un coup d'épée les retire, comme les buissons de `foret`). **Eboulis et rocher fissuré** : mêmes noms que dans `village`.
- Ce tileset ne contient pas l'herbe de plaine, les maisons ni les arbres de forêt : on mélange avec `foret` et `village` dans la même carte (Tiled accepte plusieurs tilesets par carte). Le pont-levis lui-même est une `Porte` d'apparence `pont_levis` (image dans `art/puzzles/`).

## Calques

- `Sol` : roche, gravier, sentier, herbe de montagne, neige, ruisseau (peu profond), ravin et torrent (le fond), sols de décor
- `Decor` : petits décors sans collision (fleurs, cailloux, rails, ponts, écume, éboulis dégagé…)
- `Murs` : tout ce qui bloque (falaises, ravin, torrent, rochers, arbres, mine, wagonnets). Les collisions sont dans le tileset
- `Objets` : Sortie, Spawn, PNJ, Coffre, MurFissure, StatueCorbeau, Interrupteur… (objets Tiled, pas des tuiles)
- `Dessus` : passe devant Brann (cimes des gros arbres, poutres d'étai, lanternes, chaînes)

## 1. Sols de montagne

Les tuiles 0 à 6 (roche) servent de base à tous les terrains : peindre la roche d'abord, puis le terrain par-dessus. Semer les variantes au hasard pour casser la répétition.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `roche_a` | Sol rocheux gris-bleu, de base | Sol | aucune |
| 1 | `roche_b` | Sol rocheux avec petits cailloux | Sol | aucune |
| 2 | `roche_c` | Sol rocheux fissuré | Sol | aucune |
| 3 | `roche_d` | Sol rocheux avec mousse | Sol | aucune |
| 4 | `roche_e` | Sol rocheux avec touffes d'herbe | Sol | aucune |
| 5 | `roche_f` | Dalles de roche | Sol | aucune |
| 6 | `roche_sombre` | Sol rocheux sombre (au pied des falaises) | Sol | aucune |
| 7 | `roche_claire` | Sol rocheux clair (sommets, ensoleillé) | Sol | aucune |
| 8 | `gravier_a` | Gravier gris | Sol | aucune |
| 9 | `gravier_b` | Gros gravier et cailloux | Sol | aucune |
| 10 | `schiste` | Schiste en strates grises et ocre | Sol | aucune |
| 11 | `roche_ocre` | Sol rocheux ocre (col, abords de la mine) | Sol | aucune |
| 12 | `roche_minerai` | Sol rocheux avec éclats de minerai | Sol | aucune |
| 13 | `roche_cendre` | Sol sombre de poussière de mine | Sol | aucune |
| 14 | `herbe_seche` | Herbe sèche de montagne | Sol | aucune |
| 15 | `tapis_mousse` | Tapis de mousse | Sol | aucune |

## 2. Sentier de terre (terrain `Sentier`)

Sentier ocre sur roche : peindre la roche, puis le terrain Sentier.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 16 | `sentier_base` | Roche (base du terrain Sentier) | Sol | aucune |
| 17 | `sentier_0001` | Sol : coin bas-droite seulement (Sentier de terre dans ce coin) | Sol | aucune |
| 18 | `sentier_0010` | Sol : coin bas-gauche seulement (Sentier de terre dans ce coin) | Sol | aucune |
| 19 | `sentier_0011` | Sol : Sentier de terre en bas (bord bas) | Sol | aucune |
| 20 | `sentier_0100` | Sol : coin haut-droite seulement (Sentier de terre dans ce coin) | Sol | aucune |
| 21 | `sentier_0101` | Sol : Sentier de terre à droite (bord droit) | Sol | aucune |
| 22 | `sentier_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 23 | `sentier_0111` | Sol : Sentier de terre partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 24 | `sentier_1000` | Sol : coin haut-gauche seulement (Sentier de terre dans ce coin) | Sol | aucune |
| 25 | `sentier_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 26 | `sentier_1010` | Sol : Sentier de terre à gauche (bord gauche) | Sol | aucune |
| 27 | `sentier_1011` | Sol : Sentier de terre partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 28 | `sentier_1100` | Sol : Sentier de terre en haut (bord haut) | Sol | aucune |
| 29 | `sentier_1101` | Sol : Sentier de terre partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 30 | `sentier_1110` | Sol : Sentier de terre partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 31 | `sentier_plein` | Sentier de terre, case entière | Sol | aucune |

## 3. Herbe rase de montagne (terrain `HerbeM`)

Herbe rase vert sombre sur roche.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 32 | `herbem_base` | Roche (base du terrain HerbeM) | Sol | aucune |
| 33 | `herbem_0001` | Sol : coin bas-droite seulement (Herbe de montagne dans ce coin) | Sol | aucune |
| 34 | `herbem_0010` | Sol : coin bas-gauche seulement (Herbe de montagne dans ce coin) | Sol | aucune |
| 35 | `herbem_0011` | Sol : Herbe de montagne en bas (bord bas) | Sol | aucune |
| 36 | `herbem_0100` | Sol : coin haut-droite seulement (Herbe de montagne dans ce coin) | Sol | aucune |
| 37 | `herbem_0101` | Sol : Herbe de montagne à droite (bord droit) | Sol | aucune |
| 38 | `herbem_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 39 | `herbem_0111` | Sol : Herbe de montagne partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 40 | `herbem_1000` | Sol : coin haut-gauche seulement (Herbe de montagne dans ce coin) | Sol | aucune |
| 41 | `herbem_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 42 | `herbem_1010` | Sol : Herbe de montagne à gauche (bord gauche) | Sol | aucune |
| 43 | `herbem_1011` | Sol : Herbe de montagne partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 44 | `herbem_1100` | Sol : Herbe de montagne en haut (bord haut) | Sol | aucune |
| 45 | `herbem_1101` | Sol : Herbe de montagne partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 46 | `herbem_1110` | Sol : Herbe de montagne partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 47 | `herbem_plein` | Herbe de montagne, case entière | Sol | aucune |

## 4. Neige et givre (terrain `Neige`)

Neige légère sur roche (sommets). Facultatif.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `neige_base` | Roche (base du terrain Neige) | Sol | aucune |
| 49 | `neige_0001` | Sol : coin bas-droite seulement (Neige dans ce coin) | Sol | aucune |
| 50 | `neige_0010` | Sol : coin bas-gauche seulement (Neige dans ce coin) | Sol | aucune |
| 51 | `neige_0011` | Sol : Neige en bas (bord bas) | Sol | aucune |
| 52 | `neige_0100` | Sol : coin haut-droite seulement (Neige dans ce coin) | Sol | aucune |
| 53 | `neige_0101` | Sol : Neige à droite (bord droit) | Sol | aucune |
| 54 | `neige_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 55 | `neige_0111` | Sol : Neige partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 56 | `neige_1000` | Sol : coin haut-gauche seulement (Neige dans ce coin) | Sol | aucune |
| 57 | `neige_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 58 | `neige_1010` | Sol : Neige à gauche (bord gauche) | Sol | aucune |
| 59 | `neige_1011` | Sol : Neige partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 60 | `neige_1100` | Sol : Neige en haut (bord haut) | Sol | aucune |
| 61 | `neige_1101` | Sol : Neige partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 62 | `neige_1110` | Sol : Neige partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 63 | `neige_plein` | Neige, case entière | Sol | aucune |

## 5. Ruisseau (terrain `Ruisseau`, eau peu profonde)

Eau peu profonde sur roche : Brann la traverse à gué.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 64 | `ruisseau_base` | Roche (base du terrain Ruisseau) | Sol | aucune |
| 65 | `ruisseau_0001` | Sol : coin bas-droite seulement (Eau peu profonde dans ce coin) | Sol | aucune |
| 66 | `ruisseau_0010` | Sol : coin bas-gauche seulement (Eau peu profonde dans ce coin) | Sol | aucune |
| 67 | `ruisseau_0011` | Sol : Eau peu profonde en bas (bord bas) | Sol | aucune |
| 68 | `ruisseau_0100` | Sol : coin haut-droite seulement (Eau peu profonde dans ce coin) | Sol | aucune |
| 69 | `ruisseau_0101` | Sol : Eau peu profonde à droite (bord droit) | Sol | aucune |
| 70 | `ruisseau_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Sol | aucune |
| 71 | `ruisseau_0111` | Sol : Eau peu profonde partout sauf le coin haut-gauche (coin rentrant) | Sol | aucune |
| 72 | `ruisseau_1000` | Sol : coin haut-gauche seulement (Eau peu profonde dans ce coin) | Sol | aucune |
| 73 | `ruisseau_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Sol | aucune |
| 74 | `ruisseau_1010` | Sol : Eau peu profonde à gauche (bord gauche) | Sol | aucune |
| 75 | `ruisseau_1011` | Sol : Eau peu profonde partout sauf le coin haut-droite (coin rentrant) | Sol | aucune |
| 76 | `ruisseau_1100` | Sol : Eau peu profonde en haut (bord haut) | Sol | aucune |
| 77 | `ruisseau_1101` | Sol : Eau peu profonde partout sauf le coin bas-gauche (coin rentrant) | Sol | aucune |
| 78 | `ruisseau_1110` | Sol : Eau peu profonde partout sauf le coin bas-droite (coin rentrant) | Sol | aucune |
| 79 | `ruisseau_plein` | Eau peu profonde, case entière (traversable) | Sol | aucune |

## 6. RAVIN (terrain `Ravin`, ids 80 à 95, comme dans `village`)

Roche / vide du ravin. Les cases de ravin sont solides (`Murs`) ; les flèches passent au-dessus (le code reconnaît ces ids). Le pont-levis est une `Porte` posée sur le ravin.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 80 | `ravin_base` | Roche (base du terrain Ravin) | Sol | aucune |
| 81 | `ravin_0001` | Sol : coin bas-droite seulement (Ravin dans ce coin) | Murs | partielle : 16,16 16×16 |
| 82 | `ravin_0010` | Sol : coin bas-gauche seulement (Ravin dans ce coin) | Murs | partielle : 0,16 16×16 |
| 83 | `ravin_0011` | Sol : Ravin en bas (bord bas) | Murs | partielle : 0,16 32×16 |
| 84 | `ravin_0100` | Sol : coin haut-droite seulement (Ravin dans ce coin) | Murs | partielle : 16,0 16×16 |
| 85 | `ravin_0101` | Sol : Ravin à droite (bord droit) | Murs | partielle : 16,0 16×32 |
| 86 | `ravin_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Murs | partielle : 16,0 16×16 ; 0,16 16×16 |
| 87 | `ravin_0111` | Sol : Ravin partout sauf le coin haut-gauche (coin rentrant) | Murs | partielle : 16,0 16×16 ; 0,16 32×16 |
| 88 | `ravin_1000` | Sol : coin haut-gauche seulement (Ravin dans ce coin) | Murs | partielle : 0,0 16×16 |
| 89 | `ravin_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Murs | partielle : 0,0 16×16 ; 16,16 16×16 |
| 90 | `ravin_1010` | Sol : Ravin à gauche (bord gauche) | Murs | partielle : 0,0 16×32 |
| 91 | `ravin_1011` | Sol : Ravin partout sauf le coin haut-droite (coin rentrant) | Murs | partielle : 0,0 16×16 ; 0,16 32×16 |
| 92 | `ravin_1100` | Sol : Ravin en haut (bord haut) | Murs | partielle : 0,0 32×16 |
| 93 | `ravin_1101` | Sol : Ravin partout sauf le coin bas-gauche (coin rentrant) | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 94 | `ravin_1110` | Sol : Ravin partout sauf le coin bas-droite (coin rentrant) | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 95 | `ravin_plein` | Ravin, case entière (vide, infranchissable) | Murs | pleine |

## 7. Torrent (terrain `Torrent`, eau profonde infranchissable)

Eau peu profonde / eau profonde. Les bords et la case pleine sont sur `Murs`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 96 | `torrent_base` | Eau peu profonde (base du terrain Torrent) | Sol | aucune |
| 97 | `torrent_0001` | Sol : coin bas-droite seulement (Eau profonde dans ce coin) | Murs | partielle : 16,16 16×16 |
| 98 | `torrent_0010` | Sol : coin bas-gauche seulement (Eau profonde dans ce coin) | Murs | partielle : 0,16 16×16 |
| 99 | `torrent_0011` | Sol : Eau profonde en bas (bord bas) | Murs | partielle : 0,16 32×16 |
| 100 | `torrent_0100` | Sol : coin haut-droite seulement (Eau profonde dans ce coin) | Murs | partielle : 16,0 16×16 |
| 101 | `torrent_0101` | Sol : Eau profonde à droite (bord droit) | Murs | partielle : 16,0 16×32 |
| 102 | `torrent_0110` | Sol : deux coins opposés (haut-droite et bas-gauche) | Murs | partielle : 16,0 16×16 ; 0,16 16×16 |
| 103 | `torrent_0111` | Sol : Eau profonde partout sauf le coin haut-gauche (coin rentrant) | Murs | partielle : 16,0 16×16 ; 0,16 32×16 |
| 104 | `torrent_1000` | Sol : coin haut-gauche seulement (Eau profonde dans ce coin) | Murs | partielle : 0,0 16×16 |
| 105 | `torrent_1001` | Sol : deux coins opposés (haut-gauche et bas-droite) | Murs | partielle : 0,0 16×16 ; 16,16 16×16 |
| 106 | `torrent_1010` | Sol : Eau profonde à gauche (bord gauche) | Murs | partielle : 0,0 16×32 |
| 107 | `torrent_1011` | Sol : Eau profonde partout sauf le coin haut-droite (coin rentrant) | Murs | partielle : 0,0 16×16 ; 0,16 32×16 |
| 108 | `torrent_1100` | Sol : Eau profonde en haut (bord haut) | Murs | partielle : 0,0 32×16 |
| 109 | `torrent_1101` | Sol : Eau profonde partout sauf le coin bas-gauche (coin rentrant) | Murs | partielle : 0,0 32×16 ; 16,16 16×16 |
| 110 | `torrent_1110` | Sol : Eau profonde partout sauf le coin bas-droite (coin rentrant) | Murs | partielle : 0,0 32×16 ; 0,16 16×16 |
| 111 | `torrent_plein` | Eau profonde, case entière (infranchissable) | Murs | pleine |

## 8. Variantes de sentier, neige et franchissements (hors terrain)

À semer au hasard sur les cases pleines. `gue_pierres` se pose sur le ruisseau ; les escaliers et la rampe sont passables.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 112 | `sentier_b` | Sentier, variante B | Sol | aucune |
| 113 | `sentier_c` | Sentier, variante C | Sol | aucune |
| 114 | `sentier_cailloux` | Sentier et cailloux | Sol | aucune |
| 115 | `sentier_ornieres_h` | Ornières de wagon horizontales | Sol | aucune |
| 116 | `sentier_ornieres_v` | Ornières de wagon verticales | Sol | aucune |
| 117 | `sentier_boue` | Flaque de boue gelée | Sol | aucune |
| 118 | `neige_b` | Neige, variante B | Sol | aucune |
| 119 | `neige_traces` | Neige avec traces de pas | Sol | aucune |
| 120 | `neige_givre` | Roche givrée | Sol | aucune |
| 121 | `gue_pierres` | Gué : pierres plates dans le ruisseau (passable) | Sol | aucune |
| 122 | `dalle_ancienne` | Dalle ancienne gravée (vieille route du col) | Sol | aucune |
| 123 | `escalier_pierre_h` | Marches de pierre (montée vers le haut) | Sol | aucune |
| 124 | `escalier_pierre_v` | Marches de pierre (montée de côté) | Sol | aucune |
| 125 | `rampe_terre` | Rampe de terre entre deux niveaux (passable) | Sol | aucune |
| 126 | `galets` | Galets de la rive | Sol | aucune |
| 127 | `sable_ruisseau` | Sable humide du ruisseau | Sol | aucune |

## 9. Falaise basse (3 cases : crête, face, pied)

Falaise gris-bleu. Haut de falaise = arête (la moitié basse est solide) ; les extrémités `_g` / `_d` ferment le bout d'un tronçon ; `cote_*` sont les falaises vues de côté (virages). Le plateau se peint avec le sol de votre choix au-dessus de la crête.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 128 | `falaise_crete` | Haut de falaise : arête (moitié basse solide) | Murs | partielle : 0,16 32×16 |
| 129 | `falaise_crete_g` | Haut de falaise, extrémité gauche | Murs | partielle : 3,16 29×16 |
| 130 | `falaise_crete_d` | Haut de falaise, extrémité droite | Murs | partielle : 0,16 29×16 |
| 131 | `falaise_face` | Face de falaise (roche verticale, solide) | Murs | pleine |
| 132 | `falaise_face_g` | Face de falaise, extrémité gauche | Murs | partielle : 3,0 29×32 |
| 133 | `falaise_face_d` | Face de falaise, extrémité droite | Murs | partielle : 0,0 29×32 |
| 134 | `falaise_pied` | Pied de falaise (éboulis, ombre ; on longe le bas) | Murs | partielle : 0,0 32×24 |
| 135 | `falaise_pied_g` | Pied de falaise, extrémité gauche | Murs | partielle : 3,0 29×24 |
| 136 | `falaise_pied_d` | Pied de falaise, extrémité droite | Murs | partielle : 0,0 29×24 |
| 137 | `falaise_cote_g` | Falaise vue de côté : roche à gauche, plateau à droite | Murs | partielle : 0,0 12×32 |
| 138 | `falaise_cote_d` | Falaise vue de côté : roche à droite, plateau à gauche | Murs | partielle : 20,0 12×32 |
| 139 | `falaise_cote_pied_g` | Falaise de côté, pied gauche (jonction avec le pied) | Murs | partielle : 0,0 12×24 |
| 140 | `falaise_cote_pied_d` | Falaise de côté, pied droit | Murs | partielle : 20,0 12×24 |
| 141 | `falaise_coin_int_g` | Coin rentrant gauche (la crête tourne vers le bas) | Murs | partielle : 0,0 14×32 ; 0,16 32×16 |
| 142 | `falaise_coin_int_d` | Coin rentrant droite | Murs | partielle : 18,0 14×32 ; 0,16 32×16 |
| 143 | `falaise_veine` | Face de falaise avec veine de minerai | Murs | pleine |

## 10. Falaise haute (5 cases : crête, haut, milieu, bas, pied)

Pour les grandes parois : crête, `fh_haut`, `fh_mil` (à répéter), `fh_bas`, pied. Mêmes extrémités `_g` / `_d`. Variantes neigeuse, avec grotte et avec étais de mine.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 144 | `fh_haut` | Falaise haute, face haute (sous la crête, éclairée) | Murs | pleine |
| 145 | `fh_haut_g` | Falaise haute, face haute, extrémité gauche | Murs | partielle : 3,0 29×32 |
| 146 | `fh_haut_d` | Falaise haute, face haute, extrémité droite | Murs | partielle : 0,0 29×32 |
| 147 | `fh_mil` | Falaise haute, face du milieu (à répéter) | Murs | pleine |
| 148 | `fh_mil_g` | Falaise haute, milieu, extrémité gauche | Murs | partielle : 3,0 29×32 |
| 149 | `fh_mil_d` | Falaise haute, milieu, extrémité droite | Murs | partielle : 0,0 29×32 |
| 150 | `fh_bas` | Falaise haute, face basse (sombre, strates) | Murs | pleine |
| 151 | `fh_bas_g` | Falaise haute, face basse, extrémité gauche | Murs | partielle : 3,0 29×32 |
| 152 | `fh_bas_d` | Falaise haute, face basse, extrémité droite | Murs | partielle : 0,0 29×32 |
| 153 | `falaise_neige_crete` | Crête de falaise enneigée (moitié basse solide) | Murs | partielle : 0,16 32×16 |
| 154 | `falaise_neige_face` | Face de falaise givrée | Murs | pleine |
| 155 | `falaise_etais` | Face de falaise renforcée d'étais de mine | Murs | pleine |
| 156 | `falaise_fissure` | FACE FISSURÉE : roche fendue (solide ; objet MurFissure dessus, la bombe l'ouvre) | Murs | pleine |
| 157 | `falaise_fissure_ouvert` | Face fissurée OUVERTE : trou noir dans la roche (Sortie dessus) | Decor | aucune |
| 158 | `falaise_grotte` | ENTRÉE DE GROTTE d'1 case dans la face (Sortie dessus) : trou noir, montants solides | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 159 | `falaise_grotte_haut` | Linteau de grotte : roche au-dessus de l'ouverture | Murs | pleine |
| 160 | `escalier_crete` | ESCALIER taillé, case de crête (remplace falaise_crete ; passable) | Sol | aucune |
| 161 | `escalier_face` | ESCALIER taillé, case de face (remplace falaise_face ; passable) | Sol | aucune |
| 162 | `escalier_pied` | ESCALIER taillé, case de pied (remplace falaise_pied ; passable) | Sol | aucune |
| 163 | `escalier_fh_haut` | ESCALIER taillé, falaise haute : haut | Sol | aucune |
| 164 | `escalier_fh_mil` | ESCALIER taillé, falaise haute : milieu | Sol | aucune |
| 165 | `escalier_fh_bas` | ESCALIER taillé, falaise haute : bas | Sol | aucune |
| 166 | `escalier_cote_g` | Escalier taillé le long d'une paroi, montée vers la gauche | Sol | aucune |
| 167 | `escalier_cote_d` | Escalier taillé le long d'une paroi, montée vers la droite | Sol | aucune |

## 11. Rochers, éboulis, rocher fissuré

Les rochers sont solides. ÉBOULIS : à détruire à la bombe (le code retire la tuile et pose la version dégagée). ROCHER FISSURÉ : l'objet `MurFissure` se pose dessus.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 168 | `rocher_a` | Rocher gris-bleu, solide | Murs | partielle : 4,8 24×22 |
| 169 | `rocher_b` | Gros rocher en deux blocs, solide | Murs | partielle : 4,8 24×22 |
| 170 | `rocher_mousse` | Rocher moussu, solide | Murs | partielle : 4,8 24×22 |
| 171 | `rocher_neige` | Rocher enneigé, solide | Murs | partielle : 4,8 24×22 |
| 172 | `rocher_fissure` | ROCHER FISSURÉ : bloc craquelé (solide ; objet MurFissure dessus) | Murs | pleine |
| 173 | `rocher_fissure_ouvert` | Rocher fissuré OUVERT : cavité noire entre des blocs (Sortie dessus) | Decor | aucune |
| 174 | `rocher_eau` | Rocher dans l'eau, solide | Murs | partielle : 4,8 24×22 |
| 175 | `cailloux_montagne` | Petits cailloux | Decor | aucune |
| 176 | `eboulis_a` | ÉBOULIS : tas de rochers, case pleine (solide) | Murs | pleine |
| 177 | `eboulis_b` | ÉBOULIS : variante B (solide) | Murs | pleine |
| 178 | `eboulis_g` | ÉBOULIS large, moitié gauche (2×1, solide) | Murs | pleine |
| 179 | `eboulis_d` | ÉBOULIS large, moitié droite (2×1, solide) | Murs | pleine |
| 180 | `eboulis_degage_a` | Éboulis DÉGAGÉ : gravats au sol (passable), remplace eboulis_a/b | Sol | aucune |
| 181 | `eboulis_degage_b` | Éboulis DÉGAGÉ : gravats, variante | Sol | aucune |
| 182 | `eboulis_poussiere` | Poussière et cailloux autour de l'éboulis (décor) | Decor | aucune |
| 183 | `gravats` | Gravats devant une ouverture (décor) | Decor | aucune |
| 184 | `gros_rocher_hg` | GROS ROCHER 2×2, haut gauche (solide) | Murs | partielle : 4,8 28×24 |
| 185 | `gros_rocher_hd` | GROS ROCHER 2×2, haut droite | Murs | partielle : 0,8 28×24 |
| 186 | `gros_rocher_bg` | GROS ROCHER 2×2, bas gauche | Murs | partielle : 4,0 28×24 |
| 187 | `gros_rocher_bd` | GROS ROCHER 2×2, bas droite | Murs | partielle : 0,0 28×24 |
| 188 | `cairn` | Cairn : pierres empilées (balise de sentier) | Murs | partielle : 4,8 24×22 |
| 189 | `socle_corbeau` | Socle de pierre (perchoir pour l'objet StatueCorbeau) | Murs | partielle : 4,8 24×22 |
| 190 | `bloc_taille` | Bloc de pierre taillé (vestige du col) | Murs | partielle : 4,8 24×22 |
| 191 | `colonne_brisee` | Colonne brisée | Murs | partielle : 11,14 10×18 |

## 12. Arbres 1×1 : sapins, arbres rabougris, pins morts, buissons

Les tuiles `buisson_montagne_*` sont coupables à l'épée (comme les buissons de `foret`). `sapin_dense_*` : feuillage case pleine pour les forêts de sapins.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 192 | `sapin_petit_a` | Sapin 1×1, solide | Murs | partielle : 8,12 16×18 |
| 193 | `sapin_petit_b` | Sapin 1×1, variante plus large | Murs | partielle : 8,12 16×18 |
| 194 | `sapin_dense_a` | Sapins serrés, case pleine (lisière infranchissable) | Murs | pleine |
| 195 | `sapin_dense_b` | Sapins serrés, variante | Murs | pleine |
| 196 | `arbre_rabougri_a` | Arbre rabougri tordu 1×1, solide | Murs | partielle : 8,12 16×18 |
| 197 | `arbre_rabougri_b` | Arbre rabougri, variante | Murs | partielle : 8,12 16×18 |
| 198 | `pin_mort` | Pin mort 1×1, solide | Murs | partielle : 10,10 12×20 |
| 199 | `souche_montagne` | Souche, solide | Murs | partielle : 6,12 20×16 |
| 200 | `sapin_neige_petit` | Sapin enneigé 1×1, solide | Murs | partielle : 8,12 16×18 |
| 201 | `sapin_dense_neige` | Sapins enneigés serrés, case pleine | Murs | pleine |
| 202 | `tronc_couche` | Tronc couché horizontal, solide | Murs | partielle : 2,10 28×16 |
| 203 | `buisson_montagne_a` | Arbuste de montagne coupable (1 coup d'épée) | Murs | partielle : 2,6 28×24 |
| 204 | `buisson_montagne_b` | Arbuste de montagne coupable, variante | Murs | partielle : 2,6 28×24 |
| 205 | `genevrier` | Genévrier épineux, solide (non coupable) | Murs | partielle : 2,6 28×24 |
| 206 | `buisson_neige` | Buisson enneigé, solide | Murs | partielle : 2,6 28×24 |
| 207 | `fougeres` | Fougères de sous-bois | Decor | aucune |

## 13. Gros arbres 2×2 (cime sur `Dessus`, tronc sur `Murs`)

Poser le tronc (2 cases du bas) sur `Murs` et la cime (2 cases du haut) sur `Dessus`, au-dessus du tronc : Brann passe derrière la cime.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 208 | `sapin_a_cime_hg` | Grand sapin, cime gauche (Dessus) | Dessus | aucune |
| 209 | `sapin_a_cime_hd` | Grand sapin, cime droite (Dessus) | Dessus | aucune |
| 210 | `sapin_b_cime_hg` | Grand sapin (variante), cime gauche (Dessus) | Dessus | aucune |
| 211 | `sapin_b_cime_hd` | Grand sapin (variante), cime droite (Dessus) | Dessus | aucune |
| 212 | `sapin_neige_cime_hg` | Grand sapin enneigé, cime gauche (Dessus) | Dessus | aucune |
| 213 | `sapin_neige_cime_hd` | Grand sapin enneigé, cime droite (Dessus) | Dessus | aucune |
| 214 | `rabougri_cime_hg` | Grand arbre rabougri, cime gauche (Dessus) | Dessus | aucune |
| 215 | `rabougri_cime_hd` | Grand arbre rabougri, cime droite (Dessus) | Dessus | aucune |
| 216 | `pin_mort_cime_hg` | Grand pin mort, branches gauche (Dessus) | Dessus | aucune |
| 217 | `pin_mort_cime_hd` | Grand pin mort, branches droite (Dessus) | Dessus | aucune |
| 218 | `sapin_a_tronc_g` | Grand sapin, tronc gauche (Murs) | Murs | partielle : 14,4 18×28 |
| 219 | `sapin_a_tronc_d` | Grand sapin, tronc droit (Murs) | Murs | partielle : 0,4 18×28 |
| 220 | `sapin_b_tronc_g` | Grand sapin (variante), tronc gauche (Murs) | Murs | partielle : 14,4 18×28 |
| 221 | `sapin_b_tronc_d` | Grand sapin (variante), tronc droit (Murs) | Murs | partielle : 0,4 18×28 |
| 222 | `sapin_neige_tronc_g` | Grand sapin enneigé, tronc gauche (Murs) | Murs | partielle : 14,4 18×28 |
| 223 | `sapin_neige_tronc_d` | Grand sapin enneigé, tronc droit (Murs) | Murs | partielle : 0,4 18×28 |
| 224 | `rabougri_tronc_g` | Grand arbre rabougri, tronc gauche (Murs) | Murs | partielle : 14,4 18×28 |
| 225 | `rabougri_tronc_d` | Grand arbre rabougri, tronc droit (Murs) | Murs | partielle : 0,4 18×28 |
| 226 | `pin_mort_tronc_g` | Grand pin mort, tronc gauche (Murs) | Murs | partielle : 14,4 18×28 |
| 227 | `pin_mort_tronc_d` | Grand pin mort, tronc droit (Murs) | Murs | partielle : 0,4 18×28 |

## 14. Petits décors (calque Decor, sans collision)

Fleurs de montagne, herbes, mousse, ossements.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 232 | `fleurs_alpines_a` | Fleurs alpines bleues et blanches | Decor | aucune |
| 233 | `fleurs_alpines_b` | Fleurs alpines jaunes | Decor | aucune |
| 234 | `bruyere` | Bruyère violette | Decor | aucune |
| 235 | `edelweiss` | Edelweiss | Decor | aucune |
| 236 | `touffes_seches` | Touffes d'herbe sèche | Decor | aucune |
| 237 | `herbe_haute_m` | Herbe haute de montagne | Decor | aucune |
| 238 | `mousse` | Mousse sur la roche | Decor | aucune |
| 239 | `ossements` | Ossements d'animal | Decor | aucune |

## 15. Cascade et sources

Cascade de 1 case de large : haut, milieu (répéter ; deux images à alterner pour l'animation Tiled), pied, écume. La cascade se pose sur une face de falaise (`Murs`).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 240 | `cascade_haut` | CASCADE, bord de chute : l'eau déborde de la crête (solide en bas) | Murs | partielle : 0,16 32×16 |
| 241 | `cascade_milieu_a` | CASCADE, milieu, image A (à répéter) | Murs | pleine |
| 242 | `cascade_milieu_b` | CASCADE, milieu, image B (animation) | Murs | pleine |
| 243 | `cascade_pied` | CASCADE, pied : bassin et écume (infranchissable) | Murs | pleine |
| 244 | `cascade_ecume` | Écume et éclaboussures (décor, à poser sur le bassin) | Decor | aucune |
| 245 | `source_rocher` | SOURCE : l'eau sort d'un rocher (origine d'un ruisseau) | Murs | partielle : 4,8 24×22 |
| 246 | `ecume_rive` | Écume sur une rive | Decor | aucune |
| 247 | `flaque_gel` | Flaque gelée | Decor | aucune |

## 16. Ponts de bois

Sur `Decor`, au-dessus de l'eau. Sur un TORRENT (solide), effacer le torrent de `Murs` sous le pont et peindre l'eau peu profonde sur `Sol` (le pont n'enlève pas la collision tout seul). Sur un ruisseau, rien à faire.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 248 | `pont_h` | Pont de bois horizontal (milieu, à répéter) | Decor | aucune |
| 249 | `pont_h_bout_g` | Pont horizontal, bout gauche (appui sur la rive) | Decor | aucune |
| 250 | `pont_h_bout_d` | Pont horizontal, bout droit | Decor | aucune |
| 251 | `pont_v` | Pont de bois vertical (milieu, à répéter) | Decor | aucune |
| 252 | `pont_v_bout_haut` | Pont vertical, bout haut | Decor | aucune |
| 253 | `pont_v_bout_bas` | Pont vertical, bout bas | Decor | aucune |
| 254 | `pont_pilotis` | Pilotis sous un pont (dans l'eau) | Murs | partielle : 11,14 10×18 |
| 255 | `pont_planches` | Planches posées au sol (réparation) | Decor | aucune |

## 17. Abords du ravin et du pont-levis

Le pont-levis est une `Porte` d'apparence `pont_levis` (2 cases de large) posée sur le ravin ; ces tuiles décorent ses abords. Piliers de pierre qui portent les chaînes, chaînes sur `Dessus`, palier et butée de chaque berge.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 256 | `pl_pilier_g` | Pilier de pierre qui porte les chaînes, côté gauche du pont | Murs | pleine |
| 257 | `pl_pilier_d` | Pilier de pierre qui porte les chaînes, côté droit du pont | Murs | pleine |
| 258 | `pl_chaine_g` | Chaîne du pont (haut, passe devant Brann), côté gauche | Dessus | aucune |
| 259 | `pl_chaine_d` | Chaîne du pont (haut), côté droit | Dessus | aucune |
| 260 | `pl_palier` | Palier de dalles devant le pont (rive sud) | Sol | aucune |
| 261 | `pl_palier_nord` | Palier de dalles de la berge nord (après le pont) | Sol | aucune |
| 262 | `pl_butee` | Butée de bois du pont (poutre au bord du ravin) | Murs | partielle : 0,8 32×24 |
| 263 | `garde_corps_h` | Garde-corps de bois au bord du ravin (horizontal) | Murs | partielle : 0,12 32×12 |

## 18. Rails et wagonnets de mine

Rails sur `Decor` (sans collision) ; wagonnets sur `Murs` (solides). Courbes : le coin indiqué est celui que le rail relie.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 264 | `rail_h` | Rail horizontal | Decor | aucune |
| 265 | `rail_v` | Rail vertical | Decor | aucune |
| 266 | `rail_coin_hg` | Rail courbe : relie le haut et la gauche | Decor | aucune |
| 267 | `rail_coin_hd` | Rail courbe : relie le haut et la droite | Decor | aucune |
| 268 | `rail_coin_bg` | Rail courbe : relie le bas et la gauche | Decor | aucune |
| 269 | `rail_coin_bd` | Rail courbe : relie le bas et la droite | Decor | aucune |
| 270 | `rail_buttoir_g` | Rail horizontal, buttoir à gauche (fin de voie) | Decor | aucune |
| 271 | `rail_buttoir_d` | Rail horizontal, buttoir à droite | Decor | aucune |
| 272 | `rail_buttoir_haut` | Rail vertical, buttoir en haut | Decor | aucune |
| 273 | `rail_buttoir_bas` | Rail vertical, buttoir en bas | Decor | aucune |
| 274 | `rail_croisement` | Croisement de rails | Decor | aucune |
| 275 | `rail_casse` | Rail brisé et traverses arrachées | Decor | aucune |
| 276 | `wagonnet_h` | Wagonnet plein de minerai, vu de côté (sur rail horizontal) | Murs | partielle : 2,8 28×20 |
| 277 | `wagonnet_v` | Wagonnet plein de minerai, sur rail vertical | Murs | partielle : 4,4 24×26 |
| 278 | `wagonnet_vide` | Wagonnet vide | Murs | partielle : 2,8 28×20 |
| 279 | `wagonnet_renverse` | Wagonnet renversé, minerai répandu | Murs | partielle : 2,8 28×20 |

## 19. Étais en bois, minerai, outils

Poutres d'étai : les poteaux sont solides, la poutre du haut est sur `Dessus` (on passe dessous).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 280 | `etai_poteau` | Poteau d'étai de bois (solide) | Murs | partielle : 11,14 10×18 |
| 281 | `etai_poutre_g` | Poutre d'étai, bout gauche (Dessus) | Dessus | aucune |
| 282 | `etai_poutre_m` | Poutre d'étai, milieu (Dessus) | Dessus | aucune |
| 283 | `etai_poutre_d` | Poutre d'étai, bout droit (Dessus) | Dessus | aucune |
| 284 | `etai_cadre_g` | Cadre d'étai : montant gauche contre la roche | Murs | partielle : 0,0 8×32 |
| 285 | `etai_cadre_d` | Cadre d'étai : montant droit | Murs | partielle : 24,0 8×32 |
| 286 | `barriere_h` | Barrière de planches horizontale (chantier, solide) | Murs | partielle : 0,12 32×12 |
| 287 | `barriere_v` | Barrière de planches verticale | Murs | partielle : 10,0 12×32 |
| 288 | `minerai_tas_a` | Tas de minerai, solide | Murs | partielle : 4,8 24×22 |
| 289 | `minerai_tas_b` | Tas de minerai, variante | Murs | partielle : 4,8 24×22 |
| 290 | `minerai_filon` | Bloc de roche à filon de minerai brillant (décor solide) | Murs | pleine |
| 291 | `caisse_mine` | Caisse de mine | Murs | partielle : 4,8 24×22 |
| 292 | `tonneau_mine` | Tonneau de mine | Murs | partielle : 4,8 24×22 |
| 293 | `outils_mine` | Établi de mineur : pioches et masses | Murs | partielle : 4,8 24×22 |
| 294 | `pioche_sol` | Pioche oubliée au sol | Decor | aucune |
| 295 | `tas_planches` | Tas de planches et de poutres | Murs | partielle : 4,8 24×22 |

## 20. Lanternes de mineur, panneaux, bornes

Haut de lanterne sur `Dessus`. Les panneaux portent un texte via un objet `Indice`/`PNJ` posé dessus.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 296 | `lanterne_poteau_bas` | Poteau de lanterne de mineur, pied (solide) | Murs | partielle : 11,14 10×18 |
| 297 | `lanterne_poteau_haut` | Lanterne de mineur au sommet du poteau (Dessus ; au-dessus du pied) | Dessus | aucune |
| 298 | `lanterne_murale` | Lanterne accrochée à un étai ou une paroi (Dessus) | Dessus | aucune |
| 299 | `lanterne_sol` | Lanterne posée au sol (lueur) | Decor | aucune |
| 300 | `lanterne_eteinte` | Lanterne éteinte au sol | Decor | aucune |
| 301 | `lanterne_suspendue` | Lanterne suspendue à une poutre (Dessus) | Dessus | aucune |
| 302 | `torche_support` | Torche plantée dans le sol (support ; décor solide) | Murs | partielle : 11,14 10×18 |
| 303 | `lueur_sol` | Tache de lueur chaude au sol (sous une lanterne) | Decor | aucune |
| 304 | `panneau_bois` | Panneau de bois (texte) | Murs | partielle : 11,14 10×18 |
| 305 | `panneau_g` | Panneau directionnel vers la gauche | Murs | partielle : 11,14 10×18 |
| 306 | `panneau_d` | Panneau directionnel vers la droite | Murs | partielle : 11,14 10×18 |
| 307 | `panneau_danger` | Panneau « danger » (éboulement, tête de mort) | Murs | partielle : 11,14 10×18 |
| 308 | `panneau_mine` | Panneau de la Mine (pioche croisée) | Murs | partielle : 11,14 10×18 |
| 309 | `borne_col` | Borne de pierre du col | Murs | partielle : 11,14 10×18 |
| 310 | `stele_gardiens` | Stèle des anciens gardiens (indice de l'histoire) | Murs | partielle : 4,8 24×22 |
| 311 | `fanions` | Mât de fanions fanés du col | Murs | partielle : 11,14 10×18 |

## 21. ENTRÉE DE LA MINE EFFONDRÉE (5×3 : toit de roche et poutres, façade de planches et de pierre, porte d'1 case)

À adosser à la falaise : poser la façade à la place d'une face de falaise (crête de falaise au-dessus). La porte est la case du bas au centre (`mine_porte`) : l'objet `Sortie` se pose dessus (Brann entre par le sud). L'effondrement est visible (poutres cassées, décombres).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 312 | `mine_toit_g` | Façade de la Mine, rangée du haut : roche et poutre, coin gauche | Murs | pleine |
| 313 | `mine_toit_m` | Façade de la Mine, rangée du haut : roche et poutres | Murs | pleine |
| 314 | `mine_toit_enseigne` | Façade de la Mine, rangée du haut au centre : poutre maîtresse et enseigne | Murs | pleine |
| 315 | `mine_toit_m2` | Façade de la Mine, rangée du haut : roche, variante | Murs | pleine |
| 316 | `mine_toit_d` | Façade de la Mine, rangée du haut : coin droit | Murs | pleine |
| 317 | `mine_mur_pierre` | Mur de pierre de la façade (variante pleine) | Murs | pleine |
| 318 | `mine_planches_b` | Planches clouées (variante pleine) | Murs | pleine |
| 319 | `mine_poutre_tombee_m` | Poutre effondrée en travers du mur | Murs | pleine |
| 320 | `mine_mur_g` | Façade de la Mine, rangée du milieu : coin de pierre et poteau, gauche | Murs | pleine |
| 321 | `mine_mur_planches` | Façade de la Mine, rangée du milieu : planches clouées | Murs | pleine |
| 322 | `mine_linteau` | Façade de la Mine, linteau au-dessus de la porte (poutre, trou noir sous le toit) | Murs | pleine |
| 323 | `mine_mur_effondre` | Façade de la Mine, rangée du milieu : planches arrachées et poutre cassée | Murs | pleine |
| 324 | `mine_mur_d` | Façade de la Mine, rangée du milieu : coin de pierre et poteau, droite | Murs | pleine |
| 325 | `mine_porte_barree` | Porte condamnée (planches en croix, solide) | Murs | pleine |
| 326 | `mine_porte_ouverte` | Porte ouverte : noir de la galerie (décor, à poser sur la porte) | Decor | aucune |
| 327 | `mine_enseigne_dessus` | Enseigne de la Mine suspendue (Dessus) | Dessus | aucune |
| 328 | `mine_pied_g` | Façade de la Mine, rangée du bas : socle de pierre, gauche | Murs | pleine |
| 329 | `mine_pied_decombres` | Façade de la Mine, rangée du bas : décombres | Murs | pleine |
| 330 | `mine_porte` | PORTE de la Mine, case du bas au centre (Sortie dessus) : montants solides, centre libre | Murs | partielle : 0,0 6×32 ; 26,0 6×32 |
| 331 | `mine_pied_pierre` | Façade de la Mine, rangée du bas : socle de pierre | Murs | pleine |
| 332 | `mine_pied_d` | Façade de la Mine, rangée du bas : socle de pierre, droite | Murs | pleine |
| 333 | `mine_decombres_g` | Décombres répandus devant la façade (gauche) | Decor | aucune |
| 334 | `mine_decombres_d` | Décombres répandus devant la façade (droite) | Decor | aucune |
| 335 | `mine_seuil` | Seuil de planches devant la porte (avec rails qui sortent) | Decor | aucune |

## Assemblages (pinceau « tampon » dans Tiled)

| Assemblage | Tuiles (ligne par ligne) | Calques / usage |
| --- | --- | --- |
| **Falaise basse de 3 cases de haut** | `128 / 131 / 134` | Murs — extrémités : _g / _d |
| **Falaise haute de 5 cases** | `128 / 144 / 147 / 150 / 134` | Murs — répéter fh_mil pour plus haut |
| **Escalier à travers une falaise basse** | `160 / 161 / 162` | Murs (remplace la falaise, sans collision) — ouvre un passage d'une case de large |
| **Gros rocher 2×2** | `184 185 / 186 187` | Murs |
| **Éboulis large (2×1)** | `178 179` | Murs — ferme un passage de 2 cases |
| **Grand sapin 2×2** | `208 209 / 218 219` | cime sur Dessus, tronc sur Murs — variantes : sapin_b_, sapin_neige_, rabougri_, pin_mort_ |
| **Entrée de la Mine Effondrée (5×3)** | `312 313 314 315 316 / 320 321 322 323 324 / 328 329 330 331 332` | Murs (tout) ; Sortie sur la case mine_porte — seuil, rails (rail_v) et décombres à poser devant sur Decor |

## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T). Chaque terrain est un bloc de 16 tuiles : id = base + (HG×8 + HD×4 + BG×2 + BD), 1 = terrain secondaire dans ce coin.

| Terrain | Couleurs (1 / 2) | Tuiles | Calque |
| --- | --- | --- | --- |
| `Sentier` | Roche (base du terrain Sentier) / Sentier de terre | 16–31 (+ herbe 0–6 si herbe) | Sol |
| `HerbeM` | Roche (base du terrain HerbeM) / Herbe de montagne | 32–47 (+ herbe 0–6 si herbe) | Sol |
| `Neige` | Roche (base du terrain Neige) / Neige | 48–63 (+ herbe 0–6 si herbe) | Sol |
| `Ruisseau` | Roche (base du terrain Ruisseau) / Eau peu profonde | 64–79 (+ herbe 0–6 si herbe) | Sol |
| `Ravin` | Roche (base du terrain Ravin) / Ravin | 80–95 (+ herbe 0–6 si herbe) | Sol |
| `Torrent` | Eau peu profonde (base du terrain Torrent) / Eau profonde | 96–111 (+ herbe 0–6 si herbe) | Sol |

## Notes

- Statue du corbeau : c'est un objet (`StatueCorbeau`), pas une tuile ; `socle_corbeau` est un décor de pierre où la poser.
- Cascade : `cascade_milieu_a` et `_b` sont les deux images d'une animation (à régler dans Tiled : éditeur d'animation de tuile).
- À régler dans Tiled après livraison du dessin : propriétés, animations (cascade, lanternes).
