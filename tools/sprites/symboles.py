"""Les trois symboles du Temple des Racines (gland, racine, feuille), 12x12, partages par la fresque
(temple_racines_sous_sol.py) et les cibles (enigmes.py) pour qu'ils soient identiques.
Caracteres : '.' vide, 'l' clair, 'm' moyen, 'd' sombre."""

SYMBOLS = {
    'gland': [
        ".....dd.....",
        ".....d......",
        "..mmmmmmmm..",
        ".mllmmmmmmd.",
        ".mmmmmmmmdd.",
        "..dddddddd..",
        "...llmmmmd..",
        "...lmmmmmd..",
        "...mmmmmdd..",
        "....mmmdd...",
        ".....mdd....",
        "............",
    ],
    'racine': [
        ".lm......ml.",
        "..lm....ml..",
        "...lm..ml...",
        "....lmml....",
        ".....mm.....",
        ".....mm.....",
        "....mm......",
        "....md......",
        ".....mm.....",
        ".....mdd....",
        "....mm.dd...",
        "...mm...d...",
    ],
    'feuille': [
        ".........mm.",
        ".......lmmmd",
        ".....llmmmmd",
        "....lmmdmmd.",
        "...lmmdmmmd.",
        "...lmdmmmd..",
        "..lmdmmmdd..",
        "..lmdmmdd...",
        "...ddmdd....",
        "..d.dd......",
        ".d..........",
        "d...........",
    ],
}

# couleurs naturelles (clair, moyen, sombre)
NATUREL = {
    'gland': ('#e0a458', '#b06e40', '#6a3c22'),
    'racine': ('#d08a50', '#8a5a34', '#4a2a1c'),
    'feuille': ('#9ad060', '#5a8a3c', '#3a5a2c'),
}
for _k, _g in SYMBOLS.items():
    assert len(_g) == 12 and all(len(r) == 12 for r in _g), _k
