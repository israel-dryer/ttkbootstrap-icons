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
    root = name.split(".")[0]
    if root in ("PySimpleGUI", "FreeSimpleGUI"):
        raise ImportError("blocked for this test: " + name)
    return _real(name, *args, **kwargs)
builtins.__import__ = _blocked
for _name in list(sys.modules):
    if _name.split(".")[0] in ("PySimpleGUI", "FreeSimpleGUI"):
        del sys.modules[_name]
"""


def run_child(body: str) -> subprocess.CompletedProcess:
    """Run `body` in a fresh interpreter with both flavors unimportable."""
    source = BLOCK_PSG + textwrap.dedent(body)
    return subprocess.run(
        [sys.executable, "-c", source],
        capture_output=True, text=True, timeout=120,
    )


def psg():
    """The installed flavor, or skip."""
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
        assert "pip install FreeSimpleGUI" in message
        # It must also point at the path that needs no install at all.
        assert "render_data" in message

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


class TestFlavorResolution:
    def test_a_loaded_flavor_wins_over_importing_one(self):
        """The application's own import decides, which is the whole rule."""
        sg = psg()
        from tkinter_icons.extensions.psg import resolve_flavor

        assert resolve_flavor() is sg

    def test_iconbutton_subclasses_that_flavor(self):
        sg = psg()
        from tkinter_icons.extensions.psg import IconButton

        assert issubclass(IconButton, sg.Button)
        assert IconButton._flavor == "PySimpleGUI"

    def test_the_class_is_built_once_per_flavor(self):
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
            kwargs.setdefault("icon", Icon(sample_name, 24, "#ff0000"))
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

        # Press reaches `active` on every platform, so the pressed image is
        # genuinely exercised rather than only the resting one.
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

    def test_a_color_change_re_tints_the_icon(self, build):
        """update(button_color=...) moves what the icon was derived from."""
        button, window = build(use_ttk_buttons=False)
        before = dict(button._state_colors)
        button.update(button_color=("#00ff00", None))
        window.refresh()
        assert button._state_colors[""] != before[""]

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

    def test_repeated_redraws_do_not_stack_tk_bindings(self, build):
        """`add="+"` would append a duplicate handler on every re-render."""
        button, window = build(use_ttk_buttons=False, reactive_states={"pressed": "#0000ff"})
        first = button.Widget.bind("<ButtonPress-1>")
        for _ in range(3):
            button.update(compound="top")
            button.update(compound="left")
        window.refresh()
        assert button.Widget.bind("<ButtonPress-1>") == first
