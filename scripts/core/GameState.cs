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

    /// <summary>
    /// Option d'aide (accessibilité) : multiplicateur des durées des énigmes chronométrées (cibles, plus tard torches).
    /// 1 = normal, 2 = durées doublées, 0 = illimitées. C'est un réglage du joueur, pas un état de partie :
    /// il n'est volontairement pas dans les sauvegardes : il vient de user://options.json (voir GameOptions).
    /// </summary>
    public float PuzzleTimeMultiplier
    {
        get => _puzzleTimeMultiplier;
        set => _puzzleTimeMultiplier = SwitchRules.ClampTimeMultiplier(value);
    }
    private float _puzzleTimeMultiplier = 1f;

    /// <summary>
    /// Invincibilité (s) à accorder à Brann à son arrivée dans la prochaine salle (chute dans un trou de passage).
    /// Lue et remise à zéro par <see cref="Player"/> à son _Ready.
    /// </summary>
    public float PendingArrivalInvincibility { get; set; }

    /// <summary>Id de l'objet « arc » : ses flèches sont sa quantité (butin garanti, tir).</summary>
    public const string BowItemId = "arc";

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

    /// <summary>
    /// Un coffre important (objet clé, grosse récompense) vient d'être ouvert et son contenu appliqué.
    /// Point d'accroche de la sauvegarde automatique (SaveSystem s'y abonne).
    /// </summary>
    [Signal]
    public delegate void ImportantChestOpenedEventHandler(string chestId);

    public void NotifyImportantChestOpened(string chestId) => EmitSignal(SignalName.ImportantChestOpened, chestId);

    /// <summary>Un boss vient d'être vaincu (son id est déjà mémorisé). Point d'accroche de la sauvegarde automatique.</summary>
    [Signal]
    public delegate void BossDefeatedEventHandler(string bossId);

    public void NotifyBossDefeated(string bossId) => EmitSignal(SignalName.BossDefeated, bossId);

    /// <summary>Un sceau vient d'être restauré (ramassé). Point d'accroche de la sauvegarde automatique.</summary>
    [Signal]
    public delegate void SealRestoredEventHandler(string sealId);

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
        GameOptions.LoadAndApply(); // GameState est le premier autoload : langue, aide et fenêtre sont réglées avant tout écran
        LoadItemRegistry();
    }

    // Registre Id -> ItemData (sert aussi de référence C# forte : ResourceKeeper est inutile ici) : tous les .tres de resources/items/. Un nouvel objet = un nouveau fichier, sans code.
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
            if (data.HasQuantity)
                _inventory.Clamp(id, data.MaxQuantity);
            else
                _inventory.SetQuantity(id, 1); // objet sans quantité : toujours 1
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

    private readonly HashSet<string> _visitedRooms = new();

    /// <summary>Salles de donjon déjà visitées, sous la forme « zone/id de salle » (carte du menu pause).</summary>
    public IReadOnlyCollection<string> VisitedRoomKeys => _visitedRooms;

    public bool IsRoomVisited(string zone, string roomId) => _visitedRooms.Contains(DungeonMap.MakeVisitedKey(zone, roomId));

    /// <summary>Note une salle comme visitée. Faux si zone ou id est vide, ou si elle l'était déjà.</summary>
    public bool MarkRoomVisited(string zone, string roomId)
    {
        if (string.IsNullOrEmpty(zone) || string.IsNullOrEmpty(roomId)) return false;
        return _visitedRooms.Add(DungeonMap.MakeVisitedKey(zone, roomId));
    }

    public void LoadVisitedRooms(IEnumerable<string> keys)
    {
        _visitedRooms.Clear();
        if (keys == null) return;
        foreach (var key in keys)
            if (!string.IsNullOrEmpty(key)) _visitedRooms.Add(key);
    }

    private readonly HashSet<string> _dungeonItems = new();

    /// <summary>Objets de donjon possédés (carte, boussole, grande clé), sous la forme « zone/type » (pour la sauvegarde).</summary>
    public IReadOnlyCollection<string> DungeonItemKeys => _dungeonItems;

    /// <summary>Plumes de corbeau trouvées (compteur de progression, sans usage pour l'instant).</summary>
    public int RavenFeathers { get; private set; }

    public bool HasDungeonItem(string zone, string kind) => _dungeonItems.Contains(DungeonItems.MakeKey(zone, kind));

    /// <summary>Donne un objet de donjon (carte, boussole, grande clé) pour cette zone. Faux s'il est inconnu ou déjà possédé.</summary>
    public bool AddDungeonItem(string zone, string kind)
    {
        if (!DungeonItems.IsKnownKind(kind)) return false;
        return _dungeonItems.Add(DungeonItems.MakeKey(zone, kind));
    }

    public void AddRavenFeather() => RavenFeathers++;

    private readonly List<string> _seals = new();

    /// <summary>Sceaux restaurés (« racines »...), dans l'ordre d'obtention : le compteur de progression du jeu.</summary>
    public IReadOnlyList<string> Seals => _seals;

    public int SealCount => _seals.Count;

    /// <summary>
    /// Étape d'histoire 0..4 (début, après la forêt, après la montagne, après le lac, épilogue), DÉRIVÉE des sceaux et du flag
    /// <see cref="StoryRules.EpilogueFlag"/> : rien de plus à sauvegarder. Sert à choisir dialogues, boutique et décor du village.
    /// </summary>
    public int StoryStage => StoryRules.Compute(_seals.Count, IsCollected(StoryRules.EpilogueFlag));

    public bool HasSeal(string id) => !string.IsNullOrEmpty(id) && _seals.Contains(id);

    /// <summary>Restaure un sceau. Faux s'il est vide ou déjà possédé. Prévient la sauvegarde automatique.</summary>
    public bool AddSeal(string id)
    {
        if (string.IsNullOrEmpty(id) || _seals.Contains(id)) return false;
        _seals.Add(id);
        EmitSignal(SignalName.SealRestored, id);
        return true;
    }

    /// <summary>Restaure les sceaux depuis une sauvegarde (sans signal).</summary>
    public void LoadSeals(IEnumerable<string> ids)
    {
        _seals.Clear();
        if (ids == null) return;
        foreach (var id in ids)
            if (!string.IsNullOrEmpty(id) && !_seals.Contains(id))
                _seals.Add(id);
    }

    /// <summary>Restaure les objets de donjon et les plumes depuis une sauvegarde.</summary>
    public void LoadProgress(IEnumerable<string> dungeonItems, int ravenFeathers)
    {
        _dungeonItems.Clear();
        if (dungeonItems != null)
            foreach (var key in dungeonItems)
                if (!string.IsNullOrEmpty(key))
                    _dungeonItems.Add(key);
        RavenFeathers = Mathf.Max(ravenFeathers, 0);
    }

    /// <summary>Quarts de cœur possédés vers le prochain réceptacle (0..3).</summary>
    public int HeartPieces { get; private set; }

    /// <summary>Vrai si l'objet unique (coffre, réceptacle, quart...) a déjà été ramassé.</summary>
    public bool IsCollected(string id) => !string.IsNullOrEmpty(id) && _collected.Contains(id);

    /// <summary>Poules du village attrapées (calculé sur les ids mémorisés : rien de plus à sauvegarder).</summary>
    public int Chickens => ChickenRules.Count(_collected);

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

    /// <summary>Photographie de l'état à sauvegarder (la position de reprise et le temps de jeu sont ajoutés par SaveSystem).</summary>
    public SaveData CreateSaveData()
    {
        var data = new SaveData
        {
            Health = PlayerHealth,
            MaxHealth = PlayerMaxHealth,
            HeartPieces = HeartPieces,
            Rupees = Rupees,
            Keys = Keys,
            EquippedItemId = EquippedItemId,
            RavenFeathers = RavenFeathers,
        };
        data.Seals.AddRange(_seals);
        data.DungeonItems.AddRange(_dungeonItems);
        data.DungeonItems.Sort(string.CompareOrdinal);
        data.VisitedRooms.AddRange(_visitedRooms);
        data.VisitedRooms.Sort(string.CompareOrdinal);
        foreach (var id in _inventory.Ids)
            data.Inventory.Add(new SaveInventoryEntry { Id = id, Quantity = _inventory.GetQuantity(id) });
        data.CollectedIds.AddRange(_collected);
        data.CollectedIds.Sort(string.CompareOrdinal); // ordre stable : fichiers comparables
        return data;
    }

    /// <summary>Remet l'état aux valeurs d'une nouvelle partie (vie de départ, 0 rubis, inventaire et flags vides).</summary>
    public void ResetState()
    {
        ApplySaveData(new SaveData
        {
            Health = StartMaxHealth,
            MaxHealth = StartMaxHealth,
        });
    }

    /// <summary>Remplace tout l'état par celui d'une sauvegarde (valeurs bornées) et prévient le HUD par les signaux habituels.</summary>
    public void ApplySaveData(SaveData data)
    {
        if (data == null) throw new System.ArgumentNullException(nameof(data));

        // 1) Tout préparer (sans toucher à l'état) : si quelque chose est invalide, rien n'a changé.
        var ids = new List<string>();
        var quantities = new List<int>();
        if (data.Inventory != null)
            foreach (var entry in data.Inventory)
            {
                if (string.IsNullOrEmpty(entry?.Id)) continue;
                ids.Add(entry.Id);
                quantities.Add(entry.Quantity);
            }
        int max = Mathf.Clamp(data.MaxHealth, 2, MaxPlayerHealth);
        max += max & 1;
        int health = data.Health <= 0 ? Mathf.Min(RespawnHealth, max) : Mathf.Min(data.Health, max);

        // 2) Appliquer.
        Rupees = Mathf.Clamp(data.Rupees, 0, MaxRupees);
        EmitSignal(SignalName.RupeesChanged, Rupees);
        Keys = Mathf.Max(data.Keys, 0);
        EmitSignal(SignalName.KeysChanged, Keys);

        PlayerMaxHealth = max;
        PlayerHealth = health;
        EmitSignal(SignalName.PlayerHealthChanged, PlayerHealth, PlayerMaxHealth);

        LoadInventory(ids, quantities, data.EquippedItemId);
        LoadCollected(data.CollectedIds, data.HeartPieces);
        LoadProgress(data.DungeonItems, data.RavenFeathers);
        LoadSeals(data.Seals);
        LoadVisitedRooms(data.VisitedRooms);
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
        max = Mathf.Clamp(max, 2, MaxPlayerHealth); // borne d'abord...
        max += max & 1; // ...puis arrondi au pair (cœurs entiers) ; 18 est pair, donc jamais au-dessus du plafond
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
