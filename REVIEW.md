# REVIEW — #140, `fix/glyphmap-advertises-glyphs-the-font-lacks`

Findings and resolutions, newest round last. Read `PLAN.md` for what the branch is meant to do.

**Round 3 scope is `git diff 77a0b7b..550f5ed` — three commits, not the branch.** Rounds 1 and 2 are settled below; re-reviewing the whole branch relitigates them.

Every scope in this file is pinned to explicit SHAs rather than written `..HEAD`. `HEAD` was correct in each round for about a day and then silently named the wrong range — a review file is read by a session that arrives after the tip has moved, which is the one condition under which `..HEAD` is guaranteed to mislead.

| Round | Scope | Tip when it ran |
|---|---|---|
| 1 | `main..b8817c0` | `b8817c0` |
| 2 | `b8817c0..77a0b7b` | `77a0b7b` |
| 3 | `77a0b7b..550f5ed` | `550f5ed`, pushed, unmerged |

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

- **Scope is `git diff b8817c0..77a0b7b`.** Findings 5, 6 and 7 above were triaged and deliberately left; re-raising them is duplicate unless the fix diff changed their reachability.
- Findings 1 and 2 are coupled — 2 exists because of 1, and the pair is only correct together.
- The fix step was performed by the session that wrote the branch, which is a protocol deviation the owner asked for explicitly. Its own pass caught finding 2's re-ranking and one false claim in a docstring it had just written; treat the whole fix diff as unreviewed regardless.
- `sfnt.py` is not covered by the `fontTools` parity test for any case above, since no shipped font exercises them. The parity reference in `tests/test_font_coverage.py` still admits platform 3 at every encoding, so it and `_is_unicode_encoding` would disagree on a font carrying a legacy subtable. No shipped font does. Left as-is deliberately: narrowing the reference to match the implementation would make the independent check a mirror.
- Full-suite skip count oscillates between 14 and 15 across identical runs (`test_browser_assets.py:177`, no display). That is the Tk-ordering flake `CLAUDE.md` documents, not a regression.

---

## Round 2 — `b8817c0..77a0b7b`

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

- **Scope is `git diff 77a0b7b..550f5ed`.** Rounds 1 and 2 are settled above.
- The behavior change is the thing to review hardest: `on_missing` defaulting to `"raise"` is the owner's call, but *what else was silently depending on the old default* is a review question. One such dependency was found and fixed during the change — the `"none"` sentinel drew a blank only by falling through the missing-name path, so it already raised for anyone who set `on_missing="raise"`. Look for others.
- `Coverage` is a new public class in `sfnt.py` and `render.font_codepoints` was renamed to `font_coverage`. Neither has ever been released, so nothing external can depend on the old shape.
- The fix step was again performed by the session that ran the review, at the owner's direction.

---

## Round 3 — `77a0b7b..550f5ed`

Six findings, one blocking and the rest smaller. Verification alongside them was green — 797 passed / 14 skipped, `sphinx -W -n -j auto` clean — so again none of them moved a check.

Every figure in the round's prose was independently reproduced: 17.4 KB of bounds across 31 styles, 73,990 codepoints in 2,231 ranges, `fluent:filled` at 741 KB as a set against 16 bytes in two ranges, `fontawesome:solid` at 709 ranges and 5,672 bytes, and 5,792 KB total as sets — that last one with the caveat in finding 6. Nothing in the core round-3 work was found wrong: `Coverage` membership is correct at both range edges, `_merge` and `_runs` are order-independent as documented, format 12's `.notdef` trimming is sound because group glyph ids are consecutive and non-negative, `NO_ICON` short-circuits ahead of the policy on both entry points under all three settings, and the `__bool__` cache read agrees with `__len__` including at zero.

**The behavior change was reviewed as round 2's note asked, and it turned up one more thing that was depending on the old default — finding 1.**

### 1. `icon.py:537` — the policy is per-class on one path and hardcoded on the other — **blocking** — FIXED, by removing the policy

Root cause: `_render` calls `Icon._report_missing(...)` with the base class named literally, while `render_pil` calls `cls._report_missing(...)`. `_report_missing` reads `cls.on_missing`, so a policy set on a pack subclass is honored headlessly and ignored by the Tk widget path, which reads the base class's setting instead.

Demonstrated live: with `BootstrapIcon.on_missing = "transparent"`, `BootstrapIcon.render_pil("definitely-not", icon_set=…)` returns a blank image while `BootstrapIcon("definitely-not").image` raises `KeyError: "Icon 'definitely-not' is not in icon set 'bootstrap:default'."`

This is the second dependency on the old default, and it is the damaging kind. While the default was `"transparent"` the two paths agreed by accident — the hardcoded class and the caller's class had the same setting, so nothing diverged. Flipping the default to `"raise"` makes a user who scopes `on_missing` to their own pack class to keep a UI drawing blanks get an unhandled `KeyError` inside a Tk callback instead. It is also exactly the "two entry points answer one question two ways" defect of #115 and #140, reintroduced in the file that closes it.

Minimal change as reported: `type(self)._report_missing(...)` at that call site, plus a test that sets the policy on a subclass and exercises both paths.

**Fixed differently, at the owner's direction: `on_missing` is removed entirely and a name that cannot be drawn always raises.** The reported fix would have made the two call sites agree about a policy whose existence was the real defect. Reading the history settled that — `on_missing` was introduced by the #67 renderer rework (`e1063b8`, 2026-07-30) and was not a designed feature: 4.0.x's `_render` returned `Icon._get_transparent(self.size)` for any name its map lacked, with no option and no warning, and the rework preserved that as the default while adding `"warn"` and `"raise"` as ways out of it. The option existed to escape the old behavior, and its default carried the old behavior into 5.0.0 and 5.0.1.

The justification for keeping `"transparent"` and `"warn"` — bulk renderers that must not stop at the first bad name — does not survive checking. Nothing in this repository sets the policy: not the browser, not the placement census over 178,584 renders, not the two docs extensions that render every pack's previews. They cannot reach it, because they iterate names taken from the glyph map and so cannot produce one the map lacks. The cited caller is hypothetical, and a real one writes `try`/`except`.

What removal changes, beyond deleting the divergence: `MissingPolicy`, the `on_missing` `ClassVar` and `_report_missing` are gone; the message-building moved to a module-level `_missing_glyph_error` that *returns* the exception, so there is no class state left for two call sites to read differently and no `cls` for one of them to hardcode. `NO_ICON` is answered before the lookup on both paths rather than by failing one. Tests: `TestAGlyphThatCannotBeDrawnRaises` and `TestBothEntryPointsAnswerAMissingNameIdentically`, the latter pinning that the widget path and the headless path raise the same message — the behavior, not the refactor, since it is the behavior that has now regressed twice.

**One residual sharp edge, stated rather than fixed.** `Icon.on_missing = "transparent"` still assigns cleanly, because `__slots__` governs instances and not the class, so a line left over from 5.0.x is inert rather than loud. Catching it means a metaclass — `Icon` is already `ABC`, so an `ABCMeta` subclass — which is more machinery than the setting ever justified. The changelog tells readers to delete the line. The first draft of that changelog entry claimed the assignment would "fail loudly", which was simply false and was caught by trying it.

### 2. `tests/test_font_coverage.py:472` — an assertion that cannot fail — **should-fix** — FIXED

Root cause: `assert coverage.range_count <= len(coverage)` is a tautology, since every range covers at least one codepoint by construction. The test is named `test_coverage_is_ranges_rather_than_codepoints` and its docstring says the ranges are far fewer than the codepoints they stand for, but a regression to one range per codepoint passes it unchanged. Only the `nbytes` assertion on the next line does any work.

Same shape as round 1's dead `Panel.size` finding in the docs stack: a test whose name claims the property the representation change exists for, and which no longer checks it. Note the `nbytes` assertion also hardcodes an itemsize of 4 where `sfnt.py:77` only asserts `>= 4`.

**The suggested minimal change was wrong, and measuring it is what showed that.** `range_count * 8 < len(coverage)` fails outright: 33× is the *aggregate* — 73,990 codepoints over 2,231 ranges across everything installed — and no single style comes close to it. The tightest is `fontawesome:regular` at 2.05×, 436 codepoints in 213 ranges, because a nearly-contiguous coverage and a badly scattered one compress by completely different amounts. Deriving a per-style floor from an aggregate figure is the same error as quoting the placement census's per-name and per-style counts interchangeably, which is the thing this branch already documents twice.

Fixed with three assertions instead of one: strict `range_count < len(coverage)` per style, which the degenerate one-range-per-codepoint case fails and the old `<=` did not; `nbytes == range_count * 2 * array("I").itemsize`, no longer hardcoding 4; and the 33× compression asserted as an **aggregate** with a floor of 10×, which is the form the number is actually true in and is what the module docstring and the changelog both quote. The docstring states both populations and the 2.05× tightest case, so the next person does not re-derive the same wrong floor.

### 3. `tests/test_font_coverage.py:386` — the test named for both formats reaches only one — **should-fix** — FIXED

Root cause: `test_both_are_reachable_through_the_public_entry_point` patches a subtable to format 6 and nothing to format 0. Instrumenting `_parse_subtable` across the full suite records `{4: 872, 6: 2, 12: 454, 13: 1, 14: 4}` and no format 0 at all, so the dispatch arm at `sfnt.py:309` still has zero coverage — which is the precise gap round 2's finding 1 was raised to close, in the test written to close it.

Minimal change: patch a second copy to format 0, padding the subtable to 256 glyph ids first since `_parse_format_0` now raises on a short table; or rename the test to say it covers format 6 only. The first is preferable — a name that overstates its coverage is how this gap survived round 2.

Fixed by parametrizing over both formats. No padding was needed: the patch rewrites one field of a real font, and a real format 4 subtable is far longer than the 262 bytes `_parse_format_0` reads, so the truncation guard is never reached.

**The dispatch is now counted rather than inferred.** The test asserted only that `cmap_coverage` returned non-`None`, which is why it could name two formats while exercising one — nothing in it could tell the difference. It monkeypatches the parser and asserts the call was made, so a wrong parametrization fails here instead of silently testing format 6 twice. That is the same instrument round 2 used to *find* this class of defect, now standing in the test rather than in a throwaway script.

### 4. `sfnt.py:376` — format 6 accepts a run that runs past U+FFFF — **should-fix as reported, DECLINED**

Root cause: `_parse_format_6` does not check `first_code + entry_count - 1 <= 0xFFFF`. Format 6 addresses characters as `uint16`, so such a table is structurally impossible, and the rule this same diff states in the module docstring and applies to formats 4 and 12 is that an impossible entry makes the whole font unknown.

The direction is the unsafe one. Instead of returning `None`, it yields coverage claiming codepoints the font cannot address, so `IconSet.can_draw` returns `True`, the guard passes, and Pillow draws `.notdef` — the silent blank the branch exists to prevent, reached through the branch's own guard. Reachable only through a third-party provider's font, which is exactly the population these two parsers were given tests for in round 2.

Minimal change: raise `ValueError` when the run overflows, matching the two neighboring parsers.

**Declined by the owner, 2026-08-10, and the reasoning generalizes past this finding.** It takes two things that do not co-occur: a third-party provider shipping its own font, *and* that font carrying a format 6 subtable no font toolchain emits. Consistency with the neighboring parsers is the whole argument for changing it, and symmetry is not a reason to edit a shipped parser. Round 1's findings 5 and 6 were deferred on the same ground and 6 still is; what changed is that this one had been re-ranked up to should-fix on the strength of the module's stated rule, which is an argument about tidiness rather than about anything that can happen.

Note the distinction the owner drew, because it decides the rest of this round: a defect that requires a font nobody has is hypothetical, while findings 2, 3 and 6 are wrong in artifacts that exist today.

### 5. `docs/user-guide/icons-and-names.rst:104` — two exception types described as one — **should-fix** — FIXED

Root cause: "That also raises by default, so both routes into the library answer a name they cannot draw the same way" is true of the policy and false of the type. The same page shows `ValueError` at line 97 and `KeyError` in the table at line 119. A reader who takes "the same way" literally and wraps a render loop in `except ValueError` will not catch the policy path.

Minimal change: name both exceptions in that sentence. This is the same class of defect as round 2's finding 7 — a section that is correct about mechanism and misleading about what to write.

Fixed as part of finding 1's removal, since that section was mostly about the policy. It now names `ValueError` and `KeyError`, says why they differ, and tells a reader who only cares that the icon did not draw to catch both. `headless-rendering.rst:28` carried the same conflation and is fixed with it.

### Round 3's resolutions, and what the round is worth carrying forward

All six are settled: 1 and 5 fixed by removing `on_missing`, 2, 3 and 6 fixed after, 4 declined as unreachable.

**Two of the six were defects in round 2's own fixes, and both were of the same kind — an instrument whose name overstated what it measured.** Round 2 found the parity test claiming formats it never ran; the test written to close that named formats 0 and 6 and exercised only 6. Round 2 introduced `Coverage` and a test named for the representation whose only live assertion was arithmetic about itself. Neither is sloppiness in the fix — both fixes were correct — and both are the specific failure this repository keeps producing: the check gets written, the name gets written optimistically, and nothing compares the two. The remedy that worked here is the same one the placement census landed on: **make the instrument report what it did** — count the dispatch, assert the aggregate you actually quoted — rather than asserting that nothing raised.

**And one number was wrong in the finding rather than in the code.** The suggested per-style floor for finding 2 was derived from an aggregate ratio and fails on the shipped fonts. Measuring before fixing is what caught it, which is the same discipline the finding itself was about.

**Convergence.** Round 1 found seven, round 2 seven, round 3 six — but round 3's are markedly smaller: one behavior defect, three instruments, one docs sentence, one declined. The fix diff is also the first that *deleted* public surface rather than adding to it. That is the shape of a branch approaching done rather than one still growing.

### 6. `sfnt.py:17` — the definition beside the number admits a 10% wrong answer — **nit** — FIXED

Root cause: the 5,792 KB figure is glossed as "the `frozenset` this used to return plus its int objects", which is not enough to reproduce it. Measuring `getsizeof(frozenset(list_of_codepoints))` plus the ints gives 6,399.7 KB and a factor of 368×; only `frozenset(set(...))` — what the pre-change code actually built, and which CPython presizes differently — gives 5,791.7 KB and 333×.

The number is right and the definition is under-specified, in a file whose own rule is to state the definition with the number. The same sentence is in `CHANGELOG.md:25`, which ships to the GitHub Release page, and in `CLAUDE.md`, `PLAN.md` and the test docstring. Adding "built from a `set`, as the old code did" pins it.

Both readings were reproduced before writing anything down — 5,791.7 KB and 6,399.7 KB — and `git show 77a0b7b:…/sfnt.py` confirms the pre-change code accumulated into `codepoints: set[int]` and returned `frozenset(codepoints)`, so "as the old code built it" is a fact rather than a guess. Fixed in all four places plus the changelog, each naming the construction and the 6,400 KB figure the other reading gives, since a definition that does not say what the *wrong* answer looks like is hard to check against.

`CLAUDE.md`'s copy records that this paragraph has now been wrong twice for the same reason — first measuring the array object rather than the buffer, now the freeze — and draws the general rule: "state the definition" means one someone can execute, not a phrase that sounds specific.
