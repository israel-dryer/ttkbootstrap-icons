# Verifying `feat/psg-extension` on WSL or Linux

Everything on this branch was written and verified on **Windows, one interpreter, Python 3.13**. This file is for a session running the same tree under WSL or Linux. It is a checklist, not a plan — read `PLAN.md` for what the branch is meant to do and `REVIEW.md` for what two review rounds found.

**Why bother.** This branch's history says Linux is where the assumptions break. Two of its tests were written against Windows behavior, failed on Linux CI, and were rewritten to assert the *mapping* rather than one platform's Tk — the `tk::ButtonEnter` split is the whole reason the public state vocabulary is `hover` / `pressed` / `disabled` instead of either toolkit's words. Nothing here is expected to fail. It is worth an hour anyway.

---

## Setting up

**Do not reuse `.venv` or `.venv-home`.** Both are Windows venvs whose `home =` points at a Windows interpreter; they are unusable from WSL. Build a fresh one on the Linux side.

```bash
sudo apt-get update || true          # a partial update is fine; see the note below
sudo apt-get install -y python3-tk python3-venv xvfb

python3 -m venv .venv-linux
.venv-linux/bin/python -m pip install --upgrade pip
.venv-linux/bin/python -m pip install -e packages/tkinter-icons
.venv-linux/bin/python -m pip install --no-deps $(printf -- '-e %s ' packages/tkinter-icons-*/)
.venv-linux/bin/python -m pip install --no-deps -e packages/ttkbootstrap-icons-shim
.venv-linux/bin/python -m pip install pytest PySimpleGUI -r docs/requirements.txt
```

`--no-deps` on everything but the base is not optional in a working tree — every pack floors `tkinter-icons>=5.0.0`, and until a `v5.1.0` tag exists setuptools-scm reports something below that floor, so pip goes to PyPI looking for a version that satisfies it. `CLAUDE.md`'s Environment section has the long version.

**Let `apt-get update` fail.** It exits 100 when any source on the machine is mid-sync, and a partial update still refreshes the lists that succeeded. `apt-get install` is the real gate. Both CI workflows were changed to do exactly this after an unrelated Chrome mirror failed a docs job.

**A display is needed for the useful half.** 53 of the 865 tests are marked `gui` and skip without one, and they are precisely the ones this file exists for. Under WSLg a display is already there; otherwise run everything through `xvfb-run -a`, which is what CI does:

```bash
xvfb-run -a .venv-linux/bin/python -m pytest -q
```

Check that the GUI tests actually **ran** rather than skipped — a green run that skipped them proves nothing about this branch:

```bash
xvfb-run -a .venv-linux/bin/python -m pytest -q -m gui -rs
```

---

## What to run

```bash
xvfb-run -a .venv-linux/bin/python -m pytest -q                     # expect ~851 passed
.venv-linux/bin/python -m sphinx docs docs/_build/html -b html -W --keep-going -n -j auto
.venv-linux/bin/python .github/scripts/verify_packages.py --strict
.venv-linux/bin/python .github/scripts/generate_placement_census.py --check
.venv-linux/bin/python .github/scripts/generate_pack_readmes.py --check
```

**Do not run `.github/scripts/capture_screenshots.py`.** It is Windows-only by construction — `ctypes.windll`, DWM frame bounds, `SetProcessDpiAwareness` — and the committed captures were taken on Windows deliberately. A Linux run either crashes or produces a different-looking window that must not be committed.

---

## The five places Linux could genuinely differ

Ordered by how likely they are to bite. If one fails, the question is always the same: **is this the platform, or is this the code?** Each entry says how to tell.

**1. `tk::ButtonEnter`, and the `active` state.** On win32 and aqua a `tk.Button` reaches `-state active` only while button 1 is down; on x11 it is set on entry outright, so there hover and press are one state. `test_the_tk_icon_follows_the_widgets_own_state` is written to survive both — it asserts the image matches whatever `-state` reports, and generates an `<Enter>` before the press for exactly this reason. **If it fails, read what it asserts before touching the module**: two earlier versions of that test failed on Linux against code that was doing the right thing.

**2. The ttk theme change repair.** `test_a_ttk_theme_change_does_not_empty_the_state_map` switches to the `alt` theme, which exists on X11. It asserts that *some* state survives, plus that `button._ttk_theme` moved to the new theme. **The second assertion is the repair's own signal**; the first depends on whether `alt` can derive a state colour on this platform at all. If only the first fails, that is the theme's business rather than the repair's, and the test should be told so rather than the code changed.

**3. Symbolic system colours.** The `SystemWindowText` problem `_drawable_color` fixes is a Windows-native-theme thing — X11 themes configure plain colour names. Its test configures a style with a symbolic colour by hand rather than relying on a native theme, so it should pass anywhere, and passing on Linux says less than it does on Windows. **The real check for that fix stays Windows.**

**4. PySimpleGUI's tk-vs-ttk default.** PySimpleGUI uses `tk.Button` by default off macOS, so on Linux the `tk` path is the default one and the `use_ttk_buttons=True` tests exercise the other. That is the same split as Windows; noted so a difference in which path is "normal" is not mistaken for a bug.

**5. Tk 8.6 and second interpreters.** Some tests skip with a `TclError` about a second interpreter, and *which* ones depends on ordering. That is a Tk limitation `CLAUDE.md` records, not a branch bug. A handful of skips is expected; if the count is much above ~14, look at the reasons with `-rs` before assuming anything.

---

## What to report back

- The pass/skip counts, and the **skip reasons** from `-rs` — a skip that hides a GUI test is the outcome this file is trying to prevent.
- Whether the `gui`-marked tests ran at all.
- For any failure: which of the five above it is, and whether the platform or the code is wrong. Say which, rather than fixing toward green.

Nothing here should need a code change. If something does, it belongs in `REVIEW.md` as a round of its own, with the platform named.
