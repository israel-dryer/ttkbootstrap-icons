# tkinter-icons-weather

An icon provider for the `tkinter-icons` library.  
Weather Icons is a classic set of weather-related glyphs.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-weather.svg)](https://pypi.org/project/tkinter-icons-weather/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install tkinter-icons-weather
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_weather import WeatherIcon

root = tk.Tk()

icon = WeatherIcon("day-sunny", size=24, color="#ffbf00")
tk.Button(root, image=icon.image).pack()

root.mainloop()
```

---

## Styles

This provider uses a single font without separate style variants.

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
tkinter-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](assets/weather/browser.png)

---

## License and Attribution

- **Upstream license:** Weather Icons — https://erikflowers.github.io/weather-icons/
- **Wrapper license:** MIT © Israel Dryer

