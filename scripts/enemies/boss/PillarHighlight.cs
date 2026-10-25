using System.Collections.Generic;
using Godot;

/// <summary>
/// Contour clignotant autour des piliers de l'arène (phase 2 de Sylve) : montre où l'attirer pour l'assommer.
/// Nœud en coordonnées monde (TopLevel), au-dessus du décor.
/// </summary>
public partial class PillarHighlight : Node2D
{
    public IReadOnlyList<Rect2> Pillars { get; set; } = System.Array.Empty<Rect2>();
    private float _time;

    public override void _Ready()
    {
        TopLevel = true;
        GlobalPosition = Vector2.Zero;
        ZIndex = 1;
    }

    public override void _Process(double delta)
    {
        _time += (float)delta;
        QueueRedraw();
    }

    public override void _Draw()
    {
        float pulse = 0.5f + 0.5f * Mathf.Sin(_time * 5f);
        var color = new Color(1f, 0.85f, 0.25f, 0.35f + 0.5f * pulse);
        for (int i = 0; i < Pillars.Count; i++)
            DrawRect(Pillars[i].Grow(2f + 2f * pulse), color, false, 2f);
    }
}
