"""Read a font's Unicode coverage straight out of its bytes.

One question is asked here: **does this font contain this codepoint?** Nothing
in the rest of the stack can answer it. Pillow draws `.notdef` for a codepoint
the font lacks and reports nothing, and in most icon fonts `.notdef` is empty —
so a glyph map that advertises a codepoint the font never had renders as a
blank square with no exception and no warning. That was #140.

`fontTools` answers this in one line and is not available: the base package
depends on Pillow and `typing-extensions`, and a font-table parser is not worth
a third runtime dependency. So the `cmap` table is parsed here directly, which
is a small, well-specified job.

**Unparseable means unknown, not empty.** Every failure path returns `None`
rather than an empty set. An empty set would say "this font contains no
codepoints at all", which would blank or raise on every icon in a pack the
moment an unusual font appeared. `None` means the caller learned nothing and
must draw the glyph as it always has. A guard that cannot read a font must not
be the thing that breaks it.

Only the Unicode-addressed subtables are read — platform 0 (Unicode) and
platform 3 (Windows, including the symbol encoding icon fonts use). Platform 1
(Macintosh) subtables address glyphs by byte value rather than by codepoint, so
including them would report coverage of U+0000–U+00FF that has nothing to do
with the codepoints a glyph map holds. Every recognized subtable is unioned:
this asks whether a font *can* draw a codepoint, and any subtable that maps it
is proof that it can.

**A subtable this module cannot read makes the whole font unknown.** Unioning
the ones it does understand and returning that as the answer would be a
*partial* read reported as authoritative — the font's remaining coverage would
come back as "absent", and the caller would blame the pack's glyph map for a
pack that is fine. That is the same silent-blank failure inverted, so an
unhandled format raises and the font falls into the `None` path above. The one
exception is format 14, which maps variation *sequences* onto glyphs another
subtable already reaches: it carries no coverage of its own, so skipping it
loses nothing and is not the same thing as failing to read it.
"""

from __future__ import annotations

import struct
from typing import Optional

# Codepoints that map to glyph 0 are excluded everywhere below. Glyph 0 is
# `.notdef` by definition, so a cmap entry pointing at it carries no glyph —
# which is exactly the state this module exists to detect.
_NOTDEF = 0


def cmap_codepoints(font_bytes: bytes) -> Optional[frozenset[int]]:
    """Return every codepoint the font can draw, or `None` if it cannot be read.

    Args:
        font_bytes: The raw contents of a TrueType/OpenType font file, or of a
            font collection (the first font in it is used).

    Returns:
        The set of codepoints mapped to a real glyph, or `None` when the font
        has no readable Unicode `cmap`. `None` means "unknown" — callers must
        treat it as no evidence either way, never as "contains nothing".
    """
    try:
        return _cmap_codepoints(font_bytes)
    except (struct.error, IndexError, ValueError):
        # A font we cannot parse is a font we know nothing about. Callers fall
        # back to drawing the glyph, which is what they did before this existed.
        return None


def _cmap_codepoints(font_bytes: bytes) -> Optional[frozenset[int]]:
    """Parse the Unicode `cmap` subtables. Raises on a malformed font."""
    table_directory = _table_directory_offset(font_bytes)
    cmap_offset = _find_table(font_bytes, table_directory, b"cmap")
    if cmap_offset is None:
        return None

    (subtable_count,) = struct.unpack_from(">H", font_bytes, cmap_offset + 2)

    codepoints: set[int] = set()
    found = False
    for index in range(subtable_count):
        platform_id, encoding_id, subtable_offset = struct.unpack_from(
            ">HHI", font_bytes, cmap_offset + 4 + index * 8
        )
        if not _is_unicode_encoding(platform_id, encoding_id):
            continue
        parsed = _parse_subtable(font_bytes, cmap_offset + subtable_offset)
        if parsed is None:
            # A subtable that carries no coverage of its own. It is skipped
            # without setting `found`, so a font whose only Unicode subtable is
            # one of these reports unknown rather than an empty set.
            continue
        found = True
        codepoints |= parsed

    return frozenset(codepoints) if found else None


def _table_directory_offset(font_bytes: bytes) -> int:
    """Return the offset of the table directory, stepping into a collection."""
    if font_bytes[:4] == b"ttcf":
        # A collection's header is followed by an array of offsets, one per
        # font. Packs ship a single face, so the first one is the right one.
        (first_font,) = struct.unpack_from(">I", font_bytes, 12)
        return first_font
    return 0


def _find_table(font_bytes: bytes, directory: int, tag: bytes) -> Optional[int]:
    """Return the file offset of a named table, or `None` if it is absent."""
    (table_count,) = struct.unpack_from(">H", font_bytes, directory + 4)
    for index in range(table_count):
        record = directory + 12 + index * 16
        if font_bytes[record:record + 4] == tag:
            (offset,) = struct.unpack_from(">I", font_bytes, record + 8)
            return offset
    return None


def _is_unicode_encoding(platform_id: int, encoding_id: int) -> bool:
    """Whether a subtable addresses glyphs by Unicode codepoint.

    Platform 0 is Unicode by definition, at every encoding. Platform 3
    (Windows) is Unicode at encoding 0 — nominally "symbol", where the font's
    own private-use codepoints are the keys, which is precisely how a glyph map
    stores them — and at encodings 1 and 10, the BMP and the full repertoire.

    Its encodings 2 to 6 are ShiftJIS, PRC, Big5, Wansung and Johab, which
    address glyphs by legacy multi-byte code value rather than by codepoint.
    Excluding them is the same call platform 1 gets, for the same reason: their
    keys are not codepoints, so unioning them would report coverage a glyph map
    can never ask about. It also keeps them away from the dispatch below, which
    matters more than it looks — those subtables are format 2 in practice, and
    an unhandled format now makes the *whole font* unknown. Admitting them
    would mean a font carrying one legacy table lost the coverage check for
    every glyph it has.
    """
    if platform_id == 0:
        return True
    return platform_id == 3 and encoding_id in (0, 1, 10)


def _parse_subtable(font_bytes: bytes, offset: int) -> Optional[set[int]]:
    """Dispatch on subtable format.

    Returns:
        The codepoints this subtable maps to a real glyph, or `None` for a
        subtable that carries no coverage of its own and is deliberately
        skipped.

    Raises:
        ValueError: for a format that does carry coverage and is not read here
            — formats 2 and 13, and anything a later specification adds. The
            caller turns that into "this font is unknown", because unioning
            only the subtables that *were* understood would report the font's
            real coverage as smaller than it is.
    """
    (subtable_format,) = struct.unpack_from(">H", font_bytes, offset)
    if subtable_format == 4:
        return _parse_format_4(font_bytes, offset)
    if subtable_format == 12:
        return _parse_format_12(font_bytes, offset)
    if subtable_format == 6:
        return _parse_format_6(font_bytes, offset)
    if subtable_format == 0:
        return _parse_format_0(font_bytes, offset)
    if subtable_format == 14:
        # Unicode Variation Sequences. Every glyph it selects is reachable
        # through a base subtable, so it adds nothing to a coverage question.
        return None
    raise ValueError(f"unhandled cmap subtable format {subtable_format}")


def _parse_format_0(font_bytes: bytes, offset: int) -> set[int]:
    """Byte encoding table: 256 single-byte glyph ids."""
    glyph_ids = font_bytes[offset + 6:offset + 6 + 256]
    return {code for code, glyph in enumerate(glyph_ids) if glyph != _NOTDEF}


def _parse_format_4(font_bytes: bytes, offset: int) -> set[int]:
    """Segment mapping to delta values — the standard BMP table.

    The `idRangeOffset` indirection is the awkward part: a non-zero value is a
    byte offset measured *from the position of that entry itself*, into an
    array that runs on past the end of the declared arrays. It is computed here
    the way the specification words it rather than being flattened, because the
    flattened form is where off-by-one errors live.
    """
    segment_count = struct.unpack_from(">H", font_bytes, offset + 6)[0] // 2

    end_codes = offset + 14
    start_codes = end_codes + segment_count * 2 + 2  # +2 for reservedPad
    id_deltas = start_codes + segment_count * 2
    id_range_offsets = id_deltas + segment_count * 2

    codepoints: set[int] = set()
    for segment in range(segment_count):
        (end_code,) = struct.unpack_from(">H", font_bytes, end_codes + segment * 2)
        (start_code,) = struct.unpack_from(">H", font_bytes, start_codes + segment * 2)
        (id_delta,) = struct.unpack_from(">h", font_bytes, id_deltas + segment * 2)
        range_offset_at = id_range_offsets + segment * 2
        (id_range_offset,) = struct.unpack_from(">H", font_bytes, range_offset_at)

        if start_code > end_code:
            continue
        if start_code == 0xFFFF:
            # The required terminating segment, which maps nothing.
            continue

        for code in range(start_code, min(end_code, 0xFFFE) + 1):
            if id_range_offset == 0:
                glyph_id = (code + id_delta) & 0xFFFF
            else:
                glyph_at = range_offset_at + id_range_offset + (code - start_code) * 2
                (glyph_id,) = struct.unpack_from(">H", font_bytes, glyph_at)
                if glyph_id != _NOTDEF:
                    glyph_id = (glyph_id + id_delta) & 0xFFFF
            if glyph_id != _NOTDEF:
                codepoints.add(code)
    return codepoints


def _parse_format_6(font_bytes: bytes, offset: int) -> set[int]:
    """Trimmed table mapping: a contiguous run of codepoints."""
    first_code, entry_count = struct.unpack_from(">HH", font_bytes, offset + 6)
    codepoints: set[int] = set()
    for index in range(entry_count):
        (glyph_id,) = struct.unpack_from(">H", font_bytes, offset + 10 + index * 2)
        if glyph_id != _NOTDEF:
            codepoints.add(first_code + index)
    return codepoints


def _parse_format_12(font_bytes: bytes, offset: int) -> set[int]:
    """Segmented coverage — the table that reaches past the BMP.

    Icon fonts that place their glyphs in the supplementary private-use area
    (Material Design Icons, at U+F0001 and up) are only addressable here.
    """
    (group_count,) = struct.unpack_from(">I", font_bytes, offset + 12)

    codepoints: set[int] = set()
    for group in range(group_count):
        start_char, end_char, start_glyph = struct.unpack_from(
            ">III", font_bytes, offset + 16 + group * 12
        )
        if start_char > end_char or end_char > 0x10FFFF:
            continue
        for code in range(start_char, end_char + 1):
            if start_glyph + (code - start_char) != _NOTDEF:
                codepoints.add(code)
    return codepoints


__all__ = ["cmap_codepoints"]
