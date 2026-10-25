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

    public MapRoom(string id, string floor, int x, int y, bool isBoss = false, bool hasStairs = false, bool hasFall = false)
    {
        Id = id;
        Floor = floor;
        X = x;
        Y = y;
        IsBoss = isBoss;
        HasStairs = hasStairs;
        HasFall = hasFall;
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
    public IReadOnlyList<(string A, string B)> Links { get; }

    public DungeonLayout(string zone, IReadOnlyList<MapRoom> rooms, IReadOnlyList<(string A, string B)> links)
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
            new MapRoom("donjon1_salle_01_room", "rdc", 1, 0),
            new MapRoom("donjon1_salle_02_room", "rdc", 1, 1),
            new MapRoom("donjon1_salle_03_room", "rdc", 0, 1),
            new MapRoom("donjon1_salle_04_room", "rdc", 2, 1, hasFall: true),
            new MapRoom("donjon1_salle_05_room", "rdc", 3, 1, hasStairs: true),
            new MapRoom("donjon1_salle_06_room", "rdc", 1, 2),
            new MapRoom("donjon1_salle_07_room", "rdc", 2, 2, hasFall: true),
            new MapRoom("donjon1_salle_08_room", "rdc", 3, 2),
            new MapRoom("donjon1_salle_09_room", "rdc", 3, 3, hasStairs: true),
            new MapRoom("donjon1_salle_10_room", "rdc", 2, 3, hasStairs: true),
            new MapRoom("donjon1_salle_boss_room", "rdc", 3, 4, isBoss: true),
            new MapRoom("donjon1_salle_11_room", "sous_sol", 3, 3, hasStairs: true),
            new MapRoom("donjon1_salle_12_room", "sous_sol", 2, 3, hasStairs: true),
            new MapRoom("donjon1_salle_13_room", "sous_sol", 3, 2),
            new MapRoom("donjon1_salle_14_room", "sous_sol", 2, 2),
            new MapRoom("donjon1_salle_15_room", "sous_sol", 2, 1, hasStairs: true),
        },
        new[]
        {
            ("donjon1_salle_01_room", "donjon1_salle_02_room"),
            ("donjon1_salle_02_room", "donjon1_salle_03_room"),
            ("donjon1_salle_02_room", "donjon1_salle_04_room"),
            ("donjon1_salle_02_room", "donjon1_salle_06_room"),
            ("donjon1_salle_04_room", "donjon1_salle_05_room"),
            ("donjon1_salle_06_room", "donjon1_salle_07_room"),
            ("donjon1_salle_07_room", "donjon1_salle_08_room"),
            ("donjon1_salle_07_room", "donjon1_salle_10_room"),
            ("donjon1_salle_08_room", "donjon1_salle_09_room"),
            ("donjon1_salle_09_room", "donjon1_salle_10_room"),
            ("donjon1_salle_09_room", "donjon1_salle_boss_room"),
            ("donjon1_salle_11_room", "donjon1_salle_13_room"),
            ("donjon1_salle_13_room", "donjon1_salle_14_room"),
            ("donjon1_salle_12_room", "donjon1_salle_14_room"),
        });

    /// <summary>Plan d'une zone, ou null si elle n'a pas de carte.</summary>
    public static DungeonLayout GetLayout(string zone) => zone == Donjon1.Zone ? Donjon1 : null;

    /// <summary>Clé mémorisée pour une salle visitée : « zone/id ».</summary>
    public static string MakeVisitedKey(string zone, string roomId) => (zone ?? "") + "/" + (roomId ?? "");

    /// <summary>Visitée : pleine. Non visitée : contour seulement si le joueur a la carte du donjon, sinon invisible.</summary>
    public static MapRoomState GetState(bool visited, bool hasMap) =>
        visited ? MapRoomState.Visited : hasMap ? MapRoomState.Outline : MapRoomState.Hidden;

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
