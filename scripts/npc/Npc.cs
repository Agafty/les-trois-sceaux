using Godot;

/// <summary>
/// Personnage non joueur : un CharacterBody2D immobile (ou qui flâne autour de sa case si <see cref="WanderRadius"/> &gt; 0) qui parle
/// quand Brann est en face et appuie sur « interact ». Son origine est le centre de son sprite, comme Brann (tri en profondeur cohérent).
/// - <see cref="Id"/> : nom du fichier de dialogues resources/dialogues/&lt;id&gt;.json (clé de ses dialogues).
/// - <see cref="SpriteName"/> : planche art/characters/&lt;sprite&gt;_frames.tres (par défaut l'Id).
/// Le texte dit dépend de l'étape d'histoire (GameState.StoryStage) et des flags (voir DialogueSelector). Pendant la conversation le jeu est en pause.
/// </summary>
public partial class Npc : CharacterBody2D
{
    [Export] public string Id { get; set; } = "";

    /// <summary>Nom de la planche d'animation (art/characters/&lt;nom&gt;_frames.tres). Vide : l'Id.</summary>
    [Export] public string SpriteName { get; set; } = "";

    /// <summary>Direction du regard au départ : down, up, left ou right.</summary>
    [Export] public string InitialDirection { get; set; } = "down";

    /// <summary>Rayon (px) de la petite errance autour de la case de départ. 0 = immobile.</summary>
    [Export(PropertyHint.Range, "0,128,1")] public float WanderRadius { get; set; }

    [Export(PropertyHint.Range, "10,80,1")] public float WanderSpeed { get; set; } = 28f;

    private static readonly StringName[] IdleAnims = { "idle_down", "idle_up", "idle_left", "idle_right" };
    private static readonly StringName[] WalkAnims = { "walk_down", "walk_up", "walk_left", "walk_right" };
    private const string FramesFolder = "res://art/characters/";

    private AnimatedSprite2D _sprite;
    private InteractionZone _zone;
    private GameState _state;
    private DialogueBox _box;
    private int _facing; // 0 bas, 1 haut, 2 gauche, 3 droite
    private int _talkCount;
    private bool _warnedMute;
    private Vector2 _home;
    private Vector2 _target;
    private float _wanderTimer;
    private float _walkTime;
    private bool _walking;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _zone = GetNode<InteractionZone>("ZoneInteraction");
        _state = GetNode<GameState>("/root/GameState");
        _home = GlobalPosition;
        _facing = ParseDirection(InitialDirection);

        string name = string.IsNullOrEmpty(SpriteName) ? Id : SpriteName;
        string path = $"{FramesFolder}{name}_frames.tres";
        if (RoomObjectCatalog.IsSafeName(name) && ResourceLoader.Exists(path))
            _sprite.SpriteFrames = GD.Load<SpriteFrames>(path);
        else
            GD.PushWarning($"PNJ « {Id} » : planche {path} introuvable, le sprite reste vide.");
        PlayIdle();

        if (string.IsNullOrEmpty(Id))
            GD.PushWarning($"PNJ sans Id ({GetPath()}) : il ne dira rien.");
        _zone.Interacted += OnInteracted;
        SetPhysicsProcess(WanderRadius > 0f);
        _wanderTimer = 1f + GD.Randf() * 2f;
    }

    public override void _ExitTree()
    {
        if (_zone != null) _zone.Interacted -= OnInteracted;
        if (_box != null && IsInstanceValid(_box)) _box.Finished -= OnDialogueFinished;
    }

    // --- Dialogue ---------------------------------------------------------------------------------

    /// <summary>Lignes (déjà traduites) que ce PNJ dirait maintenant ; vide s'il n'a rien à dire. Public pour les tests.</summary>
    public string[] BuildLines(out string speaker)
    {
        speaker = "";
        var data = DialogueLibrary.Get(Id);
        if (data == null) return System.Array.Empty<string>();
        var entry = DialogueSelector.Pick(data, _state.StoryStage, _state.IsCollected);
        var keys = DialogueSelector.GetLines(entry, _talkCount);
        speaker = string.IsNullOrEmpty(data.Speaker) ? "" : Tr(data.Speaker);
        var lines = new string[keys.Count];
        for (int i = 0; i < keys.Count; i++)
            lines[i] = Tr(keys[i]);
        return lines;
    }

    private void OnInteracted(Player player)
    {
        if (_box != null && IsInstanceValid(_box)) return;
        var lines = BuildLines(out string speaker);
        if (lines.Length == 0)
        {
            if (!_warnedMute)
            {
                _warnedMute = true;
                GD.PushWarning($"PNJ « {Id} » : aucun dialogue pour l'étape {_state.StoryStage}.");
            }
            return;
        }
        _talkCount++;
        _walking = false;
        Velocity = Vector2.Zero;
        FaceTowards(player.GlobalPosition - GlobalPosition);
        PlayIdle();
        SetPhysicsProcess(false);
        _box = DialogueBox.OpenModal(this, speaker, lines);
        _box.Finished += OnDialogueFinished;
    }

    private void OnDialogueFinished(int choice)
    {
        _box = null;
        _zone.BlockFor(0.3f);
        SetPhysicsProcess(WanderRadius > 0f);
    }

    // --- Errance (facultative) --------------------------------------------------------------------

    public override void _PhysicsProcess(double delta)
    {
        float dt = (float)delta;
        if (_walking)
        {
            _walkTime += dt;
            var toTarget = _target - GlobalPosition;
            if (toTarget.LengthSquared() < 4f || _walkTime > 4f)
            {
                StopWalking();
                return;
            }
            Velocity = toTarget.Normalized() * WanderSpeed;
            MoveAndSlide();
            if (GetSlideCollisionCount() > 0) StopWalking(); // s'arrête contre un obstacle
            return;
        }

        _wanderTimer -= dt;
        if (_wanderTimer > 0f) return;
        float angle = GD.Randf() * Mathf.Tau;
        _target = _home + new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * (WanderRadius * GD.Randf());
        _walking = true;
        _walkTime = 0f;
        FaceTowards(_target - GlobalPosition);
        _sprite.Play(WalkAnims[_facing]);
    }

    private void StopWalking()
    {
        _walking = false;
        Velocity = Vector2.Zero;
        _wanderTimer = 1.5f + GD.Randf() * 3f;
        PlayIdle();
    }

    // --- Orientation ------------------------------------------------------------------------------

    private void FaceTowards(Vector2 direction)
    {
        if (direction.LengthSquared() < 0.01f) return;
        _facing = Mathf.Abs(direction.X) > Mathf.Abs(direction.Y)
            ? (direction.X < 0f ? 2 : 3)
            : (direction.Y < 0f ? 1 : 0);
    }

    private void PlayIdle()
    {
        if (_sprite?.SpriteFrames != null && _sprite.SpriteFrames.HasAnimation(IdleAnims[_facing]))
            _sprite.Play(IdleAnims[_facing]);
    }

    private static int ParseDirection(string value) => value switch
    {
        "up" => 1,
        "left" => 2,
        "right" => 3,
        _ => 0,
    };
}
