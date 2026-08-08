"""What the shipped icon browser depends on, and must keep working.

The window icon ships with the base package. It used to be borrowed from
`[bootstrap]` inside a bare `except ImportError`, which meant a default install
— the base package ships no glyphs — got no icon at all, silently. These tests
guard the replacement: the mark is package data of `tkinter_icons` itself, so it
is present on every install, and a build that drops it fails here rather than in
a screenshot months later.

The browser is also the one shipped consumer of name resolution, so a change to
the resolution rules can degrade it without failing anything else. It catches
broadly enough not to crash — every icon it builds sits inside a `try` — but a
name that stops resolving becomes a red "Error" tile in the grid, an "✕" in the
preview, and "N/A" for the codepoint. That is a silent-in-CI regression of
exactly the kind this project keeps finding by eye, so the names it puts on
screen are checked here.
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
def test_the_browser_degrades_instead_of_raising(root, monkeypatch):
    """The property that makes it shippable: a broken name must not kill it.

    The checks above say every name currently resolves. This one says it does
    not matter if that stops being true — the browser is an application a user
    runs, not a library call, so a name it cannot draw has to become a tile it
    can, and never a traceback in a terminal.

    Forced rather than waited for: every resolution raises, which is worse than
    any real breakage, and the window has to still be standing afterwards.
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
    tiles = [
        grid.canvas.itemcget(item, "text")
        for item in grid.canvas.find_all()
        if grid.canvas.type(item) == "text"
        and str(grid.canvas.itemcget(item, "text")).startswith("Error")
    ]
    assert len(tiles) == len(names), (
        f"expected every name to degrade to an error tile, got {len(tiles)} of {len(names)}"
    )


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
