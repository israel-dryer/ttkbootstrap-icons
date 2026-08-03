"""Tests for PyInstaller support.

Freezing is the one place where a mistake here is invisible until someone else
runs the built application: the fonts are package *data*, so nothing fails at
import time, and a glyph with no font renders transparent by default. A frozen
app with a broken hook therefore starts up fine and simply draws nothing.

Both failures these tests cover had actually shipped. The hooks were never
registered with PyInstaller, so they were inert unless the user passed
`hookspath` by hand; and two of the sixteen packs had no hook file at all.
"""

from __future__ import annotations

import sys
from importlib.metadata import entry_points
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:  # 3.10 has no tomllib; tomli is the same API under the old name.
    tomllib = pytest.importorskip("tomli", reason="3.10 needs tomli to read pyproject.toml")

from tkinter_icons import get_hook_dirs
from tkinter_icons.packs import KNOWN_PACKS

REPO = Path(__file__).resolve().parent.parent
BASE_PYPROJECT = REPO / "packages" / "tkinter-icons" / "pyproject.toml"

#: The group PyInstaller scans for third-party hook directories.
HOOK_GROUP = "pyinstaller40"

#: This package's entry-point target. The *name* within the group is
#: conventionally `hook-dirs` for everyone, so the value is what identifies us.
TARGET = "tkinter_icons._pyinstaller:get_hook_dirs"


def hook_dir() -> Path:
    return Path(get_hook_dirs()[0])


class TestHookDirs:
    def test_returns_a_directory_that_exists(self):
        dirs = get_hook_dirs()
        assert dirs, "get_hook_dirs returned nothing"
        for entry in dirs:
            assert Path(entry).is_dir(), f"{entry} is not a directory"

    def test_the_directory_holds_hooks(self):
        assert list(hook_dir().glob("hook-*.py")), "no hook files in the hook directory"


class TestPyInstallerCanFindTheHooks:
    """The registration, without which every hook in the package is inert.

    PyInstaller discovers third-party hooks through a `pyinstaller40` entry
    point. Shipping hook files without it means they are only ever used by
    someone who already knew to pass `hookspath` - which is exactly the person
    who did not need them.
    """

    def test_pyproject_declares_the_entry_point(self):
        pyproject = tomllib.loads(BASE_PYPROJECT.read_text(encoding="utf-8"))
        group = pyproject["project"]["entry-points"][HOOK_GROUP]
        assert group["hook-dirs"] == TARGET

    def test_the_entry_point_is_installed_and_resolves(self):
        """Selected by value, not by name.

        `hook-dirs` is the conventional name in this group, so every package
        that ships hooks uses it — install PyInstaller itself and
        `_pyinstaller_hooks_contrib` registers a `hook-dirs` of its own. Taking
        the first match by name therefore resolves whichever package happens to
        sort first, which is a test that passes or fails on what else is in the
        environment rather than on anything this package does.
        """
        ours = [ep for ep in entry_points(group=HOOK_GROUP) if ep.value == TARGET]
        if not ours:
            pytest.skip("package installed before the entry point was added; reinstall to test")
        assert [Path(p) for p in ours[0].load()()] == [Path(p) for p in get_hook_dirs()]


class TestEveryPackHasAHook:
    """A pack with no hook loses its font when the application is frozen.

    `bs` and `fluent-reg` were both missing one, so a frozen application using
    Bootstrap or Fluent (Regular) icons drew nothing at all - and, because the
    missing-glyph policy is `transparent` by default, drew nothing *quietly*.
    """

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_pack_has_a_hook_file(self, pack):
        hook = hook_dir() / f"hook-{pack.module}.py"
        assert hook.is_file(), (
            f"{pack.distribution} has no PyInstaller hook. Add "
            f"{hook.name} calling collect_data_files({pack.module!r})."
        )

    def test_every_hook_names_a_known_pack(self):
        """No hook for a pack that no longer exists, which would fail the build."""
        modules = {pack.module for pack in KNOWN_PACKS} | {"tkinter_icons"}
        for hook in hook_dir().glob("hook-*.py"):
            assert hook.stem[len("hook-"):] in modules, f"{hook.name} names an unknown package"

    def test_each_hook_collects_its_own_package(self):
        for pack in KNOWN_PACKS:
            source = (hook_dir() / f"hook-{pack.module}.py").read_text(encoding="utf-8")
            assert f"collect_data_files('{pack.module}')" in source, (
                f"hook-{pack.module}.py does not collect {pack.module}"
            )