from dataclasses import dataclass
from importlib.resources import files

from ttkbootstrap_icons.providers import MultiStyleFontProvider


@dataclass
class GoogleMaterialProvider(MultiStyleFontProvider):
    name: str = "gmi"
    package: str = "ttkbootstrap_icons_gmi"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"
    styles: dict = None  # type: ignore
    default_style: str = "baseline"

    def __post_init__(self):
        if self.styles is None:
            self.styles = {
                "baseline": "fonts/MaterialIcons-Regular.ttf",
                "outlined": "fonts/MaterialIconsOutlined-Regular.otf",
                "round": "fonts/MaterialIconsRound-Regular.otf",
                "sharp": "fonts/MaterialIconsSharp-Regular.otf",
                "twotone": "fonts/MaterialIconsTwoTone-Regular.otf",
            }

    def list_styles(self) -> list[str]:
        pkg = files(self.package)
        available = []
        for style, rel in self.styles.items():
            try:
                if pkg.joinpath(rel).is_file():
                    available.append(style)
            except Exception:
                continue
        return sorted(available) or [self.default_style]

    def get_default_style(self) -> str | None:
        styles = self.list_styles()
        return self.default_style if self.default_style in styles else styles[0]

    def display_name(self) -> str:  # pragma: no cover
        return "Material Icons"

    def style_display_name(self, style: str) -> str:  # pragma: no cover
        mapping = {
            "baseline": "Baseline",
            "outlined": "Outlined",
            "round": "Round",
            "sharp": "Sharp",
            "twotone": "Two Tone",
        }
        return mapping.get(style, super().style_display_name(style))
