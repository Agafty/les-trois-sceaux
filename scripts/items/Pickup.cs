using Godot;

/// <summary>
/// Ramassable générique (rubis, cœur...) : apparaît avec un petit rebond, ne peut pas être
/// ramassé tout de suite, clignote puis disparaît s'il traîne trop longtemps.
/// </summary>
public partial class Pickup : Area2D
{
    public enum PickupType { Rubis, Coeur }

    [Export] public PickupType Type { get; set; } = PickupType.Rubis;

    /// <summary>Rubis : valeur ajoutée à la bourse. Cœur : PV rendus (1 cœur = 2 PV).</summary>
    [Export] public int Amount { get; set; } = 1;

    [Export] public float PickupDelay { get; set; } = 0.3f;
    [Export] public float Lifetime { get; set; } = 8f;
    [Export] public float BlinkDuration { get; set; } = 2f;
    [Export] public float BlinkInterval { get; set; } = 0.1f;
    [Export] public float BounceHeight { get; set; } = 14f;

    private static readonly StringName PlayerGroup = "player";

    private AnimatedSprite2D _sprite;
    private Node2D _playerInside;
    private float _age;
    private float _blinkTimer;
    private bool _collected;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        BodyEntered += OnBodyEntered;
        BodyExited += OnBodyExited;

        // Rebond à l'apparition : le sprite monte puis retombe en rebondissant.
        _sprite.Position = new Vector2(0f, -BounceHeight);
        var tween = CreateTween();
        tween.TweenProperty(_sprite, "position", Vector2.Zero, 0.4)
            .SetTrans(Tween.TransitionType.Bounce)
            .SetEase(Tween.EaseType.Out);
    }

    public override void _ExitTree()
    {
        BodyEntered -= OnBodyEntered;
        BodyExited -= OnBodyExited;
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

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(PlayerGroup)) return;
        _playerInside = body;
    }

    private void OnBodyExited(Node2D body)
    {
        if (body == _playerInside) _playerInside = null;
    }

    // Un cœur reste au sol tant que le joueur a toute sa vie.
    private bool CanCollect(Node2D player)
    {
        if (Type != PickupType.Coeur) return true;
        var health = player.GetNodeOrNull<Health>("Health");
        return health != null && health.CurrentHealth > 0 && health.CurrentHealth < health.MaxHealth;
    }

    private void Collect(Node2D player)
    {
        _collected = true;
        switch (Type)
        {
            case PickupType.Rubis:
                GetNode<GameState>("/root/GameState").AddRupees(Amount);
                break;
            case PickupType.Coeur:
                player.GetNodeOrNull<Health>("Health")?.Heal(Amount);
                break;
        }
        QueueFree();
    }
}
