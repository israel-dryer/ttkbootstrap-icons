# REVIEW — #112, `feat/psg-extension`

Findings and resolutions, newest round last. Read `PLAN.md` for what the branch is meant to do.

Scope is `git diff main..feat/psg-extension`. Triage each finding **blocking** / **should-fix** / **nit**, and pin the scope of each round to the SHA it was read at.

#144's round is gone rather than archived; it shipped in #145. The standing rule is that each branch resets both files.

---

## Round 1

Read at `493edf4`, against a live PySimpleGUI 6.3. Seven findings, all fixed.

**Blocking**

1. **The second, merging `Icon.map` call silently discarded every per-state image.** `StatefulIconMixin.map` names the child style after the icon names *that call* uses, so the merge — which named only the base icon — derived a different style from the first call whenever `reactive_states` overrode a glyph *name*, and merged into an empty map. `widget.configure(style=…)` then moved the button onto a style holding nothing but the resting image: hover, pressed and disabled all gone. Reproduced with a chosen color plus `{"disabled": {"name": …}}`.

   Fixed by seeding the resting color into the statespec rather than merging it afterward — `""` is the fallback state and belongs there like any other. The derived path (`reactive_states=True`) is the one case that cannot seed, since a statespec suppresses the derivation it exists for; the second call stays there and is safe *because* a derived spec draws every state from the base icon, so both calls hash the same child style. Guarded by `test_a_chosen_color_does_not_cost_the_ttk_state_images`.

2. **State images dropped `style=` and `options=`.** `_render_icon` fell through to the mixin default, which rebuilds the icon as `type(icon)(name, size, color)` — a constructor call with nowhere to carry either. On the nine multi-style packs the button drew the *default* style's glyph for every state: `FontAwesomeIcon("heart", style="regular")` kept its outline at rest and switched to the solid one on hover. It reached the `tk` path here and the `ttk` path through `Icon.map`, so it was never PySimpleGUI-specific.

   Fixed in `Icon`, not in the extension: `Icon._render_icon` renders against the instance's own `IconSet` and options, and `.image` renders through it too, so the resting image and the states beside it cannot come from two places. Guarded by `TestStateImagesComeFromTheIconsOwnSet`. **Round 2 found this over-corrected** — see its finding 1.

**Should fix**

3. **The color check could never match once a color was chosen.** `_refresh_for_colors` compared the parent style's foreground against `_state_colors[""]`, which holds the *chosen* color whenever the caller gave one — so an `update()` that changed no color at all re-ran the whole state map, and with finding 1 unfixed re-lost the state images each time. The parent foreground is remembered separately now. **Round 2 widened what is remembered** to the foreground *and its state map* — see its finding 4.

4. **`update()` carried on after PySimpleGUI had bailed out.** `sg.Button.update` returns early (with an error popup) on a destroyed widget or a closed window rather than raising, and the override then reached `configure()` on a dead widget and raised `TclError`. A single `_widget_alive()` guard now covers `update`, `attach_icon` and `_apply_tk_image` — the `after_idle(self.attach_icon)` callback had the same exposure.

5. **PySimpleGUI's `Update` alias bypassed the override entirely.** `Button` binds `Update = update` in its own class body, so `IconButton.Update` resolved to the base function — and PySimpleGUI calls `.Update(...)` internally, `Window.fill` among others. Rebound in the generated class.

6. **The docs read `reactive_states` as additive; it replaces.** Both paths replace — `ttk` maps with `mode="replace"`, and `_color_for` returns `None` for any non-resting state a mapping does not name — so `{"hover": …, "pressed": …}` silently loses the derived `disabled` tint. Said plainly on the page and in the class docstring. `capture_screenshots.py` was written against the additive reading, so the committed screenshot showed Tk's own disabled stipple rather than a tint this integration applied; the capture now names `disabled` and has been retaken.

**Found while closing round 1, not reported by it**

0. **A ttk theme change emptied the state map on the derived path.** Chasing whether "theme awareness" was still open turned this up. `StatefulIconMixin` records **one mapping per widget, the last one**, so on `<<ThemeChanged>>` it replayed only the merging call carrying the resting color — and ttk's style database is per-theme, so the map that merge would have merged into was gone too. The button adopted the new theme while its icon silently stopped reacting.

   Reachable without any user code touching ttk: `_change_ttk_theme` runs in seven PySimpleGUI element packers, so a window built with a different `ttk_theme=`, or after `set_options(ttk_theme=…)`, re-themes every window already on screen. It is a no-op when the theme does not actually change — `theme_use` on the theme already in use fires no event — so the common case never triggers it.

   `IconButton` binds `<<ThemeChanged>>` and re-applies on the next idle. **Two things that cost a hang and a red test to learn, both now in the code's comments.** `style.map()` and `style.configure()` fire `<<ThemeChanged>>` themselves, so answering the *event* is an endless loop; the trigger is the theme's **name** moving, compared against what was recorded at map time. And `<<ThemeChanged>>` is a queued virtual event, so `update_idletasks()` does not deliver it — the same distinction the attach trigger turns on, in the opposite direction.

   Two things it does *not* fix, both deliberate. PySimpleGUI does not restore its own per-element style configuration across a theme change — a style carrying `foreground #FFFFFF` with an `active` map is left with plain `black` and no map — so the button reverts to the theme's default colors and the icon re-derives from the button *as it now is*. And under Windows' `winnative` the button's foreground reads back as the symbolic `SystemWindowText`, which Pillow rejects, so `Icon.map` skips that state and leaves the fallback alone. That second one was called pre-existing and out of scope here, and **round 2 found it was worse than described and fixed it** — see finding 2 there. It is still why `test_a_ttk_theme_change_does_not_empty_the_state_map` names `alt` rather than taking whichever theme comes first: which states a theme can derive is the theme's business, and a test that took the first available one would be asserting that rather than the repair.

**Nit**

7. **The changelog stated the win32/aqua `tk::ButtonEnter` behavior as universal**, which is the claim `_map_tk_states` and its test exist to correct — x11 sets `-state active` on entry outright. Rewritten to the three-way split the module documents.

---

## Round 2

Read at the round-1 tree plus the theme repair. Six findings, all fixed. Two of them are round 1's own fixes being corrected, which is the pattern the #121–#125 stack recorded and worth noticing again: **the second round's findings came from the first round's fixes.**

**Blocking**

1. **Round 1's fix for the style leak silently lost cross-style per-state names.** Pinning `render_pil` with `icon_set=` is what stops the style being dropped — and it also switches `render_pil` off its resolving branch, so a `statespec` naming a glyph from another style stopped resolving. `StatefulIconMixin.map` catches the failure and `continue`s, so the state was dropped without a word. Reproduced: `FontAwesomeIcon("house", 16).map(btn, statespec=[("pressed", {"name": "42-group"})])` left the image map as the bare fallback.

   The fix is layered rather than either-or, because both halves are real: `Icon._icon_set_for_state` returns this icon's own set wherever it can draw the name, and the pack's own resolution wherever it cannot. Guarded by `test_a_state_name_from_another_style_still_resolves`, which needs a pack whose styles do not share one glyph map — **Bootstrap is no use**, its two styles are one font split by a name predicate, so the first version of that test skipped silently and proved nothing.

2. **`Icon.map` drew nothing usable on the ttk themes Windows ships as its own defaults.** A style hands back what it was configured with, and `vista`, `winnative` and `xpnative` configure `SystemWindowText`. Pillow rejects it; `map` skips any state it cannot render, *including the resting fallback*, so a mapped button came out with no reactive states and an untinted icon. Round 1 saw this as a lost `winnative` state and filed it as pre-existing and narrow; it is neither — `vista` is the default theme on Windows.

   Colors read off a style now go through `StatefulIconMixin._drawable_color`, which asks the widget, since Tk is the only thing that can resolve a system color. A color the caller wrote is untouched, because Pillow accepts specifiers Tk does not. This is a library fix rather than an extension one on purpose: `Icon.map` is what reads a style and hands the result to Pillow, and the extension already normalized its own reads through `_hex_color`.

   **Findings 1 and 2 were entangled**, and this is the part worth keeping. Finding 1's repro failed on this machine for finding 2's reason — the name resolved perfectly and both renders then died on `SystemWindowText`. Fixing one without the other looks like the fix not working.

**Should fix**

3. **`reactive_states={}` gave three answers from one input.** An empty list is falsy and `_parse_statespec` tests `if statespec:`, so it fell through to the derive-from-the-style branch and behaved as `True`; a chosen color seeded a `""` entry, which made the list truthy and stopped it reacting; and the `tk` path reacted to nothing at all. **The owner's call, 2026-08-12: an empty mapping means what `False` means** — it names no states, so nothing reacts. `_reacts_to_nothing()` is the one predicate both paths ask.

4. **`_refresh_for_colors` could not see `disabled_button_color` on the ttk path.** It compared `style.lookup(parent, "foreground")`, the base value, while `sg.Button.update(disabled_button_color=…)` writes `style.map(name, foreground=[('disabled', …)])` — the state map. So the icon kept its old disabled tint while the label changed, and the `tk` path followed the same argument correctly, because it reads `disabledforeground`. The comparison is against `(base, map)` now.

**Nits**

5. **`_apply_tk_image` could `KeyError` on its own fallback.** `self._state_images[""]` assumes a resting image, but `_color_for("")` returns `None` when the widget's foreground is empty or unparseable, while a literal in `reactive_states` still produces the other states — so the dict is non-empty and the guard above did not fire. It runs from `after_idle`, so it would have surfaced only through Tk's callback handler.

6. **The PySimpleGUI capture left a live Tk root behind.** `pysimplegui()` closed its window but left PySimpleGUI's hidden master root and `tkinter._default_root` alive, and it runs *third*, ahead of the two ttkbootstrap captures — so a full run in an environment with both installed asks Tk 8.6 for a second interpreter while the first is up. It now tears down exactly as `tests/test_extensions.py`'s fixture does, and the capture was retaken and looked at afterward.
