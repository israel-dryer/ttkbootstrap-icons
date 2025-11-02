from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_devicon.provider import DeviconFontProvider

DevStyles = Literal['plain', 'plain-wordmark', 'original', 'original-wordmark']


class DevIcon(Icon):
    """Convenience icon for the Devicon glyph set.

    Resolves the provided name (optionally with a style) using `DeviconProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "anaconda") or a raw glyph
            (e.g. "anaconda-plain"). If you pass a conflicting style (e.g. name ends
            with "-plain" but you set `style="original"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "plain", "original", "plain-wordmark", "original-wordmark". If omitted, the
            provider's default style is used. When `name` already encodes a style suffix (e.g. "-plain"), that suffix
            takes precedence.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: DevStyles | None = None):
        prov = DeviconFontProvider()
        DevIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)
 
