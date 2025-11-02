from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_ion.provider import IonFontProvider


class IonIcon(Icon):
    """Convenience icon for the Ion Icon glyph set.

    Resolves the provided name (optionally with a style) using `IonProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", **kwargs):
        prov = IonFontProvider()
        IonIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color)



