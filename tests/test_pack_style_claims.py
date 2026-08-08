"""A pack may not advertise a style its provider does not ship.

`tkinter-icons-gmi` told PyPI it offered `baseline/outlined/round/sharp/twotone`
for the whole 5.0.0 cycle. Its provider ships the first four and never had the
fifth — the claim came from upstream's copy, which went stale, and nothing read
it. It was wrong in the distribution's `description` *and* in the README intro,
which are the two places PyPI freezes at release time, so it cost a release of
that pack rather than a docs edit (#111).

Neither `verify_packages.py --strict` nor `generate_pack_readmes.py --check`
caught it: the README's *generated* body lists the real styles from the live
provider, so the page contradicted itself and both checks passed. What is not
generated is the summary line and the hand-written intro, and that is exactly
where the stale claim survived.

**Scoped to false positives on purpose.** A pack naming a style it *does* ship
is fine, and a pack characterising its glyphs is fine — "filled and outline
variants" beside a style literally named `fill` is prose, not a style claim. So
this only fires on a word that reads as a style and is not in `style_list`, and
it exempts a single-style pack naming its own style: `tkinter-icons-fluent-reg`
exists to ship Regular alone, says so, and a naive version of this check calls
that a lie. That exemption is the reason this is a small allowlist rather than a
blanket word search.
"""

from __future__ import annotations

import importlib
import pathlib
import re
import tomllib

import pytest

from tkinter_icons.packs import KNOWN_PACKS

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Words that read as a style name rather than as a description of the drawing.
#: Deliberately a closed list: any word can appear in prose, and the failure
#: being guarded is a *style* being advertised, not a font being described.
STYLE_WORDS = frozenset({
    "baseline", "outlined", "twotone", "duotone", "sharp", "round",
    "solid", "brands", "thin", "light", "regular", "filled", "fill",
    "outline", "line", "plain", "original", "wordmark",
})

#: Words that are ordinary English in a sentence about icons, where a style
#: reading would be a false positive. "filled and outline variants" describes
#: what the glyphs look like; `fill` and `outline` are what you pass to
#: `style=`. Only the exact spellings in `style_list` are treated as claims.
PROSE_SAFE = frozenset({"filled", "outline", "light", "regular", "plain", "original"})


def provider_for(pack):
    module = importlib.import_module(f"{pack.module}.provider")
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class in {pack.module}.provider")


def pack_dir(pack) -> pathlib.Path:
    path = REPO / "packages" / pack.distribution
    if not path.is_dir():
        pytest.skip("not running from a source checkout")
    return path


def summary(pack) -> str:
    config = tomllib.loads((pack_dir(pack) / "pyproject.toml").read_text(encoding="utf-8"))
    return config["project"]["description"]


def intro(pack) -> str:
    """The hand-written prose between the H1 and the first badge or heading.

    The same span `generate_pack_readmes.hand_written_intro` preserves, and the
    only part of the page a generator does not keep true.
    """
    lines = (pack_dir(pack) / "README.md").read_text(encoding="utf-8-sig").splitlines()
    out, seen_h1 = [], False
    for line in lines:
        if line.startswith("# "):
            seen_h1 = True
            continue
        if not seen_h1:
            continue
        if line.startswith("##") or line.startswith("[![") or line.strip() == "---":
            break
        out.append(line)
    return "\n".join(out)


def shipped_words(styles: set[str]) -> set[str]:
    """Every word a pack may legitimately use, including hyphen components.

    Devicon ships `plain-wordmark` and `original-wordmark`, so "wordmark" on its
    page names something real even though no style is spelled that way on its
    own. Comparing whole strings reported it as a false claim.
    """
    words = set(styles)
    for style in styles:
        words.update(style.split("-"))
    return words


def bogus_claims(text: str, styles: set[str], *, allow_prose: bool) -> list[str]:
    """Style words in `text` that this pack does not actually ship."""
    found = {word for word in STYLE_WORDS if re.search(rf"\b{word}\b", text, re.I)}
    claimed = found - shipped_words(styles)
    if allow_prose:
        claimed -= PROSE_SAFE
    return sorted(claimed)


@pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
class TestNoPackAdvertisesAStyleItDoesNotShip:
    def test_the_distribution_summary_is_true(self, pack):
        """The summary is a bare list, so every style word in it is a claim.

        This is the field that was wrong for `gmi`, and it is the first line of
        the PyPI page. No prose exemption applies: a summary reading
        "(baseline, outlined, round, sharp)" is enumerating `style_list`.

        A pack with an empty `style_list` is skipped, and that is the exemption
        `CLAUDE.md` requires rather than an oversight. `fluent-reg` ships the
        Regular cut alone and says "Regular" in its summary; with no selectable
        styles there is no `style=` argument to misrepresent, so the word is
        naming the font rather than advertising an option. The cost is that a
        style-less pack could describe itself wrongly and pass — which no
        mechanical rule can separate from naming its own identity.
        """
        styles = set(provider_for(pack).style_list or ())
        if not styles:
            pytest.skip("a pack with no selectable styles is naming its font, not a style")
        bogus = bogus_claims(summary(pack), styles, allow_prose=False)
        assert not bogus, (
            f"{pack.distribution}'s summary advertises {bogus}, which its provider "
            f"does not ship (it has {sorted(styles) or 'no styles'}). PyPI freezes "
            f"this line at release time, so fixing it needs a release of this pack."
        )

    def test_the_readme_intro_is_true(self, pack):
        """The intro is prose, so only an unambiguous style word counts.

        A single-style pack is allowed to name its one style — that is
        `fluent-reg`'s entire reason to exist, and calling it a false claim is
        how a naive version of this check earns itself an exemption list that
        everyone then ignores.
        """
        provider = provider_for(pack)
        styles = set(provider.style_list or ())
        if not styles:
            pytest.skip("a pack with no selectable styles has no style claim to check")
        bogus = bogus_claims(intro(pack), styles, allow_prose=True)
        assert not bogus, (
            f"{pack.distribution}'s README intro names {bogus}, which its provider "
            f"does not ship (it has {sorted(styles)}). The intro is the one part of "
            f"that page a generator does not keep true."
        )
