# Release Guide for ttkbootstrap-icons

## Quick Reference

### First Time Setup

1. Install build tools:
   ```bash
   pip install --upgrade build twine
   ```

2. Create PyPI account at https://pypi.org/account/register/

3. Create API token at https://pypi.org/manage/account/token/

4. (Optional) Create TestPyPI account at https://test.pypi.org/account/register/

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if you have one)
- [ ] Version number is correct in git tag
- [ ] All changes committed to git
- [ ] README has correct examples and screenshots

### Release Process

#### 1. Commit and Tag

```bash
# Commit all changes
git add .
git commit -m "Release v1.0.0"

# Create version tag (setuptools-scm uses this)
git tag v1.0.0

# Push to GitHub
git push origin main
git push origin v1.0.0
```

#### 2. Build and Publish a Package

Use the new PowerShell helper to build and publish a specific package (base or provider):

```powershell
# Syntax
./publish.ps1 <package> [-Dev]

# Examples
# Publish to PyPI
./publish.ps1 ttkbootstrap-icons             # base package (Bootstrap built-in)
./publish.ps1 ttkbootstrap-icons-fa          # Font Awesome provider
./publish.ps1 fluent                         # resolves to packages/ttkbootstrap-icons-fluent

# Publish to TestPyPI
./publish.ps1 ttkbootstrap-icons-remix -Dev
```

Prereqs:
- Set an API token in your environment before running:
  - `$env:TWINE_PASSWORD = 'pypi-xxxxxxxxxxxxxxxxxxxxx'`
- `TWINE_USERNAME` defaults to `__token__`.
- Requires `python -m pip install build twine`.

**Manual build and upload (alternative)**
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

#### 3. Verify the Release

1. Check PyPI/TestPyPI for the package you published (base or provider):
   - Base: https://pypi.org/project/ttkbootstrap-icons/
   - Example provider: https://pypi.org/project/ttkbootstrap-icons-fa/
2. Test installation:
   ```bash
   pip install --upgrade ttkbootstrap-icons
   pip install --upgrade ttkbootstrap-icons-fa   # example
   ttkbootstrap-icons  # Test previewer CLI (auto-discovers installed providers)
   ```

### Version Numbering

This project uses `setuptools-scm` for automatic versioning based on git tags.

**Format:** `vX.Y.Z`
- `X` = Major version (breaking changes)
- `Y` = Minor version (new features, backwards compatible)
- `Z` = Patch version (bug fixes)

**Examples:**
- `v1.0.0` - Initial release
- `v1.1.0` - New features added
- `v1.1.1` - Bug fixes
- `v2.0.0` - Breaking changes

### Common Issues

**Issue:** "Version already exists on PyPI"
- **Solution:** Increment the version tag (e.g., v1.0.0 → v1.0.1)

**Issue:** "Invalid authentication credentials"
- **Solution:** Check your API token in `~/.pypirc` or use `__token__` as username

**Issue:** "setuptools-scm unable to find version"
- **Solution:** Make sure you've created a git tag and pushed it

**Issue:** Files missing from package
- **Solution:** Verify `[tool.setuptools.package-data]` in the package's `pyproject.toml` includes fonts, glyphmap.json, and LICENSES/*.

### Rolling Back a Release

You cannot delete releases from PyPI, but you can:
1. Mark them as "yanked" (users won't install by default)
2. Release a new patch version with fixes

```bash
# On PyPI, go to: https://pypi.org/manage/project/ttkbootstrap-icons/releases/
# Click the version → Options → Yank release
```

### Automation with GitHub Actions (Future)

Consider setting up GitHub Actions to automate releases when tags are pushed.

## PyPI Configuration

### .pypirc File

Create `~/.pypirc` (Linux/Mac) or `%USERPROFILE%\.pypirc` (Windows):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...your-token-here

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZwI...your-test-token-here
```

**Security:** Keep this file private! Add to `.gitignore`.

---

Notes:
- Each provider package ships upstream license files under `LICENSES/` and documents attribution in its README.
- The base package includes PyInstaller hooks for all providers; freezing apps will bundle provider assets when providers are installed.
