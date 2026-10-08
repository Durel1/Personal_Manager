# Phase 2B — Formulaires intégrés et opérations de gestion

Cette étape ajoute les formulaires aux quatre modules de l’interface moderne.
Elle dépend de la phase 2A, qui doit être présente sur la branche de départ.

## Fonctionnement

Depuis une liste :

- **Ajouter** ouvre un formulaire dans le panneau principal.
- Sélectionner une ligne active **Modifier** et **Supprimer**.
- Un double clic ouvre aussi la modification de la ligne.
- **Enregistrer** valide les champs puis revient à la liste avec un message.
- **Annuler / Retour** revient à la liste sans soumettre les champs.
- **Supprimer** demande une confirmation avant la suppression.

Ces opérations concernent les employés, clients, rendez-vous et transactions.
La liste, le formulaire et le menu restent dans la même fenêtre.
Les graphiques matplotlib sont toujours l’étape suivante de la phase 2.

## Corrections métier

- SQLite attribue les identifiants des nouvelles lignes : plus d’identifiants
  aléatoires dans les opérations de l’interface moderne.
- Une modification utilise `UPDATE ... WHERE id=?` : elle conserve l’identifiant
  et le nombre de lignes, au lieu d’ajouter une autre facture.
- Un identifiant absent provoque un message plutôt qu’une nouvelle insertion.
- Les champs sont obligatoires, avec validation des e-mails et téléphones.
- Les dates saisies doivent être valides au format `AAAA-MM-JJ`.
- Les heures vont de `00:00` à `23:59`. Une saisie comme `9 : 5` devient `09:05`.
- Les montants restent des entiers positifs, selon le modèle existant.
  Les décimales ne sont pas introduites sans migration du modèle financier.
- Les valeurs sont transmises au SQL par paramètres, jamais concaténées.

Les anciennes dates sont conservées telles qu’elles existent. Une ancienne date
ambiguë comme `10/9/26` n’est pas convertie automatiquement : il faut saisir sa
date exacte en format ISO avant d’enregistrer la modification de cette ligne.
Les dates, heures et choix historiques incorrects restent donc visibles et
corrigeables ; aucune réécriture globale des données n’est faite.

## Architecture et pédagogie

`backend/management.py` définit les champs, valeurs initiales et règles de
validation. Ce module ne dépend pas de l’interface. Les noms de tables et de
colonnes proviennent du catalogue fixe, et chaque opération ferme sa connexion.
Les écrans envoient des données ; le service décide si elles peuvent être écrites.

Un formulaire générique évite quatre implémentations presque identiques.
Les champs `choice` affichent un menu, les autres affichent une entrée.
La page capture les valeurs sur le fil Tkinter, puis les services SQLite
s’exécutent dans le fil de travail déjà introduit en phase 2A.

« Enregistrer » est une demande d’écriture. Une navigation effectuée ensuite
ne retire pas une écriture déjà soumise. La gestion d’annulation d’une opération
en cours n’est pas implémentée. Les permissions par rôle sont prévues en phase 3.

La correction des factures concerne **la nouvelle interface**.
Les anciens modules Tkinter sont conservés pendant la transition et restent
accessibles avec `main.py` ; ils ne bénéficient pas de ces nouveaux formulaires.

## Appliquer et vérifier sous Windows

Depuis un état Git propre, créer la branche depuis **la phase 2A** :

```bat
git switch -c refactor/phase-2-management-codex refactor/phase-2-interface-codex
git am "C:\CHEMIN\PersonalManager_Phase2B.patch"
.venv\Scripts\python.exe tests/run_tests.py
```

La suite contient **48 tests** et doit réussir sans test ignoré.
Les dépendances restent celles de la phase 2A.

Fermer l’application et préparer une nouvelle copie avant les tests manuels :

```bat
copy projet_stage.db "%TEMP%\personal-manager-phase2b.db"
set "PERSONAL_MANAGER_DB=%TEMP%\personal-manager-phase2b.db"
.venv\Scripts\python.exe main_modern.py
```

Dans chaque module, ajouter une ligne, modifier cette ligne, puis la supprimer.
Pour une facture, vérifier que la modification garde le même ID et n’augmente
pas le nombre de transactions. Tester aussi `abc` comme montant, `24:00` comme
heure, une date inexistante et un champ vide : un message doit apparaître et
aucune écriture ne doit être faite. Annuler une suppression ne doit rien changer.

Après fermeture de l’application :

```bat
set "PERSONAL_MANAGER_DB="
git push -u origin refactor/phase-2-management-codex
```

## Vérification dans l’environnement de préparation

- 48 tests découverts : **32 réussis, 16 ignorés** faute de bcrypt/CustomTkinter.
- Les dix nouveaux tests métier passent sur SQLite réel et des bases temporaires.
- Vérification du cycle ajout/modification/suppression dans chaque module.
- Régression facture : deux factures, modification d’une seule, pas de doublon.
- Validation des montants, dates, heures, identifiants et champs.
- Ajout de 120 employés sans collision d’identifiant.
- Deux nouveaux tests de widgets Windows : création/modification d’une facture
  via le formulaire et refus d’un montant invalide sans écriture.
- Syntaxe Python vérifiée ; rendu et nouveaux parcours graphiques en attente
  de validation sous Windows.

## Pour expliquer le travail en entretien

« J’ai centralisé la validation et les opérations de gestion dans des services
indépendants de l’interface. Les formulaires utilisent ces services, ce qui permet
de tester les règles métier sur SQLite sans ouvrir une fenêtre. J’ai corrigé la
modification des factures avec un UPDATE ciblé et confié les identifiants à SQLite.
J’ai aussi testé les données invalides et les enregistrements qui n’existent plus. »
