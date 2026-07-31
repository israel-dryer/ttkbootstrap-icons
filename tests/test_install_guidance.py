"""Every surface that tells a user how to install a pack must say the same thing.

The library's premise is one library with packs as extras. Guidance that still
names raw distributions teaches the pattern being retired, and guidance that
drifts from the catalogue goes stale the moment a pack is added or renamed. So
these are checked against `packs.py` rather than written out again here.
"""

from __future__ import annotations

import inspect

import pytest

from tkinter_icons import browser
from tkinter_icons.packs import KNOWN_PACKS, find_pack, missing_pack_message, no_packs_message
from tkinter_icons.registry import LEGACY_PROVIDER_GROUP, PROVIDER_GROUP
from tkinter_icons.tools import build_all


class TestExtrasFormEverywhere:
    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_install_command_uses_quoted_extras(self, pack):
        assert pack.install_command == f'pip install "tkinter-icons[{pack.extra}]"'

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_install_command_never_names_the_raw_distribution(self, pack):
        assert pack.distribution not in pack.install_command

    def test_messages_use_the_extras_form(self):
        for text in (no_packs_message(), missing_pack_message("material")):
            assert 'pip install "tkinter-icons[' in text

    def test_browser_builds_its_guidance_from_the_catalogue(self):
        """The no-packs screen is the first thing a new user sees.

        It used to hardcode `pip install tkinter-icons-bs`, contradicting the
        extras framing at the one moment it matters most.
        """
        source = inspect.getsource(browser.IconPreviewerApp)
        assert "KNOWN_PACKS" in source, "browser should generate guidance from the catalogue"
        assert "pip install tkinter-icons-" not in source, "raw distribution install command in browser"


class TestShimMigrationMessageIsInstallable:
    """The rename warning is an install instruction, and pip will not check it.

    An unknown extra does not fail: pip prints `does not provide the extra` and
    installs the base package, which has no glyphs. So a stale extra here walks
    the user into exactly the state the rest of the same message warns about.
    It named `[all]`, which was removed when the aggregate extra was dropped.
    """

    @staticmethod
    def _extras_named_in_the_warning() -> list[str]:
        import pathlib
        import re

        import ttkbootstrap_icons

        source = pathlib.Path(ttkbootstrap_icons.__file__).read_text(encoding="utf-8-sig")
        warning = source.split("warnings.warn(", 1)[1].split("FutureWarning", 1)[0]
        return [
            extra.strip()
            for group in re.findall(r"tkinter-icons\[([^\]]+)\]", warning)
            for extra in group.split(",")
        ]

    def test_the_warning_names_at_least_one_extra(self):
        pytest.importorskip("ttkbootstrap_icons")
        assert self._extras_named_in_the_warning()

    def test_every_extra_it_names_exists(self):
        pytest.importorskip("ttkbootstrap_icons")
        known = {pack.extra for pack in KNOWN_PACKS}
        unknown = [extra for extra in self._extras_named_in_the_warning() if extra not in known]
        assert not unknown, f"migration warning tells users to install extras that do not exist: {unknown}"


class TestProviderDiscoveryIsConsistent:
    """Every discovery site must scan both entry-point groups.

    `registry.py` scans both so packs published before the rename stay
    discoverable. A tool scanning only the new group reports "no providers"
    for a pack the rest of the library can see.
    """

    def test_build_all_scans_both_groups(self, monkeypatch):
        scanned = []

        def _entry_points(*, group):
            scanned.append(group)
            return []

        monkeypatch.setattr(build_all, "entry_points", _entry_points)
        build_all.discover_provider_packages()
        assert set(scanned) == {PROVIDER_GROUP, LEGACY_PROVIDER_GROUP}

    def test_build_all_finds_a_legacy_pack(self, monkeypatch):
        class _EP:
            name = "mat"
            value = "ttkbootstrap_icons_mat.provider:Provider"

        def _entry_points(*, group):
            return [_EP()] if group == LEGACY_PROVIDER_GROUP else []

        monkeypatch.setattr(build_all, "entry_points", _entry_points)
        assert build_all.discover_provider_packages() == [("mat", "ttkbootstrap_icons_mat")]

    def test_build_all_does_not_double_count(self, monkeypatch):
        class _EP:
            name = "bs"
            value = "tkinter_icons_bs.provider:Provider"

        shared = _EP()
        monkeypatch.setattr(build_all, "entry_points", lambda *, group: [shared])
        assert build_all.discover_provider_packages() == [("bs", "tkinter_icons_bs")]

    def test_discovered_base_package_is_the_top_level_module(self):
        """The base package must be the pack's top-level module.

        This returned 'tkinter_icons_fa.provider', so run_quick_for imported
        'tkinter_icons_fa.provider.tools.generate_assets' — nonexistent — and the
        bare except there reported every provider as failed with no explanation.

        Not every pack has a generator: packs whose assets are vendored rather
        than built from upstream have no `tools` subpackage, and build_all
        skipping them is correct. What must hold is that the name resolves.
        """
        import importlib.util

        found = build_all.discover_provider_packages()
        if not found:
            pytest.skip("no providers installed")
        for name, base_pkg in found:
            assert "." not in base_pkg, f"{name}: {base_pkg} is not a top-level package"
            assert importlib.util.find_spec(base_pkg) is not None, f"{name}: {base_pkg} not importable"


class TestStaticReExports:
    """Both spellings of a renamed pack class must resolve for type checkers.

    Under PEP 484 `from X import A as B` binds only `B`, so aliasing alone
    would leave the short names without IDE support while they work fine at
    runtime — breaking the promise in `Pack.export_names`.
    """

    def test_type_checking_block_exports_every_spelling(self):
        import pathlib

        import tkinter_icons

        source = pathlib.Path(tkinter_icons.__file__).read_text(encoding="utf-8")
        block = source.split("if TYPE_CHECKING:", 1)[1].split("\n_CORE", 1)[0]

        missing = [
            name
            for pack in KNOWN_PACKS
            for name in pack.export_names
            if f" as {name}\n" not in block
        ]
        assert not missing, f"names bound only at runtime, not for type checkers: {missing}"

    def test_renamed_packs_declare_two_spellings(self):
        pack = find_pack("fontawesome")
        assert set(pack.export_names) == {"FontAwesomeIcon", "FAIcon"}
