from typing import Literal, Optional

from ttkbootstrap_icons.icon import Icon
from .provider import FluentFontProvider


FluentStyle = Literal["regular", "filled", "light"]


class FluentIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", style: Optional[FluentStyle] = None):
        base_style = (style or "").lower() if style is not None else None
        # Infer style from name if not provided
        inferred_style = None
        for sfx in ("regular", "filled", "light"):
            if name.lower().endswith(f"-{sfx}"):
                inferred_style = sfx
                break

        style_l = base_style or inferred_style or "regular"

        provider = FluentFontProvider()
        FluentIcon.initialize_with_provider(provider, style=style_l)

        # Normalize to 'ic-fluent-<base>-<style>' or 'ic-fluent-<base>-<size>-<style>'
        full_name = name
        low = full_name.lower()
        if not low.startswith("ic-fluent-"):
            full_name = f"ic-fluent-{full_name}"
            low = full_name.lower()
        if not low.endswith(("-regular", "-filled", "-light")):
            if style_l in ("regular", "filled", "light"):
                full_name = f"{full_name}-{style_l}"
                low = full_name.lower()

        def has_size_segment(stem: str) -> bool:
            if '-' not in stem:
                return False
            tail = stem.rsplit('-', 1)[-1]
            return tail.isdigit()

        stem = full_name
        for suf in ("-regular", "-filled", "-light"):
            if stem.lower().endswith(suf):
                stem = stem[: -len(suf)]
                break
        if not has_size_segment(stem):
            preferred = ["20", "24", "16", "28", "32", "48"]
            chosen = None
            for sz in preferred:
                cand = f"{stem}-{sz}{full_name[len(stem):]}"
                if cand in Icon._icon_map:
                    chosen = cand
                    break
            if chosen:
                full_name = chosen

        super().__init__(full_name, size, color)
