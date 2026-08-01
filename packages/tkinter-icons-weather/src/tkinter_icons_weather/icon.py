from __future__ import annotations

from tkinter_icons.icon import Icon
from tkinter_icons.render import RenderOptions
from tkinter_icons_weather.provider import WeatherFontProvider


class WeatherIcon(Icon):
    """Convenience icon for the Weather Icon glyph set.

    Resolves the provided name using `WeatherProvider`, then initializes the base `Icon` with
    the resolved glyph.

    Args:
        name: glyph name.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    provider_class = WeatherFontProvider

    def __init__(self, name: str, size: int = 24, color: str = "black",
                 *, options: RenderOptions | None = None, **kwargs):
        prov = WeatherFontProvider()
        WeatherIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color, options=options)



