using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.Json;

/// <summary>
/// Lecture et validation du JSON d'une cinématique (C# pur, testable). Ne lève jamais d'exception : renvoie faux et la liste des erreurs.
/// Format : { "id": "ouverture_01_matin", "drapeau_fin": "ouv_01", "passable": true, "etapes": [ { "action": "dialogue", ... }, ... ] }
/// Actions et champs (tout identifiant est en minuscules, chiffres et _) :
///  dialogue      orateur (clé Tr, facultatif), lignes (clés Tr)
///  deplacer      acteur, vers (repère ou @acteur), decalage [x,y], vitesse, attendre (vrai par défaut)
///  placer        acteur, vers, decalage                     (téléportation, à cacher par un fondu)
///  regarder      acteur, direction (up/down/left/right) ou vers
///  animer        acteur, nom (animation du sprite : wounded, hammer, idle_down...)
///  attendre      secondes, ou deplacements = true
///  fondu         vers (noir/clair), duree
///  teinte        couleur (normal/eclipse/nuit/#RRGGBB), duree
///  son           nom (voir Sfx)
///  musique       piste (« stop » ou nom de fichier de audio/musique/), duree
///  camera        vers (repère, @acteur ou « brann »), decalage, duree
///  apparaitre    cible = pnj (id, sprite, a, decalage, direction) | ennemis (type, groupe, drapeau_mort)
///                | ennemi (type, variante, a, decalage, drapeau_mort) | decor (id, image, a, decalage) | ramassable (id, contenu, a, decalage)
///  disparaitre   acteur
///  donner        contenu (resources/pickups/), id (facultatif : donné une seule fois)
///  drapeau       nom
///  aller_a       carte (res://scenes/rooms/...tscn), spawn   (dernière étape utile : la salle change)
///  secousse      force, duree
///  sauvegarder
/// </summary>
public static class CinematicParser
{
    public static readonly string[] KnownActions =
    {
        "dialogue", "deplacer", "placer", "regarder", "animer", "attendre", "fondu", "teinte", "son", "musique",
        "camera", "apparaitre", "disparaitre", "donner", "drapeau", "aller_a", "secousse", "sauvegarder",
    };

    private static readonly string[] Directions = { "up", "down", "left", "right" };
    private static readonly string[] SpawnKinds = { "pnj", "ennemis", "ennemi", "decor", "ramassable" };

    public static bool TryParse(string json, out CinematicData data, out List<string> errors)
    {
        errors = new List<string>();
        data = null;
        try
        {
            using var doc = JsonDocument.Parse(json ?? "", new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
            var root = doc.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                errors.Add("la racine doit être un objet");
                return false;
            }
            string id = Str(root, "id");
            if (!IsName(id)) errors.Add("« id » invalide (minuscules, chiffres et _)");
            string endFlag = Str(root, "drapeau_fin");
            if (endFlag.Length > 0 && !IsName(endFlag)) errors.Add("« drapeau_fin » invalide");
            bool skippable = !(root.TryGetProperty("passable", out var p) && p.ValueKind == JsonValueKind.False);

            var steps = new List<CinematicStep>();
            if (!root.TryGetProperty("etapes", out var list) || list.ValueKind != JsonValueKind.Array)
                errors.Add("« etapes » doit être une liste");
            else
            {
                int index = 0;
                foreach (var e in list.EnumerateArray())
                {
                    var step = ParseStep(e, index, errors);
                    if (step != null) steps.Add(step);
                    index++;
                }
                if (index == 0) errors.Add("« etapes » est vide");
            }
            if (errors.Count > 0) return false;
            data = new CinematicData { Id = id, EndFlag = endFlag, Skippable = skippable, Steps = steps };
            return true;
        }
        catch (Exception ex) when (ex is JsonException or InvalidOperationException or FormatException)
        {
            errors.Add("JSON invalide : " + ex.Message);
            return false;
        }
    }

    private static CinematicStep ParseStep(JsonElement e, int index, List<string> errors)
    {
        string where = $"étape {index}";
        if (e.ValueKind != JsonValueKind.Object)
        {
            errors.Add($"{where} : un objet est attendu");
            return null;
        }
        string action = Str(e, "action");
        if (Array.IndexOf(KnownActions, action) < 0)
        {
            errors.Add($"{where} : action inconnue « {action} »");
            return null;
        }
        where += $" ({action})";
        int before = errors.Count;

        string actor = Str(e, "acteur");
        string target = Str(e, "vers");
        string place = Str(e, "a");
        string value = "";
        string name = Str(e, "nom");
        string kind = Str(e, "cible");
        var lines = new List<string>();
        string direction = Str(e, "direction");
        float seconds = Num(e, "secondes", 0f);
        float duration = Num(e, "duree", 0f);
        float speed = Num(e, "vitesse", 80f);
        float strength = Num(e, "force", 3f);
        string id = Str(e, "id");
        string content = Str(e, "contenu");

        switch (action)
        {
            case "dialogue":
                if (e.TryGetProperty("lignes", out var arr) && arr.ValueKind == JsonValueKind.Array)
                {
                    foreach (var l in arr.EnumerateArray())
                    {
                        if (l.ValueKind == JsonValueKind.String && !string.IsNullOrEmpty(l.GetString())) lines.Add(l.GetString());
                        else errors.Add($"{where} : « lignes » ne contient que des clés de texte non vides");
                    }
                }
                if (lines.Count == 0) errors.Add($"{where} : « lignes » est vide ou absente");
                break;
            case "deplacer":
                NeedActor(actor, where, errors);
                NeedTarget(target, where, errors);
                if (speed <= 0f) errors.Add($"{where} : « vitesse » doit être positive");
                break;
            case "placer":
                NeedActor(actor, where, errors);
                NeedTarget(target, where, errors);
                break;
            case "regarder":
                NeedActor(actor, where, errors);
                if (direction.Length == 0 && target.Length == 0) errors.Add($"{where} : « direction » ou « vers » est requis");
                if (direction.Length > 0 && Array.IndexOf(Directions, direction) < 0) errors.Add($"{where} : direction inconnue « {direction} »");
                if (target.Length > 0) NeedTarget(target, where, errors);
                break;
            case "animer":
                NeedActor(actor, where, errors);
                if (!IsName(name)) errors.Add($"{where} : « nom » d'animation invalide");
                break;
            case "attendre":
                if (seconds < 0f) errors.Add($"{where} : « secondes » ne peut pas être négatif");
                if (seconds == 0f && !Bool(e, "deplacements")) errors.Add($"{where} : « secondes » (ou « deplacements »: true) est requis");
                break;
            case "fondu":
                value = target;
                target = "";
                if (value != "noir" && value != "clair") errors.Add($"{where} : « vers » doit être noir ou clair");
                break;
            case "teinte":
                value = Str(e, "couleur");
                if (!CinematicColors.TryParse(value, out _, out _, out _)) errors.Add($"{where} : couleur inconnue « {value} » (normal, eclipse, nuit ou #RRGGBB)");
                break;
            case "son":
                if (!IsName(name)) errors.Add($"{where} : « nom » du son invalide");
                break;
            case "musique":
                name = Str(e, "piste");
                if (!IsName(name)) errors.Add($"{where} : « piste » invalide (« stop » ou un nom de fichier sans extension)");
                break;
            case "camera":
                if (target != "brann") NeedTarget(target, where, errors);
                break;
            case "apparaitre":
                ValidateSpawn(e, where, kind, errors);
                break;
            case "disparaitre":
                NeedActor(actor, where, errors);
                break;
            case "donner":
                if (!IsName(content)) errors.Add($"{where} : « contenu » invalide (nom d'un fichier de resources/pickups/)");
                if (id.Length > 0 && !IsName(id)) errors.Add($"{where} : « id » invalide");
                break;
            case "drapeau":
                if (!IsName(name)) errors.Add($"{where} : « nom » du drapeau invalide");
                break;
            case "aller_a":
                string scene = Str(e, "carte");
                if (!scene.StartsWith("res://scenes/rooms/", StringComparison.Ordinal) || !scene.EndsWith(".tscn", StringComparison.Ordinal) || scene.Contains(".."))
                    errors.Add($"{where} : « carte » doit être un chemin res://scenes/rooms/....tscn");
                break;
            case "secousse":
                if (strength <= 0f) errors.Add($"{where} : « force » doit être positive");
                break;
        }
        if (duration < 0f) errors.Add($"{where} : « duree » ne peut pas être négative");
        if (errors.Count > before) return null;

        var off = Offset(e);
        string variant = Str(e, "variante");
        return new CinematicStep
        {
            Action = action,
            Actor = actor,
            Target = target.Length > 0 ? target : place,
            OffsetX = off.x,
            OffsetY = off.y,
            Speed = speed,
            Seconds = action == "attendre" ? seconds : duration,
            WaitMoves = Bool(e, "deplacements"),
            WaitEnd = !(e.TryGetProperty("attendre", out var w) && w.ValueKind == JsonValueKind.False),
            Speaker = Str(e, "orateur"),
            Lines = lines,
            Direction = direction,
            Value = value,
            Name = name,
            Kind = kind,
            Id = id,
            Sprite = Str(e, "sprite"),
            Type = Str(e, "type"),
            Group = Str(e, "groupe"),
            Variant = variant.Length > 0 ? variant : "normal",
            Image = Str(e, "image"),
            Content = content,
            DeathFlag = Str(e, "drapeau_mort"),
            Scene = action == "aller_a" ? Str(e, "carte") : "",
            Spawn = Str(e, "spawn"),
            Strength = strength,
        };
    }

    private static void ValidateSpawn(JsonElement e, string where, string kind, List<string> errors)
    {
        if (Array.IndexOf(SpawnKinds, kind) < 0)
        {
            errors.Add($"{where} : « cible » doit être pnj, ennemis, ennemi, decor ou ramassable");
            return;
        }
        string place = Str(e, "a");
        switch (kind)
        {
            case "pnj":
                if (!IsName(Str(e, "id"))) errors.Add($"{where} : « id » du PNJ invalide");
                NeedTarget(place, where, errors, "a");
                string dir = Str(e, "direction");
                if (dir.Length > 0 && Array.IndexOf(Directions, dir) < 0) errors.Add($"{where} : direction inconnue « {dir} »");
                if (Str(e, "sprite").Length > 0 && !IsName(Str(e, "sprite"))) errors.Add($"{where} : « sprite » invalide");
                break;
            case "ennemis":
                if (Str(e, "type").Length > 0 && !IsName(Str(e, "type"))) errors.Add($"{where} : « type » invalide");
                if (Str(e, "groupe").Length > 0 && !IsName(Str(e, "groupe"))) errors.Add($"{where} : « groupe » invalide");
                break;
            case "ennemi":
                if (!IsName(Str(e, "type"))) errors.Add($"{where} : « type » d'ennemi invalide");
                NeedTarget(place, where, errors, "a");
                break;
            case "decor":
                if (!IsName(Str(e, "id"))) errors.Add($"{where} : « id » du décor invalide");
                NeedTarget(place, where, errors, "a");
                break;
            case "ramassable":
                if (!IsName(Str(e, "id"))) errors.Add($"{where} : « id » du ramassable invalide");
                if (!IsName(Str(e, "contenu"))) errors.Add($"{where} : « contenu » invalide");
                NeedTarget(place, where, errors, "a");
                break;
        }
        string death = Str(e, "drapeau_mort");
        if (death.Length > 0 && !IsName(death)) errors.Add($"{where} : « drapeau_mort » invalide");
    }

    private static void NeedActor(string actor, string where, List<string> errors)
    {
        if (!IsName(actor)) errors.Add($"{where} : « acteur » invalide (brann ou l'id d'un PNJ)");
    }

    private static void NeedTarget(string target, string where, List<string> errors, string field = "vers")
    {
        string t = target.StartsWith('@') ? target[1..] : target;
        if (!IsName(t)) errors.Add($"{where} : « {field} » invalide (id de repère ou @acteur)");
    }

    /// <summary>Nom simple : minuscules, chiffres et _ (jamais de chemin).</summary>
    public static bool IsName(string s) => RoomObjectCatalog.IsSafeName(s);

    private static string Str(JsonElement e, string name) =>
        e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() ?? "" : "";

    private static float Num(JsonElement e, string name, float fallback) =>
        e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.Number && v.TryGetSingle(out float f) ? f : fallback;

    private static bool Bool(JsonElement e, string name) =>
        e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.True;

    private static (float x, float y) Offset(JsonElement e)
    {
        if (e.TryGetProperty("decalage", out var arr) && arr.ValueKind == JsonValueKind.Array && arr.GetArrayLength() == 2
            && arr[0].ValueKind == JsonValueKind.Number && arr[1].ValueKind == JsonValueKind.Number)
            return (arr[0].GetSingle(), arr[1].GetSingle());
        return (0f, 0f);
    }

    // --- scenarios.json ---------------------------------------------------------------------------

    /// <summary>Lit resources/cinematiques/scenarios.json : { "scenarios": [ {salle, cinematique, si, sauf, zone:[x,y,l,h]} ], "reperes": [ {salle, id, x, y} ] }.</summary>
    public static bool TryParseScenarios(string json, out ScenarioFile file, out List<string> errors)
    {
        errors = new List<string>();
        file = null;
        try
        {
            using var doc = JsonDocument.Parse(json ?? "", new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
            var root = doc.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                errors.Add("la racine doit être un objet");
                return false;
            }
            var scenarios = new List<ScenarioDef>();
            if (root.TryGetProperty("scenarios", out var sc) && sc.ValueKind == JsonValueKind.Array)
            {
                int i = 0;
                foreach (var s in sc.EnumerateArray())
                {
                    string where = $"scénario {i++}";
                    string room = Str(s, "salle");
                    string cine = Str(s, "cinematique");
                    if (!IsName(cine)) { errors.Add($"{where} : « cinematique » invalide"); continue; }
                    if (room.Length > 0 && !IsName(room)) { errors.Add($"{where} : « salle » invalide"); continue; }
                    float x = 0, y = 0, w = 0, h = 0;
                    if (s.TryGetProperty("zone", out var z))
                    {
                        if (z.ValueKind == JsonValueKind.Array && z.GetArrayLength() == 4)
                        {
                            x = z[0].GetSingle(); y = z[1].GetSingle(); w = z[2].GetSingle(); h = z[3].GetSingle();
                        }
                        else { errors.Add($"{where} : « zone » doit être [x, y, largeur, hauteur]"); continue; }
                    }
                    scenarios.Add(new ScenarioDef
                    {
                        Room = room,
                        Cinematic = cine,
                        RequiredFlags = Flags(s, "si", where, errors),
                        ForbiddenFlags = Flags(s, "sauf", where, errors),
                        X = x, Y = y, Width = w, Height = h,
                    });
                }
            }
            var points = new List<FallbackPoint>();
            if (root.TryGetProperty("reperes", out var pts) && pts.ValueKind == JsonValueKind.Array)
            {
                int i = 0;
                foreach (var p in pts.EnumerateArray())
                {
                    string where = $"repère {i++}";
                    string room = Str(p, "salle");
                    string id = Str(p, "id");
                    if (!IsName(room) || !IsName(id)) { errors.Add($"{where} : « salle » et « id » doivent être des noms simples"); continue; }
                    points.Add(new FallbackPoint { Room = room, Id = id, X = Num(p, "x", 0f), Y = Num(p, "y", 0f) });
                }
            }
            if (errors.Count > 0) return false;
            file = new ScenarioFile { Scenarios = scenarios, Points = points };
            return true;
        }
        catch (Exception ex) when (ex is JsonException or InvalidOperationException or FormatException)
        {
            errors.Add("JSON invalide : " + ex.Message);
            return false;
        }
    }

    private static List<string> Flags(JsonElement e, string name, string where, List<string> errors)
    {
        var result = new List<string>();
        if (!e.TryGetProperty(name, out var arr)) return result;
        if (arr.ValueKind != JsonValueKind.Array) { errors.Add($"{where} : « {name} » doit être une liste de drapeaux"); return result; }
        foreach (var f in arr.EnumerateArray())
        {
            string flag = f.ValueKind == JsonValueKind.String ? f.GetString() ?? "" : "";
            if (!IsName(flag)) errors.Add($"{where} : drapeau invalide dans « {name} »");
            else result.Add(flag);
        }
        return result;
    }
}

/// <summary>Couleurs nommées des teintes d'écran (multiplicateur de la salle, C# pur).</summary>
public static class CinematicColors
{
    /// <summary>« normal » = blanc (aucun effet), « eclipse » = violet, « nuit » = bleu sombre, ou « #RRGGBB ».</summary>
    public static bool TryParse(string value, out float r, out float g, out float b)
    {
        r = g = b = 1f;
        switch (value)
        {
            case "normal": return true;
            case "eclipse": r = 0.62f; g = 0.42f; b = 0.85f; return true;
            case "nuit": r = 0.45f; g = 0.5f; b = 0.8f; return true;
        }
        if (value != null && value.Length == 7 && value[0] == '#'
            && int.TryParse(value.AsSpan(1), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out int rgb))
        {
            r = ((rgb >> 16) & 0xFF) / 255f;
            g = ((rgb >> 8) & 0xFF) / 255f;
            b = (rgb & 0xFF) / 255f;
            return true;
        }
        return false;
    }
}
