from ttkbootstrap_icons.icon import Icon
from .provider import FontAwesomeFontProvider


class FAIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        FAIcon.initialize_with_provider(FontAwesomeFontProvider())
        super().__init__(name, size, color)
