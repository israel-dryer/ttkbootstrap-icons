# tkinter-icons — Claude Handoff

## Project overview

Font-based icons for Tkinter and ttkbootstrap. The library renders glyphs from
icon fonts to Tk-compatible images; the icon sets themselves ship as separate
distributions installed via extras.

**The identity shifted, and this matters for every docs decision.** This started as `ttkbootstrap-icons`, intended to be folded into ttkbootstrap. Instead, Bootstrap icons were built *directly* into ttkbootstrap. So this project's audience is now **people on raw tkinter, or people who want an icon set other than Bootstrap** — not "the way to get icons for ttkbootstrap." Renamed to `tkinter-icons` in 5.0.0 to match.

**bootstack was never connected to this project, and no user-facing text may imply otherwise.** Stated by the owner 2026-08-02. Eight places named it alongside ttkbootstrap in the rename rationale — the two READMEs, both changelogs, and four docs pages — which read as though bootstack were part of why the rename happened. All eight were corrected. bootstack is still a legitimate reference for *conventions* — its `docs/conf.py`, its changelog format, its `release_notes.py` — and those mentions below are fine. The line is between "we copied a pattern from a sibling project" and "this project was ever coupled to it."

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

**Which virtualenv works depends on the Windows account you are logged in as, so do not trust a name written down here — check.** There are two, `.venv` and `.venv-home`, created by two different accounts on this machine, and which of them is live flips with the login. Only the one whose base interpreter belongs to the current account runs at all; the other fails with `Access is denied` on the exe itself, not on a file it wants. This file asserted "use `.venv-home`, not `.venv`" for several sessions and was simply wrong by 2026-08-04, when the login had changed — so read `pyvenv.cfg` and match `home =` against the current user rather than believing the last person who wrote it down:

```bash
head -1 .venv/pyvenv.cfg .venv-home/pyvenv.cfg
```

The same ownership split makes git refuse the repository until you run `git config --global --add safe.directory D:/Development/ttkbootstrap-icons`, and it can make `.pytest_cache/` unwritable, which prints a `PytestCacheWarning` on every run and is harmless.

**Whichever one is live needs all eighteen distributions installed**, plus pytest, the docs toolchain, PyInstaller, and fontTools. If the login has just changed, the newly-live venv is probably bare and needs the whole block — it takes a couple of minutes. Substitute the working venv for `.venv` throughout:

```bash
.venv/Scripts/python.exe -m pip install --no-deps -e packages/tkinter-icons
.venv/Scripts/python.exe -m pip install --no-deps $(printf -- '-e %s ' packages/tkinter-icons-*/)
.venv/Scripts/python.exe -m pip install --no-deps -e packages/ttkbootstrap-icons-shim
.venv/Scripts/python.exe -m pip install twine pytest pyinstaller fonttools -r docs/requirements.txt
.venv/Scripts/python.exe -m pytest -q          # 414 passed (1-2 skip, Tk-ordering)
```

Having every pack installed is worth keeping. The docs build reads each pack's live provider for the packs table and the previews, `generate_metrics --all` needs them, and `verify_packages.py --imports` exercises every entry point.

**Check that the base package is actually editable, because it was not on 2026-08-12 and nothing said so.** All sixteen packs were editable and `tkinter_icons` was a plain copy in `site-packages`, so `pytest` was running against a snapshot rather than against `packages/tkinter-icons/src/`. It surfaced only as new tests failing with `AttributeError` on a method plainly present in the source. Nothing had gone stale — the copy was byte-identical to `HEAD` apart from `tools`, which is correctly excluded from wheels — but a green suite in that state is not evidence about the tree. One line answers it, and the fix is the `-e` install above:

```bash
.venv-home/Scripts/python.exe -c "import tkinter_icons,inspect;print(inspect.getfile(tkinter_icons))"
```

It must print a path under `packages/tkinter-icons/src/`. Anything under `site-packages/` means the suite is testing a copy. Worth running whenever results disagree with the source in front of you.

**`ttkbootstrap` is deliberately *not* installed here**, even though the docs have an integration page for it. Verifying those examples means a throwaway venv (`python -m venv`, then `pip install ttkbootstrap` plus the packs the example uses); that keeps a widget library out of the environment the release is verified in. It is not a large cost — the whole ttkbootstrap 2.0 rewrite was checked that way.

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

**Every pack now has generated metrics**, committed via #82. `generate_metrics --all --check` is clean, and `bs`/`fa` regenerated byte-identical to what was already committed — so the measurement reproduces across machines, which is what the release workflow's re-measure-and-compare check depends on.

---

## Current state

**5.0.1 is released, 2026-08-08, and it was the first tag-driven one.** The base is at 5.0.1, fifteen packs at 1.1.1, `fluent-reg` unchanged at 1.1.0, the shim unchanged at 5.0.0, and the GitHub Release is cut as "5.0.1 — updated metadata and docs". Both things it existed for are confirmed *on PyPI* rather than inferred from a green run: the published base carries the `3.14` classifier, so the pyversions badge finally reads past 3.13, and `gmi` no longer claims a `twotone` style anywhere. It took two workflow runs — see the publisher note below, which is the most useful thing this release taught.

**5.0.0 is released.** All eighteen distributions are on PyPI, `v5.0.0` is pushed, and the GitHub Release is cut. The integration branch `5.0` did its job long ago; **new work branches off `main` and PRs to `main`.**

| | |
|---|---|
| `main` | 5.0.0 released, plus the post-release fixes in #113 and #114 |
| the sixteen legacy packs | **published to PyPI** with their `<5` caps, 2026-08-02 |
| the eighteen 5.0.0 distributions | **all published**, 2026-08-03 through 2026-08-08 |
| `v5.0.0` | pushed, pointing at `ee118e2` — **do not move it**, see below |
| the GitHub Release | created by hand, then corrected in #113 |
| Trusted Publishing | **configured and verified working**, 2026-08-08 |

### What the release left behind that still matters

**The `v5.0.0` tag points at `ee118e2`, not at the tip of `main`, and must stay there.** #109 added a `Programming Language :: Python :: 3.14` classifier to the base `pyproject.toml` *after* the base wheel was built and published, so `main` differs from the released tree in packaged metadata. `ee118e2` describes exactly what PyPI is serving as 5.0.0; dragging the tag forward would make it describe a base wheel carrying a classifier the published 5.0.0 does not have. The release workflow's own "Confirm the base wheel matches the tag" step passes against it. If it is ever lost, recreate it with `git tag v5.0.0 ee118e2`, never at `HEAD`.

The same divergence means **the base cannot be rebuilt as-released from `main`** — build it from the tag if you ever need that. The seventeen others are untouched by #109 and rebuild from `main` identically.

**Trusted Publishing is configured on all eighteen projects, and as of the 5.0.1 release it is genuinely proven for the sixteen that uploaded a new version.** The owner filled the forms after the release rather than before it, which is what made a four-day manual upload tolerable — seventeen *pending* publishers would have been seventeen web forms standing between here and the first upload. Every form takes the same four values, and these are the OIDC claims the runner actually presents, not guesses: owner `israel-dryer`, repository `tkinter-icons`, workflow `release.yml`, environment `pypi`.

**"Verified" was wrong, and 5.0.1 is what proved it. Re-running the tagged workflow cannot check a pack's publisher.** This file used to say publishers were confirmed by re-running, because `--skip-existing` makes the packs step a safe no-op. That is exactly why it proves nothing: every pack version in that run was **already on PyPI**, so each upload returned `400 File already exists` and never exercised the token's project scope. `tkinter-icons-mat` had no Trusted Publisher for the whole period this file called all eighteen verified, and no amount of re-running would have shown it.

**Only an upload of a genuinely new version tests a publisher.** 5.0.1 was the first, and it failed with `403 Invalid API Token: OIDC scoped token is not valid for project 'tkinter-icons-mat'` — not the `invalid-publisher` error described below, which is what a missing publisher looks like at the *minting* step rather than at the upload. The mint succeeded, scoped to the projects that did have publishers.

**A failure there publishes some packs and not others.** twine uploads alphabetically and aborts on the first error, so `mat` failing left `bs` through `lucide` at 1.1.1 and `mat` through `weather` at 1.1.0 — eight published, seven not. That is not corruption and needs no re-tag: nothing partial was written for the failed project, the base step never ran so the packs-before-base order held, and re-running after adding the publisher skipped the eight and uploaded the seven. **Check what is actually live before doing anything else** — the loop under "Check what is live rather than trusting a log" answers it in one command.

Read *which step* fails. `invalid-publisher` in **Publish the packs** means the OIDC exchange itself was refused. A `403 ... not valid for project '<name>'` means the exchange worked and that one project has no publisher. A `400 File already exists` in **Publish tkinter-icons** means authentication worked and you have hit the deliberate guard below — that is success, not failure.

**A red run on the `v5.0.0` tag is expected and permanent.** The base step runs with `skip_existing: false` on purpose: a base version already on PyPI normally means the tag is wrong. Since 5.0.0's base was uploaded by hand, that check fires every time. Consequence: the `release` job never runs for this tag, which is why the GitHub Release was created by hand. This is specific to 5.0.0 — a normal tag-driven release will not hit it.

**A render check must assert on ink, never on the absence of an exception.** `render_pil` returns a fully transparent image for a name it cannot resolve, so a check that only looks for a raised exception passes on a typo. Assert `img.getbbox() is not None`, or count non-transparent pixels. This cost real time twice: once reading a live pack as broken when the name was wrong, and once when `RpgAwesomeIcon.render_pil('sword-brandish')` came back blank during the final release verification — the pack was fine, the glyph name was invented, and the real names come from `provider.build_name_lookup()[style]`, which is keyed by **style** and not by glyph name.

That behavior is now **#115**, and it was narrower than it first looked: `on_missing` was at the time a real, documented, tested policy (`"transparent"` default, `"warn"`, `"raise"`), so the transparent square was deliberate. It is removed as of 5.1.0 — see the `on_missing` entry below — but the shape of the finding is what matters here. What is *not* deliberate is that the constructor raises `ValueError` on an unresolvable name while `render_pil` swallows it — and `docs/user-guide/icons-and-names.rst:72` says the policy is for a name that "resolves but is missing from the glyph map … rather than that you made a typo". Do not file that as "blank render is a bug"; the divergence between the two entry points is the finding.

**PyPI allows four new projects per 24 hours.** Confirmed by the owner 2026-08-04, and it is not the "20 per hour" in `warehouse/config.py`. Seventeen of the eighteen names were brand new, so 5.0.0 was inherently a multi-day upload — five consecutive days, each a full 24-hour wait followed by four clean uploads with no warm-up. Publishing to a project that **already exists** does not draw from that quota, which is why the shim went up alongside `rpga` on the last day. Keep this only for the next release that creates new project names; a version bump on existing projects is unaffected.

**The base was published fifth-from-last rather than last, deliberately.** The standing rule is packs → base → shim, because the base's extras pin `>=1.1.0`. Under a four-a-day cap that rule bought nothing and cost three further days in which *nothing at all* was installable. The failure it protects against was measured before the decision and is mild: `pip install "tkinter-icons[weather]"` against an unpublished pack gives a clean `No matching distribution found` and installs nothing. Step 3 — the shim last — held regardless, so it never pointed at a version that did not exist.

**`.pypirc` is in the repository root**, gitignored at `.gitignore:33` and untracked. `twine` reads `~/.pypirc` and will not find it, so every manual upload needs `--config-file .pypirc`. With Trusted Publishing now live, manual uploads should be the exception.

**Check what is live rather than trusting a log** — a batch loop misreported this once, because `curl` inside `while read` eats stdin:

```bash
for d in $(.venv-home/Scripts/python.exe -c "from tkinter_icons.packs import KNOWN_PACKS; print(' '.join(p.distribution for p in KNOWN_PACKS))"); do
  printf '%-28s %s\n' "$d" "$(curl -s -o /dev/null -w '%{http_code}' https://pypi.org/pypi/$d/json </dev/null)"
done
```

**`dist/` may be unreadable, and that is the account split, not corruption.** The 36 artifacts built 2026-08-04 belong to the other Windows account; under the current login `twine check` on them dies with `PermissionError` on the file itself. Rebuilding the ones you need is cheap and reproduces byte-identically — `rpga` and the shim rebuilt to the same sizes as the originals. Neither uses setuptools-scm, so the PyCharm dirty-tree trap does not apply to them; **the base is the only distribution that needs `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TKINTER_ICONS=5.0.0`**, because PyCharm rewrites the tracked `.idea/modules.xml` mid-build and setuptools-scm then produces a `+local` version PyPI rejects outright.

Milestone **5.0.0** (issues #67–#71, #75, #79):

| Issue | State |
|---|---|
| #67 renderer rework | merged (#72) |
| #68 stateful icon lifecycle | merged (#73) |
| #69 packs as extras | merged (#74) |
| #75 rename to tkinter-icons | merged (#76) |
| #70 changelog + release automation | merged (#78) |
| #79 trim the published surface | merged (#81) |
| #71 Sphinx docs + reframing | merged (#85) |

Also merged: #77, three cloud-review findings plus a pack-asset-runner bug; #82
(metrics for fourteen packs); #83 (upstream license files); #84 (the
`pyinstaller40` entry point and the missing `bs`/`fluent-reg` hooks); #86
(`options=` and a working `render_pil` on all sixteen pack classes); #88
(semantic glyph names and correct attribution for Meteocons).

**Merged 2026-08-02, later the same day:**

| PR | What |
|---|---|
| #92 | `Closes #89` — sixteen per-pack docs pages, nav consolidation, landing-page rework, the five retaken assets, the browser's own app icon, and the move to Read the Docs |
| #93 | `pack_showcase` declared parallel-read safe; CI's docs job builds with `-j auto` |
| #94 | records that Read the Docs is live |
| #97 | one tag releases the repository; the eighteen-tag scheme is retired |
| #95 | the release procedure itself — legacy packs before the tag, the dry run after the merge to `main`, what that merge does and does not close, and the Meteocons decision recorded as settled |

Closed unmerged: #96, superseded by #97.

**Merged into `main` after #100, and therefore after the milestone closed:**

| PR | What |
|---|---|
| #98 | retires #95 from the handoff, reopens the list on the release |
| #99 | bootstack removed from every user-facing mention — see below |
| #100 | **the release merge**: `5.0` → `main`, closing #69, #71, #79 and #89 |

**Merged 2026-08-03, closing out the pre-tag review:**

| PR | What |
|---|---|
| #101 | four docs fixes found by reading — the shim's broken `[all]` install line, the migration guide implying 4.0.0 shipped Bootstrap, that guide explaining two releases at once, and the ttkbootstrap examples teaching a pre-2.0 API — plus the guard that would have caught the first |
| #103 | a CI badge on the repository README, and the downloads badge removed from both (it was a live 404 until the tag) |
| #104 | the three claims #102's review found in the *published release text* — a shell command inside a `python` fence, the wrong "17 MB", and a conditional dressed as unconditional |
| #105 | `Closes #90` — the sixteen pack READMEs generated from the catalog, the pre-rename screenshots dropped |

**The milestone issues are all closed, and #89 closed because #100's body named it.** That was not automatic: no commit body mentions #89, and its `Closes #89` lived only in PR #92's body, which merged to `5.0` — a non-default base — so GitHub had already discarded the link and does not re-evaluate it. #69, #71 and #79 closed from keywords already in the commit bodies. #67, #68, #70 and #75 were closed earlier by hand and their links are lost for good.

`origin` carries one branch that is **not** stale and must not be deleted with
the rest:

- `release/ttkbootstrap-icons-packs-final` — the terminal release of the sixteen
  `ttkbootstrap-icons-*` packs, cut from `v4.0.0`. Merges nowhere. See
  `RELEASE.md`.

`gh-pages` used to be listed alongside it. It is **gone as of 2026-08-08**, along
with GitHub Pages itself — but it was not dead when this file said it was, and
the entry under "Deliberate decisions" records what that cost.

**The docs moved to Read the Docs, and GitHub Pages is out of the picture.**
Decided 2026-08-02, matching `ttkbootstrap`, for versioned docs and PR previews
— both of which matter here because most of the site is generated. `docs.yml` is
deleted and `.readthedocs.yaml` replaces it.

**No `apt_packages: [python3-tk]` is needed on Read the Docs, and adding one is
cargo cult.** The worry is real-sounding — `icon.py` imports `tkinter` at module
scope, so `import tkinter_icons` needs `_tkinter` — but `ttkbootstrap` imports
`tkinter`, `tkinter.font`, and `tkinter.ttk` at module scope, mocks nothing,
lists no apt packages, and publishes to Read the Docs today. Their image has it.

**Read the Docs clones shallow and without tags**, and `fallback_version` was
removed on purpose, so setuptools-scm would fail the build. `post_checkout`
unshallows and fetches tags; do not remove it.

**A `--delete-branch` merge closes any PR that targets the deleted branch.**
Merging #84 that way closed #85 outright, and a closed PR cannot be reopened
while its base is gone or retargeted while closed — recovering it meant pushing
the base branch back at its old SHA, reopening, then retargeting. When merging a
stack, retarget the child to `5.0` *first*, merge the parent without
`--delete-branch`, and delete branches at the end.

Formerly an open follow-up: **#91** — reaching the pure-Pillow renderer should not require `tkinter` installed — **closed 2026-08-09 from #139**. **#87 closed 2026-08-08 from #130**, which captured the three real-window screenshots; its generated figures landed in #123 and its retaken assets and app icon earlier still. **#90 closed from #105**, which generated the sixteen pack READMEs rather than hand-editing them. #92 did the substance of #89 apart from its prose pass, which is folded into the list under "Next session"; #89 itself closed with #100.

**#79 shipped as #81, not #80.** #80 was merged into `5.0` prematurely — without
permission and before review — and `5.0` was reset to drop it. The rollback was
a reset rather than a revert, so `5.0`'s history is clean and there is no
reverted-content trap for later merges; verified after #81 landed. **Do not
merge a PR in this repository unless asked to merge that specific PR.** A
passing CI run, a `MERGEABLE` state, and the `gh pr merge` line under
"Conventions" are mechanics, not authorization. `5.0` exists so each piece is
reviewed before it accumulates.

**Most of these issues are still OPEN on GitHub, and that is correct** — a PR
merged into `5.0` does not close the issue it names, because GitHub only honors
`Closes #n` on a merge into the default branch. They are meant to close together
when the single `5.0` → `main` PR lands, so an issue closed early loses its link
to the merge that actually shipped it.

**Four of them are nonetheless already CLOSED — #67, #68, #70 and #75** (#70 and #75 checked 2026-07-31, #67 and #68 by 2026-08-02); #69, #71 and #79 are the ones still open. Nothing went wrong: this is the same drift the paragraph above describes, not a repeat of the #80 incident. Whatever closed them, the link to the merge that shipped them is already lost and reopening would not restore it — so leave them, and do not close any more by hand.

**`verify_packages.py --strict` reports "all clear"** across all eighteen
distributions, as of 2026-08-01 with the stack applied. Both former blockers are
closed: #82 generated the missing metrics, #83 vendored the missing license
texts, and `KNOWN_LICENSE_GAPS` is now an empty set — which is load-bearing, since
a *listed* pack downgrades the missing-license finding from an error to a
warning.

**Meteocons: decided 2026-08-02 — ships, and the question is closed.** The font
is licensed "free for use in both personal and commercial projects… **You must
not resell any icons or distribute them in any other way**", which is the
author's own text, embedded in the font, and bundling it in a wheel is arguably
that. Alessio Atzeni was asked and did not answer. The owner's call is to ship
and revert if anyone complains.

Two facts that make that a smaller call than it reads. **The font is already
distributed**: `ttkbootstrap-icons-meteocons` 1.0.0 has been on PyPI since the
4.x line, so 5.0.0 continues a distribution rather than starting one. And
**there is no true undo on PyPI** — a release can be yanked (existing pins keep
resolving) or deleted (the version number is then burned forever), but anything
that already mirrored the wheel keeps it. So "revert" means yank
`tkinter-icons-meteocons`, release a `tkinter-icons` that drops the `[meteocons]`
extra, and revert #88 — not erasure.

Do not reopen this as an open question. If a complaint arrives, the path above
is the plan.

Release mechanics live in `RELEASE.md`: tag-driven, Trusted Publishing, no token
anywhere. **One tag, `v<version>`, releases the whole repository** — it builds
all eighteen distributions, publishes the ones PyPI does not already have, and
creates one GitHub Release.

**That path is live as of 2026-08-08, but 5.0.0 itself was not released through it.** Trusted Publishing needs a publisher registered per project, and for a project that does not exist yet that means a *pending* publisher — seventeen web forms before the first upload could happen. The owner declined that on the critical path (2026-08-03), so 5.0.0 went up by hand with a token from `.pypirc` and the publishers were configured afterwards, against projects that by then existed. They are configured and verified now, so the next release is tag-driven.

**Per-distribution tags were a mistake I introduced, not a decision the owner
made.** #70 shipped `<distribution>-v<version>` for the other seventeen; the
owner's position, stated 2026-08-02, is that a monorepo has one tag and the
base package carries the change. It was retired before any such tag was ever
pushed, so nothing is orphaned. `packages.py` rejects the old shape with an
explanation rather than a parse error, because it is plausible enough that
someone will try it.

The publish order is no longer a human procedure. It is three ordered steps in
the `publish` job — packs, base, shim — with `skip-existing` on the first and
last. A base version already on PyPI fails the release, because the base is
bumped every time and an existing one means the tag is wrong.

---

## Next session — start here

### Next action: #112, PySimpleGUI integration — the last open issue in the repository

**#140 merged 2026-08-10 as PR #141, after a fourth review round.** Everything 5.1.0 was waiting on is now on `main` except #112. **5.1.0 is deliberately uncut** — the owner's call the same day, made with the merge: the milestone is not ready to tag. Do not push `v5.1.0`.

**That branch has now been verified on both platforms — Windows throughout, then WSL2 under Xvfb on 2026-08-12.** `HANDOFF-LINUX.md` was the checklist for the second pass and is deleted now that the pass is done; what outlived it is the symbolic-color entry under "Known gotchas", which is the one finding a later session is most likely to re-litigate. Three of this branch's tests were written against Windows behavior and failed off Windows against code that was correct — the `tk::ButtonEnter` split is why the public state vocabulary is `hover` / `pressed` / `disabled` rather than either toolkit's words.

**#112 is the only open issue, and it is now built and reviewed on `feat/psg-extension` — not merged.** The design is in the issue body, written 2026-08-12 against a real PySimpleGUI 6.3; the branch is `tkinter_icons.extensions.psg`, its tests, its docs page, and a captured screenshot. **Three review rounds have run and every finding is fixed**; `REVIEW.md` records them, each pinned to the SHA it was read at. Rounds 1 and 2 were on Windows, 2026-08-12, seven findings then six — and round 2's came largely from round 1's own fixes, which is this repository's recurring pattern. **Round 3 is the Linux pass**, run on WSL2 under Xvfb against Python 3.10, and it found the one thing `HANDOFF-LINUX.md` had predicted would be fine: a test asserting a Windows outcome from a Windows-only premise, which failed on X11 against code that was correct and would have failed every Linux CI job. Read the issue rather than re-deriving it; what follows is only what a later session is most likely to get wrong.

**PySimpleGUI's terms were checked, and the answer removed the blocker.** This file used to say to settle that first, because the project's licensing had not been stable. Checked 2026-08-12: PyPI serves **6.3**, classified `License :: OSI Approved :: GNU Lesser General Public License v3`, summarized as "NEW LGPL3 Version 6 released in 2026" — v6 is an open-source relaunch, and no runtime license gate appeared across dozens of windows built that day. **Nothing about PySimpleGUI is redistributed**: it stays a separate installable the user brings, so LGPL is a non-event for this package's own license provided the extension never vendors its source. There is deliberately **no `[psg]` extra** — an extra cannot express "either flavor", and in this project an extra means *an icon pack*, which `check_extras_cover_every_pack` is built around. `verify_packages.py` would tolerate a non-pack extra, so that is a choice to keep the invariant rather than a limitation.

**The module is `packages/tkinter-icons/src/tkinter_icons/extensions/psg.py`.** It grew out of a prototype under `development/`, which is **deleted as of 2026-08-12** now that the module supersedes it — do not go looking for it, and do not recreate it. It works on both the tk and ttk paths. The three findings most likely to be rediscovered the hard way are all on the issue, but the sharpest is this: **the attach must be triggered by an idle callback scheduled when the widget is created, not by `<Map>`.** PySimpleGUI packs the layout and then calls `master.update_idletasks()` to size and place the window, and `update_idletasks` **does not deliver events** — so a `<Map>` binding waits for the first real event-loop pass, by which time the window is already on screen, and the user watches the icons appear and the buttons resize. That is safe because PySimpleGUI never yields to the event loop while configuring an element, so the first idle after `element.Widget` is assigned is the first moment it is fully configured. There is no true per-element finalize hook to use instead: after the ttk style is applied, PySimpleGUI only *reads attributes* on the element, so a property getter would work today and break silently on a reordering.

**A `tk.Button` has no hover state, and reusing the word "active" across the two paths is a trap.** In ttk `active` means hover. On a `tk.Button` it means whatever the *windowing system* says: `button.tcl` defines `tk::ButtonEnter` three times, and win32 and aqua set `-state active` only while the mouse button is already down — so *pressed* — while x11 sets it on entry outright, covering hover and press together. **Do not write either platform's behavior into an assertion**; an early version of `test_the_tk_icon_follows_the_widgets_own_state` did, and failed on Linux against code that was right. The module reads `-state` back off the widget after Tk's class bindings have run, which is correct wherever it runs. The public vocabulary is therefore `hover` / `pressed` / `disabled`, translated per path, which the owner chose 2026-08-12 over mirroring either toolkit's names.

**Theme awareness was raised as an open question, and the answer dissolved it rather than deciding it: `sg.theme()` makes no runtime change.** It is a build-time setting — it selects the colors the *next* window is built with and does not touch a window that already exists, in PySimpleGUI or here. So there is no live signal to follow and nothing was traded away; an icon set at build time is already as current as the button around it. Do not read this as "we chose not to track the theme", and do not build machinery to chase one. It is stated on the page as a caveat, in the changelog, and in `update()`'s docstring. Note this is a *PySimpleGUI* theme; a **ttk** theme change is a different thing entirely — a real runtime event, which PySimpleGUI reaches through `_change_ttk_theme` in seven element packers, and which `IconButton` repairs after because `Icon.map` replays only the last mapping it recorded per widget. Do not "simplify" that binding away, and do not make it answer the event rather than the theme *name*: `style.map()` fires `<<ThemeChanged>>` itself, so the event-driven version is an endless loop that hangs the window.

**Everything from the table down is finished work.** 5.0.0 and 5.0.1 both shipped, and so has all of 5.1.0 except #112; the sections that follow are kept because they record *how*, not because anything in them is outstanding.

| Issue | State |
|---|---|
| #115 | **Closed 2026-08-09**, merged as #135. `style=` on `render_pil`, and one shared `resolve_icon` behind both entry points. |
| #136 | **Closed 2026-08-09**, merged as #137 then re-landed as #138 — see the retarget trap below. |
| #117 | Closed earlier, from #121. |
| #91 | **Closed 2026-08-09**, merged as #139. Tk is no longer needed to import the library or to render. |
| #140 | **Closed 2026-08-10**, merged as #141 after four review rounds. A glyph the font does not carry no longer renders blank in silence — and after rounds 3 and 4, neither does anything else. |
| #144 | **Closed 2026-08-12**, merged as #145. `Icon.to_data()` and `render_data()` — an icon as PNG bytes, for toolkits that take an encoded image rather than pixels. |
| #112 | PySimpleGUI integration, scoped as 5.1 since #71. **Designed but not started**; the issue body now carries the design. The next action, above. |

**#144 exists because #112 needs it, and it is worth knowing why it is not PySimpleGUI-specific.** `render_data` is `render_pil` with the image already encoded — same signature, same resolution, same failures — and it **delegates** rather than reimplementing, because two entry points answering one question two ways is the defect shape behind #115, #140 and the `on_missing` removal. The bytes are **raw PNG, not base64**: Tk's PNG reader takes binary data directly, so encoding costs about a third more (1,064 B against 796 B at 24 px) and buys portability only to Tk 8.5, which cannot read PNG at all. Nothing is cached, though the issue proposed an `lru_cache` — `render_pil` does not cache, and the expensive part, loading and sizing the font, already is.

**Both `to_data()` and `render_data()` ship, and the division is not just symmetry.** `Icon.__init__` takes no `icon_set`, so the explicit-set path is reachable only from the classmethod. Two things measured while settling that, both worth not re-deriving: constructing an icon renders **nothing** — `_img` stays `None` until `.image` — and `to_data()` never populates or reads that cache, so **`.image` and `to_data()` are two pipelines and neither warms the other**; an icon already live on a widget still pays a full re-render to hand you bytes. And the global side effect of constructing a pack icon (`initialize_with_provider` sets the process-wide active set) **cannot bite a pack class**, because a class with a `provider_class` takes `render_pil`'s resolving branch and never reads `_icon_set_current`. Only bare `Icon` reads it, which is what the library's own error message already tells you not to use.

**`PLAN.md` and `REVIEW.md` were reset with #145, closing the loose end this file used to flag.** #140's four rounds are in git history and their outcomes are in `CHANGELOG.md` and here; a plan kept past its merge is a second copy of the truth. The standing rule is now explicit: each branch resets both, and the reviewing session's scope is pinned to a SHA in `REVIEW.md`.

**What #140 turned out to be, since the plan had one half of it wrong.** The lookup guarded the glyph *map*; nothing guarded the *font*. A name in a pack's glyph map whose codepoint the font does not carry drew a fully transparent image with no exception and no warning — not even for a caller who had explicitly asked to be told about names that could not be drawn, because from the glyph map's point of view nothing was missing. **121 glyph-map entries** were in that state: 119 in `gmi` (43 outlined, 38 round, 38 sharp) and 2 in `mat`. Counted per name *per style*, the way the placement census counts, that is **123** — `mat`'s two styles share one glyph map, so its 2 entries are counted twice. Both numbers are correct and they measure different things; quote neither without saying which.

**The two root causes are different, and `PLAN.md` guessed the second one wrong.** `gmi` was as described: one downloaded *baseline* codepoints file written verbatim to all four style glyphmaps, under a comment asserting the styles share codepoints. `mat` was **not** "one style's truth published as every style's" — its two styles are genuinely one font split by a name predicate, so one shared glyph map is correct. Its actual fault is that the map is scraped from upstream's **CSS**, and MDI's CSS declares `mdi-blank` at U+F68C as a deliberately empty placeholder the webfont has no codepoint for. `glyphmap_from_ttf` is only the fallback there and was never reached. **Read the generator before trusting a written-down root cause** — the shape of the fix survived, but the mechanism did not.

**The fix has two halves, and one shared helper.** `tooling.restrict_to_font` intersects any assembled mapping with the real font's cmap and both generators now call it, so a regeneration cannot reintroduce this. The committed data was fixed by running that same code path locally rather than by re-downloading: `gmi`'s generator pulls fonts from `master`, so a regeneration would have silently moved the pack off its pinned 0.14.15. `write_glyphmap` reproduces the committed files byte-identically, which was checked first, so the data diff is 121 removed lines and nothing else.

**Three separate instruments had been reporting this all along and nobody had pointed them at it.** The census recorded `glyphmap_entries` 123 above `drawing` — the unexplained 123-glyph discrepancy from round 2 of the #121–#125 docs review, which was never a counting error. `without_metrics` was *also* exactly 123. And `metrics-outlined.json` had always held 2,191 entries against a glyph map advertising 2,234, because ink measurement skips a glyph with no ink. All three go to zero now. **When two generated artifacts disagree by a constant, that constant is a finding.**

**The runtime guard reads the font's cmap without adding a dependency.** Pillow cannot report a font's coverage — it draws `.notdef` and says nothing — so `tkinter_icons/sfnt.py` parses the `cmap` table directly rather than making `fontTools` a third runtime dependency. It is checked against `fontTools` on all 31 font/style combinations the project ships. **Every failure path returns `None`, meaning unknown, never an empty set** — an empty set would claim the font carries nothing and blank an entire pack. Parsed once per font and cached; ≤8 ms for the largest pack.

**That parity test exercises formats 4 and 12, and this file said 0, 4, 6 and 12 until 2026-08-09.** The shipped fonts do carry sixteen format 0 subtables and three format 6 ones — but all of them on platform 1, which `_is_unicode_encoding` rejects *before* the format dispatch, so no shipped font ever reaches those two parsers. Instrumenting them and running the whole suite records zero calls. The claim was true of what the files contain and false of what the test reads, which left two parsers shipping with no coverage at all; they are covered against constructed subtables now, and the docstring says that is the weaker instrument. **A format a font contains is not a format your parser runs** — the filter in between is the whole point of the module.

**Coverage is stored as sorted ranges, not as a set of codepoints.** 17.4 KB for all 31 styles against 5,792 KB, a factor of 333; membership is a `bisect` at 0.18 µs against a hash lookup at 0.04 µs. **State the definition with the number**, and this paragraph has now been wrong twice for the same reason. Ranges are `Coverage.nbytes`, the bounds buffer alone — measuring the array *object* instead gives 19.9 KB, which is how the first draft disagreed with itself. Sets are the old `frozenset` plus its int objects, **built from a `set` as the old code built it**: freeze a list of the same codepoints and CPython presizes differently, giving 6,400 KB and a factor of 368 rather than 333. Round 3 of the #140 review caught the second one, and the lesson is that "state the definition" means a definition someone can *execute*, not a phrase that sounds specific. The extremes are also two different fonts: the biggest set is `fluent:filled` at 741 KB (two ranges, 16 bytes), the biggest bounds array is `fontawesome:solid` at 5,672 bytes (709 ranges, the most fragmented coverage shipped). `Coverage.nbytes` is public so the representation can be regression-tested, because every correctness test in the suite passes either way. The same change removed the unbounded format 12 enumeration that round 1 of the #140 review deferred as a nit: groups are emitted as ranges rather than walked.

**`on_missing` is gone as of 5.1.0. A name that cannot be drawn always raises.** Two owner decisions a day apart, and the second superseded the first: on 2026-08-09 the default flipped from `"transparent"` to `"raise"`, and on 2026-08-10 the setting was removed outright. `ValueError` for a name a pack cannot resolve, `KeyError` for one that reaches an icon set with no glyph for it, and neither returns an image.

**It was never a designed feature, and reading the history is what settled it.** 4.0.x's `_render` returned `Icon._get_transparent(self.size)` for any name its glyph map lacked — no option, no warning — and #67's renderer rework (`e1063b8`) preserved that as the default while adding `"warn"` and `"raise"` as ways out. So the policy existed to escape the old behavior rather than to offer a choice, and its default carried the old behavior into 5.0.0 and 5.0.1. **The case it was justified by is unreachable in this repository**: nothing sets it — not the browser, not the placement census over 178,584 renders, not the two docs extensions that render every pack's previews — because they all iterate names taken from the glyph map and so cannot produce one the map lacks. Do not reintroduce it for a hypothetical bulk renderer; `try`/`except` is the answer, and it ends with the list of names that failed rather than a directory of blank PNGs.

**Two things were quietly relying on it, and both were found by something failing rather than by anyone reasoning.** The `"none"` sentinel drew a blank by falling through the missing-name path, so it had always raised for anyone who set `"raise"`; it is `providers.NO_ICON` and is answered before the lookup on both paths now. And `_render` read the policy off `Icon` with the class named literally while `render_pil` read it off `cls`, so a policy scoped to a pack subclass was honored headlessly and ignored on the Tk widget path — round 3's blocking finding, and the same "two entry points answer one question two ways" defect as #115 and #140, in the file that closes it. Message building is a module-level `_missing_glyph_error` that *returns* the exception, so there is no class state left for two call sites to read differently.

**One residual sharp edge, deliberately not fixed.** `Icon.on_missing = "transparent"` still assigns cleanly, because `__slots__` governs instances and not the class, so a line left over from 5.0.x is inert rather than loud. Catching it needs a metaclass — `Icon` is already `ABC` — which is more machinery than the setting ever justified. The changelog tells readers to delete the line.

**The check lives in `IconSet.glyph`, not at the call sites.** That is what makes it reach the Tk widget path as well as `render_pil` — the browser drawing blank tiles was this bug's most visible symptom, and `_render` has its own lookup. Duplicating the check at both sites would have set up the next #115. Consequence worth knowing: `len(icon_set)` and `name in icon_set` now mean "can be drawn" rather than "is in the map", and **that made a latent bug reachable** — `render_pil` selected its set with `icon_set or cls._icon_set_current`, and an `IconSet` is sized, so a set that can draw nothing is falsy and the caller's set was silently replaced by whichever loaded last. It selects on `is None` now. Any `or` over an object with `__len__` is that bug waiting.

**Two facts about the base `Icon` that round 4 turned up, both from one wrong docs comment, and both easy to get backwards.** *Installing a pack does not give `Icon` a set — constructing one does.* `Icon._icon_set_current` is set only by `initialize_with_provider`, and nothing calls it at import time, so a cold interpreter with all sixteen packs installed still raises `RuntimeError: No icon set available` from `Icon.render_pil`. That is the #102 review's cold-process trap in a second costume, and it is why the docs example for the new `KeyError` now constructs a `MaterialIcon` first and says why that line is there. *And the constructor never passes a style through:* `icon_set_id` is `f"{provider.name}:{style or 'default'}"` but `__init__` calls `initialize_with_provider(prov)` with no style, so even `BootstrapIcon("house", style="fill")` leaves the active set at `bootstrap:default`. A set id like `mat:outline` is reachable only from an explicit `Icon.initialize_with_provider(provider, "outline")`, which appears in no example — so a docs comment naming one is wrong by construction, not by drift.

**`tests/test_docs_examples.py` cannot see any of that.** It resolves only calls whose class is a pack class in `INSTALLED`, so every example written against the base `Icon` is outside it — which is exactly where the wrong comment was. Worth knowing before trusting that check to cover a page.

**Nothing is waiting on a tag, and 5.1.0 is uncut by decision rather than by omission.** `[Unreleased]` in `CHANGELOG.md` holds #115, #136, #91 and #140, all merged; the owner's call on 2026-08-10 is that the milestone is not ready. Whenever it is cut it goes out through the tag-driven path, which is proven as of 5.0.1. The one tag carries the base plus `gmi` and `mat` at **1.1.2**, with the other fourteen packs skipping existing — which is #97 working as designed.

**One lesson from #91's review worth keeping, because it is the same trap as #140.** A test hand-rolled the four steps `render_pil` encapsulates and dropped `icon_set.glyph(name)`, so it drew the *name* `"house"` as text rather than the icon. It passed: no pack's font maps ASCII, every letter renders `.notdef`, and Bootstrap's `.notdef` is a tofu box, so five boxes satisfied an ink assertion. **`resolve_icon` returns a glyph name; `render_glyph` takes a character.** And the deeper point — asserting on ink is necessary but not sufficient, because `.notdef` is ink. Three `assert "tkinter" not in sys.modules` lines were removed in the same pass for the opposite reason: they could never fail, since the import machinery drops a failed import from `sys.modules`.

### Two mechanical lessons from landing that stack, 2026-08-09

**A stacked PR merges into its base, not into `main`, and GitHub will let you do it.** #137 was based on `feat/render-pil-style`. When #135 merged to `main`, GitHub did **not** retarget #137 — it retargets on branch *deletion*, which is the one thing you must not do mid-stack. Merging #137 then put the browser work onto `feat/render-pil-style` and nowhere else: `main` never received it, and `Closes #136` was discarded because GitHub only honors it on a merge into the default branch. It looked entirely successful — both PRs showed MERGED. #138 re-landed it from `feat/render-pil-style` → `main`.

So after merging any parent in a stack, **check the child's base before merging it**, and check `main` actually received the code rather than trusting two green badges:

```bash
gh pr view <child> --json baseRefName          # must say "main"
git merge-base --is-ancestor origin/<branch> origin/main && echo on-main || echo NOT-on-main
```

**A branch can be merged and then pushed to again, so a merged PR does not mean a merged branch.** `docs/handoff-5.0.1-released` was exactly this: PR #134 merged 2026-08-08, and `f0c5cbf` was pushed to the branch afterwards and is on `main` nowhere. `git log --oneline origin/main..origin/<branch>` is the check, and it is the same one the janitorial sweep already prescribes.

**That one is now closed out, and how it ended is the part worth keeping.** The branch is gone from `origin` as of 2026-08-10 — remote heads are `main` and `release/ttkbootstrap-icons-packs-final`, nothing else — and `f0c5cbf` is still not an ancestor of `main`. **The closed-PR safety net does not cover it**: `refs/pull/134/head` serves `7bb1712`, the tip as of the merge, *not* the commit pushed afterwards. So the rule stated under the janitorial sweep — "a closed PR's head ref is the safety net" — holds only for a branch that was never touched after its PR closed, which is precisely the case this paragraph exists to warn about. Nothing was lost: that commit restructured this file's "Next session" section, its idea was absorbed when the section was rewritten for a world where #115 was done, and the section has been rewritten twice more since. There is nothing left to land, and the only surviving copy is in this clone.

### The docs stack merged, 2026-08-08 — #121 through #125

**All five are on `main`, the five branches are deleted, and `origin` carries only `main` and `release/ttkbootstrap-icons-packs-final` again.** #117 closed from #121. **#87 stayed open by design at the time** — #123 shipped the generated figures only, and the three real-window captures were split off. Those landed later the same day in #130, which closed it.

**Three review rounds ran on that stack, and each round's fixes produced the next round's findings.** That is the fact worth carrying, not the individual defects. Rounds 2 and 3 were largely *corrections being corrected*, which is a different failure from sloppy original work and wants a different remedy — stop transcribing, commit the measurement.

- **Round 1** — seven findings. A padded-box guide drawn with `round` where the renderer uses `int`, so the exemplar glyph crossed its own guide. `image-rendering: pixelated` on three figures displayed 1:1. A census that said "every glyph in all sixteen packs" over default styles only. An over-broad MB regex. A dead `Panel.size` whose use would have made a difference-assertion pass unconditionally. Two modules each declaring `PackNotInstalled`.
- **Round 2** — four. Two figure-subject numbers quoted from a 400-name sample. An unexplained denominator, which cost the reviewer a 123-glyph discrepancy they could not resolve. **The MB guard narrowed to three filenames — a regression introduced by round 1's own fix.** A missing blank line that made Markdown fold "it is gone" into the `release/ttkbootstrap-icons-packs-final` bullet.
- **Round 3** — seven, five of them numbers. The published "measured ink fills 94% to 102% of the padded box" describes something `_place_by_ink` cannot do, since it fits ink to that box and never enlarges past it. It survived because round 1's *correct* fix to `padded_box_inset` was never propagated to the prose derived from the old float arithmetic. Also `IDENTICAL`'s justification quoting a replaced figure's score, and `render_figures.setup()` re-asserting the parallel-write argument `pack_showcase` had just been rewritten to disown.

**The census is a committed artifact now, and that is round 3's answer to why round 2's fixes were themselves wrong.** Three sessions measured it with a throwaway snippet and transcribed the result by hand into four files, and the numbers disagreed every time — including once where a *correct* fix to `padded_box_inset` was never propagated to the prose derived from the old arithmetic. `.github/scripts/generate_placement_census.py` does the measuring, `docs/_data/placement-census.json` holds the result, and `tests/test_placement_census.py` checks all four files against it. Regenerate with the script, never by hand; `--check` runs in CI's docs job and verifies the tree. It is 178,584 renders and takes about 20 seconds, so the reason it is a committed artifact is not cost — it is that it needs all sixteen packs installed, which the test matrix deliberately does not guarantee.

**The definitions are the substance, not the numbers.** Round 3's review reported Weather's off-center as 9.0 px or 9.5 px depending on how it measured, against the documented 10.0 — and all three were defensible readings of an undefined phrase. Fill is now the longer side of the drawn glyph over the renderer's own padded box (`canvas - 2 * int(canvas * pad_factor)`, **not** the float `canvas * (1 - 2 * pad_factor)` — that discrepancy is what produced the impossible "ink fills up to 102%"), and off-center is the distance from the drawn glyph's center to the frame's. Quoting either figure without its definition is what made three rounds of correction possible.

**Settled — decisions, not defects. Do not re-open these:** the even-snapping figure was drawn, looked at, and deleted because a PNG cannot reproduce a 150% display scale; `tests/test_render_figures.py` deliberately refuses to judge whether a figure *reads*, because a pixel metric ranked the rejected subject above its replacement; `icons-and-names` reuses `pack-preview:: bootstrap` rather than growing a second directive.

**Verify with**, in a checkout with every pack installed:

```bash
.venv-home/Scripts/python.exe -m sphinx docs docs/_build/html -b html -W --keep-going -n -j auto
.venv-home/Scripts/python.exe -m pytest -q                       # 811 total, e.g. 797 passed 14 skipped
.venv-home/Scripts/python.exe .github/scripts/generate_placement_census.py --check
.venv-home/Scripts/python.exe .github/scripts/verify_packages.py --strict
.venv-home/Scripts/python.exe .github/scripts/generate_pack_readmes.py --check
```

Read the venv note under "Environment" first — which of `.venv` and `.venv-home` works depends on the Windows login, and the wrong one fails with `Access is denied` on the exe itself.

**Merging that stack taught one mechanical thing this file had wrong, and it is under "Conventions" now: GitHub does *not* retarget a stacked PR when its base merges.** It retargets on branch *deletion* — which is the one thing you must not do mid-stack. Retarget each child by hand with `gh pr edit <n> --base main`, and check the base before every merge.

---

**The release is finished. Nothing about 5.0.0 is outstanding.** All eighteen distributions are on PyPI, the tag is pushed, the GitHub Release is cut and corrected, Trusted Publishing is configured and verified, and every install line on every docs page and README now resolves. Do not re-run the dry run, re-review, or re-derive the publish order — all of it was done against this tree.

**The next release can be tag-driven, and that path is now proven rather than assumed.** Push `v<version>` and the workflow builds all eighteen, publishes what PyPI does not have, and cuts one GitHub Release. The one caveat is the permanent red run on `v5.0.0` described in Current state, which is specific to that tag.

**The janitorial list is finished, 2026-08-08.** Read the Docs' Default branch is back on `main`, GitHub Pages is unpublished, and eleven remote branches are deleted including `gh-pages`. A second sweep later the same day removed five more remote branches and twenty-two local ones, so both sides now carry only `main`, whatever is in flight, and `release/ttkbootstrap-icons-packs-final` — **leave that last one alone**, it is the only tree where the sixteen old packs still exist. As of 2026-08-10 nothing is in flight: `origin` carries those two heads and no others.

Three local branches were not ancestors of `main` and each was checked rather than assumed, which is the rule below working. `docs/pre-tag-review-fixes` and `docs/release-complete` each carried one commit whose **patch id** matched a commit already on `main` — the same work re-applied, safe to drop. `fix/release-latest-marker` genuinely held a commit that is on `main` nowhere: `e7e7d32`, which is #96, closed unmerged and superseded by #97. It was deleted only after confirming GitHub still serves it at `refs/pull/96/head`, so `git fetch origin refs/pull/96/head` brings it back. **A closed PR's head ref is the safety net for exactly this case** — check it before deleting the last copy of anything.

Two of the eleven were not ancestors of `main` and both were checked rather than assumed. `docs/release-complete` carried one commit past its own merge, `05077d4`, whose patch is byte-identical to `491dae8` on `main` — the same work re-applied on `docs/milestone-split` and merged by #119. `fix/release-latest-marker` is #96, closed unmerged and superseded by #97, exactly as recorded. **Verify with `git merge-base --is-ancestor origin/<branch> origin/main` before deleting**, and when it says no, find out why rather than trusting a PR's merged badge — a branch can be merged and then pushed to again.

**Both old docs URLs now return 404, and `migrating.rst:44` is true as written** — it was not, for the whole 5.0.0 cycle. See the docs-URL entry under "Deliberate decisions" for what was wrong and how it was found. Note the site was unpublished *before* the branch was deleted, which is the order that matters; the Pages API record can linger with `status: built` after the site is already serving 404, so **`curl` is what tells you the site is down and the API is what tells you the configuration is gone**. They disagree for a while, and neither alone is the whole answer.

**The follow-up work is milestoned, and the split is deliberate.** The 5.0.0 milestone is closed; what outlived it moved to **5.0.x Fixes and Cleanup** and **5.1.0**.

**5.0.x — one `v5.0.1` tag publishes the base 5.0.1 and `tkinter-icons-gmi` 1.1.1 together**, with the other fifteen packs skipping existing. That is #97 working as designed: distributions carry different version numbers, one tag ships them.

| Issue | What |
|---|---|
| #118 | The `3.14` classifier is on `main` but frozen out of the published wheel, so the pyversions badge reads up to 3.13. Needs no code change — it needs a release to carry it, and it is the reason the base is in this one. |
| #111 | `gmi` claims a `twotone` style; the provider ships four. Wrong in **two** frozen places — the README *and* the `description` field in its `pyproject.toml` — so it needs a pack release, not a docs edit. Fix the README's intro paragraph, the one hand-written part `generate_pack_readmes.py` preserves. |
| #117 | The `on_missing` scope sentence in `icons-and-names.rst:72` describes a case that cannot occur. Docs-only; split out of #115 so it can ship in a patch. |
| #87 | **Closed 2026-08-08.** The generated renderer figures (#123) and then the three real-window screenshots (#130). Both shipped on merge via Read the Docs rather than with the tag, which is why it never blocked the release. |

**5.1.0 — moved to the top of this section, since it is the live milestone.** #115, #136, #91, #140 and #144 are all closed and merged. **#112 is the only one left, and the only open issue in the repository** — see the table at the top of this section. The milestone is complete apart from it, and uncut by decision.

**Two numbers from #115 that this file had wrong, and which are now pinned by a test.** The issue's headline was **814** names rendering blank; the measurement that shipped is **849** newly resolving, over 288,418 combinations — every name once with no style, and once against each style its own pack has. The changelog first said 867 over "365,051 combinations", and neither reproduced; `TestTheDefaultStyleStoppedBeingAGate` now pins the per-pack breakdown against a frozen transcription of the old default-only rule, because a comparison against a moving `main` is not a check anyone can re-run. **Quote neither figure without the population definition** — that omission is what made three wrong versions of it look equally plausible.

### Doing 5.0.x — the plan, in order

**All three steps are done — 5.0.1 shipped 2026-08-08.** Kept as a record of what a tag-driven release actually takes, since the next one follows the same path. The only item that did not close with a PR was **#118**, because the classifier needed no file change and the release alone carried it; it was closed by hand afterwards. **The 5.0.x milestone is empty — 0 open, 8 closed** — so nothing in this section is outstanding.

**1. Read the Docs' Default branch is back on `main`** — confirmed by the owner 2026-08-08. Docs-only merges are visible again.

**2. The work that needs no tag is merged**, 2026-08-08 — #121 through #125, which grew from the planned stack of three when two review rounds were folded in. #117 is closed, and **#87 closed afterwards from #130**. Nothing in 5.0.x now depends on a merge.

**3. Then cut `v5.0.1`. This is the only step left, and it is not started.** This is the first tag-driven release — publishers are configured and verified, so pushing the tag is the whole procedure. No manual upload, no `.pypirc`.

**What the tag needs prepared first:**

- **#118 needs no file change.** The classifier is already on `main`; the base version comes from the tag through setuptools-scm. The release exists to carry it.
- **Fifteen packs are already prepared and sitting at 1.1.1**, #111 and #120 together — see below. Each has its `version`, its `description`, its README intro and its own `## [1.1.1]` changelog entry. Those four are coupled: `verify_packages.py`'s `check_changelog` requires the newest changelog entry to *be* the version being shipped, and the release preflight runs `--strict`, so a bump without an entry fails the release rather than shipping quietly. `fluent-reg` is the sixteenth and stays at 1.1.0 — its intro was already the model the other fifteen were rewritten toward.
- **The root `CHANGELOG.md` section is written — `## [5.0.1] — updated metadata and docs`, in #132.** The title is the owner's and `release_notes.py` lifts it verbatim now that #113 stopped passing the distribution name, so a future one stays short: "renamed to tkinter-icons, rebuilt around measured glyph ink" was too long even before the prefix stuttered it. Prose **unwrapped**, one line per paragraph.
- **Read the generated body before tagging**, which is not the same text as the changelog section. The last argument is the GitHub-output *file*, and `/dev/stdout` does not resolve on Windows — this file said it did, and `release_notes.py` dies with `FileNotFoundError` on `/proc/self/fd/1`. Pass a real path and read it:

  ```bash
  python .github/scripts/release_notes.py CHANGELOG.md 5.0.1 NOTES.md gh-output.txt
  ```

  There is no distribution argument any more. `gh-output.txt` is appended to, not truncated, so a second run leaves two `title=` lines and the last one is current.

The other fifteen packs are untouched and skip-existing. One tag ships the base at 5.0.1 and `gmi` at 1.1.1 together.

**The guard is written: `tests/test_pack_style_claims.py`.** It checks each pack's `description` and README intro against its provider's real `style_list`, and it was confirmed both ways — clean on the corrected tree, and failing on `google-material` the moment `twotone` is put back. Two exemptions are deliberate and both were found by the check failing on honest text. A pack with an **empty `style_list` is skipped**, which is the `fluent-reg` allowance `CLAUDE.md` always demanded: with no selectable styles there is no `style=` to misrepresent, so "Regular" names the font. And **hyphen components count as shipped**, because Devicon ships `plain-wordmark` and `original-wordmark`, so "wordmark" on its page names something real. The cost is that the seven style-less packs are skipped — 14 of the 32 cases — which is stated in the test rather than left for someone to discover from the summary line.

Note what neither existing check caught. `generate_pack_readmes.py --check` was green throughout, because the *generated* body lists the real styles from the live provider — so `gmi`'s page contradicted itself and both checks passed. The wrong text was in the two places nothing generates: the summary line and the hand-written intro.

**#120 is the bigger version of that finding, and it changes how large 5.0.1 is.** The pack README intros are written in upstream's voice — fifteen of sixteen, thirteen of them from one template: *"An icon provider for the `tkinter-icons` library. &lt;Upstream project&gt; &lt;marketing sentence&gt;."* Two things are wrong beyond the voice. **"Provider" is developer vocabulary** — #79 split that API out precisely because a consumer writes `from tkinter_icons import EvaIcon` and never touches a `BaseFontProvider`, yet it is the first noun on almost every pack's PyPI page. And the trailing sentence carries upstream's facts and upstream's framing, including "a single TTF font", which contradicts the positioning that users should never have to think about the font at all. `gmi`'s `twotone` claim is what that produces when upstream's copy goes stale.

`fluent-reg` is the model to copy — it names the pack's role here, is honest about shipping one style, and points at `[fluent]` for people who want more. `meteocons` is the one intro whose upstream reference is **load-bearing**: the Alessio Atzeni attribution stays, for the licensing reasons under "Meteocons" below. `bs` has no characterization at all, just a line and an inline badge.

**Scope decided 2026-08-08: all fifteen ship in 5.0.1.** The alternative was `gmi` alone — it is the only one publishing a false claim, where the other fourteen were publishing accurate text in the wrong voice — with the rest deferred to 5.1.0. The owner chose the wider scope, so 5.0.1 is fifteen bumps to 1.1.1 and fifteen changelog entries carried by the one `v5.0.1` tag. It is no longer a small patch, and that was the deliberate call rather than momentum.

**The distribution `description` was rewritten alongside the intro, which goes slightly past #120's title.** #120 names the README intros, but the summary line carries the same "provider for tkinter-icons" framing, is frozen at release time in exactly the same way, and is the *first* text on a PyPI page. Fixing one and not the other would have paid the whole cost of a fifteen-pack release for half the result. Every summary now reads `<Set> — an icon pack for tkinter-icons`, with the real styles in parentheses where the old one enumerated them.

**Do not touch the 5.1.0 items** — that instruction was for the 5.0.1 patch and is spent: #115 and #91 have both been done since, in that order. It is kept because the reasoning generalizes — items sharing one surface are cheaper as one pass, and pulling one forward into a patch gets the ordering wrong. And **do not move `v5.0.0`** for any reason; `v5.0.1` was cut normally at the new tip.

**Two lessons from finishing this release, both cheap to forget.** A generated artifact is only as good as the moment you read it: the release body was hard-wrapped and its title stuttered a distribution-name prefix left over from the retired eighteen-tag scheme, and neither was visible until the rendered page was read (#113). And a red CI run on a docs-only PR is worth diagnosing rather than re-running — the one on #110 was a genuine order-dependent test bug that had been passing or failing on entry-point ordering for however long (#114).

### What the #102 review found, and the two traps in it

The mechanics are on the issue. What is worth carrying forward is the shape of the mistakes, because none of them moved a check.

**A README on PyPI is frozen at release time, and that changes when a README bug must be fixed.** This is the one that nearly went wrong. The sixteen pack READMEs were known off-idiom, tracked as #90, and the obvious call was to ship and fix afterwards, since every install line and import in them resolved. That call was wrong: `curl https://pypi.org/pypi/tkinter-icons-lucide/json` returned **404**, because the sixteen `tkinter-icons-*` distributions do not exist until the tag creates them. So they were not stale pages to tidy later, they were sixteen first impressions — and deferring meant sixteen *extra pack releases*, not sixteen commits. **Check whether a page exists before deciding it can be fixed later.** #105 generated them instead.

**Prose that repeats a number is worse than prose that contradicts itself,** because nothing looks wrong. "About 17 MB" appeared in `packs.rst`, `packaging.rst` and `CHANGELOG.md`, in perfect agreement, and was wrong on either reading — the real figures are 21.86 MB installed and about 8.27 MB compressed. Cross-document consistency checks find disagreement; they do not find a number nobody ever measured.

Three more, each fixed and each invisible to `pytest`, `sphinx -W` and `verify_packages.py`:

- The 5.0.0 changelog opened with a **shell command inside a `python` fence** — the first code on the GitHub Release page, and a `NameError` if copied. Generate the release body with `release_notes.py` and *read it* before tagging; it is not the same text as the changelog section.
- "`Icon` itself still raises" was true only in a **cold process**. Construct any pack icon first and the base `Icon.render_pil` succeeds from whichever set loaded last. Test claims about fresh state in a fresh interpreter.
- The #105 generator first wrote "**reproduced in this package under `LICENSES/`**", which is false for the eight packs whose `LICENSES/` holds a summary and a link — `gmi`'s is six lines pointing at apache.org. A generator multiplies a wrong sentence by sixteen.

**Two facts a later reader will otherwise rediscover the hard way.** The multi-style packs store `metrics-<style>.json`, not `metrics.json`, so a naive existence probe falsely reports `fluent`, `fontawesome` and `google-material` as shipping no metrics. And all 93 `.. code-block:: python` blocks in the docs now execute cleanly apart from fragments that reference an earlier block on the same page — but two of the headless-rendering examples **write into the current directory**, so run them from a temp cwd or they leave `home.png` and `icons/` in the repo.

**Docs examples are checked now — `tests/test_docs_examples.py`, added 2026-08-09.** It parses every `code-block:: python` with `ast` and resolves each call whose icon name *and* style are string literals, 140 of them, against the live provider. It exists because the block introducing `style=` on `render_pil` shipped `FontAwesomeIcon.render_pil("house", style="regular")` — a name that exists only in `solid`, so the example for the feature the release adds raised for everyone who copied it, with `sphinx -W` green throughout. Examples that fail *on purpose* live in `DELIBERATE_FAILURES` and are asserted to keep raising, and an exemption naming an example nobody shows any more is itself a failure. **It only reads literals** — anything built from a variable or a loop is out of scope, because resolving those means running the block, and two of them write files into the cwd.

**The milestone is closed, and #90 with it.** #67–#71, #75, #79 and #89 closed as of #100; #90 closed from #105, #87 from #130. #91 outlived the milestone and closed 2026-08-09 from #139.

### What building the figures found, 2026-08-08

**A page's central claim was backwards, and only drawing it exposed that.** `sizing-and-quality` said `getbbox` "makes full-bleed glyphs slightly too large — they end up with no padding at all, touching the edges". `_place_by_bbox` only ever *shrinks* a glyph that overflows, so a glyph fitted that way lands **inside** the padded box: a per-pack median of 72%–95% of it against 92%–100% on the ink path. The touching is real but comes from the other half of the function — vertical centering is against `ascent + descent` rather than against the ink. Census over every glyph in **every style** of all sixteen packs, each with its own pack's options: **518 of the 89,169 glyphs that draw ink overflow on the fallback path, 0 on the measured one.** The same wrong sentence was in `_place_by_bbox`'s own docstring; both are fixed in #123.

**That number was wrong once, in the direction that flatters.** The first census iterated each pack's *default* style only — 48,082 glyphs — and the prose said "every glyph in all sixteen packs". It covered a little over half of them, and it excluded exactly the non-default cuts a user reaches through `style=`. **Iterate `provider.style_list`, not just `default_style`**, whenever a claim is about the whole library; the shortcut is easy to write and the resulting sentence is unfalsifiable by a reader.

**Measure with the options the thing actually uses.** The first subject for that figure was a Font Awesome glyph, picked from a sweep run with the *default* `RenderOptions`. Font Awesome's provider asks for `pad_factor=0.15`, so under its own options the two panels came out nearly identical. A sweep that does not use the real defaults ranks the wrong candidates first.

**And then look at it.** The rejected Font Awesome pair scores a pairwise alpha difference of **0.243**; the Eva pair that replaced it scores **0.185**. A pixel metric ranks them the wrong way round, so `tests/test_render_figures.py` deliberately does not try to judge whether a figure *reads* — its floor is 0.02, which catches panels becoming identical and nothing more. That limit is stated in the test's own docstring rather than left implied.

**A figure that cannot show its claim was drawn and deleted.** Even-snapping is about a half-pixel boundary *at fractional display scaling*, and a PNG in a browser cannot reproduce a 150% Windows scale factor — 15 pixels beside 16 shows two sizes of one icon and nothing about blur. Prefer no figure to a figure that quietly argues against the paragraph beside it.

**Two extension modules must not each declare their own `PackNotInstalled`.** `render_figures` originally copied `PackNotInstalled`, `pack_by_extra`, `provider_for` and `INK` from `pack_showcase` rather than importing them. Two classes of the same name are two unrelated exceptions, so the first time anyone reached for one more helper across the boundary — which `save_atomic` already made the natural next edit — a missing pack would stop degrading to a warning and start crashing the build. They are imported now. **`note_self` is the one that must stay local**: it registers `__file__`, so the imported copy would note the wrong module and reintroduce the stale-page bug it exists to prevent.

**`pack_showcase`'s parallel-safety reasoning changed and had to be repaired, not just relied on.** It declared `parallel_read_safe` partly because each preview path was written by exactly one document. Putting `pack-preview:: bootstrap` on `icons-and-names` makes that false — two workers, one path. Every write in both extension modules now goes through `pack_showcase.save_atomic`, which writes beside the target and renames. **If you add a directive that writes an image, route it through that**; the old invariant is gone and the comment asserting it has been replaced.

**Two more stale claims the prose pass caught, both of the "nothing was reading it" kind.** `installation.rst` still said "roughly 17 MB" — the figure #102 found wrong in three files and #104 corrected in two, missed because it was worded differently. And it still said "Tested on 3.10 through 3.13" after #109 added 3.14 to the classifiers *and* the CI matrix, which pin each other and therefore both went green. Guards for both are in #122: `TestTheCostOfInstallingEverythingIsMeasured` sums the installed packs rather than comparing documents, and `test_the_installation_page_names_the_same_range` adds the docs as a third direction on the version range.

**The pack READMEs are generated now, and hand-editing one will be reverted by CI.** `.github/scripts/generate_pack_readmes.py` writes all sixteen from `KNOWN_PACKS`, each live provider, and `pack_showcase.SHOWCASE` — the same table the docs previews use, so a README and its docs page cannot disagree. `--check` runs in CI's docs job; `TestPackReadmesTeachTheExtrasIdiom` covers the install line, the import root and the absence of a bare install on all five platforms without needing `docs/_ext`. The only hand-written part is the intro paragraph under the H1, which regeneration preserves verbatim. If you want to state a fact on one of those pages, add it to the generator.

**Two rules the owner stated this session, which outlive it.** Prose is written
**unwrapped** — one long line per paragraph in markdown, PR bodies, and commit
messages, because GitHub wraps text itself and manual breaks fight it. And when
documentation describes a feature the code does not have, **build the feature**;
do not quietly rewrite the docs down to match what ships. Both are recorded in
`~/.claude/projects/…/memory/`.

**Working style, learned the hard way this milestone:** push and open the PR,
then stop. Do not merge, and do not close milestone issues by hand.

**The checks do not read prose, and this milestone kept proving it.** `pytest`, `verify_packages.py --strict`, `generate_metrics --check` and `sphinx -W` were all green while the shim's PyPI page told users to run an install command that cannot work, the migration guide asserted the opposite of what 4.0.0 shipped, and the ttkbootstrap examples taught an API that project has retired. Every one of those was found by a person reading, and each was then fixed *and* narrowed by a guard where a guard was possible — `TestReadmesDoNotAdvertiseExtrasThatDoNotExist` is that pattern. When a docs bug is found, ask what would have caught it, and add that if it is cheap; where it is not cheap, say so in the issue rather than pretending the fix was the whole job.

**Docs images split in two, and the split is the point.** Anything that illustrates the *renderer* is drawn at build time by `docs/_ext/render_figures.py` and `pack_showcase.py`, so it cannot go stale. Anything showing *real widgets in a real window* has to be captured, and those are `.github/scripts/capture_screenshots.py` — one command that rebuilds all four from the examples their pages publish, rather than an afternoon of framing windows by hand. It needs a desktop session and is deliberately in no workflow: a headless runner yields a crash or a black rectangle, and a black rectangle is the failure that gets committed unnoticed. The `ttkbootstrap` pair is skipped unless you run it from a throwaway venv, for the usual reason. **Look at every capture before committing it** — the first run produced a quickstart window 146 px wide with its own title clipped, and the theme pair titled "bootstrap-…", neither of which any exit code reports.

**Do not paste an install command, an import, or an API call into documentation without running it.** The ttkbootstrap rewrite was verified in a throwaway venv precisely so the working venv stayed as this file describes it; that is the pattern to copy, not an unusual precaution. Note the API surface is easy to get wrong from memory even when the docs are right: `render_pil` is a **classmethod** taking the glyph name — `MaterialIcon.render_pil("home", size=32)`, not `MaterialIcon("home", size=32).render_pil()`.

---

## What #71 built

**Shipped in PR #85; this section is now a record of why, not a plan.** Where the
built site differs from what was planned, the difference and its reason are noted
inline below.

The docs were **MkDocs Material, not Sphinx**: `mkdocs.yml` at the root, 42
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

**The structure changed twice during the build, both times because the navbar
overflowed.** pydata-sphinx-theme puts every top-level toctree entry in the
header, and folds anything past the fifth into a "More" dropdown. Fifteen flat
pages wrapped the bar onto a second row; eight sections still pushed three into
the dropdown. What works is what `ttkbootstrap` and `bootstack` already do:
section landing pages at `<section>/index`, `maxdepth: 2`, and **five** top-level
entries — Getting started, Icon packs, User guide, API reference, About.
Integrations became a group inside the user guide's sidebar rather than a
top-level section, and Getting started became four pages instead of one. Depth
belongs in the sidebar, not across the top.

The structure as originally planned, 14 pages:

> **Home** → **Getting started** (install · quickstart · choosing a pack ·
> migrating from ttkbootstrap-icons) → **User guide** (icons & names · sizing and
> render quality · stateful icons · headless rendering · icon browser ·
> packaging) → **Integrations** (tkinter & ttk · ttkbootstrap) → **Icon packs**
> (one page) → **API reference** → **Contributing** → **About** (release notes ·
> license)

Decisions behind it, each of which cost a discussion:

- **One packs page — then sixteen again, deliberately. See #89 before undoing
  either.** The original call: every pack's icon class is an `Icon` subclass whose
  whole surface is `__init__(name, size, color, style)`, seven packs do not even
  take `style`, and what differs is *data* — class name, extra, styles, upstream
  version, glyph count — which is a table. Sixteen pages of 60-line boilerplate is
  why the install idiom went stale in all of them at once.

  That reasoning was about **hand-written** boilerplate, and it no longer binds.
  Per-pack pages came back in #92 because three things changed: Icon packs is a
  top-level section now, so it can carry children; the comparison table was doing
  comparison and reference and navigation at once; and nothing anywhere showed
  what a set *looks like*, which is what you actually choose on. The staleness
  risk is answered by generating every fact — `docs/_ext/pack_showcase.py` reads
  `KNOWN_PACKS` and each live provider, and renders previews with the library
  itself, so a curated name that stops resolving fails the build.

  **The pages are hand-written only where a table cannot go**: a characterization
  of the set and one runnable example. Everything else is a directive. If you are
  tempted to type a fact onto one of those pages, that is the signal a directive
  is missing, not that this rule has an exception.

  The API reference stays at one page: sixteen identical autodoc pages still earn
  nothing, because there is nothing to *show* there.

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

- **There is no docs workflow, and that is now deliberate.** `.github/workflows/`
  holds `ci.yml` and `release.yml`; Read the Docs builds the site from
  `.readthedocs.yaml`, so there is nothing for a workflow to do. `docs.yml`
  existed briefly for GitHub Pages and was deleted when the host changed.

  Its one irreplaceable step moved rather than died: the assertion that the page
  `PACKS_DOC_URL` points at actually exists is now a step in `ci.yml`'s packaging
  job. It checks `docs/packs.rst` in the source tree instead of the built file,
  because CI no longer builds the site. Do not drop it — that URL is the only
  pointer to the catalog a user with no pack installed is ever given.

- **The one packs page must land at `packs.html` — the code already links
  there.** #79 pointed `PACKS_DOC_URL` (`packs.py:29`) at
  `{DOCS_URL}/packs.html` and used it to replace `REPO_URL` in the two places a
  user with *no pack installed* meets first: `no_packs_message()`, raised from
  `Icon.__init__`, and the browser's welcome screen. It 404s until #71 ships, so
  a Sphinx structure that names that page anything else leaves a dead link as
  the only pointer to the catalog, for exactly the users least able to find it
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
| `sfnt.py` | Reads a font's `cmap` straight out of its bytes, because Pillow cannot say which codepoints a font carries and `fontTools` is not a runtime dependency. Returns a `Coverage` of sorted ranges, not a codepoint set. Unparseable returns `None` — unknown, never empty. |
| `iconset.py` | One immutable `IconSet` per (provider, style): font bytes, glyphs, metrics, options. |
| `icon.py` | Tk-facing layer only. `Icon.render_pil()` is the headless entry point. |
| `packs.py` | The pack catalog — single source of truth for every install message and the lazy import root. |
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
  one costs **22.02 MB** to get fifteen icon sets nobody opens, which is the
  bundling extras exist to avoid. (This bullet said "~17 MB" until 2026-08-08 —
  the fourth surviving copy of the figure #104 corrected in two places and #122
  in a third. It is outside `TestTheCostOfInstallingEverythingIsMeasured`'s
  sweep on purpose, since this file quotes the wrong number deliberately when
  telling the story; that exemption is exactly why this copy lasted longest.
  A number asserted here is still a number a future session will repeat.) Users needing two name two: `tkinter-icons[a,b]`.
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
  checks it.** pip does not fail on an unknown extra, and as of pip 25.3 it does
  not even mention one: measured 2026-08-02, `pip install "pillow[nonexistent]"`
  reports plain success, and a local `[all]` install of this package prints
  nothing but `Would install tkinter-icons`. Older pip printed `does not provide
  the extra`; do not rely on that warning existing. The base package installs,
  it has no glyphs, and nothing tells the user their extra was dropped — so a
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
  `v[0-9]*`. That guard was essential when packs were tagged individually — the
  default regex reads `tkinter-icons-fa-v1.1.0` as version 1.1.0, and pack tags
  were pushed *first*, so the base build would take a pack's number. With one
  tag per release it is belt-and-braces rather than load-bearing. **Keep it
  anyway**: it costs nothing, and it is the thing that would stop a stray
  hand-pushed tag in the old shape from silently renumbering a base wheel.

- **A pack's provider name is not guaranteed to be its entry-point key.**
  `registry.py` registers under `provider_instance.name`, and the entry point
  `fa` registers `fontawesome`. That is the *only* pack where the two differ —
  every other key matches its provider name, including `gmi` (which registers
  `gmi`, not `google-material`) and the `bs` directory (whose key is already
  `bootstrap`). One divergence in sixteen is what makes reading the key look
  safe. Anything passing a name to `generate_metrics` has to import the provider
  to get it — reading the key gives an argument the CLI rejects.

- **Both old docs URLs are dead — as of 2026-08-08, and not before.** GitHub
  redirects repo URLs but not project Pages, so
  `israel-dryer.github.io/ttkbootstrap-icons/` has 404'd since the rename. This
  file then asserted that `israel-dryer.github.io/tkinter-icons/` "will too",
  and `migrating.rst:44` shipped that to readers as a statement of fact.

  **It was false for the whole 5.0.0 cycle.** Checked 2026-08-08:
  `gh api repos/israel-dryer/tkinter-icons/pages` reported `status: built`,
  source `gh-pages`, and the URL returned **200**, serving the old MkDocs site
  — `<title>ttkbootstrap-icons</title>`, the pre-rename name sixty-four times
  on the landing page, and the pre-#69 install idiom that #71 exists to have
  replaced. So the docs told users the old site was gone while the old site was
  up, teaching the install pattern the new docs were written to retire.

  The lesson is the one the #102 review kept teaching: *check whether a page
  exists before writing down what it does.* One `curl` would have caught this
  at any point, and it went unverified through a rename, a docs rebuild, and a
  release.

  The owner unpublished Pages and the branch was deleted after. **That order is
  the one to keep**: deleting the branch does not take the site down, it leaves
  Pages configured against a branch that is gone. And the two signals disagree
  for a while — after unpublishing, the URL served 404 while
  `gh api .../pages` still reported `status: built` with the source set. So
  **`curl` tells you the site is down; the API tells you the configuration is
  gone.** Neither alone is the whole answer, and the earlier note in this file
  claiming the API is authoritative "not `curl`" was half right at best.

  A custom domain was considered and declined.

---

## Conventions

- **Branches:** `refactor/*`, `fix/*`, `feat/*`, `docs/*` off **`main`**, and PRs target **`main`**. This changed with #100 — `5.0` was the integration branch and is finished. Stack dependent PRs on each other.

  **A docs commit nobody is going to review goes straight to `main` — do not branch for it.** The owner's rule, stated 2026-08-10 after a handoff update was put up as PR #142: there is no gain in a branch and a PR for a change that no one will read as a diff, and the ceremony has a real cost, since an unmerged handoff branch is precisely how `f0c5cbf` was stranded. This covers updates to this file and to the planning artifacts. It does **not** cover the published docs under `docs/` — those are built and checked, and a `sphinx -W` failure on `main` is worth the branch — nor anything that a review round is expected to look at.

  **Retarget each child by hand as its parent merges — GitHub does not do it for you, and this file said it did until 2026-08-08.** Merging #121 left #122 still based on `docs/on-missing-scope`, so merging #122 next would have put it on that branch rather than on `main`. GitHub retargets when the base branch is **deleted**, which is exactly what you must not do in a stack: a `--delete-branch` merge closes any PR targeting the deleted branch, which is how #85 was lost, and with five stacked PRs it would close the next one each time. So the two rules together are: merge with plain `gh pr merge <n> --merge`, run `gh pr edit <n+1> --base main` before each subsequent merge, verify the base actually changed, and delete every branch at the end.
- **Every PR names an issue with `Closes #n`** where one exists. Now that `main` is the default branch this takes effect on merge, immediately — which is the normal GitHub behavior and was *not* true during the `5.0` period. Pure bookkeeping PRs (#94, #98) name no issue; that is an accepted exception, not an oversight.
  Merge with a merge commit (`gh pr merge <n> --merge --delete-branch`), matching #72–#78 — but **drop `--delete-branch` whenever anything is stacked on the PR**, for the reason under Branches above.
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

That is the order the `publish` job enforces, and it is right whenever the whole release can go out at once. **It was deliberately broken for 5.0.0**, where PyPI's four-new-projects-per-day cap stretched the upload across four days: the base went up on day two, ahead of nine packs, because holding it meant three further days in which nothing at all was installable. Step 3 held regardless. See "What the release left behind that still matters". The cost of publishing the base early is one clean `No matching distribution found` per not-yet-published extra, which was measured before the call rather than assumed.

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

- **A pattern that matches nothing looks exactly like a clean result, and this bit twice in one session.** The American-spelling sweep skipped the entire `.github/` tree, because it tested skip patterns as substrings and `.git` is a prefix of `.github` — it reported 27 files changed and looked like a complete pass. Then `git diff --stat v5.0.0..main -- 'packages/*/src'`, used to prove no code changed before a release, printed an empty diff: the pathspec matched nothing, and an empty diff is indistinguishable from no changes. Both conclusions happened to be right, neither was earned.

  **So prove the pattern finds something before trusting that it found nothing.** Match whole path components rather than substrings, and when a sweep or a diff comes back empty, run it once against a case you know it should catch. Every guard in this repository exists because some check was silently covering less than its name claimed.

- **A green local run proves one interpreter, and the matrix tests five.** `requires-python` is `>=3.10` and CI runs 3.10 through 3.14, but the working venv here is 3.13 — so anything version-gated passes locally and fails on collection in CI. `tests/test_pack_style_claims.py` shipped with a module-level `import tomllib`, which is 3.11 and later; the three 3.10 jobs failed to collect the file at all rather than failing a test. The pattern to copy is in `tests/test_packs.py`: guard on `sys.version_info` and fall back to `tomli`, which `ci.yml` installs below 3.11.

  **`verify_packages.py` is the exception, and it cannot run on 3.10 at all.** `.github/scripts/packages.py` bare-imports `tomllib` and documents the 3.11 floor in its own module docstring — a deliberate developer-tooling constraint, not an oversight to fix, since nothing in the matrix runs it. It matters on a machine whose default interpreter is below that: Ubuntu 22.04 ships 3.10 as `python3`, so the venv this project's own instructions build cannot run that one command, and it needs any 3.11+ interpreter instead.

- **A symbolic system color is Windows-only, and configuring one by hand does not make Tk able to resolve it.** `_drawable_color` exists because `vista`, `winnative` and `xpnative` configure a button foreground of `SystemWindowText`, which Pillow rejects — so colors read off a style are resolved through the widget. The `System*` names live only in Tk's Windows build and name a Windows *system setting* rather than a color, so on X11 `winfo_rgb` raises `unknown color name` and there is nothing to resolve them to; macOS's `systemTextColor` is just as absent. `test_a_symbolic_system_color_is_translated` is therefore gated on `win32`, and the portable half of the translation is asserted separately on `black` → `#000000`, which is what every stock X11 theme really configures.

  **Do not try to make that test portable — two plausible repairs were measured and both are wrong.** `gray50`, `light steel blue` and Tk's 16-bit `#ffff00000000` are portable and do reproduce the bug, but no real theme on any platform configures them, so the test would assert against a fabricated configuration. And a merely *named* color is worse: Pillow parses `SteelBlue`, so a test built on it passes with the translation deleted. Round 3 in that branch's `REVIEW.md` has the measurements.

  Prefer doing that **inside a helper** rather than at module scope. A module-level `importorskip` takes the whole file with it, so one missing backport silently retires every test in it — including the ones that never needed the import. That is the same "a guard quietly stops covering what it names" failure the placement census exists to prevent, one level down.

- **`apt-get update` on a GitHub runner fails for repositories this project does not use, and it used to be able to fail a release.** All three Linux `Install Tk` steps ran `sudo apt-get update && sudo apt-get install -y python3-tk`. `update` exits 100 if *any* apt source on the runner image is mid-sync, and on 2026-08-08 Google Chrome's index was 1407 bytes where its release file said 1408 — so the docs job on #125 failed, having installed nothing and skipped every step after it. Nothing in this repository was involved.

  The `&&` was the bug. A partial `update` still refreshes the lists that succeeded, so the Ubuntu archive index is present either way; all three steps now let `update` fail with a warning and use `apt-get install` as the gate, which fails when Tk is genuinely unavailable and not when a Chrome mirror is resyncing. **`release.yml` had the same line**, which mattered more — a tag-driven release would have died the same way, and the next thing on the list is `v5.0.1`.

  Worth generalising: this is the second red run on a docs-only PR that was worth reading rather than re-running. The first (#110) was a genuine order-dependent test bug. **Read which *step* failed before concluding anything** — here every later step said `skipped`, which is the signature of an early `run` step aborting, not of a test failing.

- **The "Python Versions" badge is not editable text — it is published metadata, and it is frozen.** Both READMEs carry `img.shields.io/pypi/pyversions/tkinter-icons.svg`, which shields renders purely from the `Programming Language :: Python :: 3.x` trove classifiers on the *released* base distribution. The published 5.0.0 stops at 3.13, so **the badge will read "3.10 | 3.11 | 3.12 | 3.13" until 5.0.1 ships**, regardless of what the tree says — editing the README or the pyproject changes nothing on PyPI. This is the same "frozen at release time" trap the #102 review found in the pack READMEs, in its metadata form. The tree is already ahead: #109 added the 3.14 classifier and put 3.14 in the CI matrix on all three platforms, so the fix is merged and simply waiting on a release. Nothing was *blocked* by the gap in the first place — `requires-python = ">=3.10"` has no upper bound, so newer interpreters install and run fine; the badge merely understates. **`tests/test_python_support.py` now pins the classifiers and the CI matrix to each other in both directions**, so the next version cannot be advertised without being tested, or tested without being advertised.
- **Trust a pack's `license_url` at your peril.** It was wrong twice. `weather`
  pointed at the Typicons license, so the browser's "License" link opened another
  project's terms; `meteocons` pointed at basmilius/weather-icons, which is a
  different icon set by a different author in a different format — and #83
  vendored *that* project's MIT text for it on the strength of the URL. The font's
  own embedded name records are authoritative and cost one `fontTools` call:

  ```python
  from fontTools.ttLib import TTFont
  for rec in TTFont(path)["name"].names:
      if rec.nameID in (0, 7, 8, 9, 13, 14):
          print(rec.nameID, rec.toUnicode())
  ```

  Eight packs still ship a *summary* of their license rather than the text —
  `gmi`, `mat`, `remix` (Apache 2.0), `simple` (CC0), `lucide` (ISC) link to it;
  `devicon`, `eva`, `rpga` carry the MIT body under an invented copyright line.
  Apache 2.0 requires giving recipients a copy, which a link does not satisfy.
  Recorded as a known gap in `THIRD-PARTY-NOTICES.md`; the preflight checks a file
  exists, not that it is the license.
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
