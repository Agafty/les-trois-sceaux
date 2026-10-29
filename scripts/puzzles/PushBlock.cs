using System.Collections.Generic;
using Godot;

/// <summary>
/// Bloc poussable : un bloc solide de 32x32 aligné sur la grille. Quand Brann pousse vers lui pendant
/// <see cref="PushDuration"/> secondes, il glisse d'une case (tween) si la case suivante est libre
/// (test physique : mur, autre bloc, coffre, ennemi, porte fermée... arrêtent). Il n'est pas tirable.
/// Rien n'est sauvegardé : la salle est rechargée depuis la carte, le bloc revient donc à sa position Tiled.
/// </summary>
public partial class PushBlock : AnimatableBody2D
{
    /// <summary>Le bloc vient de finir de glisser d'une case.</summary>
    [Signal]
    public delegate void MovedEventHandler();

    /// <summary>Durée (s) pendant laquelle Brann doit pousser vers le bloc avant qu'il bouge.</summary>
    [Export(PropertyHint.Range, "0.05,1,0.05")] public float PushDuration { get; set; } = 0.3f;

    /// <summary>Durée (s) du glissement d'une case.</summary>
    [Export(PropertyHint.Range, "0.05,1,0.05")] public float SlideDuration { get; set; } = 0.25f;

    /// <summary>Côté d'une case (px).</summary>
    [Export(PropertyHint.Range, "8,128,1")] public float CellSize { get; set; } = 32f;

    /// <summary>Écart latéral maximal (px) entre Brann et l'axe du bloc pour le pousser.</summary>
    [Export(PropertyHint.Range, "0,32,1")] public float LateralTolerance { get; set; } = 12f;

    /// <summary>Côté (px) du carré testé dans la case suivante : un peu moins qu'une case pour ne pas toucher les murs voisins.</summary>
    [Export(PropertyHint.Range, "8,32,1")] public float FreeCheckSize { get; set; } = 28f;

    public bool IsSliding => _sliding;

    /// <summary>
    /// Cases (colonne, ligne) où le bloc refuse de glisser : Spawn, Sortie, Porte et leurs 8 voisines. Réglé par la <see cref="Room"/> ;
    /// null (bloc posé à la main dans une scène de test) = aucune restriction.
    /// </summary>
    public HashSet<(int, int)> ForbiddenCells { get; set; }

    /// <summary>
    /// Apparence (propriété Tiled « apparence » de BlocPoussable) : vide = art/puzzles/bloc_poussable.png ; sinon art/puzzles/bloc_&lt;apparence&gt;.png
    /// (ex. « mine » pour le wagonnet de minerai). Réglé par la <see cref="Room"/> avant l'ajout à l'arbre.
    /// </summary>
    public string Appearance { get; set; } = "";

    private const int FrameSize = 32;
    private const string DefaultTexturePath = "res://art/puzzles/bloc_poussable.png";
    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName MoveLeft = "move_left";
    private static readonly StringName MoveRight = "move_right";
    private static readonly StringName MoveUp = "move_up";
    private static readonly StringName MoveDown = "move_down";
    private const float MinPushDot = 0.6f;

    private static Texture2D _placeholder;
    private static readonly HashSet<string> _warnedAppearances = new();

    private Area2D _contact;
    private Player _player;
    private float _pushTime;
    private bool _sliding;
    private Vector2 _slideStart;
    private Vector2 _slideTarget;
    private PhysicsShapeQueryParameters2D _query;
    private RectangleShape2D _checkShape;

    public override void _Ready()
    {
        SetPhysicsProcess(false); // activé seulement quand Brann touche le bloc
        _contact = GetNode<Area2D>("ZoneContact");
        _contact.BodyEntered += OnBodyEntered;
        _contact.BodyExited += OnBodyExited;

        // Requête physique réutilisée à chaque poussée (pas de new à répétition).
        _checkShape = new RectangleShape2D { Size = new Vector2(FreeCheckSize, FreeCheckSize) };
        _query = new PhysicsShapeQueryParameters2D
        {
            Shape = _checkShape,
            CollisionMask = uint.MaxValue,
            CollideWithBodies = true,
            CollideWithAreas = false,
        };
        _query.Exclude = new Godot.Collections.Array<Rid> { GetRid() };

        SetupSprite();
        // Aligne sur la grille au cas où la carte l'aurait posé à côté du centre de case.
        GlobalPosition = new Vector2(
            PushBlockRules.SnapToCellCenter(GlobalPosition.X, CellSize),
            PushBlockRules.SnapToCellCenter(GlobalPosition.Y, CellSize));
    }

    public override void _ExitTree()
    {
        if (_contact != null)
        {
            _contact.BodyEntered -= OnBodyEntered;
            _contact.BodyExited -= OnBodyExited;
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_player == null) return;
        if (!IsInstanceValid(_player))
        {
            _player = null;
            SetPhysicsProcess(false);
            return;
        }
        if (_sliding || _player.IsDead || !_player.CanInteract)
        {
            _pushTime = 0f;
            return;
        }

        var input = Input.GetVector(MoveLeft, MoveRight, MoveUp, MoveDown);
        var toBlock = GlobalPosition - (_player.GlobalPosition + Player.FeetOffset);
        if (input.LengthSquared() < 0.25f
            || !PushBlockRules.TryGetPushDirection(toBlock.X, toBlock.Y, LateralTolerance, out int dirX, out int dirY))
        {
            _pushTime = 0f;
            return;
        }

        var direction = new Vector2(dirX, dirY);
        if (input.Normalized().Dot(direction) < MinPushDot)
        {
            _pushTime = 0f;
            return;
        }

        _pushTime += (float)delta;
        if (_pushTime >= PushDuration)
        {
            _pushTime = 0f;
            TrySlide(direction);
        }
    }

    /// <summary>Fait glisser le bloc d'une case dans la direction donnée si la case est libre. Renvoie vrai s'il part.</summary>
    public bool TrySlide(Vector2 direction)
    {
        if (_sliding) return false;
        var target = GlobalPosition + direction * CellSize;
        if (ForbiddenCells != null
            && ForbiddenCells.Contains((PushBlockRules.CellIndex(target.X, CellSize), PushBlockRules.CellIndex(target.Y, CellSize))))
            return false;
        if (!IsCellFree(target)) return false;

        _sliding = true;
        AudioManager.PlayAt(Sfx.BlocPousse, GlobalPosition);
        _slideStart = GlobalPosition;
        _slideTarget = target;
        // Première moitié, puis nouveau test : si la case est devenue occupée, le bloc revient au lieu d'écraser.
        var tween = CreateTween();
        tween.SetProcessMode(Tween.TweenProcessMode.Physics);
        tween.TweenProperty(this, "global_position", _slideStart.Lerp(target, 0.5f), SlideDuration * 0.5f);
        tween.TweenCallback(Callable.From(OnSlideMidway));
        return true;
    }

    private void OnSlideMidway()
    {
        var tween = CreateTween();
        tween.SetProcessMode(Tween.TweenProcessMode.Physics);
        if (IsCellFree(_slideTarget))
        {
            tween.TweenProperty(this, "global_position", _slideTarget, SlideDuration * 0.5f);
            tween.TweenCallback(Callable.From(OnSlideFinished));
        }
        else
        {
            tween.TweenProperty(this, "global_position", _slideStart, SlideDuration * 0.5f);
            tween.TweenCallback(Callable.From(OnSlideReverted));
        }
    }

    private void OnSlideReverted() => _sliding = false;

    private void OnSlideFinished()
    {
        _sliding = false;
        EmitSignal(SignalName.Moved);
    }

    // Test physique : un carré un peu plus petit qu'une case, au centre de la case visée, touche-t-il un corps ?
    private bool IsCellFree(Vector2 center)
    {
        _query.Transform = new Transform2D(0f, center);
        var hits = GetWorld2D().DirectSpaceState.IntersectShape(_query, 1);
        return hits.Count == 0;
    }

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(PlayerGroup) || body is not Player player) return;
        _player = player;
        _pushTime = 0f;
        SetPhysicsProcess(true);
    }

    private void OnBodyExited(Node2D body)
    {
        if (body != _player) return;
        _player = null;
        _pushTime = 0f;
        SetPhysicsProcess(false);
    }

    // Image du graphiste art/puzzles/bloc_poussable.png (32x32) ou, à défaut, un placeholder dessiné par le code.
    private void SetupSprite()
    {
        var sprite = GetNode<Sprite2D>("Sprite2D");
        string path = DefaultTexturePath;
        if (!string.IsNullOrEmpty(Appearance))
        {
            string custom = $"res://art/puzzles/bloc_{Appearance}.png";
            if (RoomObjectCatalog.IsSafeName(Appearance) && ResourceLoader.Exists(custom))
                path = custom;
            else if (_warnedAppearances.Add(Appearance))
                GD.PushWarning($"Bloc poussable : apparence « {Appearance} » invalide ou image {custom} introuvable, image par défaut utilisée.");
        }
        if (path == DefaultTexturePath && ResourceLoader.Exists(path) || path != DefaultTexturePath)
        {
            sprite.Texture = GD.Load<Texture2D>(path);
            return;
        }
        _placeholder ??= BuildPlaceholder();
        sprite.Texture = _placeholder;
    }

    private static Texture2D BuildPlaceholder()
    {
        var dark = new Color(0.12f, 0.1f, 0.16f);
        var stone = new Color(0.52f, 0.5f, 0.58f);
        var light = new Color(0.68f, 0.66f, 0.74f);
        var image = Image.CreateEmpty(FrameSize, FrameSize, false, Image.Format.Rgba8);
        image.Fill(dark);
        image.FillRect(new Rect2I(2, 2, FrameSize - 4, FrameSize - 4), stone);
        image.FillRect(new Rect2I(3, 3, FrameSize - 6, 3), light);
        image.FillRect(new Rect2I(3, 3, 3, FrameSize - 6), light);
        image.FillRect(new Rect2I(10, 10, 12, 12), dark);
        image.FillRect(new Rect2I(11, 11, 10, 10), stone);
        return ImageTexture.CreateFromImage(image);
    }
}
