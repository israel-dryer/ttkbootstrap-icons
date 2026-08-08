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


class TestReadmesDoNotAdvertiseExtrasThatDoNotExist:
    """A README is an install instruction too, and it reaches further than the warning.

    The shim's warning was fixed when `[all]` was dropped; its README was not,
    and kept telling readers to run `pip install "tkinter-icons[all]"` on the
    package's own PyPI page. The warning had a test, the README had nothing.

    The failure is silent in both places for the same reason: pip does not treat
    an unknown extra as an error. It installs the base package, which has no
    glyphs, and the reader is left exactly where the surrounding text is warning
    them not to be.

    Docs pages are deliberately out of scope. `installation.rst` names
    `tkinter-icons[all]` on purpose, as the example of what fails quietly, and a
    check that could not tell that apart from an instruction would be pressure to
    delete the explanation.
    """

    @staticmethod
    def _repo_root():
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[1]
        if not (root / "packages").is_dir():
            pytest.skip("not running from a source checkout")
        return root

    def test_every_extra_named_in_a_readme_exists(self):
        import re

        root = self._repo_root()
        readmes = [p for p in [root / "README.md", *(root / "packages").glob("*/README.md")] if p.is_file()]
        assert readmes, "no READMEs found to check"

        known = {pack.extra for pack in KNOWN_PACKS}
        offenders = {}
        for readme in readmes:
            named = {
                extra.strip()
                for group in re.findall(
                    # Both spellings: pip normalises them, so `tkinter_icons[all]`
                    # is the same broken instruction and has to be caught too.
                    r"tkinter[-_]icons\[([^\]]+)\]", readme.read_text(encoding="utf-8-sig")
                )
                for extra in group.split(",")
            }
            if unknown := sorted(named - known):
                offenders[str(readme.relative_to(root))] = unknown
        assert not offenders, f"READMEs name extras that do not exist: {offenders}"


class TestTheCostOfInstallingEverythingIsMeasured:
    """The number that carries the whole argument for extras, checked against the packs.

    "There is no `[all]` extra" is justified in three places by the same figure,
    and a figure repeated in agreement is invisible when it is wrong — the #102
    review found "about 17 MB" stated identically in three files and correct in
    none of them. It was corrected in two; `installation.rst` kept saying 17 for
    another five days, because the fix that made the others agree had nothing to
    check them against.

    So this measures instead of comparing. The claim is rounded prose, so a
    whole megabyte of tolerance is the point: it fails when a pack is added or a
    font is replaced, not when a `.pyc` moves.
    """

    TOLERANCE_MB = 1.0

    #: The three places the argument against `[all]` is made. Scoped to a named
    #: list rather than swept from every `.rst`, because an unrelated size —
    #: a font's own weight on a pack page, a frozen bundle in `packaging.rst` —
    #: would otherwise fail this with "the docs give more than one size for
    #: installing every pack", which is not what went wrong. A fourth place
    #: making the same argument should be added here; a size figure about
    #: something else should not.
    SOURCES = (
        "docs/getting-started/installation.rst",
        "docs/packs.rst",
        "docs/user-guide/packaging.rst",
    )

    @staticmethod
    def _prose_claims():
        """Every `N MB` figure in the prose that argues against `[all]`."""
        import pathlib
        import re

        root = pathlib.Path(__file__).resolve().parents[1]
        if not (root / "docs").is_dir():
            pytest.skip("not running from a source checkout")

        found = {}
        for relative in TestTheCostOfInstallingEverythingIsMeasured.SOURCES:
            path = root / relative
            assert path.is_file(), f"{relative} is gone; update SOURCES"
            for match in re.finditer(r"(\d+(?:\.\d+)?) MB", path.read_text(encoding="utf-8-sig")):
                found.setdefault(float(match.group(1)), []).append(relative)
        return found

    @staticmethod
    def _measured_mb():
        """What the sixteen packs actually occupy once installed."""
        import importlib
        import pathlib

        missing = [pack.extra for pack in KNOWN_PACKS if not pack.is_installed]
        if missing:
            pytest.skip(f"needs every pack installed; missing {missing}")

        total = 0
        for pack in KNOWN_PACKS:
            module = importlib.import_module(pack.module)
            root = pathlib.Path(module.__file__).parent
            total += sum(
                f.stat().st_size
                for f in root.rglob("*")
                if f.is_file() and f.suffix not in (".pyc", ".pyo")
            )
        return total / 1e6

    def test_the_prose_states_one_figure(self):
        claims = self._prose_claims()
        assert claims, "no size claim found; the argument against [all] rests on one"
        assert len(claims) == 1, (
            f"the docs give more than one size for installing every pack: {claims}. "
            "They are all the same measurement, so they cannot disagree."
        )

    def test_that_figure_matches_the_installed_packs(self):
        claimed = next(iter(self._prose_claims()))
        measured = self._measured_mb()
        assert abs(claimed - measured) <= self.TOLERANCE_MB, (
            f"the docs say {claimed} MB but the sixteen packs measure {measured:.2f} MB"
        )


class TestPackReadmesTeachTheExtrasIdiom:
    """The sixteen pack READMEs are PyPI landing pages, and PyPI freezes them per release.

    They shipped the pre-#69 idiom for the whole 5.0.0 cycle — `pip install
    tkinter-icons-lucide` and `from tkinter_icons_lucide import LucideIcon` — because
    sixteen hand-written copies of one page go stale together and nothing read them.
    `TestReadmesDoNotAdvertiseExtrasThatDoNotExist` did not catch it: every name in
    them was real, just not the supported way in.

    Cost of catching it late is what makes this worth a test rather than an edit. A
    README on PyPI cannot be corrected without releasing a new version of that
    distribution, so sixteen wrong pages are sixteen extra pack releases, not sixteen
    commits.

    `.github/scripts/generate_pack_readmes.py --check` is the stronger guard and it
    covers the generated facts too. This one is deliberately independent of it: it
    needs no `docs/_ext` on the path and no live provider, so it still runs on every
    platform in the test matrix.
    """

    @staticmethod
    def _readme(pack):
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[1]
        path = root / "packages" / pack.distribution / "README.md"
        if not path.is_file():
            pytest.skip("not running from a source checkout")
        return path.read_text(encoding="utf-8-sig")

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_the_install_line_is_the_extras_form(self, pack):
        assert pack.install_command in self._readme(pack), (
            f"{pack.distribution}/README.md does not carry {pack.install_command!r}"
        )

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_no_bare_install_of_the_raw_distribution(self, pack):
        import re

        text = self._readme(pack)
        # The prose may name the distribution - it is the page's own title. What must
        # not appear is a *command* telling the reader to install it that way.
        bare = re.findall(rf"pip install {re.escape(pack.distribution)}\b", text)
        assert not bare, f"{pack.distribution}/README.md teaches a bare install: {bare}"

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_imports_come_from_the_single_root(self, pack):
        import re

        text = self._readme(pack)
        wrong = re.findall(rf"from {re.escape(pack.module)} import (\w+)", text)
        assert not wrong, (
            f"{pack.distribution}/README.md imports from the pack module: {wrong}. "
            f"Every class is re-exported from tkinter_icons."
        )
        assert f"from tkinter_icons import {pack.export_names[0]}" in text, (
            f"{pack.distribution}/README.md never shows the supported import"
        )


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
