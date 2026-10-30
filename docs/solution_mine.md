# Solution de la Mine Effondrée (donjon 2)

Aide-mémoire pour le joueur (ou pour aider un jeune joueur). Le plan de conception est dans `maps/donjon2/plan.md`.

## Le chemin

1. **Salle 01 (entrée)** : statue du corbeau à côté de l'arrivée. Monter au nord.
2. **Salle 02 (hall)** : la carte est dans le coffre en haut à droite. La porte nord est fermée à clé : on y reviendra.
3. **Salle 03 (ouest, facultative)** : un mur fissuré cache un quart de cœur. Revenir avec les bombes (après la salle 07).
4. **Salle 04 (est)** : battre les 3 ennemis pour ouvrir la porte est ; la boussole est dans le coffre. **Sauter dans le trou en bas à gauche** : on tombe sans perdre de vie dans la cave secrète.
5. **Salle 15 (cave)** : coffre = **petite clé n°2**. L'escalier remonte dans la salle 05.
6. **Salle 05 (wagonnets)** : énigme ci-dessous ; la grille s'ouvre, le coffre du sud donne la **petite clé n°1**.
7. Revenir dans la salle 02 et ouvrir la porte nord avec une clé.
8. **Salle 06 (tir)** : énigme ci-dessous ; la porte est s'ouvre.
9. **Salle 07** : grand coffre = **bombes**. Poser une bombe contre l'éboulis de l'est et reculer d'au moins 2 cases.
10. **Salle 08** : ramasser le **marteau de Corvan** (au sol, en bas au milieu). Le Mineur : une bombe près de lui le fait tomber (on le frappe alors), ou on le frappe de côté. Bombe contre le mur fissuré en haut à droite : **petite clé n°3**. Une fois les ennemis vaincus, la porte nord s'ouvre.
11. **Salle 09** : deux Mineurs. Porte ouest = une clé. Facultatif : la plume de corbeau est derrière le mur épais en haut à droite ; une bombe posée au milieu de ses 3 cases les casse d'un coup.
12. **Salle 10** : statue. La porte du boss demande la grande clé, qui est au sous-sol. Le **levier** à gauche (épée) ouvre un raccourci vers la salle 07. Descendre par l'escalier en bas à droite.
13. **Salle 11** : calme. Sortir par le sud.
14. **Salle 12** : énigme ci-dessous.
15. **Salle 13** : **minerai d'étoile** dans la niche brillante en haut à gauche (bombe contre le rocher fissuré). Seconde bombe contre l'éboulis en haut au milieu, puis la porte nord avec la dernière clé.
16. **Salle 14** : bombe contre le mur fissuré en haut à gauche : **grande clé** (grand coffre). Le levier en bas à gauche ouvre le raccourci vers la salle 11.
17. Retour : salle 11, escalier, salle 10, porte du boss.

## Les énigmes

### Salle 05 : deux wagonnets sur deux plaques (34 poussées)

A = wagonnet de gauche, B = wagonnet de droite. Ils avancent chacun leur tour, en se dépassant :

| Étape | Wagonnet | Poussée |
| --- | --- | --- |
| 1 | A | 1 case vers le haut |
| 2 | B | 3 cases à droite, puis 1 vers le bas |
| 3 | A | 4 cases à droite |
| 4 | B | 4 cases à droite |
| 5 | A | 2 cases vers le bas |
| 6 | B | 2 cases vers le haut |
| 7 | A | 4 cases à droite |
| 8 | B | 4 cases à droite (il est en haut à droite) |
| 9 | A | 2 cases vers le haut |
| 10 | B | 3 cases vers le bas : **plaque du bas** |
| 11 | A | 3 cases à droite, puis 1 vers le bas : **plaque du haut** |

Wagonnet coincé : sortir de la salle et revenir, ils reprennent leur place.

### Salle 06 : 3 cibles en 10 secondes

Une flèche va à 10 cases au plus : tirer depuis le milieu de la salle.

1. Sur la rangée de la cible en haut à droite, vers le milieu de la salle (avant les fosses) : tirer à droite.
2. Descendre tout droit jusqu'à la rangée de la cible en bas à droite : tirer à droite.
3. Courir à gauche sur la rangée du milieu, jusqu'à environ 3 cases de la cible du mur ouest : tirer à gauche (le pilier de cette rangée gêne si on tire de trop loin).

Avec l'option d'aide, le temps passe à 20 s.

### Salle 12 : bombe puis flèche de feu

1. Bombe contre l'éboulis du mur du milieu, reculer.
2. Se placer juste à gauche du passage ouvert et tirer vers l'est.
3. La flèche traverse le brasero, prend feu et allume la torche : la porte est s'ouvre.

## Gorm (boss)

- **Phase 1** : une bombe qui explose près de Gorm arrache une plaque d'armure. Une fois ses plaques tombées, quand il est **étourdi**, frapper le cristal rouge de sa poitrine à l'épée.
- Plus assez de bombes : un paquet apparaît sur un côté de l'arène, quelques secondes plus tard.
- **Phase 2** : des rochers tombent, annoncés par leur ombre au sol : sortir de l'ombre. Les couloirs étroits des côtés protègent de ses coups, pas des rochers.
