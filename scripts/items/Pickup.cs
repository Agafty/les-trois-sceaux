using Godot;

/// <summary>
/// Ramassable générique (rubis, cœur...) : apparaît avec un petit rebond, ne peut pas être
/// ramassé tout de suite, clignote puis disparaît s'il traîne trop longtemps.
/// </summary>
public partial class Pickup : Area2D
{
    /// <summary>
    /// Identifiant unique (ex. "donjon1_quart_01"). Non vide : objet permanent (ni durée de vie,
    /// ni rebond), mémorisé dans GameState une fois ramassé et absent s'il l'a déjà été.
    /// </summary>
    [Export] public string UniqueId { get; set; } = "";

    /// <summary>Ce que fait le ramassable (rubis, soin, clé...). Données dans resources/pickups/.</summary>
    [Export] public PickupEffect Effect { get; set; }

    [Export] public float PickupDelay { get; set; } = 0.3f;
    [Export] public float Lifetime { get; set; } = 8f;
    [Export] public float BlinkDuration { get; set; } = 2f;
    [Export] public float BlinkInterval { get; set; } = 0.1f;
    [Export] public float BounceHeight { get; set; } = 14f;

    private static readonly StringName PlayerGroup = "player";

    private AnimatedSprite2D _sprite;
    private Player _playerInside;
    private GameState _state;
    private float _age;
    private float _blinkTimer;
    private bool _collected;

    public override void _Ready()
    {
        _state = GetNode<GameState>("/root/GameState");
        if (IsUnique && _state.IsCollected(UniqueId))
        {
            _collected = true;
            QueueFree();
            return;
        }

        if (Effect == null)
            GD.PushWarning($"{Name} ({SceneFilePath}) : aucun Effect, l'objet ne pourra pas être ramassé.");

        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        BodyEntered += OnBodyEntered;
        BodyExited += OnBodyExited;

        if (IsUnique) return; // pas de rebond d'apparition

        // Rebond à l'apparition : le sprite monte puis retombe en rebondissant.
        _sprite.Position = new Vector2(0f, -BounceHeight);
        var tween = CreateTween();
        tween.TweenProperty(_sprite, "position", Vector2.Zero, 0.4)
            .SetTrans(Tween.TransitionType.Bounce)
            .SetEase(Tween.EaseType.Out);
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_collected) return;
        float dt = (float)delta;
        _age += dt;

        // Le joueur était déjà dessus quand le délai s'est terminé : on le ramasse maintenant.
        if (_age >= PickupDelay && _playerInside != null)
        {
            if (!IsInstanceValid(_playerInside))
                _playerInside = null;
            else if (CanCollect(_playerInside))
            {
                Collect(_playerInside);
                return;
            }
        }

        if (IsUnique) return; // ne disparaît jamais tout seul

        float remaining = Lifetime - _age;
        if (remaining <= 0f)
        {
            _collected = true;
            QueueFree();
            return;
        }

        if (remaining <= BlinkDuration)
        {
            _blinkTimer -= dt;
            if (_blinkTimer <= 0f)
            {
                _blinkTimer = BlinkInterval;
                _sprite.Visible = !_sprite.Visible;
            }
        }
    }

    private bool IsUnique => !string.IsNullOrEmpty(UniqueId);

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(PlayerGroup) || body is not Player player) return;
        _playerInside = player;
    }

    private void OnBodyExited(Node2D body)
    {
        if (body == _playerInside) _playerInside = null;
    }

    // Rien n'est ramassé par un joueur mort ; sinon l'effet décide (ex. cœur refusé à vie pleine).
    private bool CanCollect(Player player)
    {
        if (Effect == null || player.IsDead) return false;
        return Effect.CanApply(player, _state);
    }

    private void Collect(Player player)
    {
        _collected = true;
        Effect.Apply(player, _state);
        if (IsUnique)
            _state.MarkCollected(UniqueId);
        QueueFree();
    }
}
