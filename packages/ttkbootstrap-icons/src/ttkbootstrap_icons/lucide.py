from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons.providers import BuiltinLucideProvider


class LucideIcon(Icon):

    def __init__(self, name: str, size: int = 24, color: str = "black"):
        LucideIcon.initialize_with_provider(BuiltinLucideProvider())
        super().__init__(name, size, color)
