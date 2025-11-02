from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_simple.provider import SimpleFontProvider


class SimpleIcon(Icon):
    """Convenience icon for the Simple Icon glyph set.

    Args:
        name: glyph name.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", **kwargs):
        prov = SimpleFontProvider()
        SimpleIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color)



