# Phase 2C — Graphiques et lancement moderne par défaut

Cette étape complète l’implémentation de la phase 2. Elle dépend de la phase 2B.
La validation finale des graphiques intégrés reste à faire sur Windows.

## Graphiques disponibles

### Rendez-vous par mois

Courbe du nombre de rendez-vous selon leur date prévue, sur les six mois
calendaires se terminant au mois actuel. Tous les statuts sont inclus. Les mois
sans rendez-vous sont affichés à zéro. Les rendez-vous hors période ne sont pas
dans la courbe, mais restent dans le compteur global du module.

Seules les dates ISO `AAAA-MM-JJ` sont interprétées. Les anciennes dates comme
`10/9/26` ou `09/10/2026` peuvent dépendre de la langue du calendrier d’origine.
Elles ne sont pas devinées et un message indique le nombre de dates exclues.
Leur correction passe par le formulaire de modification de rendez-vous.

### Décaissements payés par motif

Diagramme en anneau des transactions de type **Décaissement** et de statut
**Payée**, sur toutes les dates. Les encaissements et factures non payées
n’y figurent pas. Les cinq motifs les plus importants sont montrés ; les motifs
restants sont regroupés sans perdre leur montant total. Les motifs longs sont
abrégés dans la légende ; leur texte complet reste dans la liste des finances.

Un montant historique invalide ou non entier est exclu avec un compteur visible.
Les montants restent exprimés dans l’unité utilisée par l’utilisateur : le modèle
ne stocke pas de devise et le graphique n’invente pas un symbole euro/dollar.
Une base vide affiche un message, sans données fictives ni diagramme artificiel.

## Intégration et cycle de vie

- `backend/statistics.py` calcule les indicateurs à partir d’une lecture cohérente
  de SQLite, sans aucune dépendance graphique.
- `ui/charts.py` construit les figures Matplotlib sans créer de fenêtre Tk.
- `ui/application.py` intègre les figures via `FigureCanvasTkAgg`.
- Les figures sont dessinées sur le fil Tkinter ; les requêtes restent sur le
  fil de travail pour éviter les accès aux widgets depuis un autre fil.
- Le tableau de bord défile verticalement et les compteurs sont regroupés
  sur une ligne, pour garder les graphiques lisibles.
- Le passage clair/sombre redessine le tableau de bord avec la palette adaptée.
- La navigation libère les anciennes figures et annule leurs callbacks TkAgg
  avant destruction des widgets pour éviter l’accumulation de graphiques.

Cette séparation permet de tester les calculs et de rendre les figures sans
ouvrir une interface. Les tests Windows contrôlent ensuite leur intégration.

## Points d’entrée

`main.py` lance maintenant l’interface moderne : connexion, menu, formulaires,
listes et graphiques. `main_modern.py` reste un alias compatible.
L’ancienne application est conservée dans `main_legacy.py` pendant la transition.
Les anciens guides des phases 2A et 2B décrivent leur état à l’époque : c’est ce
guide qui définit les points d’entrée après application de la phase 2C.

## Appliquer et tester sous Windows

Depuis un état de travail propre, partir de la branche **phase 2B** :

```bat
git switch -c refactor/phase-2-charts-codex refactor/phase-2-management-codex
git am "C:\CHEMIN\PersonalManager_Phase2C.patch"
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe tests/run_tests.py
```

La suite contient **57 tests** et doit réussir sans test ignoré.
Matplotlib est une nouvelle dépendance : ne pas omettre l’installation.

Fermer l’application, puis préparer une copie dédiée :

```bat
copy projet_stage.db "%TEMP%\personal-manager-phase2c.db"
set "PERSONAL_MANAGER_DB=%TEMP%\personal-manager-phase2c.db"
.venv\Scripts\python.exe main.py
```

Vérifier le tableau de bord vide ou avec les données existantes, puis ajouter :

1. Un rendez-vous avec une date du mois actuel, et un autre avec une date du mois
   précédent. Actualiser la vue d’ensemble : la courbe doit refléter ces dates.
2. Un décaissement payé, un décaissement non payé et un encaissement. Seul le
   décaissement payé doit alimenter l’anneau.
3. Modifier le montant ou le statut d’une transaction, puis actualiser : la
   répartition doit changer sans ajout d’une ligne.

Tester les thèmes clair et sombre, le redimensionnement et plusieurs allers-retours
entre tableau de bord et listes. Vérifier le défilement, les légendes et les
messages concernant les anciennes dates. Ne pas comparer le compteur de tous
les rendez-vous avec une courbe limitée à six mois comme s’ils avaient le même
périmètre.

Après fermeture de l’application :

```bat
set "PERSONAL_MANAGER_DB="
git push -u origin refactor/phase-2-charts-codex
```

## Vérifications effectuées

Dans l’environnement de préparation : **40 tests réussis et 17 ignorés**, car
bcrypt/CustomTkinter ne sont pas installés. Matplotlib est disponible.

- Six tests d’agrégation SQLite : périodes traversant une année, dates invalides,
  factures non payées, encaissements, montants invalides et regroupement des motifs.
- Deux tests de rendu Matplotlib : données vides/remplies dans les deux thèmes.
- Figures rendues et inspectées visuellement hors de Tkinter ; légendes corrigées
  pour rester dans la figure. Les données utilisées pour cette inspection sont
  uniquement des exemples de test, jamais injectés dans l’application.
- Un nouveau test Windows contrôle le changement de thème et la libération des
  graphiques lors de la navigation.
- Les nouveaux fichiers Python passent la vérification syntaxique.

Le rendu **dans la fenêtre Windows** reste à vérifier par l’utilisateur.
La phase 2 sera validée après le passage des 57 tests et cette revue.

## Pour expliquer le travail en entretien

« J’ai séparé les calculs statistiques de leur affichage. Les graphiques utilisent
les vrais enregistrements, avec un périmètre explicitement défini. J’ai conservé
les mois à zéro et signalé les anciennes dates ambiguës, plutôt que de produire
une courbe trompeuse. J’ai testé les figures sans interface, puis prévu des tests
Windows pour leur intégration et leur cycle de vie. »

Documentation : https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
