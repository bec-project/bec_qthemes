from __future__ import annotations

from pathlib import Path

from qtpy.QtGui import QColor
from qtpy.QtWidgets import QApplication, QWidget

from bec_qthemes._theme import Theme
from bec_qthemes.qss_editor.qss_editor import (
    DEFAULT_RADIUS,
    QSS_PATH,
    THEMES_PATH,
    _augment_mapping_with_derived,
    build_palette_from_mapping,
    read_theme_xml,
    render_qss,
)


def _apply_pyqtgraph_theme(mapping: dict) -> None:
    # ---- PyQtGraph global theming (mirror original working approach) ---------
    try:
        import pyqtgraph as pg
        from qtpy.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            return

        # Pick colors from theme mapping (falls back to original hardcoded scheme)
        bg_dark = mapping.get("PLOT_BG", "#141414")
        fg_dark = mapping.get("PLOT_FG", "#e8ebf1")
        lbl_dark = mapping.get("PLOT_LABEL", "#FFFFFF")
        ax_dark = mapping.get("PLOT_AXIS", "#CCCCCC")

        bg_light = mapping.get("PLOT_BG_LIGHT", "#e9ecef")
        fg_light = mapping.get("PLOT_FG_LIGHT", "#141414")
        lbl_light = mapping.get("PLOT_LABEL_LIGHT", "#000000")
        ax_light = mapping.get("PLOT_AXIS_LIGHT", "#666666")

        # Decide current mode by luminance of PLOT_BG or BG
        def _lum(hexs: str) -> float:
            c = pg.functions.mkColor(hexs)
            return 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()

        bg_guess = (
            mapping.get("PLOT_BG") or mapping.get("CARD_BG") or mapping.get("BG") or "#141414"
        )
        is_light = _lum(bg_guess) >= 140

        if is_light:
            background_color = bg_light
            foreground_color = fg_light
            label_color = lbl_light
            axis_color = ax_light
        else:
            background_color = bg_dark
            foreground_color = fg_dark
            label_color = lbl_dark
            axis_color = ax_dark

        # Collect GraphicsLayoutWidgets from all top-level widgets (original approach)
        graphic_layouts = [
            child
            for top in app.topLevelWidgets()
            for child in top.findChildren(pg.GraphicsLayoutWidget)
        ]

        # Extract PlotItems hosted by GraphicsLayout (original approach via ci.items.keys())
        plot_items = [
            item
            for gl in graphic_layouts
            for item in getattr(gl, "ci", None).items.keys()
            if getattr(gl, "ci", None)
            if isinstance(item, pg.PlotItem)
        ]

        # Extract HistogramLUTItems similarly
        histograms = [
            item
            for gl in graphic_layouts
            for item in getattr(gl, "ci", None).items.keys()
            if getattr(gl, "ci", None)
            if isinstance(item, pg.HistogramLUTItem)
        ]

        # Update global defaults so NEW plots pick the right colors
        pg.setConfigOptions(foreground=foreground_color, background=background_color)

        # Update existing GraphicsLayoutWidgets
        for gl in graphic_layouts:
            try:
                gl.setBackground(background_color)
            except Exception:
                pass

        # Update existing PlotItems
        ax_pen = pg.mkPen(color=axis_color)
        txt_pen = pg.mkPen(color=label_color)
        for pi in plot_items:
            try:
                for name in ("left", "right", "top", "bottom"):
                    ax = pi.getAxis(name)
                    if ax is None:
                        continue
                    ax.setPen(ax_pen)
                    ax.setTextPen(txt_pen)
                    try:
                        ax.setLabel(color=label_color)
                    except Exception:
                        pass
                # Title
                try:
                    pi.titleLabel.setText(pi.titleLabel.text, color=label_color)
                except Exception:
                    pass
                # Legend
                try:
                    if hasattr(pi, "legend") and pi.legend is not None:
                        pi.legend.setLabelTextColor(label_color)
                        for sample, lab in getattr(pi.legend, "items", []):
                            try:
                                lab.setText(lab.text, color=label_color)
                            except Exception:
                                pass
                except Exception:
                    pass
            except Exception:
                pass

        # Update HistogramLUTItem axes
        for h in histograms:
            try:
                h.axis.setPen(pg.mkPen(color=axis_color))
                h.axis.setTextPen(pg.mkPen(color=label_color))
            except Exception:
                pass

    except Exception:
        return


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
    elif isinstance(app.theme, Theme) and app.theme.theme == theme:
        return  # Theme is already applied

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

    # Sync PyQtGraph global/theme for existing and future plots
    _apply_pyqtgraph_theme(mapping)

    # Create and set the theme object on the application instance
    if getattr(app, "theme", None) is None:
        theme_obj = Theme(theme_name, mapping)
        app.theme = theme_obj
    else:
        app.theme.change_theme(theme_name, mapping)
