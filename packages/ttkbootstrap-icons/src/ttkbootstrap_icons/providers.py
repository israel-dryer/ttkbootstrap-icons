from __future__ import annotations

from abc import ABC
import json
from dataclasses import dataclass
from importlib.resources import files
import os
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class BaseFontProvider(ABC):
    """Base provider for font-based icon sets.

    Subclasses should set:
    - name: short identifier (e.g., "bootstrap", "lucide", "fa")
    - package: the package where assets live
    - font_filename: path (relative to package) to a .ttf font
    - glyphmap_filename: path (relative to package) to the icon JSON map
    """

    name: str
    package: str
    font_filename: str
    glyphmap_filename: str

    def display_name(self) -> str:
        return getattr(self, "display", self.name)

    def style_display_name(self, style: str) -> str:
        return style.title()
    def list_styles(self) -> list[str]:
        """Return available style identifiers for this provider (if any)."""
        return []

    def get_default_style(self) -> str | None:
        """Return the default style identifier, if any."""
        return None

    def load_assets(self, style: Optional[str] = None) -> Tuple[bytes, str]:
        """Return (font_bytes, glyphmap_json_text)."""
        pkg = files(self.package)

        # Resolve font file: explicit filename or first .ttf/.otf in fonts/
        if self.font_filename:
            font_path = pkg.joinpath(self.font_filename)
        else:
            # Fallback: pick first .ttf or .otf under package
            candidates = list(pkg.rglob("*.ttf")) + list(pkg.rglob("*.otf"))
            if not candidates:
                raise FileNotFoundError(
                    f"No font found for provider '{self.name}' in package '{self.package}'."
                )
            font_path = candidates[0]

        # Ensure the file exists
        try:
            _ = font_path.read_bytes()
        except Exception as e:
            raise FileNotFoundError(f"Font not accessible for provider '{self.name}': {font_path}") from e

        glyphmap_path = pkg.joinpath(self.glyphmap_filename)

        # Debug output for troubleshooting which font is being loaded
        if os.environ.get("TTKICONS_DEBUG"):
            try:
                print(f"[ttkicons DEBUG] provider={self.name} style={style or ''} font={font_path}")
            except Exception:
                pass

        font_bytes = font_path.read_bytes()
        glyphmap_json = glyphmap_path.read_text(encoding="utf-8")
        return font_bytes, glyphmap_json

    def build_display_index(self) -> dict:
        """Return display metadata for the previewer (generic default).

        Returns a dict with keys:
        - names: list[str]
        - names_by_style: dict[str, list[str]]
        - display_names_by_style: dict[str, list[str]]
        - styles: list[str]
        - style_labels: list[str]
        - default_style: Optional[str]
        """
        try:
            _, gm_text = self.load_assets(style=None)
            glyphmap = json.loads(gm_text)
        except Exception:
            glyphmap = {}

        def extract_names(glyphmap_obj) -> list[str]:
            if isinstance(glyphmap_obj, dict):
                sample = next(iter(glyphmap_obj.values()), None)
                if isinstance(sample, dict):
                    return sorted([str(k) for k in glyphmap_obj.keys()])
                return sorted([str(k) for k in glyphmap_obj.keys()])
            if isinstance(glyphmap_obj, list):
                names = [g.get("name") for g in glyphmap_obj if isinstance(g, dict) and g.get("name")]
                return sorted(set([str(n) for n in names if n]))
            return []

        all_names = extract_names(glyphmap)

        # Styles
        try:
            styles = list(self.list_styles())  # type: ignore[attr-defined]
        except Exception:
            styles = []

        names_by_style: dict[str, list[str]] = {}
        display_names_by_style: dict[str, list[str]] = {}
        if styles:
            has_multi_fonts = hasattr(self, "styles")
            if has_multi_fonts:
                for s in styles:
                    try:
                        _, gm_text_s = self.load_assets(style=s)
                        gm_s = json.loads(gm_text_s)
                        names = extract_names(gm_s)
                    except Exception:
                        names = []
                    names_by_style[s] = names
                    display_names_by_style[s] = list(names)
            else:
                for s in styles:
                    suffix = "-" + s
                    names = [n for n in all_names if str(n).lower().endswith(suffix)]
                    names_by_style[s] = sorted(set(names))
                    base = []
                    for n in names_by_style[s]:
                        ln = str(n).lower()
                        if ln.endswith(suffix):
                            base.append(n[: -len(suffix)])
                        else:
                            base.append(n)
                    display_names_by_style[s] = sorted(set(base))

        try:
            default_style = self.get_default_style()  # type: ignore[attr-defined]
        except Exception:
            default_style = None

        return {
            "names": all_names,
            "names_by_style": names_by_style,
            "display_names_by_style": display_names_by_style,
            "styles": styles,
            "style_labels": list(styles),
            "default_style": default_style,
        }


@dataclass
class MultiStyleFontProvider(BaseFontProvider):
    """Provider that supports multiple styles.

    Set `styles` to a mapping of style -> relative TTF path (under the package).
    If `style` is None, uses a `default_style`.
    """

    styles: dict
    default_style: str = "regular"

    def load_assets(self, style: Optional[str] = None) -> Tuple[bytes, str]:
        chosen = (style or self.default_style).lower()
        if chosen not in self.styles:
            raise FileNotFoundError(f"Style '{chosen}' not found for provider '{self.name}'.")
        self.font_filename = self.styles[chosen]
        return super().load_assets(style=style)

    def list_styles(self) -> list[str]:
        return sorted(self.styles.keys())

    def get_default_style(self) -> str | None:
        return self.default_style


class BuiltinBootstrapProvider(BaseFontProvider):
    def __init__(self) -> None:
        super().__init__(
            name="bootstrap",
            package="ttkbootstrap_icons.assets",
            font_filename="bootstrap.ttf",
            glyphmap_filename="bootstrap.json",
        )

    def display_name(self) -> str:  # pragma: no cover
        return "Bootstrap Icons"

    def list_styles(self) -> list[str]:
        return ["outline", "fill"]

    def get_default_style(self) -> str | None:  # pragma: no cover
        return "outline"

    def build_display_index(self) -> dict:
        import json
        _, gm_text = self.load_assets()
        gm = json.loads(gm_text)
        all_names = sorted(list(gm.keys())) if isinstance(gm, dict) else []
        outline = [n for n in all_names if not n.lower().endswith("-fill")]
        filled = [n for n in all_names if n.lower().endswith("-fill")]
        names_by_style = {"outline": outline, "fill": filled}
        display_names_by_style = {
            "outline": outline,
            "fill": sorted({n[:-5] for n in filled}),
        }
        return {
            "names": display_names_by_style["outline"],
            "names_by_style": names_by_style,
            "display_names_by_style": display_names_by_style,
            "styles": ["outline", "fill"],
            "style_labels": ["outline", "fill"],
            "default_style": "outline",
        }


class BuiltinLucideProvider(BaseFontProvider):
    def __init__(self) -> None:
        super().__init__(
            name="lucide",
            package="ttkbootstrap_icons.assets",
            font_filename="lucide.ttf",
            glyphmap_filename="lucide.json",
        )

    def display_name(self) -> str:  # pragma: no cover
        return "Lucide Icons"

    def build_display_index(self) -> dict:
        import json
        _, gm_text = self.load_assets()
        gm = json.loads(gm_text)
        if isinstance(gm, dict):
            names = sorted(list(gm.keys()))
        elif isinstance(gm, list):
            names = sorted({g.get("name") for g in gm if isinstance(g, dict) and g.get("name")})
        else:
            names = []
        return {
            "names": names,
            "names_by_style": {},
            "display_names_by_style": {},
            "styles": [],
            "style_labels": [],
            "default_style": None,
        }
