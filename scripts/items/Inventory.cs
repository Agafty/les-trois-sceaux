using System.Collections.Generic;

/// <summary>
/// Contenu de l'inventaire : liste ordonnée d'identifiants + quantités. Classe C# pure
/// (aucune dépendance à Godot) pour rester simple à tester et à sérialiser.
/// Un objet sans quantité (max 0) est stocké avec la quantité 1.
/// </summary>
public class Inventory
{
    private readonly List<string> _ids = new();
    private readonly Dictionary<string, int> _quantities = new();

    public IReadOnlyList<string> Ids => _ids;

    public bool Has(string id) => id != null && _quantities.ContainsKey(id);

    public int GetQuantity(string id) => id != null && _quantities.TryGetValue(id, out int q) ? q : 0;

    /// <summary>True si l'ajout changerait quelque chose (objet absent, ou quantité pas au maximum).</summary>
    public bool CanAdd(string id, int maxQuantity) => !Has(id) || (maxQuantity > 0 && GetQuantity(id) < maxQuantity);

    /// <summary>Ajoute l'objet (à la fin de la liste s'il est nouveau). Renvoie true si l'inventaire a changé.</summary>
    public bool Add(string id, int quantity, int maxQuantity)
    {
        if (string.IsNullOrEmpty(id) || quantity <= 0) return false;
        if (!CanAdd(id, maxQuantity)) return false;

        if (maxQuantity <= 0)
        {
            _ids.Add(id);
            _quantities[id] = 1;
            return true;
        }

        if (!_quantities.TryGetValue(id, out int current))
            _ids.Add(id);
        _quantities[id] = System.Math.Min(current + quantity, maxQuantity);
        return true;
    }

    /// <summary>Retire des unités (jamais sous 0, l'objet reste possédé). Renvoie false s'il n'y en a pas assez.</summary>
    public bool Remove(string id, int quantity)
    {
        if (quantity <= 0 || GetQuantity(id) < quantity) return false;
        _quantities[id] -= quantity;
        return true;
    }

    /// <summary>Borne la quantité d'un objet possédé sur un maximum.</summary>
    public void Clamp(string id, int max)
    {
        if (_quantities.TryGetValue(id, out int q) && q > max)
            _quantities[id] = max;
    }

    /// <summary>Retire complètement un objet (id inconnu à la restauration).</summary>
    public void Discard(string id)
    {
        _ids.Remove(id);
        _quantities.Remove(id);
    }

    public void Clear()
    {
        _ids.Clear();
        _quantities.Clear();
    }

    /// <summary>Remplace le contenu (chargement d'une sauvegarde). Les deux listes sont parallèles.</summary>
    public void Load(IReadOnlyList<string> ids, IReadOnlyList<int> quantities)
    {
        Clear();
        if (ids == null) return;
        for (int i = 0; i < ids.Count; i++)
        {
            if (string.IsNullOrEmpty(ids[i]) || _quantities.ContainsKey(ids[i])) continue;
            _ids.Add(ids[i]);
            _quantities[ids[i]] = quantities != null && i < quantities.Count ? System.Math.Max(quantities[i], 0) : 1;
        }
    }
}
