from __future__ import annotations

import warnings
from importlib.metadata import entry_points
from typing import Dict, Iterable, Optional

from .packs import no_packs_message
from .providers import BaseFontProvider


#: Entry-point group icon packs register their provider under.
PROVIDER_GROUP = "tkinter_icons.providers"

#: The group used before the rename from ttkbootstrap-icons. Still scanned so
#: packs published under the old name keep working with this package.
LEGACY_PROVIDER_GROUP = "ttkbootstrap_icons.providers"


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

    Both the current and the pre-rename entry-point groups are scanned, so a
    pack published as `ttkbootstrap-icons-*` stays discoverable alongside one
    published as `tkinter-icons-*`. A pack appearing in both groups is
    registered once — its provider name is the identity, not the group.

    Args:
        registry: The registry to populate.
    """
    seen: set[str] = set()
    providers_found = []
    for group in (PROVIDER_GROUP, LEGACY_PROVIDER_GROUP):
        for ep in entry_points(group=group):
            if ep.value in seen:
                continue
            seen.add(ep.value)
            providers_found.append(ep)

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
