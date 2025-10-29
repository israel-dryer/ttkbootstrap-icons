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
        # Prefer a style-specific glyphmap if present, e.g., glyphmap-regular.json
        original_map = self.glyphmap_filename
        candidate = f"glyphmap-{chosen}.json"
        try:
            pkg = files(self.package)
            if pkg.joinpath(candidate).is_file():
                self.glyphmap_filename = candidate
        except Exception:
            pass
        try:
            return super().load_assets(style=chosen)
        finally:
            # Restore to avoid leaking state across calls
            self.glyphmap_filename = original_map

    def display_name(self) -> str:  # pragma: no cover
        return "Fluent System Icons"

    def style_display_name(self, style: str) -> str:  # pragma: no cover
        mapping = {"regular": "Regular", "filled": "Filled", "light": "Light"}
        return mapping.get(style, super().style_display_name(style))

    def build_display_index(self) -> dict:
        import json
        styles = self.list_styles()
        names_by_style: dict[str, list[str]] = {}
        display_names_by_style: dict[str, list[str]] = {}
        for s in styles:
            try:
                font_bytes, gm_text = self.load_assets(style=s)
                gm = json.loads(gm_text)
            except Exception:
                gm = {}
            internal = []
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
            # Display names: strip prefix, style suffix, and trailing numeric size
            disp = []
            suffix = f"-{s}"
            for n in internal:
                b = n
                ln = n.lower()
                if ln.startswith("ic-fluent-"):
                    b = b[len("ic-fluent-"):]
                    ln = b.lower()
                if ln.endswith(suffix):
                    b = b[: -len(suffix)]
                    ln = b.lower()
                parts = b.rsplit('-', 1)
                if len(parts) == 2 and parts[1].isdigit():
                    b = parts[0]
                disp.append(b)
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
