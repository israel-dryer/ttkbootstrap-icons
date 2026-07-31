"""Pre-release preflight for every distribution in the repository.

This exists because of a specific, repeated failure: a package built and
uploaded cleanly, and was broken on install. The package-data glob matched
`glyphmap.json` while the provider shipped one file per style (#61); assets and
license files were missing from two packages entirely (25dac89); a license
reference in `pyproject.toml` pointed at a file that was not there (34a9c65).
None of those are visible in a working tree, where the files are simply on disk
next to the code — they only show up in the wheel, or on someone else's machine.

So every check here answers the same question: *would this still work if the
only thing that existed were the built distribution?*

Two severities:

* **error** — fails now, always. A broken package-data glob ships a package that
  cannot find its own font.
* **warning** — fails only under ``--strict``, which the release workflow uses.
  These are things that are fine mid-development and unacceptable to publish:
  missing glyph metrics, missing upstream license files.

Usage::

    python verify_packages.py                    # everything, warnings tolerated
    python verify_packages.py --strict           # warnings are failures
    python verify_packages.py --imports          # also import each entry point
    python verify_packages.py tkinter-icons-fa   # one distribution
"""
from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path

from packages import BASE_DIST, Package, load_all

PROVIDER_ENTRY_POINT_GROUPS = (
    "tkinter_icons.providers",
    "ttkbootstrap_icons.providers",  # legacy group, still scanned by registry.py
)

# Three packs redistribute an upstream icon font without carrying its license
# file. `bs` redistributes Bootstrap Icons; `meteocons` and `typicons` likewise.
# The other thirteen packs ship theirs under `LICENSES/`. This is a real
# compliance gap, not a checker bug — resolving it needs the actual upstream
# license text and copyright line, which is a human decision rather than
# something to guess at. Listing them here keeps `--strict` from being green by
# accident: the release workflow runs with `--strict` and will refuse to publish
# until this set is empty.
KNOWN_LICENSE_GAPS = {
    "tkinter-icons-bs",
    "tkinter-icons-meteocons",
    "tkinter-icons-typicons",
}

VERSION_RE = re.compile(r"^## \[(\d+\.\d+\.\d+[^\]]*)\]")
REQUIREMENT_RE = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*(?:\[[^\]]*\])?\s*(?:>=\s*([0-9][^,;\s]*))?")


class Report:
    """Collects findings so every package is checked before anything fails."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, dist: str, message: str) -> None:
        self.errors.append(f"{dist}: {message}")

    def warn(self, dist: str, message: str) -> None:
        self.warnings.append(f"{dist}: {message}")


def parse_version(text: str) -> tuple[int, ...]:
    """Numeric release segment only; enough to compare floors."""
    return tuple(int(part) for part in re.findall(r"\d+", text)[:3])


def changelog_versions(package: Package) -> list[str]:
    """Every ``## [version]`` heading in the package's changelog, in file order."""
    if not package.changelog.exists():
        return []
    text = package.changelog.read_text(encoding="utf-8")
    return [m.group(1) for m in (VERSION_RE.match(line) for line in text.splitlines()) if m]


def check_changelog(package: Package, report: Report) -> None:
    """A changelog exists, and its newest entry is the version being shipped."""
    if not package.changelog.exists():
        report.error(package.dist, f"no changelog at {package.changelog.name}")
        return

    versions = changelog_versions(package)
    if not versions:
        report.error(package.dist, "changelog has no '## [version]' sections")
        return

    declared = package.declared_version
    if declared is None:
        # The base package's version is dynamic (setuptools-scm reads the tag),
        # so there is no pyproject value to agree with. The release workflow
        # checks the tag against the changelog instead.
        return

    if versions[0] != declared:
        report.error(
            package.dist,
            f"pyproject version is {declared} but the newest changelog entry is "
            f"{versions[0]} — one of them is wrong",
        )


def check_package_data(package: Package, report: Report) -> None:
    """Every package-data glob matches at least one file that actually exists.

    A glob matching nothing is silent: the build succeeds, the wheel is short a
    font, and the failure surfaces on someone else's machine.
    """
    src = package.directory / "src"
    patterns = package.pyproject.get("tool", {}).get("setuptools", {}).get("package-data", {})

    if not patterns:
        return

    for module, globs in patterns.items():
        module_dir = src / Path(*module.split("."))
        if not module_dir.is_dir():
            report.error(package.dist, f"package-data names '{module}', which is not under src/")
            continue
        for pattern in globs:
            if any(module_dir.glob(pattern)):
                continue
            message = f"package-data glob '{pattern}' under {module} matches no files"
            if "LICENSE" in pattern.upper() and package.dist in KNOWN_LICENSE_GAPS:
                report.warn(package.dist, f"{message} (known upstream license gap)")
            elif pattern.startswith("metrics"):
                pass  # check_metrics reports this once, as a warning
            else:
                report.error(package.dist, message)


def check_licenses(package: Package, report: Report) -> None:
    """The wrapper's own license resolves, and upstream's is carried alongside it.

    ``license = "MIT"`` is an SPDX expression under PEP 639; it declares a
    license without shipping one. Every distribution here needs the MIT text on
    disk beside its ``pyproject.toml`` for ``license-files`` to pick up, or the
    wheel asserts a license it does not carry.
    """
    entries = package.pyproject.get("project", {}).get("license-files")
    if not entries:
        report.error(package.dist, "declares no [project] license-files")
    for entry in entries or []:
        if not any(package.directory.glob(entry)):
            report.error(package.dist, f"license-files entry '{entry}' matches no files")

    if package.dist == BASE_DIST or not package.directory.name.startswith("tkinter-icons-"):
        return  # only the packs redistribute someone else's font

    src = package.directory / "src"
    if not any(src.glob("*/LICENSES/*")) and not any(src.glob("*/assets/LICENSES/*")):
        message = "ships an upstream font with no upstream license file under LICENSES/"
        if package.dist in KNOWN_LICENSE_GAPS:
            report.warn(package.dist, message)
        else:
            report.error(package.dist, message)


def check_metrics(package: Package, report: Report) -> None:
    """Each pack ships the measured ink bounds the 5.0 renderer centers on.

    A pack without them still renders — the renderer falls back to
    ``font.getbbox()`` — but that fallback is the very miscentering 5.0.0 was
    built to fix, so shipping without metrics quietly undoes the release.
    Generate with ``tkicons-metrics --all``; verify with ``tkicons-metrics
    --all --check``, which needs the packs installed and so runs in CI rather
    than here.
    """
    if package.dist == BASE_DIST or not package.directory.name.startswith("tkinter-icons-"):
        return

    if not any((package.directory / "src").glob("*/**/metrics*.json")):
        report.warn(package.dist, "no metrics*.json - run 'tkicons-metrics --all' before release")


def check_dependencies(package: Package, by_dist: dict[str, Package], report: Report) -> None:
    """Every pinned floor names a package in this repo, at a version that exists.

    The base package's extras pin ``>=1.1.0`` against distributions that are
    released separately, which is what makes publish order load-bearing. A floor
    above what the pack actually declares would resolve to nothing on PyPI.
    """
    project = package.pyproject.get("project", {})
    requirements = list(project.get("dependencies", []))
    for extra_requirements in project.get("optional-dependencies", {}).values():
        requirements.extend(extra_requirements)

    for requirement in requirements:
        match = REQUIREMENT_RE.match(requirement)
        if not match:
            continue
        name, floor = match.group(1), match.group(2)
        if name == package.dist or name not in by_dist or floor is None:
            continue  # third-party, self-referential extra, or unpinned

        target = by_dist[name]
        available = target.declared_version or (changelog_versions(target) or [None])[0]
        if available is None:
            continue
        if parse_version(floor) > parse_version(available):
            report.error(
                package.dist,
                f"requires {name}>={floor} but {name} is at {available} — "
                f"that floor cannot resolve",
            )


def check_extras_cover_every_pack(base: Package, by_dist: dict[str, Package], report: Report) -> None:
    """Sixteen packs, sixteen extras, and ``[all]`` reaching all of them.

    The packs are separate distributions only because each ships a font; a user
    should only ever meet them as extras. A pack with no extra is a pack nobody
    can install the documented way.
    """
    extras = base.pyproject.get("project", {}).get("optional-dependencies", {})

    covered = set()
    for name, requirements in extras.items():
        if name == "all":
            continue
        for requirement in requirements:
            match = REQUIREMENT_RE.match(requirement)
            if match and match.group(1) in by_dist:
                covered.add(match.group(1))

    packs = {
        dist for dist, package in by_dist.items()
        if package.directory.name.startswith("tkinter-icons-")
    }
    for missing in sorted(packs - covered):
        report.error(base.dist, f"{missing} has no extra — it can only be installed by name")

    # `all` is written as nested self-references, e.g. "tkinter-icons[bootstrap,...]".
    reachable = set()
    for requirement in extras.get("all", []):
        inner = re.search(r"\[([^\]]*)\]", requirement)
        if inner:
            reachable.update(part.strip() for part in inner.group(1).split(","))
    for missing in sorted(set(extras) - {"all"} - reachable):
        report.error(base.dist, f"extra '{missing}' is not included in [all]")


def check_entry_points(package: Package, report: Report) -> None:
    """Each declared provider actually imports. Requires the package installed."""
    entry_points = package.pyproject.get("project", {}).get("entry-points", {})
    for group in PROVIDER_ENTRY_POINT_GROUPS:
        for name, target in entry_points.get(group, {}).items():
            module_name, _, attribute = target.partition(":")
            try:
                module = importlib.import_module(module_name)
            except ImportError as exc:
                report.error(package.dist, f"entry point '{name}' cannot import {module_name}: {exc}")
                continue
            if attribute and not hasattr(module, attribute):
                report.error(package.dist, f"entry point '{name}': {module_name} has no {attribute!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("distributions", nargs="*", help="limit to these distribution names")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--imports", action="store_true", help="also import every entry point")
    args = parser.parse_args()

    all_packages = load_all()
    by_dist = {package.dist: package for package in all_packages}

    if args.distributions:
        unknown = set(args.distributions) - set(by_dist)
        if unknown:
            print(f"unknown distribution(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        selected = [by_dist[dist] for dist in args.distributions]
    else:
        selected = all_packages

    report = Report()
    for package in selected:
        check_changelog(package, report)
        check_package_data(package, report)
        check_licenses(package, report)
        check_metrics(package, report)
        check_dependencies(package, by_dist, report)
        if package.is_base:
            check_extras_cover_every_pack(package, by_dist, report)
        if args.imports:
            check_entry_points(package, report)

    print(f"checked {len(selected)} distribution(s)")
    for warning in report.warnings:
        print(f"  warning  {warning}")
    for error in report.errors:
        print(f"  ERROR    {error}")

    if report.errors:
        print(f"\n{len(report.errors)} error(s).")
        return 1
    if report.warnings and args.strict:
        print(f"\n{len(report.warnings)} warning(s), and --strict was given.")
        return 1
    if report.warnings:
        print(f"\n{len(report.warnings)} warning(s); these fail under --strict.")
    else:
        print("\nall clear.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
