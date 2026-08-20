# Changelog

## 1.2.0

- Correction du packaging PyInstaller Windows : génération d'un EXE unique vérifié par la CI.
- Correction du workflow GitHub Actions : tests exécutés avant le build Windows.
- Correction du script `build_windows.bat` et des chemins de sortie.
- Prise en compte du format, de l'orientation et des marges de la première section DOCX.
- Respect de l'option de conservation des sauts de page.
- Nettoyage de code dans le compilateur.
- Suppression des artefacts de test du dépôt.

## 1.1.0

- Styles de base, listes, en-têtes/pieds de page, images dimensionnées et grands tableaux.
- Reconstruction PDF par blocs.
- Contrôle et tentative d'ajustement de pagination.
