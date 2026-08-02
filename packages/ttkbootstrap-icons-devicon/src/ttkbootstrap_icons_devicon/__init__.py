"""Superseded by ``tkinter-icons[devicon]``.

This distribution had its final release as 1.0.1. Devicon now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-devicon is superseded and will receive no further releases. "
    "Devicon now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[devicon]"\n'
    "    from tkinter_icons import DeviconIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .provider import DeviconFontProvider
from .icon import DevIcon

__all__ = ["DeviconFontProvider", "DevIcon"]
