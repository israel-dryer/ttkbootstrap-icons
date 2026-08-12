# PLAN — an icon as PNG bytes (#144)

Branch `feat/icon-to-data`, off `main`. The reviewing session's scope is `git diff main..feat/icon-to-data`.

Written for the session that does the work and the session that reviews it. It states what the code is meant to do and what must hold, so a finding can be checked against intent rather than guessed at.

The previous section here — #140's plan for the glyph-map/font mismatch — is gone rather than archived. It shipped in #141, and its findings live where they belong: in `CHANGELOG.md`, in `tests/test_font_coverage.py`, and in `CLAUDE.md`. A plan kept past its merge is a second copy of the truth, which is how the placement numbers drifted through three review rounds. `REVIEW.md` was reset with it, for the same reason.

---

## The gap

An icon can only reach a widget as a Tk `PhotoImage`, so it can only reach a widget that takes one. `render_pil` has produced the image without Tk since #139, so the missing piece is an encode step and nothing more.

The consumer that motivated it is #112: PySimpleGUI declares its whole interface before a window exists, and several of its elements take an encoded image rather than a widget image. This must land first so that work consumes it instead of carrying a private copy of four lines.

## What was built

Two methods on `Icon`, mirroring the pair already there so the naming stays predictable:

| new | existing it mirrors | returns |
|---|---|---|
| `Icon.render_data(...)` classmethod | `render_pil` | `bytes` |
| `Icon.to_data()` instance | `to_pil` | `bytes` |

`render_data` delegates to `render_pil` and encodes the result. It adds no resolution logic, no new failure, and no new argument — the signature is `render_pil`'s exactly. That is the point: two entry points that answer the same question two different ways is the defect shape behind #115, #140 and the `on_missing` removal, and the cheapest way not to repeat it is to have only one implementation of the question.

`data` is not borrowed vocabulary. It is the parameter name in `tk.PhotoImage(data=...)`, which is where every toolkit layered on Tk inherits it from. Naming for what consumes it is the rule `to_pil` already follows.

## What must hold

- **The bytes decode to exactly what `render_pil` drew.** The encode is lossless or the two entry points disagree, which is the whole failure this design is shaped to avoid.
- **Raw PNG, not base64.** Tk reads binary PNG data directly. Base64 costs about a third more (1,064 B against 796 B at 24 px) and buys portability only to Tk 8.5, which cannot read PNG at all.
- **PNG, not GIF.** Every glyph is antialiased against transparency; GIF carries one transparent index and would fringe every icon.
- **Failures are `render_pil`'s, unchanged.** `ValueError` for a name a pack cannot resolve, `KeyError` for one that reaches a set with no drawable glyph, `RuntimeError` with no set at all. `NO_ICON` still encodes a blank rather than raising, because it is the one blank anybody asks for.
- **No Tk.** Nothing on this path may import or require `tkinter`.
- **Size follows `render_pil`**, including even-snapping: `size=15` encodes a 16×16 PNG.

## Decisions

**Nothing is cached, and the issue proposed otherwise.** #144 called an `lru_cache` "the obvious answer". Consistency won instead: `render_pil` does not cache, so a caching sibling would make the two behave differently under repetition for no stated reason. The expensive part is already cached — `render.py` keeps an `OrderedDict` of loaded fonts — and encoding is cheap beside rendering. A caller looping over one icon should hold the result, as with any other render.

**No `format=` parameter.** PNG is what Tk reads, and a format knob invites GIF, which cannot carry the alpha this library depends on. Adding it later is compatible; removing it would not be.

## Testing

`TestRenderData` in `tests/test_icon.py`. Every assertion re-opens the bytes through Pillow and looks at them, because a name that draws nothing still encodes to a perfectly valid, perfectly transparent PNG — so asserting that bytes came back, or that nothing raised, would pass on a blank. That is the trap `CLAUDE.md` records twice.

`getcolors`, not `getdata`: the latter is deprecated for removal in Pillow 14 and adding it would put a new warning into a clean suite.

## Known-weak spots, stated rather than hidden

- **The lossless-round-trip test is the only thing pinning PNG as the format.** Nothing asserts the bytes are *not* some other format that also happens to round-trip; the magic-number check is the closest thing and is a check on the header, not on the choice.
- **No test covers a very large icon.** Encoding cost is assumed to scale with pixels and has not been measured at, say, 512 px, where a PSG layout building many icons at once might notice.
- **The docs claim base64 is a third larger.** That is one measurement of one 24 px glyph, and the ratio is fixed by the encoding rather than by the image, so the *ratio* generalizes while the byte counts do not. Both are quoted with the size they were measured at.
