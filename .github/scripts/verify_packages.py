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

    # what the release workflow runs, for one tag
    python verify_packages.py --strict --imports --tag tkinter-icons-fa-v1.1.0
"""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import re
import sys
from pathlib import Path

from packages import BASE_DIST, Package, load_all, parse_tag

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

# A requirement splits into a name, optional extras, and everything up to the
# environment marker. The specifier set is then read separately, because a floor
# can be written several ways and only reading `>=` lets the others through
# unchecked — an `==5.1.0` that resolves to nothing would pass preflight and
# fail after the tag is pushed.
REQUIREMENT_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9._-]+)\s*(?:\[[^\]]*\])?\s*(?P<specifiers>[^;]*)"
)
SPECIFIER_RE = re.compile(r"(?P<operator>[=!<>~]=|===|[<>])\s*(?P<version>[0-9][^,;\s]*)")
FLOOR_OPERATORS = ("==", "===", ">=", "~=", ">")

RELEASE_RE = re.compile(r"^v?(?P<release>\d+(?:\.\d+)*)(?P<suffix>.*)$")


class Report:
    """Collects findings so every package is checked before anything fails."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.skipped: list[str] = []

    def error(self, dist: str, message: str) -> None:
        self.errors.append(f"{dist}: {message}")

    def warn(self, dist: str, message: str) -> None:
        self.warnings.append(f"{dist}: {message}")


def parse_version(text: str) -> tuple[tuple[int, ...], int]:
    """Sortable ``(release, is_final)``; enough to compare floors.

    Not a PEP 440 parser. It knows one thing beyond the release numbers, which
    is that a pre-release sorts *below* the release it precedes — without that,
    ``1.1.0rc1`` compares equal to ``1.1.0`` and a floor of ``>=1.1.0`` looks
    satisfied by a package that has only reached the release candidate.
    """
    match = RELEASE_RE.match(text.strip())
    if not match:
        return ((0,), 0)
    release = tuple(int(part) for part in match.group("release").split("."))
    suffix = match.group("suffix").lstrip(".-_").lower()
    is_prerelease = suffix.startswith(("a", "b", "c", "rc", "dev"))
    return ((release + (0, 0, 0))[:3], 0 if is_prerelease else 1)


def requirement_floor(specifiers: str) -> tuple[str, str] | None:
    """The lowest version a specifier set can resolve to, as ``(operator, version)``.

    ``None`` when nothing in the set constrains the bottom end. ``>`` is kept
    distinct from ``>=`` because ``>5.0.0`` against an available 5.0.0 resolves
    to nothing at all, while ``>=5.0.0`` is satisfied exactly.
    """
    floor = None
    for match in SPECIFIER_RE.finditer(specifiers):
        operator, version = match.group("operator"), match.group("version")
        if operator not in FLOOR_OPERATORS:
            continue
        version = version.rstrip("*").rstrip(".")  # `==1.1.*` floors at 1.1
        if floor is None or parse_version(version) > parse_version(floor[1]):
            floor = (operator, version)
    return floor


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
            f"{versions[0]} - one of them is wrong",
        )


def metrics_files(package: Package) -> list[Path]:
    """Every ``metrics*.json`` the pack has on disk, wherever it keeps it.

    Packs differ: `bs` keeps its assets in an ``assets/`` subpackage, the rest at
    the module root.
    """
    return sorted((package.directory / "src").glob("*/**/metrics*.json"))


def shipped_files(package: Package) -> set[Path]:
    """Every file the package-data globs actually reach.

    This is the wheel's contents as far as data files go, and it is the only
    thing that matters: a file on disk that no glob names does not get built in.
    """
    src = package.directory / "src"
    patterns = package.pyproject.get("tool", {}).get("setuptools", {}).get("package-data", {})
    shipped: set[Path] = set()
    for module, globs in patterns.items():
        module_dir = src / Path(*module.split("."))
        for pattern in globs:
            shipped.update(module_dir.glob(pattern))
    return shipped


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
            elif pattern.startswith("metrics") and not metrics_files(package):
                # Nothing generated yet, anywhere. check_metrics reports that
                # once, as a warning. The `and` is load-bearing: a pack whose
                # metrics sit somewhere this glob does not reach has a file on
                # disk and none in the wheel, which is #61 exactly.
                pass
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
    Generate with ``python -m tkinter_icons.tools.generate_metrics --all``; add
    ``--check`` to verify instead of write, which needs the packs installed and
    so runs in CI rather than here.
    """
    if package.dist == BASE_DIST or not package.directory.name.startswith("tkinter-icons-"):
        return

    found = metrics_files(package)
    if not found:
        report.warn(
            package.dist,
            "no metrics*.json - run 'python -m tkinter_icons.tools.generate_metrics --all' before release",
        )
        return

    # On disk is not the same as in the wheel, and this is the failure that
    # motivated the whole script: the file is right there next to the code, so
    # nothing in a working tree looks wrong, and the pack installs elsewhere
    # falling back to `getbbox` with nothing anywhere saying so.
    shipped = shipped_files(package)
    src = package.directory / "src"
    for path in found:
        if path not in shipped:
            report.error(
                package.dist,
                f"{path.relative_to(src).as_posix()} exists but no package-data glob "
                f"reaches it - the wheel would ship without metrics",
            )


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
        name = match.group("name")
        if name == package.dist or name not in by_dist:
            continue  # third-party, or the base package's self-referential `all`

        target = by_dist[name]
        available = target.declared_version or (changelog_versions(target) or [None])[0]
        if available is None:
            continue

        floor = requirement_floor(match.group("specifiers"))
        if floor is None:
            report.warn(
                package.dist,
                f"requires {name} with no lower bound - publish order stops being "
                f"enforced, and an old {name} would satisfy this",
            )
            continue

        operator, version = floor
        # `>` needs the available version to be strictly above it; every other
        # floor is satisfied by an exact match.
        cannot_resolve = (
            parse_version(version) >= parse_version(available)
            if operator == ">"
            else parse_version(version) > parse_version(available)
        )
        if cannot_resolve:
            report.error(
                package.dist,
                f"requires {name}{operator}{version} but {name} is at {available} - "
                f"that floor cannot resolve",
            )


def check_tools_are_not_shipped(package: Package, report: Report) -> None:
    """Maintainer tooling stays out of the wheel, and stays out reliably.

    ``tools`` regenerates assets and metrics into a source tree, so it does
    nothing from an installed wheel — and once published, ``<package>.tools``
    is an import path we owe compatibility on.

    Excluding it from ``packages.find`` is not enough, and fails *silently*.
    Every package sets ``include-package-data``, which also pulls in whatever
    an existing ``.egg-info/SOURCES.txt`` lists — and the sdist rightly
    contains ``tools``, so it is listed. The release workflow editable-installs
    each pack before building, so the egg-info is there when it counts. Only
    ``exclude-package-data`` actually keeps the files out.

    Checked statically because the failure is invisible: a build in a tree with
    no egg-info produces a clean wheel from a broken config.
    """
    source_root = package.directory / "src"
    tool_dirs = list(source_root.glob("*/tools")) if source_root.is_dir() else []
    if not tool_dirs:
        return

    setuptools_config = package.pyproject.get("tool", {}).get("setuptools", {})
    excluded = setuptools_config.get("exclude-package-data", {})
    covered = {
        module
        for module, patterns in excluded.items()
        if any(pattern.startswith("tools/") or pattern == "tools" for pattern in patterns)
    }

    for tool_dir in tool_dirs:
        module = tool_dir.parent.name
        if module not in covered and "*" not in covered:
            report.error(
                package.dist,
                f"{module}/tools would ship: declare it under "
                f"[tool.setuptools.exclude-package-data] - a packages.find "
                f"exclude alone is silently bypassed by include-package-data",
            )


def check_extras_cover_every_pack(base: Package, by_dist: dict[str, Package], report: Report) -> None:
    """Sixteen packs, sixteen extras, and deliberately no ``[all]``.

    The packs are separate distributions only because each ships a font; a user
    should only ever meet them as extras. A pack with no extra is a pack nobody
    can install the documented way.

    Coverage is checked against the pack directories themselves rather than
    through an aggregate extra, so a pack added without an extra is caught by
    the same rule whether or not anything else references it.
    """
    extras = base.pyproject.get("project", {}).get("optional-dependencies", {})

    covered = set()
    for requirements in extras.values():
        for requirement in requirements:
            match = REQUIREMENT_RE.match(requirement)
            if match and match.group("name") in by_dist:
                covered.add(match.group("name"))

    packs = {
        dist for dist, package in by_dist.items()
        if package.directory.name.startswith("tkinter-icons-")
    }
    for missing in sorted(packs - covered):
        report.error(base.dist, f"{missing} has no extra - it can only be installed by name")

    # `all` was removed before 5.0.0 and must not come back: the sixteen sets
    # serve disjoint purposes, so installing every one costs ~17 MB to get
    # fifteen icon sets nobody opens - the bundling extras exist to avoid.
    if "all" in extras:
        report.error(
            base.dist,
            "the 'all' extra is back - packs are meant to be installed one or two "
            "at a time, and [all] reintroduces the bundling extras replaced",
        )


def check_release_tag(package: Package, version: str, report: Report) -> None:
    """The tag being released agrees with the package and with its changelog.

    A tag is the only thing the release workflow is given, so a tag that says
    1.2.0 against a pyproject that says 1.1.0 would publish 1.1.0 twice — the
    second upload rejected by PyPI, after the tag is already pushed.
    """
    declared = package.declared_version
    if declared is not None and declared != version:
        report.error(
            package.dist,
            f"tag names version {version} but pyproject declares {declared}",
        )

    versions = changelog_versions(package)
    if version not in versions:
        report.error(
            package.dist,
            f"no '## [{version}]' section in {package.changelog.name} - "
            f"the release would have empty notes",
        )
    elif versions[0] != version:
        report.error(
            package.dist,
            f"changelog's newest entry is {versions[0]}, not the {version} being "
            f"released - entries are newest-first",
        )


def check_entry_points(package: Package, report: Report) -> None:
    """Each declared provider actually imports.

    A pack that is not installed is skipped rather than failed. Nobody keeps all
    sixteen installed while working on one, and reporting the other fifteen as
    broken would train everyone to ignore the output. CI installs every pack, so
    coverage there is complete.
    """
    try:
        importlib.metadata.distribution(package.dist)
    except importlib.metadata.PackageNotFoundError:
        report.skipped.append(f"{package.dist}: not installed, entry points unchecked")
        return

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
    parser.add_argument(
        "--tag",
        help="release tag; checks only the package it names, and that the version "
             "it names agrees with that package's pyproject and changelog",
    )
    args = parser.parse_args()

    all_packages = load_all()
    by_dist = {package.dist: package for package in all_packages}

    tagged_version = None
    if args.tag:
        if args.distributions:
            # A tag names exactly one package. Silently ignoring the positional
            # arguments would report a clean release for something nobody asked
            # about.
            print(
                f"--tag {args.tag} already selects a package; drop the "
                f"distribution argument(s): {', '.join(args.distributions)}",
                file=sys.stderr,
            )
            return 2
        try:
            tagged, tagged_version = parse_tag(args.tag)
        except (ValueError, KeyError) as exc:
            print(f"cannot release from tag {args.tag!r}: {exc}", file=sys.stderr)
            return 2
        selected = [tagged]
    elif args.distributions:
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
        check_tools_are_not_shipped(package, report)
        check_dependencies(package, by_dist, report)
        if tagged_version is not None:
            check_release_tag(package, tagged_version, report)
        if package.is_base:
            check_extras_cover_every_pack(package, by_dist, report)
        if args.imports:
            check_entry_points(package, report)

    print(f"checked {len(selected)} distribution(s)")
    for skipped in report.skipped:
        print(f"  skipped  {skipped}")
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
