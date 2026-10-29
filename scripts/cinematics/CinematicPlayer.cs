using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Godot;

/// <summary>
/// Lecteur de cinématiques : joue une <see cref="CinematicData"/> (liste d'étapes lues dans resources/cinematiques/&lt;id&gt;.json) dans l'ordre.
/// Ce n'est PAS un autoload : un nœud enfant de chaque <see cref="Room"/>, créé par elle, qui connaît les repères de la carte et ses ennemis scénarisés.
///
/// Pendant la lecture : Brann est en mode « cinématique » (aucun contrôle, invincible), le menu pause ne s'ouvre pas
/// (<see cref="Active"/>), et le joueur peut PASSER la cinématique en maintenant « pause » (Échap / Start) une seconde. Passer ne saute pas
/// les effets durables : chaque étape a un « état final » (position, teinte, drapeaux, objets donnés, ennemis créés, salle suivante...)
/// qui est appliqué d'un coup. Les dialogues, attentes, sons et secousses, eux, sont simplement sautés.
///
/// Principe Godot : les étapes sont une méthode « async ». Chaque « await » rend la main au moteur jusqu'à la prochaine image (ou la fin
/// d'une boîte de dialogue), puis reprend là où elle s'était arrêtée : on écrit le scénario comme une suite d'instructions, sans machine à états.
/// </summary>
public partial class CinematicPlayer : Node
{
    /// <summary>Une cinématique se termine (id, passée ou non). Émis aussi si elle est passée.</summary>
    [Signal]
    public delegate void FinishedEventHandler(string id, bool skipped);

    /// <summary>Vrai pendant qu'une cinématique joue, dans n'importe quelle salle (le menu pause refuse alors de s'ouvrir).</summary>
    public static bool Active { get; private set; }

    /// <summary>Durée (s) de maintien de la touche « pause » pour passer.</summary>
    [Export(PropertyHint.Range, "0.3,3,0.1")] public float SkipHoldSeconds { get; set; } = 1f;

    public bool IsPlaying { get; private set; }

    /// <summary>La dernière cinématique jouée a été passée par le joueur.</summary>
    public bool WasSkipped { get; private set; }

    private static readonly StringName ActionSkip = "pause";
    private const string NpcScenePath = "res://scenes/npc/pnj.tscn";
    private const string ThemePath = "res://resources/ui/theme_jeu.tres";
    private const string DecorFolder = "res://art/cinematiques/";

    private Room _room;
    private Player _player;
    private SceneTree _tree;
    private GameState _state;
    private SceneManager _sceneManager;

    private bool _skip;
    private float _hold;
    private bool _leaving; // une étape « aller_a » a lancé le changement de salle : Brann reste figé jusqu'à son départ
    private int _moves;
    private readonly HashSet<string> _spawnBatch = new(); // drapeaux de combat déjà servis par la cinématique en cours
    private CinematicData _current;
    private DialogueBox _box;

    private CanvasLayer _fadeLayer;
    private ColorRect _fadeRect;
    private float _fadeAlpha;
    private CanvasLayer _hintLayer;
    private Label _hintLabel;
    private ColorRect _hintBar;
    private ColorRect _hintBarBack;

    private CameraShake _cineCam;
    private Camera2D _playerCam;

    private readonly Dictionary<string, Actor> _actors = new();
    private readonly Dictionary<string, List<Health>> _deathGroups = new();

    // Un personnage pilotable : Brann ou un PNJ.
    private sealed class Actor
    {
        public Node2D Node;
        public Player Brann;
        public Npc Npc;
        public Vector2 Position
        {
            get => Node.GlobalPosition;
            set => Node.GlobalPosition = value;
        }

        public void Pose(Vector2 direction, bool walking)
        {
            if (Brann != null) Brann.CinematicPose(direction, walking);
            else Npc?.ScriptedPose(direction, walking);
        }

        public bool Valid => GodotObject.IsInstanceValid(Node);
    }

    /// <summary>Appelé par la salle une fois Brann en place.</summary>
    public void Setup(Room room, Player player)
    {
        _room = room;
        _player = player;
        _tree = GetTree();
        _state = GetNode<GameState>("/root/GameState");
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        ProcessMode = ProcessModeEnum.Always; // le maintien de la touche « passer » doit marcher pendant un dialogue (le jeu est alors en pause)
        SetProcess(false);
    }

    public override void _ExitTree()
    {
        // La salle part (changement de salle, retour à l'écran titre...) : ne jamais laisser le jeu figé ou le menu bloqué.
        if (IsPlaying)
        {
            IsPlaying = false;
            _skip = true;
        }
        Active = false;
    }

    // --- Lecture ---------------------------------------------------------------------------------

    /// <summary>
    /// Joue la cinématique jusqu'au bout (ou jusqu'à ce que le joueur la passe). Sans effet si une autre joue déjà.
    /// À lancer avec « _ = cinematics.Play(data); » ou à attendre avec await.
    /// </summary>
    public async Task Play(CinematicData data)
    {
        if (data == null || IsPlaying || _room == null || !IsInstanceValid(_player)) return;
        if (!_player.BeginCinematic())
        {
            GD.PushWarning($"Cinématique « {data.Id} » : Brann est occupé (mort ou en chute), elle ne démarre pas.");
            return;
        }
        IsPlaying = true;
        Active = true;
        _skip = false;
        _hold = 0f;
        _leaving = false;
        _spawnBatch.Clear();
        WasSkipped = false;
        _current = data;
        SetProcess(true);
        try
        {
            ShowHint(data.Skippable);
            foreach (var step in data.Steps)
            {
                if (_skip) ApplyFinal(step, false);
                else await Execute(step);
            }
            while (_moves > 0) await NextFrame(); // un déplacement lancé sans attente finit son trajet
        }
        catch (OperationCanceledException)
        {
            return; // la salle a été libérée en cours de route : _ExitTree a déjà tout remis en ordre
        }
        catch (Exception e)
        {
            GD.PushError($"Cinématique « {data.Id} » interrompue : {e.Message}");
        }
        Finish(data);
    }

    private void Finish(CinematicData data)
    {
        if (!IsInstanceValid(this) || !IsInsideTree()) { Active = false; return; }
        bool skipped = WasSkipped = _skip;
        if (!string.IsNullOrEmpty(data.EndFlag)) _state.MarkCollected(data.EndFlag);
        SetProcess(false);
        HideHint();
        SetFade(0f); // jamais d'écran noir oublié
        ReleaseCamera();
        foreach (var actor in _actors.Values)
            ReleaseActor(actor);
        _actors.Clear();
        _current = null;
        _box = null;
        IsPlaying = false;
        if (!_leaving)
        {
            Active = false;
            if (IsInstanceValid(_player)) _player.EndCinematic();
        }
        // Si la salle change (« aller_a »), Brann reste en mode cinématique jusqu'à son remplacement et Active retombe dans _ExitTree.
        EmitSignal(SignalName.Finished, data.Id, skipped);
    }

    // Les personnages créés par la cinématique redeviennent de vrais PNJ s'ils ont un fichier de dialogues ; sinon ils restent figés (décor).
    private void ReleaseActor(Actor actor)
    {
        if (actor.Npc == null || !actor.Valid || !actor.Npc.IsScripted) return;
        if (FileAccess.FileExists($"res://resources/dialogues/{actor.Npc.Id}.json"))
            actor.Npc.EndScripted();
    }

    public override void _Process(double delta)
    {
        if (!IsPlaying || _current == null) return;
        if (!_current.Skippable || _skip)
        {
            _hold = 0f;
            return;
        }
        if (Input.IsActionPressed(ActionSkip))
        {
            _hold += (float)delta;
            if (_hold >= SkipHoldSeconds) RequestSkip();
        }
        else
            _hold = Mathf.Max(0f, _hold - (float)delta * 2f);
        UpdateHint();
    }

    /// <summary>Passe la cinématique en cours (public pour les tests) : les effets durables restent appliqués.</summary>
    public void RequestSkip()
    {
        if (!IsPlaying || _skip || _current == null || !_current.Skippable) return;
        _skip = true;
        if (_box != null && IsInstanceValid(_box)) _box.Close();
    }

    // --- Exécution d'une étape ---------------------------------------------------------------------

    private async Task Execute(CinematicStep step)
    {
        switch (step.Action)
        {
            case "dialogue": await RunDialogue(step); break;
            case "deplacer":
                {
                    var actor = FindActor(step.Actor);
                    if (actor == null || !ResolveTarget(step, out var target)) break;
                    var task = MoveActor(step, actor, target);
                    if (step.WaitEnd) await task;
                    break;
                }
            case "attendre":
                if (step.WaitMoves) { while (_moves > 0 && !_skip) await NextFrame(); }
                else await Wait(step.Seconds);
                break;
            case "fondu": await Fade(step.Value == "noir" ? 1f : 0f, step.Seconds); break;
            case "teinte": await TintTo(step); break;
            case "camera": await MoveCamera(step); break;
            case "son":
                AudioManager.Play(new StringName(step.Name));
                break;
            case "secousse":
                if (_room.GetViewport()?.GetCamera2D() is CameraShake shake) shake.Shake(step.Strength, Mathf.Max(step.Seconds, 0.1f));
                break;
            case "donner":
                ApplyFinal(step, true);
                if (!_skip) await Wait(1.6f); // le bandeau « Vous obtenez » a le temps d'être lu
                break;
            default:
                ApplyFinal(step, true);
                break;
        }
    }

    // État final d'une étape (appliqué d'un coup quand la cinématique est passée, et à la fin des étapes animées). Sans attente.
    private void ApplyFinal(CinematicStep step, bool announce)
    {
        switch (step.Action)
        {
            case "deplacer":
            case "placer":
                {
                    var actor = FindActor(step.Actor);
                    if (actor == null || !ResolveTarget(step, out var target)) break;
                    actor.Position = target;
                    if (actor.Brann != null) _playerCam?.ResetSmoothing();
                    break;
                }
            case "regarder":
                {
                    var actor = FindActor(step.Actor);
                    if (actor == null) break;
                    var look = DirectionOf(step);
                    if (step.Target.Length > 0 && ResolveTarget(step, out var lookAt)) look = lookAt - actor.Position;
                    actor.Pose(look, false);
                    break;
                }
            case "animer":
                {
                    var actor = FindActor(step.Actor);
                    if (actor == null) break;
                    if (actor.Npc != null)
                    {
                        if (!actor.Npc.ScriptedPlay(new StringName(step.Name)))
                            GD.PushWarning($"Cinématique : « {step.Actor} » n'a pas l'animation « {step.Name} ».");
                    }
                    break;
                }
            case "fondu": SetFade(step.Value == "noir" ? 1f : 0f); break;
            case "teinte":
                if (CinematicColors.TryParse(step.Value, out float r, out float g, out float b)) _room.SetTint(new Color(r, g, b));
                break;
            case "musique":
                if (step.Name == "stop") AudioManager.Instance?.StopMusic(announce ? step.Seconds : 0f);
                else AudioManager.Instance?.PlayMusicFile($"res://audio/musique/{step.Name}.ogg", announce ? step.Seconds : 0f);
                break;
            case "camera":
                if (step.Target == "brann") ReleaseCamera();
                else if (ResolveTarget(step, out var cam))
                {
                    EnsureCineCamera();
                    if (_cineCam != null) _cineCam.GlobalPosition = cam;
                }
                break;
            case "apparaitre": Appear(step); break;
            case "disparaitre": Disappear(step); break;
            case "donner": Give(step, announce); break;
            case "drapeau": _state.MarkCollected(step.Name); break;
            case "aller_a": _ = GoToScene(step); break;
            case "sauvegarder": GetNode<SaveSystem>("/root/SaveSystem").RequestAutoSave(); break;
        }
    }

    // --- Dialogue ---------------------------------------------------------------------------------

    private async Task RunDialogue(CinematicStep step)
    {
        if (_skip) return;
        var lines = new string[step.Lines.Count];
        for (int i = 0; i < lines.Length; i++)
            lines[i] = Tr(step.Lines[i]);
        string speaker = string.IsNullOrEmpty(step.Speaker) ? "" : Tr(step.Speaker);
        _box = DialogueBox.OpenModal(this, speaker, lines);
        await ToSignal(_box, DialogueBox.SignalName.Finished);
        _box = null;
    }

    // --- Déplacements -----------------------------------------------------------------------------

    private async Task MoveActor(CinematicStep step, Actor actor, Vector2 target)
    {
        _moves++;
        try
        {
            var last = Vector2.Down;
            while (!_skip && actor.Valid)
            {
                var to = target - actor.Position;
                float dist = to.Length();
                if (dist <= 0.5f) break;
                var dir = to / dist;
                last = dir;
                float stepLength = step.Speed * (float)GetProcessDeltaTime();
                actor.Position = dist <= stepLength ? target : actor.Position + dir * stepLength;
                actor.Pose(dir, true);
                await NextFrame();
            }
            if (actor.Valid)
            {
                actor.Position = target;
                actor.Pose(last, false);
            }
        }
        finally
        {
            _moves--;
        }
    }

    private static Vector2 DirectionOf(CinematicStep step)
    {
        return step.Direction switch
        {
            "up" => Vector2.Up,
            "left" => Vector2.Left,
            "right" => Vector2.Right,
            "down" => Vector2.Down,
            _ => Vector2.Down,
        };
    }

    // Position monde visée par une étape : repère de la salle ou « @acteur », plus le décalage.
    private bool ResolveTarget(CinematicStep step, out Vector2 position)
    {
        position = Vector2.Zero;
        string spec = step.Target;
        if (string.IsNullOrEmpty(spec)) return false;
        if (spec[0] == '@')
        {
            var other = FindActor(spec[1..]);
            if (other == null) return false;
            position = other.Position;
        }
        else if (!_room.TryGetPoint(spec, out position))
            return false;
        position += new Vector2(step.OffsetX, step.OffsetY);
        return true;
    }

    // Brann, un acteur créé par la cinématique, ou un PNJ déjà présent dans la salle (trouvé par son id).
    private Actor FindActor(string id)
    {
        if (string.IsNullOrEmpty(id)) return null;
        if (_actors.TryGetValue(id, out var known) && known.Valid) return known;
        if (id == "brann")
        {
            var brann = new Actor { Node = _player, Brann = _player };
            _actors[id] = brann;
            return brann;
        }
        foreach (var child in _room.EntitiesNode.GetChildren())
        {
            if (child is Npc npc && npc.Id == id && !npc.IsQueuedForDeletion())
            {
                npc.BeginScripted();
                var found = new Actor { Node = npc, Npc = npc };
                _actors[id] = found;
                return found;
            }
        }
        GD.PushWarning($"Cinématique « {_current?.Id} » : personnage « {id} » introuvable dans la salle.");
        return null;
    }

    // --- Apparitions ------------------------------------------------------------------------------

    private void Appear(CinematicStep step)
    {
        switch (step.Kind)
        {
            case "pnj": AppearNpc(step); break;
            case "ennemis": AppearScenarioEnemies(step); break;
            case "ennemi": AppearEnemy(step); break;
            case "decor": AppearDecor(step); break;
            case "ramassable":
                if (_room.HasPickup(step.Id) || _state.IsCollected(step.Id)) break; // déjà dans la carte, ou déjà ramassé : rien à poser
                if (ResolveTarget(step, out var pos)) _room.TrySpawnPickup(step.Id, step.Content, pos);
                break;
        }
    }

    private void AppearNpc(CinematicStep step)
    {
        if (!ResolveTarget(step, out var position)) return;
        var existing = FindActorQuiet(step.Id);
        if (existing != null)
        {
            existing.Position = position; // déjà là (revenu dans la salle) : on le remet à sa place
            return;
        }
        var scene = GD.Load<PackedScene>(NpcScenePath);
        if (scene == null)
        {
            GD.PushError($"Cinématique : scène {NpcScenePath} introuvable.");
            return;
        }
        var npc = scene.Instantiate<Npc>();
        PhysicsLayers.BlockedByRavine(npc);
        npc.Id = step.Id;
        npc.SpriteName = step.Sprite;
        npc.InitialDirection = string.IsNullOrEmpty(step.Direction) ? "down" : step.Direction;
        npc.Position = _room.EntitiesNode.ToLocal(position);
        _room.EntitiesNode.AddChild(npc);
        npc.BeginScripted();
        _actors[step.Id] = new Actor { Node = npc, Npc = npc };
    }

    // Comme FindActor mais sans avertissement si absent.
    private Actor FindActorQuiet(string id)
    {
        if (_actors.TryGetValue(id, out var known) && known.Valid) return known;
        foreach (var child in _room.EntitiesNode.GetChildren())
            if (child is Npc npc && npc.Id == id && !npc.IsQueuedForDeletion())
                return FindActor(id);
        return null;
    }

    private void AppearScenarioEnemies(CinematicStep step)
    {
        if (!CanSpawnEnemies(step.DeathFlag)) return;
        int count = 0;
        foreach (var info in _room.ScenarioEnemies)
        {
            if (step.Type.Length > 0 && info.Type != step.Type) continue;
            if (step.Group.Length > 0 && info.Group != step.Group) continue;
            TrackDeath(step.DeathFlag, _room.SpawnScenarioEnemy(info.Type, info.Variant, info.Position));
            count++;
        }
        if (count == 0)
            GD.PushWarning($"Cinématique « {_current?.Id} » : aucun ennemi « apparition = scenario » (type « {step.Type} », groupe « {step.Group} ») dans la carte {_room.RoomStem}.");
    }

    private void AppearEnemy(CinematicStep step)
    {
        if (!CanSpawnEnemies(step.DeathFlag) || !ResolveTarget(step, out var position)) return;
        TrackDeath(step.DeathFlag, _room.SpawnScenarioEnemy(step.Type, step.Variant, position));
    }

    // Faux si le combat est déjà gagné (drapeau posé) ou si les ennemis de ce drapeau sont déjà là (cinématique rejouée en boucle).
    private bool CanSpawnEnemies(string deathFlag)
    {
        if (string.IsNullOrEmpty(deathFlag)) return true;
        if (_spawnBatch.Contains(deathFlag)) return true; // plusieurs étapes d'un même combat dans cette cinématique
        if (_state.IsCollected(deathFlag)) return false;
        if (_deathGroups.TryGetValue(deathFlag, out var list))
        {
            list.RemoveAll(h => !IsInstanceValid(h));
            if (list.Count > 0) return false;
        }
        _spawnBatch.Add(deathFlag);
        return true;
    }

    // Quand tous les ennemis créés pour ce drapeau sont morts (ou ont quitté la salle), le drapeau est posé.
    private void TrackDeath(string flag, Node2D enemy)
    {
        if (string.IsNullOrEmpty(flag) || enemy == null) return;
        var health = enemy.GetNodeOrNull<Health>("Health");
        if (health == null) return;
        if (!_deathGroups.TryGetValue(flag, out var list))
            _deathGroups[flag] = list = new List<Health>();
        list.Add(health);
        health.Died += () => OnTrackedGone(flag, health);
        health.TreeExiting += () => Callable.From(() =>
        {
            if (IsInstanceValid(this) && IsInsideTree()) OnTrackedGone(flag, health); // pas quand c'est la salle entière qui part
        }).CallDeferred();
    }

    private void OnTrackedGone(string flag, Health health)
    {
        if (!_deathGroups.TryGetValue(flag, out var list) || !list.Remove(health)) return;
        list.RemoveAll(h => !IsInstanceValid(h));
        if (list.Count == 0) _state.MarkCollected(flag);
    }

    private void AppearDecor(CinematicStep step)
    {
        if (!ResolveTarget(step, out var position)) return;
        string name = "Decor_" + step.Id;
        if (_room.GetNodeOrNull(name) != null) return;
        var decor = new Node2D { Name = name, GlobalPosition = position };
        string path = $"{DecorFolder}{step.Image}.png";
        if (step.Image.Length > 0 && ResourceLoader.Exists(path))
            decor.AddChild(new Sprite2D { Texture = GD.Load<Texture2D>(path) });
        else
        {
            // Repère de remplacement tant que le graphiste n'a pas livré l'image : quelques empreintes sombres qui descendent.
            for (int i = 0; i < 6; i++)
                decor.AddChild(new ColorRect
                {
                    Color = new Color(0.12f, 0.08f, 0.1f, 0.85f),
                    Size = new Vector2(5f, 8f),
                    Position = new Vector2((i % 2 == 0 ? -6f : 2f), i * 14f),
                    MouseFilter = Control.MouseFilterEnum.Ignore,
                });
        }
        // Posé au sol : juste au-dessus de la carte, sous les personnages (qui sont dans le conteneur Entites, plus bas dans l'arbre).
        _room.AddChild(decor);
        var map = _room.GetNodeOrNull("Map");
        if (map != null) _room.MoveChild(decor, map.GetIndex() + 1);
    }

    private void Disappear(CinematicStep step)
    {
        if (step.Actor == "brann") return;
        var actor = FindActorQuiet(step.Actor);
        if (actor == null) return;
        _actors.Remove(step.Actor);
        if (actor.Valid) actor.Node.QueueFree();
    }

    // --- Objets, salle suivante ---------------------------------------------------------------------

    private void Give(CinematicStep step, bool announce)
    {
        if (step.Id.Length > 0 && _state.IsCollected(step.Id)) return;
        var effect = ResourceKeeper.Load<PickupEffect>(RoomObjectCatalog.PickupEffectPath(step.Content));
        if (effect == null)
        {
            GD.PushError($"Cinématique « {_current?.Id} » : contenu « {step.Content} » introuvable.");
            return;
        }
        if (!effect.CanApply(_player, _state))
        {
            GD.PushWarning($"Cinématique « {_current?.Id} » : « {step.Content} » ne peut pas être donné maintenant.");
            return;
        }
        if (step.Id.Length > 0) _state.MarkCollected(step.Id);
        effect.Apply(_player, _state);
        if (announce)
        {
            AudioManager.Play(effect.PickupSound);
            PickupBanner.Announce(_player, effect);
        }
    }

    // Change de salle (terminal : la suite de la cinématique n'a plus de sens). Brann reste figé jusqu'au remplacement de la salle.
    private async Task GoToScene(CinematicStep step)
    {
        _leaving = true;
        try
        {
            for (int tries = 0; tries < 180; tries++)
            {
                if (_sceneManager.GoToScene(step.Scene, step.Spawn)) return;
                await NextFrame(); // un fondu est déjà en cours : on réessaie
            }
            GD.PushError($"Cinématique : impossible d'aller à {step.Scene}.");
            _leaving = false;
            if (!IsPlaying && IsInstanceValid(this) && IsInsideTree())
            {
                // Finish() avait laissé Brann figé en attendant le départ : la salle ne part pas, on lui rend la main.
                Active = false;
                if (IsInstanceValid(_player)) _player.EndCinematic();
            }
        }
        catch (OperationCanceledException)
        {
            // la salle est déjà partie : rien à faire
        }
    }

    // --- Fondu noir, teinte, caméra ---------------------------------------------------------------

    private void EnsureFadeLayer()
    {
        if (_fadeLayer != null) return;
        _fadeLayer = new CanvasLayer { Name = "FonduCinematique", Layer = 5 }; // sous les boîtes de texte (6) et le fondu de salle (10)
        _fadeRect = new ColorRect { Color = new Color(0f, 0f, 0f, 0f), MouseFilter = Control.MouseFilterEnum.Ignore };
        _fadeRect.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        _fadeLayer.AddChild(_fadeRect);
        AddChild(_fadeLayer);
    }

    private void SetFade(float alpha)
    {
        if (_fadeLayer == null && alpha <= 0f) return;
        EnsureFadeLayer();
        _fadeAlpha = alpha;
        _fadeRect.Color = new Color(0f, 0f, 0f, alpha);
    }

    private async Task Fade(float target, float duration)
    {
        float start = _fadeAlpha;
        float t = 0f;
        while (t < duration && !_skip)
        {
            await NextFrame();
            t += (float)GetProcessDeltaTime();
            SetFade(Mathf.Lerp(start, target, Mathf.Clamp(t / duration, 0f, 1f)));
        }
        SetFade(target);
    }

    private async Task TintTo(CinematicStep step)
    {
        if (!CinematicColors.TryParse(step.Value, out float r, out float g, out float b)) return;
        var from = _room.Tint;
        var to = new Color(r, g, b);
        float t = 0f;
        while (t < step.Seconds && !_skip)
        {
            await NextFrame();
            t += (float)GetProcessDeltaTime();
            _room.SetTint(from.Lerp(to, Mathf.Clamp(t / step.Seconds, 0f, 1f)));
        }
        _room.SetTint(to);
    }

    private void EnsureCineCamera()
    {
        if (_cineCam != null) return;
        _playerCam = _player.GetNodeOrNull<Camera2D>("Camera2D");
        if (_playerCam == null) return;
        _cineCam = new CameraShake
        {
            Name = "CameraCinematique",
            PositionSmoothingEnabled = false,
            LimitLeft = _playerCam.LimitLeft,
            LimitTop = _playerCam.LimitTop,
            LimitRight = _playerCam.LimitRight,
            LimitBottom = _playerCam.LimitBottom,
        };
        _room.AddChild(_cineCam);
        _cineCam.GlobalPosition = _playerCam.GetScreenCenterPosition();
        _cineCam.MakeCurrent();
    }

    private void ReleaseCamera()
    {
        if (_cineCam == null) return;
        if (IsInstanceValid(_playerCam))
        {
            _playerCam.MakeCurrent();
            _playerCam.ResetSmoothing();
        }
        _cineCam.QueueFree();
        _cineCam = null;
    }

    // Caméra : glisse vers un repère (ou revient sur Brann). La caméra du joueur reprend la main à la fin du retour.
    private async Task MoveCamera(CinematicStep step)
    {
        bool toBrann = step.Target == "brann";
        Vector2 target = Vector2.Zero;
        if (!toBrann && !ResolveTarget(step, out target)) return;
        EnsureCineCamera();
        if (_cineCam == null) return;
        var from = _cineCam.GlobalPosition;
        float t = 0f;
        while (t < step.Seconds && !_skip)
        {
            await NextFrame();
            t += (float)GetProcessDeltaTime();
            var end = toBrann ? _player.GlobalPosition : target;
            _cineCam.GlobalPosition = from.Lerp(end, Mathf.SmoothStep(0f, 1f, Mathf.Clamp(t / step.Seconds, 0f, 1f)));
        }
        ApplyFinal(step, false);
    }

    // --- Attente ----------------------------------------------------------------------------------

    private async Task Wait(float seconds)
    {
        float t = 0f;
        while (t < seconds && !_skip)
        {
            await NextFrame();
            t += (float)GetProcessDeltaTime();
        }
    }

    // Image suivante. Utilise l'arbre mémorisé (pas GetTree(), qui serait null si la salle a quitté l'arbre) et abandonne la lecture si la salle est partie.
    private async Task NextFrame()
    {
        await _tree.ToSignal(_tree, SceneTree.SignalName.ProcessFrame);
        if (!IsInstanceValid(this) || !IsInsideTree()) throw new OperationCanceledException();
    }

    // --- Indication « maintenir pour passer » -----------------------------------------------------

    private void ShowHint(bool skippable)
    {
        if (!skippable) return;
        if (_hintLayer == null)
        {
            var theme = GD.Load<Theme>(ThemePath);
            _hintLayer = new CanvasLayer { Name = "IndicationPasser", Layer = 7 };
            _hintLabel = new Label
            {
                Text = Tr("CINE_SKIP"),
                Position = new Vector2(320f, 330f),
                Size = new Vector2(312f, 14f),
                HorizontalAlignment = HorizontalAlignment.Right,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                Modulate = new Color(1f, 1f, 1f, 0.6f),
            };
            if (theme != null) _hintLabel.Theme = theme;
            _hintBarBack = new ColorRect { Color = new Color(0f, 0f, 0f, 0.5f), Position = new Vector2(512f, 346f), Size = new Vector2(120f, 4f), Visible = false, MouseFilter = Control.MouseFilterEnum.Ignore };
            _hintBar = new ColorRect { Color = new Color(0.95f, 0.9f, 0.7f), Position = new Vector2(512f, 346f), Size = new Vector2(0f, 4f), Visible = false, MouseFilter = Control.MouseFilterEnum.Ignore };
            _hintLayer.AddChild(_hintLabel);
            _hintLayer.AddChild(_hintBarBack);
            _hintLayer.AddChild(_hintBar);
            AddChild(_hintLayer);
        }
        _hintLabel.Text = Tr("CINE_SKIP");
        _hintLayer.Visible = true;
        _hintBar.Visible = _hintBarBack.Visible = false;
    }

    private void UpdateHint()
    {
        if (_hintBar == null) return;
        bool holding = _hold > 0.02f;
        _hintBar.Visible = _hintBarBack.Visible = holding;
        if (holding) _hintBar.Size = new Vector2(120f * Mathf.Clamp(_hold / SkipHoldSeconds, 0f, 1f), 4f);
    }

    private void HideHint()
    {
        if (_hintLayer != null) _hintLayer.Visible = false;
    }
}
