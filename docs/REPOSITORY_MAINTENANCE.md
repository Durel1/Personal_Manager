# Nettoyage et livraison du dépôt

## Commits de cette livraison

1. Suppression de l’ancienne interface, de ses ressources et de tkcalendar.
   Six tests exclusivement consacrés à cette interface sont retirés. Les tests
   modernes de connexion, formulaires, permissions et rapports restent présents.
2. README standardisé et outil de captures adapté ; documentation historique conservée.
3. Tests graphiques exécutés chacun dans un processus neuf, sans partage des
   ressources Tk/CustomTkinter entre fenêtres de tests ; délai de 60 secondes par
   test graphique et 300 secondes pour les tests backend. Une expiration ou un test
   ignoré fait échouer le contrôle. Les workflows ont aussi une limite globale.
4. Licence MIT choisie par le propriétaire, badges, automatisation de livraison
   et outil de configuration GitHub.

Le changement de lancement des tests répond au blocage observé dans Actions.
Sa validation complète exige une exécution Windows et une CI verte ; il ne faut
pas annoncer le problème résolu avant cette vérification.

## Appliquer le patch depuis main sous Windows

Avant de commencer, `git status` doit être propre. Si le commit de retrait des
bases/caches n’a pas encore été intégré dans main, lancer le nettoyage après le patch.

```bat
git switch main
git pull --ff-only origin main
git switch -c chore/repository-polish
git am "C:\CHEMIN\PersonalManager_Nettoyage.patch"
.venv\Scripts\python.exe tools/clean_git_tracking.py
git status
```

Si le script a préparé des suppressions du suivi Git :

```bat
git commit -m "chore: stop tracking local databases, caches and IDE files"
```

Les bases restent sur le disque. Le patch ne contient aucune base personnelle,
ni aucune instruction de réécriture de l’ancien historique. Les anciens mots de
passe publiés restent exposés dans l’historique : changer tout mot de passe réel
ou réutilisé. La suppression de données historiques doit être organisée à part.

```bat
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe tests/run_tests.py
git push -u origin chore/repository-polish
```

Attendre la réussite de la PR et fusionner avec **Create a merge commit**.
Les 94 tests doivent être découverts ; tous les groupes doivent réussir, sans test
ignoré. Le processus principal signale explicitement le test ayant dépassé le délai.
Les captures modernes déjà présentes sur main restent conservées.

## Configurer GitHub depuis votre session

Les outils connectés utilisés pour préparer cette livraison ne proposent pas
l’écriture de description/topics, la protection des branches ou la création de
Releases. Le script ci-dessous utilise votre GitHub CLI authentifié ; aucun jeton
ne doit être copié dans le dépôt ou dans une conversation.

Installer GitHub CLI si nécessaire (`winget install --id GitHub.cli`), rouvrir le
terminal puis `gh auth login`. Après fusion du nettoyage et réussite de test sur main :

```bat
git switch main
git pull --ff-only origin main
.venv\Scripts\python.exe tools/configure_github.py --protect-main --delete-merged-branches
```

Le script configure la description, les topics et la suppression automatique des
branches après fusion. Il crée une protection seulement si main n’est pas déjà
protégée : PR obligatoire, contrôle `test` réussi, branche à jour, aucun push forcé
ni suppression de main, règles applicables aux administrateurs. Aucun approbateur
n’est imposé pour ne pas bloquer un développeur travaillant seul. Des protections
existantes restent intactes.

Les anciennes branches de phases sont retirées uniquement si leur commit est un
ancêtre de main ; une protection ou des commits non intégrés empêchent leur retrait.
Une vérification du SHA empêche une suppression si une nouvelle modification a été
poussée entre le contrôle et la suppression. L’historique intégré dans main reste intact.

## Publier la première version

Lancer d’abord **Windows executable** dans Actions avec **Run workflow** sur main.
Le workflow teste le code, construit le logiciel, contrôle bcrypt/SQLite/Matplotlib/
Excel/PDF et fournit un ZIP contenant le dossier PersonalManager et `_internal`.
Télécharger l’artefact, extraire les archives et vérifier manuellement la fenêtre,
les formulaires, les exports et la persistance après fermeture/réouverture.

Après validation et synchronisation de main :

```bat
git tag -a v1.0.0 -m "PersonalManager 1.0.0 - modern desktop release"
git push origin v1.0.0
```

Ce tag déclenche une construction contrôlée puis la publication d’une Release
avec `PersonalManager-Windows.zip`. Le tag doit pointer vers un commit intégré
dans main. Aucune publication n’a lieu en cas d’échec des tests ou de la construction.
Ne pas ajouter dist, build, une base locale ou un exécutable dans un commit.
Le workflow manuel ne publie pas de Release : seul le lancement sur un tag le fait.

Documentation des commandes :
- https://cli.github.com/manual/gh_repo_edit
- https://cli.github.com/manual/gh_release_create
