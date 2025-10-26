from ttkbootstrap_icons.icon import Icon
from .provider import RemixFontProvider


class RemixIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        RemixIcon.initialize_with_provider(RemixFontProvider())
        super().__init__(name, size, color)

