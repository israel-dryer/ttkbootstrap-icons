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

    def build_display_index(self) -> dict:
        import json
        from io import BytesIO
        try:
            from fontTools.ttLib import TTFont  # type: ignore
        except Exception:
            TTFont = None
        try:
            font_bytes, gm_text = self.load_assets(style=None)
            gm = json.loads(gm_text)
        except Exception:
            gm = {}
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
                    internal = sorted([k for k, v in gm.items() if v])
            else:
                internal = sorted([k for k, v in gm.items() if v])
        elif isinstance(gm, list):
            internal = sorted({g.get("name") for g in gm if isinstance(g, dict) and g.get("name")})
        else:
            internal = []
        styles = self.list_styles()
        names_by_style = {}
        display_names_by_style = {}
        for s in styles:
            suffix = f"-{s}"
            names = [n for n in internal if n.lower().endswith(suffix)]
            names_by_style[s] = names
            # Display without style suffix
            display_names_by_style[s] = sorted({n[: -len(suffix)] for n in names})
        default_style = self.get_default_style()
        base_names = display_names_by_style.get(default_style or (styles[0] if styles else ""), []) if styles else internal
        return {
            "names": base_names,
            "names_by_style": names_by_style,
            "display_names_by_style": display_names_by_style,
            "styles": styles,
            "style_labels": styles,
            "default_style": default_style,
        }
