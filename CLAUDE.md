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

**Phase 3 — Vie, inventaire, objets, sauvegarde.** (Mettre à jour cette ligne à chaque changement de phase.)

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
| `Sortie` | `cible_carte` (chemin de la carte), `cible_spawn` (id du Spawn d'arrivée) |
| `Ennemi` | `type` (nom de la ressource `EnemyData`), `variante` (`normal` ou `rouge`) |
| `Coffre` | `id` (unique, ex. `donjon1_coffre_03`), `contenu` (nom d'un `.tres` de `resources/pickups/`, sans extension), `important` (bool : grand coffre, animation plus longue, future sauvegarde auto) |
| `Porte` | `id`, `type` (`cle`, `grande_cle`, `ennemis`, `interrupteur`) |
| `Interrupteur` | `id`, `cible` (id de la porte ou de l'élément déclenché) |
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
- Format de sauvegarde : classe `SaveData` (C# pur), écriture atomique via `System.IO` (fichier `.tmp` puis renommage). Tout nouvel état à persister passe par `GameState.CreateSaveData` / `ApplySaveData` avec un champ dans `SaveData`. **Toute modification du format incrémente `SaveData.CurrentVersion` et ajoute un `case` dans `SaveSerializer.Migrate`.** La position de reprise est une scène + un id de `Spawn`, jamais des coordonnées. Chaque salle (`Room`) a une `Zone` (ex. `donjon1`, `foret`, `village`) : la sauvegarde automatique se fait au changement de zone (pas de salle), à l'ouverture d'un coffre important et après un boss. Raccourcis de debug (build debug seulement) : F10 sauvegarde le slot 1, F11 le charge.
- Textes du jeu : jamais en dur, toujours via `Tr()` et le fichier CSV de traduction (français et anglais).
- Nommage : PascalCase pour les classes, méthodes et propriétés ; `_camelCase` pour les champs privés ; scènes et dossiers en `snake_case`.

## Git

- Le dossier `.godot/` est ignoré.
- Messages de commit courts, en français, qui disent ce qui change (ex. « Ajoute le déplacement 8 directions de Brann »).
