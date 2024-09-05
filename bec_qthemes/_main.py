from __future__ import annotations

import atexit
import os
import platform
from typing import Literal

import darkdetect
from qtpy.QtCore import QObject, Signal
from qtpy.QtGui import QColor

from bec_qthemes._style_loader import load_palette, load_stylesheet

_listener = None
_proxy_style = None


ACCENT_COLORS = {
    "light": {
        "highlight": "#B53565",
        "warning": "#EAC435",
        "emergency": "#CC181E",
        "success": "#2CA58D",
    },
    "dark": {
        "highlight": "#B53565",
        "warning": "#EAC435",
        "emergency": "#CC181E",
        "success": "#2CA58D",
    },
}


class AccentColors:
    def __init__(self, theme: str) -> None:
        self.theme = theme
        self._accents = ACCENT_COLORS[theme]
        self._palette = load_palette(theme)

    @property
    def default(self) -> QColor:
        """
        The default palette color for the accent.
        """
        return self._palette.accent().color()

    @property
    def highlight(self) -> QColor:
        """
        The highlight color, which is used for normal accent without any specific meaning.
        """
        return QColor(self._accents["highlight"])

    @property
    def warning(self) -> QColor:
        """
        The warning color, which is used for warning accent.
        """
        return QColor(self._accents["warning"])

    @property
    def emergency(self) -> QColor:
        """
        The emergency color, which is used for emergency accent. This color should only be used for critical situations.
        """
        return QColor(self._accents["emergency"])

    @property
    def success(self) -> QColor:
        """
        The success color, which is used for success accent.
        """
        return QColor(self._accents["success"])


class ThemeSignal(QObject):
    theme_updated = Signal(str)


class ThemeContainer:
    """
    The theme container class.
    """

    def __init__(self, theme: Literal["auto", "dark", "light"]) -> None:
        self._default_theme = "dark"
        self.mode = "auto" if theme == "auto" else "manual"
        self.theme = theme if theme != "auto" else None

    def __getitem__(self, key):
        # backward compatibility
        return getattr(self, key)

    @property
    def theme(self) -> str:
        """
        The theme name. There are `dark`, `light` and `auto`.
        """
        if self.mode == "auto" and self._theme is None:
            self._theme = self._get_default_theme()
        return self._theme

    @theme.setter
    def theme(self, theme: Literal["auto", "dark", "light"]):
        """
        The theme name. There are `dark`, `light` and `auto`.
        """
        self._theme = theme
        self._accents = AccentColors(self.theme)

    def _get_default_theme(self) -> str:
        """
        Get the default theme. On macOS, it will return the system theme when the mode is auto.
        """
        if platform.system() == "Darwin" and self.mode == "auto":
            return darkdetect.theme().lower() or self._default_theme
        return self._default_theme

    @property
    def accent_colors(self) -> AccentColors:
        """
        The accent colors. The colors are different depending on the theme and are set
        when changing the theme.
        """
        return self._accents


def _apply_style(app, additional_qss: str | None, **kargs) -> None:
    from bec_qthemes._proxy_style import qthemesStyle

    stylesheet = load_stylesheet(**kargs)
    if additional_qss is not None:
        stylesheet += additional_qss
    app.setStyleSheet(stylesheet)

    app.setPalette(
        load_palette(
            kargs["theme"],
            kargs["custom_colors"],
            for_stylesheet=True,
            default_theme=kargs["default_theme"],
        )
    )

    global _proxy_style
    if _proxy_style is None:
        _proxy_style = qthemesStyle()
        app.setStyle(_proxy_style)


def _sync_theme_with_system(app, callback) -> None:
    from bec_qthemes._os_appearance import listener

    global _listener
    if _listener is not None:
        _listener.sig_run.emit(True)
        return

    _listener = listener.OSThemeSwitchListener(callback)

    if platform.system() == "Darwin":
        app.installEventFilter(_listener)
    else:
        atexit.register(_listener.kill)
        _listener.start()


def enable_hi_dpi() -> None:
    """Allow to HiDPI.

    This function must be set before instantiation of QApplication..
    For Qt6 bindings, HiDPI “just works” without using this function.
    """
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QGuiApplication

    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)  # type: ignore
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)  # type: ignore
    if hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )


def stop_sync() -> None:
    """Stop sync with system theme."""
    from qtpy.QtCore import QCoreApplication

    app = QCoreApplication.instance()
    global _listener
    if not app or not _listener:
        return
    _listener.sig_run.emit(False)


def setup_theme(
    theme: str = "dark",
    corner_shape: str = "rounded",
    custom_colors: dict[str, str | dict[str, str]] | None = None,
    additional_qss: str | None = None,
    *,
    default_theme: str = "dark",
    install_event_filter: bool = True,
) -> None:
    """Apply the theme which looks like flat design to the Qt App completely.

    This function applies the complete style to your Qt application. If the argument theme is ``auto``,
    try to listen to changes to the OS's theme and switch the application theme accordingly.

    Args:
        theme: The theme name. There are `dark`, `light` and `auto`.
            If ``auto``, try to sync with your OS's theme and accent (accent is only on Mac).
            If failed to detect OS's theme, use the default theme set in argument ``default_theme``.
            When primary color(``primary``) or primary child colors
            (such as ``primary>selection.background``) are set to custom_colors,
            disable to sync with the accent.
        corner_shape: The corner shape. There are `rounded` and `sharp` shape.
        custom_colors: The custom color map. Overrides the default color for color id you set.
            Also you can customize a specific theme only. See example 5.
        additional_qss: Additional stylesheet text. You can add your original stylesheet text.
        default_theme: The default theme name.
            The theme set by this argument will be used when system theme detection fails.

    Raises:
        ValueError: If the argument is wrong.
        KeyError: If the color id of custom_colors is wrong.

    Returns:
        The stylesheet string for the given arguments.

    Examples:
        Set stylesheet to your Qt application.

        1. Setup style and sync to system theme ::

            app = QApplication([])
            qthemes.setup_theme()

        2. Use Dark Theme ::

            app = QApplication([])
            qthemes.setup_theme("dark")

        3. Sharp corner ::

            # Change corner shape to sharp.
            app = QApplication([])
            qthemes.setup_theme(corner_shape="sharp")

        4. Customize color ::

            app = QApplication([])
            qthemes.setup_theme(custom_colors={"primary": "#D0BCFF"})

        5. Customize a specific theme only ::

            app = QApplication([])
            qthemes.setup_theme(
                theme="auto",
                custom_colors={
                    "[dark]": {
                        "primary": "#D0BCFF",
                    }
                },
            )
    """
    from qtpy.QtCore import QCoreApplication

    app = QCoreApplication.instance()
    if not app:
        raise Exception("setup_theme() must be called after instantiation of QApplication.")
    if theme != "auto":
        stop_sync()
    app.setProperty("_qthemes_use_setup_style", True)

    app.theme = ThemeContainer(theme)

    if not hasattr(app, "theme_signal"):
        app.theme_signal = ThemeSignal()

    def callback():
        _apply_style(
            app,
            additional_qss,
            theme=theme,
            corner_shape=corner_shape,
            custom_colors=custom_colors,
            default_theme=default_theme,
        )

    callback()

    if not install_event_filter:
        return

    if theme == "auto" and darkdetect.theme() is not None:
        _sync_theme_with_system(app, callback)
