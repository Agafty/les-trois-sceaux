using Godot;

/// <summary>
/// Noms des bruitages (fichiers audio/sfx/&lt;nom&gt;.wav, générés par tools/audio/sfx.py).
/// Toujours passer par ces constantes : pas d'allocation, pas de faute de frappe.
/// </summary>
public static class Sfx
{
    public static readonly StringName Epee = "epee";
    public static readonly StringName CoupEnnemi = "coup_ennemi";
    public static readonly StringName EnnemiMort = "ennemi_mort";
    public static readonly StringName BrannTouche = "brann_touche";
    public static readonly StringName BrannMort = "brann_mort";
    public static readonly StringName Rubis = "rubis";
    public static readonly StringName Coeur = "coeur";
    public static readonly StringName Cle = "cle";
    public static readonly StringName ObjetObtenu = "objet_obtenu";
    public static readonly StringName CoffreOuvre = "coffre_ouvre";
    public static readonly StringName PorteOuvre = "porte_ouvre";
    public static readonly StringName PorteVerrouillee = "porte_verrouillee";
    public static readonly StringName FlecheTir = "fleche_tir";
    public static readonly StringName FlecheImpact = "fleche_impact";
    public static readonly StringName FlecheEnflammee = "fleche_enflammee";
    public static readonly StringName BombeMeche = "bombe_meche";
    public static readonly StringName BombeExplosion = "bombe_explosion";
    public static readonly StringName Interrupteur = "interrupteur";
    public static readonly StringName MauvaisOrdre = "mauvais_ordre";
    public static readonly StringName Plaque = "plaque";
    public static readonly StringName BlocPousse = "bloc_pousse";
    public static readonly StringName TorcheAllume = "torche_allume";
    public static readonly StringName Chute = "chute";
    public static readonly StringName Escalier = "escalier";
    public static readonly StringName Sauvegarde = "sauvegarde";
    public static readonly StringName MenuDeplace = "menu_deplace";
    public static readonly StringName MenuValide = "menu_valide";
    public static readonly StringName MenuRetour = "menu_retour";
    public static readonly StringName BossRugit = "boss_rugit";
    public static readonly StringName BossCharge = "boss_charge";
    public static readonly StringName BossAssomme = "boss_assomme";
    public static readonly StringName BossVaincu = "boss_vaincu";
    public static readonly StringName Sceau = "sceau";
    public static readonly StringName Texte = "texte";
    public static readonly StringName Buisson = "buisson";

    /// <summary>Tous les noms, chargés au démarrage par l'AudioManager.</summary>
    public static readonly StringName[] All =
    {
        Epee, CoupEnnemi, EnnemiMort, BrannTouche, BrannMort, Rubis, Coeur, Cle, ObjetObtenu, CoffreOuvre,
        PorteOuvre, PorteVerrouillee, FlecheTir, FlecheImpact, FlecheEnflammee, BombeMeche, BombeExplosion,
        Interrupteur, MauvaisOrdre, Plaque, BlocPousse, TorcheAllume, Chute, Escalier, Sauvegarde,
        MenuDeplace, MenuValide, MenuRetour, BossRugit, BossCharge, BossAssomme, BossVaincu, Sceau, Texte, Buisson,
    };
}
