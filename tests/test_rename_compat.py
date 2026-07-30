"""Tests for compatibility across the ttkbootstrap-icons → tkinter-icons rename.

Packs published under the old name register their provider under the old
entry-point group. Those packs must stay discoverable, or upgrading the base
package silently loses every icon set the user had installed.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from tkinter_icons import registry as registry_module
from tkinter_icons.registry import (
    LEGACY_PROVIDER_GROUP,
    PROVIDER_GROUP,
    NoIconPacksWarning,
    ProviderRegistry,
    load_external_providers,
)


@dataclass
class _FakeProvider:
    name: str

    def __call__(self):
        return self


@dataclass
class _FakeEntryPoint:
    name: str
    value: str
    provider: object

    def load(self):
        return self.provider


@pytest.fixture
def fake_groups(monkeypatch):
    """Serve entry points per group from a dict the test controls."""
    groups: dict[str, list[_FakeEntryPoint]] = {}

    def _entry_points(*, group):
        return list(groups.get(group, []))

    monkeypatch.setattr(registry_module, "entry_points", _entry_points)
    return groups


def _ep(name, provider_name, module):
    return _FakeEntryPoint(name, f"{module}:Provider", _FakeProvider(provider_name))


class TestGroupNames:
    def test_current_and_legacy_groups_differ(self):
        assert PROVIDER_GROUP == "tkinter_icons.providers"
        assert LEGACY_PROVIDER_GROUP == "ttkbootstrap_icons.providers"


class TestDiscovery:
    def test_finds_packs_in_the_current_group(self, fake_groups):
        fake_groups[PROVIDER_GROUP] = [_ep("mat", "mat", "tkinter_icons_mat.provider")]
        reg = ProviderRegistry()
        load_external_providers(reg)
        assert sorted(reg.names()) == ["mat"]

    def test_finds_packs_published_before_the_rename(self, fake_groups):
        """A pack still on the old name must not vanish after upgrading."""
        fake_groups[LEGACY_PROVIDER_GROUP] = [
            _ep("mat", "mat", "ttkbootstrap_icons_mat.provider")
        ]
        reg = ProviderRegistry()
        load_external_providers(reg)
        assert sorted(reg.names()) == ["mat"]

    def test_finds_packs_across_both_groups(self, fake_groups):
        fake_groups[PROVIDER_GROUP] = [_ep("bs", "bootstrap", "tkinter_icons_bs.provider")]
        fake_groups[LEGACY_PROVIDER_GROUP] = [
            _ep("mat", "mat", "ttkbootstrap_icons_mat.provider")
        ]
        reg = ProviderRegistry()
        load_external_providers(reg)
        assert sorted(reg.names()) == ["bootstrap", "mat"]

    def test_a_pack_in_both_groups_registers_once(self, fake_groups):
        """A pack declaring both groups must not be loaded twice."""
        shared = _ep("bs", "bootstrap", "tkinter_icons_bs.provider")
        fake_groups[PROVIDER_GROUP] = [shared]
        fake_groups[LEGACY_PROVIDER_GROUP] = [shared]
        reg = ProviderRegistry()
        load_external_providers(reg)
        assert sorted(reg.names()) == ["bootstrap"]

    def test_no_packs_in_either_group_warns(self, fake_groups):
        reg = ProviderRegistry()
        with pytest.warns(NoIconPacksWarning):
            load_external_providers(reg)
        assert list(reg.names()) == []


class TestCatalogueUsesNewNames:
    def test_packs_reference_the_renamed_distributions(self):
        from tkinter_icons.packs import KNOWN_PACKS

        for pack in KNOWN_PACKS:
            assert pack.distribution.startswith("tkinter-icons-"), pack.distribution
            assert pack.module.startswith("tkinter_icons_"), pack.module

    def test_install_commands_use_the_new_name(self):
        from tkinter_icons.packs import find_pack

        assert find_pack("material").install_command == 'pip install "tkinter-icons[material]"'
        assert find_pack("material").import_statement == "from tkinter_icons import MaterialIcon"
