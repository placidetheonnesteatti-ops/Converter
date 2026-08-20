@echo off
setlocal
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1
pyinstaller --noconfirm --clean build_windows.spec
if errorlevel 1 exit /b 1
if not exist dist\Docu2TeX.exe (
  echo ERREUR : Docu2TeX.exe n'a pas ete genere.
  exit /b 1
)
echo.
echo Build termine : dist\Docu2TeX.exe
echo.
endlocal
