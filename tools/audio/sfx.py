#!/usr/bin/env python3
"""Générateur de bruitages rétro (façon jsfxr) pour Les Trois Sceaux.

Python standard uniquement (wave, math, random, struct). Écrit des .wav 16 bits mono 22050 Hz
dans audio/sfx/. Déterministe (graine fixe) : relancer le script donne les mêmes fichiers.

Usage :  python tools/audio/sfx.py            (tous les sons)
         python tools/audio/sfx.py epee rubis (seulement ceux-là)

Pour retoucher un son, modifier sa définition dans SOUNDS puis relancer.
Tous les sons sont normalisés à la même crête (PEAK) et passés dans un filtre doux
pour rester courts et pas agressifs.
"""
import math
import os
import random
import struct
import sys
import wave

RATE = 22050
PEAK = 0.55          # crête commune (volumes homogènes)
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "audio", "sfx")


def note(name):
    """Nom de note (C5, F#4, Bb3) -> fréquence en Hz."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    n = names[name[0]]
    i = 1
    if name[i] == "#":
        n += 1
        i += 1
    elif name[i] == "b":
        n -= 1
        i += 1
    octave = int(name[i:])
    midi = 12 * (octave + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12)


def tone(shape, f0, f1, dur, vol=1.0, duty=0.5, attack=0.005, release=0.04,
         vibrato=0.0, vib_hz=8.0, lowpass=0.0, curve=1.0, rng=None):
    """Un segment : forme d'onde `shape` (square, triangle, saw, sine, noise), glissando f0 -> f1.
    curve > 1 : le glissando est rapide au début. lowpass 0..0.95 : adoucit (0 = aucun)."""
    rng = rng or random
    n = max(1, int(dur * RATE))
    out = []
    phase = 0.0
    prev = 0.0
    held = 0.0
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * (t ** (1.0 / curve))
        if vibrato:
            f *= 1.0 + vibrato * math.sin(2 * math.pi * vib_hz * i / RATE)
        phase = (phase + f / RATE) % 1.0
        if shape == "square":
            s = 1.0 if phase < duty else -1.0
        elif shape == "triangle":
            s = 4.0 * abs(phase - 0.5) - 1.0
        elif shape == "saw":
            s = 2.0 * phase - 1.0
        elif shape == "sine":
            s = math.sin(2 * math.pi * phase)
        elif shape == "noise":
            # bruit "à fréquence" : nouvelle valeur aléatoire quand la phase boucle
            if i == 0 or phase < (f / RATE):
                held = rng.uniform(-1, 1)
            s = held
        else:
            raise ValueError(shape)
        # enveloppe : attaque courte, descente douce, release
        sec = i / RATE
        env = 1.0
        if sec < attack:
            env = sec / attack
        rest = dur - sec
        if rest < release:
            env *= rest / release
        env *= (1.0 - 0.35 * t)  # léger decay naturel
        s *= env * vol
        if lowpass:
            s = prev + (1.0 - lowpass) * (s - prev)
            prev = s
        out.append(s)
    return out


def silence(dur):
    return [0.0] * int(dur * RATE)


def mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    return out


def seq(*parts):
    out = []
    for p in parts:
        out.extend(p)
    return out


def melody(notes, shape="square", step=0.09, duty=0.5, vol=1.0, lowpass=0.35, hold=1.0, last_hold=2.2):
    """Suite de notes (nom, ou None pour un silence) de durée `step`."""
    out = []
    for k, nm in enumerate(notes):
        d = step * (last_hold if k == len(notes) - 1 else hold)
        if nm is None:
            out += silence(step)
        else:
            out += tone(shape, note(nm), note(nm), d, vol, duty, release=min(0.05, d * 0.5), lowpass=lowpass)
    return out


def finish(samples, peak=PEAK, fade=0.01):
    m = max(abs(v) for v in samples) or 1.0
    k = peak / m
    n = len(samples)
    f = int(fade * RATE)
    out = []
    for i, v in enumerate(samples):
        v *= k
        if i > n - f:
            v *= (n - i) / f
        out.append(max(-1.0, min(1.0, v)))
    return out


def write_wav(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(v * 32767)) for v in samples))


# --------------------------------------------------------------------------- sons
def s_epee(r):
    swish = tone("noise", 5000, 1500, 0.11, 0.9, attack=0.01, release=0.06, lowpass=0.7, rng=r)
    ring = tone("triangle", 700, 350, 0.11, 0.35, release=0.06, lowpass=0.3)
    return mix(swish, ring)


def s_coup_ennemi(r):
    return mix(tone("square", 330, 110, 0.1, 0.6, duty=0.25, lowpass=0.5),
               tone("noise", 1800, 600, 0.08, 0.5, lowpass=0.7, rng=r))


def s_ennemi_mort(r):
    return mix(tone("square", 500, 90, 0.28, 0.6, duty=0.5, lowpass=0.55, release=0.08),
               tone("noise", 1500, 300, 0.25, 0.35, lowpass=0.8, rng=r))


def s_brann_touche(r):
    return seq(tone("square", 400, 250, 0.08, 0.7, duty=0.5, lowpass=0.5),
               tone("square", 250, 150, 0.12, 0.7, duty=0.5, lowpass=0.5, release=0.06))


def s_brann_mort(r):
    return seq(melody(["E4", "D4", "C4", "A3"], "triangle", step=0.14, lowpass=0.2, last_hold=1.0),
               tone("triangle", note("A3"), note("E3"), 0.5, 0.9, lowpass=0.2, release=0.3, vibrato=0.02))


def s_rubis(r):
    return seq(tone("square", note("E6"), note("E6"), 0.05, 0.6, duty=0.25, lowpass=0.4),
               tone("square", note("A6"), note("A6"), 0.11, 0.6, duty=0.25, lowpass=0.4, release=0.07))


def s_coeur(r):
    return melody(["C5", "E5", "G5"], "triangle", step=0.07, lowpass=0.15, last_hold=2.5)


def s_cle(r):
    return melody(["G5", "C6", "E6", "G6"], "square", step=0.06, duty=0.25, vol=0.7, lowpass=0.45, last_hold=2.8)


def s_objet_obtenu(r):
    a = melody(["C5", "E5", "G5", "C6", None, "G5", "C6"], "square", step=0.1, duty=0.25, vol=0.6, lowpass=0.45, last_hold=4.0)
    b = melody(["C4", "E4", "G4", "C5", None, "G4", "C5"], "triangle", step=0.1, lowpass=0.2, last_hold=4.0)
    return mix(a, b)


def s_coffre_ouvre(r):
    creak = tone("saw", 140, 260, 0.25, 0.5, lowpass=0.75, vibrato=0.08, vib_hz=18)
    click = tone("noise", 900, 400, 0.03, 0.8, lowpass=0.6, rng=r)
    return seq(click, creak, tone("triangle", note("G5"), note("G5"), 0.08, 0.5, lowpass=0.2))


def s_porte_ouvre(r):
    rumble = tone("noise", 180, 120, 0.4, 0.8, lowpass=0.92, release=0.15, rng=r)
    grind = tone("saw", 80, 110, 0.4, 0.35, lowpass=0.85, release=0.15)
    return mix(rumble, grind)


def s_porte_verrouillee(r):
    return seq(tone("square", 160, 150, 0.06, 0.7, duty=0.5, lowpass=0.7),
               silence(0.04),
               tone("square", 140, 130, 0.08, 0.7, duty=0.5, lowpass=0.7))


def s_fleche_tir(r):
    return mix(tone("noise", 3500, 1200, 0.12, 0.7, lowpass=0.75, attack=0.01, rng=r),
               tone("triangle", 900, 300, 0.1, 0.3, lowpass=0.3))


def s_fleche_impact(r):
    return mix(tone("square", 260, 140, 0.06, 0.6, duty=0.25, lowpass=0.6),
               tone("noise", 1500, 700, 0.05, 0.6, lowpass=0.7, rng=r))


def s_fleche_enflammee(r):
    return mix(tone("noise", 900, 1800, 0.3, 0.7, lowpass=0.8, attack=0.05, release=0.12, rng=r),
               tone("triangle", 300, 700, 0.3, 0.3, lowpass=0.3, vibrato=0.1, vib_hz=25))


def s_bombe_meche(r):
    out = []
    for k in range(8):
        out += tone("noise", 4000 + 400 * k, 3000, 0.035, 0.5, lowpass=0.4, rng=r)
        out += silence(0.02)
    return out


def s_bombe_explosion(r):
    boom = tone("noise", 700, 60, 0.7, 1.0, lowpass=0.93, attack=0.005, release=0.35, rng=r)
    thump = tone("sine", 110, 40, 0.5, 0.9, release=0.25)
    return mix(boom, thump)


def s_interrupteur(r):
    return seq(tone("square", 600, 600, 0.03, 0.6, duty=0.5, lowpass=0.5),
               tone("square", 900, 900, 0.07, 0.6, duty=0.5, lowpass=0.5, release=0.04))


def s_mauvais_ordre(r):
    return seq(tone("square", 220, 220, 0.1, 0.6, duty=0.5, lowpass=0.6),
               tone("square", 165, 165, 0.18, 0.6, duty=0.5, lowpass=0.6, release=0.08))


def s_plaque(r):
    return seq(tone("square", 120, 100, 0.07, 0.7, duty=0.5, lowpass=0.75),
               tone("triangle", note("C5"), note("C5"), 0.08, 0.4, lowpass=0.2))


def s_bloc_pousse(r):
    return mix(tone("noise", 300, 150, 0.22, 0.9, lowpass=0.92, attack=0.03, release=0.1, rng=r),
               tone("saw", 70, 60, 0.22, 0.3, lowpass=0.85))


def s_torche_allume(r):
    return mix(tone("noise", 700, 2200, 0.3, 0.8, lowpass=0.85, attack=0.06, release=0.1, rng=r),
               tone("triangle", note("C5"), note("G5"), 0.25, 0.25, lowpass=0.25, curve=2.0))


def s_chute(r):
    return tone("triangle", 800, 120, 0.55, 1.0, lowpass=0.2, release=0.15)


def s_escalier(r):
    out = []
    for k in range(6):
        out += tone("square", 280 - 12 * k, 200 - 10 * k, 0.045, 0.6, duty=0.25, lowpass=0.65)
        out += silence(0.05)
    return out


def s_sauvegarde(r):
    return melody(["E5", "G5", "B5", "E6"], "triangle", step=0.1, lowpass=0.15, last_hold=3.2)


def s_menu_deplace(r):
    return tone("square", 700, 700, 0.04, 0.5, duty=0.25, lowpass=0.5, release=0.02)


def s_menu_valide(r):
    return seq(tone("square", 700, 700, 0.04, 0.5, duty=0.25, lowpass=0.5, release=0.02),
               tone("square", 1050, 1050, 0.08, 0.5, duty=0.25, lowpass=0.5))


def s_menu_retour(r):
    return seq(tone("square", 600, 600, 0.04, 0.5, duty=0.25, lowpass=0.5, release=0.02),
               tone("square", 400, 400, 0.08, 0.5, duty=0.25, lowpass=0.5))


def s_boss_rugit(r):
    growl = tone("saw", 110, 55, 0.7, 0.8, lowpass=0.9, vibrato=0.12, vib_hz=30, attack=0.08, release=0.25)
    breath = tone("noise", 400, 150, 0.7, 0.5, lowpass=0.93, attack=0.1, release=0.25, rng=r)
    return mix(growl, breath)


def s_boss_charge(r):
    return mix(tone("saw", 90, 400, 0.6, 0.6, lowpass=0.85, attack=0.1, release=0.1, curve=0.6),
               tone("noise", 300, 1500, 0.6, 0.4, lowpass=0.9, attack=0.1, release=0.1, rng=r))


def s_boss_assomme(r):
    out = []
    for k in range(3):
        out += tone("triangle", 520 - 40 * k, 380 - 40 * k, 0.16, 0.7, lowpass=0.2, vibrato=0.15, vib_hz=14)
    return out


def s_boss_vaincu(r):
    a = melody(["C5", "G4", "C5", "E5", "G5", "C6", "G5", "C6"], "square", step=0.11, duty=0.25, vol=0.55, lowpass=0.5, last_hold=5.0)
    b = melody(["C3", "C3", "C3", "C3", "C3", "C3", "C3", "C3"], "triangle", step=0.11, lowpass=0.2, last_hold=5.0)
    boom = tone("noise", 500, 100, 0.4, 0.5, lowpass=0.9, release=0.2, rng=r)
    return mix(a, b, boom)


def s_sceau(r):
    a = melody(["E5", "G#5", "B5", "E6", "G#5", "B5", "E6", "G#6"], "triangle", step=0.12, lowpass=0.15, last_hold=5.0)
    b = melody(["E4", None, "B4", None, "E5", None, "B5", None], "sine", step=0.12, last_hold=6.0, lowpass=0.0)
    return mix(a, b)


def s_buisson(r):
    # Un buisson coupé : froissement de feuilles (bruit aigu qui retombe) et petit « chuk » de lame.
    leaves = tone("noise", 4200, 1800, 0.2, 0.9, attack=0.01, release=0.12, lowpass=0.55, rng=r)
    cut = tone("triangle", 520, 300, 0.07, 0.35, release=0.04, lowpass=0.3)
    return mix(leaves, cut)


def s_texte(r):
    # Petit « bip » de voix pour le texte qui défile (très court : il est joué une lettre sur deux).
    return tone("square", 520, 470, 0.03, 0.35, duty=0.25, lowpass=0.6, attack=0.002, release=0.015)


SOUNDS = {
    "epee": s_epee, "coup_ennemi": s_coup_ennemi, "ennemi_mort": s_ennemi_mort,
    "brann_touche": s_brann_touche, "brann_mort": s_brann_mort,
    "rubis": s_rubis, "coeur": s_coeur, "cle": s_cle, "objet_obtenu": s_objet_obtenu,
    "coffre_ouvre": s_coffre_ouvre, "porte_ouvre": s_porte_ouvre, "porte_verrouillee": s_porte_verrouillee,
    "fleche_tir": s_fleche_tir, "fleche_impact": s_fleche_impact, "fleche_enflammee": s_fleche_enflammee,
    "bombe_meche": s_bombe_meche, "bombe_explosion": s_bombe_explosion,
    "interrupteur": s_interrupteur, "mauvais_ordre": s_mauvais_ordre, "plaque": s_plaque,
    "bloc_pousse": s_bloc_pousse, "torche_allume": s_torche_allume,
    "chute": s_chute, "escalier": s_escalier, "sauvegarde": s_sauvegarde,
    "menu_deplace": s_menu_deplace, "menu_valide": s_menu_valide, "menu_retour": s_menu_retour,
    "boss_rugit": s_boss_rugit, "boss_charge": s_boss_charge, "boss_assomme": s_boss_assomme,
    "boss_vaincu": s_boss_vaincu, "sceau": s_sceau, "texte": s_texte, "buisson": s_buisson,
}


def hash_name(name):
    h = 17
    for c in name:
        h = (h * 31 + ord(c)) & 0xFFFFFF
    return h


def main(argv):
    wanted = argv or list(SOUNDS)
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in wanted:
        if name not in SOUNDS:
            print("Son inconnu :", name)
            return 1
        rng = random.Random(hash_name(name))
        data = finish(SOUNDS[name](rng))
        write_wav(os.path.join(OUT_DIR, name + ".wav"), data)
        print("%-20s %.2f s" % (name, len(data) / RATE))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
