"""Superseded by ``tkinter-icons[rpg-awesome]``.

This distribution had its final release as 1.0.1. RPG Awesome now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-rpga is superseded and will receive no further releases. "
    "RPG Awesome now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[rpg-awesome]"\n'
    "    from tkinter_icons import RpgAwesomeIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .icon import RPGAIcon
from .provider import RPGAFontProvider

__all__ = ["RPGAFontProvider", "RPGAIcon"]
