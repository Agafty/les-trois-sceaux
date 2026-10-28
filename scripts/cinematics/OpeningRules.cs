using System;

/// <summary>
/// Règles de l'ouverture du jeu (C# pur). L'état tient en drapeaux dans GameState.CollectedIds (aucun nouveau champ de sauvegarde) :
/// une partie qui n'a jamais posé « ouverture_debut » (ancienne sauvegarde, salle lancée avec F6) n'est PAS dans l'ouverture :
/// elle ne rejoue rien et Brann a son épée.
/// </summary>
public static class OpeningRules
{
    /// <summary>Posé par « Nouvelle partie ».</summary>
    public const string StartedFlag = "ouverture_debut";

    /// <summary>Posé à la fin de la dernière cinématique : le jeu est libre.</summary>
    public const string DoneFlag = "ouverture_fin";

    /// <summary>Épée en bois (Pip) et vraie épée (Corvan).</summary>
    public const string WoodSwordFlag = "epee_bois";
    public const string RealSwordFlag = "epee_corvan";

    /// <summary>Posé au début de l'éclipse : le ciel reste violet jusqu'à la fin de l'ouverture.</summary>
    public const string EclipseFlag = "ouv_eclipse";

    public static bool InProgress(Func<string, bool> isSet) => isSet(StartedFlag) && !isSet(DoneFlag);

    /// <summary>Brann peut attaquer : hors ouverture, ou après avoir reçu une épée.</summary>
    public static bool HasSword(Func<string, bool> isSet) => !isSet(StartedFlag) || isSet(WoodSwordFlag) || isSet(RealSwordFlag);

    /// <summary>Vraie épée (lame claire) ; sinon épée en bois.</summary>
    public static bool HasRealSword(Func<string, bool> isSet) => !isSet(StartedFlag) || isSet(RealSwordFlag);

    /// <summary>Teinte de la salle quand elle se charge : le ciel d'éclipse pendant l'ouverture, sinon aucune.</summary>
    public static string AmbientTint(Func<string, bool> isSet) => isSet(EclipseFlag) && !isSet(DoneFlag) ? "eclipse" : "normal";
}
