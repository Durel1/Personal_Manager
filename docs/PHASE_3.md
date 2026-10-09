# Phase 3 — Recherche, exports, permissions et alertes

Cette livraison regroupe toute la phase 3, recherche de la phase 3A incluse.
Elle part de la phase 2C. La phase 4 (exécutable Windows et README final avec
captures) reste à réaliser après validation sur le PC de l’utilisateur.

## Fonctionnalités livrées

| Fonction | Comportement |
| --- | --- |
| Recherche | Recherche Unicode, délai de 250 ms, critères conservés par module, pagination filtrée |
| Statuts | Rendez-vous effectués/non effectués ; transactions payées/non payées |
| Excel/PDF | Tous les résultats filtrés, sur toutes les pages, maximum 10 000 lignes |
| Permissions | Administrateur et employé, avec contrôle des services backend |
| Gestion des rôles | Page Permissions réservée aux administrateurs ; dernier administrateur protégé |
| Alertes | Rendez-vous du jour et transactions non payées dont l’échéance est dépassée |

Les exports sont disponibles dans les quatre modules. Un export vide est valide
et indique l’absence de résultats. Un export trop grand demande d’affiner la
recherche : aucune ligne n’est omise silencieusement.

## Rôles et migration

| Action | Administrateur | Employé |
| --- | --- | --- |
| Consulter/exporter clients et rendez-vous | Oui | Oui |
| Consulter/exporter employés et finances | Oui | Non |
| Créer/modifier/supprimer les données métier | Oui | Non |
| Attribuer les rôles | Oui | Non |
| Consulter son propre profil | Oui | Oui |

La base passe de la version 2 à la version 3 dans une transaction. Les comptes
existants deviennent administrateurs pour conserver leurs anciens droits. Aucun
mot de passe n’est modifié par cette migration et les données sont conservées.
Les nouvelles inscriptions deviennent employés. Sur une base vide, le tout
premier compte devient administrateur, pour permettre l’initialisation.

L’inscription utilise une transaction BEGIN IMMEDIATE : deux inscriptions
simultanées ne peuvent pas toutes deux se considérer comme le premier compte.
La modification de rôle utilise aussi une transaction d’écriture et refuse de
retirer les droits du dernier administrateur.

L’interface masque les modules interdits et désactive les boutons de modification
pour les employés. Mais cela ne suffit pas : les services relisent le rôle du
compte en base dans la transaction qui consulte ou modifie les données. Modifier
une valeur de rôle dans l’interface ne donne donc aucun droit. Une rétrogradation
est prise en compte lors de la prochaine opération backend ; la navigation visible
est entièrement renouvelée à la reconnexion. Un administrateur qui modifie son
propre rôle voit immédiatement son interface reconstruite.

Les versions 0 à 2 conservent le fonctionnement des anciens outils/tests de
fondation. L’application moderne migre obligatoirement en version 3 avant la
connexion ; à partir de cette version, les services métier nécessitent l’identité
du compte connecté. L’entrée main_legacy.py refuse une base en version 3 : elle
ne doit pas contourner les nouvelles permissions avec l’ancienne interface.

Les permissions contrôlent l’usage de l’application. Elles ne chiffrent pas le
fichier SQLite et ne protègent pas contre une personne qui peut modifier ce
fichier ou le code Python directement. Les données métier restent partagées
entre les comptes autorisés ; ce n’est pas une séparation par entreprise.

## Échéances et alertes

Le formulaire financier possède une échéance facultative au format AAAA-MM-JJ.
Elle ne doit pas précéder la date de la transaction. La date de transaction et
l’échéance sont deux notions distinctes : on ne devine jamais une échéance à
partir des anciennes données. Une échéance vide est enregistrée comme NULL.

- Un rendez-vous daté du jour reçoit une ligne ambrée et le texte Aujourd’hui,
  quel que soit son statut. L’heure reste disponible dans la liste.
- Une transaction Non Payée avec une échéance strictement antérieure au jour
  actuel reçoit une ligne rouge et le texte En retard. Cela concerne les deux
  types de transaction, Encaissement et Décaissement.
- Une échéance aujourd’hui n’est pas encore en retard. Une transaction Payée
  ne génère aucune alerte, même avec une ancienne échéance.
- Les anciennes dates ambiguës et les échéances invalides ne sont pas devinées.
  Le tableau de bord indique les données non interprétables et les factures
  non payées sans échéance.
- Les compteurs et le graphique financier ne sont pas exposés aux employés.

Les alertes se mettent à jour au chargement d’une page et avec Actualiser.
L’application utilise la date locale du PC. Si elle reste ouverte pendant un
changement de jour, actualiser les pages. Il n’y a pas de notification système,
d’e-mail ou de tâche planifiée en arrière-plan.

## Qualité des exports

Le backend réutilise exactement les critères de recherche et de statut de la
liste, puis lit tous les résultats dans une transaction, sans pagination.
Un contrôle de permission précède cette lecture. Les exports ne contiennent
jamais les comptes utilisateurs ni les mots de passe.

Excel conserve les téléphones et identifiants comme texte. Les montants entiers
de plus de 15 chiffres restent aussi du texte, pour éviter une perte de précision
dans Excel. Les textes commençant par = sont explicitement stockés comme texte,
jamais comme formules. Le classeur comporte un titre, les critères, des en-têtes,
des filtres et un volet figé. Il n’invente pas une devise absente du modèle.

Le PDF utilise une police Vera fournie avec ReportLab, avec les accents français
vérifiés. Les listes simples utilisent un tableau ; les modules avec beaucoup
de colonnes ou du texte long utilisent des fiches avec champs disposés par paires.
Les fiches restent ensemble lorsqu’elles tiennent sur une page ; les très longues
fiches se poursuivent avec leur identifiant répété. Le titre court d’une fiche
peut être abrégé, mais son champ détaillé est conservé intégralement. Le texte
saisi est échappé avant le rendu : <b> reste du texte et n’est pas interprété.
Chaque page possède un numéro.

Le fichier est construit dans un fichier temporaire à côté de la destination,
puis remplacé uniquement après une écriture réussie. Un export qui échoue ne
détruit donc pas un rapport précédent. La boîte de dialogue demande confirmation
pour remplacer un fichier existant ; Annuler n’écrit aucun fichier. Les fichiers
ouverts/verrouillés et dossiers inaccessibles produisent un message d’erreur.

## Architecture et explication pour un entretien

| Fichier | Responsabilité |
| --- | --- |
| backend/permissions.py | Identifier le compte, contrôler les droits, attribuer les rôles |
| backend/migrations.py | Ajouter le rôle et l’échéance, préserver les comptes existants |
| backend/dashboard.py | Critères SQL communs à la pagination et aux exports |
| backend/management.py | Validation des formulaires et écritures autorisées |
| backend/statistics.py | Indicateurs limités aux données autorisées |
| backend/alerts.py | Déterminer les alertes à partir de dates explicites |
| backend/reporting.py | Construire les fichiers Excel/PDF, assurer une écriture atomique |
| ui/application.py | Navigation selon les rôles, boutons, filtres et présentation des alertes |

« J’ai ajouté des fonctions orientées utilisateur sans coupler les calculs à
l’interface. Les permissions sont vérifiées en base et pas seulement par des
boutons masqués. Les exports reprennent tous les résultats filtrés, préservent
la précision des données et protègent les rapports existants en cas d’échec.
Pour les alertes, j’ai distingué la date de transaction de l’échéance plutôt
que d’attribuer arbitrairement un retard aux anciennes factures. »

Pour le debounce, les paramètres SQL et les réponses obsolètes, lire également
PHASE_3A.md. Les dates invalides historiques se corrigent volontairement dans
les formulaires : la migration ne les transforme pas silencieusement.

## Appliquer la livraison complète sous Windows

Fermer l’application. Depuis un répertoire Git sans modifications en attente :

```bat
git switch -c feat/phase-3-complete-codex refactor/phase-2-charts-codex
git am "C:\CHEMIN\PersonalManager_Phase3.patch"
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe tests/run_tests.py
```

Le patch complet contient huit commits : les trois de la recherche, puis cinq
pour les permissions, les exports, les alertes, l’interface et la documentation.
Ne pas l’appliquer sur la branche phase 3A : la nouvelle branche part explicitement
de la phase 2C. Une branche phase 3A déjà existante est conservée intacte.

requirements-dev.txt installe les dépendances de l’application et pypdf,
utilisé pour vérifier réellement le contenu des PDF. En usage normal, seul
requirements.txt est nécessaire. La CI Windows utilise requirements-dev.txt.
Les **90 tests** doivent réussir sans échec et sans test ignoré sur Windows.

Tester sur une copie dédiée de la base, application fermée :

```bat
copy projet_stage.db "%TEMP%\personal-manager-phase3.db"
set "PERSONAL_MANAGER_DB=%TEMP%\personal-manager-phase3.db"
.venv\Scripts\python.exe main.py
```

## Validation manuelle rapide

1. Se connecter avec un compte existant. Son rôle affiché doit être Administrateur.
2. Rechercher un contact, changer un statut et utiliser Effacer. Exporter un
   résultat en Excel puis PDF. Vérifier les filtres, les accents et les téléphones.
3. Si possible, exporter une recherche avec plus de 25 résultats : les fichiers
   doivent contenir toutes les correspondances, pas seulement la page affichée.
4. Créer un compte de test après déconnexion. Il doit devenir Employé : clients
   et rendez-vous seulement, avec consultation et exports, sans modification.
5. Revenir comme administrateur et ouvrir Permissions. Promouvoir ce compte,
   puis vérifier son interface après reconnexion. Tester le refus de rétrograder
   le dernier administrateur. Conserver son compte principal administrateur.
6. Ajouter un rendez-vous pour aujourd’hui et vérifier l’alerte dans sa liste.
7. Ajouter une transaction non payée avec une date passée et une échéance hier.
   Vérifier la ligne rouge et le compteur, puis la passer en Payée : l’alerte
   doit disparaître. Vérifier aussi une facture sans échéance et une échéance
   aujourd’hui, qui ne doivent pas être indiquées en retard.
8. Tester clair/sombre, navigation pendant une recherche, annulation d’un export
   et export vers un fichier Excel encore ouvert.

Après fermeture et validation :

```bat
set "PERSONAL_MANAGER_DB="
git push -u origin feat/phase-3-complete-codex
```

La copie de test est seule migrée pendant cet essai. En lançant ensuite main.py
sans PERSONAL_MANAGER_DB, la migration s’appliquera aussi à la base habituelle.

## Vérifications effectuées dans l’environnement de préparation

Suite finale : **90 tests, 66 réussis et 24 ignorés**. Les tests cryptographiques
et les widgets sont ignorés ici faute de bcrypt/CustomTkinter. Leur validation
reste nécessaire sur Windows ; il ne s’agit pas d’une validation complète.

Les tests exécutés couvrent les droits du backend, les migrations, les alertes,
les fichiers Excel relus, les PDF relus avec pypdf, la pagination et l’écriture
atomique. Des PDF vides/remplis et à champs longs ont été rendus en PNG et
inspectés : la présentation a été corrigée pour éviter les débordements des
tableaux larges. Ces données d’inspection sont des exemples temporaires et ne
sont jamais ajoutées à la base de l’utilisateur. La syntaxe Python et le diff
sont vérifiés, ainsi que l’application du patch sur la phase 2C.

Documentation technique consultée :
- https://docs.reportlab.com/reportlab/userguide/ch7_tables/
- https://docs.reportlab.com/reportlab/userguide/ch3_fonts/
- https://openpyxl.readthedocs.io/en/stable/tutorial.html
