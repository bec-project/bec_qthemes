"""Module for handling template text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import chain, zip_longest

from bec_qthemes._util import multi_replace


@dataclass(unsafe_hash=True, frozen=True)
class _Placeholder:
    match_text: str
    value: str | int | float
    filters: tuple[str]


class Template:
    """Class that handles template text like jinja2."""

    _PLACEHOLDER_RE = re.compile(r"{{.*?}}")
    _STRING_RE = re.compile(r"""('([^'\\]*(?:\\.[^'\\]*)*)'|"([^"\\]*(?:\\.[^"\\]*)*)")""", re.S)

    def __init__(self, text: str, filters: dict):
        """Initialize Template class."""
        self._target_text = text
        self._filters = filters
        self._vars: dict[str, str] | None = None  # populated during render

    @staticmethod
    def _to_py_value(text: str):
        try:
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                return text

    @staticmethod
    def _parse_placeholders(text: str):
        placeholders: set[_Placeholder] = set()
        for match in re.finditer(Template._PLACEHOLDER_RE, text):
            match_text = match.group()
            # Extract content without the braces but preserve spaces in quoted strings
            content = match_text.strip("{}")

            # Split by pipe, but be careful about spaces in quoted strings
            parts = content.split("|")
            if len(parts) > 0:
                # The first part is the value (could be a quoted string or variable)
                value_part = parts[0].strip()
                value = Template._to_py_value(value_part)

                # The rest are filters
                filters = [f.strip() for f in parts[1:]]
                placeholders.add(_Placeholder(match_text, value, tuple(filters)))

        return placeholders

    def _run_filter(self, value: str | int | float, filter_text: str):
        contents = filter_text.split("(", 1)
        if len(contents) == 1:
            # No arguments, just call the filter with the value
            return self._filters[contents[0]](value)

        filter_name = contents[0]
        arg_text = contents[1].rstrip(")")

        # Parse arguments manually instead of trying to construct JSON
        arguments: dict[str, str] = {}
        if arg_text.strip():
            # Split arguments by comma, but be careful about quoted strings
            arg_parts = []
            current_arg = ""
            in_quotes = False
            quote_char = None

            for char in arg_text:
                if char in ('"', "'") and not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_arg += char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    quote_char = None
                    current_arg += char
                elif char == "," and not in_quotes:
                    arg_parts.append(current_arg.strip())
                    current_arg = ""
                else:
                    current_arg += char

            if current_arg.strip():
                arg_parts.append(current_arg.strip())

            # Parse each argument
            for arg_part in arg_parts:
                if "=" in arg_part:
                    key, val = arg_part.split("=", 1)
                    key = key.strip()
                    val = val.strip()

                    # Remove quotes from string values
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    elif val.startswith("'") and val.endswith("'"):
                        val = val[1:-1]
                    else:
                        # Unquoted token — try to resolve as variable from current vars
                        if self._vars and val in self._vars:
                            val = self._vars[val]

                    arguments[key] = val

        return self._filters[filter_name](value, **arguments)

    def render(self, replacements: dict) -> str:
        """Render replacements."""
        self._vars = replacements  # make available for argument resolution
        placeholders = Template._parse_placeholders(self._target_text)
        new_replacements: dict[str, str] = {}
        for placeholder in placeholders:
            value = placeholder.value

            # Handle quoted strings properly - if it's a quoted string, use it as is
            if isinstance(value, str) and len(value) > 0:
                # Check if it's a quoted string (starts and ends with quotes)
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    # It's a quoted string literal, use the value without quotes
                    value = value[1:-1]
                else:
                    # It's a variable name, look it up in replacements
                    value = replacements.get(value)
                    if value is None:
                        raise AssertionError(
                            f"There is no replacements for: {placeholder.value} in {placeholder.match_text}"
                        )

            # Apply filters
            for filter_name in placeholder.filters:
                value = self._run_filter(value, filter_name)

            new_replacements[placeholder.match_text] = str(value)
        return multi_replace(self._target_text, new_replacements)
