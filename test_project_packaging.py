from pathlib import Path


def test_windows_packaging_configuration_is_consistent():
    root = Path(__file__).resolve().parents[1]
    spec = (root / "build_windows.spec").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "windows-build.yml").read_text(encoding="utf-8")
    batch = (root / "build_windows.bat").read_text(encoding="utf-8")

    assert 'name="Docu2TeX"' in spec
    assert "dist/Docu2TeX.exe" in workflow
    assert "dist\\Docu2TeX.exe" in batch
    assert "pytest -q" in workflow
