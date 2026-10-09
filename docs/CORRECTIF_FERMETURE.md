# Correctif de fermeture après validation Windows

Le journal Windows reçu confirme que les 97 tests de phase 4 passent sous
Python 3.14.2, que l’outil a créé les trois captures et que PyInstaller 6.22.3
a terminé la construction. Le contrôle du binaire et la revue des captures
ne sont pas encore confirmés.

Le même journal contient des erreurs Tcl en arrière-plan : update et
check_dpi_scaling sont appelés après destruction d’une fenêtre. Un résultat
unittest OK n’implique pas l’absence de ces erreurs hors des assertions.

## Correction

La fermeture invalide les résultats en attente, annule les tâches planifiées,
libère les graphiques et détruit les widgets. Tous les timers et callbacks idle
de l’interpréteur propre à cette application sont annulés au niveau Tcl avant
la destruction, puis une seconde fois après celle-ci.

Cette annulation ne s’applique jamais à la navigation : les timers de l’interface
restent actifs pendant son utilisation normale. Elle ne supprime pas prématurément
les commandes Tcl appartenant aux widgets enfants : chaque widget conserve la
responsabilité de leur destruction. Un second appel à close est sans effet.

Deux tests utilisent un vrai interpréteur Tcl sans affichage. Ils vérifient
l’annulation des callbacks et la conservation des commandes pour leur propriétaire.
Un test Windows ferme l’application avec des callbacks de widgets en attente,
vérifie qu’il n’en reste aucun et intercepte les éventuelles erreurs bgerror.

La suite contient maintenant 100 tests. Localement, 73 passent et 27 sont ignorés
faute de bcrypt/CustomTkinter ; la fermeture réelle des widgets reste à vérifier
sur Windows. Le correctif retire aussi la ligne vide finale de l’archive README
qui avait causé l’avertissement de whitespace lors de git am.

## Appliquer sans perdre les captures

Sur la branche chore/phase-4-release-codex :

```bat
git add readMe.md docs/images
git commit -m "docs: add screenshots of the modern Windows interface"
git am "C:\CHEMIN\PersonalManager_Correctif_Fermeture.patch"
.venv\Scripts\python.exe tests/run_tests.py
```

Si les captures sont déjà committées, la première tentative de commit peut
simplement indiquer qu’il n’y a rien à committer. Ne pas réappliquer le patch
complet de la phase 4. Vérifier les 100 tests et l’absence des anciens bgerror.

Reconstruire puis contrôler la nouvelle distribution :

```bat
.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm PersonalManager.spec
start /wait "" "dist\PersonalManager\PersonalManager.exe" --self-test-result "%TEMP%\personalmanager-build-check.json"
type "%TEMP%\personalmanager-build-check.json"
```

Le JSON doit contenir ok: true. Ensuite, ouvrir le .exe normalement et vérifier
la connexion, les formulaires, les graphiques et les exports. Le contrôle sans
fenêtre valide les dépendances embarquées, pas le rendu graphique.

Après validation, suivre PHASE_4.md pour retirer la base et les caches du suivi
Git sans effacer les fichiers locaux, puis pousser la branche. Distribuer le
dossier PersonalManager entier, jamais le .exe isolé de ses ressources.
