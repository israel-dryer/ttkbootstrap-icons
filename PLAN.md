# PLAN — icons on PySimpleGUI (#112)

Branch `feat/psg-extension`, off `main`. The reviewing session's scope is `git diff main..feat/psg-extension`.

Written for the session that does the work and the session that reviews it. It states what the code is meant to do and what must hold, so a finding can be checked against intent rather than guessed at.

The previous section here — #144's plan — is gone rather than archived. It shipped in #145. A plan kept past its merge is a second copy of the truth.

---

## The gap

PySimpleGUI is declarative: constructing `sg.Button` creates no Tk widget, so `element.Widget` stays `None` until `sg.Window` builds the layout. An icon cannot be applied in a constructor, and cannot even be *rendered* there, because a `PhotoImage` needs an interpreter that does not exist yet.

## Settled before designing, as the handoff instructed

**PySimpleGUI 6.3 is LGPLv3** — v6 is an open-source relaunch, no runtime license gate. Nothing from it is redistributed; it stays a separate installable. That was the open question on whether the integration was appropriate at all, and the answer removed it.

**`sg.theme()` does not reach a live window.** Measured: after `sg.theme("LightGrey1")` a window built under `DarkBlue3` keeps both its `tk` foreground and its ttk style foreground, and PySimpleGUI exposes no method to re-theme one. **`update(button_color=...)` does** change live colors, on both paths. So "theme aware" means following per-element color changes, not global theme calls — following those would make the icon more reactive than the button under it.

## What was built

`tkinter_icons/extensions/__init__.py`, which imports nothing, and `extensions/psg.py`, which holds `IconButton`, `resolve_flavor` and `PySimpleGUINotInstalled`.

## What must hold

- **The base package never gains a load-time dependency on a GUI toolkit.** `import tkinter_icons` must not import PySimpleGUI, and neither must `import tkinter_icons.extensions`.
- **The icon is on the button before the window is first painted.** Not merely "eventually correct" — the failure this replaces was visible.
- **The window does not resize after it is shown.**
- **A missing dependency explains itself**, as an `ImportError`, naming both flavors and the path that needs no install at all.
- **One flavor per process.** `IconButton` subclasses one library's `Button`; a layout that mixes two must raise rather than misbehave later.
- **`hover` is unreachable on `tk` and says so.** Silently dropping it is the failure mode this project keeps writing guards against.
- **The tk icon reflects the widget's own `-state`**, never an inference from the pointer.

## Decisions

**The trigger is an idle callback scheduled when the widget is created, not `<Map>`.** `update_idletasks` does not deliver events, and PySimpleGUI sizes and places the window inside one — so `<Map>` lands after the window is on screen. Safe because the packer never yields to the event loop while configuring an element. There is **no true per-element finalize hook**: after the ttk style is applied PySimpleGUI only reads attributes on the element, so a property getter would work today and break silently on a reordering.

**`Widget` is a property.** `element.Widget = tk.Button(...)` is the one reliable "the widget now exists" signal. The flavor check lives in that setter rather than in the attach, because the setter runs synchronously inside the packer — so the error propagates out of `sg.Window(...)` instead of being printed and swallowed by Tk's idle-callback handler.

**`resolve_flavor` asks `sys.modules` before importing.** The application's own import decides. Only if neither is loaded is one imported, which is the case worth avoiding and is documented as "import your framework first".

**The class is built lazily, through a module `__getattr__`.** A class statement needs its base at class-creation time, so building at import would force the flavor choice at import. Deferring it also means `import tkinter_icons.extensions.psg` pulls in no toolkit.

**No `[psg]` extra.** An extra cannot express "either flavor", and here an extra means an icon pack — `check_extras_cover_every_pack` is built around that. `verify_packages.py` would tolerate one, so this is keeping an invariant, not working around a limit.

**PySimpleGUI is added to CI's test job.** Without it the integration would ship with no CI coverage. The absent-dependency tests still run everywhere, because they block the import in a subprocess rather than relying on it being uninstalled.

**A `tk` icon button auto-sizes.** Tk measures `-width`/`-height` in characters while a button shows text alone and in *pixels* once it also shows an image, so PySimpleGUI's `height=1` collapses the button. An explicit `size=` is therefore not honored on that path, which is stated on the docs page rather than left to be discovered.

## Known-weak spots, stated rather than hidden

- **The two-flavor path is untested.** Only PySimpleGUI is installed here; FreeSimpleGUI was deliberately not installed, since that changes the environment the release is verified in. `resolve_flavor`'s preference order and the mixing check have therefore only been exercised against one library.
- **The mixing check compares the root module name** of the window's class against the flavor the class was built from. A vendored or re-exported PySimpleGUI would defeat it.
- **`_refresh_for_colors` compares resolved colors**, so it catches a color moving but not a change that resolves to the same color through a different route.
- **Nothing tests the visual result**, only that images differ and states map. The screenshot is the only thing that says the icons *read*, and it is checked by eye.
- **The idle trigger is asserted through its consequences** — attached by the end of `finalize`, geometry stable afterward — rather than by observing which callback fired. If PySimpleGUI ever stopped calling `update_idletasks` during startup, those tests would fail, which is the intent.
