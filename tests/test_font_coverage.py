"""No pack advertises a glyph its own font cannot draw.

`on_missing` guards the glyph *map*: a name that reaches a set with no entry
for it is handled by a documented policy. Nothing guarded the *font*. A name
the map advertises at a codepoint the font never carried resolved fine, looked
up fine, and drew `.notdef` — which in these fonts is empty, so it produced a
blank square with no exception and no warning, not even under
`on_missing="raise"`. 123 entries across `gmi` and `mat` were in that state
(#140).

The counts are deliberately not asserted here. A frozen "123" stops meaning
anything the moment the data is fixed, and the whole point is that it is now
zero and must stay zero. What is asserted is the invariant itself: **every
glyph-map entry's codepoint is present in that style's own font**. That check
would have failed the day the `gmi` generator was written.

Two things were quietly disagreeing the whole time and nothing compared them.
`metrics-outlined.json` has always held 2,191 entries against a glyph map
advertising 2,234, because ink measurement skips a glyph with no ink. And the
placement census recorded `glyphmap_entries` 123 above `drawing`, a gap that
cost a reviewer time as an unexplained discrepancy. Neither was a counting
error; both were this bug, reported by instruments nobody had pointed at it.

Coverage is checked with `fontTools`, not with the parser the library ships.
The shipped `sfnt.cmap_codepoints` is what the guard rests on, so verifying the
data with it would only prove the parser agrees with itself. `fontTools` is the
independent reading, and one test below holds the two against each other.

This needs every pack installed, which the CI matrix deliberately does not
guarantee, so each case skips when its pack is absent.
"""

from __future__ import annotations

import io
import warnings

import pytest

from tkinter_icons.icon import Icon
from tkinter_icons.iconset import IconSet, get_icon_set
from tkinter_icons.render import RenderOptions, clear_font_cache, font_codepoints
from tkinter_icons.sfnt import cmap_codepoints


def reference_codepoints(font_bytes: bytes) -> set[int]:
    """Every codepoint a font maps to a real glyph, read with `fontTools`.

    The import is in here rather than at module scope on purpose. A
    module-level `importorskip` takes the whole file with it, so one missing
    backport would silently retire every test in this file — including the ones
    that never needed `fontTools`. That is the same "a guard quietly stops
    covering what it names" failure this file exists to prevent, one level
    down. `tests/test_packs.py` guards `tomllib` the same way.
    """
    fonttools = pytest.importorskip("fontTools.ttLib", reason="fontTools reads the cmap")
    font = fonttools.TTFont(io.BytesIO(font_bytes), fontNumber=0, lazy=True)

    covered: set[int] = set()
    for subtable in font["cmap"].tables:
        # Platform 1 (Macintosh) addresses glyphs by byte value rather than by
        # codepoint, so it would report coverage of U+0000-U+00FF that has
        # nothing to do with what a glyph map holds.
        if subtable.platformID not in (0, 3):
            continue
        covered |= {
            codepoint
            for codepoint, glyph_name in subtable.cmap.items()
            if font.getGlyphID(glyph_name) != 0
        }
    return covered


def every_installed_style(registry):
    """Yield `(pack, style, icon_set)` for every style of every installed pack."""
    for name in sorted(registry.names()):
        pack = registry.get_provider(name)
        for style in pack.style_list or [None]:
            yield name, style, get_icon_set(pack, style)


def style_ids(registry) -> list[str]:
    return [f"{name}:{style or 'default'}" for name, style, _ in every_installed_style(registry)]


class TestNoPackAdvertisesAGlyphItsFontLacks:
    """The invariant. One case per installed style, so a failure names the style."""

    def test_every_glyphmap_entry_is_in_the_font(self, registry):
        offenders = {}
        for pack, style, icon_set in every_installed_style(registry):
            covered = reference_codepoints(icon_set.font_bytes)
            absent = sorted(
                name
                for name, character in icon_set.glyphs.items()
                if not all(ord(char) in covered for char in character)
            )
            if absent:
                offenders[f"{pack}:{style or 'default'}"] = absent

        assert not offenders, (
            "These packs advertise names their own font cannot draw, so each one renders "
            "as a blank square with no error:\n"
            + "\n".join(
                f"  {where}: {len(names)} name(s), e.g. {', '.join(names[:6])}"
                for where, names in sorted(offenders.items())
            )
            + "\nFix the pack's generator, then rebuild its glyph map — scrubbing the data "
            "alone means the next regeneration reintroduces every one of them."
        )

    def test_what_a_set_reports_is_what_it_can_draw(self, registry):
        """`len`, membership and `glyph()` all mean "can be drawn", and agree.

        `glyphs` is the raw advertised map and is allowed to be larger in
        principle — that is what makes the drawable count a distinct number.
        For every shipped pack the two are equal, and that equality is the
        first test above restated through the public surface.
        """
        for pack, style, icon_set in every_installed_style(registry):
            where = f"{pack}:{style or 'default'}"
            assert len(icon_set) == len(icon_set.glyphs), where
            for name in icon_set.glyphs:
                assert name in icon_set, f"{where}: {name!r}"
                assert icon_set.glyph(name) is not None, f"{where}: {name!r}"


class TestTheBrowserHasNoBlankTiles:
    """The user-visible form of the invariant, stated where a user meets it.

    The shipped browser lists what `build_name_lookup` advertises, and it drew
    every one of these as an empty tile. The check above is about glyph maps;
    this one is about what someone actually sees, and it goes through the same
    lookup the browser does rather than re-deriving the names.

    Note which side of that lookup is asked. `build_name_lookup()[style]` maps
    a *display* name to a *glyph* name, and looking up the display name finds
    nothing for 46,479 perfectly good entries — the same class of mistake as
    handing `render_glyph` a name where it wants a character.
    """

    def test_every_name_the_browser_lists_can_be_drawn(self, registry):
        offenders = {}
        for pack in sorted(registry.names()):
            provider = registry.get_provider(pack)
            for style, names in provider.build_name_lookup().items():
                icon_set = get_icon_set(provider, None if style == "base" else style)
                blank = sorted(
                    display
                    for display, glyph_name in names.items()
                    if icon_set.glyph(glyph_name) is None
                )
                if blank:
                    offenders[f"{pack}:{style}"] = blank

        assert not offenders, (
            "The browser would draw these as empty tiles:\n"
            + "\n".join(
                f"  {where}: {len(names)} name(s), e.g. {', '.join(names[:6])}"
                for where, names in sorted(offenders.items())
            )
        )


class TestTheShippedCmapReaderAgreesWithFontTools:
    """The guard is only as good as the parser underneath it.

    The base package depends on Pillow and `typing-extensions`, and Pillow
    cannot report which codepoints a font carries — it draws `.notdef` and says
    nothing. So `sfnt.py` parses the `cmap` table directly rather than adding a
    third runtime dependency. That parser is worth holding against the library
    that does this properly, across every font the project ships: between them
    the packs cover subtable formats 0, 4, 6 and 12, and both the BMP and the
    supplementary private-use area that Material Design Icons lives in.
    """

    def test_the_parser_reproduces_fonttools_on_every_shipped_font(self, registry):
        for pack, style, icon_set in every_installed_style(registry):
            where = f"{pack}:{style or 'default'}"
            parsed = cmap_codepoints(icon_set.font_bytes)
            assert parsed is not None, f"{where}: no readable cmap"
            assert parsed == reference_codepoints(icon_set.font_bytes), where

    def test_an_unreadable_font_reports_unknown_rather_than_empty(self):
        """The fail-open, which is the difference between a guard and an outage.

        An empty set would claim the font contains no codepoints at all, which
        would blank or raise on every icon in the pack. `None` says the check
        learned nothing, and callers draw the glyph as they always did.
        """
        assert cmap_codepoints(b"") is None
        assert cmap_codepoints(b"not a font at all") is None
        assert cmap_codepoints(b"\x00\x01\x00\x00" + b"\xff" * 64) is None

    def test_coverage_is_parsed_once_per_font(self, registry):
        """The result is cached, so asking before every glyph costs one parse."""
        _, _, icon_set = next(iter(every_installed_style(registry)))
        first = font_codepoints(icon_set.font_key, icon_set.font_bytes)
        assert first is font_codepoints(icon_set.font_key, icon_set.font_bytes)

        clear_font_cache()
        rebuilt = font_codepoints(icon_set.font_key, icon_set.font_bytes)
        assert rebuilt is not first and rebuilt == first


class TestAFontAbsentCodepointObeysOnMissing:
    """Case 3 joins the existing policy rather than growing a new one.

    Built by hand, because after the data fix no shipped pack is in this state
    any more — which is the point, and also why this cannot be written against
    a real pack.
    """

    @pytest.fixture
    def set_that_lies(self, registry) -> IconSet:
        """A set whose map advertises a codepoint its font does not carry."""
        _, _, real = next(iter(every_installed_style(registry)))
        absent = 0x10FFFD  # a supplementary private-use codepoint no icon font maps
        assert absent not in (cmap_codepoints(real.font_bytes) or set())
        return IconSet(
            id="lies:default",
            font_bytes=real.font_bytes,
            glyphs={"not-in-the-font": chr(absent)},
            options=RenderOptions(),
        )

    def test_the_set_does_not_claim_to_have_it(self, set_that_lies):
        assert set_that_lies.glyph("not-in-the-font") is None
        assert "not-in-the-font" not in set_that_lies
        assert len(set_that_lies) == 0
        # The raw advertised map still holds it — that gap is the whole finding.
        assert "not-in-the-font" in set_that_lies.glyphs

    def test_transparent_is_still_the_default(self, set_that_lies):
        image = Icon.render_pil("not-in-the-font", icon_set=set_that_lies)
        assert image.getbbox() is None

    def test_raise_actually_raises(self, set_that_lies):
        Icon.on_missing = "raise"
        with pytest.raises(KeyError):
            Icon.render_pil("not-in-the-font", icon_set=set_that_lies)

    def test_warn_actually_warns(self, set_that_lies):
        Icon.on_missing = "warn"
        with pytest.warns(UserWarning):
            Icon.render_pil("not-in-the-font", icon_set=set_that_lies)

    def test_the_message_names_the_font_rather_than_the_name(self, set_that_lies):
        """A user who mistyped and a user who hit a broken pack need different answers.

        Both reasons reach `_report_missing`, and reporting them identically
        sends someone to check their spelling when the spelling is right and
        the pack's data is wrong.
        """
        Icon.on_missing = "raise"
        with pytest.raises(KeyError) as absent_from_font:
            Icon.render_pil("not-in-the-font", icon_set=set_that_lies)
        with pytest.raises(KeyError) as absent_from_map:
            Icon.render_pil("no-such-name", icon_set=set_that_lies)

        assert "font does not contain" in str(absent_from_font.value)
        assert "U+10FFFD" in str(absent_from_font.value)
        assert "font does not contain" not in str(absent_from_map.value)

    def test_a_real_glyph_in_the_same_set_still_draws(self, registry, set_that_lies):
        """The guard rejects one entry, not the font it came from."""
        _, _, real = next(iter(every_installed_style(registry)))
        drawable = next(
            name for name in sorted(real.glyphs) if real.glyph(name) is not None
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            image = Icon.render_pil(drawable, icon_set=real, size=32)
        assert image.getbbox() is not None
