/// <summary>
/// Choix de la musique (classe C# pure, sans Godot) : noms des pistes de audio/musique/ et correspondance salle -> piste.
/// Les fichiers sont générés par tools/audio/musique.py ; une composition posée sous le même nom (.ogg, .mp3 ou .wav) les remplace.
/// </summary>
public static class MusicRules
{
    public const string Title = "titre";
    public const string Overworld = "overworld";
    public const string Village = "village";
    public const string Dungeon = "donjon";
    public const string Boss = "boss";
    public const string FinalBattle = "combat_final";
    public const string Victory = "victoire";
    public const string GameOver = "game_over";
    public const string Credits = "fin_generique";

    /// <summary>Toutes les pistes du jeu (préchargées au démarrage).</summary>
    public static readonly string[] All =
    {
        Title, Overworld, Village, Dungeon, Boss, FinalBattle, Victory, GameOver, Credits,
    };

    /// <summary>Jingles : jouées une seule fois, la musique de la zone reprend ensuite.</summary>
    public static bool IsJingle(string track) => track == Victory || track == GameOver;

    /// <summary>
    /// Piste de fond d'une salle. <paramref name="forced"/> (propriété de carte « musique » ou export de la Room) l'emporte s'il est valide.
    /// Renvoie null si la salle n'a pas d'avis (zone inconnue ou vide) : la musique en cours continue.
    /// </summary>
    public static string ForRoom(string zone, string roomStem, string forced)
    {
        if (IsValidName(forced)) return forced.Trim();
        zone ??= "";
        roomStem ??= "";
        if (zone.StartsWith("donjon")) return Dungeon;
        switch (zone)
        {
            case "village": return Village; // village et ses intérieurs (forge, boutique, cave...)
            case "foret":
            case "montagne":
            case "lac":
            case "route":
            case "test":
                // La grotte noire sous la falaise est une salle de donjon, pas une route.
                return roomStem.StartsWith("passage_falaise") ? Dungeon : Overworld;
            case "chateau":
                // La cour est un extérieur ; les salles et l'arène sont un donjon.
                return roomStem.StartsWith("chateau_salle") ? Dungeon : Overworld;
            default: return null;
        }
    }

    /// <summary>Nom de piste valable : lettres minuscules, chiffres et « _ » (nom d'un fichier de audio/musique/ sans extension).</summary>
    public static bool IsValidName(string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return false;
        name = name.Trim();
        foreach (char c in name)
            if (!(c >= 'a' && c <= 'z') && !(c >= '0' && c <= '9') && c != '_') return false;
        return true;
    }
}
