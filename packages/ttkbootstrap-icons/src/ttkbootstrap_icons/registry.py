from __future__ import annotations

import warnings
from importlib.metadata import entry_points
from typing import Dict, Iterable, Optional

from .packs import no_packs_message
from .providers import BaseFontProvider


class NoIconPacksWarning(UserWarning):
    """Warned when provider discovery finds no icon packs installed."""


class ProviderLoadWarning(UserWarning):
    """Warned when an icon pack's entry point fails to load."""


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
    """Discover installed icon packs and register their providers.

    Problems are raised as warnings rather than printed, so an application can
    route them through `warnings` (silence them, turn them into errors, or send
    them to a log) instead of finding text on its stdout.

    Args:
        registry: The registry to populate.
    """
    providers_found = list(entry_points(group="ttkbootstrap_icons.providers"))

    if not providers_found:
        warnings.warn(no_packs_message(), NoIconPacksWarning, stacklevel=2)
        return

    for ep in providers_found:
        try:
            provider_instance = ep.load()()
            registry.register_provider(provider_instance.name, provider_instance)
        except Exception as exc:
            # A broken pack must never stop an application from starting.
            warnings.warn(
                f"Icon pack entry point '{ep.name}' -> {ep.value} failed to load: {exc}",
                ProviderLoadWarning,
                stacklevel=2,
            )
