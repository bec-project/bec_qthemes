"""A module containing multiple filters used by template engine."""

from __future__ import annotations

import platform
from pathlib import Path
import re

from qtpy.QtCore import qVersion, QCoreApplication
from qtpy.QtGui import QColor

# from bec_qthemes import __version__  # unused; cache version resolved from pyproject
from bec_qthemes._util import (
    analyze_version_str,
    get_cash_root_path,
    get_logger,
    get_project_version_from_pyproject,
)

_logger = get_logger(__name__)

# Resolve project version from pyproject.toml for cache names
_PROJECT_VERSION = get_project_version_from_pyproject()


def _sanitize_key(name: str) -> str:
    """Return a filesystem-safe key (lowercase, spaces -> -, strip invalid)."""
    name = name.strip().lower()
    # replace spaces with hyphen, then collapse invalid chars to underscore
    name = name.replace(" ", "-")
    name = re.sub(r"[^a-z0-9._-]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_.-")
    return name or "default"


def _get_theme_cache_key() -> str:
    """Return a short theme key for cache directory segregation.

    Attempts to read a dynamic application property set during setup_theme() or QSS editor.
    Falls back to "dark" when not available (e.g., during tests without a QApplication).
    """
    try:
        app = QCoreApplication.instance()
        if app is not None:
            val = app.property("theme")
            if isinstance(val, str) and val:
                return _sanitize_key(val)
    except Exception:
        pass
    return "dark"


_PATH_MEMO: dict[str, str] = {}


def _apply_color_and_rotate(svg_data: str, color: str | None, rotate: int) -> str:
    """Helper to apply color and rotation to raw SVG data."""
    # Using XML parser for a more robust implementation.
    import xml.etree.ElementTree as ET

    try:
        svg_data = re.sub(r'\sxmlns="[^"]+"', "", svg_data, count=1)
        root = ET.fromstring(svg_data)

        if color:
            root.set("fill", color)

        if rotate:
            transform = root.get("transform", "")
            # remove existing rotate
            transform = re.sub(r"rotate\s*\([^)]+\)", "", transform).strip()
            new_rotate = f"rotate({rotate}, 12, 12)"
            if transform:
                transform = f"{transform} {new_rotate}"
            else:
                transform = new_rotate
            root.set("transform", transform)

        # ET.tostring returns bytes, so we decode it.
        return ET.tostring(root, encoding="unicode")
    except ET.ParseError as e:
        _logger.warning(f"Could not parse SVG with XML parser: {e}. Falling back to regex.")
        # Fallback to regex for SVGs that the XML parser can't handle
        if color:
            if 'fill="' in svg_data:
                svg_data = re.sub(r'fill=".*?"', f'fill="{color}"', svg_data)
            else:
                svg_data = svg_data.replace("<svg ", f'<svg fill="{color}" ', 1)
        if rotate:
            transform_attr = f'transform="rotate({rotate}, 12, 12)"'
            if 'transform="' in svg_data:
                svg_data = re.sub(r'transform=".*?"', transform_attr, svg_data)
            else:
                svg_data = svg_data.replace("<svg ", f"<svg {transform_attr} ", 1)
        return svg_data


qt_version = qVersion()

if qt_version is None:
    # If Qt version can't be detected at runtime, use a high version to keep feature flags enabled.
    _logger.warning("Failed to detect Qt version. Load Qt version as the latest version.")
    _QT_VERSION = "10.0.0"  # Fairly future version for always setting latest version.
else:
    _QT_VERSION = qt_version

try:
    from qtpy import QT_API

    _QT_API = QT_API
except ImportError:
    _QT_API = "unknown"

# Import the material_icon function lazily to avoid circular imports
_material_icon = None
_MATERIAL_ICONS_AVAILABLE = None


def _get_material_icon():
    global _material_icon, _MATERIAL_ICONS_AVAILABLE
    if _MATERIAL_ICONS_AVAILABLE is None:
        try:
            from bec_qthemes._icon.material_icons import material_icon

            _material_icon = material_icon
            _MATERIAL_ICONS_AVAILABLE = True
        except ImportError:
            _material_icon = None
            _MATERIAL_ICONS_AVAILABLE = False
    return _material_icon


def _transform(color, color_state: dict[str, float]):
    """Transform color based on state (avoiding circular imports)."""
    # Simple color transformation without importing Color class
    c = QColor(color) if isinstance(color, str) else color
    if not c.isValid():
        return "#000000"

    if color_state.get("transparent"):
        alpha = int(255 * (1 - color_state["transparent"]))
        c.setAlpha(alpha)
    if color_state.get("darken"):
        c = c.darker(int(100 + color_state["darken"] * 100))
    if color_state.get("lighten"):
        c = c.lighter(int(100 + color_state["lighten"] * 100))
    return c.name()


def color(color_info: str | dict[str, str | dict], state: str | None = None):
    """Filter for template engine. This filter convert color info data to color object."""
    if isinstance(color_info, str):
        return color_info  # Return as string for QSS usage

    base_color_format: str = color_info["base"]  # type: ignore

    if state is None:
        return base_color_format

    transforms = color_info[state]
    return transforms if isinstance(transforms, str) else _transform(base_color_format, transforms)


def palette_format(color_val) -> str:
    """Filter for template engine. This filter convert color to ARGB hex format."""
    if isinstance(color_val, str):
        c = QColor(color_val)
        if c.isValid():
            return f"#{c.red():02x}{c.green():02x}{c.blue():02x}{c.alpha():02x}"
    return str(color_val)


def url(color_val, id: str, rotate: int = 0) -> str:
    """Filter for template engine. This filter create url for svg and output svg file.

    Generates an SVG file in cache from built-in SVG resources with the given color and rotation,
    and returns a url() to that SVG. No PNG buffer is used.
    """
    try:
        color_str = str(color_val) if color_val is not None else None

        # Early: compute destination path and return immediately if present (skip heavy work)
        theme_key = _get_theme_cache_key()
        cache_dir = get_cash_root_path(_PROJECT_VERSION) / theme_key / "svg_cache"
        color_part = (color_str or "auto").replace("#", "").replace("/", "_").replace(":", "_")
        filename = f"{id}_{color_part}_{int(rotate or 0)}.svg"
        svg_path = cache_dir / filename
        memo_key = f"svg:{theme_key}:{filename}"
        memo_val = _PATH_MEMO.get(memo_key)
        if memo_val:
            return f"url({memo_val})"
        if svg_path.exists():
            # memoize and return
            path_str = svg_path.as_posix()
            _PATH_MEMO[memo_key] = path_str
            return f"url({path_str})"

        # Load built-in svg resource map only when needed
        from bec_qthemes._icon.svg_util import Svg
        from bec_qthemes._color import Color

        try:
            svg = Svg(id)
            if color_str:
                svg.colored(Color(color_str))
            if rotate:
                svg.rotate(rotate)
            svg_data = str(svg)
        except KeyError:
            _logger.error(f"Unknown SVG resource id: {id}")
            return ""

        # Ensure parent and write file, record memo
        cache_dir.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(svg_data, encoding="utf-8")
        path_str = svg_path.as_posix()
        _PATH_MEMO[memo_key] = path_str
        return f"url({path_str})"
    except Exception as e:
        _logger.error(f"Error generating url() SVG for id={id}: {e}")
        return ""


def env(
    text, value: str, version: str | None = None, qt: str | None = None, os: str | None = None
) -> str:
    """Filter for template engine. This filter output empty string when unexpected environment."""
    if version and not analyze_version_str(_QT_VERSION, version):
        return ""
    if qt and qt.lower() != _QT_API.lower():
        return ""
    if os and platform.system().lower() not in os.lower():
        return ""
    return value.replace("${}", str(text))


def corner(corner_shape: str, size: str) -> str:
    """Filter for template engine. This filter manage corner shape."""
    return size if corner_shape == "rounded" else "0"


# --- New SVG-based material icon pipeline (no PNG buffer) ---


# Module-level caches for material icon JSON data
_ICONS_DATA: dict | None = None
_ICONS_FILLED_DATA: dict | None = None


def _load_icons_json() -> tuple[dict, dict]:
    """Load material icons JSON once and cache in memory."""
    global _ICONS_DATA, _ICONS_FILLED_DATA
    if _ICONS_DATA is not None and _ICONS_FILLED_DATA is not None:
        return _ICONS_DATA, _ICONS_FILLED_DATA
    import json
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    icons_file = os.path.join(base_dir, "style", "svg", "all_material_icons.json")
    icons_filled_file = os.path.join(base_dir, "style", "svg", "all_material_icons_filled.json")
    with open(icons_file, "r", encoding="utf-8") as f:
        _ICONS_DATA = json.loads(f.read())
    try:
        with open(icons_filled_file, "r", encoding="utf-8") as f:
            _ICONS_FILLED_DATA = json.loads(f.read())
    except Exception:
        _ICONS_FILLED_DATA = {}
    return _ICONS_DATA, _ICONS_FILLED_DATA


def material_icon_url(icon_name: str | int | float, **kwargs) -> str:
    """
    Generate a material icon directly as an SVG file (no PNG buffer) from the up-to-date JSON,
    and return its file path wrapped in url() for QSS usage.

    Usage in QSS templates:
    {{ "home" | material_icon_url(size="24,24", color=FG) }}
    {{ "settings" | material_icon_url(size="32,32", filled=true) }}
    {{ icon_name | material_icon_url(size="16,16", color=PRIMARY) }}

    Args:
        icon_name: The material icon name (string)
        size: Icon size as "width,height" string (default: "24,24"). For SVG this sets width/height attrs.
        color: Color as hex/rgba string resolved by the template engine (optional)
        filled: Whether to use filled version (default: false)
        rotate: Rotation in degrees (default: 0)

    Returns:
        File path wrapped in url() for use in QSS
    """
    if not isinstance(icon_name, str):
        _logger.error(f"Icon name must be a string, got {type(icon_name)}")
        return ""

    # Parse parameters
    size_str = kwargs.get("size", "24,24")
    color_str = kwargs.get("color", None)
    filled = str(kwargs.get("filled", "false")).lower() == "true"
    rotate = int(kwargs.get("rotate", 0))

    # Parse size
    try:
        width, height = map(int, str(size_str).split(","))
    except Exception:
        width, height = 24, 24

    try:
        # Early: compute destination path and return immediately if present (skip heavy work)
        theme_key = _get_theme_cache_key()
        color_part = (
            (str(color_str) if color_str else "auto")
            .replace("#", "")
            .replace("/", "_")
            .replace(":", "_")
        )
        filename = f"{icon_name}_{width}x{height}_{color_part}_{filled}_{rotate}.svg"
        cache_dir = get_cash_root_path(_PROJECT_VERSION) / theme_key / "material_icons_svg"
        file_path = cache_dir / filename
        memo_key = f"mi:{theme_key}:{filename}"
        memo_val = _PATH_MEMO.get(memo_key)
        if memo_val:
            return f"url({memo_val})"
        if file_path.exists():
            path_str = file_path.as_posix()
            _PATH_MEMO[memo_key] = path_str
            return f"url({path_str})"

        # Load material icons data from in-memory cache
        icons_data, icons_filled_data = _load_icons_json()

        # Select icon data
        if filled and icon_name in icons_filled_data:
            svg_data = icons_filled_data.get(icon_name) or icons_data[icon_name]
        else:
            svg_data = icons_data[icon_name]

        # Normalize and enforce width/height attributes on the root <svg>
        import re

        if re.search(r'\swidth="[^"]*"', svg_data):
            svg_data = re.sub(r'\swidth="[^"]*"', f' width="{width}"', svg_data, count=1)
        else:
            svg_data = svg_data.replace("<svg ", f'<svg width="{width}" ', 1)
        if re.search(r'\sheight="[^"]*"', svg_data):
            svg_data = re.sub(r'\sheight="[^"]*"', f' height="{height}"', svg_data, count=1)
        else:
            svg_data = svg_data.replace("<svg ", f'<svg height="{height}" ', 1)

        # Apply color and rotation
        svg_data = _apply_color_and_rotate(
            svg_data, color=str(color_str) if color_str else None, rotate=rotate
        )

        # Write out and memoize
        cache_dir.mkdir(parents=True, exist_ok=True)
        file_path.write_text(svg_data, encoding="utf-8")
        path_str = file_path.as_posix()
        _PATH_MEMO[memo_key] = path_str
        return f"url({path_str})"

    except Exception as e:
        _logger.error(f"Error generating material icon {icon_name} as SVG: {e}")
        import traceback

        traceback.print_exc()
        return ""


def material_icon_path(icon_name: str | int | float, **kwargs) -> str:
    """
    Generate a material icon and return its file path (without url() wrapper).

    Similar to material_icon_url but returns just the path for other use cases.
    """
    url_result = material_icon_url(icon_name, **kwargs)
    if url_result.startswith("url(") and url_result.endswith(")"):
        return url_result[4:-1]  # Remove url() wrapper
    return url_result
