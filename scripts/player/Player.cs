using Godot;

public partial class Player : CharacterBody2D
{
    private enum Direction { Bas, Haut, Gauche, Droite }
    private enum State { Deplacement, Attaque, Touche, Mort }

    private static readonly StringName DeathAnim = "death";
    private static readonly StringName LiftAnim = "lift";

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

    [Export]
    public float RespawnDelay { get; set; } = 1.0f;

    /// <summary>Distance (px) à laquelle un objet utilisé est posé devant Brann, depuis ses pieds.</summary>
    [Export]
    public float UseDistance { get; set; } = 24f;

    /// <summary>Recul (px) du point de pose par rapport au mur quand un objet est posé contre lui.</summary>
    private const float WallPoseMargin = 4f;

    private Direction _facing = Direction.Bas;
    private State _state = State.Deplacement;
    private float _attackTimer;
    private float _hurtTimer;
    private float _invincibleTimer;
    private float _blinkTimer;
    private Vector2 _knockbackVelocity;
    private float _respawnTimer = -1f;
    private SceneManager _sceneManager;
    private GameState _gameState;

    public bool IsDead => _state == State.Mort;

    /// <summary>Vie du joueur (lecture seule), utilisée par les effets de ramassables.</summary>
    public Health Health => _health;

    private AnimatedSprite2D _sprite;
    private AnimatedSprite2D _swordSprite;
    private HitBox _swordHitBox;
    private Health _health;
    private HurtBox _hurtBox;

    public override void _Ready()
    {
        AddToGroup("player");
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _swordSprite = GetNode<AnimatedSprite2D>("SwordSlash");
        _swordHitBox = GetNode<HitBox>("SwordSlash/HitBox");
        _health = GetNode<Health>("Health");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _gameState = GetNode<GameState>("/root/GameState");
        // Les _Ready des enfants passent avant celui du parent : Health a déjà fait son init par défaut.
        _health.SetValues(_gameState.PlayerHealth, _gameState.PlayerMaxHealth);
        _health.HealthChanged += OnHealthChanged;
        _hurtBox.Hit += OnHit;
        _health.Died += OnDied;
        _sprite.AnimationFinished += OnAnimationFinished;
    }

    public override void _ExitTree()
    {
        if (_hurtBox != null) _hurtBox.Hit -= OnHit;
        if (_health != null) _health.Died -= OnDied;
        if (_health != null) _health.HealthChanged -= OnHealthChanged;
        if (_sprite != null) _sprite.AnimationFinished -= OnAnimationFinished;
    }

    // Sens unique : Health -> GameState -> HUD. GameState n'écrit jamais dans Health.
    private void OnHealthChanged(int current, int max)
    {
        _gameState.SetPlayerHealth(current, max);
    }

    // Health.Died arrive AVANT HurtBox.Hit (ReceiveHit : Damage puis Hit).
    private void OnDied()
    {
        _state = State.Mort;
        // HealthChanged(0) vient d'être recopié dans GameState ; on y remet la vie de reprise sans signal.
        _gameState.PrepareRespawn();
        Velocity = Vector2.Zero;
        _knockbackVelocity = Vector2.Zero;
        _invincibleTimer = 0f;
        _hurtBox.Invincible = true;
        _hurtBox.SetDeferred(Area2D.PropertyName.Monitorable, false);
        _swordSprite.Visible = false;
        _swordHitBox.SetDeferred(Area2D.PropertyName.Monitoring, false);
        _sprite.Visible = true;
        _sprite.Play(DeathAnim);
        // Filet de sécurité si AnimationFinished n'arrive jamais (animation absente).
        _respawnTimer = RespawnDelay + 2f;
        GD.Print("Brann est mort");
    }

    private void OnAnimationFinished()
    {
        if (_state == State.Mort && _sprite.Animation == DeathAnim)
            _respawnTimer = Mathf.Min(_respawnTimer, RespawnDelay);
    }

    private void OnHit(int amount, Vector2 fromPosition)
    {
        if (_state == State.Mort) return;
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
        if (_state == State.Mort)
        {
            ProcessDead((float)delta);
            return;
        }

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
        else if (Input.IsActionJustPressed("use_item"))
            TryUseItem();
    }

    /// <summary>Vrai quand Brann peut agir (ni attaque, ni touché, ni mort) : utilisé pour interagir avec un coffre.</summary>
    public bool CanInteract => _state == State.Deplacement;

    /// <summary>Direction vers laquelle Brann regarde (Vector2.Up, Down, Left ou Right).</summary>
    public Vector2 FacingDirection => FacingVector();

    /// <summary>Pose « objet levé » (un coffre vient de s'ouvrir). Le jeu est en pause : Brann ne bouge plus.</summary>
    public void BeginLift()
    {
        Velocity = Vector2.Zero;
        _sprite.Visible = true; // le clignotement d'invincibilité pourrait l'avoir caché
        _sprite.Play(LiftAnim);
    }

    /// <summary>Fin de la pose : Brann reprend son attitude immobile, face à la même direction.</summary>
    public void EndLift() => UpdateAnimation(false);

    private Vector2 FacingVector() => _facing switch
    {
        Direction.Haut => Vector2.Up,
        Direction.Gauche => Vector2.Left,
        Direction.Droite => Vector2.Right,
        _ => Vector2.Down,
    };

    // use_item : l'objet équipé décrit son comportement par une scène (ItemData.UseScene) dont le script hérite de ItemUse.
    // Appelé seulement depuis l'état Déplacement (ni attaque, ni touché, ni mort) ; la pause stoppe _PhysicsProcess.
    private void TryUseItem()
    {
        if (_sceneManager.IsTransitioning) return; // pas d'objet posé pendant le fondu entre deux salles
        var item = _gameState.EquippedItem;
        if (item?.UseScene == null) return;
        if (item.HasQuantity && _gameState.GetQuantity(item.Id) < item.UseCost) return;

        var group = "use_" + item.Id; // allocation ponctuelle, à l'appui d'une touche seulement
        if (item.MaxSimultaneous > 0 && GetTree().GetNodesInGroup(group).Count >= item.MaxSimultaneous) return;

        var instance = item.UseScene.Instantiate();
        if (instance is not ItemUse use)
        {
            instance.QueueFree(); // jamais ajoutée à l'arbre : on la libère
            GD.PushError($"La scène d'utilisation de {item.Id} n'a pas de script ItemUse.");
            return;
        }

        var direction = FacingVector();
        var from = GlobalPosition + new Vector2(0, 6);
        float distance = item.UseDistance > 0f ? item.UseDistance : UseDistance;
        var target = from + direction * distance;

        // Un mur entre Brann et le point de pose ? Raycast(s) à l'appui de la touche seulement.
        // Les CharacterBody2D (ennemis) ne sont pas des murs : on les exclut et on relance pour voir derrière eux.
        // Pour un objet qui s'annule contre un mur, le rayon est prolongé de la longueur de sa pointe.
        var rayEnd = item.CancelIfBlocked ? target + direction * item.BlockCheckExtra : target;
        var query = PhysicsRayQueryParameters2D.Create(from, rayEnd);
        query.Exclude = new Godot.Collections.Array<Rid> { GetRid() };
        var space = GetWorld2D().DirectSpaceState;
        for (int attempt = 0; attempt < 4; attempt++)
        {
            var hit = space.IntersectRay(query);
            if (hit.Count == 0) break;
            if (hit["collider"].AsGodotObject() is CharacterBody2D body)
            {
                query.Exclude.Add(body.GetRid());
                continue;
            }
            if (item.CancelIfBlocked)
            {
                use.QueueFree(); // jamais ajoutée à l'arbre : rien n'est consommé
                return;
            }
            // Pose contre le mur, reculée de quelques pixels (une bombe collée à un mur fissuré l'atteint).
            // Mur déjà plus près que la marge : on pose au point de départ, jamais derrière Brann.
            var impact = hit["position"].AsVector2();
            target = from.DistanceTo(impact) <= WallPoseMargin ? from : impact - direction * WallPoseMargin;
            break;
        }

        GetParent().AddChild(use); // même parent que Brann : tri en profondeur (Y-sort) de la salle
        use.GlobalPosition = target;
        use.AddToGroup(group);
        use.Begin(this, direction);

        if (item.HasQuantity)
            _gameState.RemoveItem(item.Id, item.UseCost);
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

    private void ProcessDead(float delta)
    {
        if (_respawnTimer < 0f) return;

        _respawnTimer -= delta;
        if (_respawnTimer > 0f) return;

        // Si refusé (fondu en cours), on réessaie à la frame suivante.
        if (_sceneManager.ReloadCurrentRoom())
            _respawnTimer = -1f;
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
