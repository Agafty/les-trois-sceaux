/// <summary>Résultat d'une tentative d'achat.</summary>
public enum ShopResult
{
    Ok,
    SoldOut,
    CannotUse,
    NotEnoughRupees,
}

/// <summary>Règles d'achat de la boutique (classe C# pure).</summary>
public static class ShopRules
{
    /// <summary>
    /// Ordre des refus : déjà vendu, puis objet inutilisable (au maximum, ou arc non possédé pour des flèches), puis pas assez de rubis.
    /// </summary>
    public static ShopResult Check(int price, int rupees, bool canApply, bool soldOut)
    {
        if (soldOut) return ShopResult.SoldOut;
        if (!canApply) return ShopResult.CannotUse;
        if (rupees < price) return ShopResult.NotEnoughRupees;
        return ShopResult.Ok;
    }
}
