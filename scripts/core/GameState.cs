using System.Collections.Generic;
using Godot;

/// <summary>
/// Autoload : état persistant de la partie (rubis, vie du joueur, clés).
/// Étendu en Phase 3 (inventaire, coffres ouverts, sauvegarde...).
/// </summary>
public partial class GameState : Node
{
    public const int MaxRupees = 300;
    public const int StartMaxHealth = 6;
    public const int MaxPlayerHealth = 18; // plafond : 9 cœurs
    public const int RespawnHealth = 6; // reprise avec 3 cœurs

    [Signal]
    public delegate void RupeesChangedEventHandler(int total);

    [Signal]
    public delegate void PlayerHealthChangedEventHandler(int current, int max);

    [Signal]
    public delegate void KeysChangedEventHandler(int total);

    [Signal]
    public delegate void HeartPiecesChangedEventHandler(int total);

    [Signal]
    public delegate void InventoryChangedEventHandler();

    [Signal]
    public delegate void EquippedItemChangedEventHandler(string itemId);

    public const int HeartPiecesPerHeart = 4;
    private const string ItemsFolder = "res://resources/items/";

    private readonly Inventory _inventory = new();
    private readonly Dictionary<string, ItemData> _itemData = new();

    /// <summary>Identifiant de l'objet assigné à use_item ("" = rien).</summary>
    public string EquippedItemId { get; private set; } = "";

    /// <summary>Objets possédés, dans l'ordre d'obtention (pour la sauvegarde et l'affichage).</summary>
    public IReadOnlyList<string> InventoryIds => _inventory.Ids;

    public override void _Ready()
    {
        LoadItemRegistry();
    }

    // Registre Id -> ItemData : tous les .tres de resources/items/. Un nouvel objet = un nouveau fichier, sans code.
    private void LoadItemRegistry()
    {
        using var dir = DirAccess.Open(ItemsFolder);
        if (dir == null)
        {
            GD.PushWarning($"Dossier d'objets introuvable : {ItemsFolder}");
            return;
        }
        foreach (var file in dir.GetFiles())
        {
            // Dans un jeu exporté, les ressources apparaissent en « .tres.remap ».
            var name = file.EndsWith(".remap") ? file[..^6] : file;
            if (!name.EndsWith(".tres")) continue;
            if (ResourceLoader.Load(ItemsFolder + name) is ItemData data && !string.IsNullOrEmpty(data.Id))
                _itemData[data.Id] = data;
        }
    }

    /// <summary>Données d'un objet par son id (null si inconnu).</summary>
    public ItemData GetItemData(string id) => id != null && _itemData.TryGetValue(id, out var d) ? d : null;

    /// <summary>Objet actuellement équipé (null si aucun).</summary>
    public ItemData EquippedItem => GetItemData(EquippedItemId);

    public bool HasItem(string id) => _inventory.Has(id);

    /// <summary>Quantité possédée (1 pour un objet sans quantité, 0 si absent).</summary>
    public int GetQuantity(string id) => _inventory.GetQuantity(id);

    /// <summary>Faux si l'objet est déjà au maximum (le ramassable reste alors au sol).</summary>
    public bool CanAddItem(ItemData item) => item != null && _inventory.CanAdd(item.Id, item.MaxQuantity);

    /// <summary>Ajoute un objet. Le premier équipable obtenu s'équipe seul si rien n'est équipé.</summary>
    public bool AddItem(ItemData item, int quantity = 1)
    {
        if (item == null || string.IsNullOrEmpty(item.Id)) return false;
        _itemData[item.Id] = item; // garantit que le registre connaît l'objet
        if (!_inventory.Add(item.Id, quantity, item.MaxQuantity)) return false;

        EmitSignal(SignalName.InventoryChanged);
        if (item.Type == ItemType.Equipable && EquippedItemId == "")
            Equip(item.Id);
        return true;
    }

    /// <summary>Retire des unités d'un objet à quantité (bombes, flèches...). Préparé pour use_item.</summary>
    public bool RemoveItem(string id, int quantity = 1)
    {
        var data = GetItemData(id);
        if (data == null || !data.HasQuantity) return false; // objet sans quantité : rien à retirer
        if (!_inventory.Remove(id, quantity)) return false;
        EmitSignal(SignalName.InventoryChanged);
        return true;
    }

    /// <summary>Équipe un objet possédé et équipable. Renvoie false sinon.</summary>
    public bool Equip(string id)
    {
        var data = GetItemData(id);
        if (data == null || data.Type != ItemType.Equipable || !_inventory.Has(id)) return false;
        if (EquippedItemId == id) return true;

        EquippedItemId = id;
        EmitSignal(SignalName.EquippedItemChanged, id);
        return true;
    }

    /// <summary>Restaure l'inventaire depuis une sauvegarde (listes parallèles id / quantité).</summary>
    public void LoadInventory(IReadOnlyList<string> ids, IReadOnlyList<int> quantities, string equippedId)
    {
        _inventory.Load(ids, quantities);
        // Borne les quantités sur le maximum de chaque objet (1 s'il n'a pas de quantité) ; retire les ids inconnus.
        var loaded = new List<string>(_inventory.Ids);
        foreach (var id in loaded)
        {
            var data = GetItemData(id);
            if (data == null)
            {
                GD.PushWarning($"Objet inconnu dans la sauvegarde, ignoré : {id}");
                _inventory.Discard(id);
                continue;
            }
            _inventory.Clamp(id, data.HasQuantity ? data.MaxQuantity : 1);
        }
        EquippedItemId = "";
        EmitSignal(SignalName.InventoryChanged);
        if (!string.IsNullOrEmpty(equippedId) && Equip(equippedId)) return;
        EmitSignal(SignalName.EquippedItemChanged, "");
    }

    private readonly HashSet<string> _collected = new();

    /// <summary>Identifiants des objets uniques déjà ramassés (pour la sauvegarde).</summary>
    public IReadOnlyCollection<string> CollectedIds => _collected;

    /// <summary>Restaure les flags et le compteur de quarts depuis une sauvegarde.</summary>
    public void LoadCollected(IEnumerable<string> ids, int heartPieces)
    {
        _collected.Clear();
        if (ids != null)
            foreach (var id in ids)
                MarkCollected(id);
        HeartPieces = Mathf.Clamp(heartPieces, 0, HeartPiecesPerHeart - 1);
        EmitSignal(SignalName.HeartPiecesChanged, HeartPieces);
    }

    /// <summary>Quarts de cœur possédés vers le prochain réceptacle (0..3).</summary>
    public int HeartPieces { get; private set; }

    /// <summary>Vrai si l'objet unique (coffre, réceptacle, quart...) a déjà été ramassé.</summary>
    public bool IsCollected(string id) => !string.IsNullOrEmpty(id) && _collected.Contains(id);

    /// <summary>Mémorise un objet unique comme ramassé (base des flags de sauvegarde).</summary>
    public void MarkCollected(string id)
    {
        if (!string.IsNullOrEmpty(id))
            _collected.Add(id);
    }

    /// <summary>
    /// Ajoute un quart de cœur. Au 4e, le compteur retombe à 0 et la méthode renvoie true
    /// (l'appelant doit alors augmenter la vie max via le Health du joueur).
    /// </summary>
    public bool AddHeartPiece()
    {
        HeartPieces++;
        bool complete = HeartPieces >= HeartPiecesPerHeart;
        if (complete) HeartPieces = 0;
        EmitSignal(SignalName.HeartPiecesChanged, HeartPieces);
        return complete;
    }

    public int Rupees { get; private set; }

    /// <summary>Points de vie du joueur (1 PV = un demi-cœur).</summary>
    public int PlayerHealth { get; private set; } = StartMaxHealth;

    public int PlayerMaxHealth { get; private set; } = StartMaxHealth;

    /// <summary>Petites clés possédées.</summary>
    public int Keys { get; private set; }

    /// <summary>Ajoute (ou retire si négatif) des rubis, borné entre 0 et <see cref="MaxRupees"/>.</summary>
    public void AddRupees(int amount)
    {
        int newTotal = Mathf.Clamp(Rupees + amount, 0, MaxRupees);
        if (newTotal == Rupees) return;

        Rupees = newTotal;
        EmitSignal(SignalName.RupeesChanged, Rupees);
    }

    /// <summary>Fixe la vie du joueur (et son maximum). N'émet le signal que si quelque chose change.</summary>
    public void SetPlayerHealth(int current, int max)
    {
        max = Mathf.Clamp(max + (max & 1), 2, MaxPlayerHealth); // arrondi au pair (cœurs entiers)
        current = Mathf.Clamp(current, 0, max);
        if (current == PlayerHealth && max == PlayerMaxHealth) return;

        PlayerHealth = current;
        PlayerMaxHealth = max;
        EmitSignal(SignalName.PlayerHealthChanged, PlayerHealth, PlayerMaxHealth);
    }

    /// <summary>
    /// Prépare la reprise après la mort : stocke la vie de reprise SANS émettre de signal,
    /// pour que l'état ne reste jamais à 0 PV (sauvegarde) et que le HUD garde 0 cœur pendant l'animation de mort.
    /// </summary>
    public void PrepareRespawn()
    {
        PlayerHealth = Mathf.Min(RespawnHealth, PlayerMaxHealth);
    }

    /// <summary>Ajoute (ou retire si négatif) des petites clés, jamais sous 0.</summary>
    public void AddKeys(int amount)
    {
        int newTotal = Mathf.Max(Keys + amount, 0);
        if (newTotal == Keys) return;

        Keys = newTotal;
        EmitSignal(SignalName.KeysChanged, Keys);
    }
}
