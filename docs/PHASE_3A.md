# Phase 3A — Recherche dynamique et filtres

Cette étape part de la phase 2C validée. Les exports, rôles et alertes restent
pour les prochaines étapes de la phase 3.

## Comportement

La recherche porte sur le nom, l’e-mail et le téléphone des employés ; ces
champs plus la ville, le secteur et le quartier des clients ; le contact, le
téléphone, le lieu et le motif des rendez-vous ; le motif des finances.

Les rendez-vous se filtrent par statut effectué/non effectué, les finances
par statut payé/non payé. Recherche et statut se combinent. Le bouton Effacer
rétablit la liste complète. Chaque nouveau critère revient à la première page.
Les critères sont conservés pendant la navigation et après un formulaire,
puis effacés à la déconnexion. Un ajout peut rester invisible s’il ne correspond
pas aux critères : utiliser Effacer pour retrouver toutes les lignes.

La casse Unicode est ignorée : ÉLODIE et élodie correspondent. Les accents
restent significatifs : Elodie et Élodie peuvent différer. Les caractères %, _
et les apostrophes sont recherchés littéralement. La limite est de 200 caractères.

## Pourquoi cette implémentation ?

1. Le backend applique les critères en SQL avant la pagination. Filtrer seulement
   les 25 lignes affichées masquerait les correspondances des autres pages.
2. Les valeurs utilisent des paramètres SQL. Les noms de tables et colonnes
   proviennent exclusivement du catalogue interne, jamais du texte saisi.
3. Les caractères spéciaux de LIKE sont échappés : % saisi ne signifie pas
   « tous les caractères ». CASEFOLD étend la comparaison à la casse Unicode.
4. Le compteur et les lignes utilisent les mêmes critères dans une transaction
   de lecture, pour conserver une pagination cohérente.
5. L’interface observe une StringVar : saisie, collage et effacement déclenchent
   la recherche après 250 ms sans modification. C’est un debounce.
6. Les requêtes s’exécutent dans le fil de travail existant. Un numéro de requête
   invalide immédiatement les anciens résultats ; ils ne peuvent pas remplacer
   une recherche plus récente. Les actions sur les anciennes lignes sont
   désactivées pendant la recherche. La navigation annule le délai en attente.

Pour l’entretien : « J’ai filtré les données avant la pagination et conservé
des requêtes paramétrées. J’ai ajouté un debounce pour limiter les requêtes,
et rejeté les résultats obsolètes pour que l’interface corresponde toujours
aux derniers critères saisis. »

## Appliquer et vérifier sous Windows

Dans un répertoire Git sans modifications en attente, partir de la phase 2C :

```bat
git switch -c feat/phase-3-search-codex refactor/phase-2-charts-codex
git am "C:\CHEMIN\PersonalManager_Phase3A.patch"
.venv\Scripts\python.exe tests/run_tests.py
```

Aucune dépendance supplémentaire. Les **64 tests** doivent réussir sans test
ignoré sur Windows. Tester ensuite sur une copie dédiée, application fermée :

```bat
copy projet_stage.db "%TEMP%\personal-manager-phase3a.db"
set "PERSONAL_MANAGER_DB=%TEMP%\personal-manager-phase3a.db"
.venv\Scripts\python.exe main.py
```

- Rechercher un nom, un téléphone et une ville dans les modules concernés.
- Saisir rapidement puis effacer/coller du texte : seuls les critères actuels
  doivent déterminer les résultats.
- Combiner un motif avec Payée ou Non Payée, puis cliquer sur Effacer.
- Vérifier une recherche vide, sans résultat, et la pagination avec plus de
  25 correspondances si les données le permettent.
- Ouvrir puis quitter un formulaire : les critères doivent être conservés.
- Naviguer pendant une recherche, puis se déconnecter et se reconnecter.

Après fermeture et validation :

```bat
set "PERSONAL_MANAGER_DB="
git push -u origin feat/phase-3-search-codex
```

## Vérifications effectuées

La suite locale comporte 64 tests : **45 réussis, 19 ignorés**, car bcrypt et
CustomTkinter ne sont pas disponibles dans l’environnement de préparation.
Les cinq nouveaux tests backend couvrent Unicode, caractères littéraux,
critères combinés, pagination filtrée et critères invalides. Deux nouveaux
tests de widgets préparent la vérification Windows : recherche avec navigation,
et filtre de statut. La syntaxe Python et les espaces du diff sont vérifiés.
La validation des widgets et de l’affichage reste à effectuer sur Windows.
