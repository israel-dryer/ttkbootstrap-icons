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

**Coverage is kept as sorted ranges, not as a set of codepoints.** The two hold
the same information and the ranges hold it about 333 times smaller: across the
thirty-one styles this project ships, 17.4 KB of bounds against 5,792 KB of
codepoint sets. (Ranges are `Coverage.nbytes`, the bounds buffer; sets are the
`frozenset` this used to return plus its int objects. Neither figure means much
without saying which.) A font's coverage is overwhelmingly contiguous — 73,990
codepoints fall into 2,231 ranges — so the set form was paying an int object per
codepoint to hold what a pair of bounds already says.

The extremes are two different fonts, which is worth knowing before quoting one
of them. The largest *set* is Fluent's `filled` at 741 KB, whose coverage is two
ranges and 16 bytes here. The largest *bounds* array is Font Awesome's `solid`
at 5,672 bytes, because its 1,966 codepoints are scattered across 709 ranges —
the most fragmented coverage the project ships, and still 32× smaller than the
182 KB it costs as a set.

Membership is a `bisect` over an `array` rather than a hash lookup, 0.18 µs
against 0.04 µs measured over 54,993 lookups. That is the whole cost of the
change, and it is nothing beside the render it guards.

**Unparseable means unknown, not empty.** Every failure path returns `None`
rather than an empty `Coverage`. Empty would say "this font contains no
codepoints at all", which would raise on every icon in a pack the moment an
unusual font appeared. `None` means the caller learned nothing and must draw the
glyph as it always has. A guard that cannot read a font must not be the thing
that breaks it.

Only the Unicode-addressed subtables are read — platform 0 (Unicode) and
platform 3 (Windows, including the symbol encoding icon fonts use). Platform 1
(Macintosh) subtables address glyphs by byte value rather than by codepoint, so
including them would report coverage of U+0000–U+00FF that has nothing to do
with the codepoints a glyph map holds. Every recognized subtable is unioned:
this asks whether a font *can* draw a codepoint, and any subtable that maps it
is proof that it can.

**Anything this module cannot read makes the whole font unknown.** Reporting
what it did understand and calling that the answer would be a *partial* read
presented as authoritative — the rest of the font's coverage would come back as
"absent", and the caller would blame the pack's glyph map for a pack that is
fine. That is the same silent-blank failure inverted. So an unhandled subtable
format raises, and so does a structurally impossible entry inside a subtable
this module does handle; both land in the `None` path above. The one exception
is format 14, which maps variation *sequences* onto glyphs another subtable
already reaches: it carries no coverage of its own, so skipping it loses
nothing and is not the same thing as failing to read it.
"""

from __future__ import annotations

import struct
from array import array
from bisect import bisect_right
from typing import Iterable, Iterator, Optional

# Codepoints that map to glyph 0 are excluded everywhere below. Glyph 0 is
# `.notdef` by definition, so a cmap entry pointing at it carries no glyph —
# which is exactly the state this module exists to detect.
_NOTDEF = 0

#: Half-open interval bounds are stored in an unsigned-int array. `"I"` is at
#: least 2 bytes by the language spec and is 4 on every platform CPython builds
#: on; the assertion is here so a hypothetical 2-byte `"I"` fails loudly at
#: import rather than silently truncating supplementary-plane codepoints.
assert array("I").itemsize >= 4, "array('I') too narrow to hold a Unicode codepoint"


class Coverage:
    """The codepoints a font can draw, held as sorted half-open ranges.

    Built by `cmap_coverage`. Supports `in`, `len()` and iteration, so it reads
    like the `frozenset` it replaces at every call site that matters:

        if ord(character) in coverage: ...

    Internally it is a flat `array("I")` of alternating `start, end + 1` bounds
    with the ranges disjoint and ascending, which makes membership the parity of
    a `bisect_right`: an odd insertion point means the codepoint fell inside a
    range rather than in the gap after one.
    """

    __slots__ = ("_bounds",)

    def __init__(self, ranges: Iterable[tuple[int, int]]):
        """Build from disjoint ascending inclusive `(start, end)` pairs."""
        bounds = array("I")
        for start, end in ranges:
            bounds.append(start)
            bounds.append(end + 1)
        self._bounds = bounds

    def __contains__(self, codepoint: object) -> bool:
        if not isinstance(codepoint, int) or isinstance(codepoint, bool):
            return False
        if codepoint < 0:
            # `bisect` would answer 0 — even, so already False — but an array
            # of unsigned bounds has no business being asked about a negative.
            return False
        return bisect_right(self._bounds, codepoint) % 2 == 1

    def __len__(self) -> int:
        """How many codepoints are covered, summed over the ranges."""
        bounds = self._bounds
        return sum(bounds[i + 1] - bounds[i] for i in range(0, len(bounds), 2))

    def __iter__(self) -> Iterator[int]:
        """Every covered codepoint, ascending. Materializes nothing."""
        bounds = self._bounds
        for i in range(0, len(bounds), 2):
            yield from range(bounds[i], bounds[i + 1])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coverage):
            return NotImplemented
        return self._bounds == other._bounds

    __hash__ = None  # type: ignore[assignment]

    @property
    def range_count(self) -> int:
        """How many contiguous ranges the coverage occupies."""
        return len(self._bounds) // 2

    @property
    def nbytes(self) -> int:
        """Bytes held by the bounds array.

        Public because it is the thing worth regression-testing. The whole
        reason for the range form is that it does not grow with the number of
        codepoints, and a future change back to a per-codepoint structure would
        pass every correctness test in the suite while quietly costing 333×
        this.
        """
        return self._bounds.buffer_info()[1] * self._bounds.itemsize

    def __repr__(self) -> str:
        return f"Coverage({len(self)} codepoints in {self.range_count} ranges)"


def cmap_coverage(font_bytes: bytes) -> Optional[Coverage]:
    """Return what the font can draw, or `None` if its `cmap` cannot be read.

    Args:
        font_bytes: The raw contents of a TrueType/OpenType font file, or of a
            font collection (the first font in it is used).

    Returns:
        A `Coverage` over the codepoints mapped to a real glyph, or `None` when
        the font has no readable Unicode `cmap`. `None` means "unknown" —
        callers must treat it as no evidence either way, never as "contains
        nothing".
    """
    try:
        return _cmap_coverage(font_bytes)
    except (struct.error, IndexError, ValueError):
        # A font we cannot parse is a font we know nothing about. Callers fall
        # back to drawing the glyph, which is what they did before this existed.
        return None


def _cmap_coverage(font_bytes: bytes) -> Optional[Coverage]:
    """Parse the Unicode `cmap` subtables. Raises on a malformed font."""
    table_directory = _table_directory_offset(font_bytes)
    cmap_offset = _find_table(font_bytes, table_directory, b"cmap")
    if cmap_offset is None:
        return None

    (subtable_count,) = struct.unpack_from(">H", font_bytes, cmap_offset + 2)

    ranges: list[tuple[int, int]] = []
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
            # one of these reports unknown rather than empty coverage.
            continue
        found = True
        ranges.extend(parsed)

    return Coverage(_merge(ranges)) if found else None


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


def _merge(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Sort and coalesce inclusive ranges into disjoint ascending ones.

    Ranges arrive from several subtables and are unioned, so overlap between
    them is normal — the format 4 and format 12 tables of a font usually agree
    across the BMP. Touching ranges are coalesced too (`end + 1 == start`),
    since a gap of zero codepoints is not a gap and leaving it in would cost a
    pair of bounds to say nothing.

    Sorting here is also what makes the parsers below free to emit their ranges
    in whatever order the font presents them. The specification says segments
    and groups are ascending; nothing enforces that a real file obeys it, and
    correctness must not rest on it.
    """
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged


def _runs(codepoints: Iterable[int]) -> list[tuple[int, int]]:
    """Coalesce codepoints into inclusive ranges as they are produced.

    For the formats that map codepoints one at a time, this is what keeps peak
    memory proportional to the number of ranges rather than to the number of
    codepoints. Out-of-order input yields more ranges than necessary but never
    a wrong answer, because `_merge` sorts.
    """
    runs: list[tuple[int, int]] = []
    for codepoint in codepoints:
        if runs and codepoint == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], codepoint)
        else:
            runs.append((codepoint, codepoint))
    return runs


def _parse_subtable(font_bytes: bytes, offset: int) -> Optional[list[tuple[int, int]]]:
    """Dispatch on subtable format.

    Returns:
        The ranges of codepoints this subtable maps to a real glyph, or `None`
        for a subtable that carries no coverage of its own and is deliberately
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


def _parse_format_0(font_bytes: bytes, offset: int) -> list[tuple[int, int]]:
    """Byte encoding table: 256 single-byte glyph ids."""
    glyph_ids = font_bytes[offset + 6:offset + 6 + 256]
    if len(glyph_ids) < 256:
        raise ValueError("format 0 cmap subtable is truncated")
    return _runs(code for code, glyph in enumerate(glyph_ids) if glyph != _NOTDEF)


def _parse_format_4(font_bytes: bytes, offset: int) -> list[tuple[int, int]]:
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

    def covered() -> Iterator[int]:
        for segment in range(segment_count):
            (end_code,) = struct.unpack_from(">H", font_bytes, end_codes + segment * 2)
            (start_code,) = struct.unpack_from(">H", font_bytes, start_codes + segment * 2)
            (id_delta,) = struct.unpack_from(">h", font_bytes, id_deltas + segment * 2)
            range_offset_at = id_range_offsets + segment * 2
            (id_range_offset,) = struct.unpack_from(">H", font_bytes, range_offset_at)

            if start_code > end_code:
                # Not a segment this parser can make sense of, and skipping it
                # would report the font's coverage as smaller than it is while
                # presenting that as the answer. Unknown is the honest result.
                raise ValueError(
                    f"format 4 cmap segment {segment} starts at "
                    f"U+{start_code:04X} and ends at U+{end_code:04X}"
                )
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
                    yield code

    return _runs(covered())


def _parse_format_6(font_bytes: bytes, offset: int) -> list[tuple[int, int]]:
    """Trimmed table mapping: a contiguous run of codepoints."""
    first_code, entry_count = struct.unpack_from(">HH", font_bytes, offset + 6)

    def covered() -> Iterator[int]:
        for index in range(entry_count):
            (glyph_id,) = struct.unpack_from(">H", font_bytes, offset + 10 + index * 2)
            if glyph_id != _NOTDEF:
                yield first_code + index

    return _runs(covered())


def _parse_format_12(font_bytes: bytes, offset: int) -> list[tuple[int, int]]:
    """Segmented coverage — the table that reaches past the BMP.

    Icon fonts that place their glyphs in the supplementary private-use area
    (Material Design Icons, at U+F0001 and up) are only addressable here.

    Each group is emitted as one range rather than walked codepoint by
    codepoint. Glyph ids run consecutively from `startGlyphID`, and every term
    is non-negative, so `startGlyphID + (code - startCharCode)` is zero for at
    most one code in the group — the first, and only when `startGlyphID` is
    itself zero. That case is the group's whole `.notdef` exposure, so trimming
    one codepoint off the front covers it exactly. Walking instead would cost a
    million iterations on a group that legitimately spans a plane.
    """
    (group_count,) = struct.unpack_from(">I", font_bytes, offset + 12)

    ranges: list[tuple[int, int]] = []
    for group in range(group_count):
        start_char, end_char, start_glyph = struct.unpack_from(
            ">III", font_bytes, offset + 16 + group * 12
        )
        if start_char > end_char or end_char > 0x10FFFF:
            # As in format 4: a group this parser cannot read has to make the
            # font unknown rather than quietly shrink its reported coverage.
            raise ValueError(
                f"format 12 cmap group {group} spans "
                f"U+{start_char:04X}..U+{end_char:04X}"
            )
        if start_glyph == _NOTDEF:
            start_char += 1
            if start_char > end_char:
                continue
        ranges.append((start_char, end_char))
    return ranges


__all__ = ["Coverage", "cmap_coverage"]
