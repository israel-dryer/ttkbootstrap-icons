# Changelog

All notable changes to the `tkinter-icons` base package are documented in this
file. Each icon pack keeps its own changelog under `packages/<pack>/CHANGELOG.md`.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The project was published as `ttkbootstrap-icons` through 4.0.0 and renamed to
`tkinter-icons` in 5.0.0. Entries before 5.0.0 were reconstructed from git
history after the fact and are summaries rather than contemporaneous notes.

<!-- release-notes-start -->

## [5.1.0] — icons on PySimpleGUI, and no more silent blanks

### Removed

- **`Icon.on_missing` is removed, and a name that cannot be drawn now always raises.** The attribute is gone rather than re-defaulted. A name a pack cannot resolve raises `ValueError`; a name that reaches an icon set with no glyph for it raises `KeyError`. Neither returns an image.

  **Delete the line if you set it.** `Icon.on_missing = "transparent"` still assigns without complaint — Python does not stop you creating a class attribute nobody reads — and it now has no effect at all, so code carrying it will raise where it used to draw a blank. There is no deprecation period: the setting's whole purpose was to keep a failure quiet, and warning about it would have meant leaving the quiet behavior in place for another release to warn from.

  **`MissingPolicy` is removed with it**, so `from tkinter_icons.icon import MissingPolicy` now raises `ImportError`. The type alias described the values of the attribute that is gone, and anything importing it was annotating a variable holding the policy — which is the same line the paragraph above says to delete.

  It was never a designed feature. 4.0.x returned a transparent square for any name its glyph map did not have — no option, no warning — and 5.0.0's renderer rework kept that behavior as the default while adding `"warn"` and `"raise"` as ways out of it. What the default produced was a transparent square indistinguishable from an icon that rendered, which is how the glyph-map fault described under Added went unnoticed across two releases. A caller who genuinely needs to continue past a bad name can write `try`/`except`, which ends with the list of names that failed rather than a directory of blank PNGs.

  **The `"none"` sentinel is not a missing name and no longer behaves like one.** It means "deliberately no icon here", and it used to work by falling through to the missing-name path and relying on that path returning a blank — so it already raised for anyone who had set `on_missing="raise"`. It is answered before the lookup now, so it still draws a blank of the right size.

### Changed

- **`PackIcon.render_pil` raises on a name the pack cannot resolve, where it used to return a transparent image.** This is a behavior change: code that rendered a list of names and tolerated blanks now needs to catch `ValueError`. `render_pil` is the headless path — build steps, export scripts, test suites — which is exactly where a blank PNG is least likely to be noticed, and it produced one for a plain misspelling while the constructor raised on the same name. (#115)

- **An icon set reports what it can draw, rather than what its glyph map claims.** `len(icon_set)`, `name in icon_set` and `IconSet.glyph(name)` now all mean the same thing — that the set can actually produce an image — where the first two used to read the raw glyph map. `IconSet.glyphs` is still the advertised map for tooling that wants to compare the two; every shipped pack has them equal, and `tests/test_font_coverage.py` asserts it. (#140)

- **The icon browser never shows the user an error.** It is an application someone runs to look at icons, so there is no circumstance in which a diagnostic belongs on their screen, and it had two ways of producing one. An icon it could not draw painted a red `Error <name>` tile in the grid and marked the preview `✕`; a glyph it cannot render is now simply absent — an empty cell, a blank preview, `—` for the codepoint. And any exception raised inside a Tk event handler reached the terminal as `Exception in Tkinter callback` plus a full stack trace, which no amount of guarding individual call sites prevents: `main` now replaces `report_callback_exception` on the root it owns, and stops anything escaping startup. Neither is reachable in a normal install; both are checked by forcing the failure. (#136)

### Added

- **Icons on [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI), through a new `tkinter_icons.extensions` namespace.** `from tkinter_icons.extensions.psg import IconButton` gives a button whose icon sits beside its text and follows what the button is doing; everything else PySimpleGUI draws an image on — `sg.Image`, `sg.Tab`, the window icon, icon-only buttons — takes `Icon.to_data()` bytes with no bridge at all. Built and tested against PySimpleGUI 6.3, the LGPL-3.0 version 6 released in 2026. **PySimpleGUI is not a dependency and nothing from it is redistributed**: it stays a separate installable, and asking for `IconButton` without it raises an `ImportError` naming the install command. There is deliberately no `[psg]` extra, because in this project an extra means an icon pack. (#112)

  **States are named for the interaction — `hover`, `pressed`, `disabled` — because the two toolkits disagree about the word "active".** In `ttk` it means hover. On a `tk.Button` it means whatever the windowing system decides: Windows and macOS set it only while the mouse button is already down, so there it means *pressed*, while X11 sets it on entry, so there the one state covers hover and press together. Each path translates. What holds everywhere is that `hover` is not separately reachable on a `tk.Button`, so asking for it there warns rather than silently doing nothing.

  **An icon left at its default color takes the button's, and one given a color keeps it.** Leaving it alone is the usual case and means icons match the theme without being told to; giving it a color pins the resting state while hover, press and disable still follow the button, so choosing a color does not opt out of reacting.

  The icon is applied on the first idle after its widget exists rather than when the window is mapped, so it is in place before the window appears instead of resizing the buttons under the reader's eyes.

  `update()` carries the additions — a new `icon`, a new `compound`, new `reactive_states` — and follows two more without being asked, because they move the ground under the icon: `update(disabled=...)`, since a `tk.Button` has no disabled *image*, and `update(button_color=...)`, which changes the colors the icon was tinted from. **`sg.theme()` is not among them, and not because it is ignored** — it makes no runtime change to follow. A theme selects the colors the *next* window is built with and leaves an existing one alone, so an icon resolved when its button was built stays exactly as current as the button is.

- **An icon can now be handed over as bytes, for toolkits that take an encoded image rather than pixels.** `Icon.render_data()` is `render_pil()` with the image already encoded — same arguments, same name resolution, same failures, PNG bytes instead of a Pillow image — and `Icon.to_data()` is the instance form, standing to it exactly as `to_pil()` stands to `render_pil()`. Neither needs a Tk root, so an interface that is declared before its window exists can carry real icons. Tk's own `PhotoImage(data=...)` is where the name comes from, and toolkits layered on Tk inherit the parameter. (#144)

  **The bytes are raw PNG, not base64.** Tk's PNG reader takes binary data directly, so encoding it would cost about a third more to buy portability to Tk 8.5 alone, which cannot read PNG at all. PNG rather than GIF because every glyph here is antialiased against transparency, which GIF cannot carry. Nothing is cached, matching `render_pil` — encoding is cheap beside rendering, and the expensive part, loading and sizing the font, already is.

- **A glyph map that points at a codepoint its own font does not carry is now a reported failure rather than a blank square.** Two things have to be true for an icon to draw — the name has to be in the icon set's glyph map, and that glyph map's codepoint has to be in the set's font — and only the first was ever checked. A name that failed the second resolved, looked up, and handed Pillow a codepoint the font had never had, which draws `.notdef`; in these fonts `.notdef` is empty, so the result was a fully transparent image with no exception and no warning. It is now the same kind of failure as a name the glyph map does not have, and both raise. (#140)

  The two are reported differently, because a user who mistyped and a user who hit a broken pack need different answers. A name the map never had still says so; a name the map advertises at a codepoint the font lacks names the codepoint and says the fault is in the pack's data rather than in the name you asked for.

  **121 glyph-map entries were in that state and are gone from the shipped data** — 119 in `tkinter-icons-gmi` and 2 in `tkinter-icons-mat` — so neither pack advertises a name its font cannot draw. Both packs' generators now intersect what they assemble with the font's real coverage, so a regeneration cannot reintroduce it.

  **A font's coverage is read without adding a dependency.** Pillow cannot report which codepoints a font carries — it draws `.notdef` and says nothing — and `fontTools` is not worth a third runtime dependency for one question, so `tkinter_icons.sfnt` parses the `cmap` table directly, and is checked against `fontTools` on every font this project ships. A font is parsed once and cached, so asking before every glyph costs one parse per icon set: under 8 ms for the largest pack. **An unreadable font means unknown, never empty** — every failure path returns no answer rather than an empty coverage, and callers then draw the glyph exactly as they did before, because a guard that cannot read a font must not be the thing that breaks it. `sfnt.py`'s docstring carries the representation details.

- **`render_pil` takes `style`.** Same position, same meaning as the constructor's, so anything a pack can draw is reachable headlessly and the two entry points resolve a name identically. Naming a style the pack does not draw that icon in, or one the name contradicts, raises rather than returning a blank image. (#115)

- **Tk is no longer required to import the library or to render.** The drawing core is pure Pillow and never had a Tkinter import, but `__init__.py` imports `icon.py` and `icon.py` imported `tkinter` at module scope — so `import tkinter_icons` raised `ImportError` on any machine without Tk, and the renderer behind it was unreachable. On Linux `tkinter` is a distribution package (`python3-tk`) rather than part of a pip install, which makes a slim container or a CI image exactly where this was hit. The Tk imports moved to their point of use, so `import tkinter_icons`, `render_glyph` and `Icon.render_pil` all work with no `tkinter` installed at all. (#91)

  Nothing about the widget path changed except when it fails. Reaching `.image` on a machine without Tk now raises `ImportError` naming `tkinter`, instead of the import failing at the top of the program.

### Fixed

- **A per-state icon on a multi-style pack is drawn from the style the icon was built with.** `Icon.map` renders one image per state, and it used to get them from a rebuild — `type(icon)(name, size, color)` — a constructor call with nowhere to carry the `style` or the `options` the icon already had. So a `FontAwesomeIcon("heart", style="regular")` mapped onto a button kept its outline glyph at rest and switched to the *solid* one the moment the pointer touched it, which reads as the wrong icon rather than as a wrong color. State images now render through the same path `.image` uses, at the icon's own options, and pick the set per name — so the style is kept without breaking a `statespec` that deliberately reaches another style, which is how a Font Awesome brand mark sits beside a solid icon.

- **`Icon.map` works on the ttk themes Windows ships as its own defaults.** A ttk style hands back whatever it was configured with, and `vista`, `winnative` and `xpnative` configure symbolic system colors — a button's foreground reads back as `SystemWindowText`. Tk resolves those; Pillow rejects them with `unknown color specifier`, and `map` skips any state it cannot render — including the resting fallback — so a mapped button came out with no reactive states at all and an untinted icon, on three of the seven themes Windows offers and on the one it selects by default. Colors read off a style are now translated through the widget, which is the only thing that can resolve a system color. A color the *caller* wrote is still passed through untouched, since Pillow accepts specifiers Tk does not.

- **An explicitly-passed icon set that can draw nothing is no longer silently discarded.** `render_pil` selected its set with `icon_set or cls._icon_set_current`, and an `IconSet` is sized, so an empty one is falsy — the caller's set was dropped and whichever set loaded last was used in its place, producing an image from the wrong pack rather than the blank the caller asked for. It selects on `is None` now. (#140)

- **The default style is a preference, not a gate.** A name with no style written into it used to be looked for in the pack's default style *and nowhere else*, so a name that exists only in some other style resolved nowhere. Font Awesome's brand marks are the clearest case: `accusoft` is a genuine glyph in `brands`, nothing in the name points there, and the default is `solid`, so `FontAwesomeIcon("accusoft")` raised and `render_pil("accusoft")` drew a transparent square. The default is now tried first and the pack's other styles after it, so it still settles which icon you get when a name exists several ways — which it must, because all 13,620 names that exist in more than one style would otherwise be ambiguous. (#115)

- **The two entry points look a name up the same way.** `resolve_icon_style` matched `-<style>` anywhere in a name while `resolve_icon_name` matched it only at the end, so they agreed on most names by accident of the order each pack declared its styles in. Where they disagreed the failure was silent in both directions: Bootstrap's `shield-fill-check` is a real glyph the `fill` style ships, and the constructor rejected it, while `render_pil` drew it only because Bootstrap keeps every style in one font file and the unresolved name happened to be a glyph name. Both are now views of one `BaseFontProvider.resolve_icon`, which returns the style and the glyph together, so they cannot answer differently. The name rule matches whole hyphen-separated components, never the first longest match winning — which is what makes it independent of declaration order. (#115)

  Measured by resolving every one of the 94,841 names of all sixteen packs once with no style and once against each style its own pack has — 287,811 combinations — the resolution change is purely additive: **849 names newly resolve, none stopped resolving, and not one resolved to a different glyph.** Every one of the 849 was previously unreachable by name alone: 489 in Font Awesome, 185 in Fluent, 102 in Material, 35 in Bootstrap, 28 in Devicon, 8 in Typicons, 2 in Eva. All 849 are gained in the no-style column; naming a style explicitly resolves exactly what it always did. Constructor and `render_pil` agree on all 113,157 name-and-style entries across all sixteen packs, and draw identical pixels.

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