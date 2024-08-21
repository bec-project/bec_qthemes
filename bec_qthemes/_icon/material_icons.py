from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import TYPE_CHECKING

from qtpy.QtCore import QPoint, QRect, QRectF, QSize, Qt
from qtpy.QtGui import QColor, QGuiApplication, QIcon, QImage, QPainter, QPalette, QPixmap
from qtpy.QtSvg import QSvgRenderer

from bec_qthemes._color import Color
from bec_qthemes._icon.icon_engine import SvgIconEngine
from bec_qthemes._icon.svg import Svg

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


class _MaterialIconSVG(Svg):
    def __init__(self, id: str) -> None:
        """Initialize svg manager."""
        self._id = id
        self._color = None
        self._rotate = None
        self._source = _material_icons()[self._id]


class _MaterialIconEngine(SvgIconEngine):
    def paint(
        self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state, color: Color | None = None
    ):
        """Paint the icon int ``rect`` using ``painter``."""
        palette = QGuiApplication.palette()

        if color is None:
            if mode == QIcon.Mode.Disabled:
                rgba = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text).getRgb()
                color = Color.from_rgba(*rgba)
            else:
                rgba = palette.text().color().getRgb()
                color = Color.from_rgba(*rgba)
        self._svg.colored(color)

        svg_byte = str(self._svg).encode("utf-8")
        renderer = QSvgRenderer(svg_byte)  # type: ignore
        renderer.render(painter, QRectF(rect))

    def pixmap(
        self, size: QSize, mode: QIcon.Mode, state: QIcon.State, color: Color | None = None
    ) -> QPixmap:
        """Return the icon as a pixmap with requested size, mode, and state."""
        # Make size to square.
        min_size = min(size.width(), size.height())
        size.setHeight(min_size)
        size.setWidth(min_size)

        img = QImage(size, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        pixmap = QPixmap.fromImage(img, Qt.ImageConversionFlag.NoFormatConversion)
        size.width()
        self.paint(QPainter(pixmap), QRect(QPoint(0, 0), size), mode, state, color)
        return pixmap


def material_icon(
    icon_name: str,
    size: tuple | QSize | None = None,
    color: str | tuple | QColor | None = None,
    rotate=0,
    mode=None,
    state=None,
) -> QPixmap:
    """
    Return a QPixmap of a Material icon.

    Args:
        icon_name (str): The name of the Material icon.
            Check https://https://fonts.google.com/icons for the list of available icons.
        size (tuple | QSize | None, optional): The size of the icon. Defaults to None.
        color (str | tuple | QColor | None, optional): The color of the icon. Either a hex string, a tuple of RGB values, or a QColor.
            Defaults to None.
        rotate (int, optional): The rotation of the icon in degrees. Defaults to 0.
        mode ([type], optional): The mode of the icon. Defaults to None.
        state ([type], optional): The state of the icon. Defaults
            to None.

    Returns:
        QPixmap: The icon as a QPixmap

    Examples:
        >>> label = QLabel()
        >>> label.setPixmap(material_icon("point_scan", size=(200, 200), rotate=10))
    """
    svg = _MaterialIconSVG(icon_name)
    if color is not None:
        if isinstance(color, str):
            color = Color.from_hex(color)
        elif isinstance(color, tuple):
            color = Color.from_rgba(*color)
        elif isinstance(color, QColor):
            color = Color.from_rgba(color.red(), color.green(), color.blue(), color.alpha())
    if rotate != 0:
        svg.rotate(rotate)

    icon = _MaterialIconEngine(svg)
    if size is None:
        size = QSize(50, 50)
    elif isinstance(size, tuple):
        size = QSize(*size)

    return icon.pixmap(size, mode, state, color=color)


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication, QLabel

    app = QApplication([])
    label = QLabel()
    label.setPixmap(material_icon("point_scan", size=(200, 200), rotate=10))
    label.show()
    app.exec_()
