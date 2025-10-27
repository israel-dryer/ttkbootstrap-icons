from ttkbootstrap_icons.icon import Icon
from .provider import LucideFontProvider


class LucideIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        Icon.initialize_with_provider(LucideFontProvider())
        super().__init__(name, size, color)

