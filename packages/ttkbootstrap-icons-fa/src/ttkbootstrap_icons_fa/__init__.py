"""Superseded by ``tkinter-icons[fontawesome]``.

This distribution had its final release as 1.0.3. Font Awesome 6 (Free) now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-fa is superseded and will receive no further releases. "
    "Font Awesome 6 (Free) now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[fontawesome]"\n'
    "    from tkinter_icons import FontAwesomeIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .icon import FAIcon
from .provider import FontAwesomeFontProvider

__all__ = ["FontAwesomeFontProvider", "FAIcon"]
