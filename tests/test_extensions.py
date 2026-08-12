"""The PySimpleGUI integration, and the rule that keeps it optional.

PySimpleGUI is a separate installable that the caller brings. Two things follow,
and they need opposite environments to test:

* **With it absent**, importing `tkinter_icons` must not drag in a GUI toolkit,
  and asking for `IconButton` must say how to install one. Those run everywhere.
* **With it present**, the bridge itself has to be exercised against real
  widgets. Those skip where it is missing.

The absent-dependency checks run in a **subprocess** with the import blocked,
because this checkout has PySimpleGUI installed and `importorskip` cannot
simulate its absence. That is the same technique as
`test_headless_without_tkinter.py`, and for the same reason: unimporting a
package in-process, in a suite whose Tk tests are already order-sensitive, is
worse than spawning a child.

Note `pytest.importorskip` is called **inside** a helper rather than at module
scope. A module-level skip takes the whole file with it, which would silently
retire the absent-dependency tests — the ones that need PySimpleGUI gone, not
present.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest

BLOCK_PSG = """
import builtins, sys
_real = builtins.__import__
def _blocked(name, *args, **kwargs):
    if name.split(".")[0] == "PySimpleGUI":
        raise ImportError("blocked for this test: " + name)
    return _real(name, *args, **kwargs)
builtins.__import__ = _blocked
for _name in list(sys.modules):
    if _name.split(".")[0] == "PySimpleGUI":
        del sys.modules[_name]
"""


def run_child(body: str) -> subprocess.CompletedProcess:
    """Run `body` in a fresh interpreter with PySimpleGUI unimportable."""
    source = BLOCK_PSG + textwrap.dedent(body)
    return subprocess.run(
        [sys.executable, "-c", source],
        capture_output=True, text=True, timeout=120,
    )


def psg():
    """PySimpleGUI, or skip."""
    return pytest.importorskip(
        "PySimpleGUI", reason="the PySimpleGUI integration needs PySimpleGUI installed",
    )


class TestTheIntegrationStaysOptional:
    """A GUI toolkit must never become a load-time dependency of the base."""

    def test_importing_the_library_does_not_import_pysimplegui(self):
        result = run_child("""
            import tkinter_icons
            import tkinter_icons.extensions
            assert "PySimpleGUI" not in __import__("sys").modules
            print("clean")
        """)
        assert result.returncode == 0, result.stderr
        assert "clean" in result.stdout

    def test_the_extensions_package_does_not_import_its_submodules(self):
        """`extensions/__init__` importing `psg` would defeat the whole point."""
        result = run_child("""
            import tkinter_icons.extensions as ext
            assert not hasattr(ext, "psg"), "extensions/__init__ imported psg"
            print("clean")
        """)
        assert result.returncode == 0, result.stderr

    def test_asking_for_iconbutton_without_it_explains_the_install(self):
        result = run_child("""
            from tkinter_icons.extensions import psg
            try:
                psg.IconButton
            except psg.PySimpleGUINotInstalled as exc:
                print("MESSAGE:", str(exc).replace("\\n", " | "))
            else:
                raise AssertionError("expected PySimpleGUINotInstalled")
        """)
        assert result.returncode == 0, result.stderr
        message = result.stdout
        assert "pip install PySimpleGUI" in message
        # It must also point at the path that needs no install at all.
        assert "to_data" in message

    def test_the_error_is_an_importerror(self):
        """So `except ImportError` around an optional integration still works."""
        result = run_child("""
            from tkinter_icons.extensions import psg
            try:
                psg.IconButton
            except ImportError:
                print("caught as ImportError")
        """)
        assert "caught as ImportError" in result.stdout, result.stderr

    def test_the_blocker_does_not_block_the_library(self):
        """A blocker that also hid `tkinter_icons` would pass for the wrong reason."""
        result = run_child("""
            import tkinter_icons
            print("library imported:", bool(tkinter_icons.__name__))
        """)
        assert "library imported: True" in result.stdout, result.stderr

    def test_an_unknown_attribute_still_raises_attributeerror(self):
        """The module `__getattr__` must not turn every typo into an ImportError."""
        result = run_child("""
            from tkinter_icons.extensions import psg
            try:
                psg.NoSuchThing
            except AttributeError as exc:
                print("AttributeError:", exc)
        """)
        assert "AttributeError" in result.stdout, result.stderr


class TestTheClass:
    def test_iconbutton_subclasses_the_real_button(self):
        sg = psg()
        from tkinter_icons.extensions.psg import IconButton

        assert issubclass(IconButton, sg.Button)

    def test_the_class_is_built_once(self):
        """Built lazily, then cached -- two imports must not be two classes."""
        psg()
        from tkinter_icons.extensions.psg import IconButton
        from tkinter_icons.extensions import psg as module

        assert module.IconButton is IconButton


@pytest.mark.gui
class TestIconButton:
    """The bridge itself, against real widgets."""

    @pytest.fixture
    def build(self, icon_set, sample_name):
        """Build a one-button window, and always close it."""
        sg = psg()
        from tkinter_icons.extensions.psg import IconButton
        from tkinter_icons import Icon

        windows = []

        def make(**kwargs):
            # No color: the documented default, where the icon follows the
            # button. Tests that need a chosen color pass one.
            kwargs.setdefault("icon", Icon(sample_name, 24))
            use_ttk = kwargs.pop("use_ttk_buttons", True)
            button = IconButton("Go", key="-B-", use_ttk_buttons=use_ttk, **kwargs)
            try:
                window = sg.Window("t", [[button]], finalize=True, location=(50, 50))
            except Exception as exc:  # pragma: no cover - environment, not the code
                # Two different causes, and calling both "no display" would
                # misreport one of them. Either there is genuinely no display,
                # or this is Tk 8.6 failing to build a second interpreter in
                # one process -- a known limitation `CLAUDE.md` records, which
                # surfaces as `invalid command name "tcl_findLibrary"` and
                # depends on test ordering rather than on anything here.
                pytest.skip(f"could not create a Tk window: {type(exc).__name__}: {exc}")
            windows.append(window)
            return button, window

        yield make

        # Closing the windows is not enough. PySimpleGUI keeps a hidden master
        # root of its own and leaves it — and `tkinter._default_root` — alive
        # afterward, which breaks any later test that needs to control when a
        # root exists. `TestTkLifecycle` is exactly that, and failed only when
        # this file ran before it.
        import tkinter

        for window in windows:
            window.close()
        sg.Window._active_windows.clear()
        master = getattr(sg.Window, "hidden_master_root", None)
        if master is not None:
            try:
                master.destroy()
            except tkinter.TclError:  # pragma: no cover - already gone
                pass
            sg.Window.hidden_master_root = None
        tkinter._default_root = None

    def test_the_icon_is_on_before_the_first_paint(self, build):
        """Attaching on <Map> would land after the window is already shown.

        `finalize` packs the layout and sizes the window inside
        `update_idletasks`, which does not deliver events — so this passing is
        what says the trigger is an idle callback rather than a <Map> binding.
        """
        button, _window = build()
        assert button._icon_attached

    def test_the_window_does_not_resize_after_it_is_shown(self, build):
        """The visible half of the same point."""
        button, window = build()
        before = window.TKroot.winfo_geometry()
        for _ in range(3):
            window.refresh()
            window.TKroot.update_idletasks()
        assert window.TKroot.winfo_geometry() == before

    def test_ttk_gets_a_real_per_state_image_map(self, build):
        from tkinter import ttk

        button, _window = build(
            use_ttk_buttons=True,
            reactive_states={"hover": "#00ff00", "pressed": "#0000ff", "disabled": "#888888"},
        )
        mapped = ttk.Style().map(button.Widget.cget("style"), "image")
        states = {entry[0] for entry in mapped if isinstance(entry, (tuple, list)) and entry[:1]}
        # hover translates to ttk's "active" -- the reason this module does not
        # reuse that word.
        assert "active" in states
        assert "pressed" in states
        assert "disabled" in states

    def test_tk_has_no_hover_and_says_so(self, build):
        """A tk.Button reaches `pressed` and `disabled`, never `hover`."""
        with pytest.warns(UserWarning, match="no hover state"):
            button, _window = build(
                use_ttk_buttons=False,
                reactive_states={"hover": "#00ff00", "pressed": "#0000ff"},
            )
        assert "pressed" in button._state_images
        assert "hover" not in button._state_images

    def test_the_tk_icon_follows_the_widgets_own_state(self, build):
        """Not inferred from the pointer -- read back off `-state`.

        The invariant is "the image matches whatever Tk says the state is",
        and that is deliberately **not** the same as "hover changes nothing".
        `button.tcl` defines `tk::ButtonEnter` once per windowing system: win32
        and aqua set `-state active` only while button 1 is already down, while
        x11 sets it on entry outright -- "on unix the state is active just with
        mouse-over", in Tk's own comment.

        An earlier version of this test asserted the win32 behavior as
        universal and failed on Linux against code that was doing exactly the
        right thing. Assert the mapping, not one platform's Tk.
        """
        from tkinter_icons.extensions.psg import _TK_STATE_KEYS

        button, window = build(use_ttk_buttons=False, reactive_states={"pressed": "#0000ff"})
        widget = button.Widget

        def settle():
            window.TKroot.update_idletasks()
            window.TKroot.update()
            return str(widget.cget("state")), str(widget.cget("image"))

        def expected(state):
            return str(button._state_images.get(_TK_STATE_KEYS.get(state, ""),
                                                button._state_images[""]))

        for event in ("<Enter>", "<ButtonPress-1>", "<ButtonRelease-1>", "<Leave>"):
            widget.event_generate(event, x=5, y=5)
            state, image = settle()
            assert image == expected(state), f"after {event}: -state={state} but image did not match"

        # Press *while inside* reaches `active` on both, so the pressed image
        # is genuinely exercised rather than only the resting one. The <Enter>
        # is load-bearing and not decoration: the loop above ends on <Leave>,
        # and on x11 a press from outside does not set the state at all --
        # there it is <Enter> that does, which is the same platform split this
        # test exists to stop being written into an assertion.
        widget.event_generate("<Enter>", x=5, y=5)
        widget.event_generate("<ButtonPress-1>", x=5, y=5)
        state, image = settle()
        assert state == "active"
        assert image == str(button._state_images["pressed"])

    def test_disabling_swaps_the_tk_image(self, build):
        """A tk.Button has no disabled image, only disabledforeground."""
        button, window = build(use_ttk_buttons=False, reactive_states={"disabled": "#888888"})
        rest = str(button.Widget.cget("image"))
        button.update(disabled=True)
        window.refresh()
        assert str(button.Widget.cget("image")) == str(button._state_images["disabled"])
        button.update(disabled=False)
        window.refresh()
        assert str(button.Widget.cget("image")) == rest

    def test_an_unset_color_follows_the_button(self, build, sample_name):
        """The whole reason the examples pass no color."""
        from tkinter_icons import Icon

        button, _window = build(use_ttk_buttons=False, icon=Icon(sample_name, 24))
        foreground = button.Widget.cget("foreground")
        expected = button.Widget.winfo_rgb(foreground)
        actual = button.Widget.winfo_rgb(button._state_colors[""])
        assert actual == expected

    def test_a_chosen_color_is_kept(self, build, sample_name):
        """Silently overriding an argument the caller wrote is the failure mode
        this project keeps writing guards against."""
        from tkinter_icons import Icon

        button, _window = build(use_ttk_buttons=False, icon=Icon(sample_name, 24, "#ff00ff"))
        assert button._state_colors[""] == "#ff00ff"

    def test_a_chosen_color_does_not_freeze_the_other_states(self, build, sample_name):
        """Choosing a resting color must not opt out of reacting."""
        from tkinter_icons import Icon

        button, _window = build(use_ttk_buttons=False, icon=Icon(sample_name, 24, "#ff00ff"))
        assert button._state_colors[""] == "#ff00ff"
        assert button._state_colors["disabled"] != "#ff00ff"
        assert "disabled" in button._state_images

    def test_a_resting_entry_in_reactive_states_outranks_the_icon(self, build, sample_name):
        """Two ways to name the resting color, and the explicit one wins."""
        from tkinter_icons import Icon

        button, _window = build(
            use_ttk_buttons=False,
            icon=Icon(sample_name, 24, "#ff00ff"),
            reactive_states={"": "#00ff00"},
        )
        assert button._state_colors[""] == "#00ff00"

    def test_a_color_change_re_tints_the_icon(self, build):
        """update(button_color=...) moves what the icon was derived from."""
        button, window = build(use_ttk_buttons=False)
        before = dict(button._state_colors)
        button.update(button_color=("#00ff00", None))
        window.refresh()
        assert button._state_colors[""] != before[""]

    def test_a_chosen_color_survives_a_button_color_change(self, build, sample_name):
        """The caller chose it, so a later theme-ish change must not take it."""
        from tkinter_icons import Icon

        button, window = build(use_ttk_buttons=False, icon=Icon(sample_name, 24, "#ff00ff"))
        button.update(button_color=("#00ff00", None))
        window.refresh()
        assert button._state_colors[""] == "#ff00ff"

    def test_the_icon_can_be_swapped(self, build, icon_set, sample_name):
        """A play/pause button is two glyphs on one element."""
        from tkinter_icons import Icon

        button, window = build(use_ttk_buttons=False)
        before = str(button.Widget.cget("image"))
        other = sorted(icon_set.glyphs)[1] if len(icon_set.glyphs) > 1 else sample_name
        button.update(icon=Icon(other, 24, "#0000ff"))
        window.refresh()
        assert str(button.Widget.cget("image")) != before

    def test_compound_can_be_moved(self, build):
        button, window = build()
        assert str(button.Widget.cget("compound")) == "left"
        button.update(compound="top")
        window.refresh()
        assert str(button.Widget.cget("compound")) == "top"

    def test_turning_states_off_returns_the_widget_to_its_own_style(self, build):
        """Otherwise it keeps an image map it was just told to stop applying."""
        from tkinter import ttk

        button, window = build(use_ttk_buttons=True, reactive_states={"pressed": "#0000ff"})
        derived = button.Widget.cget("style")
        button.update(reactive_states=False)
        window.refresh()
        plain = button.Widget.cget("style")
        assert plain != derived
        assert not ttk.Style().map(plain, "image")

    def test_a_chosen_color_does_not_cost_the_ttk_state_images(self, build, icon_set, sample_name):
        """The resting color is seeded into the state spec, not merged after it.

        `Icon.map` names the child style after the icon names *that call* uses,
        so a second merging call that named only the base icon derived a
        different style whenever the spec renamed a glyph — and the merge then
        landed on an empty map, leaving the widget wearing a style holding
        nothing but the resting image. Every reactive state disappeared, and
        only for the combination of a chosen color and a per-state name.
        """
        from tkinter import ttk

        from tkinter_icons import Icon

        other = sorted(icon_set.glyphs)[1] if len(icon_set.glyphs) > 1 else sample_name
        button, _window = build(
            use_ttk_buttons=True,
            icon=Icon(sample_name, 24, "#ff00ff"),
            reactive_states={"hover": "#00ff00", "disabled": {"name": other}},
        )
        # The trailing fallback comes back stateless — `(('pyimage12',),)` —
        # so only the entries whose first element is a state name are states.
        mapped = ttk.Style().map(button.Widget.cget("style"), "image")
        states = {entry[0] for entry in mapped if isinstance(entry[0], str)}
        assert {"active", "disabled"} <= states

    def test_a_chosen_color_does_not_remap_on_every_update(self, build, sample_name):
        """The color check compares against the parent style's foreground.

        Compared against the resting color instead it could never match once
        the caller had chosen one — `_state_colors[""]` *is* that chosen color
        — so an update that changed no color at all re-ran the whole state map,
        which combined with the seeding bug above re-lost the state images
        every time.
        """
        from tkinter_icons import Icon

        button, window = build(use_ttk_buttons=True, icon=Icon(sample_name, 24, "#ff00ff"))
        remaps = []
        real = button._map_ttk_states
        button._map_ttk_states = lambda: (remaps.append(1), real())[1]

        button.update(text="Go")
        window.refresh()
        assert remaps == []

        # And it still notices a color that genuinely moved.
        button.update(button_color=("#00ff00", None))
        window.refresh()
        assert remaps == [1]

    def test_a_ttk_theme_change_does_not_empty_the_state_map(self, build, sample_name):
        """`Icon.map` replays one mapping per widget, and the derived path makes two.

        PySimpleGUI reaches a ttk theme change without any user code touching
        ttk — `_change_ttk_theme` runs in seven element packers — and ttk's
        style database is per-theme, so the merging second call had nothing
        left to merge into and the widget was left with the resting image
        alone. The button adopted the new theme while its icon stopped
        reacting, silently.
        """
        from tkinter import ttk

        from tkinter_icons import Icon

        button, window = build(use_ttk_buttons=True, icon=Icon(sample_name, 24, "#ff00ff"))

        def states():
            mapped = ttk.Style().map(button.Widget.cget("style"), "image")
            return {entry[0] for entry in mapped if isinstance(entry[0], str)}

        assert states(), "the derived path mapped no states, so this proves nothing"

        style = ttk.Style()
        was = style.theme_use()
        # `alt` by name rather than "any other theme", because whether a state
        # can be derived at all is the target theme's business: under Windows'
        # `winnative` the button's foreground reads back as the symbolic
        # `SystemWindowText`, which Pillow rejects, so `Icon.map` skips the
        # state and only the fallback is left. That is not this bug, and a test
        # that picked the first available theme would be reporting it as one.
        other = "alt" if "alt" in style.theme_names() and was != "alt" else None
        if other is None:
            pytest.skip("needs a second ttk theme that derives a state color")
        try:
            style.theme_use(other)
            # `update()`, not `update_idletasks()`: `<<ThemeChanged>>` is a
            # queued virtual event and idle processing does not deliver it —
            # the same distinction the attach trigger turns on. Then an idle
            # pass, because the repair defers itself to one.
            window.TKroot.update()
            window.TKroot.update_idletasks()
            # Which states these are is the new theme's business — PySimpleGUI
            # does not restore its per-element style, so the button reverts to
            # the theme's own colors and the icon follows it there. That there
            # are any is this test's subject.
            assert states()
            # And that the repair itself ran, rather than the map surviving by
            # some accident of the theme.
            assert button._ttk_theme == other
            assert not button._theme_refresh_pending
        finally:
            style.theme_use(was)

    def test_an_empty_mapping_means_what_false_means(self, build, sample_name):
        """It names no states, so nothing reacts — on both paths.

        It used to give three answers from one input: an empty list is falsy,
        so `_parse_statespec` fell through to deriving from the style and the
        button reacted exactly as `True`; a chosen color seeded a `""` entry,
        which made the list truthy and stopped it reacting; and the tk path
        gave no reactive states at all.
        """
        from tkinter import ttk

        from tkinter_icons import Icon

        for chosen in (None, "#ff00ff"):
            icon = Icon(sample_name, 24) if chosen is None else Icon(sample_name, 24, chosen)
            empty, window = build(use_ttk_buttons=True, icon=icon, reactive_states={})
            mapped = ttk.Style().map(empty.Widget.cget("style"), "image")
            states = {entry[0] for entry in mapped if isinstance(entry[0], str)}
            assert not states, f"reacted with a chosen color of {chosen!r}"

        tk_button, _window = build(use_ttk_buttons=False, reactive_states={})
        assert set(tk_button._state_images) == {""}

    def test_the_disabled_colour_alone_moving_is_noticed(self, build, sample_name):
        """`disabled_button_color` writes the style's *map*, not its base value.

        Comparing only `style.lookup(parent, "foreground")` therefore never saw
        it, and the icon kept its old disabled tint while the label changed —
        on ttk only, since the tk path reads `disabledforeground` and did
        follow the same argument.
        """
        button, window = build(use_ttk_buttons=True)
        remaps = []
        real = button._map_ttk_states
        button._map_ttk_states = lambda: (remaps.append(1), real())[1]

        button.update(disabled_button_color=("#123456", None))
        window.refresh()
        assert remaps == [1]

    def test_the_capitalized_alias_is_not_the_base_one(self, build):
        """PySimpleGUI binds `Update = update` in `Button`'s own class body.

        Left alone, `Update` resolves to *that* function and skips everything
        this class adds — including the disabled swap below. PySimpleGUI calls
        it internally, so this is not only about callers who write it.
        """
        button, window = build(use_ttk_buttons=False, reactive_states={"disabled": "#888888"})
        assert type(button).Update is type(button).update

        button.Update(disabled=True)
        window.refresh()
        assert str(button.Widget.cget("image")) == str(button._state_images["disabled"])

    def test_updating_after_the_window_closed_does_not_raise(self, build, monkeypatch):
        """`sg.Button.update` returns early on a closed window rather than raising.

        Anything carrying on past it configures a destroyed widget, so the
        override has to stop where PySimpleGUI stops.
        """
        sg = psg()

        button, window = build(use_ttk_buttons=False, reactive_states={"disabled": "#888888"})
        window.close()
        # PySimpleGUI pops a *modal* traceback window on this path, which would
        # hang the suite waiting to be clicked. The switch that silences it is
        # a global inside the implementation module, not on the package.
        inner = sys.modules[sg.Button.__module__]
        monkeypatch.setattr(inner, "SUPPRESS_ERROR_POPUPS", True)
        # A redraw, not just a state change: `_refresh_for_colors` had a guard
        # of its own, so it is the `_apply_icon` path that reached a destroyed
        # widget and raised `TclError` out of `configure`.
        button.update(compound="top")
        button.update(disabled=True)

    def test_repeated_redraws_do_not_stack_tk_bindings(self, build):
        """`add="+"` would append a duplicate handler on every re-render."""
        button, window = build(use_ttk_buttons=False, reactive_states={"pressed": "#0000ff"})
        first = button.Widget.bind("<ButtonPress-1>")
        for _ in range(3):
            button.update(compound="top")
            button.update(compound="left")
        window.refresh()
        assert button.Widget.bind("<ButtonPress-1>") == first
