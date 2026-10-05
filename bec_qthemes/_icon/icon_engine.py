from qtpy.QtCore import QPoint, QRect, QRectF, QSize, Qt
from qtpy.QtGui import QGuiApplication, QIcon, QIconEngine, QImage, QPainter, QPalette, QPixmap
from qtpy.QtSvg import QSvgRenderer

from bec_qthemes._color import Color
from bec_qthemes._icon.svg_util import Svg


def icon_from_engine(engine: QIconEngine) -> QIcon:
    """
    Create a QIcon from a Python icon engine that is safe to keep in reference cycles.

    ``QIcon(engine)`` makes the engine a shiboken child of that particular Python ``QIcon``
    wrapper, while the C++ ``QIcon`` owns the engine and deletes it with the last icon copy.
    If the wrapper and its engine end up in cyclic garbage (e.g. an icon cached on a widget
    that is collected by the GC), the collector may clear the engine first. Shiboken then
    detaches it from its parent and hands its ownership back to Python, so the C++ engine is
    deleted while the ``QIcon`` still points to it, and destroying the ``QIcon`` afterwards
    crashes the interpreter (segfault in the ``QIcon`` destructor).

    Returning a copy and dropping the wrapper created with the engine right away leaves the
    engine to the C++ side only: shiboken keeps the Python engine alive, outside the GC's view,
    until the last ``QIcon`` sharing it deletes the engine.

    Args:
        engine (QIconEngine): The engine to wrap. It must not be used directly afterwards.

    Returns:
        QIcon: An icon that renders through ``engine``.
    """
    owner = QIcon(engine)
    icon = QIcon(owner)
    del owner  # releases the parent/child link; the engine now lives as long as the C++ icons
    return icon


class SvgIconEngine(QIconEngine):
    """A custom QIconEngine that can render an SVG buffer."""

    def __init__(self, svg: Svg) -> None:
        """Initialize icon engine."""
        super().__init__()
        self._svg = svg

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state):
        """Paint the icon int ``rect`` using ``painter``."""
        palette = QGuiApplication.palette()

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

    def clone(self):
        """Required to subclass abstract QIconEngine."""
        return SvgIconEngine(self._svg)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State):
        """Return the icon as a pixmap with requested size, mode, and state."""
        # Make size to square.
        min_size = min(size.width(), size.height())
        size.setHeight(min_size)
        size.setWidth(min_size)

        img = QImage(size, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        pixmap = QPixmap.fromImage(img, Qt.ImageConversionFlag.NoFormatConversion)
        size.width()
        self.paint(QPainter(pixmap), QRect(QPoint(0, 0), size), mode, state)
        return pixmap
