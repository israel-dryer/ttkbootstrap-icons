"""Superseded by ``tkinter-icons[meteocons]``.

This distribution had its final release as 1.0.1. Meteocons now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-meteocons is superseded and will receive no further releases. "
    "Meteocons now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[meteocons]"\n'
    "    from tkinter_icons import MeteoconsIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .icon import MeteoIcon
from .provider import MeteoconsFontProvider

__all__ = ["MeteoconsFontProvider", "MeteoIcon"]
