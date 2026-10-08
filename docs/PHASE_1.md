# Phase 1 — Fondations de PersonalManager

Cette phase prépare la base de données et l’authentification. La refonte visuelle
et les nouvelles fonctionnalités restent les phases suivantes.

## Ce qui a changé, et pourquoi

1. **Schéma SQL.** `password MOT NULL` devient `password TEXT NOT NULL`.
   Les téléphones deviennent des textes pour conserver les indicatifs et les
   zéros initiaux. SQLite accepte des types inconnus : une faute peut passer
   silencieusement. `NOT NULL` interdit NULL ; la validation métier interdit
   séparément les champs vides.
2. **Connexions courtes.** Chaque requête ouvre sa connexion, lit ou écrit,
   puis ferme la connexion. Le gestionnaire SQLite valide la transaction ou
   l’annule en cas d’erreur ; un `finally` ferme explicitement la connexion.
   Les erreurs remontent jusqu’à l’interface au lieu d’être masquées.
3. **Migration du schéma.** `CREATE TABLE IF NOT EXISTS` ne modifie pas les
   tables existantes. Une migration copie leurs lignes dans des tables corrigées,
   conserve les identifiants, puis remplace les anciennes tables dans une
   transaction. Une erreur annule cette opération. Les schémas personnalisés
   incompatibles sont refusés plutôt que simplifiés avec perte d’information.
4. **Authentification.** Les nouveaux mots de passe sont hachés avec bcrypt,
   avec un sel aléatoire et un coût de 12. La connexion vérifie le hachage avec
   `checkpw`. La logique est dans `backend/auth.py`, indépendante de Tkinter.
   L’inscription demande au moins 8 caractères et au plus 72 octets UTF-8,
   sans tronquer les mots de passe. Les anciens mots de passe valides restent
   utilisables, même s’ils sont plus courts que 8 caractères.
5. **Comptes existants.** Au premier lancement, une migration hache les anciens
   mots de passe en une transaction. `PRAGMA user_version` distingue la version
   initiale (0), le schéma corrigé (1), et les mots de passe hachés (2).
   Les relancements ne hachent pas une seconde fois les valeurs. Un doublon de
   nom utilisateur ou un mot de passe historique invalide bloque la migration
   avec un message, sans conversion partielle des mots de passe.
6. **Interface.** Le profil ne récupère plus le mot de passe ni son hachage.
   L’écran de récupération explique qu’une réinitialisation sécurisée reste à
   développer : connaître un nom utilisateur ne suffit plus à lire un secret.
   La connexion appelle directement `HomePage`, sans lancer un processus.
   L’inscription revient à l’écran de connexion après succès. Les identifiants
   des nouveaux utilisateurs sont attribués par SQLite.

## Organisation

- `backend/connection.py` : chemin de la base et durée de vie des connexions.
- `backend/create_database.py` : schéma et création des tables.
- `backend/migrations.py` : transformation versionnée des données existantes.
- `backend/requests_db.py` : fonctions SQL conservant les signatures de l’UI.
- `backend/auth.py` : validation, inscription et authentification.
- `tests/` : tests sur des bases temporaires et callbacks simulés.

Les requêtes continuent à transmettre les valeurs par paramètres `?`.
Le chemin par défaut est celui de `projet_stage.db` à la racine du projet,
indépendamment du dossier du terminal. `PERSONAL_MANAGER_DB` permet d’utiliser
une autre base, notamment pour tester.

## Installer et tester sous Windows

Depuis la racine du projet dans le terminal PowerShell de VS Code :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tests/run_tests.py
```

Si Python 3.11 n’est pas installé, utiliser `py -3 -m venv .venv` avec une
version de Python compatible. Aucune activation PowerShell n’est nécessaire.
Tkinter et SQLite font partie de l’installation standard de Python sous Windows.

`run_tests.py` doit terminer sans échec **et sans test ignoré**. La commande
`python -m unittest discover -s tests -v` permet une vérification partielle,
mais ignore explicitement les tests cryptographiques si bcrypt manque.
Elle ne constitue alors pas une validation complète de cette phase.

## Vérification graphique sur une copie

Fermer l’application et copier la base avant le premier lancement. Les tests
unitaires n’utilisent jamais les données du projet. Pour la vérification manuelle :

```powershell
Copy-Item .\projet_stage.db "$env:TEMP\personal-manager-phase1.db"
$env:PERSONAL_MANAGER_DB = "$env:TEMP\personal-manager-phase1.db"
.\.venv\Scripts\python.exe main.py
```

Vérifier : connexion d’un compte existant ; refus d’un mauvais mot de passe ;
inscription d’un nouveau compte ; refus d’un doublon ; profil sans mot de passe ;
écran de récupération sans secret ; fermeture et relancement avec les mêmes
comptes. Le second lancement ne doit pas modifier les hachages.

Puis fermer l’application et supprimer la variable de cette session :

```powershell
Remove-Item Env:PERSONAL_MANAGER_DB
```

La copie temporaire avant migration contient les anciennes données sensibles.
Elle reste locale. Aucun changement aux fichiers `.db` n’est inclus dans les
patchs de cette phase. Le `.gitignore` évite d’ajouter de nouvelles bases,
mais **ne retire pas celles déjà suivies par Git**. Les anciennes données et
les mots de passe présents dans l’historique ne sont pas effacés par le hachage.
Le retrait des bases suivies et le traitement d’éventuels secrets historiques
restent à décider explicitement, sans réécrire l’historique à cette étape.

## Vérifications effectuées dans l’environnement de préparation

- 29 tests découverts : **18 réussis, 11 ignorés car bcrypt absent**.
- SQLite réel : contraintes, opérations CRUD, paramètres, fermeture,
  annulation des transactions, migration et conservation des données.
- Callbacks Tkinter : **services simulés**, navigation, champs vides,
  mauvais identifiants, erreurs SQLite, retour après inscription.
- Compilation des fichiers Python : réussie.
- Installation de bcrypt : bloquée par l’accès réseau de l’environnement.
- Rendu graphique : non vérifié, aucun affichage disponible.
- Écriture GitHub : refusée avec HTTP 403 ; commits préparés localement.

La phase est implémentée, mais **sa validation complète reste en attente** du
passage de `tests/run_tests.py` et de la vérification graphique sous Windows.
Le workflow GitHub Actions lance les tests complets sur Windows après le push.

## Pour expliquer le travail en entretien

« J’ai commencé par les fondations : corriger les contraintes du schéma,
isoler les connexions et rendre les transactions fiables. J’ai prévu une
migration pour conserver les comptes existants, puis séparé l’authentification
de l’interface et remplacé les mots de passe en clair par des hachages bcrypt.
Les changements sont découpés en commits cohérents et vérifiés par des tests.
Je distingue les tests de logique des parcours graphiques. »

## Limites restant pour les phases suivantes

La modification des factures et les validations des rendez-vous ne sont pas
corrigées ici. Les identifiants aléatoires subsistent dans les autres modules.
Les permissions administrateur/employé et la réinitialisation sécurisée restent
à implémenter. L’ancien code peut encore afficher des erreurs insuffisamment
précises hors authentification. Aucun exécutable Windows n’a été généré.

Documentation bcrypt : https://github.com/pyca/bcrypt
