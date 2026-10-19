# Les Trois Sceaux — Roadmap (Zelda-like 2D en Godot C#)

## Vue d'ensemble

Objectif : un petit Zelda-like complet (1 overworld compact, 3 donjons, 3 boss) en environ **14 à 18 mois** à raison de 6 à 10 h par semaine, avec graphismes et sons faits maison.

**Hypothèses de départ**

- Tu codes déjà (C# ou autre), mais tu découvres Godot : la première phase sert à apprendre le moteur, pas la programmation.
- Tu travailles seul sur ton temps libre : chaque phase se termine par quelque chose de jouable, pour garder la motivation.
- Combat, donjons/énigmes, inventaire et sauvegarde sont prioritaires ; l'overworld et les PNJ restent volontairement légers.
- Pixel art et audio originaux : on fige un style simple tôt, pour que la production d'assets ne devienne pas le goulot.

**Règle d'or** : terminer d'abord *un* donjon complet et poli (la « vertical slice », fin de phase 4) avant de produire le reste. C'est le point de contrôle principal du projet : si ce donjon n'est pas fun, on corrige avant de multiplier le contenu.

| Phase | Contenu | Durée |
| --- | --- | --- |
| 0 | Apprendre Godot | 3-4 sem. |
| 1 | Déplacement et caméra | 4 sem. |
| 2 | Combat et ennemis | 6 sem. |
| 3 | Inventaire, sauvegarde | 6 sem. |
| 4 | Donjon 1 + boss (vertical slice) | 8 sem. |
| 5 | Pixel art + audio, en parallèle des phases 2 à 4 | — |
| ★ | **Point de contrôle : donjon 1 fun, testé par 2-3 joueurs sans aide** | — |
| 6 | Production : 2 donjons | 5-6 mois |
| 7 | Polish et sortie | 2 mois |

Les phases 0 à 4 construisent et valident les systèmes ; la phase 5 avance en parallèle ; les phases 6 et 7 ne démarrent qu'après le point de contrôle.

## Scénario et personnages

Titre : **Les Trois Sceaux** (*The Three Seals* à l'international). Héros : **Brann**, apprenti forgeron, qui doit restaurer trois sceaux avant la prochaine éclipse.

**Pitch** : le royaume de Brumeval est protégé depuis mille ans par trois sceaux qui retiennent Morvath, un sorcier enfermé sous le château. Une éclipse les affaiblit et leurs gardiens sont corrompus. Maître Corvan, le forgeron du village, confie une épée à Brann avant de « mourir ».

| Acte | Sceau et donjon | Gardien (boss) | Objet obtenu | Ce que Brann apprend |
| --- | --- | --- | --- | --- |
| 1 | Forêt — Temple des Racines | Sylve, cerf géant envahi de ronces noires | Arc (interrupteurs à distance) | Il agit pour venger son maître |
| 2 | Montagne — Mine Effondrée | Gorm, golem de pierre devenu fou | Bombes (murs fissurés) | Les sceaux ont été sabotés volontairement |
| 3 | Lac — Sanctuaire Englouti | Ondine, sirène prisonnière d'une armure | Lanterne (passages cachés) | Le traître est Corvan, qui a simulé sa mort |

**Fin** : combat contre Corvan fusionné avec l'esprit de Morvath, au château ; les trois objets servent pendant le combat. Vaincu, Corvan redevient un vieil homme et part en exil. Brann reforge les trois sceaux en un seul et passe d'apprenti à maître.

**Brann**

- 16 ans, orphelin recueilli enfant par Corvan ; débrouillard, têtu, plus manuel que bavard
- Pas un élu : il gagne en bricolant et en comprenant comment les choses marchent
- Parle peu : une dizaine de répliques courtes aux moments forts, surtout face à Corvan
- Nom d'origine celte qui signifie « corbeau » ; le corbeau est son emblème
- Sprite 16×16 : tablier de cuir et gants de forge (brun, rouille), écharpe rouge vif avec un corbeau, cheveux en bataille lisibles de dos

**Maître Corvan**

- La soixantaine, forgeron respecté de Brumeval, bourru mais bienveillant ; ancien gardien humain des sceaux, ce que tout le monde a oublié
- Motivation : il perd la vue et la force de ses mains, et ne peut plus forger. Morvath lui promet sa jeunesse s'il le libère. Il trahit par peur de vieillir et d'être inutile, pas par cruauté.
- Fausse mort : la nuit de l'éclipse, Brann le trouve blessé, reçoit l'épée et part chercher de l'aide ; au retour, le corps a disparu. Chaque sceau restauré s'ouvre une dernière fois, assez pour que Morvath en absorbe l'énergie : Brann sert ses plans sans le savoir.
- Indices, acte 1 : les ronces du Temple ont été coupées avec un outil de forge ; un PNJ dit que Corvan allait souvent en forêt
- Indices, acte 2 : un marteau au poinçon de Corvan dans la Mine ; le golem parle d'un homme « au tablier de cuir »
- Indices, acte 3 : une silhouette observe Brann de loin ; Corvan se dévoile juste avant le boss
- Combat final : phase 1, marteau de forge (coups lents et lourds) ; phase 2, Morvath prend le dessus, le corps couvert de ronces, de pierre et d'eau, à contrer avec l'arc, les bombes et la lanterne
- Dénouement : redevenu un vieil homme, il dit quelques mots à Brann puis part en exil, seul, hors de Brumeval
- Sprite : grand et voûté, barbe grise, même tablier que Brann en plus usé ; forme finale = même silhouette aux couleurs corrompues

**Les trois gardiens**

Protecteurs des sceaux depuis mille ans, rendus fous par la corruption : Brann les libère en les battant. Chacun laisse son sceau et, sauf Ondine, une réplique qui accuse Corvan. Sprites de boss en 32×32 ou 48×48 ; la corruption (ronces, cristal, armure) sur un calque séparé qui clignote.

| Gardien | Donjon | Mécanique (objet) | Phase 2 | À la libération |
| --- | --- | --- | --- | --- |
| Sylve, le Cerf des Racines — cerf blanc, bois couverts de ronces noires | Temple des Racines | Arc : toucher les 3 bulbes de corruption sur ses bois, puis frapper à l'épée quand il s'effondre | Charges en ligne droite ; l'esquiver pour qu'il s'assomme contre un pilier | « Méfie-toi de ceux qui coupent les racines » |
| Gorm, le Golem de la Mine — colosse de roche, cristal rouge dans la poitrine | Mine Effondrée | Bombes : faire sauter les plaques d'armure, puis frapper le cristal (invincible à l'épée sinon) | Il fait trembler le sol ; rochers qui tombent, annoncés par leur ombre | Parle de « l'homme au tablier de cuir » |
| Ondine, la Gardienne du Lac — sirène prisonnière d'une armure noire | Sanctuaire Englouti | Lanterne : dans le noir, révèle où elle va surgir ; frapper l'armure à chaque apparition | L'armure se brise en morceaux qui attaquent seuls | Pas le temps de parler : Corvan surgit, absorbe le dernier sceau et lance le final |

Progression : viser, puis placer, puis éclairer ; un boss au sol, un blindé, un caché.

**Brumeval, le village**

Village de montagne au bord du lac, souvent dans la brume, sur 2 écrans : place centrale avec un puits, une dizaine de maisons, un chemin vers chaque région. Le château se voit au loin sur la falaise dès le premier écran.

- **La forge de Corvan** : maison de Brann et point central du jeu ; sauvegarde (corbeau sur l'enclume) et recharge de la vie. Vide et froide après le départ de Corvan, Brann rallume le feu dans l'épilogue.

| PNJ | Rôle | Dans l'histoire |
| --- | --- | --- |
| Mère Hulda, l'herboriste | Vend potions et cœurs | A soigné Corvan la nuit de l'éclipse ; remarque plus tard que la blessure « n'était pas si grave » |
| Pip, le gamin | Astuces de gameplay, tutoriel discret | Suit Brann partout |
| Old Tobias, le bûcheron | Ouvre le chemin du bois après l'acte 1 | Indice acte 1 : Corvan allait souvent en forêt |
| Dame Isolde, l'archiviste | Raconte l'histoire des sceaux (une scène, pas un pavé) | Acte 3 : retrouve le nom de Corvan dans les registres des anciens gardiens |
| Garrick, le marchand | Boutique : flèches, bombes, huile de lanterne, quart de cœur | Radin, touche d'humour |

**Évolution du village**

1. Début : brume épaisse, habitants apeurés, chemins fermés
2. Après la forêt : la brume se lève en partie, Tobias retourne au bois, flèches en boutique
3. Après la montagne : les mineurs reviennent, bombes en boutique, Hulda commence à douter
4. Après le lac : village vide pendant l'éclipse, ambiance tendue avant le final
5. Épilogue : soleil, fête sur la place, une dernière réplique par PNJ

Production : 3 ou 4 répliques par PNJ et par étape, dialogues en JSON indexés par les flags de la sauvegarde, un seul tileset avec variantes jour/brume par teinte de couleur.

**La carte du monde**

Environ 55 écrans au total pour 4 à 6 heures de jeu. Un écran = 256×224 px = 16×14 tuiles de 16 px.

Overworld de 5×4 écrans (1280×896 px, 80×56 tuiles) :

|  | Ouest | Ouest-centre | Centre | Est-centre | Est |
| --- | --- | --- | --- | --- | --- |
| Nord | Forêt | Forêt | Montagne | Montagne | Château |
| Nord-centre | Forêt | Forêt | Montagne | Col | Château |
| Sud-centre | Forêt | Village | Village | Route | Falaise |
| Sud | Grotte | Rive | Lac | Lac | Lac |

| Zone | Taille |
| --- | --- |
| Overworld (village 2, forêt 5, montagne 4, lac et rives 5, route/falaise/château 4) | 20 écrans |
| Temple des Racines (donjon tutoriel) | 8 à 9 salles |
| Mine Effondrée | 10 salles |
| Sanctuaire Englouti | 12 salles |
| Château final (couloir, 1-2 énigmes avec les 3 objets, combat contre Corvan) | 4 à 5 salles |
| Intérieurs (forge, Hulda, boutique, archives, 1-2 grottes secrètes), plus petits qu'un écran | 5 à 6 pièces |

Une salle de donjon = 1 écran ; les salles de boss peuvent en faire 2.

**Le bestiaire**

11 ennemis bâtis sur 4 comportements seulement : on code 4 IA, puis on change sprites, stats et paramètres.

- **Errant** : déplacement au hasard, dégâts au contact
- **Chasseur** : fonce sur Brann quand il est proche
- **Tireur** : garde ses distances et lance des projectiles
- **Spécial** : comportement propre à la zone, lié à l'objet du donjon

| Zone | Ennemi | Comportement | Coups (épée) | Particularité |
| --- | --- | --- | --- | --- |
| Forêt / Temple des Racines | Ronceau | Errant | 1 | Petite boule de ronces noires ; premier ennemi du jeu |
| Forêt / Temple des Racines | Sanglier noirci | Chasseur | 2 | Charge en ligne droite, se cogne aux murs |
| Forêt / Temple des Racines | Lutin des branches | Tireur | 1 | Caché dans un arbre, lance des glands ; arc ou attendre qu'il descende |
| Montagne / Mine Effondrée | Caillou rampant | Errant | 3 | Ronceau version pierre |
| Montagne / Mine Effondrée | Chauve-souris des mines | Chasseur | 1 | Vol en zigzag, difficile à toucher |
| Montagne / Mine Effondrée | Mineur maudit | Spécial | 2 | Bouclier de pierre qui bloque l'épée ; une bombe le fait tomber |
| Lac / Sanctuaire Englouti | Têtard d'encre | Errant | 2 | Nage en eau peu profonde, éclabousse |
| Lac / Sanctuaire Englouti | Crabe-armure | Chasseur | 3 | Vulnérable seulement de dos |
| Lac / Sanctuaire Englouti | Ombre noyée | Spécial | 2 | Invisible dans le noir ; la lanterne la révèle et l'immobilise |
| Château | Chevalier corrompu | Chasseur | 4 | Pare de face, attaque en série |
| Château | Œil de Morvath | Tireur | 1 flèche | Sentinelle murale ; la détruire à l'arc ouvre certaines portes |

**Règles communes**

- Dégâts infligés : ½ cœur en forêt, 1 cœur en montagne et au lac, 1 cœur ½ au château
- Butin : rubis (souvent), cœur (parfois), flèches et bombes une fois les objets obtenus
- Chaque ennemi porte un détail de corruption noire (ronces, taches, armure)
- Variante rouge plus forte de chaque ennemi par simple changement de palette
- Code : une scène par ennemi avec les composants `Health`, `HitBox`, `HurtBox`, `StateMachine` + une ressource `EnemyData` (PV, vitesse, dégâts, butin) pour équilibrer sans toucher au code

**La progression dans l'overworld**

Ordre fixe : forêt, montagne, lac, château. Chaque objet ouvre la zone suivante, et chaque blocage est visible avant d'être franchissable.

Au départ, Brann est à la forge et seule la forêt (ouest) est ouverte : brume épaisse au nord, éboulis au sud, falaise à l'est. Pip et les villageois en parlent.

| Étape | Donjon (emplacement) | Objet | Ce qu'il ouvre |
| --- | --- | --- | --- |
| 1 | Temple des Racines (fond de la forêt, nord-ouest) | Arc | Pont-levis relevé au-dessus d'un ravin au nord du village : une flèche dans la cible l'abaisse → route de la montagne |
| 2 | Mine Effondrée (col, est de la montagne) | Bombes | Éboulis sur la rive au sud du village → chemin du lac |
| 3 | Sanctuaire Englouti (milieu du lac, à l'est, accès par un ponton) | Lanterne | Grotte noire de la falaise à l'est de la route → château |
| 4 | Château (via la grotte de la falaise) | — | Combat final contre Corvan |

**Retours en arrière (secrets)**

- Arc : une cible cachée dans la forêt ouvre un passage vers un quart de cœur
- Bombes : la grotte du sud-ouest (mur fissuré visible dès le début) cache un réceptacle de cœur ; un mur fissuré au village mène à la cave secrète de Garrick
- Lanterne : une grotte sombre dans la montagne, repérée dès l'étape 2, mène à un quart de cœur ou une amélioration

**L'ouverture du jeu**

Environ 8 minutes ; le joueur contrôle Brann en moins de 30 secondes, et chaque scène apprend une mécanique tout en posant l'histoire.

| Temps | Scène | Ce que le joueur apprend ou découvre |
| --- | --- | --- |
| 0:00 | Écran titre : logo du corbeau et des trois cercles, brume, château sur la falaise | Ambiance, destination finale |
| 0:15 | Prologue en 3 écrans de texte, qu'on peut passer | Les sceaux, Morvath, l'éclipse de ce soir |
| 0:30 | Matin à la forge : Corvan demande du charbon | Se déplacer, interagir |
| 1:30 | Livraisons chez Garrick et Hulda, Pip suit Brann | Le village et ses PNJ ; Corvan rate un coup de marteau (indice) |
| 3:00 | Épée en bois pour « chasser les ronces du potager » ; un Ronceau minuscule | Attaquer, couper les buissons, ramasser des rubis |
| 4:30 | L'éclipse : ciel violet, musique coupée, grondement au château | Le drame commence |
| 5:00 | Corvan au sol, forge saccagée ; il confie la vraie épée | Épée et 3 cœurs de départ |
| 5:45 | Ronceaux et Sanglier noirci sur la place, Pip caché derrière le puits | Premier vrai combat, dans un espace fermé |
| 6:45 | Retour avec Hulda : le corps a disparu, traces de pas vers l'extérieur | Indice sur la fausse mort |
| 7:30 | Le corbeau sur l'enclume, Isolde explique les sceaux, Pip montre la forêt | Sauvegarde ; le joueur est libre |

Trois indices sur Corvan sont posés sans rien révéler : ses yeux, la blessure, les traces de pas.

Production : un petit système de cinématiques en C#, une liste d'actions (déplacer un PNJ, afficher un dialogue, attendre, changer la musique) jouées dans l'ordre, réutilisé pour toutes les scènes du jeu.

**Secrets et collectibles**

Brann démarre avec 3 cœurs et peut monter à 9 : 3 réceptacles de boss, 1 réceptacle secret, 8 quarts de cœur (= 2 cœurs). En plus, 10 plumes de corbeau cachées pour les joueurs qui fouillent tout.

| Où | Quarts de cœur | Comment |
| --- | --- | --- |
| Forêt | 2 | Cible cachée à l'arc ; souche creuse derrière des buissons |
| Montagne | 2 | Grotte sombre (lanterne) ; corniche à atteindre par un détour |
| Lac | 2 | Îlot près du ponton ; derrière une cascade |
| Village | 1 | Mini-jeu de Pip : retrouver 5 poules dans le village |
| Boutique de Garrick | 1 | À 150 rubis |

- Réceptacle secret : grotte du sud-ouest, derrière un mur fissuré (bombes)
- Cave secrète de Garrick (mur fissuré au village) : grand carquois et grand sac de bombes
- Plumes de corbeau : 10 au total, dans des coins de l'overworld et des donjons ; elles servent à la 2ᵉ amélioration de l'épée

**L'épée de Brann**

| Niveau | Nom | Comment l'obtenir | Effet |
| --- | --- | --- | --- |
| 1 | Épée de Corvan | Ouverture du jeu | Dégâts de base |
| 2 | Épée trempée | Minerai d'étoile trouvé dans la Mine (obligatoire), à reforger à la forge après le 2ᵉ sceau | Dégâts ×2 |
| 3 | Lame du Corbeau | Les 10 plumes de corbeau, forgées à la forge (optionnel) | Lance une onde à distance quand Brann a toute sa vie |

C'est Brann qui forge lui-même ses améliorations : il passe d'apprenti à forgeron au fil du jeu.

**L'économie**

- Rubis : vert = 1, bleu = 5, rouge = 20 ; bourse limitée à 300
- Hulda : potion rouge (rend toute la vie) à 40 rubis, 2 potions maximum dans l'inventaire
- Garrick : 10 flèches à 20, 5 bombes à 30, huile de lanterne à 10, quart de cœur à 150
- Cave secrète : grand carquois à 100, grand sac de bombes à 100
- Les ennemis et les buissons lâchent assez de rubis pour les munitions ; les gros achats (quart de cœur, sacs) demandent d'économiser ou d'explorer

**Morvath**

- Ancien mage de la cour de Brumeval, qui cherchait l'immortalité en volant la force vitale des gens ; les trois gardiens l'ont enfermé sous le château il y a mille ans
- Jamais montré en entier : une ombre avec un seul œil doré, le même symbole que les Œils de Morvath du château
- Il agit par la corruption (ronces, pierre, eau noires) et par les murmures qu'il adresse à Corvan
- Au combat final, il est la corruption qui recouvre Corvan ; vaincu, il est enfermé dans le nouveau sceau unique forgé par Brann

**Les musiques**

Une quinzaine de pistes ; pour gagner du temps, un même thème peut être réarrangé (thème du village joyeux / sous la brume, thème de l'overworld décliné par zone).

| Piste | Utilisation |
| --- | --- |
| Titre | Écran titre, calme et mélancolique |
| Village (jour) / Village (brume) | Même thème, deux arrangements |
| Thème de Corvan | Forge, scènes avec Corvan, révélation (version sombre) |
| Overworld forêt / montagne / lac | Un thème principal, trois arrangements |
| Donjon 1, 2, 3 | Un thème par donjon |
| Boss | Combats contre les gardiens |
| Combat final | Corvan et Morvath |
| Fin et générique | Épilogue, fête au village |
| Jingles | Objet obtenu, secret découvert, sceau restauré, game over |

**Options et accessibilité**

- Difficulté : Normal ou Facile (dégâts reçus divisés par 2)
- Langues : français et anglais dès le départ ; tous les textes dans un fichier CSV de traduction, affichés via `Tr()` dans Godot
- Commandes : remappage clavier et manette
- Son : volume de la musique et des effets séparés
- Affichage : plein écran, échelle de la fenêtre
- Confort : vitesse du texte, réduction des flashs et tremblements d'écran

**Le système de sauvegarde**

Deux mécanismes complémentaires, pour qu'un joueur ne perde jamais plus de quelques minutes.

| Type | Quand | Détail |
| --- | --- | --- |
| Manuelle | Aux statues du corbeau | Une à l'entrée de chaque donjon, 1 ou 2 dans l'overworld, plus la forge (corbeau sur l'enclume) ; restaure aussi la vie |
| Automatique | Changement de zone, ouverture d'un coffre important, après chaque boss | Discrète : petite icône de corbeau dans un coin de l'écran |

- 3 emplacements de sauvegarde ; chaque emplacement garde le dernier état, manuel ou automatique
- Game over : reprise au dernier point d'entrée de la zone, avec 3 cœurs
- Fichier JSON avec numéro de version dans `user://saveN.json` ; tout l'état vient de `GameState`

**Le corbeau, fil rouge visuel**

- Motif sur l'écharpe de Brann et sur la garde de son épée
- Logo du jeu : un corbeau stylisé entouré de trois cercles, un par sceau
- Un corbeau près des statues de sauvegarde, qui guide aussi vers l'entrée du donjon suivant

## Phase 0 — Apprendre Godot et s'outiller (≈ 3 à 4 semaines)

But : maîtriser la logique scènes/nœuds/signaux de Godot et avoir un projet C# propre, versionné, qui démarre.

**Setup**

- [x] Installer la dernière version stable de Godot 4 en **édition .NET** (4.7.x en juillet 2026) + le SDK .NET demandé par cette version
- [x] Choisir un IDE : VS Code + extension C# Dev Kit + Claude Code et les 5 agents du projet
- [ ] Installer l'éditeur de cartes **Tiled** et l'addon d'import Tiled pour Godot (YATI), avec l'accord explicite avant installation
- [ ] Créer une carte Tiled de test (une salle de 16×14 tuiles avec les calques de `CLAUDE.md`) et vérifier qu'elle s'importe dans Godot
- [ ] Créer un dépôt Git (GitHub/GitLab), avec un `.gitignore` qui exclut le dossier `.godot/`
- [ ] Décider des plateformes : PC (Windows/Linux/Mac) en priorité. Un projet Godot en C# ne s'exporte pas officiellement vers le web en 2026, donc pas de démo navigateur sur itch.io : prévoir un build PC téléchargeable.

**Apprentissage**

- [ ] Faire le tutoriel officiel « Your first 2D game » en le réécrivant en C#
- [ ] Comprendre : Node vs Scene, `_Ready` / `_Process` / `_PhysicsProcess`, signaux (`[Signal]` + `EmitSignal`), `[Export]`, autoloads, ressources (`Resource`)
- [ ] Comprendre le monde 2D : `CharacterBody2D`, `Area2D`, couches/masques de collision, `AnimatedSprite2D` vs `AnimationPlayer`, `TileMapLayer` (ce que produit l'import des cartes Tiled)

**Réglages pixel art (à faire dès le début)**

- [x] Résolution de base proche de la SNES : 256×224 (ou 320×180 pour du 16:9), tuiles de 16×16 px
- [x] Stretch mode `viewport`, scale mode `integer`, filtre de texture `Nearest` (pas de flou)

**Livrable** : un projet vide qui se lance, est sur Git, affiche une tuile nette en plein écran.

## Phase 1 — Prototype de déplacement (≈ 4 semaines)

But : un personnage qui se déplace dans 2 ou 3 écrans reliés, avec des formes placeholder (carrés de couleur suffisent).

- [ ] Personnage `CharacterBody2D` : déplacement 8 directions, vitesse constante, `MoveAndSlide()`
- [ ] Orientation sur 4 directions (haut/bas/gauche/droite) gardée en mémoire pour les animations et l'attaque
- [ ] Input Map : actions `move_*`, `attack`, `use_item`, `interact`, `pause` (clavier + manette dès maintenant)
- [ ] 3 cartes Tiled de test avec collisions (murs, eau, buissons), objets `Spawn` et `Sortie` lus par le code
- [ ] Caméra façon SNES : décider entre **défilement par écran** (transition glissée en salle de donjon) et **caméra qui suit** (overworld). Zelda SNES fait les deux : coder les deux modes.
- [ ] Transitions entre zones : `Area2D` en bord d'écran → chargement de la scène suivante + point d'apparition
- [ ] Gestionnaire de scènes en autoload (`SceneManager`) avec fondu au noir
- [ ] Tri en profondeur : `YSortEnabled` pour que le joueur passe devant/derrière les objets

**Livrable** : on se balade entre 3 écrans avec transitions et collisions correctes. Le déplacement doit déjà être agréable : c'est ce que le joueur ressentira pendant tout le jeu.

## Phase 2 — Combat et ennemis (≈ 6 semaines)

But : un combat à l'épée lisible et satisfaisant contre 3 types d'ennemis.

**Joueur**

- [ ] Machine à états du joueur : `Idle`, `Move`, `Attack`, `Hurt`, `Dead` (une classe par état ou un `enum` + `switch` pour commencer)
- [ ] Attaque à l'épée : hitbox `Area2D` activée quelques frames, orientée selon la direction
- [ ] Système hitbox / hurtbox réutilisable (composants `HitBox` et `HurtBox` avec dégâts et équipe)
- [ ] Recul (knockback) + invincibilité temporaire avec clignotement après un coup
- [ ] « Game feel » : hit-stop de 2-3 frames, petit tremblement de caméra, flash blanc sur l'ennemi touché

**Ennemis**

- [ ] Composant `Health` partagé joueur/ennemis (signal `Died`, `Damaged`)
- [ ] Ennemi 1 : patrouille aléatoire, dégâts au contact
- [ ] Ennemi 2 : poursuit le joueur quand il est proche (`NavigationAgent2D` ou ligne droite)
- [ ] Ennemi 3 : attaque à distance (projectile)
- [ ] Butin à la mort : cœur, rubis, avec probabilité
- [ ] Réapparition des ennemis quand on quitte et revient sur l'écran

**Livrable** : un écran avec 5 ennemis qu'on a envie de recombattre. Faire tester à quelqu'un.

## Phase 3 — Vie, inventaire, objets, sauvegarde (≈ 6 semaines)

But : la boucle « je ramasse, j'équipe, je sauvegarde, je recharge » fonctionne de bout en bout.

**HUD et ressources**

- [ ] HUD en `CanvasLayer` : cœurs (avec demi-cœurs), rubis, clés, objet équipé
- [ ] Réceptacles de cœur / quarts de cœur qui augmentent la vie max
- [ ] Objets ramassables génériques (`Pickup` + une `Resource` qui décrit l'effet)

**Inventaire et objets**

- [ ] Définir chaque objet comme une `Resource` C# (`ItemData` : id, nom, icône, type, quantité max)
- [ ] Écran d'inventaire en pause (grille, sélection à la manette)
- [ ] Objet assigné à la touche `use_item`
- [ ] Implémenter 2 objets « clés » qui servent aux énigmes : par exemple **arc** (activer des interrupteurs à distance) et **bombes** (ouvrir des murs fissurés)
- [ ] Coffres (petit objet / objet clé) avec la petite animation « objet levé au-dessus de la tête »

**Sauvegarde**

- [ ] Un objet `GameState` en autoload qui contient TOUT l'état persistant : vie, inventaire, rubis, flags (coffres ouverts, portes déverrouillées, boss vaincus), position de reprise
- [ ] Chaque coffre/porte a un identifiant unique (ex. `dungeon1_chest_03`) pour retrouver son état
- [ ] Sérialisation en JSON avec `System.Text.Json` dans `user://save1.json` ; 3 emplacements de sauvegarde
- [ ] Numéro de version dans la sauvegarde (pour migrer quand le format change)
- [ ] Écran titre : Nouvelle partie / Continuer ; statues du corbeau (sauvegarde manuelle) et sauvegarde automatique aux changements de zone, coffres importants et boss (voir « Le système de sauvegarde »)

**Livrable** : je joue, j'ouvre un coffre, je quitte, je relance : le coffre est toujours ouvert et l'objet dans mon inventaire.

## Phase 4 — Premier donjon complet : la vertical slice (≈ 8 semaines)

But : un donjon de 8 à 12 salles, jouable du début à la fin, avec son objet, ses énigmes et son boss. C'est le point de contrôle du projet.

**Briques d'énigmes (réutilisables partout)**

- [ ] Portes : verrouillées par petite clé, par grande clé (boss), ou qui s'ouvrent quand tous les ennemis sont morts
- [ ] Interrupteurs au sol (plaque de pression) et interrupteurs à frapper
- [ ] Blocs poussables (alignés sur la grille 16×16)
- [ ] Torches à allumer, murs fissurés (bombes), trous qui font tomber à l'étage inférieur
- [ ] Un petit système « déclencheur → cible » via signaux, pour câbler une énigme dans l'éditeur sans écrire de code

**Structure du donjon**

- [ ] Concevoir sur papier d'abord : plan des salles, emplacement de la carte, de la boussole, de l'objet du donjon, de la grande clé
- [ ] Règle Zelda : l'objet trouvé au milieu du donjon sert à finir le donjon ET à battre le boss
- [ ] Carte du donjon dans le menu pause (salles visitées + boussole qui montre le boss)

**Boss**

- [ ] Machine à états avec 2 ou 3 phases, attaques télégraphiées (le joueur voit venir le coup)
- [ ] Point faible lié à l'objet du donjon
- [ ] Récompense : réceptacle de cœur + cristal/médaillon (compteur de progression du jeu)

**Point de contrôle** : faire jouer le donjon à 2 ou 3 personnes sans les aider. Noter où elles bloquent et où elles s'ennuient. Ne pas passer en production tant que ce donjon n'est pas fun.

## Phase 5 — Direction artistique et audio originaux (en parallèle, à partir de la phase 2)

But : un style simple et cohérent, que tu peux produire vite. À travailler une soirée par semaine pendant les phases 2 à 4, puis à fond avant la production.

**Pixel art**

- [ ] Outil : Aseprite (payant, la référence) ou LibreSprite / Pixelorama (gratuits)
- [ ] Fixer une palette limitée (24 à 32 couleurs ; partir d'une palette existante de Lospec est un bon raccourci)
- [ ] Tuiles 16×16, personnage 16×16 ou 16×24, contour sombre ou non : décider une fois pour toutes
- [ ] Ordre de production : tileset d'un donjon → joueur (marche + attaque, 4 directions) → 3 ennemis → objets/UI → boss
- [ ] Utiliser les **terrains (autotiling) de Tiled** pour peindre les niveaux plus vite
- [ ] Écrire une page « bible graphique » : palette, tailles, nombre de frames par animation

**Audio**

- [ ] Effets sonores : jsfxr / ChipTone pour générer des sons rétro (épée, coup, rubis, coffre, porte)
- [ ] Musique : un tracker (Furnace, qui peut émuler la puce son SNES) ou un DAW (LMMS gratuit)
- [ ] Pistes minimum : titre, overworld, village, donjon (×1 ou ×3), boss, victoire, game over
- [ ] Bus audio séparés Musique / SFX dans Godot + réglage du volume dans les options

**Livrable** : la vertical slice de la phase 4 entièrement habillée avec tes propres assets.

## Phase 6 — Production du contenu (≈ 5 à 6 mois)

But : construire le reste du jeu avec les briques déjà validées. Ici on code peu de nouveaux systèmes, on assemble.

**Monde (volontairement compact)**

- [ ] Overworld de 5×4 écrans (voir « La carte du monde »), découpé en 3 zones (une par donjon), avec des passages bloqués qui s'ouvrent grâce aux objets des donjons
- [ ] Un village : Brumeval et ses 5 PNJ avec dialogues simples (boîte de texte + défilement lettre par lettre), une boutique
- [ ] Quelques secrets : grottes cachées, quarts de cœur

**Donjons 2 et 3**

- [ ] Un nouvel objet par donjon (bombes pour le donjon 2, lanterne pour le donjon 3), chacun réutilisé dans les donjons suivants
- [ ] 2 nouveaux ennemis par donjon + variantes de couleur des anciens
- [ ] Difficulté progressive ; un boss par donjon

**Histoire et fin**

- [ ] Ouverture scriptée (voir « L'ouverture du jeu ») et système de cinématiques, séquence de fin, générique
- [ ] Option : un donjon final court si le temps le permet, sinon le boss du donjon 3 est le boss final

**Méthode** : un donjon = environ 6 à 8 semaines (conception papier → blockout → énigmes → art → test). Faire tester chaque donjon dès qu'il est jouable.

## Phase 7 — Polish, tests et sortie (≈ 2 mois)

But : un jeu fini, stable, que des inconnus peuvent télécharger et terminer.

- [ ] Menu options : volume musique/SFX, plein écran, échelle de la fenêtre, remappage des touches
- [ ] Écran de game over + reprise au dernier point d'entrée
- [ ] Passe « juice » : particules (herbe coupée, poussière), animations d'UI, transitions
- [ ] Équilibrage : dégâts, vie des ennemis, prix de la boutique, nombre de cœurs
- [ ] Session de test avec 5+ joueurs, liste des bugs dans un tableau ou des issues GitHub
- [ ] Exports Windows / Linux / macOS, tester chaque build sur une autre machine
- [ ] Page itch.io (build téléchargeable), captures, GIF de gameplay, courte bande-annonce
- [ ] Optionnel plus tard : Steam (frais d'entrée et page à préparer plusieurs semaines avant)

**Livrable** : version 1.0 publiée.

## Architecture C# recommandée et pièges à éviter

**Arborescence de départ**

```
res://
  maps/        cartes Tiled (.tmx) et tilesets (tilesets/*.tsx)
  scenes/      (player/, enemies/, items/, puzzles/, rooms/, ui/)
  scripts/     (même découpage, un .cs par scène)
    core/      GameState.cs, SceneManager.cs, AudioManager.cs, SaveSystem.cs
    components/ Health.cs, HitBox.cs, HurtBox.cs, StateMachine.cs
  resources/   items/*.tres, enemies/*.tres
  art/  audio/
```

**Principes**

- Composition plutôt qu'héritage : un ennemi = `CharacterBody2D` + nœuds enfants `Health`, `HurtBox`, `HitBox`, `StateMachine`
- Les données dans des `Resource` (stats d'ennemis, objets), le comportement dans les scripts : on équilibre sans toucher au code
- Communication par signaux (ou events C#) ; éviter les `GetNode("../../..")` fragiles
- Peu d'autoloads (4 maximum : état du jeu, scènes, audio, sauvegarde)

**Pièges fréquents en C# sous Godot**

- Les classes de script doivent être `partial` et le nom du fichier doit correspondre au nom de la classe
- Recompiler (Build) après avoir ajouté un `[Export]` ou un `[Signal]`, sinon l'éditeur ne le voit pas
- Allocations à chaque frame (LINQ, `new` dans `_Process`) : à éviter dans les boucles chaudes
- Ne pas viser un Zelda SNES complet : 3 donjons finis valent mieux que 8 commencés
- Ne pas peaufiner les graphismes avant que la mécanique soit validée (phase 4)

**Ressources utiles** : documentation officielle Godot (section C#), la communauté Godot sur Discord/Reddit, et Lospec pour les palettes.
