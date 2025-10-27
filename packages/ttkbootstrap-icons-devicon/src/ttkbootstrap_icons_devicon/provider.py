from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class DeviconFontProvider(BaseFontProvider):
    name: str = "devicon"
    package: str = "ttkbootstrap_icons_devicon"
    font_filename: str = "fonts/devicon.ttf"
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Devicon"

    def list_styles(self) -> list[str]:  # variants in the single font
        return [
            "plain",
            "plain-wordmark",
            "original",
            "original-wordmark",
        ]

    def get_default_style(self) -> str | None:  # pragma: no cover
        return "plain"

    def style_display_name(self, style: str) -> str:  # pragma: no cover
        mapping = {
            "plain": "Plain",
            "plain-wordmark": "Plain Wordmark",
            "original": "Original",
            "original-wordmark": "Original Wordmark",
        }
        return mapping.get(style, super().style_display_name(style))
