# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all("PySide6")
fitz_datas, fitz_binaries, fitz_hiddenimports = collect_all("fitz")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=pyside6_binaries + fitz_binaries,
    datas=pyside6_datas + fitz_datas,
    hiddenimports=pyside6_hiddenimports + fitz_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Docu2TeX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
