# Icon Browser

Browse installed icon sets with a simple, fast UI. The browser auto-discovers any provider packages you have installed
and lets you search, filter by style (when applicable), change size and color, and copy icon names for use in your code.

![Icon Browser](providers/assets/bootstrap/browser.png)

---

## Launching the browser

From your terminal (after installing the base package):

```bash
ttkbootstrap-icons
```

Or with Python directly:

```bash
python -m ttkbootstrap_icons.browser
```

---

## Discovering providers

The browser shows the built-in Bootstrap Icons and any additional providers you have installed. External providers are
discovered via Python entry points in the group `ttkbootstrap_icons.providers`.

Install any providers you need (examples):

```bash
pip install ttkbootstrap-icons-fa           # Font Awesome Free
pip install ttkbootstrap-icons-gmi          # Google Material Icons
pip install ttkbootstrap-icons-remix        # Remix Icon
pip install ttkbootstrap-icons-fluent       # Fluent System Icons
pip install ttkbootstrap-icons-typicons     # Typicons
```

If a provider does not appear, verify it is installed in the same Python environment that launches the browser.

---

## Using the browser

- Provider: select an icon set from the dropdown at the top-left.
- Style: when a provider offers styles, choose one (e.g., fill/outline, solid/regular/brands). The grid updates
  immediately.
- Search: type to filter by name (case-insensitive, substring match).
- Size: adjust the pixel size of the previewed icons.
- Color: set the rendering color for the preview; copied names are style-aware but color is not part of the name.
- Copy Name: copies an identifier suitable for use with that provider in code. For multi-style providers, the copied
  value is style-aware.

Example usage in code after copying a name:

```python
from ttkbootstrap_icons_fa import FAIcon

# Example: a solid icon named "house"
icon = FAIcon("house-solid", size=24, color="#0d6efd")
```

---

## Troubleshooting

- Provider missing from the list
    - Ensure it is installed in the same environment. Check with:

      ```bash
      python -c "from importlib.metadata import entry_points; print([ (e.name, e.value) for e in entry_points(group='ttkbootstrap_icons.providers') ])"
      ```

    - If you installed a provider recently, restart the browser.

- Errors when launching
    - Verify that the base package is installed and up to date:

      ```bash
      pip install -U ttkbootstrap-icons
      ```

---

## Notes

- The preview grid renders icons on-demand for responsiveness; scrolling reuses cached images.
- Copied names reflect the provider's display index and style rules. When a style suffix is already present in the name,
  it is preserved.
