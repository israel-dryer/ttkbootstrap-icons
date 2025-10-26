from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons.providers import BuiltinBootstrapProvider


class BootstrapIcon(Icon):

    def __init__(self, name: str, size: int = 24, color: str = "black"):
        BootstrapIcon.initialize_with_provider(BuiltinBootstrapProvider())
        super().__init__(name, size, color)
