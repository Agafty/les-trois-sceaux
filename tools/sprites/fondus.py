"""Fondus des transitions de terrain des tilesets d'overworld (foret, village, montagne) - Les Trois Sceaux.

Usage : python tools/sprites/fondus.py [foret] [village] [montagne] [route_chateau]   (sans argument : tous)
Ne reecrit QUE les tuiles de transition (wangtiles mixtes) dans le PNG existant (jamais les tuiles pleines, jamais le .tsx).
Les tuiles pleines servent de texture : le raccord avec les transitions est donc sans couture.
Les regles de dessin sont dans fondus_lib.py ; les styles par terrain sont ci-dessous.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fondus_lib import Tileset, transitions, render, quant  # noqa: E402


def herbe_sur(ta, tb, terre_basse=True):
    """Herbe (au-dessus) qui deborde sur de la terre, du sable ou de la roche."""
    g = ta if terre_basse else tb
    return dict(raised='A' if terre_basse else 'B', out=quant(g, 0.0), lip=quant(g, 0.18), out_alt=quant(g, 0.12),
                shadow=(0.68, 0.84), bleed=(0.62, 0.30, 0.10), rbleed=None)


def eau_rive(ta, tb, herbe_a=True):
    """Terre ferme (au-dessus) / eau peu profonde : liseré sombre, ecume claire, ombre portee."""
    land, wat = (ta, tb) if herbe_a else (tb, ta)
    return dict(raised='A' if herbe_a else 'B', out=quant(land, 0.0), lip=quant(land, 0.2), out_alt=quant(land, 0.1),
                shadow=(0.62, 0.8), l1=(quant(wat, 1.0), 0.8), l1b=quant(wat, 0.8), l2=(quant(wat, 0.88), 0.35),
                l3=(quant(wat, 0.88), 0.1))


def eau_profonde(ta, tb):
    """Eau peu profonde / profonde (solide) : degrade tramé sur 3-4 px."""
    return dict(raised='A', solid=True, out=quant(tb, 0.35), lip=quant(ta, 0.55), out_alt=quant(tb, 0.25), out_alt_p=0.5,
                bleed=(0.42, 0.18, 0.06), rbleed=(0.0, 0.0, 0.0), bleed_col=quant(ta, 0.7), seed=3)


def eau_profonde2(ta, tb):
    s = eau_profonde(ta, tb)
    s['rbleed'] = None
    return s


def ravin(ta, tb):
    """Terre / ravin (solide) : levre d'herbe ou de roche, paroi claire sur 1-2 px."""
    return dict(raised='A', solid=True, out=quant(ta, 0.0), lip=quant(ta, 0.22), out_alt=quant(ta, 0.12),
                l1=(quant(tb, 1.0), 1.0), l2=(quant(tb, 0.75), 0.55), shadow=None)


def paves(ta, tb):
    return dict(raised='B', out=quant(tb, 0.0), lip=quant(tb, 0.78), out_alt=quant(tb, 0.2), out_alt_p=0.3,
                shadow=(0.66, 0.84), rbleed=(0.0, 0.28, 0.10))


def sentier(ta, tb):
    """Roche (au-dessus) / sentier de terre."""
    return dict(raised='A', out=quant(ta, 0.0), lip=quant(ta, 1.0), out_alt=quant(ta, 0.1), shadow=(0.72, 0.86),
                bleed=(0.45, 0.22, 0.07))


def neige(ta, tb):
    """Neige (au-dessus) sur roche : flocons semes sur la roche."""
    return dict(raised='B', out=quant(tb, 0.3), lip=quant(tb, 1.0), out_alt=quant(tb, 0.45), shadow=(0.7, 0.84),
                bleed=(0.6, 0.3, 0.1), rbleed=None)


STYLES = {
    'foret': {'Chemin': lambda a, b: herbe_sur(a, b), 'Eau': lambda a, b: eau_rive(a, b),
              'Eau profonde': eau_profonde},
    'village': {'Paves': paves, 'Terre': lambda a, b: herbe_sur(a, b), 'Rive': lambda a, b: eau_rive(a, b),
                'Lac profond': eau_profonde, 'Ravin': ravin},
    'montagne': {'Sentier': sentier, 'HerbeM': lambda a, b: herbe_sur(a, b, False),
                 'Neige': neige, 'Ruisseau': lambda a, b: eau_rive(a, b, True),
                 'Ravin': ravin, 'Torrent': eau_profonde},
}


def patch(name):
    ts = Tileset(name)
    done = []
    for i, pat, ws, ta, tb in transitions(ts):
        st = STYLES[name].get(ws)
        if st is None:
            continue
        ts.put(i, render(pat, ta, tb, st(ta, tb)))
        done.append(i)
    ts.save()
    print(name, len(done), 'tuiles de transition redessinees :', done)


if __name__ == '__main__':
    names = sys.argv[1:] or ['foret', 'village', 'montagne']
    for n in names:
        patch(n)
