"""The surface every pack's icon class is expected to have.

Both gaps these cover were found by running what the documentation claims,
not by a failing build — which is the point of pinning them here.

`RenderOptions` is public API and the documented way to change how an icon
draws, but no pack class took it, so the only ways in were `Icon.render_pil`
or the base `Icon` (which raises unless a provider is already active).

`render_pil` read `Icon._icon_set_current`, a `ClassVar` shared by every
subclass, so `MaterialIcon.render_pil("home")` drew a Material icon only if
something else had constructed one first. In a fresh process it raised.
"""

from __future__ import annotations

import importlib
import inspect
import subprocess
import sys

import pytest

from tkinter_icons.icon import Icon
from tkinter_icons.packs import KNOWN_PACKS
from tkinter_icons.render import RenderOptions

INSTALLED = [pack for pack in KNOWN_PACKS if pack.is_installed]


def icon_class(pack):
    return getattr(importlib.import_module(pack.module), pack.icon_class)


@pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
class TestEveryPackClass:
    """Parametrized over the catalog, so a new pack has to comply too."""

    def test_accepts_options(self, pack):
        if not pack.is_installed:
            pytest.skip(f"{pack.distribution} is not installed")
        parameters = inspect.signature(icon_class(pack).__init__).parameters
        assert "options" in parameters, (
            f"{pack.icon_class} does not accept `options`, so RenderOptions "
            f"cannot be used with the class users actually construct"
        )
        assert parameters["options"].kind is inspect.Parameter.KEYWORD_ONLY, (
            "`options` must be keyword-only so it is never confused with `style`"
        )

    def test_declares_its_provider(self, pack):
        if not pack.is_installed:
            pytest.skip(f"{pack.distribution} is not installed")
        cls = icon_class(pack)
        assert cls.provider_class is not None, (
            f"{pack.icon_class}.provider_class is unset, so render_pil on it "
            f"depends on another call having initialized a provider"
        )
        assert cls.provider_class().name == pack.provider


@pytest.mark.parametrize("pack", INSTALLED, ids=lambda p: p.extra)
def test_options_reach_the_renderer(pack):
    """Padding passed to the class changes the pixels, not just the signature."""
    cls = icon_class(pack)
    name = next(iter(cls.provider_class().build_display_index()["names_by_style"].values()))
    name = next(iter(name))

    tight = cls(name, size=64, options=RenderOptions(pad_factor=0.0)).to_pil()
    padded = cls(name, size=64, options=RenderOptions(pad_factor=0.30)).to_pil()

    tight_box, padded_box = tight.getchannel("A").getbbox(), padded.getchannel("A").getbbox()
    if tight_box is None or padded_box is None:
        pytest.skip(f"{name} renders no ink in {pack.extra}")
    assert (tight_box[2] - tight_box[0]) > (padded_box[2] - padded_box[0]), (
        "padding made no difference, so `options` was accepted and dropped"
    )


class TestRenderPilNeedsNoWarmUp:
    """The documented headless entry point, used the way the docs use it."""

    def test_works_in_a_fresh_interpreter(self):
        """A subprocess, because the class-level icon set leaks between tests.

        Any earlier test constructing an icon sets `Icon._icon_set_current`,
        which is exactly the state that hid this bug — so the only honest check
        is a process that has done nothing else.
        """
        code = (
            "from tkinter_icons import MaterialIcon\n"
            "img = MaterialIcon.render_pil('home', size=32, color='black')\n"
            "assert img.size == (32, 32)\n"
            "assert img.getchannel('A').getbbox() is not None, 'nothing drawn'\n"
            "print('ok')\n"
        )
        pack = next((p for p in INSTALLED if p.extra == "material"), None)
        if pack is None:
            pytest.skip("the material pack is not installed")
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr
        assert "ok" in result.stdout

    def test_resolves_friendly_names(self):
        """`render_pil` on a pack takes the names its constructor takes."""
        pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
        if pack is None:
            pytest.skip("the bootstrap pack is not installed")
        cls = icon_class(pack)
        # "house-fill" is a style-suffixed friendly name; before this it was
        # passed to the glyph map unresolved and rendered transparent.
        image = cls.render_pil("house-fill", size=32, color="black")
        assert image.getchannel("A").getbbox() is not None

    def test_a_name_the_pack_cannot_resolve_raises(self):
        """A typo is the caller's mistake, and `on_missing` is not for it.

        This asserted the opposite until #115: a name no style of the pack has
        came back as a transparent square, so a misspelling in a build script
        or an export loop produced a blank PNG and exited zero. The policy is
        for a set whose glyph map is inconsistent with the names built from it,
        which is a different thing and is still covered below.
        """
        pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
        if pack is None:
            pytest.skip("the bootstrap pack is not installed")
        cls = icon_class(pack)
        original = Icon.on_missing
        try:
            Icon.on_missing = "transparent"
            with pytest.raises(ValueError, match="not-a-real-icon-name"):
                cls.render_pil("not-a-real-icon-name", size=16)
        finally:
            Icon.on_missing = original

    def test_on_missing_still_governs_a_set_asked_for_a_glyph_it_lacks(self):
        """The case the policy was written for, still reachable.

        Handing a name straight to a set skips resolution entirely, so nothing
        has vouched for it — that is where a glyph can be absent without anyone
        having made a typo, and where `on_missing` applies.
        """
        pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
        if pack is None:
            pytest.skip("the bootstrap pack is not installed")
        from tkinter_icons.iconset import get_icon_set

        icon_set = get_icon_set(icon_class(pack).provider_class(), "outline")
        original = Icon.on_missing
        try:
            Icon.on_missing = "transparent"
            image = Icon.render_pil("not-a-real-icon-name", size=16, icon_set=icon_set)
            assert image.getchannel("A").getbbox() is None

            Icon.on_missing = "raise"
            with pytest.raises(KeyError, match="not-a-real-icon-name"):
                Icon.render_pil("not-a-real-icon-name", size=16, icon_set=icon_set)
        finally:
            Icon.on_missing = original

    def test_both_entry_points_reject_the_same_name(self):
        """The asymmetry `icons-and-names` used to teach, now gone.

        The constructor was the only entry point that raised of its own
        accord, so the same typo produced a `ValueError` one way and a blank
        image the other. Pinned as a pair because the prose describing it is
        otherwise unfalsifiable in either direction.
        """
        pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
        if pack is None:
            pytest.skip("the bootstrap pack is not installed")
        cls = icon_class(pack)
        with pytest.raises(ValueError):
            cls("not-a-real-icon-name")
        with pytest.raises(ValueError):
            cls.render_pil("not-a-real-icon-name")

    def test_base_icon_still_requires_a_set(self):
        """`Icon` has no pack, so it must keep raising rather than guessing."""
        original = Icon._icon_set_current
        try:
            Icon._icon_set_current = None
            with pytest.raises(RuntimeError, match="No icon set available"):
                Icon.render_pil("house", size=16)
        finally:
            Icon._icon_set_current = original
