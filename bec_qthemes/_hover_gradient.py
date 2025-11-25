"""Hover gradient effect helper usable on any QWidget."""

from __future__ import annotations

import re
import types

from qtpy import QtCore, QtGui, QtWidgets


class _HoverGradientFilter(QtCore.QObject):
    """Track hover/press state for a widget and trigger repaints."""

    def __init__(self, target: QtWidgets.QWidget):
        super().__init__(target)
        self._target = target
        target.destroyed.connect(self._on_dead)
        self._propagate_mouse_tracking(target)

    @QtCore.Slot()
    def _on_dead(self) -> None:
        """Target widget is gone → remove the filter."""
        self._target = None
        self.deleteLater()

    def _propagate_mouse_tracking(self, widget: QtWidgets.QWidget) -> None:
        """Ensure all descendants forward mouse move events."""
        for child in widget.findChildren(QtWidgets.QWidget):
            child.setMouseTracking(True)
            child.installEventFilter(self)
            self._propagate_mouse_tracking(child)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:  # noqa: N802
        if self._target is None:
            return False

        target = self._target
        event_type = event.type()

        if event_type == QtCore.QEvent.MouseMove:
            inside = target.rect().contains(target.mapFromGlobal(event.globalPos()))
            if inside:
                pos = target.mapFromGlobal(event.globalPos())
                if pos != getattr(target, "_hg_pos", QtCore.QPoint()):
                    target._hg_pos = pos
                    target.update()
                target._hg_hover = True
            elif getattr(target, "_hg_hover", False):
                target._hg_hover = False
                target.update()
        elif event_type == QtCore.QEvent.Enter:
            target._hg_hover, target._hg_pos = True, event.pos()
            target.update()
        elif event_type == QtCore.QEvent.Leave:
            target._hg_hover = False
            target.update()
        elif event_type == QtCore.QEvent.MouseButtonPress:
            target._hg_pressed = True
            target.update()
        elif event_type == QtCore.QEvent.MouseButtonRelease:
            target._hg_pressed = False
            target.update()

        return super().eventFilter(watched, event)


def _draw_hover_gradient(widget: QtWidgets.QWidget, painter: QtGui.QPainter, path, opacity: float):
    if not getattr(widget, "_hg_hover", False) or widget._hg_pos.x() < 0:
        return

    pressed = getattr(widget, "_hg_pressed", False)
    colours = getattr(widget, "_hg_cols", [QtGui.QColor("#ffffff")])
    accent = colours[0]

    radius = max(widget.width(), widget.height()) * (0.6 if pressed else 0.9)
    gradient = QtGui.QRadialGradient(widget._hg_pos, radius)

    centre = QtGui.QColor(accent)
    centre.setAlpha(opacity if pressed else opacity * 0.6)
    gradient.setColorAt(0.0, centre)

    edge = colours[1] if len(colours) > 1 else QtCore.Qt.transparent
    gradient.setColorAt(1.0, edge)

    painter.fillPath(path, gradient)


def _extract_border_radius(widget: QtWidgets.QWidget) -> int:
    """
    Try to read any border-radius that applies to the widget, including rules coming from
    global QSS (e.g. theme_base.qss). Not tied to the widget variant; we simply return the
    most specific (last) radius we can find.
    """
    sources = [widget.styleSheet()]

    app = QtWidgets.QApplication.instance()
    if app:
        sources.append(app.styleSheet())

    for source in sources:
        matches = re.findall(r"border-radius\s*:\s*([0-9]+)", source)
        if matches:
            # Take the last occurrence to respect later rules in the sheet
            return int(matches[-1])

    return 0


def enable_hover_gradient(widget: QtWidgets.QWidget, colours=None, opacity: float = 1.0) -> None:
    """
    Inject a radial hover gradient into any QWidget.

    Parameters
    ----------
    widget : QWidget
        The widget to enhance.
    colours : str | list[str] | None
        One colour → accent→transparent. Two colours → accent→edge.
    opacity : float
        Opacity multiplier in the range [0, 1].
    """
    if getattr(widget, "_hg_enabled", False):
        return

    opacity = 255 * opacity
    if colours is None:
        colours = ["#ffffff"]
    if isinstance(colours, str):
        colours = [colours]

    widget._hg_enabled = True
    widget._hg_cols = [QtGui.QColor(c) for c in colours]
    widget._hg_hover = False
    widget._hg_pressed = False
    widget._hg_pos = QtCore.QPoint(-1, -1)

    original_paint = widget.paintEvent

    def patched_paint(self, event):  # type: ignore[override]
        original_paint(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        radius = getattr(self, "_hg_radius", None)
        if radius is None:
            radius = _extract_border_radius(self)
            self._hg_radius = radius
        path = QtGui.QPainterPath()
        if radius > 0:
            path.addRoundedRect(self.rect().adjusted(0, 0, -1, -1), radius, radius)
        else:
            path.addRect(self.rect().adjusted(0, 0, -1, -1))

        _draw_hover_gradient(self, painter, path, opacity)
        painter.end()

    widget.paintEvent = types.MethodType(patched_paint, widget)
    widget._hg_orig_paint = original_paint

    hover_filter = _HoverGradientFilter(widget)
    widget._hg_filter = hover_filter
    widget.installEventFilter(hover_filter)

    widget.setAttribute(QtCore.Qt.WA_StyledBackground, True)
    widget.setMouseTracking(True)


__all__ = ["enable_hover_gradient"]
