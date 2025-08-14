from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import TYPE_CHECKING, Literal, overload

from qtpy.QtCore import QRect, QRectF, QSize
from qtpy.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPalette, QPixmap
from qtpy.QtSvg import QSvgRenderer

from bec_qthemes._color import Color
from bec_qthemes._icon.icon_engine import SvgIconEngine
from bec_qthemes._icon.svg_util import Svg

if TYPE_CHECKING:
    from qtpy.QtGui import QPixmap


@lru_cache()
def _material_icons() -> dict[str, str]:
    icons_file = (
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        + "/style/svg/all_material_icons.json"
    )
    with open(icons_file, "r", encoding="utf-8") as f:
        data = f.read()
        return json.loads(data)


@lru_cache()
def _material_icons_filled() -> dict[str, str]:
    icons_file = (
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        + "/style/svg/all_material_icons_filled.json"
    )
    with open(icons_file, "r", encoding="utf-8") as f:
        data = f.read()
        return json.loads(data)


class _MaterialIconSVG(Svg):
    def __init__(self, id: str, filled=False) -> None:
        """Initialize svg manager."""
        self._id = id
        self._color = None
        self._rotate = None

        if filled:
            if id not in _material_icons_filled():
                self._source = _material_icons()[id]
            else:
                self._source = _material_icons_filled()[id]
        else:
            self._source = _material_icons()[id]


class _MaterialIconEngine(SvgIconEngine):
    def __init__(self, svg: _MaterialIconSVG) -> None:
        """Initialize icon engine."""
        super().__init__(svg)
        self.color = None

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state):
        """Paint the icon int ``rect`` using ``painter``."""
        # Always rely on application palette to avoid legacy theme loader.
        palette = QGuiApplication.palette()

        if self.color is None:
            if mode == QIcon.Mode.Disabled:
                rgba = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text).getRgb()
                color = Color.from_rgba(*rgba)
            else:
                rgba = palette.text().color().getRgb()
                color = Color.from_rgba(*rgba)
        else:
            if isinstance(self.color, str):
                color = Color.from_hex(self.color)
            elif isinstance(self.color, dict):
                # Theme-aware dict not supported without theme manager; fall back to text color
                rgba = palette.text().color().getRgb()
                color = Color.from_rgba(*rgba)
            elif isinstance(self.color, tuple):
                color = Color.from_rgba(*self.color)
            elif isinstance(self.color, QColor):
                color = Color.from_rgba(
                    self.color.red(), self.color.green(), self.color.blue(), self.color.alpha()
                )
        if color is not None:
            self._svg.colored(color)

        svg_byte = str(self._svg).encode("utf-8")
        renderer = QSvgRenderer(svg_byte)  # type: ignore
        renderer.render(painter, QRectF(rect))


@overload
def material_icon(
    icon_name: str,
    size: tuple | QSize | None = None,
    color: str | tuple | QColor | dict[Literal["dark", "light"], str] | None = None,
    rotate=0,
    mode=None,
    filled=False,
    convert_to_pixmap=True,
) -> QPixmap: ...


@overload
def material_icon(
    icon_name: str,
    size: tuple | QSize | None = None,
    color: str | tuple | QColor | dict[Literal["dark", "light"], str] | None = None,
    rotate=0,
    mode=None,
    filled=False,
    convert_to_pixmap=False,
) -> QIcon: ...


def material_icon(
    icon_name: str,
    size: tuple | QSize | None = None,
    color: str | tuple | QColor | dict[Literal["dark", "light"], str] | None = None,
    rotate=0,
    mode=None,
    filled=False,
    convert_to_pixmap=True,
) -> QPixmap | QIcon:
    """
    Return a QPixmap or QIcon of a Material icon.

    Args:
        icon_name (str): The name of the Material icon.
            Check https://https://fonts.google.com/icons for the list of available icons.
        size (tuple | QSize | None, optional): The size of the icon. Defaults to None.
        color (str | tuple | QColor | None, optional): The color of the icon. Either a hex string, a tuple of RGB values, or a QColor.
            Defaults to None.
        rotate (int, optional): The rotation of the icon in degrees. Defaults to 0.
        mode ([type], optional): The mode of the icon. Defaults to None.
        filled (bool, optional): Whether to use the filled version of the icon. Defaults to False.
        convert_to_pixmap (bool, optional): Whether to convert the icon to a QPixmap. Defaults to True.

    Returns:
        QPixmap | QIcon
    """
    svg = _MaterialIconSVG(icon_name, filled)
    if rotate != 0:
        svg.rotate(rotate)

    icon = _MaterialIconEngine(svg)
    if color is not None:
        icon.color = color
    if not convert_to_pixmap:
        return QIcon(icon)

    if size is None:
        size = QSize(50, 50)
    elif isinstance(size, tuple):
        size = QSize(*size)

    return icon.pixmap(size, mode, state=None)


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication, QLabel

    app = QApplication([])
    label = QLabel()
    label.setPixmap(material_icon("palette", size=(200, 200), filled=False, color="#000000"))
    label.show()
    app.exec_()
