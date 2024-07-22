"""Tests for the main program with Qt."""

import platform
import re
from unittest import mock

import pytest
from qtpy.QtGui import QGuiApplication, QPalette

import bec_qthemes


@pytest.mark.parametrize(
    ("theme", "custom_colors"),
    [
        # Test theme
        ("dark", None),
        ("light", None),
        # Test theme and custom_colors
        ("dark", {}),
        ("dark", {"foreground": "#112233"}),
        ("dark", {"foreground>icon": "#112233"}),
        # Test color code
        ("dark", {"foreground": "#112"}),
        ("dark", {"foreground": "#11223344"}),
        ("dark", {"foreground": "#1122"}),
        # Test automatic theme
        ("auto", None),
        ("auto", {"foreground": "#112233"}),
        ("auto", {"[dark]": {"foreground": "#112233"}}),
        ("auto", {"foreground": "#112233", "[dark]": {"foreground": "#112233"}}),
        ("auto", {"foreground": "#112233", "[light]": {"foreground": "#112233"}}),
        ("auto", {"[dark]": {"foreground": "#112233"}, "[light]": {"foreground": "#112233"}}),
    ],
)
def test_load_palette(theme, custom_colors) -> None:
    """Verify that the function `load_stylesheet()` runs successfully when using various arguments."""
    bec_qthemes.load_palette(theme, custom_colors)


def test_apply_stylesheet_to_qt_app(qapp: QGuiApplication) -> None:
    """Verify that the function `load_stylesheet()` runs without error."""
    qapp.setStyleSheet(bec_qthemes.load_stylesheet())  # type: ignore


def test_apply_palette_to_qt_app(qapp: QGuiApplication) -> None:
    """Verify that the function `load_palette()` runs without error."""
    qapp.setPalette(bec_qthemes.load_palette())


@pytest.mark.parametrize(
    ("theme", "additional_qss"), [("dark", None), ("light", None), ("dark", "QWidget{color: red;}")]
)
def test_setup_theme(qapp, theme, additional_qss) -> None:
    """Verify that the function `setup_theme()` runs without error."""
    bec_qthemes.setup_theme(theme, additional_qss=additional_qss)


def test_enable_high_dpi(qapp) -> None:
    """Verify that the function `enable_high_dpi()` runs without error."""
    bec_qthemes.enable_hi_dpi()


def test_stop_sync(qapp) -> None:
    """Verify that the function `stop_sync()` runs without error."""
    bec_qthemes.setup_theme("auto")
    bec_qthemes.stop_sync()


def test_setup_theme_without_qapp() -> None:
    """Verify we raise Exception when qapp is none."""
    with mock.patch("qtpy.QtCore.QCoreApplication.instance", return_value=None):
        with pytest.raises(
            Exception,
            match=re.escape("setup_theme() must be called after instantiation of QApplication."),
        ):
            bec_qthemes.setup_theme()


if platform.system() == "Darwin":

    def test_theme_event_filter(qapp: QGuiApplication) -> None:
        """Verify that the internal class `ThemeEventFilter` runs without error."""

        bec_qthemes.setup_theme("auto")
        with mock.patch("darkdetect.theme", return_value="light"):
            qapp.setPalette(QPalette())
        with mock.patch("darkdetect.theme", return_value="dark"):
            qapp.setPalette(QPalette())
        with mock.patch("bec_qthemes._os_appearance.accent", return_value="red"):
            qapp.setPalette(QPalette())
