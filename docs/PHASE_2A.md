# Phase 2A — Fenêtre unique et navigation moderne

La phase 1 a été validée sur Windows. Cette étape prépare l’interface moderne
avant de migrer les formulaires de gestion et d’ajouter les graphiques.

## Disponible dans l’aperçu

- Connexion et inscription CustomTkinter utilisant l’authentification de phase 1.
- Une seule fenêtre avec menu latéral et page sélectionnée mise en évidence.
- Tableau de bord avec les nombres réels d’employés, clients, rendez-vous et transactions.
- Listes paginées (25 lignes) avec défilement vertical et horizontal.
- Profil sans mot de passe ni hachage.
- Modes clair et sombre, palette bleu nuit/cyan et police Segoe UI.
- Déconnexion et navigation remplaçant la page au lieu d’empiler des fenêtres.
- Requêtes et hachages exécutés dans un fil de travail pour garder l’interface réactive.

Cet aperçu permet de **consulter** les modules. Les formulaires d’ajout,
modification et suppression seront migrés dans l’étape suivante. Les graphiques
matplotlib restent à ajouter. `main.py` garde l’ancienne application complète ;
`main_modern.py` lance cet aperçu. La phase 2 entière n’est pas encore terminée.

## Architecture et explication pédagogique

`backend/dashboard.py` fournit des données sans connaître Tkinter. Les noms de
tables et colonnes proviennent d’un catalogue fixe. Les paramètres de pagination
sont validés et transmis séparément au SQL. Le profil est lu par identifiant et
ne sélectionne jamais la colonne `password`.

`ui/application.py` contient la fenêtre racine et les vues. `grid` distribue
l’espace entre le menu et le contenu ; la page précédente est détruite lors
d’une navigation. Un compteur de génération permet d’ignorer le résultat d’une
requête si l’utilisateur a déjà changé de page.

Un `ThreadPoolExecutor` réalise les opérations SQLite/bcrypt hors du fil graphique.
Le fil graphique vérifie la fin des opérations avec `after`, puis met à jour les
widgets. Le fil de travail ne touche jamais aux widgets. Chaque opération garde
sa propre connexion SQLite conformément à la phase 1.

Les contrôles utilisent CustomTkinter. Les tableaux utilisent un `ttk.Treeview`
avec une palette adaptée et des barres de défilement CustomTkinter : la bibliothèque
ne fournit pas de tableau natif équivalent. Cela conserve une sélection et un
défilement efficaces, sans fabriquer des centaines de widgets par ligne.

## Installer et lancer sous Windows (terminal cmd/Cmder)

Après application des patchs sur une nouvelle branche depuis la phase 1 :

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe tests/run_tests.py
```

La suite contient maintenant **36 tests**. Elle doit réussir sans test ignoré.
Les nouveaux tests de widgets créent une vraie fenêtre et la ferment : ils
vérifient la construction et la navigation, mais pas la qualité visuelle.

Fermer toute application utilisant la base, puis lancer sur une copie dédiée :

```bat
copy projet_stage.db "%TEMP%\personal-manager-phase2a.db"
set "PERSONAL_MANAGER_DB=%TEMP%\personal-manager-phase2a.db"
.venv\Scripts\python.exe main_modern.py
```

Se connecter, consulter chaque page, changer le thème, redimensionner la fenêtre,
tester l’inscription et la déconnexion. Vérifier la lisibilité et l’absence de
texte coupé. Les listes peuvent défiler horizontalement si leurs colonnes
dépassent la largeur disponible. Aucun chiffre fictif n’alimente le tableau de bord.

Après fermeture de l’application :

```bat
set "PERSONAL_MANAGER_DB="
git push -u origin refactor/phase-2-interface-codex
```

## Vérifications dans l’environnement de préparation

- Sources de phase 1 comparées à GitHub : identiques à la branche publiée,
  commit `663dbcc0a8a6691a56be68c6deeaaac43fafa21b`.
- Suite : **22 tests réussis et 14 ignorés**, car bcrypt et CustomTkinter manquent.
- Requêtes SQLite réelles : comptes, pagination de 60 lignes, paramètres invalides,
  liste vide et profil sans secret.
- Analyse syntaxique des nouveaux fichiers Python : réussie.
- Aucun rendu de la nouvelle interface n’a pu être vérifié ici.

La validation de l’aperçu exige donc le passage des **36 tests sous Windows**
et la revue visuelle. Les anciennes 29 vérifications sont conservées.

## Pour un entretien

« J’ai migré l’interface progressivement. J’ai commencé par une fenêtre unique,
un menu latéral et des vues de consultation, en gardant l’application complète
disponible. J’ai séparé les requêtes de la présentation et évité de bloquer
l’interface pendant le hachage ou les lectures de la base. J’ai ensuite prévu
la migration des formulaires et les graphiques. »

Documentation : https://customtkinter.tomschimansky.com/documentation/
