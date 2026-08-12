# PLAN — icons on PySimpleGUI (#112)

Branch `feat/psg-extension`, off `main`. The reviewing session's scope is `git diff main..feat/psg-extension`.

Written for the session that does the work and the session that reviews it. It states what the code is meant to do and what must hold, so a finding can be checked against intent rather than guessed at.

The previous section here — #144's plan — is gone rather than archived. It shipped in #145. A plan kept past its merge is a second copy of the truth.

---

## Amendments

Written after the work and after CI, before the review. Corrections and late decisions only, so a finding can be measured against what the code was actually meant to do rather than against the first draft of this file.

**`tk`'s `active` state is not one behavior, and this plan first assumed it was.** `button.tcl` defines `tk::ButtonEnter` three times, once per windowing system. **win32 and aqua** set `-state active` only while button 1 is already down, so the state changes on press. **x11** sets it on entry outright — *"on unix the state is active just with mouse-over"*, in Tk's own comment — so there one state covers hover *and* press. The implementation was always correct, because it reads `-state` rather than inferring from the pointer; the first two versions of `test_the_tk_icon_follows_the_widgets_own_state` were not, and both failed on Linux against working code. What holds everywhere is that **`hover` is not separately reachable on `tk`** — on win32 because no hover state exists, on x11 because hover is indistinguishable from press. The docstring, the warning and the docs page all said "no hover state at all" until CI proved otherwise.

**`compound` stays an explicit user setting; it is deliberately not inferred.** An icon-only button wants `"none"`, and the default `"left"` reserves a text slot that is not free — an empty-text ttk button asks for **96 px** against **26**. Inferring it from the absence of button text was implemented and then reverted on the owner's call, 2026-08-12: `tk` and `ttk` accept different values for image-only (`ttk` takes `"image"`, `tk` does not), so the choice belongs to the caller. It is stated as a caveat on the docs page, and the demo and screenshot pass it.

**The docs teach `Icon.to_data()`, not the `render_data()` classmethod.** Owner's call, and the reason is consistency rather than taste: the same page already constructs icons for `IconButton(icon=...)`, so a classmethod for images would put two idioms on one page. `render_data` appears once, as a tip.

**A test that builds a PySimpleGUI window has to tear down more than the window.** PySimpleGUI keeps a hidden master root alive after `Window.close()`, along with `tkinter._default_root`. Leaving them breaks any later test that controls when a root exists — `TestTkLifecycle` failed exactly that way, and only when this file ran first.

---

## The gap

PySimpleGUI is declarative: constructing `sg.Button` creates no Tk widget, so `element.Widget` stays `None` until `sg.Window` builds the layout. An icon cannot be applied in a constructor, and cannot even be *rendered* there, because a `PhotoImage` needs an interpreter that does not exist yet.

## Settled before designing, as the handoff instructed

**PySimpleGUI 6.3 is LGPLv3** — v6 is an open-source relaunch, no runtime license gate. Nothing from it is redistributed; it stays a separate installable. That was the open question on whether the integration was appropriate at all, and the answer removed it.

**`sg.theme()` does not reach a live window.** Measured: after `sg.theme("LightGrey1")` a window built under `DarkBlue3` keeps both its `tk` foreground and its ttk style foreground, and PySimpleGUI exposes no method to re-theme one. **`update(button_color=...)` does** change live colors, on both paths. So "theme aware" means following per-element color changes, not global theme calls — following those would make the icon more reactive than the button under it.

## What was built

`tkinter_icons/extensions/__init__.py`, which imports nothing, and `extensions/psg.py`, which holds `IconButton` and `PySimpleGUINotInstalled`.

## What must hold

- **The base package never gains a load-time dependency on a GUI toolkit.** `import tkinter_icons` must not import PySimpleGUI, and neither must `import tkinter_icons.extensions`.
- **The icon is on the button before the window is first painted.** Not merely "eventually correct" — the failure this replaces was visible.
- **The window does not resize after it is shown.**
- **A missing dependency explains itself**, as an `ImportError`, naming the install command and the path that needs no install at all.
- **`hover` is unreachable on `tk` and says so.** Silently dropping it is the failure mode this project keeps writing guards against.
- **The tk icon reflects the widget's own `-state`**, never an inference from the pointer — and **no test may assert one platform's Tk semantics**. See the amendment below.

## Decisions

**The trigger is an idle callback scheduled when the widget is created, not `<Map>`.** `update_idletasks` does not deliver events, and PySimpleGUI sizes and places the window inside one — so `<Map>` lands after the window is on screen. Safe because the packer never yields to the event loop while configuring an element. There is **no true per-element finalize hook**: after the ttk style is applied PySimpleGUI only reads attributes on the element, so a property getter would work today and break silently on a reordering.

**`Widget` is a property.** `element.Widget = tk.Button(...)` is the one reliable "the widget now exists" signal, and a property setter is the only way to observe an assignment PySimpleGUI makes from outside.

**The class is built lazily, through a module `__getattr__`.** A class statement needs its base at class-creation time, and the base is PySimpleGUI's `Button`, so building at import would import PySimpleGUI at import. Deferring it means `import tkinter_icons.extensions.psg` pulls in no toolkit, and that a missing PySimpleGUI is reported by `PySimpleGUINotInstalled` rather than by a bare `ModuleNotFoundError`.

**Only PySimpleGUI is targeted.** An earlier draft also resolved FreeSimpleGUI and picked between them from `sys.modules`, which brought a public `resolve_flavor`, a mixing check, a per-library class cache, and an import-order caveat on the docs page — all for a path that could not be tested here. The owner's call on 2026-08-12 was to target PySimpleGUI proper, and removing the rest deleted the branch this plan had listed as its largest untested surface.

**No `[psg]` extra.** In this project an extra means an icon pack — `check_extras_cover_every_pack` is built around that. `verify_packages.py` would tolerate one, so this is keeping an invariant, not working around a limit.

**PySimpleGUI is added to CI's test job.** Without it the integration would ship with no CI coverage. The absent-dependency tests still run everywhere, because they block the import in a subprocess rather than relying on it being uninstalled.

**A `tk` icon button auto-sizes.** Tk measures `-width`/`-height` in characters while a button shows text alone and in *pixels* once it also shows an image, so PySimpleGUI's `height=1` collapses the button. An explicit `size=` is therefore not honored on that path, which is stated on the docs page rather than left to be discovered.

## Known-weak spots, stated rather than hidden

- **`_refresh_for_colors` compares resolved colors**, so it catches a color moving but not a change that resolves to the same color through a different route.
- **Nothing tests the visual result**, only that images differ and states map. The screenshot is the only thing that says the icons *read*, and it is checked by eye.
- **The idle trigger is asserted through its consequences** — attached by the end of `finalize`, geometry stable afterward — rather than by observing which callback fired. If PySimpleGUI ever stopped calling `update_idletasks` during startup, those tests would fail, which is the intent.
- **Every claim about PySimpleGUI's internals was read off version 6.3 and nothing pins it.** That the packer never yields to the event loop while configuring an element, that `element.Widget` is assigned before the ttk style is applied, that `sg.theme()` cannot reach a live window — all true when measured, none asserted by a test that would fail if a future release changed them. The consequences are covered; the mechanisms are not.
- **The `gui`-marked tests skip rather than fail when a second Tk interpreter cannot be built**, which is the Tk 8.6 limitation `CLAUDE.md` records. Locally that is one or two of them depending on ordering, so a green run does not guarantee every button test executed. `-rs` shows which.
- **`_ttk_parent_foreground` reads `Icon._parent_style_for`**, a private classmethod of another module. It is the only way to recover the style PySimpleGUI applied once `Icon.map` has derived a child from it, but it is a private coupling and would break silently if that helper changed.
