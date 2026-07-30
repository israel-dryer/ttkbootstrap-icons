"""Tests for the pack catalogue and the single import root.

The catalogue is the source of truth behind every "install this" message and
behind the lazy re-export, so it has to stay in step with the actual packages —
these tests check it against the repo's own pyproject files.
"""

from __future__ import annotations

import importlib
import sys
import tomllib
from pathlib import Path

import pytest

import ttkbootstrap_icons
from ttkbootstrap_icons.packs import (
    KNOWN_PACKS,
    PACK_BY_EXPORT,
    find_pack,
    installed_packs,
    missing_pack_message,
    no_packs_message,
)

REPO = Path(__file__).resolve().parent.parent
PACKAGES = REPO / "packages"


class TestCatalogue:
    def test_every_pack_is_uniquely_keyed(self):
        for field in ("extra", "distribution", "module", "provider"):
            values = [getattr(p, field) for p in KNOWN_PACKS]
            assert len(values) == len(set(values)), f"duplicate {field}"

    def test_export_names_do_not_collide(self):
        names = [n for p in KNOWN_PACKS for n in p.export_names]
        assert len(names) == len(set(names))

    def test_alias_defaults_to_the_class_name(self):
        pack = find_pack("bootstrap")
        assert pack.alias == pack.icon_class == "BootstrapIcon"
        assert pack.export_names == ("BootstrapIcon",)

    def test_renamed_packs_export_both_spellings(self):
        pack = find_pack("material")
        assert pack.alias == "MaterialIcon"
        assert pack.icon_class == "MatIcon"
        assert set(pack.export_names) == {"MaterialIcon", "MatIcon"}

    @pytest.mark.parametrize(
        "key", ["material", "ttkbootstrap-icons-mat", "ttkbootstrap_icons_mat", "mat"]
    )
    def test_lookup_accepts_any_name_a_pack_goes_by(self, key):
        assert find_pack(key) is find_pack("material")

    def test_lookup_is_case_and_separator_insensitive(self):
        assert find_pack("Google-Material") is find_pack("google-material")
        assert find_pack("RPG_AWESOME") is find_pack("rpg-awesome")

    def test_unknown_key_returns_none(self):
        assert find_pack("not-a-pack") is None

    def test_install_command_is_shell_quoted(self):
        # Unquoted brackets are a glob in most shells; zsh fails outright.
        assert find_pack("material").install_command == 'pip install "ttkbootstrap-icons[material]"'

    def test_import_statement_uses_the_single_root(self):
        assert find_pack("material").import_statement == "from ttkbootstrap_icons import MaterialIcon"


class TestCatalogueMatchesRepo:
    """Guards against the catalogue drifting from the actual packages."""

    def _pyproject(self, pack):
        path = PACKAGES / pack.distribution / "pyproject.toml"
        if not path.exists():
            pytest.skip(f"{pack.distribution} not present in this checkout")
        return tomllib.loads(path.read_text(encoding="utf-8-sig"))

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_distribution_exists_with_matching_name(self, pack):
        assert self._pyproject(pack)["project"]["name"] == pack.distribution

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_module_directory_exists(self, pack):
        src = PACKAGES / pack.distribution / "src" / pack.module
        if not src.parent.exists():
            pytest.skip(f"{pack.distribution} not present in this checkout")
        assert src.is_dir()

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_icon_class_is_exported_by_its_module(self, pack):
        init = PACKAGES / pack.distribution / "src" / pack.module / "__init__.py"
        if not init.exists():
            pytest.skip(f"{pack.distribution} not present in this checkout")
        assert pack.icon_class in init.read_text(encoding="utf-8-sig")

    @pytest.mark.parametrize("pack", KNOWN_PACKS, ids=lambda p: p.extra)
    def test_base_declares_an_extra_for_every_pack(self, pack):
        base = PACKAGES / "ttkbootstrap-icons" / "pyproject.toml"
        extras = tomllib.loads(base.read_text(encoding="utf-8-sig"))["project"]["optional-dependencies"]
        assert pack.extra in extras, f"no [{pack.extra}] extra in the base pyproject"
        assert any(pack.distribution in dep for dep in extras[pack.extra])

    def test_all_extra_covers_every_pack(self):
        base = PACKAGES / "ttkbootstrap-icons" / "pyproject.toml"
        extras = tomllib.loads(base.read_text(encoding="utf-8-sig"))["project"]["optional-dependencies"]
        combined = " ".join(extras["all"])
        missing = [p.extra for p in KNOWN_PACKS if p.extra not in combined]
        assert not missing, f"[all] omits: {missing}"


class TestMessages:
    def test_no_packs_message_explains_the_split(self):
        text = no_packs_message()
        assert "renderer" in text
        assert 'pip install "ttkbootstrap-icons[bootstrap]"' in text
        assert '[all]' in text

    def test_missing_pack_message_names_the_extra(self):
        text = missing_pack_message("material")
        assert 'pip install "ttkbootstrap-icons[material]"' in text
        assert "Material Design Icons" in text

    def test_missing_pack_message_lists_what_is_installed(self, provider):
        assert "Currently installed:" in missing_pack_message("material")

    def test_unknown_pack_message_lists_the_valid_ones(self):
        text = missing_pack_message("nonsense")
        assert "Unknown icon pack" in text
        assert "material" in text and "bootstrap" in text


class TestImportRoot:
    def test_installed_pack_resolves_from_the_base(self):
        from ttkbootstrap_icons import BootstrapIcon

        from ttkbootstrap_icons_bs import BootstrapIcon as direct

        assert BootstrapIcon is direct

    def test_alias_and_original_name_are_the_same_class(self):
        assert ttkbootstrap_icons.FontAwesomeIcon is ttkbootstrap_icons.FAIcon

    def test_original_package_import_still_works(self):
        """Existing code must keep working after the single root is added."""
        module = importlib.import_module("ttkbootstrap_icons_fa")
        assert module.FAIcon is ttkbootstrap_icons.FAIcon

    def test_missing_pack_raises_import_error_with_the_command(self, monkeypatch):
        pack = find_pack("material")
        monkeypatch.delitem(sys.modules, pack.module, raising=False)
        monkeypatch.delitem(ttkbootstrap_icons.__dict__, pack.alias, raising=False)
        monkeypatch.setattr(
            importlib, "import_module",
            lambda name, *a, **k: (_ for _ in ()).throw(ModuleNotFoundError(name)),
        )
        with pytest.raises(ImportError, match=r'pip install "ttkbootstrap-icons\[material\]"'):
            getattr(ttkbootstrap_icons, "MaterialIcon")

    def test_unknown_attribute_raises_attribute_error(self):
        with pytest.raises(AttributeError, match="NotAnIcon"):
            ttkbootstrap_icons.NotAnIcon

    def test_dir_lists_every_pack_class(self):
        listed = set(dir(ttkbootstrap_icons))
        assert set(PACK_BY_EXPORT) <= listed
        assert {"Icon", "RenderOptions", "IconSet"} <= listed

    def test_resolved_class_is_cached_on_the_module(self):
        ttkbootstrap_icons.__dict__.pop("BootstrapIcon", None)
        ttkbootstrap_icons.BootstrapIcon
        assert "BootstrapIcon" in ttkbootstrap_icons.__dict__

    def test_installed_packs_reflects_the_environment(self):
        names = {p.extra for p in installed_packs()}
        assert "bootstrap" in names
        assert all(find_pack(n).is_installed for n in names)
