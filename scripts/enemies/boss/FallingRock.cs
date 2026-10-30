using Godot;

/// <summary>
/// Rocher qui tombe du plafond (attaque de Gorm). D'abord une ombre au sol qui grandit puis clignote en rouge (<see cref="WarnDuration"/>),
/// puis le rocher tombe vite, s'écrase (la <see cref="HitBox"/> blesse un instant) et s'éparpille en débris. Aucun corps solide.
/// Le nœud est posé <see cref="SortOffset"/> px au-dessus du point d'impact visible, pour que le tri en profondeur le place sous Brann
/// quand il est dessus (même astuce que <see cref="ThornEruption"/>). Images : art/bosses/gorm/rocher.png et rocher_ombre.png (32x32).
/// </summary>
public partial class FallingRock : Node2D
{
    /// <summary>Durée (s) de l'avertissement : l'ombre au sol, avant la chute.</summary>
    [Export(PropertyHint.Range, "0.3,3,0.05")] public float WarnDuration { get; set; } = 1.0f;
    [Export(PropertyHint.Range, "0.05,1,0.01")] public float FallDuration { get; set; } = 0.18f;
    [Export(PropertyHint.Range, "0.05,1,0.01")] public float ActiveDuration { get; set; } = 0.12f;
    [Export(PropertyHint.Range, "0.1,2,0.05")] public float DebrisDuration { get; set; } = 0.5f;
    /// <summary>Hauteur (px) d'où le rocher tombe.</summary>
    [Export(PropertyHint.Range, "40,400,10")] public float FallHeight { get; set; } = 180f;
    /// <summary>Rayon (px) de la zone qui blesse.</summary>
    [Export(PropertyHint.Range, "8,32,1")] public float Radius { get; set; } = 15f;

    /// <summary>Décalage (px) entre l'origine du nœud et le point d'impact dessiné.</summary>
    public const float SortOffset = 24f;

    private const float BlinkStart = 0.3f;

    /// <summary>Vrai tant que le rocher n'a pas fini sa chute (l'avertissement ou la chute sont en cours).</summary>
    public bool IsFalling => _time < WarnDuration + FallDuration;

    private Sprite2D _shadow;
    private Sprite2D _rock;
    private HitBox _hitBox;
    private float _time;
    private bool _landed;
    private bool _activeOff;

    public override void _Ready()
    {
        _shadow = GetNode<Sprite2D>("Ombre");
        _rock = GetNode<Sprite2D>("Rocher");
        _hitBox = GetNode<HitBox>("HitBox");
        var shape = _hitBox.GetNode<CollisionShape2D>("CollisionShape2D");
        shape.Shape = new CircleShape2D { Radius = Radius }; // forme neuve : la ressource du .tscn est partagée
        shape.Position = new Vector2(0f, SortOffset);
        _hitBox.Monitoring = false;
        _shadow.Position = new Vector2(0f, SortOffset);
        _rock.Visible = false;
        _rock.Frame = GD.Randf() < 0.5f ? 0 : 1;
        ApplyShadow();
    }

    public override void _PhysicsProcess(double delta)
    {
        _time += (float)delta;
        float landAt = WarnDuration + FallDuration;
        if (_time < WarnDuration)
        {
            ApplyShadow();
            return;
        }
        if (_time < landAt)
        {
            if (!_rock.Visible) _rock.Visible = true;
            _shadow.Frame = 3;
            float k = (_time - WarnDuration) / FallDuration;
            _rock.Position = new Vector2(0f, SortOffset - FallHeight * (1f - k * k));
            return;
        }
        if (!_landed)
        {
            _landed = true;
            _shadow.Visible = false;
            _rock.Position = new Vector2(0f, SortOffset);
            _hitBox.Monitoring = true;
            AudioManager.PlayAt(Sfx.FlecheImpact, GlobalPosition + new Vector2(0f, SortOffset));
            if (GetViewport().GetCamera2D() is CameraShake shake) shake.Shake(1.5f, 0.12f);
        }
        float since = _time - landAt;
        if (!_activeOff && since >= ActiveDuration)
        {
            _activeOff = true;
            _hitBox.Monitoring = false;
        }
        // Impact : trois cases de débris (2, 3, 4) réparties sur DebrisDuration.
        int frame = 2 + Mathf.Min(2, (int)(since / DebrisDuration * 3f));
        _rock.Frame = frame;
        if (since >= DebrisDuration) QueueFree();
    }

    // Ombre : trois tailles qui grandissent, puis le cercle rouge qui clignote juste avant la chute.
    private void ApplyShadow()
    {
        float remaining = WarnDuration - _time;
        int frame;
        if (remaining <= BlinkStart)
            frame = ((int)(remaining * 12f) % 2 == 0) ? 3 : 2;
        else
            frame = Mathf.Min(2, (int)(_time / (WarnDuration - BlinkStart) * 3f));
        _shadow.Frame = frame;
    }
}
