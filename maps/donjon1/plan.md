# Plan du Temple des Racines (donjon 1)

Document de conception (étape 1). Aucun `.tmx` n'existe encore : on attend la validation de ce plan.
Le script `verif_donjon.py` (même dossier) **lit les aperçus de ce fichier** et prouve les propriétés annoncées plus bas.

## 1. Intention et courbe de difficulté

**Intention** : donjon tutoriel. Le joueur y apprend, dans l'ordre : frapper un ennemi sans danger, esquiver la charge d'un sanglier, tuer tout le monde pour ouvrir une porte, chercher une petite clé, obtenir l'arc, puis combiner arc + ennemis + interrupteurs avant le boss Sylve.

| Étape | Salle | Ce qui est appris ou testé | Tension |
| --- | --- | --- | --- |
| 1 | 01 Entrée | Frapper un Ronceau isolé ; la statue du corbeau (sauvegarde) | très faible |
| 2 | 02 Hall | 2 Ronceaux ; carte ; la porte à clé est visible | faible |
| 3 | 03 Antre (facultative) | Charge du Sanglier, piliers ; pousser un bloc (plume) | moyenne, optionnelle |
| 4 | 04 Broussailles | Porte « tous les ennemis morts » (2 Ronceaux + Sanglier) ; boussole | moyenne |
| 5 | 05 Ronces coupées | Repos ; indice sur Corvan ; petite clé n°1 | repos |
| 6 | 06 Salle de l'arc | Sanglier + Ronceau, **arc** (grand coffre), cible derrière un trou (démo sûre) | moyenne puis démo calme |
| 7 | 07 Allée des lutins | Lutins à l'arc ; petite clé n°2 | moyenne-haute |
| 8 | 08 Harde | Épreuve de force, variante rouge, porte « ennemis » | haute |
| 9 | 09 Antichambre | Arc + Lutins rouges + cible + grande clé | haute (puzzle) |
| 10 | Boss | Sylve | boss |

Rythme : calme (01) - fight léger (02) - fight (04) - **repos** (05) - fight + récompense (06) - tir (07) - force (08) - combinaison (09) - boss. La salle 03 est un détour facultatif de plaisir.

## 2. Règles de raccord (valables pour toutes les salles)

Salle 20×11 (mur du pourtour : 1 case d'épaisseur, intérieur 18×9). **Une seule position pour chaque ouverture** :

| Mur | Case d'ouverture (colonne, ligne) | Pixels (x, y, l, h) | Spawn d'arrivée (centre) | Id du Spawn |
| --- | --- | --- | --- | --- |
| haut (nord) | (9, 0) | (288, 0, 32, 32) | (304, 80) | `depuis_nord` |
| bas (sud) | (9, 10) (boss : (9, 21)) | (288, 320, 32, 32) (boss : y=672) | (304, 272) (boss : (304, 624)) | `depuis_sud` |
| gauche (ouest) | (0, 5) | (0, 160, 32, 32) | (80, 176) | `depuis_ouest` |
| droite (est) | (19, 5) | (608, 160, 32, 32) | (560, 176) | `depuis_est` |

- Un passage = un `Sortie` sur la case d'ouverture (de chaque côté) + un `Spawn` dans la salle d'arrivée. Le `Spawn` du côté X s'appelle `depuis_<côté X>` (on est arrivé *par* ce côté). Dans la salle 01, l'arrivée de la forêt (côté sud) s'appelle `depuis_foret`.
- Tuiles d'ouverture du tileset : `porte_haut/bas` (passage de 20 px) et `porte_gauche/droite` (24 px) ; Brann fait 16×20 px (capsule rayon 8, hauteur 20) : ça passe.
- Une porte non libre (`D`, `G`, `N`, `I`) est un objet `Porte` **posé sur la même case que le `Sortie`**, dans **chacune des deux salles, avec le même `id`** (l'état « ouverte » est mémorisé par l'id).
- Arc : flèche 300 px/s, `MaxDistance` 320 px (10 cases), `UseCost` 1, 10 flèches dans le coffre. Toutes les cibles se touchent à 9 cases ou moins, en ligne droite.

## 3. Plan des salles

```text
 y=3                [salle_09]=G=[salle_boss]      (le boss est en réalité au nord de la 09 : 20x22)
                       N
 y=2  [salle_06]=I=[salle_07]=D=[salle_08]
         D
 y=1  [salle_03]-[salle_02]-[salle_04]=N=[salle_05]
                    |
 y=0             [salle_01]--> forêt (overworld)

 - passage libre   D petite clé   G grande clé   N tous les ennemis morts   I interrupteur (flèche)
```

Cadre d'ensemble (orientation Nord en haut) : la 06 est au-dessus de la 02 (porte à clé 01), la 07 à l'est de la 06 (cible), la 08 à l'est de la 07 (porte à clé 04), la 09 au nord de la 08 (porte « ennemis » 05), le boss au nord de la 09 (grande clé).

| Élément | Lieu |
| --- | --- |
| Statue du corbeau | salle 01 |
| Carte | salle 02, `donjon1_coffre_01` |
| Boussole | salle 04, `donjon1_coffre_02` |
| Petite clé n°1 | salle 05, `donjon1_coffre_03` (sert à la porte 01) |
| Arc | salle 06, `donjon1_coffre_04` (grand coffre) |
| Petite clé n°2 | salle 07, `donjon1_coffre_05` (sert à la porte 04) |
| Grande clé | salle 09, `donjon1_coffre_06` (grand coffre, sert à la porte 07) |
| Boss | salle boss (au nord de la 09) |
| Plume de corbeau (facultative) | salle 03, derrière le bloc, `donjon1_plume_01` |

| Porte | Entre | Type | Ouverture |
| --- | --- | --- | --- |
| `donjon1_porte_01` | 02 (nord) et 06 (sud) | `cle` | petite clé n°1 |
| `donjon1_porte_02` | 04 (est) et 05 (ouest) | `ennemis` | salle 04 nettoyée |
| `donjon1_porte_03` | 06 (est) et 07 (ouest) | `interrupteur` | flèche dans `donjon1_interrupteur_01` |
| `donjon1_porte_04` | 07 (est) et 08 (ouest) | `cle` | petite clé n°2 |
| `donjon1_porte_05` | 08 (nord) et 09 (sud) | `ennemis` | salle 08 nettoyée |
| `donjon1_porte_06` | intérieure de la 09 (niche) | `interrupteur` | flèche dans `donjon1_interrupteur_02` |
| `donjon1_porte_07` | 09 (nord) et boss (sud) | `grande_cle` | grande clé |

**Économie des clés** : 2 petites clés pour 2 portes à clé, une seule porte à clé à la fois accessible (voir la vérification). La grande clé n'ouvre que la porte du boss.

Légende des aperçus : `#` mur, `.` sol, `~` trou, `O` pilier ou mur isolé, `r` ronces noires (solides), `i` brèche coupée net (indice), `P` Spawn d'arrivée, `E` ennemi (Ronceau, Sanglier), `L` Lutin des branches, `C` coffre, `S` cible/interrupteur (flèche), `B` bloc poussable, `F` plume, `R` statue du corbeau, `X` passage libre, `D` porte petite clé, `G` porte grande clé, `N` porte ennemis, `I` porte interrupteur.

## 4. Les salles

### salle_01 - Entrée

Premier pas. Un seul Ronceau, loin de l'arrivée, dans une grande salle vide : on apprend à l'approcher, à le frapper, à se faire toucher sans conséquence. La statue du corbeau est à côté de l'arrivée.

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

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/foret_temple_room.tscn (à créer), `cible_spawn`=`depuis_temple`, `godot_node_type`=`area`
- `Spawn` point (304,272) : `id`=`depuis_foret`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Ennemi` point (496,112) : `type`=`ronceau`, `variante`=`normal`
- `StatueCorbeau` (13,8) -> centre (432,272) : `id`=`donjon1_statue_01`

### salle_02 - Hall des racines

Carrefour. Deux Ronceaux ; trois sorties libres (ouest, est) et une porte à clé au nord, **visible dès l'arrivée** : le joueur sait qu'il lui faudra une clé. Le coffre de la carte est en vue (sécurité : coffre ouvert d'emblée).

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

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_01_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_03_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_04_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_06_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon1_porte_01`, `type`=`cle`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Ennemi` point (240,176) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (400,208) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (496,80) : `id`=`donjon1_coffre_01`, `contenu`=`carte_donjon`, `important`=false

### salle_03 - Antre du sanglier

Impasse facultative. **Un seul Sanglier** dans une salle avec piliers : on apprend la charge et à s'écarter pour qu'il se cogne. Derrière un bloc poussable, une plume de corbeau : le bloc est présenté sans danger (voir le contrôle des blocs). Le joueur peut sauter cette salle ; la salle 04 réutilise le sanglier.

<!-- salle_03 -->
```text
####################
###.#..............#
###.F#.............#
###B#.....O........#
#.............O....#
#................P.X
#.............O....#
#.....E...O........#
#..................#
#..................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (208,240) : `type`=`sanglier_noirci`, `variante`=`normal`
- `BlocPoussable` (3,3) -> centre (112,112)
- `Ramassable` (4,2) -> centre (144,80) : `id`=`donjon1_plume_01`, `contenu`=`plume_corbeau` (ressource à créer)

### salle_04 - Salle des broussailles

Porte « ennemis ». Deux Ronceaux et un Sanglier ; la porte est du côté est, fermée tant qu'ils ne sont pas tous morts. Le coffre de la boussole attend au fond (on le prend en passant).

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
#.............E....#
#..................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_05_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_02`, `type`=`ennemis`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (208,80) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (464,272) : `type`=`ronceau`, `variante`=`normal`
- `Ennemi` point (336,176) : `type`=`sanglier_noirci`, `variante`=`normal`
- `Coffre` point (496,80) : `id`=`donjon1_coffre_02`, `contenu`=`boussole`, `important`=false

### salle_05 - Salle des ronces coupées

Repos et indice. Aucun ennemi. Une haie de ronces noires coupe la salle en deux ; **le passage est une coupure nette** (les ronces sont tranchées à ras, comme avec un outil de forge). C'est le seul chemin vers le coffre de la petite clé.

<!-- salle_05 -->
```text
####################
#..................#
#........C.........#
#..................#
#rrrrrrriiirrrrrrrr#
N.P................#
#..................#
#..................#
#....O........O....#
#..................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_04_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_02`, `type`=`ennemis`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Coffre` point (304,80) : `id`=`donjon1_coffre_03`, `contenu`=`cle_petite`, `important`=false
- Décor : tuiles `ronces_bloc_a/b` sur la ligne 4 (colonnes 1-7 et 11-18), coupées à ras de chaque côté de la brèche (colonnes 8-10)
- **Indice** : rectangle nommé `indice_ronces_coupees` (256,128,96,32), sur la brèche (voir « Conventions à créer »)

### salle_06 - Salle de l'arc

Salle de l'arc. Le joueur a la petite clé (porte 01). Un Sanglier et un Ronceau gardent le grand coffre. Une fois l'arc en main, **démonstration sans danger** : la porte est est fermée, une cible se trouve de l'autre côté d'un trou que l'épée ne peut pas atteindre ; une flèche suffit.

<!-- salle_06 -->
```text
####################
#.............~~~~~#
#.....C.......~~~~S#
#.............~~~~~#
#...O.....O........#
#................P.I
#..................#
#..E....O....O.....#
#........P....E....#
#..................#
#########D##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_02_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon1_porte_01`, `type`=`cle`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_07_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_03`, `type`=`interrupteur`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (464,272) : `type`=`sanglier_noirci`, `variante`=`normal`
- `Ennemi` point (112,240) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (208,80) : `id`=`donjon1_coffre_04`, `contenu`=`objet_arc`, `important`=true
- `Interrupteur` (18,2) -> centre (592,80) : `id`=`donjon1_interrupteur_01`, `cible`=`donjon1_porte_03` (mode flèche)

### salle_07 - Allée des lutins

Première mise en pratique de l'arc contre des ennemis : deux Lutins des branches aux deux extrémités, des piliers pour se couvrir, un Ronceau. La petite clé n°2 est dans le coffre, à découvert dans le tir croisé.

<!-- salle_07 -->
```text
####################
#......L...........#
#................C.#
#....O....O...O....#
#..................#
I.P.......E......P.D
#..................#
#....O....O...O....#
#..................#
#............L.....#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_06_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_03`, `type`=`interrupteur`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Sortie` (608,160,32,32) côté est : `cible_carte`=res://scenes/rooms/donjon1_salle_08_room.tscn, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) côté est : `id`=`donjon1_porte_04`, `type`=`cle`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Ennemi` point (240,48) : `type`=`lutin_des_branches`, `variante`=`normal`
- `Ennemi` point (432,304) : `type`=`lutin_des_branches`, `variante`=`normal`
- `Ennemi` point (336,176) : `type`=`ronceau`, `variante`=`normal`
- `Coffre` point (560,80) : `id`=`donjon1_coffre_05`, `contenu`=`cle_petite`, `important`=false

### salle_08 - Salle de la harde

Épreuve de force (variante rouge). Sanglier rouge et deux Ronceaux rouges dans une salle à piliers ; sortie au nord par une porte « ennemis ». Aucun puzzle : on teste l'esquive et l'épée avant la salle d'énigme.

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

- `Sortie` (0,160,32,32) côté ouest : `cible_carte`=res://scenes/rooms/donjon1_salle_07_room.tscn, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) côté ouest : `id`=`donjon1_porte_04`, `type`=`cle`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_09_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon1_porte_05`, `type`=`ennemis`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Ennemi` point (496,208) : `type`=`sanglier_noirci`, `variante`=`rouge`
- `Ennemi` point (400,80) : `type`=`ronceau`, `variante`=`rouge`
- `Ennemi` point (240,304) : `type`=`ronceau`, `variante`=`rouge`

### salle_09 - Antichambre du cerf

Combinaison finale : deux Lutins rouges et un Ronceau rouge, une cible derrière un trou (même principe qu'en 06, cette fois sous le feu), qui ouvre une niche contenant la **grande clé**. Porte de la grande clé juste au nord, vers le boss.

<!-- salle_09 -->
```text
#########G##########
#~~~~~~.....#......#
#S~~~~~..P..#...C..#
#~~~~~~.....#......#
#...........###I####
#..........E.......#
#.....O......O.....#
#..L............L..#
#........P.........#
#..................#
#########N##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; « centre » = centre de la case.

- `Sortie` (288,320,32,32) côté sud : `cible_carte`=res://scenes/rooms/donjon1_salle_08_room.tscn, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) côté sud : `id`=`donjon1_porte_05`, `type`=`ennemis`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Sortie` (288,0,32,32) côté nord : `cible_carte`=res://scenes/rooms/donjon1_salle_boss_room.tscn, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) côté nord : `id`=`donjon1_porte_07`, `type`=`grande_cle`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Ennemi` point (112,240) : `type`=`lutin_des_branches`, `variante`=`rouge`
- `Ennemi` point (528,240) : `type`=`lutin_des_branches`, `variante`=`rouge`
- `Ennemi` point (368,176) : `type`=`ronceau`, `variante`=`rouge`
- `Coffre` point (528,80) : `id`=`donjon1_coffre_06`, `contenu`=`grande_cle`, `important`=true
- `Interrupteur` (1,2) -> centre (48,80) : `id`=`donjon1_interrupteur_02`, `cible`=`donjon1_porte_06` (mode flèche)
- `Porte` (480,128,32,32) intérieure, mur de la niche : `id`=`donjon1_porte_06`, `type`=`interrupteur`

### salle_boss - Salle du boss : Clairière de Sylve

Arène de Sylve (20×22, deux écrans en hauteur). Quatre piliers de 2×2 cases. Phase 1 : viser les trois bulbes avec l'arc ; phase 2 : charges, l'esquive derrière un pilier l'assomme.

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
- Rectangle nommé `boss_sylve` (centre de la case (9,4) -> (304,144)) : point d'apparition de Sylve (convention à créer)
- 4 rectangles nommés `pilier` (128,224,64,64), (448,224,64,64), (128,416,64,64), (448,416,64,64) : emplacement des piliers (convention à créer)

## 5. Vérification des petites clés, des portes et des blocs

Lancer `python maps/donjon1/verif_donjon.py` (bibliothèque standard seulement). Résultat sur ce plan :

- **Parcours sur l'état du joueur** (salle, côté d'arrivée, portes ouvertes, coffres ouverts, interrupteurs touchés, salles nettoyées ; clés et arc déduits des coffres ouverts) : 56 514 états atteignables, **0 état d'où le boss est hors de portée**. La salle du boss est donc atteignable quel que soit l'ordre dans lequel le joueur ouvre les portes, prend les coffres, nettoie les salles ou revient en arrière.
- **Clés** : 2 petites clés pour 2 portes à clé ; **au plus une porte à clé utilisable à la fois** (01 avant d'avoir l'arc, 04 ensuite). La clé n°1 est derrière une porte « ennemis » (sans clé), la clé n°2 derrière la porte à cible (sans clé) : jamais de clé enfermée derrière la porte qu'elle ouvre. La grande clé n'ouvre que la porte du boss.
- **Auto-test** : retirer une des deux clés, ou remplacer la clé n°2 par une carte, rend bien le boss inatteignable (le vérificateur détecte un manque de clé).
- **Blocs** : un seul bloc, dans un couloir d'une case de large (salle 03). Il ne peut aller que de (3,3) vers (3,1) : 3 positions, pas de coin où se coincer, et Brann a toujours son chemin de retour libre derrière lui. Le script explore toutes les positions : 0 état sans retour vers l'entrée. Dans tous les cas, **sortir de la salle et y revenir remet le bloc à sa place** (à implémenter côté code : le bloc se réinitialise à chaque chargement de la salle). Le bloc est facultatif (il ne garde que la plume).
- Chemin le plus court vers le boss (récupéré par le script) : 02, 04 (nettoyer), 05 (clé 1), 02 (porte 01), 06 (arc, cible), 07 (clé 2), porte 04, 08 (nettoyer), 09 (cible, grande clé), porte 07, boss.

Hypothèses du vérificateur (à garder en tête) : déplacement sur grille à 4 voisins (estimation prudente) ; une porte `ennemis` s'ouvre quand la salle est nettoyée et reste ouverte (état mémorisé) ; les Lutins demandent l'arc (ou qu'ils descendent) : aucune porte `ennemis` n'est dans une salle à Lutins ; **les flèches ne manquent pas**.

## 6. Risques et décisions pour le développeur

1. **Pénurie de flèches** : l'arc donne 10 flèches ; le joueur peut les gaspiller avant d'avoir touché la cible de la salle 06. Il faudrait garantir un butin de flèches (par exemple : un ennemi qui meurt lâche toujours une flèche si le joueur possède l'arc et a moins de 5 flèches), et que les ennemis réapparaissent quand on quitte puis revient dans la salle. Sans cette règle, un soft-lock est possible.
2. **Portes sur les deux faces** : chaque porte non libre existe en double (un objet `Porte` dans chacune des deux salles, même `id`) ; l'état est mémorisé par l'`id`.
3. **Porte `ennemis`** : fermée tant que les `Ennemi` de la salle ne sont pas tous morts, puis ouverte définitivement (id mémorisé). Seule la sortie est verrouillée : l'entrée d'où l'on vient reste libre (la porte 02 se ferme côté salle 04 quand on y entre, mais le joueur peut repartir par la porte ouest).
4. **Trous (`~`)** : le tileset n'a pas de collision sur les trous ; la chute (dégât et retour à l'entrée de la salle) est à implémenter (convention `trou` demandée par le graphiste).
5. **Cibles de flèche** : l'`Interrupteur` doit accepter la flèche (`IArrowTarget`) et pas l'épée (cible hors de portée de l'épée, derrière un trou). Une propriété `mode` (`fleche`, `epee`) est à ajouter à l'`Interrupteur` (convention à créer).
6. **Boss** : salle 20×22, quatre piliers de 2×2 cases ; couloirs libres de 3 cases sur les côtés, 8 cases au centre, 4 cases entre les rangées de piliers. À valider en jeu avec la taille réelle de Sylve (3 cases de large si 96 px).

## 7. Conventions et ressources manquantes (à demander)

| Élément | Où | Proposition |
| --- | --- | --- |
| `resources/pickups/carte_donjon.tres`, `boussole.tres`, `grande_cle.tres`, `plume_corbeau.tres` | coffres 01, 02, 06 ; ramassable plume | `PickupEffect` avec `Icon` et `NameKey` (`OBJ_*`) |
| Propriété `mode` de `Interrupteur` | salles 06 et 09 | `fleche` (toutes les cibles de ce donjon) |
| Objet rectangle `indice_ronces_coupees` | salle 05 | à transformer en classe `Indice` (id, clé de texte) quand le texte existera |
| Objets rectangle `boss_sylve` et `pilier` | salle boss | le boss y lit son point de départ et le groupe des piliers qui l'assomment |
| Scène de forêt `res://scenes/rooms/foret_temple_room.tscn` et Spawn `depuis_temple` | sortie de la salle 01 | à créer avec l'overworld (la sortie de la salle 01 pointe dessus) |
| Porte intérieure | salle 09, case (15,4) | un `Porte` de type `interrupteur` posé dans un mur intérieur (tuile `porte_bas`) |
| Réinitialisation des blocs | salle 03 | le bloc revient à (3,3) à chaque chargement de la salle |
| Sortie du boss | salle boss | après la victoire, retour au sud par la porte 07 ou nouvelle `Sortie` (à décider) |

Scènes de salle à créer par le développeur : `scenes/rooms/donjon1_salle_01_room.tscn` à `donjon1_salle_09_room.tscn` et `donjon1_salle_boss_room.tscn` (chacune avec sa `Zone` = `donjon1`).

Tuiles à prévoir pour l'étape 2 (carte) : murs, portes (`porte_haut` à `porte_droite` et leurs `*_dessus`), trous (rectangles), ronces (`ronces_bloc_a/b`), colonnes (`colonne_base` + `colonne_haut` pour les `O` de 1 case), bloc de mur 2×2 (terrain `Murs`) pour les piliers du boss, sols (`dalle_*`, `terre`), décors (racines, mousse, feuilles). **Rien ne manque pour l'instant**, sauf la tuile d'un pilier fait de ronces coupées (facultatif, on utilisera les ronces).

## 8. Suite

Plan validé. Les 10 cartes `salle_01.tmx` à `salle_boss.tmx` sont créées (étape 2) et `verif_donjon.py` relit aussi les `.tmx` : il reconstruit l'aperçu de chaque carte et le compare à ceux de ce fichier. Décisions validées : butin de flèches garanti (moins de 5 flèches avec l'arc : chaque ennemi tué en lâche une, et les ennemis réapparaissent au retour dans la salle) ; couloirs du boss (3 à 8 cases) et Sylve de 96 px acceptés.

Précisions de réalisation : les trous (`~`) sont peints en rectangles avec les tuiles du terrain `Trous` ; les deux cibles (salles 06 et 09) sont posées sur la dernière colonne ou la première du rectangle de trou ; les `O` de 1 case sont `colonne_base` (Murs) + `colonne_haut` (Dessus) ; les piliers du boss sont des blocs 2×2 de `mur_coin_ext_*`.
