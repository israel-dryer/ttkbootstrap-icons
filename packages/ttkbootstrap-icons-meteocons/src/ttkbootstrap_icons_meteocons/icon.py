from ttkbootstrap_icons_meteocons.provider import MeteoconsFontProvider

from ttkbootstrap_icons.icon import Icon


class MeteoIcon(Icon):
    """Convenience icon for the Meteocons glyph set.

    Resolves the provided name (optionally with a style) using `MeteoconsProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", **kwargs):
        prov = MeteoconsFontProvider()
        MeteoIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color)
 
