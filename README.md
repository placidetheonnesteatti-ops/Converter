# Docu2TeX

Docu2TeX est une application de bureau **hors ligne** destinée à reconstruire des documents Word (`.docx`) et PDF (`.pdf`) en projets LaTeX éditables.

## Ce que fait la version 1.2.0

- DOCX → LaTeX avec texte, styles de base, titres, listes, tableaux, sauts de page et images.
- PDF → LaTeX par reconstruction des blocs de texte et extraction des images.
- Nettoyage/échappement des caractères spéciaux LaTeX.
- Conservation approximative des dimensions d'images DOCX.
- Prise en compte du format, de l'orientation et des marges de la première section Word.
- Tableaux courts en `tabularx`, tableaux longs en `longtable`.
- En-tête et pied de page simples.
- Compilation locale avec XeLaTeX, LuaLaTeX ou PDFLaTeX.
- Mesure du nombre de pages et tentative limitée d'ajustement de pagination.
- Aucun document envoyé vers une API ou un serveur.
- Génération d'un projet avec `main.tex`, `images/` et les fichiers de compilation.

## Limites connues

La reproduction **pixel-perfect** de Word/PDF n'est pas garantie. Les moteurs Word, PDF et TeX ont des règles de composition différentes. Les PDF scannés, objets Office, équations complexes, tableaux avec cellules fusionnées, mises en page absolues et documents comportant plusieurs sections très différentes peuvent nécessiter une retouche.

La V1.2 privilégie un LaTeX **compilable, éditable et propre** plutôt qu'une capture visuelle figée.

## Installation pour le développement

Python 3.13 est utilisé par la CI.

```text
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-dev.txt
python main.py
```

Pour produire automatiquement le PDF, installer MiKTeX ou TeX Live et rendre `xelatex` accessible dans le PATH.

## Tests

```text
pytest -q
```

## Construire l'EXE localement sous Windows

```text
build_windows.bat
```

Le résultat attendu est :

```text
dist\\Docu2TeX.exe
```

## Construire avec GitHub Actions

1. Créer un dépôt GitHub.
2. Pousser tout le contenu du projet.
3. Aller dans **Actions → Build Windows EXE → Run workflow**, ou pousser un tag `v1.2.0`.
4. Récupérer `Docu2TeX-Windows.zip` dans les artifacts ou la Release.

La CI lance d'abord les tests, puis construit l'EXE Windows. L'EXE **ne contient pas MiKTeX/TeX Live** : une distribution LaTeX reste nécessaire sur la machine pour compiler les PDF.

## Structure

```text
Docu2TeX/
├── app/                  # interface PySide6
├── core/                 # moteurs de conversion
├── tests/                # tests automatisés
├── docs/                 # documentation
├── .github/workflows/    # CI Windows + tests
├── build_windows.spec    # configuration PyInstaller
├── build_windows.bat     # build local Windows
├── run_windows.bat       # lancement local
├── main.py
└── requirements*.txt
```

## Confidentialité

Les documents sont traités localement. Docu2TeX ne fournit aucune API cloud et n'envoie pas les fichiers convertis à un service distant.

## GitHub

Le dépôt peut être envoyé soit avec le contenu de ce dossier à la racine du dépôt, soit avec le dossier `Docu2TeX/` conservé comme sous-dossier. Le workflow GitHub détecte automatiquement ces deux organisations.

Le workflow installe explicitement les dépendances de test et d'empaquetage, exécute les tests, puis construit `Docu2TeX.exe` avec PyInstaller.
