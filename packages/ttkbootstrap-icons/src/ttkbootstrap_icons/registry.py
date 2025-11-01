from __future__ import annotations

from importlib.metadata import entry_points
from typing import Dict, Iterable, Optional

from .providers import BaseFontProvider


class ProviderRegistry:
    """Simple registry for icon providers.

    This lets applications discover external providers and create icon
    subclasses bound to those providers.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, BaseFontProvider] = {}

    def register_provider(self, name: str, provider: BaseFontProvider) -> None:
        self._providers[name] = provider

    def get_provider(self, name: str) -> Optional[BaseFontProvider]:
        return self._providers.get(name)

    def names(self) -> Iterable[str]:
        return self._providers.keys()


def load_external_providers(registry: ProviderRegistry) -> None:
    for ep in entry_points(group="ttkbootstrap_icons.providers"):
        try:
            ProviderCls = ep.load()
            provider_instance = ProviderCls()
            registry.register_provider(provider_instance.name, provider_instance)
        except Exception:
            # Ignore bad entry points, but continue loading others
            pass
