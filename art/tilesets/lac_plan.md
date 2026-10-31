# Plan du tileset `lac` — Le lac (overworld : cascade, Sanctuaire Englouti à demi noyé, quai, îlot et gué)

> Fichier généré par `tools/sprites/lac.py` : modifier le script, pas ce fichier. **État : DESSIN FINAL** (les numéros sont ceux du plan, aucune tuile n'a bougé).

- Image : `art/tilesets/lac.png`, 256×480 px, 8 colonnes × 15 lignes de tuiles 32×32, sans marge ni espacement (120 cases). Tileset Tiled : `maps/tilesets/lac.tsx` (collisions et terrains définis). `art/tilesets/lac_numeros.png` = la planche ×2 avec les numéros.
- **Numéro = id local Tiled** (ligne × 8 + colonne, en partant de 0). Une tuile ne change jamais de numéro. Lignes 12 à 15 (ids 88 à 119) : réserve vide, pour les ajouts. Les cases vides au bout d'une ligne sont aussi libres.
- Collisions en pixels dans la tuile (x,y largeur×hauteur, origine en haut à gauche). Les terrains (Wang par coins) sont dans le panneau Terrains de Tiled.
- Vue de dessus 3/4, lumière en haut à gauche, contour sombre d'1 px. Palette : bleus-verts froids de l'eau, pierre gris-violet du Sanctuaire. Les collisions sont dans le tileset (voir la colonne Collision).
- **Ce tileset ne contient que ce qui manque.** À utiliser avec `village` (firstgid 1), `foret` (401) et `lac` (le troisième). Eau peu profonde : `village` 63 `rive_plein` et 64 `lac_base` (Sol), bords `rive_*` 48-62 (terrain `Rive`). Eau profonde : `village` 65-79 (terrain `Lac profond`, sur `Murs`, solide). Ponton : `village` 312-317 (Decor) + pilotis 318, bitte 319, roseaux 324-325, nénuphars 326, rocher dans l'eau 327. Éboulis : `village` 138/139. Falaises : `village` 120-132. Buissons coupables : `village` 300, `foret` 96-99.
- **Aucun terrain (Wang) nouveau** : l'autotiling de l'eau est celui de `village` (`Rive`, `Lac profond`). Les tuiles de ce tileset se posent à la main (ou avec le pinceau « tampon » pour les assemblages).
- **Animations** (déjà dans le `.tsx`, 250 ms par image) : `cascade_chute_a` -> `_b` et `cascade_voile_a` -> `_b`. Peindre uniquement les tuiles `_a`.
- **Rideau de cascade** : `cascade_voile_*` sont semi-transparentes, sur le calque `Dessus`, sans collision, au-dessus de cases libres de l'alcôve (`alcove_sol`) : Brann passe dessous. Peindre le fond (`alcove_fond` en haut, `alcove_sol` en bas) sur `Murs` / `Sol`, puis le voile sur `Dessus`.
- **Portail du Sanctuaire** : la `Sortie` (64×32) se pose sur les deux cases `sanct_portail_g` / `sanct_portail_d` (rangée du bas de la façade).

## Calques

- `Sol` : eau (village), dalles du quai, herbe d'îlot, sol d'alcôve, bassin, marches immergées
- `Decor` : sans collision (ponton, pierres du gué, algues, éclaboussures, ruines basses, jonction ponton-quai)
- `Murs` : tout ce qui bloque (cascade et falaise, façade du Sanctuaire, colonnes, bords de quai, eau profonde de village)
- `Objets` : Sortie, Spawn, Porte (rocher), Interrupteur, Ennemi, StatueCorbeau… (objets Tiled, pas des tuiles)
- `Dessus` : rideau de cascade (semi-transparent), haut du portail

## 1. Cascade et alcôve (le secret d'observation : quart de cœur derrière le rideau)

La cascade tombe dans la falaise (colonnes 35-36 du lac) : `cascade_haut` en haut de la falaise, `cascade_chute_a` en dessous, `cascade_bassin` au pied (ruisseau d'eau peu profonde). L'alcôve (2×2) est creusée dans la falaise : `alcove_fond` (mur du fond, solide) et `alcove_sol` (sol de roche mouillée) ; le rideau `cascade_voile_*` passe devant, sur `Dessus`. Les jambages `cascade_jambage_g` / `_d` encadrent la chute avec la falaise de `village`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 0 | `cascade_haut` | CASCADE, haut : roche et eau qui déborde de la crête (solide) | Murs | pleine |
| 1 | `cascade_chute_a` | CASCADE, chute sur la falaise, image A (à répéter ; animée A->B) | Murs | pleine |
| 2 | `cascade_chute_b` | CASCADE, chute sur la falaise, image B (seconde image de l'animation) | Murs | pleine |
| 3 | `cascade_jambage_g` | Jambage de roche à gauche de la chute (solide) | Murs | pleine |
| 4 | `cascade_jambage_d` | Jambage de roche à droite de la chute (solide) | Murs | pleine |
| 5 | `alcove_fond` | Alcôve : mur du fond, roche sombre avec trouée (solide, sous le rideau) | Murs | pleine |
| 6 | `alcove_sol` | Alcôve : sol de roche mouillée (libre, sous le rideau) | Sol | aucune |
| 7 | `cascade_bassin` | Bassin au pied de la cascade : eau peu profonde avec écume (libre) | Sol | aucune |
| 8 | `cascade_voile_a` | RIDEAU d'eau semi-transparent, image A (Dessus, sans collision ; animé A->B) | Dessus | aucune |
| 9 | `cascade_voile_b` | RIDEAU d'eau semi-transparent, image B (seconde image de l'animation) | Dessus | aucune |
| 10 | `cascade_voile_pied` | Pied du rideau : écume semi-transparente (Dessus, sans collision) | Dessus | aucune |
| 11 | `alcove_lueur` | Scintillement au sol de l'alcôve (sous le quart de cœur) | Decor | aucune |
| 12 | `cascade_ecume` | Écume et éclaboussures au pied de la chute (à poser sur le bassin) | Decor | aucune |
| 13 | `ruisseau_pierres` | Pierres plates dans le ruisseau de la cascade | Decor | aucune |

## 2. Façade du Sanctuaire Englouti (6×3, portail de 2 cases, mur à demi noyé)

Rangée du haut = frise et fronton ; rangée du milieu = pilastres, murs et linteau ; rangée du bas = soubassement dans l'eau et PORTAIL (`sanct_portail_g` / `_d`, ouvert : seuls les montants sont solides ; la `Sortie` 64×32 se pose dessus). Toute la façade est sur `Murs`.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 16 | `sanct_frise_g` | Frise, coin gauche (solide) | Murs | pleine |
| 17 | `sanct_frise_a` | Frise, pierre sculptée, variante A (solide) | Murs | pleine |
| 18 | `sanct_fronton_g` | Fronton au-dessus du portail, moitié gauche (solide) | Murs | pleine |
| 19 | `sanct_fronton_d` | Fronton au-dessus du portail, moitié droite (solide) | Murs | pleine |
| 20 | `sanct_frise_b` | Frise, pierre sculptée, variante B (solide) | Murs | pleine |
| 21 | `sanct_frise_d` | Frise, coin droit (solide) | Murs | pleine |
| 24 | `sanct_mur_g` | Mur, coin gauche avec pilastre (solide) | Murs | pleine |
| 25 | `sanct_mur_noye_a` | Mur à demi noyé, algues, variante A (solide) | Murs | pleine |
| 26 | `sanct_linteau_g` | Linteau du portail, moitié gauche (solide) | Murs | pleine |
| 27 | `sanct_linteau_d` | Linteau du portail, moitié droite (solide) | Murs | pleine |
| 28 | `sanct_mur_noye_b` | Mur à demi noyé, algues, variante B (solide) | Murs | pleine |
| 29 | `sanct_mur_d` | Mur, coin droit avec pilastre (solide) | Murs | pleine |
| 30 | `sanct_pilastre` | Pilastre intermédiaire (solide) | Murs | pleine |
| 31 | `sanct_pilier` | Pilier massif isolé (solide) | Murs | partielle : 4,8 24×22 |
| 32 | `sanct_pied_g` | Soubassement dans l'eau, coin gauche (solide) | Murs | pleine |
| 33 | `sanct_pied_noye_a` | Soubassement noyé, variante A (solide) | Murs | pleine |
| 34 | `sanct_portail_g` | PORTAIL, case gauche (Sortie dessus) : montant solide, centre libre | Murs | partielle : 0,0 8×32 |
| 35 | `sanct_portail_d` | PORTAIL, case droite (Sortie dessus) : montant solide, centre libre | Murs | partielle : 24,0 8×32 |
| 36 | `sanct_pied_noye_b` | Soubassement noyé, variante B (solide) | Murs | pleine |
| 37 | `sanct_pied_d` | Soubassement dans l'eau, coin droit (solide) | Murs | pleine |
| 38 | `sanct_marches` | Marches immergées devant le portail (libre) | Sol | aucune |
| 39 | `sanct_seuil` | Seuil de pierre du portail (libre) | Sol | aucune |
| 40 | `sanct_colonne_a` | Colonne brisée, variante A (solide) | Murs | partielle : 4,8 24×22 |
| 41 | `sanct_colonne_b` | Colonne brisée, variante B (solide) | Murs | partielle : 4,8 24×22 |
| 42 | `sanct_colonne_pied` | Base de colonne écroulée (solide) | Murs | partielle : 2,14 28×18 |
| 43 | `sanct_portail_haut` | Haut du portail : rideau d'eau qui goutte (Dessus, facultatif) | Dessus | aucune |
| 44 | `sanct_gravats` | Gravats de la façade au pied du mur (décor) | Decor | aucune |
| 45 | `sanct_algues_mur` | Algues accrochées au bas d'un mur (décor) | Decor | aucune |
| 46 | `sanct_lanterne_eau` | Lueur bleue dans l'eau, devant le portail (décor) | Decor | aucune |

## 3. Quai de pierre devant le Sanctuaire

Dalles mouillées (Sol), bords de quai (Murs, partiels : la partie extérieure est solide), bitte et jonction avec le ponton de `village` (312-317).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 48 | `quai_dalle_a` | Dalle de quai mouillée, variante A | Sol | aucune |
| 49 | `quai_dalle_b` | Dalle de quai, variante B (joint fissuré) | Sol | aucune |
| 50 | `quai_dalle_c` | Dalle de quai, variante C (flaque) | Sol | aucune |
| 51 | `quai_dalle_rune` | Dalle gravée d'un sceau effacé (devant le portail) | Sol | aucune |
| 52 | `quai_bord_bas` | Bord de quai, côté sud (moitié basse solide) | Murs | partielle : 0,22 32×10 |
| 53 | `quai_bord_g` | Bord de quai, côté ouest | Murs | partielle : 0,0 10×32 |
| 54 | `quai_bord_d` | Bord de quai, côté est | Murs | partielle : 22,0 10×32 |
| 55 | `quai_bord_haut` | Bord de quai, côté nord (moitié haute solide) | Murs | partielle : 0,0 32×10 |
| 56 | `quai_coin_bg` | Coin de quai, bas-gauche | Murs | partielle : 0,22 32×10 ; 0,0 10×22 |
| 57 | `quai_coin_bd` | Coin de quai, bas-droite | Murs | partielle : 0,22 32×10 ; 22,0 10×22 |
| 58 | `quai_jonction` | Jonction ponton-quai : planches qui finissent sur la dalle (à droite du dernier ponton_h) | Decor | aucune |
| 59 | `quai_bitte` | Bitte d'amarrage en pierre (solide) | Murs | partielle : 11,14 10×18 |
| 60 | `quai_amarre` | Anneau et corde d'amarrage (solide, bord de quai) | Murs | partielle : 0,22 32×10 |
| 61 | `quai_flaque` | Flaque sur le quai (décor) | Decor | aucune |
| 62 | `quai_mousse` | Mousse et algues séchées sur une dalle (décor) | Decor | aucune |
| 63 | `quai_caisse_brisee` | Planches et caisse brisée échouées (décor) | Decor | aucune |

## 4. Îlot et gué (quart de cœur à l'arc)

Terre de l'îlot (Sol) : à poser sur les 3 cases entourées d'eau profonde (`village` 65-79, qui font le rivage). Le rocher du gué est une `Porte` (`apparence`=`rocher`, image `art/puzzles/porte_rocher_eau.png`), pas une tuile. `gue_goulet` marque le goulet d'eau peu profonde qui mène à la cible.

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 64 | `ilot_herbe_a` | Herbe d'îlot, variante A | Sol | aucune |
| 65 | `ilot_herbe_b` | Herbe d'îlot, variante B | Sol | aucune |
| 66 | `ilot_herbe_c` | Herbe d'îlot, touffes et fleurs | Sol | aucune |
| 67 | `ilot_sable` | Sable de l'îlot | Sol | aucune |
| 68 | `gue_pierres_a` | Pierres plates du gué, variante A (sur eau peu profonde) | Decor | aucune |
| 69 | `gue_pierres_b` | Pierres plates du gué, variante B | Decor | aucune |
| 70 | `gue_goulet` | Goulet d'eau peu profonde, eau calme avec reflets (libre) | Sol | aucune |
| 71 | `ilot_coquillages` | Coquillages et galets sur l'îlot (décor) | Decor | aucune |

## 5. Ambiance de l'eau et ruines immergées

Décor sans collision à semer sur l'eau (sauf `ruine_bloc` et `ruine_arche`, solides).

| N° | Nom | Rôle | Calque | Collision |
| --- | --- | --- | --- | --- |
| 72 | `algues_a` | Algues flottantes, variante A | Decor | aucune |
| 73 | `algues_b` | Algues flottantes, variante B | Decor | aucune |
| 74 | `eclaboussure_a` | Éclaboussures (sillage d'un Têtard), variante A | Decor | aucune |
| 75 | `eclaboussure_b` | Éclaboussures, variante B | Decor | aucune |
| 76 | `reflets_a` | Reflets brillants sur l'eau, variante A | Decor | aucune |
| 77 | `reflets_b` | Reflets brillants, variante B | Decor | aucune |
| 78 | `ruine_dalle` | Dalle ancienne affleurant dans l'eau peu profonde | Decor | aucune |
| 79 | `ruine_dalle_b` | Dalle ancienne gravée, immergée | Decor | aucune |
| 80 | `ruine_bloc` | Bloc de pierre taillé qui dépasse de l'eau (solide) | Murs | partielle : 4,8 24×22 |
| 81 | `ruine_arche` | Morceau d'arche immergée (solide) | Murs | partielle : 4,8 24×22 |
| 82 | `coquillages` | Coquillages sur la rive | Decor | aucune |
| 83 | `ecume_quai` | Écume le long d'un quai ou d'un mur | Decor | aucune |
| 84 | `nenuphar_fleur` | Nénuphar en fleur | Decor | aucune |
| 85 | `roseaux_c` | Roseaux, variante C | Decor | aucune |
| 86 | `bulles` | Bulles à la surface | Decor | aucune |
| 87 | `brume_basse` | Voile de brume basse sur l'eau (décor, semi-transparent) | Decor | aucune |

## Assemblages (pinceau « tampon » dans Tiled)

| Assemblage | Tuiles (ligne par ligne) | Calques / usage |
| --- | --- | --- |
| **Cascade (colonne de 1 case de large, 3 de haut)** | `0 / 1 / 7` | Murs, Murs, Sol — chute sur 2 cases ou plus : répéter cascade_chute_a ; jambages de chaque côté |
| **Alcôve derrière le rideau (2×2)** | `5 5 / 6 6` | Murs (rangée du haut), Sol (rangée du bas) — rideau cascade_voile_a sur Dessus au-dessus des 4 cases, cascade_voile_pied sur la rangée du bas |
| **Façade du Sanctuaire Englouti (6×3, portail aux colonnes 2-3)** | `16 17 18 19 20 21 / 24 25 26 27 28 29 / 32 33 34 35 36 37` | Murs (tout) ; Sortie sur les 2 cases portail — pour une façade plus large, répéter frise_a / mur_noye_a / pied_noye_a ou intercaler sanct_pilastre |

## Notes

- `cascade_chute_a` et `cascade_voile_a` portent leur animation dans le `.tsx` (250 ms par image) : peindre seulement les tuiles `_a`.
- Tuiles `village` à utiliser pour le lac : 63/64 (eau peu profonde), 48-62 (bords `Rive`), 65-79 (eau profonde), 312-317 (ponton), 318 (pilotis), 324-327 (roseaux, nénuphars, rocher dans l'eau), 138/139 (éboulis), 120-132 (falaise), 300 (buisson coupable).
- À régler dans Tiled si besoin : rien (collisions et animations sont dans le `.tsx`).
