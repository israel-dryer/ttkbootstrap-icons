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

- **An icon can now be handed over as bytes, for toolkits that take an encoded image rather than pixels.** `Icon.render_data()` is `render_pil()` with the image already encoded — same arguments, same name resolution, same failures, PNG bytes instead of a Pillow image — and `Icon.to_data()` is the instance form, standing to it exactly as `to_pil()` stands to `render_pil()`. Neither needs a Tk root, so an interface that is declared before its window exists can carry real icons. Tk's own `PhotoImage(data=...)` is where the name comes from, and toolkits layered on Tk inherit the parameter. (#144)

  **The bytes are raw PNG, not base64.** Tk's PNG reader takes binary data directly, so encoding it would cost about a third more — 1,064 bytes against 796 for a 24 px icon — to buy portability to Tk 8.5 alone, which cannot read PNG at all. PNG rather than GIF because every glyph here is antialiased against transparency, which GIF cannot carry.

  Nothing is cached, matching `render_pil`. Encoding is cheap beside rendering, and the expensive part — loading and sizing the font — is already cached.

- **A glyph map that points at a codepoint its own font does not carry is now a reported failure rather than a blank square.** Two things have to be true for an icon to draw — the name has to be in the icon set's glyph map, and that glyph map's codepoint has to be in the set's font — and only the first was ever checked. A name that failed the second resolved, looked up, and handed Pillow a codepoint the font had never had, which draws `.notdef`; in these fonts `.notdef` is empty, so the result was a fully transparent image with no exception and no warning — **not even for a caller who had explicitly asked to be told about names that could not be drawn**, because from the glyph map's point of view nothing was missing. It is now the same kind of failure as a name the glyph map does not have, and both raise. (#140)

  The two are reported differently, because a user who mistyped and a user who hit a broken pack need different answers. A name the map never had still says so; a name the map advertises at a codepoint the font lacks names the codepoint and says the fault is in the pack's data rather than in the name you asked for.

  **The font's coverage is read without adding a dependency.** Pillow cannot report which codepoints a font carries — it draws `.notdef` and says nothing — and `fontTools` is not worth a third runtime dependency for one question, so `tkinter_icons.sfnt` parses the `cmap` table directly. It is checked against `fontTools` on every font the project ships, which between them exercise subtable formats 4 and 12, the BMP, and the supplementary private-use area that Material Design Icons lives in. Formats 0 and 6 are also read, for fonts this project does not ship; no shipped font reaches them, since the ones that carry such subtables carry them on the Macintosh platform, which is excluded before the format is dispatched on. Those two are covered against constructed subtables instead, which is a weaker check than the parity test and is worth saying so rather than counting them among what `fontTools` verifies. A font is parsed once and cached, so asking before every glyph costs one parse per icon set — under 8 ms for the largest pack.

  **Coverage is kept as ranges rather than as a set of codepoints**, which is the difference between 17.4 KB and 5,792 KB across the thirty-one styles this project ships — 333×. Both figures need their definition to mean anything: 17.4 KB is `Coverage.nbytes`, the bounds buffers alone, and 5,792 KB is the `frozenset` this used to return plus its int objects, built from a `set` as the old code built it. Freezing a *list* of the same codepoints presizes differently and gives 6,400 KB, which is a 10% disagreement with the number printed beside it. A font's coverage is overwhelmingly contiguous: 73,990 codepoints fall into 2,231 ranges, so the set form was paying an integer object per codepoint to hold what a pair of bounds already says. The largest single coverage is Fluent's `filled` at 741 KB as a set and 16 bytes as ranges; the most fragmented is Font Awesome's `solid`, 709 ranges and 5,672 bytes against 182 KB. Membership becomes a `bisect` rather than a hash lookup, 0.18 µs against 0.04 µs over 54,993 lookups, which is nothing beside the render it guards.

  **An unreadable font means unknown, never empty.** Every failure path in that parser returns `None` rather than an empty set, and callers then draw the glyph exactly as they did before. An empty set would claim the font contains no codepoints at all, which would blank or raise on every icon in the pack the moment an unusual font appeared: a guard that cannot read a font must not be the thing that breaks it.

- **`render_pil` takes `style`.** Same position, same meaning as the constructor's, so anything a pack can draw is reachable headlessly and the two entry points resolve a name identically. Naming a style the pack does not draw that icon in, or one the name contradicts, raises rather than returning a blank image. (#115)

- **Tk is no longer required to import the library or to render.** The drawing core is pure Pillow and never had a Tkinter import, but `__init__.py` imports `icon.py` and `icon.py` imported `tkinter` at module scope — so `import tkinter_icons` raised `ImportError` on any machine without Tk, and the renderer behind it was unreachable. On Linux `tkinter` is a distribution package (`python3-tk`) rather than part of a pip install, which makes a slim container or a CI image exactly where this was hit. The Tk imports moved to their point of use, so `import tkinter_icons`, `render_glyph` and `Icon.render_pil` all work with no `tkinter` installed at all. (#91)

  Three sites, not one. `PIL.ImageTk` does `import tkinter` itself, so guarding `tkinter` in `icon.py` while still importing `PhotoImage` at module scope would have changed nothing — the third is `from tkinter.ttk import Style, Widget` in `stateful_icon_mixin.py`, where both names are type hints apart from a single `Style()` construction.

  The imports stay at module scope and tolerate `ImportError` rather than hiding behind `TYPE_CHECKING`, which was the first attempt and broke the documentation. `from __future__ import annotations` makes every hint a string, and `typing.get_type_hints` — which Sphinx autodoc calls — resolves those against the module's globals, so names that exist only for a type checker raise `NameError` there. That failure is per module rather than per name, so it took the ttk aliases and every other annotated name down with `PhotoImage`. Importing eagerly wherever Tk exists keeps every annotation resolvable and leaves the degraded path to machines that have no Tk to describe.

  Nothing about the widget path changed except when it fails. Reaching `.image` on a machine without Tk raises `ImportError` naming `tkinter` instead of the import failing at the top of the program, and a test asserts that rather than leaving it to be discovered as an `AttributeError`.

### Changed

- **`PackIcon.render_pil` raises on a name the pack cannot resolve, where it used to return a transparent image.** This is a behavior change: code that rendered a list of names and tolerated blanks now needs to catch `ValueError`. It is deliberate. `render_pil` is the headless path — build steps, export scripts, test suites — which is exactly where a blank PNG is least likely to be noticed, and it produced one for a plain misspelling while the constructor raised on the same name. This is the failure mode 5.0.0's own changelog called out for the PyInstaller hooks: *"a glyph with no font renders transparent, so the application started normally and drew nothing."* (#115)

  The change was not safe to make on its own, which is why it lands with the rest and not before: while 849 real icons were unreachable by name, raising would have failed on names that were not typos at all. They resolve now, so what is left really is a bad name.

  **The icon browser is unaffected.** It is the one shipped consumer of name resolution, and it never used `render_pil`; every icon it builds already sits inside a `try`. Checked rather than assumed: all 61,153 names it lists, across every style of all sixteen packs, still resolve, and drawing them into a real window puts an icon in every cell it reaches and an error tile in none. Both are now guarded by tests, because a resolution change can degrade the browser without failing anything else — and resolving is a step short of drawing, since the grid builds the image inside the same `try` that swallows a bad name.

  **A name handed straight to an icon set is the other door, and it is closed too** — see the `on_missing` removal below.

- **`Icon.on_missing` is removed, and a name that cannot be drawn now always raises.** The attribute is gone rather than re-defaulted. The remaining failures are `ValueError` for a name a pack cannot resolve and `KeyError` for a name that reaches an icon set with no glyph for it; neither returns an image.

  **Delete the line if you set it.** `Icon.on_missing = "transparent"` still assigns without complaint — Python does not stop you creating a class attribute nobody reads — and it now has no effect at all, so code carrying it will raise where it used to draw a blank. There is no deprecation period: the setting's whole purpose was to keep a failure quiet, and warning about it would have meant leaving the quiet behavior in place for another release to warn from.

  **`MissingPolicy` is removed with it.** The type alias — `Literal["transparent", "warn", "raise"]`, exported from `tkinter_icons.icon` in both 5.0.0 and 5.0.1 — described the values of the attribute that is gone, so `from tkinter_icons.icon import MissingPolicy` now raises `ImportError`. Anything importing it was annotating a variable holding the policy, which is the same line the paragraph above says to delete.

  It was never a designed feature. 4.0.x returned a transparent square for any name its glyph map did not have — no option, no warning — and 5.0.0's renderer rework kept that behavior as the default while adding `"warn"` and `"raise"` as ways out of it. So the policy existed to escape the old bug rather than to offer a choice anyone had asked for, and its default carried the bug forward into two releases.

  The case it was justified by does not exist. `"warn"` and `"transparent"` were for bulk renderers that must not stop at the first bad name — but this project's own bulk renderers, the icon browser and the placement census over 178,584 renders and the docs extensions that draw every pack's previews, never set it and cannot reach it: they iterate names that come out of the glyph map, so a name the map lacks is not a case they have. A caller who genuinely needs to continue can write `try`/`except`, which is one line and ends with the list of names that failed rather than a directory of blank PNGs.

  What the default did produce is a transparent square that is indistinguishable from an icon that rendered. That is not a hypothetical cost: it is how the glyph-map bug above went unnoticed across two releases, and how the icon browser came to draw blank tiles nobody could explain.

  **The `"none"` sentinel is not a missing name and no longer behaves like one.** It means "deliberately no icon here", and it worked by falling through to the missing-name path and relying on that path returning a blank — so it already raised for anyone who had set `on_missing="raise"`, and it would have raised for everyone once the blank stopped being available. It is answered before the lookup now rather than by failing one, so it still draws a blank of the right size.

- **The icon browser never shows the user an error.** It is an application someone runs to look at icons, so there is no circumstance in which a diagnostic belongs on their screen, and it had two ways of producing one. An icon it could not draw painted a red `Error <name>` tile in the grid and marked the preview `✕`; a glyph it cannot render is now simply absent — an empty cell, a blank preview, `—` for the codepoint. And any exception raised inside a Tk event handler reached the terminal as `Exception in Tkinter callback` plus a full stack trace, which no amount of guarding individual call sites prevents: `main` now replaces `report_callback_exception` on the root it owns, and stops anything escaping startup. Neither is reachable in a normal install; both are checked by forcing the failure. (#136)

- **An icon set reports what it can draw, rather than what its glyph map claims.** `len(icon_set)`, `name in icon_set` and `IconSet.glyph(name)` now all mean the same thing — that the set can actually produce an image — where the first two read the raw glyph map and the third is what the renderer consults. `IconSet.glyphs` is still the advertised map for tooling that wants to compare the two; every shipped pack has them equal, and `tests/test_font_coverage.py` asserts it. (#140)

  The check lives in `IconSet.glyph` rather than at the call sites, which is why it reaches the widget path and not just `render_pil`. Duplicating it would have set up the next version of #115 — the same name answered two different ways by two entry points is the defect that keeps recurring here, and the browser drawing blank tiles was this bug's most visible symptom.

### Fixed

- **An explicitly-passed icon set that can draw nothing is no longer silently discarded.** `render_pil` selected its set with `icon_set or cls._icon_set_current`, and an `IconSet` is sized, so an empty one is falsy — the caller's set was dropped and whichever set loaded last was used in its place, producing an image from the wrong pack rather than the blank the caller asked for. Reachable before this release only with a genuinely empty glyph map; reachable much more easily once a set's length became the count of what it can draw. It selects on `is None` now. (#140)

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