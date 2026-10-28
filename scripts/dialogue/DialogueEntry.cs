using System;
using System.Collections.Generic;

/// <summary>
/// Un bloc de répliques d'un personnage, valable pour une étape d'histoire et des conditions de flags (classe C# pure).
/// Les répliques sont des CLÉS de traduction (textes.csv), jamais du texte.
/// </summary>
public sealed class DialogueEntry
{
    /// <summary>Étape d'histoire (0..4) pour laquelle ce bloc est valable ; null = toutes les étapes.</summary>
    public int? Stage { get; init; }

    /// <summary>Flags (ids de GameState.IsCollected) qui doivent TOUS être posés.</summary>
    public IReadOnlyList<string> Flags { get; init; } = Array.Empty<string>();

    /// <summary>Flags qui ne doivent PAS être posés.</summary>
    public IReadOnlyList<string> NotFlags { get; init; } = Array.Empty<string>();

    /// <summary>Faux (défaut) : toutes les répliques s'enchaînent à chaque interaction. Vrai : une seule par interaction, en boucle.</summary>
    public bool Cycle { get; init; }

    /// <summary>Récompense donnée quand la conversation se termine (facultative). Ignorée si son id est déjà mémorisé.</summary>
    public DialogueReward Reward { get; init; }

    public IReadOnlyList<string> Lines { get; init; } = Array.Empty<string>();

    public bool FlagsMatch(Func<string, bool> hasFlag)
    {
        foreach (var f in Flags)
            if (!hasFlag(f)) return false;
        foreach (var f in NotFlags)
            if (hasFlag(f)) return false;
        return true;
    }
}
