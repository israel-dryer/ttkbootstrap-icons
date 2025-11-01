from ttkbootstrap_icons.providers import BaseFontProvider


class IonProvider(BaseFontProvider):
    """Initialize the provider with style configuration.

    Uses a single font file (`ionicons.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="ion",
            display_name="Ion Icons",
            package="ttkbootstrap_icons_ion",
            filename="fonts/ionicons.ttf",
            scale_to_fit=True,
        )
