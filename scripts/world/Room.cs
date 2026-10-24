using Godot;
using System.Collections.Generic;

/// <summary>
/// Une salle de jeu : une carte Tiled importée + un conteneur « Entites » (tri en profondeur) où vit Brann.
/// Au chargement, la salle lit le calque d'objets « Objets » de la carte (Spawn, Sortie, Ennemi, Coffre,
/// StatueCorbeau, Ramassable, Porte) et instancie les vraies scènes aux positions des marqueurs.
/// La scène importée n'est jamais modifiée sur le disque : seuls les nœuds de l'arbre en cours sont retirés.
/// </summary>
public partial class Room : Node2D
{
    /// <summary>
    /// Zone de jeu (ex. « donjon1 », « foret », « village »). La sauvegarde automatique se déclenche
    /// quand on passe d'une zone à une autre, pas à chaque changement de salle.
    /// </summary>
    [Export]
    public string Zone { get; set; } = "";

    /// <summary>
    /// Provisoire : si la carte d'une Sortie pointe vers une scène qui n'existe pas encore, on va ici à la place
    /// (vide : on reste dans la salle et un avertissement est écrit). À vider quand la scène cible existera.
    /// </summary>
    [Export(PropertyHint.File, "*.tscn")]
    public string MissingExitFallbackScene { get; set; } = "";

    [ExportGroup("Variante rouge")]
    /// <summary>Multiplicateur de points de vie d'un ennemi de variante « rouge ».</summary>
    [Export(PropertyHint.Range, "1,5,0.5")]
    public float RedHealthFactor { get; set; } = 2f;

    /// <summary>Multiplicateur de dégâts au contact d'un ennemi de variante « rouge » (le projectile du Lutin n'est pas touché).</summary>
    [Export(PropertyHint.Range, "1,5,1")]
    public int RedContactDamageFactor { get; set; } = 2;

    /// <summary>Le dernier ennemi de la salle vient de mourir (seulement ceux créés depuis la carte).</summary>
    [Signal]
    public delegate void EnemiesClearedEventHandler();

    /// <summary>Nombre d'ennemis de la carte encore vivants.</summary>
    public int AliveEnemies => _aliveEnemies;

    private const string ChestScenePath = "res://scenes/puzzles/coffre.tscn";
    private const string StatueScenePath = "res://scenes/puzzles/statue_corbeau.tscn";
    private const string DoorScenePath = "res://scenes/puzzles/porte.tscn";
    private const string PickupScenePath = "res://scenes/items/objet_inventaire.tscn";
    private const int DessusZIndex = 2; // au-dessus des entités (0) et de l'icône d'un coffre (1)
    private static readonly Vector2 FootOffset = new(0f, 16f); // coffres et statues : posés au bas de leur case

    // Avertissements « type inconnu » : une seule fois par session, pas à chaque chargement de salle.
    private static readonly HashSet<string> WarnedKeys = new();

    private Node2D _entities;
    private int _aliveEnemies;
    private readonly Dictionary<Health, EnemyTrack> _trackedEnemies = new();
    private bool _leaving;
    private readonly List<Door> _doors = new();

    /// <summary>Zone de la salle courante (chaîne vide hors d'une salle).</summary>
    public static string ZoneOf(Node node)
    {
        return node?.GetTree()?.CurrentScene is Room room ? room.Zone ?? "" : "";
    }

    public override void _Ready()
    {
        // Le HUD vit avec la salle (pas d'autoload supplémentaire) ; il ne dépend que de GameState.
        var hudScene = GD.Load<PackedScene>("res://scenes/ui/hud.tscn"); // mis en cache par Godot
        if (hudScene != null)
            AddChild(hudScene.Instantiate());
        else
            GD.PushError("HUD introuvable : res://scenes/ui/hud.tscn");

        var player = FindPlayer(this);
        _entities = player?.GetParent() as Node2D ?? GetNodeOrNull<Node2D>("Entites");
        if (_entities == null)
        {
            _entities = new Node2D { Name = "Entites", YSortEnabled = true };
            AddChild(_entities);
        }

        TreeExiting += OnRoomExiting;
        ConfigureLayers();

        // Brann d'abord sur son Spawn, puis les objets : rien n'apparaît sous ses pieds avant qu'il soit placé.
        var sceneManager = GetNode<SceneManager>("/root/SceneManager");
        var spawn = FindSpawnById(this, sceneManager.ConsumeSpawnId());
        if (player != null && spawn != null)
            player.GlobalPosition = spawn.GlobalPosition;

        SpawnObjects();

        foreach (var sortie in FindAllByClass(this, "Sortie"))
        {
            if (sortie is Area2D area)
                area.BodyEntered += body => OnSortieEntered(area, body);
        }

        if (player != null)
            ConfigureCamera(player);
    }

    // Rôle : cesser de suivre les ennemis quand la salle quitte l'arbre. Attention : Godot émet tree_exiting des enfants
    // AVANT celui de la salle ; _leaving ne suffit donc pas, d'où le traitement différé des départs sans Died.
    private void OnRoomExiting()
    {
        _leaving = true;
        TreeExiting -= OnRoomExiting;
        foreach (var track in _trackedEnemies.Values)
            track.Disconnect();
        _trackedEnemies.Clear();
    }

    // Suivi d'un ennemi : décompté une seule fois, qu'il meure (Died) ou quitte l'arbre (TreeExiting).
    private sealed class EnemyTrack
    {
        private readonly Health _health;
        private readonly Health.DiedEventHandler _onDied;
        private readonly System.Action _onExit;

        public EnemyTrack(Health health, System.Action died, System.Action exited)
        {
            _health = health;
            _onDied = () => died();
            _onExit = exited;
            health.Died += _onDied;
            health.TreeExiting += _onExit;
        }

        public void Disconnect()
        {
            if (!IsInstanceValid(_health)) return;
            _health.Died -= _onDied;
            _health.TreeExiting -= _onExit;
        }
    }

    // Le calque « Dessus » (haut des portes, cimes) doit passer devant Brann : il est dans la carte,
    // donc dessiné avant le conteneur d'entités, sauf si on le remonte avec un z_index.
    private void ConfigureLayers()
    {
        if (FindNodeByName(this, "Dessus") is TileMapLayer dessus)
            dessus.ZIndex = DessusZIndex;
    }

    private void ConfigureCamera(Player player)
    {
        var camera = player.GetNodeOrNull<Camera2D>("Camera2D");
        var tileMapLayer = FindNodeByName(this, "Sol") as TileMapLayer;
        if (camera == null || tileMapLayer?.TileSet == null)
            return;

        // Limites = la carte entière (20x11 cases pour une salle ordinaire, 20x22 pour la salle du boss).
        var usedRect = tileMapLayer.GetUsedRect();
        var tileSize = tileMapLayer.TileSet.TileSize;

        camera.LimitLeft = usedRect.Position.X * tileSize.X;
        camera.LimitTop = usedRect.Position.Y * tileSize.Y;
        camera.LimitRight = (usedRect.Position.X + usedRect.Size.X) * tileSize.X;
        camera.LimitBottom = (usedRect.Position.Y + usedRect.Size.Y) * tileSize.Y;
        camera.PositionSmoothingEnabled = true;
        camera.ResetSmoothing(); // Brann vient d'être placé au Spawn : pas de glissement depuis l'ancienne position
    }

    // --- Objets du calque « Objets » ------------------------------------------------------------

    private void SpawnObjects()
    {
        var objets = FindNodeByName(this, "Objets");
        if (objets == null) return;

        // On collecte d'abord : on retire des nœuds pendant le traitement.
        var markers = new List<Node>();
        foreach (var child in objets.GetChildren())
            markers.Add(child);

        var portes = new List<Node>();
        foreach (var node in markers)
        {
            if (!node.HasMeta("class"))
            {
                HandleUnclassed(node);
                continue;
            }

            switch (node.GetMeta("class").AsString())
            {
                case "Spawn":
                case "Sortie":
                    break; // gérés plus bas, directement sur les nœuds importés
                case "Ennemi": SpawnEnemy(node); break;
                case "Coffre": SpawnChest(node); break;
                case "StatueCorbeau": SpawnStatue(node); break;
                case "Ramassable": SpawnPickup(node); break;
                case "Porte": portes.Add(node); break; // après les ennemis : elles ont besoin de leur nombre
                default:
                    WarnOnce("class:" + node.GetMeta("class").AsString(),
                        $"Objet Tiled de classe « {node.GetMeta("class").AsString()} » pas encore géré ({Name}) : ignoré.");
                    break;
            }
        }

        foreach (var node in portes)
            SpawnDoor(node);
    }

    // Rectangles ou points nommés sans classe (indice_ronces_coupees, boss_sylve, pilier...).
    private void HandleUnclassed(Node node)
    {
        string name = node.Name;
        if (name.StartsWith("indice", System.StringComparison.Ordinal) && node is StaticBody2D)
        {
            // Zone d'indice : YATI en fait un corps solide qui boucherait le passage. On le retire (la carte reste intacte).
            WarnOnce("indice-solide", "Le rectangle « indice... » est importé comme un corps solide (il manque godot_node_type=area dans Tiled) : retiré à l'exécution.");
            RemoveMarker(node);
            return;
        }
        if (node is Marker2D || node is not StaticBody2D)
            WarnOnce("nom:" + BaseName(name), $"Objet Tiled « {BaseName(name)} » sans classe pas encore géré : ignoré.");
    }

    private void SpawnEnemy(Node marker)
    {
        string type = GetString(marker, "type");
        string variant = GetString(marker, "variante", "normal");
        if (!RoomObjectCatalog.IsSafeName(type))
        {
            WarnOnce("ennemi-type:" + type, $"Ennemi Tiled avec un type invalide « {type} » ({Name}).");
            return;
        }
        string path = RoomObjectCatalog.EnemyScenePath(type);
        if (!ResourceLoader.Exists(path))
        {
            WarnOnce("ennemi-scene:" + type, $"Ennemi « {type} » : scène introuvable ({path}).");
            return;
        }

        var enemy = GD.Load<PackedScene>(path).Instantiate<Node2D>();
        enemy.Position = _entities.ToLocal(MarkerPosition(marker));
        if (RoomObjectCatalog.IsRedVariant(variant))
            ApplyRedVariant(enemy, type);
        else if (variant != "normal")
            WarnOnce("ennemi-variante:" + variant, $"Variante d'ennemi inconnue « {variant} » : traité comme « normal ».");
        _entities.AddChild(enemy);

        var health = enemy.GetNodeOrNull<Health>("Health");
        if (health != null)
        {
            _trackedEnemies[health] = new EnemyTrack(health, () => OnEnemyGone(health), () => OnEnemyLeftTree(health));
            _aliveEnemies++;
        }
        RemoveMarker(marker);
    }

    // Variante rouge : palette rouge (art/enemies/<type>_red_frames.tres), plus de vie, plus de dégâts au contact.
    // Appelé avant AddChild : Health.MaxHealth est lu au _Ready.
    private void ApplyRedVariant(Node2D enemy, string type)
    {
        string framesPath = RoomObjectCatalog.EnemyRedFramesPath(type);
        var sprite = enemy.GetNodeOrNull<AnimatedSprite2D>("AnimatedSprite2D");
        if (sprite != null && ResourceLoader.Exists(framesPath))
            sprite.SpriteFrames = GD.Load<SpriteFrames>(framesPath);
        else
            WarnOnce("rouge-frames:" + type, $"Pas de sprites rouges pour « {type} » ({framesPath}) : apparence normale.");

        var health = enemy.GetNodeOrNull<Health>("Health");
        if (health != null)
            health.MaxHealth = Mathf.Max(1, Mathf.RoundToInt(health.MaxHealth * RedHealthFactor));
        var hitBox = enemy.GetNodeOrNull<HitBox>("HitBox");
        if (hitBox != null)
            hitBox.Damage *= RedContactDamageFactor;
    }

    // Un ennemi quitte l'arbre sans Died (trou, QueueFree). Si c'est la salle entière qui part, ses enfants sortent
    // avant elle : on diffère d'une image et on ignore si la salle n'est plus valide, plus dans l'arbre ou en cours de suppression.
    private void OnEnemyLeftTree(Health health)
    {
        if (_leaving) return;
        Callable.From(() =>
        {
            if (!IsInstanceValid(this) || _leaving || !IsInsideTree() || IsQueuedForDeletion()) return;
            OnEnemyGone(health);
        }).CallDeferred();
    }

    private void OnEnemyGone(Health health)
    {
        if (_leaving) return; // salle entière libérée : rien à ouvrir
        if (!_trackedEnemies.Remove(health, out var track)) return; // déjà décompté (Died puis TreeExiting)
        track.Disconnect();
        if (_aliveEnemies > 0) _aliveEnemies--;
        if (_aliveEnemies != 0) return;

        for (int i = 0; i < _doors.Count; i++)
        {
            if (IsInstanceValid(_doors[i]))
                _doors[i].NotifyRoomCleared();
        }
        EmitSignal(SignalName.EnemiesCleared);
    }

    private void SpawnChest(Node marker)
    {
        string id = GetString(marker, "id");
        string content = GetString(marker, "contenu");
        var effect = LoadPickupEffect(content, "Coffre " + id);

        var chest = GD.Load<PackedScene>(ChestScenePath).Instantiate<Chest>();
        chest.Id = id;
        chest.Effect = effect;
        chest.Important = GetBool(marker, "important");
        chest.Position = _entities.ToLocal(MarkerPosition(marker)) + FootOffset;
        _entities.AddChild(chest);
        RemoveMarker(marker);
    }

    private void SpawnStatue(Node marker)
    {
        var statue = GD.Load<PackedScene>(StatueScenePath).Instantiate<RavenStatue>();
        statue.Id = GetString(marker, "id");
        statue.Position = _entities.ToLocal(MarkerPosition(marker)) + FootOffset;
        _entities.AddChild(statue);
        RemoveMarker(marker);
    }

    private void SpawnPickup(Node marker)
    {
        string id = GetString(marker, "id");
        var effect = LoadPickupEffect(GetString(marker, "contenu"), "Ramassable " + id);
        if (effect == null)
        {
            RemoveMarker(marker);
            return;
        }

        var pickup = GD.Load<PackedScene>(PickupScenePath).Instantiate<ItemPickup>();
        pickup.UniqueId = id; // non vide : objet permanent, absent s'il a déjà été ramassé
        pickup.Effect = effect;
        pickup.Position = _entities.ToLocal(MarkerPosition(marker));
        _entities.AddChild(pickup);
        RemoveMarker(marker);
    }

    private void SpawnDoor(Node marker)
    {
        string id = GetString(marker, "id");
        string typeValue = GetString(marker, "type");
        if (!DoorRules.TryParseKind(typeValue, out var kind))
        {
            GD.PushError($"Porte « {id} » : type inconnu « {typeValue} » (cle, grande_cle, ennemis ou interrupteur) dans {Name}.");
            RemoveMarker(marker);
            return;
        }

        // YATI a fait un StaticBody2D (solide) de ce rectangle : on lit sa forme pour la case, puis on le retire.
        var center = MarkerPosition(marker) + new Vector2(16f, 16f);
        var size = new Vector2(32f, 32f);
        var shapeNode = marker.GetNodeOrNull<CollisionShape2D>("Rectangle Shape");
        if (shapeNode == null)
            foreach (var child in marker.GetChildren())
                if (child is CollisionShape2D found) { shapeNode = found; break; }
        if (shapeNode != null)
        {
            center = shapeNode.GlobalPosition;
            if (shapeNode.Shape is RectangleShape2D rect) size = rect.Size;
        }

        var door = GD.Load<PackedScene>(DoorScenePath).Instantiate<Door>();
        door.Id = id;
        door.Kind = kind;
        door.Zone = Zone ?? "";
        door.CellSize = size;
        door.RoomHasEnemies = _aliveEnemies > 0;
        door.Position = _entities.ToLocal(center);
        _entities.AddChild(door);
        _doors.Add(door);
        RemoveMarker(marker);
    }

    private PickupEffect LoadPickupEffect(string content, string owner)
    {
        if (!RoomObjectCatalog.IsSafeName(content))
        {
            GD.PushError($"{owner} : contenu invalide « {content} » ({Name}).");
            return null;
        }
        string path = RoomObjectCatalog.PickupEffectPath(content);
        if (!ResourceLoader.Exists(path))
        {
            GD.PushError($"{owner} : contenu « {content} » introuvable ({path}).");
            return null;
        }
        return GD.Load<PickupEffect>(path);
    }

    // Retire le marqueur importé de l'arbre (pas du fichier) : il est remplacé par la vraie scène.
    private static void RemoveMarker(Node marker)
    {
        marker.GetParent()?.RemoveChild(marker);
        marker.QueueFree();
    }

    private static Vector2 MarkerPosition(Node marker) => marker is Node2D n ? n.GlobalPosition : Vector2.Zero;

    private static string GetString(Node node, string key, string fallback = "")
    {
        if (!node.HasMeta(key)) return fallback;
        return node.GetMeta(key).AsString();
    }

    private static bool GetBool(Node node, string key)
    {
        if (!node.HasMeta(key)) return false;
        var value = node.GetMeta(key);
        return value.VariantType == Variant.Type.Bool ? value.AsBool() : value.AsString() == "true";
    }

    private static string BaseName(string name)
    {
        int space = name.IndexOf(' ');
        return space > 0 ? name[..space] : name;
    }

    private static void WarnOnce(string key, string message)
    {
        if (WarnedKeys.Add(key))
            GD.PushWarning(message);
    }

    // --- Recherches dans l'arbre -----------------------------------------------------------------

    private static Player FindPlayer(Node root)
    {
        foreach (var child in root.GetChildren())
        {
            if (child is Player player)
                return player;
            var found = FindPlayer(child);
            if (found != null)
                return found;
        }
        return null;
    }

    private static Node FindNodeByName(Node root, string name)
    {
        foreach (var child in root.GetChildren())
        {
            if (child.Name == name)
                return child;
            var found = FindNodeByName(child, name);
            if (found != null)
                return found;
        }
        return null;
    }

    private void OnSortieEntered(Node sortie, Node body)
    {
        if (body is not Player { IsDead: false }) return;
        if (!sortie.HasMeta("cible_carte")) return;
        if (IsBlockedByClosedDoor(sortie)) return; // recul ou poussée qui amènerait Brann sur la Sortie d'une porte fermée

        var cibleCarte = (string)sortie.GetMeta("cible_carte");
        var cibleSpawn = sortie.HasMeta("cible_spawn") ? (string)sortie.GetMeta("cible_spawn") : "";
        if (!ResourceLoader.Exists(cibleCarte))
        {
            // Scène pas encore créée (ex. la forêt devant le temple) : repli provisoire ou rien.
            if (string.IsNullOrEmpty(MissingExitFallbackScene))
            {
                WarnOnce("sortie:" + cibleCarte, $"Sortie vers « {cibleCarte} » : la scène n'existe pas encore.");
                return;
            }
            WarnOnce("sortie:" + cibleCarte, $"Sortie vers « {cibleCarte} » : la scène n'existe pas encore, repli provisoire sur {MissingExitFallbackScene}.");
            cibleCarte = MissingExitFallbackScene;
            cibleSpawn = "";
        }
        GetNode<SceneManager>("/root/SceneManager").GoToScene(cibleCarte, cibleSpawn);
    }

    // Une Sortie est ignorée tant qu'une porte fermée occupe la même case (centres à 1 px près).
    private bool IsBlockedByClosedDoor(Node sortie)
    {
        if (sortie is not Node2D area) return false;
        var center = area.GlobalPosition + new Vector2(16f, 16f);
        foreach (var child in sortie.GetChildren())
        {
            if (child is CollisionShape2D shape) { center = shape.GlobalPosition; break; }
        }
        for (int i = 0; i < _doors.Count; i++)
        {
            var door = _doors[i];
            if (!IsInstanceValid(door) || door.IsOpen) continue;
            if (door.GlobalPosition.DistanceSquaredTo(center) <= 1f) return true;
        }
        return false;
    }

    private static Node2D FindSpawnById(Node root, string spawnId)
    {
        Node2D firstSpawn = null;
        foreach (var node in FindAllByClass(root, "Spawn"))
        {
            if (node is not Node2D node2D) continue;
            firstSpawn ??= node2D;
            if (!string.IsNullOrEmpty(spawnId) && node.HasMeta("id") && (string)node.GetMeta("id") == spawnId)
                return node2D;
        }
        return firstSpawn;
    }

    private static List<Node> FindAllByClass(Node root, string className)
    {
        var results = new List<Node>();
        CollectByClass(root, className, results);
        return results;
    }

    private static void CollectByClass(Node root, string className, List<Node> results)
    {
        foreach (var child in root.GetChildren())
        {
            if (HasClass(child, className))
                results.Add(child);
            CollectByClass(child, className, results);
        }
    }

    private static bool HasClass(Node node, string className)
    {
        return node.HasMeta("class") && node.GetMeta("class").AsString() == className;
    }
}
