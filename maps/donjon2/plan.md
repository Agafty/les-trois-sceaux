# Plan de la Mine Effondrée (donjon 2) - 16 salles sur deux étages

Document de conception (étape 1). **Aucun `.tmx` n'existe encore** : on attend la validation de ce plan. Même niveau de détail et même format que `maps/donjon1/plan.md` (le plan du Temple des Racines v2), dont les règles de raccord sont reprises telles quelles.
Les aperçus de ce fichier ont été relus par un script de vérification (bibliothèque standard seulement : taille des salles, ouvertures, accessibilité des objets, solution de la salle 05, temps de la salle 06, parcours sur l'état du joueur) ; résultats au §5.

## 1. Intention et courbe de difficulté

**Intention** : donjon des **bombes**. Brann a l'arc depuis le Temple ; ici il apprend à **poser une bombe contre un mur fissuré ou un éboulis**, à **se mettre à distance du souffle**, à **faire tomber le bouclier d'un mineur**, puis à **combiner** bombes et arc (ouvrir un éboulis pour tirer à travers, ouvrir le vestibule d'une porte à clé). La Mine est un peu plus dure que le Temple : plus d'ennemis à bouclier, une salle de tir à trois cibles, un sous-sol où chaque salle demande une bombe. Public : un adulte qui découvre, et un enfant de 5 ans qui joue aidé (combats faciles, aucune énigme ne coûte de point de vie, les fosses mortelles sont toujours hors du chemin).

**Récit** : les poutres de la Mine ont été sciées (indice : le **marteau au poinçon de Corvan**, ramassé en salle 08, sur le chemin obligatoire) ; Gorm, le golem de la Mine, est devenu fou. Le **minerai d'étoile** (obligatoire pour l'Épée trempée) est dans un coffre de la salle 13, que l'on ne peut pas éviter.

| Étape | Salle | Ce qui est appris ou testé | Tension |
| --- | --- | --- | --- |
| 1 | 01 Entrée | Le Caillou rampant (3 coups) ; statue du corbeau | très faible |
| 2 | 02 Hall des wagons | Carte ; la porte à clé nord est visible ; trois chemins ; rails et wagonnets en décor | faible |
| 3 | 03 Dépôt de minerai (facultative) | Chauve-souris (vol en zigzag) ; **premier mur fissuré**, vu mais pas franchissable (quart de cœur à prendre plus tard) | moyenne, optionnelle |
| 4 | 04 Galerie des bennes | Porte « tous les ennemis morts » ; boussole ; **trou de passage** vers la cave secrète | moyenne |
| 5 | 15 Cave secrète | Atterrissage calme ; **petite clé n°2** | repos |
| 6 | 05 Salle des wagonnets | **2 blocs sur 2 plaques** (wagonnets) ; petite clé n°1 visible derrière une grille | réflexion, peu de combat |
| 7 | 06 Salle de tir | **3 cibles en 10 s** à l'arc, au-dessus de fosses | moyenne-haute (chrono) |
| 8 | 07 Salle du grand coffre | **Bombes** ; un éboulis bloque la sortie : première bombe, sans danger | moyenne puis démo calme |
| 9 | 08 Galerie des étais | **Mineur maudit** seul (bombe ou contournement) ; marteau de Corvan ; **petite clé n°3** derrière un mur fissuré | moyenne |
| 10 | 09 Carrefour effondré | 2 Mineurs maudits ; mur épais (3 cases) qui cache une plume | haute |
| 11 | 10 Antichambre | Porte du boss et statue visibles, **grande clé absente** ; levier-raccourci ; escalier vers le sous-sol | moyenne |
| 12 | 11 Galerie basse | Arrivée au sous-sol ; grille-raccourci vue de l'ouest | calme |
| 13 | 12 Salle du brasero | **Bombe puis arc** : l'éboulis cache la ligne de tir brasero - torche | moyenne |
| 14 | 13 Veine d'étoile | **Minerai d'étoile** (coffre libre) ; vestibule bouché : bombe, porte à clé | calme puis moyenne |
| 15 | 14 Réserve de Gorm | 2 Mineurs + chauve-souris ; **grande clé** derrière un mur fissuré ; levier-raccourci | haute (défi final) |
| 16 | Boss | Gorm : bombes sur les plaques d'armure, puis épée sur le cristal | boss |

Rythme : calme (01) - fight léger (02) - fight (04) - **repos** (15) - réflexion (05) - chrono (06) - démo (07) - fight à bouclier (08) - fight dur (09) - calme (10, 11) - bombe + arc (12) - calme (13) - défi (14) - retour rapide - boss. Les salles 03 et la plume de la 09 sont des plaisirs facultatifs.

## 2. Règles de raccord (valables pour toutes les salles)

Identiques au Temple (`maps/donjon1/plan.md` §2) : salle 20x11, mur du pourtour d'une case, **une seule position pour chaque ouverture** (nord (9,0), sud (9,10) ou (9,21) pour le boss, ouest (0,5), est (19,5)), `Spawn` d'arrivée `depuis_<côté>` à (9,2), (9,8), (2,5), (17,5), une `Porte` par face dans chacune des deux salles avec le même `id`, déclencheur toujours dans une salle qui contient une face de sa porte, un seul escalier par salle (`Spawn` `depuis_escalier` sur la case voisine), trous de passage `Chute` (jamais à moins de 2 cases d'un `Spawn` d'arrivée), fosses mortelles 58-66, blocs jamais dans une salle à trous, à cibles ou à torches, jamais sur ou à côté d'un `Spawn`/`Sortie`/`Porte`. Dans la salle 01, l'arrivée du dehors s'appelle `depuis_montagne` (le `Sortie` de `montagne.tmx` vise `donjon2_salle_01_room.tscn` / `depuis_montagne`) et la `Sortie` sud de la salle 01 vise `montagne_room.tscn` / `depuis_mine` (ce `Spawn` existe déjà dans `montagne.tmx`).

**Règles propres aux bombes** (relevées dans `Bomb.cs`, `CrackedWall.cs`, `MinerEnemy.cs`) :
- Bombe : mèche 1,5 s, **rayon du souffle 40 px**, **1 PV de dégâts à Brann** s'il est dans le rayon, 3 PV aux ennemis, une seule bombe posée à la fois. Stock maximal **10** (`GameState.GetMaxQuantity`), le grand coffre en donne **5** (`objet_bombes`), un paquet au sol en donne 5 (`boutique_bombes`, posé seulement si Brann possède déjà les bombes).
- Portée mesurée **jusqu'au bord** du destructible : une bombe détruit les murs fissurés des **8 cases voisines** de la case où elle est posée (pas ceux à 2 cases). Un mur fissuré est donc cassé en se plaçant à côté, en posant la bombe contre lui, puis en **reculant d'au moins 2 cases** pendant la mèche. Chaque cible bombée est toujours précédée de **3 cases libres** pour reculer.
- Mur fissuré : `MurFissure`, état mémorisé par `id` ; sur une ouverture de salle il recouvre la `Sortie` (`apparence` = `eboulis`).
- Mineur maudit (déjà codé) : le bouclier bloque l'épée **et les flèches de face** ; de côté ou de dos il est vulnérable ; une bombe à portée le fait tomber (étourdi 4 s, sans bouclier). Il n'est donc **jamais obligatoire de le bomber** : le contourner suffit (donc aucun blocage possible).
- **Munitions de bombes (anti-blocage)** : trois sources, détaillées au §3 : le grand coffre (5), des paquets au sol (`donjon2_bombes_01` à `04`, uniques), et surtout le **butin de bombes garanti** (NOUVEAU, §7) : tant que Brann a moins de 3 bombes, chaque ennemi vaincu lâche un paquet. Chaque salle à bombe contient au moins un ennemi qui n'est pas un Mineur (Caillou ou Chauve-souris), et les ennemis réapparaissent à chaque retour dans la salle : on ne peut donc jamais rester sans bombe devant un mur obligatoire.
- Arc : comme dans le Temple (flèche 300 px/s, 10 cases de portée, butin de flèches garanti sous 10 flèches). Les salles de tir (06, 12) contiennent un ennemi qui ne tire pas.

## 3. Plan des salles

```text
ÉTAGE (rez-de-chaussée : les galeries)

                                [boss]
                                 G
                                 |
                                [10]=====D=====[09]
                                 I              N
                                 |              |
                 [06]=====I=====[07]=====e=====[08]
                  D
                  |
  [03]-----------[02]-----------[04]=====N=====[05]
                  |
                  |
                 [01]

SOUS-SOL (le fond de la mine)

  [11]=====I=====[14]
   |              D
   |              |
  [12]=====I=====[13]

      [15]  (cave secrète, seulement par l'escalier 05-15 ou le trou 04 -> 15)

Liens d'étage : escaliers 05-15 et 10-11 ; trou de passage 04 -> 15 (sens unique).
Légende : - passage libre, D petite clé, G grande clé, N tous les ennemis morts, I interrupteur (levier, cibles ou torche),
e éboulis à la bombe, = porte ou passage entre deux salles. Raccourcis : 07-10 (levier de la 10), 11-14 (levier de la 14).
```

Position des salles (carte du menu pause : propriétés de carte `etage`, `carte_x`, `carte_y`, même sens que le Temple : y augmente vers le boss) :

| Étage | Salle | (x, y) | Étage | Salle | (x, y) |
| --- | --- | --- | --- | --- | --- |
| `rdc` | 01 | (1, 0) | `sous_sol` | 11 | (2, 3) |
| `rdc` | 02 | (1, 1) | `sous_sol` | 12 | (2, 2) |
| `rdc` | 03 | (0, 1) | `sous_sol` | 13 | (3, 2) |
| `rdc` | 04 | (2, 1) | `sous_sol` | 14 | (3, 3) |
| `rdc` | 05 | (3, 1) | `sous_sol` | 15 | (3, 1) |
| `rdc` | 06 | (1, 2) | | | |
| `rdc` | 07 | (2, 2) | | | |
| `rdc` | 08 | (3, 2) | | | |
| `rdc` | 09 | (3, 3) | | | |
| `rdc` | 10 | (2, 3) | | | |
| `rdc` | boss | (2, 4) | | | |

| Élément | Lieu |
| --- | --- |
| Statues du corbeau | salle 01 (`donjon2_statue_01`, entrée) et salle 10 (`donjon2_statue_02`, avant le boss et avant l'escalier) |
| Carte | salle 02, `donjon2_coffre_01` (en vue dès l'arrivée) |
| Boussole | salle 04, `donjon2_coffre_02` |
| Petite clé n°1 | salle 05, `donjon2_coffre_03` (derrière la grille des plaques) |
| Petite clé n°2 (cachée) | salle 15, `donjon2_coffre_06` (cave atteinte par le trou de la 04 ou l'escalier de la 05) |
| **Bombes** | salle 07, `donjon2_coffre_04` (grand coffre ; 7e salle sur 16 dans l'ordre conseillé, donc vers le **milieu** du parcours) |
| Petite clé n°3 | salle 08, `donjon2_coffre_05` (derrière un mur fissuré : demande les bombes) |
| **Minerai d'étoile** (obligatoire pour l'Épée trempée) | salle 13, `donjon2_coffre_07` (`important`=true, coffre libre, en vue dès l'arrivée, sur le chemin obligatoire) |
| **Grande clé** | **salle 14 (sous-sol)**, `donjon2_coffre_08` (grand coffre, derrière un mur fissuré) ; sert à la porte 07, **à l'étage du dessus**, dans la salle 10 (la porte du boss n'est pas dans la salle de la clé) |
| **Marteau au poinçon de Corvan** (indice d'histoire) | salle 08, `donjon2_marteau_corvan` (ramassable posé au pied d'une poutre sciée ; indice `indice_poutres_sciees`) |
| Quart de cœur (facultatif) | salle 03, `donjon2_quart_coeur_01` (derrière le premier mur fissuré, qu'on voit dès le début et qu'on ouvre après les bombes) |
| Plume de corbeau (facultative) | salle 09, `donjon2_plume_01` (derrière un mur épais de 3 cases) |
| Paquets de bombes (uniques) | `donjon2_bombes_01` (07), `_02` (08), `_03` (09), `_04` (14) |
| Boss | salle boss (au nord de la 10) |

| Porte | Entre | Type | Ouverture |
| --- | --- | --- | --- |
| `donjon2_porte_01` | 02 (nord) et 06 (sud) | `cle` | une petite clé |
| `donjon2_porte_02` | 04 (est) et 05 (ouest) | `ennemis` | salle 04 nettoyée |
| `donjon2_porte_03` | 06 (est) et 07 (ouest) | `interrupteur` | 3 cibles de flèche en 10 s (salle 06) |
| `donjon2_porte_04` | 08 (nord) et 09 (sud) | `ennemis` | salle 08 nettoyée |
| `donjon2_porte_05` | 09 (ouest) et 10 (est) | `cle` | une petite clé |
| `donjon2_porte_06` | 07 (nord) et 10 (sud) | `interrupteur` | levier à l'épée (salle 10) : **raccourci** |
| `donjon2_porte_07` | 10 (nord) et boss (sud) | `grande_cle` | grande clé |
| `donjon2_porte_08` | 13 (nord) et 14 (sud) | `cle` | une petite clé (derrière le vestibule bouché de la 13) |
| `donjon2_porte_09` | 12 (est) et 13 (ouest) | `interrupteur` | torche (15,5) allumée par une flèche enflammée (salle 12) |
| `donjon2_porte_10` | 11 (est) et 14 (ouest) | `interrupteur` | levier à l'épée (salle 14) : **raccourci** |
| `donjon2_porte_11` | grille intérieure de la 05 (9,8) | `interrupteur` | 2 plaques (14,3) et (17,3) avec 2 blocs : petite clé n°1 |

| Mur fissuré / éboulis | Lieu | Effet |
| --- | --- | --- |
| `donjon2_mur_01` | 03 (3,2) | alcôve du quart de cœur (facultatif) |
| `donjon2_mur_02` | 07 est (19,5) et 08 ouest (0,5), `eboulis`, **même id des deux côtés** | passage obligatoire vers 08 (première bombe) |
| `donjon2_mur_03` | 08 (16,2) | alcôve de la petite clé n°3 (obligatoire) |
| `donjon2_mur_04` à `06` | 09 (16,1), (16,2), (16,3) | mur épais, alcôve de la plume (facultatif) : une bombe posée en (15,2) casse les trois |
| `donjon2_mur_07` | 12 (11,5), `eboulis` | ouvre la ligne de tir brasero - torche (obligatoire) |
| `donjon2_mur_08` | 13 (9,3), `eboulis` | vestibule de la porte à clé 08 (obligatoire) |
| `donjon2_mur_09` | 14 (3,2) | alcôve de la grande clé (obligatoire) |

| Lien d'étage | Départ | Arrivée | Sens |
| --- | --- | --- | --- |
| `donjon2_escalier_01` | 05, tuile (1,1) | 15, tuile (1,2) | deux sens |
| `donjon2_escalier_02` | 10, tuile (18,8) | 11, tuile (18,2) | deux sens |
| `donjon2_chute_04` | 04, trou (1..2, 8..9) | 15, Spawn (9,5) | **sens unique** (vers le bas) |

**Économie des clés** : 3 petites clés (n°1 en 05, n°2 en 15, n°3 en 08, derrière un mur fissuré) pour 3 portes à clé (01, 05, 08). Les clés sont interchangeables. Les trois portes sont **obligatoires** (le vérificateur condamne chacune tour à tour : le boss devient inatteignable) et les trois clés sont nécessaires, donc aucune clé n'est gaspillable. Les clés n°1 et n°2 sont atteignables **sans** aucune porte à clé (donc sans bombes), la clé n°3 seulement après les bombes mais avant toute autre porte à clé que la 01 : quel que soit l'ordre, il reste toujours une clé ou un moyen d'en trouver une. La grande clé n'ouvre que la porte du boss, elle est **au sous-sol** alors que la porte est à l'étage, et elle est derrière la porte à clé 08 et un mur fissuré.

**Munitions de bombes salle par salle** (bombes nécessaires pour la suite obligatoire / ce qui les fournit) :

| Salle | Bombes obligatoires | Source disponible avant cette salle |
| --- | --- | --- |
| 07 | 1 (`donjon2_mur_02`) | grand coffre (5) dans la même salle, paquet `donjon2_bombes_01` (5), 2 Cailloux |
| 08 | 1 (`donjon2_mur_03`) | il reste au moins 4 bombes en arrivant, paquet `_02`, 1 Caillou |
| 09 | 0 (plume : 1 si bien placée) | paquet `_03`, 1 Caillou |
| 12 | 1 (`donjon2_mur_07`) | butin garanti des 2 Cailloux, stock restant |
| 13 | 1 (`donjon2_mur_08`) | butin garanti de la Chauve-souris et du Caillou rouge |
| 14 | 1 (`donjon2_mur_09`) | paquet `_04`, butin garanti de la Chauve-souris |

**Parcours conseillé** (celui que le vérificateur retrouve, à quelques détours facultatifs près) :
1. 01 (statue), puis le Hall 02 (carte ; la porte nord est verrouillée, on le voit).
2. 03 (facultative : le mur fissuré est vu, on reviendra), 04 (nettoyer les 3 ennemis, boussole).
3. Trou de passage de la 04 : cave secrète 15 (petite clé n°2) ; escalier de retour jusqu'à la 05 (ou à pied par la porte est de la 04).
4. 05 : deux blocs sur deux plaques, la grille s'ouvre, petite clé n°1.
5. Retour par 04 et 02 : porte nord (une clé), 06 : trois cibles en 10 s, porte est.
6. 07 : grand coffre des **bombes**, première bombe sur l'éboulis de l'est, 08.
7. 08 : marteau de Corvan (indice), Mineur maudit, bombe sur l'alcôve (petite clé n°3), porte « ennemis » ; 09 : deux Mineurs ; porte à clé (une clé) ; 10 : statue, porte du boss visible, **escalier**.
8. Sous-sol : 11 (calme), 12 (bombe sur l'éboulis, flèche à travers le brasero pour allumer la torche), 13 (**minerai d'étoile**, bombe sur le vestibule, porte à clé), 14 (deux Mineurs, bombe sur l'alcôve, **grande clé**, levier-raccourci).
9. Retour : grille du levier vers 11, escalier vers 10, porte du boss (grande clé), Gorm.

**Ordres possibles** : la cave 15 et la 05 peuvent être faites dans n'importe quel ordre ; 03 et le mur épais de la 09 sont facultatifs et peuvent être faits à tout moment après le coffre des bombes (retours en arrière encouragés par la carte, qui montre les salles non visitées) ; le levier de la 10 et celui de la 14 sont des raccourcis (oublis sans conséquence) ; le trou de la 04 est sens unique mais l'escalier de la 15 ramène à la 05.

**Chaque blocage est visible avant d'être franchissable** :

| Blocage | Où on le voit | Où on le franchit |
| --- | --- | --- |
| Porte à clé 01 (Hall) | dès l'arrivée dans 02 | après la clé n°1 ou n°2 |
| Cibles de la 06 | dès l'entrée dans 06 (derrière la porte est fermée) | à l'arc (déjà acquis) |
| Grille de la clé n°1 | dans 05, avant les blocs | deux blocs sur deux plaques |
| Mur fissuré de la 03 | dès la première visite de 03 | après les bombes |
| Éboulis de la 07 | dans 07, en vue du grand coffre et du paquet de bombes | bombes |
| Alcôve de la clé n°3 | dans 08 | bombes |
| Porte du boss | dans 10, avant même de descendre | grande clé de la 14 |
| Brasero, torche et éboulis | dans 12, tout est visible d'un coup | bombe puis arc |
| Vestibule bouché de la 13 | dans 13, avec la porte à clé au fond | bombe puis clé |
| Alcôve de la grande clé | dans 14 | bombes |
| Grille vers 11 (levier) | dans 11 (côté bloqué) | levier de la 14 |
| Raccourci 07 - 10 | dans 07 (porte fermée côté nord) | levier de la 10 |

Légende des aperçus : `#` mur, `.` sol, `~` fosse mortelle, `T` trou de passage, `O` pilier ou mur isolé, `c` Caillou rampant, `r` Caillou rampant rouge, `b` Chauve-souris des mines, `m` Mineur maudit, `g` Gorm (boss), `P` Spawn d'arrivée, `C` coffre, `S` cible de flèche, `l` levier (interrupteur à l'épée), `f` torche éteinte, `Y` brasero, `B` bloc poussable (wagonnet), `p` plaque de pression, `M` mur fissuré, `e` éboulis (MurFissure `eboulis`), `o` paquet de bombes (ramassable), `Q` quart de cœur, `F` plume, `H` marteau de Corvan, `R` statue du corbeau, `v` escalier descendant, `^` escalier montant, `X` passage libre, `D` porte petite clé, `G` porte grande clé, `N` porte ennemis, `I` porte interrupteur (porte entre deux salles ou grille intérieure). Sur un bord, `M` et `e` recouvrent une ouverture.

## 4. Les salles

### salle_01 - Entrée de la Mine

Premier pas, volontairement identique à l'entrée du Temple : un seul Caillou rampant, loin de l'arrivée, dans une grande salle ; la statue du corbeau est à côté de l'arrivée. On y apprend que le Caillou demande 3 coups (il ne fuit pas). Rails et wagonnets en décor.

<!-- salle_01 -->
```text
#########X##########
#..................#
#........P.........#
#..............c...#
#....O........O....#
#..................#
#..................#
#....O.............#
#........P...R.....#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon2_salle_02_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/montagne_room.tscn, `cible_spawn`=`depuis_mine`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (304,272) : `id`=`depuis_montagne`
- `Ennemi` point (496,112) : `type`=`caillou_rampant`, `variante`=`normal`
- `StatueCorbeau` (13,8) -> centre (432,272) : `id`=`donjon2_statue_01`

### salle_02 - Hall des wagons

Carrefour : deux Cailloux, trois sorties libres (ouest, est, sud) et une **porte à clé au nord, visible dès l'arrivée**. Le coffre de la carte est en vue. Un faisceau de rails au sol mène vers les trois sorties (guide visuel).

<!-- salle_02 -->
```text
#########D##########
#..................#
#........P.....C...#
#.....O......O.....#
#..................#
X.P....c.........P.X
#...........c......#
#.....O......O.....#
#........P.........#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`).

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon2_salle_06_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon2_porte_01`, `type`=`cle`
- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon2_salle_01_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_03_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_04_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Coffre` point (496,80) : `id`=`donjon2_coffre_01`, `contenu`=`carte_donjon`, `important`=false
- `Ennemi` point (240,176) : `type`=`caillou_rampant`, `variante`=`normal`
- `Ennemi` point (400,208) : `type`=`caillou_rampant`, `variante`=`normal`

### salle_03 - Dépôt de minerai (facultative)

Impasse facultative. Une Chauve-souris (elle zigzague : on apprend à l'attendre et à la frapper quand elle mord) et un Caillou. Dans l'angle nord-ouest, une alcôve fermée par un **mur fissuré** (visible, fissures claires) avec un **quart de cœur** : c'est le premier mur fissuré que le joueur voit, **avant d'avoir les bombes** ; il y reviendra. L'alcôve se casse en se plaçant en (4,2), bombe posée contre le mur, puis en reculant vers l'est (6 cases libres).

<!-- salle_03 -->
```text
####################
#Q.#...............#
#..M...............#
####...............#
#.....O.........O..#
#................P.X
#..................#
#..................#
#...b..........c...#
#..................#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_02_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ramassable` point (48,48) : `id`=`donjon2_quart_coeur_01`, `contenu`=`quart_coeur`
- `Ennemi` point (144,272) : `type`=`chauve_souris`, `variante`=`normal`
- `Ennemi` point (496,272) : `type`=`caillou_rampant`, `variante`=`normal`
- `MurFissure` (96,64,32,32) : `id`=`donjon2_mur_01`, `apparence`=`mur`

### salle_04 - Galerie des bennes

Porte « ennemis » et **trou de passage**. Deux Cailloux et une Chauve-souris ; la porte est du côté est, fermée tant qu'ils ne sont pas tous morts. Le coffre de la boussole attend au fond. Dans l'angle sud-ouest, un trou 2x2 d'aspect différent des fosses mortelles (puits à échelle brisée, lueur chaude au fond) : on peut y sauter sans dégât et on atterrit dans la cave secrète (salle 15).

<!-- salle_04 -->
```text
####################
#..................#
#.....c........C...#
#............O.....#
#....O.............#
X.P.......b......P.N
#....O.............#
#............O.....#
#TT...........c....#
#TT................#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_02_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_05_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon2_porte_02`, `type`=`ennemis`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Chute` (32,256,64,64) : `id`=`donjon2_chute_04`, `cible_carte`=res://scenes/rooms/donjon2_salle_15_room.tscn, `cible_spawn`=`depuis_chute_salle_04`, `godot_node_type`=`area`
- `Ennemi` point (208,80) : `type`=`caillou_rampant`, `variante`=`normal`
- `Coffre` point (496,80) : `id`=`donjon2_coffre_02`, `contenu`=`boussole`, `important`=false
- `Ennemi` point (336,176) : `type`=`chauve_souris`, `variante`=`normal`
- `Ennemi` point (464,272) : `type`=`caillou_rampant`, `variante`=`normal`

### salle_05 - Salle des wagonnets

**Deux blocs (deux wagonnets de minerai), deux plaques.** Variante en miroir vertical de la salle 05 du Temple, dont la solution est prouvée : une rangée de chevalets coupe la salle en deux ; au sud, derrière la brèche, un coffre dans une alcôve fermée par une grille (la petite clé n°1 est visible sans être prenable). Au nord, un couloir d'une case de large contient deux plaques (14,3) et (17,3) et deux wagonnets attendent dans la zone ouest. L'escalier vers la cave secrète (salle 15) est dans l'angle nord-ouest, visible dès l'arrivée.

Solution (25 pousses minimum, vérifiées) : monter ou descendre chaque bloc d'une case pour l'aligner sur la rangée 3, puis le pousser vers l'est dans le couloir : le premier jusqu'à la plaque du fond (17,3), le second jusqu'à (14,3). Quand les deux plaques sont pressées en même temps, la grille (9,8) s'ouvre définitivement. Si on se trompe, **sortir de la salle et revenir remet les blocs à leur place**. Un Caillou (butin) rôde au sud.

<!-- salle_05 -->
```text
####################
#vP................#
#...B.....##########
#.............p..p##
#...B.....##########
N.P................#
#OOOOOOO...OOOOOOOO#
#..................#
#........I....c....#
#.......#C#........#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_04_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon2_porte_02`, `type`=`ennemis`
- `Sortie` (32,32,32,32) sur la tuile d'escalier : `cible_carte`=res://scenes/rooms/donjon2_salle_15_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (80,48) : `id`=`depuis_escalier`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Ennemi` point (464,272) : `type`=`caillou_rampant`, `variante`=`normal`
- `Coffre` point (304,304) : `id`=`donjon2_coffre_03`, `contenu`=`cle_petite`, `important`=false
- `BlocPoussable` (4,2) -> centre (144,80) et (4,4) -> centre (144,144)
- `PlaqueDePression` (448,96,32,32) : `id`=`donjon2_plaque_01`, `cible`=`donjon2_porte_11`, `declencheur`=`bloc`, `godot_node_type`=`area`
- `PlaqueDePression` (544,96,32,32) : `id`=`donjon2_plaque_02`, `cible`=`donjon2_porte_11`, `declencheur`=`bloc`, `godot_node_type`=`area`
- `Porte` (288,256,32,32) intérieure (grille) : `id`=`donjon2_porte_11`, `type`=`interrupteur`

### salle_06 - Salle de tir

**Trois cibles à toucher en moins de 10 secondes.** Les cibles sont visibles dès l'entrée, derrière la porte est fermée : deux au bout de fosses (nord-est et sud-est), une dans le mur ouest. Des piliers interdisent le tir depuis les angles faciles (la cible ouest ne se tire pas depuis l'est de la rangée 5 à cause du pilier (5,5), il faut passer par la colonne 1 ou par les cases (2..4,5)). L'enchaînement le plus court prend **6,6 s** (66 % du temps accordé) : confortable pour un adulte, et l'option d'aide double la durée pour l'enfant. Un chronomètre visible sur chaque cible (anneau qui se vide). Deux Cailloux (butin de flèches). Les fosses sont mortelles (1 PV, retour à l'entrée) mais jamais sur le chemin.

<!-- salle_06 -->
```text
####################
#.............~~~~~#
#.............~~~~S#
#.............~~~~O#
#..c...............#
#S...O...........P.I
#...........c......#
#.............~~~~O#
#........P....~~~~S#
#.............~~~~~#
#########D##########
```

Objets Tiled (calque `Objets`).

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon2_salle_02_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon2_porte_01`, `type`=`cle`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_07_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon2_porte_03`, `type`=`interrupteur`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Interrupteur` (18,2) -> centre (592,80) : `id`=`donjon2_interrupteur_01`, `cible`=`donjon2_porte_03`, `mode`=`fleche`, `duree`=10
- `Ennemi` point (112,144) : `type`=`caillou_rampant`, `variante`=`normal`
- `Interrupteur` (1,5) -> centre (48,176) : `id`=`donjon2_interrupteur_02`, `cible`=`donjon2_porte_03`, `mode`=`fleche`, `duree`=10
- `Ennemi` point (400,208) : `type`=`caillou_rampant`, `variante`=`normal`
- `Interrupteur` (18,8) -> centre (592,272) : `id`=`donjon2_interrupteur_03`, `cible`=`donjon2_porte_03`, `mode`=`fleche`, `duree`=10

### salle_07 - Salle du grand coffre

Le grand coffre des **bombes**, gardé par deux Cailloux. L'**éboulis** de l'est (ouverture bouchée) est visible dès l'arrivée, avec un paquet de bombes posé contre lui (les mineurs en ont laissé) : montrer avant d'exiger. Le joueur ouvre le coffre (5 bombes), pose une bombe contre l'éboulis et recule : le passage s'ouvre pour toujours. C'est la **leçon sans danger** (aucun ennemi à bouclier ici, 8 cases libres pour reculer). L'ouverture nord est une porte-grille fermée de ce côté (raccourci depuis la salle 10) ; l'ouest est la porte d'entrée (cibles de la 06).

<!-- salle_07 -->
```text
#########I##########
#..................#
#........P.........#
#.....O.....C..O...#
#..................#
I.P..............P.e
#..................#
#....c.....O.......#
#..............o...#
#........c.........#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_06_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon2_porte_03`, `type`=`interrupteur`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon2_salle_10_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon2_porte_06`, `type`=`interrupteur`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_08_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `MurFissure` (608,160,32,32) (même rectangle que la `Sortie`, qui n'est active qu'une fois le mur détruit) : `id`=`donjon2_mur_02`, `apparence`=`eboulis`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Coffre` point (400,112) : `id`=`donjon2_coffre_04`, `contenu`=`objet_bombes`, `important`=true
- `Ennemi` point (176,240) : `type`=`caillou_rampant`, `variante`=`normal`
- `Ramassable` point (496,272) : `id`=`donjon2_bombes_01`, `contenu`=`boutique_bombes` (5 bombes, posé seulement si Brann possède les bombes)
- `Ennemi` point (304,304) : `type`=`caillou_rampant`, `variante`=`normal`

### salle_08 - Galerie des étais

Premier **Mineur maudit**, seul dans une grande galerie : on le voit se tourner pour garder son bouclier face à Brann. Deux solutions : poser une bombe quand il s'approche (il tombe, étourdi 4 s, on le frappe) ou le contourner et le frapper de côté. Le **marteau au poinçon de Corvan** est posé au pied d'une poutre sciée (décor) : le rectangle d'indice `indice_poutres_sciees` affiche un texte de Brann (« Cette poutre a été sciée net... »). Dans l'angle nord-est, une alcôve fermée par un mur fissuré contient la petite clé n°3 (obligatoire) ; on la casse depuis (15,2). La porte nord est « tous les ennemis morts » (Mineur + Caillou) ; paquet de bombes `donjon2_bombes_02` au sud-ouest.

<!-- salle_08 -->
```text
#########N##########
#...............#C.#
#........P......M..#
#...............####
#.....O............#
e.P........m.......#
#..................#
#..................#
#..o..c....H.......#
#..................#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_07_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `MurFissure` (0,160,32,32) (même rectangle que la `Sortie`, qui n'est active qu'une fois le mur détruit) : `id`=`donjon2_mur_02`, `apparence`=`eboulis`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon2_salle_09_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon2_porte_04`, `type`=`ennemis`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Coffre` point (560,48) : `id`=`donjon2_coffre_05`, `contenu`=`cle_petite`, `important`=false
- `Ennemi` point (368,176) : `type`=`mineur_maudit`, `variante`=`normal`
- `Ramassable` point (112,272) : `id`=`donjon2_bombes_02`, `contenu`=`boutique_bombes` (5 bombes, posé seulement si Brann possède les bombes)
- `Ennemi` point (208,272) : `type`=`caillou_rampant`, `variante`=`normal`
- `Ramassable` point (368,272) : `id`=`donjon2_marteau_corvan`, `contenu`=`marteau_corvan`
- `MurFissure` (512,64,32,32) : `id`=`donjon2_mur_03`, `apparence`=`mur`
- Rectangle nommé `indice_poutres_sciees` (320,224,96,64) : `godot_node_type`=`area` (texte `INDICE_POUTRES_SCIEES`)

### salle_09 - Carrefour effondré

Combat plus dur, sans énigme obligatoire : deux Mineurs maudits et un Caillou. Les piliers (5,4) et (6,7) permettent de se mettre de côté. Dans l'angle nord-est, un **mur épais de 3 cases** cache une alcôve avec une **plume de corbeau** (facultative) : une bombe posée en (15,2) les casse toutes les trois (posée en (15,1) ou (15,3) elle n'en casse que deux : un deuxième paquet est alors nécessaire, d'où le paquet de bombes `donjon2_bombes_03` dans la salle). Sortie ouest par la porte à clé (K2).

<!-- salle_09 -->
```text
####################
#...............M..#
#...............M.F#
#...............M..#
#....O...........###
D.P................#
#......m...........#
#.....O.........m..#
#........P.....o...#
#...c..............#
#########N##########
```

Objets Tiled (calque `Objets`).

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon2_salle_08_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon2_porte_04`, `type`=`ennemis`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_10_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon2_porte_05`, `type`=`cle`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Ramassable` point (592,80) : `id`=`donjon2_plume_01`, `contenu`=`plume_corbeau`
- `Ennemi` point (240,208) : `type`=`mineur_maudit`, `variante`=`normal`
- `Ennemi` point (528,240) : `type`=`mineur_maudit`, `variante`=`normal`
- `Ramassable` point (496,272) : `id`=`donjon2_bombes_03`, `contenu`=`boutique_bombes` (5 bombes, posé seulement si Brann possède les bombes)
- `Ennemi` point (144,304) : `type`=`caillou_rampant`, `variante`=`normal`
- `MurFissure` (512,32,32,32) : `id`=`donjon2_mur_04`, `apparence`=`mur`
- `MurFissure` (512,64,32,32) : `id`=`donjon2_mur_05`, `apparence`=`mur`
- `MurFissure` (512,96,32,32) : `id`=`donjon2_mur_06`, `apparence`=`mur`

### salle_10 - Antichambre de Gorm

La **porte de la grande clé est visible dès l'arrivée, mais la clé n'est pas ici** : le joueur doit descendre. L'escalier vers le sous-sol (angle sud-est), un levier à l'épée près de l'arrivée nord-ouest qui ouvre le **raccourci** vers la salle 07 (grille au sud), et la statue du corbeau juste avant le boss. Combat léger : deux Chauves-souris et un Caillou.

<!-- salle_10 -->
```text
#########G##########
#.............b....#
#.....R..P.........#
#.l................#
#...O.........O....#
#................P.D
#.....O......O.....#
#....c.............#
#........P.......Pv#
#...b..............#
#########I##########
```

Objets Tiled (calque `Objets`).

- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_09_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon2_porte_05`, `type`=`cle`
- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon2_salle_07_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon2_porte_06`, `type`=`interrupteur`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon2_salle_boss_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon2_porte_07`, `type`=`grande_cle`
- `Sortie` (576,256,32,32) sur la tuile d'escalier : `cible_carte`=res://scenes/rooms/donjon2_salle_11_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Spawn` point (560,272) : `id`=`depuis_escalier`
- `Ennemi` point (464,48) : `type`=`chauve_souris`, `variante`=`normal`
- `StatueCorbeau` (6,2) -> centre (208,80) : `id`=`donjon2_statue_02`
- `Interrupteur` (2,3) -> centre (80,112) : `id`=`donjon2_interrupteur_04`, `cible`=`donjon2_porte_06`, `mode`=`epee` (levier)
- `Ennemi` point (176,240) : `type`=`caillou_rampant`, `variante`=`normal`
- `Ennemi` point (144,304) : `type`=`chauve_souris`, `variante`=`normal`

### salle_11 - Galerie basse (sous-sol)

Arrivée au sous-sol par l'escalier : un lieu calme avec deux Cailloux. L'ouverture sud mène à la 12 ; l'ouverture est est une grille qui ne s'ouvre que depuis la 14 (levier) : on la voit sans pouvoir la passer. Sol et murs plus sombres, cristaux rouges au mur (guide visuel).

<!-- salle_11 -->
```text
####################
#..................#
#................P^#
#..................#
#...OO.........OO..#
#................P.I
#..................#
#..c...........c...#
#........P.........#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`).

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon2_salle_12_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_14_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon2_porte_10`, `type`=`interrupteur`
- `Sortie` (576,64,32,32) sur la tuile d'escalier : `cible_carte`=res://scenes/rooms/donjon2_salle_10_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (560,80) : `id`=`depuis_escalier`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Ennemi` point (112,240) : `type`=`caillou_rampant`, `variante`=`normal`
- `Ennemi` point (496,240) : `type`=`caillou_rampant`, `variante`=`normal`

### salle_12 - Salle du brasero (sous-sol)

**Bombe puis arc.** Un mur de roche coupe la salle ; l'unique passage est un éboulis en (11,5). De l'autre côté, un brasero allumé en (13,5) et une torche éteinte en (15,5) sont **alignés sur la rangée 5**, avec la porte est fermée derrière. Solution : poser une bombe contre l'éboulis depuis (10,5) et reculer ; puis, depuis (10,5) ou (9,5), **tirer vers l'est** : la flèche traverse l'éboulis ouvert, le brasero (elle s'enflamme) et allume la torche (distance 5 cases) : la porte est (`donjon2_porte_09`) s'ouvre. Deux Cailloux (un de chaque côté) donnent le butin de bombes et de flèches. Aucun chronomètre.

<!-- salle_12 -->
```text
#########X##########
#..........#.......#
#........P.#.......#
#..........#.......#
#..........#.......#
#..........e.Y.f.P.I
#..........#.......#
#..c.......#.......#
#..........#....c..#
#..........#.......#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon2_salle_11_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon2_salle_13_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon2_porte_09`, `type`=`interrupteur`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (112,240) : `type`=`caillou_rampant`, `variante`=`normal`
- `Ennemi` point (528,272) : `type`=`caillou_rampant`, `variante`=`normal`
- `MurFissure` (352,160,32,32) : `id`=`donjon2_mur_07`, `apparence`=`eboulis`
- `Torche` (13,5) -> centre (432,176) : `id`=`donjon2_brasero_01`, `etat`=`allumee`, `permanente`=true (brasero)
- `Torche` (15,5) -> centre (496,176) : `id`=`donjon2_torche_01`, `etat`=`eteinte`, `permanente`=false, `duree`=0, `cible`=`donjon2_porte_09`

### salle_13 - Veine d'étoile (sous-sol)

La **veine de minerai d'étoile** brille dans le mur nord-ouest (décor lumineux) : le **coffre du minerai** (`donjon2_coffre_07`) est libre, en vue dès l'arrivée, dans la salle que tout le monde traverse. Le vestibule de la porte à clé nord est fermé par un éboulis en (9,3) : bombe depuis (9,4) en reculant (4 cases libres vers le sud), puis petite clé n°3 ou toute autre clé. Une Chauve-souris et un Caillou rouge (vie x2) gardent la salle.

<!-- salle_13 -->
```text
#########D##########
#.......#.#........#
#..C....#P#........#
#.......#e#........#
#..................#
I.P................#
#.............b....#
#..................#
#..........r.......#
#..................#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_12_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon2_porte_09`, `type`=`interrupteur`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon2_salle_14_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon2_porte_08`, `type`=`cle`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Coffre` point (112,80) : `id`=`donjon2_coffre_07`, `contenu`=`minerai_etoile`, `important`=true
- `Ennemi` point (464,208) : `type`=`chauve_souris`, `variante`=`normal`
- `Ennemi` point (368,272) : `type`=`caillou_rampant`, `variante`=`rouge`
- `MurFissure` (288,96,32,32) : `id`=`donjon2_mur_08`, `apparence`=`eboulis`
- Rectangle nommé `indice_veine_etoile` (64,32,96,64) : `godot_node_type`=`area` (texte `INDICE_VEINE_ETOILE`)

### salle_14 - Réserve de Gorm (sous-sol)

Défi des bombes avant le boss : deux Mineurs maudits et une Chauve-souris, des piliers pour se couvrir, un paquet de bombes. Le **grand coffre de la grande clé** est dans l'alcôve nord-ouest, fermée par un mur fissuré (on le casse depuis (4,2) en reculant vers l'est). Un levier à l'épée au sud-ouest ouvre la grille vers la salle 11 (raccourci de retour vers l'escalier). Chaque Mineur peut aussi être contourné : aucun combat n'est obligatoire.

<!-- salle_14 -->
```text
####################
#.C#...............#
#..M...............#
####...............#
#.......O.....O....#
I.P................#
#......m...........#
#...........m......#
#.l......P....o....#
#......b...........#
#########D##########
```

Objets Tiled (calque `Objets`).

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon2_salle_13_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon2_porte_08`, `type`=`cle`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon2_salle_11_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon2_porte_10`, `type`=`interrupteur`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Coffre` point (80,48) : `id`=`donjon2_coffre_08`, `contenu`=`grande_cle`, `important`=true
- `Ennemi` point (240,208) : `type`=`mineur_maudit`, `variante`=`normal`
- `Ennemi` point (400,240) : `type`=`mineur_maudit`, `variante`=`normal`
- `Interrupteur` (2,8) -> centre (80,272) : `id`=`donjon2_interrupteur_06`, `cible`=`donjon2_porte_10`, `mode`=`epee` (levier)
- `Ramassable` point (464,272) : `id`=`donjon2_bombes_04`, `contenu`=`boutique_bombes` (5 bombes, posé seulement si Brann possède les bombes)
- `Ennemi` point (240,304) : `type`=`chauve_souris`, `variante`=`normal`
- `MurFissure` (96,64,32,32) : `id`=`donjon2_mur_09`, `apparence`=`mur`

### salle_15 - Cave secrète (sous-sol)

**Petite clé n°2 cachée.** On y arrive en sautant dans le trou de la 04 ou par l'escalier de la 05. Aucun puzzle : un Caillou, un coffre, un escalier pour remonter. Elle apparaît sur la carte du donjon, ce qui guide le joueur curieux. La clé ne sert que plus tard (retour en arrière).

<!-- salle_15 -->
```text
####################
#..................#
#^P................#
#..................#
#...O..........O...#
#........P.........#
#..................#
#..............C...#
#...........c......#
#..................#
####################
```

Objets Tiled (calque `Objets`).

- `Sortie` (32,64,32,32) sur la tuile d'escalier : `cible_carte`=res://scenes/rooms/donjon2_salle_05_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (80,80) : `id`=`depuis_escalier`
- `Spawn` point (304,176) : `id`=`depuis_chute_salle_04`
- `Coffre` point (496,240) : `id`=`donjon2_coffre_06`, `contenu`=`cle_petite`, `important`=false
- `Ennemi` point (400,272) : `type`=`caillou_rampant`, `variante`=`normal`

### salle_boss - Salle du boss : Cœur de la Mine (Gorm)

Arène de Gorm, 20x22 (deux écrans en hauteur, `camera` = `ecran`). Gorm (colosse de roche de 96x96 environ, cristal rouge dans la poitrine) apparaît au nord, au centre. **Ce dont le boss a besoin côté carte** :
- Point `boss_gorm` en (9,4) (la scène `scenes/enemies/boss/gorm.tscn`, id `donjon2_boss_gorm`).
- 4 rectangles `pilier` de 2x2 cases (comme Sylve) : ils arrêtent le corps de Gorm (couche 3) et masquent Brann des rochers de la phase 2. Le couloir central fait 10 cases de large ; les **couloirs latéraux ne font que 2 cases** : Gorm (3 cases) n'y passe pas, ce sont les refuges de Brann contre son corps à corps (pas contre les rochers).
- **Bombes** : phase 1 = faire sauter les plaques d'armure à la bombe, puis frapper le cristal. Quatre `Marqueur` `gorm_bombes_1` à `4` dans les couloirs latéraux sont les points où le boss fait apparaître un paquet de bombes (quand Brann en a moins de 3, avec un délai) ; Brann arrive avec au moins 3 bombes grâce au butin garanti de la salle 10 (Caillou, Chauves-souris) et à la statue qui précède. Le sol est sans fosse (rien ne peut bloquer la partie).
- Phase 2 : tremblements et rochers annoncés par leur ombre (aucun objet Tiled : le boss choisit les impacts, hors piliers et murs).
- Porte d'arène : la `Porte` sud `donjon2_porte_07` se verrouille pendant le combat (`LockForEncounter`) et se rouvre à la victoire ; réceptacle et sceau = ramassables `donjon2_boss_gorm_receptacle` et `donjon2_boss_gorm_sceau` (créés par la `Room`).

<!-- salle_boss -->
```text
####################
#..................#
#..................#
#..................#
#........g.........#
#..................#
#..................#
#..OO..........OO..#
#..OO..........OO..#
#..................#
#o................o#
#..................#
#..................#
#..OO..........OO..#
#..OO..........OO..#
#..................#
#..................#
#o................o#
#..................#
#........P.........#
#..................#
#########G##########
```

Objets Tiled (calque `Objets`).

- `Sortie` (288,672,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon2_salle_10_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,672,32,32) côté sud : `id`=`donjon2_porte_07`, `type`=`grande_cle`
- `Spawn` point (304,624) : `id`=`depuis_sud`
- Rectangle ou point nommé `boss_gorm` : apparition de Gorm, centre de la case (9,4) -> (304,144)
- 4 rectangles nommés `pilier` (96,224,64,64), (480,224,64,64), (96,416,64,64), (480,416,64,64)
- 4 `Marqueur` dans les couloirs latéraux : `id`=`gorm_bombes_1` (48,336), `gorm_bombes_2` (592,336), `gorm_bombes_3` (48,560), `gorm_bombes_4` (592,560) (lieux où Gorm fait apparaître des bombes)

## 5. Vérification des clés, des portes, des étages et des énigmes

Script de vérification (bibliothèque standard seulement, non commité) appliqué aux aperçus ci-dessus. Résultats :

- **Structure** : 16 aperçus de la bonne taille (20x11, boss 20x22), ouvertures uniquement aux positions fixes, chaque objet (coffres, leviers, torches, plaques, paquets de bombes, quart de cœur, plume, marteau, statues, sorties) **atteignable** depuis les arrivées de sa salle une fois les murs fissurés de la salle ouverts (les cibles de la 06 se tirent depuis 5, 11 et 5 cases de tir), aucun ennemi à moins de 3 cases d'une arrivée.
- **Parcours sur l'état du joueur** (salle, petites clés en poche, portes ouvertes et leviers actionnés, objets obtenus) : **8 704 états atteignables, 0 état d'où le boss est hors de portée**. La salle du boss est donc atteignable quel que soit l'ordre dans lequel le joueur ouvre les portes, prend les coffres, tombe dans le trou, descend ou remonte l'escalier, revient en arrière. Les 16 salles sont atteintes ; les 10 objets de progression (carte, boussole, 3 clés, bombes, grande clé, minerai, quart de cœur, plume) sont tous obtenables.
- **Clés** : 3 petites clés pour 3 portes à clé (01, 05, 08), **au plus 2 en poche à la fois**. Retirer l'une des trois portes du modèle rend le boss inatteignable (les trois sont donc obligatoires, comme les trois clés).
- **Énigmes** : salle 05, solution trouvée en **25 pousses** (exploration complète de 3 490 états, règle « pas de bloc près d'une arrivée »). Salle 06 : temps minimal des 3 cibles **6,6 s** pour 10 s accordées (66 %, à 3,125 cases/s et 0,7 s par tir ; le critère est de rester sous 70 %). Salles 03, 07, 08, 09, 12, 13, 14 : une bombe suffit à chaque obstacle obligatoire (1 en 07, 1 en 08, 1 en 12, 1 en 13, 1 en 14), plus 1 facultative (03) et 1 facultative (09).
- **Blocs** : un seul puzzle de blocs (salle 05) ; comme dans le Temple, il existe des états où les blocs sont coincés : **sortir de la salle et y revenir remet les blocs en place** (déjà le comportement de `Room`).
- **Bombes** : voir le tableau « munitions de bombes » du §3 ; aucun état d'attente sans solution grâce au butin garanti (NOUVEAU) et au fait que les ennemis réapparaissent.

Hypothèses : arc acquis (Temple fait), les ennemis ne bloquent pas les flèches, une porte `ennemis` reste ouverte une fois ouverte, les bombes sont réapprovisionnées par le butin garanti (le vérificateur compte « avoir des bombes » comme un état booléen après le grand coffre).

## 6. Risques et décisions pour le développeur

1. **Munitions de bombes** : la sécurité repose sur le butin garanti (NOUVEAU, §7) ; sans lui, il faudrait ajouter à la main des sources réapparaissantes.
2. **Dégâts de la bombe sur Brann** : 1 PV dans 40 px ; toutes les poses obligatoires laissent 3 cases pour reculer. Un enfant se fera parfois toucher : rappeler le rayon dans un indice (rectangle `indice_*`) à la première salle de bombe (07).
3. **Pose de la bombe contre un mur** : la portée est mesurée jusqu'au bord du destructible (8 cases voisines). Le mur épais de la 09 est le seul où l'emplacement compte ; il est facultatif.
4. **Un mur fissuré de chaque côté d'une ouverture** : `donjon2_mur_02` existe dans 07 et 08 avec le **même id** (comme les portes) ; détruit d'un côté, il l'est des deux.
5. **Mineur maudit** : jamais obligatoire à tuer à la bombe (il se contourne) ; une porte `ennemis` (08) le compte parmi les ennemis à vaincre, mais il est vulnérable de côté et de dos. Prévoir qu'un Mineur ne se bloque pas contre un pilier (pas de piège à Mineur).
6. **Chauve-souris** : vole (groupe `vol`), ne tombe pas dans les trous ; elle passe sur les fosses de la 06.
7. **Torche derrière un éboulis (12)** : la flèche ne doit passer qu'une fois l'éboulis détruit (`CrackedWall` est un corps solide qui arrête la flèche) ; la flèche traverse ensuite le brasero (donc `IArrowInteractor`) puis allume la torche (`duree` = 0, reste allumée).
8. **Cibles chronométrées de la 06** : durée 10 s x le multiplicateur d'aide (x2, ou illimité) ; l'anneau `cible_chrono` doit se voir.
9. **Longueur** : 16 salles (11 au sol dont le boss, 5 au sous-sol) ; temps estimé 70 à 100 minutes la première fois, à valider par un test.
10. **Minerai d'étoile** : il est dans un coffre libre sur le chemin obligatoire ; si le joueur le laisse (coffre non ouvert), il pourra revenir (donjon accessible, coffre mémorisé). Prévoir que la forge/Hulda demande le minerai et le dise (dialogue).

## 7. Conventions et ressources manquantes (à demander)

### Mécanique à coder

**NOUVEAU (à coder), au plus 1 :**
- **Butin de bombes garanti** : sur le modèle du butin de flèches (`LootDropper.GuaranteeArrows` / `ArrowsBelow` / `ArrowLootRule`) : si Brann possède les bombes et en a moins de `BombsBelow` (3), chaque ennemi vaincu lâche **en plus** du tirage normal un paquet de bombes (2 bombes, 20 s au sol), nouvelle scène `scenes/items/bombes_paquet.tscn` (pickup `GiveItemEffect` `Quantity` = 2, `OnlyIfOwned`). Même règle pour les ennemis des salles 07 à 14 et pour Gorm si le développeur le souhaite. Aucun nouvel état de sauvegarde.

**Aucune autre mécanique** : pas de wagonnet roulant (les « wagonnets » des salles 05 et décors sont des `BlocPoussable` habillés et des décors solides), pas de rails fonctionnels (décor seulement).

### Classes d'objets utilisées (toutes déjà prévues dans `CLAUDE.md`)

`Spawn`, `Sortie` (`transition`=`escalier`), `Porte` (`cle`, `grande_cle`, `ennemis`, `interrupteur`), `Interrupteur` (`fleche` avec `duree`, `epee` levier), `PlaqueDePression`, `BlocPoussable`, `Torche` (brasero et torche), `Chute`, `MurFissure` (`mur` et `eboulis`), `Coffre`, `Ramassable`, `StatueCorbeau`, `Ennemi` (`caillou_rampant`, `chauve_souris`, `mineur_maudit`), rectangle `indice_*`, `boss_gorm`, `pilier`, `Marqueur`. Propriétés de carte : `etage`, `carte_x`, `carte_y`, `camera` (boss : `ecran`).

### Ressources de ramassage à créer (développeur)

- `resources/pickups/marteau_corvan.tres` : `FlagEffect` posant le drapeau `marteau_corvan` (indice d'histoire, `ShowNameOnPickup`, texte de Brann ; Icon et NameKey `OBJ_MARTEAU_CORVAN`), à rappeler dans le dialogue de Gorm (« l'homme au tablier de cuir »).
- `resources/pickups/minerai_etoile.tres` : objet de quête (flag ou item `minerai_etoile`, Icon, NameKey `OBJ_MINERAI_ETOILE`, `important`) lu par la forge pour l'Épée trempée.
- `sceau_montagne.tres` (`SealEffect`), `receptacle.tres` existe déjà. `quart_coeur.tres`, `plume_corbeau.tres`, `objet_bombes.tres`, `boutique_bombes.tres`, `cle_petite.tres`, `grande_cle.tres`, `carte_donjon.tres`, `boussole.tres` existent déjà.
- Textes à ajouter à `textes.csv` : `INDICE_POUTRES_SCIEES`, `INDICE_VEINE_ETOILE`, noms des objets, `SALLE_DONJON2_01` à `15` et `SALLE_DONJON2_BOSS`, dialogue de Gorm.

### Code à compléter (développeur)

- Scènes de salle : `scenes/rooms/donjon2_salle_01_room.tscn` à `donjon2_salle_15_room.tscn` et `donjon2_salle_boss_room.tscn`, `Zone` = `donjon2`.
- `HoleWatcher` / `HoleRules` : reconnaître les tuiles 58 à 66 (fosses mortelles) des tilesets `mine` et `mine_sous_sol` (comme pour `temple_racines` et `temple_racines_sous_sol`) ; `Chute` : tuiles `trou_passage` 31 à 39 décoratives.
- `TileRules` : paires fermée → ouverte des murs fissurés et éboulis du tileset `mine` (voir §ci-dessous).
- `DungeonMap.cs` : plan du donjon 2 (positions du tableau du §3, liens, escaliers, chute, ids de portes, coffres des salles).
- Boss `Gorm` : scène `scenes/enemies/boss/gorm.tscn` (sous-classe de `Boss`), plaques d'armure, cristal, rochers et ombres.
- Retour après le boss et sortie vers la montagne (à décider avec le Temple).

### Tuiles à demander au graphiste (tilesets `mine` pour le rez-de-chaussée et `mine_sous_sol` à la même numérotation, plus sombre et bleuté, cristaux rouges)

Garder les **mêmes numéros que `temple_racines`** pour les éléments reconnus par le code : escaliers 56 (montant) et 57 (descendant), fosses mortelles 58 à 66 (centre, 4 bords, 4 coins), trous de passage 31 à 39. Le reste au choix du graphiste, avec un plan `art/tilesets/mine_plan.md`.

| Élément | Détail |
| --- | --- |
| Sols | `roche_sol` a à d (gris-brun avec cailloux), `terre_battue`, `gravier_rail`, `planches` (passerelle de bois), `dalle_ancienne` ; terrain de bordure sol / terre ; version sous-sol (bleu-gris, cristaux) |
| Murs de roche | face (visible) + dessus, bords haut / bas / gauche / droite, coins extérieurs et intérieurs (4 + 4), mur plein, mur avec veine de minerai, mur avec **veine d'étoile** (lumineux, bleu-blanc, pour la 13), mur avec cristaux rouges (sous-sol) |
| Étais de bois | `etai_h`, `etai_v`, `etai_coin`, poutre haute (calque `Dessus`), **poutre sciée** (coupe nette, décor de la 08), poutre brisée, porte d'étais (cadre de l'ouverture de salle) |
| Piliers / colonnes | `colonne_base` (Murs) et `colonne_haut` (Dessus) pour les `O` de 1 case ; blocs 2x2 pour les piliers du boss (coins extérieurs de mur) |
| Ouvertures de salle | `porte_haut`, `porte_bas` (passage de 20 px) et `porte_gauche`, `porte_droite` (24 px), cadre d'étais |
| **Murs fissurés** | `mur_fissure` (fermé, solide, fissures claires, lisible de face ; variantes pour les parois vues de face et de côté si besoin) et `mur_fissure_ouvert` (ouvert, trou noir, sans collision, calque `Decor`) |
| **Éboulis** | `eboulis_a`, `eboulis_b` (solides), `eboulis_degage_a`, `eboulis_degage_b` (gravats au sol, sans collision) ; une version « éboulis dans une ouverture » (case dans l'encadrement d'une porte) ; mêmes numéros que `montagne` (176 à 181) si le graphiste le peut, pour réutiliser `TileRules` |
| **Trous mortels** (58-66) | noir profond, bord de pierre ; nettement différents des trous de passage |
| **Trous de passage** (31-39) | puits à échelle brisée, lueur chaude orangée au fond, anneau de planches ; 2x2 |
| Escaliers | `escalier_montant` (56), `escalier_descendant` (57), en pierre et bois |
| Rails | `rail_h`, `rail_v`, 4 coins, 4 « T », croisement, 4 butoirs, rail brisé : calque `Decor`, sans collision |
| Wagonnets (calque `Murs`) | `wagonnet_vide_h/v` et `wagonnet_plein_h/v` (solides, collision partielle) ; **le bloc poussable** = `bloc_mine` (wagonnet-caisse de minerai) : image pour `BlocPoussable` à fournir (ou propriété `apparence` à ajouter côté code) |
| Décor | caisses, tonneaux, pioches, pelles, lanterne murale (`Dessus`), toiles, tas de gravats (décor), établi, cristaux rouges, minerai au sol, flaques, panneau de bois (pour les indices) |
| Grilles | `grille_h` et `grille_v` (fermée, ouverte) pour les alcôves : réutiliser les images de `art/puzzles/` du Temple, version « fer rouillé » |
| Sprites hors tileset | `art/puzzles/bloc_mine`, `torche` / `brasero` (existent), `levier` (existe), `plaque_pression` (existe), `cible_chrono` (existe), `bombes_paquet`, icônes `marteau_corvan` et `minerai_etoile`, sprites de Gorm (plaques d'armure, cristal, rochers, ombres) |

## 8. Suite

À valider par la personne qui joue au projet. Après validation (étape 2) :

- Le graphiste livre le plan du tileset `mine` (et `mine_sous_sol`).
- Le level-designer crée `maps/donjon2/salle_01.tmx` à `salle_15.tmx` et `salle_boss.tmx` à partir de ce plan, avec un script de vérification qui relit aussi les `.tmx` (comme `maps/donjon1/verif_donjon.py`).
- Mises à jour par ailleurs : `docs/roadmap.md` (Mine Effondrée : 10 salles devient 16 ; cocher la phase 6 correspondante) et `CLAUDE.md` (aucune nouvelle classe Tiled ; mentionner le butin de bombes garanti une fois codé).
