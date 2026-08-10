# REVIEW — #140, `fix/glyphmap-advertises-glyphs-the-font-lacks`

Findings and resolutions, newest round last. Read `PLAN.md` for what the branch is meant to do.

**Round 2 scope is `git diff b8817c0..HEAD` — the fix diff only, not the branch.** Round 1 reviewed `main..b8817c0` and its findings are settled below; re-reviewing the whole branch relitigates them.

---

## Round 1 — `main..b8817c0`

Seven findings. Verification run alongside them was green: 781 passed / 15 skipped, `sphinx -W -n -j auto` clean, census, pack READMEs, packaging preflight and `generate_metrics --all --check` all clean. The data change was checked as internally consistent — `gmi` 2234+2191+2196+2196 = 8,817 matches its README, `mat` 14,894 matches, and the changelog's 43/38/38 split matches the three glyphmap diffs.

Nothing in the core fix was found wrong: the check in `IconSet.glyph` reaches both `render_pil` and `_render`, the `icon_set or …` → `is None` correction was genuinely latent, `_report_missing`'s branch is reachable only in the state its message describes, and `restrict_to_font`'s fail-loud-in-generator / fail-open-in-renderer asymmetry is deliberate.

### 1. `sfnt.py:81` — a partial cmap read returned as authoritative — **should-fix** — FIXED

Root cause: `_parse_subtable` returned `None` for any format it did not handle and `_cmap_codepoints` skipped it, but `found` was already `True` from an earlier subtable. The union returned was therefore missing that subtable's coverage while being reported as the complete answer. A subtable that *raised* aborted the whole parse correctly; one that was merely unrecognized silently narrowed the result. Fail-closed, in a module whose stated contract is fail-open.

Failure scenario: a font pairing a format 4 at (3,1) with a format 13 at (3,10). Every supplementary glyph reports absent, `IconSet.glyph` returns `None`, and the user gets a transparent square — or a `KeyError` under `on_missing="raise"` asserting the fault is in the pack's glyph map, for a pack that is fine.

Reachability: no shipped font is affected. All 31 font/style combinations use only formats 0/4/6/12 on platforms 0/1/3. Reachable only through a third-party `BaseFontProvider` subclass.

Fixed: an unhandled format raises `ValueError`, which `cmap_codepoints` already converts to `None`. Format 14 returns `None` from the dispatch and is skipped *without* setting `found`, since it maps variation sequences onto glyphs a base subtable already reaches. Test: `test_a_subtable_it_cannot_read_makes_the_whole_font_unknown`, verified to fail against the pre-fix source. `test_a_variation_sequence_table_is_skipped_without_emptying_the_font` covers the exception and passes both before and after — it is not a regression test, it constrains the fix's shape.

### 2. `sfnt.py:116` — `_is_unicode_encoding` admitted non-Unicode encodings — **nit as reported, should-fix after finding 1** — FIXED

Root cause: platform 3 encodings 2–6 are ShiftJIS, PRC, Big5, Wansung and Johab, which address glyphs by legacy multi-byte code value rather than by codepoint — the same reason platform 1 is excluded.

Severity was re-ranked during the fix step. As reported this errs fail-open and is nearly unreachable, since those subtables are format 2 in practice and the dispatch dropped them. Finding 1's fix inverts that: an unhandled format now poisons the whole font, so a font carrying one legacy table would lose the coverage check for every glyph it has.

Fixed: platform 3 restricted to encodings 0, 1 and 10. Verified a no-op for everything shipped by comparing old and new admission for every subtable of all 31 styles — 0 changed. Test: `test_only_codepoint_addressed_subtables_are_read`.

### 3. `iconset.py:103` — `len()` and `bool()` are O(n) and uncached — **should-fix** — FIXED

Root cause: `__len__` called `can_draw` once per entry and kept nothing, so every call rescanned the map. `__bool__` was undefined and fell through to it. Measured 5.33 ms per call for `mat`'s 14,894 glyphs; the underlying frozenset membership is only 0.041 µs of that, the rest being per-call overhead multiplied by the entry count.

No live regression — nothing in shipped code calls either in a loop; the only callers are tests. The branch's own changelog documents `icon_set or …` as a trap, so truthiness is an operation users demonstrably write.

Fixed: the count is a `cached_property` on the frozen dataclass, and `__bool__` short-circuits at the first drawable glyph. `len()` 5330 µs → 0.063 µs, `bool()` 5330 µs → 0.597 µs, `glyph()` unchanged at 0.45 µs. Both answers still derive from `can_draw`, so a set cannot report truthy while counting zero. Tests: `test_the_count_is_memoized_not_recomputed` (verified to fail against the pre-fix source) and `test_truthiness_agrees_with_the_count`.

### 4. `docs/user-guide/icons-and-names.rst:134` — paragraph renders as a detached block quote — **should-fix** — FIXED

Root cause: the closing paragraph was indented three spaces following an unindented paragraph, so reStructuredText made it a block quote rather than body text or part of the `.. versionchanged:: 5.1.0` directive it visually reads as. `sphinx -W -n` cannot catch this because a block quote is legal markup.

Fixed: dedented to column 0. Built HTML now shows it as a `<p>` and the page has zero `<blockquote>` elements.

### 5. `sfnt.py:175` (was 135) — `_parse_format_0` truncates silently — **nit** — NOT FIXED

Root cause: the 256 glyph ids are taken with a slice rather than `unpack_from`, so a truncated subtable yields fewer entries with no exception and the partial coverage is marked `found = True`. Every other parser here raises on truncation.

Deferred: unreachable for shipped fonts. Every format 0 subtable in the project sits on platform 1, which is excluded before the dispatch. Same fail-closed direction as finding 1; minimal change is `struct.unpack_from(">256B", …)`.

### 6. `sfnt.py:207,211` (was 165) — U+FFFF unconditionally excluded — **nit** — NOT FIXED

Root cause: a segment with `start_code == 0xFFFF` is skipped and every other segment clamped with `min(end_code, 0xFFFE)`, so a font genuinely mapping U+FFFF would report it absent and would fail `test_the_parser_reproduces_fonttools_on_every_shipped_font`. The existing `glyph_id != _NOTDEF` check already handles the required terminating segment.

Deferred: U+FFFF is a noncharacter and is not mapped by real fonts.

### 7. `sfnt.py:250` (was 208) — format 12 enumeration is unbounded — **nit** — NOT FIXED

Root cause: `_parse_format_12` enumerates every codepoint in every group. One group declaring `0x0`–`0x10FFFF` passes the `end_char > 0x10FFFF` guard at ~1.1M iterations and ~50 MB for that group alone, and `group_count` is bounded only by file length. This is on the path of the first `IconSet.glyph` call, so a guard designed never to break rendering could instead freeze startup. `struct.error`/`MemoryError` from the group header is caught; the enumeration is not.

Deferred: requires a malformed font, and fonts arrive as fixed bytes inside a pack wheel rather than from user input. Real parses measure 3.5–6.6 ms. Minimal change is a cap on total codepoints returning `None` past it, or storing ranges rather than members.

---

## Notes for round 2

- **Scope is `git diff b8817c0..HEAD`.** Findings 5, 6 and 7 above were triaged and deliberately left; re-raising them is duplicate unless the fix diff changed their reachability.
- Findings 1 and 2 are coupled — 2 exists because of 1, and the pair is only correct together.
- The fix step was performed by the session that wrote the branch, which is a protocol deviation the owner asked for explicitly. Its own pass caught finding 2's re-ranking and one false claim in a docstring it had just written; treat the whole fix diff as unreviewed regardless.
- `sfnt.py` is not covered by the `fontTools` parity test for any case above, since no shipped font exercises them. The parity reference in `tests/test_font_coverage.py` still admits platform 3 at every encoding, so it and `_is_unicode_encoding` would disagree on a font carrying a legacy subtable. No shipped font does. Left as-is deliberately: narrowing the reference to match the implementation would make the independent check a mirror.
- Full-suite skip count oscillates between 14 and 15 across identical runs (`test_browser_assets.py:177`, no display). That is the Tk-ordering flake `CLAUDE.md` documents, not a regression.

---

## Round 2 — `b8817c0..HEAD`

Seven findings, one medium and six low. Verification alongside them was green — 787 passed / 14 skipped, `sphinx -W -n -j auto`, census, pack READMEs and `verify_packages --strict` all clean — so none of them moved a check. The data change was independently re-derived and holds: 43/38/38 for `gmi` with round and sharp identical and both subsets of outlined, all 43 still in `baseline`, the seven named substitutes present in all three cuts, `mat` losing `blank`/`mdi-blank` only, every metrics file now matching its glyph map exactly, and none of the 45 removed names referenced by `pack_showcase.SHOWCASE`, the docs examples or any script.

**All seven are fixed, together with round 1's deferred findings 5 and 7.** Two changes the owner directed landed in the same pass and are not review findings: `on_missing` now defaults to `"raise"`, and coverage is stored as ranges rather than as a set of codepoints.

### 1. `tests/test_font_coverage.py:234` — the parity test claimed formats it never runs — **medium** — FIXED

Root cause: the shipped fonts carry sixteen format 0 and three format 6 subtables, but every one is on platform 1, which `_is_unicode_encoding` rejects before the dispatch. The formats actually parsed across all 31 styles are 4 and 12 only; instrumenting `_parse_format_0` and `_parse_format_6` and running the full suite recorded zero calls to each. So two parsers shipped with no coverage at all, and they are exactly the ones only a third-party font can reach — the population the fail-open exists for. Round 1's own finding 5 recorded that format 0 is unreachable, so the fact was known and the claim was not corrected. The same sentence was in `CHANGELOG.md`, which ships to the GitHub Release page, and in `CLAUDE.md`.

Fixed both ways: the claim now says formats 4 and 12 are what `fontTools` verifies, and `TestTheFormatsNoShippedFontReaches` covers 0 and 6 against constructed subtables with hand-computed expectations. That is a weaker instrument than the parity test and the test's own docstring says so.

### 2. `sfnt.py:248` — a malformed format 12 group was skipped while the font still reported success — **low** — FIXED

Root cause: exactly round 1's finding 1 one level down. `continue` on a backwards or out-of-range group left `found` already `True`, so the union came back missing that group's coverage and presented as authoritative. `_parse_format_4` had the same shape. Both raise now, which `cmap_coverage` converts to `None`, and the module docstring states the rule for entries as well as for formats. Test: `TestAMalformedSubtableMakesTheFontUnknown`.

### 3. `packages/tkinter-icons-gmi/.../generate_assets.py:152` — partial write before refusing — **low** — FIXED

Root cause: the `font_path is None` guard sat inside the write loop, so a download failure on `sharp` exited after baseline, outlined and round had already been rewritten — three regenerated maps beside one stale one. The check is hoisted above the loop and names every missing font at once.

### 4. `providers.py:474` — style resolution does not consult the font — **low** — NOT FIXED, documented

Root cause: `resolve_icon` picks the first candidate style whose glyph map has the name; the font check runs afterwards in `IconSet.glyph`. A name mapped in several styles, absent from the first candidate's font and present in a later one's, resolves to the style that cannot draw it.

Deferred deliberately, and the reasoning is now in `resolve_icon`'s docstring rather than only here. Closing it means loading and parsing every candidate style's font during resolution — most of the work of rendering, on every name — to fix a case no shipped pack can reach, since `test_font_coverage.py` asserts every style's map against its own font and both generators intersect the two before writing. The docstring names this as the second place to change if that invariant is ever relaxed.

### 5. `iconset.py:140` — `__bool__` ignored the memoized count — **low** — FIXED

`_drawable_count` is a `cached_property` and `__bool__` re-scanned regardless. Harmless for a healthy set, which stops at the first drawable glyph, and worst for a set that draws nothing — the one case the short-circuit was written for. It now reads the cache when `__len__` has populated it and falls back to `any` otherwise.

### 6. `icon.py:462` — the diagnostic blamed a pack for a hand-built set — **low** — FIXED

"A fault in the icon pack's glyph map" was emitted for any `IconSet`, including one the caller assembled and passed as `icon_set=` — which `render_pil`'s docstring explicitly supports. The message now distinguishes the two by asking whether the registry hands out that exact object, and `test_the_message_blames_a_pack_only_when_a_pack_is_involved` exercises both branches, because a message with one unread branch is what rots.

### 7. `docs/user-guide/icons-and-names.rst:127` — the section contradicted itself — **low** — FIXED

The lead said a pack's own name can land in the policy; four paragraphs later the same section said every pack advertises exactly what it can draw. Both were defensible readings of mechanism versus current data. The lead is now scoped to the mechanism and says plainly that no shipped pack is in that state.

### Round 1's deferrals, revisited

- **Finding 5 (format 0 truncates silently) — now FIXED.** It stopped being unreachable-in-principle the moment finding 1 above gave the two parsers real tests; `_parse_format_0` raises on a short table.
- **Finding 7 (format 12 enumeration unbounded) — now FIXED, by the representation change.** Round 1 named the two options as "a cap on total codepoints, or storing ranges rather than members"; the second is what shipped, for the memory reason rather than this one. Groups are emitted as ranges without being walked, so a group spanning a plane costs one pair of bounds instead of 1.1M iterations and ~50 MB. Measured on the shipped styles: 17.4 KB of bounds against 5,792 KB of codepoint sets, membership 0.18 µs against 0.04 µs.
- **Finding 6 (U+FFFF excluded) — still NOT FIXED.** Unchanged reasoning: U+FFFF is a noncharacter and real fonts do not map it.

### Notes for round 3

- **Scope is `git diff <this round's base>..HEAD`.** Rounds 1 and 2 are settled above.
- The behavior change is the thing to review hardest: `on_missing` defaulting to `"raise"` is the owner's call, but *what else was silently depending on the old default* is a review question. One such dependency was found and fixed during the change — the `"none"` sentinel drew a blank only by falling through the missing-name path, so it already raised for anyone who set `on_missing="raise"`. Look for others.
- `Coverage` is a new public class in `sfnt.py` and `render.font_codepoints` was renamed to `font_coverage`. Neither has ever been released, so nothing external can depend on the old shape.
- The fix step was again performed by the session that ran the review, at the owner's direction.
