from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class WeatherFontProvider(BaseFontProvider):
    name: str = "weather"
    package: str = "ttkbootstrap_icons_weather"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Weather Icons"

    def get_pad_factor(self) -> float:
        # Moderate padding to avoid clipping without over-shrinking
        return 0.18

    def get_y_bias(self) -> float:
        # Shift glyphs slightly downward to prevent top clipping
        return 0.06

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
