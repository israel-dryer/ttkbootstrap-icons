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

# Every extra named here must exist. pip does not fail on an unknown extra - it
# prints a warning and installs the base package - so a stale name in this
# message would walk the user into the no-glyphs state the message itself is
# warning them about. There is deliberately no `[all]` extra to fall back on.
warnings.warn(
    "ttkbootstrap-icons has been renamed to tkinter-icons. This package now "
    "forwards to it and receives no further updates.\n"
    "  pip uninstall ttkbootstrap-icons\n"
    '  pip install "tkinter-icons[bootstrap]"\n'
    "Then replace `ttkbootstrap_icons` with `tkinter_icons` in your imports.\n"
    "Icon packs are now extras, one per set, and there is no [all] - name the "
    'ones you use: pip install "tkinter-icons[bootstrap,material]"',
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

#: Names 4.0.0 published at the root of this package that `tkinter_icons` does
#: not re-export. Its root is deliberately the application-facing API, so the
#: provider-definition machinery now lives only in its own module — but 4.0.0's
#: `__all__` was exactly `Icon`, `get_hook_dirs`, `ProviderRegistry`,
#: `load_external_providers`, and forwarding three of four is not a shim. The
#: submodule aliases above only cover `from ttkbootstrap_icons.registry import
#: ProviderRegistry`; these cover the root spelling 4.0.0 actually shipped.
_RELOCATED = {
    "ProviderRegistry": "tkinter_icons.registry",
    "load_external_providers": "tkinter_icons.registry",
}

__all__ = [*getattr(_target, "__all__", ()), *_RELOCATED]
__version__ = getattr(_target, "__version__", "")


def __getattr__(name: str):
    """Forward attribute access to `tkinter_icons`.

    Delegating lazily rather than copying the namespace at import time means
    anything added to `tkinter_icons` later — including the pack icon classes,
    which resolve on demand — stays reachable through the old name.
    """
    try:
        return getattr(_target, name)
    except AttributeError:
        module = _RELOCATED.get(name)
        if module is None:
            raise
        return getattr(importlib.import_module(module), name)


def __dir__() -> list[str]:
    return sorted({*dir(_target), *_RELOCATED})
