"""Lifetime of the Python icon engine behind ``material_icon(..., convert_to_pixmap=False)``."""

import gc
import os
import subprocess
import sys
import textwrap

import pytest
from qtpy.QtCore import QSize
from qtpy.QtGui import QColor, QIcon

from bec_qthemes import material_icon
from bec_qthemes._icon.material_icons import _MaterialIconEngine

# Icons are created before the dict that holds them, so the GC visits each engine before its
# QIcon and before the dict when the holder becomes cyclic garbage. Without the fix the engine's
# C++ object is deleted first and destroying the QIcon afterwards segfaults.
_CYCLIC_GARBAGE_SCRIPT = textwrap.dedent("""
    import faulthandler
    import gc
    import os

    faulthandler.enable(all_threads=False)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from qtpy.QtWidgets import QApplication, QPushButton

    from bec_qthemes import material_icon

    app = QApplication([])


    class Holder:
        pass


    icons = [material_icon("database", convert_to_pixmap=False) for _ in range(20)]
    holder = Holder()
    holder.icons = dict(enumerate(icons))
    holder.cycle = holder
    button = QPushButton()
    button.setIcon(holder.icons[0])
    del icons, holder
    gc.collect()
    button.deleteLater()
    app.processEvents()
    print("collected", flush=True)
    """)


def test_material_icon_in_cyclic_garbage_does_not_crash():
    """Collecting icons that sit in a reference cycle must not crash the interpreter."""
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    proc = subprocess.run(
        [sys.executable, "-c", _CYCLIC_GARBAGE_SCRIPT],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    assert (
        proc.returncode == 0 and "collected" in proc.stdout
    ), f"child exited with {proc.returncode}\n{proc.stdout[-2000:]}\n{proc.stderr[:4000]}"


def _engine_count() -> int:
    gc.collect()
    return sum(1 for obj in gc.get_objects() if isinstance(obj, _MaterialIconEngine))


def test_material_icon_engine_lives_as_long_as_the_icon(qapp):
    """The engine keeps painting after the factory returned and is released with the icon."""
    before = _engine_count()
    icon = material_icon("database", color="#ff0000", convert_to_pixmap=False)
    assert isinstance(icon, QIcon)
    assert _engine_count() == before + 1

    image = icon.pixmap(QSize(24, 24)).toImage()
    colors = {image.pixelColor(x, y).name() for x in range(24) for y in range(24)}
    assert QColor("#ff0000").name() in colors

    copy = QIcon(icon)
    del icon
    assert _engine_count() == before + 1  # still shared by the copy
    assert not copy.pixmap(QSize(24, 24)).isNull()

    del copy
    assert _engine_count() == before


# Qt calls ``QIconEngine.clone()`` when a shared QIcon detaches and takes ownership of the
# returned engine. Without handing it over to Qt, Python deleted the clone right away and the
# following call on the detached icon segfaulted.
_DETACH_SCRIPT = textwrap.dedent("""
    import faulthandler
    import gc
    import os
    import sys

    faulthandler.enable(all_threads=False)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from qtpy.QtCore import QSize
    from qtpy.QtGui import QColor, QIcon, QPixmap
    from qtpy.QtWidgets import QApplication

    from bec_qthemes import material_icon
    from bec_qthemes._icon import icon_engine
    from bec_qthemes._icon.material_icons import _MaterialIconEngine

    app = QApplication([])


    def has_red(icon):
        image = icon.pixmap(QSize(24, 24)).toImage()
        red = QColor("#ff0000").name()
        return any(image.pixelColor(x, y).name() == red for x in range(24) for y in range(24))


    def live_clones():
        gc.collect()
        return [e for e in icon_engine._CPP_OWNED_ENGINES if icon_engine.isalive(e)]


    op = sys.argv[1]
    icon = material_icon("database", color="#ff0000", convert_to_pixmap=False)
    shared = QIcon(icon)
    if op == "addPixmap":
        icon.addPixmap(QPixmap(16, 16))
    elif op == "addFile":
        icon.addFile("does_not_exist.png")
    elif op == "setIsMask":
        icon.setIsMask(True)

    clones = live_clones()
    assert len(clones) == 1 and isinstance(clones[0], _MaterialIconEngine), clones
    assert has_red(icon), "clone lost the icon color"
    assert has_red(shared), "original engine broken"
    del clones, icon
    assert live_clones() == [], "clone not released with the detached icon"
    assert has_red(shared)
    print("detached", flush=True)
    """)


@pytest.mark.parametrize("op", ["addPixmap", "addFile", "setIsMask"])
def test_detaching_shared_material_icon_does_not_crash(op):
    """Modifying a copy of a material icon clones its engine; the clone must outlive the call."""
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    proc = subprocess.run(
        [sys.executable, "-c", _DETACH_SCRIPT, op],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    assert (
        proc.returncode == 0 and "detached" in proc.stdout
    ), f"child exited with {proc.returncode}\n{proc.stdout[-2000:]}\n{proc.stderr[:4000]}"
