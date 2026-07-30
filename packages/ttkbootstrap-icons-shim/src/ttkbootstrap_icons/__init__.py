"""Compatibility shim: `ttkbootstrap_icons` is now `tkinter_icons`.

Importing this package emits a warning and then forwards every attribute and
submodule to `tkinter_icons`, so existing code keeps working unchanged while it
migrates.

`FutureWarning` rather than `DeprecationWarning` is deliberate. Python hides
`DeprecationWarning` unless it fires in `__main__`, so an application that
imports this from one of its own modules would see nothing at all.
`FutureWarning` is the class Python designates for deprecations aimed at end
users, and it is shown by default — which is the point of the message.
"""

from __future__ import annotations

import importlib
import sys
import warnings

warnings.warn(
    "ttkbootstrap-icons has been renamed to tkinter-icons. This package now "
    "forwards to it and receives no further updates.\n"
    '  pip uninstall ttkbootstrap-icons && pip install "tkinter-icons[all]"\n'
    "Then replace `ttkbootstrap_icons` with `tkinter_icons` in your imports.\n"
    "Icon packs are now extras: pip install \"tkinter-icons[material]\"",
    FutureWarning,
    stacklevel=2,
)

import tkinter_icons as _target

#: Submodules aliased into this package's namespace. Without these,
#: `from ttkbootstrap_icons.icon import Icon` fails — forwarding only the
#: top-level attributes is not enough, because Python resolves submodule
#: imports through sys.modules rather than through __getattr__.
_SUBMODULES = (
    "browser",
    "icon",
    "iconset",
    "packs",
    "providers",
    "registry",
    "render",
    "stateful_icon_mixin",
)

for _name in _SUBMODULES:
    try:
        sys.modules[f"{__name__}.{_name}"] = importlib.import_module(f"tkinter_icons.{_name}")
    except ImportError:  # pragma: no cover - a module dropped in a later release
        pass

__all__ = list(getattr(_target, "__all__", ()))
__version__ = getattr(_target, "__version__", "")


def __getattr__(name: str):
    """Forward attribute access to `tkinter_icons`.

    Delegating lazily rather than copying the namespace at import time means
    anything added to `tkinter_icons` later — including the pack icon classes,
    which resolve on demand — stays reachable through the old name.
    """
    return getattr(_target, name)


def __dir__() -> list[str]:
    return dir(_target)
