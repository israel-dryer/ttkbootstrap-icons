"""The advertised Python versions and the tested Python versions must agree.

The README badge is ``img.shields.io/pypi/pyversions/tkinter-icons.svg``, which
shields renders from the trove classifiers on the *published* base distribution
- not from anything editable after the fact. So a classifier is a support claim
that reaches users and cannot be corrected without a new release, which makes
"claimed but never tested" the expensive direction of drift. This pins the two
together.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:  # 3.10 has no tomllib; tomli is the same API under the old name.
    tomllib = pytest.importorskip("tomli", reason="3.10 needs tomli to read pyproject.toml")

REPO = Path(__file__).resolve().parents[1]
BASE_PYPROJECT = REPO / "packages" / "tkinter-icons" / "pyproject.toml"
CI_WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"

_VERSION = re.compile(r'"(3\.\d+)"')


def _classifier_versions() -> set[str]:
    """The `3.x` versions the base package advertises to PyPI."""
    project = tomllib.loads(BASE_PYPROJECT.read_text(encoding="utf-8-sig"))["project"]
    prefix = "Programming Language :: Python :: "
    return {
        c[len(prefix):]
        for c in project["classifiers"]
        if c.startswith(prefix) and c != prefix.rstrip() and "." in c[len(prefix):]
    }


def _tested_versions() -> set[str]:
    """The `3.x` versions CI's test matrix actually runs.

    Parsed with a regex rather than a YAML library on purpose: PyYAML is not a
    test dependency, and adding one to read a file this project owns and this
    test pins the shape of would cost more than it explains.
    """
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    matrix = re.search(r"\n      matrix:\n(.*?)\n    steps:", text, re.S)
    assert matrix, "could not find the test job's matrix block in ci.yml"
    return set(_VERSION.findall(matrix.group(1)))


class TestAdvertisedPythonVersionsAreTested:
    def test_every_classifier_is_covered_by_ci(self) -> None:
        untested = _classifier_versions() - _tested_versions()
        assert not untested, (
            f"the base package advertises Python {sorted(untested)} but CI never runs it. "
            "A classifier is frozen into the published wheel and drives the README's "
            "pyversions badge, so remove it or add it to ci.yml's matrix."
        )

    def test_every_tested_version_is_advertised(self) -> None:
        unclaimed = _tested_versions() - _classifier_versions()
        assert not unclaimed, (
            f"CI tests Python {sorted(unclaimed)} but the base package does not advertise it. "
            "Add the classifier - it only reaches users on the next release, so the gap "
            "is easy to leave open for a whole version."
        )

    def test_requires_python_floor_matches_the_lowest_tested(self) -> None:
        project = tomllib.loads(BASE_PYPROJECT.read_text(encoding="utf-8-sig"))["project"]
        floor = project["requires-python"]
        lowest = min(_tested_versions(), key=lambda v: tuple(int(p) for p in v.split(".")))
        assert floor == f">={lowest}", (
            f"requires-python is {floor!r} but the lowest version CI tests is {lowest}"
        )
