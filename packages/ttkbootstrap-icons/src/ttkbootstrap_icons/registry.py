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
    providers_found = list(entry_points(group="ttkbootstrap_icons.providers"))

    if not providers_found:
        print("[ttkbootstrap-icons] No icon providers installed.")
        print("[ttkbootstrap-icons] Install a provider package to use icons:")
        print("[ttkbootstrap-icons]   pip install ttkbootstrap-icons-bs  # Bootstrap Icons")
        print("[ttkbootstrap-icons]   pip install ttkbootstrap-icons-fa  # Font Awesome")
        print("[ttkbootstrap-icons]   pip install ttkbootstrap-icons-mat # Material Icons")
        print("[ttkbootstrap-icons] See: https://github.com/israel-dryer/ttkbootstrap-icons")

    for ep in providers_found:
        try:
            ProviderCls = ep.load()
            provider_instance = ProviderCls()
            registry.register_provider(provider_instance.name, provider_instance)
        except Exception as exc:
            # Print a lightweight warning to help debug bad entry points
            try:
                print(f"[ttkbootstrap-icons] Failed to load provider entry point '{ep.name}' -> {ep.value}: {exc}")
            except Exception:
                # Ensure failures here never break app startup
                pass
