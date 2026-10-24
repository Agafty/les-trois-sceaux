/// <summary>
/// Objets propres à un donjon (carte, boussole, grande clé). Classe C# pure : sert à fabriquer la clé
/// mémorisée dans GameState et la sauvegarde, par exemple « donjon1/grande_cle ».
/// </summary>
public static class DungeonItems
{
    public const string Map = "carte";
    public const string Compass = "boussole";
    public const string BigKey = "grande_cle";

    /// <summary>Clé unique d'un objet de donjon : zone + type. Le séparateur « / » ne peut pas se trouver dans un id de zone.</summary>
    public static string MakeKey(string zone, string kind) => (zone ?? "") + "/" + (kind ?? "");

    public static bool IsKnownKind(string kind) => kind == Map || kind == Compass || kind == BigKey;
}
