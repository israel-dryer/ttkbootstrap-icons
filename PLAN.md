# PLAN — name resolution (#115)

Branch `feat/render-pil-style`, PR #135. Review scope for round 1 is
`git diff 3ee00f1..feat/render-pil-style`.

Written for the reviewing session. It states what the code is meant to do and
what must hold, so that a finding can be checked against intent rather than
guessed at.

---

## What this is supposed to do

A pack's icon class and `Icon.render_pil` are two doors onto one library. A name
must mean the same thing at both, and every icon a pack ships must be reachable
by name.

Three things stood in the way, all in `BaseFontProvider`:

1. `render_pil` took no `style`, so a name reachable through
   `PackIcon(name, style=...)` had no headless spelling.
2. The default style **gated** resolution. A name with no style written into it
   was looked for in the default style and nowhere else, so a name existing only
   in another style resolved nowhere. 849 real icons were in that position.
3. `resolve_icon_style` and `resolve_icon_name` read a style out of a name by
   different rules — substring-anywhere versus suffix-only. They agreed on most
   names by accident of each pack's style declaration order.

The intended end state: one resolution function, three ordered rules, used
everywhere.

---

## The rules, in order

Implemented by `BaseFontProvider.candidate_styles`.

1. **An explicit `style` is the only candidate.** Asking for one and getting
   another would make the argument decorative.
2. **A style written into the name is the only candidate.** `"house-fill"` is a
   request, not a hint.
3. **Otherwise: the default style first, then every other style.**

Name parsing is `infer_style_from_name`: a style must match whole
hyphen-separated components, never starting at component 0, longest match wins.

| rule detail | the pack that forces it |
|---|---|
| whole components | Fluent's `filled` is not Bootstrap's `fill` |
| never the first component | Remix has a `line` style *and* a `line-chart` glyph, which is a chart |
| longest match wins | Devicon has both `plain` and `plain-wordmark` |
| mid-name matches count | Bootstrap ships `shield-fill-check` in the `fill` style |

---

## Invariants

These are the things a change here must not break. Each is asserted by a test;
where a number is quoted it was measured against `3ee00f1` (the merge base).

- **No successful resolution changes.** Over all 94,964 names of all sixteen
  packs, once with no style and once against each style its own pack has
  (288,418 combinations): 849 newly resolve, 0 stop resolving, 0 resolve to a
  *different* glyph. `TestTheDefaultStyleStoppedBeingAGate` pins the per-pack
  breakdown, so the figure cannot drift out of the changelog again.
- **The two entry points agree.** Constructor and `render_pil` resolve all
  113,399 name-and-style entries identically and draw identical pixels.
- **Every name a pack lists is reachable**, including from the browser, whose
  names are the lookup's *values* rather than its keys.
- **`resolve_icon_style` and `resolve_icon_name` cannot disagree.** They are
  views of `resolve_icon`, which returns the style and glyph together. This is
  structural: it is not enough for the two rules to match.
- **`"none"` is a sentinel, not a name.** It means "deliberately no icon", is
  passed through unresolved by both entry points, and renders transparent.
- **The default style cannot be removed.** All 13,658 names that exist in more
  than one style write no style into the name, so with nothing to prefer each
  becomes ambiguous. Removing it breaks 13,640 names that work today.
- **Every icon a docs example names is one its pack ships.** Added in review,
  after the block introducing `style=` on `render_pil` was found to call
  `FontAwesomeIcon.render_pil("house", style="regular")` — a name that exists
  only in `solid`, so the example for the feature this branch adds raised for
  anyone who copied it. `tests/test_docs_examples.py` parses the `code-block`
  bodies with `ast` and resolves every call whose name and style are string
  literals: 140 of them today, across every page. Examples that fail *on
  purpose* are listed in `DELIBERATE_FAILURES` and asserted to keep raising,
  and an exemption naming an example nobody shows any more is itself a failure.

---

## Behavior changes (deliberate)

- **`PackIcon.render_pil` raises `ValueError`** on a name the pack cannot
  resolve, where it returned a transparent image. Callers tolerating blanks must
  catch it. Sequenced *after* the resolution fixes on purpose: while 849 real
  icons were unreachable, raising would have failed on names that were not
  typos.
- **`on_missing` no longer sees pack resolution failures.** It still governs a
  name that reaches an icon set without being resolved against it — the base
  `Icon`, or `render_pil` with an explicit `icon_set` — and still defaults to
  `"transparent"`. Its documented scope ("the set's data is inconsistent",
  not "you made a typo") is now true of the code; #117 had deleted that sentence
  because it was not.
- **An explicit `style` is never swallowed.** A style the pack does not draw
  that icon in, or one the name contradicts, raises. Dropping it would draw the
  wrong style rather than nothing, since the icon set follows the style.

---

## Structure notes

- `resolve_icon` is the single resolution path. `resolve_icon_style` and
  `resolve_icon_name` project one element each out of it. `render_pil` calls
  `resolve_icon` once so the set and the glyph cannot come from two readings.
- `_lookup_within_style` holds the name spellings accepted within one style: as
  written, with the style appended, lowercased, and with a trailing style
  suffix stripped.
- `resolve_icon_style` swallows `ValueError` and falls back to the default. It
  is a non-raising accessor; callers use it to pick a set to apply `on_missing`
  against.
- The `"none"` sentinel computes its style inline. Routing it through
  `resolve_icon_style` recurses, because that delegates back to `resolve_icon`.
- The sixteen pack `__init__` methods were **not** modified. They call
  `resolve_icon_style` then `resolve_icon_name`, which are now consistent by
  construction.

---

## Known-weak spots — worth a reviewer's attention

- `candidate_styles` assumes `default_style` is a member of `style_list`.
  `BaseFontProvider.__init__` enforces that, but the dedup in the last line
  would silently produce a wrong candidate order if it ever were not.
- ~~The "Style X is not valid" error names `candidates[0]`, which is the default
  when several styles were searched.~~ Fixed in review: it accused the default
  of being invalid while listing it under "Available". One candidate means the
  caller named it or wrote it into the name and is still quoted; several means
  no style of the pack has a lookup at all, which is now what it says.
- `resolve_icon_style` returning the default on failure means a caller cannot
  distinguish "resolved to default" from "did not resolve". Only `render_pil`'s
  fallback path relies on this.
- `_lookup_within_style` strips a trailing `-{style}` suffix. The old code
  stripped only when the style had been *inferred* from the name. These
  coincide today; whether they must is not proven.
