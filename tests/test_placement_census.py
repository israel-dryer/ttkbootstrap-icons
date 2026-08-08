"""Every placement number in prose, checked against the census that produced it.

Four files quote how the renderer places glyphs: the `sizing-and-quality` page,
`_place_by_bbox`'s docstring in the shipped wheel, `render_figures.FIGURES`'
note, and `CLAUDE.md`. They have to agree with each other and with the
renderer, and for three rounds of review they did neither.

The reason was never carelessness. The measurement was a snippet someone ran
once and threw away, so correcting a number meant re-deriving it from scratch
and retyping it into four places — and a round that fixed `padded_box_inset` to
use the renderer's `int()` arithmetic left the prose still quoting figures
derived from the float, which is how the docs came to claim the measured path
fills "up to 102%" of a box it is arithmetically incapable of overflowing.

So the measurement is committed now — `.github/scripts/generate_placement_census.py`
writes `docs/_data/placement-census.json` — and this reads the prose back out
and compares. Transcription is still by hand, because a shipped docstring and a
handoff file cannot read JSON. What changed is that a bad transcription now
fails here instead of surviving to the next review.

**A failure here is not necessarily a wrong number.** If the renderer's
placement genuinely changed, the census is what is stale: regenerate it, then
bring all four files to the new figures. Running the generator is the only
correct way to change any number this file checks.
"""

from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass
from typing import Callable

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
CENSUS = REPO / "docs" / "_data" / "placement-census.json"
GENERATOR = ".github/scripts/generate_placement_census.py"

#: Where each claim has to appear, by the shorthand the table below uses.
FILES = {
    "page": "docs/user-guide/sizing-and-quality.rst",
    "docstring": "packages/tkinter-icons/src/tkinter_icons/render.py",
    "figures": "docs/_ext/render_figures.py",
    "handoff": "CLAUDE.md",
}

#: A percentage range, spelled either "72% to 95%" or "72%–95%". Prose style
#: differs between a user-guide page and a handoff file, and forcing one
#: spelling on both would be this check dictating tone rather than facts.
RANGE = r"(\d+(?:\.\d+)?)%\s*(?:to|–|-|—)\s*(\d+(?:\.\d+)?)%"

#: A count, with or without thousands separators.
COUNT = r"(\d[\d,]*)"


def number(text: str) -> float:
    return float(text.replace(",", ""))


@dataclass(frozen=True)
class Claim:
    """One fact, the sentence each file states it in, and where it comes from.

    Patterns are per file and anchored to their own wording rather than shared.
    A loose pattern reused across files is worse than no check: the first
    version matched `at (\\d+) (?:pixels|px)` everywhere and picked up "at 16
    pixels" from an unrelated paragraph about oversampling, so it compared the
    wrong number and would have gone on comparing it.
    """

    label: str
    patterns: dict[str, str]
    expected: Callable[[dict], tuple[float, ...]]
    #: Prose rounds. Half a unit is exactly the slack that allows, so a figure
    #: rounded the wrong way still fails.
    tolerance: float = 0.5


CLAIMS = (
    Claim(
        "the getbbox path's per-pack median fill",
        {
            "page": r"per-pack median of " + RANGE + r" of the padded box",
            "docstring": r"per-pack median of " + RANGE + r" of it",
            "handoff": r"per-pack median of " + RANGE + r" of it",
        },
        lambda c: (c["pack_median_fill_pct"]["bbox"]["min"],
                   c["pack_median_fill_pct"]["bbox"]["max"]),
    ),
    Claim(
        "the ink path's per-pack median fill",
        {
            "page": r"Measured ink fills " + RANGE,
            "docstring": r"against " + RANGE + r" on the ink path",
            "handoff": r"against " + RANGE + r" on the ink path",
        },
        lambda c: (c["pack_median_fill_pct"]["ink"]["min"],
                   c["pack_median_fill_pct"]["ink"]["max"]),
    ),
    Claim(
        "how many glyphs run past the frame, and how many draw at all",
        {
            key: COUNT + r" of the " + COUNT + r" glyphs that draw"
            for key in ("page", "docstring", "handoff")
        },
        lambda c: (c["frame_overflow"]["bbox"], c["totals"]["drawing"]),
        tolerance=0,
    ),
    Claim(
        "the glyph-map total and the count that draws nothing",
        {"docstring": r"hold " + COUNT + r" entries; the " + COUNT + r" that render nothing"},
        lambda c: (c["totals"]["glyphmap_entries"], c["totals"]["blank"]),
        tolerance=0,
    ),
    Claim(
        "the worst pack's median off-center distance on the getbbox path",
        {
            "page": r"sits a median (\d+(?:\.\d+)?) pixels off-center in the worst pack",
            "figures": r"Weather sits a median (\d+(?:\.\d+)?) px off-center",
        },
        lambda c: (c["pack_median_offcenter_px"]["bbox"]["max"],),
    ),
    Claim(
        "the ink path's own centering, median and worst case",
        {"page": r"median (\d+(?:\.\d+)?) pixels off-center with a worst case of (\d+(?:\.\d+)?)"},
        lambda c: (c["ink_path_centering_px"]["median"],
                   c["ink_path_centering_px"]["max"]),
        tolerance=0.05,
    ),
    Claim(
        "the fill of the glyph the measured-ink figure draws",
        {"figures": r"Eva fills (\d+)% of the padded box on the fallback path against (\d+)%"},
        lambda c: (c["subjects"]["eva/home"]["fill_pct"]["bbox"],
                   c["subjects"]["eva/home"]["fill_pct"]["ink"]),
    ),
    Claim(
        "the size everything was measured at",
        {
            "page": r"with its own pack's options at (\d+) pixels",
            "figures": r"off-center at (\d+) px",
        },
        lambda c: (c["size_px"],),
        tolerance=0,
    ),
)


@pytest.fixture(scope="module")
def census() -> dict:
    if not CENSUS.is_file():
        pytest.skip("not running from a source checkout")
    return json.loads(CENSUS.read_text(encoding="utf-8"))


def read(key: str) -> str:
    path = REPO / FILES[key]
    if not path.is_file():
        pytest.skip(f"{FILES[key]} is not present")
    return path.read_text(encoding="utf-8-sig")


@pytest.mark.parametrize(
    ("claim", "key"),
    [(claim, key) for claim in CLAIMS for key in claim.patterns],
    ids=lambda value: value.label if isinstance(value, Claim) else value,
)
class TestEveryQuotedFigureMatchesTheCensus:
    def test_the_file_still_states_it(self, claim, key):
        """A claim that vanishes is as bad as one that drifts.

        Losing the phrasing silently retires the check, and these numbers are
        the argument the pages make — a page that stops stating them has either
        been reworded past this regex or has dropped the claim. Both want a
        person, and neither should pass.
        """
        assert re.search(claim.patterns[key], read(key)), (
            f"{FILES[key]} no longer states {claim.label}. If it was reworded, "
            f"update the pattern in {pathlib.Path(__file__).name}; if the claim "
            f"was dropped, drop it from CLAIMS too."
        )

    def test_it_agrees_with_the_measurement(self, claim, key, census):
        found = re.search(claim.patterns[key], read(key))
        if found is None:
            pytest.skip("covered by test_the_file_still_states_it")
        quoted = [number(group) for group in found.groups()]
        measured = claim.expected(census)
        assert len(quoted) == len(measured), (
            f"the pattern for {claim.label} captured {len(quoted)} numbers but "
            f"the census supplies {len(measured)}"
        )
        for value, truth in zip(quoted, measured):
            assert abs(value - truth) <= claim.tolerance, (
                f"{FILES[key]} says {quoted} for {claim.label}, but the census "
                f"measured {list(measured)}. Regenerate with "
                f"`python {GENERATOR}` if the renderer changed; otherwise the "
                f"prose is what is wrong."
            )


class TestTheInkPathCannotOverfill:
    """The one invariant that would have caught the "102%" claim on its own.

    `_place_by_ink` fits ink to the padded box and never enlarges past it, so a
    measured-path median above 100% is not a surprising measurement — it is
    proof that whatever produced it was not measuring the renderer's padded
    box. The docs quoted 102% for a full release cycle, and it was a float
    denominator where the renderer truncates. This is here rather than in the
    generator because it is a claim about the renderer, not about the file.
    """

    def test_no_pack_fills_more_than_the_box_it_was_fitted_to(self, census):
        assert census["pack_median_fill_pct"]["ink"]["max"] <= 100.0
        assert census["frame_overflow"]["ink"] == 0
