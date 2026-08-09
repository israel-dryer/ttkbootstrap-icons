# Changelog

All notable changes to the `tkinter-icons` base package are documented in this
file. Each icon pack keeps its own changelog under `packages/<pack>/CHANGELOG.md`.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The project was published as `ttkbootstrap-icons` through 4.0.0 and renamed to
`tkinter-icons` in 5.0.0. Entries before 5.0.0 were reconstructed from git
history after the fact and are summaries rather than contemporaneous notes.

<!-- release-notes-start -->

## [Unreleased]

### Added

- **`render_pil` takes `style`.** Same position, same meaning as the constructor's, so anything a pack can draw is reachable headlessly and the two entry points resolve a name identically. Naming a style the pack does not draw that icon in, or one the name contradicts, raises rather than returning a blank image. (#115)

### Changed

- **`PackIcon.render_pil` raises on a name the pack cannot resolve, where it used to return a transparent image.** This is a behavior change: code that rendered a list of names and tolerated blanks now needs to catch `ValueError`. It is deliberate. `render_pil` is the headless path — build steps, export scripts, test suites — which is exactly where a blank PNG is least likely to be noticed, and it produced one for a plain misspelling while the constructor raised on the same name. This is the failure mode 5.0.0's own changelog called out for the PyInstaller hooks: *"a glyph with no font renders transparent, so the application started normally and drew nothing."* (#115)

  The change was not safe to make on its own, which is why it lands with the rest and not before: while 849 real icons were unreachable by name, raising would have failed on names that were not typos at all. They resolve now, so what is left really is a bad name.

  **The icon browser is unaffected.** It is the one shipped consumer of name resolution, and it never used `render_pil`; every icon it builds already sits inside a `try`. Checked rather than assumed: all 61,153 names it lists, across every style of all sixteen packs, still resolve, and drawing them into a real window puts an icon in every cell it reaches and an error tile in none. Both are now guarded by tests, because a resolution change can degrade the browser without failing anything else — and resolving is a step short of drawing, since the grid builds the image inside the same `try` that swallows a bad name.

  **`on_missing` is unaffected in the case it was written for.** A name that reaches an icon set without being resolved against it — the base `Icon`, or `render_pil` with an explicit `icon_set` — still applies the policy, and `"transparent"` is still the default. What changed is that a pack's own resolution failures no longer route into it. That restores the scope `docs/user-guide/icons-and-names.rst` described from the start and the code did not honor; #117 deleted the sentence because it was false, and this makes it true instead.

- **The icon browser never shows the user an error.** It is an application someone runs to look at icons, so there is no circumstance in which a diagnostic belongs on their screen, and it had two ways of producing one. An icon it could not draw painted a red `Error <name>` tile in the grid and marked the preview `✕`; a glyph it cannot render is now simply absent — an empty cell, a blank preview, `—` for the codepoint. And any exception raised inside a Tk event handler reached the terminal as `Exception in Tkinter callback` plus a full stack trace, which no amount of guarding individual call sites prevents: `main` now replaces `report_callback_exception` on the root it owns, and stops anything escaping startup. Neither is reachable in a normal install; both are checked by forcing the failure. (#136)

### Fixed

- **The default style is a preference, not a gate.** A name with no style written into it used to be looked for in the pack's default style *and nowhere else*, so a name that exists only in some other style resolved nowhere. Font Awesome's brand marks are the clearest case; `accusoft` is a genuine glyph in `brands`, nothing in the name points there, and the default is `solid`, so `FontAwesomeIcon("accusoft")` raised and `render_pil("accusoft")` drew a transparent square. The default is now tried first and the pack's other styles after it, so it still settles which icon you get when a name exists several ways — which it must, because all 13,658 names that exist in more than one style would otherwise be ambiguous. (#115)

- **The two entry points look a name up the same way.** `resolve_icon_style` matched `-<style>` anywhere in a name while `resolve_icon_name` matched it only at the end, so they agreed on most names by accident of the order each pack declared its styles in. Where they disagreed the failure was silent in both directions: Bootstrap's `shield-fill-check` is a real glyph the `fill` style ships, and the constructor rejected it, while `render_pil` drew it only because Bootstrap keeps every style in one font file and the unresolved name happened to be a glyph name. Both are now views of one `BaseFontProvider.resolve_icon`, which returns the style and the glyph together, so they cannot answer differently. The name rule matches whole hyphen-separated components, never the first, longest match winning — which is what makes it independent of declaration order. 35 Bootstrap names start constructing. (#115)

  Measured against `main` by resolving every one of the 94,964 names of all sixteen packs once with no style and once against each style its own pack has — 288,418 combinations — the resolution change is purely additive: **849 names newly resolve, none stopped resolving, and not one resolved to a different glyph.** Every one of the 849 was previously unreachable by name alone: 489 in Font Awesome, 185 in Fluent, 102 in Material, 35 in Bootstrap, 28 in Devicon, 8 in Typicons, 2 in Eva. All 849 are gained in the no-style column; naming a style explicitly resolves exactly what it always did. Constructor and `render_pil` agree on all 113,399 name-and-style entries across all sixteen packs, and draw identical pixels.

## [5.0.1] — updated metadata and docs

A patch release with no executable code change. Every source edit in the eighteen distributions is a comment or a docstring; what moved is text and metadata that PyPI freezes at release time, and therefore could not be corrected without shipping a version.

Fifteen of the sixteen icon packs go to 1.1.1. `tkinter-icons-fluent-reg` is unchanged at 1.1.0.

### Fixed

- **`tkinter-icons[google-material]` advertised a `twotone` style it does not ship.** Its PyPI summary and README both listed baseline, outlined, round, sharp and twotone; the pack ships the first four. Both are frozen at release time, so the correction needed this release rather than a documentation edit. A test now checks every pack's summary and README intro against the styles its provider really has. (#111)

- **Python 3.14 is declared.** It has worked since 5.0.0 — `requires-python` has no upper bound — and CI has tested it on Linux, macOS and Windows since before that release. What was missing is the trove classifier, which is what the "Python Versions" badge reads, so the badge stopped at 3.13 and understated support. Editing the badge or the README could not change it; only a release can. (#118)

- **`_place_by_bbox`'s docstring described the measured path as overflowing the box it fits to.** It quoted a per-pack median fill of "94% to 102%", which the renderer cannot produce: `_place_by_ink` fits ink to the padded box and never enlarges past it, so 100% is the ceiling. The real figures are 72% to 95% on the `getbbox` fallback and 92% to 100% on the measured path, and they are now generated by a committed census rather than transcribed by hand.

### Changed

- **Fifteen pack pages are written from this library's side rather than upstream's.** Each opened by describing the pack as "a provider for `tkinter-icons`" — `provider` is the developer API, and nobody installing a pack ever touches one — and then repeated the upstream project's own marketing, including framing about font files that the extras model exists to hide. Each page now says what the set covers and when to reach for it. The PyPI summary line was rewritten with it, for the same reason and the same freezing problem. (#120)

- **The documentation illustrates its claims instead of asserting them.** The pages on sizing, render quality and choosing a pack now carry figures drawn at build time by the library itself, so they cannot go stale; quickstart and both integration pages carry real screenshots, which they never had. (#87)

## [5.0.0] — renamed, and rebuilt on measured ink

`ttkbootstrap-icons` is now **`tkinter-icons`**. Bootstrap icons were built directly into ttkbootstrap, so this library is no longer the way to get icons for ttkbootstrap — it is for people on raw tkinter, and for people who want an icon set other than Bootstrap. The name now says that.

Installing `ttkbootstrap-icons` still works. It becomes a forwarding shim that depends on `tkinter-icons` and re-exports everything, including submodules, so `from ttkbootstrap_icons.icon import Icon` keeps working. It warns once on import and will not be updated again.

```bash
pip install "tkinter-icons[material]"
```

```python
from tkinter_icons import MaterialIcon
```

### Summary

- **The library is now `tkinter-icons`.** `ttkbootstrap-icons` becomes a forwarding shim, so existing imports keep working. (#75)
- **Icon packs install as extras** — `tkinter-icons[material]` — rather than as distributions you name yourself. (#69)
- **Glyphs are centered on ink measured from the font** instead of on Pillow's `getbbox()`, which fixes padding and centering across every pack. (#67)
- **Icons render without a display.** `Icon.render_pil()` returns a PIL image and touches no Tk. (#67)
- **The published surface is smaller** — twenty-eight asset-building commands, the `tools` modules, and the `[all]` extra are gone. (#79)

### Added

- **Sixteen icon packs are now extras of one library.** Each pack is still its own distribution — it has to be, since each ships a font — but you no longer install them by name. `pip install "tkinter-icons[material]"` pulls in the right one, and two are named together as `tkinter-icons[material,simple]`. Asking for a pack that is not installed raises with the exact install command for it. (#69)

- **`Icon.render_pil()`, a headless entry point.** It returns a PIL image and touches no Tk, so icons can be rendered in a test suite, a build step, or any process without a display. (#67)

- **`RenderOptions`, carrying every drawing knob as one immutable value.** Size, color, padding, rotation, flip, and oversampling travel together instead of living as mutable class state on `Icon`. (#67)

- **`IconSet`, one immutable object per provider and style,** holding the font bytes, the glyph map, the ink metrics, and the default options. (#67)

- **`python -m tkinter_icons.tools.generate_metrics`, which measures and verifies glyph ink bounds.** `--all` regenerates every installed pack, `--check` verifies without writing, which is what CI runs to catch drift in the committed metrics. (#67)

### Changed

- **Glyphs are centered on measured ink, not on `font.getbbox()`.** Pillow's `getbbox()` under-reports ink on icon fonts, which left full-bleed icons with no padding at all and nudged everything else off center. Each glyph's true ink is now measured once at 512px and shipped with its pack as em-fraction bounds in `metrics.json`. A pack without metrics falls back to `getbbox`, so old packs still render. (#67)

- **The Bootstrap `y_bias` fudge was removed.** It existed to cancel the `getbbox` skew; against real ink metrics it visibly pushes glyphs low. (#67)

- **An odd size snaps up to the next even one.** `size=15` renders at 16px. Half-pixel geometry is what produced the soft LANCZOS edges at fractional display scaling. `icon.rendered_size` reports what was actually drawn, and it is part of the cache key. (#67)

- **The drawing internals are public.** `render.py` is pure PIL and imports no Tkinter; `icon.py` is the only Tk-facing layer. Subclassing `Icon` to change how something draws is no longer the only way in. (#67)

- **Entry-point discovery scans both provider groups.** A pack published against either `ttkbootstrap_icons.providers` or `tkinter_icons.providers` is found, so upgrading the base package with old packs installed does not silently lose every icon set. (#75)

### Fixed

- **Image caches are scoped to the Tk interpreter and dropped when its root is destroyed.** A `PhotoImage` belongs to the interpreter that created it, so a process-wide cache handed out dead handles as soon as a root was replaced — which is what happened in test suites and in any app that tears a window down and builds another. (#68)

- **A stateful icon releases its widget bindings.** Icons bound to widget state kept the widget, its images, and its theme-change binding alive after the widget was gone. (#68)

- **The pack asset runner no longer stops on a pack with nothing to build.** `bs` has no `tools/generate_assets` — its assets were vendored, not generated — and the runner treated that as a failure rather than a skip. (#77)

- **`render_pil` works on a pack's icon class without a warm-up.** It read `Icon._icon_set_current`, a `ClassVar` shared by every subclass, so `MaterialIcon.render_pil("home")` drew a Material icon only if something had already constructed one — and raised `RuntimeError` in a fresh process, which is exactly how a test suite or a build step would call it. A pack now names its own provider through `Icon.provider_class`, and `render_pil` resolves friendly names the way the constructor does. The base `Icon` has no pack of its own, so it raises in a fresh process and otherwise falls back to whichever set was loaded last. (#86)

- **Every pack's icon class accepts `options`.** `RenderOptions` was public API and the documented way to change how an icon draws, reachable only through `Icon.render_pil` or the base `Icon` — never through the sixteen classes anyone actually constructs. It is keyword-only, so it cannot be confused with `style`. (#86)

- **PyInstaller finds the bundled hooks by itself.** The package shipped hooks but never registered them, so PyInstaller had no reason to look in `_pyinstaller/` and every frozen application needed an explicit `hookspath`. A `pyinstaller40` entry point now points at `get_hook_dirs`, which is what the documentation had always described. Two packs also had no hook file at all — `bs` and `fluent-reg` — so a frozen application using Bootstrap or Fluent (Regular) icons shipped without their fonts. All three failures were silent by construction: a glyph with no font renders transparent, so the application started normally and drew nothing. (#84)

### Removed

- **Only the icon browser is published as a command.** The base package installed `tkicons-build-all` and `tkicons-metrics`, and each pack installed its own `tkicons-<pack>-build` and `tkicons-<pack>-quick` — twenty-eight commands across fourteen packs. They regenerate assets and metrics into a source tree, so they do nothing useful from an installed wheel, and `generate_metrics` would have written into site-packages. Maintainers run them with `python -m`. `tkinter-icons` remains. (#79)

- **The `tools` modules no longer ship in any wheel.** Auto-discovery had been sweeping `tkinter_icons_<pack>.tools` into all sixteen pack wheels, and `tkinter_icons.tooling` into the base — upstream-scraping asset generators that no user can run and that nothing imports at runtime. `tooling` moved under `tkinter_icons.tools` with the rest. (#79)

- **The `[all]` extra.** The sixteen sets serve disjoint purposes — brand marks, developer logos, fantasy glyphs, weather symbols — so no application draws from all of them, and installing every one cost about 22 MB of fonts and JSON on disk to get fifteen icon sets nobody opens. That is the bundling extras exist to avoid. Name the one or two you need. (#79)

- **`BaseFontProvider`, `ProviderRegistry`, and `load_external_providers` are no longer re-exported from the package root.** They define an icon set rather than use one, and sat beside `MaterialIcon` as though the two were the same kind of thing. Import them from `tkinter_icons.providers` and `tkinter_icons.registry` — which is how all sixteen packs already do. (#79)

## [4.0.0] — the base package no longer ships icons

### Changed

- **Bootstrap icons moved out of the base package** into their own
  `ttkbootstrap-icons-bs` distribution, making the base package fully
  provider-agnostic. This is breaking: an install that relied on Bootstrap
  being built in needs the pack added.

- **Asking for a provider that is not installed says how to install it,**
  rather than failing on an empty registry.

### Added

- **`ttkbootstrap-icons-fluent-reg`,** packaging the regular weight of Fluent
  System Icons separately from the filled set.

### Fixed

- **Package data and license references** that resolved on a working tree but
  not in a built wheel.

## [3.3.0] — sharper icons at small sizes

### Changed

- **Icons are oversampled and downscaled,** which is what fixed alignment and
  softness at small sizes.

- **Package licenses use the PEP 621 form** (`license = "MIT"` with
  `license-files`) instead of the deprecated classifier and table.

### Fixed

- **A missing icon names itself in the error,** quoted, instead of being
  reported as an unspecified lookup failure.

- **Multi-font providers ship all their glyph maps.** The package-data glob
  matched only `glyphmap.json`, so a provider with a file per style shipped one
  of them. (#61)

## [3.2.0] — cache keys

### Changed

- **The image cache key is a hash** rather than a concatenation of subclass
  names, which could collide.

## [3.1.2] — Python 3.10

### Fixed

- **`typing-extensions` is a dependency,** so Python 3.10 installs work.

## [3.1.1] — theme changes

### Fixed

- **Stateful icons follow a theme change** instead of keeping the colors of the
  theme they were created under. (#54)

## [3.1.0] — stateful icons

### Added

- **`StatefulIconMixin`,** which maps an icon to a widget's ttk state so it
  recolors on hover, press, and disable along with the widget.

### Fixed

- **Multi-state ttk foreground maps parse correctly,** including compound states
  such as `pressed !disabled`.

- **A widget with no existing image map** no longer raises when an icon is
  attached to it.

- **The fallback state color** is the normal foreground rather than black.

## [3.0.1] — provider asset fixes

### Fixed

- **Invalid icon references** in several providers. (#46)

- **Font Awesome's generated glyph map** covers the brands and regular styles,
  not just solid. (#48)

## [3.0.0] — one provider API

### Changed

- **Every provider was rewritten against a single API.** Names, styles, and
  display names resolve the same way everywhere, whether the style is passed as
  an argument or carried in the name. (#31)

- **Font scaling and padding are standard parameters** across all providers.

### Added

- **Typicons** and **Meteocons** packs. (#12, #19)

- **Documentation site and per-provider metadata,** with a visual test per pack.
  (#32, #34)

## [2.1.0] — more packs, typed styles

### Added

- **Eva Icons**, **RPG Awesome**, and **Devicon** packs. (#10, #15, #17)

- **Type hints for style arguments.** (#21)

### Fixed

- **Fluent style naming.** (#23)

## [2.0.0] — packs became separate distributions

### Changed

- **The project was restructured so each icon set is its own installable
  package,** discovered through entry points, instead of everything living in
  one distribution.

### Added

- **Font Awesome**, **Material Design Icons**, **Remix**, **Ionicons**,
  **Fluent System Icons**, **Simple Icons**, **Weather Icons**, **Lucide**, and
  **Google Material Icons** packs. (#1–#9)

- **Multi-style icon support**, for fonts shipping more than one weight.

- **PyInstaller hooks** for the pack subpackages.

### Fixed

- **Icons are no longer clipped** at their bounding box.

## [1.0.0] — initial release

Font-based Bootstrap icons for Tkinter and ttkbootstrap, rendered to
Tk-compatible images.