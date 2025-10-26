from ttkbootstrap_icons.icon import Icon
from .provider import IonFontProvider


class IonIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        IonIcon.initialize_with_provider(IonFontProvider())
        super().__init__(name, size, color)

