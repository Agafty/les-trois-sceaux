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
    private const int ScreenHeight = 360;

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

    private const int HeartPieceGap = 4;
    private readonly Texture2D[] _heartPieceTextures = new Texture2D[GameState.HeartPiecesPerHeart];
    private TextureRect _heartPieceRect;

    private TextureRect[] _hearts = System.Array.Empty<TextureRect>();
    private TextureRect[] _rupeeDigits;
    private TextureRect[] _keyDigits;

    // Objet équipé : icône 24x24 centrée dans le cadre 32x32, quantité en bas à droite du cadre.
    private static readonly Vector2 EquippedIconPos = new(FramePos.X + 4, FramePos.Y + 4);
    private static readonly Vector2 EquippedDigitsPos = new(FramePos.X + 15, FramePos.Y + 23);
    private TextureRect _equippedIcon;
    private TextureRect[] _equippedDigits;

    // Petite icône de corbeau en bas à droite, visible un instant après une sauvegarde automatique.
    private const string SaveIconPath = "res://art/ui/icone_sauvegarde.png";
    private const int SaveIconSize = 16;
    private const int SaveIconMargin = 8;
    private const float SaveIconHold = 1f;
    private const float SaveIconFade = 0.5f;
    private SaveSystem _saveSystem;
    private TextureRect _saveIcon;
    private Tween _saveIconTween;
    private AtlasTexture _saveIconAtlas; // planche de 2 images 16x16 (ailes hautes / basses)
    private bool _saveIconWingsUp;

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
        _equippedIcon = AddRect(null, EquippedIconPos);
        _equippedDigits = CreateDigits(2, EquippedDigitsPos);
        _rupeeDigits = CreateDigits(3, RupeeDigitsPos);
        _keyDigits = CreateDigits(2, KeyDigitsPos);

        for (int i = 0; i < _heartPieceTextures.Length; i++)
            _heartPieceTextures[i] = LoadTexture($"res://art/ui/quart_coeur_hud_{i}.png");
        _heartPieceRect = AddRect(null, Vector2.Zero);

        CreateSaveIcon();

        _gameState.RupeesChanged += OnRupeesChanged;
        _gameState.HeartPiecesChanged += OnHeartPiecesChanged;
        _gameState.KeysChanged += OnKeysChanged;
        _gameState.PlayerHealthChanged += OnHealthChanged;
        _gameState.InventoryChanged += RefreshEquipped;
        _gameState.EquippedItemChanged += OnEquippedItemChanged;

        OnRupeesChanged(_gameState.Rupees);
        OnHeartPiecesChanged(_gameState.HeartPieces);
        OnKeysChanged(_gameState.Keys);
        OnHealthChanged(_gameState.PlayerHealth, _gameState.PlayerMaxHealth);
        RefreshEquipped();

        // L'écran d'inventaire vit avec le HUD (il ne dépend que de GameState).
        var menuScene = GD.Load<PackedScene>("res://scenes/ui/inventaire.tscn");
        if (menuScene != null)
            AddChild(menuScene.Instantiate());
        else
            GD.PushError("Inventaire introuvable : res://scenes/ui/inventaire.tscn");
    }

    public override void _ExitTree()
    {
        if (_saveSystem != null) _saveSystem.AutoSaved -= OnAutoSaved;
        if (_gameState == null) return;
        _gameState.RupeesChanged -= OnRupeesChanged;
        _gameState.HeartPiecesChanged -= OnHeartPiecesChanged;
        _gameState.KeysChanged -= OnKeysChanged;
        _gameState.PlayerHealthChanged -= OnHealthChanged;
        _gameState.InventoryChanged -= RefreshEquipped;
        _gameState.EquippedItemChanged -= OnEquippedItemChanged;
    }

    private void OnEquippedItemChanged(string itemId) => RefreshEquipped();

    // Seule la sauvegarde AUTOMATIQUE passe par ici : la statue affiche son propre message, F10 est un outil de test.
    private void CreateSaveIcon()
    {
        var texture = ResourceLoader.Exists(SaveIconPath) ? GD.Load<Texture2D>(SaveIconPath) : null;
        if (texture == null)
        {
            // Remplacement tant que le graphiste n'a pas livré icone_sauvegarde.png.
            var image = Image.CreateEmpty(SaveIconSize * 2, SaveIconSize, false, Image.Format.Rgba8);
            image.Fill(new Color(0.25f, 0.22f, 0.32f));
            image.FillRect(new Rect2I(4, 4, 8, 8), new Color(0.75f, 0.7f, 0.9f));
            image.FillRect(new Rect2I(20, 4, 8, 8), new Color(0.75f, 0.7f, 0.9f));
            texture = ImageTexture.CreateFromImage(image);
        }
        _saveIconAtlas = new AtlasTexture { Atlas = texture, Region = new Rect2(0, 0, SaveIconSize, SaveIconSize) };
        _saveIcon = AddRect(_saveIconAtlas, new Vector2(ScreenWidth - SaveIconMargin - SaveIconSize, ScreenHeight - SaveIconMargin - SaveIconSize));
        _saveIcon.Visible = false;

        _saveSystem = GetNodeOrNull<SaveSystem>("/root/SaveSystem");
        if (_saveSystem != null) _saveSystem.AutoSaved += OnAutoSaved;
    }

    private void OnAutoSaved(int slot)
    {
        _saveIconTween?.Kill();
        _saveIcon.Visible = true;
        _saveIcon.Modulate = Colors.White;
        _saveIconTween = CreateTween();
        for (int i = 0; i < 4; i++) // le corbeau bat des ailes pendant la seconde où l'icône reste affichée
        {
            _saveIconTween.TweenCallback(Callable.From(FlapWings));
            _saveIconTween.TweenInterval(SaveIconHold / 4f);
        }
        _saveIconTween.TweenProperty(_saveIcon, "modulate:a", 0f, SaveIconFade);
        _saveIconTween.TweenCallback(Callable.From(HideSaveIcon));
    }

    private void FlapWings()
    {
        _saveIconWingsUp = !_saveIconWingsUp;
        _saveIconAtlas.Region = new Rect2(_saveIconWingsUp ? SaveIconSize : 0, 0, SaveIconSize, SaveIconSize);
    }

    private void HideSaveIcon() => _saveIcon.Visible = false;

    private void RefreshEquipped()
    {
        var item = _gameState.EquippedItem;
        _equippedIcon.Texture = item?.Icon;
        bool showCount = item != null && item.HasQuantity;
        foreach (var digit in _equippedDigits)
            digit.Visible = showCount;
        if (showCount)
            SetNumber(_equippedDigits, _gameState.GetQuantity(item.Id));
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

    private void OnHeartPiecesChanged(int total)
    {
        _heartPieceRect.Texture = _heartPieceTextures[Mathf.Clamp(total, 0, _heartPieceTextures.Length - 1)];
    }

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
        _heartPieceRect.Position = new Vector2(left - HeartPieceGap - HeartSize, HeartsTop);
        for (int i = 0; i < count; i++)
        {
            var pos = new Vector2(left + (i % HeartsPerRow) * HeartSize, HeartsTop + (i / HeartsPerRow) * HeartSize);
            _hearts[i] = AddRect(null, pos);
        }
    }
}
