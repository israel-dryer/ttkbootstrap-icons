# Weather Icons (ttkbootstrap-icons-weather)

Weather Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-weather
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Weather Icons
- Icon Version (preset default): 2.0.10
- Source: https://erikflowers.github.io/weather-icons/ (CDN: https://cdnjs.com/libraries/weather-icons)

## License and Attribution

- Fonts: SIL Open Font License 1.1 (OFL-1.1)
- Code: MIT License
- Documentation: Creative Commons Attribution 3.0 (CC BY 3.0)
- Attribution: Weather Icons by Erik Flowers — https://erikflowers.github.io/weather-icons/

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_weather import WeatherIcon

root = tk.Tk()

icon = WeatherIcon("day-sunny", size=24, color="#ffbf00")
tk.Button(root, image=icon.image).pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

```bash
# Quick build (uses preset wi2)
ttkicons-weather-quick

# Preset for Weather Icons via cdnjs
ttkicons-weather-build --preset wi2 --version 2.0.10

# Or direct URL
ttkicons-weather-build --font-url https://cdnjs.cloudflare.com/ajax/libs/weather-icons/2.0.10/font/weathericons-regular-webfont.ttf

# Optional: provide CSS to get readable icon names
ttkicons-weather-build --preset wi2 --version 2.0.10 \
  --css-url https://cdnjs.cloudflare.com/ajax/libs/weather-icons/2.0.10/css/weather-icons.min.css
```

Omitting metadata uses TTF-only extraction (needs `fonttools`).

## Changelog

| Version | Date       | Notes                                 |
|--------:|------------|---------------------------------------|
| 0.2.0   | 2025-10-28 | Docs consistency; previewer UX tweaks |
| 0.1.0   | 2024-10-27 | Initial provider and basic usage docs |
