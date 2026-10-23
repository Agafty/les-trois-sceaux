using Godot;

public partial class DeathEffect : AnimatedSprite2D
{
    public override void _Ready()
    {
        Play("poof");
        AnimationFinished += QueueFree;
    }
}
