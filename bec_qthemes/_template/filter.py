"""A module containing multiple filters used by template engine."""

from __future__ import annotations

import platform

from qtpy.QtCore import qVersion

from bec_qthemes import __version__
from bec_qthemes._color import Color
from bec_qthemes._icon.svg import Svg
from bec_qthemes._util import analyze_version_str, get_cash_root_path, get_logger

_logger = get_logger(__name__)

qt_version = qVersion()

if qt_version is None:
    _logger.warning("Failed to detect Qt version. Load Qt version as the latest version.")
    _QT_VERSION = "10.0.0"  # Fairly future version for always setting latest version.
else:
    _QT_VERSION = qt_version


def _transform(color: Color, color_state: dict[str, float]) -> Color:
    if color_state.get("transparent"):
        color = color.transparent(color_state["transparent"])
    if color_state.get("darken"):
        color = color.darken(color_state["darken"])
    if color_state.get("lighten"):
        return color.lighten(color_state["lighten"])
    return color


def color(color_info: str | dict[str, str | dict], state: str | None = None) -> Color:
    """Filter for template engine. This filter convert color info data to color object."""
    if isinstance(color_info, str):
        return Color.from_hex(color_info)

    base_color_format: str = color_info["base"]  # type: ignore
    color = Color.from_hex(base_color_format)

    if state is None:
        return color

    transforms = color_info[state]
    return (
        Color.from_hex(transforms) if isinstance(transforms, str) else _transform(color, transforms)
    )


def palette_format(color: Color) -> str:
    """Filter for template engine. This filter convert color object to ARGB hex format.

    QPalette parser for hex only support ARGB hex format. color.Color class use RGB hex format.
    So we need to convert Color object to ARGB hex format.
    """
    return f"#{color.to_hex_argb()}"


def url(color: Color, id: str, rotate: int = 0) -> str:
    """Filter for template engine. This filter create url for svg and output svg file."""
    svg_path = get_cash_root_path(__version__) / f"{id}_{color._to_hex()}_{rotate}.svg"
    url = f"url({svg_path.as_posix()})"
    if svg_path.exists():
        return url
    svg = Svg(id).colored(color).rotate(rotate)
    svg_path.write_text(str(svg))
    return url


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
