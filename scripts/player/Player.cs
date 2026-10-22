using Godot;

public partial class Player : CharacterBody2D
{
    private enum Direction { Bas, Haut, Gauche, Droite }

    [Export]
    public float Speed { get; set; } = 100f;

    private Direction _facing = Direction.Bas;
    private AnimatedSprite2D _sprite;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
    }

    public override void _PhysicsProcess(double delta)
    {
        var input = Vector2.Zero;
        if (Input.IsActionPressed("move_right")) input.X += 1;
        if (Input.IsActionPressed("move_left")) input.X -= 1;
        if (Input.IsActionPressed("move_down")) input.Y += 1;
        if (Input.IsActionPressed("move_up")) input.Y -= 1;

        Velocity = input != Vector2.Zero ? input.Normalized() * Speed : Vector2.Zero;
        MoveAndSlide();

        UpdateAnimation(input != Vector2.Zero);
    }

    private void UpdateAnimation(bool moving)
    {
        if (moving)
        {
            if (Mathf.Abs(Velocity.X) > Mathf.Abs(Velocity.Y))
                _facing = Velocity.X > 0 ? Direction.Droite : Direction.Gauche;
            else
                _facing = Velocity.Y > 0 ? Direction.Bas : Direction.Haut;
        }

        string anim = (moving, _facing) switch
        {
            (true, Direction.Bas) => "marche_bas",
            (true, Direction.Haut) => "marche_haut",
            (true, Direction.Gauche) => "marche_gauche",
            (true, Direction.Droite) => "marche_droite",
            (false, Direction.Bas) => "idle_bas",
            (false, Direction.Haut) => "idle_haut",
            (false, Direction.Gauche) => "idle_gauche",
            (false, Direction.Droite) => "idle_droite",
            _ => "idle_bas",
        };
        _sprite.Play(anim);
    }
}
