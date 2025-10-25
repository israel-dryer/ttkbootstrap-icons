from ttkbootstrap_icons.icon import Icon


class BootstrapIcon(Icon):

    def __init__(self, name: str, size: int = 24, color: str = "black"):
        BootstrapIcon.initialize("bootstrap")
        super().__init__(name, size, color)
