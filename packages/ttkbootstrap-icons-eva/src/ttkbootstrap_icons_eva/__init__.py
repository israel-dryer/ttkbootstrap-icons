"""Superseded by ``tkinter-icons[eva]``.

This distribution had its final release as 1.0.1. Eva Icons now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-eva is superseded and will receive no further releases. "
    "Eva Icons now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[eva]"\n'
    "    from tkinter_icons import EvaIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .icon import EvaIcon
from .provider import EvaFontProvider

__all__ = ["EvaFontProvider", "EvaIcon"]
