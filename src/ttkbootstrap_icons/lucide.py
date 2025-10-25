from ttkbootstrap_icons.icon import Icon


class LucideIcon(Icon):

    def __init__(self, name: str, size: int = 24, color: str = "black"):
        LucideIcon.initialize("lucide")
        super().__init__(name, size, color)
