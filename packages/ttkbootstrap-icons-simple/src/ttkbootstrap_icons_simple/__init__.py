"""Superseded by ``tkinter-icons[simple]``.

This distribution had its final release as 1.0.1. Simple Icons now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-simple is superseded and will receive no further releases. "
    "Simple Icons now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[simple]"\n'
    "    from tkinter_icons import SimpleIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .icon import SimpleIcon
from .provider import SimpleFontProvider

__all__ = ["SimpleFontProvider", "SimpleIcon"]
