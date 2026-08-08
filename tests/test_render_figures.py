"""The renderer figures must keep resolving, and must keep showing something.

`docs/_ext/render_figures.py` draws the side-by-side comparisons on
`sizing-and-quality` and the pack grid on `choosing-a-pack`. The Sphinx build
already fails if a name stops resolving or a panel comes out blank, so what is
left for a test is the drift the build cannot see.

**What this does not do is judge the figures.** The first subject chosen for the
measured-ink comparison was a Font Awesome glyph, and it was rejected by looking
at it: the two panels were the same drawing a few pixels apart, which argues
against the paragraph beside it. That pick scores a pairwise alpha difference of
0.243 — *higher* than the Eva glyph that replaced it, at 0.185. A pixel metric
ranks them the wrong way round, so there is no threshold here that would have
caught it and pretending otherwise would be worse than pretending nothing.

The floor below is set to catch a different failure: two panels becoming
*identical*, which is what a refactor that quietly stops honouring `ink=False`
or a `Panel` whose options no longer differ would produce. Everything above that
floor still needs a person to look at it.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXT = REPO / "docs" / "_ext"

if not EXT.is_dir():  # pragma: no cover - an installed checkout has no docs/
    pytest.skip("docs/_ext is not present", allow_module_level=True)

sys.path.insert(0, str(EXT))
render_figures = pytest.importorskip(
    "render_figures", reason="the docs extensions need Pillow and the packs"
)

#: Below this, two panels are the same picture. Well under the smallest real
#: gap in the current set (0.059 for the oversampling pair), because this is a
#: floor against collapse, not a judgement of whether a figure reads.
IDENTICAL = 0.02


def alpha_difference(first, second) -> float:
    """Mean per-pixel difference of the alpha channels, 0.0 to 1.0."""
    from PIL import ImageChops

    if first.size != second.size:
        return 1.0
    diff = ImageChops.difference(first.getchannel("A"), second.getchannel("A"))
    total = sum(value * count for value, count in enumerate(diff.histogram()))
    return total / (255 * first.size[0] * first.size[1])


def panels_for(figure):
    pack = render_figures.pack_by_extra(figure.pack)
    try:
        render_figures.provider_for(pack)
    except render_figures.PackNotInstalled:
        pytest.skip(f"the {figure.pack} pack is not installed")
    return [render_figures.build_panel(pack, figure, panel, "#111827") for panel in figure.panels]


@pytest.mark.parametrize(
    "key", sorted(render_figures.FIGURES), ids=lambda key: key
)
class TestEveryFigureStillDraws:
    def test_every_panel_has_ink(self, key):
        """A blank panel is worse than no figure, and the build says so too."""
        for panel, image in zip(render_figures.FIGURES[key].panels, panels_for(render_figures.FIGURES[key])):
            assert image.getchannel("A").getbbox() is not None, (
                f"{key}: the {panel.caption!r} panel drew nothing"
            )

    def test_the_panels_are_not_the_same_picture(self, key):
        """The difference between panels is the entire content of a figure."""
        images = panels_for(render_figures.FIGURES[key])
        for (i, first), (j, second) in itertools.combinations(enumerate(images), 2):
            difference = alpha_difference(first, second)
            assert difference > IDENTICAL, (
                f"{key}: panels {i} and {j} are the same picture "
                f"({difference:.4f} <= {IDENTICAL}). Whatever the figure was "
                f"demonstrating, it no longer demonstrates it."
            )


class TestTheComparisonGridIsComplete:
    """Five packs by five concepts, and a gap reads as "this pack has no star"."""

    def test_every_pack_has_a_name_for_every_row(self):
        for concept, by_pack in render_figures.COMPARISON_ROWS:
            missing = sorted(set(render_figures.COMPARISON_PACKS) - set(by_pack))
            assert not missing, f"the {concept!r} row has no name for {missing}"

    def test_every_name_resolves_in_its_pack(self):
        """Vocabularies are per pack, so none of this can be derived."""
        broken = []
        for concept, by_pack in render_figures.COMPARISON_ROWS:
            for extra in render_figures.COMPARISON_PACKS:
                pack = render_figures.pack_by_extra(extra)
                try:
                    provider = render_figures.provider_for(pack)
                except render_figures.PackNotInstalled:
                    continue
                try:
                    provider.resolve_icon_name(by_pack[extra], provider.default_style)
                except ValueError:
                    broken.append(f"{extra}/{by_pack[extra]} ({concept})")
        assert not broken, f"COMPARISON_ROWS names glyphs that no longer resolve: {broken}"


class TestFiguresNameRealPacks:
    def test_every_figure_names_a_pack_in_the_catalogue(self):
        from tkinter_icons.packs import KNOWN_PACKS

        known = {pack.extra for pack in KNOWN_PACKS}
        unknown = {
            key: figure.pack
            for key, figure in render_figures.FIGURES.items()
            if figure.pack not in known
        }
        assert not unknown, f"FIGURES names packs that do not exist: {unknown}"

    def test_the_comparison_names_packs_in_the_catalogue(self):
        from tkinter_icons.packs import KNOWN_PACKS

        known = {pack.extra for pack in KNOWN_PACKS}
        unknown = sorted(set(render_figures.COMPARISON_PACKS) - known)
        assert not unknown, f"COMPARISON_PACKS names packs that do not exist: {unknown}"
