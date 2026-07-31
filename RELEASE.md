# Releasing

Releases are made by pushing a tag. GitHub Actions builds, verifies, publishes
to PyPI, and writes the GitHub Release. Nothing is uploaded from a laptop, and
no PyPI token is stored anywhere.

## The tag decides what gets released

This repository holds eighteen distributions. The tag names which one:

| Tag | Releases | From |
|---|---|---|
| `v5.0.0` | `tkinter-icons` | `packages/tkinter-icons` |
| `tkinter-icons-fa-v1.1.0` | `tkinter-icons-fa` | `packages/tkinter-icons-fa` |
| `ttkbootstrap-icons-v5.0.0` | `ttkbootstrap-icons` | `packages/ttkbootstrap-icons-shim` |

The base package keeps the bare `v<version>` form it has used since 1.0.0.
Everything else is `<distribution>-v<version>`.

Note the third row: **the shim's directory is not named after the distribution
it builds**, because the plain name was taken by the package being renamed away
from it. `.github/scripts/packages.py` resolves the mapping by reading every
`pyproject.toml`, so it cannot go stale — but any tooling you add must go
through it rather than assuming `packages/<dist>`.

`tkinter-icons-v5.0.0` is rejected on purpose. It looks like a valid base tag,
but setuptools-scm is configured to match only the bare `v` form, so building
from it would quietly produce a version derived from some older tag.

## Publish order is load-bearing

The base package's extras pin `>=1.1.0` against the packs, and the shim pins
`>=5.0.0` against the base. Release in this order, letting each run finish:

1. **the sixteen packs** at `1.1.0`
2. **`tkinter-icons`** at `5.0.0`
3. **`ttkbootstrap-icons`** at `5.0.0` — the shim, last

Out of order, a package points at a version PyPI does not have yet, and
`pip install "tkinter-icons[material]"` fails for everyone who tries it in the
window between the two uploads.

The shim is published **once**. It depends on `tkinter-icons>=5.0.0` with no
upper bound, so it forwards to every future version without another release.

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

1. **Update the changelog.** Root `CHANGELOG.md` for the base package, or
   `packages/<package>/CHANGELOG.md` for a pack. Add a section at the top:

   ```markdown
   ## [1.2.0] — a short descriptive title
   ```

   That heading is not decoration. `release_notes.py` reads it: the title
   becomes the GitHub Release title, and everything under it up to the next
   `## [` becomes the release body.

2. **Set the version.** Packs and the shim carry `version = "1.2.0"` in their
   `pyproject.toml`. The base package does not — its version comes from the tag
   through setuptools-scm, so there is nothing to edit.

3. **Check it locally**, which is the same preflight the workflow runs:

   ```bash
   python .github/scripts/verify_packages.py --strict --imports --tag tkinter-icons-fa-v1.2.0
   ```

4. **Merge to `main`**, then tag the merge commit and push:

   ```bash
   git tag tkinter-icons-fa-v1.2.0
   git push origin tkinter-icons-fa-v1.2.0
   ```

5. **Watch the run.** If the `pypi` environment has reviewers, it waits for
   approval before uploading.

If something fails before the publish step, delete the tag, fix, and re-tag:

```bash
git tag -d tkinter-icons-fa-v1.2.0
git push origin :refs/tags/tkinter-icons-fa-v1.2.0
```

Once the publish step has run, that version is gone — PyPI does not allow
re-uploading a version, even a deleted one. Ship a patch instead.

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

### Two known blockers

Both are warnings today, and both will stop a `--strict` release:

- **Fourteen packs have no generated metrics.** Only `bs` and `fa` do. Fixing it
  is one `python -m tkinter_icons.tools.generate_metrics --all` in an
  environment with every pack installed, then a commit.
- **Three packs ship no upstream license file** — `bs`, `meteocons`, and
  `typicons`, while the other thirteen do. `bs` redistributes Bootstrap Icons.
  This needs the actual upstream license text and copyright line, which is a
  decision rather than something to generate. They are listed in
  `KNOWN_LICENSE_GAPS` in `verify_packages.py`; delete each from that set as it
  is resolved.

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

## Publishing to TestPyPI

`publish.ps1` builds one package and uploads it to TestPyPI, for trying a
package out before it is real. It refuses to publish to PyPI — that is the
tag-driven workflow's job, and doing it by hand is what this replaced.

```powershell
$env:TWINE_PASSWORD = 'pypi-...'   # a TestPyPI token
./publish.ps1 fa
```

## Verifying afterwards

```bash
pip install --upgrade "tkinter-icons[fontawesome]"
tkinter-icons    # the browser; auto-discovers whatever packs are installed
```
