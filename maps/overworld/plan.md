# Plan de l'overworld et du village de Brumeval (phase 6, étape 1)

Document de conception. **Aucun `.tmx` de ce plan n'existe encore** : on attend la validation (section 8). Seul `foret_temple.tmx` existe ; il serait modifié à l'étape 2 (section 1.3). Les aperçus ASCII ont été vérifiés par un parcours (BFS) : toutes les portes, sorties, PNJ et poules du village sont atteignables depuis l'arrivée ouest, et les poches secrètes de la forêt le sont une fois le rocher ouvert ou les buissons coupés.

Conventions de tous les aperçus : une lettre par case de 32 px. Légende commune : `#` solide (arbre, falaise, mur), `.` sol libre, `X` Sortie, `P` Spawn, `D` porte de maison enterrable (Sortie), `d` porte de maison fermée (décor), `H` maison (toit et mur), `W` puits, `E` ennemi, `R` statue du corbeau, `F` mur fissuré, `L` tronc en travers, `b` buisson coupable, `o` poule, `t` Tobias, `i` Pip, `u` villageois, `s` cachette de Pip, `Q` quart de cœur, `Y` cible à l'arc, `r` rocher, `f` plume de corbeau, `x` vide noir (intérieurs).

## 1. Découpage de l'overworld en cartes

### 1.1 Une carte par zone, alignées sur la grille 5×4

L'overworld fait 5×4 écrans (100×44 cases). Chaque carte `.tmx` occupe un rectangle d'écrans entier ; la caméra suit Brann (`camera` = `suivre`). Origine = coin haut-gauche de la carte dans le monde, en cases.

| Fichier | Taille (cases) | Écrans (colonne, ligne) | Origine monde | Contenu |
| --- | --- | --- | --- | --- |
| `foret_temple.tmx` (existe) | 40×22 | (0,0) (1,0) (0,1) (1,1) | (0,0) | Forêt nord-ouest, Temple des Racines, rivière et pont, souche creuse |
| `foret_sud.tmx` | 20×11 | (0,2) | (0,22) | Sentier entre le village et la forêt, statue, plume, cible cachée |
| `village.tmx` | 40×11 | (1,2) (2,2) | (20,22) | Brumeval |
| `montagne.tmx` | 40×22 | (2,0) (3,0) (2,1) (3,1) | (40,0) | Ravin et pont-levis (écran sud-ouest), montagne, col et entrée de la Mine (écran sud-est) |
| `route_falaise.tmx` | 40×11 | (3,2) (4,2) | (60,22) | Route de l'est, falaise, grotte noire |
| `chateau.tmx` | 20×22 | (4,0) (4,1) | (80,0) | Cour et façade du château |
| `grotte_sw.tmx` | 20×11 | (0,3) | (0,33) | Cul-de-sac rocheux du sud-ouest, mur fissuré visible |
| `lac.tmx` | 80×11 | (1,3) (2,3) (3,3) (4,3) | (20,33) | Rive (éboulis), lac, ponton, Sanctuaire Englouti |

Total : 4+1+2+4+2+2+1+4 = **20 écrans**, soit forêt 5, village 2, montagne 4, lac et rives 5 (lac 4 + grotte du sud-ouest 1), route-falaise-château 4. Une zone du jeu (`Zone` de la `Room`) = un préfixe d'id : `foret`, `village`, `montagne`, `route`, `chateau`, `lac`. Chaque `.tmx` aura sa scène `scenes/rooms/<nom>_room.tscn`.

Propriétés de carte proposées (pour une future carte du monde, sans effet sur le jeu) : `monde_x`, `monde_y` (origine en écrans, ex. 1 et 2 pour le village).

**Pourquoi des cartes séparées** (et non une seule de 100×44) : l'état des PNJ, des brumes et des ennemis se recharge par zone, un fichier à la fois reste lisible dans Tiled, et le mécanisme existe déjà (Sortie/Spawn). **Règle de raccord** : toutes les cartes qui se touchent partagent la même ligne ou colonne d'ouverture (même numéro de case des deux côtés), et chaque traversée est un **passage de 2 cases** (jamais un bord entier), avec un seul Spawn par passage, centré, à 2 cases de la Sortie. Le reste du bord est fermé (arbres, falaise, eau profonde).

### 1.2 Raccords (Sortie / Spawn)

Les Sorties sont des rectangles `area` de 1 case d'épaisseur sur le bord, les Spawns sont posés à 2 cases à l'intérieur. Convention des ids : `depuis_<zone d'origine>` ; pour une deuxième liaison entre les mêmes zones : `depuis_<zone>_<lieu>`.

| Passage | Sortie (carte, x, y, l, h en px) | Spawn d'arrivée (carte, id, centre en px) |
| --- | --- | --- |
| Forêt (temple) vers forêt sud | `foret_temple` 192, 672, 64, 32 (cases 6-7, ligne 21) | `foret_sud` `depuis_foret_temple` (224, 80) |
| Forêt sud vers forêt (temple) | `foret_sud` 192, 0, 64, 32 | `foret_temple` `depuis_foret_sud` (224, 624) (c'est la position de l'actuel `depuis_village`) |
| Forêt sud vers village | `foret_sud` 608, 128, 32, 64 (colonne 19, lignes 4-5) | `village` `depuis_foret_sud` (80, 160) |
| Village vers forêt sud | `village` 0, 128, 32, 64 | `foret_sud` `depuis_village` (560, 160) |
| Forêt sud vers grotte SO | `foret_sud` 288, 320, 64, 32 (cases 9-10, ligne 10) | `grotte_sw` `depuis_foret_sud` (320, 80) |
| Grotte SO vers forêt sud | `grotte_sw` 288, 0, 64, 32 | `foret_sud` `depuis_grotte_sw` (320, 272) |
| Village vers montagne | `village` 1024, 0, 64, 32 (cases 32-33, ligne 0) | `montagne` `depuis_village` (416, 624) |
| Montagne vers village | `montagne` 384, 672, 64, 32 (cases 12-13, ligne 21) | `village` `depuis_montagne` (1056, 80) |
| Village vers route | `village` 1248, 128, 32, 64 (colonne 39) | `route_falaise` `depuis_village` (80, 160) |
| Route vers village | `route_falaise` 0, 128, 32, 64 | `village` `depuis_route` (1200, 160) |
| Village vers lac (rive) | `village` 608, 320, 64, 32 (cases 19-20, ligne 10) | `lac` `depuis_village` (640, 80) |
| Lac vers village | `lac` 608, 0, 64, 32 | `village` `depuis_lac` (640, 272) |
| Village vers forêt (raccourci de Tobias) | `village` 224, 0, 64, 32 (cases 7-8, ligne 0) | `foret_temple` `depuis_village_raccourci` (896, 624) |
| Forêt (raccourci) vers village | `foret_temple` 864, 672, 64, 32 (cases 27-28, ligne 21) | `village` `depuis_foret_raccourci` (256, 80) |

Passages **volontairement fermés** (falaise ou eau, pas de Sortie) : forêt est vers montagne, montagne sud vers route, montagne est vers château, grotte SO vers lac, route/falaise vers lac. Le château (`chateau.tmx`) s'atteint seulement par la grotte noire de la falaise : `route_falaise` > intérieur `passage_falaise` > `chateau` `depuis_passage_falaise`.

### 1.3 `foret_temple.tmx` : à garder tel quel, avec 4 retouches (étape 2)

`foret_temple.tmx` fait 40×22 = exactement 2×2 écrans : on l'**intègre sans l'étendre**, comme partie nord-ouest de la forêt. Le cinquième écran de forêt est `foret_sud.tmx` (écran (0,2)), car l'écran (1,2) est le village. Constats sur le fichier actuel :
- L'entrée du temple (Sortie `depuis_foret`) est en haut au centre (case 19,3), pas dans un coin ; la rivière coupe la carte en deux (lignes 10-14) avec un seul passage, le pont des cases 11-12.
- Le passage sud (cases 6-7, lignes 18-21) est **ouvert** dans le calque `Murs` : je n'y trouve **pas** les 2 buissons mentionnés. À vérifier dans Tiled avant l'étape 2.
- La souche creuse (tuile 78) est en (34,17), entourée de buissons ; son « secret » est un rubis rouge (`foret_rubis_secret_01`, en (34,18)), pas encore un quart de cœur.
- `TitleScreen.NewGameSpawnId` vaut `depuis_village` (spawn en (7,19)).

Retouches prévues : (1) Sortie vers `foret_sud` en bas (cases 6-7, ligne 21) et Spawn `depuis_foret_sud` ; on **garde** `depuis_village` jusqu'à ce que la nouvelle partie démarre dans la forge ; (2) ouverture du raccourci (cases 27-28, ligne 21) fermée par un `Porte` tronc (voir 5) ; (3) le contenu de la souche creuse devient le quart de cœur `foret_quart_coeur_souche` ; (4) option : deux buissons coupables en (6,19) et (7,19) si l'épée coupe les buissons à ce moment-là (sinon passage libre).

## 2. Le village de Brumeval (`village.tmx`, 40×11)

### 2.1 Idée de composition

Deux écrans côte à côte, l'ouest (colonnes 0-19) et l'est (20-39). Une rue horizontale (lignes 4-5) relie l'entrée ouest (forêt) à l'entrée est (route). Maisons au nord (lignes 1-3, portes ligne 3) et au sud (lignes 6-8, portes ligne 8, ouvertes sur un chemin ligne 9). Au centre, une **place** de 8 cases de large (colonnes 16-23) avec le **puits** (19-20, lignes 4-5) ; sa moitié nord est le **potager de Hulda** (buissons coupables et un Ronceau minuscule pour la scène de l'épée de bois), sa moitié sud sert d'arène à la scène du Sanglier (Pip se cache derrière le puits, case `s`). Quatre sorties ouvertes dès le début, une fermée par un tronc ; le château se voit en silhouette sur les lignes 0 (décor, sans collision) en haut à droite.

Hauteur : 11 lignes imposées par la grille ; les maisons font 3 lignes (toit arrière sur `Dessus`, toit avant et façade sur `Murs`) pour laisser la rue à 2 cases de large.

### 2.2 Aperçu

Aperçu (colonnes 0 à 39, lignes 0 à 10) :

```
#######XX#######################XX######
#HHHHH#LL#HHHHH.......E..HHHHHH#.o#HHHH#
#HHHHH#P.#HHHHHo.b.b.b...HHHHHH#P.#HHHH#
#HHdHH#..#HHDHH..........HHDHHH#..#HdHH#
X.P..t......P......WW......P...........X
X..i...............WW.........u......P.X
#HHHHHH#HHHHHHH.....s....HHHHHH#HHHHHRR#
#HHHHHH#HHHHHHH..u......oHHHHHH#HHHHHRR#
#HHdHHH#HHHDHHH....P.....HHDHHH#HHdHHFR#
#.....o....P...............P.......o.P.#
###################XX###################
```

### 2.3 Maisons (dix bâtiments)

| Bâtiment | Cases (colonnes x lignes) | Porte | Rôle |
| --- | --- | --- | --- |
| Hutte de Tobias | 1-5 x 1-3 | (3,3) `d` | Fermée ; tas de bois devant |
| Maison de Hulda | 10-14 x 1-3 | (12,3) `D` | Intérieur `maison_hulda` |
| Archives d'Isolde | 25-30 x 1-3 | (27,3) `D` | Intérieur `archives_isolde` |
| Maison des mineurs | 35-38 x 1-3 | (36,3) `d` | Fermée, volets clos ; s'ouvre visuellement à l'étape 3 (mineurs de retour) |
| Maison de Pip | 1-6 x 6-8 | (3,8) `d` | Fermée (parents) |
| **Forge de Corvan** | 8-14 x 6-8 | (11,8) `D` | Intérieur `forge`, point central |
| Boutique de Garrick | 25-30 x 6-8 | (27,8) `D` | Intérieur `boutique_garrick` |
| Maison du pêcheur | 32-36 x 6-8 | (34,8) `d` | Fermée ; ses volets s'ouvrent à l'étape 4 ou 5 (décor) |
| Rocher fissuré | 37-38 x 6-8 | mur fissuré (37,8) `F` | Cave secrète de Garrick (bombes) |
| Poulailler et grange | décor, entre les maisons | — | 2 petits annexes décoratifs, cachent des poules |

Les portes des bâtiments fermés sont une tuile `porte fermée` sans Sortie (la lettre `d`). Les 4 maisons enterables + la cave donnent les 5 Sorties intérieures du village.

### 2.4 Sorties et blocages (tous visibles dès l'étape 0)

| Sortie | Cases | Mène à | État au début | Comment il s'ouvre |
| --- | --- | --- | --- | --- |
| Ouest | col. 0, lignes 4-5 | `foret_sud` (puis le temple) | **Ouverte** | — |
| Nord-ouest | cases 7-8, ligne 0 | raccourci vers la forêt (`foret_temple`) | **Fermée** : un tronc en travers (`LL`, ligne 1) avec la hache de Tobias plantée dedans | Disparaît à l'étape 2 (Tobias retourne au bois) |
| Nord-est | cases 32-33, ligne 0 | `montagne` (écran sud-ouest) | Ouverte jusqu'à un **ravin** : pont-levis relevé et cible à l'arc visibles, brume épaisse | Flèche dans la cible (arc, étape 1) |
| Est | col. 39, lignes 4-5 | `route_falaise` | **Ouverte, en cul-de-sac** : la route finit au pied d'une falaise percée d'une grotte noire (indice : « Il fait trop sombre ») | Lanterne (étape 3) |
| Sud | cases 19-20, ligne 10 | `lac` (rive) | Ouverte jusqu'à un **éboulis** de rochers qui barre la rive | Bombe (étape 2) |
| Cave de Garrick | case (37,8) | intérieur `cave_garrick` | Mur fissuré visible | Bombe (étape 2) |

« Brume au nord » : une zone de brume épaisse (classe `Brume`, voir 5) couvre le village et le ravin. Elle ne bloque pas le passage (on peut aller voir le ravin, le pont relevé et la cible dès le début, « montrer avant d'exiger ») ; elle s'éclaircit aux étapes 2 à 5 (liste de densités par étape).

### 2.5 Le ravin et le pont-levis (écran sud-ouest de `montagne.tmx`, lignes 11 à 21)

Le pont-levis est dans `montagne.tmx`, pas dans le village : on y arrive par la sortie nord-est, sur un palier bordé d'un ravin. La **cible** (`Y`) est sur la berge nord, alignée avec le palier ; le joueur tire par-dessus le ravin (à confirmer avec le développeur : la flèche doit passer au-dessus du ravin comme au-dessus d'un trou, voir 5). Le pont (`BB`, 2×2 cases, cases 12-13) est une `Porte` d'apparence `pont_levis` dont l'`Interrupteur` (mode `fleche`) est la cible.

```
############..######
###########....#####
##########......####
##########Y.....####
#~~~~~~~~~~~BB~~~~~#
#~~~~~~~~~~~BB~~~~~#
#..................#
#..................#
#.........P........#
#..................#
############XX######
```
(Ravin `~` : impassable, laisse passer les flèches. Après le pont, le chemin continue vers le nord, colonnes 12-13.)

### 2.6 PNJ du village et étapes de l'histoire

Étapes (à stocker dans `GameState.StoryStage`, voir 5) : **0** prologue et matin (cinématiques) ; **1** libre, brume épaisse (début de la forêt) ; **2** après le Temple, brume en partie levée ; **3** après la Mine ; **4** après le Sanctuaire, village vide pendant l'éclipse ; **5** épilogue, soleil et fête.

| PNJ (`id`) | Étapes | Emplacement (colonne, ligne) | Comportement |
| --- | --- | --- | --- |
| `pip` | 0 à 1 | (3,5) au départ ; cachette derrière le puits (20,6) dans la scène du Sanglier | Suit Brann dans le village et la forêt sud (pas dans les donjons) ; conseils de gameplay ; donne le quart de cœur des poules |
| `pip` | 2 à 4 | (21,7) près du puits | Immobile ; parle des poules |
| `pip` | 5 | (18,6) à la fête | Immobile |
| `tobias` | 0 à 1 | (5,4) devant sa hutte | Immobile ; indice : Corvan allait souvent en forêt |
| `tobias` | 2 à 3 | dans `foret_sud`, (12,5) | Immobile ; a dégagé le raccourci |
| `tobias` | 5 | (23,4) à la fête | Immobile |
| `hulda` | 0 à 5 | dans `maison_hulda`, derrière le comptoir | Boutique (potion, cœur) ; à l'étape 5 elle est sur la place |
| `garrick` | 0 à 5 | dans `boutique_garrick`, derrière le comptoir | Boutique ; l'étal des bombes apparaît à l'étape 3 |
| `isolde` | 0 à 5 | dans `archives_isolde` ; en scène à la forge (étape 0) | Raconte l'histoire des sceaux ; retrouve le nom de Corvan à l'étape 4 |
| `villageois_apeure` | 0 à 1 | (17,7) | Dialogue court (brume) |
| `villageois_mineur` | 3 | (30,5) | Le mineur revenu ; parle de la Mine |
| `corvan` | 0 | dans la forge | Scènes du prologue (disparaît après la scène) |

Il n'y a pas d'autres habitants : les 2 villageois sont facultatifs (décision 9).

### 2.7 Évolution du village (une seule carte, états par étape)

Une seule carte `village.tmx`. Chaque objet porte `etape_min` / `etape_max` (voir 5) : les PNJ, les tuiles-objets (guirlandes de fête, volets ouverts, feu de la forge) et les ennemis scénarisés n'existent qu'aux étapes voulues. La teinte jour/brume/éclipse est une teinte de couleur appliquée par le code (comme prévu dans la roadmap, un seul tileset).

| Étape | Brume (densité) | Ce qui change |
| --- | --- | --- |
| 0 | 0,5 | Matin ; l'éclipse (ciel violet) en fin de prologue ; Ronceaux et Sanglier sur la place (scénarisés) |
| 1 | 0,8 | Brume épaisse, volets clos, villageois apeurés ; tronc au nord-ouest |
| 2 | 0,45 | Tobias parti, tronc retiré ; flèches en boutique |
| 3 | 0,3 | Mineurs de retour (maison des mineurs ouverte) ; bombes en boutique |
| 4 | 0,7 | Village vide : seuls Hulda et Isolde restent ; ciel d'éclipse ; huile de lanterne en boutique |
| 5 | 0 | Soleil, guirlandes, tous les PNJ sur la place ; le feu de la forge est rallumé |

### 2.8 Collectibles et secrets du village

- **5 poules** (`Poule`, mini-jeu de Pip, quart de cœur à la fin) : (6,9) chemin sud, derrière la maison de Pip ; (15,2) jardin de Hulda ; (24,7) sud-est de la place ; (33,1) couloir du ravin ; (35,9) chemin sud, près du rocher.
- **Cave secrète de Garrick** : mur fissuré (37,8), visible dès le début, bombes (étape 2).
- **Plume de corbeau** : 1, derrière le poulailler (annexe), à placer à l'étape 2 de production.
- Statue du corbeau : dans la forge (id `village_statue_forge`).
- Rubis dans les buissons du potager et de la place, comme dans la forêt.

## 3. Les intérieurs

Principe : **tous les intérieurs sont des cartes de 20×11 cases en `camera` = `ecran`**. La pièce est dessinée au centre sur fond noir (`x`), plus petite qu'un écran comme prévu par la roadmap, **sans rien demander au code** (pas de caméra à centrer). Calques habituels ; le tileset `interieurs` est à créer (section 6). Spawn d'entrée `depuis_village` toujours en (9,8), devant la porte (Sortie en (9,9)). Légende ajoutée : `T` comptoir ou table, `e` étal (`Etal`), `B` étagère de livres, `h` Hulda, `g` Garrick, `a` Isolde, `N` Corvan, `F` fourneau, `b` lit, `A` enclume, `c` charbon, `%` roche, `.` sol.

### 3.1 La forge de Corvan (`maps/interieurs/forge.tmx`)

```
xxxxxxxxxxxxxxxxxxxx
xxx##############xxx
xxx#.FFF..TTT.bb#xxx
xxx#.FFF......bb#xxx
xxx#............#xxx
xxx#.....RN.....#xxx
xxx#cc..........#xxx
xxx#............#xxx
xxx#.....P......#xxx
xxx######D#######xxx
xxxxxxxxxxxxxxxxxxxx
```
La statue du corbeau `R` est posée sur l'enclume (1 case solide, 1 objet `StatueCorbeau` id `village_statue_forge`) ; `N` = Corvan (étape 0 seulement). `F` : fourneau 3×2 froid (tuile-objet avec `etape_max` 4) puis fourneau allumé (`etape_min` 5). `TTT` : établi et outils ; `bb` : lit de Brann. `cc` : deux `Ramassable` de charbon (`village_charbon_01/02`, étape 0, quête du matin). Sortie : (9,9) vers `village`, spawn `depuis_forge`. Spawn d'arrivée : `depuis_village` (9,8). Plus tard : établi d'amélioration de l'épée (épée trempée après le 2ᵉ sceau, Lame du Corbeau avec les 10 plumes), objet `Forge` à spécifier à ce moment-là.

### 3.2 Maison de Hulda (`maps/interieurs/maison_hulda.tmx`)

```
xxxxxxxxxxxxxxxxxxxx
xxx##############xxx
xxx#HHHHHHHHHHHH#xxx
xxx#H....h.....H#xxx
xxx#...TeTTeT...#xxx
xxx#............#xxx
xxx#............#xxx
xxx#............#xxx
xxx#.....P......#xxx
xxx######D#######xxx
xxxxxxxxxxxxxxxxxxxx
```
Deux `Etal` sur le comptoir : potion rouge (40 rubis, 2 maximum dans l'inventaire) et petit cœur de soin (10 rubis, prix à valider, décision 7). `H` : étagères d'herbes. Hulda (`h`) est derrière le comptoir ; on lui parle de dos au comptoir, les étals s'achètent en face.

### 3.3 Boutique de Garrick (`maps/interieurs/boutique_garrick.tmx`)

```
xxxxxxxxxxxxxxxxxxxx
xxx##############xxx
xxx#HHHHHHHHHHHH#xxx
xxx#....g....e..#xxx
xxx#..TeTeTeT...#xxx
xxx#............#xxx
xxx#............#xxx
xxx#............#xxx
xxx#.....P......#xxx
xxx######D#######xxx
xxxxxxxxxxxxxxxxxxxx
```
Étals du comptoir (de gauche à droite) : 10 flèches (20 rubis, dès l'étape 2), 5 bombes (30, dès l'étape 3), huile de lanterne (10, dès l'étape 4). Étal seul contre le mur : quart de cœur (150 rubis, `stock` 1, mémorisé). Garrick radin : un dialogue de marchandage au premier achat.

### 3.4 Archives de Dame Isolde (`maps/interieurs/archives_isolde.tmx`)

```
xxxxxxxxxxxxxxxxxxxx
x##################x
x#BBBBBBBBBBBBBBBB#x
x#B..............B#x
x#B....TTTT......B#x
x#B....TTTT...a..B#x
x#B..............B#x
x#B..............B#x
x#.......P........#x
x########D#########x
xxxxxxxxxxxxxxxxxxxx
```
Plus large (16×7 utiles). Isolde (`a`) à côté de la grande table. Un rectangle `indice_registres` (area) devant les registres du fond affiche « Registres des gardiens » : à l'étape 4, Isolde y retrouve le nom de Corvan (dialogue). Pas de combat, pas d'objet obligatoire.

### 3.5 Cave secrète de Garrick (`maps/interieurs/cave_garrick.tmx`)

```
xxxxxxxxxxxxxxxxxxxx
xxxxxx%%%%%%%%xxxxxx
xxxx%%........%%xxxx
xxx%%..e..g.e..%%xxx
xxx%............%xxx
xxx%............%xxx
xxx%%..........%%xxx
xxxx%%........%%xxxx
xxxxxx%%.P..%%xxxxxx
xxxxxxxx%X%%xxxxxxxx
xxxxxxxxxxxxxxxxxxxx
```
Deux `Etal` : grand carquois (100 rubis) et grand sac de bombes (100 rubis), chacun `stock` 1. Garrick (`g`, id `garrick_cave`) y marmonne : « Comment as-tu trouvé ça ? ». Sortie (9,9) vers `village`, spawn `depuis_cave_garrick` (37,9). Le Spawn d'arrivée de la cave est `depuis_village` (9,8).

### 3.6 Autres intérieurs (plus tard)

`grotte_sw` (réceptacle de cœur, derrière le mur fissuré de l'écran (0,3)), `grotte_sombre_montagne` (lanterne, quart de cœur), `passage_falaise` (couloir noir vers le château). Ces 3 pièces s'ajoutent aux 5 ci-dessus : **8 intérieurs au total** (la roadmap en annonce 5 à 6 plus 1 ou 2 grottes ; l'écart vient de la montagne et de la falaise).

## 4. La forêt complète (5 écrans)

Forêt = `foret_temple.tmx` (4 écrans, existe) + `foret_sud.tmx` (1 écran). Le fond du Temple reste au nord-centre ; l'accès normal depuis le village est : village (entrée ouest) > forêt sud > sortie nord (cases 6-7) > moitié basse de `foret_temple` > pont (cases 11-12) > moitié haute > temple. Le raccourci du village (étape 2) débouche dans la moitié basse est, près de la souche creuse.

### 4.1 `foret_sud.tmx` (20×11)

```
######XX############
#####.....####..#bf#
#####.P........E.#b#
#.........R........#
#..................X
####........t......X
####E...........####
######....E.####...#
#....#......####...#
#.Q..r.........Y####
#########XX#########
```
- Ennemis : 2 Ronceaux et 1 Sanglier noirci (faciles, au-dessus du niveau de départ ; le Sanglier à gauche du sentier).
- `R` : statue du corbeau (`foret_statue_clairiere`), point de sauvegarde avant le gros de la forêt.
- `t` : Tobias aux étapes 2 et 3.
- **Quart de cœur n°1 (cible cachée à l'arc)** : une cible `Y` camouflée dans un buisson (`Interrupteur` mode `fleche`, `symbole` `feuille`) au bout de la ligne 9 ; elle ouvre un rocher `r` (une `Porte` d'apparence `rocher`) qui ferme une poche en bas à gauche contenant le quart de cœur `Q` (`foret_quart_coeur_cible`). Indice visible dès le début : le rocher isolé au bout d'un couloir dégagé, avec des fleurs qui guident le regard ; accessible seulement après l'arc (donc après le temple) ; rien n'est obligatoire.
- **Plume n°1** : `f`, dans une niche du coin nord-est, fermée par 2 buissons coupables `b` (`foret_plume_01`).
- Raccords : nord (cases 6-7), est (colonne 19, lignes 4-5), sud (cases 9-10).

### 4.2 `foret_temple.tmx` (retouches, étape 2)

Voir 1.3. En plus : **quart de cœur n°2** = souche creuse (34,17), déjà derrière des buissons. **Plume n°2** : à placer dans le coin nord-est de la moitié haute (par exemple vers (36,3), pas encore utilisé). Le rubis rouge secret `foret_rubis_secret_01` est déplacé d'une case ou remplacé par le quart de cœur.

### 4.3 Répartition des 10 plumes de corbeau (proposition)

Temple des Racines 2 (déjà prévues dans les salles 03 et 12), forêt 2, village 1, montagne 1 et Mine 1, lac 1 et Sanctuaire 1, route/falaise 1. Id : `<zone>_plume_NN`.

## 5. Nouveautés Tiled et code à faire valider (à ajouter au `CLAUDE.md` après accord)

Le principe : **réutiliser au maximum les classes existantes** (`Porte`, `Interrupteur`, `MurFissure`, `Ramassable`, `StatueCorbeau`, `PNJ`, rectangles `indice_`) et ajouter peu de choses.

1. **Propriétés communes à tous les objets du calque `Objets`** : `etape_min` (entier, défaut 0) et `etape_max` (entier, défaut 99). La `Room` n'instancie l'objet que si `GameState.StoryStage` est dans l'intervalle. Sert aux PNJ, ennemis, ramassables, étals, portes (tronc), brumes, et aux **objets tuiles** (feu de forge éteint/allumé, guirlandes).
2. **`PNJ`** : `id` (clé des dialogues et de l'état), `sprite` (nom de `art/npcs/<sprite>_frames.tres`), `direction` (`bas` par défaut), `comportement` (`immobile` par défaut, `errant`, `suit`). Dialogue : clés `PNJ_<ID>_E<étape>_<n>` dans `textes.csv` (ou JSON indexé par flags, selon le développeur). Convention : plusieurs objets `PNJ` de même `id` à des étapes disjointes.
3. **`Etal`** (boutique, achat à la manière de A Link to the Past, sans menu) : `id`, `contenu` (nom d'un `.tres` de `resources/pickups/`), `prix` (rubis), `stock` (0 = illimité, 1 = unique, mémorisé par `id`), plus `etape_min` / `etape_max`. Point posé sur la case du comptoir ; le prix s'affiche au-dessus.
4. **`Porte` généralisée** : propriété `apparence` (`porte` par défaut, `pont_levis`, `tronc`, `rocher`, `eboulis`) ; rectangle de taille libre (pont 2×2, tronc 2×1, rocher 1×1) et **sans `Sortie`** quand elle bloque un passage d'overworld. Type `interrupteur` pour le pont et le rocher (ouverts par un `Interrupteur`), et le tronc n'a pas besoin de type : il porte `etape_max` 1 (l'objet n'existe plus à l'étape 2). Image : `art/puzzles/porte_<apparence>.png`.
5. **`MurFissure`** : propriété `apparence` (`mur` par défaut, `eboulis` pour la rive) ; peut recouvrir une `Sortie` de même rectangle (comme une `Porte`), la `Sortie` s'activant une fois le mur détruit. Utilise `IBombDestructible`.
6. **`Brume`** : rectangle ; propriété `densite` = liste de 6 valeurs (une par étape de 0 à 5, ex. `0.5,0.8,0.45,0.3,0.7,0`) ; ne bloque pas le passage. Calque `Dessus` ou superposition de brume avec la teinte de couleur de la zone.
7. **`Poule`** : point, `id` (`village_poule_01` à `05`) ; marcher dessus ou la frapper l'attrape ; compteur `GameState.Chickens` ; `pip` donne le quart de cœur à 5 (récompense mémorisée par `village_quart_coeur_poules`).
8. **`Marqueur`** : point, `id`, pour les cinématiques (où se place Pip, où marche Corvan) sans coordonnées en dur dans le code.
9. **`Ennemi`** : propriété `apparition` (`chargement` par défaut, `scenario` : n'existe que lancé par une cinématique, pour la scène du Sanglier sur la place).
10. **`Interrupteur`** : `symbole` `feuille` + mode `fleche` sert de cible camouflée ; aucune nouveauté, mais l'art doit la rendre discrète.
11. **Propriétés de carte** `monde_x`, `monde_y` (facultatives). Les intérieurs sont en `camera` = `ecran`.
12. **Sorties de bord à plusieurs cases** : le `.tmx` actuel n'en a que de 1 case ; les rectangles de 2 cases de large (et 64×32) sont à confirmer côté code. Un seul Spawn par passage.
13. **Pour le développeur, en code** : `GameState.StoryStage` (sauvegardé, `SaveData` version +1), boîte de dialogue PNJ avec défilement des lettres (une `DialogueBox` existe pour les boss), `Etal`, `Poule`, système de cinématiques, `TitleScreen` : nouvelle partie dans la forge (`maps/interieurs/forge.tmx`, spawn `depuis_village`), pause de jeu pendant les achats, ressources `.tres` des objets : `quart_de_coeur` (4 = un cœur), `plume_corbeau`, `potion_rouge`, `petit_coeur`, `fleches_10`, `bombes_5`, `huile_lanterne`, `grand_carquois`, `grand_sac_bombes`.
14. **Pour le développeur, à vérifier** : la flèche passe-t-elle au-dessus d'un ravin (comme au-dessus d'un trou) ? Une `Porte` peut-elle être posée hors d'une `Sortie` ? Pip suiveur d'une carte à l'autre (village + forêt sud) ?

### À demander au graphiste

Dans l'ordre d'utilité (le plan d'un tileset se livre avant son dessin, comme d'habitude) :
1. **`village`** (nouveau `.tsx`) : herbe et pavés de la place, terre de la rue, puits 2×2, maisons à 3 variantes de toit (toit arrière en `Dessus`), portes ouvertes et fermées, volets ouverts et clos, clôtures, potager, tas de bois, tonneaux, poulailler, étals, enseigne de forge et de boutique, guirlandes, silhouette du château (décor de fond), tronc en travers, rocher fissuré avec variante éboulis.
2. **`interieurs`** (nouveau `.tsx`) : sols (bois, pierre), murs, étagères d'herbes et de livres, comptoir, étal, lit, établi, fourneau 3×2 (froid et allumé), enclume avec corbeau, table, registres, roche de cave.
3. **Sprites PNJ** : Pip, Tobias, Hulda, Isolde, Garrick, Corvan, 2 villageois, poule (marche, picore).
4. **`montagne`**, **`lac`** (rive, ponton, éboulis), **`route_chateau`** (route pavée, falaise sombre, grotte noire, façade du château) : dans l'ordre des étapes de production.
5. **Images de `Porte`** : `pont_levis` (relevé et abaissé, 64×64), `tronc`, `rocher`, `eboulis` ; cible camouflée (feuillage) ; texture de brume.
6. Objets : quart de cœur, plume de corbeau, grand carquois, grand sac de bombes, potion rouge, huile, icône de prix.

## 6. Ordre de production conseillé (phase 6)

Objectif : une **boucle jouable village > forêt > temple > retour au village** le plus tôt possible.

1. **Valider ce plan**, puis demander au graphiste le plan des tilesets `village` et `interieurs` ; au développeur : `StoryStage`, `PNJ` + dialogues, `etape_min/max`.
2. **`foret_sud.tmx` et retouches de `foret_temple.tmx`** : n'utilisent que le tileset `foret` existant, donc faisables tout de suite. On peut déjà tester le chemin forêt sud > temple.
3. **`village.tmx` (blockout)**, puis **`forge.tmx`** avec la statue : nouvelle partie dans la forge, sortie sur la place, sortie ouest vers la forêt. La boucle est jouable ; Pip, Tobias et Corvan sont des placeholders.
4. **Retour au village** après le boss : Pip, Tobias et Hulda parlent (étape 2), flèches en boutique : `maison_hulda.tmx`, `boutique_garrick.tmx` avec les `Etal`.
5. **Montagne, écran sud-ouest** (`montagne.tmx` réduit à un palier, le ravin, la cible, le pont-levis et la fermeture du reste par la falaise) : boucle « arc obtenu > pont abaissé ».
6. Secrets de la forêt (cible cachée, souche creuse, plume), poules de Pip, `archives_isolde.tmx`.
7. Scènes d'ouverture (cinématiques) et teintes jour/brume/éclipse.
8. Donjon 2 : reste de `montagne.tmx` et Mine ; éboulis du lac et `lac.tmx` partiel (rive), `grotte_sw`, `cave_garrick` (bombes).
9. Donjon 3 : reste de `lac.tmx`, `route_falaise.tmx`, grotte noire, `chateau.tmx`.
10. Évolution du village (étapes 3 à 5), épilogue.

## 7. Cohérence avec les contraintes de progression

- Chaque blocage est visible avant d'être franchissable : ravin et cible (nord), éboulis (sud), fissure (est du village et grotte SO), grotte noire (route), tronc (raccourci).
- Rien n'exige un objet avant l'endroit où on l'obtient : l'arc est dans le Temple (forêt, ouvert), la cible est ensuite au ravin ; les bombes sont dans la Mine, derrière le pont ; la lanterne est dans le Sanctuaire, derrière l'éboulis. Les secrets de la forêt demandent l'arc et sont facultatifs. Aucune soft-lock : le tronc, la cible et le rocher sont des états sauvegardés ou dépendants de l'étape.
- Les blocs poussables ne sont pas utilisés dans l'overworld.

## 8. Décisions à faire valider

1. `foret_temple.tmx` gardé tel quel (2×2 écrans) avec `foret_sud.tmx` comme 5ᵉ écran de forêt (et non une extension de `foret_temple`).
2. Une carte par zone, 8 cartes extérieures, avec passages de 2 cases (section 1).
3. Le village sur 40×11 (hauteur imposée par la grille) avec 10 bâtiments dont 4 enterables, plus la cave.
4. Le ravin et le pont-levis sont dans `montagne.tmx` et non dans le village ; la brume ne bloque pas (on voit les obstacles avant d'avoir l'arc).
5. Route de l'est ouverte dès le début mais en cul-de-sac (grotte noire visible) ; sinon fermer la sortie est par une barrière jusqu'à l'étape 3.
6. Raccourci Tobias (village vers la moitié basse du temple, ouvert à l'étape 2) : à garder ou à retirer ?
7. Prix : petit cœur chez Hulda à 10 rubis ? Quart de cœur de Garrick à 150 comme dans la roadmap.
8. Intérieurs en 20×11 avec fond noir (aucune caméra spéciale) plutôt que des cartes réellement plus petites.
9. Habitants supplémentaires (2 villageois anonymes) ; Pip suiveur limité au village et à la forêt sud.
10. Les 2 buissons du passage sud de `foret_temple` : ils n'existent pas dans le fichier actuel. À ajouter (si l'épée coupe) ou à oublier ?
11. Nouvelles classes et propriétés de la section 5 (`etape_min/max`, `Etal`, `Poule`, `Brume`, `Marqueur`, `apparence` sur `Porte` et `MurFissure`, `apparition`), à inscrire au `CLAUDE.md`.
12. Huit intérieurs au lieu des 5 ou 6 annoncés, et l'ordre de production de la section 6.
