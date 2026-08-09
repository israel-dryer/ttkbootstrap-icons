"""What the shipped icon browser depends on, and must keep working.

The window icon ships with the base package. It used to be borrowed from
`[bootstrap]` inside a bare `except ImportError`, which meant a default install
— the base package ships no glyphs — got no icon at all, silently. These tests
guard the replacement: the mark is package data of `tkinter_icons` itself, so it
is present on every install, and a build that drops it fails here rather than in
a screenshot months later.

The browser is also the one shipped consumer of name resolution, so a change to
the resolution rules can degrade it without failing anything else. It catches
broadly enough not to crash — every icon it builds sits inside a `try` — and a
name it cannot draw now leaves an empty cell in the grid, a blank preview, and
"—" for the codepoint. That is the whole problem: the failure is invisible by
design, so nothing about it is visible in CI either. It used to be a red "Error"
tile and an "✕", which was at least loud; quieting it for the user is what makes
checking it here necessary rather than optional. Both directions are covered —
that every name it lists resolves, and that a name which stops resolving still
reaches nobody.
"""

from __future__ import annotations

import importlib
import tkinter as tk
from importlib.resources import files

import pytest

from tkinter_icons.iconset import get_icon_set
from tkinter_icons.packs import KNOWN_PACKS

INSTALLED = [pack for pack in KNOWN_PACKS if pack.is_installed]

# The sizes `_set_app_icon` asks for. Tk picks per use: 32 for the title bar,
# 64 for the taskbar and Alt-Tab.
SIZES = (32, 64)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("size", SIZES)
def test_app_icon_is_packaged(size):
    resource = files("tkinter_icons.assets").joinpath(f"icon-{size}.png")
    assert resource.is_file(), f"icon-{size}.png is missing from tkinter_icons.assets"


@pytest.mark.parametrize("size", SIZES)
def test_app_icon_is_a_real_png(size):
    """Readable as bytes and actually a PNG.

    `_set_app_icon` hands the bytes to Tk base64-encoded rather than by path, so
    that it works from a zipped install — `read_bytes` is the operation that has
    to keep working, not `os.path.exists`.
    """
    raw = files("tkinter_icons.assets").joinpath(f"icon-{size}.png").read_bytes()
    assert raw.startswith(PNG_MAGIC)


def test_browser_does_not_borrow_a_pack_glyph_for_its_icon():
    """The regression this replaced: no pack import in the app-icon path."""
    from tkinter_icons import browser

    source = browser._set_app_icon.__code__.co_consts
    assert not any(
        isinstance(c, str) and c.startswith("tkinter_icons_") for c in source
    ), "the window icon must not depend on an icon pack being installed"


def provider_for(pack):
    module = importlib.import_module(f"{pack.module}.provider")
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class in {pack.module}.provider")


@pytest.mark.parametrize("pack", INSTALLED, ids=lambda p: p.extra)
def test_every_name_the_browser_lists_still_resolves(pack):
    """The browser's own call, on its own names, for every style it offers.

    `BrowserGrid._draw` and the detail panel both do exactly this — take a name
    out of `build_display_index()["names_by_style"]` and resolve it against the
    style it was listed under. Those are *glyph* names, the values of the
    lookup rather than its keys, which is a different population from the one
    the resolution tests sweep; a rule that handles friendly names perfectly
    could still strand these.
    """
    provider = provider_for(pack)

    checked = 0
    broken = []
    for style, names in provider.build_display_index()["names_by_style"].items():
        lookup_style = None if style == "base" else style
        icon_set = get_icon_set(provider, lookup_style)
        for name in names:
            checked += 1
            try:
                resolved = provider.resolve_icon_name(name, style=lookup_style)
            except ValueError as exc:
                broken.append((style, name, str(exc)))
                continue
            if icon_set.glyph(resolved) is None:
                broken.append((style, name, f"{resolved} absent from the set"))

    assert not broken, (
        f"{len(broken)} of {checked} name(s) the browser lists for {pack.extra} would "
        f"draw as an error tile: {broken[:5]}"
    )
    assert checked, f"the browser would list no names at all for {pack.extra}"


@pytest.mark.gui
def test_the_browser_draws_every_icon_it_puts_on_screen(root):
    """The positive half: resolution succeeding is not the same as an icon.

    `test_every_name_the_browser_lists_still_resolves` checks resolution
    directly, which is one step short of what the user sees — a name can
    resolve and still draw nothing, because `_render_visible` builds the `Icon`
    and hands its `.image` to the canvas inside the same `try` that swallows a
    resolution failure. Anything raised in that second half produces exactly
    what a bad name produces: an empty cell, silently.

    Asserted per cell the grid actually attempted rather than against a total.
    The grid is virtualized, so how many cells it reaches depends on the
    viewport, and a count quoted here would be a property of this test's window
    size rather than of the browser.

    Every pack runs against **one** root rather than the file's usual
    parametrize-per-pack, which would ask Tk 8.6 for sixteen interpreters in
    one process — the thing it cannot reliably do. Failures name the pack and
    style instead, so the parametrize buys nothing here.
    """
    from tkinter_icons import browser

    failures = []
    attempted = 0
    for pack in INSTALLED:
        provider = provider_for(pack)
        for style, names in provider.build_display_index()["names_by_style"].items():
            lookup_style = None if style == "base" else style
            frame = tk.Frame(root)
            frame.pack()
            try:
                grid = browser.SimpleIconGrid(
                    frame, provider, list(names), icon_size=32, icon_style=lookup_style
                )
                grid.canvas.configure(width=700, height=400)
                root.update_idletasks()
                grid._render_visible()

                cells = len(grid.visible_items)
                blank = [
                    grid.filtered[idx]
                    for idx, (items, _icon) in grid.visible_items.items()
                    if not items
                ]
                if blank:
                    failures.append(
                        f"{pack.extra}/{style}: {len(blank)} of {cells} cells empty {blank[:3]}"
                    )
                text = [
                    item for item in grid.canvas.find_all() if grid.canvas.type(item) == "text"
                ]
                if text:
                    failures.append(f"{pack.extra}/{style}: {len(text)} text item(s) on screen")
                if not cells:
                    failures.append(f"{pack.extra}/{style}: drew nothing at all")
                attempted += cells
            finally:
                frame.destroy()

    assert not failures, f"{len(failures)} pack/style combination(s) failed: {failures[:5]}"
    assert attempted, "the browser drew nothing for any pack"


@pytest.mark.gui
def test_the_browser_fails_invisibly(root, monkeypatch):
    """The property that makes it shippable, in the form an app needs.

    The checks above say every name currently resolves. This one says it does
    not matter if that stops being true. Two things have to hold, and the
    second is the one that is easy to get wrong:

    1. Nothing propagates. It is an application a user runs, not a library
       call, so a name it cannot draw must never become a traceback.
    2. Nothing is *shown*. The browser used to paint a red "Error <name>" tile
       and mark the preview "✕", which is a diagnostic in front of someone who
       can do nothing with it. Surviving is not the same as staying quiet, and
       an earlier version of this very test asserted the error tiles were
       drawn — it would have passed against the behavior being removed here.

    Forced rather than waited for: every resolution raises, which is worse than
    any plausible breakage.
    """
    from tkinter_icons import browser
    from tkinter_icons.providers import BaseFontProvider

    pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
    if pack is None:
        pytest.skip("the bootstrap pack is not installed")
    provider = provider_for(pack)
    names = list(provider.build_display_index()["names_by_style"]["outline"])[:12]

    def always_fails(self, name, style=None):
        raise ValueError(f"simulated failure for {name}")

    monkeypatch.setattr(BaseFontProvider, "resolve_icon_name", always_fails)

    frame = tk.Frame(root)
    frame.pack()
    grid = browser.SimpleIconGrid(frame, provider, names, icon_size=32, icon_style="outline")
    root.update_idletasks()

    assert root.winfo_exists(), "the window did not survive a resolution failure"

    drawn = [
        str(grid.canvas.itemcget(item, "text"))
        for item in grid.canvas.find_all()
        if grid.canvas.type(item) == "text"
    ]
    assert not drawn, f"the grid put text on screen for icons it could not draw: {drawn[:5]}"

    images = [item for item in grid.canvas.find_all() if grid.canvas.type(item) == "image"]
    assert not images, "the grid drew an image for a name that does not resolve"


@pytest.mark.gui
def test_a_raising_callback_prints_nothing(root, capsys):
    """Tk's own traceback path, which no amount of guarding call sites closes.

    Every exception raised inside an event handler goes to
    `Tk.report_callback_exception`, which by default writes "Exception in
    Tkinter callback" and a full stack trace to stderr. Someone who typed
    `tkinter-icons` to look at some icons would read a traceback about a widget
    they did not know existed.

    A dozen handlers exist, several do real work outside any `try`, and the
    next one added would be unguarded again — so the default is replaced rather
    than each caller wrapped.
    """
    from tkinter_icons import browser

    browser._silence_callback_errors(root)

    def explode():
        raise RuntimeError("failure inside an event handler")

    button = tk.Button(root, text="x", command=explode)
    button.pack()
    root.update_idletasks()
    button.invoke()
    root.update()

    assert root.winfo_exists(), "the window did not survive a raising callback"
    captured = capsys.readouterr()
    assert "Traceback" not in captured.err, f"a traceback reached the user: {captured.err[:300]}"
    assert "Exception in Tkinter callback" not in captured.err
    assert captured.out == ""


@pytest.mark.gui
def test_main_never_lets_an_error_escape(monkeypatch, capsys):
    """The console script is the whole app, so nothing may escape it.

    `main` creates the root, so it is where the callback default is replaced
    and where a startup failure has to stop. Nothing about this is reachable
    normally — it is the last line of defense for a user who typed a command
    and expects a window, not a stack trace.
    """
    from tkinter_icons import browser

    monkeypatch.setattr(tk.Tk, "mainloop", lambda self: None)

    # `main` creates its own root, and with `mainloop` stubbed out nothing
    # destroys it. A root left alive breaks the next test that needs a fresh
    # interpreter — Tk 8.6 cannot reliably create a second one in a process —
    # so it is captured here and torn down. Getting this wrong is invisible in
    # this file and fails somewhere else entirely.
    real_tk = tk.Tk
    created = []

    def capture(*args, **kwargs):
        window = real_tk(*args, **kwargs)
        created.append(window)
        return window

    monkeypatch.setattr(tk, "Tk", capture)

    def explode(root):
        raise RuntimeError("catastrophic startup failure")

    monkeypatch.setattr(browser, "IconPreviewerApp", explode)

    try:
        browser.main()  # must not raise
    finally:
        for window in created:
            try:
                window.destroy()
            except tk.TclError:
                pass

    captured = capsys.readouterr()
    assert "Traceback" not in captured.err, f"a traceback reached the user: {captured.err[:300]}"
    assert captured.out == ""


def test_no_display_is_not_a_traceback(monkeypatch, capsys):
    """The one failure a real user actually hits, and the one left uncovered.

    Everything else here is unreachable in a working install. This is not: run
    `tkinter-icons` over SSH, or on a box where Tk was never installed, and
    `tk.Tk()` itself raises. It sat outside the `try` in the first draft, so the
    single most likely way for this command to fail was the one way it still
    printed a stack trace.

    Needs no display of its own — the failure is simulated, which is the point.
    """
    from tkinter_icons import browser

    def no_display(*args, **kwargs):
        raise tk.TclError('no display name and no $DISPLAY environment variable')

    monkeypatch.setattr(tk, "Tk", no_display)

    browser.main()  # must not raise

    captured = capsys.readouterr()
    assert "Traceback" not in captured.err, f"a traceback reached the user: {captured.err[:300]}"
    assert captured.err == ""
    assert captured.out == ""


def test_the_browser_chrome_icons_resolve():
    """The two glyphs the browser draws itself, rather than from its catalog.

    Both sit in a `try`, so a failure is invisible: the link simply loses its
    icon. Bootstrap only, and skipped when it is absent, which is also the
    condition under which the browser does without them.
    """
    pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
    if pack is None:
        pytest.skip("the bootstrap pack is not installed")
    provider = provider_for(pack)

    for name in ("house", "file-earmark-text"):
        resolved = provider.resolve_icon_name(name, style="fill")
        assert get_icon_set(provider, "fill").glyph(resolved) is not None, (
            f"the browser's {name!r} link icon no longer resolves"
        )
