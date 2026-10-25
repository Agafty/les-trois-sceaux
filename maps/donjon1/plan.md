# Plan du Temple des Racines (donjon 1) - version 2 : deux étages, 16 salles

Document de conception (étape 1, remplace le plan à 10 salles). **Aucun `.tmx` de cette version n'existe encore** : on attend la validation de ce plan. Les 10 cartes du plan précédent (jouable de bout en bout) restent dans le dépôt, inchangées, jusqu'à l'étape 2 (voir §8 : 4 salles sont reprises telles quelles, 5 sont retravaillées, 6 sont nouvelles).
Le script `verif_donjon.py` (même dossier) **lit les aperçus de ce fichier** et prouve les propriétés annoncées plus bas.

## 1. Intention et courbe de difficulté

**Retour de test du plan précédent** : « trop simple, la clé du boss est dans la salle de sa porte, trop peu d'énigmes, trop peu de salles ». Décisions : 14 à 16 salles sur deux étages (le Temple au sol, les Racines profondes au sous-sol), reliés par **3 escaliers** et **2 trous de passage** (chute sans dégât vers l'étage du dessous), des énigmes de vrai Zelda (ordre à trouver, retours en arrière, petite clé cachée, raccourcis qui s'ouvrent) et une grande clé qui demande un vrai détour.

**Intention** : donjon d'apprentissage de l'arc, pour un adulte qui découvre et pour un enfant de 5 ans qui joue avec de l'aide. Le joueur apprend, dans l'ordre : frapper, esquiver la charge d'un sanglier, tuer tout le monde pour ouvrir une porte, amener un bloc sur une plaque (puis deux blocs sur deux plaques), sauter dans un trou de passage et remonter, obtenir l'arc, toucher deux cibles en temps limité, allumer une torche en tirant à travers un brasero, lire une fresque pour toucher trois cibles dans l'ordre, allumer une chaîne de torches contre la montre ; puis il combine arc, ennemis, étages et raccourcis avant Sylve.

**Réglage de la difficulté** : les combats restent faciles (au plus 3 ennemis par salle, un seul ennemi dans les salles à énigme, variantes rouges seulement dans les salles 08 et 09) ; la difficulté vient des énigmes et de l'orientation. Aucune énigme ne coûte de point de vie sauf les fosses mortelles (1 PV, retour à l'entrée de la salle), toujours hors du chemin. Une erreur d'énigme ne se punit que par du temps (réinitialisation en sortant et revenant, ou nouvel essai).

| Étape | Salle | Ce qui est appris ou testé | Tension |
| --- | --- | --- | --- |
| 1 | 01 Entrée | Frapper un Ronceau isolé ; la statue du corbeau (sauvegarde) | très faible |
| 2 | 02 Hall | 2 Ronceaux ; carte ; la porte à clé nord est visible ; trois chemins au choix | faible |
| 3 | 03 Antre (facultative) | Charge du Sanglier ; **1 bloc sur 1 plaque** ouvre une alcôve (plume) | moyenne, optionnelle |
| 4 | 04 Broussailles | Porte « tous les ennemis morts » (2 Ronceaux + Sanglier) ; boussole ; **trou de passage** (première chute, sans danger) | moyenne |
| 5 | 15 Cave secrète | Atterrissage calme ; **petite clé n°3 cachée** ; escalier de retour | repos |
| 6 | 05 Deux dalles | **2 blocs sur 2 plaques** ; la petite clé n°1 est visible derrière une grille ; escalier vers la cave | réflexion, pas de combat |
| 7 | 06 Salle de l'arc | Sanglier + Ronceau ; **arc** ; **2 cibles en temps limité** (6 s) visibles depuis l'entrée | moyenne puis démo calme |
| 8 | 07 Allée des lutins | Lutins à l'arc ; carrefour (porte à clé 04 visible, accès nord, trou de passage) | moyenne-haute |
| 9 | 10 Braseros | **Flèche enflammée** (brasero puis torche) ; petite clé n°2 | calme |
| 10 | 08 Harde | Épreuve de force, variantes rouges, porte « ennemis » | haute |
| 11 | 09 Antichambre | Porte de la grande clé visible, **clé absente** ; statue ; levier-raccourci ; escalier vers le sous-sol | moyenne |
| 12 | 11 Cave d'arrivée | **Fresque** : l'ordre des symboles | calme |
| 13 | 13 Trois cibles | **Séquence de cibles** dans l'ordre de la fresque ; porte à clé 11 | moyenne |
| 14 | 14 Galerie des torches | **Chaîne de torches chronométrée** ; **grande clé** ; levier-raccourci | haute (puzzle) |
| 15 | 12 Galerie du retour (facultative) | Bloc + plaque + Brann sur une plaque ; plume ; retour par l'escalier | faible |
| 16 | Boss | Sylve (arc contre les 3 bulbes, puis charges contre les piliers) | boss |

Rythme : calme (01) - fight léger (02) - fight (04) - **repos** (15) - réflexion (05) - fight + récompense (06) - tir (07) - calme (10) - force (08) - calme (11) - cibles (13) - chrono (14) - retour rapide (12) - boss. Les salles 03 et 12 sont des détours facultatifs de plaisir.

## 2. Règles de raccord (valables pour toutes les salles)

Salle 20x11 (mur du pourtour : 1 case d'épaisseur, intérieur 18x9). **Une seule position pour chaque ouverture** :

| Mur | Case d'ouverture (colonne, ligne) | Pixels (x, y, l, h) | Spawn d'arrivée (centre) | Id du Spawn |
| --- | --- | --- | --- | --- |
| haut (nord) | (9, 0) | (288, 0, 32, 32) | (304, 80) | `depuis_nord` |
| bas (sud) | (9, 10) (boss : (9, 21)) | (288, 320, 32, 32) (boss : y=672) | (304, 272) (boss : (304, 624)) | `depuis_sud` |
| gauche (ouest) | (0, 5) | (0, 160, 32, 32) | (80, 176) | `depuis_ouest` |
| droite (est) | (19, 5) | (608, 160, 32, 32) | (560, 176) | `depuis_est` |

- Un passage = un `Sortie` sur la case d'ouverture (de chaque côté) + un `Spawn` dans la salle d'arrivée. Le `Spawn` du côté X s'appelle `depuis_<côté X>` (on est arrivé *par* ce côté). Dans la salle 01, l'arrivée de la forêt (côté sud) s'appelle `depuis_foret`.
- Tuiles d'ouverture du tileset : `porte_haut/bas` (passage de 20 px) et `porte_gauche/droite` (24 px) ; Brann fait 16x20 px (capsule rayon 8, hauteur 20) : ça passe.
- Une porte non libre (`D`, `G`, `N`, `I`) est un objet `Porte` **posé sur la même case que le `Sortie`**, dans **chacune des deux salles, avec le même `id`** (l'état « ouverte » est mémorisé par l'id). Une grille intérieure (`I` loin du bord) n'a qu'une face.
- **Règle des déclencheurs** : l'interrupteur, la plaque ou la torche qui ouvre une `Porte` est toujours **dans la même salle** que l'une des faces de cette porte. Rien n'agit sur une salle non chargée (aucune propagation entre salles à coder).
- **Escalier** : une tuile `escalier_descendant` (étage du dessus) ou `escalier_montant` (sous-sol) portant un `Sortie` de 32x32 (propriété `transition`=`escalier`), et un `Spawn` `depuis_escalier` sur la **case voisine**, jamais sur le `Sortie` (sinon l'aller-retour se déclenche en boucle). Un seul escalier par salle.
- **Trou de passage** : un rectangle `Chute` couvrant exactement les tuiles `trou_passage` ; il envoie Brann vers un `Spawn` `depuis_chute_<salle de départ>` d'une salle de l'étage **du dessous**, sans dégât. Le `Spawn` d'arrivée n'est jamais à moins de 2 cases d'un trou.
- **Fosse mortelle** : tuiles `trou` 58 à 66 (inchangé : 1 PV perdu, retour au Spawn d'entrée de la salle). Les deux sortes de trous n'ont ni la même couleur ni la même animation.
- **Blocs** : jamais dans une salle à trous, à cibles ou à torches ; un bloc **ne peut pas être poussé sur une case de Spawn, de `Sortie` ou de `Porte`, ni sur leurs 8 cases voisines** (règle à coder, voir §7) ; il revient à sa place à chaque chargement de la salle.
- Arc : flèche 300 px/s, `MaxDistance` 320 px (10 cases), `UseCost` 1, 20 flèches dans le coffre. Toutes les cibles et torches se touchent à 9 cases ou moins, en ligne droite. **Flèche enflammée** : une flèche qui traverse un brasero ou une torche allumée prend feu pour le reste de son vol et allume la première torche éteinte qu'elle touche. Il n'y a ni lanterne ni bombes dans ce donjon : c'est la seule façon d'allumer une torche.
- Chaque salle où l'on tire (06, 10, 13, 14) contient au moins un ennemi qui ne tire pas (Ronceau ou Sanglier) : le butin de flèches garanti (moins de 5 flèches) évite de manquer de munitions.

## 3. Plan des salles

```text
 ÉTAGE (rez-de-chaussée)
                                            [boss]
                                              G
                                              |
                              [10]=====I====[09]
                               |             N
                               |             |
                [06]=====I====[07]=====D====[08]
                 D
                 |
  [03]----------[02]----------[04]=====N====[05]
                 |
                 |
                [01] --> forêt

 SOUS-SOL
                              [12]          [11]
                               I             |
                              [14]=====D====[13]

                              [15]

 Liens d'étage : escaliers 05-15, 09-11, 10-12 ; trous de passage 04 -> 15 et 07 -> 12 (sens unique).
 Légende : - passage libre, D petite clé, G grande clé, N tous les ennemis morts, I interrupteur (levier, cibles,
 plaques ou torches), = porte entre deux salles.
```

Position des salles (pour la carte du menu pause : propriétés de carte `etage`, `carte_x`, `carte_y`) :

| Étage | Salle | (x, y) | Étage | Salle | (x, y) |
| --- | --- | --- | --- | --- | --- |
| `rdc` | 01 | (1, 0) | `sous_sol` | 11 | (3, 3) |
| `rdc` | 02 | (1, 1) | `sous_sol` | 12 | (2, 3) |
| `rdc` | 03 | (0, 1) | `sous_sol` | 13 | (3, 2) |
| `rdc` | 04 | (2, 1) | `sous_sol` | 14 | (2, 2) |
| `rdc` | 05 | (3, 1) | `sous_sol` | 15 | (2, 1) |
| `rdc` | 06 | (1, 2) | | | |
| `rdc` | 07 | (2, 2) | | | |
| `rdc` | 08 | (3, 2) | | | |
| `rdc` | 09 | (3, 3) | | | |
| `rdc` | 10 | (2, 3) | | | |
| `rdc` | boss | (3, 4) | | | |

| Élément | Lieu |
| --- | --- |
| Statues du corbeau | salle 01 (`donjon1_statue_01`, entrée) et salle 09 (`donjon1_statue_02`, avant le boss) |
| Carte | salle 02, `donjon1_coffre_01` (en vue dès l'arrivée) |
| Boussole | salle 04, `donjon1_coffre_02` |
| Petite clé n°1 | salle 05, `donjon1_coffre_03` (derrière la grille des plaques) |
| Petite clé n°3 (cachée) | salle 15, `donjon1_coffre_06` (cave atteinte par le trou de la 04 ou l'escalier de la 05) |
| **Arc** | salle 06, `donjon1_coffre_04` (grand coffre ; vers le **milieu** du parcours : 7e salle sur 16 en comptant l'ordre conseillé) |
| Petite clé n°2 | salle 10, `donjon1_coffre_05` (derrière la grille de la torche) |
| **Grande clé** | **salle 14 (sous-sol)**, `donjon1_coffre_07` (grand coffre, derrière la grille des torches) ; sert à la porte 07, **à l'étage du dessus** |
| Boss | salle boss (au nord de la 09) |
| Plumes de corbeau (facultatives) | salle 03 (`donjon1_plume_01`) et salle 12 (`donjon1_plume_02`) |

| Porte | Entre | Type | Ouverture |
| --- | --- | --- | --- |
| `donjon1_porte_01` | 02 (nord) et 06 (sud) | `cle` | une petite clé |
| `donjon1_porte_02` | 04 (est) et 05 (ouest) | `ennemis` | salle 04 nettoyée |
| `donjon1_porte_03` | 06 (est) et 07 (ouest) | `interrupteur` | 2 cibles de flèche en 6 s (salle 06) |
| `donjon1_porte_04` | 07 (est) et 08 (ouest) | `cle` | une petite clé |
| `donjon1_porte_05` | 08 (nord) et 09 (sud) | `ennemis` | salle 08 nettoyée |
| `donjon1_porte_06` | 09 (ouest) et 10 (est) | `interrupteur` | levier à l'épée (salle 09) : **raccourci** |
| `donjon1_porte_07` | 09 (nord) et boss (sud) | `grande_cle` | grande clé |
| `donjon1_porte_08` | grille intérieure de la 03 (3,2) | `interrupteur` | plaque (15,2) avec un bloc : alcôve de la plume (facultatif) |
| `donjon1_porte_09` | grille intérieure de la 05 (9,2) | `interrupteur` | 2 plaques (14,7) et (17,7) avec 2 blocs : petite clé n°1 |
| `donjon1_porte_10` | grille intérieure de la 10 (9,2) | `interrupteur` | torche (5,2) allumée : petite clé n°2 |
| `donjon1_porte_11` | 13 (ouest) et 14 (est) | `cle` | une petite clé |
| `donjon1_porte_12` | grille intérieure de la 13 (4,5) | `interrupteur` | 3 cibles dans l'ordre gland, racine, feuille |
| `donjon1_porte_13` | grille intérieure de la 14 (17,2) | `interrupteur` | 3 torches allumées en même temps : grande clé |
| `donjon1_porte_14` | 14 (nord) et 12 (sud) | `interrupteur` | levier à l'épée (salle 14) : **raccourci** |
| `donjon1_porte_15` | grille intérieure de la 12 (3,2) | `interrupteur` | plaque (14,2) avec un bloc + Brann sur la plaque (16,8) : plume (facultatif) |

| Lien d'étage | Départ | Arrivée | Sens |
| --- | --- | --- | --- |
| `donjon1_escalier_01` | 05, tuile (1,9) | 15, tuile (1,8) | deux sens |
| `donjon1_escalier_02` | 09, tuile (18,8) | 11, tuile (18,2) | deux sens |
| `donjon1_escalier_03` | 10, tuile (1,8) | 12, tuile (18,1) | deux sens |
| `donjon1_chute_04` | 04, trou (1..2, 8..9) | 15, Spawn (9,5) | **sens unique** (vers le bas) |
| `donjon1_chute_07` | 07, trou (17..18, 8..9) | 12, Spawn (9,4) | **sens unique** (vers le bas) |

**Économie des clés** : 3 petites clés (n°1 en 05, n°2 en 10, n°3 cachée en 15) pour 3 portes à clé (01, 04, 11). Les clés sont interchangeables : n'importe quelle clé ouvre n'importe quelle porte. Les trois portes sont **obligatoires** (le vérificateur condamne chacune tour à tour : le boss devient inatteignable) et les trois clés sont obligatoires, donc aucune clé n'est gaspillable. Une seule porte à clé est visible et utilisable à la fois (01 au début, 04 après l'arc, 11 dans les Racines profondes). La grande clé n'ouvre que la porte du boss, et elle est **au sous-sol** alors que la porte est à l'étage : sans changer d'étage, ni la grande clé ni le boss ne sont atteignables.

**Parcours conseillé** (celui que le vérificateur retrouve, à quelques détours facultatifs près) :
1. 01, puis le Hall 02 (carte ; la porte nord est verrouillée, on le voit).
2. 03 (facultative : bloc, plaque, plume), 04 (nettoyer, boussole).
3. Trou de passage de la 04 : cave secrète 15 (petite clé n°3 dans le coffre) ; on remonte par l'escalier jusqu'à la 05 (ou on y arrive à pied par la porte est de la 04).
4. 05 : deux blocs sur deux plaques, la grille s'ouvre, petite clé n°1.
5. Retour par 04 et 02 : porte nord (une clé), salle de l'arc 06 : arc, deux cibles en 6 s, porte est.
6. 07 (Lutins), accès nord vers 10 : flèche enflammée, petite clé n°2 ; retour en 07, porte est (une clé), 08 (harde), 09 (antichambre : porte du boss visible, statue, levier de raccourci).
7. Escalier de la 09 vers la cave 11 (fresque), 13 (trois cibles dans l'ordre), porte à clé 11, 14 (chaîne de torches), **grande clé**, levier-raccourci.
8. Retour : par la 12 et l'escalier de la 10 (raccourci), ou par 13, 11 et l'escalier de la 09. Puis la porte du boss (grande clé) et Sylve.

**Ordres possibles** : la cave 15 peut être visitée avant ou après la 05 ; les salles 03 et 12 sont facultatives ; le trou de la 07 mène à la 12 (retour par l'escalier de la 10) ; le levier de la 09 peut être oublié (le chemin long reste ouvert). Le vérificateur prouve qu'aucun de ces choix ne bloque la partie.

**Chaque blocage est visible avant d'être franchissable** :

| Blocage | Où on le voit | Où on le franchit |
| --- | --- | --- |
| Porte à clé 01 (Hall) | dès l'arrivée dans 02 | après la clé n°1 ou n°3 |
| Cibles de la 06 | dès l'entrée dans 06 (derrière la porte est fermée) | après l'arc |
| Grille de la clé n°1 | dans 05, avant les blocs | deux blocs sur deux plaques |
| Grille de la clé n°2 | dans 10, à côté de la torche et du brasero | après l'arc |
| Porte du boss | dans 09, avant même de descendre | grande clé de la 14 |
| Grille vers la 14 (levier) | dans 12 (côté bloqué) | levier de la 14, après la 13 |
| Escalier de la 10 vers la 12 | dans 10 | libre (deux sens) |

Légende des aperçus : `#` mur, `.` sol, `~` fosse mortelle, `T` trou de passage, `O` pilier ou mur isolé, `r` ronces noires (solides), `i` zone d'indice ou brèche coupée net, `P` Spawn d'arrivée, `E` ennemi (Ronceau, Sanglier), `L` Lutin des branches, `C` coffre, `S` cible de flèche, `l` levier (interrupteur à l'épée), `f` torche éteinte, `Y` brasero allumé en permanence, `B` bloc poussable, `p` plaque de pression, `F` plume, `R` statue du corbeau, `v` escalier descendant, `^` escalier montant, `X` passage libre, `D` porte petite clé, `G` porte grande clé, `N` porte ennemis, `I` porte interrupteur (porte entre deux salles ou grille intérieure).

## 4. Les salles

### salle_01 - Entrée

Premier pas, inchangé. Un seul Ronceau, loin de l'arrivée, dans une grande salle vide : on apprend à l'approcher, à le frapper, à se faire toucher sans conséquence. La statue du corbeau (sauvegarde) est à côté de l'arrivée.

<!-- salle_01 -->
```text
#########X##########
#..................#
#........P.........#
#..............E...#
#....O........O....#
#..................#
#..................#
#....O.............#
#........P...R.....#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/foret_temple_room.tscn (à créer), `cible_spawn`=`depuis_temple`, `godot_node_type`=`area`
- `Spawn` point (304,272) : `id`=`depuis_foret`
- `Ennemi` point (496,112) : `type`=`ronceau`, `variante`=`normal`
- `StatueCorbeau` (13,8) -> centre (432,272) : `id`=`donjon1_statue_01`

### salle_02 - Hall des racines

Carrefour, inchangé. Deux Ronceaux ; deux sorties libres (ouest, est) et une porte à clé au nord, **visible dès l'arrivée** : le joueur sait qu'il lui faudra une clé (n'importe laquelle des trois, voir l'économie des clés). Le coffre de la carte est en vue (sécurité : coffre ouvert d'emblée).

<!-- salle_02 -->
```text
#########D##########
#..................#
#........P.....C...#
#.....O......O.....#
#..................#
X.P....E.........P.X
#...........E......#
#.....O......O.....#
#........P.........#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_06_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon1_porte_01`, `type`=`cle`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_01_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_04_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_03_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Ennemi` point (240,176) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (400,208) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (496,80) : `id`=`donjon1_coffre_01`, `contenu`=`carte_donjon`, `important`=false

### salle_03 - Antre du sanglier (facultative)

Impasse facultative et **première plaque de pression**, sans danger : un seul Sanglier (on apprend la charge et à s'écarter), un bloc, une plaque dans le coin nord-est et, bien visible dans l'angle nord-ouest, une alcôve fermée par une grille avec une plume de corbeau. Le joueur voit la grille, la plaque et le bloc dans le même écran : il comprend qu'il faut amener le bloc sur la plaque.

Solution (14 pousses) : pousser le bloc vers la droite le long de la rangée 7 jusqu'à la colonne 15, puis vers le haut jusqu'à la plaque (15,2). La grille s'ouvre définitivement. Pas de trou dans cette salle (règle des blocs).

<!-- salle_03 -->
```text
####################
#F.#...............#
#..I...........p...#
####...............#
#.....O.........O..#
#................P.X
#..................#
#.....B............#
#...E......O.......#
#..................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (144,272) : `type`=`sanglier_noirci`, `variante`=`normal`
- `Ramassable` point (48,48) : `id`=`donjon1_plume_01`, `contenu`=`plume_corbeau`
- `BlocPoussable` (6,7) -> centre (208,240)
- `PlaqueDePression` (480,64,32,32) : `id`=`donjon1_plaque_01`, `cible`=`donjon1_porte_08`, `declencheur`=`bloc`, `godot_node_type`=`area`
- `Porte` (96,64,32,32) intérieure (grille) : `id`=`donjon1_porte_08`, `type`=`interrupteur`

### salle_04 - Salle des broussailles

Porte « ennemis » et **premier trou de passage**. Deux Ronceaux et un Sanglier ; la porte est du côté est, fermée tant qu'ils ne sont pas tous morts. Le coffre de la boussole attend au fond (on le prend en passant). Dans l'angle sud-ouest, à l'écart de tout chemin, un trou 2x2 d'un aspect différent des trous mortels (anneau de racines, lueur verte au fond) : on peut y sauter sans dégât et on atterrit dans la cave secrète (salle 15). Un Ronceau ou le Sanglier qui tombe dedans disparaît (comme dans un trou mortel), ce qui peut aussi aider à finir la salle.

<!-- salle_04 -->
```text
####################
#..................#
#.....E........C...#
#............O.....#
#....O.............#
X.P.......E......P.N
#....O.............#
#............O.....#
#TT...........E....#
#TT................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_05_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_02`, `type`=`ennemis`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Chute` (32,256,64,64) : `id`=`donjon1_chute_04`, `cible_carte`=res://scenes/rooms/donjon1_salle_15_room.tscn, `cible_spawn`=`depuis_chute_salle_04`, `godot_node_type`=`area`
- `Ennemi` point (208,80) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (336,176) : `type`=`sanglier_noirci`, `variante`=`normal`
- `Ennemi` point (464,272) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (496,80) : `id`=`donjon1_coffre_02`, `contenu`=`boussole`, `important`=false

### salle_05 - Salle des deux dalles

**Deux blocs, deux plaques.** Une haie de ronces noires coupe la salle en deux ; le passage est une coupure nette (indice sur Corvan, inchangé). Au nord, derrière la brèche, un coffre dans une alcôve fermée par une grille : on voit la petite clé n°1 sans pouvoir la prendre. Au sud, un couloir d'une case de large contient deux plaques (14,7) et (17,7), et deux blocs attendent dans la zone ouest. L'escalier vers la cave secrète (salle 15) est dans l'angle sud-ouest, visible dès l'arrivée.

Solution (25 pousses) : descendre ou monter chaque bloc d'une case pour l'aligner sur la rangée 7, puis le pousser vers l'est dans le couloir : le premier jusqu'à la plaque du fond (17,7), le second jusqu'à (14,7). Quand les deux plaques sont pressées en même temps, la grille (9,2) s'ouvre définitivement. Si on se trompe, sortir de la salle et revenir remet les blocs à leur place.

<!-- salle_05 -->
```text
####################
#.......#C#........#
#........I.........#
#..................#
#rrrrrrriiirrrrrrrr#
N.P................#
#...B.....##########
#.............p..p##
#...B.....##########
#vP................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_04_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_02`, `type`=`ennemis`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Sortie` (32,288,32,32) sur la tuile d'escalier `escalier_descendant` : `cible_carte`=res://scenes/rooms/donjon1_salle_15_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (80,304) : `id`=`depuis_escalier`
- `Coffre` point (304,48) : `id`=`donjon1_coffre_03`, `contenu`=`cle_petite`, `important`=false
- `BlocPoussable` (4,6) -> centre (144,208)
- `BlocPoussable` (4,8) -> centre (144,272)
- `PlaqueDePression` (448,224,32,32) : `id`=`donjon1_plaque_02`, `cible`=`donjon1_porte_09`, `declencheur`=`bloc`, `godot_node_type`=`area`
- `PlaqueDePression` (544,224,32,32) : `id`=`donjon1_plaque_03`, `cible`=`donjon1_porte_09`, `declencheur`=`bloc`, `godot_node_type`=`area`
- `Porte` (288,64,32,32) intérieure (grille) : `id`=`donjon1_porte_09`, `type`=`interrupteur`
- Rectangle nommé `indice_ronces_coupees` (256,128,96,32) : godot_node_type=area

### salle_06 - Salle de l'arc

Salle de l'arc. Le joueur a ouvert la porte 01 avec une petite clé. Un Sanglier et un Ronceau gardent le grand coffre de l'arc. Une fois l'arc en main, **deux cibles à toucher en moins de 6 secondes** : elles sont visibles dès l'entrée, au fond de deux fosses, derrière la porte est fermée. Des piliers en (18,3) et (18,7) interdisent le tir depuis la bande d'arrivée : il faut tirer en travers de la fosse depuis une case de la rangée 2 (colonnes 9 à 13), puis redescendre tirer depuis la rangée 8 (mêmes colonnes). L'enchaînement prend 2,6 s au minimum : large pour un adulte, confortable pour un enfant aidé. Les trous de cette salle sont mortels (1 PV, retour à l'entrée) mais jamais sur le chemin.

<!-- salle_06 -->
```text
####################
#.............~~~~~#
#.....C.......~~~~S#
#.............~~~~O#
#...O.....O........#
#................P.I
#..................#
#..E....O....O~~~~O#
#........P....~~~~S#
#...........E.~~~~~#
#########D##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon1_porte_01`, `type`=`cle`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_07_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_03`, `type`=`interrupteur`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (112,240) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (400,304) : `type`=`sanglier_noirci`, `variante`=`normal`
- `Coffre` point (208,80) : `id`=`donjon1_coffre_04`, `contenu`=`objet_arc`, `important`=true
- `Interrupteur` (18,2) -> centre (592,80) : `id`=`donjon1_interrupteur_01`, `cible`=`donjon1_porte_03`, `mode`=`fleche`, `duree`=6
- `Interrupteur` (18,8) -> centre (592,272) : `id`=`donjon1_interrupteur_02`, `cible`=`donjon1_porte_03`, `mode`=`fleche`, `duree`=6

### salle_07 - Allée des lutins

Première mise en pratique de l'arc contre des ennemis : deux Lutins des branches aux deux extrémités, des piliers pour se couvrir, un Ronceau. Il n'y a plus de coffre ici : la salle sert de **carrefour** (porte à clé 04 à l'est, bien visible ; ouverture libre au nord vers la salle 10 ; trou de passage 2x2 au sud-est, hors du chemin, qui mène à la galerie du retour au sous-sol). Le joueur qui tombe dans ce trou remonte par l'escalier de la salle 10 : sans danger.

<!-- salle_07 -->
```text
#########X##########
#....L.............#
#........P.........#
#....O....O...O....#
#..................#
I.P.......E......P.D
#..................#
#....O....O...O....#
#................TT#
#............L...TT#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_10_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_08_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_04`, `type`=`cle`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_06_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_03`, `type`=`interrupteur`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Chute` (544,256,64,64) : `id`=`donjon1_chute_07`, `cible_carte`=res://scenes/rooms/donjon1_salle_12_room.tscn, `cible_spawn`=`depuis_chute_salle_07`, `godot_node_type`=`area`
- `Ennemi` point (176,48) : `type`=`lutin_des_branches`, `variante`=`normal`
- `Ennemi` point (336,176) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (432,304) : `type`=`lutin_des_branches`, `variante`=`normal`

### salle_08 - Salle de la harde

Épreuve de force, inchangée sauf une variante : Ronceau rouge, Sanglier rouge et un Ronceau normal (pour rester abordable avec un enfant). Aucun puzzle : on teste l'esquive et l'épée avant l'antichambre. Sortie au nord par une porte « ennemis ».

<!-- salle_08 -->
```text
#########N##########
#..................#
#........P..E......#
#..................#
#.....O......O.....#
D.P................#
#..............E...#
#.....O......O.....#
#..................#
#......E...........#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_09_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon1_porte_05`, `type`=`ennemis`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_07_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_04`, `type`=`cle`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Ennemi` point (400,80) : `type`=`ronceau`, `variante`=`rouge`
- `Ennemi` point (496,208) : `type`=`sanglier_noirci`, `variante`=`rouge`
- `Ennemi` point (240,304) : `type`=`ronceau`, `variante`=`normal`

### salle_09 - Antichambre du cerf

Antichambre. La **porte de la grande clé est visible dès l'arrivée, mais la clé n'est pas ici** : le joueur doit descendre. Un escalier vers le sous-sol (angle sud-est), un levier à l'épée (à côté de l'arrivée ouest) qui ouvre le **raccourci** vers la salle 10, une deuxième statue du corbeau juste avant le boss. Combat léger : deux Lutins et un Ronceau rouge.

<!-- salle_09 -->
```text
#########G##########
#.............L....#
#.....R..P.........#
#.l................#
#...O.........O....#
I.P................#
#.....O......O.....#
#....L.......E.....#
#........P.......Pv#
#..................#
#########N##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_boss_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon1_porte_07`, `type`=`grande_cle`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_08_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon1_porte_05`, `type`=`ennemis`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_10_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_06`, `type`=`interrupteur`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Sortie` (576,256,32,32) sur la tuile d'escalier `escalier_descendant` : `cible_carte`=res://scenes/rooms/donjon1_salle_11_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (560,272) : `id`=`depuis_escalier`
- `Ennemi` point (464,48) : `type`=`lutin_des_branches`, `variante`=`normal`
- `Ennemi` point (176,240) : `type`=`lutin_des_branches`, `variante`=`normal`
- `Ennemi` point (432,240) : `type`=`ronceau`, `variante`=`rouge`
- `StatueCorbeau` (6,2) -> centre (208,80) : `id`=`donjon1_statue_02`
- `Interrupteur` (2,3) -> centre (80,112) : `id`=`donjon1_interrupteur_06`, `cible`=`donjon1_porte_06`, `mode`=`epee` (levier)

### salle_10 - Salle des braseros

**Première torche** (montrer avant d'exiger) et petite clé n°2. Dans une salle calme (un Ronceau), un brasero allumé en (5,6) et une torche éteinte en (5,2), alignés sur la même colonne ; la clé n°2 est visible dans une alcôve fermée par une grille. Solution : se placer au sud du brasero (colonne 5) et tirer vers le nord : la flèche traverse le brasero, s'enflamme et allume la torche, ce qui ouvre la grille. Un escalier (angle sud-ouest) descend vers la salle 12 ; l'ouverture est (porte 06) donne sur l'antichambre et reste fermée de ce côté jusqu'à ce que le levier de la salle 09 l'ouvre.

<!-- salle_10 -->
```text
####################
#.......#C#........#
#....f...I.........#
#..................#
#...O..........O...#
#................P.I
#....Y.......E.....#
#..................#
#vP......P.........#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_07_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_09_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_06`, `type`=`interrupteur`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Sortie` (32,256,32,32) sur la tuile d'escalier `escalier_descendant` : `cible_carte`=res://scenes/rooms/donjon1_salle_12_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (80,272) : `id`=`depuis_escalier`
- `Ennemi` point (432,208) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (304,48) : `id`=`donjon1_coffre_05`, `contenu`=`cle_petite`, `important`=false
- `Torche` point (176,80) : `id`=`donjon1_torche_01`, `etat`=`eteinte`, `permanente`=false, `duree`=0, `cible`=`donjon1_porte_10`
- `Torche` point (176,208) : `id`=`donjon1_brasero_01`, `etat`=`allumee`, `permanente`=true (brasero)
- `Porte` (288,64,32,32) intérieure (grille) : `id`=`donjon1_porte_10`, `type`=`interrupteur`

### salle_11 - Cave d'arrivée (sous-sol)

Arrivée au sous-sol par l'escalier de la salle 09 : un lieu calme, deux Ronceaux, une **fresque** sur le mur nord qui montre trois symboles dans un ordre (gland, racine, feuille). Le joueur qui marche devant la fresque (rectangle d'indice) la lit ; elle donne l'ordre des cibles de la salle 13. Pas de statue ici : celle de la salle 09 est à un escalier d'ici.

<!-- salle_11 -->
```text
####################
#.......iii........#
#................P^#
#..................#
#...OO.........OO..#
#..................#
#..................#
#..E...........E...#
#........P.........#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_13_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (576,64,32,32) sur la tuile d'escalier `escalier_montant` : `cible_carte`=res://scenes/rooms/donjon1_salle_09_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (560,80) : `id`=`depuis_escalier`
- `Ennemi` point (112,240) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (496,240) : `type`=`ronceau`, `variante`=`normal`
- Rectangle nommé `indice_ordre_cibles` (256,32,96,32) : godot_node_type=area

### salle_12 - Galerie du retour (sous-sol)

Galerie du retour. On y arrive par l'escalier de la salle 10 ou en tombant du trou de la salle 07. La porte sud (vers la salle 14) est une grille **que l'on ne peut ouvrir que de l'autre côté** (levier de la salle 14) : de ce côté on la voit sans pouvoir la passer. Une récompense facultative : une plume de corbeau dans une alcôve fermée par une grille, ouverte quand un bloc est sur la plaque (14,2) **et** que Brann est debout sur la plaque (16,8).

Solution (12 pousses) : pousser le bloc vers l'est le long de la rangée 6 jusqu'à la colonne 14, puis vers le nord jusqu'à la plaque (14,2) ; aller ensuite se placer sur la plaque (16,8). Un Ronceau garde la salle (butin de flèches).

<!-- salle_12 -->
```text
####################
#F.#.............P^#
#..I..........p....#
####...............#
#........P.........#
#..................#
#.....B............#
#..................#
#...E....P......p..#
#..................#
#########I##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_14_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon1_porte_14`, `type`=`interrupteur`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (576,32,32,32) sur la tuile d'escalier `escalier_montant` : `cible_carte`=res://scenes/rooms/donjon1_salle_10_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (560,48) : `id`=`depuis_escalier`
- `Spawn` point (304,144) : `id`=`depuis_chute_salle_07` (arrivée du trou de passage de la salle 07)
- `Ennemi` point (144,272) : `type`=`ronceau`, `variante`=`normal`
- `Ramassable` point (48,48) : `id`=`donjon1_plume_02`, `contenu`=`plume_corbeau`
- `BlocPoussable` (6,6) -> centre (208,208)
- `PlaqueDePression` (448,64,32,32) : `id`=`donjon1_plaque_04`, `cible`=`donjon1_porte_15`, `declencheur`=`bloc`, `godot_node_type`=`area`
- `PlaqueDePression` (512,256,32,32) : `id`=`donjon1_plaque_05`, `cible`=`donjon1_porte_15`, `declencheur`=`joueur`, `godot_node_type`=`area`
- `Porte` (96,64,32,32) intérieure (grille) : `id`=`donjon1_porte_15`, `type`=`interrupteur`

### salle_13 - Salle des trois cibles (sous-sol)

**Séquence de trois cibles.** Au milieu d'une fosse (mortelle, mais jamais sur le chemin), trois cibles ornées de symboles. Le chemin de ronde permet de les atteindre toutes ; des piliers en (7,3), (13,3) et (10,9) ferment certains angles de tir, mais chaque cible se tire depuis au moins trois cases différentes, tout autour de la fosse (le joueur doit donc se déplacer entre deux tirs). L'ordre à toucher est celui de la fresque de la salle 11 : gland (nord-est), racine (sud), feuille (nord-ouest). Un mauvais ordre remet tout à zéro (flash et son, sans dégâts). Le bon ordre ouvre la grille (4,5) qui garde le vestibule de la porte à clé (porte 11, petite clé), derrière laquelle se trouve la galerie des torches. Un Ronceau garde la salle (butin de flèches).

<!-- salle_13 -->
```text
#########X##########
#...#..............#
#...#....P.........#
#...#..O.....O.....#
#...#..S~~~~~S.....#
D.P.I..~~~~~~~.....#
#...#..~~~~~~~.....#
#...#..~~~~~~~.....#
#...#..~~~S~~~..E..#
#...#.....O........#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_11_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_14_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_11`, `type`=`cle`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Ennemi` point (528,272) : `type`=`ronceau`, `variante`=`normal`
- `Interrupteur` (13,4) -> centre (432,144) : `id`=`donjon1_interrupteur_03`, `cible`=`donjon1_porte_12`, `mode`=`fleche`, `ordre`=1, `symbole`=`gland`
- `Interrupteur` (10,8) -> centre (336,272) : `id`=`donjon1_interrupteur_04`, `cible`=`donjon1_porte_12`, `mode`=`fleche`, `ordre`=2, `symbole`=`racine`
- `Interrupteur` (7,4) -> centre (240,144) : `id`=`donjon1_interrupteur_05`, `cible`=`donjon1_porte_12`, `mode`=`fleche`, `ordre`=3, `symbole`=`feuille`
- `Porte` (128,160,32,32) intérieure (grille) : `id`=`donjon1_porte_12`, `type`=`interrupteur`

### salle_14 - Galerie des torches (sous-sol)

**Chaîne de torches chronométrée** et grande clé. Un brasero allumé en (2,2) et trois torches éteintes (7,2), (7,8), (14,8). Il faut les allumer en chaîne : tirer vers l'est depuis (1,2) à travers le brasero (allume la torche 1) ; tirer vers le sud depuis (7,1) à travers la torche 1 allumée (allume la torche 2) ; tirer vers l'est depuis (6,8) à travers la torche 2 (allume la torche 3). Les trois torches doivent brûler **en même temps** : chacune s'éteint 15 s après avoir été allumée. Une rangée de fosses mortelles (rangée 5) oblige à contourner par l'ouest ou l'est : le parcours minimal demande environ 8 s. Quand les trois torches brûlent, la grille (17,2) de l'alcôve s'ouvre et révèle le **coffre de la grande clé**. Un levier à l'épée près de la porte nord ouvre la grille vers la salle 12 (raccourci vers l'escalier du retour). Un Ronceau (butin de flèches) rôde dans la partie nord.

<!-- salle_14 -->
```text
#########I##########
#.........l.....#C##
#.Y....f.P.......I.#
#............E.....#
#..................#
#...~~~~~~~~~~~~.P.D
#..................#
#..................#
#......f......f....#
#..................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_12_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon1_porte_14`, `type`=`interrupteur`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_13_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_11`, `type`=`cle`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (432,112) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (560,48) : `id`=`donjon1_coffre_07`, `contenu`=`grande_cle`, `important`=true
- `Torche` point (240,80) : `id`=`donjon1_torche_02`, `etat`=`eteinte`, `permanente`=false, `duree`=15, `cible`=`donjon1_porte_13`
- `Torche` point (240,272) : `id`=`donjon1_torche_03`, `etat`=`eteinte`, `permanente`=false, `duree`=15, `cible`=`donjon1_porte_13`
- `Torche` point (464,272) : `id`=`donjon1_torche_04`, `etat`=`eteinte`, `permanente`=false, `duree`=15, `cible`=`donjon1_porte_13`
- `Torche` point (80,80) : `id`=`donjon1_brasero_02`, `etat`=`allumee`, `permanente`=true (brasero)
- `Interrupteur` (10,1) -> centre (336,48) : `id`=`donjon1_interrupteur_07`, `cible`=`donjon1_porte_14`, `mode`=`epee` (levier)
- `Porte` (544,64,32,32) intérieure (grille) : `id`=`donjon1_porte_13`, `type`=`interrupteur`

### salle_15 - Cave secrète (sous-sol)

Cave secrète, **petite clé n°3 cachée**. On y arrive en sautant dans le trou de la salle 04 ou par l'escalier de la salle 05. Aucun puzzle : un Ronceau, un coffre, un escalier pour remonter. Elle apparaît sur la carte du donjon une fois la carte récupérée, ce qui donne un indice au joueur curieux. Cette clé ne sert que bien plus tard (porte 11, sous-sol) : c'est le « retour en arrière » du donjon.

<!-- salle_15 -->
```text
####################
#..................#
#..........C.......#
#..................#
#...O..........O...#
#........P.........#
#..................#
#............E.....#
#^P................#
#..................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (32,256,32,32) sur la tuile d'escalier `escalier_montant` : `cible_carte`=res://scenes/rooms/donjon1_salle_05_room.tscn, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (80,272) : `id`=`depuis_escalier`
- `Spawn` point (304,176) : `id`=`depuis_chute_salle_04` (arrivée du trou de passage de la salle 04)
- `Ennemi` point (432,240) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (368,80) : `id`=`donjon1_coffre_06`, `contenu`=`cle_petite`, `important`=false

### salle_boss - Salle du boss : Clairière de Sylve

Arène de Sylve (20x22, deux écrans en hauteur), inchangée. Quatre piliers de 2x2 cases. Phase 1 : viser les trois bulbes avec l'arc ; phase 2 : charges, l'esquive derrière un pilier l'assomme.

<!-- salle_boss -->
```text
####################
#..................#
#..................#
#..................#
#..................#
#..................#
#..................#
#...OO........OO...#
#...OO........OO...#
#..................#
#..................#
#..................#
#..................#
#...OO........OO...#
#...OO........OO...#
#..................#
#..................#
#..................#
#..................#
#........P.........#
#..................#
#########G##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,672,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_09_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,672,32,32) côté sud : `id`=`donjon1_porte_07`, `type`=`grande_cle`
- `Spawn` point (304,624) : `id`=`depuis_sud`
- Rectangle nommé `boss_sylve` (centre de la case (9,4) -> (304,144)) : point d'apparition de Sylve (convention existante)
- 4 rectangles nommés `pilier` (128,224,64,64), (448,224,64,64), (128,416,64,64), (448,416,64,64) : emplacement des piliers (convention existante)


## 5. Vérification des clés, des portes, des étages et des énigmes

Lancer `python -I maps/donjon1/verif_donjon.py` (bibliothèque standard seulement, environ 6 s). Résultat sur ce plan :

- **Structure** : 16 aperçus de la bonne taille, ouvertures aux positions fixes, chaque côté de porte avec le bon caractère et un Spawn d'arrivée, chaque Spawn `P` rattaché à une arrivée déclarée (côté, escalier ou chute), tables d'objets identiques aux aperçus (7 coffres, 15 portes, 3 escaliers, 2 trous de passage, 9 énigmes), aucun ennemi à moins de 3 cases d'une arrivée, aucun Spawn contre un trou, aucun bloc dans une salle à trous, à cibles ou à torches.
- **Parcours sur l'état du joueur** (salle, zone atteignable, portes ouvertes, petites clés, grande clé, arc) : **874 états atteignables, 0 état d'où le boss est hors de portée**. La salle du boss est donc atteignable quel que soit l'ordre dans lequel le joueur ouvre les portes, prend les coffres, tombe dans un trou, descend ou remonte un escalier, revient en arrière. Les 16 salles sont atteintes ; les 7 coffres et les 2 plumes sont atteignables ; les 9 énigmes sont faisables (les 2 facultatives aussi).
- **Clés** : 3 petites clés pour 3 portes à clé, les trois portes et les trois clés sont obligatoires ; au plus une porte à clé utilisable à la fois. Retirer une clé ou l'arc rend bien le boss inatteignable (auto-test).
- **Deux étages** : sans escalier ni trou, seuls 84 états sont atteignables, la grande clé et le boss restent hors de portée. La grande clé est au sous-sol, la porte du boss à l'étage. Les deux trous de passage descendent d'un étage, tombent sur un Spawn libre (à plus de 2 cases de tout trou), et depuis chaque état d'arrivée on peut remonter ou gagner. Auto-test : supprimer l'escalier de retour de la cave 15 est bien détecté (148 états piégés).
- **Énigmes** : plaques et blocs résolus par exploration complète des états (salle 03 : 14 pousses ; salle 05 : 25 pousses ; salle 12 : 12 pousses) ; cibles chronométrées de la 06 : 2,6 s au minimum pour 6 s accordées ; chaîne de torches de la 14 : 7,8 s au minimum pour 15 s accordées (le vérificateur exige moins de 70 % du temps) ; séquence de la 13 et levier : faisables depuis tous les états où elles restent à faire. Auto-test : ramener la limite des torches à 6 s rend le boss inatteignable.
- **Blocs** : dans les salles 03, 05 et 12, **aucun état où Brann est enfermé** (avec la règle « pas de bloc près d'une sortie ») ; il existe en revanche des états où l'énigme n'est plus résoluble (blocs coincés : 41 sur 138 en 03, 1289 sur 1894 en 05, 37 sur 125 en 12) : **sortir de la salle et y revenir remet les blocs en place** (à implémenter côté code : les blocs se réinitialisent à chaque chargement de la salle, c'est déjà le cas dans `Room`). Dans la salle 05, 3 états coupent momentanément la sortie d'arrivée sans enfermer Brann.

Hypothèses du vérificateur (à garder en tête) : déplacement sur grille à 4 voisins à 3,125 cases/s (estimation prudente) ; une porte `ennemis` s'ouvre quand la salle est nettoyée et reste ouverte ; les Lutins demandent l'arc (ou qu'ils descendent) ; **les flèches ne manquent pas** (butin garanti, salles de tir avec un ennemi) ; 0,7 s par tir (viser, tirer, vol) ; une flèche enflammée garde sa portée de 9 cases ; les ennemis ne bloquent pas les flèches.

## 6. Risques et décisions pour le développeur

1. **Munitions** : les énigmes de tir (06, 10, 13, 14) consomment des flèches. Le butin garanti (moins de 5 flèches : chaque ennemi tué en lâche une, et les ennemis réapparaissent au retour) est indispensable, d'où un Ronceau dans chaque salle de tir. Les torches chronométrées de la 14 demandent au moins 3 flèches propres.
2. **Portes sur les deux faces** : chaque porte non libre existe en double (même `id`) ; les grilles intérieures n'ont qu'une face. Un déclencheur est toujours dans une salle qui contient une face de sa porte (rien à propager).
3. **Chute de passage** : aucune perte de PV ; le trou doit se distinguer au premier coup d'œil d'une fosse mortelle (couleur, anneau de racines, lueur, animation). Un recul d'ennemi peut faire tomber Brann dans un trou de passage (c'est voulu et sans danger) ; un ennemi qui tombe disparaît sans butin.
4. **Torches et cibles chronométrées** : prévoir une option d'aide (durées doublées ou illimitées) pour l'enfant de 5 ans, dans les options d'accessibilité. Une cible ou une torche chronométrée doit montrer visiblement qu'elle va s'éteindre (flamme qui rétrécit, anneau qui se vide).
5. **Séquence de cibles** : un mauvais ordre remet tout à zéro avec un retour visuel et sonore, sans pénalité. Le texte de la fresque (`INDICE_ORDRE_CIBLES`) et l'image des trois symboles doivent exister avant la salle 13.
6. **Blocs** : la règle « pas de bloc sur ou à côté d'un Spawn, d'un `Sortie` ou d'une `Porte` » est indispensable : sans elle, un bloc poussé devant la porte est (19,5) de la salle 03 enferme Brann (le vérificateur le montre). Les blocs se réinitialisent à chaque chargement.
7. **Porte `ennemis` et retours** : les ennemis réapparaissent quand on revient dans une salle, mais une porte `ennemis` déjà ouverte reste ouverte (id mémorisé). En arrivant dans la 09 par l'escalier du sous-sol, la porte sud (déjà ouverte) ne se referme pas.
8. **Levier-raccourci de la 14** : la grille de la porte 14 se voit des deux côtés mais ne s'ouvre que depuis la 14. Si le joueur tombe dans la 12 par le trou de la 07, il voit cette grille fermée et remonte par l'escalier de la 10 : prévoir une indication visuelle (grille avec un levier dessiné de l'autre côté).
9. **Boss** : salle 20x22, quatre piliers de 2x2 cases ; couloirs libres de 3 cases sur les côtés, 8 cases au centre, 4 cases entre les rangées de piliers. Inchangé.
10. **Longueur** : 16 salles (11 au sol dont le boss, 5 au sous-sol) pour une partie d'environ 60 à 90 minutes la première fois ; à valider par le test de la phase 4 (2 ou 3 personnes sans aide).

## 7. Conventions et ressources manquantes (à demander)

**Nouvelles classes d'objets du calque `Objets`** (à ajouter au tableau de `CLAUDE.md` avant toute carte qui les utilise) :

| Classe | Forme | Propriétés | Comportement attendu |
| --- | --- | --- | --- |
| `PlaqueDePression` | rectangle 32x32, `godot_node_type`=`area` | `id`, `cible` (id d'une `Porte` de type `interrupteur`), `declencheur` (`bloc`, `joueur` ou `tous`, par défaut `tous`) | Enfoncée tant qu'un `BlocPoussable` (centre dans la case) ou Brann s'y trouve, selon `declencheur`. La `Porte` s'ouvre quand **toutes** les plaques de même `cible` sont enfoncées en même temps, puis reste ouverte (mémorisée par l'id de la porte). L'état des plaques n'est pas sauvegardé. |
| `Chute` | rectangle, `godot_node_type`=`area` | `id`, `cible_carte`, `cible_spawn` | Trou de passage : quand le centre de Brann entre dans la zone, courte animation de chute, transition vers la carte et le `Spawn` indiqués, **0 PV perdu**, 1 s d'invincibilité à l'arrivée. Un ennemi qui y tombe disparaît sans butin. Les tuiles `trou_passage` ne sont **pas** reconnues par `HoleRules` (seules les tuiles 58 à 66 sont mortelles). |
| `Torche` | point (centre de la case) | `id`, `etat` (`eteinte` ou `allumee`), `permanente` (bool : `true` = brasero qui ne s'éteint jamais), `duree` (secondes avant extinction, 0 = reste allumée), `cible` (id d'une `Porte` de type `interrupteur`) | Obstacle pour Brann (collision d'une demi-case), **transparente pour les flèches si elle est allumée** (la flèche passe et prend feu), arrête la flèche si elle est éteinte (la flèche enflammée l'allume). Toutes les torches de même `cible` doivent brûler en même temps pour ouvrir la porte (mémorisée ensuite). Une torche non permanente allumée s'éteint après `duree` secondes ; sa flamme rétrécit pendant les 3 dernières secondes. Un brasero n'a pas de `cible`. |
| `Interrupteur` (extension) | inchangé | `mode` (`fleche` ou `epee`), **nouveaux** : `ordre` (entier, 0 = pas d'ordre), `duree` (secondes, 0 = permanent), `symbole` (`gland`, `racine`, `feuille` : choix du sprite) | Plusieurs `Interrupteur` de même `cible` forment un **groupe** : la porte s'ouvre quand tous sont actifs ensemble. Avec `duree`, chaque cible touchée reste active `duree` secondes. Avec `ordre`, les cibles doivent être touchées dans l'ordre ; une cible hors ordre remet tout le groupe à zéro (flash et son). `mode`=`epee` avec `symbole` vide = levier. |
| `Sortie` (extension) | inchangé | **nouvelle propriété facultative** : `transition` (`escalier` : fondu et bruit de pas ; sinon la transition normale) | Un escalier est une `Sortie` posée sur une tuile 56 ou 57 ; le `Spawn` d'arrivée (`depuis_escalier`) est sur la case voisine. La `Sortie` ne se redéclenche pas tant que Brann n'a pas quitté sa zone. |
| Propriétés de carte | propriétés personnalisées de la carte Tiled | `etage` (`rdc` ou `sous_sol`), `carte_x`, `carte_y` (position dans la grille du donjon, voir §3) | Lues par la carte du menu pause : deux plans empilés, la boussole montre le boss, la carte montre aussi les salles non visitées (donc la cave secrète). |
| Rectangle `indice_*` | inchangé (`godot_node_type`=`area`) | nom `indice_ordre_cibles` (salle 11), `indice_ronces_coupees` (salle 05) | Affiche un texte (clés `INDICE_ORDRE_CIBLES` et `INDICE_RONCES_COUPEES` dans `textes.csv`). La fresque de la salle 11 est dessinée dans le décor ; le rectangle ne fait qu'ouvrir le texte. |

**Règles de comportement à coder** :
- **Flèche enflammée** : `Arrow` porte un état `Burning`. Elle devient `Burning` en traversant une `Torche` allumée (sans s'arrêter) ; une flèche `Burning` qui touche une torche éteinte l'allume et disparaît ; une flèche normale qui touche une torche éteinte disparaît sans effet. Sprite de flèche enflammée à fournir. Les cibles continuent de fonctionner avec une flèche enflammée.
- **Blocs** : `BlocPoussable` refuse de glisser vers une case où se trouve un `Spawn`, un `Sortie` ou une `Porte`, ou l'une de leurs 8 voisines. Les plaques sont des cases normales pour un bloc. Pas de bloc dans une salle à trous (règle existante).
- **Trous mortels et trous de passage** : à ne pas mélanger dans `HoleRules` (les tuiles `trou_passage` sont des tuiles décoratives sous un objet `Chute`).
- **Option d'aide** (accessibilité) : multiplicateur de `duree` des torches et des cibles.
- **Sauvegarde** : rien de nouveau (les portes ouvertes sont déjà mémorisées par leur `id` ; plaques, torches et cibles se réinitialisent au chargement de la salle).

**Ressources de ramassage** : `resources/pickups/carte_donjon.tres`, `boussole.tres`, `grande_cle.tres`, `plume_corbeau.tres` (coffres 01, 02, 07 ; ramassables des salles 03 et 12) avec `Icon` et `NameKey` (`OBJ_*`). `cle_petite` et `objet_arc` existent déjà (étape 1 du donjon, à vérifier).

**Scènes de salle à créer** par le développeur : `scenes/rooms/donjon1_salle_01_room.tscn` à `donjon1_salle_15_room.tscn` et `donjon1_salle_boss_room.tscn` (chacune avec sa `Zone` = `donjon1`) ; la scène de forêt `res://scenes/rooms/foret_temple_room.tscn` et son Spawn `depuis_temple` (sortie de la salle 01) restent à créer avec l'overworld. Après la victoire, retour au sud par la porte 07 ou nouvelle `Sortie` (à décider).

**Tuiles et sprites à demander au graphiste** (le graphiste décide des numéros ; propositions entre parenthèses) :

| Élément | Où | Détail |
| --- | --- | --- |
| `trou_passage` x9 (centre, 4 bords, 4 coins, comme les tuiles 58 à 66) | tileset `temple_racines`, réserve 31 à 39 | Tuiles décoratives sans collision. À distinguer **nettement** du trou mortel noir : anneau de racines ou de planches, fond vert-bleu lumineux avec un sol visible loin en dessous. Trous 2x2 dans le plan. |
| Variante « sous-sol » du sol et des murs (`dalle_sous_*`, `terre_sous_*`, ou tileset recoloré `temple_racines_sous_sol` à la même numérotation) | salles 11 à 15 | Plus sombre, bleu-vert, racines plus épaisses ; garder les mêmes numéros pour réutiliser les terrains. |
| `fresque_ordre_a/b/c` (3 tuiles de mur côte à côte) | salle 11, mur nord | Trois symboles dans l'ordre gland, racine, feuille, lisibles à 96 px de large. |
| `plaque_pression` : 2 images (relevée, enfoncée) | `art/puzzles/` | 32x32, doit se lire sur le sol de dalles. |
| `torche` : éteinte, allumée (animation 4 images), qui s'éteint (flamme qui rétrécit) ; `brasero` : allumé (animation 4 images) | `art/puzzles/` | Obstacle de 32x32, flamme nette même sur fond de dalles. |
| `fleche_enflammee` : 2 à 3 images | `art/items/` | Même taille que la flèche, avec flamme et traînée. |
| `cible_gland`, `cible_racine`, `cible_feuille` : 3 états chacune (inactive, active, erreur) ; `cible_chrono` (anneau ou jauge qui se vide, pour les cibles de la salle 06) | `art/puzzles/` | Les trois symboles de la fresque doivent être identiques à ceux des cibles. |
| `levier` : 2 images (haut, bas) | `art/puzzles/` | Posé sur le sol contre un mur, 32x32. |
| `grille_h` et `grille_v` (fermée, ouverte, animation d'ouverture) | `art/puzzles/` | Grilles intérieures de 32x32 pour les alcôves (03, 05, 10, 12, 13, 14) ; la grille 14 entre les salles 12 et 14 utilise l'image d'une porte `interrupteur` existante. |
| Animation de chute (Brann qui rétrécit en tournant) et de remontée par l'escalier | `art/player/` ou effet | Facultatif au début : un fondu suffit. |
| Sons : plaque qui s'enfonce, torche qui s'allume, flèche qui prend feu, bonne et mauvaise cible, chute, escalier | audio | Facultatif au début. |

## 8. Suite

À valider par la personne qui joue au projet. Après validation (étape 2) :

- **Reprises telles quelles** : `salle_01.tmx`, `salle_02.tmx`, `salle_08.tmx` (seule la variante d'un Ronceau passe de `rouge` à `normal`), `salle_boss.tmx`.
- **À retravailler** : `salle_03.tmx` (bloc, plaque, grille, alcôve), `salle_04.tmx` (trou de passage), `salle_05.tmx` (couloir à plaques, deux blocs, alcôve de la clé, escalier), `salle_06.tmx` (deux cibles, piliers, un coffre d'arc inchangé), `salle_07.tmx` (ouverture nord, trou de passage, plus de coffre), `salle_09.tmx` (refaite : escalier, levier, statue, plus de niche ni de grande clé).
- **À créer** : `salle_10.tmx` à `salle_15.tmx` (sous-sol : 11 à 15 avec le tileset de sous-sol).
- `verif_donjon.py` sera étendu pour relire aussi les `.tmx` et comparer leurs aperçus à ceux de ce fichier (comme à l'étape précédente) ; les anciennes cartes ne correspondent plus au plan et ne sont donc plus relues pour l'instant.
- Précisions de réalisation (reprises du plan précédent) : les fosses mortelles (`~`) sont peintes en rectangles avec le terrain `Trous` ; les `O` de 1 case sont `colonne_base` (Murs) + `colonne_haut` (Dessus) ; les piliers du boss sont des blocs 2x2 de `mur_coin_ext_*`. Les trous de passage sont peints en rectangles avec les tuiles `trou_passage`.
- À mettre à jour par ailleurs : `docs/roadmap.md` (tableau des donjons, ligne « Temple des Racines : 8 à 9 salles », devient 16 salles) et la phase 4 (briques d'énigmes : plaques, torches, trous de passage).
