using System;

/// <summary>Règles de l'épée de Brann (C# pur) : niveau 2 « Épée trempée », dégâts multipliés.</summary>
public static class SwordRules
{
    /// <summary>Drapeau posé à la forge quand Brann a reforgé son épée avec le minerai d'étoile.</summary>
    public const string TemperedFlag = "epee_trempee";

    public static bool IsTempered(Func<string, bool> isSet) => isSet(TemperedFlag);

    /// <summary>Dégâts d'un coup d'épée : de base, multipliés si l'épée est trempée.</summary>
    public static int Damage(int baseDamage, int temperedMultiplier, Func<string, bool> isSet) =>
        IsTempered(isSet) ? baseDamage * Math.Max(1, temperedMultiplier) : baseDamage;
}
