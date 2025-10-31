from ttkbootstrap_icons.providers import BaseFontProvider


class SimpleProvider(BaseFontProvider):
    """Initialize the provider with style configuration.

    Uses a single font file (`SimpleIcons.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="simple",
            display_name="Simple Icons",
            package="ttkbootstrap_icons_simple",
            filename="fonts/SimpleIcons.ttf"
        )
