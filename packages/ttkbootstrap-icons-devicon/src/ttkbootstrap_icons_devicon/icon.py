from typing import Literal

from ttkbootstrap_icons.icon import Icon
from .provider import DeviconFontProvider


_DEVICON_STYLES = {
    "plain",
    "plain-wordmark",
    "original",
    "original-wordmark",
}


def _ensure_variant_name(name: str, style: str) -> str:
    # Allow passthrough
    if name == "none":
        return name
    # If already has a known variant suffix, keep as-is
    for s in sorted(_DEVICON_STYLES, key=len, reverse=True):
        if name.endswith("-" + s):
            return name
    # Otherwise, append requested style
    style = style if style in _DEVICON_STYLES else "plain"
    return f"{name}-{style}"


DeviconStyle = Literal["plain", "plain-wordmark", "original", "original-wordmark"]


class DevIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", style: DeviconStyle = "plain"):
        # Initialize provider once; style is naming-level for this single-font provider
        DevIcon.initialize_with_provider(DeviconFontProvider())
        resolved = _ensure_variant_name(name, style)
        super().__init__(resolved, size, color)
