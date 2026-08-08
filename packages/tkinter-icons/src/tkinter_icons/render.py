"""Pure-PIL glyph rendering — the drawing core, with no Tkinter involvement.

Everything here works on `PIL.Image` objects and plain data, so it can be
exercised without a display. `icon.Icon` is the Tk-facing layer on top; if you
want to render an icon to a PIL image, a file, or anything that is not a ttk
widget, call `render_glyph` directly.

Centering strategy
------------------
Pillow's `font.getbbox()` under-reports the inked area of icon-font glyphs,
which leaves full-bleed icons with no padding and nudges others off-center. The
accurate route is to measure each glyph's true ink once, offline, and ship the
result: `measure_ink_bounds` produces normalized bounds that
`tools/generate_metrics.py` writes to a provider's `metrics.json`, and
`render_glyph` uses them to fit and center on real ink.

Providers published before metrics existed have none, so `render_glyph` falls
back to the `getbbox` measurement path. The fallback is less accurate, never
absent.
"""

from __future__ import annotations

import io
from collections import OrderedDict
from dataclasses import dataclass, replace
from typing import Optional, Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    _RESAMPLE_LANCZOS = Image.Resampling.LANCZOS  # Pillow >= 9.1.0
except AttributeError:  # pragma: no cover - older Pillow fallback
    _RESAMPLE_LANCZOS = Image.LANCZOS


#: Normalized ink bounds: ``[left, top, width, height]`` as fractions of the
#: font size, measured from the text draw origin.
InkBounds = Sequence[float]

#: Reference size used when measuring glyph ink. Large enough that hinting
#: noise is negligible relative to the measurement.
MEASURE_REF = 512

#: Decimal places kept per normalized fraction (sub-pixel even at 4K sizes).
MEASURE_PRECISION = 5

#: Cap on the number of live `FreeTypeFont` objects. Each distinct pixel size
#: makes a new one, and a resizable UI can walk through many.
_FONT_CACHE_MAX = 128

_font_cache: "OrderedDict[tuple[str, int], ImageFont.FreeTypeFont]" = OrderedDict()


@dataclass(frozen=True)
class RenderOptions:
    """Knobs controlling how a glyph is drawn into its frame.

    A provider supplies the defaults for its icon set; individual calls can
    override any of them via `RenderOptions.merge`.

    Attributes:
        pad_factor: Fraction of the frame reserved as padding on each edge. The
            glyph's ink is fitted to the box that remains.
        y_bias: Extra vertical offset as a fraction of the frame, applied after
            centering. Rarely needed once ink metrics are available — it exists
            to nudge icon sets whose glyphs are intentionally off-center.
        scale_to_fit: Shrink the glyph so its ink fits inside the padded box.
            When false the glyph is drawn at the frame size and only centered.
        oversample: Render at this multiple of the target size and downscale.
            `None` selects a factor from the target size (3x under 32px, 2x
            under 64px, 1x above).
        align: Snap the draw origin to the pixel grid of the *final* image, so
            edges land on whole pixels instead of being antialiased across a
            sub-pixel offset. Crisper for standalone marks that fill their
            frame; off by default so glyphs sitting beside text keep their exact
            optical centering.
        sharpen: Apply a light unsharp mask after downscaling, restoring the
            edge contrast that LANCZOS softens. No effect when not oversampling.
        snap_even: Round the requested size up to an even number of pixels.
            Eliminates half-pixel blur at fractional display scale factors
            (125%, 150%), where an odd size lands the glyph between pixels.
    """

    pad_factor: float = 0.10
    y_bias: float = 0.0
    scale_to_fit: bool = True
    oversample: Optional[int] = None
    align: bool = False
    sharpen: bool = True
    snap_even: bool = True

    def merge(self, **overrides) -> "RenderOptions":
        """Return a copy with `overrides` applied, ignoring `None` values.

        Args:
            **overrides: Any field of `RenderOptions`. A value of `None` leaves
                the existing value alone, so callers can pass optional
                arguments straight through.

        Returns:
            A new `RenderOptions`; `self` is unchanged.
        """
        clean = {k: v for k, v in overrides.items() if v is not None}
        return replace(self, **clean) if clean else self


def auto_oversample(size: int) -> int:
    """Return the oversample factor used for a target `size` in pixels."""
    if size < 32:
        return 3
    if size < 64:
        return 2
    return 1


def snap_size(size: int, *, snap_even: bool = True) -> int:
    """Round `size` up to the next even pixel count when `snap_even` is set.

    Args:
        size: Requested pixel size.
        snap_even: When false, `size` is returned unchanged.

    Returns:
        The size the icon will actually be rendered at. Callers that cache
        rendered images should key on this value, not the requested one.
    """
    size = max(1, int(size))
    if snap_even and size % 2:
        return size + 1
    return size


def load_font(font_key: str, font_bytes: bytes, size: int) -> ImageFont.FreeTypeFont:
    """Return a cached `FreeTypeFont` for `font_bytes` at `size`.

    The font is read from memory — no temporary file is written to disk, so
    there is nothing to clean up afterwards.

    Args:
        font_key: Stable identity for this font file, used as the cache key.
            Two calls with the same key must pass equivalent `font_bytes`.
        font_bytes: The raw font file.
        size: Pixel size to instantiate.

    Returns:
        A `FreeTypeFont`, shared with other callers using the same key and size.
    """
    key = (font_key, size)
    font = _font_cache.get(key)
    if font is not None:
        _font_cache.move_to_end(key)
        return font

    # Pillow reads lazily from the stream, so each font needs its own BytesIO
    # that stays alive as long as the font does. Holding it in the cache value
    # (via the font's own reference) is enough.
    font = ImageFont.truetype(io.BytesIO(font_bytes), size)
    _font_cache[key] = font
    while len(_font_cache) > _FONT_CACHE_MAX:
        _font_cache.popitem(last=False)
    return font


def clear_font_cache() -> None:
    """Drop every cached `FreeTypeFont`."""
    _font_cache.clear()


def measure_ink_bounds(
    font: ImageFont.FreeTypeFont,
    glyph: str,
    *,
    ref: int = MEASURE_REF,
    precision: int = MEASURE_PRECISION,
) -> Optional[list[float]]:
    """Measure a glyph's true inked bounds as fractions of the font size.

    A glyph's ink is color-independent and scales linearly with font size, so
    this only has to run once per glyph — offline, at a high reference size —
    and the result is reusable at every render size.

    Args:
        font: A font already instantiated at `ref` pixels.
        glyph: The single character to measure.
        ref: The size `font` was created at.
        precision: Decimal places to keep in the returned fractions.

    Returns:
        `[left, top, width, height]` relative to the text draw origin, as
        fractions of the font size, or `None` if the glyph renders no pixels.
    """
    # Generous canvas so glyphs extending past the em in any direction are still
    # captured; the draw origin sits one full ref inside the top-left corner.
    canvas = Image.new("RGBA", (ref * 3, ref * 3), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).text((ref, ref), glyph, font=font, fill="#000000")
    bbox = canvas.getchannel("A").getbbox()
    if bbox is None:
        return None
    left, top, right, bottom = bbox
    return [
        round((left - ref) / ref, precision),
        round((top - ref) / ref, precision),
        round((right - left) / ref, precision),
        round((bottom - top) / ref, precision),
    ]


def render_glyph(
    glyph: str,
    size: int,
    color: str,
    *,
    font_key: str,
    font_bytes: bytes,
    ink: Optional[InkBounds] = None,
    options: RenderOptions = RenderOptions(),
) -> Image.Image:
    """Draw a single glyph centered in a square RGBA image.

    Args:
        glyph: The character to draw.
        size: Edge length of the output in pixels, before even-snapping.
        color: Fill color, in any form Pillow accepts.
        font_key: Stable identity for the font file (see `load_font`).
        font_bytes: The raw font file.
        ink: Precomputed normalized ink bounds for this glyph, from
            `measure_ink_bounds`. When omitted, the glyph is measured at render
            time with `getbbox`, which is less accurate for full-bleed glyphs.
        options: How to fit, center, and post-process the glyph.

    Returns:
        A square RGBA image of the snapped size. Fully transparent if `glyph`
        is empty.
    """
    size = snap_size(size, snap_even=options.snap_even)
    if not glyph:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    oversample = options.oversample or auto_oversample(size)
    oversample = max(1, int(oversample))

    canvas_size = size * oversample
    pad = int(canvas_size * options.pad_factor)
    inner = max(1, canvas_size - 2 * pad)

    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if ink:
        font, dx, dy = _place_by_ink(glyph, ink, canvas_size, inner, font_key, font_bytes, options)
    else:
        font, dx, dy = _place_by_bbox(glyph, canvas_size, inner, pad, font_key, font_bytes, options)

    if options.y_bias:
        dy += canvas_size * options.y_bias

    if options.align:
        # Round to a multiple of the oversample factor so that, after the
        # downscale, the glyph lands on whole pixels of the final image.
        dx = round(dx / oversample) * oversample
        dy = round(dy / oversample) * oversample

    draw.text((dx, dy), glyph, font=font, fill=color)

    if oversample > 1:
        img = img.resize((size, size), _RESAMPLE_LANCZOS)
        if options.sharpen:
            img = img.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=0))

    return img


def _place_by_ink(
    glyph: str,
    ink: InkBounds,
    canvas_size: int,
    inner: int,
    font_key: str,
    font_bytes: bytes,
    options: RenderOptions,
) -> tuple[ImageFont.FreeTypeFont, float, float]:
    """Size and position a glyph from precomputed ink bounds.

    Fits the ink to the padded box without ever enlarging past the frame, then
    centers the ink — not the em box — in the frame.
    """
    left, top, width, height = ink
    if options.scale_to_fit:
        extent = max(width, height, 1e-6)
        font_size = max(1, int(min(canvas_size, inner / extent)))
    else:
        font_size = canvas_size

    font = load_font(font_key, font_bytes, font_size)
    ink_w, ink_h = width * font_size, height * font_size
    dx = (canvas_size - ink_w) / 2 - left * font_size
    dy = (canvas_size - ink_h) / 2 - top * font_size
    return font, dx, dy


def _place_by_bbox(
    glyph: str,
    canvas_size: int,
    inner: int,
    pad: int,
    font_key: str,
    font_bytes: bytes,
    options: RenderOptions,
) -> tuple[ImageFont.FreeTypeFont, float, float]:
    """Size and position a glyph by measuring it at render time.

    The fallback for glyphs with no entry in the provider's `metrics.json`.

    `getbbox` under-reports ink on icon fonts, and this only ever shrinks a
    glyph that overflows, so a glyph fitted this way lands *inside* the padded
    box rather than filling it — a per-pack median of 73% to 96% of it,
    against 94% to 102% on the ink path. Centering is vertical against
    `ascent + descent` rather than against the ink, so a set whose glyphs sit
    off the font's baseline rides high in the frame: over every style of all
    sixteen packs, 518 of the 89,169 glyphs that draw any ink run past the edge
    of the frame on this path, and 0 of them do on the ink path. (The glyph
    maps hold 89,292 entries; the 123 that render nothing are excluded, since
    an empty image cannot overflow.) Regenerate the provider's metrics to take
    the accurate path.
    """
    font = load_font(font_key, font_bytes, max(1, canvas_size))
    ascent, descent = font.getmetrics()
    bbox = font.getbbox(glyph)
    glyph_w = bbox[2] - bbox[0]
    glyph_h = bbox[3] - bbox[1]

    if options.scale_to_fit and (glyph_w > inner or glyph_h > inner):
        scale = min(inner / max(glyph_w, 1), inner / max(glyph_h, 1)) * 0.95
        font = load_font(font_key, font_bytes, max(1, int(canvas_size * scale)))
        ascent, descent = font.getmetrics()
        bbox = font.getbbox(glyph)
        glyph_w = bbox[2] - bbox[0]
        glyph_h = bbox[3] - bbox[1]

    full_height = ascent + descent
    dx = pad + (inner - glyph_w) / 2 - bbox[0]
    dy = pad + (inner - full_height) / 2 + (ascent - bbox[3])
    return font, dx, dy


__all__ = [
    "InkBounds",
    "MEASURE_PRECISION",
    "MEASURE_REF",
    "RenderOptions",
    "auto_oversample",
    "clear_font_cache",
    "load_font",
    "measure_ink_bounds",
    "render_glyph",
    "snap_size",
]