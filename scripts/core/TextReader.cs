using System.Collections.Generic;
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
/// Windows : arrêter une lecture quelques instants après son lancement (DisplayServer.TtsStop) fige parfois tout le jeu (blocage du
/// moteur de synthèse, reproduit hors du jeu). Les arrêts sont donc différés d'au moins <see cref="SafeStopMs"/> après le dernier
/// TtsSpeak : les commandes sont mises en attente (seule la dernière coupe compte) et appliquées par un minuteur.
/// Réglage de projet requis : audio/general/text_to_speech = true.
/// </summary>
public static class TextReader
{
    private const int Volume = 100;
    private const ulong RetryVoiceMs = 2000; // voix introuvable : on réessaie au plus toutes les 2 s
    private const ulong StartGraceMs = 400;  // TtsIsSpeaking peut répondre faux juste après TtsSpeak
    private const ulong SafeStopMs = 700; // délai minimal entre un TtsSpeak et le TtsStop suivant (le blocage a été vu à 170 ms)

    private static string _voiceLanguage;
    private static string _voiceId = "";
    private static ulong _voiceCheckedAt;
    private static bool _warned;
    private static TextSource _current;
    private static ulong _lastSpeakAt;
    private static bool _hasCurrent;
    private static bool _engineMaybeSpeaking; // un TtsSpeak a été envoyé et aucun TtsStop depuis : un arrêt est nécessaire
    private static bool _pendingStop;
    private static bool _timerArmed;
    private static readonly List<PendingSpeech> Pending = new();


    private readonly record struct PendingSpeech(string Text, string Voice, float Rate);

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
        if (interrupt)
        {
            Pending.Clear();
            _pendingStop = true;
        }
        Pending.Add(new PendingSpeech(clean, voice, TextReaderRules.RateFor(GameOptions.Current.ReadSpeed)));
        _current = source;
        _hasCurrent = true;
        Pump();
    }

    /// <summary>Coupe la lecture en cours, quelle que soit son origine (pause, transition, mort).</summary>
    public static void Stop()
    {
        _hasCurrent = false;
        if (!IsSupported) return;
        Pending.Clear();
        _pendingStop = _engineMaybeSpeaking; // rien n'a été lancé : rien à arrêter
        Pump();
    }

    /// <summary>Coupe la lecture seulement si elle vient de cette source (ex. quitter une zone d'indice ne coupe pas un dialogue).</summary>
    public static void Stop(TextSource source)
    {
        if (_hasCurrent && _current == source) Stop();
    }

    private static bool IsBusyWithHigher(TextSource source)
    {
        if (!_hasCurrent || _current <= source) return false;
        if (Pending.Count > 0 || Time.GetTicksMsec() - _lastSpeakAt < StartGraceMs || DisplayServer.TtsIsSpeaking()) return true;
        _hasCurrent = false; // la lecture précédente est finie
        if (Time.GetTicksMsec() - _lastSpeakAt >= SafeStopMs) _engineMaybeSpeaking = false;
        return false;
    }

    // Applique les commandes en attente : un arrêt n'est envoyé que 700 ms après le dernier TtsSpeak, sinon on réessaie plus tard.
    private static void Pump()
    {
        ulong now = Time.GetTicksMsec();
        if (_pendingStop)
        {
            if (!_engineMaybeSpeaking) _pendingStop = false;
            else
            {
                ulong elapsed = now - _lastSpeakAt;
                if (elapsed < SafeStopMs)
                {
                    ArmTimer((SafeStopMs - elapsed) / 1000.0 + 0.02);
                    return;
                }
                DisplayServer.TtsStop();
                _engineMaybeSpeaking = false;
                _pendingStop = false;
            }
        }
        for (int i = 0; i < Pending.Count; i++)
        {
            var p = Pending[i];
            DisplayServer.TtsSpeak(p.Text, p.Voice, Volume, 1f, p.Rate, 0, false);
            _engineMaybeSpeaking = true;
            _lastSpeakAt = now;
        }
        Pending.Clear();
    }

    private static void ArmTimer(double seconds)
    {
        if (_timerArmed) return;
        if (Engine.GetMainLoop() is not SceneTree tree)
        {
            Pending.Clear(); // pas de minuteur possible : on abandonne les commandes en attente
            _pendingStop = false;
            return;
        }
        _timerArmed = true;
        tree.CreateTimer(seconds, true, false, true).Timeout += OnTimer; // actif même en pause
    }

    private static void OnTimer()
    {
        _timerArmed = false;
        Pump();
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
