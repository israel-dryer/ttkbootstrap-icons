"""Immutable per-(provider, style) icon data, built once and shared.

An `IconSet` is everything the renderer needs to draw any glyph in one style of
one provider: the font bytes, the name-to-character map, the ink metrics, and
the render options. It replaces the mutable class-level state that used to live
on `Icon`, where whichever provider initialized last owned the glyph map and
using two providers at once meant reading around the globals.

Icon sets are cached by id, so building the same one twice is free and two
providers can be live at the same time without interfering.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Mapping, Optional, TYPE_CHECKING

from .render import InkBounds, RenderOptions, font_codepoints

if TYPE_CHECKING:
    from .providers import BaseFontProvider


@dataclass(frozen=True)
class IconSet:
    """One provider's glyphs in one style, ready to render.

    Attributes:
        id: Stable identity, `"<provider>:<style>"`. Used as the cache key and
            as part of every rendered-image cache key.
        font_bytes: The raw font file backing this style.
        glyphs: Icon name to the single character that draws it, exactly as the
            provider's glyphmap file declares it. Ask `glyph()` rather than
            reading this directly unless you specifically want the advertised
            map — an entry here is not proof the font carries the codepoint.
        metrics: Icon name to normalized ink bounds, from the provider's
            `metrics.json`. Empty when the provider ships none, in which case
            the renderer measures at draw time.
        options: The provider's default render options for this style.
    """

    id: str
    font_bytes: bytes
    glyphs: Mapping[str, str]
    metrics: Mapping[str, InkBounds] = field(default_factory=dict)
    options: RenderOptions = RenderOptions()

    @property
    def font_key(self) -> str:
        """Cache key identifying this set's font file."""
        return self.id

    def glyph(self, name: str) -> Optional[str]:
        """Return the character that draws `name`, or `None` if this set cannot draw it.

        A name is undrawable two ways, and both answer `None` so that callers
        apply one policy rather than two. Either the glyph map has no entry for
        it, or the entry points at a codepoint **the font does not contain** —
        which used to render as a silent blank square, because Pillow draws
        `.notdef` for an absent codepoint and in most icon fonts `.notdef` is
        empty (#140).

        This is the single place that question is answered. `Icon.render_pil`
        and the Tk render path both come through here, and the reason they do
        is #115: the same name answered two different ways by two entry points
        is the defect that keeps recurring in this library.
        """
        character = self.glyphs.get(name)
        if character is None or not self.can_draw(character):
            return None
        return character

    def can_draw(self, character: str) -> bool:
        """Whether this set's font contains every codepoint in `character`.

        Returns `True` when the font's character map cannot be read, which is
        the deliberate fail-open: an unparseable font is one this check knows
        nothing about, and a guard that cannot read a font must not be the
        thing that stops it rendering.
        """
        codepoints = font_codepoints(self.font_key, self.font_bytes)
        if codepoints is None:
            return True
        return all(ord(char) in codepoints for char in character)

    def ink(self, name: str) -> Optional[InkBounds]:
        """Return precomputed ink bounds for `name`, or `None` to measure live."""
        return self.metrics.get(name)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.glyph(name) is not None

    @cached_property
    def _drawable_count(self) -> int:
        """How many glyph-map entries the font actually carries, counted once.

        Memoized because every input is fixed for the life of the set: the font
        bytes and the glyph map are both frozen, and re-parsing the same bytes
        after `clear_font_cache()` yields the same coverage. Counting costs one
        `can_draw` per entry — about 5 ms for the largest pack — and answering
        `len()` or `bool()` is not worth paying that more than once.

        `cached_property` writes straight into `__dict__`, which is why it works
        on a frozen dataclass where an ordinary attribute assignment would
        raise. It is not an annotated class attribute, so it is not a field.
        """
        return sum(1 for character in self.glyphs.values() if self.can_draw(character))

    def __len__(self) -> int:
        """How many names this set can actually draw.

        Not `len(self.glyphs)`. Membership, `glyph()` and this count all mean
        the same thing on purpose — a set that reports a name it cannot draw is
        the bug this class was changed to prevent. `glyphs` is still the raw
        advertised map for tooling that wants to compare the two; every shipped
        pack has them equal, which `tests/test_font_coverage.py` asserts.
        """
        return self._drawable_count

    def __bool__(self) -> bool:
        """Whether this set can draw anything at all.

        Exactly `len(self) > 0`, and defined only so it can stop at the first
        drawable glyph instead of counting them all — without it Python falls
        back to `__len__`, which is correct but scans the whole map the first
        time it is asked.

        The shortcut has to be over what the font carries, not over `glyphs`.
        Stopping at "the map is non-empty" would be faster still and would make
        a set call itself truthy while `len()` reported 0, which is the same
        set answering one question two ways — the defect this class keeps
        having (#115, #140). Both answers come from `can_draw` for that reason.

        Note this does not rescue `icon_set or fallback`: a set that genuinely
        draws nothing is still falsy, which is why `Icon.render_pil` selects on
        `is None`. Any `or` over an object with `__len__` is that bug waiting.
        """
        return any(self.can_draw(character) for character in self.glyphs.values())


_icon_sets: dict[str, IconSet] = {}


def icon_set_id(provider: "BaseFontProvider", style: Optional[str] = None) -> str:
    """Return the cache id for a provider/style pair."""
    return f"{provider.name}:{style or 'default'}"


def get_icon_set(provider: "BaseFontProvider", style: Optional[str] = None) -> IconSet:
    """Build (or return the cached) `IconSet` for a provider and style.

    Args:
        provider: The provider to load assets from.
        style: Style name, or `None` for the provider's default.

    Returns:
        The shared `IconSet`. Repeat calls return the same object.
    """
    set_id = icon_set_id(provider, style)
    cached = _icon_sets.get(set_id)
    if cached is not None:
        return cached

    font_bytes, glyphmap_json = provider.load_assets(style=style)
    icon_set = IconSet(
        id=set_id,
        font_bytes=font_bytes,
        glyphs=parse_glyphmap(json.loads(glyphmap_json)),
        metrics=provider.load_metrics(style=style),
        options=provider.render_options,
    )
    _icon_sets[set_id] = icon_set
    return icon_set


def registered_icon_sets() -> Mapping[str, IconSet]:
    """Return every icon set built so far, keyed by id."""
    return dict(_icon_sets)


def clear_icon_sets() -> None:
    """Drop every cached icon set, forcing the next use to rebuild."""
    _icon_sets.clear()


def parse_glyphmap(data: Any) -> dict[str, str]:
    """Normalize any supported glyphmap shape into `{name: character}`.

    Three layouts are in the wild across the provider packages:

    - a flat map of name to codepoint, `{"house": "EA01"}`
    - a map of name to detail object, `{"house": {"unicode": "EA01"}}`
    - a list of detail objects, `[{"name": "house", "unicode": "EA01"}]`

    Codepoints may be hex strings or integers. Entries that are malformed or
    missing a codepoint are skipped rather than failing the whole map — one bad
    row in a generated asset should not take down every icon in the package.

    Args:
        data: Parsed JSON from a provider's glyphmap file.

    Returns:
        Icon name to the character that draws it.

    Raises:
        TypeError: If `data` is neither a list nor a dict.
    """
    if isinstance(data, list):
        return _parse_entries(
            (entry.get("name"), entry.get("unicode"))
            for entry in data
            if isinstance(entry, dict)
        )

    if isinstance(data, dict):
        try:
            sample = next(iter(data.values()))
        except StopIteration:
            return {}

        if isinstance(sample, dict):
            return _parse_entries(
                (name, detail.get("unicode"))
                for name, detail in data.items()
                if isinstance(detail, dict)
            )
        return _parse_entries(data.items())

    raise TypeError(f"glyphmap must be a list or dict, got {type(data).__name__}")


def _parse_entries(pairs) -> dict[str, str]:
    """Build the name-to-character map from (name, codepoint) pairs."""
    mapping: dict[str, str] = {}
    for name, codepoint in pairs:
        if not name or codepoint is None:
            continue
        try:
            value = int(codepoint, 16) if isinstance(codepoint, str) else int(codepoint)
            mapping[str(name).strip()] = chr(value)
        except (TypeError, ValueError):
            continue
    return mapping


__all__ = [
    "IconSet",
    "clear_icon_sets",
    "get_icon_set",
    "icon_set_id",
    "parse_glyphmap",
    "registered_icon_sets",
]