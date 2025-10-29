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
                # Always target the '-fill' variant for consistency
                if not low.endswith("-fill"):
                    resolved = f"{name}-fill"
            else:  # outline
                # Accept '-outline' as alias: strip suffix unconditionally
                if low.endswith("-outline"):
                    resolved = name[:-8]
                # Or strip '-fill' to get base outline
                elif low.endswith("-fill"):
                    resolved = name[:-5]
        super().__init__(resolved, size, color)
