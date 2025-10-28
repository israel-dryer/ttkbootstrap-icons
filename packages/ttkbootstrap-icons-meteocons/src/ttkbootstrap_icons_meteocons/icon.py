from ttkbootstrap_icons.icon import Icon
from .provider import MeteoconsFontProvider


class MeteoconsIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        Icon.initialize_with_provider(MeteoconsFontProvider())
        super().__init__(name, size, color)

