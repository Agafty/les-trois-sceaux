using Godot;

/// <summary>
/// Ramassable générique (rubis, cœur...) : apparaît avec un petit rebond, ne peut pas être
/// ramassé tout de suite, clignote puis disparaît s'il traîne trop longtemps.
/// </summary>
public partial class Pickup : Area2D
{
    // Ajouter les nouvelles valeurs à la fin : les scènes enregistrent l'entier.
    public enum PickupType { Rubis, Coeur, Receptacle, QuartCoeur }

    /// <summary>
    /// Identifiant unique (ex. "donjon1_quart_01"). Non vide : objet permanent (ni durée de vie,
    /// ni rebond), mémorisé dans GameState une fois ramassé et absent s'il l'a déjà été.
    /// </summary>
    [Export] public string UniqueId { get; set; } = "";

    [Export] public PickupType Type { get; set; } = PickupType.Rubis;

    /// <summary>
    /// Rubis : valeur ajoutée à la bourse. Cœur : PV rendus (1 cœur = 2 PV).
    /// Réceptacle / quart de cœur complété : PV max ajoutés (2 = un cœur).
    /// </summary>
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
        if (IsUnique && GetNode<GameState>("/root/GameState").IsCollected(UniqueId))
        {
            _collected = true;
            QueueFree();
            return;
        }

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
        if (!body.IsInGroup(PlayerGroup)) return;
        _playerInside = body;
    }

    private void OnBodyExited(Node2D body)
    {
        if (body == _playerInside) _playerInside = null;
    }

    // Rien n'est ramassé par un joueur mort. Un cœur reste au sol à vie pleine ;
    // un réceptacle ou un quart reste au sol quand la vie max est au plafond.
    private bool CanCollect(Node2D player)
    {
        if (player is Player { IsDead: true }) return false;
        switch (Type)
        {
            case PickupType.Coeur:
            {
                var health = player.GetNodeOrNull<Health>("Health");
                return health != null && health.CurrentHealth > 0 && health.CurrentHealth < health.MaxHealth;
            }
            case PickupType.Receptacle:
            case PickupType.QuartCoeur:
            {
                var health = player.GetNodeOrNull<Health>("Health");
                return health != null && health.CurrentHealth > 0 && health.MaxHealth < Health.MaxHealthCap;
            }
            default:
                return true;
        }
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
            case PickupType.Receptacle:
                player.GetNodeOrNull<Health>("Health")?.IncreaseMax(Amount, true);
                break;
            case PickupType.QuartCoeur:
                if (GetNode<GameState>("/root/GameState").AddHeartPiece())
                    player.GetNodeOrNull<Health>("Health")?.IncreaseMax(Amount, true);
                break;
        }
        if (IsUnique)
            GetNode<GameState>("/root/GameState").MarkCollected(UniqueId);
        QueueFree();
    }
}
