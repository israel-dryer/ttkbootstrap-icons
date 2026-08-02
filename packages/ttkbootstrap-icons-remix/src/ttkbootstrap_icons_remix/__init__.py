"""Superseded by ``tkinter-icons[remix]``.

This distribution had its final release as 1.0.1. Remix Icon now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-remix is superseded and will receive no further releases. "
    "Remix Icon now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[remix]"\n'
    "    from tkinter_icons import RemixIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .icon import RemixIcon
from .provider import RemixFontProvider

__all__ = ["RemixFontProvider", "RemixIcon"]
