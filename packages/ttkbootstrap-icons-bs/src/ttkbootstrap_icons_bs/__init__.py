"""Superseded by ``tkinter-icons[bootstrap]``.

This distribution had its final release as 1.0.1. Bootstrap Icons now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-bs is superseded and will receive no further releases. "
    "Bootstrap Icons now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[bootstrap]"\n'
    "    from tkinter_icons import BootstrapIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from ttkbootstrap_icons_bs.icon import BootstrapIcon
from ttkbootstrap_icons_bs.provider import BootstrapFontProvider

__all__ = [
    "BootstrapIcon",
    "BootstrapFontProvider",
]