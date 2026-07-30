"""Tests for `StatefulIconMixin` — state maps and, mainly, lifecycle.

The mapping table holds a strong reference to the icon, so an entry that
outlives its widget leaks. It used to be keyed by widget path alone (which Tk
reuses) and pruned only when a theme change happened to notice a dead weakref.
"""

from __future__ import annotations

import pytest

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons.stateful_icon_mixin import StatefulIconMixin

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
