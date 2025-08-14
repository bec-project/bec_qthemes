from __future__ import annotations

import json
import re
from functools import lru_cache

from bec_qthemes._color import Color


@lru_cache()
def _svg_resources() -> dict[str, str]:
    """Load SVG resources from JSON files."""
    import pkgutil

    # Assuming the JSON files are in the 'style/svg' directory relative to the package
    # and are included in the package data.
    try:
        regular_icons_data = pkgutil.get_data("bec_qthemes", "style/svg/all_material_icons.json")
        filled_icons_data = pkgutil.get_data(
            "bec_qthemes", "style/svg/all_material_icons_filled.json"
        )
    except FileNotFoundError:
        # Fallback for environments where pkgutil might not work as expected (e.g., editable install)
        from pathlib import Path

        base_path = Path(__file__).parent.parent / "style/svg"
        regular_icons_path = base_path / "all_material_icons.json"
        filled_icons_path = base_path / "all_material_icons_filled.json"
        regular_icons_data = regular_icons_path.read_bytes()
        filled_icons_data = filled_icons_path.read_bytes()

    if regular_icons_data is None or filled_icons_data is None:
        raise FileNotFoundError("Could not locate the SVG resource files.")

    resources = json.loads(regular_icons_data)
    resources.update(json.loads(filled_icons_data))
    return resources


class Svg:
    """Class to manage SVG."""

    _SVG_FILL_RE = re.compile(r'fill=".*?"')
    _SVG_FILL_OPACITY_RE = re.compile(r'fill-opacity=".*?"')
    _SVG_TRANSFORM_RE = re.compile(r'transform=".*?"')
    _SVG_STROKE = re.compile(r"stroke:.*?;")

    def __init__(self, id: str) -> None:
        """Initialize svg manager."""
        self._id = id
        self._color = None
        self._rotate = None
        self._source = _svg_resources()[self._id]

    def __str__(self) -> str:
        """Return the svg source code."""
        return self._source

    def colored(self, color: Color) -> Svg:
        """Add or change svg color."""
        svg_tiny_color_formats = color.to_svg_tiny_color_format().split(" ")
        if len(svg_tiny_color_formats) == 2:
            new_svg_color, new_svg_opacity = svg_tiny_color_formats
        else:
            new_svg_color = svg_tiny_color_formats[0]
            new_svg_opacity = None

        current_svg_color = Svg._SVG_FILL_RE.search(self._source)
        current_svg_opacity = Svg._SVG_FILL_OPACITY_RE.search(self._source)
        current_svg_stroke = Svg._SVG_STROKE.search(self._source)

        # Add or change SVG color.
        if current_svg_color is None:
            self._source = self._source.replace("<svg ", f"<svg {new_svg_color} ")
        else:
            self._source = self._source.replace(current_svg_color.group(), new_svg_color)

        # Add or change SVG opacity.
        if new_svg_opacity is not None and current_svg_opacity is None:
            self._source = self._source.replace("<svg ", f"<svg {new_svg_opacity} ")
        elif new_svg_opacity is not None and current_svg_opacity is not None:
            self._source = self._source.replace(current_svg_opacity.group(), new_svg_opacity)

        if current_svg_stroke is not None:
            self._source = self._source.replace(
                current_svg_stroke.group(), f"stroke: #{color._to_hex()};"
            )

        # Remove SVG opacity
        if new_svg_opacity is None and current_svg_opacity is not None:
            self._source = self._source.replace(" " + current_svg_opacity.group(), "")
        return self

    def rotate(self, rotate: int) -> Svg:
        """Rotate svg."""
        if rotate == 0:
            return self

        current_svg_transform = Svg._SVG_TRANSFORM_RE.search(self._source)
        new_svg_transform = f'transform="rotate({rotate}, 12, 12)"'
        if current_svg_transform is None:
            self._source = self._source.replace("<svg ", f"<svg {new_svg_transform} ")
        else:
            self._source = self._source.replace(current_svg_transform.group(), new_svg_transform)

        return self
