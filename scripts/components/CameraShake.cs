using Godot;

public partial class CameraShake : Camera2D
{
    private float _strength;
    private float _duration;
    private float _timer;
    private readonly RandomNumberGenerator _rng = new();

    public override void _Ready()
    {
        _rng.Randomize();
    }

    public void Shake(float strength, float duration)
    {
        _strength = strength;
        _duration = duration;
        _timer = duration;
    }

    public override void _Process(double delta)
    {
        if (_timer <= 0f)
        {
            Offset = Vector2.Zero;
            return;
        }

        _timer -= (float)delta;
        var falloff = _timer / _duration;
        Offset = new Vector2(_rng.RandfRange(-1f, 1f), _rng.RandfRange(-1f, 1f)) * _strength * falloff;
    }
}
