from ttkbootstrap_icons.icon import Icon
from .provider import RPGAFontProvider


class RPGAIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        # RPG Awesome names usually include the class prefix e.g., 'ra-sword'
        RPGAIcon.initialize_with_provider(RPGAFontProvider())
        super().__init__(name, size, color)

