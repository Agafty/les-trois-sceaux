/// <summary>
/// Teinte d'éclipse imposée par l'étape d'histoire (classe C# pure, sans Godot). À l'étape 3 (3 sceaux, Morvath pas encore vaincu)
/// le ciel est violet sur tout l'extérieur et dans le château ; à l'étape 4 la lumière revient.
/// La teinte devient la <c>BaseTint</c> de la salle : la cinématique « teinte normal » y revient donc aussi.
/// </summary>
public static class StageTintRules
{
    /// <summary>Étape de l'éclipse (avant le combat final).</summary>
    public const int EclipseStage = 3;

    /// <summary>Zones d'extérieur teintées (cartes en caméra « suivre ») : les intérieurs des mêmes zones (forge, boutique…, en caméra « ecran ») ne le sont pas.</summary>
    private static readonly string[] OutdoorZones = { "lac", "village", "route", "foret", "montagne" };

    /// <summary>Cartes à ciel fermé malgré leur zone et leur caméra (grotte du sud-ouest, zone « foret »).</summary>
    private static readonly string[] ExcludedRooms = { "grotte_sw_room" };

    /// <summary>Zone entièrement teintée, salles en caméra « ecran » comprises (le château est sous le ciel d'éclipse).</summary>
    public const string CastleZone = "chateau";

    /// <summary>
    /// Vrai si la salle doit porter la teinte d'éclipse. Une salle sombre (pénombre) garde sa pénombre : l'appelant passe isDark.
    /// </summary>
    public static bool UseEclipse(int stage, string zone, string cameraMode, string roomStem, bool isDark, bool lacEclipseSeen = true)
    {
        if (stage != EclipseStage || isDark) return false;
        if (zone == "lac" && !lacEclipseSeen) return false; // la cinématique lac_retour_eclipse fait elle-même le fondu
        if (zone == CastleZone) return true;
        if (cameraMode != "suivre") return false;
        foreach (var excluded in ExcludedRooms)
            if (excluded == roomStem) return false;
        foreach (var outdoor in OutdoorZones)
            if (outdoor == zone) return true;
        return false;
    }
}
