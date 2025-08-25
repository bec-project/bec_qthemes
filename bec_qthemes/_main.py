from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Union

from qtpy.QtWidgets import QApplication, QWidget
from qtpy.QtGui import QColor

from bec_qthemes._theme import Theme
from bec_qthemes.qss_editor.qss_editor import (
    QSS_PATH,
    THEMES_PATH,
    build_palette_from_mapping,
    read_theme_xml,
    render_qss,
    DEFAULT_RADIUS,
    _augment_mapping_with_derived,
)


def apply_theme(
    theme: str | Path,
    additional_qss: str = "",
    target: QWidget | QApplication | None = None,
    qss_template_path: Path | None = None,
):
    """
    Apply a theme from an XML file and a QSS template to a Qt application or widget.

    Args:
        theme (str | Path): The name of the theme (e.g., "dark") or a path to the theme XML file.
        additional_qss (str, optional): Additional QSS to append to the rendered stylesheet. Defaults to "".
        target (QWidget | QApplication | None, optional): The target to apply the theme to.
                                                        If None, it applies to the QApplication instance.
                                                        Defaults to None.
        qss_template_path (Path | None, optional): Path to the QSS template file.
                                                   If None, the default 'theme_base.qss' is used.
                                                   Defaults to None.
    """
    app = QApplication.instance()
    if not app:
        raise RuntimeError("QApplication instance not found. Please create a QApplication first.")

    if not hasattr(app, "theme"):
        app.theme = None

    if target is None:
        target = app

    if qss_template_path is None:
        qss_template_path = QSS_PATH

    theme_path: Path
    if isinstance(theme, str):
        theme_path = THEMES_PATH / f"{theme}.xml"
        if not theme_path.exists():
            # Fallback for names with spaces like "Dark Blue"
            theme_path = THEMES_PATH / f"{theme.replace('_', ' ').title()}.xml"

        if not theme_path.exists():
            raise FileNotFoundError(
                f"Theme '{theme}' not found at '{theme_path}' or its variations."
            )
    else:
        theme_path = theme

    theme_name, mapping = read_theme_xml(theme_path)
    template = qss_template_path.read_text(encoding="utf-8")

    # Normalize and augment mapping (public API parity with ThemeWidget/apply_qss_with_xml)
    # Ensure radius defaults
    for k, v in DEFAULT_RADIUS.items():
        mapping.setdefault(k, v)
    # Normalize aliases (INPUT_BG ↔ FIELD_BG)
    if "INPUT_BG" in mapping and "FIELD_BG" not in mapping:
        mapping["FIELD_BG"] = mapping["INPUT_BG"]
    if "FIELD_BG" in mapping:
        mapping["INPUT_BG"] = mapping["FIELD_BG"]
    # Ensure ON_PRIMARY exists
    if "ON_PRIMARY" not in mapping:
        try:
            c = QColor(mapping.get("PRIMARY", "#3b82f6"))
            yiq = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
            mapping["ON_PRIMARY"] = "#000000" if yiq >= 140 else "#ffffff"
        except Exception:
            mapping["ON_PRIMARY"] = "#ffffff"

    # Derived variables (disabled/toggle) and other tokens used by QSS
    mapping = _augment_mapping_with_derived(mapping)

    # Create and set the theme object on the application instance
    theme_obj = Theme(theme_name, mapping)
    app.theme = theme_obj

    # Set theme name for cache segregation
    app.setProperty("_qthemes_current_theme", theme_name)

    # Apply QPalette
    palette = build_palette_from_mapping(mapping)
    app.setPalette(palette)

    # Render QSS
    stylesheet = render_qss(mapping, template)
    if additional_qss:
        stylesheet += f"\n{additional_qss}"

    target.setStyleSheet(stylesheet)

    # Emit theme changed signal
    if hasattr(app.theme, "themeChanged"):
        app.theme.themeChanged.emit()
