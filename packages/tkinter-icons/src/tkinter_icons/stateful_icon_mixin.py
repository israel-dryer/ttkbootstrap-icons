"""
stateful_icon_mixin.py

Mixin for mapping per-state icons onto a ttk widget style.

This module provides `StatefulIconMixin`, which applies state-aware images to a
child ttk style derived from a widget's current style. By default, an icon's
tint follows the parent style's `foreground` for each state. You can override
the icon **name** and/or **color** per state. A fallback (`''`) mapping is
always added using the instance's original (untinted) image.

Key behaviors:
- Icon tint follows the parent style's state `foreground` unless explicitly
  overridden in `statespec`.
- Per-state custom icon names are supported (with optional color override).
- Child style naming:
  * If `subclass` is provided → `"{subclass}.{ParentStyle}"`.
  * Otherwise → hash the unique icon names used (including the base) and size
    to generate a short deterministic prefix, e.g., `"a3f4e7b2c1d6.my.TButton"`.
    This avoids style naming conflicts with ttkbootstrap's style parser.
- Merge is the default:
  * `mode="merge"` reads the existing `image` map for the **same child style**,
    overwrites incoming states, preserves order for existing entries, and
    appends new states.
  * `mode="replace"` sets a fresh `image` map for that child style.

Nuances:
- Merging only applies when the derived child style name is the same across
  calls. If you rely on auto naming (no `subclass`) and change the set of icon
  names, the child style name will change and you will not merge into the
  previous map. Pass a stable `subclass` to guarantee merging.
- ttk state maps are "first match wins". This mixin preserves existing entry
  order on merge, then appends new states.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, ClassVar
import weakref
import hashlib

try:
    # `icon.py` imports this module and `__init__.py` imports that, so a plain
    # module-scope `from tkinter.ttk import ...` put Tk in front of the whole
    # package - including the pure-PIL renderer, which never touches a widget.
    # Tolerating its absence is what lets `import tkinter_icons` work without
    # Tk installed; importing it when it *is* there keeps the annotations
    # resolvable, which Sphinx needs. See the longer note in `icon.py`.
    #
    # `Style` and `Widget` are hints everywhere except one `Style()` in `map`,
    # which imports it there - anything reaching that line has a live widget.
    from tkinter.ttk import Style, Widget
except ImportError:  # pragma: no cover - exercised in a subprocess, see tests
    Style = Any  # type: ignore[misc, assignment]
    Widget = Any  # type: ignore[misc, assignment]

StateMapMode = Literal["replace", "merge"]
# Accepted statespec entries:
#   ('hover', '#fff')
#   ('pressed', {'color': '#0af'})
#   ('hover', {'name': 'house-fill'})
#   ('pressed', {'name': 'house-fill', 'color': '#0af'})
IconStateSpec = tuple[str, str | dict[str, str]]


class StatefulIconMixin:
    """Mixin that maps per-state ttk `image` onto a child style.

    The host class must expose the following attributes and property:

    Attributes:
        name: Base icon name used when a state does not override `name`.
        size: Pixel size of the icon to render.

    Properties:
        image: A Tk-compatible image (e.g., `PhotoImage`) for the current
            instance (used as the `''` fallback).

    The host may optionally override `_render_icon()` to supply a custom image
    renderer. The default implementation constructs a new instance of the host's
    class (`type(self)`) with `(name, size, color)` and returns its `.image`.

    Note:
        This mixin does not define `__init__` and does not assume any specific
        constructor signature on the host beyond `(name: str, size: int,
        color: Optional[str] = None)`. If your constructor differs, override
        `_render_icon()` to render state images without instantiation.
    """

    # Cached untinted base image for the '' fallback (per instance)
    _original_image: Optional[object] = None

    #: Live mappings, keyed by (interpreter id, widget path). Tk reuses widget
    #: path strings, so the path alone is not a stable identity — a new widget
    #: can be handed the name of a destroyed one. Entries are removed by the
    #: widget's own <Destroy> binding rather than being left to accumulate
    #: until a theme change happens to notice the dead reference.
    _widget_mappings: ClassVar[dict[tuple[int, str], tuple]] = {}

    #: Interpreters whose root already carries the <<ThemeChanged>> binding.
    #: A single global flag would leave a second root — or the next root in a
    #: test suite — with no binding at all, silently ending theme following.
    _theme_bound: ClassVar[set[int]] = set()

    _is_regenerating: ClassVar[bool] = False

    # ---------------- Rendering ----------------

    def _render_icon(self, name: str, size: int, color: Optional[str]) -> object:
        """Render a Tk-compatible image for (name, size, color).

        By default, this constructs a new instance of `type(self)` with the
        provided `(name, size, color)` and returns its `.image`. If your host
        class requires a different constructor or you want a more direct path,
        override this method.

        Args:
            name: Icon name to render.
            size: Icon size in pixels.
            color: Optional color to tint the icon. If `None`, render untinted.

        Returns:
            A Tk-compatible image object (e.g., `PhotoImage`).
        """
        # Default path: create a sibling instance using the host class
        inst = type(self)(name, size, color)  # type: ignore[misc]
        return inst.image

    # ---------------- Helpers ----------------

    @staticmethod
    def _slug(token: str) -> str:
        """Return a style-safe token by replacing unsupported characters.

        Args:
            token: Arbitrary token (e.g., icon name).

        Returns:
            A string containing only alphanumerics, '-' or '_'.
        """
        return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in token)

    @staticmethod
    def _state_tuple(state: str) -> tuple[str, ...]:
        """Convert a state string into a ttk lookup tuple.

        Args:
            state: Single state flag (e.g., 'hover', 'pressed').

        Returns:
            A one-element tuple containing `state`.
        """
        return (state,)

    @staticmethod
    def _drawable_color(widget: Widget, color: Optional[str]) -> Optional[str]:
        """Translate a color read off a *style* into one Pillow can draw with.

        A ttk style hands back whatever it was configured with, and the native
        Windows themes configure symbolic system colors — `vista`, `winnative`
        and `xpnative` all give `SystemWindowText` for a button's foreground.
        Tk resolves those; Pillow rejects them outright with `unknown color
        specifier`, and because `map` skips a state it cannot render, the
        result was a button with no reactive states *and* no tinted resting
        image, on the three themes Windows ships as its defaults.

        Only colors read off a style come through here. A color the caller
        wrote is left as typed, since Pillow accepts specifiers Tk does not.

        Tk is the only thing that can translate a system color, so the widget
        is asked. Anything it cannot parse is handed back unchanged rather than
        dropped — it may still be something Pillow understands.
        """
        if not color:
            return None
        try:
            rgb = widget.winfo_rgb(color)
        except Exception:  # pragma: no cover - not a Tk colour name
            return color
        return "#{:02x}{:02x}{:02x}".format(*(channel >> 8 for channel in rgb))

    def _button_color_for_state(
        self, style: Style, parent_style: str, state: str, widget: Widget,
    ) -> Optional[str]:
        """Resolve the parent style's foreground color for a given state.

        Args:
            style: ttk `Style` instance.
            parent_style: Parent style name (e.g., 'my.TButton').
            state: State flag to resolve (e.g., 'hover').
            widget: The widget being styled, used to resolve symbolic colors.

        Returns:
            The resolved color string or `None` if not available.
        """
        val = style.lookup(parent_style, "foreground", state=self._state_tuple(state))
        if not val:
            val = style.lookup(parent_style, "foreground")
        return self._drawable_color(widget, val)

    def _ensure_original_image(self) -> None:
        """Ensure the untinted base image is cached for the '' fallback.

        Notes:
            Uses the instance's own `.image` to avoid re-instantiation or
            recursion during host initialization.
        """
        if self._original_image is None:
            self._original_image = self.image  # rely on host's already-rendered image

    def _parse_statespec(
            self,
            style: Style,
            parent_style: str,
            statespec: Optional[list[IconStateSpec]],
            widget: Widget,
    ) -> list[tuple[str, str, Optional[str]]]:
        """Parse the state spec into `(state, icon_name, color)` triples.

        If `statespec` is not provided, triples are derived from the parent's
        `foreground` map using the base icon.

        Args:
            style: ttk `Style` instance.
            parent_style: Parent style name to read maps from.
            statespec: Optional list describing per-state overrides. Each item
                is a `(state, spec)` pair where `spec` is either a color string
                or a dict with keys `name` and/or `color`.

        Returns:
            A list of triples `(state, icon_name, color_or_None)`. If `color` is
            `None`, the caller will resolve to the parent's state `foreground`.
        """
        out: list[tuple[str, str, Optional[str]]] = []

        if statespec:
            for state, spec in statespec:
                if isinstance(spec, dict):
                    icon_name = spec.get("name", self.name)  # type: ignore[attr-defined]
                    color = spec.get("color")
                    if color is None:
                        color = self._button_color_for_state(style, parent_style, state, widget)
                    out.append((state, icon_name, color))
                else:
                    # spec is a raw color string for the base icon
                    out.append((state, self.name, spec))  # type: ignore[attr-defined]
            return out

        # No explicit spec → derive from parent's foreground map
        fg_map = style.map(parent_style, "foreground")
        if fg_map and isinstance(fg_map, list):
            # TTK state maps can have multiple state flags: (*states, value)
            # e.g., ('pressed', '!disabled', '#fff') means pressed AND not disabled
            for item in fg_map:
                if isinstance(item, (tuple, list)) and len(item) >= 2:
                    # Last element is the value, everything before is state flags
                    *state_flags, val = item
                    if isinstance(val, str) and val:
                        # Combine state flags with space: "pressed !disabled"
                        st = " ".join(state_flags) if len(state_flags) > 1 else state_flags[0]
                        val = self._drawable_color(widget, val)
                        out.append((st, self.name, val))  # type: ignore[attr-defined]

        # If we couldn't derive any states from the map, use the base foreground color
        if not out:
            base = self._drawable_color(widget, style.lookup(parent_style, "foreground"))
            if base:
                out.append(("!disabled", self.name, base))  # type: ignore[attr-defined]
        return out

    @classmethod
    def _on_theme_changed(cls, event) -> None:
        """Regenerate every mapped icon after a `<<ThemeChanged>>` event.

        Icons tint themselves from the parent style's `foreground`, so a theme
        change invalidates every rendered image; the cache is cleared and each
        live mapping is reapplied against its original parent style.
        """
        from .icon import Icon

        cls._is_regenerating = True
        try:
            Icon.clear_cache()

            for key, mapping_data in list(cls._widget_mappings.items()):
                try:
                    icon, widget_ref, parent_style, subclass, statespec, mode = mapping_data
                    widget = widget_ref()

                    if widget is None or not widget.winfo_exists():
                        cls._widget_mappings.pop(key, None)
                        continue

                    # Restore the original parent style so the remap derives the
                    # same child style name it did the first time.
                    widget.configure(style=parent_style)
                    icon.map(widget, subclass=subclass, statespec=statespec, mode=mode)
                except Exception:
                    cls._widget_mappings.pop(key, None)
        finally:
            cls._is_regenerating = False

    @classmethod
    def _forget_widget(cls, key: tuple[int, str]) -> None:
        """Drop a widget's mapping once the widget is gone."""
        cls._widget_mappings.pop(key, None)

    @classmethod
    def _parent_style_for(cls, widget: Widget) -> str:
        """Return the style `widget` had before any icon mapping was applied.

        Reading `widget.cget("style")` directly is only right the first time.
        On a second `map()` the widget already wears the derived child style,
        so prefixing again compounds it — `abc123.abc123.TButton` — which both
        grows without bound and defeats the merge in `mode="merge"`, since the
        child style name is different every call. The original parent is
        remembered per widget instead.
        """
        remembered = cls._widget_mappings.get((id(widget.tk), str(widget)))
        if remembered is not None:
            return remembered[2]
        return widget.cget("style") or widget.winfo_class()

    @classmethod
    def _track(cls, widget: Widget, mapping: tuple) -> None:
        """Record a live mapping and arrange for its removal on destroy.

        The entry holds the icon itself, so it has to come out when the widget
        does — otherwise every mapped widget leaks its icon for the life of the
        process.
        """
        key = (id(widget.tk), str(widget))
        cls._widget_mappings[key] = mapping

        def _on_destroy(event, _widget=widget, _key=key):
            # A container's <Destroy> also reaches this binding for its
            # children; only the mapped widget's own destruction counts.
            if event.widget is _widget:
                StatefulIconMixin._forget_widget(_key)

        try:
            widget.bind("<Destroy>", _on_destroy, add=True)
        except Exception:  # pragma: no cover - widget already being torn down
            pass

    @classmethod
    def _bind_theme_listener(cls, widget: Widget) -> None:
        """Ensure this widget's interpreter regenerates icons on theme change."""
        interp = id(widget.tk)
        if interp in cls._theme_bound:
            return
        try:
            root = widget.winfo_toplevel()
            root.bind("<<ThemeChanged>>", cls._on_theme_changed, add=True)
            cls._theme_bound.add(interp)
        except Exception:  # pragma: no cover
            pass

    # ---------------- Public API ----------------

    def map(
            self,
            widget: Widget,
            *,
            subclass: Optional[str] = None,
            statespec: Optional[list[IconStateSpec]] = None,
            mode: StateMapMode = "merge",
    ) -> None:
        """Apply per-state images to a child style derived from the widget's style.

        This computes per-state images from `statespec` (or the parent's
        `foreground` map when `statespec` is omitted), generates a child style
        name, and maps the `image` option accordingly. The empty-state (`''`)
        fallback is always set to the instance's original untinted image.

        Args:
            widget: ttk widget to style (e.g., `ttk.Button`).
            subclass: Optional child style prefix. If omitted, the name is
                generated by hashing the unique icon names used (including the
                base) and size, e.g., `"a3f4e7b2c1d6.my.TButton"`.
            statespec: Optional list of per-state overrides. Each item is a
                `(state, spec)` pair where `spec` is a color string or a dict
                with `name` and/or `color`. If `color` is omitted, the icon
                color follows the parent's `foreground` for that state.
            mode: Merge strategy for the child style's `image` map.
                `"merge"`, the default, reads the existing map for the same
                child style, overwrites incoming states, preserves the order of
                existing entries, and appends new ones. `"replace"` ignores any
                existing map and applies only the states given, plus the
                fallback.
        """
        from tkinter.ttk import Style

        style = Style()
        parent_style = self._parent_style_for(widget)

        # Build (state, icon_name, color) triples
        triples = self._parse_statespec(style, parent_style, statespec, widget)

        # Determine child style name
        used_names = {self.name} | {nm for _, nm, _ in triples}  # type: ignore[attr-defined]
        if subclass:
            child_prefix = subclass
        else:
            # Hash the concatenated icon names and size to avoid style naming conflicts
            names_token = "-".join(sorted(used_names))
            hash_input = f"{names_token}-{self.size}"  # type: ignore[attr-defined]
            hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
            child_prefix = hash_digest
        new_style = f"{child_prefix}.{parent_style}"

        # Render images
        incoming_pairs: list[tuple[str, object]] = []
        for st, icon_name, color in triples:
            try:
                img = self._render_icon(icon_name, self.size, color)  # type: ignore[attr-defined]
                incoming_pairs.append((st, img))
            except Exception:
                # Skip invalid name/color safely
                continue

        # Merge/replace with deterministic order
        if mode == "replace":
            existing_pairs: list[tuple[str, object]] = []
        else:  # mode == "merge"
            raw_existing = style.map(new_style, "image")
            # Ensure we have a valid list of tuples
            # ttk may return [""] or other invalid formats when no mapping exists
            if raw_existing and isinstance(raw_existing, list):
                # Filter out invalid entries (must be tuples/lists of length 2)
                existing_pairs = [
                    item for item in raw_existing
                    if isinstance(item, (tuple, list)) and len(item) == 2
                ]
            else:
                existing_pairs = []

        existing_dict = dict(existing_pairs) if existing_pairs else {}
        incoming_dict = dict(incoming_pairs)
        merged = {**existing_dict, **incoming_dict}

        # Preserve original order for existing states, then append newly added states
        ordered: list[tuple[str, object]] = [(st, merged[st]) for st, _ in existing_pairs if st in merged]
        for st in incoming_dict.keys():
            if st not in existing_dict:
                ordered.append((st, merged[st]))

        # Create fallback image for '' state with normal foreground color
        # If we don't have an explicit '' state already, render one with the normal color
        fallback_img = merged.get("")
        if fallback_img is None:
            # Get the normal state foreground color
            normal_color = self._drawable_color(
                widget, style.lookup(parent_style, "foreground"))
            try:
                fallback_img = self._render_icon(self.name, self.size, normal_color)  # type: ignore[attr-defined]
            except Exception:
                # Fall back to original untinted image if rendering fails
                self._ensure_original_image()
                fallback_img = self._original_image

        image_map = [(st, img) for st, img in ordered if st != ""]
        image_map.append(("", fallback_img))

        # Configure compound and apply map
        try:
            style.configure(new_style, compound="left")
        except Exception:
            pass

        style.map(new_style, image=image_map)
        widget.configure(style=new_style)

        if not StatefulIconMixin._is_regenerating:
            StatefulIconMixin._track(
                widget,
                (self, weakref.ref(widget), parent_style, subclass, statespec, mode),
            )
            StatefulIconMixin._bind_theme_listener(widget)

    def unmap(self, widget: Widget) -> None:
        """Stop tracking `widget`, so theme changes no longer restyle it.

        Rarely needed — a destroyed widget forgets itself — but useful to
        release an icon early on a widget that outlives its icon.

        Args:
            widget: A widget previously passed to `map`.
        """
        StatefulIconMixin._forget_widget((id(widget.tk), str(widget)))
