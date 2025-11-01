from ttkbootstrap_icons.providers import BaseFontProvider


class SimpleFontProvider(BaseFontProvider):
    """Initialize the provider"""

    def __init__(self):
        super().__init__(
            name="simple",
            display_name="Simple Icons",
            package="ttkbootstrap_icons_simple",
            license_url="https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md",
            icon_version="15.18.0",
            homepage="https://simpleicons.org/",
            filename="fonts/SimpleIcons.ttf",
            pad_factor=0.15,
            scale_to_fit=True,
        )
