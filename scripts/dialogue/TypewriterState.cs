using System;

/// <summary>Défilement lettre par lettre d'un texte (classe C# pure) : combien de caractères sont visibles à cet instant.</summary>
public sealed class TypewriterState
{
    private readonly int _total;
    private readonly float _charsPerSecond;
    private float _progress;

    public TypewriterState(int totalChars, float charsPerSecond)
    {
        _total = Math.Max(0, totalChars);
        _charsPerSecond = Math.Max(1f, charsPerSecond);
    }

    public int Total => _total;

    /// <summary>Nombre de caractères visibles.</summary>
    public int Visible => Math.Min(_total, (int)_progress);

    public bool IsComplete => Visible >= _total;

    /// <summary>Fait avancer le défilement ; renvoie le nombre de nouveaux caractères révélés.</summary>
    public int Update(float delta)
    {
        int before = Visible;
        if (!IsComplete) _progress += Math.Max(0f, delta) * _charsPerSecond;
        return Visible - before;
    }

    /// <summary>Affiche tout le texte d'un coup.</summary>
    public void Skip() => _progress = _total;
}
