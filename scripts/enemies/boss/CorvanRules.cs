using System;

/// <summary>
/// Règles pures du combat final contre Corvan puis Morvath (sans Godot, donc testables) : manches de la phase 2,
/// objet à utiliser, durées d'aide, cercles du marteau, ravitaillement, progression de la barre de vie, tirs de l'Œil.
/// Les dégâts sont en PV de Brann (1 PV = un demi-cœur) : jamais plus de 3 PV (un cœur et demi) par coup.
/// </summary>
public static class CorvanRules
{
    /// <summary>PV de Corvan en phase 1 (coups d'épée de base).</summary>
    public const int Phase1Health = 8;
    /// <summary>PV par manche de la phase 2 (trois manches : 9 PV au total).</summary>
    public const int RoundHealth = 3;
    public const int RoundCount = 3;
    /// <summary>PV de l'Œil détaché : une flèche (2 dégâts) ou deux coups d'épée de base.</summary>
    public const int EyeHealth = 2;

    /// <summary>Marteau : un cœur et demi. Ambiance (ronces, rochers) : un cœur. Eau : un demi-cœur. Orbe de l'Œil : un cœur.</summary>
    public const int HammerDamage = 3;
    public const int AmbientDamage = 2;
    public const int WaterDamage = 1;
    public const int ContactDamage = 1;

    public const int RoundThorns = 0;
    public const int RoundStone = 1;
    public const int RoundWater = 2;

    /// <summary>Plafond du multiplicateur d'aide pour les annonces et les fenêtres de coup (x2, comme Ondine).</summary>
    public const float MaxHelpFactor = 2f;

    /// <summary>Durée multipliée par l'option d'aide (1, 2, ou 0 = illimité), plafonnée à x2 (0 vaut x2).</summary>
    public static float HelpSeconds(float baseSeconds, float helpMultiplier) => OndineRules.AnnounceSeconds(baseSeconds, helpMultiplier);

    /// <summary>Identifiant de l'objet à utiliser pendant une manche : arc, bombes, lanterne (l'ordre dans lequel Brann les a gagnés).</summary>
    public static string RoundItem(int round) => round switch
    {
        RoundThorns => GameStateIds.Bow,
        RoundStone => GameStateIds.Bombs,
        _ => GameStateIds.Lantern,
    };

    /// <summary>Clé du conseil affiché la première fois qu'une manche commence (BOSS_CORVAN_CONSEIL_n).</summary>
    public static string RoundHintKey(int round) => "BOSS_CORVAN_CONSEIL_" + (Math.Clamp(round, 0, RoundCount - 1) + 2);

    /// <summary>Deux cercles d'ombre à partir de la mi-vie (jamais plus de deux).</summary>
    public static int HammerCircleCount(int healthLeft, int healthMax) => healthMax > 0 && healthLeft * 2 <= healthMax ? 2 : 1;

    /// <summary>Vrai si Brann (pieds) est dans le cercle d'ombre de rayon <paramref name="radius"/> (bord inclus).</summary>
    public static bool InCircle(float dx, float dy, float radius) => dx * dx + dy * dy <= radius * radius;

    /// <summary>Faut-il ravitailler Brann ? Oui s'il possède l'objet, en a moins que le seuil, et qu'aucun paquet n'est déjà au sol.</summary>
    public static bool NeedsSupply(bool hasItem, int quantity, int below, bool packOnGround) => hasItem && !packOnGround && quantity < below;

    /// <summary>Barre de vie de la phase 1 : PV restants sur 8.</summary>
    public static float Phase1Progress(int healthLeft) => BossRules.Progress(healthLeft, Phase1Health);

    /// <summary>Barre de vie de la phase 2 : PV restants sur 9 (3 par manche). Une manche entamée compte ce qu'il reste de ses 3 PV.</summary>
    public static float Phase2Progress(int round, int healthLeftInRound)
    {
        int done = Math.Clamp(round, 0, RoundCount) * RoundHealth;
        int left = RoundCount * RoundHealth - done - (RoundHealth - Math.Clamp(healthLeftInRound, 0, RoundHealth));
        return BossRules.Progress(left, RoundCount * RoundHealth);
    }

    /// <summary>Barre de vie de la finale : PV de l'Œil sur 2.</summary>
    public static float EyeProgress(int eyeHealthLeft) => BossRules.Progress(eyeHealthLeft, EyeHealth);

    /// <summary>
    /// Choisit le point suivant de l'Œil parmi <paramref name="count"/> : toujours différent du dernier (s'il y en a plus d'un),
    /// <paramref name="random01"/> dans [0, 1[. -1 si la liste est vide.
    /// </summary>
    public static int NextEyePoint(int count, int last, float random01)
    {
        if (count <= 0) return -1;
        if (count == 1) return 0;
        int candidates = last >= 0 && last < count ? count - 1 : count;
        int pick = Math.Min((int)(Math.Clamp(random01, 0f, 0.999999f) * candidates), candidates - 1);
        if (last >= 0 && last < count && pick >= last) pick++;
        return pick;
    }

    /// <summary>Nombre de pointes d'une ligne de ronces qui tiennent entre le départ et la limite, espacées de <paramref name="spacing"/>.</summary>
    public static int ThornCount(float distanceAvailable, float spacing, int max)
    {
        if (spacing <= 0f || distanceAvailable <= 0f) return 0;
        return Math.Min(max, (int)(distanceAvailable / spacing));
    }
}

/// <summary>Identifiants d'objets (resources/items/*.tres) utilisés par le combat, sans dépendre de Godot.</summary>
public static class GameStateIds
{
    public const string Bow = "arc";
    public const string Bombs = "bombes";
    public const string Lantern = "lanterne";
}
