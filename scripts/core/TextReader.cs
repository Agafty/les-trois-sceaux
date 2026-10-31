using Godot;

/// <summary>Origine d'une lecture, par priorité croissante : un indice ne coupe pas un bandeau ni un dialogue, un bandeau ne coupe pas un dialogue.</summary>
public enum TextSource
{
    Hint = 0,
    Banner = 1,
    Dialogue = 2,
}

/// <summary>
/// Lecture à voix haute (synthèse vocale du système, API intégrée de Godot : DisplayServer.TtsSpeak). Classe statique, pas un
/// autoload. Sans effet si l'option « Lecture des textes » est désactivée, si la plateforme ne gère pas la synthèse ou si le
/// système n'a aucune voix de la langue courante (un seul avertissement dans la sortie). Le texte doit être DÉJÀ traduit.
/// Réglage de projet requis : audio/general/text_to_speech = true.
/// </summary>
public static class TextReader
{
    private const int Volume = 100;
    private const ulong RetryVoiceMs = 2000; // voix introuvable : on réessaie au plus toutes les 2 s
    private const ulong StartGraceMs = 400;  // TtsIsSpeaking peut répondre faux juste après TtsSpeak

    private static string _voiceLanguage;
    private static string _voiceId = "";
    private static ulong _voiceCheckedAt;
    private static bool _warned;
    private static TextSource _current;
    private static ulong _lastSpeakAt;
    private static bool _hasCurrent;

    /// <summary>Vrai si la plateforme gère la synthèse vocale (faux en headless).</summary>
    public static bool IsSupported => DisplayServer.HasFeature(DisplayServer.Feature.TextToSpeech);

    /// <summary>Vrai si une voix de la langue courante existe dans le système.</summary>
    public static bool HasVoice => IsSupported && FindVoice().Length > 0;

    /// <summary>
    /// Lit le texte (nettoyé). Une lecture en cours d'une source plus prioritaire n'est pas coupée (le nouveau texte est ignoré).
    /// </summary>
    public static void Speak(string text, TextSource source, bool interrupt = true)
    {
        if (!GameOptions.Current.ReadAloud) return;
        SpeakAlways(text, source, interrupt);
    }

    /// <summary>Lit même si l'option est désactivée (phrase d'essai du menu d'options).</summary>
    public static void SpeakAlways(string text, TextSource source, bool interrupt = true)
    {
        if (!IsSupported) return;
        if (IsBusyWithHigher(source)) return;
        string clean = TextReaderRules.Clean(text, TextReaderRules.LanguageOf(TranslationServer.GetLocale()));
        if (clean.Length == 0)
        {
            if (interrupt) Stop(source);
            return;
        }
        string voice = FindVoice();
        if (voice.Length == 0)
        {
            if (!_warned)
            {
                _warned = true;
                GD.PushWarning($"Lecture des textes : aucune voix « {TextReaderRules.LanguageOf(TranslationServer.GetLocale())} » dans le système.");
            }
            return;
        }
        if (interrupt) DisplayServer.TtsStop();
        DisplayServer.TtsSpeak(clean, voice, Volume, 1f, TextReaderRules.RateFor(GameOptions.Current.ReadSpeed), 0, false);
        _current = source;
        _hasCurrent = true;
        _lastSpeakAt = Time.GetTicksMsec();
    }

    /// <summary>Coupe la lecture en cours, quelle que soit son origine (pause, transition, mort).</summary>
    public static void Stop()
    {
        _hasCurrent = false;
        if (IsSupported) DisplayServer.TtsStop();
    }

    /// <summary>Coupe la lecture seulement si elle vient de cette source (ex. quitter une zone d'indice ne coupe pas un dialogue).</summary>
    public static void Stop(TextSource source)
    {
        if (_hasCurrent && _current == source) Stop();
    }

    private static bool IsBusyWithHigher(TextSource source)
    {
        if (!_hasCurrent || _current <= source) return false;
        if (Time.GetTicksMsec() - _lastSpeakAt < StartGraceMs || DisplayServer.TtsIsSpeaking()) return true;
        _hasCurrent = false; // la lecture précédente est finie
        return false;
    }

    // Voix de la langue courante. Un résultat vide n'est pas gardé : on réessaie toutes les 2 s (voix ajoutée en cours de jeu).
    private static string FindVoice()
    {
        string language = TextReaderRules.LanguageOf(TranslationServer.GetLocale());
        ulong now = Time.GetTicksMsec();
        if (language == _voiceLanguage)
        {
            if (_voiceId.Length > 0 || now - _voiceCheckedAt < RetryVoiceMs) return _voiceId;
        }
        else
        {
            _warned = false;
        }
        _voiceLanguage = language;
        _voiceCheckedAt = now;
        var voices = DisplayServer.TtsGetVoicesForLanguage(language);
        _voiceId = voices.Length > 0 ? voices[0] : "";
        return _voiceId;
    }
}
