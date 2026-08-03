"""Tests for glyphmap parsing and icon-set construction."""

from __future__ import annotations

import pytest

from tkinter_icons.iconset import (
    IconSet,
    clear_icon_sets,
    get_icon_set,
    icon_set_id,
    parse_glyphmap,
    registered_icon_sets,
)


class TestParseGlyphmap:
    """The provider packages ship three different glyphmap layouts."""

    def test_flat_hex_map(self):
        assert parse_glyphmap({"house": "EA01"}) == {"house": chr(0xEA01)}

    def test_flat_int_map(self):
        assert parse_glyphmap({"house": 59905}) == {"house": chr(59905)}

    def test_dict_of_dicts(self):
        result = parse_glyphmap({"house": {"unicode": "EA01", "extra": "ignored"}})
        assert result == {"house": chr(0xEA01)}

    def test_list_of_dicts(self):
        result = parse_glyphmap([{"name": "house", "unicode": "EA01"}])
        assert result == {"house": chr(0xEA01)}

    def test_empty_map(self):
        assert parse_glyphmap({}) == {}

    def test_names_are_stripped(self):
        assert parse_glyphmap({"  house  ": "EA01"}) == {"house": chr(0xEA01)}

    @pytest.mark.parametrize(
        "data",
        [
            {"good": "EA01", "bad": "not-hex"},
            {"good": "EA01", "bad": None},
            [{"name": "good", "unicode": "EA01"}, {"name": "bad"}],
            [{"name": "good", "unicode": "EA01"}, {"unicode": "EA02"}],
            [{"name": "good", "unicode": "EA01"}, "not-a-dict"],
        ],
    )
    def test_malformed_entries_are_skipped_not_fatal(self, data):
        """One bad row in a generated asset must not take down the pack."""
        assert parse_glyphmap(data) == {"good": chr(0xEA01)}

    def test_unsupported_shape_raises(self):
        with pytest.raises(TypeError):
            parse_glyphmap("nonsense")


class TestIconSet:
    def test_lookup_helpers(self):
        icon_set = IconSet(id="x:y", font_bytes=b"", glyphs={"a": ""}, metrics={"a": [0, 0, 1, 1]})
        assert icon_set.glyph("a") == ""
        assert icon_set.glyph("missing") is None
        assert icon_set.ink("a") == [0, 0, 1, 1]
        assert icon_set.ink("missing") is None
        assert "a" in icon_set and "missing" not in icon_set
        assert len(icon_set) == 1

    def test_font_key_is_the_set_id(self):
        icon_set = IconSet(id="bootstrap:outline", font_bytes=b"", glyphs={})
        assert icon_set.font_key == "bootstrap:outline"


class TestIconSetCache:
    def test_same_provider_and_style_is_cached(self, provider):
        clear_icon_sets()
        assert get_icon_set(provider) is get_icon_set(provider)

    def test_id_distinguishes_styles(self, provider):
        assert icon_set_id(provider, "solid") != icon_set_id(provider, "regular")
        assert icon_set_id(provider, None).endswith(":default")

    def test_registry_reports_built_sets(self, provider):
        clear_icon_sets()
        assert registered_icon_sets() == {}
        icon_set = get_icon_set(provider)
        assert registered_icon_sets() == {icon_set.id: icon_set}

    def test_styles_get_independent_sets(self, registry):
        """Two styles of one provider must not share glyph data."""
        multi = next(
            (
                p for name in registry.names()
                if (p := registry.get_provider(name)).has_styles and not p.uses_single_file
            ),
            None,
        )
        if multi is None:
            pytest.skip("no multi-font provider installed")
        first, second = multi.style_list[0], multi.style_list[1]
        assert get_icon_set(multi, first) is not get_icon_set(multi, second)
        assert get_icon_set(multi, first).glyphs != get_icon_set(multi, second).glyphs

    def test_set_carries_provider_render_options(self, provider):
        assert get_icon_set(provider).options == provider.render_options


class TestProviderMetrics:
    def test_metrics_load_for_default_style(self, provider):
        metrics = provider.load_metrics()
        assert metrics, "provider ships no metrics.json — run tkicons-metrics"
        name, bounds = next(iter(metrics.items()))
        assert len(bounds) == 4
        assert all(isinstance(v, (int, float)) for v in bounds)

    def test_every_metric_name_is_a_real_glyph(self, provider):
        icon_set = get_icon_set(provider)
        unknown = set(icon_set.metrics) - set(icon_set.glyphs)
        assert not unknown, f"metrics reference missing glyphs: {sorted(unknown)[:5]}"

    def test_asset_suffix_matches_style_layout(self, provider):
        if provider.uses_single_file or not provider.has_styles:
            assert provider.asset_suffix() == ""
        else:
            assert provider.asset_suffix(provider.default_style) == f"-{provider.default_style}"

    def test_missing_metrics_degrade_to_empty(self, provider, monkeypatch):
        """A pack without metrics.json must load, not explode."""
        from tkinter_icons.providers import BaseFontProvider

        monkeypatch.setattr(BaseFontProvider, "_metrics_cache_global", {})
        monkeypatch.setattr(
            provider, "asset_suffix", lambda style=None: "-does-not-exist", raising=False
        )
        assert provider.load_metrics() == {}
