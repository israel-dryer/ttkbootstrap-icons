from typing import Literal

from ttkbootstrap_icons.icon import Icon
from .provider import FontAwesomeFontProvider


FAStyle = Literal["solid", "regular", "brands"]


class FAIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", style: FAStyle = "solid"):
        # style: 'solid' | 'regular' | 'brands'
        FAIcon.initialize_with_provider(FontAwesomeFontProvider(), style=style)
        super().__init__(name, size, color)
