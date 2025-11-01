from ttkbootstrap_icons.providers import BaseFontProvider


class GMIProvider(BaseFontProvider):
    """Initialize the provider with style configuration"""

    def __init__(self):
        super().__init__(
            name="gmi",
            display_name="Google Material Icons",
            package="ttkbootstrap_icons_gmi",
            default_style="baseline",
            styles={
                "baseline": {"filename": "fonts/MaterialIcons-Regular.ttf"},
                "outlined": {"filename": "fonts/MaterialIconsOutlined-Regular.otf"},
                "round": {"filename": "fonts/MaterialIconsRound-Regular.otf"},
                "sharp": {"filename": "fonts/MaterialIconsSharp-Regular.otf"}
            },
            scale_to_fit=True,
        )
