"""Tilesets du Sanctuaire Englouti (donjon 3) — Les Trois Sceaux. ÉTAT : PLAN (aplats lisibles, numéros définitifs).

Usage : python tools/sprites/sanctuaire.py
Produit : art/tilesets/sanctuaire.png, sanctuaire_numeros.png, sanctuaire_crypte.png, sanctuaire_crypte_numeros.png,
          art/tilesets/sanctuaire_plan.md, maps/tilesets/sanctuaire.tsx, maps/tilesets/sanctuaire_crypte.tsx.
Deux planches de même numérotation : rez-de-chaussée (bleu, pierre claire) et cryptes (recoloration plus sombre).
DISPOSITION : comme `mine` / `temple_racines` pour ce que le code reconnaît : murs 16-30, portes 40-47, escaliers 56/57,
eau peu profonde 80-92 ; ids 31-39 et 58-66 VIDES (ce donjon n'a ni fosse ni trou de passage).
RÈGLE : ne jamais déplacer une tuile ; on ajoute dans les lignes de réserve (à la fin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplan import *  # noqa: E402,F401,F403
import tsplan  # noqa: E402

tsplan.CATS.update(
    dalle='#7c88a8', crypte='#4a5878', mur='#5e6290', eau='#4aa0d0', profonde='#1c3a8a', planches='#9a7048', chaussee='#a8a8b8',
    escalier='#d0c090', colonne='#8a8ab0', rune='#40e0f0', secret='#a040e0', porte='#e8782c', algue='#40d890', deco='#b0a0c0',
    ombre='#3a3858', balcon='#c070a0', estrade='#c8a860', bassin='#6ac8e0')

FAMILLES = ('dalle (bleu-gris) / crypte (bleu sombre) / mur (violet-gris) / eau peu profonde (bleu clair) / eau profonde (bleu foncé) / '
            'planches (brun) / chaussée (gris clair) / escalier (beige) / colonne (gris-bleu) / rune (cyan) / fissuré à la bombe (violet) / '
            'porte (orange) / algues lumineuses (vert) / balcon (rose) / estrade (or) / bassin (turquoise)')

DEV = """
## POUR LE DÉVELOPPEUR ET LE LEVEL-DESIGNER : ids à connaître

Tilesets `sanctuaire` (rez-de-chaussée) ET `sanctuaire_crypte` (sous-sol) : **mêmes ids, mêmes collisions**, 8 colonnes, id local Tiled = ligne × 8 + colonne.

| Famille | Ids | Calque | À savoir |
| --- | --- | --- | --- |
| **MURS FISSURÉS** fermé -> ouvert (`TileRules`, salle 03) | **72 -> 76** (haut), **73 -> 77** (bas), **74 -> 78** (gauche), **75 -> 79** (droite) | fermés `Murs`, ouverts `Decor` | Comme `mine` 144 -> 148 : la bombe retire la tuile fermée de `Murs`, le code pose la version ouverte sur `Decor` (ou elle est déjà posée dessous). Les versions ouvertes sont opaques (fond noir). La salle 03 n'utilise qu'une orientation (le mur de l'alcôve est vertical : 74 ou 75). |
| **Escaliers** | 56 (montant), 57 (descendant) | `Sol` | Posent une `Sortie` `transition=escalier`, comme les autres donjons. |
| **Ids VIDES** | 31 à 39 et 58 à 66 | — | Réservés (trous de passage / trous mortels des autres donjons). Aucun trou dans ce donjon : **`HoleRules` / `HoleWatcher` n'ont rien à reconnaître ici** (ne pas y ajouter les tilesets `sanctuaire*`). |
| **EAU PROFONDE (solide)** | 96 à 111 | `Murs` | Terrain `Eau profonde` : collision par quarts de case (la moitié « rive » d'un bord reste praticable), flèches arrêtées comme par un mur. Se peint sur `Murs` ; dessous, mettre du sol. |
| **EAU PEU PROFONDE (praticable)** | 80 à 95 | `Sol` | Terrain `Eau`, sans collision, comme `mine`. |
| **PASSERELLES / CHAUSSÉE** | 48 à 55 | `Sol` | Praticables, sans collision. Posées sur `Sol` aux cases où l'on ne peint pas d'eau profonde sur `Murs` : la passerelle de 3 cases de large coupe le fossé. |
| **BALCON** de Corvan (salle 08) | 67 à 69, garde-corps 70 | `Murs` (67-69), `Dessus` (70) | Solide, inaccessible. |
| **MUR À RUNE** (`Porte` type `lanterne`) | tuile dessous : 144 `alcove_sol_rune` | `Sol` | L'image `art/puzzles/porte_mur_rune.png` (64×32 : fermée, ouverte) est posée par la `Porte`. Mur autour : 145 `mur_rune_grave` (indice discret, solide). |
| Piliers 2×2 du boss | 120 à 123 | `Murs` | Solides ; les rectangles `pilier` restent la référence du boss. |
| Bassins d'Ondine (3×3) | 128 à 136 (+ anneau 137/138 sur `Decor`) | `Sol` | Eau peu profonde, praticable. |

Tout le reste est géré par les collisions du `.tsx` (murs 16-30, portes 40-43, 67-69, 72-75, 96-110 et 111, 113-116, 120-123, 145-149, 151) : aucun code.
"""

TERRAINS = """## Terrains (Wang, par coins)

Dans Tiled : panneau **Terrains**, choisir le terrain puis le pinceau de terrain (T).

| Terrain | Couleurs | Calque | Tuiles |
| --- | --- | --- | --- |
| `Murs` | `mur` (le reste = vide) | Murs | 16 à 30 |
| `Eau` | `sol`, `eau` | Sol | 0 à 2 (sol), 80 à 94 (93-94 = pleines, au hasard avec 80) |
| `Eau profonde` | `profonde` (le reste = vide) | **Murs** | 96 à 110 (111 = variante pleine) |

"""


class SancSheet(Sheet):
    def md(self, script):
        w, self.wang = self.wang, {}
        try:
            o = super().md(script)
        finally:
            self.wang = w
        o = o.replace('\n## Calques', DEV + '\n## Calques', 1)
        o = o.replace('## Notes', TERRAINS + '## Notes', 1)
        return o


S = SancSheet('sanctuaire', 8, 'Le Sanctuaire Englouti (donjon 3 : pierre à demi noyée, eau, passerelles, cryptes, arène d\'Ondine)',
              ['- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d\'1 px. Palette finale : pierre gris-violet et bleus-verts froids '
               '(comme la façade du Sanctuaire dans `lac`). En PLAN, **la couleur indique la famille** (' + FAMILLES + ') ; une zone plus sombre '
               'dans une tuile = zone solide.',
               '- DEUX planches de même numérotation : `sanctuaire.png` (rez-de-chaussée, clair) et `sanctuaire_crypte.png` (cryptes : recoloration '
               'plus sombre ; tileset `sanctuaire_crypte.tsx` identique). Dans le dessin final, la crypte aura des algues lumineuses aux murs.',
               '- **Aucune fosse ni trou** dans ce donjon : les ids 31 à 39 et 58 à 66 sont volontairement vides.'],
              ['`Sol` : dalles, sol de crypte, eau peu profonde, passerelles et chaussée, escaliers, estrade, bassins d\'Ondine',
               '`Decor` : algues lumineuses, coquillages, ombres, lueurs, anneaux d\'ondes, ouvertures de mur fissuré (version ouverte)',
               '`Murs` : tout ce qui bloque (murs, eau profonde, colonnes, piliers, vasques, balcon, murs fissurés fermés). Collisions dans le tileset',
               '`Objets` : Sortie, Spawn, Ennemi, Coffre, Porte, MurFissure, Torche, boss_ondine, pilier… (objets Tiled, pas des tuiles)',
               '`Dessus` : passe devant Brann (haut de colonne, algues et fresques plaquées sur les murs, garde-corps du balcon)'])
S.reserve = 4

PIL2 = [(2, 2, 30, 30)]
PIL2R = [(0, 2, 30, 30)]
PIL2B = [(2, 0, 30, 30)]
PIL2BR = [(0, 0, 30, 30)]
DOORH = [(0, 0, 6, 32), (26, 0, 6, 32)]
DOORV = [(0, 0, 32, 4), (0, 28, 32, 4)]


def at(i, nom, role, calque, coll, cat, **k):
    S.cur = i
    return S.add(nom, role, calque, coll, cat, **k)


def grp(first, titre, note=''):
    S.cur = first
    S.group(titre, note)


def so(i, nom, role, cat='dalle', **k):
    at(i, nom, role, 'Sol', None, cat, **k)


def de(i, nom, role, cat='deco', **k):
    at(i, nom, role, 'Decor', None, cat, **k)


def mu(i, nom, role, coll, cat, **k):
    at(i, nom, role, 'Murs', coll, cat, **k)


def du(i, nom, role, cat='deco', coll=None, **k):
    at(i, nom, role, 'Dessus', coll, cat, **k)


def bi(b):
    return b[0] * 8 + b[1] * 4 + b[2] * 2 + b[3]


def edge(i, nom, role, catA, catB, bits, calque='Sol', coll=None):
    at(i, nom, role, calque, coll, catB, plan=('terrain', bi(bits), catA, catB))


EDGES9 = {'haut': (0, 0, 1, 1), 'bas': (1, 1, 0, 0), 'gauche': (0, 1, 0, 1), 'droite': (1, 0, 1, 0),
          'coin_hg': (0, 0, 0, 1), 'coin_hd': (0, 0, 1, 0), 'coin_bg': (0, 1, 0, 0), 'coin_bd': (1, 0, 0, 0)}
CREUX = {'creux_hg': (0, 1, 1, 1), 'creux_hd': (1, 0, 1, 1), 'creux_bg': (1, 1, 0, 1), 'creux_bd': (1, 1, 1, 0)}
FULL4 = (1, 1, 1, 1)

# ------------------------------------------------------------------ 1. sols
grp(0, 'Sols, algues, ombres', 'Rez-de-chaussée : dalles de pierre mouillée (0 à 3, au hasard), dalle gravée du sceau effacé (4, décor du Parvis), dalle à algues (5). '
    'Cryptes : sol bleu-gris (6 à 9). Algues lumineuses et coquillages sur `Decor`. Ombres 12 à 14 sous les murs (`Decor`).')
so(0, 'dalle_a', 'Dalle de pierre mouillée, de base (bleu-gris)')
so(1, 'dalle_b', 'Dalle de pierre mouillée avec reflets')
so(2, 'dalle_c', 'Dalle de pierre en joints irréguliers')
so(3, 'dalle_fissuree', 'Dalle fissurée (fissure en diagonale)')
so(4, 'dalle_sceau', 'Dalle gravée d\'un sceau effacé (centre du Parvis, une seule fois)')
so(5, 'dalle_algues', 'Dalle recouverte d\'algues vertes (variante de sol)', 'algue')
so(6, 'crypte_a', 'Sol de crypte bleu-gris, de base', 'crypte')
so(7, 'crypte_b', 'Sol de crypte avec petits cailloux', 'crypte')
so(8, 'crypte_c', 'Sol de crypte en dalles brisées', 'crypte')
so(9, 'crypte_d', 'Sol de crypte avec algues lumineuses discrètes', 'crypte')
de(10, 'algues_lum_a', 'Algues lumineuses au sol (guide visuel, décor)', 'algue')
de(11, 'algues_lum_b', 'Algues lumineuses au sol, variante (décor)', 'algue')
de(12, 'ombre_mur_haut', 'Ombre portée d\'un mur du haut sur le sol (trame), sous un mur_haut', 'ombre')
de(13, 'ombre_mur_gauche', 'Ombre portée d\'un mur de gauche sur le sol', 'ombre')
de(14, 'ombre_mur_coin', 'Ombre portée dans un angle haut-gauche (mur en haut et à gauche)', 'ombre')
de(15, 'coquillages', 'Coquillages et petits cailloux posés au sol', 'deco')

# ------------------------------------------------------------------ 2. murs
grp(16, 'Murs de pierre à demi noyée (terrain `Murs`)', 'Pierre taillée, dessus sombre + face avant plus claire visible (algues au pied). Toutes les tuiles sont pleines. '
    'Mêmes numéros et mêmes formes que `mine` / `temple_racines` (16 à 30).')
WALLS = {16: ('mur_haut', 'Mur du haut de la salle : sol en dessous, face avant visible', (1, 1, 0, 0)),
         17: ('mur_bas', 'Mur du bas de la salle : sol au-dessus', (0, 0, 1, 1)),
         18: ('mur_gauche', 'Mur de gauche de la salle : sol à droite', (1, 0, 1, 0)),
         19: ('mur_droite', 'Mur de droite de la salle : sol à gauche', (0, 1, 0, 1)),
         20: ('mur_coin_int_hg', 'Coin intérieur haut-gauche (angle de salle) : sol seulement en bas-droite', (1, 1, 1, 0)),
         21: ('mur_coin_int_hd', 'Coin intérieur haut-droite (angle de salle) : sol seulement en bas-gauche', (1, 1, 0, 1)),
         22: ('mur_coin_int_bg', 'Coin intérieur bas-gauche (angle de salle) : sol seulement en haut-droite', (1, 0, 1, 1)),
         23: ('mur_coin_int_bd', 'Coin intérieur bas-droite (angle de salle) : sol seulement en haut-gauche', (0, 1, 1, 1)),
         24: ('mur_coin_ext_hg', 'Coin extérieur haut-gauche d\'un bloc de mur posé dans la salle : mur seulement en bas-droite', (0, 0, 0, 1)),
         25: ('mur_coin_ext_hd', 'Coin extérieur haut-droite d\'un bloc de mur : mur seulement en bas-gauche', (0, 0, 1, 0)),
         26: ('mur_coin_ext_bg', 'Coin extérieur bas-gauche d\'un bloc de mur : mur seulement en haut-droite', (0, 1, 0, 0)),
         27: ('mur_coin_ext_bd', 'Coin extérieur bas-droite d\'un bloc de mur : mur seulement en haut-gauche', (1, 0, 0, 0)),
         28: ('mur_plein', 'Mur plein (intérieur d\'un mur épais, rien de visible autour)', (1, 1, 1, 1)),
         29: ('mur_diag_a', 'Mur en diagonale (mur en haut-gauche et bas-droite) — complète le terrain', (1, 0, 0, 1)),
         30: ('mur_diag_b', 'Mur en diagonale (mur en haut-droite et bas-gauche) — complète le terrain', (0, 1, 1, 0))}
for i, (n, r, b) in WALLS.items():
    mu(i, n, r, FULL, 'mur')
S.wang['Murs'] = dict(colors=[('mur', tsplan.CATS['mur'])], tile=28, fam='',
                      tiles={i: tuple(1 if k else 0 for k in b) for i, (n, r, b) in WALLS.items()})

# ------------------------------------------------------------------ 3. ids réservés (31-39 vides)
grp(31, 'Ids réservés : 31 à 39 (vides)', 'Trous de passage des autres donjons : ce donjon n\'en a pas, ces cases restent VIDES (ne rien y dessiner).')

# ------------------------------------------------------------------ 4. portes
grp(40, 'Ouvertures de salle (cadre de pierre)', 'Remplacer la tuile de mur par `porte_<côté>` (calque Murs), poser `porte_<côté>_dessus` dans la même case du calque '
    '`Dessus`, puis l\'objet `Porte` par-dessus. Mêmes numéros et mêmes collisions que `mine`.')
mu(40, 'porte_haut', 'Ouverture dans le mur haut (remplace une tuile mur_haut) ; passage de 20 px au centre, l\'objet Porte se pose dessus', DOORH, 'porte')
mu(41, 'porte_bas', 'Ouverture dans le mur bas (remplace une tuile mur_bas) ; passage de 20 px au centre, l\'objet Porte se pose dessus', DOORH, 'porte')
mu(42, 'porte_gauche', 'Ouverture dans le mur gauche (remplace une tuile mur_gauche) ; passage de 24 px au centre, l\'objet Porte se pose dessus', DOORV, 'porte')
mu(43, 'porte_droite', 'Ouverture dans le mur droite (remplace une tuile mur_droite) ; passage de 24 px au centre, l\'objet Porte se pose dessus', DOORV, 'porte')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    du(44 + k, f'porte_{s}_dessus', f'Haut de l\'encadrement de porte_{s}, même case que porte_{s}', 'porte')

# ------------------------------------------------------------------ 5. passerelles et chaussée
grp(48, 'Passerelles de planches et chaussée de pierre', 'Praticables, calque `Sol`, sans collision. La passerelle (3 cases de large dans la salle 07) et la chaussée '
    '(salle 08) traversent un fossé d\'eau profonde : ne PAS peindre l\'eau profonde (`Murs`) sur ces cases. Extrémités pour finir proprement.')
so(48, 'planches_h', 'Passerelle de planches horizontale (planches dans le sens est-ouest)', 'planches')
so(49, 'planches_v', 'Passerelle de planches verticale (planches dans le sens nord-sud)', 'planches')
so(50, 'chaussee_pierre', 'Chaussée de pierre, dalles larges (traverse un fossé)', 'chaussee')
so(51, 'chaussee_pierre_b', 'Chaussée de pierre, variante usée', 'chaussee')
so(52, 'planches_h_g', 'Passerelle horizontale : extrémité gauche (poteaux)', 'planches')
so(53, 'planches_h_d', 'Passerelle horizontale : extrémité droite (poteaux)', 'planches')
so(54, 'planches_v_haut', 'Passerelle verticale : extrémité haute (poteaux)', 'planches')
so(55, 'planches_v_bas', 'Passerelle verticale : extrémité basse (poteaux)', 'planches')

# ------------------------------------------------------------------ 6. escaliers + vides
grp(56, 'Escaliers (56/57) ; ids réservés 58 à 66 (vides)', 'La transition est un objet `Sortie` (`transition=escalier`). 58 à 66 = trous mortels des autres donjons : '
    'VIDES ici (aucune fosse dans le Sanctuaire).')
so(56, 'escalier_montant', 'Escalier qui monte (vers le haut de l\'écran), pierre noyée ; la transition est un objet Sortie', 'escalier')
so(57, 'escalier_descendant', 'Escalier qui descend (vers le bas de l\'écran), pierre noyée ; la transition est un objet Sortie', 'escalier')

# ------------------------------------------------------------------ 7. balcon
grp(67, 'Balcon de Corvan (salle 08, inaccessible)', 'Plate-forme de pierre surélevée au-dessus du fossé, dans l\'angle nord-est : 3 cases de large (`balcon_g`, `balcon_m`, `balcon_d`). '
    'Solide, sur `Murs` ; le garde-corps passe devant sur `Dessus`.')
mu(67, 'balcon_g', 'Balcon, extrémité gauche (pierre surélevée, solide)', FULL, 'balcon')
mu(68, 'balcon_m', 'Balcon, milieu (solide)', FULL, 'balcon')
mu(69, 'balcon_d', 'Balcon, extrémité droite (solide)', FULL, 'balcon')
du(70, 'balcon_garde_corps', 'Garde-corps de pierre du balcon (Dessus, à poser sur le balcon)', 'balcon')
de(71, 'balcon_ombre', 'Ombre du balcon sur l\'eau (Decor, sous le balcon)', 'ombre')

# ------------------------------------------------------------------ 8. murs fissurés
grp(72, 'MURS FISSURÉS (bombes) : fermé -> ouvert', 'Fermés : sur `Murs` (solides, objet `MurFissure` par-dessus, fissures claires). Ouverts : sur `Decor`, opaques (trou noir '
    'dans la pierre). Paires : **72->76, 73->77, 74->78, 75->79** (haut, bas, gauche, droite). La salle 03 n\'utilise qu\'une orientation.')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    mu(72 + k, f'mur_fissure_{s}', f'MUR FISSURÉ {s} (face avant fissurée ; solide ; objet MurFissure dessus, la bombe l\'ouvre)', FULL, 'secret')
for k, s in enumerate(('haut', 'bas', 'gauche', 'droite')):
    de(76 + k, f'mur_fissure_{s}_ouvert', f'Mur {s} OUVERT : trou noir dans la pierre, gravats (passage dessous)', 'secret')

# ------------------------------------------------------------------ 9. eau peu profonde
grp(80, 'Eau peu profonde (terrain `Eau`)', 'Praticable, calque `Sol`, sans collision, sans ralentissement. Le bord passe au milieu de la tuile. '
    '93 et 94 : eau pleine avec dalles affleurantes (se mélangent à 80) ; 95 : reflets (variante à animer).')
at(80, 'eau', 'Eau peu profonde, case entière (Brann la traverse)', 'Sol', None, 'eau', plan=('terrain', 15, 'dalle', 'eau'))
EAU = {80: FULL4, 93: FULL4, 94: FULL4}
names = [('eau_bord_haut', 'Eau peu profonde : bord haut (sol au-dessus)', EDGES9['haut']),
         ('eau_bord_bas', 'Eau peu profonde : bord bas (sol en dessous)', EDGES9['bas']),
         ('eau_bord_gauche', 'Eau peu profonde : bord gauche (sol à gauche)', EDGES9['gauche']),
         ('eau_bord_droite', 'Eau peu profonde : bord droite (sol à droite)', EDGES9['droite']),
         ('eau_creux_hg', 'Eau peu profonde : coin rentrant, sol seulement en haut-gauche', CREUX['creux_hg']),
         ('eau_creux_hd', 'Eau peu profonde : coin rentrant, sol seulement en haut-droite', CREUX['creux_hd']),
         ('eau_creux_bg', 'Eau peu profonde : coin rentrant, sol seulement en bas-gauche', CREUX['creux_bg']),
         ('eau_creux_bd', 'Eau peu profonde : coin rentrant, sol seulement en bas-droite', CREUX['creux_bd']),
         ('eau_coin_hg', 'Eau peu profonde : coin haut-gauche d\'une étendue rectangulaire (eau seulement dans le quart opposé)', EDGES9['coin_hg']),
         ('eau_coin_hd', 'Eau peu profonde : coin haut-droite d\'une étendue rectangulaire', EDGES9['coin_hd']),
         ('eau_coin_bg', 'Eau peu profonde : coin bas-gauche d\'une étendue rectangulaire', EDGES9['coin_bg']),
         ('eau_coin_bd', 'Eau peu profonde : coin bas-droite d\'une étendue rectangulaire', EDGES9['coin_bd'])]
for k, (n, r, b) in enumerate(names):
    edge(81 + k, n, r, 'dalle', 'eau', b)
    EAU[81 + k] = b
at(93, 'eau_dalles_a', 'Eau peu profonde pleine avec dalles affleurantes (variante, mélanger avec 80)', 'Sol', None, 'eau', plan=('terrain', 15, 'dalle', 'eau'))
at(94, 'eau_dalles_b', 'Eau peu profonde pleine avec dalles affleurantes, variante', 'Sol', None, 'eau', plan=('terrain', 15, 'dalle', 'eau'))
at(95, 'eau_reflets', 'Eau peu profonde à reflets brillants (à animer plus tard ; pas dans le terrain)', 'Sol', None, 'eau', plan=('terrain', 15, 'dalle', 'eau'))
S.wang['Eau'] = dict(colors=[('sol', tsplan.CATS['dalle']), ('eau', tsplan.CATS['eau'])], tile=80, fam='',
                     tiles={**{i: (1, 1, 1, 1) for i in (0, 1, 2)}, **{i: tuple(2 if k else 1 for k in b) for i, b in EAU.items()}})

# ------------------------------------------------------------------ 10. eau profonde
grp(96, 'Eau profonde SOLIDE (terrain `Eau profonde`, calque `Murs`)', 'Fossés des salles 07 et 08. Collision par quarts de case : la partie « rive » d\'une tuile de bord reste '
    'praticable, la partie eau est solide (flèches arrêtées comme par un mur). Se peint sur `Murs` ; sous les cases de rive, mettre du sol. Les passerelles/chaussée '
    '(48 à 55) se posent sur `Sol` aux cases où l\'on ne peint pas d\'eau profonde.')
DEEP = {96: FULL4, 111: FULL4}
mu(96, 'eau_profonde', 'EAU PROFONDE : case entière (solide)', FULL, 'profonde', plan=('terrain', 15, 'dalle', 'profonde'))
# ordre des ids : 97-100 bords, 101-104 creux, 105-108 coins, 109-110 diagonales
dnames = [('bord_haut', 'bord haut (rive au-dessus)', EDGES9['haut']), ('bord_bas', 'bord bas (rive en dessous)', EDGES9['bas']),
          ('bord_gauche', 'bord gauche (rive à gauche)', EDGES9['gauche']), ('bord_droite', 'bord droite (rive à droite)', EDGES9['droite']),
          ('creux_hg', 'coin rentrant, rive seulement en haut-gauche', CREUX['creux_hg']), ('creux_hd', 'coin rentrant, rive seulement en haut-droite', CREUX['creux_hd']),
          ('creux_bg', 'coin rentrant, rive seulement en bas-gauche', CREUX['creux_bg']), ('creux_bd', 'coin rentrant, rive seulement en bas-droite', CREUX['creux_bd']),
          ('coin_hg', 'coin haut-gauche d\'un fossé rectangulaire (eau seulement dans le quart bas-droite)', EDGES9['coin_hg']),
          ('coin_hd', 'coin haut-droite d\'un fossé rectangulaire (eau seulement dans le quart bas-gauche)', EDGES9['coin_hd']),
          ('coin_bg', 'coin bas-gauche d\'un fossé rectangulaire (eau seulement dans le quart haut-droite)', EDGES9['coin_bg']),
          ('coin_bd', 'coin bas-droite d\'un fossé rectangulaire (eau seulement dans le quart haut-gauche)', EDGES9['coin_bd']),
          ('diag_a', 'deux quarts opposés (eau en haut-gauche et bas-droite)', (1, 0, 0, 1)),
          ('diag_b', 'deux quarts opposés (eau en haut-droite et bas-gauche)', (0, 1, 1, 0))]
for k, (n, r, b) in enumerate(dnames):
    i = 97 + k
    mu(i, f'eau_profonde_{n}', 'EAU PROFONDE : ' + r + ' (solide sur la partie eau)', quarter_rects(bi(b)), 'profonde',
       plan=('terrain', bi(b), 'dalle', 'profonde'))
    DEEP[i] = b
mu(111, 'eau_profonde_b', 'EAU PROFONDE pleine, variante à reflets (mélanger avec 96 ; à animer plus tard)', FULL, 'profonde', plan=('terrain', 15, 'dalle', 'profonde'))
S.wang['Eau profonde'] = dict(colors=[('profonde', tsplan.CATS['profonde'])], tile=96, fam='',
                              tiles={i: tuple(1 if k else 0 for k in b) for i, b in DEEP.items()})

# ------------------------------------------------------------------ 11. colonnes et mobilier
grp(112, 'Colonnes, vasques, statues, fresques', 'Une colonne de 1 case = `colonne_base` (Murs, solide) + `colonne_haut` (Dessus) juste au-dessus. Algues et fresques se plaquent '
    'sur une tuile de mur (calque `Dessus`).')
du(112, 'colonne_haut', 'Haut de colonne (chapiteau), case au-dessus de colonne_base', 'colonne')
mu(113, 'colonne_base', 'Base de colonne de pierre, pieds dans l\'eau (solide)', BASE, 'colonne')
mu(114, 'colonne_brisee', 'Colonne brisée, tronc coupé (solide, 1 seule case)', OBJ, 'colonne')
mu(115, 'vasque', 'Vasque de pierre pleine d\'eau (solide)', OBJ, 'deco')
mu(116, 'statue_brisee', 'Statue de gardien brisée (solide)', OBJ, 'deco')
du(117, 'fresque_mur', 'Fresque effacée plaquée sur une face de mur (Dessus)', 'deco')
du(118, 'algues_mur', 'Algues pendantes sur une face de mur (Dessus)', 'algue')
du(119, 'algues_mur_lum', 'Algues LUMINEUSES sur une face de mur (Dessus, cryptes surtout)', 'algue')

# ------------------------------------------------------------------ 12. piliers 2x2, estrade
grp(120, 'Piliers 2×2 (arène du boss), estrade, divers', 'Pilier de 4 cases (le boss : 4 piliers de 2×2) : `pilier_hg` `pilier_hd` / `pilier_bg` `pilier_bd`, tous sur `Murs`, solides. '
    'Les rectangles Tiled nommés `pilier` restent ceux du boss. Estrade : sol surélevé de la chapelle et d\'Ondine (praticable).')
mu(120, 'pilier_hg', 'Pilier 2×2 : haut-gauche (solide)', PIL2, 'colonne')
mu(121, 'pilier_hd', 'Pilier 2×2 : haut-droite (solide)', PIL2R, 'colonne')
mu(122, 'pilier_bg', 'Pilier 2×2 : bas-gauche (solide)', PIL2B, 'colonne')
mu(123, 'pilier_bd', 'Pilier 2×2 : bas-droite (solide)', PIL2BR, 'colonne')
so(124, 'estrade_dalle', 'Estrade de pierre (chapelle de la lanterne, estrade d\'Ondine) : dalle dorée', 'estrade')
so(125, 'estrade_marches', 'Marches d\'estrade (bord bas de l\'estrade, praticable)', 'estrade')
de(126, 'lueur_bleue', 'Tache de lueur bleue au sol (semi-transparente)', 'rune')
de(127, 'debris', 'Débris de pierre et gravats noyés', 'deco')

# ------------------------------------------------------------------ 13. bassin d'Ondine
grp(128, 'Bassin rond d\'Ondine (arène, 6 bassins de 3×3)', 'Bassin de 3×3 cases, eau peu profonde praticable avec margelle de pierre : `bassin_hg bassin_h bassin_hd / bassin_g bassin_c bassin_d / '
    'bassin_bg bassin_b bassin_bd` sur `Sol`, sans collision. Le `Marqueur` `ondine_surgit_N` va sur `bassin_c`. L\'anneau d\'ondes (137/138, deux images) se pose sur `Decor`.')
for k, s in enumerate(('hg', 'h', 'hd', 'g', 'c', 'd', 'bg', 'b', 'bd')):
    so(128 + k, f'bassin_{s}', 'Bassin d\'Ondine : ' + ('centre (eau)' if s == 'c' else 'margelle ' + s), 'bassin')
de(137, 'anneau_ondes_a', 'Anneau d\'ondes qui annonce le surgissement d\'Ondine, image A (Decor, semi-transparent)', 'bassin')
de(138, 'anneau_ondes_b', 'Anneau d\'ondes, image B (plus large)', 'bassin')

# ------------------------------------------------------------------ 14. rune et salles spéciales
grp(144, 'Mur à rune, chapelle', 'Le mur à rune est une `Porte` (type `lanterne`, `apparence=mur_rune`) dont l\'image `art/puzzles/porte_mur_rune.png` couvre l\'alcôve ; '
    'dessous : `alcove_sol_rune`. Le mur autour est un mur ordinaire (16-30) ou `mur_rune_grave`.')
so(144, 'alcove_sol_rune', 'Fond d\'alcôve : dalle avec rune bleue discrète (sous le mur à rune ; praticable une fois la porte ouverte)', 'rune')
mu(145, 'mur_rune_grave', 'Mur plein avec une rune gravée très discrète (indice, solide)', FULL, 'rune')
mu(146, 'mur_algues', 'Mur plein couvert d\'algues (variante, solide)', FULL, 'mur')
mu(147, 'mur_fresque', 'Mur plein avec fresque (variante, solide)', FULL, 'mur')
mu(148, 'mur_eau', 'Mur plein dont le pied baigne dans l\'eau (variante, solide)', FULL, 'mur')
mu(149, 'mur_lumineux', 'Mur plein aux algues lumineuses (cryptes, solide)', FULL, 'algue')
so(150, 'dalle_lanterne', 'Dalle gravée d\'une lanterne (piédestal de la chapelle 04, texte d\'indice)', 'rune')
mu(151, 'piedestal', 'Piédestal de pierre (solide)', OBJ, 'deco')

PAIRES = [('mur_fissure_haut', 'mur_fissure_haut_ouvert'), ('mur_fissure_bas', 'mur_fissure_bas_ouvert'),
          ('mur_fissure_gauche', 'mur_fissure_gauche_ouvert'), ('mur_fissure_droite', 'mur_fissure_droite_ouvert')]

S.notes += [
    'IDS À RECONNAÎTRE PAR LE CODE : voir la section « Pour le développeur » en tête de ce fichier (mur fissuré 72->76… ; aucun id de trou).',
    'Terrains Tiled (Wang par coins) : `Murs` (16 à 30), `Eau` (0-2, 80 à 94), `Eau profonde` (96 à 111, calque `Murs`). Pas de terrain de trou.',
    'Eau profonde : se peint sur `Murs` ; les tuiles de rive ont une collision par quarts. Une passerelle (48-55) ou la chaussée (50-51) se pose sur `Sol` à la place de l\'eau.',
    'Porte : remplacer la tuile de mur par `porte_<côté>`, poser `porte_<côté>_dessus` dans la même case de `Dessus`, puis l\'objet `Porte`.',
    'Lumière : braseros, torches et lueurs sont des objets (`Torche`) ou gérés par le code, pas des tuiles.',
    'À régler dans Tiled/Godot après livraison : animations de tuiles (eau, reflets, anneaux d\'ondes 137/138).']


# ------------------------------------------------------------------ export
def crypte_px(px_rows):
    out = []
    for row in px_rows:
        nr = []
        for c in row:
            if c is None:
                nr.append(None)
                continue
            r, g, b, a = c
            L = 0.3 * r + 0.59 * g + 0.11 * b
            nr.append((int(r * 0.5 + L * 0.1), int(g * 0.58 + L * 0.1), min(255, int(b * 0.72 + L * 0.2 + 8)), a))
        out.append(nr)
    return out


def main():
    S.save_all('sanctuaire.py')
    out_t = os.path.join(ROOT, 'art', 'tilesets')
    dark = crypte_px(S.sheet(numbers=False))
    big = [[dark[y // 2][x // 2] for x in range(len(dark[0]) * 2)] for y in range(len(dark) * 2)]
    for i in S.tiles:
        stamp_number(dark, (i % S.cols) * T + 1, (i // S.cols) * T + 1, i, 1)
        stamp_number(big, (i % S.cols) * T * 2 + 1, (i // S.cols) * T * 2 + 1, i, 2)
    save_png(os.path.join(out_t, 'sanctuaire_crypte.png'), dark)
    save_png(os.path.join(out_t, 'sanctuaire_crypte_numeros.png'), big)
    old = S.name
    S.name = 'sanctuaire_crypte'
    try:
        with open(os.path.join(ROOT, 'maps', 'tilesets', 'sanctuaire_crypte.tsx'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(S.tsx())
    finally:
        S.name = old


if __name__ == '__main__':
    main()
