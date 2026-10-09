# Phase 4 — Préparation de la livraison Windows

Cette étape part de la phase 3 complète validée. Elle prépare les diagnostics,
la distribution et la présentation du projet. La construction réelle du .exe,
les captures et la revue finale doivent encore être faites sur Windows.

## Modifications

- Les erreurs inattendues du fil de travail et des callbacks d’affichage sont
  journalisées avec un message lisible dans l’interface. Les erreurs de validation
  restent affichées dans le formulaire. Les erreurs au lancement sont aussi prises
  en charge, y compris avec un exécutable sans console.
- Les journaux sont limités en taille et n’incluent ni les valeurs des exceptions,
  ni les paramètres SQL, ni les mots de passe. Ils indiquent le type d’erreur et
  les fonctions/lignes concernées, pour aider au diagnostic.
- Le programme empaqueté crée sa base dans les données locales de l’utilisateur,
  pas dans le dossier du programme ni dans le dossier temporaire de PyInstaller.
  Le lancement depuis les sources conserve le chemin historique du projet.
- La spécification PyInstaller inclut les ressources CustomTkinter et les polices
  ReportLab. Elle ne copie jamais la base personnelle dans l’application.
- Un contrôle intégré vérifie les imports, SQLite/bcrypt, les graphiques et les
  fichiers Excel/PDF sur une base temporaire. Il restaure la variable d’environnement
  originale et ne touche pas aux données personnelles.
- Le README décrit l’usage réel, les limites, l’architecture et les tests. L’ancien
  texte est archivé dans docs/archive/README_ORIGINAL.md.
- L’outil de captures photographie le vrai logiciel dans une session Windows,
  avec des données temporaires. Il ajoute trois images et la galerie au README.

## Appliquer et tester

Fermer l’application. Partir de la branche phase 3, sans modifications en attente :

```bat
git switch -c chore/phase-4-release-codex feat/phase-3-complete-codex
git am "C:\CHEMIN\PersonalManager_Phase4.patch"
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe tests/run_tests.py
```

La suite contient **97 tests** et doit passer sans test ignoré sous Windows.
requirements-build.txt inclut les dépendances de l’application, les tests et
PyInstaller. Utiliser le Python standard de l’environnement virtuel.

## Captures réelles pour le README

```bat
.venv\Scripts\python.exe tools/capture_screenshots.py
```

Garder le bureau visible, éviter d’utiliser la souris ou de déplacer des fenêtres
pendant la capture. Les données de démonstration sont dans une base temporaire
distincte. L’outil restaure PERSONAL_MANAGER_DB à la fin. Il ne lit pas la base
personnelle pour produire les images. Vérifier les trois PNG de docs/images :
fenêtre complète, textes lisibles, absence de fenêtres superposées. La vue
d’ensemble défile : une capture du haut montre les compteurs et la courbe.

Après inspection :

```bat
git add readMe.md docs/images
git commit -m "docs: add screenshots of the modern Windows interface"
```

## Retirer les fichiers locaux déjà suivis par Git

Le projet original suivait sa base SQLite, des caches Python et des fichiers IDE.
La règle .gitignore ne retire pas les fichiers déjà suivis. Le patch ne les
supprime pas du disque, car cela pourrait effacer la base locale pendant git am.

```bat
.venv\Scripts\python.exe tools/clean_git_tracking.py
git status
git commit -m "chore: stop tracking local database and generated files"
```

L’outil utilise git rm --cached : les fichiers restent sur le PC. Cela retire
leur suivi pour les prochains commits, sans réécrire l’historique. Si Git indique
qu’il n’y a rien à committer, les fichiers avaient déjà été retirés du suivi.
Les anciennes versions restent accessibles dans l’historique Git.

## Construire et contrôler l’exécutable

```bat
.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm PersonalManager.spec
start /wait "" "dist\PersonalManager\PersonalManager.exe" --self-test-result "%TEMP%\personalmanager-build-check.json"
type "%TEMP%\personalmanager-build-check.json"
```

Le résultat JSON doit contenir ok: true et quatre contrôles réussis. Une erreur
indique son type, sans valeur sensible. Ce contrôle fonctionne sans fenêtre et
sert aussi au workflow GitHub Windows executable.

Le mode dossier (onedir) rassemble l’exécutable et ses ressources. Distribuer tout
dist/PersonalManager, pas uniquement le .exe. PyInstaller construit un programme
pour la plateforme où il s’exécute : produire un .exe nécessite Windows.

Pour la revue graphique, lancer PersonalManager.exe par double-clic. Il utilise
par défaut une nouvelle base dans %LOCALAPPDATA%\PersonalManager, sauf si
PERSONAL_MANAGER_DB est défini dans son environnement. Pour vérifier le démarrage
normal depuis le terminal, effacer cette variable avant lancement :

```bat
set "PERSONAL_MANAGER_DB="
start "" "dist\PersonalManager\PersonalManager.exe"
```

Créer un compte de test et vérifier connexion, formulaires, rôles, graphiques,
exports, thèmes et fermeture. Relancer et vérifier la persistance. Le contrôle
automatique ne remplace pas cette revue d’une véritable fenêtre Windows.

## Distribuer

Archiver le dossier PersonalManager entier et tester l’archive après extraction
dans un autre dossier, idéalement sur un PC sans Python. La base locale existante
reste en dehors de l’archive : déplacer le programme ne déplace pas les données.
Cette préparation ne publie aucune release et ne fusionne aucune branche.

Le workflow manuel de construction sera accessible depuis Actions lorsque son
fichier aura été intégré à la branche par défaut du dépôt. Il exécute les tests,
construit l’application, contrôle le binaire et conserve le dossier comme artifact.

Après la validation locale et les commits de captures/nettoyage :

```bat
git push -u origin chore/phase-4-release-codex
```

## Pour l’entretien

« J’ai traité séparément les erreurs métier et les erreurs inattendues. Le programme
affiche un message utilisable et conserve un diagnostic limité sans données sensibles.
J’ai préparé une distribution avec les ressources graphiques et un dossier de données
indépendant. J’ai ajouté un contrôle de l’exécutable pour tester les dépendances réellement
embarquées, puis une revue graphique sur Windows. Les captures proviennent du logiciel
avec des données de démonstration isolées. »

## Vérifications de préparation et limites

Localement : **97 tests, 71 réussis, 26 ignorés**. bcrypt et CustomTkinter ne sont
pas disponibles dans cet environnement ; les tests cryptographiques, les widgets
et le contrôle intégré complet restent à exécuter sur Windows. Les nouveaux tests
exécutés vérifient le chemin de stockage, la priorité du chemin personnalisé,
l’absence de valeurs sensibles dans les journaux, la tolérance à une panne de
journalisation et la conservation des fichiers par le nettoyage Git.

La syntaxe, le diff et l’application du patch sont vérifiés. Aucun .exe Windows
ni capture du nouveau design n’a été produit dans cet environnement Linux.
Ne déclarer la livraison finale terminée qu’après les vérifications ci-dessus.

Références :
- https://pyinstaller.org/en/stable/spec-files.html
- https://pyinstaller.org/en/stable/
- https://customtkinter.tomschimansky.com/documentation/packaging/
