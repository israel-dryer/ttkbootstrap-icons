from __future__ import annotations

import json
from abc import ABC
from collections.abc import Callable
from copy import deepcopy
from importlib.resources import files
from types import MappingProxyType
from typing import ClassVar, Mapping, Optional

try:  # Prefer stdlib typing (Py 3.11+) and fall back to typing_extensions
    from typing import NotRequired, TypedDict, Unpack  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    from typing_extensions import NotRequired, TypedDict, Unpack


class FontProviderOptions(TypedDict):
    """Options for configuring a font provider."""
    name: str
    package: str
    display_name: NotRequired[str]
    filename: NotRequired[str]
    homepage: NotRequired[str]
    license_url: NotRequired[str]
    icon_version: NotRequired[str]
    styles: NotRequired[Mapping[str, Mapping[str, str | Callable[[str], bool]]]]
    default_style: NotRequired[str]
    pad_factor: NotRequired[float]
    y_bias: NotRequired[float]
    scale_to_fit: NotRequired[bool]


class BaseFontProvider(ABC):
    """Base class for icon providers with class-level caches."""

    __slots__ = (
        "_name", "_package", "_display_name", "_filename", "_homepage",
        "_license_url", "_default_style", "_styles", "_styles_view",
        "_name_lookup", "_pad_factor", "_y_bias", "_scale_to_fit", "_icon_version"
    )

    # Global caches shared per provider class
    _glyphmap_cache_global: ClassVar[dict[tuple[type, str], dict]] = {}
    _font_bytes_cache_global: ClassVar[dict[tuple[type, str], bytes]] = {}
    _name_lookup_global: ClassVar[dict[type, dict[str, dict[str, str]]]] = {}

    _name: str
    _package: str
    _display_name: str
    _filename: Optional[str]
    _homepage: Optional[str]
    _license_url: Optional[str]
    _default_style: Optional[str]
    _icon_version: Optional[str]
    _styles: Mapping[str, Mapping[str, str | Callable[[str], bool]]]
    _styles_view: Mapping[str, Mapping[str, str | Callable[[str], bool]]]
    _name_lookup: dict[str, dict[str, str]]
    _pad_factor: float
    _y_bias: float
    _scale_to_fit: bool

    def __init__(self, **kwargs: Unpack[FontProviderOptions]):
        self._name = kwargs.get('name')  # required
        self._display_name = kwargs.get('display_name', self._name)
        self._package = kwargs.get('package')  # required
        self._filename = kwargs.get('filename')
        self._homepage = kwargs.get('homepage')
        self._license_url = kwargs.get('license_url')
        self._icon_version = kwargs.get('icon_version')
        self._default_style = kwargs.get('default_style')

        self._styles = deepcopy(kwargs.get("styles", {}))
        self._styles_view = MappingProxyType(self._styles)

        self._pad_factor = kwargs.get('pad_factor', 0.10)
        self._y_bias = kwargs.get('y_bias', 0.0)
        self._scale_to_fit = kwargs.get('scale_to_fit', True)

        if self.has_styles and (not self._default_style or self._default_style not in self._styles):
            self._default_style = next(iter(self._styles.keys()))

        self._name_lookup = self.build_name_lookup()

    # -----------------------------
    # Properties
    # -----------------------------
    @property
    def has_styles(self) -> bool:
        """Return True if this provider defines styles."""
        return len(self._styles) > 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def icon_version(self):
        return self._icon_version

    @property
    def homepage(self):
        return self._homepage

    @property
    def license_url(self):
        return self._license_url

    @property
    def default_style(self) -> Optional[str]:
        return self._default_style

    @property
    def style_list(self) -> tuple[str, ...]:
        return tuple(self._styles_view.keys())

    @property
    def style_map(self) -> Mapping[str, Mapping[str, str | Callable[[str], bool]]]:
        return self._styles_view

    @property
    def package(self) -> str:
        return self._package

    @property
    def font_filename(self) -> Optional[str]:
        return self._filename

    @property
    def uses_single_file(self) -> bool:
        if self._filename:
            return True
        if not self.has_styles:
            return False
        try:
            style_files = list({s['filename'] for s in self._styles.values()})
        except KeyError:
            return False
        return len(style_files) == 1

    @property
    def pad_factor(self) -> float:
        """Padding factor for icon rendering (0.0-1.0)."""
        return self._pad_factor

    @property
    def y_bias(self) -> float:
        """Vertical bias adjustment for icon rendering."""
        return self._y_bias

    @property
    def scale_to_fit(self) -> bool:
        """Whether to scale down glyphs that exceed the available space."""
        return self._scale_to_fit

    # -----------------------------
    # Asset Loading
    # -----------------------------
    def _read_glyphmap_for_style(self, style: Optional[str]) -> dict:
        if self.uses_single_file:
            glyphmap_name = "glyphmap.json"
            style_key = "single"
        else:
            style_key = style or self._default_style
            if not style_key:
                raise ValueError(f"No style specified and no default_style configured for provider '{self._name}'.")
            glyphmap_name = f"glyphmap-{style_key}.json"

        gkey = (type(self), style_key)
        cached = self._glyphmap_cache_global.get(gkey)
        if cached is not None:
            return cached

        pkg = files(self.package)
        glyphmap_path = pkg.joinpath(glyphmap_name)
        try:
            glyphmap_text = glyphmap_path.read_text(encoding="utf-8")
            glyphmap = json.loads(glyphmap_text)
        except Exception as e:
            raise FileNotFoundError(f"Glyphmap not accessible for provider '{self.name}': {glyphmap_path}") from e

        self._glyphmap_cache_global[gkey] = glyphmap
        return glyphmap

    def load_assets(self, style: Optional[str] = None) -> tuple[bytes, str]:
        pkg = files(self.package)

        if self.has_styles:
            style_key = style or self._default_style
            if not style_key:
                raise ValueError(f"No style specified and no default_style configured for provider '{self._name}'.")
            filename = self._styles.get(style_key, {}).get("filename") or self._filename
        else:
            filename = self._filename

        if not filename:
            raise FileNotFoundError(f"Font filename not set for provider '{self.name}'.")

        # font bytes cache
        fkey = (type(self), filename)
        font_bytes = self._font_bytes_cache_global.get(fkey)
        if font_bytes is None:
            font_bytes = pkg.joinpath(filename).read_bytes()
            self._font_bytes_cache_global[fkey] = font_bytes

        # glyphmap name
        if self.uses_single_file:
            glyphmap_filename = "glyphmap.json"
        else:
            style_key = style or self._default_style
            glyphmap_filename = f"glyphmap-{style_key}.json"

        glyphmap_json = pkg.joinpath(glyphmap_filename).read_text(encoding="utf-8")
        return font_bytes, glyphmap_json

    # -----------------------------
    # Name Handling
    # -----------------------------
    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        return str(glyph_name).lower()

    def resolve_icon_style(self, name: str, style: Optional[str] = None):
        """Resolve a user-supplied icon name and style to the actual style"""
        if style is not None:
            return style

        if self.has_styles:
            for s in self.style_list:
                if f"-{s}" in name:
                    return s
            return self.default_style
        return None

    def resolve_icon_name(self, name: str, style: Optional[str] = None) -> str:
        """Resolve a user-supplied icon name to the actual glyph name.

        Rules:
        - If *style* is explicitly provided, we resolve within that style only. If the *name*
          clearly encodes a conflicting style suffix (e.g., "-fill" vs requested "outline"),
          a ValueError is raised.
        - If *style* is not provided, infer the style from a "-<style>" suffix when present;
          otherwise use the provider's default style (or "base" when no styles).
        """
        if name == "none":
            return "none"

        if self.has_styles:
            inferred_style = None
            for s in self.style_list:
                if name.endswith(f"-{s}"):
                    inferred_style = s
                    break

            if style is not None and inferred_style is not None and style != inferred_style:
                raise ValueError(
                    f"{name} is not valid for style '{style}' in {self.name}. Try style '{inferred_style}' or use an unsuffixed name."
                )

            lookup_style = style or inferred_style or self.default_style or "base"
            lookup = self._name_lookup.get(lookup_style, {})
            if not lookup:
                raise ValueError(f"Style '{lookup_style}' is not valid for {self.name}. Available: {self.style_list}")

            formatted = self.format_glyph_name(name)
            if name in lookup:
                return lookup[name]
            composite = f"{name}-{lookup_style}"
            if composite in lookup:
                return lookup[composite]
            if formatted in lookup:
                return lookup[formatted]

            # If we inferred a style from the name suffix, try stripping it
            # This handles cases where the glyph names don't include style suffixes
            if inferred_style is not None and name.endswith(f"-{inferred_style}"):
                base_name = name[:-len(f"-{inferred_style}")]
                if base_name in lookup:
                    return lookup[base_name]
                formatted_base = self.format_glyph_name(base_name)
                if formatted_base in lookup:
                    return lookup[formatted_base]

            raise ValueError(f"{name} not found in lookup for {self.name} in {lookup_style} style.")

        # no styles
        lookup = self._name_lookup.get("base", {})
        formatted = self.format_glyph_name(name)
        if name in lookup:
            return lookup[name]
        if formatted in lookup:
            return lookup[formatted]
        raise ValueError(f"{name} is not a valid icon for {self.name}.")

    def get_icons_names_for_display(self) -> dict[str, dict[str, str]]:
        if self.has_styles:
            return {s: {k: v for k, v in d.items() if k != v} for s, d in self._name_lookup.items() if s != "base"}
        base = self._name_lookup.get("base", {})
        return {"base": {k: v for k, v in base.items() if k != v}}

    def build_name_lookup(self) -> dict[str, dict[str, str]]:
        cached = self._name_lookup_global.get(type(self))
        if cached is not None:
            return cached

        lookup: dict[str, dict[str, str]] = {}

        def fallback_predicate(_: str) -> bool:
            return True

        if self.has_styles:
            for style in self.style_list:
                cfg = self._styles.get(style, {})
                pred = cfg.get("predicate", fallback_predicate)
                if not callable(pred):
                    pred = fallback_predicate
                style_lookup: dict[str, str] = {}
                glyphmap = self._read_glyphmap_for_style(style)
                for n in glyphmap.keys():
                    if pred(n):
                        formatted = self.format_glyph_name(n)
                        style_lookup[formatted] = n
                        style_lookup[n] = n
                        # Only add the style suffix if it's not already present anywhere in the name
                        # This handles both cases like "archive-fill" and "shield-fill-check"
                        if f"-{style}" not in n.lower():
                            style_lookup[f"{n}-{style}"] = n
                lookup[style] = style_lookup
        else:
            glyphmap = self._read_glyphmap_for_style(None)
            base_lookup: dict[str, str] = {}
            for n in glyphmap.keys():
                formatted = self.format_glyph_name(n)
                base_lookup[formatted] = n
                base_lookup[n] = n
            lookup["base"] = base_lookup

        self._name_lookup_global[type(self)] = lookup
        return lookup

    def build_display_index(self) -> dict:
        # Ensure lookup exists
        if type(self) not in self._name_lookup_global:
            self.build_name_lookup()

        # Get unique glyph names (values) for each style for display in browser
        # Preserve a stable, insertion-based order instead of using an unordered set.
        if self.has_styles:
            names_by_style: dict[str, dict[str, str]] = {}
            for style, lookup in self._name_lookup.items():
                if style == "base":
                    continue
                seen: set[str] = set()
                ordered: list[str] = []
                for v in lookup.values():
                    if v not in seen:
                        seen.add(v)
                        ordered.append(v)
                names_by_style[style] = {name: name for name in ordered}
        else:
            base_lookup = self._name_lookup.get("base", {})
            seen: set[str] = set()
            ordered: list[str] = []
            for v in base_lookup.values():
                if v not in seen:
                    seen.add(v)
                    ordered.append(v)
            names_by_style = {"base": {name: name for name in ordered}}

        return {
            "names_by_style": names_by_style,
            "has_styles": self.has_styles,
            "styles": self.style_list,
            "default_style": self.default_style,
        }
