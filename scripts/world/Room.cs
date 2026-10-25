using Godot;
using System.Collections.Generic;
using System.Globalization;
using System.Threading.Tasks;

/// <summary>
/// Une salle de jeu : une carte Tiled importée + un conteneur « Entites » (tri en profondeur) où vit Brann.
/// Au chargement, la salle lit le calque d'objets « Objets » de la carte (Spawn, Sortie, Ennemi, Coffre,
/// StatueCorbeau, Ramassable, Porte, Interrupteur, PlaqueDePression, Chute, Torche, BlocPoussable, plus les rectangles nommés « boss_<nom> » et « pilier ») et instancie les vraies scènes aux positions des marqueurs.
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

    /// <summary>Durée (s) du fondu quand une Sortie a la propriété « transition » = « escalier » (plus lent qu'une porte).</summary>
    [Export(PropertyHint.Range, "0.1,2,0.05")]
    public float StairsFadeDuration { get; set; } = 0.6f;

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

    /// <summary>Étage du donjon (propriété de carte « etage » : « rdc » ou « sous_sol »). Vide si la carte n'en a pas.</summary>
    public string MapFloor { get; private set; } = "";

    /// <summary>Position de la salle dans la grille du donjon (propriétés de carte « carte_x » et « carte_y »), pour la carte du menu pause.</summary>
    public Vector2I MapCell { get; private set; } = Vector2I.Zero;

    /// <summary>Vrai si la carte porte les trois propriétés etage, carte_x et carte_y.</summary>
    public bool HasMapPosition { get; private set; }

    /// <summary>
    /// Mode de caméra (propriété de carte Tiled « camera »). « suivre » (défaut) : la caméra suit Brann, limitée à la carte
    /// (une salle d'un écran ne bouge donc jamais). « ecran » : défilement par écran façon ALttP, la caméra se cale sur
    /// l'écran de 20x11 cases où se trouve Brann et glisse d'un écran à l'autre.
    /// </summary>
    public string CameraMode { get; private set; } = "suivre";

    /// <summary>Nombre d'ennemis de la carte encore vivants.</summary>
    public int AliveEnemies => _aliveEnemies;

    private const string ChestScenePath = "res://scenes/puzzles/coffre.tscn";
    private const string StatueScenePath = "res://scenes/puzzles/statue_corbeau.tscn";
    private const string DoorScenePath = "res://scenes/puzzles/porte.tscn";
    private const string PickupScenePath = "res://scenes/items/objet_inventaire.tscn";
    private const string SwitchScenePath = "res://scenes/puzzles/interrupteur.tscn";
    private const string BlockScenePath = "res://scenes/puzzles/bloc_poussable.tscn";
    private const string PlateScenePath = "res://scenes/puzzles/plaque_pression.tscn";
    private const string TorchScenePath = "res://scenes/puzzles/torche.tscn";
    private const string FallScenePath = "res://scenes/puzzles/chute.tscn";
    private const float GridCell = 32f;
    private const int DessusZIndex = 2; // au-dessus des entités (0) et de l'icône d'un coffre (1)
    private static readonly Vector2 FootOffset = new(0f, 16f); // coffres et statues : posés au bas de leur case

    // Avertissements « type inconnu » : une seule fois par session, pas à chaque chargement de salle.
    private static readonly HashSet<string> WarnedKeys = new();

    private const int ScreenTilesX = 20;
    private const int ScreenTilesY = 11;

    private Node2D _entities;
    private Camera2D _screenCamera;
    private Player _screenPlayer;
    private Vector2I _screenSize;
    private Rect2I _screenArea; // zone de la carte en pixels (mode « ecran »)
    private Vector2I _screenCell = new(int.MinValue, int.MinValue);
    private int _aliveEnemies;
    private readonly Dictionary<Health, EnemyTrack> _trackedEnemies = new();
    private bool _leaving;
    private readonly List<Door> _doors = new();
    private HoleWatcher _holes;
    private PackedScene _switchScene;
    private PackedScene _blockScene;
    private PackedScene _torchScene;
    private PackedScene _plateScene;
    private PackedScene _fallScene;
    private HintBox _hintBox;
    private Hud _hud;
    private readonly List<Node> _bossMarkers = new();
    private readonly List<Rect2> _pillars = new();
    private readonly List<PushBlock> _blocks = new();

    // Une Sortie « armée » se déclenche quand Brann y entre. Elle ne l'est pas tant que Brann, arrivé dessus, ne l'a pas quittée.
    private sealed class SortieState
    {
        public Area2D Area;
        public bool Armed;
    }

    /// <summary>Position de Brann à l'arrivée dans la salle (son Spawn) : il y revient après une chute dans un trou.</summary>
    public Vector2 EntryPosition { get; private set; }

    /// <summary>Zone de la salle courante (chaîne vide hors d'une salle).</summary>
    public static string ZoneOf(Node node)
    {
        return node?.GetTree()?.CurrentScene is Room room ? room.Zone ?? "" : "";
    }

    public override void _Ready()
    {
        SetPhysicsProcess(false); // activé seulement par le mode caméra « ecran »
        // Le HUD vit avec la salle (pas d'autoload supplémentaire) ; il ne dépend que de GameState.
        var hudScene = GD.Load<PackedScene>("res://scenes/ui/hud.tscn"); // mis en cache par Godot
        if (hudScene != null)
        {
            _hud = hudScene.Instantiate<Hud>();
            AddChild(_hud);
        }
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
        ReadMapProperties();
        if (HasMapPosition && !string.IsNullOrEmpty(SceneFilePath))
            GetNode<GameState>("/root/GameState").MarkRoomVisited(Zone, System.IO.Path.GetFileNameWithoutExtension(SceneFilePath));
        ConfigureLayers();

        // Brann d'abord sur son Spawn, puis les objets : rien n'apparaît sous ses pieds avant qu'il soit placé.
        var sceneManager = GetNode<SceneManager>("/root/SceneManager");
        var spawn = FindSpawnById(this, sceneManager.ConsumeSpawnId());
        if (player != null && spawn != null)
            player.GlobalPosition = spawn.GlobalPosition;

        EntryPosition = player?.GlobalPosition ?? Vector2.Zero;
        SetupHoles(player);

        SpawnObjects();

        ShareForbiddenCells();

        var sorties = new List<SortieState>();
        foreach (var sortie in FindAllByClass(this, "Sortie"))
        {
            if (sortie is not Area2D area) continue;
            var state = new SortieState { Area = area };
            sorties.Add(state);
            area.BodyEntered += body => OnSortieEntered(state, body);
            area.BodyExited += body =>
            {
                if (body is Player) state.Armed = true;
            };
        }
        if (sorties.Count > 0)
            _ = ArmSortiesAfterArrival(sorties, player);

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

        if (CameraMode == "ecran")
        {
            // Défilement par écran : _PhysicsProcess recale les limites sur l'écran de Brann ; LimitSmoothed fait glisser la caméra.
            _screenCamera = camera;
            _screenPlayer = player;
            _screenArea = new Rect2I(
                usedRect.Position.X * tileSize.X, usedRect.Position.Y * tileSize.Y,
                usedRect.Size.X * tileSize.X, usedRect.Size.Y * tileSize.Y);
            _screenSize = new Vector2I(ScreenTilesX * tileSize.X, ScreenTilesY * tileSize.Y);
            camera.LimitSmoothed = true;
            SetPhysicsProcess(true);
            UpdateScreenLimits();
        }
        camera.ResetSmoothing(); // Brann vient d'être placé au Spawn : pas de glissement depuis l'ancienne position
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_screenCamera != null && IsInstanceValid(_screenCamera) && IsInstanceValid(_screenPlayer))
            UpdateScreenLimits();
    }

    // Limites de la caméra = l'écran (640x352) qui contient Brann, borné à la carte. Aucune allocation.
    private void UpdateScreenLimits()
    {
        int w = _screenSize.X, h = _screenSize.Y;
        var pos = _screenPlayer.GlobalPosition;
        int cx = Mathf.Clamp(Mathf.FloorToInt((pos.X - _screenArea.Position.X) / w), 0, Mathf.Max(0, (_screenArea.Size.X - 1) / w));
        int cy = Mathf.Clamp(Mathf.FloorToInt((pos.Y - _screenArea.Position.Y) / h), 0, Mathf.Max(0, (_screenArea.Size.Y - 1) / h));
        if (cx == _screenCell.X && cy == _screenCell.Y) return;
        _screenCell = new Vector2I(cx, cy);
        // Dernier écran calé sur la fin de la carte si elle n'est pas un multiple d'un écran (jamais plus petit que le viewport).
        int left = Mathf.Min(_screenArea.Position.X + cx * w, Mathf.Max(_screenArea.Position.X, _screenArea.End.X - w));
        int top = Mathf.Min(_screenArea.Position.Y + cy * h, Mathf.Max(_screenArea.Position.Y, _screenArea.End.Y - h));
        _screenCamera.LimitLeft = left;
        _screenCamera.LimitTop = top;
        _screenCamera.LimitRight = Mathf.Min(left + w, _screenArea.End.X);
        _screenCamera.LimitBottom = Mathf.Min(top + h, _screenArea.End.Y);
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
                case "Interrupteur": SpawnSwitch(node); break;
                case "BlocPoussable": SpawnBlock(node); break;
                case "PlaqueDePression": SpawnPlate(node); break;
                case "Chute": SpawnFallPassage(node); break;
                case "Torche": SpawnTorch(node); break;
                case "Porte": portes.Add(node); break; // après les ennemis : elles ont besoin de leur nombre
                default:
                    WarnOnce("class:" + node.GetMeta("class").AsString(),
                        $"Objet Tiled de classe « {node.GetMeta("class").AsString()} » pas encore géré ({Name}) : ignoré.");
                    break;
            }
        }

        foreach (var node in portes)
            SpawnDoor(node);

        // Le boss après les portes (il referme celles de la salle) et après les piliers (il s'y assomme).
        foreach (var marker in _bossMarkers)
            SpawnBoss(marker);
    }

    // Rectangles ou points nommés sans classe (indice_ronces_coupees, boss_sylve, pilier...).
    private void HandleUnclassed(Node node)
    {
        string name = node.Name;
        string baseName = BaseName(name);
        if (baseName.StartsWith(BossRules.PillarName, System.StringComparison.Ordinal))
        {
            // Pilier de l'arène : reste un corps solide (YATI) ; on retient son rectangle pour que le boss s'y assomme.
            RegisterPillar(node);
            return;
        }
        if (BossRules.TryParseMarker(baseName, out _))
        {
            _bossMarkers.Add(node); // instancié après les portes
            return;
        }
        if (HintRules.IsHintName(name) && node is StaticBody2D)
        {
            // Zone d'indice : YATI en fait un corps solide qui boucherait le passage. On le retire (la carte reste intacte).
            WarnOnce("indice-solide", "Le rectangle « indice... » est importé comme un corps solide (il manque godot_node_type=area dans Tiled) : retiré à l'exécution.");
            RemoveMarker(node);
            return;
        }
        if (HintRules.IsHintName(name) && node is Area2D hintArea)
        {
            string key = HintRules.KeyFor(name);
            if (string.IsNullOrEmpty(key))
                WarnOnce("indice-nom:" + name, $"Indice « {name} » : nom invalide ({Name}).");
            else
            {
                if (_hintBox == null)
                {
                    _hintBox = new HintBox { Name = "BoiteIndices" }; // une seule boîte de texte pour toute la salle
                    AddChild(_hintBox);
                }
                AddChild(new HintZone { Name = "Indice_" + key, Zone = hintArea, TextKey = key, Box = _hintBox });
            }
            return;
        }
        if (node is Marker2D || node is not StaticBody2D)
            WarnOnce("nom:" + BaseName(name), $"Objet Tiled « {BaseName(name)} » sans classe pas encore géré : ignoré.");
    }

    private void RegisterPillar(Node marker)
    {
        foreach (var child in marker.GetChildren())
        {
            if (child is CollisionShape2D { Shape: RectangleShape2D rect } shape)
            {
                _pillars.Add(new Rect2(shape.GlobalPosition - rect.Size * 0.5f, rect.Size));
                return;
            }
        }
        WarnOnce("pilier-forme", $"Rectangle « pilier » sans forme rectangulaire ({Name}) : ignoré.");
    }

    // --- Boss -----------------------------------------------------------------------------------

    // Rectangle ou point « boss_<nom> » : instancie scenes/enemies/boss/<nom>.tscn. Boss déjà vaincu : pas de boss, la salle est calme
    // et les récompenses pas encore ramassées sont posées au sol.
    private void SpawnBoss(Node marker)
    {
        BossRules.TryParseMarker(BaseName(marker.Name), out string bossName);
        string path = BossRules.ScenePath(bossName);
        if (!ResourceLoader.Exists(path))
        {
            WarnOnce("boss-scene:" + bossName, $"Boss « {bossName} » : scène introuvable ({path}).");
            RemoveMarker(marker);
            return;
        }

        var state = GetNode<GameState>("/root/GameState");
        string bossId = BossRules.BossId(Zone, bossName);
        var boss = GD.Load<PackedScene>(path).Instantiate<Boss>();
        var spot = MarkerPosition(marker);
        var center = spot;
        if (_pillars.Count > 0)
        {
            center = Vector2.Zero;
            foreach (var pillar in _pillars) center += pillar.GetCenter();
            center /= _pillars.Count; // récompenses au milieu des piliers
        }

        if (state.IsCollected(bossId))
        {
            SpawnBossRewards(bossId, boss.DropsHeartContainer, boss.SealPickupName, center, false);
            boss.Free(); // jamais ajouté à l'arbre
            RemoveMarker(marker);
            return;
        }

        boss.BossId = bossId;
        boss.Pillars = _pillars.ToArray();
        boss.ArenaDoors = _doors;
        boss.ArenaBounds = ComputeArenaBounds();
        boss.EntryPoint = EntryPosition;
        boss.Position = _entities.ToLocal(spot);
        _entities.AddChild(boss);
        boss.EncounterStarted += () => _hud?.ShowBossBar(boss.NameKey);
        boss.ProgressChanged += fraction => _hud?.SetBossBar(fraction);
        boss.EncounterEnded += () => _hud?.HideBossBar();
        boss.HintRequested += (key, seconds) =>
        {
            if (_hintBox == null)
            {
                _hintBox = new HintBox { Name = "BoiteIndices" };
                AddChild(_hintBox);
            }
            _hintBox.ShowTimed(key, seconds);
        };
        boss.Defeated += () => OnBossDefeated(boss, center);
        RemoveMarker(marker);
    }

    // Limites où le centre du boss peut aller : la carte entière moins l'épaisseur des murs et son rayon.
    private Rect2 ComputeArenaBounds()
    {
        const float inset = 58f;
        if (FindNodeByName(this, "Sol") is not TileMapLayer floor || floor.TileSet == null)
            return new Rect2();
        var used = floor.GetUsedRect();
        var tile = floor.TileSet.TileSize;
        var pos = floor.GlobalPosition + new Vector2(used.Position.X * tile.X, used.Position.Y * tile.Y);
        var size = new Vector2(used.Size.X * tile.X, used.Size.Y * tile.Y);
        return new Rect2(pos + new Vector2(inset, inset), size - new Vector2(inset * 2f, inset * 2f));
    }

    private void OnBossDefeated(Boss boss, Vector2 center)
    {
        if (!string.IsNullOrEmpty(boss.FarewellKey))
            DialogueBox.Open(this, boss.NameKey, boss.FarewellKey);
        SpawnBossRewards(boss.BossId, boss.DropsHeartContainer, boss.SealPickupName, center, true);
    }

    // Réceptacle de cœur et sceau : deux ramassables uniques (id <boss>_receptacle / <boss>_sceau), mémorisés une fois ramassés.
    private void SpawnBossRewards(string bossId, bool heart, string sealName, Vector2 center, bool animate)
    {
        const float gap = 28f;
        if (heart)
        {
            var heartScene = GD.Load<PackedScene>("res://scenes/items/receptacle.tscn");
            if (heartScene == null)
                GD.PushError("Réceptacle de cœur introuvable : res://scenes/items/receptacle.tscn");
            else
            {
                var pickup = heartScene.Instantiate<Pickup>();
                pickup.UniqueId = BossRules.RewardId(bossId, "receptacle");
                PlaceReward(pickup, center + new Vector2(-gap, 0f), animate);
            }
        }
        if (!string.IsNullOrEmpty(sealName))
        {
            var effect = LoadPickupEffect(sealName, "Sceau de " + bossId);
            if (effect != null)
            {
                var pickup = GD.Load<PackedScene>(PickupScenePath).Instantiate<ItemPickup>();
                pickup.UniqueId = BossRules.RewardId(bossId, "sceau");
                pickup.Effect = effect;
                PlaceReward(pickup, center + new Vector2(gap, 0f), animate);
            }
        }
    }

    private void PlaceReward(Pickup pickup, Vector2 worldPosition, bool animate)
    {
        pickup.Position = _entities.ToLocal(worldPosition);
        _entities.AddChild(pickup);
        var sprite = pickup.GetNodeOrNull<AnimatedSprite2D>("AnimatedSprite2D");
        if (!animate || sprite == null) return;
        sprite.Position = new Vector2(0f, -48f); // l'objet tombe du ciel en rebondissant
        pickup.CreateTween().TweenProperty(sprite, "position", Vector2.Zero, 0.6)
            .SetTrans(Tween.TransitionType.Bounce).SetEase(Tween.EaseType.Out);
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
        _holes?.Track(enemy);

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

    // Interrupteur : propriétés id, cible, mode (fleche par défaut, car les premières cartes n'ont pas « mode »).
    private void SpawnSwitch(Node marker)
    {
        string id = GetString(marker, "id");
        string modeValue = GetString(marker, "mode");
        if (!SwitchRules.TryParseMode(modeValue, out var mode))
            WarnOnce("interrupteur-mode:" + modeValue, $"Interrupteur « {id} » : mode inconnu « {modeValue} » (fleche ou epee) dans {Name}, traité comme « fleche ».");
        else if (string.IsNullOrEmpty(modeValue))
            WarnOnce("interrupteur-sans-mode", "Interrupteur sans propriété « mode » dans Tiled : traité comme « fleche ».");

        var sw = (_switchScene ??= GD.Load<PackedScene>(SwitchScenePath)).Instantiate<Switch>();
        sw.Id = id;
        sw.Target = GetString(marker, "cible");
        sw.Mode = mode;
        sw.Order = Mathf.Max(0, Mathf.RoundToInt(GetFloat(marker, "ordre")));
        sw.Duration = Mathf.Max(0f, GetFloat(marker, "duree"));
        sw.Symbol = GetString(marker, "symbole");
        sw.Position = _entities.ToLocal(ObjectCenter(marker));
        _entities.AddChild(sw);
        RemoveMarker(marker);
    }

    // Bloc poussable : posé au centre de la case du marqueur ; revient là à chaque chargement (rien n'est sauvegardé).
    private void SpawnBlock(Node marker)
    {
        var block = (_blockScene ??= GD.Load<PackedScene>(BlockScenePath)).Instantiate<PushBlock>();
        block.Position = _entities.ToLocal(ObjectCenter(marker));
        _entities.AddChild(block);
        _blocks.Add(block);
        RemoveMarker(marker);
    }

    // Torche ou brasero : un point au centre de la case ; propriétés id, etat, permanente, duree, cible.
    private void SpawnTorch(Node marker)
    {
        string id = GetString(marker, "id");
        string stateValue = GetString(marker, "etat");
        if (!TorchRules.TryParseLit(stateValue, out bool lit))
            WarnOnce("torche-etat:" + stateValue, $"Torche « {id} » : etat inconnu « {stateValue} » (eteinte ou allumee) dans {Name}, traité comme « eteinte ».");

        var torch = (_torchScene ??= GD.Load<PackedScene>(TorchScenePath)).Instantiate<Torch>();
        torch.Id = id;
        torch.Target = GetString(marker, "cible");
        torch.Permanent = GetBool(marker, "permanente");
        torch.StartLit = lit || torch.Permanent;
        torch.Duration = Mathf.Max(0f, GetFloat(marker, "duree"));
        torch.Position = _entities.ToLocal(ObjectCenter(marker));
        _entities.AddChild(torch);
        RemoveMarker(marker);
    }

    // Propriétés de carte Tiled (etage, carte_x, carte_y) : YATI les met en metadata sur la racine de la carte importée.
    private void ReadMapProperties()
    {
        Node source = null;
        foreach (var child in GetChildren())
            if (child.HasMeta("etage") || child.HasMeta("carte_x") || child.HasMeta("carte_y") || child.HasMeta("camera"))
            {
                source = child;
                break;
            }
        if (source == null) return;

        string camera = GetString(source, "camera").Trim().ToLowerInvariant();
        if (camera == "ecran" || camera == "suivre")
            CameraMode = camera;
        else if (camera != "")
            WarnOnce("camera:" + camera, $"Carte {Name} : camera inconnue « {camera} » (ecran ou suivre), « suivre » utilisé.");

        MapFloor = GetString(source, "etage");
        MapCell = new Vector2I(Mathf.RoundToInt(GetFloat(source, "carte_x")), Mathf.RoundToInt(GetFloat(source, "carte_y")));
        HasMapPosition = source.HasMeta("etage") && source.HasMeta("carte_x") && source.HasMeta("carte_y");
        if (MapFloor != "" && MapFloor != "rdc" && MapFloor != "sous_sol")
            WarnOnce("etage:" + MapFloor, $"Carte {Name} : etage inconnu « {MapFloor} » (rdc ou sous_sol).");
    }

    // Plaque de pression : une case de 32x32 au sol, dessinée sous les entités (Brann et les blocs passent dessus).
    private void SpawnPlate(Node marker)
    {
        string id = GetString(marker, "id");
        string triggerValue = GetString(marker, "declencheur");
        if (!PressurePlateRules.TryParseTrigger(triggerValue, out var trigger))
            WarnOnce("plaque-declencheur:" + triggerValue, $"Plaque « {id} » : declencheur inconnu « {triggerValue} » (bloc, joueur ou tous) dans {Name}, traité comme « tous ».");

        var plate = (_plateScene ??= GD.Load<PackedScene>(PlateScenePath)).Instantiate<PressurePlate>();
        plate.Id = id;
        plate.Target = GetString(marker, "cible");
        plate.Trigger = trigger;
        var center = ObjectCenter(marker);
        center = new Vector2(
            PushBlockRules.SnapToCellCenter(center.X, plate.CellSize),
            PushBlockRules.SnapToCellCenter(center.Y, plate.CellSize));
        AddUnderEntities(plate, center);
        RemoveMarker(marker);
    }

    // Trou de passage : un rectangle (Area2D importée ou corps solide) remplacé par la scène « chute ».
    private void SpawnFallPassage(Node marker)
    {
        string id = GetString(marker, "id");
        var center = ObjectCenter(marker);
        var size = new Vector2(32f, 32f);
        foreach (var child in marker.GetChildren())
            if (child is CollisionShape2D { Shape: RectangleShape2D rect })
            {
                size = rect.Size;
                break;
            }

        var passage = (_fallScene ??= GD.Load<PackedScene>(FallScenePath)).Instantiate<FallPassage>();
        passage.Id = id;
        passage.TargetScene = GetString(marker, "cible_carte");
        passage.TargetSpawn = GetString(marker, "cible_spawn");
        if (string.IsNullOrEmpty(passage.TargetScene))
            GD.PushError($"Chute « {id} » sans propriété « cible_carte » dans {Name}.");
        // La forme de la scène est partagée entre instances : on la remplace par une copie à la bonne taille.
        passage.GetNode<CollisionShape2D>("CollisionShape2D").Shape = new RectangleShape2D { Size = size };
        AddUnderEntities(passage, center);
        RemoveMarker(marker);
    }

    // Pose un nœud juste avant le conteneur d'entités : au-dessus de la carte, sous Brann et les ennemis.
    private void AddUnderEntities(Node2D node, Vector2 globalCenter)
    {
        var parent = _entities.GetParent();
        parent.AddChild(node);
        parent.MoveChild(node, _entities.GetIndex());
        node.GlobalPosition = globalCenter;
    }

    // Les blocs refusent de glisser sur ou à côté d'un Spawn, d'une Sortie ou d'une Porte (sinon ils pourraient enfermer Brann).
    private void ShareForbiddenCells()
    {
        if (_blocks.Count == 0) return;
        var forbidden = new HashSet<(int, int)>();
        foreach (var spawn in FindAllByClass(this, "Spawn"))
        {
            if (spawn is not Node2D point) continue;
            var p = point.GlobalPosition;
            PushBlockRules.AddForbiddenAround(forbidden, PushBlockRules.CellIndex(p.X, GridCell), PushBlockRules.CellIndex(p.Y, GridCell));
        }
        foreach (var sortie in FindAllByClass(this, "Sortie"))
            AddRectCells(forbidden, sortie);
        foreach (var door in _doors)
        {
            if (!IsInstanceValid(door)) continue;
            var p = door.GlobalPosition;
            PushBlockRules.AddForbiddenAround(forbidden, PushBlockRules.CellIndex(p.X, GridCell), PushBlockRules.CellIndex(p.Y, GridCell));
        }
        foreach (var block in _blocks)
            block.ForbiddenCells = forbidden;
    }

    // Ajoute (avec leurs voisines) toutes les cases couvertes par le rectangle d'un objet Tiled.
    private static void AddRectCells(HashSet<(int, int)> forbidden, Node marker)
    {
        var center = MarkerPosition(marker);
        var size = Vector2.Zero;
        foreach (var child in marker.GetChildren())
            if (child is CollisionShape2D { Shape: RectangleShape2D rect } shape)
            {
                center = shape.GlobalPosition;
                size = rect.Size;
                break;
            }
        if (size == Vector2.Zero)
        {
            PushBlockRules.AddForbiddenAround(forbidden, PushBlockRules.CellIndex(center.X, GridCell), PushBlockRules.CellIndex(center.Y, GridCell));
            return;
        }
        // 0,5 px de marge : un rectangle exactement aligné sur la grille ne déborde pas sur la case voisine.
        int x0 = PushBlockRules.CellIndex(center.X - size.X * 0.5f + 0.5f, GridCell);
        int x1 = PushBlockRules.CellIndex(center.X + size.X * 0.5f - 0.5f, GridCell);
        int y0 = PushBlockRules.CellIndex(center.Y - size.Y * 0.5f + 0.5f, GridCell);
        int y1 = PushBlockRules.CellIndex(center.Y + size.Y * 0.5f - 0.5f, GridCell);
        for (int cx = x0; cx <= x1; cx++)
            for (int cy = y0; cy <= y1; cy++)
                PushBlockRules.AddForbiddenAround(forbidden, cx, cy);
    }

    // Trous : surveillés d'après le calque « Sol » (voir HoleWatcher). Pas de calque Sol : pas de trous.
    private void SetupHoles(Player player)
    {
        if (player == null || FindNodeByName(this, "Sol") is not TileMapLayer floor) return;
        _holes = new HoleWatcher { Name = "Trous", Floor = floor, Player = player, RespawnPosition = EntryPosition };
        AddChild(_holes);
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
        return ResourceKeeper.Load<PickupEffect>(path); // référence forte gardée (voir ResourceKeeper) ; erreur claire si null
    }

    // Retire le marqueur importé de l'arbre (pas du fichier) : il est remplacé par la vraie scène.
    private static void RemoveMarker(Node marker)
    {
        marker.GetParent()?.RemoveChild(marker);
        marker.QueueFree();
    }

    // Centre d'un objet Tiled : le point lui-même, ou le centre de la forme si l'objet est un rectangle.
    private static Vector2 ObjectCenter(Node marker)
    {
        foreach (var child in marker.GetChildren())
            if (child is CollisionShape2D shape)
                return shape.GlobalPosition;
        return MarkerPosition(marker);
    }

    private static Vector2 MarkerPosition(Node marker) => marker is Node2D n ? n.GlobalPosition : Vector2.Zero;

    private static string GetString(Node node, string key, string fallback = "")
    {
        if (!node.HasMeta(key)) return fallback;
        return node.GetMeta(key).AsString();
    }

    private static float GetFloat(Node node, string key, float fallback = 0f)
    {
        if (!node.HasMeta(key)) return fallback;
        var value = node.GetMeta(key);
        switch (value.VariantType)
        {
            case Variant.Type.Int: return (float)value.AsInt64();
            case Variant.Type.Float: return (float)value.AsDouble();
            case Variant.Type.String:
                return float.TryParse(value.AsString(), NumberStyles.Float, CultureInfo.InvariantCulture, out float parsed) ? parsed : fallback;
            default: return fallback;
        }
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

    // Règle générale : une Sortie ne se déclenche pas si Brann est déjà dans sa zone à l'arrivée (Spawn posé dessus, retour
    // après une mort...). Elle s'arme quand il l'a quittée. Au départ aucune n'est armée ; après deux images physiques
    // (le temps que les zones détectent Brann) on arme celles qui ne le touchent pas.
    private async Task ArmSortiesAfterArrival(List<SortieState> sorties, Player player)
    {
        try
        {
            var tree = GetTree();
            await ToSignal(tree, SceneTree.SignalName.PhysicsFrame);
            await ToSignal(tree, SceneTree.SignalName.PhysicsFrame);
            if (!IsInstanceValid(this) || !IsInsideTree()) return;
            foreach (var state in sorties)
            {
                if (!IsInstanceValid(state.Area)) continue;
                if (player == null || !IsInstanceValid(player) || !state.Area.OverlapsBody(player))
                    state.Armed = true;
            }
        }
        catch (System.Exception e)
        {
            GD.PushError($"Armement des Sorties de {Name} : {e.Message}");
            foreach (var state in sorties) state.Armed = true; // mieux vaut des sorties actives qu'une salle sans issue
        }
    }

    private void OnSortieEntered(SortieState state, Node body)
    {
        if (!state.Armed) return;
        var sortie = state.Area;
        if (body is not Player { IsDead: false }) return;
        if (!sortie.HasMeta("cible_carte")) return;
        if (IsBlockedByClosedDoor(sortie)) return; // recul ou poussée qui amènerait Brann sur la Sortie d'une porte fermée

        var cibleCarte = (string)sortie.GetMeta("cible_carte");
        var cibleSpawn = sortie.HasMeta("cible_spawn") ? (string)sortie.GetMeta("cible_spawn") : "";
        if (!SceneIsAvailable(cibleCarte))
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

        var sceneManager = GetNode<SceneManager>("/root/SceneManager");
        if (GetString(sortie, "transition") == "escalier")
            sceneManager.GoToScene(cibleCarte, cibleSpawn, null, "escalier", StairsFadeDuration); // signal TransitionStarted("escalier") : accroche du son
        else
            sceneManager.GoToScene(cibleCarte, cibleSpawn);
    }

    // Une scène est utilisable si son fichier existe ET que ses dépendances directes existent (ex. foret_temple_room.tscn
    // existe avant que le .tmx de la carte ait été peint). Chaque dépendance : « uid://...::type::chemin » ; on teste l'uid
    // d'abord (le fichier a pu être déplacé), puis le chemin.
    private static bool SceneIsAvailable(string path)
    {
        if (!ResourceLoader.Exists(path)) return false;
        foreach (var dep in ResourceLoader.GetDependencies(path))
        {
            if (dep.StartsWith("uid://", System.StringComparison.Ordinal))
            {
                int end = dep.IndexOf("::", System.StringComparison.Ordinal);
                string uid = end >= 0 ? dep.Substring(0, end) : dep;
                long id = ResourceUid.TextToId(uid);
                if (id != ResourceUid.InvalidId && ResourceUid.HasId(id)) continue;
            }
            int cut = dep.LastIndexOf("::", System.StringComparison.Ordinal);
            string depPath = cut >= 0 ? dep.Substring(cut + 2) : dep;
            if (depPath.Length > 0 && !ResourceLoader.Exists(depPath)) return false;
        }
        return true;
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
