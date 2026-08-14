# Releasing

Releases are made by pushing a tag. GitHub Actions builds, verifies, publishes
to PyPI, and writes the GitHub Release. Nothing is uploaded from a laptop, and
no PyPI token is stored anywhere.

## One tag releases the repository

This is a monorepo, and the tag names the repository's release rather than one package's:

```bash
git tag v5.0.0
git push origin v5.0.0
```

That builds all eighteen distributions, publishes the ones PyPI does not already have, and creates one GitHub Release.

The base package is bumped for every release — it carries the change — so the tag is always its version, and always new. The other seventeen ride along on whatever their `pyproject.toml` declares. A pack whose version has not moved is simply skipped at upload, which is what makes a font bump to one pack a normal release rather than a special case: bump that pack, bump the base, tag, and only those two go out.

The base package's version comes *from* the tag through setuptools-scm; every other distribution carries a static version. That is why the tag is the base's and not an arbitrary repository version — there would otherwise be nothing to derive the base's version from.

**Per-distribution tags are retired.** `tkinter-icons-fa-v1.1.0` and friends are rejected by `packages.py` with an explanation rather than a generic parse failure. They meant eighteen tags and eighteen GitHub Releases for one coordinated release — a notification each, to anyone watching releases — and they left the publish order as a procedure a human had to execute correctly, at the exact moment when getting it wrong is unrecoverable. No such tag was ever pushed, so nothing is orphaned by the change.

`tkinter-icons-v5.0.0` is rejected too, and separately: it looks like a valid base tag, but setuptools-scm matches only the bare `v` form, so building from it would quietly produce a version derived from some older tag.

## Publish order is enforced, not documented

The base package's extras pin `>=1.1.0` against the packs, and the shim pins `>=5.0.0` against the base. The `publish` job uploads in three ordered steps:

1. **the sixteen packs** — `skip-existing`, since most will be unchanged
2. **`tkinter-icons`** — no `skip-existing`; a base version already on PyPI means the tag is wrong, and failing is correct
3. **`ttkbootstrap-icons`** — the shim, `skip-existing`, since it is published once and never again

Out of order, the base points at pack versions PyPI does not have yet and `pip install "tkinter-icons[material]"` fails for everyone who tries it in the window between uploads. That used to be your responsibility across eighteen tag pushes. It is now three steps in one job, in one file, and cannot be done out of order by accident.

The shim depends on `tkinter-icons>=5.0.0` with no upper bound, so it forwards to every future version without another release — which is why `skip-existing` is the normal outcome for it rather than a fallback.

### The legacy packs are published by hand, before the tag

The sixteen `ttkbootstrap-icons-*` packs get one final release — READMEs rewritten as signposts, base pin capped below the shim, a `FutureWarning` on import. They are not part of the run above and never will be: they live on `release/ttkbootstrap-icons-packs-final`, cut from `v4.0.0`, which is the only tree where those sixteen still exist since on `5.0` they were renamed into `tkinter-icons-*`. That branch merges nowhere.

`v4.0.0` predates the release automation entirely — no `.github` directory at all — so nothing there is tag-driven. Check the branch out, run `git clean -xdf packages/` first (switching to it leaves the `5.0` build artifacts behind, because git will not remove ignored files, and a stray `.egg-info` changes what lands in a wheel), build `packages/ttkbootstrap-icons-*/`, and upload with a token. Trusted Publishing is workflow-scoped, so it does not apply.

**That `clean` cuts both ways — restore the editable installs before you trust any later wheel.** `-x` removes ignored files, which is the point, but it also deletes every `*.egg-info/` under `packages/`, and on `5.0` those are load-bearing: a pack's `exclude-package-data` is fed from `.egg-info/SOURCES.txt`, so a pack with no `.egg-info` builds a *clean-looking* wheel from a broken config and reports a false pass. That mistake has been made here once already, and it would have shipped `tools` in fourteen wheels. Coming back from the legacy branch, re-run the editable installs before inspecting anything:

```bash
python -m pip install --no-deps $(printf -- '-e %s ' packages/tkinter-icons-*/)
```

**Do this before pushing the `v5.0.0` tag.** Every legacy pack pins `ttkbootstrap-icons` with no upper bound, so the moment the shim publishes, a fresh install of any of them resolves its base to a forwarding package onto a different library. Their final release adds `<5`. Land the caps first and that window never opens.

That inverts the advice this file carried while releases were eighteen separate tag pushes, where the legacy packs slotted between the base and the shim. There is no longer a gap between those two — the `publish` job does all three in one run — so the only choice is before the tag or after the whole thing, and before is right.

The cost of going first is cosmetic and brief: those READMEs tell the reader to run `pip install "tkinter-icons[<extra>]"`, which does not work until the `v5.0.0` run finishes. Text briefly ahead of reality beats a dependency silently resolving somewhere new. Note also that `pypi.org/project/<name>/` returns 200 for any name at all, so it is useless as an existence check — `pypi.org/pypi/<name>/json` is the one that 404s honestly.

## Before the first release: PyPI Trusted Publishing

Each of the eighteen PyPI projects needs a trusted publisher configured once, at
`https://pypi.org/manage/project/<name>/settings/publishing/`:

| Field | Value |
|---|---|
| Owner | `israel-dryer` |
| Repository | `tkinter-icons` |
| Workflow | `release.yml` |
| Environment | `pypi` |

For a project that does not exist on PyPI yet — every `tkinter-icons-*` name is
new — use the *pending publisher* form under your account settings instead. Same
values, plus the project name.

The repository also needs a GitHub environment named `pypi`
(Settings → Environments). Adding required reviewers to it is worth considering:
it turns every publish into an approval step, which is the only thing standing
between a mistyped tag and an immutable upload.

## Making a release

1. **Update the changelogs.** The root `CHANGELOG.md` always, because the base package is always part of a release. Plus `packages/<package>/CHANGELOG.md` for any pack whose version moved. Each gets a section at the top:

   ```markdown
   ## [5.0.1] — a short descriptive title
   ```

   That heading is not decoration. `release_notes.py` reads the root one: the title becomes the GitHub Release title, and everything under it up to the next `## [` becomes the release body.

2. **Set the versions.** Packs and the shim carry `version = "1.2.0"` in their `pyproject.toml`; bump the ones that changed. The base package does not — its version comes from the tag through setuptools-scm, so there is nothing to edit for it.

3. **Check it locally.** Same preflight the workflow runs, over all eighteen:

   ```bash
   python .github/scripts/verify_packages.py --strict --imports --tag v5.0.1
   ```

4. **Merge to `main`.** This comes before the dry run, not after. GitHub only shows a *Run workflow* button for a workflow that exists on the **default branch**, so `release.yml` has to have reached `main` before it can be dispatched at all — which for the 5.0.0 release means the merge, since `main` is still at 4.0.0 and has no `.github` directory. Merging first also means the dry run verifies the tree you are about to tag rather than a near-miss of it.

5. **Do a dry run.** Actions → Release → *Run workflow*, naming the tag and `main`. It builds and verifies everything and publishes nothing — the `publish` and `release` jobs are gated on `github.event_name == 'push'`. Worth doing at least once before a release that matters, since the real run ends in uploads PyPI will not let you take back.

   The `build` job uploads all eighteen distributions as the `dist` artifact, so this is also how you try a wheel out before its version is permanent: download the artifact and `pip install` the file. That is what the old `publish.ps1` and its TestPyPI upload were for, and it is why neither exists any more — a real wheel installed from disk answers the question, without an index that cannot resolve Pillow or the packs' floor on `tkinter-icons`.

6. **Tag the merge commit and push:**

   ```bash
   git tag v5.0.1
   git push origin v5.0.1
   ```

7. **Watch the run.** If the `pypi` environment has reviewers, it waits for approval before uploading.

If something fails before the publish step, delete the tag, fix, and re-tag:

```bash
git tag -d v5.0.1
git push origin :refs/tags/v5.0.1
```

Once the publish step has run, that version is gone — PyPI does not allow re-uploading a version, even a deleted one. Ship a patch instead. Note that a partial failure is possible in principle: the packs upload before the base, so a base failure leaves published packs behind. They are harmless on their own — nothing points at them until a base release does — and the next attempt skips them.

## What the preflight checks

`verify_packages.py` exists because of a specific, repeated failure: a package
that built and uploaded cleanly, and was broken on install. The package-data
glob matched `glyphmap.json` while the provider shipped one file per style
(#61); assets and license files were missing from two packages entirely
(25dac89); a license reference pointed at a file that was not there (34a9c65).
None of that is visible in a working tree, where the files are simply on disk
next to the code.

Every check asks the same question: *would this still work if the only thing
that existed were the built distribution?*

**Errors** fail always:

- a package-data glob that matches no files
- a `license-files` entry that matches no files, or none declared
- a changelog missing, or disagreeing with `pyproject.toml`
- a dependency floor above what the named package actually declares
- a pack with no corresponding extra on the base package, or an `all` extra
  reappearing on it
- an entry point that does not import (with `--imports`)
- with `--tag`: a tag whose version does not match the pyproject and changelog

**Warnings** fail only under `--strict`, which the release workflow uses. These
are fine mid-development and unacceptable to publish:

- a pack with no generated `metrics*.json`
- a pack shipping an upstream font with no upstream license file

The release workflow additionally re-measures the released pack's glyph metrics
and compares them against what is committed, so committed metrics cannot drift
from the font that produced them.

### Both former blockers are closed

Two warnings used to stand between this preflight and a `--strict` release. Neither does now: #82 generated metrics for the fourteen packs that lacked them, and #83 vendored upstream license files for `bs`, `meteocons` and `typicons`. All sixteen packs carry both today, and `verify_packages.py --strict --imports --tag v5.0.0` reports all clear across all eighteen distributions.

**`KNOWN_LICENSE_GAPS` is now an empty set, and keeping it empty is load-bearing.** A *listed* pack downgrades the missing-license finding from an error to a warning, so with nothing listed, a seventeenth pack added without its upstream license fails the preflight outright instead of passing as a known exception. Do not add a name there to get a build through.

What remains is not a preflight failure and does not block a release: the check asks whether a license file exists, not whether it is the right text. Eight packs ship a summary or the wrong copyright line — `gmi`, `mat` and `remix` (Apache 2.0), `simple` (CC0) and `lucide` (ISC) link to the canonical text rather than reproducing it, and `devicon`, `eva` and `rpga` carry the MIT body under a generic copyright line rather than upstream's own. Apache 2.0 in particular requires giving recipients a copy, which a link does not satisfy. `THIRD-PARTY-NOTICES.md` records it under "Known gap"; that is the place to update when it is fixed.

## Version numbering

Semantic versioning. The base package is at `5.0.0`, every pack at `1.1.0`, and
each pack requires `tkinter-icons>=5.0.0`.

A pack changes version when its font, glyph map, or metrics change — not when
the base package does. A pack pinning a new base floor is a minor bump; a
removed or renamed icon is a major one.

## Local development

Install the base package editable, then the packs with `--no-deps`:

```bash
python -m pip install -e packages/tkinter-icons
python -m pip install --no-deps -e packages/tkinter-icons-bs -e packages/tkinter-icons-fa
python -m pip install --no-deps -e packages/ttkbootstrap-icons-shim
python -m pytest -q
```

`--no-deps` matters. Every pack pins `tkinter-icons>=5.0.0`, and until a
`v5.0.0` tag exists setuptools-scm derives something *lower* from the last tag —
`4.0.1.dev16+...` — so pip decides the local base package does not satisfy the
floor and goes to PyPI for one that does. `--no-deps` sidesteps it; their only
other dependency is Pillow, which the base install brings in.

If you would rather have resolution work normally, pin what setuptools-scm
reports instead:

```bash
SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TKINTER_ICONS=5.0.0 \
    python -m pip install -e packages/tkinter-icons
```

## Verifying afterwards

```bash
pip install --upgrade "tkinter-icons[fontawesome]"
tkinter-icons    # the browser; auto-discovers whatever packs are installed
```
