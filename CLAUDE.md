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
.venv/Scripts/python.exe -m pip install -e packages/tkinter-icons
.venv/Scripts/python.exe -m pip install --no-deps \
    -e packages/tkinter-icons-bs -e packages/tkinter-icons-fa \
    -e packages/ttkbootstrap-icons-shim
.venv/Scripts/python.exe -m pytest -q          # 237 passed, 1 skipped
```

**Everything but the base package needs `--no-deps`** in a working tree. Each
pack and the shim require `tkinter-icons>=5.0.0`, and setuptools-scm now really
does read git — so until a `v5.0.0` tag exists the local base package reports
`4.0.1.dev<n>+g<sha>`, which is *below* the floor, and pip goes to PyPI looking
for one that satisfies it. Their only other dependency is Pillow, which the base
install brings in.

`SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TKINTER_ICONS=5.0.0` is the alternative if
you want resolution to work normally.

Before #70 this only bit the shim, because setuptools-scm was misconfigured and
silently returned `fallback_version` — which happened to be 5.0.0 — for every
build. That setting is gone as of #78; the pretend-version variable above is now
the only way to build this package without git. See "Deliberate decisions".

Only `bs` and `fa` are installed here. **The other 14 packs have no generated
metrics yet** — that's one `python -m tkinter_icons.tools.generate_metrics --all` in an
environment with all
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
| #70 changelog + release automation | merged (#78) |
| #71 Sphinx docs + reframing | **not started — the only issue left** |
| #79 trim the published surface | in review on `refactor/trim-published-surface` — reviewed, fixes committed, not yet merged to `5.0` |

Also merged: #77, fixing three cloud-review findings plus a pre-existing
pack-asset-runner bug.

**Every one of those issues is still OPEN on GitHub, and that is correct.** A PR
merged into `5.0` does not close the issue it names — GitHub only honours
`Closes #n` on a merge into the default branch. They all close at once when the
single `5.0` → `main` PR lands. Do not close them by hand; an issue closed early
loses its link to the merge that actually shipped it.

`5.0` is code-complete. #71 is all that is left before release — plus the two
blockers below, which are work rather than decisions.

**Two things block a `--strict` release**, both surfaced by the preflight:

1. **Fourteen packs have no generated metrics.** One `python -m
   tkinter_icons.tools.generate_metrics --all` in
   an environment with every pack installed, then commit. Note the preflight now
   also checks that each generated file is *reachable by that pack's
   package-data globs* — thirteen packs declare `metrics*.json` at the module
   root and `bs` relies on `assets/*.json`, so if the generator writes anywhere
   else, `--strict` fails rather than shipping a wheel without metrics.
2. **Three packs ship no upstream license file** — `bs`, `meteocons`,
   `typicons`. Needs a human decision on the exact license text; see gotchas.
   `KNOWN_LICENSE_GAPS` in `verify_packages.py` must end up empty.

Release mechanics live in `RELEASE.md`, and are real now: tag-driven, Trusted
Publishing, no token anywhere. The tag scheme is `v<version>` for the base
package and `<distribution>-v<version>` for the other seventeen.

---

## What #71 picks up

The docs today are **MkDocs Material, not Sphinx**: `mkdocs.yml` at the root, 42
markdown pages under `docs/`, API pages through **mkdocstrings**, and provider
pages written at build time by `scripts/gen_providers_docs.py` via the
**gen-files** plugin. #71 moves all of it to Sphinx, for consistency with
`ttkbootstrap` and `bootstack`.

**The old docs are not being ported — they are being replaced.** Decided
deliberately: the rename is the moment to write what this library actually needs
rather than carry the structure of a set of pages that predates the extras
model. Delete `mkdocs.yml`, `scripts/gen_providers_docs.py`, and the 42 pages
under `docs/`; nothing there is a source for the new set.

That call was not aesthetic. The old pages are **pre-#69 in substance**, not just
in tone: `pip install tkinter-icons tkinter-icons-bs` and
`from tkinter_icons_bs import BootstrapIcon` appear across `index.md`,
`getting-started.md`, `stateful-icons.md`, `icon-browser.md`, and `README.md` —
a bare install line and the raw distribution names, both of which the library now
contradicts. Only `docs/providers/bootstrap.md` used the single import root, so
the old set disagreed with itself.

The settled structure, 14 pages:

> **Home** → **Getting started** (install · quickstart · choosing a pack ·
> migrating from ttkbootstrap-icons) → **User guide** (icons & names · sizing and
> render quality · stateful icons · headless rendering · icon browser ·
> packaging) → **Integrations** (tkinter & ttk · ttkbootstrap) → **Icon packs**
> (one page) → **API reference** → **Contributing** → **About** (release notes ·
> license)

Decisions behind it, each of which cost a discussion:

- **One packs page, not sixteen.** Every pack's icon class is an `Icon` subclass
  whose whole surface is `__init__(name, size, color, style)`; seven packs do not
  even take `style`. What differs between packs is *data* — class name, extra,
  styles, upstream version, glyph count — which is a table. Sixteen pages of
  60-line boilerplate is why the install idiom went stale in all of them at once.
  The same reasoning applies to the API reference: sixteen identical autodoc
  pages earn nothing.

- **No "bring your own font" guide.** The mechanism cannot be made private —
  sixteen wheels subclass `BaseFontProvider` across a distribution boundary — but
  building an icon font is a separate toolchain, and documenting it as a
  supported path commits to a public API for a rare case. It belongs in
  Contributing, as how a *pack* is built, not in the user guide as an invitation.

- **Split consumer from developer.** `tkinter_icons` root is the consumer API and
  is what the user guide and API reference cover; `tkinter_icons.providers`,
  `.registry`, `.packs`, and the tools are the developer API and live in
  Contributing. #79 made the code agree with this.

- **The user guide is framework-neutral; framework idioms live in Integrations.**
  A 5.1 PySimpleGUI 6 integration (lazy factory functions, since PSG does not
  guarantee a window up front) then costs one page instead of a pass over every
  example. It fits the existing model: `Icon.__init__` never touches Tk and
  rendering defers to first `.image` access, so describe an `Icon` as a
  description that renders on demand — not as a rendered image.

- **Use `.. versionadded::` from the start,** so 5.1 additions are marked rather
  than silently appearing.

- **Release notes include the root `CHANGELOG.md` only,** via a myst `include`
  with `:start-after: <!-- release-notes-start -->` — the marker `release_notes.py`
  already slices on, so one marker serves both. Needs
  `suppress_warnings = ["myst.header"]`. The seventeen other changelogs stay
  release artifacts, linked from the packs table; they are near-identical to each
  other and tell the same story sixteen times.

- **Docs dependencies go in `docs/requirements.txt`,** matching bootstack, and
  not into an extra of the base package. (The `[all]` reachability rule that used
  to force this is gone with #79, but the family pattern stands.)

- **There is no docs workflow.** `.github/workflows/` holds `ci.yml` and
  `release.yml` only; the `gh-pages` branch came from a manual `mkdocs
  gh-deploy`. A build-and-deploy job is part of #71. The site URL is
  `israel-dryer.github.io/tkinter-icons/`; the old one is dead on purpose.

- **The one packs page must land at `packs.html` — the code already links
  there.** #79 pointed `PACKS_DOC_URL` (`packs.py:29`) at
  `{DOCS_URL}/packs.html` and used it to replace `REPO_URL` in the two places a
  user with *no pack installed* meets first: `no_packs_message()`, raised from
  `Icon.__init__`, and the browser's welcome screen. It 404s until #71 ships, so
  a Sphinx structure that names that page anything else leaves a dead link as
  the only pointer to the catalogue, for exactly the users least able to find it
  another way. Reverting to `REPO_URL` in the meantime was considered and
  declined — it is a second thing to remember to undo, and a silent revert if
  forgotten. Noted on #71. A preflight assertion that the path exists in the
  built docs would close it for good.

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
measured once at 512px by `generate_metrics` and shipped as em-fraction bounds in
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
- **There is no `[all]` extra, and it must not come back.** The sixteen sets
  serve disjoint purposes — brand marks, developer logos, fantasy glyphs,
  weather symbols — so no application draws from all of them; installing every
  one costs ~17 MB to get fifteen icon sets nobody opens, which is the bundling
  extras exist to avoid. Users needing two name two: `tkinter-icons[a,b]`.
  Enforced twice: `test_there_is_no_all_extra`, and an error in
  `check_extras_cover_every_pack`. Pack-to-extra coverage is now checked against
  the pack directories rather than through `[all]`, which is a better check —
  it catches a pack with no extra whether or not anything else references it.
- **`tkinter-icons` is the only console script, and `tools` ships in no wheel.**
  The base had `tkicons-build-all` and `tkicons-metrics`; each of fourteen packs
  had `tkicons-<pack>-build` and `-quick` — twenty-eight commands on users'
  PATH. All of them regenerate assets into a *source tree*, so they do nothing
  from an installed wheel, and `generate_metrics` resolves its output through
  `files(provider.package)` — under a normal install that is site-packages.
  Removing the scripts and shipping `tools` are one change, not two: excluding
  the module while leaving the entry points would install commands that crash on
  import. `tkinter_icons.tooling` moved under `tools/` for the same reason —
  it is developer-only by its own docstring, and a module cannot be dropped from
  a wheel while it sits at the package root.
- **`exclude-package-data` is what keeps `tools` out of all seventeen wheels —
  `packages.find` alone does not.** Every package sets
  `include-package-data = true`, and that makes setuptools treat files it learns
  about from *outside* the package list as package data, past any
  `packages.find` exclude. Two different sources feed it, which is why this
  looks like two unrelated bugs:
  - The **packs** get it from `.egg-info/SOURCES.txt`, which legitimately lists
    the `tools` files because the sdist includes them — as it should; an sdist
    is meant to be complete. The release workflow editable-installs every pack
    before `python -m build`, so that file is present exactly when it matters.
  - The **base** gets it from setuptools-scm's git file-finder, which sweeps in
    every tracked file under `src/tkinter_icons/`.

  **Verify by building and listing the wheel, never by reading the config**, and
  build a pack that is *installed*. A pack with no `.egg-info` produces a clean
  wheel with a broken config and reports a false pass — that mistake was made
  once already, and it would have shipped `tools` in fourteen wheels.

  **Both stanzas are required, and `check_tools_are_not_shipped` now enforces
  both.** They stop different things: `packages.find` stops `tools` being
  *declared* a package, `exclude-package-data` stops its files arriving as
  *data*. Either alone ships the directory, so the check reads both and names
  which one is missing — it originally read only `exclude-package-data`, which
  meant a seventeenth pack copied from a sibling with the `packages.find` stanza
  dropped would ship `tools` with a green preflight.
- **The root exports the consumer API only, and the shim absorbs the
  difference.** `BaseFontProvider`, `ProviderRegistry`, and
  `load_external_providers` define an icon set rather than use one, and are
  reached from `tkinter_icons.providers` / `.registry` — which is how all
  sixteen packs already import them.

  `ProviderRegistry` and `load_external_providers` *did* ship at the root in
  4.0.0 — its `__all__` was exactly `Icon`, `get_hook_dirs`, `ProviderRegistry`,
  `load_external_providers` — so this is a real removal. **Submodule aliasing
  does not cover it**, and believing otherwise is the trap: the aliases rescue
  `from ttkbootstrap_icons.registry import ProviderRegistry`, but 4.0.0 users
  wrote `from ttkbootstrap_icons import ProviderRegistry`, which the shim
  resolves through `getattr(tkinter_icons, name)` and which therefore began
  raising an `AttributeError` naming a module the caller never imported.

  The shim now carries the two relocated names itself, in `_RELOCATED`, tried
  only after `getattr(_target, name)` raises `AttributeError` — so a pack's
  `ImportError` still propagates untouched. `TestShimForwardsTheWholeOldSurface`
  pins all four 4.0.0 names. **Anything else leaving the root has to be added
  there too**; the base package's root is free to shrink precisely because the
  shim is the compatibility layer, not the module paths.
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
  `sys.modules` so `from ttkbootstrap_icons.icon import Icon` still works, and
  carries the root names `tkinter_icons` dropped (above). Pinned `>=5.0.0` with
  no ceiling, so it never needs another release.

  **Its migration warning is an install instruction, and nothing downstream
  checks it.** pip does not fail on an unknown extra — it prints `does not
  provide the extra` and installs the base package, which has no glyphs — so a
  stale extra in that text walks the user into the state the rest of the same
  message is warning about. It named `[all]` until #79's review caught it.
  `TestShimMigrationMessageIsInstallable` parses the extras back out of the
  warning source and checks each against `KNOWN_PACKS`; keep that true of any
  install line added to it.
- **`registry.py` scans both entry-point groups.** Drop the legacy group and
  anyone upgrading with an old pack installed silently loses every icon set.
- **The base package's setuptools-scm config is load-bearing in two ways.**
  `root = "../.."` points at the repository — without it setuptools-scm looked
  for a repo at `packages/tkinter-icons`, found none, and silently used
  `fallback_version`, so the tag was decorative and a `v5.0.1` tag would have
  shipped a wheel numbered 5.0.0. `fallback_version` has since been **removed**:
  with `root` correct it is unreachable from CI and from a release (both check
  out at `fetch-depth: 0`) and unnecessary for an sdist (the version comes from
  PKG-INFO), so all it could still do is silently number a git-less source build
  5.0.0 forever. Without it that build fails loudly instead, and
  `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TKINTER_ICONS` is the honest escape hatch.
  And `describe_command` matches only
  `v[0-9]*`, because the default tag regex reads `tkinter-icons-fa-v1.1.0` as
  version 1.1.0 — and pack tags are pushed *first* in a release, so without it
  the base build takes a pack's number.

- **A pack's provider name is not guaranteed to be its entry-point key.**
  `registry.py` registers under `provider_instance.name`, and the entry point
  `fa` registers `fontawesome`. That is the *only* pack where the two differ —
  every other key matches its provider name, including `gmi` (which registers
  `gmi`, not `google-material`) and the `bs` directory (whose key is already
  `bootstrap`). One divergence in sixteen is what makes reading the key look
  safe. Anything passing a name to `generate_metrics` has to import the provider
  to get it — reading the key gives an argument the CLI rejects.

- **The old docs URL is dead and that was accepted.** GitHub redirects repo URLs
  but not project Pages. `israel-dryer.github.io/ttkbootstrap-icons/` 404s;
  a custom domain was considered and declined.

---

## Conventions

- **Branches:** `refactor/*`, `fix/*`, `feat/*` off `5.0`. PRs target `5.0`.
  Stack dependent PRs on each other; GitHub retargets on merge.
- **Every PR names an issue** on the 5.0.0 milestone with `Closes #n` — which
  takes effect only when `5.0` reaches `main`, so the issues stay open in the
  meantime. Merge with a merge commit (`gh pr merge <n> --merge --delete-branch`),
  matching #72–#78.
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

**`metrics.json` stays committed — decided.** The release workflow re-measures
the released pack and compares against what is committed, so the drift that
committed generated data invites is caught at the only moment it matters. Build
time generation was the alternative; it was declined because it makes Pillow a
build requirement for every sdist.

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
  the pack asset runner correctly skips it.

---

## Related projects

`ttkbootstrap` and `bootstack` (both at `D:\Development\`) have Bootstrap icons
built in and use Sphinx for docs. #71 moves this project to Sphinx for family
consistency; bootstack's `docs/conf.py` is the reference, and its
`release-notes.rst` shows the pattern for including `CHANGELOG.md` via myst.
