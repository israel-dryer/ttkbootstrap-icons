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

**`5.0` reached `main` on 2026-08-02 as PR #100, and `main` is now 5.0.0 — untagged.** The integration branch has done its job; `5.0` still exists on `origin` but nothing lands there any more. **New work branches off `main` and PRs to `main`.**

| | |
|---|---|
| `main` | 5.0.0 content, merged; `v5.0.0` exists **locally, unpushed**, and now points at the tip — see below |
| the sixteen legacy packs | **published to PyPI** with their `<5` caps, 2026-08-02 |
| the release workflow | dry run **passed** at `31fcf74`, 2026-08-03 — later commits are documentation only, so the artifacts it verified still stand |
| the #102 pre-tag review | **done** 2026-08-03; findings on the issue, fixes in #104 and #105 |
| **the 5.0.0 release** | **eight of eighteen published, and metered out over several days** — see below |

### The release is in progress, and it is rationed — read this before touching anything

**Twelve of the eighteen are on PyPI as of 2026-08-05.** `tkinter-icons-bs`, `-devicon`, `-eva`, `-fa` went up 2026-08-03; `tkinter-icons` 5.0.0 itself plus `-mat`, `-simple`, `-lucide` went up 2026-08-04; `-weather`, `-gmi`, `-remix`, `-fluent` went up 2026-08-05. **Still unpublished: five packs** — `typicons`, `fluent-reg`, `meteocons`, `ion`, `rpga` — **and the `ttkbootstrap-icons` 5.0.0 shim**, which still shows 4.0.0 on PyPI.

**The limit is four new PyPI projects per 24 hours.** Israel confirmed this directly, 2026-08-04 — it is not a guess from watching uploads fail, and it is not the "20 per hour" default in `warehouse/config.py`. Seventeen of the eighteen distributions are brand-new project names, so the release is inherently a four-day operation. The eighteenth, the shim, publishes to a project that already exists and so should not cost a slot; it has not been tested, because it is scheduled last anyway.

**A refused attempt does not obviously spend from the quota, and the earlier claim that it does was never well-supported.** This file used to assert it, reasoning from eight probes over 5.5 hours that all failed — but every one of those probes fell inside 24 hours of the four successes, so a plain rolling window explains them equally well. 2026-08-04 supports the simpler reading: after a full 24-hour wait, four uploads went through back-to-back with no warm-up. Still, **do not retry in a loop** — there is no upside, and PyPI's own guidance from [the trusted-publishers troubleshooting page](https://docs.pypi.org/trusted-publishers/troubleshooting/#ratelimiting) is to wait, try once, then email admin@pypi.org. Note that page documents a *different* limit — 100 trusted-publisher registrations per 24h — so only its remedy applies, not its number.

**The base was published fifth-from-last rather than last, deliberately reversing what this file used to instruct.** The old rule was "publish the base only after all sixteen packs are live", because its extras pin `>=1.1.0`. Under a four-a-day cap that rule bought nothing and cost three extra days in which *nothing at all* was installable, including the four packs already up. The failure it was protecting against was measured before the decision and is mild: `pip install "tkinter-icons[weather]"` against an unpublished pack gives `ERROR: No matching distribution found`, resolution aborts, and nothing is installed — a clean refusal, not a half-installed environment. `pip install "tkinter-icons[material,simple]"` was verified end-to-end from PyPI in a throwaway venv the same day, down to `MatIcon.render_pil('home')` returning real ink.

**The last four went up 2026-08-05, 10:07–10:09 EDT**, back-to-back with no refusals and no warm-up — the fourth day running that a full 24-hour wait was followed by four clean uploads. **The next window opens ~10:07 EDT 2026-08-06.** No fifth was attempted this time; there is nothing to learn from it that the previous two probes did not already fail to settle.

`pip install "tkinter-icons[weather]"` was verified end-to-end from PyPI in a throwaway venv the same day, down to `WeatherIcon.render_pil("day-sunny", size=32)` returning 323 non-transparent pixels.

### Resuming the release

**The artifacts already exist, in `dist/`, and do not need rebuilding.** All 36 files, `twine check` clean, built 2026-08-04. `dist/` is gitignored at `.gitignore:3`, so unlike the previous attempt — which built into a session scratchpad and lost everything — these survive between sessions. Rebuild only if something in the tree actually changes.

**If you do rebuild, the base needs `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TKINTER_ICONS=5.0.0`, and this is not optional while PyCharm is open.** PyCharm rewrites the tracked file `.idea/modules.xml` while it runs, including *during* a build, which makes setuptools-scm see a dirty tree at the tag and produce `5.0.1.dev0+g<sha>.d<date>`. That `+…` local version identifier is **rejected outright by PyPI**. Stashing `.idea` first is not enough — the IDE puts it back mid-build. The tag alone is not enough either.

```bash
DIST=dist && rm -rf $DIST && mkdir -p $DIST
for d in packages/tkinter-icons-*/ packages/ttkbootstrap-icons-shim; do
  .venv/Scripts/python.exe -m build --outdir $DIST "$d"
done
SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TKINTER_ICONS=5.0.0 \
  .venv/Scripts/python.exe -m build --outdir $DIST packages/tkinter-icons
.venv/Scripts/python.exe -m twine check $DIST/*          # expect 36 PASSED
```

**The `v5.0.0` tag is local and unpushed, and points at `ee118e2`. Do not move it again.** It was moved there 2026-08-04, off `31fcf74`, because handoff commits had left it three behind and the base was building as `5.0.1.dev3+g<sha>`; that was safe at the time because the only delta was `CLAUDE.md`, which ships in no distribution. **That is no longer true.** #109 added a `Programming Language :: Python :: 3.14` classifier to the base `pyproject.toml`, so `main` now differs from the released tree in packaged metadata. The tag as it stands describes exactly what went to PyPI as 5.0.0; dragging it to the tip would make it describe a base wheel carrying a classifier the published 5.0.0 does not have. If it is ever lost, recreate it with `git tag v5.0.0 ee118e2`, not at `HEAD`.

**The same divergence changes what "rebuild the artifacts" means.** The five remaining packs and the shim are untouched by #109 and rebuild from `main` identically — that is the only rebuild the rest of this release needs. The **base** is different: rebuilding `tkinter_icons-5.0.0` from `main` now produces a wheel that is not what PyPI is serving. It does not matter in practice, because the base is already published and must not be re-uploaded, but do not treat a wholesale `rm -rf dist` as free. If you need the base rebuilt as-released, build it from the tag.

Then upload **one project at a time**, stopping at the first 429 — four per day, in this order:

```bash
# 2026-08-06: typicons, fluent_reg, meteocons, ion
.venv/Scripts/python.exe -m twine upload --config-file .pypirc dist/tkinter_icons_typicons-1.1.0*
# 2026-08-07: rpga, then the shim (below), then push the tag

# last, so it never points at a version that does not exist
.venv/Scripts/python.exe -m twine upload --config-file .pypirc --skip-existing \
  dist/ttkbootstrap_icons-5.0.0*
```

**`rpga` and the shim can go on the same day**, which is why 08-07 carries two: `ttkbootstrap-icons` publishes to a project that already exists, so it should not draw from the four-new-projects quota. That remains untested — it is scheduled last either way — so if it does 429, it is the only thing left and 08-08 finishes it.

**One glob to be careful with:** `dist/tkinter_icons_fluent-1.1.0*` matches only `fluent`, because `fluent_reg`'s files are `tkinter_icons_fluent_reg-1.1.0*` — the character after `fluent` is `_`, not `-`. That is correct as written, but it is one hyphen away from silently spending two quota slots in a command that reads like it spends one.

Check what is actually live rather than trusting a log — a batch loop misreported this once, because `curl` inside `while read` eats stdin:

```bash
for d in $(.venv/Scripts/python.exe -c "from tkinter_icons.packs import KNOWN_PACKS; print(' '.join(p.distribution for p in KNOWN_PACKS))"); do
  printf '%-28s %s\n' "$d" "$(curl -s -o /dev/null -w '%{http_code}' https://pypi.org/pypi/$d/json </dev/null)"
done
```

**`.pypirc` is in the repository root**, gitignored at `.gitignore:33` and untracked, so the token cannot be committed. `twine` does not find it automatically — it reads `~/.pypirc` — hence `--config-file .pypirc` on every command above.

### After the packages are up

**Pushing `v5.0.0` will produce one red workflow run, and that is expected.** `publish` fails deliberately when the base version is already on PyPI, because normally that means the tag is wrong (`release.yml`, and "Deliberate decisions" below). Since the base will have been uploaded by hand, that check fires. Packs and the shim skip-existing cleanly. Consequence: the `release` job never runs, so **create the GitHub Release by hand**:

```bash
.venv/Scripts/python.exe .github/scripts/release_notes.py CHANGELOG.md 5.0.0 NOTES.md /dev/stdout tkinter-icons
gh release create v5.0.0 --title "tkinter-icons 5.0.0 — renamed to tkinter-icons, rebuilt around measured glyph ink" --notes-file NOTES.md
```

**Trusted Publishing was deliberately deferred, and this is the reason.** The owner's call, 2026-08-03: registering seventeen *pending* publishers means seventeen web forms of five fields each before anything can be published, which is not a reasonable thing to have on the critical path. Once these projects exist, a publisher is configured on each project's own settings page instead, at whatever pace suits — see `RELEASE.md`. Until that is done **the release workflow cannot publish**, so 5.0.1 is a manual upload too unless the publishers are set up first.

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
| #105 | `Closes #90` — the sixteen pack READMEs generated from the catalogue, the pre-rename screenshots dropped |

**The milestone issues are all closed, and #89 closed because #100's body named it.** That was not automatic: no commit body mentions #89, and its `Closes #89` lived only in PR #92's body, which merged to `5.0` — a non-default base — so GitHub had already discarded the link and does not re-evaluate it. #69, #71 and #79 closed from keywords already in the commit bodies. #67, #68, #70 and #75 were closed earlier by hand and their links are lost for good.

`origin` also carries two branches that are **not** stale and must not be
deleted with the rest:

- `release/ttkbootstrap-icons-packs-final` — the terminal release of the sixteen
  `ttkbootstrap-icons-*` packs, cut from `v4.0.0`. Merges nowhere. See
  `RELEASE.md`.
- `gh-pages` — dead, and *can* now go; it served the old MkDocs site and Read
  the Docs replaced it.

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

Open follow-ups, neither a release blocker: **#87** — the screenshots and
the browser's app icon are done, the *generated* renderer figures are not; and
**#91** — reaching the pure-Pillow renderer should not require `tkinter`
installed. **#90 closed from #105**, which generated the sixteen pack READMEs rather than hand-editing them. #92 did the substance of #89 apart from its prose pass, which is folded into the list under "Next session"; #89 itself closed with #100.

**#79 shipped as #81, not #80.** #80 was merged into `5.0` prematurely — without
permission and before review — and `5.0` was reset to drop it. The rollback was
a reset rather than a revert, so `5.0`'s history is clean and there is no
reverted-content trap for later merges; verified after #81 landed. **Do not
merge a PR in this repository unless asked to merge that specific PR.** A
passing CI run, a `MERGEABLE` state, and the `gh pr merge` line under
"Conventions" are mechanics, not authorization. `5.0` exists so each piece is
reviewed before it accumulates.

**Most of these issues are still OPEN on GitHub, and that is correct** — a PR
merged into `5.0` does not close the issue it names, because GitHub only honours
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

**None of that is live yet, and 5.0.0 is not being released that way.** Trusted
Publishing needs a publisher registered per project, and for a project that does
not exist yet that means a *pending* publisher — seventeen web forms before the
first upload. The owner declined that on the critical path (2026-08-03), so
5.0.0 is being uploaded by hand with a token from `.pypirc`, and the publishers
get configured afterwards against projects that exist. **Until they are
configured the workflow cannot publish anything**, so treat the tag-driven path
as designed-and-tested but not yet in service.

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

**The release is metered out four distributions a day and is not finished. Do not start anything else until it is.** Full detail is under "The release is in progress, and it is rationed" in Current state; the short version is that twelve of eighteen are published, the base among them, and PyPI allows four new projects per 24 hours.

**The next action is four uploads after ~10:07 EDT on 2026-08-06** — `typicons`, `fluent_reg`, `meteocons`, `ion`, one command each, stopping at the first 429. The artifacts are already built in `dist/`; nothing needs rebuilding. Then `rpga` plus the shim on 08-07, after which push the tag and cut the GitHub Release by hand.

**The remaining order is chosen, and the reasoning is worth not re-deriving.** Download counts on the legacy `ttkbootstrap-icons-*` packs separate `bs` (1595/month) and to a lesser degree `fa` and `weather` (~300) from everything else, but the rest sit between 95 and 141 a month, which at that scale is indistinguishable mirror and bot traffic. The better signal was which extras the project's own entry-path docs tell people to type: `[material]` appears six times across the READMEs and getting-started pages, `[material,simple]` three times, then `[lucide,simple]`, `[lucide,material]`, `[weather]`, `[bootstrap]`. That is why `mat`, `simple` and `lucide` went first and `weather` led the 08-05 batch. **As of 2026-08-05 every install line in the two READMEs, `docs/index.rst` and `docs/getting-started/` resolves against PyPI** — the real extras named there are exactly `bootstrap`, `lucide`, `material`, `simple` and `weather`, all live. (`[all]` also appears on that path, in `installation.rst:31`, but it is the note explaining that no such extra exists; `[example]` and `[extra]` are hypotheticals in `contributing.rst`.) So the ordering question is settled and the five left are alphabetical convenience.

**The sixteen per-pack docs pages are a different matter, and five of them are briefly wrong in public.** Each names its own extra, so `packs/typicons`, `packs/fluent-regular`, `packs/meteocons`, `packs/ionicons` and `packs/rpg-awesome` currently print an install line that 404s — live on Read the Docs right now. That is inherent to a rationed release rather than a defect, and it self-resolves on 08-07; it is recorded here only so it is recognised as expected rather than rediscovered as a bug.

**Everything that precedes publishing is done.** The dry run passed against `31fcf74`, whose packaged content is identical to the tip, the #102 review is complete, and there are no open PRs beyond handoff bookkeeping. The review's findings are two comments on #102 — the findings, then the wrap-up marking every item closed — and they record what was measured, not just what was concluded. Read those before re-opening any of it.

**Do not re-run the dry run or re-review.** Both were done against the current tree. The only thing standing between here and a finished release is PyPI's quota.

**Afterwards** — once all eighteen are on PyPI and the GitHub Release exists: point Read the Docs' Default branch back at `main`; delete `gh-pages`; set up the seventeen trusted publishers so the *next* release can be tag-driven; delete the merged remote branches — `5.0`, `docs/handoff-post-95`, `docs/legacy-final-release-and-meteocons`, `docs/drop-bootstack-references`, `docs/migration-scope-and-shim-extra`, `docs/ci-badge`, `docs/pack-readmes-generated`, and `fix/release-latest-marker` (that last is #96, closed unmerged and superseded by #97). **Leave `release/ttkbootstrap-icons-packs-final` alone** — it is the only tree where the sixteen old packs still exist.

### What the #102 review found, and the two traps in it

The mechanics are on the issue. What is worth carrying forward is the shape of the mistakes, because none of them moved a check.

**A README on PyPI is frozen at release time, and that changes when a README bug must be fixed.** This is the one that nearly went wrong. The sixteen pack READMEs were known off-idiom, tracked as #90, and the obvious call was to ship and fix afterwards, since every install line and import in them resolved. That call was wrong: `curl https://pypi.org/pypi/tkinter-icons-lucide/json` returned **404**, because the sixteen `tkinter-icons-*` distributions do not exist until the tag creates them. So they were not stale pages to tidy later, they were sixteen first impressions — and deferring meant sixteen *extra pack releases*, not sixteen commits. **Check whether a page exists before deciding it can be fixed later.** #105 generated them instead.

**Prose that repeats a number is worse than prose that contradicts itself,** because nothing looks wrong. "About 17 MB" appeared in `packs.rst`, `packaging.rst` and `CHANGELOG.md`, in perfect agreement, and was wrong on either reading — the real figures are 21.86 MB installed and about 8.27 MB compressed. Cross-document consistency checks find disagreement; they do not find a number nobody ever measured.

Three more, each fixed and each invisible to `pytest`, `sphinx -W` and `verify_packages.py`:

- The 5.0.0 changelog opened with a **shell command inside a `python` fence** — the first code on the GitHub Release page, and a `NameError` if copied. Generate the release body with `release_notes.py` and *read it* before tagging; it is not the same text as the changelog section.
- "`Icon` itself still raises" was true only in a **cold process**. Construct any pack icon first and the base `Icon.render_pil` succeeds from whichever set loaded last. Test claims about fresh state in a fresh interpreter.
- The #105 generator first wrote "**reproduced in this package under `LICENSES/`**", which is false for the eight packs whose `LICENSES/` holds a summary and a link — `gmi`'s is six lines pointing at apache.org. A generator multiplies a wrong sentence by sixteen.

**Two facts a later reader will otherwise rediscover the hard way.** The multi-style packs store `metrics-<style>.json`, not `metrics.json`, so a naive existence probe falsely reports `fluent`, `fontawesome` and `google-material` as shipping no metrics. And all 93 `.. code-block:: python` blocks in the docs now execute cleanly apart from fragments that reference an earlier block on the same page — but two of the headless-rendering examples **write into the current directory**, so run them from a temp cwd or they leave `home.png` and `icons/` in the repo.

### Not blocking, and worth doing next

- **#87's other half.** The five screenshots are retaken and the browser has its own icon, but the *generated* figures are not built: `user-guide/sizing-and-quality` still describes measured ink, padding, oversampling and even-snapping entirely in prose, where every claim is unfalsifiable by the reader and every one of them is a side-by-side render the library could draw at build time. Same for outline-vs-fill on `icons-and-names` and the multi-pack comparison on `choosing-a-pack`. `pack_showcase.py` already does exactly this for the pack previews — the pattern, the light/dark handling and the `-W` safety net all exist.
- **#89's prose pass.** The pages shipped; the re-read did not. Repetition across pages, and `#0d6efd` — Bootstrap blue — still in the examples on `index.rst` and `icons-and-names.rst`, on a site whose palette is teal. The landing page and both READMEs were fixed; these two were left because changing one of three would have been worse than leaving all three. #89 is closed, so this survives only here — it is a genuine loose end, not a completed item.
- **#91.** `import tkinter_icons` requires `tkinter` even for `render_pil`, which the headless guide had to be softened to admit. Making the Tk imports lazy is a small, contained change and restores the stronger claim. Note that the base `Icon.render_pil` being order-dependent — raising cold, succeeding after any pack icon exists — lives in the same code and is worth folding in.

**The milestone is closed, and #90 with it.** #67–#71, #75, #79 and #89 closed as of #100; #90 closed from #105. The two still open — **#87** and **#91** — are genuine follow-ups that outlive the milestone and block nothing.

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

  **The pages are hand-written only where a table cannot go**: a characterisation
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
  pointer to the catalogue a user with no pack installed is ever given.

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

- **Both old docs URLs are dead and that was accepted.** GitHub redirects repo
  URLs but not project Pages, so `israel-dryer.github.io/ttkbootstrap-icons/`
  404s — and since the move to Read the Docs,
  `israel-dryer.github.io/tkinter-icons/` will too. A custom domain was
  considered and declined. `migrating.rst` tells readers where the docs went.

---

## Conventions

- **Branches:** `refactor/*`, `fix/*`, `feat/*`, `docs/*` off **`main`**, and PRs target **`main`**. This changed with #100 — `5.0` was the integration branch and is finished. Stack dependent PRs on each other; GitHub retargets on merge.
- **Every PR names an issue with `Closes #n`** where one exists. Now that `main` is the default branch this takes effect on merge, immediately — which is the normal GitHub behaviour and was *not* true during the `5.0` period. Pure bookkeeping PRs (#94, #98) name no issue; that is an accepted exception, not an oversight.
  Merge with a merge commit (`gh pr merge <n> --merge --delete-branch`), matching #72–#78.
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

That is the order the `publish` job enforces, and it is right whenever the whole release can go out at once. **It was deliberately broken for 5.0.0**, where PyPI's four-new-projects-per-day cap stretched the upload across four days: the base went up on day two, ahead of nine packs, because holding it meant three further days in which nothing at all was installable. Step 3 held regardless. See "The release is in progress, and it is rationed". The cost of publishing the base early is one clean `No matching distribution found` per not-yet-published extra, which was measured before the call rather than assumed.

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

- **The "Python Versions" badge is not editable text — it is published metadata, and it is frozen.** Both READMEs carry `img.shields.io/pypi/pyversions/tkinter-icons.svg`, which shields renders purely from the `Programming Language :: Python :: 3.x` trove classifiers on the *released* base distribution. The published 5.0.0 stops at 3.13, so **the badge will read "3.10 | 3.11 | 3.12 | 3.13" until 5.0.1 ships**, regardless of what the tree says — editing the README or the pyproject changes nothing on PyPI. This is the same "frozen at release time" trap the #102 review found in the pack READMEs, in its metadata form. The tree is already ahead: #109 added the 3.14 classifier and put 3.14 in the CI matrix on all three platforms, so the fix is merged and simply waiting on a release. Nothing was *blocked* by the gap in the first place — `requires-python = ">=3.10"` has no upper bound, so newer interpreters install and run fine; the badge merely understates. **`tests/test_python_support.py` now pins the classifiers and the CI matrix to each other in both directions**, so the next version cannot be advertised without being tested, or tested without being advertised.
- **Trust a pack's `license_url` at your peril.** It was wrong twice. `weather`
  pointed at the Typicons licence, so the browser's "License" link opened another
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
