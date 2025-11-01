from ttkbootstrap_icons.providers import BaseFontProvider


class FontAwesomeFontProvider(BaseFontProvider):
    """Initialize the provider with style configuration"""

    def __init__(self):
        super().__init__(
            name="fontawesome",
            display_name="Font Awesome 6 (Free)",
            package="ttkbootstrap_icons_fa",
            homepage="https://fontawesome.com/v6/icons",
            license_url="https://fontawesome.com/license",
            icon_version="6.7.2",
            default_style="solid",
            styles={
                "solid": {"filename": "fonts/fa-solid-900.ttf"},
                "regular": {"filename": "fonts/fa-regular-400.ttf"},
                "brands": {"filename": "fonts/fa-brands-400.ttf"},
            },
            pad_factor=0.15,
            scale_to_fit=True,
        )
