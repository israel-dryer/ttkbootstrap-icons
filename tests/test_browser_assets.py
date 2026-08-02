"""The icon browser's window icon ships with the base package.

It used to be borrowed from `[bootstrap]` inside a bare `except ImportError`,
which meant a default install — the base package ships no glyphs — got no icon
at all, silently. These tests guard the replacement: the mark is package data of
`tkinter_icons` itself, so it is present on every install, and a build that drops
it fails here rather than in a screenshot months later.
"""

from __future__ import annotations

from importlib.resources import files

import pytest

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
