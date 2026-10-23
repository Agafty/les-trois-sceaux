using Godot;

/// <summary>
/// HUD : cadre d'objet, rubis, clés, cœurs. Lit uniquement GameState (valeurs au _Ready, puis signaux).
/// Les nœuds sont créés en code ; les sprites absents laissent simplement un vide.
/// </summary>
public partial class Hud : CanvasLayer
{
    private const int HeartsPerRow = 10;
    private const int HeartSize = 16;
    private const int DigitSize = 8;
    private const int ScreenWidth = 640;

    private static readonly Vector2 FramePos = new(8, 4);
    private static readonly Vector2 RupeeIconPos = new(48, 6);
    private static readonly Vector2 KeyIconPos = new(48, 24);
    private static readonly Vector2 RupeeDigitsPos = new(68, 10);
    private static readonly Vector2 KeyDigitsPos = new(68, 28);
    private const int HeartsMarginRight = 8;
    private const int HeartsTop = 6;

    private GameState _gameState;
    private Texture2D _heartFull;
    private Texture2D _heartHalf;
    private Texture2D _heartEmpty;
    private readonly AtlasTexture[] _digitTextures = new AtlasTexture[10];

    private TextureRect[] _hearts = System.Array.Empty<TextureRect>();
    private TextureRect[] _rupeeDigits;
    private TextureRect[] _keyDigits;

    public override void _Ready()
    {
        Layer = 5; // sous le fondu du SceneManager (10)
        _gameState = GetNode<GameState>("/root/GameState");

        _heartFull = LoadTexture("res://art/ui/coeur_plein.png");
        _heartHalf = LoadTexture("res://art/ui/coeur_moitie.png");
        _heartEmpty = LoadTexture("res://art/ui/coeur_vide.png");

        var digitsSheet = LoadTexture("res://art/ui/chiffres.png");
        for (int i = 0; i < _digitTextures.Length; i++)
        {
            _digitTextures[i] = new AtlasTexture
            {
                Atlas = digitsSheet,
                Region = new Rect2(i * DigitSize, 0, DigitSize, DigitSize),
            };
        }

        AddRect(LoadTexture("res://art/ui/cadre_objet.png"), FramePos);
        AddRect(LoadTexture("res://art/ui/icone_rubis.png"), RupeeIconPos);
        AddRect(LoadTexture("res://art/ui/icone_cle.png"), KeyIconPos);
        _rupeeDigits = CreateDigits(3, RupeeDigitsPos);
        _keyDigits = CreateDigits(2, KeyDigitsPos);

        _gameState.RupeesChanged += OnRupeesChanged;
        _gameState.KeysChanged += OnKeysChanged;
        _gameState.PlayerHealthChanged += OnHealthChanged;

        OnRupeesChanged(_gameState.Rupees);
        OnKeysChanged(_gameState.Keys);
        OnHealthChanged(_gameState.PlayerHealth, _gameState.PlayerMaxHealth);
    }

    public override void _ExitTree()
    {
        if (_gameState == null) return;
        _gameState.RupeesChanged -= OnRupeesChanged;
        _gameState.KeysChanged -= OnKeysChanged;
        _gameState.PlayerHealthChanged -= OnHealthChanged;
    }

    private static Texture2D LoadTexture(string path)
    {
        if (ResourceLoader.Exists(path))
            return GD.Load<Texture2D>(path);
        GD.PushWarning($"Texture du HUD absente : {path}");
        return null;
    }

    private TextureRect AddRect(Texture2D texture, Vector2 position)
    {
        var rect = new TextureRect
        {
            Texture = texture,
            Position = position,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            StretchMode = TextureRect.StretchModeEnum.Keep,
        };
        AddChild(rect);
        return rect;
    }

    private TextureRect[] CreateDigits(int count, Vector2 origin)
    {
        var digits = new TextureRect[count];
        for (int i = 0; i < count; i++)
            digits[i] = AddRect(null, origin + new Vector2(i * DigitSize, 0));
        return digits;
    }

    private void SetNumber(TextureRect[] digits, int value)
    {
        int cap = 1;
        for (int i = 0; i < digits.Length; i++) cap *= 10;
        value = Mathf.Clamp(value, 0, cap - 1);
        for (int i = digits.Length - 1; i >= 0; i--)
        {
            digits[i].Texture = _digitTextures[value % 10];
            value /= 10;
        }
    }

    private void OnRupeesChanged(int total) => SetNumber(_rupeeDigits, total);

    private void OnKeysChanged(int total) => SetNumber(_keyDigits, total);

    private void OnHealthChanged(int current, int max)
    {
        int heartCount = (max + 1) / 2;
        if (heartCount != _hearts.Length)
            RebuildHearts(heartCount);

        for (int i = 0; i < _hearts.Length; i++)
        {
            int remaining = current - i * 2;
            _hearts[i].Texture = remaining >= 2 ? _heartFull : remaining == 1 ? _heartHalf : _heartEmpty;
        }
    }

    private void RebuildHearts(int count)
    {
        foreach (var heart in _hearts)
            heart.QueueFree();

        _hearts = new TextureRect[count];
        int rowWidth = HeartsPerRow * HeartSize;
        float left = ScreenWidth - HeartsMarginRight - rowWidth;
        for (int i = 0; i < count; i++)
        {
            var pos = new Vector2(left + (i % HeartsPerRow) * HeartSize, HeartsTop + (i / HeartsPerRow) * HeartSize);
            _hearts[i] = AddRect(null, pos);
        }
    }
}
