> Archive documentaire de la première interface. Les anciens fichiers et captures sont disponibles dans l’historique Git. Ses instructions ne décrivent pas la version actuelle ; consultez [README.md](../../README.md).

# PersonalManager — version moderne (phase 3)

Application de gestion locale en Python, SQLite et CustomTkinter : employés,
clients, rendez-vous, finances, graphiques, recherche, exports Excel/PDF,
permissions administrateur/employé et alertes.

Lancement sous Windows, avec un environnement virtuel déjà créé :

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Pour installer aussi les dépendances de test et lancer les vérifications :

```bat
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe tests/run_tests.py
```

Le guide [Phase 3](docs/PHASE_3.md) explique les rôles, les migrations et les
vérifications à faire sur une copie de la base. Les guides précédents se trouvent
dans `docs/`. La création d’un exécutable et le README final avec captures restent
prévus pour la phase 4.

## Documentation historique

Le contenu ci-dessous décrit l’application originale et ne constitue plus le
mode d’installation de la version moderne.

\# PersonalManager



\*\*PersonalManager\*\* est une mini-application de gestion destinée aux petites entreprises. \[cite\_start]Elle permet de sécuriser et de faciliter les opérations quotidiennes comme la gestion du personnel, des clients, des rendez-vous et des finances\[cite: 109, 110].



\## 📋 Fonctionnalités



L'application offre quatre modules principaux :



\* \[cite\_start]\*\*👥 Gestion des employés :\*\* Enregistrer de nouveaux employés, les supprimer et consulter la liste du personnel\[cite: 112, 113, 114, 115].

\* \[cite\_start]\*\*📅 Gestion des Évènements (Rendez-vous) :\*\* Enregistrer, supprimer et consulter la liste des rendez-vous de l'entreprise\[cite: 116, 117, 118, 119].

\* \[cite\_start]\*\*🤝 Gestion des clients :\*\* Enregistrer, supprimer et consulter la liste des clients\[cite: 120, 121, 122, 123].

\* \[cite\_start]\*\*💰 Gestion des finances :\*\* Enregistrer les factures de transactions et consulter l'état financier\[cite: 124, 125, 126].



\## 🛠 Technologies utilisées



\* \[cite\_start]\*\*Langage :\*\* Python 3.11.0 \[cite: 127]

\* \[cite\_start]\*\*Base de données :\*\* Sqlite3 \[cite: 127]

\* \[cite\_start]\*\*Interface Graphique :\*\* Tkinter \[cite: 128]



\## ⚙️ Installation et Prérequis



\### 1. Prérequis

\[cite\_start]Il est recommandé d'utiliser l'IDE \*\*Visual Studio Code\*\* avec les extensions suivantes : Pylance, Python, Python Debugger et Code Runner\[cite: 136, 137].



\### 2. Installation des dépendances

\[cite\_start]Assurez-vous d'avoir Python installé\[cite: 132]. \[cite\_start]Ouvrez votre invite de commande et exécutez les commandes suivantes pour installer les modules nécessaires\[cite: 133]:



bash

pip install tkinter

pip install sqlite3



\## 🚀 Utilisation

Ouvrez le dossier du projet dans Visual Studio Code.



Exécutez le fichier main.py (via l'extension Code Runner par exemple).



Au premier lancement, la base de données se créera automatiquement.



Une interface de connexion apparaîtra. Vous pourrez vous connecter ou créer un compte pour accéder aux fonctionnalités.
