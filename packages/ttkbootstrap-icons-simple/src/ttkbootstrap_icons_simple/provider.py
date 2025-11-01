from ttkbootstrap_icons.providers import BaseFontProvider


class SimpleProvider(BaseFontProvider):
    """Initialize the provider"""

    def __init__(self):
        super().__init__(
            name="simple",
            display_name="Simple Icons",
            package="ttkbootstrap_icons_simple",
            filename="fonts/SimpleIcons.ttf",
            pad_factor=0.15,
            scale_to_fit=True,
        )
