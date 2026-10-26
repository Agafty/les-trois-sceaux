using System.Collections.Generic;

/// <summary>Une salle sur la carte d'un donjon : id (nom de la scène sans extension), étage et case de la grille.</summary>
public sealed class MapRoom
{
    public string Id { get; }
    public string Floor { get; }
    public int X { get; }
    public int Y { get; }
    public bool IsBoss { get; }
    /// <summary>Escalier vers l'autre étage.</summary>
    public bool HasStairs { get; }
    /// <summary>Trou de passage (sens unique) vers l'étage du dessous.</summary>
    public bool HasFall { get; }
    /// <summary>Clé de traduction du nom court de la salle (affiché sous la carte).</summary>
    public string NameKey { get; }
    /// <summary>Ids des coffres de la salle (vide si aucun).</summary>
    public IReadOnlyList<string> ChestIds { get; }
    /// <summary>Vrai si l'un des coffres est un grand coffre (propriété « important » de la carte Tiled).</summary>
    public bool HasBigChest { get; }

    public MapRoom(string id, string floor, int x, int y, string nameKey = "", string[] chests = null, bool bigChest = false,
        bool isBoss = false, bool hasStairs = false, bool hasFall = false)
    {
        NameKey = nameKey;
        ChestIds = chests ?? System.Array.Empty<string>();
        HasBigChest = bigChest;
        Id = id;
        Floor = floor;
        X = x;
        Y = y;
        IsBoss = isBoss;
        HasStairs = hasStairs;
        HasFall = hasFall;
    }
}

/// <summary>Nature d'un passage entre deux salles (type de l'objet Tiled « Porte »).</summary>
public enum MapDoorKind
{
    Free,
    Key,
    BossKey,
    Enemies,
    Switch,
}

/// <summary>Passage entre deux salles voisines d'un même étage, avec sa porte éventuelle.</summary>
public sealed class MapLink
{
    public string A { get; }
    public string B { get; }
    public MapDoorKind Kind { get; }
    /// <summary>Id de la porte (mémorisé dans GameState quand elle est ouverte), vide si le passage est libre.</summary>
    public string DoorId { get; }

    public MapLink(string a, string b, MapDoorKind kind = MapDoorKind.Free, string doorId = "")
    {
        A = a;
        B = b;
        Kind = kind;
        DoorId = doorId;
    }
}

/// <summary>Plan complet d'un donjon : salles et liens (portes) entre salles voisines d'un même étage. C# pur.</summary>
public sealed class DungeonLayout
{
    public const string FloorGround = "rdc";
    public const string FloorBasement = "sous_sol";

    public string Zone { get; }
    public IReadOnlyList<MapRoom> Rooms { get; }
    /// <summary>Paires d'ids de salles reliées par un passage (même étage).</summary>
    public IReadOnlyList<MapLink> Links { get; }

    public DungeonLayout(string zone, IReadOnlyList<MapRoom> rooms, IReadOnlyList<MapLink> links)
    {
        Zone = zone;
        Rooms = rooms;
        Links = links;
    }

    public MapRoom Find(string id)
    {
        foreach (var room in Rooms)
            if (room.Id == id) return room;
        return null;
    }
}

/// <summary>État d'affichage d'une salle sur la carte.</summary>
public enum MapRoomState
{
    Hidden,
    Outline,
    Visited,
}

/// <summary>Plans connus et règles d'affichage de la carte. C# pur, testable hors du moteur.</summary>
public static class DungeonMap
{
    /// <summary>Plan du Temple des Racines (voir maps/donjon1/plan.md §3). À mettre à jour si le plan change.</summary>
    public static readonly DungeonLayout Donjon1 = new(
        "donjon1",
        new[]
        {
            new MapRoom("donjon1_salle_01_room", "rdc", 1, 0, "SALLE_DONJON1_01"),
            new MapRoom("donjon1_salle_02_room", "rdc", 1, 1, "SALLE_DONJON1_02", new[] { "donjon1_coffre_01" }),
            new MapRoom("donjon1_salle_03_room", "rdc", 0, 1, "SALLE_DONJON1_03"),
            new MapRoom("donjon1_salle_04_room", "rdc", 2, 1, "SALLE_DONJON1_04", new[] { "donjon1_coffre_02" }, hasFall: true),
            new MapRoom("donjon1_salle_05_room", "rdc", 3, 1, "SALLE_DONJON1_05", new[] { "donjon1_coffre_03" }, hasStairs: true),
            new MapRoom("donjon1_salle_06_room", "rdc", 1, 2, "SALLE_DONJON1_06", new[] { "donjon1_coffre_04" }, bigChest: true),
            new MapRoom("donjon1_salle_07_room", "rdc", 2, 2, "SALLE_DONJON1_07", hasFall: true),
            new MapRoom("donjon1_salle_08_room", "rdc", 3, 2, "SALLE_DONJON1_08"),
            new MapRoom("donjon1_salle_09_room", "rdc", 3, 3, "SALLE_DONJON1_09", hasStairs: true),
            new MapRoom("donjon1_salle_10_room", "rdc", 2, 3, "SALLE_DONJON1_10", new[] { "donjon1_coffre_05" }, hasStairs: true),
            new MapRoom("donjon1_salle_boss_room", "rdc", 3, 4, "SALLE_DONJON1_BOSS", isBoss: true),
            new MapRoom("donjon1_salle_11_room", "sous_sol", 3, 3, "SALLE_DONJON1_11", hasStairs: true),
            new MapRoom("donjon1_salle_12_room", "sous_sol", 2, 3, "SALLE_DONJON1_12", hasStairs: true),
            new MapRoom("donjon1_salle_13_room", "sous_sol", 3, 2, "SALLE_DONJON1_13"),
            new MapRoom("donjon1_salle_14_room", "sous_sol", 2, 2, "SALLE_DONJON1_14", new[] { "donjon1_coffre_07" }, bigChest: true),
            new MapRoom("donjon1_salle_15_room", "sous_sol", 2, 1, "SALLE_DONJON1_15", new[] { "donjon1_coffre_06" }, hasStairs: true),
        },
        new[]
        {
            new MapLink("donjon1_salle_01_room", "donjon1_salle_02_room"),
            new MapLink("donjon1_salle_02_room", "donjon1_salle_03_room"),
            new MapLink("donjon1_salle_02_room", "donjon1_salle_04_room"),
            new MapLink("donjon1_salle_02_room", "donjon1_salle_06_room", MapDoorKind.Key, "donjon1_porte_01"),
            new MapLink("donjon1_salle_04_room", "donjon1_salle_05_room", MapDoorKind.Enemies, "donjon1_porte_02"),
            new MapLink("donjon1_salle_06_room", "donjon1_salle_07_room", MapDoorKind.Switch, "donjon1_porte_03"),
            new MapLink("donjon1_salle_07_room", "donjon1_salle_08_room", MapDoorKind.Key, "donjon1_porte_04"),
            new MapLink("donjon1_salle_07_room", "donjon1_salle_10_room"),
            new MapLink("donjon1_salle_08_room", "donjon1_salle_09_room", MapDoorKind.Enemies, "donjon1_porte_05"),
            new MapLink("donjon1_salle_09_room", "donjon1_salle_10_room", MapDoorKind.Switch, "donjon1_porte_06"),
            new MapLink("donjon1_salle_09_room", "donjon1_salle_boss_room", MapDoorKind.BossKey, "donjon1_porte_07"),
            new MapLink("donjon1_salle_11_room", "donjon1_salle_13_room"),
            new MapLink("donjon1_salle_13_room", "donjon1_salle_14_room", MapDoorKind.Key, "donjon1_porte_11"),
            new MapLink("donjon1_salle_12_room", "donjon1_salle_14_room", MapDoorKind.Switch, "donjon1_porte_14"),
        });

    /// <summary>Plan d'une zone, ou null si elle n'a pas de carte.</summary>
    public static DungeonLayout GetLayout(string zone) => zone == Donjon1.Zone ? Donjon1 : null;

    /// <summary>Clé mémorisée pour une salle visitée : « zone/id ».</summary>
    public static string MakeVisitedKey(string zone, string roomId) => (zone ?? "") + "/" + (roomId ?? "");

    /// <summary>Visitée : pleine. Non visitée : contour seulement si le joueur a la carte du donjon, sinon invisible.</summary>
    public static MapRoomState GetState(bool visited, bool hasMap) =>
        visited ? MapRoomState.Visited : hasMap ? MapRoomState.Outline : MapRoomState.Hidden;

    /// <summary>Icône de coffre : salle visitée, ou salle affichée sur la carte quand Brann a la boussole (comme ALttP).</summary>
    public static bool ShowChestIcon(MapRoomState state, bool hasCompass) =>
        state == MapRoomState.Visited || (hasCompass && state != MapRoomState.Hidden);

    /// <summary>Le boss n'est marqué que si le joueur a la boussole (et que la salle est visible).</summary>
    public static bool ShowBossIcon(MapRoom room, MapRoomState state, bool hasCompass) =>
        room.IsBoss && hasCompass && state != MapRoomState.Hidden;

    /// <summary>
    /// Un lien est tracé s'il touche une salle visitée et que l'autre bout est affiché
    /// (le joueur a vu au moins un côté du passage).
    /// </summary>
    public static bool ShowLink(MapRoomState a, MapRoomState b) =>
        (a == MapRoomState.Visited || b == MapRoomState.Visited) && a != MapRoomState.Hidden && b != MapRoomState.Hidden;
}
