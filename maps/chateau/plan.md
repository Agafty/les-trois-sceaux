# Plan de la fin du jeu : route de la falaise, grotte noire, château, combat final, épilogue et générique

Document de conception (phase 6, « Séquence de fin et générique » et « donjon final court »). **Aucun `.tmx` n'existe encore** : on attend la validation de ce plan, surtout les décisions de la section 11. Même format que `maps/donjon3/plan.md` et `maps/overworld/plan.md`, dont les règles de raccord sont reprises telles quelles. Les aperçus ASCII ont été relus par un script (bibliothèque standard seulement : taille des cartes, apparitions à plus de 3 cases des ennemis, accessibilité de chaque objet, de chaque mur à ouvrir, lignes de tir à l'arc) ; résultats en section 9.

Cartes concernées (fichiers à créer) : `maps/overworld/route_falaise.tmx` (40×11), `maps/interieurs/passage_falaise.tmx` (20×22, voir 2.3), `maps/overworld/chateau.tmx` (20×22), puis `maps/chateau/salle_01.tmx` à `salle_04.tmx` (20×11) et `maps/chateau/salle_boss.tmx` (20×22).

## 1. Récit, intention et rythme

**Intention** : la fin n'apprend plus rien de nouveau, elle **réunit** ce que Brann a appris. Chaque objet a un dernier moment (lanterne à la falaise, bombes à la poterne, arc contre les Œils, les trois ensemble dans la salle des Trois Sceaux), puis le combat final reprend la même trinité, dans l'ordre où les objets ont été gagnés (arc, bombes, lanterne). Le public reste un adulte qui joue pour l'histoire et un enfant de 5 ans qui joue aidé : aucune mort en un coup, annonces toujours visibles, aucun chronomètre.

**Récit, étape par étape** (les noms de drapeaux sont ceux du jeu ; les nouveaux sont en gras)

| # | Moment | Où | Ce qui se passe | Drapeaux |
| --- | --- | --- | --- | --- |
| 1 | Sceau du lac pris | salle du boss d'Ondine | Corvan absorbe l'énergie (existe : `donjon3_corvan_final`) | `corvan_absorbe_sceau`, étape 3 |
| 2 | Retour au lac sous l'éclipse | `lac.tmx` | Ciel violet, la caméra cadre le château, « C'est là qu'il m'attend. » (existe : `lac_retour_eclipse`) | `lac_eclipse_vu` |
| 3 | Village vide, éclipse | `village.tmx` (étape 3) | Brann traverse le village ; Hulda et Isolde restent. Pas de cinématique, seulement leurs dialogues de l'étape 3 (déjà prévus) | — |
| 4 | Route de la falaise | `route_falaise.tmx` | Route calme sous l'éclipse ; la bouche de la grotte, fermée par un mur à rune qui brille, était visible depuis le début du jeu | — |
| 5 | Grotte noire | `passage_falaise.tmx` | Deux murs à rune, trois Ombres noyées ; la lanterne sert une dernière fois « seule » | — |
| 6 | Cour du château | `chateau.tmx` | **Une voix lointaine (Corvan) conseille la petite porte** : cinématique `chateau_cour_voix` | **`chateau_cour_vu`** |
| 7 | Les quatre salles | `maps/chateau/salle_01` à `04` | Œils (arc), Chevaliers, salle des Trois Sceaux (arc, bombes, lanterne), antichambre et statue | — |
| 8 | Défi de Corvan | `salle_boss` | Dernier dialogue avant le combat | **`corvan_defie`** |
| 9 | Combat final | `salle_boss` | Phase 1 (marteau), Morvath prend le dessus, phase 2 (ronces, pierre, eau), l'Œil de Morvath | **`morvath_eveille`** |
| 10 | Corvan vieil homme, exil | `salle_boss` | Dialogue, Corvan s'en va ; l'éclipse se termine | **`morvath_vaincu`** (étape 4), **`corvan_exil`** |
| 11 | Le sceau unique | `forge.tmx` | Brann forge les trois sceaux en un seul ; Morvath y est enfermé | **`sceau_unique`** |
| 12 | La fête | `village.tmx` (étape 4) | Soleil, guirlandes, toast ; Brann regarde la route de l'est | **`fete_vue`**, **`jeu_termine`** |
| 13 | Générique | `scenes/ui/generique.tscn` | Défilement, musique « Fin et générique » ; retour à l'écran titre | — |

**Courbe de difficulté** (tension de 1 à 5) : route 1, grotte 2, cour 2 (premier Chevalier, seul), salle 01 (Œils) 2, salle 02 (2 Chevaliers) 3, salle 03 (énigme sans ennemi) 2, antichambre 1 (repos, statue), combat final 4 à 5 puis cinématiques de fin 0. Rythme : calme - calme-sombre - découverte - tir - combat - énigme - repos - **grand combat** - longues scènes calmes. Durée estimée : 30 minutes, dont 5 à 6 de combat final et 8 de cinématiques.

## 2. Chaîne des cartes, raccords et propriétés de carte

### 2.1 La chaîne

```text
village (est) --- route_falaise --[mur à rune, lanterne]-- passage_falaise (sombre, 2 écrans)
                                                               |
                                                          chateau (cour) --[poterne fissurée, bombe]-- salle_01 (arc)
                                                                                                         |
                                                                                                       salle_02 (Chevaliers)
                                                                                                         |
                                                                                                       salle_03 (Trois Sceaux : grande clé)
                                                                                                         |
                                                                                                       salle_04 (antichambre, statue)
                                                                                                         |  [grande clé]
                                                                                                       salle_boss (Corvan / Morvath)
                                                                                                         |
                                                                              (cinématique) --> forge --> village (fête) --> générique
```

Toutes les liaisons sont à deux sens, sauf la dernière flèche (`aller_a`, voir 7).

### 2.2 Raccords (Sortie / Spawn)

Les ids de `Spawn` suivent la règle du Sanctuaire : `depuis_<côté ou lieu d'où l'on vient>`. Coordonnées en pixels. Les raccords village/route sont **déjà fixés** dans `maps/overworld/plan.md` §1.2 (non modifiés ici).

| Passage | Sortie (carte, rectangle) | Spawn d'arrivée (carte, id, centre) |
| --- | --- | --- |
| Village vers route | (déjà fixé) | `route_falaise` `depuis_village` (80, 160) |
| Route vers village | `route_falaise` (0, 128, 32, 64) | `village` `depuis_route` (1200, 160) |
| Route vers grotte | `route_falaise` (1056, 32, 64, 32), **derrière le mur à rune** `route_porte_01` | `passage_falaise` `depuis_route` (304, 624) |
| Grotte vers route | `passage_falaise` (288, 672, 32, 32) | `route_falaise` `depuis_passage_falaise` (1088, 112) |
| Grotte vers cour | `passage_falaise` (288, 0, 64, 32) | `chateau` `depuis_passage_falaise` (320, 624) |
| Cour vers grotte | `chateau` (288, 672, 64, 32) | `passage_falaise` `depuis_chateau` (320, 80) |
| Cour vers salle 01 | `chateau` (128, 128, 32, 32), **sous le mur fissuré** `chateau_mur_01` | `chateau_salle_01` `depuis_cour` (304, 272) |
| Salle 01 vers cour | `salle_01` (288, 320, 32, 32) | `chateau` `depuis_salle_01` (144, 208) |
| Salle 01 vers 02 | `salle_01` (288, 0, 32, 32) + `Porte` `chateau_porte_01` | `salle_02` `depuis_sud` (304, 272) |
| Salle 02 vers 01 | `salle_02` (288, 320, 32, 32) | `salle_01` `depuis_nord` (304, 80) |
| Salle 02 vers 03 | `salle_02` (288, 0, 32, 32) + `Porte` `chateau_porte_02` | `salle_03` `depuis_sud` (304, 272) |
| Salle 03 vers 02 | `salle_03` (288, 320, 32, 32) | `salle_02` `depuis_nord` (304, 80) |
| Salle 03 vers 04 | `salle_03` (288, 0, 32, 32) (sans porte) | `salle_04` `depuis_sud` (304, 272) |
| Salle 04 vers 03 | `salle_04` (288, 320, 32, 32) | `salle_03` `depuis_nord` (304, 80) |
| Salle 04 vers boss | `salle_04` (288, 0, 32, 32) + `Porte` `chateau_porte_05` (`grande_cle`) | `salle_boss` `depuis_sud` (304, 624) |
| Boss vers salle 04 | `salle_boss` (288, 672, 32, 32) + même `Porte` `chateau_porte_05` | `salle_04` `depuis_nord` (304, 80) |
| Fin du combat vers la forge | aucune `Sortie` : action `aller_a` de la cinématique `chateau_corvan_vaincu` | `forge` `depuis_chateau` (à créer dans `forge.tmx`, case libre devant l'établi, jamais sur la porte) |

Les trois cartes d'extérieur sont raccordées à la grille du monde : `route_falaise` monde (3,2), `chateau` monde (4,0).

### 2.3 Propriétés de carte

| Carte | `Zone` (scène) | `camera` | `obscurite` | Autres |
| --- | --- | --- | --- | --- |
| `route_falaise` | `route` | `suivre` | — | `monde_x`=3, `monde_y`=2 |
| `passage_falaise` | `route` | `ecran` | `penombre` | intérieur (fond noir inutile : la carte remplit ses 2 écrans) |
| `chateau` | `chateau` | `suivre` | — | `monde_x`=4, `monde_y`=0 |
| `salle_01` à `salle_04`, `salle_boss` | `chateau` | `ecran` (salles), aucune pour le boss (la caméra suit Brann, comme Ondine) | — | pas de `etage`, `carte_x`, `carte_y` : pas de carte de donjon (décision 1) |

Scènes à créer : `scenes/rooms/route_falaise_room.tscn`, `passage_falaise_room.tscn`, `chateau_room.tscn`, `chateau_salle_01_room.tscn` à `chateau_salle_04_room.tscn`, `chateau_salle_boss_room.tscn`.

**Pourquoi 20×22 pour la grotte** : le plan de l'overworld la prévoyait en 20×11. Une grotte sombre d'un seul écran ne laisse la place qu'à un mur à rune ; sur deux écrans (défilement par écran, comme les salles de plusieurs écrans) elle contient l'antichambre lumineuse, le mur obligatoire, la salle des Ombres et l'alcôve de la plume. Elle reste un « intérieur » (`maps/interieurs/`).

## 3. Règles communes et légende

- Salles du château : mêmes règles de raccord que le Sanctuaire (pourtour d'une case, ouvertures aux positions fixes (9,0) et (9,10), `Spawn` à (9,2) et (9,8), une `Porte` par face dans chacune des deux cartes avec le même `id`, déclencheur toujours dans la salle d'une face de sa porte, aucun ennemi à moins de 3 cases d'un `Spawn`, levier ou cible jamais sur ou à côté d'une `Porte` ou d'une `Sortie`, ni dans un couloir d'une case).
- **Aucune petite clé, aucun bloc poussable, aucune fosse mortelle, aucune plaque** : l'économie des clés se réduit à une grande clé, donc pas de risque de blocage (section 9). Le « fossé de ronces » `~` est un ravin (infranchissable, laisse passer les flèches).
- Ambiance : à l'étape 3, tout l'extérieur et tout le château sont sous la teinte d'éclipse (code, voir 10.3). Seule la grotte est en `penombre`.
- Textes d'indice : très peu, la disposition guide (rune qui brille, fissure dans le mur, œil gravé). Les indices sont des rectangles `indice_*` (clé `INDICE_*`).

Légende des aperçus : `#` mur, `.` sol, `~` fossé de ronces (infranchissable, les flèches passent), `O` pilier, rocher ou colonne, `H` portail scellé (décor solide), `P` Spawn (le `Spawn` d'un passage de 2 cases est au centre des deux cases : une seule lettre ici), `X` Sortie, `R` statue du corbeau, `Y` brasero, `k` Chevalier corrompu, `o` Œil de Morvath, `u` Ombre noyée, `r` Ronceau rouge, `s` Sanglier noirci rouge, `c` Caillou rampant, `F` mur fissuré, `Z` mur à rune, `N` porte « ennemis » (sur une Sortie), `I` grille à interrupteur, `G` porte grande clé (sur une Sortie), `C` coffre, `l` levier (interrupteur à l'épée), `S` cible de flèche, `f` plume de corbeau, `m` paquet de flèches, `b` paquet de bombes, `h` petit cœur, `g` Corvan (point `boss_corvan`), `1` `2` `3` positions de l'Œil de Morvath (Marqueurs).

## 4. Les cartes

### 4.1 `route_falaise.tmx` (40×11, deux écrans)

Intention : un temps de respiration entre le village vide et la grotte. La route est **la même qu'au début du jeu** (on l'a déjà vue en cul-de-sac) ; ce qui change est la teinte d'éclipse et le mur à rune, **visible depuis l'étape 0** (« montrer avant d'exiger » : il brille faiblement, le joueur apprend « il fait trop sombre ici »), qui s'ouvre enfin avec la lanterne. Quatre ennemis seulement, jamais plus de deux à la fois dans le champ de la caméra.

Propriétés : `Zone`=`route`, `camera`=`suivre`, `monde_x`=3, `monde_y`=2.

<!-- route_falaise -->
```text
########################################
#################################XX#####
#############............O.......ZZ....#
#.....O...............O.......O........#
X.P.............OO.....................#
X........r............c.......R........#
#........O.......s..........c.......O..#
#############O......O..................#
#############O.............#############
########################################
########################################
```

Objets Tiled (calque `Objets`) :

- `Sortie` (0,128,32,64) : `cible_carte`=`res://scenes/rooms/village_room.tscn`, `cible_spawn`=`depuis_route`, `godot_node_type`=`area`
- `Spawn` point (80,160) : `id`=`depuis_village`
- `Sortie` (1056,32,64,32) [alcôve derrière la rune] : `cible_carte`=`res://scenes/rooms/passage_falaise_room.tscn`, `cible_spawn`=`depuis_route`, `godot_node_type`=`area`
- `Porte` (1056,64,64,32) : `id`=`route_porte_01`, `type`=`lanterne`, `apparence`=`mur_rune`, **sans `etape_min`** (présente dès le début du jeu)
- `Spawn` point (1088,112) : `id`=`depuis_passage_falaise`
- `StatueCorbeau` point (976,176) : `id`=`route_statue_falaise`
- `Ennemi` point (304,176) : `type`=`ronceau`, `variante`=`rouge`
- `Ennemi` point (560,208) : `type`=`sanglier_noirci`, `variante`=`rouge`
- `Ennemi` point (720,176) : `type`=`caillou_rampant`, `variante`=`normal`
- `Ennemi` point (912,208) : `type`=`caillou_rampant`, `variante`=`normal`
- Rectangle `indice_grotte` (1024,96,128,64), `godot_node_type`=`area` : clé `INDICE_GROTTE_FALAISE`

La `Sortie` de l'alcôve n'est **pas** sur le rectangle de la `Porte` (elle est une case derrière) : la `Porte` `mur_rune` est « sans `Sortie` » comme le veut la convention (question au développeur en 10.3).

### 4.2 `passage_falaise.tmx` (20×22, intérieur, grotte noire)

Intention : réutiliser la lanterne une dernière fois **sans nouveauté**. Écran du bas : antichambre éclairée par deux braseros (arrivée sûre), puis le couloir étroit barré par le **mur à rune obligatoire**. Écran du haut : la salle des Ombres, trois Ombres noyées normales (jamais obligatoires, elles se figent dans la lumière), deux braseros près de la sortie, et à l'est une alcôve derrière un second mur à rune (facultatif) : la **plume de corbeau** de la falaise. Courte : 2 à 3 minutes.

Propriétés : `Zone`=`route`, `camera`=`ecran`, `obscurite`=`penombre`.

<!-- passage_falaise -->
```text
#########XX#########
###.....Y..Y....####
###......P......####
###.............####
###..u..........Z.f#
###.....O..O....Z..#
###.............####
###..........u..####
###...u.........####
###.............####
#########..#########
#########..#########
#######......#######
#######......#######
#########ZZ#########
#########..#########
######........######
######........######
######.Y....Y.######
######...P....######
######........######
#########X##########
```

Objets Tiled :

- `Sortie` (288,672,32,32) : `cible_carte`=`res://scenes/rooms/route_falaise_room.tscn`, `cible_spawn`=`depuis_passage_falaise`, `godot_node_type`=`area`
- `Sortie` (288,0,64,32) : `cible_carte`=`res://scenes/rooms/chateau_room.tscn`, `cible_spawn`=`depuis_passage_falaise`, `godot_node_type`=`area`
- `Spawn` point (304,624) : `id`=`depuis_route` ; `Spawn` point (320,80) : `id`=`depuis_chateau`
- `Porte` (288,448,64,32) : `id`=`route_porte_02`, `type`=`lanterne`, `apparence`=`mur_rune` (obligatoire)
- `Porte` (512,128,32,64) : `id`=`route_porte_03`, `type`=`lanterne`, `apparence`=`mur_rune` (facultatif, plume)
- `Ramassable` point (592,144) : `id`=`route_plume_01`, `contenu`=`plume_corbeau`
- `Torche` (brasero, `permanente`=`true`, `etat`=`allumee`) points (240,592), (400,592), (272,48), (368,48) : `id` `route_brasero_01` à `04`
- `Ennemi` points (176,144), (432,240), (208,272) : `type`=`ombre_noyee`, `variante`=`normal`
- Rectangle `indice_passage` (256,544,128,96), `godot_node_type`=`area` : clé `INDICE_PASSAGE_SOMBRE`

### 4.3 `chateau.tmx` (20×22, la cour)

Intention : la cour est **l'apprentissage du Chevalier** (un seul, en patrouille, dans un grand espace) et de la **poterne**. Le grand portail, scellé par le symbole de l'Œil (décor solide), est évidemment infranchissable ; une fissure se voit dans la muraille à gauche, et la voix de Corvan souffle la solution (cinématique `chateau_cour_voix`). Un Œil de Morvath dans une niche de la façade tire doucement : c'est l'occasion d'apprendre qu'il se tue d'une flèche (ou d'un coup d'épée de près, il est à portée de main ici), avant la salle 01 où il faudra l'arc. Statue du corbeau à l'arrivée. La carte est sous la teinte d'éclipse.

Propriétés : `Zone`=`chateau`, `camera`=`suivre`, `monde_x`=4, `monde_y`=0.

<!-- chateau -->
```text
####################
####################
#########HH#########
#########HH#########
####F####HH###o#####
#..................#
#..................#
#..................#
#..................#
#...O..........O...#
#..................#
#..................#
#.............k....#
#..................#
#..................#
#...O..........O...#
#..................#
#..................#
#..................#
#.....R..P.........#
#..................#
#########XX#########
```

Objets Tiled :

- `Sortie` (288,672,64,32) : `cible_carte`=`res://scenes/rooms/passage_falaise_room.tscn`, `cible_spawn`=`depuis_chateau`, `godot_node_type`=`area`
- `Spawn` point (320,624) : `id`=`depuis_passage_falaise`
- `StatueCorbeau` point (208,624) : `id`=`chateau_statue_cour`
- `MurFissure` (128,128,32,32) : `id`=`chateau_mur_01`, `apparence`=`mur` ; `Sortie` de **même rectangle** : `cible_carte`=`res://scenes/rooms/chateau_salle_01_room.tscn`, `cible_spawn`=`depuis_cour`, `godot_node_type`=`area`
- `Spawn` point (144,208) : `id`=`depuis_salle_01`
- `Ennemi` point (464,400) : `type`=`chevalier_corrompu`, `variante`=`normal`
- `Ennemi` point (464,144) : `type`=`oeil_morvath`, `variante`=`normal` (dans la niche de la façade)
- `Marqueur` point (320,112) : `id`=`chateau_portail`
- `Scenario` point (320,576) : `cinematique`=`chateau_cour_voix`, `si`=`corvan_absorbe_sceau`, `sauf`=`chateau_cour_vu`
- Rectangle `indice_portail` (256,160,128,64), `godot_node_type`=`area` : clé `INDICE_CHATEAU_PORTAIL`

Les piliers `O` sont des statues de chevaliers (décor solide) qui servent d'abri contre le Chevalier. Le tir de l'Œil de la niche est lent (1 cœur) ; La cour offre des centaines de cases pour reculer pendant la mèche de la bombe.

### 4.4 `salle_01.tmx` : Hall des Veilleurs (l'arc)

Intention : le **dernier cours d'arc**. Deux Œils sont logés dans la muraille du nord, derrière deux fosses de ronces : l'épée ne les atteint pas (distance mini 3,2 cases), seule la flèche les touche (portée de l'arc : 10 cases ; la fosse laisse passer les flèches). La porte du nord est fermée tant qu'ils vivent. Aucun autre ennemi : le joueur peut viser tranquillement et esquiver les orbes lents (un pas de côté). Si Brann est à court de flèches, il sort par la poterne (le Chevalier de la cour lâche un paquet).

<!-- salle_01 -->
```text
###o#####N######o###
#~~~~~........~~~~~#
#~~~~~...P....~~~~~#
#~~~~~........~~~~~#
#~~~~~........~~~~~#
#..................#
#..................#
#..................#
#.....O..P...O.....#
#..................#
#########X##########
```

Objets Tiled :

- `Sortie` (288,0,32,32) + `Porte` (même rectangle) : `id`=`chateau_porte_01`, `type`=`ennemis` ; `cible_carte`=`res://scenes/rooms/chateau_salle_02_room.tscn`, `cible_spawn`=`depuis_sud`
- `Sortie` (288,320,32,32) : `cible_carte`=`res://scenes/rooms/chateau_room.tscn`, `cible_spawn`=`depuis_salle_01`
- `Spawn` points (304,272) `depuis_cour` et (304,80) `depuis_nord`
- `Ennemi` points (112,16) et (528,16) : `type`=`oeil_morvath` (dans la muraille ; ce sont les deux seuls ennemis de la salle)

### 4.5 `salle_02.tmx` : Galerie des Armures (le combat)

Intention : **le combat** de l'ensemble. Deux Chevaliers aux deux extrémités d'une galerie à piliers. Ils ne se voient pas d'emblée (portée de détection 5 cases) : on peut en attirer un seul. Les piliers servent d'abri (le Chevalier n'a pas de projectile). La porte du nord s'ouvre quand les deux sont vaincus. Ils lâchent des cœurs, des flèches et des bombes (butin garanti sous les seuils) pour préparer la salle 03.

<!-- salle_02 -->
```text
#########N##########
#.Y..............Y.#
#........P.........#
#....O........O....#
#..................#
#...k..........k...#
#..................#
#....O........O....#
#........P.........#
#..................#
#########X##########
```

Objets Tiled :

- `Sortie` (288,0,32,32) + `Porte` `chateau_porte_02` (`ennemis`) ; `cible_carte`=`res://scenes/rooms/chateau_salle_03_room.tscn`, `cible_spawn`=`depuis_sud`
- `Sortie` (288,320,32,32) : `cible_carte`=`res://scenes/rooms/chateau_salle_01_room.tscn`, `cible_spawn`=`depuis_nord`
- `Spawn` points (304,272) `depuis_sud` et (304,80) `depuis_nord`
- `Ennemi` points (144,176) et (496,176) : `type`=`chevalier_corrompu`, `variante`=`normal`
- `Torche` (brasero) points (80,48), (560,48) : `chateau_brasero_01`, `02`

### 4.6 `salle_03.tmx` : Salle des Trois Sceaux (arc, bombes, lanterne ; la grande clé)

Intention : **l'énigme finale, sans ennemi**, qui rejoue les trois dons. Au centre, une petite chambre scellée par une grille contient le grand coffre (la **grande clé**). La grille s'ouvre quand les **trois interrupteurs** de même `cible` sont actifs :

| Sceau rappelé | Interrupteur | Où | Ce qu'il faut |
| --- | --- | --- | --- |
| Racines (arc) | cible `chateau_interrupteur_01` (`mode`=`fleche`, `symbole`=`racine`) | extrémité ouest de la salle, dans l'axe de la ligne 5 | une flèche (tir dégagé, 1 à 6 cases) |
| Montagne (bombes) | levier `chateau_interrupteur_02` (`mode`=`epee`) | cellule fermée à l'est, derrière le mur fissuré `chateau_mur_02` | une bombe, puis un coup d'épée |
| Lac (lanterne) | levier `chateau_interrupteur_03` (`mode`=`epee`) | alcôve sud-ouest, derrière le mur à rune `chateau_porte_04` | la lanterne (à moins de 64 px pendant 0,8 s), puis un coup d'épée |

Les trois sont visibles dès l'entrée : une cible gravée, une fissure, une rune qui brille. Ordre libre. Le sol a trois petits symboles (décor) qui rappellent le sceau de chaque région. Si Brann sort de la salle avant d'avoir fini, les interrupteurs reviennent à zéro (l'état d'un groupe n'est pas sauvegardé) mais le mur fissuré et le mur à rune restent ouverts : il ne reste qu'un tir et deux coups d'épée à refaire.

<!-- salle_03 -->
```text
#########X##########
#.......Y..Y.......#
#........P......####
#.......####....#..#
#.......#C##....#..#
#S......#I##....F.l#
#...............#..#
###ZZ###........#..#
#......#.P......####
#..l...#...........#
#########X##########
```

Objets Tiled :

- `Sortie` (288,0,32,32) (sans porte) : `cible_carte`=`res://scenes/rooms/chateau_salle_04_room.tscn`, `cible_spawn`=`depuis_sud`
- `Sortie` (288,320,32,32) : `cible_carte`=`res://scenes/rooms/chateau_salle_02_room.tscn`, `cible_spawn`=`depuis_nord`
- `Spawn` points (304,272) `depuis_sud` et (304,80) `depuis_nord`
- `Porte` (288,160,32,32) [grille intérieure] : `id`=`chateau_porte_03`, `type`=`interrupteur`
- `Coffre` point (304,144) : `id`=`chateau_coffre_01`, `contenu`=`grande_cle`, `important`=`true`
- `Interrupteur` point (48,176) : `id`=`chateau_interrupteur_01`, `cible`=`chateau_porte_03`, `mode`=`fleche`, `symbole`=`racine`
- `MurFissure` (512,160,32,32) : `id`=`chateau_mur_02`, `apparence`=`mur`
- `Interrupteur` point (592,176) : `id`=`chateau_interrupteur_02`, `cible`=`chateau_porte_03`, `mode`=`epee`
- `Porte` (96,224,64,32) : `id`=`chateau_porte_04`, `type`=`lanterne`, `apparence`=`mur_rune`
- `Interrupteur` point (112,304) : `id`=`chateau_interrupteur_03`, `cible`=`chateau_porte_03`, `mode`=`epee`
- `Torche` (brasero) points (272,48), (368,48) : `chateau_brasero_03`, `04`
- Rectangle `indice_trois_sceaux` (96,160,448,64) : clé `INDICE_CHATEAU_TROIS`

### 4.7 `salle_04.tmx` : Antichambre

Intention : **repos avant le combat**. Statue du corbeau (sauvegarde et soin) près de l'arrivée, deux braseros, un paquet de flèches et un paquet de bombes posés au sol (ramassables uniques : le ravitaillement supplémentaire pendant le combat est prévu dans l'arène, section 6.5). La porte du nord est à grande clé, avec le symbole de l'Œil.

<!-- salle_04 -->
```text
#########G##########
#..................#
#....Y...P....Y....#
#..................#
#..................#
#..m............b..#
#..................#
#..................#
#........P..R......#
#..................#
#########X##########
```

Objets Tiled :

- `Sortie` (288,0,32,32) + `Porte` `chateau_porte_05` (`grande_cle`) ; `cible_carte`=`res://scenes/rooms/chateau_salle_boss_room.tscn`, `cible_spawn`=`depuis_sud`
- `Sortie` (288,320,32,32) : `cible_carte`=`res://scenes/rooms/chateau_salle_03_room.tscn`, `cible_spawn`=`depuis_nord`
- `Spawn` points (304,272) `depuis_sud` et (304,80) `depuis_nord`
- `StatueCorbeau` point (400,272) : `id`=`chateau_statue_antichambre`
- `Ramassable` point (112,176) : `id`=`chateau_fleches_01`, `contenu`=paquet de flèches (à créer ou à confirmer, voir 10.3)
- `Ramassable` point (528,176) : `id`=`chateau_bombes_01`, `contenu`=`bombes_paquet`
- `Torche` (brasero) points (176,80), (464,80) : `chateau_brasero_05`, `06`
- Rectangle `indice_antichambre` (224,64,192,64) : clé `INDICE_CHATEAU_ANTICHAMBRE`

### 4.8 `salle_boss.tmx` : l'arène de Corvan (20×22)

Intention : une arène **ouverte** (deux écrans en hauteur, caméra qui suit), quatre piliers 2×2 qui font abri, quatre braseros, un cercle des sceaux gravé au centre (décor). Corvan est au nord ; l'arrivée est au sud, loin de lui. Les Marqueurs servent aux ravitaillements, aux positions de l'Œil et aux cinématiques.

Propriétés : `Zone`=`chateau`, pas de `camera` (suit Brann).

<!-- salle_boss -->
```text
####################
#..................#
#..Y.....3......Y..#
#..................#
#..1.....g......2..#
#..................#
#..................#
#..................#
#...OO........OO...#
#...OO........OO...#
#..................#
#.m......h.......m.#
#..................#
#...OO........OO...#
#...OO........OO...#
#..................#
#.b......h.......b.#
#..................#
#..................#
#.....Y..P...Y.....#
#..................#
#########G##########
```

Objets Tiled :

- `Sortie` (288,672,32,32) + `Porte` `chateau_porte_05` (`grande_cle`, se verrouille pendant le combat : `LockForEncounter`) ; `cible_carte`=`res://scenes/rooms/chateau_salle_04_room.tscn`, `cible_spawn`=`depuis_nord`
- `Spawn` point (304,624) : `id`=`depuis_sud`
- Point nommé `boss_corvan` (304,144) (scène `scenes/enemies/boss/corvan.tscn`, id `chateau_boss_corvan`)
- 4 rectangles `pilier` (64×64) : (128,256), (448,256), (128,416), (448,416)
- `Marqueur` : `corvan_fleches_1` (80,368), `corvan_fleches_2` (560,368), `corvan_bombes_1` (80,528), `corvan_bombes_2` (560,528), `corvan_coeur_1` (304,368), `corvan_coeur_2` (304,528) (`m`, `b`, `h` du dessin)
- `Marqueur` : `morvath_oeil_1` (112,144), `morvath_oeil_2` (528,144), `morvath_oeil_3` (304,80)
- `Marqueur` : `corvan_defi` (304,144) (là où Corvan parle), `corvan_exil` (304,656) (là où il disparaît, devant la porte)
- `Torche` (brasero) points (112,80), (528,80), (208,624), (432,624) : `chateau_brasero_07` à `10`
- `Scenario` point (304,560) : `cinematique`=`chateau_corvan_defi`, `si`=`corvan_absorbe_sceau`, `sauf`=`corvan_defie`
- Pas de `Scenario` de victoire : le boss lance lui-même `chateau_corvan_vaincu` (voir 7). `Room.VictoryExitScene` **vide** (la cinématique fait `aller_a`).

## 5. Ennemis

Dégâts : « 1 cœur ½ au château » (roadmap) s'applique aux **coups directs** (contact et coups du Chevalier, marteau de Corvan). Les attaques à distance et d'ambiance (orbes, ronces, rochers, flaques) valent **1 cœur** ou moins : l'enfant ne perd jamais plus d'un cœur et demi d'un coup. L'option Facile (dégâts divisés par 2) s'applique partout.

### 5.1 Chevalier corrompu (`chevalier_corrompu`, nouveau script `ChevalierEnemy`)

Chasseur à bouclier, sur le modèle du Mineur maudit (bouclier de face, bombe qui renverse). Taille 32×32, armure noire avec une tache de corruption violette sur le plastron (lisible), le dos nu et plus clair.

| Réglage | Valeur proposée |
| --- | --- |
| PV | 4 (soit 2 coups d'épée trempée) |
| Rôde | marche lente (36 px/s) autour de son point ; ne voit Brann qu'à moins de 160 px avec ligne dégagée |
| Poursuite | 64 px/s (plus lent que Brann) ; garde le bouclier vers Brann (`BlockCosine` 0,5, rotation lente : après 0,6 s, comme le Mineur) |
| Attaque en série | à moins de 40 px : annonce 0,6 s (épée levée, lueur rouge), puis **2 coups** espacés de 0,45 s ; dégâts 1 cœur ½ (invincibilité de Brann entre les coups : un seul coup touche s'il reste immobile) |
| Fenêtre de coup | **récupération 1,2 s** après la série, bouclier baissé : vulnérable de partout ; vulnérable aussi de côté et de dos en permanence |
| Flèches | bloquées de face (`Blocked`, flèche détruite), normales de côté et de dos |
| Bombe | `destructible_bombe` : le fait tomber 4 s (vulnérable partout), 0,3 s d'immunité au souffle, comme le Mineur |
| Butin | cœur, rubis ; flèches et bombes garanties sous les seuils existants |
| Variante rouge | **non utilisée** (3 cœurs par coup : trop dur pour l'enfant, décision 6) |

### 5.2 Œil de Morvath (`oeil_morvath`, nouveau script `EyeSentryEnemy`)

Sentinelle murale, immobile, 32×32 ; un œil doré dans un cadre de pierre (le symbole de Morvath, repris du boss). Une flèche suffit ; un coup d'épée aussi, quand on peut l'atteindre (cour).

| Réglage | Valeur proposée |
| --- | --- |
| PV | 1 |
| Éveil | paupière fermée tant que Brann est à plus de 8 cases ou hors ligne de vue ; en dessous, elle s'ouvre (0,8 s, iris qui brille : annonce) |
| Tir | un orbe sombre lent (90 px/s) dans la direction de Brann au moment du tir, un tir toutes les 2,5 s, dégâts **1 cœur** ; l'orbe disparaît sur un mur ou un pilier ; il ne se réfléchit pas |
| Position | dans une case de mur (niche) ; derrière une fosse de ronces dans la salle 01 (l'épée n'y arrive pas) |
| Mort | éclat doré, petit son ; compte comme ennemi pour une `Porte` `ennemis` |
| Bombe | une explosion à portée le détruit aussi |
| Variante rouge | non utilisée |

### 5.3 Autres ennemis et variantes rouges

Route : un **Ronceau rouge** et un **Sanglier noirci rouge** (contact 1 cœur), plus deux Cailloux rampants normaux. Grotte : trois Ombres noyées **normales** (la rouge ferait 2 cœurs au contact). Il n'y a **aucun** Crabe, Têtard, Chauve-souris ni Mineur au château : le joueur combine les mécaniques sans refaire les anciens combats. Règle retenue : aucune variante rouge qui retire plus de 1 cœur ½ au contact.

## 6. Le combat final : Corvan, puis Morvath

Scène `scenes/enemies/boss/corvan.tscn` (sous-classe de `Boss`, id `chateau_boss_corvan`, script `CorvanBoss`), corps en couche de collision 3 (comme Gorm et Ondine : ne bloque ni Brann ni les flèches, s'arrête sur murs et piliers). Sprite de boss 64×64 (phase 1) puis 96×96 (phase 2). Musique « Combat final ». Barre de vie du boss (`Hud.ShowBossBar`). Les PV sont en « coups d'épée de base » (l'épée trempée ×2 les divise par deux : les valeurs sont à régler avec `SwordRules`).

### 6.1 Vue d'ensemble

| Partie | Qui | Ce qu'il faut faire | Durée |
| --- | --- | --- | --- |
| Défi | Corvan | dialogue, la porte se verrouille | 20 s |
| Phase 1 | Corvan au marteau, 8 PV | esquiver le cercle d'ombre, frapper quand le marteau est coincé | 1 à 1,5 min |
| Transition | Morvath prend le dessus | cinématique, 2 petits cœurs, ravitaillement | 15 s |
| Phase 2, manche 1 | couche de **ronces** | 3 flèches sur les bulbes, puis frapper | 50 s |
| Phase 2, manche 2 | couche de **pierre** | 2 bombes, puis frapper | 50 s |
| Phase 2, manche 3 | couche d'**eau** | la lanterne révèle les 3 bulles, les frapper, puis frapper | 50 s |
| Finale | l'Œil de Morvath se détache | une flèche ou un coup d'épée | 20 s |
| Victoire | Corvan vieil homme | cinématique de fin | voir 7 |

L'ordre des manches est **toujours le même** (arc, bombes, lanterne : l'ordre dans lequel Brann a gagné ses objets). Une icône de l'objet à utiliser flotte au-dessus du boss pendant toute la manche (flèche, bombe, lanterne) et un bandeau (`BOSS_CORVAN_CONSEIL_n`) l'annonce à la première fois.

### 6.2 Phase 1 : Corvan, le marteau (8 PV)

Cycle de 6 à 7 s :
1. Corvan marche vers Brann (40 px/s) pendant 2,5 s au plus, sans le toucher (contact : ½ cœur).
2. Quand Brann est à moins de 72 px, ou après 2,5 s : **annonce 1,2 s** (× `PuzzleTimeMultiplier`, plafonné à ×2) : le marteau se lève au-dessus de sa tête et un **cercle d'ombre** (rayon 56 px) se dessine au sol à l'endroit où se trouvait Brann ; le cercle se remplit, ne suit plus Brann.
3. **Coup** : poussière, dégâts **1 cœur ½** à qui est dans le cercle.
4. **Marteau coincé 2,5 s** : Corvan est penché, il tire sur le manche ; vulnérable partout. C'est la fenêtre de 2 à 4 coups d'épée.
5. À mi-vie : deux cercles d'ombre côte à côte (une case d'écart) au lieu d'un, jamais plus.

Brann peut aussi tirer à l'arc (dégâts de flèche) mais n'y est pas poussé. Aucune attaque n'est sans annonce.

### 6.3 Transition : Morvath prend le dessus

Cinématique `chateau_morvath_prend` (lancée par le boss à 0 PV) : le marteau glisse, Corvan tombe à genoux, une ombre à l'œil doré sort du sol et l'enveloppe ; la teinte devient plus sombre ; deux petits cœurs apparaissent aux Marqueurs `corvan_coeur_1/2` ; une fois la scène finie, la vie du boss est remplie à 9 PV (3 manches de 3 PV), la musique change.

### 6.4 Phase 2 : Corvan-Morvath, les trois couches

Le boss est agrandi (96×96) et couvert, tour à tour, d'une couche de corruption. **Tant qu'une couche est présente, l'épée ne lui fait rien** (coup « `Blocked` »). Dans chaque manche :

| Manche | Couche (HurtBox) | Contre | Attaque d'ambiance (une à la fois, annoncée 1,5 s × multiplicateur) | Dégâts |
| --- | --- | --- | --- | --- |
| 1 | **Ronces** : 3 bulbes noirs sur ses bras | **l'arc** : 1 flèche par bulbe (3 flèches) | des pointes sortent du sol en une ligne (colonne ou rangée) depuis un pilier : monticule sombre 1,5 s, pointes 1 s | 1 cœur |
| 2 | **Pierre** : plastron de roche | **les bombes** : 2 explosions à moins de 3 cases (`IBombDestructible`, comme Gorm) | rochers qui tombent (`FallingRock` existant : ombre, puis chute), jamais plus de 3 à la fois | 1 cœur |
| 3 | **Eau** : 3 bulles d'eau noire qui flottent autour de lui | **la lanterne** : les bulles sont invisibles et mobiles hors de la lumière, figées et visibles dans le cercle de la lanterne (comme l'Ombre noyée) ; chacune se frappe à l'épée (1 coup) | anneaux d'ondes (comme Ondine), puis flaque 1 s | ½ cœur |

Quand la couche est brisée : **Corvan-Morvath est étourdi 4 s** (× multiplicateur, plafonné à ×2), vulnérable à l'épée partout ; il a 3 PV par manche. Deux petits cœurs tombent. À la fin de la manche, l'étourdissement se termine, la couche suivante apparaît (annonce 2 s). Pendant l'annonce et l'étourdissement, aucune attaque.

### 6.5 Finale : l'Œil de Morvath

Après la manche 3, l'Œil doré se détache de Corvan (qui s'effondre, inoffensif) et flotte entre les trois Marqueurs `morvath_oeil_1/2/3`. À chaque déplacement, un anneau doré s'affiche 1 s à l'arrivée, puis l'Œil reste **2,5 s** immobile (vulnérable) et tire un orbe lent (1 cœur) toutes les 3 s. Il a **2 PV** : 2 flèches, ou 2 coups d'épée s'il passe près de Brann. À sa mort : victoire (`MarkCollected`, `BossDefeated`, sauvegarde automatique), cinématique de fin.

### 6.6 Faisable par un enfant de 5 ans aidé

- **Chaque erreur coûte au plus 1 cœur ½**, la plupart du temps ½ ou 1 ; l'option Facile divise par 2.
- **Aucun chronomètre.** Les annonces, l'étourdissement et l'écoute de l'Œil sont multipliés par `PuzzleTimeMultiplier` (×1, ×2, ou « illimité » = ×2 plafonné, comme Ondine).
- **Une seule chose à la fois** : jamais deux attaques en même temps, jamais d'attaque sans annonce visible.
- **L'icône de l'objet à utiliser** est toujours au-dessus du boss ; la couche à briser clignote.
- **Ravitaillement** : si Brann a moins de 10 flèches, des paquets apparaissent aux Marqueurs `corvan_fleches_1/2` ; moins de 3 bombes, aux Marqueurs `corvan_bombes_1/2` (même principe que Gorm) ; les petits cœurs aux Marqueurs `corvan_coeur_1/2` à chaque transition. Les piliers font abri.
- **Pas de piège** : aucun trou dans l'arène, aucun bloc.
- **Reprise** après un game over : l'arène est rechargée en phase 1 ; recommandation : Brann repart de la statue de l'antichambre (`depuis_nord` de la salle 04) avec toute sa vie, et non avec 3 cœurs (question au développeur, 10.3).

## 7. La fin : cinématiques, drapeaux et textes

Toutes les cinématiques sont `passable` (maintenir « pause » 1 s les passe et applique leurs effets durables d'un coup). Pas de nouvelle action de cinématique, sauf pour `animer` de la forge si besoin (10.3).

### 7.1 Tableau

| Id | Déclencheur | `si` / `sauf` | `drapeau_fin` | Résumé |
| --- | --- | --- | --- | --- |
| `lac_retour_eclipse` | **existe** : `Scenario` dans `lac_room` | `si` `corvan_absorbe_sceau`, `sauf` `lac_eclipse_vu` | `lac_eclipse_vu` | Éclipse, caméra sur le château, « C'est là qu'il m'attend. » |
| `chateau_cour_voix` | `Scenario` point dans `chateau` | `si` `corvan_absorbe_sceau`, `sauf` `chateau_cour_vu` | `chateau_cour_vu` | La voix de Corvan souffle la poterne |
| `chateau_corvan_defi` | `Scenario` point dans `salle_boss` | `si` `corvan_absorbe_sceau`, `sauf` `corvan_defie` | `corvan_defie` | Dernier dialogue ; le combat démarre ensuite |
| `chateau_morvath_prend` | lancée par `CorvanBoss` à 0 PV de la phase 1 | — | `morvath_eveille` | Morvath prend le dessus |
| `chateau_corvan_vaincu` | lancée par `CorvanBoss` à la mort de l'Œil | — | **`morvath_vaincu`** (étape 4) | Corvan redevient un vieil homme et part en exil, puis `aller_a` la forge |
| `forge_sceau_unique` | `Scenario` point dans `forge_room` | `si` `morvath_vaincu`, `sauf` `sceau_unique` | `sceau_unique` | Brann forge le sceau unique |
| `village_fete` | `Scenario` point dans `village_room` (à l'arrivée sur la place) | `si` `sceau_unique`, `sauf` `fete_vue` | `fete_vue` | Toast, regard vers l'est, puis `aller_a` le générique |

Le drapeau `jeu_termine` est posé par la dernière étape de `village_fete` (action `drapeau`), avant `sauvegarder`.

**Pourquoi `morvath_vaincu` est posé à la fin de `chateau_corvan_vaincu`** : c'est le `drapeau_fin`, donc posé même si le joueur passe la scène (les effets durables sont appliqués d'un coup). L'étape d'histoire devient 4 à ce moment, la `Room` de la forge et du village se chargent ensuite avec les objets d'étape 4 (feu de forge allumé, guirlandes, PNJ de la fête).

### 7.2 Étapes de chaque cinématique

**`chateau_cour_voix`** : `camera` vers `chateau_portail` (1,5 s) - `attendre` 0,5 - `dialogue` Corvan (voix, boîte sans portrait) `DLG_CH_COUR_1`, `DLG_CH_COUR_2` - `camera` vers Brann (1,2 s).

**`chateau_corvan_defi`** : la porte se verrouille (`LockForEncounter`) - `regarder` Brann vers `corvan_defi` - `dialogue` `DLG_CH_DEFI_1` à `4` (Corvan, Brann, Corvan, Corvan) - `musique` « Combat final » - fin : le combat commence (le boss est inactif tant que la cinématique joue).

**`chateau_morvath_prend`** : `secousse` - `son` - `animer` Corvan à genoux - `apparaitre` l'Œil et l'ombre - `teinte` plus sombre (2 s) - `dialogue` `DLG_CH_MORVATH_1`, `2` (Morvath), `3` (Corvan) - `apparaitre ramassable` 2 petits cœurs aux Marqueurs `corvan_coeur_1/2` - `drapeau` `morvath_eveille`.

**`chateau_corvan_vaincu`** : `son` éclat doré - `secousse` - `disparaitre` l'Œil - `teinte` revient du violet au jour (3 s : l'éclipse se termine) - la fumée noire est aspirée par les trois sceaux de Brann (`son` sceau) - `animer` Corvan (sprite `corvan_vieux`, de dos) - `dialogue` `DLG_CH_EXIL_1` à `7` - Corvan marche jusqu'au Marqueur `corvan_exil` (`deplacer`) - `disparaitre` - `dialogue` Brann `DLG_CH_EXIL_8` - `drapeau` `corvan_exil` - `sauvegarder` - `fondu` noir - `aller_a` `forge_room` / `depuis_chateau`. Le `drapeau_fin` `morvath_vaincu` est posé à la fin (ou à la fin du passage).

**`forge_sceau_unique`** : `fondu` d'entrée (noir vers clair, 1,5 s) - `teinte` normal - `musique` « Fin et générique » arrangement calme - `dialogue` Brann `DLG_FORGE_FIN_1` - `animer` Brann (3 coups de marteau, `son` forge, `secousse` légère) - `son` sceau - `donner` `sceau_unique` (objet de quête) - `drapeau` `sceau_unique` - `apparaitre` Pip à la porte - `dialogue` `DLG_FORGE_FIN_2`, `3` - `sauvegarder`.

**`village_fete`** : `teinte` normal - `musique` « Fin et générique » - `camera` sur `fete_place` - `dialogue` `DLG_FETE_1` (Hulda), `DLG_FETE_2` (Pip), `DLG_FETE_3` (Isolde) - `regarder` Brann vers `fete_route` (la route de l'est), `camera` vers `fete_route` (2 s) - `dialogue` Brann `DLG_FETE_4` - `fondu` noir - `drapeau` `jeu_termine` - `sauvegarder` - `aller_a` `scenes/ui/generique.tscn`.

### 7.3 Textes proposés (français ; l'anglais est à écrire à l'intégration)

Les noms de locuteur utilisent les clés existantes `PNJ_BRANN`, `PNJ_CORVAN` ; nouvelles : `PNJ_MORVATH` (« Morvath »), `PNJ_VOIX` (« Une voix », pour `chateau_cour_voix`, si on préfère ne pas nommer Corvan). Phrases courtes (lecture à voix haute et jeune lecteur).

| Clé | Texte |
| --- | --- |
| `DLG_CH_COUR_1` | Le grand portail est scellé, petit. Passe par la poterne, comme toujours. |
| `DLG_CH_COUR_2` | Tu as toujours aimé les murs qui sonnent creux. |
| `DLG_CH_DEFI_1` | Tu as rapporté les trois sceaux, Brann. Ils sont tous ouverts, maintenant. |
| `DLG_CH_DEFI_2` (Brann) | Maître... revenez à la forge. Je vous en prie. |
| `DLG_CH_DEFI_3` | La forge est froide, petit. Mes mains ne savent plus rien faire. |
| `DLG_CH_DEFI_4` | Alors je vais te montrer ce qu'elles savent encore. |
| `DLG_CH_MORVATH_1` (Morvath) | Assez joué, vieil homme. Ce corps est à moi. |
| `DLG_CH_MORVATH_2` (Corvan) | Non... Brann... Je ne voulais pas... |
| `DLG_CH_MORVATH_3` (Morvath) | Mille ans dans le noir. Tu vas m'amuser, petit forgeron. |
| `DLG_CH_EXIL_1` (Corvan, voix faible) | Brann... c'est toi ? Mes yeux n'y voient plus rien. |
| `DLG_CH_EXIL_2` (Brann) | Oui, Maître. C'est fini. |
| `DLG_CH_EXIL_3` | J'avais si peur de vieillir. Et regarde ce que j'ai fait. |
| `DLG_CH_EXIL_4` (Brann) | Vous m'avez appris à forger. Ça, vous ne l'avez pas gâché. |
| `DLG_CH_EXIL_5` | Les sceaux sont à toi, maintenant. Forge-les en un seul. Un qui ne s'ouvrira plus. |
| `DLG_CH_EXIL_6` | Je ne peux plus rester à Brumeval. Je partirai loin, là où personne ne me connaît. |
| `DLG_CH_EXIL_7` | Prends soin de la forge, Maître Brann. |
| `DLG_CH_EXIL_8` (Brann) | Je garderai le feu allumé. |
| `DLG_FORGE_FIN_1` (Brann) | Un seul sceau. Solide, cette fois. |
| `DLG_FORGE_FIN_2` (Pip) | Brann ! Tout le monde t'attend sur la place ! |
| `DLG_FORGE_FIN_3` (Brann) | J'arrive. |
| `DLG_FETE_1` (Hulda) | Maître Brann ! À ta santé ! |
| `DLG_FETE_2` (Pip) | Je savais que tu gagnerais. J'ai même gardé une poule pour toi ! |
| `DLG_FETE_3` (Isolde) | J'écrirai ton nom dans les registres des gardiens. En lettres d'or. |
| `DLG_FETE_4` (Brann) | Prenez soin de vous, Maître. |
| `BOSS_CORVAN_NOM` | Corvan, le Forgeron |
| `BOSS_CORVAN_CONSEIL_1` | Son marteau est lent. Écarte-toi du cercle d'ombre, puis frappe ! |
| `BOSS_CORVAN_CONSEIL_2` | Les ronces craignent les flèches. Vise les bulbes ! |
| `BOSS_CORVAN_CONSEIL_3` | La pierre éclate sous les bombes ! |
| `BOSS_CORVAN_CONSEIL_4` | Dans l'eau noire, la lanterne montre où frapper. |
| `BOSS_CORVAN_CONSEIL_5` | L'Œil de Morvath ! Une flèche, vite ! |
| `INDICE_GROTTE_FALAISE` | Une grotte noire. Une rune brille sur le mur. |
| `INDICE_PASSAGE_SOMBRE` | Il fait sombre. Suis la lumière des braseros. |
| `INDICE_CHATEAU_PORTAIL` | Le portail est scellé par l'Œil de Morvath. |
| `INDICE_CHATEAU_TROIS` | Une flèche, une fissure, une rune. Trois sceaux, trois dons. |
| `INDICE_CHATEAU_ANTICHAMBRE` | La porte du fond attend la grande clé. |
| `OBJ_SCEAU_UNIQUE` | Le sceau de Brumeval |

**Dernières répliques des PNJ à l'étape 4** (dialogues JSON ordinaires, bloc `stage` 4, une réplique chacun ; clés `DLG_<PNJ>_4_n`, à vérifier avec les blocs déjà écrits) : Hulda « Un cœur tout neuf pour toi, Maître Brann. » (offerte une fois, `reward` d'un petit cœur, optionnel) ; Pip « Les poules ! Tu as retrouvé toutes les poules ? » (**garder** le bloc des poules et du quart de cœur : il ne doit pas disparaître avec la fête) ; Tobias « Plus de ronces dans mon bois. Merci, gamin. » ; Isolde « Les trois sceaux n'en font plus qu'un. Mille ans de plus. » ; Garrick « Pour une fois, le premier verre est gratuit. »

### 7.4 Générique

Scène `scenes/ui/generique.tscn` (nouvelle) : fond sombre étoilé et brume, le logo du corbeau et des trois cercles **qui deviennent un seul cercle** ; défilement vertical lent (≈ 60 s) ; sections « Un jeu de », « Programmation », « Graphismes », « Musique », « Level design », « Textes », « Tests », « Remerciements » (noms à fournir par l'utilisatrice) ; musique « Fin et générique » ; maintenir « pause » 1 s ou valider accélère ; à la fin, image fixe de l'enclume avec le corbeau et « Fin » ; retour à l'écran titre. Une partie « Continuer » charge la sauvegarde de la fête (village, étape 4, libre de se promener, de finir les secrets).

## 8. Étapes d'histoire : incohérences relevées dans `maps/overworld/plan.md` et correction proposée

Le code (`CLAUDE.md`) a `GameState.StoryStage` de **0 à 4**, dérivée : nombre de sceaux (max 3), ou 4 si `morvath_vaincu`. Le plan de l'overworld écrit six étapes (0 à 5). Équivalence :

| `overworld/plan.md` (§2.6, 2.7) | Code (`StoryStage`) | Sens |
| --- | --- | --- |
| 0 prologue et matin ; 1 libre, brume épaisse | **0** (aucun sceau) | début du jeu |
| 2 après le Temple | **1** (1 sceau) | brume en partie levée |
| 3 après la Mine | **2** | mineurs de retour, bombes en boutique |
| 4 après le Sanctuaire | **3** (3 sceaux) | village vide, éclipse |
| 5 épilogue | **4** (`morvath_vaincu`) | soleil, fête, forge allumée |

À corriger dans `maps/overworld/plan.md` (par l'utilisatrice, hors de mon territoire) :
1. §2.6 : les colonnes « Étapes » de Pip, Tobias, Hulda, Garrick, Isolde, villageois suivent la numérotation 0-5 ; passer à la numérotation code (par exemple `tobias` 2-3 devient 1-2, `pip` 5 devient 4, `isolde` « retrouve le nom à l'étape 4 » devient 3).
2. §2.7 : le tableau de brume a 6 lignes et §5 point 6 parle de 6 valeurs de `densite` ; le code en lit **5** (une par étape de 0 à 4). Fusionner les lignes 0 et 1.
3. §2.7 et §3.1 : fourneau « froid `etape_max` 4, allumé `etape_min` 5 » devient `etape_max` 3 / `etape_min` 4. Tronc du raccourci : « `etape_max` 1 » (disparaît à l'étape 2) devient `etape_max` 0 (il disparaît à l'étape 1).
4. §3.3 : l'étal « huile de lanterne (dès l'étape 4) » n'existe plus (décision du 2026-11-01, la lanterne est passive). Étals : flèches dès l'étape 1, bombes dès l'étape 2.
5. §5 : `Etal`, `comportement`, la liste des `Poule`, etc. sont dépassés par `CLAUDE.md` (`Article`, `errance`, `Poule` gérée) ; marquer la section 5 comme remplacée.
6. §3.6 et §1.1 : `passage_falaise` passe de 20×11 à 20×22 (ce document), toujours un intérieur ; la zone est `route`.
7. §1.2 et §2.4 : la route de l'est est décrite comme « cul-de-sac, grotte noire visible » ; il n'y avait pas de barrage précis : ce document en propose un (le mur à rune, 4.1). Le plan du Sanctuaire (§7.1) dit que `corvan_absorbe_sceau` « ouvre la route » : ici le barrage est la **lanterne** (visible dès l'étape 0), et le drapeau ne sert qu'aux cinématiques et à la teinte ; les deux coïncident dans la pratique (la lanterne est dans le Sanctuaire, juste avant le sceau).
8. Roadmap : « Option : un donjon final court si le temps le permet, sinon le boss du donjon 3 est le boss final » (phase 6) est résolue par ce plan ; « Dégâts infligés : ... 1 cœur ½ au château » est précisé en 5.

## 9. Vérification

### 9.1 Parcours et accessibilité

Script de vérification (bibliothèque standard seulement, non commité) appliqué aux aperçus ci-dessus : construction de la grille, parcours (BFS) depuis les `Spawn`, obstacles fermés tant que leur condition n'est pas remplie, lignes de tir de l'arc (portée 10 cases). Résultats :

```text
Structure : route 40x11 ; passage 20x22 ; cour 20x22 ; salles 01 à 04 20x11 ; boss 20x22 : OK (toutes les lignes ont la bonne longueur)
Apparitions : aucun ennemi à moins de 3 cases d'un Spawn : OK
route    : statue, mur à rune (approchable) : OK ; cases atteignables 202
passage  : mur à rune obligatoire (9,14)-(10,14) approchable ; depuis l'arrivée sud, le nord (Ombres, sortie) n'est PAS atteignable rune fermée, il l'est rune ouverte : OK
           plume (18,4) fermée tant que la rune (16,4)-(16,5) est fermée : OK ; Ombres atteignables mais jamais obligatoires
cour     : statue, Chevalier, mur fissuré (4,4) approchable ; 265 cases à 4 cases ou plus du mur pour reculer pendant la mèche
salle 01 : porte (9,0) approchable ; Œils en (3,0) et (16,0) : plus proche case atteignable à 3,2 cases (hors portée d'épée), 5 cases de tir chacun, à 5 à 9 cases (portée de l'arc : 10)
salle 02 : deux Chevaliers atteignables, porte (9,0) approchable
salle 03 : cible (1,5) : 11 cases de tir, 1 à 6 cases ; mur fissuré (16,5) et mur à rune (3,7)-(4,7) approchables ;
           leviers (18,5) et (3,9) fermés avant ouverture, atteignables après ; coffre (9,4) fermé avant la grille ;
           levier à 2,0 cases d'une Porte ou d'un mur fissuré (règle : pas à côté) : OK
salle 04 : statue, paquets, porte (9,0) approchables
boss     : tous les Marqueurs de ravitaillement atteignables, porte approchable
```

### 9.2 Progression, objets, clés, retours

| Obstacle | Exige | Obtenu avant ? |
| --- | --- | --- |
| Mur à rune `route_porte_01` (route) | lanterne | oui : Sanctuaire |
| Mur à rune `route_porte_02` (grotte) | lanterne | oui |
| Mur fissuré `chateau_mur_01` (cour) | bombes | oui : Mine |
| Porte `chateau_porte_01` (salle 01) | arc (les Œils) | oui : Temple |
| Porte `chateau_porte_02` (salle 02) | épée | oui |
| Grille `chateau_porte_03` (salle 03) | arc + bombes + lanterne + épée | oui |
| Porte `chateau_porte_05` (antichambre) | grande clé de `chateau_coffre_01` | oui, juste avant, dans la salle 03 |
| Facultatifs : plume (`route_porte_03`) | lanterne | oui |

- **Clés** : 0 petite clé, 1 grande clé pour 1 porte. La grande clé est dans la salle 03, la porte dans la salle 04 : aucun ordre d'ouverture ne peut laisser le joueur sans clé.
- **Parcours sur l'état du joueur** (salle, objets possédés, murs ouverts, grande clé) : un seul chemin en chaîne ; chaque obstacle se franchit avec un objet que Brann a déjà et se trouve dans la salle de son déclencheur. Les ouvertures franchies sont mémorisées (`MarkCollected`) : portes « ennemis », grille, mur fissuré, murs à rune, grande clé. **Aucun état d'où la salle du boss soit hors de portée** ; en condamner une porte (obligatoires : route 01, grotte 02, cour 01, salle 01, 02, 03, 05) la rendrait inatteignable, ce qui est le fonctionnement attendu.
- **Munitions** : les Œils exigent 2 flèches, la salle 03 en demande 1, le combat 3 + 2 ; si Brann n'en a plus, tous les passages sont à deux sens : il revient à la cour (le Chevalier lâche des flèches et des bombes sous les seuils garantis, il réapparaît à chaque retour) ou au village (Garrick). **Pas de soft-lock par manque de munitions.**
- **Retours** : tous les passages sont à deux sens ; la statue de la cour et celle de l'antichambre sauvegardent. Aucun bloc poussable, aucun trou.
- **Après la victoire** : `aller_a` envoie Brann à la forge sans retour imposé ; la route, la grotte et le château restent ouverts (états mémorisés) : plume et secrets de la zone restent faisables après le générique. Aucun objet obligatoire n'a de `etape_max`. Vérifier que les blocs de dialogue de Pip pour les poules existent encore à l'étape 4.
- **Non vérifié** (dépend du code et des tuiles) : l'import Godot (aucun `.tmx` n'existe), la visibilité réelle des runes dans la grotte, le comportement du boss.

## 10. Besoins

### 10.1 Graphiste (le plan du tileset d'abord, comme d'habitude)

Deux tilesets (même numérotation pour ce que le code reconnaît : voir 10.3) avec leur plan `art/tilesets/<nom>_plan.md` :

| Tileset | Contenu |
| --- | --- |
| `route_chateau` (route et cour) | route pavée de l'est, falaise sombre (face et dessus), rochers (`O`), bouche de grotte avec cadre de pierre (alcôve de la `Sortie`), façade du château (murs, créneaux, niche d'Œil, grand portail scellé 2×3 avec symbole de l'Œil), poterne et sa version fissurée / ouverte (paire fermée-ouverte, voir 10.3), dalles de la cour, statues de chevaliers (colonnes `O`), herbe d'éclipse, grotte (sol, murs de roche, stalagmites, mur à rune porte `art/puzzles/porte_mur_rune.png` existante), braseros |
| `chateau` (intérieur) | pierre sombre et violette, tapis, armures et statues, piliers et colonnes, fosse de ronces (ravin, voir 10.3), mur fissuré (fermé et ouvert), cadres de porte (haut, bas, gauche, droite), sol de l'arène avec cercle des sceaux (décor), trois symboles au sol (arc, bombe, lanterne), socle |

Images de portes par zone : `art/puzzles/porte_<type>_chateau.png` (facultatif) ; grille de la salle 03 ; porte à grande clé avec l'Œil.

### 10.2 Sprites

| Sprite | Détail |
| --- | --- |
| `chevalier_corrompu` 32×32 | marche 4 directions, bouclier levé, annonce, 2 coups, récupération (bouclier baissé), renversé ; dos clair lisible |
| `oeil_morvath` 32×32 | paupière fermée, ouverture, tir, éclat doré ; cadre de pierre |
| Orbe sombre (projectile), éclat | animations courtes |
| `corvan` boss 64×64 | marche, marteau levé, coup, marteau coincé, à genoux ; humain voûté, même tablier |
| `corvan_corrompu` 96×96 + trois calques `ronces` (3 bulbes), `pierre`, `eau` | silhouette de Corvan couverte de corruption ; les calques clignotent, se brisent |
| Bulle d'eau noire (3 images), cercle d'ombre du marteau, pointes de ronces (monticule puis pointes), anneau d'ondes (existe pour Ondine) | effets |
| Œil détaché 32×32 (flottant) | idle, déplacement, tir |
| `corvan_vieux` 32×32 | repos, marche (de face, de dos), sans barbe sombre, cheveux blancs |
| Icônes au-dessus du boss | flèche, bombe, lanterne |
| `sceau_unique` (icône d'objet, ~32×32) | les trois cercles fondus en un |
| Brann qui forge | 4 images (marteau levé / frappe) |
| Générique | fond, logo animé (trois cercles vers un), image finale (enclume et corbeau) |

### 10.3 Nouvelles conventions et code (à signaler, à valider avant usage)

**Aucune nouvelle classe Tiled.** Réutilisés : `Spawn`, `Sortie`, `Porte` (`ennemis`, `interrupteur`, `grande_cle`, `lanterne` / `mur_rune`), `Interrupteur` (`fleche` + `racine`, `epee`), `MurFissure`, `Coffre`, `Ramassable`, `StatueCorbeau`, `Torche`, `Ennemi`, `Marqueur`, `Scenario`, rectangles `indice_*`, `boss_corvan`, `pilier`. Valeurs nouvelles : `Ennemi.type` = `chevalier_corrompu`, `oeil_morvath`.

Points à confirmer ou à coder (développeur) :

1. **`Porte` `mur_rune` avec une `Sortie` une case derrière** (4.1) : suppose que la `Sortie` n'est ignorée que si elle partage le rectangle d'une `Porte`. À vérifier.
2. **`Ennemi` dans une case de mur** (Œils) : le point est le centre de la case de mur ; son corps ne doit pas être poussé hors de la niche.
3. **Ravin (fossé de ronces) dans le tileset `chateau`** : `TileFeatures` reconnaît le ravin par id pour `village` et `montagne` (80-95) ; ajouter `chateau` (mêmes ids 80-95 réservés). Même chose pour `TileRules` : paire fermée-ouverte des murs fissurés (poterne dans `route_chateau`, salle 03 dans `chateau`) et pour la tuile de mur à rune si elle en a une.
4. **Scripts** : `ChevalierEnemy`, `EyeSentryEnemy` (+ projectile d'orbe), `CorvanBoss` (phase 1, transition, manches, finale), calques de couche à `HurtBox` (invincible tant que la couche est là, émet `Blocked`), bulles d'eau (réutiliser la logique de l'Ombre noyée), lignes de ronces, `FallingRock` existant, `IBombDestructible` pour la couche de pierre (comme Gorm), icône d'objet au-dessus du boss, ravitaillement par seuils (flèches < 10, bombes < 3).
5. **Le boss lance des cinématiques** (`chateau_morvath_prend` à la transition, `chateau_corvan_vaincu` à la victoire) : `CinematicPlayer.Play(id)` appelé par le code, le boss reste inactif pendant ; `drapeau_fin` `morvath_vaincu` ; `VictoryExitScene` vide ; pas de réceptacle ni de sceau ; `BossDefeated` + sauvegarde auto. `aller_a` doit pouvoir viser `forge_room` avec un spawn `depuis_chateau` (à ajouter dans `forge.tmx`) ; le `Scenario` de la forge doit attendre la fin du fondu.
6. **Teinte d'éclipse par étape** : `Room.StageTint` : à l'étape 3, `BaseTint` = éclipse pour les zones `lac`, `village`, `route`, `chateau`, `foret_sud`… (liste à fixer) ; à l'étape 4, retour à la lumière. Évite une propriété de carte de plus. La cinématique `teinte normal` revient déjà à `BaseTint`.
7. **Actions de cinématique** : `animer` pour Brann (marteau) et Corvan (genoux, de dos) ; `donner` un objet de quête (`sceau_unique.tres`, `KeyItem`) ; `apparaitre ramassable` pour les petits cœurs (existe). Vérifier que `aller_a` accepte une scène d'interface (`generique.tscn`).
8. **Générique** : `scenes/ui/generique.tscn` et script (défilement, accélération, retour au titre), texte via `Tr()` et lecture à voix haute (`TextReader.Speak`) ; clés `GENERIQUE_*` à ajouter.
9. **Game over** : où reprend Brann après une défaite contre Corvan (recommandation : statue de l'antichambre, vie pleine).
10. **Sons** (`sfx.py` et `Sfx`) : marteau qui frappe, poussière, orbe, œil qui s'ouvre, ronces, bulle, éclat doré, forge. **Musiques** : « Combat final », « Fin et générique » (le plan musical de la roadmap les prévoit déjà).
11. **Textes** : toutes les clés de 7.3 dans `textes.csv` (français et anglais), puis un import (`--headless --import`) pour régénérer les `.translation`. Les clés `INDICE_*` lues à voix haute.
12. **Sauvegarde** : aucun nouvel état (drapeaux déjà sauvegardés ; `jeu_termine` est un drapeau). `GameState.StoryStage` passe à 4 via `morvath_vaincu`, déjà prévu.
13. **Carte du donjon** (menu pause) : facultatif ; sans propriétés `etage`/`carte_x`/`carte_y`, rien n'est à faire (décision 1).

Propositions pour les fichiers communs (à appliquer par l'utilisatrice) : `CLAUDE.md` : zones `route` et `chateau`, ennemis `chevalier_corrompu`, `oeil_morvath`, boss `corvan` (id `chateau_boss_corvan`), drapeaux `chateau_cour_vu`, `corvan_defie`, `morvath_eveille`, `morvath_vaincu`, `corvan_exil`, `sceau_unique`, `fete_vue`, `jeu_termine`, correction de l'équivalence des étapes (section 8). `docs/roadmap.md` : cocher « Séquence de fin et générique » et « donjon final court » une fois réalisés ; préciser « Château final : cour + 4 salles + arène » ; `passage_falaise` en 20×22.

## 11. Décisions pour l'utilisatrice

1. **Château complet (cour + 4 salles + arène, environ 20 minutes) ou version courte ?** La version courte supprime les salles 01 et 02 (Œils et Chevaliers) : la poterne mène directement à la salle des Trois Sceaux, puis l'antichambre et l'arène (cour + 2 salles + arène, environ 12 minutes). Recommandation : **complet**, parce que chaque objet a ainsi son dernier moment (l'arc contre les Œils, l'épée contre les Chevaliers) et que le rythme calme / combat / énigme / repos prépare bien le grand combat ; la version courte reste possible en retirant 01 et 02 sans toucher au reste (la poterne vise alors `salle_03`). Pas de carte ni de boussole dans le château (2 salles de plus ne le justifient pas).
2. **Où mettre la séquence de fin ?** Option A (recommandée) : tout s'enchaîne : combat, exil de Corvan, **forge du sceau unique**, **fête**, générique ; ensuite « Continuer » ramène au village (étape 4) pour finir les secrets. Option B : générique tout de suite après l'exil, la forge et la fête restant jouables ensuite au village. Recommandation : **A**, parce que la forge et la fête sont l'aboutissement du récit de Brann (« d'apprenti à maître ») et se jouent en 4 à 5 minutes.
3. **Le combat final** : phase 1 au marteau (8 PV, cercle d'ombre), 3 manches fixes (arc, bombes, lanterne) de 3 PV, l'Œil détaché en finale, aucune attaque sans annonce, ravitaillement aux Marqueurs, dégâts 1 cœur ½ au maximum. Recommandation : **oui, tel quel** ; on peut retirer la finale de l'Œil (victoire à la fin de la manche 3) si c'est jugé trop long.
4. **Barrage de la grotte** : un mur à rune visible dès le début de la partie sur la route de l'est, ouvert par la lanterne (et non par un drapeau d'histoire). Recommandation : **oui** : le blocage est visible avant d'être franchissable et la lanterne n'est obtenue qu'à la fin du Sanctuaire.
5. **Grotte sur deux écrans (20×22)** au lieu d'un (20×11), et teinte d'éclipse imposée par l'étape 3 dans le code (au lieu d'une propriété de carte). Recommandation : **oui** aux deux.
6. **Aucune variante rouge de Chevalier ni d'Œil**, et Corvan appelle Brann « Maître Brann » à la fin (premier « Maître » du jeu), sans autre signe de mort. Recommandation : **oui** : un Chevalier rouge ferait 3 cœurs par coup, trop pour l'enfant ; l'option Facile suffit pour le reste.

**Décisions validées le 2026-11-03** : les six recommandations sont acceptées.
1. Château complet : cour, salles 01 à 04, arène.
2. Fin tout enchaînée : combat, exil de Corvan, forge du sceau unique, fête, générique, puis « Continuer » au village (étape 4).
3. Combat final tel quel, avec la finale de l'Œil.
4. Grotte barrée par un mur à rune visible dès le début, ouvert par la lanterne.
5. Grotte sur deux écrans (20×22) ; teinte d'éclipse imposée par l'étape 3 dans le code.
6. Aucune variante rouge de Chevalier ni d'Œil ; Corvan appelle Brann « Maître Brann ». Après une défaite contre Corvan, reprise à la statue de l'antichambre, vie pleine.
