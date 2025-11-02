# PyInstaller Hooks

This package includes built-in PyInstaller support so the required font and glyphmap assets are bundled when you freeze your app.

---

## Basic Build

```bash
pip install pyinstaller
pyinstaller --onefile your_app.py
```

PyInstaller usually detects the included hook automatically.

---

## Manual Hook Configuration (If Needed)

If automatic detection does not work, point PyInstaller to the bundled hook directory:

```bash
# Using the command line
pyinstaller --additional-hooks-dir path/to/site-packages/ttkbootstrap_icons/_pyinstaller your_app.py
```

Or in a `.spec` file:

```python
# your_app.spec

a = Analysis(
    ['your_app.py'],
    ...,
    hookspath=['path/to/site-packages/ttkbootstrap_icons/_pyinstaller'],
    ...,
)
```

---

## Programmatic Hook Discovery

Use this if you generate spec files or drive PyInstaller from Python:

```python
from ttkbootstrap_icons import get_hook_dirs

hook_dirs = get_hook_dirs()  # pass to PyInstaller
```

---

## Post-build Check and Cleanup

After building with PyInstaller, test that icons render correctly in the frozen app:

```bash
./dist/your_app      # Linux/Mac
./dist/your_app.exe  # Windows
```

Optionally, clean up temporary font files on exit:

```python
import atexit
from ttkbootstrap_icons import Icon

atexit.register(Icon.cleanup)
```
