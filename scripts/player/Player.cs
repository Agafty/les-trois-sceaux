using Godot;

public partial class Player : CharacterBody2D
{
    private enum Direction { Bas, Haut, Gauche, Droite }
    private enum State { Deplacement, Attaque, Touche }

    [Export]
    public float Speed { get; set; } = 100f;

    [Export]
    public float AttackDuration { get; set; } = 0.2f;

    [Export]
    public float HurtDuration { get; set; } = 0.2f;

    [Export]
    public float InvincibleDuration { get; set; } = 1.0f;

    [Export]
    public float BlinkInterval { get; set; } = 0.08f;

    [Export]
    public float KnockbackSpeed { get; set; } = 200f;

    [Export]
    public float KnockbackFriction { get; set; } = 600f;

    private Direction _facing = Direction.Bas;
    private State _state = State.Deplacement;
    private float _attackTimer;
    private float _hurtTimer;
    private float _invincibleTimer;
    private float _blinkTimer;
    private Vector2 _knockbackVelocity;

    private AnimatedSprite2D _sprite;
    private AnimatedSprite2D _swordSprite;
    private HitBox _swordHitBox;
    private Health _health;
    private HurtBox _hurtBox;

    public override void _Ready()
    {
        AddToGroup("player");
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _swordSprite = GetNode<AnimatedSprite2D>("SwordSlash");
        _swordHitBox = GetNode<HitBox>("SwordSlash/HitBox");
        _health = GetNode<Health>("Health");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.Hit += OnHit;
    }

    private void OnHit(int amount, Vector2 fromPosition)
    {
        _state = State.Touche;
        _hurtTimer = HurtDuration;
        _invincibleTimer = InvincibleDuration;
        _blinkTimer = BlinkInterval;
        _hurtBox.Invincible = true;

        _knockbackVelocity = (GlobalPosition - fromPosition).Normalized() * KnockbackSpeed;

        _swordSprite.Visible = false;
        _swordHitBox.Monitoring = false;

        string anim = _facing switch
        {
            Direction.Bas => "hurt_down",
            Direction.Haut => "hurt_up",
            Direction.Gauche => "hurt_left",
            Direction.Droite => "hurt_right",
            _ => "hurt_down",
        };
        _sprite.Play(anim);
        GD.Print($"Brann touché (-{amount}) : {_health.CurrentHealth}/{_health.MaxHealth} PV");
    }

    public override void _PhysicsProcess(double delta)
    {
        UpdateInvincibility((float)delta);

        if (_state == State.Attaque)
        {
            ProcessAttack((float)delta);
            return;
        }

        if (_state == State.Touche)
        {
            ProcessHurt((float)delta);
            return;
        }

        var input = Vector2.Zero;
        if (Input.IsActionPressed("move_right")) input.X += 1;
        if (Input.IsActionPressed("move_left")) input.X -= 1;
        if (Input.IsActionPressed("move_down")) input.Y += 1;
        if (Input.IsActionPressed("move_up")) input.Y -= 1;

        Velocity = input != Vector2.Zero ? input.Normalized() * Speed : Vector2.Zero;
        MoveAndSlide();

        UpdateFacing(input);
        UpdateAnimation(input != Vector2.Zero);

        if (Input.IsActionJustPressed("attack"))
            StartAttack();
    }

    private void UpdateFacing(Vector2 input)
    {
        if (input == Vector2.Zero) return;

        if (Mathf.Abs(input.X) > Mathf.Abs(input.Y))
            _facing = input.X > 0 ? Direction.Droite : Direction.Gauche;
        else
            _facing = input.Y > 0 ? Direction.Bas : Direction.Haut;
    }

    private void UpdateAnimation(bool moving)
    {
        string anim = (moving, _facing) switch
        {
            (true, Direction.Bas) => "walk_down",
            (true, Direction.Haut) => "walk_up",
            (true, Direction.Gauche) => "walk_left",
            (true, Direction.Droite) => "walk_right",
            (false, Direction.Bas) => "idle_down",
            (false, Direction.Haut) => "idle_up",
            (false, Direction.Gauche) => "idle_left",
            (false, Direction.Droite) => "idle_right",
            _ => "idle_down",
        };
        _sprite.Play(anim);
    }

    private void StartAttack()
    {
        _state = State.Attaque;
        _attackTimer = AttackDuration;
        Velocity = Vector2.Zero;

        var (animBody, animSlash, slashOffset) = _facing switch
        {
            Direction.Bas => ("attack_down", "slash_down", new Vector2(0, 16)),
            Direction.Haut => ("attack_up", "slash_up", new Vector2(0, -16)),
            Direction.Gauche => ("attack_left", "slash_left", new Vector2(-16, 0)),
            Direction.Droite => ("attack_right", "slash_right", new Vector2(16, 0)),
            _ => ("attack_down", "slash_down", new Vector2(0, 16)),
        };

        _sprite.Play(animBody);
        _swordSprite.Play(animSlash);
        _swordSprite.Position = slashOffset;
        _swordSprite.Visible = true;
        _swordHitBox.Monitoring = true;
    }

    private void ProcessAttack(float delta)
    {
        _attackTimer -= delta;
        if (_attackTimer > 0f) return;

        _state = State.Deplacement;
        _swordSprite.Visible = false;
        _swordHitBox.Monitoring = false;
    }

    private void ProcessHurt(float delta)
    {
        Velocity = _knockbackVelocity;
        MoveAndSlide();
        _knockbackVelocity = _knockbackVelocity.MoveToward(Vector2.Zero, KnockbackFriction * delta);

        _hurtTimer -= delta;
        if (_hurtTimer > 0f) return;

        _state = State.Deplacement;
    }

    private void UpdateInvincibility(float delta)
    {
        if (_invincibleTimer <= 0f) return;

        _invincibleTimer -= delta;
        _blinkTimer -= delta;
        if (_blinkTimer <= 0f)
        {
            _blinkTimer = BlinkInterval;
            _sprite.Visible = !_sprite.Visible;
        }

        if (_invincibleTimer <= 0f)
        {
            _sprite.Visible = true;
            _hurtBox.Invincible = false;
        }
    }
}
