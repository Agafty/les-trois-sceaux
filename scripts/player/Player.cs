using Godot;

public partial class Player : CharacterBody2D
{
    private enum Direction { Bas, Haut, Gauche, Droite }
    private enum State { Deplacement, Attaque, Touche, Mort, Chute }

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

    /// <summary>Durée (s) de l'animation de chute dans un trou.</summary>
    [Export(PropertyHint.Range, "0.1,2,0.05")]
    public float FallDuration { get; set; } = 0.5f;

    /// <summary>PV perdus en tombant dans un trou (1 PV = un demi-cœur). Une chute ne tue jamais : il reste au moins 1 PV.</summary>
    [Export(PropertyHint.Range, "0,6,1")]
    public int FallDamage { get; set; } = 1;

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
    private Camera2D _camera;
    private float _fallTimer;
    private Vector2 _fallRespawn;
    private System.Func<bool> _fallLeave; // chute dans un trou de passage : lance le changement de salle (vrai quand accepté)
    private bool _fallLeft;
    private float _fallLeaveWait; // filet de sécurité : si le changement de salle n'arrive pas, Brann revient dans la salle
    private const float FallLeaveTimeout = 3f;
    private SceneManager _sceneManager;
    private GameState _gameState;

    /// <summary>Décalage (px) entre l'origine de Brann et le centre de ses pieds (centre de sa capsule de collision).</summary>
    public static readonly Vector2 FeetOffset = new(0f, 6f);

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
        _camera = GetNodeOrNull<Camera2D>("Camera2D");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _gameState = GetNode<GameState>("/root/GameState");
        // Les _Ready des enfants passent avant celui du parent : Health a déjà fait son init par défaut.
        _health.SetValues(_gameState.PlayerHealth, _gameState.PlayerMaxHealth);
        _health.HealthChanged += OnHealthChanged;
        _hurtBox.Hit += OnHit;
        _health.Died += OnDied;
        _sprite.AnimationFinished += OnAnimationFinished;

        // Arrivée par un trou de passage : invincibilité accordée par GameState (une seule fois).
        if (_gameState.PendingArrivalInvincibility > 0f)
        {
            _invincibleTimer = _gameState.PendingArrivalInvincibility;
            _blinkTimer = BlinkInterval;
            _hurtBox.Invincible = true; // levée par UpdateInvincibility à la fin du délai
            _gameState.PendingArrivalInvincibility = 0f;
        }
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
        GetNodeOrNull<PickupBanner>("PickupBanner")?.HideBanner();
        _swordHitBox.SetDeferred(Area2D.PropertyName.Monitoring, false);
        _sprite.Visible = true;
        _sprite.Play(DeathAnim);
        AudioManager.Play(Sfx.BrannMort);
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

        if (_state == State.Chute)
        {
            ProcessFall((float)delta);
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

    /// <summary>
    /// Brann tombe dans un trou : il rétrécit, perd <see cref="FallDamage"/> PV (sans jamais mourir), puis réapparaît à
    /// <paramref name="respawnPosition"/> avec une brève invincibilité. Sans effet s'il est mort ou déjà en train de tomber.
    /// </summary>
    public bool Fall(Vector2 respawnPosition) => BeginFall(respawnPosition, true, null);

    /// <summary>
    /// Brann tombe dans un trou de passage : même animation, mais aucun dégât, et il ne réapparaît pas dans la salle.
    /// Une fois la chute finie, <paramref name="leave"/> est appelée à chaque image jusqu'à ce qu'elle renvoie vrai
    /// (elle lance le changement de salle ; faux = transition déjà en cours, on réessaie). Brann reste figé et invisible entre-temps.
    /// Si la nouvelle salle n'est pas arrivée au bout de quelques secondes (chargement échoué), Brann réapparaît à
    /// <paramref name="respawnPosition"/> comme après une chute ordinaire, sans dégât. Sans effet (faux) s'il est mort ou déjà en train de tomber.
    /// </summary>
    public bool FallThrough(System.Func<bool> leave, Vector2 respawnPosition) => BeginFall(respawnPosition, false, leave);

    /// <summary>Vrai pendant une chute dans un trou (mortel ou de passage).</summary>
    public bool IsFalling => _state == State.Chute;

    private bool BeginFall(Vector2 respawnPosition, bool applyDamage, System.Func<bool> leave)
    {
        if (_state == State.Mort || _state == State.Chute) return false;

        _state = State.Chute;
        _fallTimer = FallDuration;
        _fallRespawn = respawnPosition;
        _fallLeave = leave;
        _fallLeft = false;
        Velocity = Vector2.Zero;
        _knockbackVelocity = Vector2.Zero;
        _hurtBox.Invincible = true; // aucun ennemi ne peut le toucher pendant la chute
        _swordSprite.Visible = false;
        _swordHitBox.Monitoring = false;
        _sprite.Visible = true;
        UpdateAnimation(false);

        AudioManager.Play(Sfx.Chute);
        int damage = applyDamage ? HoleRules.FallDamage(_health.CurrentHealth, FallDamage) : 0;
        if (damage > 0)
            _health.Damage(damage); // HealthChanged -> GameState -> HUD
        GD.Print($"Brann tombe dans un trou (-{damage}) : {_health.CurrentHealth}/{_health.MaxHealth} PV");
        return true;
    }

    private void ProcessFall(float delta)
    {
        if (_fallLeft)
        {
            // Trou de passage : le changement de salle est lancé, Brann attend la nouvelle salle (qui le remplacera).
            _fallLeaveWait -= delta;
            if (_fallLeaveWait > 0f) return;
            GD.PushError("Chute de passage : la salle d'arrivée n'a pas été chargée, Brann reste dans la salle.");
            _gameState.PendingArrivalInvincibility = 0f;
            _fallLeft = false;
            _sprite.Visible = true;
            FinishFall(); // dénouement d'une chute ordinaire : retour à _fallRespawn, état Déplacement, invincibilité
            return;
        }

        _fallTimer -= delta;
        if (_fallTimer > 0f)
        {
            float shrink = Mathf.Lerp(1f, 0.1f, 1f - _fallTimer / FallDuration);
            _sprite.Scale = new Vector2(shrink, shrink);
            return;
        }

        if (_fallLeave != null)
        {
            _sprite.Visible = false;
            if (_fallLeave()) // faux : un fondu est déjà en cours, on réessaie à l'image suivante
            {
                _fallLeave = null;
                _fallLeft = true;
                _fallLeaveWait = FallLeaveTimeout;
            }
            return;
        }

        FinishFall();
    }

    private void FinishFall()
    {
        _sprite.Scale = Vector2.One;
        GlobalPosition = _fallRespawn;
        _camera?.ResetSmoothing();
        _state = State.Deplacement;
        _invincibleTimer = InvincibleDuration;
        _blinkTimer = BlinkInterval;
        _hurtBox.Invincible = true; // levée par UpdateInvincibility à la fin du délai
        UpdateAnimation(false);
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
    private const int MaxRayAttempts = 8;

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
        query.CollisionMask = ~PhysicsLayers.Ravine; // un ravin n'est pas un mur : flèches et bombes passent au-dessus
        var excluded = new Godot.Collections.Array<Rid> { GetRid() };
        query.Exclude = excluded;
        var space = GetWorld2D().DirectSpaceState;
        bool settled = false; // vrai si la boucle a conclu (rien devant, ou mur trouvé)
        for (int attempt = 0; attempt < MaxRayAttempts; attempt++)
        {
            var hit = space.IntersectRay(query);
            if (hit.Count == 0) { settled = true; break; }
            var collider = hit["collider"].AsGodotObject();
            if (collider is CharacterBody2D body)
            {
                excluded.Add(body.GetRid());
                query.Exclude = excluded; // la propriété renvoie une copie : on la réassigne
                continue;
            }
            // Torche / brasero (objet qui s'annule contre un mur, donc l'arc) : ce n'est pas un mur, c'est la flèche qui décide en la touchant (traverse si allumée, s'arrête sinon).
            if (item.CancelIfBlocked && collider is IArrowInteractor and CollisionObject2D interactorBody)
            {
                excluded.Add(interactorBody.GetRid());
                query.Exclude = excluded;
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
            settled = true;
            break;
        }
        if (!settled && item.CancelIfBlocked)
        {
            use.QueueFree(); // trop d'obstacles « traversables » d'affilée : on considère le tir bloqué
            return;
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
        AudioManager.Play(Sfx.Epee);
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
