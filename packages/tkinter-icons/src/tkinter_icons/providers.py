from __future__ import annotations

import json
from abc import ABC
from collections.abc import Callable
from copy import deepcopy
from importlib.resources import files
from types import MappingProxyType
from typing import ClassVar, Mapping, Optional

from .render import InkBounds, RenderOptions

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
    oversample: NotRequired[int]
    align: NotRequired[bool]
    sharpen: NotRequired[bool]
    snap_even: NotRequired[bool]


class BaseFontProvider(ABC):
    """Base class for icon providers with class-level caches."""

    __slots__ = (
        "_name", "_package", "_display_name", "_filename", "_homepage",
        "_license_url", "_default_style", "_styles", "_styles_view",
        "_name_lookup", "_render_options", "_icon_version"
    )

    # Global caches shared per provider class
    _glyphmap_cache_global: ClassVar[dict[tuple[type, str], dict]] = {}
    _font_bytes_cache_global: ClassVar[dict[tuple[type, str], bytes]] = {}
    _name_lookup_global: ClassVar[dict[type, dict[str, dict[str, str]]]] = {}
    _metrics_cache_global: ClassVar[dict[tuple[type, str], dict[str, InkBounds]]] = {}

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
    _render_options: RenderOptions

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

        self._render_options = RenderOptions().merge(
            pad_factor=kwargs.get('pad_factor'),
            y_bias=kwargs.get('y_bias'),
            scale_to_fit=kwargs.get('scale_to_fit'),
            oversample=kwargs.get('oversample'),
            align=kwargs.get('align'),
            sharpen=kwargs.get('sharpen'),
            snap_even=kwargs.get('snap_even'),
        )

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
    def render_options(self) -> RenderOptions:
        """Default drawing options for this provider's glyphs.

        Overridable per call — see `tkinter_icons.render.RenderOptions`.
        """
        return self._render_options

    @property
    def pad_factor(self) -> float:
        """Padding factor for icon rendering (0.0-1.0)."""
        return self._render_options.pad_factor

    @property
    def y_bias(self) -> float:
        """Vertical bias adjustment for icon rendering."""
        return self._render_options.y_bias

    @property
    def scale_to_fit(self) -> bool:
        """Whether to scale down glyphs that exceed the available space."""
        return self._render_options.scale_to_fit

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

    def asset_suffix(self, style: Optional[str] = None) -> str:
        """Return the filename suffix for this provider's per-style assets.

        Providers backed by one font file name their assets `glyphmap.json` and
        `metrics.json`; providers with a font per style append the style, as in
        `glyphmap-solid.json`.

        Args:
            style: Style name, or `None` for the provider's default.

        Returns:
            The empty string for single-file providers, otherwise `"-<style>"`.
        """
        if self.uses_single_file:
            return ""
        style_key = style or self._default_style
        if not style_key:
            raise ValueError(f"No style specified and no default_style configured for provider '{self._name}'.")
        return f"-{style_key}"

    def load_metrics(self, style: Optional[str] = None) -> dict[str, InkBounds]:
        """Load precomputed ink bounds for this provider's glyphs.

        The metrics file is what lets the renderer center on a glyph's true ink
        instead of Pillow's `getbbox`, which under-reports it. Generate it with
        `python -m tkinter_icons.tools.generate_metrics <package>`.

        A missing or unreadable file is not an error: providers published
        before metrics existed simply have none, and the renderer falls back to
        measuring at draw time.

        Args:
            style: Style name, or `None` for the provider's default.

        Returns:
            Icon name to `[left, top, width, height]` as font-size fractions.
            Empty when the provider ships no metrics for this style.
        """
        suffix = self.asset_suffix(style)
        mkey = (type(self), suffix)
        cached = self._metrics_cache_global.get(mkey)
        if cached is not None:
            return cached

        try:
            text = files(self.package).joinpath(f"metrics{suffix}.json").read_text(encoding="utf-8")
            metrics = json.loads(text)
            if not isinstance(metrics, dict):
                metrics = {}
        except (OSError, ValueError, ModuleNotFoundError):
            metrics = {}

        self._metrics_cache_global[mkey] = metrics
        return metrics

    # -----------------------------
    # Name Handling
    # -----------------------------
    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        return str(glyph_name).lower()

    def infer_style_from_name(self, name: str) -> Optional[str]:
        """Return the style `name` encodes, or `None` if it encodes none.

        A style is written into a name as whole hyphen-separated components -
        `"house-fill"`, `"shield-fill-check"` - so this matches components
        rather than substrings, and never at the start: Remix ships a `line`
        style *and* a glyph called `line-chart`, which is a chart, not a line.

        The longest match wins, which is what makes it independent of the
        order `style_list` happens to be in. Devicon has both `plain` and
        `plain-wordmark`, so `"aarch64-plain-wordmark"` is a wordmark whichever
        way round those two are declared.

        Args:
            name: The name as the caller wrote it.

        Returns:
            The style encoded in the name, or `None`.
        """
        if not self.has_styles:
            return None

        parts = name.split("-")
        best: Optional[str] = None
        for s in self.style_list:
            tokens = s.split("-")
            span = len(tokens)
            for i in range(1, len(parts) - span + 1):
                if parts[i:i + span] == tokens:
                    if best is None or len(s) > len(best):
                        best = s
                    break
        return best

    def _lookup_within_style(self, name: str, style: str) -> Optional[str]:
        """Find `name` in one style's table, or return `None`.

        The several spellings a name is accepted in, tried in order: as
        written, with the style appended, lowercased, and - where the name ends
        in the style - with that suffix taken off, since not every pack builds
        the style into its glyph names.
        """
        lookup = self._name_lookup.get(style, {})
        if not lookup:
            return None

        if name in lookup:
            return lookup[name]
        composite = f"{name}-{style}"
        if composite in lookup:
            return lookup[composite]
        formatted = self.format_glyph_name(name)
        if formatted in lookup:
            return lookup[formatted]

        suffix = f"-{style}"
        if name.endswith(suffix):
            base = name[: -len(suffix)]
            if base in lookup:
                return lookup[base]
            formatted_base = self.format_glyph_name(base)
            if formatted_base in lookup:
                return lookup[formatted_base]
        return None

    def candidate_styles(self, name: str, style: Optional[str] = None) -> tuple[str, ...]:
        """The styles a name may be drawn from, in the order they are tried.

        - An explicit `style` is the only candidate. Asking for one and getting
          another would make the argument decorative.
        - A name that spells a style out is the same: `"house-fill"` is a
          request for the `fill` cut, not a suggestion.
        - Otherwise every style is a candidate, default first.

        That last case is the one that changed. The default used to be the only
        place an unadorned name was looked for, which made it a gate rather
        than a preference: Font Awesome's `accusoft` is a real glyph in
        `brands` and nothing in the name points there, so it was unreachable
        without naming the style. Now the default is only what wins when a name
        exists in several styles, and the rest of `style_list` is tried after
        it rather than not at all.

        The default cannot simply be dropped, which is the obvious next
        thought. It is what settles the 13,658 names that live in more than one
        style - `MaterialIcon("home")`, `EvaIcon("activity")` - none of which
        writes a style into the name, so without it each is ambiguous and would
        have to raise.

        Args:
            name: The name as the caller wrote it.
            style: An explicit style, or `None`.

        Returns:
            Styles to search, in order. Empty for a provider with no styles.
        """
        if not self.has_styles:
            return ()
        if style is not None:
            return (style,)

        encoded = self.infer_style_from_name(name)
        if encoded is not None:
            return (encoded,)

        default = self.default_style
        if not default:
            return self.style_list
        return (default, *(s for s in self.style_list if s != default))

    def resolve_icon(self, name: str, style: Optional[str] = None) -> tuple[Optional[str], str]:
        """Resolve a name to the style it draws from and its glyph name.

        `resolve_icon_style` and `resolve_icon_name` are both views of this, so
        that they cannot answer differently. They used to be separate readings
        of the name and they did disagree - one matched a style anywhere in the
        name, the other only at the end - which selected one style's font and
        then looked the glyph up in another's table. The result drew a blank
        square with nothing raised anywhere.

        Args:
            name: The name as the caller wrote it.
            style: Style to resolve within, or `None` to work it out.

        Returns:
            `(style, glyph_name)`; the style is `None` for a provider that has
            none.

        Raises:
            ValueError: If the name does not resolve, or if it spells out a
                style that contradicts `style`.
        """
        if name == "none":
            # The sentinel for "deliberately no icon". No pack has a glyph
            # called this, so it is not resolved but passed through, and the
            # caller draws nothing. It has to live here rather than in
            # `resolve_icon_name` alone: `render_pil` calls this directly, so a
            # sentinel handled one level up would raise on the headless path
            # while the constructor accepted it - the exact split this method
            # exists to close.
            #
            # The style is worked out inline rather than through
            # `resolve_icon_style`, which delegates back here and would recurse.
            if not self.has_styles:
                return None, "none"
            return style or self.default_style, "none"

        if not self.has_styles:
            glyph = self._lookup_within_style(name, "base")
            if glyph is None:
                raise ValueError(f"'{name}' is not a valid icon for {self.name}.")
            return None, glyph

        encoded = self.infer_style_from_name(name)
        if style is not None and encoded is not None and style != encoded:
            raise ValueError(
                f"'{name}' is not valid for style '{style}' in {self.name}. Try style '{encoded}' or use an unsuffixed name."
            )

        candidates = self.candidate_styles(name, style)
        if not any(self._name_lookup.get(s) for s in candidates):
            # Name what was actually searched, for the same reason the sibling
            # below does. With no explicit style `candidates` is every style
            # the pack has, default first, so quoting `candidates[0]` accused
            # the *default* of being invalid while listing it as available:
            # `Style 'outline' is not valid for bootstrap. Available: ('fill',
            # 'outline')`. One candidate means the caller named it or wrote it
            # into the name, and then it is the right thing to quote.
            available = ", ".join(self.style_list)
            if len(candidates) == 1:
                raise ValueError(f"Style '{candidates[0]}' is not valid for {self.name}. Available: {available}.")
            raise ValueError(
                f"No style of {self.name} has any glyphs to resolve against; tried {', '.join(candidates)}."
            )

        for candidate in candidates:
            glyph = self._lookup_within_style(name, candidate)
            if glyph is not None:
                return candidate, glyph

        # Name what was actually searched. Reporting one style when several
        # were tried sends the reader off to look for a `style=` that would
        # fix it, and there isn't one.
        if len(candidates) == 1:
            raise ValueError(f"{name} not found in lookup for {self.name} in {candidates[0]} style.")
        raise ValueError(
            f"{name} not found in lookup for {self.name} in any of its styles: {', '.join(candidates)}."
        )

    def resolve_icon_style(self, name: str, style: Optional[str] = None):
        """Resolve a user-supplied icon name and style to the style it draws from.

        Args:
            name: The name as the caller wrote it.
            style: An explicit style, which wins outright, or `None` to work
                one out.

        Returns:
            The style to draw from, or `None` for a provider with no styles.
            A name that resolves nowhere falls back to the provider's default,
            so the caller gets a set to apply `on_missing` against rather than
            an exception from a function that does not otherwise raise.
        """
        if style is not None:
            return style
        if not self.has_styles:
            return None
        try:
            return self.resolve_icon(name)[0]
        except ValueError:
            return self.default_style

    def resolve_icon_name(self, name: str, style: Optional[str] = None) -> str:
        """Resolve a user-supplied icon name to the actual glyph name.

        A name may carry its own style, so the two arguments can disagree; the
        rules settle which one wins.

        - With an explicit `style`, resolution happens within that style only.
          A `name` spelling out a conflicting style - `"-fill"` against a
          requested `"outline"` - raises rather than silently preferring one.
        - A name that spells a style out is resolved within that style, for the
          same reason.
        - Otherwise the provider's default style is tried first and the rest
          after it, so a name that exists only in a non-default style still
          resolves. See `candidate_styles`.

        Args:
            name: The name as the caller wrote it, with or without a style.
            style: Style to resolve within, or `None` to work it out.

        Returns:
            The glyph name as it appears in this provider's glyph map.

        Raises:
            ValueError: If the name does not resolve, or if it spells out a
                style that contradicts `style`.
        """
        if name == "none":
            return "none"
        return self.resolve_icon(name, style)[1]

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
