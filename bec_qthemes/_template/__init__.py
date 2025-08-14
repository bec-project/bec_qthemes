"""Template system for QSS processing with material icon support."""

from __future__ import annotations

from bec_qthemes._template.engine import Template
from bec_qthemes._template.filter import (
    color,
    palette_format,
    url,
    env,
    corner,
    material_icon_url,
    material_icon_path,
)

# Create filters dictionary for the template engine
TEMPLATE_FILTERS = {
    "color": color,
    "palette_format": palette_format,
    "url": url,
    "env": env,
    "corner": corner,
    "material_icon_url": material_icon_url,
    "material_icon": material_icon_url,  # Alias for convenience
    "material_icon_path": material_icon_path,
}


def render_template(template_text: str, variables: dict[str, str]) -> str:
    """
    Render a QSS template with material icon support.

    Args:
        template_text: QSS template with placeholders like {{ "icon_name" | material_icon(size="24,24") }}
        variables: Dictionary of variables to substitute (e.g., PRIMARY, BACKGROUND, etc.)

    Returns:
        Rendered QSS with material icons and variables resolved
    """
    template = Template(template_text, TEMPLATE_FILTERS)
    return template.render(variables)


__all__ = [
    "Template",
    "TEMPLATE_FILTERS",
    "render_template",
    "material_icon_url",
    "material_icon_path",
]
