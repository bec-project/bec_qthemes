"""Module for checking tag validation in GitHub auto release action."""

import argparse
import logging
import sys
from importlib.metadata import version

import bec_qthemes

logging.basicConfig(level=logging.INFO)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="This program check package built by poetry.")
    parser.add_argument("--tag-version", help="Version name of the pushed tag", required=True)
    return parser.parse_args()


def _test_qthemes() -> None:
    for theme in bec_qthemes.get_themes():
        bec_qthemes.load_stylesheet(theme)


def _main() -> None:
    args = _parse_args()
    git_tag_v: str = args.tag_version.replace("v", "")
    package_v = version("pyqtdarktheme")
    if git_tag_v == package_v == bec_qthemes.__version__:
        logging.info("The package version, module version and tag version are the same.")
    else:
        logging.info("The version names of package and tag are different.")
        logging.info("tag version(GitHub tags)         : ", git_tag_v)
        logging.info("package version(pyproject.toml)  : ", package_v)
        logging.info("module version(__version__)      : ", bec_qthemes.__version__)
        sys.exit(1)

    _test_qthemes()
    logging.info("Test finished successfully!")


if __name__ == "__main__":
    _main()
