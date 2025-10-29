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
            if style == "twotone":
                continue
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

    def build_display_index(self) -> dict:
        import json
        styles = self.list_styles()
        names_by_style = {}
        display_names_by_style = {}
        for s in styles:
            try:
                font_bytes, gm_text = self.load_assets(style=s)
                gm = json.loads(gm_text)
            except Exception:
                gm = {}
            from io import BytesIO
            try:
                from fontTools.ttLib import TTFont  # type: ignore
            except Exception:
                TTFont = None
            if isinstance(gm, dict):
                if TTFont is not None:
                    try:
                        tt = TTFont(BytesIO(font_bytes))
                        cmap = set()
                        for table in tt["cmap"].tables:
                            cmap.update(table.cmap.keys())
                        internal = []
                        for k, v in gm.items():
                            if not v:
                                continue
                            try:
                                cp = int(v, 16) if isinstance(v, str) else int(v)
                            except Exception:
                                continue
                            if cp in cmap:
                                internal.append(k)
                        internal = sorted(set(internal))
                    except Exception:
                        internal = sorted(list(gm.keys()))
                else:
                    internal = sorted(list(gm.keys()))
            elif isinstance(gm, list):
                internal = sorted({g.get("name") for g in gm if isinstance(g, dict) and g.get("name")})
            else:
                internal = []
            names_by_style[s] = internal
            suffix = f"-{s}"
            disp = []
            for n in internal:
                ln = n.lower()
                disp.append(n[:-len(suffix)] if ln.endswith(suffix) else n)
            display_names_by_style[s] = sorted(set(disp))
        default_style = self.get_default_style()
        base_names = display_names_by_style.get(default_style or (styles[0] if styles else ""), []) if styles else []
        return {
            "names": base_names,
            "names_by_style": names_by_style,
            "display_names_by_style": display_names_by_style,
            "styles": styles,
            "style_labels": styles,
            "default_style": default_style,
        }
