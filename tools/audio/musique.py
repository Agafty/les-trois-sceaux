#!/usr/bin/env python3
"""Générateur de musiques chiptune pour Les Trois Sceaux.

Python standard uniquement (wave, math, random, struct). Écrit des .wav 16 bits mono 22050 Hz
dans audio/musique/ (et crée les .import de réglage de boucle s'ils n'existent pas).
Déterministe (graine fixe) : relancer le script donne les mêmes fichiers.

Usage :  python tools/audio/musique.py              (toutes les pistes)
         python tools/audio/musique.py titre boss   (seulement celles-là)
         python tools/audio/musique.py --liste      (noms, durées, boucle ou non)

REMPLACER UNE PISTE : déposer sa propre composition dans audio/musique/ sous le même nom
(titre.ogg, titre.mp3 ou titre.wav). Le jeu cherche d'abord .ogg, puis .mp3, puis .wav.
Une boucle doit être réglée en « loop » dans le panneau Import de Godot ; les jingles
(victoire, game_over) ne bouclent pas.

COMMENT LIRE UNE PARTITION
- Une mesure = 16 pas (doubles-croches), 4/4. Une note s'écrit  NOM:durée  (durée en pas) :
      "E5:6 A5:4 G5:2 E5:4"   = mi noire pointée, la noire, sol croche, mi noire  (6+4+2+4 = 16)
  Noms : C D E F G A B, dièse « # », bémol « b », puis l'octave (A4 = 440 Hz). « r:4 » = silence.
- Les accords s'écrivent  Am F C G7 Bb Dm Em7 Cmaj7 Bdim ...  (un par mesure).
- La basse et les arpèges sont fabriqués à partir des accords avec un motif :
      basse : r = fondamentale, 3 = tierce, 5 = quinte, 8 = octave, x = silence   "r:2 r:2 8:2 r:2 ..."
      arpège : 0 1 2 = notes de l'accord, 3 4 5 = les mêmes une octave plus haut, x = silence
- La batterie est une chaîne de 16 caractères par mesure :
      k = grosse caisse, s = caisse claire, h = charleston, o = charleston ouvert, t = tom, . = rien
- Le tempo (bpm), les instruments (INSTRUMENTS) et le volume de chaque voix se règlent plus bas.
"""
import math
import os
import random
import struct
import sys
import wave

RATE = 22050
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "audio", "musique")
RMS_TARGET = 0.15     # volume moyen visé (toutes les pistes à peu près aussi fortes)
PEAK_LIMIT = 0.90     # crête maximale : jamais de saturation
TAIL = 3.0            # secondes de queue (échos, relâchements) repliées sur le début des boucles

# ---------------------------------------------------------------------------------------------
# Notes et accords
# ---------------------------------------------------------------------------------------------
PITCH = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CHORD_TYPES = {
    "": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10),
    "maj7": (0, 4, 7, 11), "dim": (0, 3, 6), "sus4": (0, 5, 7),
}


def midi_of(name):
    n = PITCH[name[0]]
    i = 1
    if name[i] == "#":
        n += 1
        i += 1
    elif name[i] == "b":
        n -= 1
        i += 1
    return 12 * (int(name[i:]) + 1) + n


def name_of(midi):
    return NAMES[midi % 12] + str(midi // 12 - 1)


def parse_chord(text):
    """'Bb7' -> (hauteur de la fondamentale 0..11, intervalles)."""
    pc = PITCH[text[0]]
    i = 1
    if len(text) > 1 and text[1] == "#":
        pc += 1
        i = 2
    elif len(text) > 1 and text[1] == "b":
        pc -= 1
        i = 2
    return pc % 12, CHORD_TYPES[text[i:]]


def bass_tokens(chords, patterns):
    """Basse : une mesure par accord, motif en degrés (r 3 5 8 x) -> mesures de notes."""
    bars = []
    for i, chord in enumerate(chords):
        pc, ivs = parse_chord(chord)
        root = 40 + ((pc - 4) % 12)       # fondamentale entre E2 et D#3
        degrees = {"r": root, "3": root + ivs[1], "5": root + 7, "8": root + 12}
        pat = patterns[i % len(patterns)]
        out = []
        for tok in pat.split():
            d, _, ln = tok.partition(":")
            out.append(("r:" + ln) if d == "x" else name_of(degrees[d]) + ":" + ln)
        bars.append(" ".join(out))
    return bars


def arp_tokens(chords, patterns, base_octave=4):
    """Arpège : motif en indices de l'accord (0-5, x) -> mesures de notes."""
    bars = []
    for i, chord in enumerate(chords):
        pc, ivs = parse_chord(chord)
        root = 12 * (base_octave + 1) + pc
        tones = [root + v for v in ivs] + [root + v + 12 for v in ivs]
        pat = patterns[i % len(patterns)]
        out = []
        for tok in pat.split():
            d, _, ln = tok.partition(":")
            out.append(("r:" + ln) if d == "x" else name_of(tones[int(d)]) + ":" + ln)
        bars.append(" ".join(out))
    return bars


def parse_bar(bar, where):
    """'E5:6 A5:4 r:2' -> [(pas de départ dans la mesure, midi ou None, durée)]."""
    events = []
    pos = 0
    for tok in bar.split():
        n, _, ln = tok.partition(":")
        ln = int(ln) if ln else 2
        events.append((pos, None if n == "r" else midi_of(n), ln))
        pos += ln
    if pos != 16:
        raise ValueError("%s : la mesure « %s » fait %d pas au lieu de 16" % (where, bar, pos))
    return events


# ---------------------------------------------------------------------------------------------
# Instruments
# echo = (retard en pas, gain, nombre de répétitions) ; vib = (profondeur, Hz, retard s)
# ---------------------------------------------------------------------------------------------
INSTRUMENTS = {
    # voix principales
    "lead":      dict(kind="pulse", duty=0.50, vol=0.20, a=0.012, d=0.60, s=0.80, r=0.07, gate=0.92, vib=(0.010, 5.5, 0.20), echo=(3, 0.30, 3)),
    "lead25":    dict(kind="pulse", duty=0.25, vol=0.20, a=0.008, d=0.50, s=0.75, r=0.06, gate=0.90, vib=(0.008, 5.8, 0.25), echo=(3, 0.28, 3)),
    "lead_dur":  dict(kind="pulse", duty=0.25, vol=0.19, a=0.004, d=0.40, s=0.80, r=0.04, gate=0.88, vib=None, echo=(2, 0.22, 2)),
    "flute":     dict(kind="pulse", duty=0.50, vol=0.17, a=0.04, d=0.80, s=0.85, r=0.12, gate=0.95, vib=(0.014, 5.0, 0.18), echo=(4, 0.34, 3)),
    "sombre":    dict(kind="pulse", duty=0.125, vol=0.18, a=0.02, d=0.70, s=0.70, r=0.15, gate=0.95, vib=(0.012, 4.8, 0.30), echo=(4, 0.40, 4)),
    # accompagnement
    "arp":       dict(kind="pulse", duty=0.125, vol=0.09, a=0.002, d=0.14, s=0.10, r=0.05, gate=0.80, vib=None, echo=(3, 0.25, 2)),
    "arp_soft":  dict(kind="pulse", duty=0.25, vol=0.07, a=0.003, d=0.22, s=0.08, r=0.10, gate=0.85, vib=None, echo=(4, 0.30, 3)),
    "pluck":     dict(kind="pulse", duty=0.25, vol=0.10, a=0.002, d=0.16, s=0.05, r=0.06, gate=0.85, vib=None, echo=(3, 0.20, 2)),
    "ostinato":  dict(kind="pulse", duty=0.50, vol=0.07, a=0.002, d=0.10, s=0.30, r=0.03, gate=0.70, vib=None, echo=None),
    "bass":      dict(kind="tri", vol=0.34, a=0.004, d=0.60, s=0.85, r=0.04, gate=0.80, vib=None, echo=None),
    "bass_long": dict(kind="tri", vol=0.30, a=0.02, d=0.90, s=0.90, r=0.12, gate=0.98, vib=None, echo=None),
    "pad":       dict(kind="tri", vol=0.14, a=0.25, d=1.20, s=0.80, r=0.35, gate=1.00, vib=(0.004, 4.0, 0.5), echo=None),
}

DRUM_VOL = {"k": 0.42, "s": 0.26, "h": 0.07, "o": 0.08, "t": 0.30}


def make_drums():
    """Échantillons de batterie, fabriqués une seule fois (bruit à graine fixe)."""
    rng = random.Random(7)
    out = {}
    kick = []
    ph = 0.0
    for i in range(int(0.20 * RATE)):
        t = i / RATE
        ph += (42 + 120 * math.exp(-t * 38)) / RATE
        kick.append(math.sin(2 * math.pi * ph) * math.exp(-t * 17))
    out["k"] = kick
    snare = []
    for i in range(int(0.17 * RATE)):
        t = i / RATE
        snare.append((rng.uniform(-1, 1) * 0.8 + math.sin(2 * math.pi * 190 * t) * 0.5) * math.exp(-t * 24))
    out["s"] = snare
    hat = []
    prev = 0.0
    for i in range(int(0.05 * RATE)):
        t = i / RATE
        n = rng.uniform(-1, 1)
        hat.append((n - prev) * 0.6 * math.exp(-t * 85))
        prev = n
    out["h"] = hat
    opened = []
    prev = 0.0
    for i in range(int(0.22 * RATE)):
        t = i / RATE
        n = rng.uniform(-1, 1)
        opened.append((n - prev) * 0.6 * math.exp(-t * 16))
        prev = n
    out["o"] = opened
    tom = []
    ph = 0.0
    for i in range(int(0.30 * RATE)):
        t = i / RATE
        ph += (70 + 50 * math.exp(-t * 14)) / RATE
        tom.append(math.sin(2 * math.pi * ph) * math.exp(-t * 9))
    out["t"] = tom
    return out


# ---------------------------------------------------------------------------------------------
# Synthèse
# ---------------------------------------------------------------------------------------------
def render_notes(buf, events, inst, step_s):
    """Ajoute dans buf les notes d'une voix. events = [(pas absolu, midi, durée en pas)]."""
    kind = inst["kind"]
    duty = inst.get("duty", 0.5)
    vol = inst["vol"]
    a_s, d_s, sus, r_s = inst["a"], inst["d"], inst["s"], inst["r"]
    gate = inst["gate"]
    vib = inst["vib"]
    size = len(buf)
    decay_k = math.exp(-1.0 / (max(d_s, 1e-3) * RATE))
    two_pi = 2 * math.pi
    for start_step, midi, length in events:
        if midi is None:
            continue
        freq = 440.0 * 2 ** ((midi - 69) / 12)
        s0 = int(round(start_step * step_s * RATE))
        hold = max(1, int(length * step_s * gate * RATE))
        rel = max(1, int(r_s * RATE))
        total = hold + rel
        attack = max(1, int(a_s * RATE))
        phase = 0.0
        x = 1.0
        env_end = 0.0
        vib_depth, vib_rate, vib_delay = vib if vib else (0.0, 0.0, 0.0)
        dt0 = freq / RATE
        for i in range(total):
            idx = s0 + i
            if idx >= size:
                break
            # enveloppe : attaque linéaire, décroissance exponentielle vers le palier, relâchement linéaire
            if i < hold:
                x *= decay_k
                env = sus + (1.0 - sus) * x
                if i < attack:
                    env *= i / attack
                env_end = env
            else:
                env = env_end * (1.0 - (i - hold) / rel)
            if vib_depth and i > vib_delay * RATE:
                dt = dt0 * (1.0 + vib_depth * math.sin(two_pi * vib_rate * (i / RATE - vib_delay)))
            else:
                dt = dt0
            phase += dt
            if phase >= 1.0:
                phase -= 1.0
            if kind == "pulse":
                v = 1.0 if phase < duty else -1.0
                # correction PolyBLEP des deux fronts (moins de repliement de spectre)
                t = phase
                if t < dt:
                    q = t / dt
                    v += q + q - q * q - 1.0
                elif t > 1.0 - dt:
                    q = (t - 1.0) / dt
                    v += q * q + q + q + 1.0
                t = phase - duty
                if t < 0.0:
                    t += 1.0
                if t < dt:
                    q = t / dt
                    v -= q + q - q * q - 1.0
                elif t > 1.0 - dt:
                    q = (t - 1.0) / dt
                    v -= q * q + q + q + 1.0
            else:  # triangle, quantifié sur 32 niveaux comme une vraie puce
                v = 4.0 * abs(phase - 0.5) - 1.0
                v = round(v * 15.5) / 15.5
            buf[idx] += v * env * vol


def render_drums(buf, bars, samples, step_s):
    size = len(buf)
    for b, bar in enumerate(bars):
        if len(bar) != 16:
            raise ValueError("batterie : la mesure « %s » n'a pas 16 caractères" % bar)
        for i, ch in enumerate(bar):
            if ch == ".":
                continue
            s0 = int(round((b * 16 + i) * step_s * RATE))
            gain = DRUM_VOL[ch]
            for j, v in enumerate(samples[ch]):
                if s0 + j >= size:
                    break
                buf[s0 + j] += v * gain


def echo(buf, inst, step_s, loop):
    e = inst["echo"]
    if not e:
        return buf
    delay = int(e[0] * step_s * RATE)
    gain, taps = e[1], e[2]
    out = list(buf)
    n = len(buf)
    for k in range(1, taps + 1):
        g = gain ** k
        d = delay * k
        if loop:
            shifted = buf[-d % n:] + buf[:-d % n] if d % n else buf
        else:
            shifted = [0.0] * d + buf[:n - d]
        out = [o + g * s for o, s in zip(out, shifted)]
    return out


def render_track(spec, drums):
    bpm = spec["bpm"]
    loop = spec["loop"]
    step_s = 60.0 / bpm / 4.0
    bars_count = len(spec["parts"][0][1])
    n = int(round(bars_count * 16 * step_s * RATE))
    size = n + int(TAIL * RATE)
    mix = [0.0] * size
    for part in spec["parts"]:
        name, bars = part[0], part[1]
        gain = part[2] if len(part) > 2 else 1.0
        if len(bars) != bars_count:
            raise ValueError("%s : %d mesures au lieu de %d" % (spec["name"], len(bars), bars_count))
        buf = [0.0] * size
        if name == "drums":
            render_drums(buf, bars, drums, step_s)
        else:
            inst = INSTRUMENTS[name if name in INSTRUMENTS else part[3]]
            events = []
            for b, bar in enumerate(bars):
                for pos, midi, ln in parse_bar(bar, "%s/%s mesure %d" % (spec["name"], name, b + 1)):
                    events.append((b * 16 + pos, midi, ln))
            render_notes(buf, events, inst, step_s)
            if inst["echo"]:
                if loop:
                    buf = fold(buf, n)
                    buf = echo(buf, inst, step_s, True) + [0.0] * (size - n)
                else:
                    buf = echo(buf, inst, step_s, False)
        for i in range(size):
            mix[i] += buf[i] * gain
    if loop:
        out = fold(mix, n)
        # très léger adoucissement circulaire (moyenne avec l'échantillon précédent, y compris au raccord)
        out = [0.62 * out[i] + 0.38 * out[i - 1] for i in range(n)]
    else:
        out = mix
        out = [0.62 * out[i] + 0.38 * out[i - 1] if i else out[0] * 0.62 for i in range(len(out))]
        # on garde 0,8 s de queue (écho, relâchement) puis fondu de sortie
        out = out[:min(len(out), n + int(0.8 * RATE))]
        fade_in = int(0.003 * RATE)
        for i in range(fade_in):
            out[i] *= i / fade_in
        fade_out = int(0.6 * RATE)
        for i in range(fade_out):
            out[len(out) - 1 - i] *= i / fade_out
    return out


def fold(buf, n):
    """Replie ce qui dépasse n sur le début : la fin de la boucle rejoint son début sans coupure."""
    out = buf[:n]
    for i in range(n, len(buf)):
        out[(i - n) % n] += buf[i]
    return out


def normalize(samples):
    rms = math.sqrt(sum(s * s for s in samples) / len(samples))
    scale = RMS_TARGET / rms if rms > 1e-9 else 1.0
    peak = max(abs(s) for s in samples) * scale
    if peak > PEAK_LIMIT:
        scale *= PEAK_LIMIT / peak
    return [s * scale for s in samples]


def write_wav(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(round(s * 32767))))) for s in samples))


def write_import(wav_path, loop):
    """Crée le .import (loop_mode 2 = Forward, 1 = Disabled dans le panneau Import) s'il n'existe pas ; Godot le complétera à l'import."""
    imp = wav_path + ".import"
    if os.path.exists(imp):
        return
    name = os.path.basename(wav_path)
    text = (
        "[remap]\n\nimporter=\"wav\"\ntype=\"AudioStreamWAV\"\n\n"
        "[deps]\n\nsource_file=\"res://audio/musique/%s\"\n\n"
        "[params]\n\nforce/8_bit=false\nforce/mono=false\nforce/max_rate=false\nforce/max_rate_hz=44100\n"
        "edit/trim=false\nedit/normalize=false\nedit/loop_mode=%d\nedit/loop_begin=0\nedit/loop_end=-1\ncompress/mode=0\n"
    ) % (name, 2 if loop else 1)
    with open(imp, "w", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------------------------------------
# PARTITIONS
# ---------------------------------------------------------------------------------------------
def rep(bar, n):
    return [bar] * n


def drum_bars(*groups):
    out = []
    for pattern, count in groups:
        out += [pattern] * count
    return out


TRACKS = {}


def track(name, bpm, loop, parts, description):
    TRACKS[name] = dict(name=name, bpm=bpm, loop=loop, parts=parts, description=description)


# --- 1. TITRE : la mineur, mélancolique, 76 bpm, 16 mesures (~50 s) -------------------------
_c = "Am F C G Am F Dm E F G Am Em F C Dm E7".split()
_m = [
    "E5:6 A5:4 G5:2 E5:4", "F5:6 A5:4 C6:2 A5:4", "G5:6 E5:4 G5:2 C6:4", "B5:8 A5:4 G5:4",
    "E5:6 A5:4 G5:2 E5:4", "F5:6 C6:4 A5:2 F5:4", "D5:4 F5:4 A5:4 D6:4", "E6:8 B5:4 G#5:4",
    "A5:6 C6:4 A5:2 F5:4", "G5:6 B5:4 D6:2 B5:4", "C6:6 B5:2 A5:4 E5:4", "G5:4 B5:4 E6:8",
    "F6:6 E6:2 C6:4 A5:4", "G5:4 C6:4 E6:8", "D6:6 C6:2 A5:4 F5:4", "E5:2 G#5:2 B5:4 D6:4 B5:4",
]
track("titre", 76, True, [
    ("lead25", _m, 1.0, "lead25"),
    ("arp_soft", arp_tokens(_c, ["0:2 1:2 2:2 3:2 2:2 1:2 0:2 1:2"], 4)),
    ("bass_long", bass_tokens(_c, ["r:8 5:8"])),
    ("pad", arp_tokens(_c, ["1:16"], 4), 0.8, "pad"),
], "calme et mélancolique, mélodie lente en la mineur, sans batterie")

# --- 2. OVERWORLD : do majeur, aventure enjouée, 132 bpm, 24 mesures (~44 s) ------------------
_A = ["C", "C", "F", "G", "Am", "Em", "F", "G"]
_B = ["Am", "F", "C", "G", "Am", "F", "G", "G"]
_c = _A + _A + _B
_mA = [
    "G5:4 C6:2 C6:2 E6:4 D6:2 C6:2", "D6:4 G5:4 G5:8", "A5:4 C6:2 C6:2 F6:4 E6:2 D6:2", "D6:6 B5:2 G5:8",
    "A5:4 C6:2 E6:2 A6:4 G6:2 E6:2", "G6:4 E6:4 B5:8", "A5:4 C6:4 F6:4 A6:4", "G6:6 F6:2 D6:4 B5:4",
]
_mA2 = _mA[:4] + [
    "E6:4 C6:2 A5:2 E6:4 C6:2 A5:2", "G5:4 B5:4 E6:8", "F6:4 E6:2 D6:2 C6:4 A5:4", "D6:4 G6:4 B5:8",
]
_mB = [
    "E6:3 E6:3 D6:2 C6:4 A5:4", "C6:3 C6:3 A5:2 F5:4 A5:4", "E6:3 E6:3 G6:2 E6:4 C6:4", "D6:3 D6:3 B5:2 G5:8",
    "A5:2 C6:2 E6:2 A6:2 G6:4 E6:4", "F6:3 F6:3 E6:2 D6:2 C6:6", "B5:2 D6:2 G6:4 F6:2 E6:2 D6:4", "D6:4 G5:2 B5:2 D6:8",
]
_dr = drum_bars(("k.h.s.h.k.h.s.hh", 1), ("k.h.s.h.k.h.s.h.", 1))
track("overworld", 132, True, [
    ("lead_dur", _mA + _mA2 + _mB, 1.0, "lead_dur"),
    ("arp", arp_tokens(_c, ["0:2 2:2 1:2 2:2 0:2 2:2 1:2 2:2", "0:2 2:2 4:2 2:2 1:2 3:2 5:2 3:2"], 4), 0.7, "arp"),
    ("bass", bass_tokens(_c, ["r:2 r:2 8:2 r:2 r:2 5:2 8:2 5:2"])),
    ("drums", (_dr * 12)),
], "aventure enjouée, thème héroïque en do majeur, batterie légère")

# --- 3. VILLAGE : sol majeur, calme et chaleureux, 96 bpm, 16 mesures (~40 s) ----------------
_c = "G Em C D G Bm C D Em D C G Am D G D".split()
_m = [
    "B5:4 D6:4 G6:4 D6:4", "E6:6 D6:2 B5:4 G5:4", "E6:4 G6:6 E6:2 C6:4", "A5:4 D6:4 F#6:4 A6:4",
    "G6:6 F#6:2 E6:4 D6:4", "D6:4 F#6:4 B6:4 F#6:4", "C6:4 E6:4 G6:6 E6:2", "F#6:4 E6:4 D6:8",
    "E6:4 G6:4 B6:6 G6:2", "A6:4 F#6:4 D6:4 A5:4", "G6:4 E6:4 C6:4 E6:4", "D6:4 B5:4 G5:8",
    "A5:4 C6:4 E6:6 C6:2", "F#6:4 A6:4 D6:8", "B5:4 D6:4 G6:8", "A5:4 C#6:4 D6:4 F#6:4",
]
track("village", 96, True, [
    ("flute", _m, 1.0, "flute"),
    ("pluck", arp_tokens(_c, ["0:2 1:2 2:2 1:2 0:2 1:2 2:2 1:2"], 4)),
    ("bass", bass_tokens(_c, ["r:4 x:2 5:2 r:4 x:2 5:2"])),
    ("drums", rep("....h.......h.h.", 16), 0.8),
], "calme et chaleureux, air champêtre en sol majeur")

# --- 4. DONJON : ré mineur, mystérieux, 92 bpm, 16 mesures (~42 s) ---------------------------
_c = "Dm Dm Bb A Dm Gm Bb A Dm Dm Bb C Gm A Bb A".split()
_m = [
    "r:4 D5:4 F5:4 A5:4", "G5:6 F5:2 E5:8", "D5:4 F5:4 Bb5:8", "A5:6 G5:2 C#5:4 E5:4",
    "r:4 D5:4 F5:4 A5:4", "Bb5:6 A5:2 G5:4 D5:4", "F5:4 D5:4 Bb4:4 D5:4", "C#5:4 E5:4 A5:4 r:4",
    "D6:8 A5:4 F5:4", "E5:2 F5:2 G5:4 A5:8", "Bb5:6 A5:2 F5:8", "G5:4 E5:4 C5:8",
    "D5:4 G5:4 Bb5:8", "A5:4 E5:4 C#5:4 E5:4", "D5:4 F5:6 E5:2 D5:4", "C#5:6 D5:2 E5:4 r:4",
]
track("donjon", 92, True, [
    ("sombre", _m, 1.0, "sombre"),
    ("arp_soft", arp_tokens(_c, ["0:4 2:4 1:4 2:4", "x:2 0:2 2:4 x:2 1:2 2:4"], 3), 0.9, "arp_soft"),
    ("bass_long", bass_tokens(_c, ["r:12 5:4", "r:8 r:4 3:4"])),
    ("pad", arp_tokens(_c, ["2:16"], 3), 0.7, "pad"),
    ("drums", drum_bars(("t.........t.....", 1), ("................", 1)) * 8, 0.7),
], "mystérieux, tension douce, ré mineur, échos")

# --- 5. BOSS : mi mineur, rapide et intense, 168 bpm, 28 mesures (~40 s) ---------------------
_cA = ["Em", "Em", "C", "D", "Em", "Em", "C", "B"]
_cB = ["Am", "Am", "Em", "Em", "C", "D", "Bm", "B"]
_cC = ["Em", "Em", "C", "B"]
_c = _cA + _cB + _cA + _cC
_mA = [
    "E5:2 E5:2 G5:2 E5:2 B5:4 A5:2 G5:2", "E5:2 E5:2 G5:2 E5:2 B5:4 D6:4", "C6:2 C6:2 E6:2 C6:2 G5:4 E5:4", "D6:2 D6:2 F#6:2 D6:2 A6:4 F#6:4",
    "B5:2 E6:2 G6:2 E6:2 B6:4 G6:4", "E6:2 D6:2 B5:2 G5:2 E5:8", "G5:2 C6:2 E6:2 G6:2 E6:4 C6:4", "F#6:2 D#6:2 B5:2 F#5:2 B5:8",
]
_mB = [
    "A5:4 C6:2 E6:2 A6:4 E6:4", "C6:2 E6:2 A6:2 E6:2 C6:4 A5:4", "B5:4 E6:2 G6:2 B6:4 G6:4", "G6:2 E6:2 B5:2 E6:2 G6:8",
    "E6:4 G6:2 E6:2 C6:4 G5:4", "A5:2 D6:2 F#6:2 A6:2 F#6:4 D6:4", "B5:2 D6:2 F#6:2 B6:2 F#6:4 D6:4", "D#6:2 F#6:2 B6:2 F#6:2 D#6:4 B5:4",
]
_mC = ["E6:8 G6:8", "B6:8 G6:8", "E6:4 G6:4 E6:4 C6:4", "B5:2 D#6:2 F#6:2 B6:2 B6:8"]
_dA = "k.h.s.hhk.k.s.h."
_dF = "k.h.s.hhk.s.s.sk"
_drums = drum_bars((_dA, 7), (_dF, 1), (_dA, 7), (_dF, 1), (_dA, 7), (_dF, 1), ("k...k...k...k.kk", 1), ("k.s.k.s.kkssksks", 1), ("k.h.s.hhk.k.s.h.", 1), ("k.s.k.s.k.k.ssss", 1))
track("boss", 168, True, [
    ("lead25", _mA + _mB + _mA + _mC, 1.0, "lead25"),
    ("ostinato", arp_tokens(_c, ["0:1 2:1 1:1 2:1 0:1 2:1 1:1 2:1 0:1 2:1 1:1 2:1 0:1 2:1 1:1 2:1"], 4), 1.0, "ostinato"),
    ("bass", bass_tokens(_c, ["r:2 r:2 r:2 8:2 r:2 r:2 5:2 8:2"])),
    ("drums", _drums),
], "rapide et intense, mi mineur, batterie à double temps")

# --- 6. COMBAT FINAL : ré mineur, épique et sombre, 150 bpm, 28 mesures (~45 s) --------------
_cA = ["Dm", "Dm", "Bb", "C", "Dm", "Dm", "Bb", "A"]
_cB = ["Gm", "Gm", "Dm", "Dm", "Bb", "C", "A", "A"]
_cC = ["Dm", "Bb", "Gm", "A"]
_c = _cA + _cB + _cA + _cC
_mA = [
    "A5:6 D6:4 C6:2 A5:4", "F5:2 A5:2 D6:4 F6:8", "Bb5:6 D6:4 C6:2 Bb5:4", "C6:4 E6:4 G6:8",
    "A5:6 D6:4 C6:2 A5:4", "D6:4 F6:4 A6:8", "G6:4 F6:4 D6:4 Bb5:4", "A5:2 C#6:2 E6:4 A6:8",
]
_mB = [
    "G5:2 Bb5:2 D6:2 G6:2 D6:4 Bb5:4", "Bb5:2 D6:2 G6:2 Bb6:2 G6:8", "A5:2 D6:2 F6:2 A6:2 F6:4 D6:4", "D6:2 E6:2 F6:2 G6:2 A6:8",
    "F6:4 D6:4 Bb5:4 D6:4", "E6:4 G6:4 E6:4 C6:4", "C#6:4 E6:4 A6:4 E6:4", "E6:2 F6:2 E6:2 C#6:2 A5:8",
]
_mC = ["F6:8 D6:8", "D6:8 Bb5:8", "G5:4 Bb5:4 D6:8", "E6:4 C#6:4 A5:8"]
_drums = drum_bars(("k...s...k.k.s...", 8), ("k.k.s.k.k.k.s.kk", 8), ("k...s...k.k.s...", 7), ("k.s.k.s.ksksksss", 1), ("k.......t.t.t.t.", 4))
track("combat_final", 150, True, [
    ("sombre", _mA + _mB + _mA + _mC, 1.2, "sombre"),
    ("lead25", [b for b in (["r:16"] * 8 + _mB + ["r:16"] * 12)], 0.5, "lead25"),
    ("ostinato", arp_tokens(_c, ["0:1 0:1 3:1 0:1 0:1 0:1 3:1 0:1 0:1 0:1 3:1 0:1 2:1 2:1 4:1 2:1"], 3), 1.0, "ostinato"),
    ("bass", bass_tokens(_c, ["r:2 r:2 8:2 r:2 r:2 r:2 8:2 r:2"])),
    ("pad", arp_tokens(_c, ["1:16"], 4), 1.0, "pad"),
    ("drums", _drums),
], "épique et plus sombre, ré mineur, cite le thème du titre")

# --- 7. VICTOIRE : jingle do majeur, 140 bpm, 3 mesures (~5 s), non bouclé -------------------
_c = ["C", "G", "C"]
track("victoire", 140, False, [
    ("lead_dur", ["G5:3 G5:1 G5:2 G5:2 C6:8", "B5:3 B5:1 B5:2 B5:2 D6:8", "E6:2 D6:2 C6:2 G6:2 C7:8"], 1.0, "lead_dur"),
    ("arp", arp_tokens(_c, ["0:1 1:1 2:1 3:1 4:1 3:1 2:1 1:1 0:1 1:1 2:1 3:1 4:1 3:1 2:1 1:1"], 4), 0.9, "arp"),
    ("bass", bass_tokens(_c, ["r:4 r:4 5:4 8:4", "r:4 r:4 5:4 8:4", "r:8 8:8"])),
    ("drums", ["k.k.k.k.kkkkkkkk", "k...s...k...s...", "k...............s"][:2] + ["k..............."], 0.9),
], "jingle de victoire, court et triomphant, non bouclé")

# --- 8. GAME OVER : jingle la mineur, 80 bpm, 2 mesures (~6 s), non bouclé --------------------
_c = ["F", "Am"]
track("game_over", 80, False, [
    ("sombre", ["A5:4 G5:4 F5:4 E5:4", "D5:4 C5:4 A4:8"], 1.1, "sombre"),
    ("arp_soft", arp_tokens(_c, ["0:4 1:4 2:4 1:4"], 3), 0.9, "arp_soft"),
    ("bass_long", bass_tokens(_c, ["r:16", "r:16"])),
    ("drums", ["t...............", "................"], 1.0),
], "triste, descente en la mineur, non bouclé")

# --- 9. FIN / GÉNÉRIQUE : do majeur, douce et nostalgique, 72 bpm, 18 mesures (~60 s) ---------
_c = "C Em Am F C G Am G F C G Am F C Dm G F G7".split()
_m = [
    "G5:6 C6:4 B5:2 G5:4", "E5:4 G5:4 B5:6 A5:2", "C6:6 E6:4 D6:2 C6:4", "A5:6 C6:4 A5:2 F5:4",
    "G5:6 C6:4 B5:2 G5:4", "D6:4 B5:4 G5:4 B5:4", "C6:4 E6:6 D6:2 C6:4", "B5:8 D6:8",
    "A5:4 C6:4 F6:6 E6:2", "E6:8 G6:4 E6:4", "D6:6 B5:2 G5:4 B5:4", "A5:4 C6:4 E6:8",
    "F6:6 E6:2 C6:4 A5:4", "G5:4 C6:4 E6:4 G6:4", "F6:4 D6:4 A5:8", "G5:4 B5:4 D6:8",
    "A5:6 C6:2 F6:8", "G6:6 F6:2 D6:4 B5:4",
]
track("fin_generique", 72, True, [
    ("flute", _m, 1.0, "flute"),
    ("pluck", arp_tokens(_c, ["0:2 1:2 2:2 3:2 2:2 1:2 0:2 1:2"], 4), 0.8, "pluck"),
    ("bass_long", bass_tokens(_c, ["r:8 5:8"])),
    ("pad", arp_tokens(_c, ["0:16"], 4), 0.9, "pad"),
], "douce et nostalgique, reprend le thème du titre en majeur")


# ---------------------------------------------------------------------------------------------
def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--liste" in argv:
        for name, spec in TRACKS.items():
            bars = len(spec["parts"][0][1])
            sec = bars * 16 * 60.0 / spec["bpm"] / 4.0
            print("%-14s %5.1f s  %s  %s" % (name, sec, "boucle " if spec["loop"] else "jingle ", spec["description"]))
        return 0
    wanted = [a for a in argv if not a.startswith("-")] or list(TRACKS)
    unknown = [w for w in wanted if w not in TRACKS]
    if unknown:
        print("Pistes inconnues :", ", ".join(unknown), "(voir --liste)")
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    drums = make_drums()
    for name in wanted:
        spec = TRACKS[name]
        samples = normalize(render_track(spec, drums))
        path = os.path.join(OUT_DIR, name + ".wav")
        write_wav(path, samples)
        write_import(path, spec["loop"])
        print("%-14s %5.1f s  %5.0f Ko  crête %.2f" % (name, len(samples) / RATE, os.path.getsize(path) / 1024, max(abs(s) for s in samples)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
