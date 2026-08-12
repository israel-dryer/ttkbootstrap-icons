"""Tests for `StatefulIconMixin` — state maps and, mainly, lifecycle.

The mapping table holds a strong reference to the icon, so an entry that
outlives its widget leaks. It used to be keyed by widget path alone (which Tk
reuses) and pruned only when a theme change happened to notice a dead weakref.
"""

from __future__ import annotations

import sys

import pytest

from tkinter_icons.icon import Icon
from tkinter_icons.stateful_icon_mixin import StatefulIconMixin

pytestmark = pytest.mark.gui


@pytest.fixture
def button(root):
    from tkinter import ttk

    widget = ttk.Button(root, text="Go")
    widget.pack()
    root.update_idletasks()
    return widget


def mapping_keys():
    return set(StatefulIconMixin._widget_mappings)


def cross_style_case():
    """An installed pack whose styles do not all carry the same names.

    Returns `(icon_class, a name in the default style, a name only another
    style has, that other style's set)`, or `None` if no installed pack
    qualifies — which is the case for every single-style pack and for the ones
    whose styles share one glyph map, Bootstrap among them.
    """
    import importlib

    from tkinter_icons.packs import KNOWN_PACKS

    for pack in KNOWN_PACKS:
        if not pack.is_installed:
            continue
        cls = getattr(importlib.import_module(pack.module), pack.icon_class)
        provider = cls.provider_class()
        styles = list(getattr(provider, "style_list", None) or [])
        if len(styles) < 2:
            continue
        home = Icon.initialize_with_provider(provider)
        for style in styles:
            if style == provider.default_style:
                continue
            other = Icon.initialize_with_provider(provider, style)
            elsewhere = next(
                (name for name in sorted(other.glyphs) if home.glyph(name) is None), None,
            )
            if elsewhere is not None:
                Icon.initialize_with_provider(provider)
                return cls, next(iter(sorted(home.glyphs))), elsewhere, other
    return None


class TestMapping:
    def test_map_applies_a_child_style(self, root, button, icon_set, sample_name):
        original = button.cget("style") or button.winfo_class()
        Icon(sample_name, 16).map(button)
        assert button.cget("style").endswith(original)
        assert button.cget("style") != original

    def test_explicit_subclass_names_the_style(self, root, button, icon_set, sample_name):
        Icon(sample_name, 16).map(button, subclass="mine")
        assert button.cget("style").startswith("mine.")

    def test_auto_name_is_stable_for_the_same_icon(self, root, button, icon_set, sample_name):
        Icon(sample_name, 16).map(button)
        first = button.cget("style")
        Icon(sample_name, 16).map(button)
        assert button.cget("style") == first

    def test_statespec_colors_are_mapped(self, root, button, icon_set, sample_name):
        from tkinter import ttk

        Icon(sample_name, 16).map(button, subclass="spec", statespec=[("pressed", "#ff0000")])
        image_map = ttk.Style().map(button.cget("style"), "image")
        assert any("pressed" in str(entry) for entry in image_map)


class TestStateImagesComeFromTheIconsOwnSet:
    """`_render_icon` must not rebuild the icon through its constructor.

    The mixin's default does — `type(icon)(name, size, color)` — and a
    constructor call has nowhere to carry the `style` the icon was built with
    or the `options` it was given. The state images then came from the pack's
    *default* style at the pack's default options, disagreeing with the resting
    image beside them.
    """

    def test_a_non_default_style_survives(self, root, button, provider, icon_set):
        styles = list(getattr(provider, "style_list", None) or [])
        if len(styles) < 2:
            pytest.skip(f"{provider.name} has no second style to be lost")

        other = next(s for s in styles if s != provider.default_style)
        other_set = Icon.initialize_with_provider(provider, other)
        name = next(iter(sorted(other_set.glyphs)))
        icon = Icon(name, 16)
        # Back to the default, which is what a constructor call would pick up.
        Icon.initialize_with_provider(provider)
        assert Icon._icon_set_current.id != icon.icon_set.id

        icon.map(button, subclass="styled", statespec=[("pressed", "#ff0000")])

        rendered_from = {key[0] for cache in Icon._caches.values() for key in cache.images}
        assert icon.icon_set.id in rendered_from
        assert Icon._icon_set_current.id not in rendered_from

    def test_a_state_name_from_another_style_still_resolves(self, root, button):
        """Preferring the icon's own set must not cost cross-style state names.

        Pinning `render_pil` to a set switches it off its resolving branch, so
        a statespec that deliberately reaches another style — a Font Awesome
        brand mark beside a solid icon — stopped resolving, and `map` catches
        the failure and drops the state without a word. The set is chosen per
        name instead: this icon's own where it can draw the name, the pack's
        resolution where it cannot.

        It has to run on a **pack's** class, not on `Icon`: resolution needs a
        `provider_class`, and the base has none. Bootstrap is no use either —
        its two styles are one font split by a name predicate, so every name is
        in both maps and there is no other style to reach.
        """
        from tkinter import ttk

        found = cross_style_case()
        if found is None:
            pytest.skip("no installed pack has a name only one of its styles carries")
        cls, home_name, elsewhere, other_set = found

        icon = cls(home_name, 16)
        icon.map(button, subclass="cross", statespec=[("pressed", {"name": elsewhere})])

        mapped = ttk.Style().map(button.cget("style"), "image")
        assert any(entry[0] == "pressed" for entry in mapped if isinstance(entry[0], str))
        rendered_from = {key[0] for cache in Icon._caches.values() for key in cache.images}
        assert other_set.id in rendered_from

    def test_per_icon_options_survive(self, root, icon_set, sample_name):
        from tkinter_icons.render import RenderOptions

        options = RenderOptions(pad_factor=0.35)
        icon = Icon(sample_name, 16, options=options)
        state_image = icon._render_icon(sample_name, 16, "#ff0000")

        # Same set, name, size, color and options is one cache entry, so an
        # icon built that way holds the very same image. Rebuilt through the
        # constructor it would carry the set's options instead, and be another.
        assert state_image is Icon(sample_name, 16, "#ff0000", options=options).image
        assert state_image is not Icon(sample_name, 16, "#ff0000").image


class TestColorsReadOffAStyle:
    """A style's color is not necessarily a color Pillow can draw with."""

    def test_a_name_a_theme_configures_is_resolved_to_hex(self, root, button, icon_set, sample_name):
        """A theme configures a colour *name*, and Pillow does not take every name Tk does.

        This is the portable half of the translation, and the only half that
        can be asserted off Windows. Every stock X11 theme — `clam`, `alt`,
        `default`, `classic` — configures a button foreground of `black` or
        `#000000`, so this is the value the function really meets there.

        It still has teeth: untranslated, the style hands back the name, and
        the assertion below is that a hex comes out instead.
        """
        assert Icon._drawable_color(button, "black") == "#000000"
        assert Icon._drawable_color(button, "#000000") == "#000000"

    @pytest.mark.skipif(
        sys.platform != "win32",
        reason=(
            "SystemWindowText names a Windows system setting rather than a colour; "
            "Tk elsewhere raises `unknown color name` and has nothing to resolve it to"
        ),
    )
    def test_a_symbolic_system_color_is_translated(self, root, button, icon_set, sample_name):
        """The native Windows themes configure `SystemWindowText`, not a hex.

        Tk resolves those; Pillow rejects them outright, and `map` skips any
        state it cannot render — including the fallback — so the button was
        left with no reactive states *and* an untinted resting icon, on the
        three themes Windows ships as its own defaults.

        Windows-only by nature, not by convenience: the symbolic names exist
        only in Tk's Windows build, so there is no portable value that
        reproduces this integration. The translation itself is covered
        everywhere by the test above.
        """
        from tkinter import ttk

        style = ttk.Style()
        style.configure("Symbolic.TButton", foreground="SystemWindowText")
        style.map("Symbolic.TButton", foreground=[("pressed", "SystemWindowText")])
        button.configure(style="Symbolic.TButton")

        Icon(sample_name, 16).map(button, subclass="sym")
        image_map = ttk.Style().map(button.cget("style"), "image")
        assert any(entry[0] == "pressed" for entry in image_map if isinstance(entry[0], str))

    def test_a_colour_the_caller_wrote_is_left_alone(self, root, button, icon_set, sample_name):
        """Pillow accepts specifiers Tk does not, so a spec colour is not touched."""
        assert Icon._drawable_color(button, "hsl(200, 50%, 50%)") == "hsl(200, 50%, 50%)"
        assert Icon._drawable_color(button, "") is None


class TestLifecycle:
    def test_mapping_is_tracked(self, root, button, icon_set, sample_name):
        before = mapping_keys()
        Icon(sample_name, 16).map(button)
        assert mapping_keys() - before

    def test_destroying_the_widget_forgets_it(self, root, icon_set, sample_name):
        from tkinter import ttk

        widget = ttk.Button(root, text="temp")
        widget.pack()
        root.update_idletasks()

        Icon(sample_name, 16).map(widget)
        key = (id(widget.tk), str(widget))
        assert key in StatefulIconMixin._widget_mappings

        widget.destroy()
        root.update()
        assert key not in StatefulIconMixin._widget_mappings

    def test_a_child_destroy_does_not_forget_the_parent(self, root, icon_set, sample_name):
        """<Destroy> reaches a container's bindings for its children too."""
        from tkinter import ttk

        frame = ttk.Frame(root)
        frame.pack()
        child = ttk.Label(frame, text="x")
        child.pack()
        root.update_idletasks()

        Icon(sample_name, 16).map(frame)
        key = (id(frame.tk), str(frame))
        assert key in StatefulIconMixin._widget_mappings

        child.destroy()
        root.update()
        assert key in StatefulIconMixin._widget_mappings, "parent was forgotten by a child's destroy"

        frame.destroy()
        root.update()
        assert key not in StatefulIconMixin._widget_mappings

    def test_unmap_releases_the_entry(self, root, button, icon_set, sample_name):
        icon = Icon(sample_name, 16)
        icon.map(button)
        key = (id(button.tk), str(button))
        assert key in StatefulIconMixin._widget_mappings

        icon.unmap(button)
        assert key not in StatefulIconMixin._widget_mappings

    def test_mapped_icon_is_released_with_its_widget(self, root, icon_set, sample_name):
        """The tracking table must not pin the icon after the widget is gone."""
        import gc
        import weakref
        from tkinter import ttk

        widget = ttk.Button(root, text="temp")
        widget.pack()
        root.update_idletasks()

        icon = Icon(sample_name, 16)
        icon.map(widget)
        ref = weakref.ref(icon)

        widget.destroy()
        root.update()
        del icon
        gc.collect()
        assert ref() is None, "icon outlived its widget"

    def test_theme_binding_is_per_interpreter(self, root, button, icon_set, sample_name):
        """A single global flag left later roots with no binding at all."""
        Icon(sample_name, 16).map(button)
        assert id(root.tk) in StatefulIconMixin._theme_bound

    def test_theme_change_regenerates_mapped_icons(self, root, button, icon_set, sample_name):
        from tkinter import ttk

        Icon(sample_name, 16).map(button, subclass="themed")
        styled = button.cget("style")

        ttk.Style().theme_use(ttk.Style().theme_use())
        root.event_generate("<<ThemeChanged>>")
        root.update()

        # Still mapped, still pointing at the same child style.
        assert button.cget("style") == styled
        assert ttk.Style().map(styled, "image")
