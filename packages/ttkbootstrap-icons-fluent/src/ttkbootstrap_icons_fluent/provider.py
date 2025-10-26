from dataclasses import dataclass

from importlib.resources import files
from ttkbootstrap_icons.providers import MultiStyleFontProvider


@dataclass
class FluentFontProvider(MultiStyleFontProvider):
    name: str = "fluent"
    package: str = "ttkbootstrap_icons_fluent"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"
    styles: dict = None  # type: ignore
    default_style: str = "regular"

    def __post_init__(self):
        if self.styles is None:
            self.styles = {
                "regular": "fonts/FluentSystemIcons-Regular.ttf",
                "filled": "fonts/FluentSystemIcons-Filled.ttf",
                "light": "fonts/FluentSystemIcons-Light.ttf",
            }

    def list_styles(self) -> list[str]:
        # Return only styles whose font files exist
        pkg = files(self.package)
        available = []
        for style, rel in self.styles.items():
            try:
                if pkg.joinpath(rel).is_file():
                    available.append(style)
            except Exception:
                continue
        return sorted(available)

    def get_default_style(self) -> str | None:
        styles = self.list_styles()
        if not styles:
            return None
        return self.default_style if self.default_style in styles else styles[0]

    def load_assets(self, style: str | None = None):
        chosen = style or self.get_default_style()
        if not chosen:
            # Defer to base which will error meaningfully
            return super().load_assets(style=None)
        return super().load_assets(style=chosen)
