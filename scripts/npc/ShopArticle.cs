using Godot;

/// <summary>
/// Article à vendre posé sur un comptoir. Brann s'approche, le regarde et appuie sur « interact » : la boîte de dialogue demande
/// « Acheter X pour N rubis ? » (Oui/Non). Oui : les rubis sont payés et l'effet est appliqué (comme un ramassable). Refus expliqué,
/// sans payer, si Brann n'a pas assez de rubis, si l'objet est déjà au maximum ou si des flèches sont achetées sans arc.
/// - <see cref="Unique"/> : vendu une seule fois (quart de cœur) ; l'<see cref="Id"/> est alors mémorisé dans GameState (MarkCollected).
/// - <see cref="MinStage"/> / <see cref="RequiredFlag"/> : l'article n'est proposé qu'à partir de cette étape d'histoire / de ce flag.
/// </summary>
public partial class ShopArticle : Node2D
{
    /// <summary>Identifiant unique (obligatoire si <see cref="Unique"/>), ex. "village_boutique_quart_coeur".</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Ce que reçoit Brann (un .tres de resources/pickups/).</summary>
    [Export] public PickupEffect Effect { get; set; }

    [Export(PropertyHint.Range, "0,999,1")] public int Price { get; set; } = 10;

    [Export] public bool Unique { get; set; }

    /// <summary>Étape d'histoire minimale (0 = toujours proposé).</summary>
    [Export(PropertyHint.Range, "0,4,1")] public int MinStage { get; set; }

    /// <summary>Flag (GameState.IsCollected) exigé pour proposer l'article ; vide = aucun.</summary>
    [Export] public string RequiredFlag { get; set; } = "";

    /// <summary>Clé de traduction du nom du vendeur affiché dans la boîte.</summary>
    [Export] public string SellerKey { get; set; } = "PNJ_GARRICK";

    private Sprite2D _sprite;
    private Label _priceLabel;
    private InteractionZone _zone;
    private GameState _state;
    private DialogueBox _box;
    private Player _buyer;
    private bool _available;

    /// <summary>Vrai si l'article est proposé en ce moment (condition remplie, pas déjà vendu).</summary>
    public bool IsAvailable => _available;

    public override void _Ready()
    {
        ResourceKeeper.Pin(Effect); // référence C# forte (voir ResourceKeeper)
        _sprite = GetNode<Sprite2D>("Sprite2D");
        _priceLabel = GetNode<Label>("Prix");
        _zone = GetNode<InteractionZone>("ZoneInteraction");
        _state = GetNode<GameState>("/root/GameState");

        if (Effect == null)
            GD.PushWarning($"Article « {Id} » : aucun contenu, il ne sera pas proposé.");
        if (Unique && string.IsNullOrEmpty(Id))
            GD.PushError($"Article unique sans Id ({GetPath()}) : donnez-lui un identifiant, sinon il serait vendu à l'infini.");

        _available = Effect != null
            && _state.StoryStage >= MinStage
            && (string.IsNullOrEmpty(RequiredFlag) || _state.IsCollected(RequiredFlag))
            && !(Unique && _state.IsCollected(Id));
        Refresh();
        _zone.Interacted += OnInteracted;
    }

    public override void _ExitTree()
    {
        if (_zone != null) _zone.Interacted -= OnInteracted;
        if (_box != null && IsInstanceValid(_box)) _box.Finished -= OnFinished;
    }

    private void Refresh()
    {
        Visible = _available;
        _zone.Enabled = _available;
        _zone.SetDeferred(Area2D.PropertyName.Monitoring, _available);
        if (!_available) return;

        var icon = Effect.GetIcon();
        _sprite.Texture = icon;
        float scale = icon != null && Mathf.Max(icon.GetWidth(), icon.GetHeight()) <= 16 ? 2f : 1f;
        _sprite.Scale = new Vector2(scale, scale);
        _priceLabel.Text = Price.ToString();
    }

    private string ItemName() => string.IsNullOrEmpty(Effect?.GetNameKey()) ? "?" : Tr(Effect.GetNameKey());

    /// <summary>Résultat qu'aurait un achat maintenant (sans rien payer). Public pour les tests.</summary>
    public ShopResult Evaluate(Player player) =>
        ShopRules.Check(Price, _state.Rupees, _available && Effect.CanApply(player, _state), !_available);

    private void OnInteracted(Player player)
    {
        if (!_available || (_box != null && IsInstanceValid(_box))) return;
        _buyer = player;
        string seller = string.IsNullOrEmpty(SellerKey) ? "" : Tr(SellerKey);
        switch (Evaluate(player))
        {
            case ShopResult.Ok:
                Open(seller, string.Format(Tr("SHOP_ASK"), ItemName(), Price), new[] { Tr("SHOP_YES"), Tr("SHOP_NO") });
                break;
            case ShopResult.NotEnoughRupees:
                AudioManager.Play(Sfx.PorteVerrouillee);
                Open(seller, Tr("SHOP_NO_RUPEES"), null);
                break;
            case ShopResult.CannotUse:
                AudioManager.Play(Sfx.PorteVerrouillee);
                bool needsBow = Effect is GiveItemEffect { OnlyIfOwned: true, Item: not null } give && !_state.HasItem(give.Item.Id);
                Open(seller, Tr(needsBow ? "SHOP_NEED_BOW" : "SHOP_FULL"), null);
                break;
        }
    }

    private void Open(string seller, string text, string[] choices)
    {
        _box = DialogueBox.OpenModal(this, seller, new[] { text }, choices);
        _box.Finished += OnFinished;
    }

    private void OnFinished(int choice)
    {
        _box = null;
        _zone.BlockFor(0.3f);
        if (choice == 0) Purchase(_buyer);
    }

    /// <summary>Paie et donne l'objet si tout est en règle. Renvoie vrai si l'achat a eu lieu. Public pour les tests.</summary>
    public bool Purchase(Player player)
    {
        if (!IsInstanceValid(player) || Evaluate(player) != ShopResult.Ok) return false;
        _state.AddRupees(-Price);
        Effect.Apply(player, _state);
        AudioManager.Play(Sfx.ObjetObtenu);
        if (Unique)
        {
            _state.MarkCollected(Id);
            _available = false;
            Refresh();
        }
        string seller = string.IsNullOrEmpty(SellerKey) ? "" : Tr(SellerKey);
        Open(seller, string.Format(Tr("SHOP_BOUGHT"), ItemName()), null);
        return true;
    }
}
