from ttkbootstrap_icons.icon import Icon
from .provider import SimpleFontProvider


class SimpleIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        SimpleIcon.initialize_with_provider(SimpleFontProvider())
        super().__init__(name, size, color)

