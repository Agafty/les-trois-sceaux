using System;
using System.Collections.Generic;

/// <summary>
/// Une cinématique lue depuis resources/cinematiques/&lt;id&gt;.json : une liste d'étapes jouées dans l'ordre.
/// Classe C# pure (aucune dépendance à Godot) : la lecture et la validation se testent hors du moteur.
/// </summary>
public sealed class CinematicData
{
    public string Id { get; init; } = "";

    /// <summary>Drapeau (GameState.MarkCollected) posé à la fin, même si la cinématique est passée. Vide : elle peut se rejouer.</summary>
    public string EndFlag { get; init; } = "";

    /// <summary>Faux : le joueur ne peut pas la passer (rare).</summary>
    public bool Skippable { get; init; } = true;

    public IReadOnlyList<CinematicStep> Steps { get; init; } = Array.Empty<CinematicStep>();
}

/// <summary>
/// Une étape. Seuls les champs utiles à l'action sont renseignés (voir <see cref="CinematicParser"/> pour la liste).
/// Les distances sont en pixels, les durées en secondes.
/// </summary>
public sealed class CinematicStep
{
    public string Action { get; init; } = "";

    /// <summary>Personnage concerné : « brann » ou l'id d'un PNJ.</summary>
    public string Actor { get; init; } = "";

    /// <summary>Destination : id de repère (Marqueur, Spawn ou repère de repli) ou « @acteur ».</summary>
    public string Target { get; init; } = "";

    public float OffsetX { get; init; }
    public float OffsetY { get; init; }
    public float Speed { get; init; } = 80f;
    public float Seconds { get; init; }

    /// <summary>Pour « attendre » : attendre la fin de tous les déplacements lancés sans attente.</summary>
    public bool WaitMoves { get; init; }

    /// <summary>Pour « deplacer » : faux = le déplacement se fait pendant que la suite continue.</summary>
    public bool WaitEnd { get; init; } = true;

    public string Speaker { get; init; } = "";
    public IReadOnlyList<string> Lines { get; init; } = Array.Empty<string>();

    /// <summary>up, down, left ou right (« regarder »).</summary>
    public string Direction { get; init; } = "";

    /// <summary>« fondu » : noir ou clair ; « teinte » : normal, eclipse, nuit ou #RRGGBB.</summary>
    public string Value { get; init; } = "";

    /// <summary>Nom d'un son, d'une musique, d'un drapeau ou d'une animation selon l'action.</summary>
    public string Name { get; init; } = "";

    /// <summary>« apparaitre » : pnj, ennemis, ennemi, decor ou ramassable.</summary>
    public string Kind { get; init; } = "";

    public string Id { get; init; } = "";
    public string Sprite { get; init; } = "";
    public string Type { get; init; } = "";
    public string Group { get; init; } = "";
    public string Variant { get; init; } = "normal";
    public string Image { get; init; } = "";

    /// <summary>Contenu (resources/pickups/&lt;contenu&gt;.tres) pour « donner » et « apparaitre ramassable ».</summary>
    public string Content { get; init; } = "";

    /// <summary>« apparaitre » ennemis : drapeau posé quand tous les ennemis créés pour ce drapeau sont morts.</summary>
    public string DeathFlag { get; init; } = "";

    public string Scene { get; init; } = "";
    public string Spawn { get; init; } = "";
    public float Strength { get; init; } = 3f;
}

/// <summary>Un déclencheur de cinématique : lu dans la carte (classe Tiled « Scenario ») ou dans resources/cinematiques/scenarios.json.</summary>
public sealed class ScenarioDef
{
    /// <summary>Nom de la scène sans extension (« forge_room »). Vide : toute salle.</summary>
    public string Room { get; init; } = "";

    public string Cinematic { get; init; } = "";

    /// <summary>Drapeaux qui doivent tous être posés.</summary>
    public IReadOnlyList<string> RequiredFlags { get; init; } = Array.Empty<string>();

    /// <summary>Drapeaux dont aucun ne doit être posé.</summary>
    public IReadOnlyList<string> ForbiddenFlags { get; init; } = Array.Empty<string>();

    /// <summary>Zone en pixels (le centre de Brann doit y être). Largeur ou hauteur 0 : pas de zone, la cinématique part dès que les conditions sont vraies.</summary>
    public float X { get; init; }
    public float Y { get; init; }
    public float Width { get; init; }
    public float Height { get; init; }

    public bool HasZone => Width > 0f && Height > 0f;

    public bool ZoneContains(float px, float py) => px >= X && px <= X + Width && py >= Y && py <= Y + Height;
}

/// <summary>Un repère de repli (point nommé) lu dans scenarios.json, utilisé quand la carte n'a pas le Marqueur voulu.</summary>
public sealed class FallbackPoint
{
    public string Room { get; init; } = "";
    public string Id { get; init; } = "";
    public float X { get; init; }
    public float Y { get; init; }
}

/// <summary>Contenu de resources/cinematiques/scenarios.json.</summary>
public sealed class ScenarioFile
{
    public IReadOnlyList<ScenarioDef> Scenarios { get; init; } = Array.Empty<ScenarioDef>();
    public IReadOnlyList<FallbackPoint> Points { get; init; } = Array.Empty<FallbackPoint>();
}

/// <summary>Règles de déclenchement (C# pur).</summary>
public static class ScenarioRules
{
    /// <summary>Vrai si les conditions de drapeaux sont remplies et que la cinématique n'est pas déjà finie (drapeau de fin).</summary>
    public static bool Matches(ScenarioDef def, string endFlag, Func<string, bool> isSet)
    {
        if (!string.IsNullOrEmpty(endFlag) && isSet(endFlag)) return false;
        foreach (var f in def.RequiredFlags)
            if (!isSet(f)) return false;
        foreach (var f in def.ForbiddenFlags)
            if (isSet(f)) return false;
        return true;
    }

    /// <summary>Découpe « a, b,c » en liste de drapeaux (vides ignorés).</summary>
    public static List<string> SplitFlags(string text)
    {
        var result = new List<string>();
        if (string.IsNullOrWhiteSpace(text)) return result;
        foreach (var part in text.Split(','))
        {
            string flag = part.Trim();
            if (flag.Length > 0) result.Add(flag);
        }
        return result;
    }
}
