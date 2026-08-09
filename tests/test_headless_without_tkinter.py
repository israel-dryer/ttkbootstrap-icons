"""The pure-PIL path must work on a machine with no Tk at all.

`render.py` has never had a Tkinter import, but `__init__.py` imports `icon.py`
and `icon.py` imported `tkinter` at module scope — so `import tkinter_icons`
raised `ImportError` wherever Tk was absent, and the renderer behind it was
unreachable. On Linux `tkinter` is a distro package (`python3-tk`), not part of
a pip install, so the environments the headless guide is written for — a slim
CI image, `python:3.12-slim`, a thumbnail worker — are exactly the ones that
lack it. Pillow, which does all the drawing, is already a dependency.

Run in a **subprocess**, not by patching `sys.meta_path` in-process. Blocking
`tkinter` here would mean unimporting `tkinter`, `PIL.ImageTk` and every
`tkinter_icons` module and letting them all load again under the block, in a
suite whose Tk tests are already order-sensitive. A child interpreter is both
a cleaner simulation of the real machine and incapable of breaking a later
test.

The blocker matches `tkinter` exactly or as a dotted prefix, never as a string
prefix: `tkinter_icons` starts with `tkinter`, and a blocker written with
`startswith("tkinter")` would block the package under test and "pass" by
failing for entirely the wrong reason. `test_the_blocker_does_not_block_the_library`
is that check.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest

from tkinter_icons.packs import KNOWN_PACKS

INSTALLED = [pack for pack in KNOWN_PACKS if pack.is_installed]

BLOCK_TKINTER = '''
import sys


class NoTkinter:
    """Refuse `tkinter` and its submodules, as a box without python3-tk would.

    `tkinter_icons` is deliberately not matched: it is not `tkinter`, and it is
    not under `tkinter.`.
    """

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "tkinter" or fullname.startswith("tkinter."):
            raise ImportError(f"No module named {fullname!r} (simulated: no python3-tk)")
        return None


sys.meta_path.insert(0, NoTkinter())

# Prove the block is real before concluding anything from what follows.
try:
    import tkinter
except ImportError:
    pass
else:
    raise SystemExit("the tkinter blocker did not work; the rest proves nothing")
'''


def run_without_tkinter(body: str):
    """Run `body` in a child interpreter that cannot import `tkinter`."""
    script = BLOCK_TKINTER + textwrap.dedent(body)
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
    )


def check(body: str):
    result = run_without_tkinter(body)
    assert result.returncode == 0, (
        f"the pure-PIL path failed without tkinter installed\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    return result


def test_the_blocker_does_not_block_the_library():
    """The floor: a blocker that also hides `tkinter_icons` proves nothing.

    `tkinter_icons` shares its first seven characters with `tkinter`, which is
    the same shape as the `.git`/`.github` prefix bug this project has already
    been bitten by. If this ever fails, every other test in the file is
    passing for the wrong reason.
    """
    result = check(
        """
        import tkinter_icons
        print("imported", tkinter_icons.__name__)
        """
    )
    assert "imported tkinter_icons" in result.stdout


def test_importing_the_package_does_not_need_tkinter():
    check(
        """
        import tkinter_icons
        from tkinter_icons import Icon, RenderOptions, render_glyph, measure_ink_bounds
        assert "tkinter" not in sys.modules, "something imported tkinter after all"
        """
    )


def test_render_glyph_draws_without_tkinter():
    """The lower-level entry point, which never had a reason to need Tk."""
    pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
    if pack is None:
        pytest.skip("the bootstrap pack is not installed")

    check(
        f"""
        import importlib
        from tkinter_icons import render_glyph
        from tkinter_icons.iconset import get_icon_set

        module = importlib.import_module("{pack.module}.provider")
        provider = next(
            obj() for name, obj in vars(module).items()
            if name.endswith("FontProvider") and name != "BaseFontProvider"
        )
        style, glyph = provider.resolve_icon("house", None)
        icon_set = get_icon_set(provider, style)
        img = render_glyph(
            glyph, 32, "#000000",
            font_key=icon_set.font_key,
            font_bytes=icon_set.font_bytes,
            ink=icon_set.ink(glyph),
            options=icon_set.options,
        )
        assert img.getchannel("A").getbbox() is not None, "render_glyph drew nothing"
        assert "tkinter" not in sys.modules
"""
    )


def test_render_pil_draws_without_tkinter():
    """The documented headless entry point, on a pack class."""
    pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
    if pack is None:
        pytest.skip("the bootstrap pack is not installed")

    check(
        f"""
        from tkinter_icons import {pack.icon_class}

        img = {pack.icon_class}.render_pil("house", size=32, color="#000000")
        assert img.getchannel("A").getbbox() is not None, "render_pil drew nothing"
        assert "tkinter" not in sys.modules
        """
    )


def test_saving_a_png_works_without_tkinter():
    """The whole worked example from the headless guide, end to end."""
    pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
    if pack is None:
        pytest.skip("the bootstrap pack is not installed")

    check(
        f"""
        import tempfile, pathlib
        from tkinter_icons import {pack.icon_class}

        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "house.png"
            {pack.icon_class}.render_pil("house", size=64).save(out)
            assert out.stat().st_size > 0, "wrote an empty file"
        assert "tkinter" not in sys.modules
        """
    )


def test_the_widget_path_still_reports_the_missing_dependency():
    """Deferring an import must not turn a clear failure into a confusing one.

    Reaching `.image` without Tk is a genuine error and has to stay one. What
    it must not become is an `AttributeError` or a `NameError` from the
    deferred import site — the caller asked for a widget image on a machine
    with no Tk, and `ImportError` naming `tkinter` is the honest answer.
    """
    pack = next((p for p in INSTALLED if p.extra == "bootstrap"), None)
    if pack is None:
        pytest.skip("the bootstrap pack is not installed")

    result = check(
        f"""
        from tkinter_icons import {pack.icon_class}

        icon = {pack.icon_class}("house", size=32)   # constructing is fine; it draws nothing yet
        try:
            icon.image
        except ImportError as exc:
            assert "tkinter" in str(exc), f"unhelpful message: {{exc}}"
            print("raised ImportError as expected")
        else:
            raise SystemExit("reaching .image without Tk should have raised ImportError")
        """
    )
    assert "raised ImportError as expected" in result.stdout
