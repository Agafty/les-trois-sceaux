# Les Trois Sceaux — instructions pour Claude

## Le projet

**Les Trois Sceaux** (*The Three Seals*) est un Zelda-like 2D en vue de dessus, inspiré de *A Link to the Past* (Super Nintendo).
Le héros, **Brann**, apprenti forgeron, doit restaurer trois sceaux avant la prochaine éclipse.

- Moteur : **Godot 4 (édition .NET)**, dernière version stable 4.x
- Langage : **C#** uniquement (pas de GDScript)
- Plateformes : PC (Windows, Linux, macOS). Pas d'export web (non supporté officiellement en C#).
- Développeur : solo, sur son temps libre. Il connaît la programmation mais **découvre Godot**.

La conception complète (scénario, personnages, carte, bestiaire, économie, phases de développement) est dans **`docs/roadmap.md`**. C'est la référence : lis la section concernée avant de proposer du code ou du contenu.

## Phase en cours

**Phase 4 — Premier donjon complet (vertical slice).** (Mettre à jour cette ligne à chaque changement de phase.)

## Comment travailler avec moi

- Explique le code que tu proposes, en particulier ce qui est propre à Godot (nœuds, scènes, signaux, cycle de vie). Je débute sur le moteur.
- Avance par petites étapes testables : une fonctionnalité à la fois, que je peux lancer dans l'éditeur.
- Quand une étape demande une manipulation dans l'éditeur Godot (créer une scène, ajouter un nœud, régler une propriété), décris-la précisément, étape par étape.
- Quand une tâche de la roadmap est terminée, coche-la dans `docs/roadmap.md` (`- [ ]` → `- [x]`).
- Si une demande contredit la roadmap, signale-le avant de coder.
- Réponds en français.

## Réglages techniques fixés

- Résolution de base : **640×360** (16:9 ; ×2 en 720p, ×3 en 1080p, ×4 en 1440p, ×6 en 4K), tuiles de **32×32 px**
- Sprites : **tous** les personnages dans une case de **32×32**, Corvan compris (le plus grand, tenu en 32×32 grâce à son dos voûté), boss en **64×64 à 96×96**, proportions trapues (grosse tête) pour la lisibilité
- Stretch mode `viewport`, scale mode `integer`, filtre de texture `Nearest`
- Caméra : défilement par écran dans les donjons, caméra qui suit dans l'overworld
- Un écran = **20×11 tuiles** (640×352 px ; les 8 px restants en bas servent de marge, le HUD est en surimpression) ; overworld de 5×4 écrans = 100×44 tuiles

## Agents du projet

Cinq agents sont définis dans `.claude/agents/` : `developpeur`, `relecteur`, `testeur`, `graphiste`, `level-designer`.
Pour chaque tâche de code : **developpeur** → **relecteur** → corrections → **testeur** → commit. Le graphiste et le level-designer travaillent en parallèle.
Aucun agent n'installe ni ne télécharge quoi que ce soit sans mon accord.

### Partage des fichiers entre agents

Pour que plusieurs agents travaillent en même temps sans s'écraser, chacun ne modifie que son territoire :

| Agent | Peut modifier | Ne touche pas |
| --- | --- | --- |
| `graphiste` | `art/`, `tools/sprites/`, création de nouveaux `.tsx` dans `maps/tilesets/` | `maps/**/*.tmx`, `scenes/`, `scripts/` |
| `level-designer` | `maps/**/*.tmx` (et `.tx` si besoin) | `maps/tilesets/*.tsx`, `art/`, `scenes/`, `scripts/` |
| `developpeur` | `scripts/`, `scenes/`, `resources/`, `project.godot`, `.csproj`, `localization/` | `art/`, `maps/` |
| `relecteur`, `testeur` | rien (ils lisent et rapportent) ; le testeur peut ajouter des tests | — |

- Fichiers communs (`CLAUDE.md`, `docs/roadmap.md`) : un agent qui veut y ajouter une convention ou cocher une tâche le **propose dans son rapport** ; je l'applique (ou je donne mon accord explicite).
- Un besoin hors de son territoire (une tuile manquante pour le level-designer, une nouvelle classe d'objet Tiled, une scène à créer) est **demandé dans le rapport**, jamais fait directement.
- Avant de modifier un fichier, l'agent vérifie avec `git status` qu'il n'a pas de modifications non commitées ; si c'est le cas, il s'arrête et le signale.
- Un commit par tâche terminée, pour que le travail d'un agent soit visible par les autres.

### Tilesets : le plan d'abord, le dessin ensuite

Une carte Tiled mémorise le **numéro** de chaque tuile, pas son dessin. Pour que le level-designer peigne les cartes pendant que le graphiste dessine :

1. Le graphiste livre d'abord le **plan** du tileset d'une zone : le `.tsx` et son PNG avec toutes les tuiles à leur place définitive (aplats de couleur lisibles), les collisions et les terrains (autotiling) déjà définis, et un fichier `art/tilesets/<nom>_plan.md` qui liste chaque tuile (numéro, rôle, collision).
2. Le level-designer peint les cartes avec ce tileset.
3. Le graphiste remplace ensuite le dessin de chaque tuile **au même emplacement**. Les cartes se mettent à jour sans être repeintes.

Il est interdit de déplacer, retirer ou réordonner une tuile d'un tileset utilisé par une carte : on ajoute seulement des lignes à la fin du PNG.

## Cartes : Tiled

Les cartes sont faites dans l'éditeur **Tiled** et importées dans Godot par un addon d'import (YATI, à installer en phase 0 avec mon accord). Le fichier Tiled est la source de vérité : on ne modifie jamais à la main la scène générée par l'import.

**Format** : orientation orthogonale, tuiles de 32×32, cartes non infinies, données de calque en **CSV**.

**Réglage d'import YATI important** : dans le panneau Import de Godot, l'option **« Add Class As Metadata »** doit être cochée (et enregistrée comme valeur par défaut pour le type « Tiled Map ») pour que la classe Tiled d'un objet (`Spawn`, `Sortie`, `Ennemi`...) soit lisible en jeu via les metadata du nœud (`node.GetMeta("class")`). Sans ça, seules les propriétés personnalisées (comme `id`) sont importées, pas la classe elle-même.

**Objets rectangle qui doivent être une zone de détection (`Sortie`, futurs interrupteurs...)** : par défaut, YATI transforme un objet rectangle sans type Godot reconnu en `StaticBody2D` (solide, bloque le joueur), pas en zone traversable. Pour obtenir une `Area2D` (qui détecte le passage sans bloquer), ajouter une propriété personnalisée **string** nommée `godot_node_type` avec la valeur `area` sur l'objet, en plus de sa `class` Tiled (`Sortie`). La `class` sert à nos metadata de gameplay, `godot_node_type` ne sert qu'à dire à YATI quel nœud Godot générer — les deux coexistent sans conflit.

**Cache d'import à surveiller** : modifier un `.tsx` externe ne déclenche pas toujours le réimport des `.tmx` qui le référencent (bug de cache observé avec YATI). Si un changement du tileset (nouvelle collision, etc.) ne se reflète pas en jeu malgré un rechargement du projet, supprimer les fichiers correspondants dans `.godot/imported/` force une réimportation complète.

**Fichiers**
- Cartes : `maps/` — une carte par salle de donjon (`maps/donjon1/salle_01.tmx`, 20×11 tuiles), une carte par zone d'overworld (`maps/overworld/foret.tmx`), une par intérieur (`maps/interieurs/forge.tmx`)
- Tilesets : `maps/tilesets/*.tsx`, qui pointent vers les PNG de `art/tilesets/`

**Calques (de bas en haut, noms exacts)**
- `Sol` : sol, herbe, eau peu profonde
- `Decor` : éléments posés au sol, sans collision
- `Murs` : tout ce qui bloque ; les collisions sont définies sur les tuiles dans le tileset
- `Objets` : calque d'objets pour tout le gameplay (voir ci-dessous)
- `Dessus` : ce qui passe devant le joueur (cimes d'arbres, haut des portes)

**Classes d'objets du calque `Objets` et leurs propriétés**

| Classe | Propriétés |
| --- | --- |
| `Spawn` | `id` (point d'arrivée, ex. `depuis_village`) |
| `Sortie` | `cible_carte` (chemin de la carte), `cible_spawn` (id du Spawn d'arrivée), `transition` facultative (`escalier` : posée sur une tuile 56/57, Spawn `depuis_escalier` sur la case voisine ; une Sortie ne se redéclenche pas tant que Brann n'en est pas sorti) |
| `Ennemi` | `type` (nom de la ressource `EnemyData`), `variante` (`normal` ou `rouge`) |
| `Coffre` | `id` (unique, ex. `donjon1_coffre_03`), `contenu` (nom d'un `.tres` de `resources/pickups/`, sans extension), `important` (bool : grand coffre, animation plus longue, future sauvegarde auto) |
| `Porte` | `id`, `type` (`cle`, `grande_cle`, `ennemis`, `interrupteur`) |
| `Interrupteur` | `id`, `cible` (id de la porte ou de l'élément déclenché), `mode` (`fleche` par défaut, ou `epee`), `ordre` (entier, 0 = pas d'ordre), `duree` (s, 0 = permanent), `symbole` (`gland`, `racine`, `feuille` ; vide + `epee` = levier). Les interrupteurs de même `cible` forment un groupe : la porte s'ouvre quand tous sont actifs ; hors ordre = tout le groupe revient à zéro |
| `PlaqueDePression` | rectangle 32×32, `godot_node_type`=`area` : `id`, `cible` (porte `interrupteur`), `declencheur` (`bloc`, `joueur`, `tous` par défaut). Toutes les plaques de même `cible` enfoncées ensemble ouvrent la porte (mémorisée) ; plaques non sauvegardées |
| `Chute` | rectangle, `godot_node_type`=`area` : `id`, `cible_carte`, `cible_spawn` (`depuis_chute_<salle>`). Trou de passage vers l'étage du dessous, 0 PV perdu ; peint avec les tuiles `trou_passage`, jamais avec les tuiles 58-66 (mortelles) |
| `Torche` | point : `id`, `etat` (`eteinte`/`allumee`), `permanente` (bool, brasero), `duree` (s, 0 = reste allumée), `cible` (porte `interrupteur`). Allumée : la flèche passe et prend feu ; éteinte : arrête la flèche (une flèche enflammée l'allume). Toutes les torches de même `cible` allumées ensemble ouvrent la porte |
| `BlocPoussable` | — |
| `MurFissure` | `id` (s'ouvre avec une bombe, état sauvegardé) |
| `StatueCorbeau` | `id` (point de sauvegarde) |
| `PNJ` | `id` (clé de ses dialogues) |
| `Ramassable` | `id`, `contenu` (quart de cœur, plume de corbeau…) |

**Éléments détruits par une bombe** (`MurFissure`…) : le nœud est dans le groupe Godot `destructible_bombe` et implémente l'interface C# `IBombDestructible` (`OnBombExplosion(Vector2 center)`). L'explosion appelle cette méthode sur chaque nœud du groupe à portée.

**Cibles touchées par une flèche** (interrupteurs à distance, Œil de Morvath…) : le nœud est dans le groupe Godot `cible_fleche`, implémente `IArrowTarget` (`OnArrowHit(Vector2 position, Vector2 direction)`) et a une `Area2D` ou un corps de collision sur la couche 1. Un simple mur (`StaticBody2D`, tuile solide) arrête la flèche sans rien de plus.

**Munitions** : les flèches sont la quantité de l'objet `arc` (pas d'objet séparé). Un ramassable de munitions utilise `GiveItemEffect` avec `OnlyIfOwned` (reste au sol tant que l'objet n'est pas possédé) et éventuellement `PickupIcon`.

**Coffres** : l'`Id` est mémorisé dans `GameState` via `MarkCollected` (un `Id` vide est une erreur). Le contenu est un `PickupEffect` ; tout `PickupEffect` doit renseigner `Icon` et `NameKey` (clé `OBJ_*` dans `textes.csv`) pour l'affichage « Vous obtenez ». Pendant l'animation d'ouverture le jeu est en pause : aucun code ne doit lancer de transition (`GoToScene`) à ce moment.

**Objets utilisables** (`use_item`) : chaque `ItemData` utilisable référence une scène dans `UseScene`, dont le script hérite de `ItemUse` (`Begin(Player, direction)`). Le joueur ne connaît aucun objet en particulier. Si un mur est entre Brann et le point de pose : avec `CancelIfBlocked` (arc) rien n'est utilisé ni consommé ; sinon (bombe) l'objet est posé contre le mur. Une `HitBox` avec `SingleHit` ne blesse qu'une seule cible (flèche).

**Chargement des objets Tiled (`Room`, phase 4)** : au `_Ready`, la `Room` lit le calque `Objets` et instancie les vraies scènes sous le nœud `Entites` (celui qui contient Brann), puis retire du jeu le marqueur importé (jamais du fichier). Lues : `Ennemi` (`type` = nom de `scenes/enemies/<type>.tscn`, `variante` = `normal` ou `rouge`), `Coffre` (`id`, `contenu` = nom de `resources/pickups/<contenu>.tres`, `important` bool), `StatueCorbeau` (`id`), `Ramassable` (`id`, `contenu` comme le coffre ; ramassable unique mémorisé par son `id`), `Porte`. `Interrupteur` (`scenes/puzzles/interrupteur.tscn`, `Switch` : mode `fleche` = groupe `cible_fleche`, mode `epee` = `IMeleeTarget` touché par une `HitBox` avec `Melee` ; ouvre la `Porte` du groupe `portes` dont l'id = `cible` ; état mémorisé par son id), `BlocPoussable` (point au centre d'une case ; poussé ~0,3 s il glisse d'une case si elle est libre ; revient à sa position Tiled à chaque chargement, rien en sauvegarde ; règle de level design : pas de bloc dans une salle à trous, ni sur la ligne de tir d'un interrupteur, ni sur un Spawn). Trous : tuiles 58 à 66 de `temple_racines` sur le calque `Sol` (reconnues par id dans `HoleRules`, sans collision) ; Brann perd 1 PV sans mourir et revient au Spawn d'entrée de la salle ; un ennemi qui tombe disparaît sans butin ; flèches et bombes passent au-dessus. Les classes pas encore gérées (`MurFissure`, `PNJ`...) et les rectangles nommés sans classe (`boss_sylve`, `pilier`) donnent un seul avertissement. Les ennemis réapparaissent à chaque retour dans la salle (la salle est rechargée depuis la carte).
- **Position** : pour `Coffre` et `StatueCorbeau`, le point Tiled est le **centre de la case** ; l'objet est posé au bas de cette case (+16 px, son origine est ses pieds). Pour `Ennemi` et `Ramassable`, le point est le centre de l'objet.
- **Variante `rouge`** : sprites `art/enemies/<type>_red_frames.tres`, vie × `Room.RedHealthFactor` (2), dégâts au contact × `Room.RedContactDamageFactor` (2). Le projectile du Lutin n'est pas modifié.
- **`Porte`** : rectangle posé sur la **même case que la `Sortie`** (exactement le même rectangle ; une `Sortie` derrière une porte fermée est ignorée), dans chacune des deux salles, avec le **même `id`** (propriété `type` : `cle`, `grande_cle`, `ennemis`, `interrupteur`). YATI en fait un `StaticBody2D` que la `Room` remplace par `scenes/puzzles/porte.tscn` (`Door`). L'état ouvert est mémorisé dans `GameState` (`MarkCollected(id)`, sauvegardé avec les `CollectedIds`). `cle` : Brann pousse dessus, 1 petite clé consommée. `grande_cle` : grande clé du donjon (non consommée). `ennemis` : fermée tant que les ennemis de la carte vivent. `interrupteur` : `Door.Open()`, appelé par l'interrupteur (les portes sont dans le groupe `portes`). Un ennemi doit quitter la salle soit en mourant via `Health`, soit en sortant de l'arbre : la porte `ennemis` compte les deux.
- **Objets de donjon** (carte, boussole, grande clé) : `DungeonItemEffect` ; mémorisés par `GameState` sous la forme `<zone>/<type>` (ex. `donjon1/grande_cle`), la zone étant la `Zone` de la `Room`. Plume de corbeau : compteur `GameState.RavenFeathers`.
- **Rectangle d'indice** (`indice_*`) : doit porter `godot_node_type=area` (sinon il bloque le passage) ; en attendant la `Room` retire le corps solide d'un rectangle nommé `indice...`.
- **Image d'une porte** : `art/puzzles/porte_<cle|grande_cle|ennemis|interrupteur>.png`, 32 px par image (fermée, puis ouverte en option) ; sans fichier, un placeholder est dessiné par le code.
- **Calque `Dessus`** : la `Room` lui donne `z_index = 2` pour qu'il passe devant Brann.
- **Sortie vers une scène pas encore créée** : `Room.MissingExitFallbackScene` (provisoire) ; sinon avertissement et rien ne se passe.
- **Butin de flèches garanti** : le coffre de l'arc donne 20 flèches ; `LootDropper.ArrowsBelow` vaut 10 : sous ce seuil, chaque ennemi vaincu lâche EN PLUS du tirage normal un paquet de 5 flèches (20 s au sol).
- **Corps des interrupteurs** : le `Switch` (levier et cibles) a un corps solide `Corps` (`SwitchBody`, 20×16 à la base de la case) qui bloque Brann et les blocs et arrête la flèche en activant l'interrupteur ; une cible ou un levier ne doit pas barrer un couloir d'une case, ni être posé sur ou à côté d'une case de `Sortie` ou de `Porte`. Une flèche s'arrête sur un interrupteur en mode `epee` (comme sur un mur) et traverse un interrupteur déjà résolu.
- **Nom des objets ramassés** : `PickupEffect.ShowNameOnPickup` affiche « Vous obtenez : … » (+ `DescriptionKey` facultative) au ramassage d'un objet au sol, sans pause ; à activer pour tout objet non courant (pas les rubis, petits cœurs, flèches).

**Carte du donjon (menu pause)** : l'action `map_page` (Tab / Select) bascule entre l'inventaire et la carte ; haut/bas changent d'étage. Le plan d'un donjon (salles, positions, liens, escaliers, chutes) est codé dans `DungeonMap.cs` (C# pur, `GetLayout`) : à mettre à jour si une salle est ajoutée ou déplacée, en plus des propriétés `etage`/`carte_x`/`carte_y` des `.tmx`. Salles visitées : `GameState` sous `<zone>/<nom de la scène>`, sauvegardées dans `SaveData.VisitedRooms` (version 4). Images dans `art/ui/carte/` (`cadre`, `salle_visitee`, `salle_inconnue`, `icone_brann`, `icone_boss`, `icone_escalier`, `icone_chute`).

**Propriété de carte `camera`** : `suivre` (défaut : la caméra suit Brann, limitée à la carte — overworld et grandes cartes) ou `ecran` (défilement par écran de 20×11 avec glissement, pour les salles de donjon de plusieurs écrans) ; exposée par `Room.CameraMode`. En `ecran`, une carte qui n'est pas un multiple de 20×11 voit son dernier écran calé sur le bord. **Overworld** : une scène par zone (`scenes/rooms/foret_temple_room.tscn`, `Zone` = `foret`) qui instancie `maps/overworld/<zone>.tmx` ; mêmes calques et objets que les salles ; le `Spawn` d'arrivée n'est jamais sur une `Sortie` ou une `Porte`.

**Propriétés de carte (donjons)** : `etage` (`rdc` ou `sous_sol`), `carte_x`, `carte_y` (position dans la grille du donjon, pour la carte du menu pause). **Règles de conception** : un déclencheur (interrupteur, plaque, torche) est toujours dans la même salle qu'une face de sa porte ; un bloc ne peut pas être poussé sur ou à côté (8 voisines) d'un Spawn, d'une `Sortie` ou d'une `Porte` ; option d'aide = multiplicateur des `duree` (torches, cibles) pour le jeune joueur.

**Énigmes (code)** : l'état des plaques, des torches et des interrupteurs en groupe (ordre/durée) n'est pas sauvegardé, seule la porte l'est ; un interrupteur isolé et permanent mémorise son propre id. Scènes `scenes/puzzles/plaque_pression.tscn`, `chute.tscn`, `interrupteur.tscn`. `GameState.PuzzleTimeMultiplier` (1 par défaut, 0 = illimité, max 4) est un réglage du joueur, hors sauvegarde (futur fichier d'options). `SceneManager.GoToScene(scene, spawn, beforeChange, kind, fadeDuration)` ; signal `TransitionStarted(kind)` (`""`, `escalier`, `chute`). Aucune `Sortie` ne se déclenche tant que Brann ne l'a pas quittée après son arrivée. `HoleWatcher` reconnaît les trous 58-66 des tilesets `temple_racines` et `temple_racines_sous_sol`. Torches : `scenes/puzzles/torche.tscn` (`Torch`), un corps qui interagit avec la flèche implémente `IArrowInteractor` (il décide si elle s'arrête) ; `Arrow.IsBurning` / `Ignite()`. Une cible avec `duree` sans `symbole` utilise `cible_chrono.png`. Indices : un rectangle `indice_xxx` (area) affiche la clé `INDICE_XXX` de `textes.csv` tant que Brann est dedans. Propriétés de carte exposées par `Room.MapFloor`, `Room.MapCell`, `Room.HasMapPosition`.

**Boss** : un rectangle ou point nommé `boss_<nom>` (sans classe) fait instancier `scenes/enemies/boss/<nom>.tscn` (sous-classe de `Boss`, id `<zone>_boss_<nom>`) ; les rectangles nommés `pilier` sont transmis au boss. Victoire : `MarkCollected(id)`, signal `GameState.BossDefeated` (sauvegarde auto), porte d'arène rouverte (`Door.LockForEncounter` / `UnlockAfterEncounter`, rien de mémorisé), réplique via `DialogueBox`, réceptacle et sceau = ramassables uniques `<id>_receptacle` / `<id>_sceau`. Boss déjà vaincu : salle calme, récompenses non ramassées reposées. Sceaux : `GameState.Seals` (ids, ex. `racines`), `SaveData.Seals` (version 3), `SealEffect`. `HurtBox.Blocked` = coup sur une zone invincible ; `Hud.ShowBossBar/SetBossBar/HideBossBar`. Le corps d'un boss est en couche de collision 3 (masque 1) : il ne bloque ni Brann ni les flèches mais s'arrête sur murs et piliers ; ses HurtBox/HitBox restent en couche 1.

Ces conventions sont un point de départ, à ajuster en phase 1. Toute nouvelle convention est ajoutée ici avant d'être utilisée dans une carte ou dans le code.

## Architecture et conventions C#

```
res://
  maps/         cartes Tiled (.tmx) et tilesets (tilesets/*.tsx)
  addons/       addon d'import Tiled
  scenes/       (player/, enemies/, items/, puzzles/, rooms/, ui/)
  scripts/      (même découpage, un .cs par scène)
    core/       GameState.cs, SceneManager.cs, AudioManager.cs, SaveSystem.cs
    components/ Health.cs, HitBox.cs, HurtBox.cs, StateMachine.cs
  resources/    items/*.tres, enemies/*.tres
  art/          (characters/, enemies/, tilesets/, ui/, palette.png)
  audio/
tools/          scripts de génération (sprites…), hors du jeu
docs/           roadmap.md
```

- **Composition plutôt qu'héritage** : un ennemi = `CharacterBody2D` + nœuds enfants `Health`, `HurtBox`, `HitBox`, `StateMachine`.
- **Dégâts au contact** : la `HitBox` qui inflige des dégâts au toucher (corps à corps, pas une arme à portée) doit être **légèrement plus grande** que la forme de collision physique du personnage. Deux `CharacterBody2D` solides s'arrêtent pile au contact sans vraiment se chevaucher, donc une `Area2D` de la même taille ne détecte quasiment jamais le contact sauf quand l'un pousse activement dans l'autre (c'est pour ça qu'un ennemi semblait ne faire mal "que quand il fonce sur le joueur").
- **Données dans des `Resource`** (`ItemData`, `EnemyData`) ; le comportement dans les scripts. On équilibre sans toucher au code.
- **Communication par signaux** (`[Signal]` + `EmitSignal`) ou events C#. Éviter les `GetNode("../../..")` fragiles.
- **Autoloads limités à 4** : `GameState`, `SceneManager`, `AudioManager`, `SaveSystem`.
- Les classes de script sont `partial` et le nom du fichier correspond au nom de la classe.
- Penser à recompiler (Build) après l'ajout d'un `[Export]` ou d'un `[Signal]`.
- Pas d'allocations dans les boucles chaudes (`_Process`, `_PhysicsProcess`) : pas de LINQ ni de `new` à chaque frame.
- Sauvegarde : JSON via `System.Text.Json` dans `user://saveN.json`, avec un numéro de version. Chaque coffre, porte ou objet unique a un identifiant unique en français (ex. `donjon1_coffre_03`), mémorisé dans `GameState` une fois utilisé.
- Format de sauvegarde : classe `SaveData` (C# pur), écriture atomique via `System.IO` (fichier `.tmp` puis renommage). Tout nouvel état à persister passe par `GameState.CreateSaveData` / `ApplySaveData` avec un champ dans `SaveData`. **Toute modification du format incrémente `SaveData.CurrentVersion` et ajoute un `case` dans `SaveSerializer.Migrate`.** La position de reprise est une scène + un id de `Spawn`, jamais des coordonnées. Chaque salle (`Room`) a une `Zone` (ex. `donjon1`, `foret`, `village`) : la sauvegarde automatique se fait au changement de zone (pas de salle), à l'ouverture d'un coffre important et après un boss. La scène principale est l'écran titre (`scenes/ui/ecran_titre.tscn`) ; une salle lancée seule avec F6 n'a pas d'emplacement choisi (`CurrentSlot == 0`) et la statue sauvegarde alors dans l'emplacement 1 seulement s'il est vide (sinon elle refuse). « Nouvelle partie » écrit l'emplacement dès l'arrivée dans la première salle. Statues du corbeau : `scenes/puzzles/statue_corbeau.tscn`, id `<zone>_statue_<lieu>` (ex. `donjon1_statue_entree`). Le signal `AutoSaved` (icône du HUD) ne concerne que la sauvegarde auto ; `GameSaved` couvre toutes les sauvegardes. Raccourcis de debug (build debug seulement) : F10 sauvegarde le slot 1, F11 le charge.
- **Ressources C# en référence forte** : toute `Resource` dont la classe est écrite en C# (`PickupEffect`, `LootTable`, `LootEntry`, futures données d'ennemis ou de dialogues…) et chargée par code passe par `ResourceKeeper.Load<T>(path)`, ou `ResourceKeeper.Pin(res)` dans le `_Ready` si elle vient d'une scène (fait pour `Pickup`, `Chest`, `LootDropper` ; les `ItemData` sont tenues par le registre de `GameState`). `ResourceKeeper` : thread principal uniquement. Sinon le ramasse-miettes .NET peut l'invalider (plantage « gchandle.is_released() » ou `[Export]` vide). Inutile pour les types natifs (`PackedScene`, `Texture2D`, `Theme`…).
- **Tir et obstacles traversables** : le test de mur de `TryUseItem` (objet `CancelIfBlocked`) ignore les `CharacterBody2D` et les corps `IArrowInteractor` ; c'est l'interaction de la flèche qui décide. Un nouvel obstacle qu'une flèche peut traverser implémente `IArrowInteractor`. La torche a en plus une zone `ZoneFleche` (32×32, décalée de 4 px vers le bas) pour qu'un tir depuis n'importe quelle hauteur de la case alignée la touche ; un `IArrowInteractor` doit traiter une même flèche une seule fois (voir `Torch`).
- **Piège Godot C#** : `PhysicsRayQueryParameters2D.Exclude` renvoie une **copie** ; `query.Exclude.Add(x)` n'a aucun effet. Garder une liste locale et réassigner `query.Exclude = liste` après chaque ajout.
- Textes du jeu : jamais en dur, toujours via `Tr()` et le fichier CSV de traduction (français et anglais).
- Nommage : PascalCase pour les classes, méthodes et propriétés ; `_camelCase` pour les champs privés ; scènes et dossiers en `snake_case`.

## Git

- Le dossier `.godot/` est ignoré.
- Messages de commit courts, en français, qui disent ce qui change (ex. « Ajoute le déplacement 8 directions de Brann »).
