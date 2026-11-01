using Godot;

/// <summary>
/// La lanterne de Brann (enfant de Player). Elle est passive : tant que Brann possède l'objet « lanterne », elle agit sans touche.
/// - Dans une salle en pénombre (<see cref="Room.IsDarkRoom"/>) : un petit halo permanent, plus un grand cercle de lumière chaude
///   décalé devant Brann avec la lanterne.
/// - Dans toute salle : les objets du <see cref="LanternRegistry"/> (torche éteinte, mur à rune) réagissent quand Brann reste à portée.
/// Aucune allocation par image : registre C# parcouru par indice, lumières créées une fois.
/// </summary>
public partial class LanternLight : Node2D
{
    private const float LightFollowSpeed = 400f; // px/s : la lumière glisse vers le côté regardé
    private static readonly Vector2 BodyCenter = new(0f, 6f);

    private Player _player;
    private GameState _state;
    private PointLight2D _lantern;
    private PointLight2D _halo;
    private Node2D _pivot;

    public override void _Ready()
    {
        _player = GetParent<Player>();
        _state = GetNode<GameState>("/root/GameState");
        // La Room lit « obscurite » dans son _Ready, après celui de Brann : le CallDeferred repousse la vérification
        // à après ce _Ready (il dépend de cet ordre).
        Callable.From(SetupLights).CallDeferred();
    }

    /// <summary>
    /// Vrai si la lumière de la lanterne (et non le simple halo) couvre ce point du monde : la lanterne est allumée
    /// (possédée, salle sombre) et le point est dans son cercle. Sans allocation ; sert à l'Ombre noyée.
    /// </summary>
    public bool LanternCovers(Vector2 worldPosition)
    {
        if (_lantern == null || !_lantern.Visible) return false;
        return LanternRules.IsNear(_lantern.GlobalPosition.X, _lantern.GlobalPosition.Y, worldPosition.X, worldPosition.Y, LanternRules.LightRadius * 0.9f);
    }

    private void SetupLights()
    {
        if (!IsInsideTree() || !Room.IsDarkRoom(this)) return;
        _pivot = new Node2D { Name = "Lumieres", Position = BodyCenter };
        AddChild(_pivot);
        _halo = RoomLights.Create(LanternRules.HaloRadius, new Color(0.8f, 0.85f, 1f), 0.8f);
        _lantern = RoomLights.Create(LanternRules.LightRadius, new Color(1f, 0.85f, 0.55f), 0.9f);
        _lantern.Visible = false;
        _pivot.AddChild(_halo);
        _pivot.AddChild(_lantern);
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_player.IsDead) return;
        bool has = _state.HasItem(LanternRules.ItemId);

        if (_lantern != null)
        {
            _lantern.Visible = has;
            if (has)
            {
                var target = _player.FacingDirection * LanternRules.LightOffset;
                _lantern.Position = _lantern.Position.MoveToward(target, LightFollowSpeed * (float)delta);
            }
        }
        if (!has) return;

        var items = LanternRegistry.All;
        var center = _player.GlobalPosition + BodyCenter;
        float dt = (float)delta;
        for (int i = items.Count - 1; i >= 0; i--)
        {
            // Parcours inverse : un objet retiré pendant le parcours (ou un autre retiré par sa réaction) est au pire traité au tick suivant.
            if (i >= items.Count) continue;
            var item = items[i];
            var pos = item.LanternPosition;
            bool near = LanternRules.IsNear(center.X, center.Y, pos.X, pos.Y, item.LanternReach);
            item.LanternTimer = LanternRules.Advance(item.LanternTimer, near, dt);
            if (near && LanternRules.IsReached(item.LanternTimer, item.LanternDwell))
                item.OnLanternReached();
        }
    }
}
