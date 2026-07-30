"""Tests for the pure-PIL rendering core — no display required."""

from __future__ import annotations

import pytest
from PIL import Image

from ttkbootstrap_icons.render import (
    RenderOptions,
    auto_oversample,
    clear_font_cache,
    load_font,
    measure_ink_bounds,
    render_glyph,
    snap_size,
)


def solid_bbox(img: Image.Image, threshold: int = 40):
    """Bounding box of clearly-inked pixels.

    A plain `getbbox()` on the alpha channel also catches the faint ringing
    LANCZOS leaves around a downscaled glyph, which reaches the frame edge and
    makes every icon look full-bleed. Thresholding first measures the ink a
    viewer actually sees.
    """
    mask = img.getchannel("A").point(lambda v: 255 if v >= threshold else 0)
    return mask.getbbox()


class TestSizing:
    @pytest.mark.parametrize(
        "size, expected",
        [(16, 16), (15, 16), (1, 2), (23, 24), (24, 24)],
    )
    def test_odd_sizes_snap_up_to_even(self, size, expected):
        assert snap_size(size) == expected

    def test_snapping_can_be_disabled(self):
        assert snap_size(15, snap_even=False) == 15

    @pytest.mark.parametrize(
        "size, factor",
        [(16, 3), (31, 3), (32, 2), (63, 2), (64, 1), (128, 1)],
    )
    def test_oversample_falls_off_with_size(self, size, factor):
        assert auto_oversample(size) == factor


class TestRenderOptions:
    def test_merge_ignores_none(self):
        base = RenderOptions(pad_factor=0.2, y_bias=0.05)
        merged = base.merge(pad_factor=None, y_bias=0.0)
        assert merged.pad_factor == 0.2
        assert merged.y_bias == 0.0

    def test_merge_leaves_original_alone(self):
        base = RenderOptions()
        base.merge(align=True)
        assert base.align is False

    def test_options_are_hashable(self):
        # Icon cache keys include the options, so they must hash.
        assert hash(RenderOptions()) == hash(RenderOptions())
        assert hash(RenderOptions(align=True)) != hash(RenderOptions())


class TestFontCache:
    def test_same_key_and_size_returns_one_object(self, icon_set):
        clear_font_cache()
        first = load_font(icon_set.font_key, icon_set.font_bytes, 32)
        second = load_font(icon_set.font_key, icon_set.font_bytes, 32)
        assert first is second

    def test_different_sizes_are_distinct(self, icon_set):
        clear_font_cache()
        assert load_font(icon_set.font_key, icon_set.font_bytes, 32) is not load_font(
            icon_set.font_key, icon_set.font_bytes, 33
        )

    def test_cache_is_bounded(self, icon_set):
        clear_font_cache()
        from ttkbootstrap_icons.render import _FONT_CACHE_MAX, _font_cache

        for size in range(8, 8 + _FONT_CACHE_MAX + 20):
            load_font(icon_set.font_key, icon_set.font_bytes, size)
        assert len(_font_cache) <= _FONT_CACHE_MAX


class TestRenderGlyph:
    def test_output_is_square_and_snapped(self, icon_set, sample_name):
        img = render_glyph(
            icon_set.glyph(sample_name), 15, "#000000",
            font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
        )
        assert img.size == (16, 16)
        assert img.mode == "RGBA"

    def test_empty_glyph_renders_transparent(self, icon_set):
        img = render_glyph(
            "", 24, "#000000",
            font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
        )
        assert img.getchannel("A").getbbox() is None

    def test_color_is_applied(self, icon_set, sample_name):
        img = render_glyph(
            icon_set.glyph(sample_name), 32, "#ff0000",
            font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
            ink=icon_set.ink(sample_name),
        )
        opaque = [
            img.getpixel((x, y))
            for x in range(img.width)
            for y in range(img.height)
            if img.getpixel((x, y))[3] > 200
        ]
        assert opaque, "glyph rendered no opaque pixels"
        assert all(r > 200 and g < 60 and b < 60 for r, g, b, _ in opaque)

    def test_padding_is_respected(self, icon_set, sample_name):
        """A glyph must not touch the frame edge when padding is asked for."""
        options = RenderOptions(pad_factor=0.2, y_bias=0.0)
        img = render_glyph(
            icon_set.glyph(sample_name), 64, "#000000",
            font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
            ink=icon_set.ink(sample_name), options=options,
        )
        box = solid_bbox(img)
        assert box is not None
        left, top, right, bottom = box
        assert left >= 5 and top >= 5
        assert right <= 59 and bottom <= 59

    def test_zero_padding_fills_the_frame(self, icon_set):
        """A full-bleed glyph with no padding should reach the edges."""
        name = self._full_bleed_name(icon_set)
        options = RenderOptions(pad_factor=0.0, y_bias=0.0, sharpen=False)
        img = render_glyph(
            icon_set.glyph(name), 64, "#000000",
            font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
            ink=icon_set.ink(name), options=options,
        )
        left, top, right, bottom = solid_bbox(img)
        assert left <= 1 and top <= 1
        assert right >= 63 and bottom >= 63

    @staticmethod
    def _full_bleed_name(icon_set):
        for name, ink in icon_set.metrics.items():
            if ink[2] >= 0.99 and ink[3] >= 0.99:
                return name
        pytest.skip("no full-bleed glyph in this icon set")


class TestInkCentering:
    """The reason metrics exist: ink lands dead center, not the em box."""

    def test_ink_is_centered_when_metrics_are_present(self, icon_set):
        options = RenderOptions(y_bias=0.0, sharpen=False)
        checked = 0
        for name in sorted(icon_set.metrics)[:25]:
            img = render_glyph(
                icon_set.glyph(name), 64, "#000000",
                font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
                ink=icon_set.ink(name), options=options,
            )
            box = solid_bbox(img)
            if box is None:
                continue
            left, top, right, bottom = box
            assert abs(left - (64 - right)) <= 2, f"{name} off-center horizontally"
            assert abs(top - (64 - bottom)) <= 2, f"{name} off-center vertically"
            checked += 1
        assert checked, "no glyphs were measured"

    def test_y_bias_shifts_the_glyph_down(self, icon_set, sample_name):
        kwargs = dict(
            font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
            ink=icon_set.ink(sample_name),
        )
        centered = render_glyph(
            icon_set.glyph(sample_name), 64, "#000000",
            options=RenderOptions(y_bias=0.0), **kwargs,
        )
        nudged = render_glyph(
            icon_set.glyph(sample_name), 64, "#000000",
            options=RenderOptions(y_bias=0.05), **kwargs,
        )
        assert solid_bbox(nudged)[1] > solid_bbox(centered)[1]

    def test_missing_metrics_still_render(self, icon_set, sample_name):
        """The getbbox fallback keeps packs without metrics working."""
        img = render_glyph(
            icon_set.glyph(sample_name), 32, "#000000",
            font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
            ink=None,
        )
        assert solid_bbox(img) is not None


class TestMeasureInkBounds:
    def test_bounds_are_normalized_fractions(self, icon_set, sample_name):
        font = load_font(icon_set.font_key, icon_set.font_bytes, 512)
        bounds = measure_ink_bounds(font, icon_set.glyph(sample_name), ref=512)
        assert bounds is not None
        left, top, width, height = bounds
        assert 0 < width <= 1.5 and 0 < height <= 1.5
        assert -1 < left < 1 and -2 < top < 2

    def test_measurement_is_size_independent(self, icon_set, sample_name):
        """Ink scales linearly, so the fractions must not depend on `ref`."""
        glyph = icon_set.glyph(sample_name)
        at_256 = measure_ink_bounds(load_font(icon_set.font_key, icon_set.font_bytes, 256), glyph, ref=256)
        at_512 = measure_ink_bounds(load_font(icon_set.font_key, icon_set.font_bytes, 512), glyph, ref=512)
        for a, b in zip(at_256, at_512):
            assert a == pytest.approx(b, abs=0.01)

    def test_glyph_with_no_ink_measures_none(self, icon_set):
        """Nothing drawn means no bounds — the generator skips these names.

        Note an icon font's U+0020 is usually *not* blank; it commonly carries
        a real glyph or a .notdef box, so an empty string is the honest case.
        """
        font = load_font(icon_set.font_key, icon_set.font_bytes, 128)
        assert measure_ink_bounds(font, "", ref=128) is None
