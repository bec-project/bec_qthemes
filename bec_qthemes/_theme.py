from __future__ import annotations

from qtpy.QtCore import Property, QObject, Signal
from qtpy.QtGui import QColor

ACCENT_COLORS = {
    "light": {
        "ACCENT_DEFAULT": "#0a60ff",
        "ACCENT_HIGHLIGHT": "#B53565",
        "ACCENT_WARNING": "#EAC435",
        "ACCENT_EMERGENCY": "#CC181E",
        "ACCENT_SUCCESS": "#2CA58D",
    },
    "dark": {
        "ACCENT_DEFAULT": "#8ab4f7",
        "ACCENT_HIGHLIGHT": "#B53565",
        "ACCENT_WARNING": "#EAC435",
        "ACCENT_EMERGENCY": "#CC181E",
        "ACCENT_SUCCESS": "#2CA58D",
    },
}


class AccentColors:
    def __init__(self, colors: dict[str, QColor]) -> None:
        self._colors = colors

    @property
    def default(self) -> QColor:
        """
        The default palette color for the accent.
        """
        return self._colors.get("ACCENT_DEFAULT", QColor("#000000"))

    @property
    def highlight(self) -> QColor:
        """
        The highlight color, which is used for normal accent without any specific meaning.
        """
        return self._colors.get("ACCENT_HIGHLIGHT", QColor("#000000"))

    @property
    def warning(self) -> QColor:
        """
        The warning color, which is used for warning accent.
        """
        return self._colors.get("ACCENT_WARNING", QColor("#000000"))

    @property
    def emergency(self) -> QColor:
        """
        The emergency color, which is used for emergency accent. This color should only be used for critical situations.
        """
        return self._colors.get("ACCENT_EMERGENCY", QColor("#000000"))

    @property
    def success(self) -> QColor:
        """
        The success color, which is used for success accent.
        """
        return self._colors.get("ACCENT_SUCCESS", QColor("#000000"))


class Theme(QObject):
    """A class to hold theme information."""

    theme_changed = Signal(str)

    def __init__(self, theme: str, colors: dict[str, str], parent=None):
        super().__init__(parent)
        self._theme = theme
        self._colors = {k: QColor(v) for k, v in colors.items()}
        self.accent_colors = AccentColors(self._colors)

    def change_theme(self, theme: str, colors: dict[str, str]) -> None:
        """Change the theme and its colors."""
        self._theme = theme
        self._colors = {k: QColor(v) for k, v in colors.items()}
        self.accent_colors = AccentColors(self._colors)
        self.theme_changed.emit(theme)

    @Property(str, notify=theme_changed)
    def theme(self) -> str:
        """The name of the theme."""
        return self._theme

    def color(self, key: str, fallback: str = "#000000") -> QColor:
        """Get a color from the theme by key."""
        return self._colors.get(key, QColor(fallback))

    def __getitem__(self, key: str) -> QColor:
        """Get a color from the theme by key."""
        return self.color(key)

    @Property("QVariantMap", notify=theme_changed)
    def colors(self) -> dict[str, QColor]:
        """A map of all colors in the theme."""
        return self._colors
