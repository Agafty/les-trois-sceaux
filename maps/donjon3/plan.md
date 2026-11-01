# Plan du Sanctuaire Englouti (donjon 3) - 13 cartes (12 salles + le boss) sur deux étages

Document de conception (étape 1). **Aucun `.tmx` n'existe encore** : on attend la validation de ce plan, en particulier la mécanique de la lanterne (§2), qui n'est pas encore codée. Même format et même niveau de détail que `maps/donjon2/plan.md` (la Mine), dont les règles de raccord sont reprises telles quelles. Raccord avec le lac : `maps/overworld/plan_lac.md` (le portail du Sanctuaire vise `donjon3_salle_01_room.tscn` / `depuis_lac` ; le retour, et la sortie après le boss, visent `lac_room.tscn` / `depuis_sanctuaire`).
Les aperçus de ce fichier ont été relus par un script de vérification (bibliothèque standard seulement : taille des salles, ouvertures, accessibilité des objets, lignes de tir, parcours sur l'état du joueur) ; résultats au §8.

## 1. Intention et courbe de difficulté

**Intention** : donjon de la **lanterne**. Brann a déjà l'épée, l'arc et les bombes ; ici il apprend à **voir dans le noir** (un cercle de lumière devant lui), à **allumer des torches en s'en approchant**, à **révéler ce que l'obscurité cache** (murs à rune, Ombres noyées, cibles), puis à **combiner** lanterne, arc et épée (cibles dans le noir, Crabes-armures frappés dans le dos). Le rez-de-chaussée est clair, bleu, à demi noyé ; la lanterne est trouvée à la 4e salle sur 12 ; les cryptes du sous-sol sont les salles sombres. Public : un adulte qui découvre, et un enfant de 5 ans qui joue aidé (aucune énigme ne coûte de point de vie, **aucune fosse ni trou**, aucun chronomètre, les Ombres ne sont jamais obligatoires, la lanterne s'utilise sans toucher une seule touche).

**Récit** : le Sanctuaire était le temple des gardiens du lac. Ondine, la sirène qui le protège, est prisonnière d'une armure noire. Une **silhouette** observe Brann de loin (deux fois, sans un mot) ; juste avant le boss, **Corvan se dévoile** sur un balcon inaccessible ; après la victoire, il surgit, absorbe l'énergie du dernier sceau et lance le final (§7).

| Étape | Salle | Ce qui est appris ou testé | Tension |
| --- | --- | --- | --- |
| 1 | 01 Parvis | Le Têtard d'encre (2 coups, eau peu profonde) ; statue du corbeau | très faible |
| 2 | 02 Nef inondée | Carte ; la porte à clé nord est visible ; **première rune** dans un mur, vue mais pas franchissable ; silhouette de Corvan | faible |
| 3 | 03 Bassin des Têtards (facultative) | Boussole ; trois Têtards ; **mur fissuré** à la bombe (quart de cœur) | moyenne, optionnelle |
| 4 | 04 Chapelle | **Lanterne** (grand coffre) ; trois Têtards ; porte « ennemis » | moyenne |
| 5 | 05 Galerie des veilleuses | **Première salle sombre, sans ennemi** ; allumer deux torches en s'en approchant ; **petite clé n°1** derrière une grille | calme, découverte |
| 6 | 06 Salle des runes | **Mur à rune** obligatoire (la lanterne l'ouvre) ; levier ; première **Ombre noyée** (jamais obligatoire) | moyenne |
| 7 | 07 Pont des Crabes | **Crabe-armure** (frapper dans le dos) ; escalier vers les cryptes ; seconde silhouette | moyenne |
| 8 | 09 Crypte d'arrivée | Arrivée au sous-sol ; grille-raccourci vue de l'ouest | repos |
| 9 | 10 Salle des Ombres | **Trois Ombres** ; tourner la lanterne ; **petite clé n°2** | moyenne-haute |
| 10 | 11 Galerie des cibles | **Trois cibles à l'arc, vues dans la lumière** ; Crabe et Ombre | moyenne |
| 11 | 12 Reliquaire | **Grande clé** ; deux Crabes et deux Ombres ; levier-raccourci | haute (défi final) |
| 12 | 08 Antichambre | Porte du boss, statue du corbeau ; **Corvan se dévoile** | calme, narratif |
| 13 | Boss | Ondine : la lanterne montre où elle surgit (armure), puis morceaux d'armure à figer et frapper | boss |

Rythme : calme (01) - fight léger (02, 03) - **lanterne** (04) - **démo calme dans le noir** (05) - découverte et premier danger discret (06) - fight à dos (07) - repos (09) - pic sombre (10) - visée (11) - défi (12) - retour rapide - repos et révélation (08) - boss. La salle 03 et la plume de la 02 sont des plaisirs facultatifs.

## 2. La lanterne : mécanique proposée (à valider)

### 2.1 Ce qui existe déjà

- `resources/items/lanterne.tres` : `Id` = `lanterne`, `Type` = `Equipable`, `MaxQuantity` = 0, **pas de `UseScene`**, description « Éclaire les salles sombres et allume les torches. » (clés `ITEM_LANTERNE_NOM` / `ITEM_LANTERNE_DESC`, icône `art/ui/items/lanterne.png`).
- Les objets à touche (`use_item`) sont des `ItemData` avec une `UseScene` dont le script hérite de `ItemUse` (`Begin(Player, direction)`) ; il n'y a **qu'un objet équipé à la fois** (`GameState.EquippedItem`) : l'arc et les bombes se changent dans le menu.
- `Room.SetTint(Color)` pose un `CanvasModulate` (teinte de salle, HUD non teinté) ; `Torch.Light()` allume une torche ; `ItemType.KeyItem` existe (« possédé mais jamais équipé »).

### 2.2 Les choix, avec une recommandation pour chacun

| Question | Options | Recommandation |
| --- | --- | --- |
| **Objet à touche ou effet passif ?** | **A. Passif** : tant que Brann possède la lanterne, il la porte allumée dans les salles sombres ; elle ne prend pas la touche `use_item` (type `KeyItem`). **B. Interrupteur** : `use_item` l'allume et l'éteint (une `ItemUse` à bascule). **C. Éclair** : `use_item` lance un flash de 2 s qui révèle et fige, avec temps de recharge. | **A**. Un enfant de 5 ans ne doit pas penser à la lanterne ni échanger l'arc contre elle en plein combat (une seule touche d'objet) ; B ne sert à rien si elle ne s'use pas ; C oblige à changer d'objet. Le combat final (arc, bombes et lanterne ensemble) devient possible : la lanterne n'occupe pas la touche. Coût : `lanterne.tres` passe en `KeyItem` (aucune `UseScene`). |
| **Consomme-t-elle de l'huile ?** | **A. Non, jamais.** **B. Oui** : jauge qui baisse dans les salles sombres, huile de Garrick (10 rubis, roadmap). | **A**. Une jauge ajoute du stress et un risque de blocage (plus d'huile devant une salle sombre). **Conséquence** : l'huile de Garrick de la roadmap est à retirer ou à remplacer (par exemple par un autre article). À demander à l'utilisatrice (§11). |
| **Quelle obscurité ?** | **A. Pénombre** : la salle est teintée en bleu sombre (les murs et le sol restent devinables), Brann a un petit halo permanent (rayon 48 px) et, avec la lanterne, un grand cercle de lumière. **B. Noir quasi total** : on ne voit que le cercle. **C. Aucune salle sombre** : la lanterne ne ferait que révéler. | **A**. Le noir total fatigue et perd un joueur qui ne lit pas ; la pénombre garde la lisibilité (sorties, murs) et la lanterne reste utile. |
| **Forme de la lumière** | **A. Cercle centré sur Brann.** **B. Cercle décalé devant lui** (centre à 40 px dans la direction du regard, rayon 120 px : 5 cases devant, 2,5 cases derrière). | **B**. Une lanterne éclaire surtout devant : le joueur voit où il va, et une Ombre qui arrive **de dos** n'est figée que quand il se retourne (un peu de tension sans danger réel). |
| **Que révèle-t-elle exactement ?** | Voir 2.3. | Liste courte et lisible : pas de pont invisible ni de chasse au pixel. |

### 2.3 Ce que fait la lanterne (règles pour le développeur)

1. **Éclaire** (salles `obscurite`=`penombre`) : lumière chaude, cercle décalé devant Brann (2.2). Les torches et braseros allumés éclairent aussi (rayon 96 px) : ce sont les îlots de sécurité (arrivées, coffres importants). Les cibles et leviers dans le noir ne se voient que dans la lumière, **sans code** (c'est l'obscurité).
2. **Allume les torches** : une torche éteinte non permanente se rallume quand Brann reste à moins de 40 px d'elle pendant 0,5 s avec la lanterne (appel de `Torch.Light()`). Les torches de ce donjon ont `duree` = 0 (elles restent allumées) et `cible` = la grille de la 05. La flèche enflammée reste valable.
3. **Murs à rune** : `Porte` de `type` = `lanterne`, `apparence` = `mur_rune` (NOUVEAU). Le mur émet une faible lueur bleue, **visible même dans le noir** (une `PointLight2D` de 40 px, pour que le joueur la trouve). Quand Brann, lanterne portée, reste à moins de 64 px pendant 0,8 s, la rune s'allume et le mur s'ouvre pour toujours (`MarkCollected(id)`, état sauvegardé comme les autres portes). Il n'y a pas de `Sortie` dessous : c'est une alcôve à l'intérieur d'une salle.
4. **Ombre noyée** (`ombre_noyee`, 2 PV, vitesse 36 px/s, dégâts de contact d'un Têtard) : invisible et mobile hors de la lumière de la lanterne ; **figée et visible** tant que le cercle de lumière la couvre ; vulnérable dans les deux cas, mais on ne la frappe que si on la voit. Elle ne s'éclaire que par la lanterne (les braseros ne la révèlent pas : calque de lumière 2). Les rôdeurs se règlent sur le champ de la lanterne : une Ombre qui arrive de face est figée à 5 cases, une Ombre qui arrive de dos l'est à 2,5 cases.
5. **Morceaux d'armure** d'Ondine : même comportement que l'Ombre (§7).
6. **Rien d'autre** ne dépend de la lanterne dans ce donjon (pas de plateforme invisible, pas de texte caché).

### 2.4 Réglage et accessibilité

- Propriété de carte `obscurite` : `non` (défaut) ou `penombre` (NOUVEAU). `Room` pose la teinte de la salle (par exemple `0.30, 0.34, 0.55`) et ajoute le halo de Brann ; sans lanterne (on ne peut pas y arriver, sauf la 05) le halo de 48 px suffit à marcher.
- La 05 est la seule salle sombre accessible sans lanterne (la chapelle 04 mène à la 05 sans obliger à prendre le coffre) : elle ne contient **aucun ennemi**. Toutes les salles sombres à ennemis sont derrière la 05 (clé n°1) et donc après la lanterne (§8 le vérifie).
- Option d'aide : la lanterne n'a ni durée ni jauge, rien à régler. Le multiplicateur de durée (`PuzzleTimeMultiplier`) allonge seulement l'annonce des vagues d'Ondine (§7).
- Réutilisation : la grotte sombre de la montagne, la grotte noire de la falaise vers le château et le combat final réutilisent `obscurite`, les murs à rune et l'Ombre.

## 3. Le thème de l'eau

| Élément | Choix |
| --- | --- |
| Eau peu profonde (`w`) | Praticable, sans ralentissement ni dégâts (comme au lac) ; les Têtards y nagent mais errent aussi sur le sol ; sert de décor et de repère. |
| Eau profonde (`~`) | Solide pour Brann et les ennemis ; arrête les flèches ; forme les fossés des salles 07 et 08 (passerelle de planches `=` d'une largeur de 3 cases). |
| Fosses mortelles et trous de passage | **Aucun** : l'eau profonde remplace les trous, donc pas de `Chute`, pas de tuiles 58 à 66 ni 31 à 39 (numéros réservés, laissés vides, pour garder la numérotation commune des tilesets de donjon). |
| Niveau d'eau qui monte ou descend | **Option écartée.** Il faudrait changer les calques `Sol` et `Murs` (donc les collisions) pendant la partie, mémoriser l'état par salle, et gérer Brann, les blocs et les ennemis qui se trouveraient dans l'eau au moment du changement (risque de soft-lock). Le thème est servi sans cela : fossés, passerelles, bassins d'où surgit Ondine. |
| Blocs poussables et plaques | Non utilisés : le Temple et la Mine en ont déjà ; dans le noir, ils ajouteraient des soft-lock sans rien apprendre de plus. |

**Mécaniques existantes réutilisées** (aucune nouvelle classe d'objets Tiled sauf la `Porte` de type `lanterne` du §2.3) : épée et Têtards (01 à 04) ; carte, boussole, statues du corbeau ; bombes et mur fissuré (03) ; torches (05) ; leviers à l'épée (06, 12) ; cibles de flèche (11) ; porte à clé (02-06, 07-08), porte « ennemis » (04-05), porte grande clé (08-boss), grilles à interrupteur ; escalier entre étages (07-09) ; grand coffre (lanterne, grande clé).

## 4. Règles de raccord (valables pour toutes les salles)

Identiques au Temple et à la Mine (`maps/donjon2/plan.md` §2) : salle 20x11, mur du pourtour d'une case, **une seule position pour chaque ouverture** (nord (9,0), sud (9,10) ou (9,21) pour le boss, ouest (0,5), est (19,5)), `Spawn` d'arrivée `depuis_<côté>` à (9,2), (9,8) (boss : (9,19)), (2,5), (17,5), une `Porte` par face dans chacune des deux salles avec le même `id`, déclencheur toujours dans une salle qui contient une face de sa porte, un seul escalier par salle (`Spawn` `depuis_escalier` sur la case voisine ouest de la tuile d'escalier), aucun ennemi à moins de 3 cases d'un `Spawn`, levier ou cible jamais sur ou à côté d'une `Porte` ou d'une `Sortie`, et jamais dans un couloir d'une case. Particularités :

- Salle 01 : arrivée du lac `depuis_lac` en (9,8) (le `Sortie` de `lac.tmx` vise `donjon3_salle_01_room.tscn` / `depuis_lac`), et la `Sortie` sud de la 01 vise `lac_room.tscn` / `depuis_sanctuaire` (ce `Spawn` existe déjà dans `lac.tmx`, à 2 cases du portail).
- Les `Porte` de type `lanterne` (murs à rune) sont **intérieures** (une alcôve dans une salle) : elles n'ont pas de `Sortie` ni de seconde face.
- Les murs à rune ne portent ni `Sortie` ni `Porte` voisine : leur case d'approche (au moins 2 cases libres) est toujours dans la même salle.
- Pas de bloc, pas de trou, pas de plaque. Les Ombres et les Crabes sont des `Ennemi` ordinaires (`apparition` = `chargement`) ; ils réapparaissent à chaque retour dans la salle.
- Arc : butin de flèches garanti sous 10 flèches (`LootDropper.ArrowsBelow`) ; la salle 11 (cibles) contient un Crabe et une Ombre qui lâchent des flèches. Bombes : seule la 03 en demande une (facultative) ; butin de bombes garanti sous 3.

## 5. Plan des salles

```text
ÉTAGE (rez-de-chaussée : le Sanctuaire, clair puis sombre)

                          [boss]
                            G   (grande clé, du sous-sol)
                            |
                          [08]  statue, Corvan se dévoile
                            D   (petite clé n°2, du sous-sol)
                            |
                          [07] --v  (escalier vers les cryptes)
                            I   (levier caché dans la 06)
                            |
                          [06]  sombre, mur à rune
                            D   (petite clé n°1, de la 05)
                            |
      [03]-----------------[02]-----------------[04]=====N=====[05]
                            |                                    sombre
                          [01]
                            |
                          (lac)

SOUS-SOL (les cryptes noyées, toutes sombres)

   y=3   [09]^=====I=====[12]
          |               I
   y=2   [10]-----------[11]

Liens d'étage : escalier 07-09 (deux sens, seul lien).
Légende : - passage libre, D petite clé, G grande clé, N tous les ennemis morts, I interrupteur (levier, torches ou cibles),
= porte ou passage entre deux salles, ^ et v escaliers. Raccourci : 09-12 (levier de la 12).
```

Position des salles (carte du menu pause : propriétés de carte `etage`, `carte_x`, `carte_y`, même sens que le Temple et la Mine : y augmente vers le boss) :

| Étage | Salle | (x, y) | Étage | Salle | (x, y) |
| --- | --- | --- | --- | --- | --- |
| `rdc` | 01 | (1, 0) | `sous_sol` | 09 | (1, 3) |
| `rdc` | 02 | (1, 1) | `sous_sol` | 10 | (1, 2) |
| `rdc` | 03 | (0, 1) | `sous_sol` | 11 | (2, 2) |
| `rdc` | 04 | (2, 1) | `sous_sol` | 12 | (2, 3) |
| `rdc` | 05 | (3, 1) | | | |
| `rdc` | 06 | (1, 2) | | | |
| `rdc` | 07 | (1, 3) | | | |
| `rdc` | 08 | (1, 4) | | | |
| `rdc` | boss | (1, 5) | | | |

**Deux étages recommandés** (et non un seul) : le rez-de-chaussée clair rend la lanterne d'abord inutile puis évidente ; les quatre cryptes sombres forment un bloc cohérent, ce qui garde toutes les salles à ennemis sombres après la lanterne et rend le retour (raccourci 09-12, escalier) lisible sur la carte.

| Élément | Lieu |
| --- | --- |
| Statues du corbeau | salle 01 (`donjon3_statue_entree`, entrée) et salle 08 (`donjon3_statue_antichambre`, avant le boss) |
| Carte | salle 02, `donjon3_coffre_01` (en vue dès l'arrivée) |
| Boussole | salle 03, `donjon3_coffre_02` |
| **Lanterne** | **salle 04, `donjon3_coffre_03` (grand coffre, `important`=true, contenu `objet_lanterne`)**, 4e salle sur 12 dans l'ordre conseillé (premier tiers) |
| Petite clé n°1 | salle 05, `donjon3_coffre_04` (derrière la grille des torches : demande la lanterne) |
| Petite clé n°2 | salle 10 (sous-sol), `donjon3_coffre_05` |
| **Grande clé** | **salle 12 (sous-sol)**, `donjon3_coffre_06` (grand coffre, `important`=true) ; sert à la porte 08, **à l'étage du dessus**, dans la salle 08 |
| Quart de cœur (facultatif) | salle 03, `donjon3_quart_coeur_01`, derrière le mur fissuré `donjon3_mur_01` (bombe) |
| Plume de corbeau (facultative) | salle 02, `donjon3_plume_01`, derrière le mur à rune `donjon3_porte_05` (lanterne) |
| Réceptacle de cœur et sceau | salle du boss (`donjon3_boss_ondine_receptacle` et `donjon3_boss_ondine_sceau`) |

| Porte | Entre | Type | Ouverture |
| --- | --- | --- | --- |
| `donjon3_porte_01` | 02 (nord) et 06 (sud) | `cle` | une petite clé |
| `donjon3_porte_02` | 04 (est) et 05 (ouest) | `ennemis` | salle 04 nettoyée (3 Têtards) |
| `donjon3_porte_03` | grille intérieure de la 05 (9,7) | `interrupteur` | 2 torches `donjon3_torche_01` et `_02`, allumées avec la lanterne |
| `donjon3_porte_04` | 06 (nord) et 07 (sud) | `interrupteur` | levier à l'épée `donjon3_interrupteur_01`, caché derrière le mur à rune de la 06 |
| `donjon3_porte_05` | mur à rune de la 02 (16,1) | `lanterne` | lanterne portée à moins de 64 px (facultatif : plume) |
| `donjon3_porte_06` | mur à rune de la 06 (3,1) | `lanterne` | lanterne portée à moins de 64 px (**obligatoire** : levier) |
| `donjon3_porte_07` | 07 (nord) et 08 (sud) | `cle` | une petite clé |
| `donjon3_porte_08` | 08 (nord) et boss (sud) | `grande_cle` | grande clé |
| `donjon3_porte_09` | 11 (nord) et 12 (sud) | `interrupteur` | 3 cibles de flèche (`donjon3_interrupteur_02` à `04`), salle 11 |
| `donjon3_porte_10` | 09 (est) et 12 (ouest) | `interrupteur` | levier à l'épée `donjon3_interrupteur_05` (salle 12) : **raccourci** |

| Lien d'étage | Départ | Arrivée | Sens |
| --- | --- | --- | --- |
| `donjon3_escalier_01` | 07, tuile (18,8) | 09, tuile (18,2) | deux sens |

**Économie des clés** : 2 petites clés (n°1 en 05, n°2 en 10) pour 2 portes à clé (`porte_01`, `porte_07`), plus la grande clé pour `porte_08`. La clé n°1 est atteignable sans aucune porte à clé ; la clé n°2 est derrière la porte 01 (donc après la clé n°1). Comme la `porte_07` n'est atteignable qu'après la `porte_01`, **il n'existe qu'un seul ordre possible** : le joueur ne peut jamais dépenser une clé à la mauvaise porte. Au plus **1 clé en poche à la fois**. La grande clé n'ouvre que la porte du boss, elle est **au sous-sol** alors que la porte est à l'étage.

**Parcours conseillé** (celui que le vérificateur retrouve, à quelques détours facultatifs près) :
1. 01 (statue), 02 (carte, silhouette ; la porte nord est verrouillée, la rune est vue).
2. 03 (boussole, bassin ; quart de cœur à la bombe), puis 04 : **lanterne** ; nettoyer les Têtards, porte « ennemis ».
3. 05 (salle sombre) : allumer les deux torches, grille, **petite clé n°1** ; retour par 04 et 02 (plume derrière la rune, facultative).
4. 02 : porte nord (clé n°1), 06 : mur à rune, levier, porte nord.
5. 07 : Crabes (dans le dos), escalier vers les cryptes.
6. 09 (repos), 10 (Ombres, **clé n°2**), 11 (trois cibles), 12 (**grande clé**, levier-raccourci).
7. Retour par la grille de la 12 vers la 09, escalier vers la 07, porte à clé de la 07 (clé n°2), 08 : Corvan se dévoile, statue, porte du boss (grande clé), Ondine.

**Ordres possibles** : 03 et la plume de la 02 sont facultatives et se font à tout moment (avec la lanterne pour la plume) ; le levier de la 12 est un raccourci (oublié, on revient par la 11 et la 10 sans conséquence) ; les Ombres et les Crabes ne sont jamais obligatoires.

**Chaque blocage est visible avant d'être franchissable** :

| Blocage | Où on le voit | Où on le franchit |
| --- | --- | --- |
| Porte à clé 01 (nef) | dès l'arrivée dans 02 | après la clé n°1 (05) |
| Rune de la 02 | dès l'arrivée dans 02 (lueur bleue dans le mur) | avec la lanterne |
| Mur fissuré de la 03 | dès la première visite de 03 | avec la bombe (déjà possédée) |
| Porte « ennemis » de la 04 | dans 04 | tous les Têtards morts |
| Grille de la clé n°1 | dans 05, avec un brasero allumé derrière | deux torches allumées par la lanterne |
| Rune obligatoire de la 06 | dès l'entrée dans 06 (elle brille dans le noir) | avec la lanterne (déjà apprise en 02 et 05) |
| Porte nord de la 06 | dans 06 | levier derrière la rune |
| Porte du boss | dans 08, avant même de descendre | grande clé de la 12 |
| Grille vers 09 | dans 09 (côté bloqué) | levier de la 12 |
| Cibles de la 11 | dans 11, dès que la lanterne les éclaire | à l'arc |

Légende des aperçus : `#` mur ou pilier, `.` sol, `w` eau peu profonde (praticable), `~` eau profonde (solide), `=` passerelle de planches (praticable), `O` pilier ou colonne, `t` Têtard d'encre, `k` Crabe-armure, `u` Ombre noyée, `g` Ondine (boss), `P` Spawn d'arrivée, `C` coffre, `S` cible de flèche (dans le noir), `l` levier (interrupteur à l'épée), `f` torche éteinte, `Y` brasero allumé, `M` mur fissuré, `Z` mur à rune (`Porte` de type `lanterne`), `Q` quart de cœur, `F` plume, `R` statue du corbeau, `v` escalier descendant, `^` escalier montant, `V` balcon inaccessible (Corvan), `X` passage libre, `D` porte petite clé, `G` porte grande clé, `N` porte ennemis, `I` porte interrupteur (porte entre deux salles ou grille intérieure), `1` à `6` points d'apparition d'Ondine (bassins, boss), `n` repère de Corvan (boss).

## 6. Les salles

### salle_01 - Parvis du Sanctuaire

Premier pas : le Parvis, à demi noyé, derrière le portail du lac. Un seul Têtard d'encre, loin de l'arrivée, dans le bassin de l'est ; la statue du corbeau est à côté de l'arrivée. On y apprend que l'eau peu profonde se traverse (le sol brille, les colonnes sortent de l'eau) et que le Têtard se bat comme le Caillou rampant. Aucune obscurité : la lumière bleue de l'eau éclaire tout. Dalle gravée d'un sceau effacé au centre (décor).

Propriétés de carte : `etage`=`rdc`, `carte_x`=1, `carte_y`=0.

<!-- salle_01 -->
```text
#########X##########
#..................#
#........P.........#
#..www..O....O.www.#
#..www.........www.#
#..www.........wtw.#
#..www.........www.#
#..................#
#........P..R......#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,0,32,32) [côté nord] : `cible_carte`=`res://scenes/rooms/donjon3_salle_02_room.tscn`, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Sortie` (288,320,32,32) [côté sud, vers le lac] : `cible_carte`=`res://scenes/rooms/lac_room.tscn`, `cible_spawn`=`depuis_sanctuaire`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (304,272) : `id`=`depuis_lac`
- `StatueCorbeau` point (400,272) : `id`=`donjon3_statue_entree`
- `Ennemi` point (528,176) : `type`=`tetard_encre`, `variante`=`normal`

### salle_02 - Nef inondée

Carrefour et carte. Deux Têtards, quatre sorties (sud vers le Parvis, ouest, est, **porte à clé au nord visible dès l'arrivée**) et le coffre de la carte en vue. Dans l'angle nord-est, une **rune gravée dans le mur** (`Z`) brille faiblement : c'est la première fois que le joueur voit un passage caché, **avant d'avoir la lanterne** ; il y reviendra (alcôve de la plume, facultative). La **silhouette** de Corvan apparaît ici à la première visite (§7, cinématique muette de 4 secondes).

Propriétés de carte : `etage`=`rdc`, `carte_x`=1, `carte_y`=1.

<!-- salle_02 -->
```text
#########D##########
#...............Z.F#
#........P..C...####
#.ww..O......O..ww.#
#.ww............ww.#
X.P....t.........P.X
#.ww........t...ww.#
#.ww..O......O..ww.#
#........P.........#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,0,32,32) [côté nord] : `cible_carte`=`res://scenes/rooms/donjon3_salle_06_room.tscn`, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) [côté nord] : `id`=`donjon3_porte_01`, `type`=`cle`
- `Sortie` (288,320,32,32) [côté sud] : `cible_carte`=`res://scenes/rooms/donjon3_salle_01_room.tscn`, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Sortie` (0,160,32,32) [côté ouest] : `cible_carte`=`res://scenes/rooms/donjon3_salle_03_room.tscn`, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) [côté est] : `cible_carte`=`res://scenes/rooms/donjon3_salle_04_room.tscn`, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (512,32,32,32) [intérieure] : `id`=`donjon3_porte_05`, `type`=`lanterne`, `apparence`=`mur_rune`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Coffre` point (400,80) : `id`=`donjon3_coffre_01`, `contenu`=`carte_donjon`, `important`=`false`
- `Ennemi` point (240,176) : `type`=`tetard_encre`, `variante`=`normal`
- `Ennemi` point (400,208) : `type`=`tetard_encre`, `variante`=`normal`
- `Ramassable` point (592,48) : `id`=`donjon3_plume_01`, `contenu`=`plume_corbeau` (alcôve derrière la rune)
- Rectangle nommé `indice_rune_mur` (448,32,96,64) [texte `INDICE_RUNE_MUR`] : `godot_node_type`=`area`
- `Marqueur` point (304,48) : `id`=`silhouette_nef` (repère de la silhouette)
- `Scenario` point (304,176) : `cinematique`=`donjon3_silhouette_01`, `si`=`ouverture_fin`, `sauf`=`silhouette_vue_1`

### salle_03 - Bassin des Têtards (facultative)

Impasse facultative qui donne la boussole. Trois Têtards dans un bassin, le coffre de la boussole au nord-est. Dans l'angle sud-ouest, une alcôve fermée par un **mur fissuré** (`M`) contient un **quart de cœur** : Brann a déjà les bombes (acte 2), il peut l'ouvrir tout de suite (réutilise la bombe). Il se casse depuis (5,9) : pose contre le mur en (4,9), puis recule vers l'est (14 cases libres).

Propriétés de carte : `etage`=`rdc`, `carte_x`=0, `carte_y`=1.

<!-- salle_03 -->
```text
####################
#..................#
#..wwwwww.....C....#
#..wwtwww..........#
#..wwwwww..........#
#....www.........P.X
#....wwt...........#
#..........wtw.....#
####.......www.....#
#Q.M...............#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (608,160,32,32) [côté est] : `cible_carte`=`res://scenes/rooms/donjon3_salle_02_room.tscn`, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Coffre` point (464,80) : `id`=`donjon3_coffre_02`, `contenu`=`boussole`, `important`=`false`
- `Ennemi` point (176,112) : `type`=`tetard_encre`, `variante`=`normal`
- `Ennemi` point (240,208) : `type`=`tetard_encre`, `variante`=`normal`
- `Ennemi` point (400,240) : `type`=`tetard_encre`, `variante`=`normal`
- `Ramassable` point (48,304) : `id`=`donjon3_quart_coeur_01`, `contenu`=`quart_coeur`
- `MurFissure` (96,288,32,32) : `id`=`donjon3_mur_01`, `apparence`=`mur`

### salle_04 - Chapelle de la lanterne

Le **grand coffre de la lanterne**, sur une estrade entre deux braseros, gardé par trois Têtards. Un rectangle d'indice gravé (la lanterne sur le piédestal) donne le ton. La sortie est est une porte « ennemis » (3 Têtards) qui mène à la première salle sombre : on la voit fermée, on l'ouvre avec l'épée, on peut sortir de la salle sans prendre la lanterne mais **on ne peut pas vraiment avancer sans elle** (la 05 sert de démonstration, la 06 l'exige). C'est la **4e salle sur 12** (premier tiers).

Propriétés de carte : `etage`=`rdc`, `carte_x`=2, `carte_y`=1.

<!-- salle_04 -->
```text
####################
#..................#
#....Y...C...Y.....#
#..................#
#..................#
X.P..............P.N
#.....O...t..O.....#
#..................#
#...t...www....t...#
#.......www........#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (0,160,32,32) [côté ouest] : `cible_carte`=`res://scenes/rooms/donjon3_salle_02_room.tscn`, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) [côté est] : `cible_carte`=`res://scenes/rooms/donjon3_salle_05_room.tscn`, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) [côté est] : `id`=`donjon3_porte_02`, `type`=`ennemis`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Coffre` point (304,80) : `id`=`donjon3_coffre_03`, `contenu`=`objet_lanterne`, `important`=`true`
- `Torche` point (176,80) [brasero] : `id`=`donjon3_brasero_01`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (432,80) [brasero] : `id`=`donjon3_brasero_02`, `etat`=`allumee`, `permanente`=`true`
- `Ennemi` point (336,208) : `type`=`tetard_encre`, `variante`=`normal`
- `Ennemi` point (144,272) : `type`=`tetard_encre`, `variante`=`normal`
- `Ennemi` point (496,272) : `type`=`tetard_encre`, `variante`=`normal`
- Rectangle nommé `indice_lanterne_gravee` (256,96,96,64) [texte `INDICE_LANTERNE_GRAVEE`] : `godot_node_type`=`area`

### salle_05 - Galerie des veilleuses

**Première salle sombre, sans aucun ennemi** (démonstration). Brann y voit un cercle de lumière devant lui ; l'indice « Il fait sombre ici… » s'affiche à l'entrée. Deux torches éteintes (`f`) sont posées dans le fond : **marcher à côté d'une torche avec la lanterne l'allume** et elle éclaire alors toute la zone. Quand les deux brûlent, la grille du vestibule sud (`I`) s'ouvre et révèle le coffre de la **petite clé n°1**. Un brasero allumé dans le vestibule est visible à travers la grille dès l'arrivée (montrer avant d'exiger). Pas de flèche, pas de chrono.

Propriétés de carte : `etage`=`rdc`, `carte_x`=3, `carte_y`=1, `obscurite`=`penombre`.

<!-- salle_05 -->
```text
####################
#..................#
#....f........f....#
#..................#
#........O.........#
N.P................#
#..................#
#########I##########
#...Y..............#
#........C.........#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (0,160,32,32) [côté ouest] : `cible_carte`=`res://scenes/rooms/donjon3_salle_04_room.tscn`, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) [côté ouest] : `id`=`donjon3_porte_02`, `type`=`ennemis`
- `Porte` (288,224,32,32) [intérieure] : `id`=`donjon3_porte_03`, `type`=`interrupteur`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Coffre` point (304,304) : `id`=`donjon3_coffre_04`, `contenu`=`cle_petite`, `important`=`false`
- `Torche` point (144,272) [brasero] : `id`=`donjon3_brasero_03`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (176,80) : `id`=`donjon3_torche_01`, `etat`=`eteinte`, `permanente`=`false`, `duree`=`0`, `cible`=`donjon3_porte_03`
- `Torche` point (464,80) : `id`=`donjon3_torche_02`, `etat`=`eteinte`, `permanente`=`false`, `duree`=`0`, `cible`=`donjon3_porte_03`
- Rectangle nommé `indice_salle_sombre` (32,128,96,96) [texte `INDICE_SALLE_SOMBRE`] : `godot_node_type`=`area`

### salle_06 - Salle des runes

**Salle de la rune obligatoire**, sombre. L'arrivée (porte à clé au sud) est éclairée par deux braseros. Le **levier** qui ouvre la porte nord est dans une alcôve du nord-ouest fermée par un **mur à rune** (`Z`) : ce mur brille dans le noir (il émet une lueur bleue), on le voit de loin. Avec la lanterne, s'approcher du mur le fait s'ouvrir ; on entre, on frappe le levier à l'épée, la porte nord (`donjon3_porte_04`) s'ouvre. Deux **Ombres noyées** rôdent : invisibles hors de la lumière, elles se figent et apparaissent dès que la lanterne les éclaire (deux coups d'épée). Elles ne sont **pas obligatoires** à vaincre.

Propriétés de carte : `etage`=`rdc`, `carte_x`=1, `carte_y`=2, `obscurite`=`penombre`.

<!-- salle_06 -->
```text
#########I##########
#l.Z...............#
####.....P.........#
#....Y.........u...#
#.....O......O.....#
#..................#
#.....O......O.....#
#...u..............#
#.....Y..P..Y......#
#..................#
#########D##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,0,32,32) [côté nord] : `cible_carte`=`res://scenes/rooms/donjon3_salle_07_room.tscn`, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) [côté nord] : `id`=`donjon3_porte_04`, `type`=`interrupteur`
- `Sortie` (288,320,32,32) [côté sud] : `cible_carte`=`res://scenes/rooms/donjon3_salle_02_room.tscn`, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) [côté sud] : `id`=`donjon3_porte_01`, `type`=`cle`
- `Porte` (96,32,32,32) [intérieure] : `id`=`donjon3_porte_06`, `type`=`lanterne`, `apparence`=`mur_rune`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Torche` point (176,112) [brasero] : `id`=`donjon3_brasero_04`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (208,272) [brasero] : `id`=`donjon3_brasero_05`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (400,272) [brasero] : `id`=`donjon3_brasero_06`, `etat`=`allumee`, `permanente`=`true`
- `Interrupteur` point (48,48) [levier] : `id`=`donjon3_interrupteur_01`, `cible`=`donjon3_porte_04`, `mode`=`epee`
- `Ennemi` point (496,112) : `type`=`ombre_noyee`, `variante`=`normal`
- `Ennemi` point (144,240) : `type`=`ombre_noyee`, `variante`=`normal`
- Rectangle nommé `indice_ombre` (256,160,96,64) [texte `INDICE_OMBRE`] : `godot_node_type`=`area`

### salle_07 - Pont des Crabes

**Premier Crabe-armure.** Un canal d'eau profonde coupe la salle en deux ; une passerelle de planches de 3 cases de large est le seul passage. Un Crabe au sud (en vue dès l'arrivée) et un au nord : le Crabe charge en ligne droite, **sa carapace arrête l'épée de face et de côté** ; il faut le frapper **dans le dos** (esquiver sa charge, le laisser se cogner contre un mur ou un pilier, le contourner). Les piliers du nord et les braseros éclairent. L'escalier vers les cryptes est dans l'angle sud-est (côté arrivée), la porte à clé n°2 au nord. Seconde silhouette de Corvan (§7).

Propriétés de carte : `etage`=`rdc`, `carte_x`=1, `carte_y`=3.

<!-- salle_07 -->
```text
#########D##########
#..................#
#..O.k...P....Y....#
#..................#
#~~~~~~~===~~~~~~~~#
#~~~~~~~===~~~~~~~~#
#..................#
#.............k....#
#...Y....P.......Pv#
#..................#
#########I##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,0,32,32) [côté nord] : `cible_carte`=`res://scenes/rooms/donjon3_salle_08_room.tscn`, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) [côté nord] : `id`=`donjon3_porte_07`, `type`=`cle`
- `Sortie` (288,320,32,32) [côté sud] : `cible_carte`=`res://scenes/rooms/donjon3_salle_06_room.tscn`, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) [côté sud] : `id`=`donjon3_porte_04`, `type`=`interrupteur`
- `Sortie` (576,256,32,32) [sur la tuile d'escalier] : `cible_carte`=`res://scenes/rooms/donjon3_salle_09_room.tscn`, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Spawn` point (560,272) : `id`=`depuis_escalier`
- `Torche` point (464,80) [brasero] : `id`=`donjon3_brasero_07`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (144,272) [brasero] : `id`=`donjon3_brasero_08`, `etat`=`allumee`, `permanente`=`true`
- `Ennemi` point (176,80) : `type`=`crabe_armure`, `variante`=`normal`
- `Ennemi` point (464,240) : `type`=`crabe_armure`, `variante`=`normal`
- `Marqueur` point (528,80) : `id`=`silhouette_pont` (repère de la silhouette)
- `Scenario` rectangle (256,192,96,64) : `cinematique`=`donjon3_silhouette_02`, `si`=`ouverture_fin`, `sauf`=`silhouette_vue_2`, `godot_node_type`=`area`

### salle_08 - Antichambre d'Ondine

**Antichambre**, repos avant le boss. La **porte du boss est visible dès l'arrivée** au bout d'une chaussée de pierre qui traverse un fossé d'eau profonde ; dans l'angle nord-est, un **balcon** de pierre inaccessible (`V`). Statue du corbeau, deux braseros près de la chaussée, aucun ennemi. Quand Brann s'approche de la chaussée, Corvan **se dévoile sur le balcon** (§7). La porte nord demande la **grande clé**, qui est au sous-sol (salle 12).

Propriétés de carte : `etage`=`rdc`, `carte_x`=1, `carte_y`=4.

<!-- salle_08 -->
```text
#########G##########
#~~~~~~~===~~~~~VVV#
#~~~~~~~=P=~~~~~~~~#
#..................#
#......Y....Y......#
#...O..........O...#
#..................#
#..................#
#.....R..P.........#
#..................#
#########D##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,0,32,32) [côté nord] : `cible_carte`=`res://scenes/rooms/donjon3_salle_boss_room.tscn`, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) [côté nord] : `id`=`donjon3_porte_08`, `type`=`grande_cle`
- `Sortie` (288,320,32,32) [côté sud] : `cible_carte`=`res://scenes/rooms/donjon3_salle_07_room.tscn`, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) [côté sud] : `id`=`donjon3_porte_07`, `type`=`cle`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `StatueCorbeau` point (208,272) : `id`=`donjon3_statue_antichambre`
- `Torche` point (240,144) [brasero] : `id`=`donjon3_brasero_09`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (400,144) [brasero] : `id`=`donjon3_brasero_10`, `etat`=`allumee`, `permanente`=`true`
- `Marqueur` point (560,48) : `id`=`corvan_balcon` (le balcon inaccessible)
- `Scenario` rectangle (224,96,160,64) : `cinematique`=`donjon3_corvan_revele`, `sauf`=`corvan_revele`, `godot_node_type`=`area`

### salle_09 - Crypte d'arrivée (sous-sol)

**Arrivée au sous-sol, repos.** On descend l'escalier de la 07 ; la crypte est sombre mais deux braseros éclairent l'arrivée. Un Têtard dans un bassin, des piliers. L'ouverture sud mène à la 10 ; l'ouverture est est une **grille** qui ne s'ouvre que depuis la 12 (levier) : on la voit sans pouvoir la passer. Sol bleu-gris, algues lumineuses au mur (guide visuel).

Propriétés de carte : `etage`=`sous_sol`, `carte_x`=1, `carte_y`=3, `obscurite`=`penombre`.

<!-- salle_09 -->
```text
####################
#..................#
#....Y.......Y...P^#
#.....O......O.....#
#..................#
#..wwww..........P.I
#..wtww...O........#
#..wwww............#
#........P.........#
#..................#
#########X##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,320,32,32) [côté sud] : `cible_carte`=`res://scenes/rooms/donjon3_salle_10_room.tscn`, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) [côté est] : `cible_carte`=`res://scenes/rooms/donjon3_salle_12_room.tscn`, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Porte` (608,160,32,32) [côté est] : `id`=`donjon3_porte_10`, `type`=`interrupteur`
- `Sortie` (576,64,32,32) [sur la tuile d'escalier] : `cible_carte`=`res://scenes/rooms/donjon3_salle_07_room.tscn`, `cible_spawn`=`depuis_escalier`, `transition`=`escalier`, `godot_node_type`=`area`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Spawn` point (560,80) : `id`=`depuis_escalier`
- `Torche` point (176,80) [brasero] : `id`=`donjon3_brasero_11`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (432,80) [brasero] : `id`=`donjon3_brasero_12`, `etat`=`allumee`, `permanente`=`true`
- `Ennemi` point (144,208) : `type`=`tetard_encre`, `variante`=`normal`

### salle_10 - Salle des Ombres (sous-sol)

**Salle des Ombres.** Trois Ombres noyées dans une grande crypte sombre, deux braseros près de l'entrée nord ; le coffre de la **petite clé n°2** est au sud-ouest. Le joueur a appris dans la 06 que la lanterne fige et révèle les Ombres, ici il doit **tourner la lanterne** : les Ombres venant de derrière sont figées seulement quand le cercle de lumière les couvre. Les piliers servent d'abri. Les Ombres ne sont **pas obligatoires**, le coffre se prend en les évitant.

Propriétés de carte : `etage`=`sous_sol`, `carte_x`=1, `carte_y`=2, `obscurite`=`penombre`.

<!-- salle_10 -->
```text
#########X##########
#..................#
#......Y.P.Y.......#
#...u..............#
#.....O.....O......#
#................P.X
#.........u........#
#.....O.....O......#
#..C...........u...#
#..................#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,0,32,32) [côté nord] : `cible_carte`=`res://scenes/rooms/donjon3_salle_09_room.tscn`, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Sortie` (608,160,32,32) [côté est] : `cible_carte`=`res://scenes/rooms/donjon3_salle_11_room.tscn`, `cible_spawn`=`depuis_ouest`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (560,176) : `id`=`depuis_est`
- `Coffre` point (112,272) : `id`=`donjon3_coffre_05`, `contenu`=`cle_petite`, `important`=`false`
- `Torche` point (240,80) [brasero] : `id`=`donjon3_brasero_13`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (368,80) [brasero] : `id`=`donjon3_brasero_14`, `etat`=`allumee`, `permanente`=`true`
- `Ennemi` point (144,112) : `type`=`ombre_noyee`, `variante`=`normal`
- `Ennemi` point (336,208) : `type`=`ombre_noyee`, `variante`=`normal`
- `Ennemi` point (496,272) : `type`=`ombre_noyee`, `variante`=`normal`

### salle_11 - Galerie des cibles (sous-sol)

**Trois cibles dans le noir.** Les cibles ne sont visibles que dans la lumière : la lanterne montre une cible, l'arc la touche (portée 10 cases, plus que le cercle de lumière : on peut viser une cible vue de loin, ou en éclairant d'abord la zone). Ordre libre, aucune durée. Un Crabe-armure et une Ombre troublent la visée. La porte nord (`donjon3_porte_09`) s'ouvre quand les trois sont touchées. Un brasero au centre éclaire la salle.

Propriétés de carte : `etage`=`sous_sol`, `carte_x`=2, `carte_y`=2, `obscurite`=`penombre`.

<!-- salle_11 -->
```text
#########I##########
#..S............S..#
#........P.........#
#.....O......O.....#
#..................#
X.P......Y.........#
#..................#
#.....O......Ok....#
#....u.............#
#........S.........#
####################
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,0,32,32) [côté nord] : `cible_carte`=`res://scenes/rooms/donjon3_salle_12_room.tscn`, `cible_spawn`=`depuis_sud`, `godot_node_type`=`area`
- `Porte` (288,0,32,32) [côté nord] : `id`=`donjon3_porte_09`, `type`=`interrupteur`
- `Sortie` (0,160,32,32) [côté ouest] : `cible_carte`=`res://scenes/rooms/donjon3_salle_10_room.tscn`, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Spawn` point (304,80) : `id`=`depuis_nord`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Torche` point (304,176) [brasero] : `id`=`donjon3_brasero_15`, `etat`=`allumee`, `permanente`=`true`
- `Interrupteur` point (112,48) [cible dans le noir] : `id`=`donjon3_interrupteur_02`, `cible`=`donjon3_porte_09`, `mode`=`fleche`, `ordre`=`0`, `duree`=`0`, `symbole`=`feuille`
- `Interrupteur` point (528,48) [cible dans le noir] : `id`=`donjon3_interrupteur_03`, `cible`=`donjon3_porte_09`, `mode`=`fleche`, `ordre`=`0`, `duree`=`0`, `symbole`=`feuille`
- `Interrupteur` point (304,304) [cible dans le noir] : `id`=`donjon3_interrupteur_04`, `cible`=`donjon3_porte_09`, `mode`=`fleche`, `ordre`=`0`, `duree`=`0`, `symbole`=`feuille`
- `Ennemi` point (464,240) : `type`=`crabe_armure`, `variante`=`normal`
- `Ennemi` point (176,272) : `type`=`ombre_noyee`, `variante`=`normal`

### salle_12 - Reliquaire (sous-sol)

**Reliquaire** (défi final avant le retour). Le **grand coffre de la grande clé** est au nord, entre deux braseros. Deux Crabes-armures gardent les côtés, deux Ombres rôdent au sud. Un levier à l'épée, au sud-ouest, ouvre la grille de l'ouest : **raccourci** vers la crypte d'arrivée (09) et l'escalier du retour. Aucun combat n'est obligatoire : chaque ennemi se contourne.

Propriétés de carte : `etage`=`sous_sol`, `carte_x`=2, `carte_y`=3, `obscurite`=`penombre`.

<!-- salle_12 -->
```text
####################
#..................#
#........C.........#
#....k.Y....Y..k...#
#..................#
I.P...O......O.....#
#..................#
#..................#
#.l..u...P....u....#
#..................#
#########I##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,320,32,32) [côté sud] : `cible_carte`=`res://scenes/rooms/donjon3_salle_11_room.tscn`, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,320,32,32) [côté sud] : `id`=`donjon3_porte_09`, `type`=`interrupteur`
- `Sortie` (0,160,32,32) [côté ouest] : `cible_carte`=`res://scenes/rooms/donjon3_salle_09_room.tscn`, `cible_spawn`=`depuis_est`, `godot_node_type`=`area`
- `Porte` (0,160,32,32) [côté ouest] : `id`=`donjon3_porte_10`, `type`=`interrupteur`
- `Spawn` point (304,272) : `id`=`depuis_sud`
- `Spawn` point (80,176) : `id`=`depuis_ouest`
- `Coffre` point (304,80) : `id`=`donjon3_coffre_06`, `contenu`=`grande_cle`, `important`=`true`
- `Torche` point (240,112) [brasero] : `id`=`donjon3_brasero_16`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (400,112) [brasero] : `id`=`donjon3_brasero_17`, `etat`=`allumee`, `permanente`=`true`
- `Interrupteur` point (80,272) [levier] : `id`=`donjon3_interrupteur_05`, `cible`=`donjon3_porte_10`, `mode`=`epee`
- `Ennemi` point (176,112) : `type`=`crabe_armure`, `variante`=`normal`
- `Ennemi` point (496,112) : `type`=`crabe_armure`, `variante`=`normal`
- `Ennemi` point (176,272) : `type`=`ombre_noyee`, `variante`=`normal`
- `Ennemi` point (464,272) : `type`=`ombre_noyee`, `variante`=`normal`

### salle_boss - Salle du boss : le Bassin d'Ondine

Arène d'Ondine, **20×22** (deux écrans en hauteur ; aucune propriété `camera` : la caméra suit Brann, comme les salles de Sylve et de Gorm). Pénombre : deux braseros éclairent l'arrivée au sud, trois autres le centre et l'estrade d'Ondine. **Six bassins** d'eau peu profonde (un au centre de chaque aile) sont les points où elle surgit. Ce dont le boss a besoin côté carte :
- Point `boss_ondine` en (9,6) (304,208) (la scène `scenes/enemies/boss/ondine.tscn`, id `donjon3_boss_ondine`).
- 6 `Marqueur` `ondine_surgit_1` à `ondine_surgit_6` au centre des bassins (chiffres `1` à `6` de l'aperçu, de haut en bas, la gauche avant la droite) : points d'apparition d'Ondine.
- 4 rectangles `pilier` de 2×2 cases (comme Sylve et Gorm) qui arrêtent les morceaux d'armure et font abri.
- `Marqueur` `corvan_final` en (9,3) (304,112) (cinématique de fin, §7).
- Porte de l'arène : la `Porte` sud `donjon3_porte_08` se verrouille pendant le combat (`LockForEncounter`) et se rouvre à la victoire. Réceptacle et sceau : ramassables `donjon3_boss_ondine_receptacle` et `donjon3_boss_ondine_sceau` créés par la `Room`.
- `Room.VictoryExitScene` = `res://scenes/rooms/lac_room.tscn`, `Room.VictoryExitSpawn` = `depuis_sanctuaire`, `VictoryExitDelay` par défaut (2,2 s), réglés dans `donjon3_salle_boss_room.tscn`.
- `Scenario` point : `cinematique`=`donjon3_corvan_final`, `si`=`sceau:lac`, `sauf`=`corvan_final`.

Propriétés de carte : `etage`=`rdc`, `carte_x`=1, `carte_y`=5, `obscurite`=`penombre`.

<!-- salle_boss -->
```text
####################
#..................#
#........Y.........#
#.www....n.....www.#
#.w1w..........w2w.#
#.www..........www.#
#........g.........#
#..................#
#.....OO....OO.....#
#.www.OO....OO.www.#
#.w3w...Y..Y...w4w.#
#.www..........www.#
#..................#
#.....OO....OO.....#
#.....OO....OO.....#
#.www..........www.#
#.w5w..........w6w.#
#.www..........www.#
#..................#
#......Y.P..Y......#
#..................#
#########G##########
```

Objets Tiled (calque `Objets`). Coordonnées en pixels ; point = centre de la case.

- `Sortie` (288,672,32,32) [côté sud] : `cible_carte`=`res://scenes/rooms/donjon3_salle_08_room.tscn`, `cible_spawn`=`depuis_nord`, `godot_node_type`=`area`
- `Porte` (288,672,32,32) [côté sud] : `id`=`donjon3_porte_08`, `type`=`grande_cle`
- `Spawn` point (304,624) : `id`=`depuis_sud`
- `Torche` point (304,80) [brasero] : `id`=`donjon3_brasero_18`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (272,336) [brasero] : `id`=`donjon3_brasero_19`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (368,336) [brasero] : `id`=`donjon3_brasero_20`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (240,624) [brasero] : `id`=`donjon3_brasero_21`, `etat`=`allumee`, `permanente`=`true`
- `Torche` point (400,624) [brasero] : `id`=`donjon3_brasero_22`, `etat`=`allumee`, `permanente`=`true`
- `Marqueur` point (112,144) : `id`=`ondine_surgit_1`
- `Marqueur` point (528,144) : `id`=`ondine_surgit_2`
- `Marqueur` point (112,336) : `id`=`ondine_surgit_3`
- `Marqueur` point (528,336) : `id`=`ondine_surgit_4`
- `Marqueur` point (112,528) : `id`=`ondine_surgit_5`
- `Marqueur` point (528,528) : `id`=`ondine_surgit_6`
- Point nommé `boss_ondine` (304,208) (centre de la case (9,6))
- Rectangle nommé `pilier` (192,256,64,64)
- Rectangle nommé `pilier` (384,256,64,64)
- Rectangle nommé `pilier` (192,416,64,64)
- Rectangle nommé `pilier` (384,416,64,64)
- `Marqueur` point (304,112) : `id`=`corvan_final`
- `Scenario` point (304,400) : `cinematique`=`donjon3_corvan_final`, `si`=`sceau:lac`, `sauf`=`corvan_final`


## 7. Histoire et boss

### 7.1 Les moments d'histoire (système de cinématiques existant)

| Moment | Où | Comment | Fichiers et drapeaux |
| --- | --- | --- | --- |
| Silhouette n°1 | salle 02, à la première visite | cinématique muette de 4 s, **passable** | `resources/cinematiques/donjon3_silhouette_01.json`, `drapeau_fin` = `silhouette_vue_1`, `Scenario` point de la 02 |
| Silhouette n°2 | salle 07, quand Brann arrive devant la passerelle | cinématique muette de 4 s, **passable** | `donjon3_silhouette_02.json`, `drapeau_fin` = `silhouette_vue_2`, `Scenario` rectangle de la 07 |
| **Corvan se dévoile** | salle 08, quand Brann s'approche de la chaussée du boss | cinématique avec dialogue (5 répliques) | `donjon3_corvan_revele.json`, `drapeau_fin` = `corvan_revele`, `Scenario` rectangle de la 08 |
| Victoire sur Ondine | salle du boss | code existant (`Boss`) : porte rouverte, réplique d'Ondine, réceptacle et sceau | `BOSS_ONDINE_REPLIQUE` |
| **Corvan surgit et absorbe le sceau** | salle du boss, dès que Brann ramasse le sceau | cinématique de 15 s | `donjon3_corvan_final.json`, `drapeau_fin` = `corvan_final`, `Scenario` point (`si`=`sceau:lac`) |
| Retour au lac sous l'éclipse | `lac.tmx` (hors de ce plan) | cinématique courte à l'arrivée | `lac_retour_eclipse.json` (proposé), `si`=`corvan_absorbe_sceau`, `sauf`=`lac_eclipse_vu` |

**Silhouette : simple apparition, pas de scène.** Un personnage drapé (sprite `corvan_ombre`, ou le sprite `corvan` en repli) apparaît à un `Marqueur` (`silhouette_nef` en 02, `silhouette_pont` en 07), tourne la tête vers Brann, reste immobile 1,5 s, puis disparaît (`disparaitre`). Étapes : `apparaitre` (cible `pnj`) - `regarder` Brann vers lui - `attendre` 1,5 - `disparaitre` - `drapeau`. Aucun dialogue : l'enfant voit « quelqu'un », l'adulte comprend. Les deux apparitions n'ont aucune condition de lanterne et ne bloquent rien.

**Corvan se dévoile (salle 08).** Le balcon (`V`, `Marqueur` `corvan_balcon` en (17,1)) est inaccessible (fossé d'eau profonde). Étapes : `camera` vers `corvan_balcon` - `apparaitre` Corvan (sprite `corvan`, humain, voûté, tablier) - `dialogue` Brann - `dialogue` Corvan (plusieurs répliques) - `disparaitre` (fondu) - `camera` vers Brann - `drapeau` `corvan_revele`. Il ne **bloque pas** la porte : il n'attaque pas, il parle. Textes proposés (clés `DLG_D3_REVELE_n`, à faire valider) :
1. Brann : « Maître Corvan ? Vous êtes vivant ! »
2. Corvan : « Tu es doué, Brann. Je t'ai bien formé. »
3. Corvan : « Mes yeux me trahissent, mes mains tremblent. Morvath me rendra ma jeunesse. »
4. Brann : « Pourquoi ? Les sceaux protègent tout le monde ! »
5. Corvan : « Libère Ondine, petit. Il ne manque plus qu'un sceau. »

**Fin d'Ondine : ce qui se passe concrètement.** La sortie automatique vers le lac existe déjà (`VictoryExitScene`) et **attend la fin d'une cinématique**. On s'appuie dessus :
1. Victoire : la porte sud se rouvre, Ondine (libérée, sans armure) dit une réplique courte coupée en deux (`BOSS_ONDINE_REPLIQUE` : « Merci, forgeron... Prends mon sceau, vite ! »). Le réceptacle et le sceau apparaissent (ramassables uniques).
2. Brann ramasse le sceau (n'importe quel ordre avec le réceptacle) : `GameState.Seals` contient `lac`, l'**étape d'histoire passe à 3** (3 sceaux). C'est ce qui déclenche le `Scenario` (`si`=`sceau:lac`).
3. Cinématique `donjon3_corvan_final` (sans sauter le dialogue, mais **passable** en maintenant « pause ») : `teinte` éclipse (1,2 s) - `secousse` - `apparaitre` Corvan au `Marqueur` `corvan_final` (9,3) - `dialogue` Corvan - la lumière du sceau coule vers lui (`son`, `secousse`) - `dialogue` Brann - `dialogue` Corvan - `disparaitre` - `teinte` de retour à la pénombre de la salle - `drapeau` `corvan_absorbe_sceau` - `sauvegarder`.
4. La cinématique finie, et le réceptacle ramassé, le fondu existant renvoie Brann au lac (`lac_room.tscn` / `depuis_sanctuaire`).
5. Au lac, une courte cinématique pose le ciel d'éclipse (teinte de salle), cadre le château (`camera`) et fait dire une ligne à Brann (« C'est là qu'il m'attend. »). Le drapeau `corvan_absorbe_sceau` sert ensuite à ouvrir la route vers la grotte noire de la falaise (plan de l'overworld à venir) ; la lanterne y servira.
Brann **garde le sceau** (3 sceaux, étape 3) : Corvan n'en absorbe que l'énergie, comme l'annonce la roadmap (« chaque sceau restauré s'ouvre une dernière fois »).
Textes proposés (clés `DLG_D3_FINAL_n`) :
1. Corvan : « Merci, petit. Le dernier sceau est le plus doux. »
2. Brann : « Maître, arrêtez ! »
3. Corvan : « Le château t'attend, Brann. Viens... si tu l'oses. »

### 7.2 Boss : Ondine, la Gardienne du Lac

Principe (roadmap) : la lanterne montre où elle va surgir ; on frappe l'armure à chaque apparition ; l'armure se brise en morceaux qui attaquent seuls. L'arène est décrite dans la salle `boss` (§6). Scène `scenes/enemies/boss/ondine.tscn` (sous-classe de `Boss`, id `donjon3_boss_ondine`), corps en couche de collision 3 (comme Gorm : ne bloque ni Brann ni les flèches, s'arrête sur murs et piliers), boss sprite 96×96, armure sur un calque séparé qui clignote.

**Phase 1 : le surgissement (armure intacte).** Cycle d'environ 8 s, répété :
1. Ondine plonge (invisible, **intouchable**, 2 s).
2. **Annonce (1,5 s)** : elle choisit un bassin parmi ceux dont le centre est à moins de 190 px de Brann (lumière de la lanterne : 160 px, plus une marge), jamais deux fois le même d'affilée ; s'il n'y en a pas, le plus proche. Un anneau d'ondes y apparaît : on le voit **dans le cercle de lumière**, un « glou » s'entend partout. La lanterne sert donc à lire l'annonce.
3. Elle surgit : éclaboussure qui retire un demi-cœur à Brann **s'il est resté à moins de 28 px du centre** (il a eu 1,5 s pour s'écarter).
4. **Exposée 3,5 s** : l'armure clignote, on la frappe à l'épée (seule `HurtBox` `Armure` vulnérable). Elle replonge.
5. Après la perte de **6 PV d'armure** (environ trois apparitions ; valeur à régler selon `SwordRules`), l'armure éclate : phase 2.

**Phase 2 : les morceaux d'armure.** Ondine, sans armure, s'agenouille au centre, **invincible et inoffensive**. Quatre `morceau_armure` (casque, plastron, deux gantelets) partent d'elle **par vagues de deux** : même comportement que l'Ombre noyée (invisibles et mobiles hors de la lumière, figés et visibles dans le cercle de lumière), 2 PV chacun, vitesse 44 px/s, dégâts de contact d'un demi-cœur, corps arrêtés par les `pilier`. Ils lâchent de petits cœurs. Le boss est vaincu quand les quatre sont détruits : Ondine est libre.

**Faisable par un enfant aidé** : aucun chronomètre, chaque erreur coûte au plus un demi-cœur, annonces allongées par `PuzzleTimeMultiplier` (option d'aide), deux braseros près de l'arrivée pour se replier dans la lumière, petits cœurs lâchés par les morceaux d'armure, arène sans obstacle gênant, et la phase 2 ne demande que de se retourner pour figer.

Sprites : `ondine` (96×96, forme libre sous l'armure), `ondine_armure` (calque qui clignote), `morceau_armure_casque / plastron / gantelet` (32×32), anneau d'ondes (animation sur l'eau). Clés de texte : `BOSS_ONDINE_*`.

## 8. Vérification des clés, des portes, des étages et des énigmes

Script de vérification (bibliothèque standard seulement, non commité, relancé à chaque changement des aperçus) appliqué aux aperçus de ce fichier. Sortie du script :

```text
1. Structure : 13 salles (12 salles de 20x11 et l arene du boss de 20x22), pourtour plein, ouvertures aux positions fixes : OK
2. Accessibilite (objets, leviers, torches, cibles, coffres, ennemis, ouvertures) depuis les arrivees, barrieres internes ouvertes : OK
   05 : coffre de la clef atteignable grille fermee = False (attendu False)
   02 : plume atteignable rune fermee = False (attendu False)
   03 : quart de coeur atteignable mur intact = False (attendu False)
   03 : cases libres pour reculer vers l'est apres une bombe posee en (4,9) : 14
   08 : balcon de Corvan (16..18,1) atteignable = False (attendu False)
   06 : levier atteignable avant / apres la rune = False / True (attendu False / True)
   11 : cible (3, 1) : 19 cases de tir, distance de 1 a 9 cases (portee de l'arc 10)
   11 : cible (16, 1) : 19 cases de tir, distance de 1 a 9 cases (portee de l'arc 10)
   11 : cible (9, 9) : 20 cases de tir, distance de 1 a 9 cases (portee de l'arc 10)
   05 : torche (5, 2), 4 cases voisines libres
   05 : torche (14, 2), 4 cases voisines libres
3. Connexions : chaque ouverture a son vis-a-vis, meme type de porte des deux cotes (13 passages dont la sortie vers le lac) + 1 escalier : OK
   Etats du joueur atteignables : 1780 ; salles atteintes : 13/13
   Etats d'ou la salle du boss est hors de portee (soft-lock) : 0
   Petites cles en poche au maximum : 1
   Salles sombres visitables sans la lanterne : ['05']
   Porte p01 condamnee : boss atteignable = False
   Porte p07 condamnee : boss atteignable = False
   Porte p08 condamnee : boss atteignable = False
   Objets et portes obtenus : ['arc', 'bombes', 'boussole', 'grande_cle', 'lanterne', 'p01', 'p02', 'p03', 'p04', 'p07', 'p08', 'p09', 'p10', 'plume', 'quart'] ; manque : rien
RESULTAT GLOBAL : OK
```

Lecture :
- **Structure** : 13 aperçus de la bonne taille (12 de 20x11, le boss de 20x22), ouvertures uniquement aux positions fixes, chaque passage a le même type de porte des deux côtés, chaque objet (coffres, leviers, torches, cibles, quart de cœur, plume, statues) est **atteignable** depuis les arrivées de sa salle une fois les barrières de la salle ouvertes (mur fissuré, rune, grille), aucun ennemi à moins de 3 cases d'une arrivée.
- **Parcours sur l'état du joueur** (salle, petites clés en poche, portes ouvertes, objets obtenus, lanterne) : **aucun état d'où la salle du boss est hors de portée**, quel que soit l'ordre des portes, des coffres et des allers-retours ; les 13 salles sont atteintes ; les objets de progression (carte, boussole, lanterne, 2 petites clés, grande clé, quart de cœur, plume) sont tous obtenables. Les portes 01, 07 et 08 sont obligatoires (en condamner une rend le boss inatteignable).
- **Clés** : 2 petites clés pour 2 portes à clé, au plus 1 en poche à la fois ; un seul ordre d'ouverture possible (voir §5).
- **Lanterne** : les seules salles sombres visitables sans la lanterne sont la 05 (aucun ennemi) ; toutes les autres salles sombres exigent la clé n°1, donc la lanterne (la grille de la 05 demande la lanterne pour allumer les torches).
- **Énigmes** : 05 (deux torches, quatre cases voisines libres chacune), 06 (le levier n'est atteignable qu'après la rune), 11 (chaque cible a de 19 à 20 cases de tir à 9 cases ou moins, portée de l'arc 10), 03 (14 cases libres pour reculer après la bombe). **Aucun bloc poussable, aucune fosse** : pas de risque de bloc coincé, pas de salle à trous.
- **Non vérifié** (dépend du code et des tuiles) : la visibilité réelle des cibles dans la lumière, les collisions des tuiles de l'eau, l'import Godot (aucun `.tmx` n'existe encore).

Hypothèses : arc et bombes acquis (donjons 1 et 2), les ennemis ne bloquent pas les flèches, une porte « ennemis » reste ouverte une fois ouverte (état mémorisé par `id`), le butin garanti de flèches et de bombes joue sous ses seuils.

## 9. Risques et décisions pour le développeur

1. **Mécanique non codée** : toute la lanterne (§2) est nouvelle ; tant qu'elle n'est pas prête, aucune salle sombre ne peut être jouée. Recommandation : la coder et la tester en premier dans une salle d'essai.
2. **Teinte et cinématiques** : `Room.SetTint` sert à la fois à l'obscurité et aux cinématiques (`teinte`). La salle doit mémoriser sa teinte d'ambiance et la restituer quand une cinématique demande `teinte normal` (salles 05 à 12 et boss).
3. **Ombre invisible** : elle doit n'être éclairée que par la lanterne (calque de lumière 2 sur le sprite, `range_item_cull_mask` de la lanterne = 1+2, braseros et torches = 1) ; prévoir en plus une opacité nulle hors lumière. Non vérifiable en headless : à regarder en jeu.
4. **Cible, rune et levier dans le noir** : leur visibilité vient de l'obscurité, sans code ; mais une rune doit émettre sa propre lueur pour être trouvée.
5. **Crabe-armure** : vulnérable de dos seulement (`HurtBox.BlockFilter` inverse du Mineur : le coup est bloqué sauf si l'attaquant est dans le cône arrière de 120°) ; il faut un **repère visuel** (ventre ou dos pâle) pour que l'enfant comprenne. La bombe (3 PV) le tue aussi : à garder comme solution de secours (décision n°5).
6. **Têtard hors de l'eau** : comme au lac, le Têtard n'est pas confiné à l'eau (`ErrantEnemy`) ; c'est voulu (combat facile).
7. **Porte « ennemis » 04-05** : les Têtards réapparaissent à chaque retour dans la 04 ; l'état ouvert est mémorisé par `id`, donc on n'a pas à les retuer (à confirmer dans `Door`).
8. **Sceau `lac`** : le `Scenario` `sceau:lac` suppose que `sceau_lac.tres` (`SealEffect`) a `SealId` = `lac` ; sinon ajuster le pseudo-drapeau.
9. **Sortie après le boss** : la cinématique de fin peut commencer avant ou après le ramassage du réceptacle ; le code actuel attend déjà la fin d'une cinématique avant la sortie, mais il faut tester les deux ordres de ramassage.
10. **Longueur** : 12 salles, temps estimé 55 à 80 minutes la première fois, à valider par un test.
11. **Salles trop sombres** : régler la teinte d'ambiance (`0.30, 0.34, 0.55` proposé) pour que les sorties restent devinables sans lanterne.
12. **Conditions des `Scenario`** : les silhouettes utilisent `si`=`ouverture_fin` (une ancienne partie sans ce drapeau ne les verra pas, sans conséquence) ; le `Scenario` de la 08 n'a **pas** de `si` (la révélation de Corvan doit toujours avoir lieu) : à vérifier que `ScenarioWatcher` accepte une liste `si` vide, sinon utiliser `si`=`ouverture_debut,ouverture_fin` ou un drapeau posé par la lanterne.

## 10. Conventions et ressources manquantes (à demander)

### Mécanique à coder (NOUVEAU)

- **`lanterne.tres`** : `Type` = `KeyItem` (plus d'`Equipable`), aucune `UseScene`.
- **`LanternLight`** (script + scène, enfant de `Player`) : `PointLight2D` (texture générée par code, aucune image) décalée devant Brann (40 px, rayon 120 px) quand Brann possède `lanterne` et que la salle a `obscurite`=`penombre` ; halo permanent de 48 px sinon ; relève 10 fois par seconde les nœuds du groupe `eclairable` et leur dit s'ils sont éclairés (interface `ILanternReactive`, `SetLit(bool)` ; aucune allocation par image).
- **`Room`** : propriété de carte `obscurite` (`non`, `penombre`) : teinte d'ambiance et halo ; mémorisation de la teinte pour les cinématiques (risque 2).
- **`Door`** : valeur de type `lanterne` (NOUVEAU) et `apparence` `mur_rune` (NOUVEAU) : s'ouvre quand `LanternLight` reste à moins de 64 px pendant 0,8 s ; lueur propre ; mémorisé comme les autres portes.
- **`Torch`** : allumée par la lanterne à moins de 40 px pendant 0,5 s (appel de `Light()` existant).
- **Ennemis** : `ombre_noyee` (nouveau script `OmbreEnemy`, ou `ErrantEnemy` avec un état « figé » : à choisir par le développeur), `crabe_armure` (`ChasseurEnemy` + `HurtBox.BlockFilter` du dos, 3 PV), `morceau_armure` (variante de l'Ombre pour le boss). `tetard_encre` existe déjà.
- **Boss `Ondine`** : scène `scenes/enemies/boss/ondine.tscn`, cycle de surgissement, choix du bassin selon la lumière, phase 2 par vagues.

### Classes d'objets utilisées (déjà prévues dans `CLAUDE.md`, sauf la valeur `lanterne` de `Porte.type`)

`Spawn`, `Sortie` (`transition`=`escalier`), `Porte` (`cle`, `grande_cle`, `ennemis`, `interrupteur`, **`lanterne`** NOUVEAU, `apparence`=`mur_rune` NOUVEAU), `Interrupteur` (`fleche` sans durée, `epee` levier), `Torche` (brasero et torche), `MurFissure` (`mur`), `Coffre`, `Ramassable`, `StatueCorbeau`, `Ennemi` (`tetard_encre`, `crabe_armure`, `ombre_noyee`), rectangles `indice_*`, `boss_ondine`, `pilier`, `Marqueur`, `Scenario`. Propriétés de carte : `etage`, `carte_x`, `carte_y`, **`obscurite`** (NOUVEAU).

### Ressources de ramassage à créer (développeur)

- `resources/pickups/objet_lanterne.tres` : `GiveItemEffect` (`lanterne`), `Icon`, `NameKey` `OBJ_LANTERNE`, `ShowNameOnPickup`.
- `resources/pickups/sceau_lac.tres` : `SealEffect` (`SealId` = `lac`, `Icon` `art/items/sceau_lac.png`, `NameKey` `OBJ_SCEAU_LAC`).
- Existent déjà : `receptacle.tres`, `quart_coeur.tres`, `plume_corbeau.tres`, `carte_donjon.tres`, `boussole.tres`, `cle_petite.tres`, `grande_cle.tres`.
- Textes à ajouter à `textes.csv` : `INDICE_RUNE_MUR`, `INDICE_LANTERNE_GRAVEE`, `INDICE_SALLE_SOMBRE`, `INDICE_OMBRE`, `OBJ_LANTERNE`, `OBJ_SCEAU_LAC`, `SALLE_DONJON3_01` à `12` et `SALLE_DONJON3_BOSS`, `DLG_D3_REVELE_1` à `5`, `DLG_D3_FINAL_1` à `3`, `BOSS_ONDINE_*`.

### Code à compléter (développeur)

- Scènes de salle : `scenes/rooms/donjon3_salle_01_room.tscn` à `donjon3_salle_12_room.tscn` et `donjon3_salle_boss_room.tscn`, `Zone` = `donjon3` ; `Room.VictoryExitScene` = `res://scenes/rooms/lac_room.tscn`, `VictoryExitSpawn` = `depuis_sanctuaire` pour la salle du boss.
- `DungeonMap.cs` : plan du donjon 3 (positions du tableau du §5, liens, escalier 07-09, ids de portes et de coffres, `NameKey`).
- `TileRules` : paire fermée -> ouverte du mur fissuré des tilesets `sanctuaire` et `sanctuaire_crypte` (salle 03). Aucune règle de trou (`HoleRules`) à ajouter.
- Cinématiques : `resources/cinematiques/donjon3_silhouette_01.json`, `donjon3_silhouette_02.json`, `donjon3_corvan_revele.json`, `donjon3_corvan_final.json` (`Scenario` posés dans les cartes) ; plus `lac_retour_eclipse.json` avec un `Scenario` dans `lac.tmx` (hors de ce plan).
- Sauvegarde : **aucun nouvel état** (la lanterne est un objet, les portes sont mémorisées par `id`, les drapeaux de cinématique sont déjà sauvegardés).

### Propositions pour les fichiers communs (à appliquer par l'utilisatrice)

- `CLAUDE.md` : classe `Porte` type `lanterne` / `apparence` `mur_rune` ; propriété de carte `obscurite` ; ennemis `tetard_encre`, `crabe_armure`, `ombre_noyee` ; drapeaux `silhouette_vue_1/2`, `corvan_revele`, `corvan_final`, `corvan_absorbe_sceau` ; sceau `lac` ; lanterne passive (sans huile).
- `docs/roadmap.md` : Sanctuaire Englouti « 12 salles » devient « 13 cartes (12 salles + boss) sur 2 étages » ; huile de Garrick à retirer ou remplacer selon la décision n°1 ; lanterne passive.

### Tuiles à demander au graphiste (tilesets `sanctuaire` pour le rez-de-chaussée et `sanctuaire_crypte` à la même numérotation, plus sombre, algues lumineuses)

Garder les **mêmes numéros que les autres tilesets de donjon** pour ce que le code reconnaît : escaliers 56 (montant) et 57 (descendant) ; les numéros 58 à 66 et 31 à 39 restent vides (ce donjon n'a ni fosse ni trou). Le reste au choix du graphiste, avec un plan `art/tilesets/sanctuaire_plan.md`. S'inspirer de `lac` (façade du Sanctuaire) pour la pierre gris-violet et les bleus-verts froids.

| Élément | Détail |
| --- | --- |
| Sols | dalles de pierre mouillée (4 variantes), dalle gravée d'un sceau effacé, sol de crypte bleu-gris (4 variantes), algues lumineuses au sol ; terrain de bordure sol / eau |
| Eau peu profonde | sol brillant à reflets, praticable ; variante avec dalles affleurantes ; bords et coins (terrain) ; version crypte |
| Eau profonde | solide ; plein, 4 bords, 4 coins extérieurs et 4 intérieurs (terrain) ; animation de reflets ; collision pleine |
| Murs | pierre à demi noyée (algues), face + dessus, bords haut / bas / gauche / droite, coins (4 + 4), mur plein ; version crypte avec algues lumineuses |
| Murs fissurés (salle 03) | `mur_fissure` (fermé, solide, fissures claires) et `mur_fissure_ouvert` (ouvert, sans collision, calque `Decor`) ; **à coordonner avec `TileRules`** |
| Colonnes et piliers | `colonne_base` (Murs) et `colonne_haut` (Dessus) pour les `O` de 1 case ; bloc 2x2 pour les piliers du boss |
| Passerelle et chaussée | `planches_h`, `planches_v` (praticables, calque `Decor`), `chaussee_pierre` ; bord de fossé ; balcon `V` (plate-forme de pierre surélevée, solide, calque `Murs`) |
| Ouvertures de salle | `porte_haut`, `porte_bas` (passage de 20 px) et `porte_gauche`, `porte_droite` (24 px), cadre de pierre |
| Escaliers | `escalier_montant` (56), `escalier_descendant` (57), pierre noyée |
| Mur à rune | image de porte `art/puzzles/porte_mur_rune.png` (64x32 : fermée avec rune bleue lumineuse, puis ouverte) ; la tuile dessous est le fond de l'alcôve |
| Décor | vasques, fresques, algues, coquillages, statues brisées, lueurs bleues au sol, estrade d'Ondine (boss), bassins ronds (boss) |
| Portes par zone | `art/puzzles/porte_<type>_donjon3.png` (type : cle, grande_cle, ennemis ou interrupteur) (facultatif ; sinon les images par défaut) |
| Sprites hors tileset | `ombre_noyee`, `crabe_armure` (avec ventre ou dos pâle), `morceau_armure` (casque, plastron, gantelet), `ondine` (96x96) et `ondine_armure` (calque), anneau d'ondes, `corvan_ombre` (silhouette drapée), icône `sceau_lac`, icône de l'objet lanterne dans le coffre (`art/ui/items/lanterne.png` existe) |

## 11. Décisions pour l'utilisatrice

1. **La lanterne est-elle un effet passif, toujours allumée dans les salles sombres, sans huile ?** Recommandation : **oui**. Elle ne prend pas la touche d'objet (l'arc et les bombes restent utilisables), elle éclaire surtout devant Brann, allume les torches, ouvre les murs à rune, fige les Ombres. Conséquence : l'« huile de lanterne » de la boutique de Garrick (10 rubis) est retirée de la roadmap ou remplacée par un autre article.
2. **Quelle obscurité ?** Recommandation : **pénombre** (teinte bleue sombre, murs devinables, grand cercle de lumière devant Brann) plutôt que noir total, pour qu'un enfant ne se perde pas.
3. **Structure : deux étages (rez-de-chaussée clair, cryptes sombres), pas de niveau d'eau qui monte, aucun trou, aucun bloc ?** Recommandation : **oui** ; les fossés, les passerelles, les bassins d'Ondine servent le thème de l'eau sans risque de blocage.
4. **Histoire : deux silhouettes muettes (salles 02 et 07), Corvan qui se dévoile sur un balcon avant le boss (salle 08), puis Corvan qui surgit quand Brann ramasse le sceau d'Ondine, absorbe l'énergie (Brann garde le sceau, étape 3), disparaît, et retour au lac sous l'éclipse ?** Recommandation : **oui** ; tout s'appuie sur les cinématiques et la sortie automatique qui existent déjà.
5. **Le Crabe-armure (vulnérable seulement de dos, 3 coups) est-il trop difficile pour l'enfant de 5 ans ?** Recommandation : le **garder**, avec un ventre ou un dos pâle bien visible et la bombe comme solution de secours (3 PV), et jamais obligatoire de le vaincre.

**Décisions validées le 2026-11-01** :
1. Lanterne passive, toujours allumée, sans huile (l'huile est retirée de la boutique de Garrick).
2. Pénombre bleue.
3. Deux étages, sans niveau d'eau variable, sans trou ni bloc.
4. Histoire comme proposée (2 silhouettes, balcon, Corvan absorbe l'énergie, retour au lac sous l'éclipse).
5. **Crabe-armure simplifié** : vulnérable de partout (3 coups) **sauf pendant sa charge**, où sa carapace bloque les coups (`HurtBox.BlockFilter` actif seulement en état de charge). Il suffit d'esquiver la charge puis de frapper. Les descriptions « frapper dans le dos » des salles 07, 11 et 12 se lisent donc « esquiver la charge puis frapper ».

## 12. Suite

À valider par la personne qui joue au projet (surtout la lanterne, §2). Après validation (étape 2) :

- Le développeur code la lanterne (§10) et la teste dans une salle d'essai.
- Le graphiste livre le plan du tileset `sanctuaire` (et `sanctuaire_crypte`).
- Le level-designer crée `maps/donjon3/salle_01.tmx` à `salle_12.tmx` et `salle_boss.tmx` à partir de ce plan, avec un script de vérification qui relit aussi les `.tmx`.
- Mises à jour par ailleurs : `docs/roadmap.md` (Sanctuaire : 12 salles devient 13 cartes ; huile de lanterne ; cocher la phase 6 correspondante) et `CLAUDE.md` (nouvelles conventions du §10).
