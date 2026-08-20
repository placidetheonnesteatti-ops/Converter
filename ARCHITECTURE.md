# Architecture technique

## Chaîne de conversion

1. `core.service.convert_file()` choisit le moteur selon l'extension.
2. `docx_converter.py` lit la structure OOXML de Word, récupère les médias, les paragraphes, les listes, les tableaux et les paramètres de la première section.
3. `pdf_converter.py` lit les blocs de texte et les images d'un PDF avec PyMuPDF et reconstruit les pages séquentiellement.
4. `tex_writer.py` construit un document LaTeX autonome.
5. `compiler.py` cherche un moteur local et compile jusqu'à deux passes.
6. `service.py` mesure les pages et peut modifier légèrement `parskip` pour tenter de rapprocher la pagination.

## Packaging Windows

PyInstaller construit un **EXE unique**. Le workflow GitHub exécute les tests sur Linux avant de construire l'EXE sur `windows-latest`. Le fichier final attendu est `dist/Docu2TeX.exe`.

## Principes

Le programme privilégie un LaTeX compilable et éditable. La reproduction pixel-perfect n'est pas garantie et les cas complexes sont signalés plutôt que masqués.
