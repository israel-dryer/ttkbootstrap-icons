"""Reaching a pack's non-default styles, and reading a style out of a name.

Two defects sat behind #115, and they are the same defect seen from either
end. A pack's icon class takes `style`; `render_pil` did not, so a name that
exists only in a non-default style — Font Awesome's brand marks, most of
Fluent's `light` cut — was reachable from the constructor and unreachable
headlessly. And the two functions that read a style out of a name disagreed:
`resolve_icon_style` matched `-<style>` as a substring anywhere,
`resolve_icon_name` matched it only as a suffix. They agreed on most names by
accident of the order `style_list` happened to be declared in.

Where they disagreed the failure was silent in both directions. Bootstrap's
`shield-fill-check` is a real glyph in the `fill` style, named that way on
purpose — `build_name_lookup` singles it out in a comment. The suffix rule
could not see the `fill`, so the constructor raised on a name the pack ships,
while `render_pil` drew it anyway, because Bootstrap keeps every style in one
font file and the unresolved name happened to be a glyph name. One entry point
failed on a good name; the other succeeded for the wrong reason.

So the checks here are of two kinds. The rule itself is pinned against
synthetic providers, because the cases that separate a right rule from a wrong
one are specific shapes — a style word inside a name, a style word that is a
prefix of another style, a style word at the very start — and each of those is
one real pack's data. The consequences are then checked against every pack
installed, over every name in every style rather than the default style only:
a claim about the whole library measured over half of it was how the placement
census went wrong once already.
"""

from __future__ import annotations

import importlib

import pytest

from tkinter_icons.iconset import get_icon_set
from tkinter_icons.packs import KNOWN_PACKS
from tkinter_icons.providers import BaseFontProvider

INSTALLED = [pack for pack in KNOWN_PACKS if pack.is_installed]

#: How many candidate names a pack gets to offer before a style is reported as
#: drawing nothing. Icon fonts do contain blank glyphs, so one transparent
#: render is not evidence of a bug; a whole run of them is.
INK_ATTEMPTS = 12


class FakeProvider(BaseFontProvider):
    """A provider with styles and no assets, for testing name parsing alone.

    `build_name_lookup` is overridden because the real one reads a glyphmap off
    disk, and none of these tests resolve a name — they only ask which style a
    name encodes.
    """

    def __init__(self, styles, default=None):
        super().__init__(
            name="fake",
            package="tkinter_icons",
            styles={style: {} for style in styles},
            default_style=default or (styles[0] if styles else None),
        )

    def build_name_lookup(self):
        return {}


def icon_class(pack):
    return getattr(importlib.import_module(pack.module), pack.icon_class)


def provider_for(pack):
    module = importlib.import_module(f"{pack.module}.provider")
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class in {pack.module}.provider")


def styled_packs():
    """Installed packs that have styles at all, since only those can differ."""
    return [pack for pack in INSTALLED if provider_for(pack).has_styles]


def names_by_style(provider):
    """Every user-facing name the provider accepts, grouped by style.

    Read off `_name_lookup` rather than the glyph maps: it is what resolution
    consults, so it is the set of names a user can legitimately write.
    """
    return {style: provider._name_lookup.get(style, {}) for style in provider.style_list}


class TestAStyleIsWholeComponentsOfAName:
    """The inference rule, on the four shapes that tell the rules apart."""

    def test_a_style_is_found_in_the_middle_of_a_name(self):
        """Bootstrap's `shield-fill-check`: the suffix rule could not see it."""
        provider = FakeProvider(("fill", "outline"), default="outline")
        assert provider.infer_style_from_name("shield-fill-check") == "fill"
        assert provider.infer_style_from_name("house-fill") == "fill"
        assert provider.infer_style_from_name("shield-check") is None

    def test_a_style_word_starting_a_name_is_not_a_style(self):
        """Remix ships a `line` style and a `line-chart` glyph, which is a chart."""
        provider = FakeProvider(("line", "fill"), default="fill")
        assert provider.infer_style_from_name("line-chart") is None
        assert provider.infer_style_from_name("line") is None
        assert provider.infer_style_from_name("line-chart-fill") == "fill"
        assert provider.infer_style_from_name("line-fill") == "fill"

    def test_a_partial_component_is_not_a_style(self):
        """`-fill` must not match inside `filled`, or Fluent reads as Bootstrap."""
        provider = FakeProvider(("regular", "filled"), default="regular")
        assert provider.infer_style_from_name("access-time-filled") == "filled"
        provider = FakeProvider(("fill", "outline"), default="outline")
        assert provider.infer_style_from_name("access-time-filled") is None

    @pytest.mark.parametrize(
        "styles",
        [
            ("plain", "plain-wordmark", "original", "original-wordmark"),
            ("original-wordmark", "original", "plain-wordmark", "plain"),
        ],
        ids=["short-first", "long-first"],
    )
    def test_the_longest_style_wins_whatever_the_declaration_order(self, styles):
        """Devicon's four styles, where two are prefixes of the other two.

        The old rules both scanned `style_list` in order and took the first
        hit, so which one they found depended on how the pack happened to
        declare them. This is what "they agree by accident" meant.
        """
        provider = FakeProvider(styles, default="plain")
        assert provider.infer_style_from_name("aarch64-plain-wordmark") == "plain-wordmark"
        assert provider.infer_style_from_name("aarch64-plain") == "plain"
        assert provider.infer_style_from_name("aarch64-original-wordmark") == "original-wordmark"

    def test_a_provider_without_styles_never_infers_one(self):
        provider = FakeProvider(())
        assert provider.infer_style_from_name("anything-fill") is None


class TestTheTwoResolversReadANameTheSameWay:
    """`resolve_icon_style` and `resolve_icon_name` must agree, on every name.

    They pick the icon set and the glyph within it respectively, so a
    disagreement means drawing from a set that does not contain the glyph that
    was resolved — a blank square where the pack has the icon, with nothing
    raised anywhere.
    """

    @pytest.mark.parametrize("pack", styled_packs(), ids=lambda p: p.extra)
    def test_a_name_that_spells_out_its_style_resolves_as_written(self, pack):
        """The class of name the alignment fixes, over every pack's own data.

        Restricted to names that spell their style out, and that restriction is
        the point rather than a convenience: a name spelling nothing out — Font
        Awesome's `accusoft` — is unreachable without `style=` by construction,
        which is a different claim, checked below. A name that does has said
        everything needed to find it, so failing to find it is the two readers
        disagreeing.

        **Which names those are is read off the lookup tables, not off
        `infer_style_from_name`.** Asking the rule under test which names it
        considers styled makes the check self-fulfilling: the suffix-only rule
        does not think `shield-fill-check` names a style at all, so defining
        the population that way excused it from the census and the whole thing
        passed green against the code it was written to catch. Membership is
        `f"-{style}" in name` against the style whose table holds the name —
        crude, fixed, and answering the same 46,165 names whichever rule is
        installed.
        """
        provider = provider_for(pack)
        sets = {style: get_icon_set(provider, style) for style in provider.style_list}

        checked = 0
        disagreed = []
        for style, lookup in names_by_style(provider).items():
            for name in lookup:
                if f"-{style}" not in name:
                    continue
                checked += 1
                try:
                    glyph = provider.resolve_icon_name(name)
                except ValueError as exc:
                    disagreed.append((name, style, str(exc)))
                    continue
                if sets[provider.resolve_icon_style(name)].glyph(glyph) is None:
                    disagreed.append((name, style, f"{glyph} absent from the style chosen"))

        assert not disagreed, (
            f"{len(disagreed)} of {checked} name(s) in {pack.extra} spell out a style "
            f"and still do not draw: {disagreed[:5]}"
        )
        assert checked, f"no name in {pack.extra} spells out a style, so this checked nothing"


class TestEveryNameIsReachableWithAnExplicitStyle:
    """The claim `style=` exists to make true.

    867 names across seven packs could not be reached by name at all, and the
    ones in a non-default style had no headless spelling either. The census
    runs over every style rather than each pack's default, because the names in
    question are by definition the ones outside the default — measuring over
    defaults would exclude exactly the population under test.
    """

    @pytest.mark.parametrize("pack", styled_packs(), ids=lambda p: p.extra)
    def test_every_name_resolves_within_its_own_style(self, pack):
        provider = provider_for(pack)
        sets = {style: get_icon_set(provider, style) for style in provider.style_list}

        unreachable = []
        for style, lookup in names_by_style(provider).items():
            for name in lookup:
                try:
                    glyph = provider.resolve_icon_name(name, style)
                except ValueError as exc:
                    unreachable.append((name, style, str(exc)))
                    continue
                if sets[style].glyph(glyph) is None:
                    unreachable.append((name, style, "resolved but absent"))

        assert not unreachable, (
            f"{len(unreachable)} name(s) in {pack.extra} cannot be drawn even "
            f"when their style is named: {unreachable[:5]}"
        )

    @pytest.mark.parametrize("pack", styled_packs(), ids=lambda p: p.extra)
    def test_render_pil_draws_ink_for_every_style(self, pack):
        """End to end, on the raster.

        Asserting on ink rather than on the absence of an exception: an
        unresolvable name comes back as a fully transparent image, so a check
        that only watches for a raise passes on a typo.
        """
        cls = icon_class(pack)
        provider = provider_for(pack)

        for style, lookup in names_by_style(provider).items():
            drawn = None
            for name in list(lookup)[:INK_ATTEMPTS]:
                image = cls.render_pil(name, size=32, style=style)
                if image.getchannel("A").getbbox() is not None:
                    drawn = name
                    break
            assert drawn is not None, (
                f"none of the first {INK_ATTEMPTS} names in {pack.extra}'s "
                f"{style!r} style drew any ink through render_pil(style=...)"
            )

    def test_a_name_only_in_a_non_default_style_needs_no_argument(self):
        """The worked example from the issue, both ways round.

        Font Awesome's brand marks carry no style token, so nothing in the name
        can lead a resolver to `brands`. While the default style gated
        resolution this was the silent transparent square that made 867 real
        icons look like typos; now the default is only a preference, and the
        name finds the one style that has it.
        """
        pack = next((p for p in INSTALLED if p.extra == "fontawesome"), None)
        if pack is None:
            pytest.skip("the fontawesome pack is not installed")
        cls = icon_class(pack)

        assert cls.render_pil("accusoft", size=32).getchannel("A").getbbox() is not None
        assert cls.render_pil("accusoft", size=32, style="brands").getchannel("A").getbbox() is not None
        assert cls("accusoft", size=32).to_pil().getchannel("A").getbbox() is not None

    @pytest.mark.parametrize("pack", styled_packs(), ids=lambda p: p.extra)
    def test_no_name_a_pack_ships_is_out_of_reach(self, pack):
        """The claim the default-as-preference change makes true.

        Every name in every style, resolved with nothing but the name — which
        is what a user writes. Before, a name absent from the default style and
        silent about its own was unreachable however it was spelled.
        """
        provider = provider_for(pack)
        sets = {style: get_icon_set(provider, style) for style in provider.style_list}

        unreachable = []
        for lookup in names_by_style(provider).values():
            for name in lookup:
                try:
                    resolved_style, glyph = provider.resolve_icon(name)
                except ValueError as exc:
                    unreachable.append((name, str(exc)))
                    continue
                if sets[resolved_style].glyph(glyph) is None:
                    unreachable.append((name, f"{glyph} absent from {resolved_style}"))

        assert not unreachable, (
            f"{len(unreachable)} name(s) in {pack.extra} cannot be drawn from the "
            f"name alone: {unreachable[:5]}"
        )


class TestTheTwoEntryPointsLookNamesUpTheSameWay:
    """What a user expects, and what #115 was really about.

    `PackIcon(name)` and `PackIcon.render_pil(name)` are two doors onto one
    library, so a name means the same thing at both. It did not: each read the
    name with its own rules, and the disagreements were silent — a blank square
    from one, a `ValueError` from the other, for a name the pack ships.

    Both now go through `BaseFontProvider.resolve_icon`, which returns the
    style and the glyph together. That is what makes this structural rather
    than a convention two functions have to keep to.

    Failure matches too: a name the pack cannot resolve raises from both.
    `on_missing` keeps the case it was written for, where a name reaches a set
    without having been resolved against it — see `test_pack_icon_surface`.
    """

    #: Icons rendered per style to compare pixels. Resolution is checked over
    #: every name — it is dictionary lookups — but rendering all 113,399 would
    #: cost more than the rest of the suite put together, so the raster check
    #: is a bounded sample and says so.
    PIXEL_SAMPLE = 5

    @pytest.mark.parametrize("pack", INSTALLED, ids=lambda p: p.extra)
    def test_every_name_resolves_identically(self, pack):
        cls = icon_class(pack)
        provider = provider_for(pack)

        checked = 0
        mismatched = []
        for style in provider.style_list or ("base",):
            for name in provider._name_lookup.get(style, {}):
                checked += 1
                try:
                    through_constructor = cls(name, 32).name
                except ValueError:
                    through_constructor = "<raised>"
                try:
                    through_render_pil = provider.resolve_icon(name)[1]
                except ValueError:
                    through_render_pil = "<raised>"
                if through_constructor != through_render_pil:
                    mismatched.append((name, through_constructor, through_render_pil))

        assert not mismatched, (
            f"{len(mismatched)} of {checked} name(s) in {pack.extra} mean different "
            f"things to the constructor and to render_pil: {mismatched[:5]}"
        )
        assert checked, f"{pack.extra} offered no names, so this checked nothing"

    @pytest.mark.parametrize("pack", INSTALLED, ids=lambda p: p.extra)
    def test_they_draw_the_same_pixels(self, pack):
        cls = icon_class(pack)
        provider = provider_for(pack)

        for style in provider.style_list or ("base",):
            for name in list(provider._name_lookup.get(style, {}))[: self.PIXEL_SAMPLE]:
                through_constructor = cls(name, 32).to_pil()
                through_render_pil = cls.render_pil(name, 32)
                assert through_constructor.tobytes() == through_render_pil.tobytes(), (
                    f"{pack.extra}:{style} {name!r} draws differently depending on "
                    f"which entry point asked for it"
                )


class TestAnExplicitStyleIsNeverSilentlyDropped:
    """Asking for a style you cannot have is an error, not a quiet substitution.

    Naming a style narrows resolution to it and nothing else, so a name the
    pack does not draw that way fails rather than falling back to a style that
    does. Dropping the argument would be worse than drawing nothing: the icon
    set follows the style, so the caller would get a real glyph in the wrong
    cut and no indication of it.
    """

    def test_a_style_the_name_contradicts_raises(self):
        pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
        if pack is None:
            pytest.skip("the bootstrap pack is not installed")
        cls = icon_class(pack)
        with pytest.raises(ValueError, match="not valid for style"):
            cls.render_pil("house-fill", size=32, style="outline")

    def test_a_name_absent_from_the_named_style_raises(self):
        pack = next((p for p in INSTALLED if p.extra == "fontawesome"), None)
        if pack is None:
            pytest.skip("the fontawesome pack is not installed")
        cls = icon_class(pack)
        with pytest.raises(ValueError, match="solid"):
            cls.render_pil("accusoft", size=32, style="solid")

    @pytest.mark.parametrize("pack", INSTALLED, ids=lambda p: p.extra)
    def test_the_none_sentinel_draws_nothing_rather_than_raising(self, pack):
        """`"none"` means "deliberately no icon", and is not a name to resolve.

        No pack has a glyph called this; it is passed through so the caller
        draws an empty square. It nearly broke when `render_pil` started
        raising: the sentinel lived in `resolve_icon_name`, one level above the
        `resolve_icon` that `render_pil` now calls, so the constructor kept
        accepting it while the headless path raised on it — reintroducing the
        exact split this work exists to close, on the one name guaranteed not
        to be a typo.
        """
        cls = icon_class(pack)
        provider = provider_for(pack)

        assert provider.resolve_icon_name("none") == "none"
        assert provider.resolve_icon("none")[1] == "none"
        assert cls("none", size=16).name == "none"

        image = cls.render_pil("none", size=16)
        assert image.size == (16, 16)
        assert image.getchannel("A").getbbox() is None, "the sentinel drew ink"

    def test_a_typo_raises_whether_or_not_a_style_was_named(self):
        """Searching every style makes a typo fail against all of them.

        A name that resolves nowhere means the pack has no such icon under any
        style, which is the caller's mistake either way — so the error does not
        depend on whether `style` was passed.
        """
        pack = next((p for p in INSTALLED if p.extra == "fontawesome"), None)
        if pack is None:
            pytest.skip("the fontawesome pack is not installed")
        cls = icon_class(pack)
        with pytest.raises(ValueError, match="accusofft"):
            cls.render_pil("accusofft", size=32)
        with pytest.raises(ValueError, match="accusofft"):
            cls.render_pil("accusofft", size=32, style="brands")

    def test_a_style_with_no_provider_to_resolve_it_raises(self):
        """`Icon` itself takes resolved glyph names, so it has no style to apply."""
        from tkinter_icons.icon import Icon

        with pytest.raises(ValueError, match="needs a provider"):
            Icon.render_pil("house", size=16, style="fill")

    def test_a_style_alongside_an_explicit_icon_set_raises(self):
        """The set is already chosen, so the style could only be ignored."""
        pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
        if pack is None:
            pytest.skip("the bootstrap pack is not installed")
        cls = icon_class(pack)
        outline = get_icon_set(provider_for(pack), "outline")
        with pytest.raises(ValueError, match="needs a provider"):
            cls.render_pil("house", size=16, style="fill", icon_set=outline)


class TestTheConstructorTakesTheNamesThePackShips:
    """The other half of the disagreement, which raised on a real glyph."""

    def test_a_mid_name_style_constructs(self):
        pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
        if pack is None:
            pytest.skip("the bootstrap pack is not installed")
        cls = icon_class(pack)
        icon = cls("shield-fill-check", size=32)
        assert icon.to_pil().getchannel("A").getbbox() is not None

    def test_a_longer_style_wins_over_the_one_it_starts_with(self):
        """Devicon's real data, where the old substring rule answered `plain`.

        Devicon keeps every style in one font file, so this never drew the
        wrong glyph — `resolve_icon_name` was already reading the suffix
        correctly and the set it picked contained everything either way. It is
        pinned because it is the pack the ordering hazard is real in: a
        multi-file pack shaped like this would have drawn blank.
        """
        pack = next((p for p in INSTALLED if p.extra == "devicon"), None)
        if pack is None:
            pytest.skip("the devicon pack is not installed")
        provider = provider_for(pack)
        assert provider.resolve_icon_style("aarch64-plain-wordmark") == "plain-wordmark"

        icon = icon_class(pack)("aarch64-plain-wordmark", size=32)
        assert icon.to_pil().getchannel("A").getbbox() is not None
