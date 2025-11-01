from ttkbootstrap_icons.providers import BaseFontProvider


class FAProvider(BaseFontProvider):
    """Initialize the provider with style configuration"""

    def __init__(self):
        super().__init__(
            name="fontawesome",
            display_name="Font Awesome",
            package="ttkbootstrap_icons_fa",
            default_style="solid",
            styles={
                "solid": {"filename": "fonts/fa-solid-900.ttf"},
                "regular": {"filename": "fonts/fa-regular-400.ttf"},
                "brands": {"filename": "fonts/fa-brands-400.ttf"},
            }
        )
