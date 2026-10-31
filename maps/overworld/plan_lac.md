# Plan du lac (`lac.tmx`) et de la grotte du sud-ouest (`grotte_sw.tmx`) - phase 6, étape 1

Document de conception. Plan **validé le 2026-10-31** (section 6). Il complète `maps/overworld/plan.md` (§1 découpage et raccords, §2.4 blocages, §4.3 plumes, §7 cohérence) et suit le format de `maps/donjon2/plan.md`. Les aperçus ont été relus par un script de vérification (Python, bibliothèque standard seulement, non versionné) : parcours (BFS) depuis l'arrivée, avant et après chaque ouverture ; résultats en section 5.

Rappels de numérotation : `GameState.StoryStage` vaut 0 (début), 1 (après la forêt), 2 (après la montagne, **c'est à cette étape que Brann a les bombes et vient au lac**), 3 (après le Sanctuaire), 4 (épilogue). Les densités de `Brume` sont donc 5 valeurs (étapes 0 à 4).

Légende de `plan.md` (une lettre = une case de 32 px), complétée : `#` solide (arbre, falaise, mur, pilier), `.` sol libre, `~` **eau profonde (solide)**, `w` **eau peu profonde (praticable)**, `=` ponton (sur eau peu profonde), `X` Sortie, `P` Spawn, `R` statue du corbeau, `E` ennemi (Têtard d'encre), `V` ennemi volant (chauve-souris), `b` buisson coupable, `F` éboulis (`MurFissure`), `r` rocher dans le gué (`Porte`), `Y` cible à l'arc, `c` rideau de cascade (traversable), `Q` quart de cœur, `f` plume de corbeau, `$` rubis.

## 1. Intention et courbe de difficulté

**Intention** : l'overworld du lac est la **récompense de la Mine** : Brann a enfin les bombes, et le blocage vu depuis le début (l'éboulis de la rive) s'ouvre. Le joueur y **réutilise** ce qu'il sait (bombe contre un blocage, flèche sur une cible) dans un décor nouveau, voit le Sanctuaire Englouti au bout d'un long ponton et affronte les premiers ennemis aquatiques avant le donjon 3. Pas de lanterne ici (elle est dans le Sanctuaire) : tout ce qui est fermé demande l'épée, l'arc ou les bombes.

| Étape de jeu | Lieu | Ce qui est appris ou testé | Tension |
| --- | --- | --- | --- |
| 0-1 | Plage ouest (avant l'éboulis) | On arrive sur une rive calme ; l'éboulis barre l'isthme, on voit l'eau derrière ; une plume dans une niche à buissons | nulle |
| 2 | Isthme | Poser une bombe contre l'éboulis et reculer (même geste que dans la Mine, en plein air et sans danger) | faible |
| 2 | Berge est | Un Têtard isolé dans l'eau peu profonde (premier ennemi aquatique, sans pression) ; la statue du corbeau ; le rideau de la cascade (quart de cœur) | faible |
| 2 | Ponton | 2 Têtards dans l'eau de chaque côté, le gué à rocher et la cible dans l'eau (quart de cœur de l'îlot, facultatif) | moyenne |
| 2 | Quai du Sanctuaire | 2 Têtards, une chauve-souris, le Sanctuaire à demi noyé et son portail : repos puis entrée du donjon 3 | moyenne puis repos |
| 3-4 | Tout le lac | Ennemis disparus, brume levée : on peut revenir chercher les secrets en paix | nulle |

Rythme : repos (plage) - geste appris (éboulis) - ouverture d'horizon (berge) - combat léger (ponton) - choix facultatif (îlot, cascade) - quai calme.

## 2. `lac.tmx` (80×11 cases, 2560×352 px)

### 2.1 Propriétés et tilesets

- Propriétés de carte : `camera` = `suivre`, `monde_x` = 1, `monde_y` = 3. Zone de la `Room` : `lac` (scène `scenes/rooms/lac_room.tscn`, déjà visée par la Sortie sud de `village.tmx`).
- Tilesets, dans cet ordre (`firstgid` indiqué par Tiled) : `village` (1), `foret` (401), `lac` (NOUVEAU, voir §4 ; il ne contient que ce qui manque). Réutilisés tels quels :
  - **eau peu profonde** : `village` 63 `rive_plein` et 64 `lac_base` (Sol), bords `rive_*` 48-62 (terrain `Rive`) ;
  - **eau profonde** : `village` 65-79 (terrain `Lac profond`, sur `Murs`, collision partielle ou pleine) ;
  - **éboulis** : `village` 138/139 (`eboulis_g`/`eboulis_d`, Murs) ; le code pose 140/141 à l'ouverture ; poussière 145 en Decor ;
  - **ponton** 312-317 (Decor), pilotis 318, roseaux 324/325, nénuphars 326, rocher dans l'eau 327 ;
  - **falaise** `village` 120-132, rochers 133/134, buisson fleuri 300 (coupable) ; `foret` : herbe 0-7, arbres 72-75, buissons coupables 96-99.
- **Choix de level design** : l'eau profonde est **solide pour Brann et les ennemis** (collision des tuiles 65-79) ; l'eau peu profonde est **praticable, sans ralentissement ni dégâts** (aucun code : le ralentissement est une option différée, voir §4.3 point 4). Le ponton est **peint au-dessus d'eau peu profonde** (jamais d'eau profonde dessous : le plan du tileset village dit de retirer la collision sous un ponton, on évite d'en avoir besoin). Les flèches s'arrêtent sur l'eau profonde (comme sur un mur) : aucune cible n'est donc visée à travers de l'eau profonde.

### 2.2 Raccords

| Passage | Objet | Rectangle / point (px) | Cible |
| --- | --- | --- | --- |
| Lac vers village | `Sortie` | x=608, y=0, 64×32 (cases 19-20, ligne 0), `godot_node_type`=`area` | `res://scenes/rooms/village_room.tscn`, spawn `depuis_lac` |
| Arrivée du village | `Spawn` `depuis_village` | (640, 80) | existant dans `plan.md` §1.2 |
| Lac vers Sanctuaire | `Sortie` | x=2240, y=64, 64×32 (cases 70-71, ligne 2) | `res://scenes/rooms/donjon3_salle_01_room.tscn`, spawn `depuis_lac` (scène pas encore créée : `Room.MissingExitFallbackScene`) |
| Retour du Sanctuaire | `Spawn` `depuis_sanctuaire` | (2272, 144), 2 cases devant la Sortie | à viser depuis la salle 01 du donjon 3 (convention comme `depuis_mine`) |

Les bords ouest, sud et est sont fermés (arbres, eau profonde, façade du Sanctuaire) : le lac n'a **pas d'autre sortie** (plan.md §1.2 : route/falaise et grotte SO ne donnent pas sur le lac).

### 2.3 Aperçu par écran

Chaque écran fait 20 colonnes. Le `P` de l'écran 1 est le Spawn `depuis_village`, en réalité centré entre les cases 19 et 20. Le `P` de l'écran 4 est le Spawn `depuis_sanctuaire` (entre les cases 70 et 71).

```text
Écran 1 (colonnes 0 à 19) : la plage
    01234567890123456789
 0  ###################X
 1  #.##............bb..
 2  #fb................P
 3  #b........##........
 4  #.............#.....
 5  #..............#....
 6  #.....##............
 7  #...................
 8  #wwwwwwwwwwwwwwwwwww
 9  ~~~~~~~~~~~~~~~~~~~~
10  ~~~~~~~~~~~~~~~~~~~~

Écran 2 (colonnes 20 à 39) : l'isthme, l'éboulis, la cascade
    01234567890123456789
 0  X###################
 1  ..#############cQ###
 2  ..#############cc###
 3  .....FF........ww...
 4  .....FF......#.ww...
 5  .....FF...bb...ww...
 6  ..$..~~...b....ww...
 7  .....~~wwwwwwwwwwwww
 8  wwwww~~~~~~~~~~~~~~~
 9  ~~~~~~~~~~~~~~~~~~~~
10  ~~~~~~~~~~~~~~~~~~~~

Écran 3 (colonnes 40 à 59) : la berge, le début du ponton, l'îlot
    01234567890123456789
 0  ####################
 1  ........~~~~~~~~~~~~
 2  ........~~~~~~~~~~~~
 3  .....R..~~~~~~~~~~~~
 4  ........wwwwEwwwwwww
 5  ..#.....============
 6  ........============
 7  EwwwwwwwwwwwwwwwEwww
 8  ~~~~~~~~~~~~~~r~~~w~
 9  ~~~~~~~~~~~~~.Q.~~Y~
10  ~~~~~~~~~~~~~~~~~~~~

Écran 4 (colonnes 60 à 79) : fin du ponton, quai, Sanctuaire
    01234567890123456789
 0  ####################
 1  ~~~~~~############~~
 2  ~~~~~~####XX######~~
 3  ~~~~~~~.#....#...~~~
 4  wwwEwww...P......~~~
 5  =======..........~~~
 6  =======.....V....~~~
 7  wwEwwww........$.~~~
 8  ~~~~~~~#........#~~~
 9  ~~~~~~~~~~~~~~~~~~~~
10  ~~~~~~~~~~~~~~~~~~~~
```

Lecture du parcours :
- **Plage (écran 1)** : le joueur entre par le haut (cases 19-20), et la plage s'étire à l'ouest et à l'est. Deux rochers/arbres (`#`) cassent le plat. Le rivage est une bande d'eau peu profonde (ligne 8) puis l'eau profonde : on voit déjà le lac.
- **Isthme (écran 2, colonnes 25-26)** : falaise au nord, eau profonde au sud, **3 cases de large (lignes 3-5) bouchées par l'éboulis** (`FF`, 2×3 cases). On le voit en entrant (5 cases de l'arrivée) et on ne peut pas le contourner (aucune case d'eau peu profonde ne touche l'isthme). 4 cases libres devant (colonnes 21-24) pour reculer pendant la mèche.
- **Berge est (colonnes 27-47)** : prairie de 4 cases de haut, falaise au nord. La **cascade** tombe dans la falaise (colonnes 35-36) ; son bassin forme un petit ruisseau d'eau peu profonde (`ww`, lignes 3-7) qui rejoint le lac. Le **rideau** (`c`, lignes 1-2) cache une alcôve de 2×2 cases : le quart de cœur y brille.
- **Ponton (colonnes 48-66)** : bande d'eau peu profonde de 4 cases (lignes 4-7) avec le ponton de bois sur les lignes 5-6, de la rive jusqu'au quai. Les Têtards nagent dans l'eau peu profonde de chaque côté.
- **Îlot** : 3 cases de terre (ligne 9, colonnes 53-55) cachées derrière un **rocher** posé dans le gué (case (54,8)). La **cible** (`Y`, case (58,9)) est au bout d'un petit goulet d'eau peu profonde (case (58,8)), alignée sur la colonne 58 du ponton : on tire vers le sud depuis le ponton.
- **Quai (colonnes 67-76)** : dalle de pierre devant la façade à demi noyée du Sanctuaire (lignes 0-2). Le portail est aux cases 70-71 (ligne 2). Deux piliers (`#`, lignes 3 et 8) et des colonnes brisées donnent du décor sans fermer le passage.

### 2.4 Objets Tiled (calque `Objets`), coordonnées en pixels

Point = centre de la case (colonne × 32 + 16, ligne × 32 + 16). `etape_min` / `etape_max` : voir §2.5.

| # | Classe | Position / rectangle | Propriétés |
| --- | --- | --- | --- |
| 1 | `Sortie` | 608, 0, 64×32 | `cible_carte`=`res://scenes/rooms/village_room.tscn`, `cible_spawn`=`depuis_lac`, `godot_node_type`=`area` |
| 2 | `Spawn` | (640, 80) | `id`=`depuis_village` |
| 3 | `MurFissure` | 800, 96, 64×96 (cases 25-26, lignes 3-5) | `id`=`lac_eboulis_rive`, `apparence`=`eboulis` (tuiles 138/139 posées dans `Murs`) |
| 4 | `Ramassable` | (48, 80) | `id`=`lac_plume_01`, `contenu`=`plume_corbeau` (niche de la case (1,2), fermée par les buissons (2,2) et (1,3)) |
| 5 | `Ramassable` | (720, 208) | `id`=`lac_rubis_01`, `contenu`=`rubis_vert` |
| 6 | `Ramassable` | (1168, 48) | `id`=`lac_quart_coeur_cascade`, `contenu`=`quart_coeur` (alcôve derrière le rideau) |
| 7 | `StatueCorbeau` | (1456, 112) | `id`=`lac_statue_ponton` |
| 8 | `Ennemi` | (1296, 240) | `type`=`tetard_encre`, `variante`=`normal`, `etape_max`=2 |
| 9 | `Ennemi` | (1680, 144) | idem |
| 10 | `Ennemi` | (1808, 240) | idem |
| 11 | `Ennemi` | (2032, 144) | idem |
| 12 | `Ennemi` | (2000, 240) | idem |
| 13 | `Ennemi` | (2320, 208) | `type`=`chauve_souris`, `variante`=`normal`, `etape_max`=2 |
| 14 | `Porte` | 1728, 256, 32×32 | `id`=`lac_rocher_ilot`, `type`=`interrupteur`, `apparence`=`rocher` (sans `Sortie`) |
| 15 | `Interrupteur` | (1872, 304) | `id`=`lac_cible_ilot`, `cible`=`lac_rocher_ilot`, `mode`=`fleche`, `ordre`=0, `duree`=0, `symbole`=`feuille` |
| 16 | `Ramassable` | (1744, 304) | `id`=`lac_quart_coeur_ilot`, `contenu`=`quart_coeur` (îlot derrière le rocher) |
| 17 | `Ramassable` | (2416, 240) | `id`=`lac_rubis_02`, `contenu`=`rubis_bleu` (sur le quai : récompense de la traversée) |
| 18 | `Sortie` | 2240, 64, 64×32 | `cible_carte`=`res://scenes/rooms/donjon3_salle_01_room.tscn`, `cible_spawn`=`depuis_lac`, `godot_node_type`=`area` |
| 19 | `Spawn` | (2272, 144) | `id`=`depuis_sanctuaire` |
| 20 | `Brume` (plage) | 0, 0, 800×352 | `densite`=`0.4,0.5,0.4,0.2,0`, `godot_node_type`=`area` |
| 21 | `Brume` (lac) | 800, 0, 1760×352 | `densite`=`0.15,0.25,0.5,0.2,0`, `godot_node_type`=`area` |

Buissons coupables : 2 sur la niche de la plume ((2,2) et (1,3)), 2 devant la plage nord ((16,1) et (17,1)), 3 sur la berge ((30,5), (31,5), (30,6)) : tuiles `village` 300 ou `foret` 96-99, sur `Murs`. Ils ne cachent rien d'obligatoire. L'état de la cible et du rocher est **sauvegardé par `id`** (porte ouverte mémorisée) ; la plume, les quarts de cœur et les rubis sont des ramassables uniques mémorisés par `id`.

**Position de tir de la cible de l'îlot** : depuis (58,5) ou (58,6) (le ponton), vers le sud ; les cases (58,6), (58,7) et (58,8) sont de l'eau peu profonde sans obstacle, la flèche touche la cible en (58,9). Aucun Têtard n'est placé sur cette colonne (le Têtard (56,7) est à 2 colonnes) : sa position peut varier, mais un ennemi dans la ligne ne bloque que le temps de le tuer.

### 2.5 Ce qui change selon l'étape (`etape_min` / `etape_max`)

| Objet | Étapes | Raison |
| --- | --- | --- |
| Les 5 Têtards et la chauve-souris | `etape_max`=2 | Après le Sanctuaire, le lac se calme (pas de combat inutile pour revenir chercher les secrets) |
| Brume (plage) | 0,4 / 0,5 / 0,4 / 0,2 / 0 | Brume du village qui descend jusqu'à la plage ; se lève avec les sceaux |
| Brume (lac) | 0,15 / 0,25 / 0,5 / 0,2 / 0 | Le plus dense à l'étape 2 (la menace est au Sanctuaire), puis se lève |
| Tout le reste | toutes | Éboulis, rocher, cible, secrets, statue et portail ne dépendent pas de l'étape |

Pas de PNJ sur le lac dans ce plan (le pêcheur du village est évoqué en décision hors plan, §6). Le ciel d'éclipse de l'étape 3 est une **teinte de salle** (`Room.SetTint`), à lancer depuis la cinématique de sortie du Sanctuaire : ce n'est pas du ressort de la carte.

### 2.6 Les deux quarts de cœur du lac

- **Îlot près du ponton** (`lac_quart_coeur_ilot`) : **arc**. Le joueur voit depuis le ponton, trois cases au sud, un îlot de 3 cases où brille le quart de cœur, **fermé par un rocher** dans un gué ; plus loin dans l'eau, une cible au bout d'un goulet. Il tire depuis le ponton (colonne 58), le rocher disparaît, il traverse le gué. Même mécanique que la cible cachée de la forêt (`foret_sud`), mais ici la cible est **visible** (symbole `feuille` dans les roseaux, bien lisible) puisque le lac est déjà une zone « on se débrouille ». L'arc est possédé depuis le Temple ; la bombe n'est pas utilisée ici, pour ne pas gaspiller le stock juste après l'éboulis.
- **Derrière la cascade** (`lac_quart_coeur_cascade`) : **aucun objet** requis, seulement l'**observation**. Le rideau d'eau est dessiné sur le calque `Dessus` (semi-transparent) au-dessus de cases libres : Brann marche dedans et passe « derrière ». Indices : un bassin et un ruisseau qui descendent de la falaise, une trouée sombre dans la roche à travers l'eau, un scintillement. Rien n'est fermé, c'est un secret de curieux, accessible dès l'arrivée de la berge (étape 2). Pas de soft-lock : l'alcôve a une seule ouverture au sud.

## 3. `grotte_sw.tmx` (20×11 cases)

### 3.1 Intention

Un cul-de-sac rocheux au sud-ouest de la forêt (sortie sud de `foret_sud.tmx`, cases 9-10 ligne 10, déjà posée). **Dès l'étape 0**, le joueur y voit un mur de roche fendu au bout de la salle (face fissurée) et un petit scintillement dans l'ombre : « je reviendrai ». Aux étapes 0 et 1 la salle est un détour sans danger (2 Ronceaux). À l'étape 2, une bombe ouvre la fissure et donne le **réceptacle de cœur secret**.

- Propriétés de carte : `camera` = `suivre` (comme `foret_sud`), `monde_x` = 0, `monde_y` = 3.
- **Zone** : `foret` (la grotte est une annexe de la forêt sud : pas de sauvegarde automatique parasite ; la statue de la clairière est juste au-dessus). Scène `scenes/rooms/grotte_sw_room.tscn` (déjà visée par `foret_sud.tmx`).
- Tilesets : `montagne` seul (sols de roche 0-15, falaise 128-143, **face fissurée 156 / ouverte 157** déjà gérées par `TileRules`, rochers 168-170, gravats 183, buissons coupables 203/204).

### 3.2 Aperçu

```text
    01234567890123456789
 0  #########XX#########
 1  #########..#########
 2  #######..P...#######
 3  ####....#......#####
 4  ###.bb#........#####
 5  ###...E........F.Q##
 6  ###.......#....#####
 7  ###......E.....#####
 8  ####..........######
 9  ####################
10  ####################
```

(`F` : face fissurée 156 sur `Murs` ; `Q` : réceptacle.) Le `P` est le Spawn centré entre les cases 9 et 10.

Lecture : un couloir de 2 cases (ligne 1) débouche dans une salle ovale de 12 cases de large. Le `F` est sur le mur est, aligné avec la ligne 5, au bout de 5 cases de sol libre ; une alcôve de 2 cases (16-17, ligne 5) se cache derrière. Gravats au pied de la fissure, quelques rochers et deux buissons en décor.

### 3.3 Objets Tiled

| # | Classe | Position / rectangle (px) | Propriétés |
| --- | --- | --- | --- |
| 1 | `Sortie` | 288, 0, 64×32 | `cible_carte`=`res://scenes/rooms/foret_sud_room.tscn`, `cible_spawn`=`depuis_grotte_sw`, `godot_node_type`=`area` |
| 2 | `Spawn` | (320, 80) | `id`=`depuis_foret_sud` |
| 3 | `MurFissure` | 480, 160, 32×32 (case 15,5) | `id`=`foret_grotte_mur_secret`, `apparence`=`mur` (face 156 dans `Murs` ; le code pose 157 dans `Decor`) |
| 4 | `Ramassable` | (560, 176) | `id`=`foret_receptacle_secret`, `contenu`=`receptacle` |
| 5 | `Ramassable` | (112, 144) | `id`=`foret_grotte_rubis_01`, `contenu`=`rubis_vert` |
| 6 | `Ennemi` | (208, 176) | `type`=`ronceau`, `variante`=`normal` |
| 7 | `Ennemi` | (304, 240) | `type`=`ronceau`, `variante`=`normal` |

Pose de la bombe : Brann se place en (13,5), pose la bombe contre le mur en (14,5), puis **recule** vers l'ouest : la salle offre 5 cases libres sur la ligne 5 (colonnes 9 à 14). Les 2 Ronceaux garantissent le **butin de bombes** si Brann en manque (`LootDropper.BombsBelow` = 3, ils réapparaissent à chaque retour) et ne sont pas dans la ligne de recul.

## 4. Tuiles à demander au graphiste et nouveautés de code

### 4.1 Réutilisation maximale

Le tileset `village` contient déjà **toute** la rive : eau peu profonde, eau profonde, ponton, roseaux, nénuphars, rocher dans l'eau, éboulis et falaises ; `montagne` contient le mur fissuré, les rochers et les falaises de la grotte. On ne change **aucun id** déjà reconnu par `TileRules` (éboulis `village` 136-139 / 140-141, face fissurée `montagne` 156 / 157, buissons) ni `TileFeatures` (ravin 80-95, buissons). Aucun code de tuile n'est à ajouter.

### 4.2 Nouveau tileset `lac` (plan d'abord, puis dessin) : uniquement ce qui manque

À créer en plus des tilesets existants (aucune tuile existante ne bouge). Numéros locaux à fixer par le graphiste dans `art/tilesets/lac_plan.md`.

| Groupe | Tuiles | Calque | Collision |
| --- | --- | --- | --- |
| Cascade | `cascade_haut` (roche + chute), `cascade_voile_a` et `cascade_voile_b` (rideau d'eau **semi-transparent**, 2 images pour l'animation), `cascade_voile_pied` (écume), `cascade_bassin` (eau peu profonde avec écume), `alcove_sol` (roche mouillée), `cascade_gauche`/`droite` (jambages de roche) | Murs / Dessus / Sol | `cascade_haut` : pleine ; `voile_*` : **aucune** (Dessus) ; `bassin`, `alcove_sol` : aucune |
| Sanctuaire Englouti (façade) | fronton 3×2, pilastres, colonnes brisées (2 variantes), marches immergées, portail 2 cases (haut linteau, bas ouvert, la `Sortie` est dessus), mur à demi noyé (algues, 2 variantes), pilier massif | Murs / Dessus | solides sauf marche et seuil |
| Quai | dalles de pierre mouillées (3 variantes), bord de quai (haut, bas, côté), bitte, jonction ponton - quai | Sol / Murs / Decor | bord : partielle ; dalles : aucune |
| Îlot et gué | herbe/sable d'îlot (3 variantes), pierres plates du gué (Decor), jambage de gué | Sol / Decor | aucune |
| Ambiance | algues flottantes, reflets/éclaboussures, ruines immergées (dalle, bloc), coquillages | Decor | aucune |

Environ 35 tuiles. Les images de porte `art/puzzles/porte_rocher.png` et `porte_eboulis.png` existent (`Porte` généralisée) ; il faut juste une **variante « dans l'eau »** du rocher si le graphiste le juge utile (`porte_rocher_eau.png` : le code ne la lit pas encore, voir 4.3, donc à n'ajouter que si le développeur le décide). La cible `Interrupteur` utilise le symbole existant (`feuille`).

### 4.3 Côté code et scènes (les nouveautés sont marquées NOUVEAU)

1. **NOUVEAU - ennemi `tetard_encre`** : `scenes/enemies/tetard_encre.tscn`, script **existant** `ErrantEnemy` (aucun nouveau comportement), données : 2 PV, dégâts 1 cœur au contact, sprites `art/enemies/tetard_encre_frames.tres`. « Éclabousse » = effet visuel seulement. **Repli sans code** si la scène n'est pas prête : mettre `caillou_rampant` (mêmes statistiques) dans les 5 emplacements, à remplacer ensuite.
2. **Pas de nouveauté de code** pour : l'éboulis multi-cases (`MurFissure` accepte un rectangle de taille libre), le rocher dans le gué (`Porte` `apparence`=`rocher`, type `interrupteur`, sans `Sortie`), la cible (`Interrupteur` `fleche`), la brume, `etape_max`, la face fissurée de la grotte, le quart de cœur (`quart_coeur.tres`), la plume, la statue, le réceptacle (`receptacle.tres`).
3. **NOUVEAU (à vérifier, a priori sans code)** : le **rideau de cascade traversable** est un calque `Dessus` de tuiles sans collision ; la `Room` donne `z_index` 2 au calque `Dessus`, donc Brann passe sous l'eau. Vérifier seulement que les tuiles semi-transparentes sont bien dessinées avec transparence dans Godot.
4. **NOUVEAU (facultatif, différé)** : confiner le Têtard à l'eau peu profonde (une zone interdite aux ennemis terrestres) et ralentir Brann dans l'eau peu profonde. Aucun des deux n'est nécessaire à ce plan (le Têtard erre aussi sur le ponton et la rive, ce qui reste un combat correct) : à étudier plus tard avec le développeur.
5. **NOUVEAU - scènes** : `scenes/rooms/lac_room.tscn` (Zone `lac`) et `scenes/rooms/grotte_sw_room.tscn` (Zone `foret`), instanciant `maps/overworld/lac.tmx` et `grotte_sw.tmx`. `donjon3_salle_01_room.tscn` n'existe pas encore : repli `Room.MissingExitFallbackScene`.
6. **Convention d'id** : `lac_eboulis_rive`, `lac_rocher_ilot`, `lac_cible_ilot`, `lac_quart_coeur_cascade`, `lac_quart_coeur_ilot`, `lac_plume_01`, `lac_rubis_01/02`, `lac_statue_ponton`, `foret_grotte_mur_secret`, `foret_receptacle_secret`, `foret_grotte_rubis_01`. À ajouter ensuite à `CLAUDE.md` (spawns `depuis_lac`, `depuis_sanctuaire`).

## 5. Vérification

Script (hors dépôt) : une grille 80×11 et une grille 20×11 sont bâties telles qu'affichées plus haut ; parcours en 4 connexités depuis le Spawn d'arrivée, `#` `~` `F` `r` `Y` `b` solides (les buissons deviennent praticables une fois coupés), `w` `=` `c` praticables.

| Test | Résultat |
| --- | --- |
| Zone atteinte depuis l'arrivée sans rien casser (lac) | colonnes 0 à 24 seulement : l'éboulis (25-26) barre bien l'isthme, aucun contournement par l'eau |
| Éboulis visible depuis la plage | oui (accessible en 5 cases de l'arrivée, case voisine atteignable) |
| Après l'éboulis et les buissons : statue, portail du Sanctuaire, goulet de la cible, gué, alcôve de la cascade, niche de la plume | tous atteignables |
| Îlot (54,9) avant d'avoir ouvert le rocher / après | inatteignable / atteignable (donc le rocher est bien le seul verrou) |
| Ligne de tir colonne 58, de (58,5) à (58,9) | ponton, ponton, eau peu profonde, eau peu profonde, cible : aucune case solide avant la cible |
| Grotte : réceptacle avant / après la bombe | inatteignable / atteignable ; case de pose (14,5) atteinte sans rien casser ; 6 cases libres sur la ligne de recul |
| Objets sur une case solide ou une Sortie | aucun (Spawns et ennemis sur des cases libres) |

Cohérence de progression :
- **Chaque blocage est visible avant d'être franchissable** : l'éboulis (dès l'arrivée, avec le lac visible derrière), la fissure de la grotte (dès l'étape 0), le rocher du gué et sa cible (depuis le ponton), la niche à buissons de la plume, le rideau et l'éclat dans l'alcôve de la cascade.
- **Aucun objet exigé avant d'être obtenu** : bombes (donjon 2) pour l'éboulis et la fissure ; arc (donjon 1) pour la cible ; épée pour les buissons ; **pas de lanterne**. Le Sanctuaire s'atteint sans rien d'autre que l'éboulis.
- **Pas de soft-lock** : aucun bloc, aucun trou, aucune porte à clé ; l'éboulis, le rocher et le mur fissuré sont des états sauvegardés par `id` ; l'eau profonde ne blesse pas. Bombes : les ennemis du lac et de la grotte lâchent du butin de bombes sous 3 en stock, ils réapparaissent à chaque retour, et la boutique de Garrick en vend. Le Sanctuaire est ré-accessible à tout moment (portail ouvert).
- **Import Godot** : non lançable à ce stade (aucun `.tmx` n'existe encore).

## 6. Décisions (validées le 2026-10-31)

L'utilisatrice a validé les quatre recommandations : (1) îlot ouvert à l'**arc** (cible + rocher) ; (2) grotte du sud-ouest en Zone `foret` (ids `foret_receptacle_secret`, `foret_grotte_*`) ; (3) **Têtard d'encre créé maintenant** (type `tetard_encre`, scène en cours côté développeur) ; (4) cascade **libre**. Le détail des options reste ci-dessous.

1. **Quart de cœur de l'îlot : arc (cible dans l'eau) ou bombe ?** Recommandation : **arc**. La cible est un geste que le joueur connaît déjà (forêt), la bombe a son moment avec l'éboulis, et l'arc fait vivre le ponton (on s'arrête pour viser). L'alternative (un éboulis dans le gué) ferait trois blocages à la bombe de suite (éboulis, grotte, îlot).
2. **Zone de la grotte du sud-ouest : `foret` ou une zone à part (`grotte`) ?** Recommandation : **`foret`**, donc les ids `foret_receptacle_secret` et `foret_grotte_*` : pas de sauvegarde automatique parasite en entrant dans un cul-de-sac, et le réceptacle compte comme un secret de la forêt. (Ce que l'on perd : rien, la grotte n'a pas de musique propre prévue.)
3. **Têtard d'encre : créer l'ennemi maintenant (réutilisation de `ErrantEnemy`, nouveau sprite) ou utiliser le Caillou rampant en attendant ?** Recommandation : **créer le Têtard** (un `.tscn` + un sprite, aucun code) ; le Caillou rampant sert de repli pour tester la carte tout de suite. Sans confinement à l'eau ni ralentissement (voir 4.3 point 4).
4. **Cascade : secret entièrement libre (aucun objet) ou fermer l'alcôve (par exemple un mur fissuré à la bombe) ?** Recommandation : **libre**, c'est le secret « d'observation » du lac ; les trois autres secrets du plan (éboulis, îlot, grotte) utilisent déjà bombe et arc. Hors plan, à trancher plus tard : un PNJ pêcheur sur la berge à l'étape 2 (indice sur le Sanctuaire) coûterait un sprite et un dialogue.
