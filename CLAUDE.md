# tkinter-icons — Claude Handoff

## Project overview

Font-based icons for Tkinter and ttkbootstrap. The library renders glyphs from
icon fonts to Tk-compatible images; the icon sets themselves ship as separate
distributions installed via extras.

**The identity shifted, and this matters for every docs decision.** This started
as `ttkbootstrap-icons`, intended to be folded into ttkbootstrap or bootstack.
Instead, Bootstrap icons were built *directly* into both of those. So this
project's audience is now **people on raw tkinter, or people who want an icon set
other than Bootstrap** — not "the way to get icons for ttkbootstrap." Renamed to
`tkinter-icons` in 5.0.0 to match.

**Positioning:** one library, sixteen installable icon packs. The packs are
separate PyPI distributions only because each ships its own font; users should
never have to think about that.

```
pip install "tkinter-icons[material]"
from tkinter_icons import MaterialIcon
```

---

## Environment

**Working directory is `D:\Development\ttkbootstrap-icons`** — the *local folder
name is still the old one*. The GitHub repo is `israel-dryer/tkinter-icons` and
every package inside is renamed; only the containing directory lags. Don't
"fix" it mid-session without updating the remote checkout path.

`.venv` works: Python 3.13.7, Tk 8.6. Install editable before running anything:

```bash
.venv/Scripts/python.exe -m pip install -e packages/tkinter-icons \
    -e packages/tkinter-icons-bs -e packages/tkinter-icons-fa
.venv/Scripts/python.exe -m pip install --no-deps -e packages/ttkbootstrap-icons-shim
.venv/Scripts/python.exe -m pytest -q          # 226 passing
```

The shim **needs `--no-deps`** in a working tree: it requires `tkinter-icons>=5.0.0`,
and setuptools-scm derives the local version from git tags. Until a `v5.0.0` tag
exists, the local version comes from `fallback_version` and pip can't resolve it
from an index.

Only `bs` and `fa` are installed here. **The other 14 packs have no generated
metrics yet** — that's one `tkicons-metrics --all` in an environment with all
packs installed, and it must happen before release.

---

## Current state

| Branch | What |
|---|---|
| `main` | 4.0.0, untouched, still publishable |
| `5.0` | integration branch — all 5.0 work lands here, then one PR to `main` |

Milestone **5.0.0** (issues #67–#71, #75):

| Issue | State |
|---|---|
| #67 renderer rework | merged (#72) |
| #68 stateful icon lifecycle | merged (#73) |
| #69 packs as extras | merged (#74) |
| #75 rename to tkinter-icons | merged (#76) |
| #70 changelog + release automation | **not started** |
| #71 Sphinx docs + reframing | **not started** |

Also merged: #77, fixing three cloud-review findings plus a pre-existing
`tkicons-build-all` bug.

`5.0` is code-complete. Everything left is release tooling and docs.

---

## Architecture

The drawing internals are **public on purpose** — the old version buried
everything behind mutable class state on `Icon`.

| Module | Role |
|---|---|
| `render.py` | Drawing core. Pure PIL, **no Tkinter** — runs without a display. `RenderOptions` carries all the knobs. |
| `iconset.py` | One immutable `IconSet` per (provider, style): font bytes, glyphs, metrics, options. |
| `icon.py` | Tk-facing layer only. `Icon.render_pil()` is the headless entry point. |
| `packs.py` | The pack catalogue — single source of truth for every install message and the lazy import root. |
| `providers.py` | `BaseFontProvider`, glyphmap/metrics loading. |
| `registry.py` | Entry-point discovery. Scans **both** provider groups. |

**Centering works from measured ink.** `font.getbbox()` under-reports icon-font
glyph ink, which left full-bleed icons with no padding. Each glyph's true ink is
measured once at 512px by `tkicons-metrics` and shipped as em-fraction bounds in
each pack's `metrics.json`. Packs without metrics fall back to `getbbox`.

**Caches are scoped to the Tk interpreter** and dropped on root `<Destroy>`. A
`PhotoImage` belongs to the interpreter that created it; a global cache hands out
dead handles once a root is replaced.

---

## Deliberate decisions — do not silently undo

Each of these looks like a defect in isolation. They aren't.

- **The base install ships no glyphs.** `pip install tkinter-icons` gets a
  renderer that draws nothing until a pack is added. Chosen over re-bundling
  Bootstrap (which 4.0.0 deliberately removed) and over a default pack. Docs must
  never show a bare install — every install line carries an extra.
- **Odd sizes snap up to even.** `size=15` renders 16px. Removes half-pixel
  LANCZOS blur at fractional display scaling. `icon.rendered_size` reports the
  real size, and it is part of the cache key.
- **Bootstrap's `y_bias` was removed.** It compensated for the `getbbox` skew;
  with real ink metrics it visibly pushes glyphs low. Visually verified.
- **Both class-name spellings are exported.** `MaterialIcon` and `MatIcon` both
  resolve. The `A as A` lines in the `TYPE_CHECKING` block look redundant but are
  required — PEP 484 binds only the name after `as`.
- **No per-pack shims.** Download data decided this: base ~9k/month, `lucide`
  ~38/month. Nobody imports pack modules directly.
- **One base shim, published once.** `ttkbootstrap-icons` 5.0.0 forwards to
  `tkinter-icons`. Uses **`FutureWarning`, not `DeprecationWarning`** — Python
  hides the latter unless it fires in `__main__`. Aliases submodules into
  `sys.modules` so `from ttkbootstrap_icons.icon import Icon` still works. Pinned
  `>=5.0.0` with no ceiling, so it never needs another release.
- **`registry.py` scans both entry-point groups.** Drop the legacy group and
  anyone upgrading with an old pack installed silently loses every icon set.
- **The old docs URL is dead and that was accepted.** GitHub redirects repo URLs
  but not project Pages. `israel-dryer.github.io/ttkbootstrap-icons/` 404s;
  a custom domain was considered and declined.

---

## Conventions

- **Branches:** `refactor/*`, `fix/*`, `feat/*` off `5.0`. PRs target `5.0`.
  Stack dependent PRs on each other; GitHub retargets on merge.
- **Every PR closes an issue** on the 5.0.0 milestone.
- **Changelog:** root `CHANGELOG.md` for the base package, plus one per pack.
  Format follows bootstack: `## [<version>] — <descriptive title>`, which drives
  the GitHub Release title and body via `release_notes.py`.
  See `D:\Development\bootstack\.github\scripts\release_notes.py`.
- **Versions:** base `5.0.0`; all sixteen packs `1.1.0`, requiring
  `tkinter-icons>=5.0.0`.

**Release publish order is load-bearing** — the base extras pin `>=1.1.0`, so:

1. the 16 packs at 1.1.0
2. `tkinter-icons` 5.0.0
3. `ttkbootstrap-icons` 5.0.0 (the shim) — last, so it never points at a version
   that doesn't exist yet

---

## Open decisions

**Should `metrics.json` stay committed?** ~24,000 lines of generated coordinate
data live in source. They're fully reproducible from font + glyphmap, which is
why `tkicons-metrics --check` exists — to catch the drift committed generated
data invites. They also blew past the code-review size limit. Generating at build
time removes the whole category, at the cost of slower builds and Pillow being
required to build from sdist. **Decide before #70's release workflow hardens
around the current choice.**

**Thread safety is undesigned.** `_font_cache`, `_icon_sets`, and `Icon._caches`
are plain dicts with read-modify-write patterns. Tkinter is effectively
single-threaded, but `render_pil` is documented as usable without Tk, which
invites worker-pool use. Needs a decision even if the answer is "document as not
thread-safe."

---

## Known gotchas

- **Three packs ship no upstream license file** — `bs`, `meteocons`, `typicons` —
  while the other thirteen do. `bs` redistributes Bootstrap Icons. This is an
  unresolved compliance gap; the exact upstream license and copyright line needs
  a human decision, so it was flagged rather than guessed. `verify_packages.py`
  (#70) should enforce it.
- **The shim's directory is `packages/ttkbootstrap-icons-shim/` but it builds the
  distribution `ttkbootstrap-icons`.** Deliberate — the plain name was taken by
  the directory being renamed. Any tag-to-directory resolution in the release
  workflow must handle it explicitly.
- **Tk 8.6 cannot reliably create a second interpreter in one process.** It
  intermittently fails reloading ttk themes. Tests that need a fresh root guard
  with `pytest.skip` on `TclError`; which root trips it depends on test ordering.
  This is a Tk limitation, not a library bug — don't "fix" it.
- **`.egg-info` directories break `git mv`** on package renames. Remove them
  first: `find packages -name "*.egg-info" -type d -exec rm -rf {} +`.
- **Eleven pack `icon.py` files carry a UTF-8 BOM.** Harmless to Python, but
  `read_text(encoding="utf-8")` chokes — use `utf-8-sig` when scripting over
  source files.
- **`--check` your assumptions about pack layout.** Packs differ: `bs` keeps
  assets in an `assets/` subpackage, others at the module root. `bs` has no
  `tools/generate_assets` at all (its assets were vendored, not generated), so
  `tkicons-build-all` correctly skips it.

---

## Related projects

`ttkbootstrap` and `bootstack` (both at `D:\Development\`) have Bootstrap icons
built in and use Sphinx for docs. #71 moves this project to Sphinx for family
consistency; bootstack's `docs/conf.py` is the reference, and its
`release-notes.rst` shows the pattern for including `CHANGELOG.md` via myst.
