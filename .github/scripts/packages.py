"""The repository's distribution catalogue, derived from the tree itself.

Eighteen distributions live under ``packages/``: the base package, sixteen icon
packs, and the ``ttkbootstrap-icons`` compatibility shim. Nothing here is
hardcoded — the mapping is read from each ``pyproject.toml``, because a
hand-maintained table is exactly the thing that goes stale when a package is
added or renamed.

**Directory name and distribution name are not the same thing.** The shim lives
in ``packages/ttkbootstrap-icons-shim/`` but builds the distribution
``ttkbootstrap-icons`` — the plain directory name was taken by the package being
renamed away from it. Anything resolving a tag to a directory has to go through
the distribution name, which is what :func:`find` does.

Tag scheme::

    v<version>                  the base package, e.g. v5.0.0
    <distribution>-v<version>   everything else, e.g. tkinter-icons-fa-v1.1.0
                                                    ttkbootstrap-icons-v5.0.0

The base package keeps the bare ``v`` form it has used since 1.0.0, and its
setuptools-scm config matches only that form, so a pack tag can never become the
base package's version.

Needs Python 3.11 or newer for ``tomllib``. That is no constraint on the library,
which supports 3.10 — this and its sibling scripts only ever run in CI, on 3.12.
"""
from __future__ import annotations

import importlib
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages"

BASE_DIST = "tkinter-icons"

TAG_RE = re.compile(r"^(?:(?P<dist>.+)-)?v(?P<version>\d+\.\d+\.\d+.*)$")


@dataclass(frozen=True)
class Package:
    """One buildable distribution in the monorepo."""

    dist: str
    """The distribution name, as PyPI knows it."""

    directory: Path
    """Where it lives. Not necessarily named after the distribution."""

    pyproject: dict
    """Its parsed ``pyproject.toml``."""

    @property
    def is_base(self) -> bool:
        return self.dist == BASE_DIST

    @property
    def changelog(self) -> Path:
        """The base package's changelog is the repository's root one."""
        return REPO_ROOT / "CHANGELOG.md" if self.is_base else self.directory / "CHANGELOG.md"

    @property
    def declared_version(self) -> str | None:
        """The static version in ``pyproject.toml``.

        ``None`` for the base package, whose version is dynamic and comes from
        the git tag through setuptools-scm.
        """
        return self.pyproject.get("project", {}).get("version")

    @property
    def entry_point_targets(self) -> dict[str, str]:
        """This package's provider entry points, as ``{key: "module:attr"}``."""
        groups = self.pyproject.get("project", {}).get("entry-points", {})
        targets: dict[str, str] = {}
        for group in ("tkinter_icons.providers", "ttkbootstrap_icons.providers"):
            for key, target in groups.get(group, {}).items():
                targets.setdefault(key, target)
        return targets

    @property
    def provider_names(self) -> list[str]:
        """The names this pack's providers are registered under.

        These are what ``generate_metrics`` takes as arguments, and they are not
        guaranteed to be the entry-point keys: ``registry.py`` registers each
        provider under ``provider_instance.name``, and the pack whose entry
        point reads ``fa`` registers ``fontawesome``. Reading the key would send
        ``generate_metrics`` an argument it rejects. ``fa`` is the only pack the
        two disagree on today, which is exactly why reading the key looks safe
        and is not.

        Getting the real name means instantiating the provider, so this needs
        the pack installed. Where it is not, the entry-point key is returned as
        a best guess — callers that must be right about it should import first.
        """
        names: list[str] = []
        for key, target in self.entry_point_targets.items():
            module_name, _, attribute = target.partition(":")
            try:
                module = importlib.import_module(module_name)
                names.append(getattr(module, attribute)().name)
            except Exception:
                names.append(key)
        return names

    def tag_for(self, version: str) -> str:
        return f"v{version}" if self.is_base else f"{self.dist}-v{version}"


def load_all() -> list[Package]:
    """Every distribution under ``packages/``, sorted by distribution name."""
    packages = []
    for pyproject_path in sorted(PACKAGES_DIR.glob("*/pyproject.toml")):
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        name = data.get("project", {}).get("name")
        if not name:
            raise ValueError(f"{pyproject_path} declares no project.name")
        packages.append(Package(dist=name, directory=pyproject_path.parent, pyproject=data))
    return sorted(packages, key=lambda p: p.dist)


def find(dist: str) -> Package:
    """Look a distribution up by name."""
    for package in load_all():
        if package.dist == dist:
            return package
    known = ", ".join(p.dist for p in load_all())
    raise KeyError(f"no distribution named {dist!r} under packages/. Known: {known}")


def parse_tag(tag: str) -> tuple[Package, str]:
    """Resolve a release tag to the package it releases and its version.

    Raises ``ValueError`` on a tag that does not fit the scheme, and on the one
    ambiguous form: ``tkinter-icons-v<version>``. That tag *looks* like a
    correct base-package tag, but the base package's setuptools-scm config
    matches only ``v[0-9]*``, so building from it would silently produce a
    version derived from some older tag instead. Rejecting it loudly beats
    publishing a mislabelled wheel.
    """
    match = TAG_RE.match(tag)
    if not match:
        raise ValueError(
            f"tag {tag!r} does not fit the scheme: 'v<version>' for the base "
            f"package, '<distribution>-v<version>' for everything else"
        )

    dist, version = match.group("dist"), match.group("version")

    if dist is None:
        return find(BASE_DIST), version

    if dist == BASE_DIST:
        raise ValueError(
            f"tag {tag!r} is ambiguous — the base package is tagged 'v{version}', "
            f"not '{BASE_DIST}-v{version}'. Its setuptools-scm config matches only "
            f"the bare 'v' form, so this tag would build the wrong version."
        )

    return find(dist), version


def main() -> None:
    """``python packages.py <tag>`` prints the resolution, for the workflow.

    Emits ``key=value`` lines to stdout, and to ``$GITHUB_OUTPUT`` when the
    workflow passes it as a second argument.
    """
    tag = sys.argv[1]
    try:
        package, version = parse_tag(tag)
    except (ValueError, KeyError) as exc:
        # A bad tag is operator error, not a bug — say what is wrong and stop,
        # rather than burying it under a traceback in the workflow log.
        print(f"cannot release from tag {tag!r}: {exc}", file=sys.stderr)
        raise SystemExit(2)

    outputs = {
        "dist": package.dist,
        "directory": package.directory.relative_to(REPO_ROOT).as_posix(),
        "version": version,
        "changelog": package.changelog.relative_to(REPO_ROOT).as_posix(),
        "is_base": "true" if package.is_base else "false",
        "providers": " ".join(package.provider_names),
    }

    for key, value in outputs.items():
        print(f"{key}={value}")

    if len(sys.argv) > 2:
        with open(sys.argv[2], "a", encoding="utf-8") as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
