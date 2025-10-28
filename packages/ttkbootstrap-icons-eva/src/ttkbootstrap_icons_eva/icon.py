from typing import Literal

from ttkbootstrap_icons.icon import Icon
from .provider import EvaFontProvider


EvaStyle = Literal["outline", "fill"]


def _resolve_name_with_map(name: str, style: EvaStyle) -> str:
    if name == "none":
        return name
    low = name.lower()
    # If already suffixed, keep
    if low.endswith("-outline") or low.endswith("-fill"):
        return name
    # Prefer best match using the loaded icon map
    mp = Icon._icon_map  # populated after initialize_with_provider
    if style == "fill":
        if name in mp:
            return name
        cand = f"{name}-fill"
        if cand in mp:
            return cand
        # Fallback to base if exists
        return name
    else:  # outline
        cand = f"{name}-outline"
        if cand in mp:
            return cand
        # Fallback to base if exists
        return name


class EvaIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", style: EvaStyle = "outline"):
        EvaIcon.initialize_with_provider(EvaFontProvider())
        resolved = _resolve_name_with_map(name, style)
        super().__init__(resolved, size, color)
