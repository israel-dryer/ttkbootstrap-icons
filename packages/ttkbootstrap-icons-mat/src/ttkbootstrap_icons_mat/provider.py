from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class MaterialFontProvider(BaseFontProvider):
    name: str = "mat"
    package: str = "ttkbootstrap_icons_mat"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Material Design Icons"

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
        # MDI often has -outline or other suffixes; we keep raw names, no styles
        return {
            "names": internal,
            "names_by_style": {},
            "display_names_by_style": {},
            "styles": [],
            "style_labels": [],
            "default_style": None,
        }
