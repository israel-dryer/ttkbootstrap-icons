from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class LucideFontProvider(BaseFontProvider):
    name: str = "lucide"
    package: str = "ttkbootstrap_icons_lucide"
    # If local fonts are not shipped yet, you can temporarily fall back by copying
    # assets from the base package into this provider's fonts/ and glyphmap.json.
    font_filename: str = "fonts/lucide.ttf"
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Lucide Icons"

    def build_display_index(self) -> dict:
        import json
        try:
            _, gm_text = self.load_assets(style=None)
            gm = json.loads(gm_text)
        except Exception:
            gm = {}
        if isinstance(gm, dict):
            internal = sorted(list(gm.keys()))
        elif isinstance(gm, list):
            internal = sorted({g.get("name") for g in gm if isinstance(g, dict) and g.get("name")})
        else:
            internal = []
        return {
            "names": internal,
            "names_by_style": {},
            "display_names_by_style": {},
            "styles": [],
            "style_labels": [],
            "default_style": None,
        }
