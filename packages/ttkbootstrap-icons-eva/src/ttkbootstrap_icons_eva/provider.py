from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class EvaFontProvider(BaseFontProvider):
    name: str = "eva"
    package: str = "ttkbootstrap_icons_eva"
    font_filename: str = "fonts/eva-icons.ttf"
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Eva Icons"

    def list_styles(self) -> list[str]:  # outline/fill variants encoded in names
        return ["outline", "fill"]

    def get_default_style(self) -> str | None:  # pragma: no cover
        return "fill"

    def build_display_index(self) -> dict:
        import json
        try:
            _, gm_text = self.load_assets(style=None)
            gm = json.loads(gm_text)
        except Exception:
            gm = {}
        names = sorted(list(gm.keys())) if isinstance(gm, dict) else []
        styles = ["outline", "fill"]
        names_by_style: dict[str, list[str]] = {}
        display_names_by_style: dict[str, list[str]] = {}

        outline_names = [n for n in names if n.lower().endswith("-outline")]
        names_by_style["outline"] = outline_names
        display_names_by_style["outline"] = sorted({n[:-8] for n in outline_names})

        fill_names = [n for n in names if not n.lower().endswith("-outline")]
        names_by_style["fill"] = fill_names
        fill_display = set()
        for n in fill_names:
            ln = n.lower()
            if ln.endswith("-fill"):
                fill_display.add(n[:-5])
            else:
                fill_display.add(n)
        display_names_by_style["fill"] = sorted(fill_display)

        display_union = sorted(set(display_names_by_style["outline"]) | set(display_names_by_style["fill"]))
        return {
            "names": display_union,
            "names_by_style": names_by_style,
            "display_names_by_style": display_names_by_style,
            "styles": styles,
            "style_labels": styles,
            "default_style": self.get_default_style(),
        }
