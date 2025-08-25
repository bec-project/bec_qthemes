import sys
from pathlib import Path
from xml.etree import ElementTree as ET
import importlib.util

from qtpy.QtCore import QObject, QEvent
from qtpy.QtCore import Qt, QFileSystemWatcher, QTimer, QPoint
from qtpy.QtGui import QColor, QCursor, QPalette
from qtpy.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QSlider,
    QColorDialog,
    QFrame,
    QScrollArea,
    QMessageBox,
    QInputDialog,
    QToolButton,
    QRubberBand,
)

# Import template system for material icon support
try:
    from bec_qthemes._template import render_template

    TEMPLATE_AVAILABLE = True
except ImportError:
    render_template = None  # type: ignore
    TEMPLATE_AVAILABLE = False

# ------------------------- Paths & defaults -------------------------

SCRIPT_DIR = Path(__file__).parent
THEME_QSS_PATH = SCRIPT_DIR / "theme_base.qss"
THEMES_DIR = SCRIPT_DIR / "themes"
QSS_DIR = SCRIPT_DIR / "qss"
# Expose paths for external use
QSS_PATH = THEME_QSS_PATH
THEMES_PATH = THEMES_DIR

DEFAULT_QSS = """"""
# ------------------------- QPalette builder -------------------------


def _qc(hex_str: str, fallback: str = "#000000") -> QColor:
    c = QColor(hex_str)
    if not c.isValid():
        c = QColor(fallback)
    return c


# simple linear blend between two colors
def _mix(c1: QColor, c2: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, float(t)))
    r = int(c1.red() * (1.0 - t) + c2.red() * t)
    g = int(c1.green() * (1.0 - t) + c2.green() * t)
    b = int(c1.blue() * (1.0 - t) + c2.blue() * t)
    a = int(c1.alpha() * (1.0 - t) + c2.alpha() * t)
    out = QColor(r, g, b)
    out.setAlpha(a)
    return out


# Radius variables (added): names and defaults
RADIUS_KEYS = ["RADIUS_SMALL", "RADIUS_MEDIUM", "RADIUS_LARGE"]
DEFAULT_RADIUS = {"RADIUS_SMALL": "4px", "RADIUS_MEDIUM": "6px", "RADIUS_LARGE": "9px"}


def build_palette_from_mapping(mapping: dict[str, str]) -> QPalette:
    """Create a QPalette from our color mapping using Qt roles sensibly.

    Variables (all optional; smart fallbacks used if missing):
      BG, FG, FIELD_BG, CARD_BG, PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK, ON_PRIMARY, BORDER
      BUTTON_BG, ALT_BG, HEADER_BG, SEPARATOR
    """

    def _is_dark(c: QColor) -> bool:
        return (0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()) < 128

    # Base tokens
    bg = _qc(mapping.get("BG", "#0f1115"))
    fg = _qc(mapping.get("FG", "#e8ebf1"))
    base = _qc(mapping.get("FIELD_BG", "#10131a"))
    card = _qc(mapping.get("CARD_BG", "#171a21"))
    border = _qc(mapping.get("BORDER", "#2a2f3a"))
    primary = _qc(mapping.get("PRIMARY", "#3b82f6"))
    on_primary = _qc(mapping.get("ON_PRIMARY", "#ffffff"))

    # Optional tokens
    button_bg = _qc(mapping.get("BUTTON_BG", mapping.get("CARD_BG", card.name())))
    separator = _qc(mapping.get("SEPARATOR", mapping.get("BORDER", border.name())))

    # Derived smart defaults when missing
    if "ALT_BG" in mapping:
        alt_bg = _qc(mapping["ALT_BG"])
    else:
        alt_bg = _mix(base, fg if _is_dark(base) else bg, 0.06)

    if "HEADER_BG" in mapping:
        header_bg = _qc(mapping["HEADER_BG"])
    else:
        header_bg = _mix(card, fg if _is_dark(card) else bg, 0.07)

    # Legacy bevel roles derived from header/sep so headers don't pick BORDER by mistake
    light1 = header_bg.lighter(125)
    light2 = header_bg.lighter(112)
    darkline = separator.darker(120)
    shadow = separator.darker(150)

    pal = QPalette()

    for group in (QPalette.Active, QPalette.Inactive):
        # Containers
        pal.setColor(group, QPalette.Window, bg)
        pal.setColor(group, QPalette.WindowText, fg)
        # Viewports / editors
        pal.setColor(group, QPalette.Base, base)
        pal.setColor(group, QPalette.AlternateBase, alt_bg)
        pal.setColor(group, QPalette.Text, fg)
        # Buttons & many headers/toolbars
        pal.setColor(group, QPalette.Button, header_bg)
        pal.setColor(group, QPalette.ButtonText, fg)
        pal.setColor(group, QPalette.BrightText, on_primary)
        # Tooltips
        pal.setColor(group, QPalette.ToolTipBase, card)
        pal.setColor(group, QPalette.ToolTipText, fg)
        # Links / selection
        pal.setColor(group, QPalette.Link, primary)
        pal.setColor(group, QPalette.LinkVisited, primary)
        pal.setColor(group, QPalette.Highlight, primary)
        pal.setColor(group, QPalette.HighlightedText, on_primary)
        # Bevel/sections
        pal.setColor(group, QPalette.Mid, header_bg)  # some styles sample Mid for sections
        pal.setColor(group, QPalette.Dark, darkline)
        pal.setColor(group, QPalette.Shadow, shadow)
        pal.setColor(group, QPalette.Light, light1)
        pal.setColor(group, QPalette.Midlight, light2)
        # Placeholder
        try:
            pal.setColor(group, QPalette.PlaceholderText, _mix(fg, base, 0.55))
        except Exception:
            pass

    # Disabled — keep surfaces, dim text & selection
    dim_fg = _mix(fg, base, 0.55)
    pal.setColor(QPalette.Disabled, QPalette.Window, bg)
    pal.setColor(QPalette.Disabled, QPalette.WindowText, dim_fg)
    pal.setColor(QPalette.Disabled, QPalette.Base, base)
    pal.setColor(QPalette.Disabled, QPalette.AlternateBase, alt_bg)
    pal.setColor(QPalette.Disabled, QPalette.Text, dim_fg)
    pal.setColor(QPalette.Disabled, QPalette.Button, _mix(header_bg, base, 0.2))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, dim_fg)
    pal.setColor(QPalette.Disabled, QPalette.BrightText, on_primary)
    pal.setColor(QPalette.Disabled, QPalette.ToolTipBase, card)
    pal.setColor(QPalette.Disabled, QPalette.ToolTipText, dim_fg)
    pal.setColor(QPalette.Disabled, QPalette.Link, primary)
    pal.setColor(QPalette.Disabled, QPalette.LinkVisited, primary)
    pal.setColor(QPalette.Disabled, QPalette.Highlight, _mix(primary, base, 0.75))
    pal.setColor(QPalette.Disabled, QPalette.HighlightedText, on_primary)

    pal.setColor(QPalette.Disabled, QPalette.Mid, header_bg)
    pal.setColor(QPalette.Disabled, QPalette.Dark, darkline)
    pal.setColor(QPalette.Disabled, QPalette.Shadow, shadow)
    pal.setColor(QPalette.Disabled, QPalette.Light, light1)
    pal.setColor(QPalette.Disabled, QPalette.Midlight, light2)

    try:
        pal.setColor(QPalette.Disabled, QPalette.PlaceholderText, _mix(fg, base, 0.7))
    except Exception:
        pass

    return pal


DEFAULT_THEMES = [
    (
        "Dark Blue",
        {
            "PRIMARY": "#3b82f6",
            "PRIMARY_LIGHT": "#60a5fa",
            "PRIMARY_DARK": "#1d4ed8",
            "ON_PRIMARY": "#ffffff",
            "BG": "#0f1115",
            "CARD_BG": "#171a21",
            "FIELD_BG": "#10131a",
            "BORDER": "#2a2f3a",
            "FG": "#e8ebf1",
            "ACCENT_DEFAULT": "#8ab4f7",
            "ACCENT_HIGHLIGHT": "#B53565",
            "ACCENT_WARNING": "#EAC435",
            "ACCENT_EMERGENCY": "#CC181E",
            "ACCENT_SUCCESS": "#2CA58D",
            # radius defaults
            **DEFAULT_RADIUS,
            "CONTRAST_FACTOR": "1.00",
        },
    ),
    (
        "Light Purple",
        {
            "PRIMARY": "#8b5cf6",
            "PRIMARY_LIGHT": "#a78bfa",
            "PRIMARY_DARK": "#6d28d9",
            "ON_PRIMARY": "#ffffff",
            "BG": "#f6f7fb",
            "CARD_BG": "#ffffff",
            "FIELD_BG": "#ffffff",
            "BORDER": "#d9dde6",
            "FG": "#151924",
            "ACCENT_DEFAULT": "#0a60ff",
            "ACCENT_HIGHLIGHT": "#B53565",
            "ACCENT_WARNING": "#EAC435",
            "ACCENT_EMERGENCY": "#CC181E",
            "ACCENT_SUCCESS": "#2CA58D",
            # radius defaults
            **DEFAULT_RADIUS,
            "CONTRAST_FACTOR": "1.00",
        },
    ),
]


# ------------------------- Core rendering -------------------------


def render_qss(vars_map: dict[str, str], template: str) -> str:
    """
    Render QSS template with material icon support and variable substitution.

    First does %%VARIABLE%% replacement, then processes template syntax with resolved colors.
    """
    qss = template

    # Step 1: First resolve all %%VARIABLE%% placeholders to actual hex values
    # This ensures theme variables are available to material icon filters
    for key, val in vars_map.items():
        qss = qss.replace(f"%%{key}%%", val)

    # Step 2: Process template syntax (material icons, etc.) with resolved variables
    if TEMPLATE_AVAILABLE:
        try:
            # Pass the resolved variables to the template engine
            qss = render_template(qss, vars_map)
        except Exception as e:
            print(f"Template processing error: {e}")
            import traceback

            traceback.print_exc()
            # Fall back to the already processed QSS

    # Check for any remaining unresolved placeholders
    if "%%" in qss:
        import re

        missing = sorted(set(m.group(1) for m in re.finditer(r"%%([A-Z_]+)%%", qss)))
        if missing:
            raise ValueError(f"Unresolved stylesheet placeholders: {missing}")

    return qss


def _augment_mapping_with_derived(mapping: dict[str, str]) -> dict[str, str]:
    """Ensure palette-derived variables exist so QSS doesn't have unresolved placeholders."""
    try:
        bg_c = _qc(mapping.get("BG", "#0f1115"))
        base_c = _qc(mapping.get("FIELD_BG", "#10131a"))
        card_c = _qc(mapping.get("CARD_BG", "#171a21"))
        fg_c = _qc(mapping.get("FG", "#e8ebf1"))
        border_c = _qc(mapping.get("BORDER", "#2a2f3a"))

        mapping.setdefault("DISABLED_FG", _mix(fg_c, base_c, 0.60).name())
        mapping.setdefault("DISABLED_BG", _mix(base_c, card_c, 0.50).name())
        mapping.setdefault("DISABLED_BORDER", _mix(border_c, base_c, 0.60).name())

        mapping.setdefault("TOGGLE_BG", _mix(base_c, fg_c, 0.25).name())
        mapping.setdefault("TOGGLE_BORDER", _mix(border_c, fg_c, 0.35).name())

        # Plot colors: preserve previous hardcoded scheme but make it themable
        # Decide light/dark by BG luminance
        def _lum(c: QColor) -> float:
            return 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()

        is_dark = _lum(bg_c) < 128
        mapping.setdefault("THEME_MODE", "dark" if is_dark else "light")
        mapping.setdefault("IS_DARK", "true" if is_dark else "false")
        if is_dark:
            mapping.setdefault("PLOT_BG", "#141414")
            mapping.setdefault("PLOT_FG", "#e8ebf1")
            mapping.setdefault("PLOT_LABEL", "#ffffff")
            mapping.setdefault("PLOT_AXIS", "#cccccc")
        else:
            mapping.setdefault("PLOT_BG", "#e9ecef")
            mapping.setdefault("PLOT_FG", "#141414")
            mapping.setdefault("PLOT_LABEL", "#000000")
            mapping.setdefault("PLOT_AXIS", "#666666")
    except Exception:
        pass
    return mapping


# ------------------------- Theme XML utils -------------------------


def ensure_files():
    THEMES_DIR.mkdir(exist_ok=True)
    if not THEME_QSS_PATH.exists():
        THEME_QSS_PATH.write_text(DEFAULT_QSS, encoding="utf-8")
    if not any(THEMES_DIR.glob("*.xml")):
        for name, mapping in DEFAULT_THEMES:
            write_theme_xml(THEMES_DIR / f"{name}.xml", name, mapping)


def write_theme_xml(path: Path, theme_name: str, mapping: dict[str, str]) -> None:
    # Determine and persist theme mode (dark/light) on the root for downstream consumers
    mode = None
    try:
        mode = (mapping.get("THEME_MODE") or mapping.get("theme_mode") or "").strip().lower()
        if mode not in ("dark", "light"):
            bg = _qc(mapping.get("BG", "#0f1115"))
            # compute perceived luminance
            lum = 0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue()
            mode = "dark" if lum < 128 else "light"
        # reflect into mapping for completeness
        mapping.setdefault("THEME_MODE", mode)
        mapping.setdefault("IS_DARK", "true" if mode == "dark" else "false")
    except Exception:
        pass

    root = ET.Element("theme", {"name": theme_name, "mode": mode or ""})
    for k, v in mapping.items():
        el = ET.SubElement(root, "color", {"name": k})
        el.text = v
    try:
        ET.indent(root, space="  ")  # Python 3.9+
    except Exception:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def read_theme_xml(path: Path) -> tuple[str, dict[str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        raise ValueError(f"Cannot read theme XML '{path}': {e}") from e
    if not text.strip():
        raise ValueError(f"Theme XML '{path}' is empty.")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in '{path}': {e}") from e
    if root.tag != "theme":
        raise ValueError(f"Theme XML '{path}' must have root <theme>, got <{root.tag}>.")
    theme_name = root.attrib.get("name", path.stem)
    mapping: dict[str, str] = {}
    for el in root.findall("./color"):
        name = el.attrib.get("name")
        val = (el.text or "").strip() or el.attrib.get("value", "").strip()
        if name and val:
            mapping[name] = val
    # Restore mode information (if provided) for downstream consumers (e.g., pyqtgraph)
    mode = (root.attrib.get("mode", "") or mapping.get("THEME_MODE", "")).strip().lower()
    if mode in ("dark", "light"):
        mapping.setdefault("THEME_MODE", mode)
        mapping.setdefault("IS_DARK", "true" if mode == "dark" else "false")
    return theme_name, mapping


def list_theme_files() -> list[Path]:
    THEMES_DIR.mkdir(exist_ok=True)
    return sorted(THEMES_DIR.glob("*.xml"))


def list_qss_files() -> list[Path]:
    """Return available QSS templates. Prefer files in qss/ directory; fallback to theme_base.qss."""
    qss_dir = QSS_DIR
    qss_dir.mkdir(exist_ok=True)
    found = sorted(qss_dir.glob("*.qss"))
    if not found:
        # Fallback so the tool still works without a qss/ folder content
        if THEME_QSS_PATH.exists():
            return [THEME_QSS_PATH]
    return found


# ------------------------- Reusable applier -------------------------


def apply_qss_with_xml(
    qss_path: Path, xml_path: Path, target: QWidget | QApplication | None = None
) -> str:
    template = qss_path.read_text(encoding="utf-8")
    theme_name, mapping = read_theme_xml(xml_path)
    # Ensure radius defaults exist
    for k, v in DEFAULT_RADIUS.items():
        mapping.setdefault(k, v)
    # Normalize aliases (INPUT_BG ↔ FIELD_BG)
    if "INPUT_BG" in mapping and "FIELD_BG" not in mapping:
        mapping["FIELD_BG"] = mapping["INPUT_BG"]
    if "FIELD_BG" in mapping:
        mapping["INPUT_BG"] = mapping["FIELD_BG"]
    # Ensure ON_PRIMARY exists even if XML omitted it
    if "ON_PRIMARY" not in mapping:
        try:
            # Choose contrasting text vs PRIMARY (fallback to white)
            c = QColor(mapping.get("PRIMARY", "#3b82f6"))
            if not c.isValid():
                raise ValueError("invalid primary")
            yiq = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
            mapping["ON_PRIMARY"] = "#000000" if yiq >= 140 else "#ffffff"
        except Exception:
            mapping["ON_PRIMARY"] = "#ffffff"
    try:
        bg_c = _qc(mapping.get("BG", "#0f1115"))
        base_c = _qc(mapping.get("FIELD_BG", "#10131a"))
        card_c = _qc(mapping.get("CARD_BG", "#171a21"))
        fg_c = _qc(mapping.get("FG", "#e8ebf1"))
        border_c = _qc(mapping.get("BORDER", "#2a2f3a"))

        # Disabled palette tokens
        mapping.setdefault("DISABLED_FG", _mix(fg_c, base_c, 0.60).name())
        mapping.setdefault("DISABLED_BG", _mix(base_c, card_c, 0.50).name())
        mapping.setdefault("DISABLED_BORDER", _mix(border_c, base_c, 0.60).name())

        # Toggled toolbar button tokens — neutral grey derived from surfaces
        mapping.setdefault("TOGGLE_BG", _mix(base_c, fg_c, 0.18).name())
        mapping.setdefault("TOGGLE_BORDER", _mix(border_c, fg_c, 0.25).name())
    except Exception:
        pass
    mapping = _augment_mapping_with_derived(mapping)
    app = QApplication.instance()
    # expose the current XML theme name for cache segregation BEFORE rendering
    try:
        if app is not None and isinstance(theme_name, str) and theme_name:
            app.setProperty("theme", theme_name)
    except Exception:
        pass
    qss = render_qss(mapping, template)
    # Reset stylesheet first so old rules don't linger
    try:
        if target is None or isinstance(target, QApplication):
            app.setStyleSheet("")
        elif isinstance(target, QWidget):
            target.setStyleSheet("")
        else:
            app.setStyleSheet("")
    except Exception:
        pass
    if target is None or isinstance(target, QApplication):
        app.setStyleSheet(qss)
    elif isinstance(target, QWidget):
        target.setStyleSheet(qss)
    else:
        app.setStyleSheet(qss)

    # Also apply palette
    palette = build_palette_from_mapping(mapping)
    app.setPalette(palette)

    return qss


# ------------------------- Inspector -------------------------


class WidgetInspector(QWidget):
    """Hover-based inspector: highlights widget under cursor and shows selector hints."""

    def __init__(self, exclude_roots: list[QWidget] | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._exclude_roots = exclude_roots or []
        self._rubber = QRubberBand(QRubberBand.Rectangle)
        self._hint = QLabel()
        self._hint.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self._hint.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._hint.setStyleSheet(
            "QLabel {"
            " background: rgba(20,20,28,190);"
            " color: white;"
            " border: 1px solid rgba(255,255,255,100);"
            " padding: 6px 8px;"
            " border-radius: 6px;"
            " font-size: 12px;"
            "}"
        )
        self._pos = QCursor.pos()
        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._tick)
        self._enabled = False
        self._info_to_copy = ""

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if not self._enabled:
            return super().eventFilter(watched, event)

        if event.type() == QEvent.MouseButtonPress:
            w = QApplication.widgetAt(QCursor.pos())
            if w and not self._is_excluded(w):
                clipboard = QApplication.clipboard()
                if clipboard and self._info_to_copy:
                    clipboard.setText(self._info_to_copy)
                    print(
                        f"Inspector: Copied QSS rule for '{w.objectName() or w.metaObject().className()}' to clipboard."
                    )
                    # Flash rubber band for feedback
                    self._rubber.setStyleSheet("border: 2px solid #3b82f6;")
                    QTimer.singleShot(300, lambda: self._rubber.setStyleSheet(""))
                return True  # Consume the event
        return super().eventFilter(watched, event)

    def set_enabled(self, enabled: bool):
        if self._enabled == enabled:
            return
        self._enabled = enabled
        app = QApplication.instance()
        if enabled:
            if app:
                app.installEventFilter(self)
            self._rubber.show()
            self._hint.show()
            self._timer.start()
        else:
            if app:
                app.removeEventFilter(self)
            self._timer.stop()
            self._rubber.hide()
            self._hint.hide()

    def _is_excluded(self, w: QWidget | None) -> bool:
        if w is None:
            return False
        for root in self._exclude_roots:
            p = w
            while p is not None:
                if p is root:
                    return True
                p = p.parentWidget()
        return False

    def _tick(self):
        pos = QCursor.pos()
        if pos == self._pos:
            return
        self._pos = pos
        w = QApplication.widgetAt(pos)
        if w is None or self._is_excluded(w):
            self._rubber.hide()
            self._hint.hide()
            return
        # Compute global rect of the widget
        top_left = w.mapToGlobal(QPoint(0, 0))
        rect = w.rect()
        self._rubber.setGeometry(top_left.x(), top_left.y(), rect.width(), rect.height())
        self._rubber.show()

        # Build info
        cls = w.metaObject().className()
        obj = w.objectName() or "<no objectName>"
        props = []
        try:
            for b in w.dynamicPropertyNames():
                key = bytes(b).decode()
                # Filter out internal Qt properties and complex values
                if key.startswith("_q_") or not isinstance(
                    w.property(key), (str, int, float, bool)
                ):
                    continue
                val = w.property(key)
                if isinstance(val, bool):
                    val = str(val).lower()
                props.append(f'[{key}="{val}"]')
        except Exception:
            pass
        # Parent chain (short)
        chain = []
        p = w.parentWidget()
        depth = 0
        while p is not None and depth < 3:
            chain.append(p.metaObject().className())
            p = p.parentWidget()
            depth += 1
        chain_str = " → ".join(chain) if chain else "<top>"

        # Inheritance chain
        inheritance_chain = []
        try:
            for base_class in w.__class__.__mro__:
                inheritance_chain.append(base_class.__name__)
                if base_class is QWidget:
                    break
        except Exception:
            inheritance_chain = ["Could not determine inheritance"]
        inheritance_str = " → ".join(inheritance_chain)

        # Widget states
        states_parts = []
        states_parts.append("<b><code>:hover</code></b>")  # Hover is implicit

        if w.isEnabled():
            states_parts.append("<b><code>:enabled</code></b>")
            states_parts.append("<code>:disabled</code>")
        else:
            states_parts.append("<code>:enabled</code>")
            states_parts.append("<b><code>:disabled</code></b>")

        if w.hasFocus():
            states_parts.append("<b><code>:focus</code></b>")
        else:
            states_parts.append("<code>:focus</code>")

        if hasattr(w, "isCheckable") and w.isCheckable():
            if w.isChecked():
                states_parts.append("<b><code>:checked</code></b>")
                states_parts.append("<code>:unchecked</code>")
            else:
                states_parts.append("<code>:checked</code>")
                states_parts.append("<b><code>:unchecked</code></b>")

        if isinstance(w, (QPushButton, QToolButton)):
            if hasattr(w, "isDown") and w.isDown():
                states_parts.append("<b><code>:pressed</code></b>")
            else:
                states_parts.append("<code>:pressed</code>")

        if isinstance(w, QComboBox):
            if w.view().isVisible():
                states_parts.append("<b><code>:open</code></b>")
                states_parts.append("<code>:closed</code>")
            else:
                states_parts.append("<code>:open</code>")
                states_parts.append("<b><code>:closed</code></b>")

        states_str = " ".join(states_parts)

        selectors = [cls]
        if obj and obj != "<no objectName>":
            selectors.append(f"{cls}#{obj}")
        selectors += [f"{cls}{p}" for p in props]

        # Set the text to be copied to the most specific selector
        self._info_to_copy = f"{selectors[-1]} {{\n\n}}"

        selector_strings = [f"&nbsp;&nbsp;<code>{s}</code>" for s in selectors]
        info = (
            f"<b>{cls}</b>  (objectName: <code>{obj}</code>)<br>"
            f"Inheritance: <code>{inheritance_str}</code><br>"
            f"States: {states_str}<br>"
            f"Parents: {chain_str}<br>"
            f"Selectors (click widget to copy rule):<br>" + "<br>".join(selector_strings)
        )
        self._hint.setText(info)
        self._hint.adjustSize()
        self._hint.move(pos.x() + 16, pos.y() + 20)
        self._hint.show()


# ------------------------- ThemeWidget (floating tool) -------------------------


class ThemeWidget(QWidget):
    """
    Floating theming tool. Manage XML color themes, render a QSS template,
    and apply live to the application or a specific widget.

    Usage:
        tool = ThemeWidget()               # optional: pass qss_path, themes_dir
        tool.attach(target=None)           # None => app-wide
        tool.show()                        # floating panel
    """

    def __init__(
        self,
        qss_path: Path | None = None,
        themes_dir: Path | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent, Qt.Tool)
        self.setWindowTitle("Theme Tool")
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # Init state before any UI callbacks may fire
        self._var_rows: dict[str, dict] = {}
        self._is_setting_up: bool = True
        # Locks for variables (prevent auto-derive from touching them)
        self._locked: set[str] = set()

        self.qss_path = Path(qss_path) if qss_path else THEME_QSS_PATH
        self.themes_dir = Path(themes_dir) if themes_dir else THEMES_DIR
        self.qss_dir = QSS_DIR
        self._apply_target: QWidget | QApplication | None = None  # None => app

        # Watcher for qss + themes dir
        self._watcher = QFileSystemWatcher()
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(150)
        self._debounce.timeout.connect(self._on_fs_changed)
        self._arm_watcher()

        # Inspector (exclude the tool itself)
        self._inspector = WidgetInspector(exclude_roots=[self])

        # UI
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # First row: QSS + Theme combos
        row1 = QHBoxLayout()
        self.qss_combo = QComboBox()
        self._qss_files: list[Path] = []
        self.qss_combo.currentIndexChanged.connect(self._on_qss_selected)

        self.theme_combo = QComboBox()
        self._theme_files: list[Path] = []
        self.theme_combo.currentIndexChanged.connect(self._on_theme_selected)

        row1.addWidget(QLabel("QSS:"))
        row1.addWidget(self.qss_combo, 1)
        row1.addSpacing(8)
        row1.addWidget(QLabel("Theme:"))
        row1.addWidget(self.theme_combo, 1)

        # Second row: action buttons
        row2 = QHBoxLayout()
        btn_new = QPushButton("New")
        btn_new.clicked.connect(self._new_theme)
        btn_add = QPushButton("Add Var")
        btn_add.clicked.connect(self._add_var)
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._save_theme)
        btn_save_as = QPushButton("Save As…")
        btn_save_as.clicked.connect(self._save_theme_as)
        btn_apply = QPushButton("Apply")
        btn_apply.clicked.connect(self.apply_theme)

        btn_inspect = QToolButton()
        btn_inspect.setText("Inspect")
        btn_inspect.setCheckable(True)
        btn_inspect.toggled.connect(self._inspector.set_enabled)

        row2.addStretch(1)
        row2.addWidget(btn_new)
        row2.addWidget(btn_add)
        row2.addWidget(btn_save)
        row2.addWidget(btn_save_as)
        row2.addWidget(btn_apply)
        row2.addWidget(btn_inspect)

        self.vars_area = QScrollArea()
        self.vars_area.setWidgetResizable(True)
        self.vars_body = QWidget()
        self.vars_layout = QVBoxLayout(self.vars_body)
        self.vars_layout.setContentsMargins(0, 0, 0, 0)
        self.vars_layout.setSpacing(8)
        self.vars_layout.addStretch()
        self.vars_area.setWidget(self.vars_body)

        root.addLayout(row1)
        root.addLayout(row2)

        # Row 3: auto-derive & fine-tuning controls
        row3 = QHBoxLayout()
        self.auto_derive_chk = QCheckBox("Auto-derive palette")
        self.auto_derive_chk.setChecked(True)
        self.auto_derive_chk.toggled.connect(lambda _: self._recompute_auto_vars(apply_now=True))

        self.fine_tune_toggle = QToolButton()
        self.fine_tune_toggle.setText("Palette fine tuning")
        self.fine_tune_toggle.setCheckable(True)
        self.fine_tune_toggle.setChecked(False)
        self.fine_tune_toggle.toggled.connect(
            lambda _: self._on_theme_selected(self.theme_combo.currentIndex())
        )

        row3.addWidget(self.auto_derive_chk)
        row3.addSpacing(12)
        row3.addWidget(self.fine_tune_toggle)
        row3.addStretch(1)
        root.addLayout(row3)

        # Row 4: Contrast factor for auto-derive (0.50x … 2.00x)
        row4 = QHBoxLayout()
        lbl_c = QLabel("Contrast:")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(50, 200)  # 0.50 … 2.00
        self.contrast_slider.setSingleStep(1)
        self.contrast_slider.setPageStep(5)
        self.contrast_slider.setValue(100)  # default 1.00x
        self.contrast_val_lbl = QLabel("1.00x")
        self.contrast_val_lbl.setMinimumWidth(48)

        def _cchg(v: int):
            self.contrast_val_lbl.setText(f"{v/100:.2f}x")
            # Any change recomputes derived colors live
            self._recompute_auto_vars(apply_now=True)

        self.contrast_slider.valueChanged.connect(_cchg)
        row4.addWidget(lbl_c)
        row4.addWidget(self.contrast_slider, 1)
        row4.addWidget(self.contrast_val_lbl)
        root.addLayout(row4)

        root.addWidget(self.vars_area, 1)

        # Populate combos before any selection handlers run
        self._load_qss_into_combo()
        self._load_themes_into_combo()

        # initial selection: load theme vars first, then qss
        self._on_theme_selected(self.theme_combo.currentIndex())
        self._on_qss_selected(self.qss_combo.currentIndex())
        self._is_setting_up = False
        # single initial apply after both selections
        self.apply_theme()

    # ---------- public ----------
    def attach(self, target: QWidget | QApplication | None = None):
        """Attach applying scope. None => application wide."""
        self._apply_target = target
        self.apply_theme()

    # ---------- watcher ----------
    def _arm_watcher(self):
        paths: list[str] = []
        # Selected QSS file and its parent folder
        if self.qss_path.exists():
            paths.append(str(self.qss_path))
        paths.append(str(self.qss_path.parent))
        # Dedicated qss/ folder
        paths.append(str(self.qss_dir))
        # Themes folder
        paths.append(str(self.themes_dir))
        try:
            self._watcher.addPaths(paths)
        except Exception:
            pass
        self._watcher.fileChanged.connect(lambda _: self._debounce.start())
        self._watcher.directoryChanged.connect(lambda _: self._debounce.start())

    def _reset_watcher(self):
        try:
            files = getattr(self._watcher, "files", lambda: [])()
            dirs = getattr(self._watcher, "directories", lambda: [])()
            if files:
                try:
                    self._watcher.removePaths(files)
                except Exception:
                    pass
            if dirs:
                try:
                    self._watcher.removePaths(dirs)
                except Exception:
                    pass
        except Exception:
            pass
        self._arm_watcher()

    def _on_fs_changed(self):
        # Re-arm in case of atomic replace
        try:
            self._reset_watcher()
        except Exception:
            pass
        print("Filesystem change detected, reloading lists and re-applying…")
        self._load_qss_into_combo(refresh_only=True)
        self._load_themes_into_combo(refresh_only=True)
        self.apply_theme()

    # ---------- QSS IO ----------
    def _load_qss_into_combo(self, refresh_only: bool = False):
        files = list_qss_files()
        names = [p.stem for p in files]
        if not files and THEME_QSS_PATH.exists():
            files = [THEME_QSS_PATH]
            names = [THEME_QSS_PATH.stem]
        self._qss_files = files
        if not refresh_only:
            self.qss_combo.blockSignals(True)
            self.qss_combo.clear()
            for n in names:
                self.qss_combo.addItem(n)
            # Preselect the current qss_path if present in the list
            try:
                current_idx = next((i for i, p in enumerate(files) if p == self.qss_path), 0)
            except Exception:
                current_idx = 0
            self.qss_combo.setCurrentIndex(current_idx)
            self.qss_combo.blockSignals(False)

    def _current_qss_path(self) -> Path:
        idx = self.qss_combo.currentIndex()
        if 0 <= idx < len(self._qss_files):
            return self._qss_files[idx]
        return self.qss_path

    def _on_qss_selected(self, _idx: int):
        new_path = self._current_qss_path()
        if new_path != self.qss_path:
            self.qss_path = new_path
            self._reset_watcher()
        # When switching QSS, overwrite previously applied styles by re-applying
        if not getattr(self, "_is_setting_up", False):
            self.apply_theme()

    # ---------- theme IO ----------
    def _load_themes_into_combo(self, refresh_only: bool = False):
        raw = list_theme_files()
        valid_files: list[Path] = []
        names: list[str] = []
        for p in raw:
            try:
                name, _ = read_theme_xml(p)
            except Exception as e:
                print(f"Skipping invalid theme '{p}': {e}")
                continue
            valid_files.append(p)
            names.append(name)
        if not valid_files:
            for name, mapping in DEFAULT_THEMES:
                write_theme_xml(self.themes_dir / f"{name}.xml", name, mapping)
            valid_files = list_theme_files()
            names = [read_theme_xml(p)[0] for p in valid_files]
        self._theme_files = valid_files
        if not refresh_only:
            self.theme_combo.blockSignals(True)
            self.theme_combo.clear()
            for n in names:
                self.theme_combo.addItem(n)
            self.theme_combo.blockSignals(False)

    def _current_theme_path(self) -> Path:
        idx = self.theme_combo.currentIndex()
        if self._theme_files:
            if 0 <= idx < len(self._theme_files):
                return self._theme_files[idx]
            return self._theme_files[0]
        # Fallback: try to (re)load themes; _load will also create defaults if missing
        try:
            self._load_themes_into_combo()
        except Exception:
            pass
        if self._theme_files:
            idx = 0 if not (0 <= idx < len(self._theme_files)) else idx
            return self._theme_files[idx]
        # Last resort: write the first default theme and return it
        try:
            name, mapping = DEFAULT_THEMES[0]
            p = self.themes_dir / f"{name}.xml"
            write_theme_xml(p, name, mapping)
            self._load_themes_into_combo()
            return p
        except Exception as e:
            raise RuntimeError(f"No themes available and failed to create default: {e}")

    # ---------- var panel ----------
    def _clear_vars_panel(self):
        if hasattr(self, "_var_rows"):
            for _, parts in list(self._var_rows.items()):
                row = parts.get("row")
                if row is not None:
                    row.setParent(None)
            self._var_rows.clear()
        else:
            self._var_rows = {}

    def _insert_var_row(self, name: str, value: str):
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        btn = QPushButton(f"{name}  {value}")
        btn.clicked.connect(lambda _, n=name: self._on_var_clicked(n))
        self._style_color_button(btn, value)

        lock = QToolButton()
        lock.setCheckable(True)
        lock.setChecked(name in self._locked)
        lock.setText("🔒" if name in self._locked else "🔓")
        lock.setToolTip("Lock this variable so auto-derive won't change it")
        lock.setFixedWidth(24)

        def _on_lock(t: bool, n=name, w=lock):
            self._toggle_lock(n, t)
            w.setText("🔒" if t else "🔓")

        lock.toggled.connect(_on_lock)

        rm = QToolButton()
        rm.setText("✕")
        rm.setToolTip(f"Remove '{name}'")
        rm.setFixedWidth(24)
        rm.clicked.connect(lambda _, n=name: self._remove_var(n))

        h.addWidget(btn, 1)
        h.addWidget(lock, 0)
        h.addWidget(rm, 0)

        self._var_rows[name] = {"row": row, "btn": btn, "lock": lock, "rm": rm, "type": "color"}
        self.vars_layout.insertWidget(self.vars_layout.count() - 1, row)

    def _insert_section(self, title: str):
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 8, 0, 4)
        h.setSpacing(6)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: 600; opacity: 0.8;")
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("margin-top: 8px; margin-bottom: 0px;")

        h.addWidget(lbl, 0)
        h.addWidget(line, 1)

        self._var_rows["__section__" + title] = {"row": row, "type": "section"}
        self.vars_layout.insertWidget(self.vars_layout.count() - 1, row)

    def _insert_radius_row(self, name: str, value_px: int):
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        lbl = QLabel(name)
        lbl.setMinimumWidth(120)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 24)
        slider.setSingleStep(1)
        slider.setValue(value_px)
        val_lbl = QLabel(f"{value_px} px")
        val_lbl.setMinimumWidth(50)

        def _on_changed(v: int):
            val_lbl.setText(f"{v} px")
            # live-apply theme on change
            self.apply_theme()

        slider.valueChanged.connect(_on_changed)

        rm = QToolButton()
        rm.setText("✕")
        rm.setToolTip(f"Remove '{name}'")
        rm.setFixedWidth(24)
        rm.clicked.connect(lambda: self._remove_var(name))

        h.addWidget(lbl, 0)
        h.addWidget(slider, 1)
        h.addWidget(val_lbl, 0)
        h.addWidget(rm, 0)

        self._var_rows[name] = {
            "row": row,
            "label": lbl,
            "slider": slider,
            "val_lbl": val_lbl,
            "rm": rm,
            "type": "radius",
        }
        self.vars_layout.insertWidget(self.vars_layout.count() - 1, row)

    def _style_color_button(self, btn: QPushButton, hex_color: str):
        text_color = self._contrast_text(hex_color)
        btn.setStyleSheet(
            "QPushButton {"
            f" background-color: {hex_color};"
            f" color: {text_color};"
            " border: 1px solid #40454f; padding: 8px 12px; border-radius: 8px; text-align: left;"
            "}"
        )

    def _contrast_text(self, hex_color: str) -> str:
        c = QColor(hex_color)
        if not c.isValid():
            return "#000000"
        yiq = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        return "#000000" if yiq >= 140 else "#ffffff"

    def _populate_vars(self, mapping: dict[str, str]):
        self._clear_vars_panel()
        # Ensure radius keys present with defaults
        for k, v in DEFAULT_RADIUS.items():
            mapping.setdefault(k, v)

        # Ensure ON_PRIMARY exists so QSS placeholders are always resolvable and the button is visible
        try:
            if "ON_PRIMARY" not in mapping:
                mapping["ON_PRIMARY"] = self._contrast_text(mapping.get("PRIMARY", "#3b82f6"))
        except Exception:
            mapping.setdefault("ON_PRIMARY", "#ffffff")

        CORE_PRIMARY = ["PRIMARY", "PRIMARY_LIGHT", "PRIMARY_DARK", "ON_PRIMARY"]
        CORE_BG_SURF = ["BG", "CARD_BG", "FIELD_BG"]  # FIELD_BG = INPUT_BG
        CORE_TEXT_BORDER = ["FG", "BORDER"]
        ACCENTS = [
            "ACCENT_DEFAULT",
            "ACCENT_HIGHLIGHT",
            "ACCENT_WARNING",
            "ACCENT_EMERGENCY",
            "ACCENT_SUCCESS",
        ]
        ADVANCED = ["BUTTON_BG", "ALT_BG", "HEADER_BG", "SEPARATOR"]
        RADII = RADIUS_KEYS[:]

        # Show core sections
        self._insert_section("Primary")
        for k in CORE_PRIMARY:
            if k in mapping:
                self._insert_var_row(k, mapping[k])

        self._insert_section("Background / Surfaces")
        for k in CORE_BG_SURF:
            if k in mapping:
                self._insert_var_row(k, mapping[k])

        self._insert_section("Text & Border")
        for k in CORE_TEXT_BORDER:
            if k in mapping:
                self._insert_var_row(k, mapping[k])

        self._insert_section("Accent")
        for k in ACCENTS:
            if k in mapping:
                self._insert_var_row(k, mapping[k])

        # Advanced (hidden unless toggled)
        shown = set(CORE_PRIMARY + CORE_BG_SURF + CORE_TEXT_BORDER + ACCENTS)
        if getattr(self, "fine_tune_toggle", None) and self.fine_tune_toggle.isChecked():
            self._insert_section("Palette fine tuning")
            for k in ADVANCED:
                if k in mapping:
                    self._insert_var_row(k, mapping[k])
            # Any custom variables
            custom = [k for k in mapping.keys() if k not in shown and k not in RADII]
            for k in custom:
                self._insert_var_row(k, mapping[k])

        # Radius sliders at the end
        self._insert_section("Radius")
        for k in RADII:
            if k in mapping:
                try:
                    vv = int(str(mapping[k]).replace("px", "").strip())
                except Exception:
                    vv = int(DEFAULT_RADIUS.get(k, "6px").replace("px", ""))
                self._insert_radius_row(k, vv)

    def _toggle_lock(self, name: str, locked: bool):
        if locked:
            self._locked.add(name)
        else:
            self._locked.discard(name)

    def _gather_vars(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for name, parts in self._var_rows.items():
            typ = parts.get("type", "color")
            if typ == "radius":
                slider: QSlider = parts.get("slider")  # type: ignore
                if slider is None:
                    continue
                v = int(slider.value())
                mapping[name] = f"{v}px"
                continue
            if typ == "section":
                # visual separator row; no data
                continue
            btn = parts.get("btn")
            if btn is None:
                continue
            text = btn.text() if hasattr(btn, "text") else ""
            val = text.split("  ", 1)[1] if "  " in text else ""
            if val:
                mapping[name] = val
        try:
            mapping["CONTRAST_FACTOR"] = f"{self.contrast_slider.value()/100:.2f}"
        except Exception:
            mapping["CONTRAST_FACTOR"] = "1.00"
        return mapping

    def _set_var_value(self, name: str, value: str):
        parts = self._var_rows.get(name)
        if not parts:
            return
        if parts.get("type") == "radius":
            slider: QSlider = parts.get("slider")  # type: ignore
            if slider is not None:
                try:
                    v = int(str(value).replace("px", "").strip())
                except Exception:
                    return
                slider.setValue(v)
            return
        btn = parts.get("btn")
        btn.setText(f"{name}  {value}")
        self._style_color_button(btn, value)

    def _remove_var(self, name: str):
        parts = self._var_rows.pop(name, None)
        if not parts:
            return
        row = parts.get("row")
        if row is not None:
            row.setParent(None)
        self.apply_theme()

    # ---------- actions ----------
    def _on_theme_selected(self, _idx: int):
        path = self._current_theme_path()
        try:
            name, mapping = read_theme_xml(path)
        except Exception as e:
            QMessageBox.warning(self, "Theme Error", f"Failed to load theme:\n{e}")
            return
        # Expose current theme name for cache segregation
        try:
            app = QApplication.instance()
            if app is not None and isinstance(name, str) and name:
                app.setProperty("_qthemes_current_theme", name)
        except Exception:
            pass
        # ensure radius keys always available in the editor view
        for k, v in DEFAULT_RADIUS.items():
            mapping.setdefault(k, v)

        # Sync contrast factor from XML if present
        try:
            cf = float(mapping.get("CONTRAST_FACTOR", "1.0"))
            cf_int = max(50, min(200, int(round(cf * 100))))
            self.contrast_slider.blockSignals(True)
            self.contrast_slider.setValue(cf_int)
            self.contrast_val_lbl.setText(f"{cf_int/100:.2f}x")
            self.contrast_slider.blockSignals(False)
        except Exception:
            pass
        self._populate_vars(mapping)
        if not getattr(self, "_is_setting_up", False):
            self.apply_theme()

    def _new_theme(self):
        base = f"New Theme {len(self._theme_files)+1}"
        mapping = {
            "PRIMARY": "#3b82f6",
            "PRIMARY_LIGHT": "#60a5fa",
            "PRIMARY_DARK": "#1d4ed8",
            "ON_PRIMARY": "#ffffff",
            "BG": "#0f1115",
            "CARD_BG": "#171a21",
            "FIELD_BG": "#10131a",
            "BORDER": "#2a2f3a",
            "FG": "#e8ebf1",
            "ACCENT_DEFAULT": "#8ab4f7",
            "ACCENT_HIGHLIGHT": "#B53565",
            "ACCENT_WARNING": "#EAC435",
            "ACCENT_EMERGENCY": "#CC181E",
            "ACCENT_SUCCESS": "#2CA58D",
            **DEFAULT_RADIUS,
        }
        path = self.themes_dir / f"{base}.xml"
        write_theme_xml(path, base, mapping)
        self._load_themes_into_combo()
        self.theme_combo.setCurrentIndex(self.theme_combo.count() - 1)
        self._on_theme_selected(self.theme_combo.currentIndex())

    def _add_var(self):
        name, ok = QInputDialog.getText(self, "Add Variable", "Variable name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self._var_rows:
            QMessageBox.information(self, "Add Variable", f"'{name}' already exists.")
            return
        # If user adds one of the recognized radius variables, create a slider row
        if name.upper() in RADIUS_KEYS:
            default_v = int(DEFAULT_RADIUS[name.upper()].replace("px", ""))
            self._insert_radius_row(name.upper(), default_v)
            self.apply_theme()
            return
        chosen = QColorDialog.getColor(QColor("#3b82f6"), self, f"Choose color for {name}")
        if chosen.isValid():
            self._insert_var_row(name, chosen.name())
            self.apply_theme()

    def _save_theme(self):
        path = self._current_theme_path()
        name = self.theme_combo.currentText() or path.stem
        mapping = self._gather_vars()
        try:
            write_theme_xml(path, name, mapping)
        except Exception as e:
            QMessageBox.warning(self, "Save Theme", f"Failed to save theme:\n{e}")

    def _save_theme_as(self):
        base = self.theme_combo.currentText() or "Untitled"
        name, ok = QInputDialog.getText(
            self, "Save Theme As", "New theme name:", text=f"{base} Copy"
        )
        if not ok or not name.strip():
            return
        mapping = self._gather_vars()
        path = self.themes_dir / f"{name.strip()}.xml"
        try:
            write_theme_xml(path, name.strip(), mapping)
            self._load_themes_into_combo()
            self.theme_combo.setCurrentIndex(self.theme_combo.count() - 1)
            self._on_theme_selected(self.theme_combo.currentIndex())
        except Exception as e:
            QMessageBox.warning(self, "Save Theme As", f"Failed to save:\n{e}")

    # ---------- color picking ----------
    def _on_var_clicked(self, name: str):
        parts = self._var_rows.get(name)
        if parts and parts.get("type") == "radius":
            # radius vars are adjusted with their slider
            return
        current_val = self._gather_vars().get(name, "#3b82f6")
        original = current_val
        initial = QColor(current_val) if QColor(current_val).isValid() else QColor("#3b82f6")

        dialog = QColorDialog(self)
        dialog.setOption(QColorDialog.DontUseNativeDialog, False)
        dialog.setCurrentColor(initial)

        def _preview(c: QColor):
            if c.isValid():
                self._set_var_value(name, c.name())
                self._recompute_auto_vars(apply_now=True)

        def _finalize(c: QColor):
            if c.isValid():
                self._set_var_value(name, c.name())
                self._recompute_auto_vars(apply_now=True)

        dialog.currentColorChanged.connect(_preview)
        dialog.colorSelected.connect(_finalize)

        result = dialog.exec_()
        if result == 0:  # canceled -> restore
            self._set_var_value(name, original)
            self._recompute_auto_vars(apply_now=True)

    def _mapping_with_auto_derived(self, mapping: dict[str, str]) -> dict[str, str]:
        m = dict(mapping)
        # carry contrast factor forward
        try:
            m["CONTRAST_FACTOR"] = f"{float(mapping.get('CONTRAST_FACTOR', '1.0')):.2f}"
        except Exception:
            m["CONTRAST_FACTOR"] = "1.00"
        # Mirror aliases
        if "INPUT_BG" in m and "FIELD_BG" not in m:
            m["FIELD_BG"] = m["INPUT_BG"]
        if "FIELD_BG" in m:
            m["INPUT_BG"] = m["FIELD_BG"]
        if getattr(self, "auto_derive_chk", None) and self.auto_derive_chk.isChecked():
            derived = self._auto_derive_colors(m)
            for k, v in derived.items():
                if k.startswith("ACCENT_"):
                    continue
                if k in self._locked:
                    continue
                m[k] = v
        # Ensure ON_PRIMARY exists even when auto-derive is off
        if "ON_PRIMARY" not in m:
            try:
                m["ON_PRIMARY"] = self._contrast_text(m.get("PRIMARY", "#3b82f6"))
            except Exception:
                m["ON_PRIMARY"] = "#ffffff"
        return m

    def _recompute_auto_vars(self, apply_now: bool = False):
        mapping = self._gather_vars()
        # Keep aliases in sync for UI
        if "FIELD_BG" in mapping:
            mapping["INPUT_BG"] = mapping["FIELD_BG"]
        if self.auto_derive_chk.isChecked():
            derived = self._auto_derive_colors(mapping)
            for k, v in derived.items():
                if k.startswith("ACCENT_") or k in self._locked:
                    continue
                if k in self._var_rows and self._var_rows[k].get("type") != "radius":
                    self._set_var_value(k, v)
        if apply_now:
            self.apply_theme()

    def _auto_derive_colors(self, mapping: dict[str, str]) -> dict[str, str]:
        # Helpers
        def is_dark(hexs: str) -> bool:
            c = QColor(hexs)
            return (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000 < 140

        def hex_of(c: QColor) -> str:
            return c.name()

        # contrast factor (0.5 … 2.0), default 1.0
        try:
            cf = float(mapping.get("CONTRAST_FACTOR", "1.0"))
        except Exception:
            cf = 1.0
        cf = max(0.5, min(2.0, cf))
        bg = mapping.get("BG", "#0f1115")
        card = mapping.get("CARD_BG", "#171a21")
        base = mapping.get("FIELD_BG", mapping.get("INPUT_BG", "#10131a"))
        fg = mapping.get("FG", "#e8ebf1")
        border = mapping.get("BORDER", "#2a2f3a")
        primary = mapping.get("PRIMARY", "#3b82f6")

        c_bg = _qc(bg)
        c_card = _qc(card)
        c_base = _qc(base)
        c_fg = _qc(fg)
        c_primary = _qc(primary)
        dark = is_dark(bg)

        # Surfaces: BG < CARD_BG < FIELD_BG  (for dark), reversed for light
        if dark:
            d_card = _mix(c_bg, QColor("#ffffff"), 0.06 * cf)
            d_base = _mix(d_card, c_bg, 0.35 * cf)
        else:
            d_card = _mix(c_bg, QColor("#000000"), 0.04 * cf)
            d_base = _mix(d_card, c_bg, 0.15 * cf)

        d_fg = (
            _mix(QColor("#ffffff"), c_bg, 0.15 * cf)
            if dark
            else _mix(QColor("#000000"), c_bg, 0.20 * cf)
        )
        d_border = (
            _mix(c_bg, QColor("#ffffff"), 0.18 * cf)
            if dark
            else _mix(c_bg, QColor("#000000"), 0.12 * cf)
        )

        d_alt = _mix(d_base, d_fg if dark else c_bg, 0.06 * cf)
        d_header = _mix(d_card, d_fg if dark else c_bg, 0.07 * cf)
        d_button = d_card
        d_sep = d_border

        p_light = _qc(hex_of(c_primary)).lighter(int(100 + round(20 * cf)))
        p_dark = _qc(hex_of(c_primary)).darker(int(100 + round(20 * cf)))
        on_p = QColor("#000000") if not is_dark(c_primary.name()) else QColor("#ffffff")

        return {
            "BG": hex_of(c_bg),
            "CARD_BG": hex_of(d_card),
            "FIELD_BG": hex_of(d_base),
            "INPUT_BG": hex_of(d_base),
            "FG": hex_of(d_fg),
            "BORDER": hex_of(d_border),
            "ALT_BG": hex_of(d_alt),
            "HEADER_BG": hex_of(d_header),
            "BUTTON_BG": hex_of(d_button),
            "SEPARATOR": hex_of(d_sep),
            "PRIMARY_LIGHT": p_light.name(),
            "PRIMARY_DARK": p_dark.name(),
            "ON_PRIMARY": on_p.name(),
            "CONTRAST_FACTOR": f"{cf:.2f}",
        }

    # ---------- apply ----------
    def apply_theme(self):
        try:
            template = self.qss_path.read_text(encoding="utf-8")
            mapping = self._gather_vars()

            # Ensure radius defaults exist so QSS placeholders are always resolved
            for k, v in DEFAULT_RADIUS.items():
                mapping.setdefault(k, v)

            # Check for PySide6QtAds and apply additional styles if available
            if importlib.util.find_spec("PySide6QtAds"):
                # Prefer theme_ads.qss next to selected QSS, fallback to package root
                ads_candidates = [
                    self.qss_path.parent / "theme_ads.qss",
                    SCRIPT_DIR / "theme_ads.qss",
                ]
                for ads_qss_path in ads_candidates:
                    if ads_qss_path.exists():
                        template += "\n" + ads_qss_path.read_text(encoding="utf-8")
                        break

            # Make sure theme name is exposed before rendering
            try:
                app = QApplication.instance()
                theme_name = self.theme_combo.currentText().strip()
                if app is not None and theme_name:
                    app.setProperty("theme", theme_name)
            except Exception:
                pass

            # Normalize aliases (INPUT_BG ↔ FIELD_BG)
            if "INPUT_BG" in mapping and "FIELD_BG" not in mapping:
                mapping["FIELD_BG"] = mapping["INPUT_BG"]
            if "FIELD_BG" in mapping:
                mapping["INPUT_BG"] = mapping["FIELD_BG"]

            # Apply auto-derivation (respects locks, leaves accents)
            mapping = self._mapping_with_auto_derived(mapping)

            # Build palette & stylesheet from the (possibly) derived mapping
            pal = build_palette_from_mapping(mapping)
            app = QApplication.instance()

            mapping = _augment_mapping_with_derived(mapping)
            qss = render_qss(mapping, template)

            # Reset stylesheet first so old rules don't linger
            try:
                if self._apply_target is None or isinstance(self._apply_target, QApplication):
                    app.setStyleSheet("")
                else:
                    self._apply_target.setStyleSheet("")
            except Exception:
                pass

            # Apply palette and then new stylesheet
            app.setPalette(pal)
            if self._apply_target is None or isinstance(self._apply_target, QApplication):
                app.setStyleSheet(qss)
            else:
                self._apply_target.setStyleSheet(qss)

            # Apply material icons programmatically using your icon engine (for buttons only)
            if hasattr(self, "_apply_material_icons_with_engine"):
                self._apply_material_icons_with_engine(mapping, template)

            # Sync PyQtGraph global/theme for existing and future plots so labels/axes recolor
            self._apply_pyqtgraph_theme(mapping)

        except Exception as e:
            QMessageBox.warning(self, "Apply Theme", f"Failed to apply theme:\n{e}")
            import traceback

            traceback.print_exc()

    def _apply_pyqtgraph_theme(self, mapping: dict) -> None:
        try:
            import pyqtgraph as pg
            from qtpy.QtWidgets import QApplication

            app = QApplication.instance()
            if app is None:
                return

            bg_dark = mapping.get("PLOT_BG", "#141414")
            fg_dark = mapping.get("PLOT_FG", "#e8ebf1")
            lbl_dark = mapping.get("PLOT_LABEL", "#FFFFFF")
            ax_dark = mapping.get("PLOT_AXIS", "#CCCCCC")

            bg_light = mapping.get("PLOT_BG_LIGHT", "#e9ecef")
            fg_light = mapping.get("PLOT_FG_LIGHT", "#141414")
            lbl_light = mapping.get("PLOT_LABEL_LIGHT", "#000000")
            ax_light = mapping.get("PLOT_AXIS_LIGHT", "#666666")

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

            graphic_layouts = [
                child
                for top in app.topLevelWidgets()
                for child in top.findChildren(pg.GraphicsLayoutWidget)
            ]

            plot_items = [
                item
                for gl in graphic_layouts
                for item in getattr(gl, "ci", None).items.keys()
                if getattr(gl, "ci", None)
                if isinstance(item, pg.PlotItem)
            ]

            histograms = [
                item
                for gl in graphic_layouts
                for item in getattr(gl, "ci", None).items.keys()
                if getattr(gl, "ci", None)
                if isinstance(item, pg.HistogramLUTItem)
            ]

            pg.setConfigOptions(foreground=foreground_color, background=background_color)

            for gl in graphic_layouts:
                try:
                    gl.setBackground(background_color)
                except Exception:
                    pass

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
                    try:
                        pi.titleLabel.setText(pi.titleLabel.text, color=label_color)
                    except Exception:
                        pass
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

            for h in histograms:
                try:
                    h.axis.setPen(pg.mkPen(color=axis_color))
                    h.axis.setTextPen(pg.mkPen(color=label_color))
                except Exception:
                    pass
        except Exception:
            pass


# ------------------------- Example app (independent) -------------------------


class ExampleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example App Window")
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        container = QFrame()
        container.setProperty("role", "card")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        title = QLabel("Live QSS Theme Demo")
        title.setProperty("role", "h1")

        r1 = QHBoxLayout()
        btn_primary = QPushButton("Primary Action")
        btn_primary.setObjectName("primary-action")
        btn_secondary = QPushButton("Secondary")
        r1.addWidget(btn_primary)
        r1.addWidget(btn_secondary)
        r1.addStretch(1)

        r2 = QHBoxLayout()
        line = QLineEdit()
        line.setPlaceholderText("Type to see focus/selection…")
        combo = QComboBox()
        combo.addItems(["Alpha", "Bravo", "Charlie", "Delta"])
        r2.addWidget(line, 2)
        r2.addWidget(combo, 1)

        r3 = QHBoxLayout()
        check = QCheckBox("Enable feature")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(42)
        r3.addWidget(check)
        r3.addWidget(slider, 1)

        lay.addWidget(title)
        lay.addLayout(r1)
        lay.addLayout(r2)
        lay.addLayout(r3)

        root.addWidget(container)


# ------------------------- Main -------------------------


def main():
    ensure_files()

    app = QApplication(sys.argv)

    # Independent example window (not part of the theme tool)
    demo = ExampleWindow()
    demo.setProperty("role", "app")
    demo.show()

    # Floating theming panel; attach app-wide so it can profile any running UI
    tool = ThemeWidget(qss_path=THEME_QSS_PATH, themes_dir=THEMES_DIR)
    tool.attach(target=None)  # None => application-wide apply
    tool.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
