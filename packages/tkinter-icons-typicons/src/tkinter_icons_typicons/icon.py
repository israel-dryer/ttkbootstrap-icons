from __future__ import annotations

from tkinter_icons_typicons.provider import TypiconsFontProvider

from tkinter_icons.icon import Icon
from tkinter_icons.render import RenderOptions


class TypiconsIcon(Icon):
    """Convenience icon for the Typicons glyph set.

    Resolves the provided name using `TypiconsProvider`, then initializes the base `Icon`
    with the resolved glyph name.
    """

    provider_class = TypiconsFontProvider

    def __init__(self, name: str, size: int = 24, color: str = "black",
                 *, options: RenderOptions | None = None, **kwargs):
        prov = TypiconsFontProvider()
        TypiconsIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color, options=options)
 
