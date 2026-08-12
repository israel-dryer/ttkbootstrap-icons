# Verifying `feat/psg-extension` on WSL or Linux

Everything on this branch was written and verified on **Windows, one interpreter, Python 3.13**. This file is for a session running the same tree under WSL or Linux. It is a checklist, not a plan — read `PLAN.md` for what the branch is meant to do and `REVIEW.md` for what three review rounds found, the third of them this one.

**Why bother.** This branch's history says Linux is where the assumptions break. Two of its tests were written against Windows behavior, failed on Linux CI, and were rewritten to assert the *mapping* rather than one platform's Tk — the `tk::ButtonEnter` split is the whole reason the public state vocabulary is `hover` / `pressed` / `disabled` instead of either toolkit's words.

**This file used to say "nothing here is expected to fail". It was wrong, and it was wrong about a specific test it had reasoned through** — see **3** below and round 3 in `REVIEW.md`. That is the argument for running it, not against: the failure was a third Windows assumption of exactly the kind the two above it were, sitting in a test written to guard against them. The pass has been done once now, so a clean run is the expectation again; the entry in **3** is what a fresh session most needs, because the wrong reasoning there is more persuasive than the right answer.

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
.venv-linux/bin/python -m pip install pytest PySimpleGUI 'tomli; python_version < "3.11"' -r docs/requirements.txt
```

`--no-deps` on everything but the base is not optional in a working tree — every pack floors `tkinter-icons>=5.0.0`, and until a `v5.1.0` tag exists setuptools-scm reports something below that floor, so pip goes to PyPI looking for a version that satisfies it. `CLAUDE.md`'s Environment section has the long version.

**Mind the interpreter — this branch was written on 3.13, and a stock WSL image is not.** Ubuntu 22.04 ships **3.10.12** as `python3`, which is inside `requires-python` and runs the library fine, but 3.10 has no `tomllib`. That is why `tomli` is on the line above; `ci.yml:69` installs it the same conditional way, and without it the tests that read `pyproject.toml` fail to collect rather than fail a test. **`verify_packages.py` is the harder case: it cannot run on 3.10 at all.** `.github/scripts/packages.py` bare-imports `tomllib` and documents the 3.11 floor in its own module docstring — a deliberate developer-tooling constraint, unchanged from `main`, not something to work around. Run that one command under any 3.11+ interpreter you have, which on a default WSL image means the system `python3.13` rather than the venv:

```bash
python3.13 .github/scripts/verify_packages.py --strict
```

**`.venv-linux/` is not gitignored.** `.gitignore` carries `.venv/` and `venv/` only, so the venv this file tells you to build shows up as untracked. Harmless, but do not sweep it into a commit.

**Let `apt-get update` fail.** It exits 100 when any source on the machine is mid-sync, and a partial update still refreshes the lists that succeeded. `apt-get install` is the real gate. Both CI workflows were changed to do exactly this after an unrelated Chrome mirror failed a docs job.

**A display is needed for the useful half.** 54 of the 866 tests are marked `gui` and skip without one, and they are precisely the ones this file exists for. With a display, expect 53 to run and one to skip — that one is the Windows-gated colour test in **3**. Under WSLg a display is already there; otherwise run everything through `xvfb-run -a`, which is what CI does:

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
xvfb-run -a .venv-linux/bin/python -m pytest -q                     # 849 passed, 17 skipped
.venv-linux/bin/python -m sphinx docs docs/_build/html -b html -W --keep-going -n -j auto
python3.13 .github/scripts/verify_packages.py --strict               # needs 3.11+, see above
.venv-linux/bin/python .github/scripts/generate_placement_census.py --check
.venv-linux/bin/python .github/scripts/generate_pack_readmes.py --check
```

Those counts are what round 3 measured on WSL2 under Xvfb, after its one fix. The seventeenth skip is the Windows-gated colour test described in **3** below, and one of the 849 is new — that test split in two.

**Do not run `.github/scripts/capture_screenshots.py`.** It is Windows-only by construction — `ctypes.windll`, DWM frame bounds, `SetProcessDpiAwareness` — and the committed captures were taken on Windows deliberately. A Linux run either crashes or produces a different-looking window that must not be committed.

---

## The five places Linux could genuinely differ

Ordered by how likely they are to bite. If one fails, the question is always the same: **is this the platform, or is this the code?** Each entry says how to tell.

**1. `tk::ButtonEnter`, and the `active` state.** On win32 and aqua a `tk.Button` reaches `-state active` only while button 1 is down; on x11 it is set on entry outright, so there hover and press are one state. `test_the_tk_icon_follows_the_widgets_own_state` is written to survive both — it asserts the image matches whatever `-state` reports, and generates an `<Enter>` before the press for exactly this reason. **If it fails, read what it asserts before touching the module**: two earlier versions of that test failed on Linux against code that was doing the right thing.

**2. The ttk theme change repair.** `test_a_ttk_theme_change_does_not_empty_the_state_map` switches to the `alt` theme, which exists on X11. It asserts that *some* state survives, plus that `button._ttk_theme` moved to the new theme. **The second assertion is the repair's own signal**; the first depends on whether `alt` can derive a state colour on this platform at all. If only the first fails, that is the theme's business rather than the repair's, and the test should be told so rather than the code changed.

**3. Symbolic system colours. This is the one that actually failed — the prediction below was wrong, and round 3 replaced it.** This entry used to say the test "should pass anywhere" because it configures the symbolic colour by hand rather than relying on a native theme. **Configuring a value by hand does not make Tk able to resolve it.** On X11 `winfo_rgb("SystemWindowText")` raises `unknown color name`: the `System*` names live only in Tk's Windows build, and they name a Windows *system setting* rather than a colour, so off Windows there is nothing to resolve them to. The code was doing exactly what it documents — pass the unresolvable value through, let Pillow reject it, skip the state — and the test was asserting a Windows outcome from a Windows-only premise.

It is now two tests. `test_a_name_a_theme_configures_is_resolved_to_hex` runs everywhere and asserts `black` becomes `#000000`, which is what every stock X11 theme — `clam`, `alt`, `default`, `classic` — really configures. The `SystemWindowText` integration test is unchanged and gated on `sys.platform == "win32"`, so **the real check for that fix still stays Windows**, and on Linux it now skips loudly instead of failing.

**If you are ever tempted to make that Windows test portable, read round 3 in `REVIEW.md` first.** Two plausible repairs are wrong: values like `gray50` or `#ffff00000000` are portable and do reproduce the bug, but no real theme on any platform configures them, and a plain named colour such as `SteelBlue` is worse still — Pillow parses it, so the test passes with the translation deleted.

**4. PySimpleGUI's tk-vs-ttk default.** PySimpleGUI uses `tk.Button` by default off macOS, so on Linux the `tk` path is the default one and the `use_ttk_buttons=True` tests exercise the other. That is the same split as Windows; noted so a difference in which path is "normal" is not mistaken for a bug.

**5. Tk 8.6 and second interpreters.** Some tests skip with a `TclError` about a second interpreter, and *which* ones depends on ordering. That is a Tk limitation `CLAUDE.md` records, not a branch bug. A handful of skips is expected; round 3 saw **none of this kind at all** on WSL2, and its 17 are the 16 benign ones — 2 fontTools, 14 style-less packs — plus the Windows-gated colour test. If the count climbs past that, look at the reasons with `-rs` before assuming anything.

---

## What to report back

- The pass/skip counts, and the **skip reasons** from `-rs` — a skip that hides a GUI test is the outcome this file is trying to prevent.
- Whether the `gui`-marked tests ran at all.
- For any failure: which of the five above it is, and whether the platform or the code is wrong. Say which, rather than fixing toward green.

Round 3 needed one change — a test, not the module — and it is recorded in `REVIEW.md` as a round of its own with the platform named. That is the pattern to follow if anything else turns up: a round of its own, the platform named, and the verdict stated as *platform* or *code* rather than left implied by the fix.
