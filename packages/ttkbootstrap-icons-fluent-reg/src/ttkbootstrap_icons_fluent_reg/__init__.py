"""Superseded by ``tkinter-icons[fluent-regular]``.

This distribution had its final release as 1.0.1. Fluent System Icons (Regular) now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-fluent-reg is superseded and will receive no further releases. "
    "Fluent System Icons (Regular) now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[fluent-regular]"\n'
    "    from tkinter_icons import FluentRegularIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from ttkbootstrap_icons_fluent_reg.icon import FluentRegularIcon
from ttkbootstrap_icons_fluent_reg.provider import FluentRegularFontProvider

__all__ = [
    "FluentRegularIcon",
    "FluentRegularFontProvider",
]
