# Guide d'utilisation Windows

## 1. Prérequis

Docu2TeX fonctionne localement avec Python et ses dépendances. Pour obtenir automatiquement un PDF après conversion, installer MiKTeX ou TeX Live et vérifier que `xelatex` est accessible dans le PATH.

## 2. Depuis GitHub

Le workflow `Build Windows EXE` peut être lancé manuellement. Il peut aussi être déclenché en poussant un tag, par exemple `v1.1.0`. L'archive produite est `Docu2TeX-Windows.zip`.

## 3. Utilisation

Ouvrir Docu2TeX, déposer un `.docx` ou `.pdf`, choisir le dossier de sortie et lancer `CONVERTIR`.

Le dossier généré contient `main.tex`, les images extraites et le PDF compilé lorsque le moteur LaTeX est disponible.

## 4. Pagination

Pour un DOCX, Docu2TeX essaie de mesurer le nombre de pages en rendant d'abord le document via LibreOffice lorsque celui-ci est installé. Après compilation, un ajustement limité de l'espacement des paragraphes est tenté si les nombres de pages diffèrent.

La correspondance exacte avec Word ne peut pas être garantie pour tous les documents, car Word et TeX ne composent pas la page avec les mêmes règles. Les documents simples et structurés sont ceux qui donnent les meilleurs résultats.

## 5. Confidentialité

Les documents sont traités localement. Docu2TeX n'envoie aucun fichier vers un service distant.
