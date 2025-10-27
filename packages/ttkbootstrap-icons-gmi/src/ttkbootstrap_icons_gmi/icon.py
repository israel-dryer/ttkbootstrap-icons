from ttkbootstrap_icons.icon import Icon
from .provider import GoogleMaterialProvider


class GMIIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", style: str | None = None):
        GoogleMaterialProviderInstance = GoogleMaterialProvider()
        Icon.initialize_with_provider(GoogleMaterialProviderInstance, style=(style or "baseline").lower())
        super().__init__(name, size, color)

