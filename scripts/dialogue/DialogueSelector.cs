using System;
using System.Collections.Generic;

/// <summary>Choisit le bloc de répliques à dire selon l'étape d'histoire et les flags (classe C# pure).</summary>
public static class DialogueSelector
{
    /// <summary>
    /// Premier bloc, dans l'ordre du fichier, dont l'étape est celle demandée (ou sans étape) et dont les flags conviennent.
    /// Sinon repli sur l'étape précédente la plus proche qui a un bloc (un PNJ sans texte neuf répète son dernier propos).
    /// Renvoie null si rien ne convient.
    /// </summary>
    public static DialogueEntry Pick(DialogueData data, int stage, Func<string, bool> hasFlag)
    {
        if (data == null) return null;
        foreach (var entry in data.Entries)
            if ((entry.Stage == null || entry.Stage == stage) && entry.FlagsMatch(hasFlag))
                return entry;
        for (int s = stage - 1; s >= 0; s--)
            foreach (var entry in data.Entries)
                if (entry.Stage == s && entry.FlagsMatch(hasFlag))
                    return entry;
        return null;
    }

    /// <summary>Répliques à montrer pour cette interaction. <paramref name="interactionCount"/> = nombre de fois où le joueur a déjà parlé (sert au mode « cycle »).</summary>
    public static IReadOnlyList<string> GetLines(DialogueEntry entry, int interactionCount)
    {
        if (entry == null || entry.Lines.Count == 0) return Array.Empty<string>();
        if (!entry.Cycle) return entry.Lines;
        return new[] { entry.Lines[Math.Abs(interactionCount) % entry.Lines.Count] };
    }
}
