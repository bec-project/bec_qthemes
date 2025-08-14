"""Utility methods for qthemes."""

from __future__ import annotations

import inspect
import logging
import operator as ope
import re
from pathlib import Path

import bec_qthemes

# greater_equal and less_equal must be evaluated before greater and less.
_OPERATORS = {"==": ope.eq, "!=": ope.ne, ">=": ope.ge, "<=": ope.le, ">": ope.gt, "<": ope.lt}


def multi_replace(target: str, replacements: dict[str, str]) -> str:
    """Given a string and a replacement map, it returns the replaced string.

    See https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729.

    Args:
        target: String to execute replacements on.
        replacements: Replacement dictionary {value to find: value to replace}.

    Returns:
        str: Target string that replaced with `replacements`.
    """
    if len(replacements) == 0:
        return target

    replacements_sorted = sorted(replacements, key=len, reverse=True)
    replacements_escaped = [re.escape(i) for i in replacements_sorted]
    pattern = re.compile("|".join(replacements_escaped))
    return pattern.sub(lambda match: replacements[match.group()], target)


def get_logger(logger_name: str) -> logging.Logger:
    """Return the logger with the name specified by logger_name arg.

    Args:
        logger_name: The name of logger.

    Returns:
        Logger reformatted for this package.
    """
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(name)s] [%(levelname)s] %(message)s"))
    logger.addHandler(ch)
    return logger


def get_cash_root_path(version: str) -> Path:
    """Return the cache root dir path inside the repository folder.

    Previously this used the user's home directory (e.g. ~/.cache). Now it is placed under
    the repository root so artifacts are local to the project checkout.
    Layout: <repo>/.cache/bec_qthemes/v<version>
    """
    # Package root: .../bec_qthemes/bec_qthemes
    pkg_root = Path(inspect.getfile(bec_qthemes)).parent
    # Repo root: parent of the package folder
    repo_root = pkg_root.parent
    return repo_root / ".cache" / "bec_qthemes" / f"v{version}"


def get_qthemes_root_path() -> Path:
    """Return the qthemes package root path.

    Returns:
        qthemes package root path.
    """
    return Path(inspect.getfile(bec_qthemes)).parent


def _compare_v(v1: str, operator: str, v2: str) -> bool:
    """Comparing two versions."""
    v1_list, v2_list = (tuple(map(int, (v.split(".")))) for v in (v1, v2))
    return _OPERATORS[operator](v1_list, v2_list)


def analyze_version_str(target_version: str, version_text: str) -> bool:
    """Analyze text comparing versions."""
    for operator in _OPERATORS:
        if operator not in version_text:
            continue
        version = version_text.replace(operator, "")
        return _compare_v(target_version, operator, version)
    raise AssertionError("Text comparing versions is wrong.")


# --- New helper: read project version from pyproject.toml ---


def get_project_version_from_pyproject() -> str:
    """Return the project version declared in pyproject.toml.

    Looks for [project] version in the repository's pyproject.toml. Falls back to
    bec_qthemes.__version__ and then to "0.0.0" if not found.
    """
    try:
        pkg_root = Path(inspect.getfile(bec_qthemes)).parent
        repo_root = pkg_root.parent
        pyproject = repo_root / "pyproject.toml"
        if pyproject.is_file():
            text = pyproject.read_text(encoding="utf-8", errors="ignore")
            # Find the [project] table and capture its version = "..."
            # Use a simple state machine to avoid wrong matches in other sections.
            in_project = False
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("[") and stripped.endswith("]"):
                    in_project = stripped.lower() == "[project]"
                    continue
                if in_project and stripped.lower().startswith("version"):
                    m = re.search(r'version\s*=\s*"([^"]+)"', stripped)
                    if m:
                        return m.group(1).strip()
        # Fallbacks
        v = getattr(bec_qthemes, "__version__", None)
        if isinstance(v, str) and v:
            return v
    except Exception:
        pass
    return "0.0.0"
