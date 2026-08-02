"""Superseded by ``tkinter-icons[fluent]``.

This distribution had its final release as 1.0.1. Fluent System Icons now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-fluent is superseded and will receive no further releases. "
    "Fluent System Icons now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[fluent]"\n'
    "    from tkinter_icons import FluentIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .icon import FluentIcon
from .provider import FluentSystemFontProvider

__all__ = ["FluentSystemFontProvider", "FluentIcon"]
