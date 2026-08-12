"""Icons on PySimpleGUI buttons.

PySimpleGUI is declarative: constructing ``sg.Button`` creates no Tk widget at
all — ``element.Widget`` stays ``None`` until ``sg.Window`` builds the layout.
So an icon cannot be applied in a constructor, and cannot even be *rendered*
there, since a `PhotoImage` needs an interpreter that does not exist yet.
:class:`IconButton` bridges that, and the bridge is the whole module::

    from tkinter_icons import BootstrapIcon
    from tkinter_icons.extensions.psg import IconButton

    layout = [[IconButton("Save", icon=BootstrapIcon("floppy"), key="-SAVE-")]]
    window = sg.Window("App", layout, finalize=True)

PySimpleGUI is **not** a dependency of this package and nothing from it is
redistributed here. Install it yourself.

Not every icon needs this. Anything that takes an encoded image —
``sg.Image(data=...)``, ``sg.Tab(image_source=...)``, ``sg.Window(icon=...)``,
and icon-*only* buttons through ``image_data=`` — can take
:meth:`Icon.to_data <tkinter_icons.Icon.to_data>` bytes directly, with
no deferral and no subclass. Reach for :class:`IconButton` when the icon sits
beside text, or has to react to what the button is doing.

.. versionadded:: 5.1.0
"""

from __future__ import annotations

import importlib
import inspect
import tkinter as tk
import warnings
from tkinter import ttk
from typing import Any, Mapping, Optional

from ..icon import Icon

__all__ = ["IconButton", "PySimpleGUINotInstalled"]

#: ttk's own name for each state. ttk calls hover "active", which is why this
#: module does not reuse that word. Unknown keys pass through untouched, so a
#: caller wanting a raw ttk state expression — ``"pressed !disabled"`` — can
#: still write one.
_TTK_STATES = {"": "", "hover": "active", "pressed": "pressed", "disabled": "disabled"}

#: `tk.Button` options holding the color for each state it can reach. There is
#: no hover entry because a `tk.Button` has no hover state — see
#: :meth:`IconButton._map_tk_states`.
_TK_STATE_COLORS = {
    "": "foreground",
    "pressed": "activeforeground",
    "disabled": "disabledforeground",
}

#: The inverse: what tk reports in ``-state``, mapped back to a name here.
_TK_STATE_KEYS = {"normal": "", "active": "pressed", "disabled": "disabled"}

#: Events whose class bindings change a `tk.Button`'s ``-state``. Enter and
#: Leave belong here because they matter while button 1 is held.
_TK_STATE_EVENTS = ("<ButtonPress-1>", "<ButtonRelease-1>", "<Enter>", "<Leave>")


class PySimpleGUINotInstalled(ImportError):
    """PySimpleGUI could not be imported."""


def _not_installed_message() -> str:
    lines = [
        "This integration needs PySimpleGUI, which tkinter-icons does not install for you.",
        "",
        "  pip install PySimpleGUI",
        "",
        "Icons that do not need this module — sg.Image, sg.Tab, sg.Window(icon=) —",
        "take Icon.to_data() bytes directly.",
    ]
    return "\n".join(lines)


def _import_psg():
    """Import PySimpleGUI, or explain how to install it.

    Raises:
        PySimpleGUINotInstalled: If it is not installed.
    """
    try:
        return importlib.import_module("PySimpleGUI")
    except ImportError as exc:
        raise PySimpleGUINotInstalled(_not_installed_message()) from exc


def _chosen_color(icon: Icon) -> Optional[str]:
    """The color the caller asked for, or `None` if the icon was left as-is.

    An `Icon` records its color but not whether anyone chose it, so the
    constructor default is read off the signature and compared. Reading it
    rather than hard-coding ``"black"`` means this cannot drift if that default
    ever changes.

    The one thing it cannot tell apart is a deliberate black from a defaulted
    one, and that is harmless in practice: a button whose text is black gives a
    black icon either way, and on a button whose text is not black, asking for
    black is not what anyone meant.
    """
    try:
        default = inspect.signature(type(icon).__init__).parameters["color"].default
    except (ValueError, KeyError):  # pragma: no cover - a pack with an odd signature
        default = "black"
    return None if icon.color == default else icon.color


def _hex_color(widget, color) -> Optional[str]:
    """Normalize a Tk color into something Pillow can parse.

    A widget hands back whatever it was configured with, and on Windows the
    defaults are symbolic system colors — ``disabledforeground`` reads back as
    ``systemdisabledtext``, which Tk resolves and Pillow rejects outright.
    Only colors read *off a widget* come through here; a color the caller
    wrote stays as typed, since Pillow accepts specifiers Tk does not.
    """
    if not color:
        return None
    try:
        rgb = widget.winfo_rgb(color)
    except tk.TclError:
        return None
    return "#{:02x}{:02x}{:02x}".format(*(channel >> 8 for channel in rgb))


def _build_icon_button(sg) -> type:
    """Build `IconButton` on PySimpleGUI's `Button`.

    A class statement needs its base at class-creation time, so this runs on
    first use rather than at module import — see the module `__getattr__`.
    """

    class IconButton(sg.Button):
        """A PySimpleGUI button with a `tkinter_icons` icon on it.

        Args:
            args: Positional arguments for ``sg.Button``, i.e. the button text.
            icon: The icon to draw. Constructing one costs nothing — an `Icon`
                renders on demand, not on construction — so building it inline
                in a layout is fine. **Leave its color unset** and the icon
                takes the button's, so it matches the theme without being told
                to; **give it one** and that color is kept for the resting
                state while the others still follow the button.
            reactive_states: ``True`` to follow the button's own colors,
                ``False`` to draw the icon exactly as given, or a mapping of
                state name to either a color or a ``{"name": ..., "color": ...}``
                dict, which can swap the glyph as well as tint it. A ``""``
                entry names the resting state and outranks the icon's color.
            compound: Where the icon sits relative to the text, as Tk means it.
                Pass ``"none"`` for a button with **no text**: the default
                ``"left"`` reserves a text slot, and on ttk that is not free —
                an empty-text button asks for 96 px against 26. ``ttk`` also
                accepts ``"image"``, which ``tk`` does not, so ``"none"`` is
                the value that means image-only on both.
            kwargs: Further keyword arguments for ``sg.Button``.

        State names describe the interaction — ``hover``, ``pressed``,
        ``disabled`` — rather than either toolkit's vocabulary, because Tk and
        ttk disagree about the word "active": in ttk it means hover, on a
        `tk.Button` it means pressed. Each path translates. A `tk.Button`
        cannot carry a separate hover image at all, so asking for ``hover``
        there warns rather than silently doing nothing.
        """

        def __init__(
            self,
            *args,
            icon: Icon,
            reactive_states: Any = True,
            compound: str = "left",
            **kwargs,
        ):
            self._icon = icon
            self._reactive_states = reactive_states
            self._compound = compound
            self._icon_attached = False
            # tk path only. A widget option holds the Tk image *name*, so
            # something has to hold the images themselves or they are collected.
            self._state_images: dict[str, Any] = {}
            self._state_colors: dict[str, Optional[str]] = {}
            self._tk_bound = False
            self._widget = None
            super().__init__(*args, **kwargs)

        # -- deferred attach ------------------------------------------------

        @property
        def Widget(self):  # noqa: N802 - PySimpleGUI's own casing
            return self._widget

        @Widget.setter
        def Widget(self, widget):  # noqa: N802
            # Assigned twice: once as None by Element.__init__, then for real
            # by the packer.
            self._widget = widget
            if widget is None:
                return
            # Idle is the trigger, not <Map>. PySimpleGUI never yields to the
            # event loop while configuring an element, so the first idle after
            # the widget exists is the first moment it is fully configured —
            # which on the ttk path means after its style has been applied,
            # and that is what Icon.map reads. It is also early: PySimpleGUI
            # packs the layout and then calls update_idletasks() to size and
            # place the window, and that call runs this. Attaching on <Map>
            # instead is visibly too late, because update_idletasks does not
            # deliver events — the window is already on screen by then, and
            # the icons appear and the buttons resize in front of the user.
            widget.after_idle(self.attach_icon)
            # Backstop for a widget built outside that startup pass.
            # attach_icon is idempotent, so whichever fires first wins.
            widget.bind("<Map>", self.attach_icon, add="+")

        def attach_icon(self, _event=None) -> None:
            """Render and apply the icon. Runs once; re-entry is a no-op.

            Called for you. Reach for it directly only to force the icon on
            before the first pass through the event loop — ``finalize=True``
            builds the widgets but does not get as far as mapping them, so a
            test or a screenshot taken immediately after it would otherwise
            catch the button bare.
            """
            if self._icon_attached or self._widget is None:
                return
            self._icon_attached = True
            self._apply_icon()

        def _apply_icon(self) -> None:
            """Render the icon onto the widget. Safe to re-run."""
            if isinstance(self._widget, ttk.Widget):
                self._map_ttk_states()
            else:
                self._map_tk_states()
            # A widget option beats the style, so this wins over the compound
            # Icon.map sets, and covers both paths in one place.
            self._widget.configure(compound=self._compound)

        # -- ttk: real per-state images -------------------------------------

        def _map_ttk_states(self) -> None:
            """Hand the widget to `Icon.map`, which owns the ttk state machinery.

            PySimpleGUI gives every ttk button a private style and applies it
            during the build, so by attach time ``widget.cget("style")`` is the
            real parent — `Icon.map` derives a child of it and inherits the
            font and colors PySimpleGUI configured.
            """
            if self._reactive_states is False:
                # Hand the widget back to PySimpleGUI's own style. Leaving it
                # in a derived one would keep an image map that update() was
                # just told to stop applying. Read the parent before unmap,
                # which is what remembers it.
                parent = Icon._parent_style_for(self._widget)
                self._icon.unmap(self._widget)
                self._widget.configure(style=parent, image=self._icon.image)
                self._state_colors = {}
                return

            # None tells Icon.map to derive states from the parent style's
            # foreground map, which is where PySimpleGUI wrote mouseover_colors
            # and disabled_button_color.
            statespec = None
            if isinstance(self._reactive_states, Mapping):
                statespec = [(_TTK_STATES.get(state, state), spec)
                             for state, spec in self._reactive_states.items()]
            self._icon.map(self._widget, statespec=statespec, mode="replace")

            # A color the caller chose wins for the resting state. It has to be
            # a second, merging call: handing Icon.map a statespec makes it use
            # only that spec, so folding "" into the first call would discard
            # the states derived from the style. Merging keeps them and
            # overwrites the one entry.
            chosen = _chosen_color(self._icon)
            if chosen is not None and not self._has_own_resting_spec():
                self._icon.map(self._widget, statespec=[("", chosen)], mode="merge")
            self._state_colors = {"": chosen or self._ttk_parent_foreground()}

        def _has_own_resting_spec(self) -> bool:
            """Whether `reactive_states` names the resting state itself."""
            return isinstance(self._reactive_states, Mapping) and "" in self._reactive_states

        def _ttk_parent_foreground(self) -> Optional[str]:
            """The style foreground the ttk icons were last derived from."""
            style = ttk.Style()
            return style.lookup(Icon._parent_style_for(self._widget), "foreground") or None

        # -- tk: no state images exist, so approximate them ------------------

        def _map_tk_states(self) -> None:
            """Pre-render one image per state and swap between them by hand.

            The widget is the only authority on which state it is in, so rather
            than infer from the pointer this re-reads ``-state`` after Tk's
            class bindings have run. That is correct on every platform by
            construction, whatever each one does.

            Which matters, because Tk's ``active`` does not mean what ttk's
            does, and **it does not mean the same thing on every platform**.
            ``button.tcl`` defines ``tk::ButtonEnter`` three times, once per
            windowing system:

            * **win32 and aqua** set ``-state active`` only when the mouse
              button is already down, so the state changes on *press* and
              ``<Enter>`` alone leaves it ``normal``.
            * **x11** sets it on entry unconditionally — "on unix the state is
              active just with mouse-over", in Tk's own comment — so there the
              one state covers hover *and* press.

            Reading the widget rather than the pointer is what makes this
            correct anywhere: whichever Tk does, the icon follows. What stays
            true everywhere is that ``hover`` is not separately reachable — on
            win32 because no hover state exists, on x11 because hover is
            indistinguishable from press.
            """
            # A tk.Button measures -width/-height in characters and lines while
            # it shows text alone, and in *pixels* once it also shows an image.
            # PySimpleGUI built this one with height=1 meaning one line, so
            # leaving it collapses the button to one pixel tall. Auto-size
            # instead, which does mean an explicit size= is not honored here.
            # ttk has no such reinterpretation and is left alone.
            self._widget.configure(width=0, height=0)

            if isinstance(self._reactive_states, Mapping) and "hover" in self._reactive_states:
                warnings.warn(
                    f"{type(self).__name__}(key={self.Key!r}) was given a 'hover' state, but a "
                    f"tk.Button cannot carry a separate hover image, so it is ignored — on "
                    f"Windows and macOS because it has no hover state at all, on X11 because "
                    f"hover and press are both '-state active' there. Pass use_ttk_buttons=True "
                    f"for a real hover, or use 'pressed'.",
                    stacklevel=2,
                )

            self._render_tk_images()
            # Bound once for the widget's life, not once per render: update()
            # can re-render, and add="+" would stack a duplicate every time.
            if "pressed" in self._state_images and not self._tk_bound:
                self._tk_bound = True
                # add="+" matters: PySimpleGUI binds <Enter>/<Leave> for
                # tooltips and for mouseover images, and a bare bind() would
                # drop them.
                for sequence in _TK_STATE_EVENTS:
                    self._widget.bind(sequence, self._sync_tk_image, add="+")
            self._apply_tk_image()

        def _render_tk_images(self) -> None:
            """Build one image per reachable state, recording the colors used."""
            states = ("",) if self._reactive_states is False else ("", "pressed", "disabled")
            images, colors = {}, {}
            for state in states:
                color = self._color_for(state)
                colors[state] = color
                if color is not None:
                    images[state] = self._icon._render_icon(
                        self._name_for(state), self._icon.size, color,
                    )
            self._state_images = images
            self._state_colors = colors

        def _name_for(self, state: str) -> str:
            if isinstance(self._reactive_states, Mapping):
                spec = self._reactive_states.get(state)
                if isinstance(spec, Mapping):
                    return spec.get("name", self._icon.name)
            return self._icon.name

        def _color_for(self, state: str) -> Optional[str]:
            """The color for one state, or None if the state is unstyled."""
            if isinstance(self._reactive_states, Mapping):
                spec = self._reactive_states.get(state)
                if spec is None and state:
                    return None
                if isinstance(spec, Mapping):
                    if spec.get("color") is not None:
                        return spec["color"]
                elif spec is not None:
                    return spec
            elif self._reactive_states is False:
                return self._icon.color

            # A color the caller chose wins for the resting state; the others
            # still follow the button, so a chosen color does not freeze the
            # icon against being greyed out when the button is disabled.
            if state == "":
                chosen = _chosen_color(self._icon)
                if chosen is not None:
                    return chosen
            return _hex_color(self._widget, self._widget.cget(_TK_STATE_COLORS[state]))

        def _sync_tk_image(self, _event=None) -> None:
            """Re-read ``-state`` once Tk has finished handling the event.

            A widget binding runs *before* the class binding that does the
            state change, so reading ``-state`` here would report the old
            value. Idle is the first moment the widget agrees with itself.
            """
            self._widget.after_idle(self._apply_tk_image)

        def _apply_tk_image(self) -> None:
            """Show the image matching the widget's current state."""
            widget = self._widget
            # Reached from after_idle, so the window may have closed since.
            if widget is None or not self._state_images or not widget.winfo_exists():
                return
            state = _TK_STATE_KEYS.get(str(widget.cget("state")), "")
            widget.configure(image=self._state_images.get(state) or self._state_images[""])

        # -- staying in step with the button --------------------------------

        def update(
            self,
            *args,
            icon: Optional[Icon] = None,
            reactive_states: Any = None,
            compound: Optional[str] = None,
            **kwargs,
        ):
            """Update the button, including anything this class added to it.

            Args:
                args: Positional arguments for ``sg.Button.update``.
                icon: A new icon to draw. Swapping one is the point — a
                    play/pause button is two glyphs on one element.
                reactive_states: New per-state behavior, as the constructor
                    takes it.
                compound: Move the icon relative to the text.
                kwargs: Further keyword arguments for ``sg.Button.update``.

            Two things also move on their own and are followed without being
            asked for. ``update(disabled=...)`` changes the state, and a
            `tk.Button` has no disabled *image* — only ``disabledforeground``,
            which does not touch the glyph — so the image is swapped by hand.
            And ``update(button_color=...)`` changes the colors the icon was
            tinted from, on both paths.

            Global re-theming is deliberately **not** followed. ``sg.theme()``
            affects only windows built afterward — PySimpleGUI has no method to
            re-theme a live one, and the usual answer is to close the window
            and rebuild it — so an icon that chased it would react to something
            the button under it ignores.
            """
            result = super().update(*args, **kwargs)

            redraw = icon is not None or reactive_states is not None
            if icon is not None:
                self._icon = icon
            if reactive_states is not None:
                self._reactive_states = reactive_states
            if compound is not None and compound != self._compound:
                self._compound = compound
                redraw = True

            # Before the attach there is nothing to redo: it reads these
            # attributes when it runs, so it will pick the new values up.
            if not self._icon_attached:
                return result

            if redraw:
                self._apply_icon()
            else:
                self._refresh_for_colors()
            if not isinstance(self._widget, ttk.Widget):
                self._apply_tk_image()
            return result

        def _refresh_for_colors(self) -> None:
            """Re-derive the icons if the colors they were tinted from moved.

            Compares against what was actually used rather than tracking which
            arguments `update` was called with, so a caller reconfiguring the
            widget directly is caught too.
            """
            if self._reactive_states is False or self._widget is None:
                return
            if not self._widget.winfo_exists():
                return

            if isinstance(self._widget, ttk.Widget):
                if self._ttk_parent_foreground() != self._state_colors.get(""):
                    self._map_ttk_states()
                    self._widget.configure(compound=self._compound)
                return

            current = {state: self._color_for(state) for state in self._state_colors}
            if current != self._state_colors:
                self._render_tk_images()

    IconButton.__qualname__ = "IconButton"
    IconButton.__module__ = __name__
    return IconButton


_ICON_BUTTON: list = []


def __getattr__(name: str):
    """Build `IconButton` on first use, not at import.

    A class statement needs its base at class-creation time, and the base is
    PySimpleGUI's `Button`. Building it here rather than at module scope means
    ``import tkinter_icons.extensions.psg`` pulls in no GUI toolkit, and that a
    missing PySimpleGUI is reported by :class:`PySimpleGUINotInstalled` rather
    than by a bare `ModuleNotFoundError` from an import line.
    """
    if name != "IconButton":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    if not _ICON_BUTTON:
        _ICON_BUTTON.append(_build_icon_button(_import_psg()))
    return _ICON_BUTTON[0]
