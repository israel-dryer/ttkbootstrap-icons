"""Superseded by ``tkinter-icons[typicons]``.

This distribution had its final release as 1.0.1. Typicons now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-typicons is superseded and will receive no further releases. "
    "Typicons now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[typicons]"\n'
    "    from tkinter_icons import TypiconsIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .provider import TypiconsFontProvider
from .icon import TypiconsIcon

__all__ = ["TypiconsFontProvider", "TypiconsIcon"]

