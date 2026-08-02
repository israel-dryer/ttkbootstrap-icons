"""Superseded by ``tkinter-icons[material]``.

This distribution had its final release as 1.0.1. Material Design Icons now ship as an extra
of ``tkinter-icons``; see https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html
"""

import warnings

warnings.warn(
    "ttkbootstrap-icons-mat is superseded and will receive no further releases. "
    "Material Design Icons now ship as an extra of tkinter-icons:\n"
    "\n"
    '    pip install "tkinter-icons[material]"\n'
    "    from tkinter_icons import MaterialIcon\n"
    "\n"
    "The class name is unchanged; only the import root moves. "
    "See https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html",
    FutureWarning,
    stacklevel=2,
)

from .provider import MaterialDesignFontProvider
from .icon import MatIcon

__all__ = ["MaterialDesignFontProvider", "MatIcon"]
