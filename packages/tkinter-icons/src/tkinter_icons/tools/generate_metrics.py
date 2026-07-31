"""Generate ink-bounds metrics for installed icon providers.

The renderer centers glyphs on their true inked bounds, because Pillow's
`font.getbbox()` under-reports ink on icon fonts — which leaves full-bleed
icons with no padding and nudges others off-center. Ink is color-independent
and scales linearly with font size, so it is measured once per glyph at a high
reference size and stored as fractions of the em.

Run this whenever a provider's font or glyphmap changes::

    python -m tkinter_icons.tools.generate_metrics --all              # every installed provider
    python -m tkinter_icons.tools.generate_metrics fa mat             # named providers
    python -m tkinter_icons.tools.generate_metrics bootstrap --check  # verify without writing

Output goes next to the provider's glyphmap: `metrics.json` for single-font
providers, `metrics-<style>.json` for providers with a font per style.
"""

from __future__ import annotations

import argparse
import json
import sys
from importlib.resources import files
from pathlib import Path
from typing import Optional, Sequence

from ..iconset import parse_glyphmap
from ..providers import BaseFontProvider
from ..registry import ProviderRegistry, load_external_providers
from ..render import MEASURE_PRECISION, MEASURE_REF, load_font, measure_ink_bounds


def _provider_styles(provider: BaseFontProvider) -> list[Optional[str]]:
    """Return the styles that need their own metrics file.

    Providers backed by a single font file share one metrics file across every
    style, since ink is a property of the glyph, not of the name it goes by.
    """
    if provider.uses_single_file or not provider.has_styles:
        return [None]
    return list(provider.style_list)


def _output_dir(provider: BaseFontProvider, override: Optional[Path]) -> Path:
    """Resolve where a provider's metrics file should be written."""
    if override is not None:
        return override
    return Path(str(files(provider.package)))


def generate_for_style(
    provider: BaseFontProvider,
    style: Optional[str],
    *,
    ref: int = MEASURE_REF,
    precision: int = MEASURE_PRECISION,
) -> tuple[dict[str, list[float]], list[str]]:
    """Measure every glyph in one style of one provider.

    Args:
        provider: The provider to measure.
        style: Style name, or `None` for a single-font provider.
        ref: Reference render size in pixels.
        precision: Decimal places kept per fraction.

    Returns:
        A `(metrics, empty)` pair: the name-to-bounds map, and the names of
        glyphs that render no pixels at all (blanks and spacers, which the
        renderer draws as transparent anyway).
    """
    font_bytes, glyphmap_json = provider.load_assets(style=style)
    glyphs = parse_glyphmap(json.loads(glyphmap_json))
    font = load_font(f"measure:{provider.name}:{style}:{ref}", font_bytes, ref)

    metrics: dict[str, list[float]] = {}
    empty: list[str] = []
    for name in sorted(glyphs):
        bounds = measure_ink_bounds(font, glyphs[name], ref=ref, precision=precision)
        if bounds is None:
            empty.append(name)
        else:
            metrics[name] = bounds
    return metrics, empty


def generate_for_provider(
    provider: BaseFontProvider,
    *,
    out_dir: Optional[Path] = None,
    ref: int = MEASURE_REF,
    check: bool = False,
) -> bool:
    """Write (or verify) every metrics file for one provider.

    Args:
        provider: The provider to process.
        out_dir: Where to write. Defaults to the provider's own package
            directory, alongside its glyphmap.
        ref: Reference render size in pixels.
        check: Compare against what is on disk instead of writing. Used in CI
            to catch metrics that have drifted from their font.

    Returns:
        True if every style is up to date (or was written successfully).
    """
    target = _output_dir(provider, out_dir)
    ok = True

    for style in _provider_styles(provider):
        suffix = provider.asset_suffix(style)
        path = target / f"metrics{suffix}.json"
        metrics, empty = generate_for_style(provider, style, ref=ref)
        payload = json.dumps(metrics, indent=0, sort_keys=True) + "\n"

        label = f"{provider.name}{suffix}"
        if check:
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current == payload:
                print(f"  ok       {label}: {len(metrics)} glyphs")
            else:
                state = "missing" if current is None else "stale"
                print(f"  {state.upper():8s} {label}: run generate_metrics {provider.name}")
                ok = False
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        note = f", {len(empty)} blank glyphs skipped" if empty else ""
        print(f"  wrote    {path.name}: {len(metrics)} glyphs{note}")

    return ok


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("providers", nargs="*", help="Provider names to process (default: --all).")
    parser.add_argument("--all", action="store_true", help="Process every installed provider.")
    parser.add_argument("--check", action="store_true", help="Verify metrics are current; write nothing.")
    parser.add_argument("--ref", type=int, default=MEASURE_REF, help=f"Reference size in px (default: {MEASURE_REF}).")
    parser.add_argument(
        "--out-dir", type=Path, default=None,
        help="Write here instead of the provider's package directory.",
    )
    args = parser.parse_args(argv)

    registry = ProviderRegistry()
    load_external_providers(registry)
    available = sorted(registry.names())

    if not available:
        print("No icon providers installed; nothing to measure.", file=sys.stderr)
        return 1

    if args.all or not args.providers:
        selected = available
    else:
        selected = args.providers
        unknown = [n for n in selected if registry.get_provider(n) is None]
        if unknown:
            print(f"Unknown provider(s): {', '.join(unknown)}", file=sys.stderr)
            print(f"Installed: {', '.join(available)}", file=sys.stderr)
            return 2

    verb = "Checking" if args.check else "Generating"
    print(f"{verb} metrics for {len(selected)} provider(s) at ref={args.ref}px")

    ok = True
    for name in selected:
        provider = registry.get_provider(name)
        print(f"{provider.display_name} ({name}):")
        try:
            ok &= generate_for_provider(provider, out_dir=args.out_dir, ref=args.ref, check=args.check)
        except Exception as exc:
            print(f"  FAILED   {name}: {exc}", file=sys.stderr)
            ok = False

    if args.check and not ok:
        print("\nMetrics are out of date.", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
