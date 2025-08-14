# Material Icons in QSS - Complete Usage Guide

## Overview

You can use Google Material Icons directly in your QSS stylesheets using a simple template syntax. The system
now generates SVGs on-demand from the up-to-date JSON sources and references them via url() in QSS. No PNG buffer is
used.

## Basic Syntax

Use the template syntax `{{ "icon_name" | material_icon(...) }}` in your QSS files. The `material_icon` filter is an
alias of `material_icon_url` and returns a url() to a generated SVG file.

```qss
QPushButton {
    icon: {{ "home" | material_icon(size="16,16", color="#ffffff") }};
}
```

## Available Parameters

- size: Icon dimensions as "width,height" (default: "24,24")
- color: Hex/rgba color or theme variable (default: auto)
- filled: Use filled variant — true or false (default: false)
- rotate: Rotation in degrees 0–360 (default: 0)

## Examples

### Basic Icons

```qss
/* Simple home icon */
QPushButton {
    icon: {{ "home" | material_icon(size="16,16") }};
}

/* Settings icon with custom color */
QToolButton {
    icon: {{ "settings" | material_icon(size="24,24", color="#3b82f6") }};
}
```

### Using Theme Variables

```qss
/* Icon color adapts to theme */
QPushButton {
    icon: {{ "home" | material_icon(size="16,16", color=ON_PRIMARY) }};
    background-color: %%PRIMARY%%;
}

/* Dropdown arrow using theme foreground color */
QComboBox::down-arrow {
    image: {{ "arrow_drop_down" | material_icon(size="20,20", color=FG) }};
}
```

### Filled and Rotated Icons

```qss
/* Filled save icon */
QToolButton[action="save"] {
    icon: {{ "save" | material_icon(size="24,24", filled=true, color=FG) }};
}

/* Rotated refresh icon */
QPushButton[role="refresh"] {
    icon: {{ "refresh" | material_icon(size="18,18", rotate=45) }};
}
```

### State-Specific Icons

```qss
/* Checkboxes with check icon when checked */
QCheckBox::indicator:checked {
    image: {{ "check" | material_icon(size="14,14", color=ON_PRIMARY) }};
}

/* Menu items with icons */
QMenu::item[action="copy"] {
    icon: {{ "content_copy" | material_icon(size="16,16", color=FG) }};
}

QMenu::item[action="paste"] {
    icon: {{ "content_paste" | material_icon(size="16,16", color=FG) }};
}
```

## How It Works

1. Template Processing: When your QSS is loaded, the template engine processes `{{ ... }}` expressions.
2. SVG Generation: Material icons are generated as SVG files with your specified parameters (size, color, rotate,
   filled).
3. Caching: Generated SVGs are cached to avoid regeneration.
4. URL Injection: The system injects url() paths to the generated SVG files into your QSS.

## Cache Location

- Cache directory: `~/.cache/bec_qthemes/material_icons_svg/`
- Different size/color/filled/rotation combinations create separate cached files.
- Clear the cache if you need to force regeneration.

## Available Icons

You can use any icon from Google's Material Icons library. Check the full list at:
https://fonts.google.com/icons

Popular icons include:

- home, settings, search, menu, close
- add, remove, edit, delete, save
- arrow_back, arrow_forward, arrow_drop_down
- visibility, visibility_off, star, favorite
- check, cancel, info, warning, error
- folder, file_copy, download, upload

## Integration with QSS Editor

The QSS editor automatically processes material icon templates when:

1. You edit your theme colors
2. You save/apply themes
3. Files are modified and auto-reloaded

## Theme Variables in Icons

You can use theme variables in icon colors:

- PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK
- FG (foreground), BG (background)
- ON_PRIMARY (text on primary color)
- BORDER, CARD_BG, FIELD_BG

## Troubleshooting

If icons don't appear:

1. Check the icon name is correct (case-sensitive)
2. Verify template syntax: `{{ "name" | material_icon(size="w,h") }}`
3. Ensure color values are valid hex/rgba codes or theme variables
4. Check console for error messages

## Migration from PNG pipeline

Replace PNG-based or resource icons with SVG-generating template calls:

```qss
/* Before */
QPushButton { icon: url(:/icons/home.png); }

/* After */
QPushButton { icon: {{ "home" | material_icon(size="16,16", color=FG) }}; }
```
