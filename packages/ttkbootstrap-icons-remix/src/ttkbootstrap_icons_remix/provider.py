from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class RemixFontProvider(BaseFontProvider):
    name: str = "remix"
    package: str = "ttkbootstrap_icons_remix"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Remix Icon"

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
                    internal = sorted(list(gm.keys()))
            else:
                internal = sorted(list(gm.keys()))
        elif isinstance(gm, list):
            internal = sorted({g.get("name") for g in gm if isinstance(g, dict) and g.get("name")})
        else:
            internal = []
        # Remix includes variants like -line/-fill; show base names per suffix
        names_by_style = {}
        display_names_by_style = {}
        for s in ("line", "fill"):  # common Remix variants
            suffix = f"-{s}"
            names = [n for n in internal if n.lower().endswith(suffix)]
            names_by_style[s] = names
            display_names_by_style[s] = sorted({n[: -len(suffix)] for n in names})
        base_names = display_names_by_style.get("line") or display_names_by_style.get("fill") or internal
        return {
            "names": base_names,
            "names_by_style": names_by_style,
            "display_names_by_style": display_names_by_style,
            "styles": [k for k, v in names_by_style.items() if v],
            "style_labels": [k for k, v in names_by_style.items() if v],
            "default_style": "line" if names_by_style.get("line") else ("fill" if names_by_style.get("fill") else None),
        }
