from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons.providers import BuiltinBootstrapProvider


class BootstrapIcon(Icon):

    def __init__(self, name: str, size: int = 24, color: str = "black", style: str | None = None):
        style_l = (style or "outline").lower()
        prov = BuiltinBootstrapProvider()
        BootstrapIcon.initialize_with_provider(prov)
        resolved = name
        if name != "none":
            low = name.lower()
            if style_l == "fill":
                if not low.endswith("-fill"):
                    cand = f"{name}-fill"
                    if cand in Icon._icon_map:
                        resolved = cand
            else:  # outline
                if low.endswith("-fill"):
                    base = name[:-5]
                    if base in Icon._icon_map:
                        resolved = base
        super().__init__(resolved, size, color)
