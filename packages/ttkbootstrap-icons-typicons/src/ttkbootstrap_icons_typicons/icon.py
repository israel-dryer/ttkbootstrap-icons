from ttkbootstrap_icons_typicons.provider import TypiconsFontProvider

from ttkbootstrap_icons.icon import Icon


class TypiconsIcon(Icon):
    """Convenience icon for the Typicons glyph set.

    Resolves the provided name using `TypiconsProvider`, then initializes the base `Icon`
    with the resolved glyph name.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", **kwargs):
        prov = TypiconsFontProvider()
        TypiconsIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color)
 
