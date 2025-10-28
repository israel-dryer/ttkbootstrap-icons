from typing import Literal, Optional

from ttkbootstrap_icons.icon import Icon
from .provider import FluentFontProvider


FluentStyle = Literal["regular", "filled", "light"]


class FluentIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", style: Optional[FluentStyle] = None):
        base_style = (style or "").lower() if style is not None else None
        # Infer style from name if not provided
        inferred_style = None
        for sfx in ("regular", "filled", "light"):
            if name.lower().endswith(f"-{sfx}"):
                inferred_style = sfx
                break

        style_l = base_style or inferred_style or "regular"

        provider = FluentFontProvider()
        FluentIcon.initialize_with_provider(provider, style=style_l)

        # If a style was provided (or inferred) but the icon name doesn't include it,
        # append the style suffix to help match glyph names like 'home-16-regular'.
        full_name = name
        if not name.lower().endswith(tuple(["-regular", "-filled", "-light"])):
            if style_l in ("regular", "filled", "light"):
                full_name = f"{name}-{style_l}"

        super().__init__(full_name, size, color)
