# PLAN — a glyph the font does not carry renders blank with no error (#140)

Branch `fix/glyphmap-advertises-glyphs-the-font-lacks`, off `main`. Not created yet — this plan is written before the work, and the reviewing session's scope will be `git diff main..fix/glyphmap-advertises-glyphs-the-font-lacks`.

Written for the session that does the work and the session that reviews it. It states what the code is meant to do and what must hold, so a finding can be checked against intent rather than guessed at.

The previous section here — #91's plan for making Tk optional — is gone rather than archived. It shipped in #139, and its findings are recorded where they belong: in `CHANGELOG.md`, in `tests/test_headless_without_tkinter.py`, and in `CLAUDE.md`. A plan kept past its merge is a second copy of the truth, which is how the placement numbers drifted through three review rounds.

---

## Amendments to this plan

Written after the work, before the review. The plan below is unchanged; this section records where it was **wrong** or **left something open**, so the review measures the diff against what the code was actually meant to do.

**Corrections and decisions only.** The reasoning behind each choice is deliberately not here, and is not in any file the review needs. A reviewer who reads why an approach seemed sound tends to agree with it instead of testing it.

**`mat`'s root cause below is wrong, in both halves.** The plan says its generator "builds the mapping with `glyphmap_from_ttf` from one font and writes a single shared `glyphmap.json` used by both `outline` and `fill`", and calls that "one style's truth published as every style's". In fact `mat`'s two styles are one font split by a name predicate — `_is_outline_style` tests for the `-outline` suffix — so one shared glyph map is what that pack is supposed to have. And `glyphmap_from_ttf` is only the fallback; the mapping comes from upstream's **CSS** whenever one is available, and one was. The fault is that MDI's stylesheet declares `mdi-blank` at U+F68C as a placeholder the webfont has no codepoint for. `mat` therefore contributes **one icon under two names**, not four glyphs.

**Two counts, not one, and the plan quotes only the second.** 121 glyph-map entries were removed. The placement census reports 123, counting once per name *per style*, because `mat`'s two styles share one map. The plan's "123 glyphs across two packs" and "123 of 89,292 entries" apply the per-style figure to an entry-count denominator. Both numbers appear in the shipped prose, each stated with the definition that makes it true.

**The guard is in `IconSet.glyph`, not "beside the existing lookup at `icon.py:331`" as the plan directs.** `icon.py:331` is `render_pil`'s lookup. The Tk widget path has a second one at `icon.py:470`, and this plan's own invariant — "the browser shows no blank tiles" — is a claim about that second path.

**In scope beyond what the plan describes**, both consequences of the line above:

- `IconSet.__len__` and `__contains__` now report what the set can draw rather than what its map advertises. `IconSet.glyphs` is unchanged and still exposes the raw map.
- `render_pil` selected its icon set with `icon_set or cls._icon_set_current`. A sized object that can draw nothing is falsy, so the caller's set could be replaced by whichever loaded last. It selects on `is None` now.

**The open decision at "Known-weak spots" was decided: filter the committed data locally, do not regenerate from upstream.** The generators' new `restrict_to_font` step was run against the tree as committed. `write_glyphmap` was first confirmed to reproduce all five committed files byte-identically, so the data diff is 121 removed lines and nothing else.

**Metrics were already correct and were not regenerated.** `generate_metrics --all --check` is clean both before and after the data change.

---

## What this is supposed to do

A name that is in a pack's glyph map but whose codepoint the pack's own font does not carry renders as a fully transparent image, with no exception and no warning — **not even under `on_missing="raise"`**. 123 glyphs across two packs are in this state, they are advertised by the packs' own `build_name_lookup()`, and the shipped icon browser draws them as empty tiles.

There are three ways an icon can fail to be found. Two are answered; the third is not.

| | Case | Where | Behavior |
|---|---|---|---|
| 1 | The name resolves nowhere in the pack | `provider.resolve_icon`, `icon.py:324` | Raises `ValueError`, matching the constructor. Correct — this is what #115/#135 closed. |
| 2 | The name resolves, but the set has no glyph for it | `icon_set.glyph`, `icon.py:331` | `on_missing` policy. Correct, deliberate, documented. |
| 3 | The set has a glyph, but the **font's cmap has no such codepoint** | nowhere | Silently draws nothing. **This issue.** |

`on_missing` guards the glyph *map*. Nothing guards the *font*. In case 3 `resolve_icon` succeeds and `icon_set.glyph(name)` returns a real character, so `_report_missing` never fires — from the glyph map's point of view nothing is missing — and `render_glyph` hands the codepoint to Pillow, which renders `.notdef`. In both affected packs `.notdef` is empty, so the result is a blank square rather than the usual tofu box.

The same pack answers the same name two different ways, which is the #115 divergence one layer down:

```
MatIcon.render_pil("blank", style="outline")  ->  ValueError: blank not found in lookup for mat in outline style.
MatIcon.render_pil("blank", style="fill")     ->  blank image, silently
```

---

## Root cause — two separate bugs, not one

**`gmi`, 119 of the 123.** `packages/tkinter-icons-gmi/src/tkinter_icons_gmi/tools/generate_assets.py:132-136` parses one downloaded `.codepoints` text file — the **baseline** one — and writes it verbatim to all four style glyphmaps, under a comment that states the false assumption out loud: *"Material Icons use the same codepoints across all styles"*. Baseline carries 43 codepoints `outlined` does not, 38 `round` does not, and 38 `sharp` does not. This is also why all four styles report an identical 4,468 names. The generator already imports `glyphmap_from_ttf` and does not use it on this path.

**`mat`, the other 4.** `packages/tkinter-icons-mat/src/tkinter_icons_mat/tools/generate_assets.py:108-114` builds the mapping with `glyphmap_from_ttf` from one font and writes a single shared `glyphmap.json` used by both `outline` and `fill`. Different mechanism, same shape of defect: one style's truth published as every style's.

Neither is a data scrub. **Fix the generators, or the next asset regeneration reintroduces all 123.**

---

## The shape of the fix — two halves

**The data half fixes today's symptom.** Build each style's glyphmap from that style's own font, or intersect the shared mapping with each font's cmap before writing. This needs a pack release for `gmi` and `material`, which the single `v5.1.0` tag carries alongside the base — that is #97 working as designed.

**The guard half makes the next one loud.** Add the cmap check beside the existing lookup at `icon.py:331` and route a miss through `_report_missing`, so it lands under the same `on_missing` policy: a name in the map with no glyph in the font is precisely "the set's data is inconsistent", which is what that policy is documented to cover. Compute the cmap's codepoint set once per `IconSet` and cache it alongside `font_bytes`, so the cost is one membership test per render.

The argument for the guard is stronger *because* the generators are the root cause: they are run rarely and by hand, upstream fonts drift between releases, and nothing in CI reads a font.

---

## Invariants

- **Every glyph-map entry's codepoint is present in that style's font**, for every installed pack and every style. This is the invariant to assert directly — not a frozen count of 123, which stops meaning anything the moment the data is fixed.
- **`on_missing` still governs case 2 unchanged.** `"transparent"` stays the default and the transparent square for a name that reaches a set without a glyph stays deliberate. Case 3 joins that policy rather than growing a new one.
- **Case 1 still raises.** Nothing here may soften what #135 established.
- **The browser shows no blank tiles in any style of any pack**, which is the user-visible statement of the first invariant.
- **`render_glyph` keeps taking a character, not a name.** It sits below resolution and must not grow a provider dependency. (See the docstring on `test_render_glyph_draws_without_tkinter` for what happens when a caller confuses the two.)
- **The census delta goes to zero.** `totals.glyphmap_entries - totals.drawing` is currently exactly 123; after the data fix it is 0.

---

## How it should be tested

A new test asserting the first invariant, alongside `tests/test_placement_census.py` and with the same skip-if-absent handling — it needs all sixteen packs installed, which the CI matrix deliberately does not guarantee. Shape:

```python
for pack in installed_packs:
    for style in provider.style_list or [None]:
        iset = get_icon_set(provider, style)
        cmap = TTFont(io.BytesIO(iset.font_bytes)).getBestCmap()
        for name, ch in iset.glyphs.items():
            assert len(ch) == 1 and ord(ch) in cmap
```

That check would have failed the day the `gmi` generator was written, and it stays meaningful after the data is fixed.

Guard the `fontTools` import the way `tests/test_packs.py` guards `tomllib` — CI runs 3.10 through 3.14 and the working venv here is only one of them. Prefer guarding **inside a helper** rather than at module scope, so a missing dependency does not silently retire the whole file.

For the guard half, a test that a set whose glyph map points at an absent codepoint applies `on_missing` — constructed by hand, since after the data fix no shipped pack is in that state.

---

## Knock-on, and the sequencing that matters

Fixing the data moves the census. `.github/scripts/generate_placement_census.py` must be re-run and the four files `tests/test_placement_census.py` checks updated with it: `docs/user-guide/sizing-and-quality.rst`, `docs/_ext/render_figures.py`, `docs/_data/placement-census.json`, and `CLAUDE.md`. It is 178,584 renders, about 20 seconds. **Do this before writing any 5.1.0 release prose, not after** — the released numbers should be the fixed ones.

Regenerate with the script, never by hand. Three sessions measured these numbers with throwaway snippets and transcribed them, and they disagreed every time.

---

## Known-weak spots — worth a reviewer's attention

- **Regenerating a pack's assets downloads from upstream**, so a regeneration is not reproducible against a moving source and may pick up unrelated upstream drift. Consider filtering the *committed* glyphmaps against the committed fonts instead, which is a pure local transform and reviewable as a diff. That is a real decision, not an obvious call — the generator is still wrong either way and should be fixed, but whether this PR *runs* it is separate.
- **Dropping names is a user-visible removal.** Anyone currently calling `GMatIcon("add_call", style="outlined")` gets a blank today and a `ValueError` after the fix. That is the intended improvement, but it belongs in `CHANGELOG.md` under Changed with the names counted, not buried under Fixed.
- **The cmap lookup is per-`IconSet`, and `IconSet` is immutable and cached.** Whatever holds the codepoint set has to respect that, and `fontTools` on every set construction is not free — measure before assuming it is negligible, or derive the set from the glyph map's own values rather than parsing the font twice.
- **`.notdef` being empty is what made this invisible.** A pack whose `.notdef` is a tofu box would have shown visible garbage instead of nothing. Do not write the guard in a way that only catches the blank case.
- **Scale is modest and should not be oversold**: 123 of 89,292 entries, 0.14%, two of sixteen packs, and every pack's default style is already clean. Nothing crashes and no correct call yields a wrong image. It is worth fixing because the silence violates the rule that a missing icon should say so, and because it already cost a reviewer time as an unexplained census discrepancy.
