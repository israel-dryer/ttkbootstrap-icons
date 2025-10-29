from dataclasses import dataclass

from ttkbootstrap_icons.providers import MultiStyleFontProvider


@dataclass
class FontAwesomeFontProvider(MultiStyleFontProvider):
    name: str = "fa"
    package: str = "ttkbootstrap_icons_fa"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"
    styles: dict = None  # type: ignore
    default_style: str = "solid"

    def __post_init__(self):
        if self.styles is None:
            self.styles = {
                "solid": "fonts/fa-solid-900.ttf",
                "regular": "fonts/fa-regular-400.ttf",
                "brands": "fonts/fa-brands-400.ttf",
            }

    def display_name(self) -> str:  # pragma: no cover
        return "Font Awesome"

    def style_display_name(self, style: str) -> str:  # pragma: no cover
        mapping = {"solid": "Solid", "regular": "Regular", "brands": "Brands"}
        return mapping.get(style, super().style_display_name(style))

    def get_pad_factor(self) -> float:
        # Slightly increase padding to reduce top clipping on some glyphs
        return 0.14

    def get_y_bias(self) -> float:
        # Nudge glyphs down a bit to add top headroom
        return 0.03

    def build_display_index(self) -> dict:
        import json
        from io import BytesIO
        try:
            from fontTools.ttLib import TTFont  # type: ignore
        except Exception:
            TTFont = None  # optional filtering
        styles = self.list_styles()
        names_by_style = {}
        display_names_by_style = {}
        for s in styles:
            try:
                font_bytes, gm_text = self.load_assets(style=s)
                gm = json.loads(gm_text)
            except Exception:
                gm = {}
            internal = []
            if isinstance(gm, dict):
                if TTFont is not None:
                    try:
                        tt = TTFont(BytesIO(font_bytes))
                        cmap = set()
                        for table in tt["cmap"].tables:
                            cmap.update(table.cmap.keys())
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
                        internal = sorted([k for k, v in gm.items() if v])
                else:
                    internal = sorted([k for k, v in gm.items() if v])
            elif isinstance(gm, list):
                internal = sorted({g.get("name") for g in gm if isinstance(g, dict) and g.get("name")})
            else:
                internal = []
            names_by_style[s] = internal
            # FA: display base names; drop style suffix when present
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
