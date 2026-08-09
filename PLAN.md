# PLAN — Tk is not required to render (#91)

Branch `fix/tk-not-required-for-render-pil`, off `main`. Review scope is `git diff main..fix/tk-not-required-for-render-pil`.

Written for the reviewing session. It states what the code is meant to do and what must hold, so a finding can be checked against intent rather than guessed at.

The two previous sections here — #115's resolution plan and #136's browser plan — are gone rather than archived. Both shipped, and their findings are recorded where they belong: in `CHANGELOG.md`, in the tests that guard them, and in `CLAUDE.md`. A plan kept past its merge is a second copy of the truth, which is how the placement numbers drifted through three review rounds.

---

## What this is supposed to do

The drawing core is pure Pillow and has never had a Tkinter import. But `__init__.py` imports `icon.py`, and `icon.py` imported `tkinter` at module scope, so `import tkinter_icons` raised `ImportError` on any machine without Tk — putting Tk in front of a renderer that never touches it.

This is not theoretical. On Linux `tkinter` is a distribution package (`python3-tk`) rather than part of a pip install, so the environments the headless guide names — a slim CI image, `python:3.12-slim`, a thumbnail worker — are exactly the ones that lack it.

**Three import sites, not one.** Finding only the first is the trap:

| site | what | why it counts |
|---|---|---|
| `icon.py` | `import tkinter` | the one the issue names |
| `icon.py` | `from PIL.ImageTk import PhotoImage` | **`PIL.ImageTk` does `import tkinter` itself**, so fixing the first alone changes nothing |
| `stateful_icon_mixin.py` | `from tkinter.ttk import Style, Widget` | `icon.py` imports this module, so it is on the same path |

---

## The shape of the fix, and why it is not `TYPE_CHECKING`

Each import stays at module scope inside `try: ... except ImportError:`, and every *runtime* use re-imports at the point of use.

**`TYPE_CHECKING` was the first attempt and it broke the documentation.** `from __future__ import annotations` makes every hint a string, and `typing.get_type_hints` — which Sphinx autodoc calls — resolves those strings against the module's globals. A name imported only under `TYPE_CHECKING` is not there at runtime, so resolution raises `NameError`. That failure is **per module, not per name**: hiding `PhotoImage` also cost `MissingPolicy`, `StateMapMode`, `IconStateSpec` and `Widget` their cross-references, and `sphinx -W` went from clean to six errors.

Importing eagerly wherever Tk exists keeps every annotation resolvable, so machines with Tk — the docs build, CI, any desktop — behave exactly as before. Only a genuinely Tk-less machine takes the degraded path, and nothing introspects annotations there.

The `except ImportError` is narrow on purpose. It tolerates Tk being absent and nothing else; a `PIL` broken some other way still raises, from the point-of-use import, where the message names what actually failed.

---

## Invariants

- **`import tkinter_icons` works with no `tkinter` installed**, and so do `render_glyph`, `Icon.render_pil`, and saving the result to a PNG.
- **Nothing imports `tkinter` as a side effect.** Each test asserts `"tkinter" not in sys.modules` after the fact, not merely that no exception was raised.
- **The widget path still fails, and fails legibly.** Reaching `.image` without Tk raises `ImportError` naming `tkinter` — not `AttributeError`, not `NameError` from a deferred import site, and not a `TypeError` from calling the `Any` placeholder.
- **Constructing an icon is still free of Tk.** `PackIcon("house", size=32)` renders nothing until `.image`, which is what makes the point above reachable at all.
- **`sphinx -W --keep-going -n` stays clean**, which is the check that caught the `TYPE_CHECKING` attempt.

---

## How it is tested

`tests/test_headless_without_tkinter.py`, in a **subprocess**. Blocking `tkinter` in-process would mean unimporting `tkinter`, `PIL.ImageTk` and every `tkinter_icons` module and letting them reload under the block, in a suite whose Tk tests are already order-sensitive. A child interpreter is a truer simulation and cannot break a later test.

The blocker matches `tkinter` exactly or as a dotted prefix, **never as a string prefix**. `tkinter_icons` starts with `tkinter`, so `startswith("tkinter")` would block the package under test and "pass" by failing for the wrong reason — the same shape as the `.git`/`.github` bug this project has already been bitten by. `test_the_blocker_does_not_block_the_library` is that floor, and the blocker also proves itself by importing `tkinter` and requiring the failure before any assertion runs.

Verified against the old code both ways: collapsing the tolerant import back to a hard `import tkinter` fails these tests with the exact `ImportError` from the issue.

---

## Known-weak spots — worth a reviewer's attention

- `PhotoImage = Any` and `Style = Any` are placeholders that exist only so annotations resolve. Nothing should ever *call* them — the point-of-use imports shadow them — but nothing enforces that beyond the tests, and calling `Any(...)` gives a poor message.
- `tkinter = None` on the fallback path means an annotation like `tkinter.Misc` would raise `AttributeError` rather than `NameError` if anything resolved hints on a Tk-less machine. Nothing does, and there is no test for it because there is no caller to write one against.
- The subprocess tests cost about a second in total. If the suite grows more of them, they should share one child rather than one each.
- `browser.py` still imports Tk at module scope, correctly — it is the console script. Nothing checks that it stays off `__init__.py`'s import path, though `test_importing_the_package_does_not_need_tkinter` would fail if it ever landed there.
