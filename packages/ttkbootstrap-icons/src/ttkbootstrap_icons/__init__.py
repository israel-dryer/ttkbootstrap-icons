"""Font-based icons for Tkinter and ttkbootstrap.

Install an icon provider alongside this package and use its icon class::

    pip install ttkbootstrap-icons-mat

    from ttkbootstrap_icons_mat import MatIcon
    MatIcon("home", size=24, color="#333").image

The drawing internals are public and importable on purpose — `render` for
pure-PIL rendering with no Tk involved, `iconset` for a provider's glyph and
metrics data, and `RenderOptions` for per-icon control over fit and sharpness.
"""

from ttkbootstrap_icons._pyinstaller import get_hook_dirs
from ttkbootstrap_icons.icon import Icon, create_transparent_icon
from ttkbootstrap_icons.iconset import IconSet, get_icon_set
from ttkbootstrap_icons.providers import BaseFontProvider
from ttkbootstrap_icons.registry import ProviderRegistry, load_external_providers
from ttkbootstrap_icons.render import RenderOptions, measure_ink_bounds, render_glyph

__all__ = [
    "BaseFontProvider",
    "Icon",
    "IconSet",
    "ProviderRegistry",
    "RenderOptions",
    "create_transparent_icon",
    "get_hook_dirs",
    "get_icon_set",
    "load_external_providers",
    "measure_ink_bounds",
    "render_glyph",
]
