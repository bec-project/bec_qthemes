"""Tests for the Theme object and the material_icon public API."""

import pytest
from qtpy.QtGui import QColor, QIcon, QPixmap

from bec_qthemes import material_icon
from bec_qthemes._theme import Theme


def test_theme_color_lookup_and_fallback():
    theme = Theme("dark", {"PRIMARY": "#3b82f6"})

    assert theme.color("PRIMARY") == QColor("#3b82f6")
    assert theme["PRIMARY"] == QColor("#3b82f6")
    # Unknown keys fall back instead of raising.
    assert theme.color("UNKNOWN", fallback="#abcdef") == QColor("#abcdef")
    assert theme["UNKNOWN"] == QColor("#000000")


def test_theme_change_theme_emits_signal(qtbot):
    theme = Theme("dark", {"PRIMARY": "#000000"})

    with qtbot.waitSignal(theme.theme_changed, timeout=1000) as blocker:
        theme.change_theme("light", {"PRIMARY": "#ffffff"})

    assert blocker.args == ["light"]
    assert theme.theme == "light"
    assert theme["PRIMARY"] == QColor("#ffffff")


def test_theme_accent_colors_from_mapping():
    theme = Theme("dark", {"ACCENT_SUCCESS": "#00ff00", "ACCENT_EMERGENCY": "#ff0000"})

    assert theme.accent_colors.success == QColor("#00ff00")
    assert theme.accent_colors.emergency == QColor("#ff0000")


def test_material_icon_returns_pixmap_and_icon(qapp):
    pixmap = material_icon("home", size=(24, 24))
    assert isinstance(pixmap, QPixmap)
    assert not pixmap.isNull()

    icon = material_icon("home", convert_to_pixmap=False)
    assert isinstance(icon, QIcon)
    assert not icon.isNull()


def test_material_icon_unknown_name_raises(qapp):
    with pytest.raises(KeyError):
        material_icon("this-icon-does-not-exist")
