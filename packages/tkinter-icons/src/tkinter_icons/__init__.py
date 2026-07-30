"""Font-based icons for Tkinter and ttkbootstrap.

One library; the icon sets are installed as extras::

    pip install "tkinter-icons[material]"

    from tkinter_icons import MaterialIcon
    MaterialIcon("home", size=24, color="#333").image

Icon classes are re-exported here from whichever packs are installed, so the
name you install is the name you import. Each pack's own module
(`tkinter_icons_mat` and friends) still works exactly as before — the
re-export is an addition, not a replacement.

The base install has no glyphs of its own: it is the renderer, and it draws
nothing until at least one pack is added. Asking for a class from a pack that
is not installed raises an `ImportError` naming the extra to install.

The drawing internals are public on purpose — `render` for pure-PIL rendering
with no Tk involved, `iconset` for a pack's glyph and metrics data, and
`RenderOptions` for per-icon control over fit and sharpness.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from tkinter_icons._pyinstaller import get_hook_dirs
from tkinter_icons.icon import Icon, create_transparent_icon
from tkinter_icons.iconset import IconSet, get_icon_set
from tkinter_icons.packs import (
    KNOWN_PACKS,
    PACK_BY_EXPORT,
    Pack,
    find_pack,
    installed_packs,
    missing_pack_message,
)
from tkinter_icons.providers import BaseFontProvider
from tkinter_icons.registry import ProviderRegistry, load_external_providers
from tkinter_icons.render import RenderOptions, measure_ink_bounds, render_glyph

if TYPE_CHECKING:
    # Import the pack classes under their exported names so type checkers and
    # IDEs resolve them. These are never executed at runtime — a pack that is
    # not installed must fail through __getattr__ with an actionable message,
    # not blow up on importing this module.
    from tkinter_icons_bs import BootstrapIcon as BootstrapIcon
    from tkinter_icons_devicon import DevIcon as DeviconIcon
    from tkinter_icons_eva import EvaIcon as EvaIcon
    from tkinter_icons_fa import FAIcon as FontAwesomeIcon
    from tkinter_icons_fluent import FluentIcon as FluentIcon
    from tkinter_icons_fluent_reg import FluentRegularIcon as FluentRegularIcon
    from tkinter_icons_gmi import GMatIcon as GoogleMaterialIcon
    from tkinter_icons_ion import IonIcon as IonIcon
    from tkinter_icons_lucide import LucideIcon as LucideIcon
    from tkinter_icons_mat import MatIcon as MaterialIcon
    from tkinter_icons_meteocons import MeteoIcon as MeteoconsIcon
    from tkinter_icons_remix import RemixIcon as RemixIcon
    from tkinter_icons_rpga import RPGAIcon as RpgAwesomeIcon
    from tkinter_icons_simple import SimpleIcon as SimpleIcon
    from tkinter_icons_typicons import TypiconsIcon as TypiconsIcon
    from tkinter_icons_weather import WeatherIcon as WeatherIcon


_CORE = [
    "BaseFontProvider",
    "Icon",
    "IconSet",
    "KNOWN_PACKS",
    "Pack",
    "ProviderRegistry",
    "RenderOptions",
    "create_transparent_icon",
    "find_pack",
    "get_hook_dirs",
    "get_icon_set",
    "installed_packs",
    "load_external_providers",
    "measure_ink_bounds",
    "render_glyph",
]

__all__ = [*_CORE, *sorted(PACK_BY_EXPORT)]


def __getattr__(name: str) -> Any:
    """Resolve an icon class from its pack on first access (PEP 562).

    Keeps the import root single without importing sixteen fonts' worth of
    packs at startup — only the packs actually named get loaded.

    Args:
        name: Attribute being looked up on `tkinter_icons`.

    Returns:
        The pack's icon class.

    Raises:
        ImportError: If `name` belongs to a pack that is not installed. The
            message names the extra to install.
        AttributeError: If `name` is not an icon class at all.
    """
    pack = PACK_BY_EXPORT.get(name)
    if pack is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    try:
        module = importlib.import_module(pack.module)
    except ModuleNotFoundError as exc:
        raise ImportError(missing_pack_message(pack.extra)) from exc

    icon_class = getattr(module, pack.icon_class)
    globals()[name] = icon_class  # cache, so this runs once per name
    return icon_class


def __dir__() -> list[str]:
    """List the core API plus every pack class, installed or not."""
    return sorted(__all__)
