from pathlib import Path

from bec_qthemes import clear_svg_cache
from bec_qthemes._util import get_cash_root_path, get_project_version_from_pyproject


def test_clear_svg_cache_disk_and_memory(tmp_path: Path, monkeypatch):
    # Arrange: point cache root into a temp dir by monkeypatching get_cash_root_path
    version = get_project_version_from_pyproject()

    def fake_cache_root(v: str) -> Path:
        assert v == version
        return tmp_path / ".cache" / "bec_qthemes" / f"v{v}"

    monkeypatch.setattr("bec_qthemes._cache.get_cash_root_path", fake_cache_root)

    # Create theme-specific cache dirs and files
    theme_name = "My Fancy Theme"
    sanitized = "my-fancy-theme"
    base = fake_cache_root(version) / sanitized
    svg_dir = base / "svg_cache"
    mi_dir = base / "material_icons_svg"
    svg_dir.mkdir(parents=True, exist_ok=True)
    mi_dir.mkdir(parents=True, exist_ok=True)
    (svg_dir / "a.svg").write_text("<svg/>")
    (mi_dir / "b.svg").write_text("<svg/>")

    # Also create another theme to ensure selective clear doesn't touch it
    other = fake_cache_root(version) / "other-theme"
    (other / "svg_cache").mkdir(parents=True, exist_ok=True)
    (other / "material_icons_svg").mkdir(parents=True, exist_ok=True)

    # Put something into the template filter memo and ensure it's cleared
    import importlib

    tf = importlib.import_module("bec_qthemes._template.filter")
    tf._PATH_MEMO["k"] = "v"

    # Act: clear only chosen theme
    clear_svg_cache(theme_name)

    # Assert: theme_name caches removed, other theme remains, and memo cleared
    assert not svg_dir.exists()
    assert not mi_dir.exists()
    assert (other / "svg_cache").exists()
    assert (other / "material_icons_svg").exists()
    assert tf._PATH_MEMO == {}

    # Act: clear all themes
    clear_svg_cache()

    # Assert: other theme caches also removed and version root cleaned up if empty
    assert not (other / "svg_cache").exists()
    assert not (other / "material_icons_svg").exists()


def test_clear_svg_cache_purge_theme(tmp_path: Path, monkeypatch):
    version = get_project_version_from_pyproject()

    def fake_cache_root(v: str) -> Path:
        assert v == version
        return tmp_path / ".cache" / "bec_qthemes" / f"v{v}"

    monkeypatch.setattr("bec_qthemes._cache.get_cash_root_path", fake_cache_root)

    # Create two themes
    t1 = fake_cache_root(version) / "theme-one"
    t2 = fake_cache_root(version) / "theme-two"
    (t1 / "svg_cache").mkdir(parents=True, exist_ok=True)
    (t1 / "material_icons_svg").mkdir(parents=True, exist_ok=True)
    (t2 / "svg_cache").mkdir(parents=True, exist_ok=True)

    # Purge only theme-one
    clear_svg_cache("Theme One", purge=True)

    # theme-one folder should be gone entirely; theme-two intact
    assert not t1.exists()
    assert (t2 / "svg_cache").exists()


def test_clear_svg_cache_purge_all(tmp_path: Path, monkeypatch):
    version = get_project_version_from_pyproject()

    def fake_cache_root(v: str) -> Path:
        assert v == version
        return tmp_path / ".cache" / "bec_qthemes" / f"v{v}"

    monkeypatch.setattr("bec_qthemes._cache.get_cash_root_path", fake_cache_root)

    root = fake_cache_root(version)
    (root / "a" / "svg_cache").mkdir(parents=True, exist_ok=True)
    (root / "b" / "material_icons_svg").mkdir(parents=True, exist_ok=True)

    # Purge all version cache
    clear_svg_cache(purge=True)

    # Entire version root should be removed
    assert not root.exists()


def test_clear_svg_cache_cleanup_empty_dirs(tmp_path: Path, monkeypatch):
    version = get_project_version_from_pyproject()

    def fake_cache_root(v: str) -> Path:
        assert v == version
        return tmp_path / ".cache" / "bec_qthemes" / f"v{v}"

    monkeypatch.setattr("bec_qthemes._cache.get_cash_root_path", fake_cache_root)

    base = fake_cache_root(version) / "cleanup-theme"
    (base / "svg_cache").mkdir(parents=True, exist_ok=True)
    (base / "material_icons_svg").mkdir(parents=True, exist_ok=True)

    # Non-purge clear should remove subfolders and then the empty theme folder itself
    clear_svg_cache("cleanup-theme", purge=False)

    assert not base.exists()
    # If version root becomes empty, it should be cleaned too
    root = fake_cache_root(version)
    assert not root.exists()
