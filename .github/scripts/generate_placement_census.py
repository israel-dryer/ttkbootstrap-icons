#!/usr/bin/env python
"""Measure how the renderer places glyphs, across every style of every pack.

`sizing-and-quality`, `_place_by_bbox`'s docstring, `render_figures.FIGURES`
and `CLAUDE.md` all quote numbers about placement — how much of the padded box
a glyph fills, how far off-center it sits, how many run past the frame. Those
numbers were measured three times by ad-hoc snippets that were run once and
thrown away, then transcribed by hand into four files that have to agree. Two
review rounds found them wrong, and the second round found errors that the
first round's *fixes* introduced: a corrected `int()` in `padded_box_inset`
that was never propagated to the prose derived from the old float, and figures
restated from a 400-name sample rather than a census.

So the measurement lives here instead, the result is committed, and a test
checks the prose against it. Transcription is still by hand — the numbers are
in a shipped docstring and in `CLAUDE.md`, neither of which can read a JSON
file — but a wrong transcription now fails a test instead of surviving a
review.

Definitions, which are the whole reason the numbers disagreed
-------------------------------------------------------------
Every one of these was implicit before, and two of them were implicitly
*different* in different files.

**The padded box** is the renderer's own, reproduced rather than approximated:
`render_glyph` computes `pad = int(canvas_size * pad_factor)` in oversampled
space, so the box is `canvas_size - 2 * pad` there and `that / oversample` in
final-image pixels. At 96 px with `pad_factor=0.10` it is **78** px, not the
`96 * (1 - 2 * 0.10) = 76.8` px a float reading gives. This is exactly the
difference that made the docs claim the ink path fills "up to 102%" of a box
it is arithmetically incapable of overflowing. `docs/_ext/render_figures.py`'s
`padded_box_inset` reproduces the same arithmetic for the guide lines it draws.

**Fill** is the longer side of the rendered glyph's alpha bounding box, in
final-image pixels, over that padded box side. Measured on the raster rather
than from the placement arithmetic, because the raster is what a reader sees.

**Overflow** is the alpha bounding box touching the frame boundary. Anything
past the frame is clipped, so touching it is the only evidence available that
a glyph wanted more room than it was given.

**Off-center** is the Euclidean distance from the center of the alpha bounding
box to the center of the frame, in final-image pixels.

**A glyph "draws" if it has ink on the measured path.** The blank ones are
excluded from every ratio: an empty image cannot overflow a frame or fail to
fill a box, and including them would drag every median toward zero.

Usage
-----
    python .github/scripts/generate_placement_census.py            # rewrite
    python .github/scripts/generate_placement_census.py --check    # verify

`--check` re-measures and fails if the committed file no longer describes this
tree. It runs in the docs job, which already installs every pack.

It is a committed artifact rather than a pytest fixture for two reasons, and
speed is only half of one: 178,338 renders take about 20 seconds, which is
nothing for a CI step and seven times the whole test suite. The other half is
that it needs all sixteen packs installed, where the tests are meant to run on
every platform in the matrix. Same call `metrics.json` already made.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "docs" / "_data" / "placement-census.json"

#: The size everything is measured at, and the size the figures are drawn at,
#: so "at this size" in the prose means one thing. Recorded in the output
#: because fill and off-center both depend on it through `int()` truncation.
SIZE = 96

#: Any opaque color measures the same — only the alpha channel is read.
COLOR = "#111827"

#: Individual glyphs the figures single out, so their captions quote a
#: measurement rather than a recollection. `(extra, style, name)`; a style of
#: `None` means the pack's default, which is what the figure draws.
SUBJECTS: tuple[tuple[str, str | None, str], ...] = (
    ("eva", None, "home"),
)

#: Decimal places kept. The prose quotes whole percentages and one decimal of
#: a pixel; keeping one more than that lets the test tell a real drift from a
#: rounding boundary.
PRECISION = 2


def packs():
    from tkinter_icons.packs import KNOWN_PACKS

    return list(KNOWN_PACKS)


def provider_for(pack):
    """Instantiate a pack's provider, or raise `ImportError` if it is absent."""
    import importlib

    module = importlib.import_module(f"{pack.module}.provider")
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class in {pack.module}.provider")


def padded_box_side(options) -> float:
    """The padded box in final-image pixels, by the renderer's own arithmetic.

    Kept here rather than imported from `render_figures` because that module
    lives in `docs/_ext` and returns the *inset* it draws a guide at, rounded
    to a whole displayed pixel. This needs the box's width, unrounded, as a
    denominator. Both reproduce `render_glyph`; neither approximates it.
    """
    from tkinter_icons.render import auto_oversample, snap_size

    snapped = snap_size(SIZE, snap_even=options.snap_even)
    oversample = max(1, int(options.oversample or auto_oversample(snapped)))
    canvas = snapped * oversample
    pad = int(canvas * options.pad_factor)
    return max(1, canvas - 2 * pad) / oversample


def measure(image, box_side: float, frame: int) -> tuple[float, float, bool] | None:
    """Fill fraction, off-center distance, and whether the ink hit the frame."""
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        return None
    left, top, right, bottom = bounds
    fill = max(right - left, bottom - top) / box_side
    center = frame / 2
    offset = (((left + right) / 2 - center) ** 2 + ((top + bottom) / 2 - center) ** 2) ** 0.5
    touches = left <= 0 or top <= 0 or right >= frame or bottom >= frame
    return fill, offset, touches


def census() -> dict:
    """Render every glyph of every style both ways and reduce the results."""
    from tkinter_icons.iconset import get_icon_set
    from tkinter_icons.render import render_glyph, snap_size

    entries = blank = without_metrics = 0
    overflow = {"bbox": 0, "ink": 0}
    ink_offsets: list[float] = []
    by_pack: dict[str, dict] = {}
    subjects: dict[str, dict] = {}
    wanted = {(extra, style, name) for extra, style, name in SUBJECTS}

    for pack in packs():
        try:
            provider = provider_for(pack)
        except ImportError:
            raise SystemExit(
                f"the {pack.extra} pack is not installed, so this would measure "
                f"a subset and report it as a census. Install every pack first: "
                f"pip install --no-deps -e packages/{pack.distribution}"
            )

        options = provider.render_options
        box_side = padded_box_side(options)
        frame = snap_size(SIZE, snap_even=options.snap_even)
        fills = {"bbox": [], "ink": []}
        offsets = {"bbox": [], "ink": []}

        for style in provider.style_list or (None,):
            icon_set = get_icon_set(provider, style)
            is_default = style is None or style == provider.default_style
            for name, glyph in icon_set.glyphs.items():
                entries += 1
                ink = icon_set.ink(name)
                if ink is None:
                    without_metrics += 1

                drawn = {}
                for path, bounds in (("ink", ink), ("bbox", None)):
                    image = render_glyph(
                        glyph, SIZE, COLOR,
                        font_key=icon_set.font_key,
                        font_bytes=icon_set.font_bytes,
                        ink=bounds,
                        options=options,
                    )
                    drawn[path] = measure(image, box_side, frame)

                if drawn["ink"] is None:
                    blank += 1
                    continue

                for path, result in drawn.items():
                    if result is None:
                        continue
                    fill, offset, touches = result
                    fills[path].append(fill)
                    offsets[path].append(offset)
                    overflow[path] += touches

                ink_offsets.append(drawn["ink"][1])

                if (pack.extra, style, name) in wanted or (
                    is_default and (pack.extra, None, name) in wanted
                ):
                    subjects[f"{pack.extra}/{name}"] = {
                        "fill_pct": {
                            path: round(drawn[path][0] * 100, PRECISION)
                            for path in ("bbox", "ink") if drawn[path]
                        },
                    }

        by_pack[pack.extra] = {
            "glyphs": len(fills["ink"]),
            "median_fill_pct": {
                path: round(statistics.median(values) * 100, PRECISION)
                for path, values in fills.items() if values
            },
            "median_offcenter_px": {
                path: round(statistics.median(values), PRECISION)
                for path, values in offsets.items() if values
            },
        }
        print(f"  {pack.extra:<14} {by_pack[pack.extra]['glyphs']:>6} glyphs", file=sys.stderr)

    drawing = entries - blank

    def medians(path: str, key: str) -> list[float]:
        return [pack[key][path] for pack in by_pack.values() if path in pack[key]]

    return {
        "_comment": (
            "Generated by .github/scripts/generate_placement_census.py — do not edit. "
            "Every placement number in the docs, in render.py's docstring and in "
            "CLAUDE.md is checked against this file by tests/test_placement_census.py. "
            "Read that script's docstring for what each figure means; the definitions "
            "are the reason earlier hand-measured versions disagreed."
        ),
        "size_px": SIZE,
        "totals": {
            "glyphmap_entries": entries,
            "blank": blank,
            "drawing": drawing,
            "without_metrics": without_metrics,
        },
        "frame_overflow": {"bbox": overflow["bbox"], "ink": overflow["ink"]},
        "pack_median_fill_pct": {
            path: {
                "min": min(medians(path, "median_fill_pct")),
                "max": max(medians(path, "median_fill_pct")),
            }
            for path in ("bbox", "ink")
        },
        "pack_median_offcenter_px": {
            path: {
                "min": min(medians(path, "median_offcenter_px")),
                "max": max(medians(path, "median_offcenter_px")),
                "worst_pack": max(
                    by_pack, key=lambda e: by_pack[e]["median_offcenter_px"][path]
                ),
            }
            for path in ("bbox", "ink")
        },
        "ink_path_centering_px": {
            "median": round(statistics.median(ink_offsets), PRECISION),
            "max": round(max(ink_offsets), PRECISION),
            "over_half_pixel": sum(offset > 0.5 for offset in ink_offsets),
        },
        "subjects": subjects,
        "by_pack": by_pack,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check", action="store_true",
        help="fail if the committed census no longer describes this tree",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    print("censusing every style of every pack; about 20 seconds", file=sys.stderr)
    fresh = census()
    rendered = json.dumps(fresh, indent=2) + "\n"

    if args.check:
        if not args.out.is_file():
            print(f"{args.out} does not exist; run this script without --check", file=sys.stderr)
            return 1
        if args.out.read_text(encoding="utf-8") != rendered:
            print(
                f"{args.out.relative_to(REPO)} is out of date. The renderer's "
                f"placement has changed, so every number quoted from it has too — "
                f"regenerate, then update the prose the test names.",
                file=sys.stderr,
            )
            return 1
        print("placement census is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
