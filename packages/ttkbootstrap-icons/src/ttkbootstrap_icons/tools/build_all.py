from __future__ import annotations

import argparse
import importlib
from importlib.metadata import entry_points
from typing import Iterable, List, Tuple


def discover_provider_packages() -> List[Tuple[str, str]]:
    """Return list of (name, base_package) for installed providers.

    Uses the 'ttkbootstrap_icons.providers' entry points to infer the
    provider package base (e.g., 'ttkbootstrap_icons_fa').
    """
    items: List[Tuple[str, str]] = []
    for ep in entry_points(group="ttkbootstrap_icons.providers"):
        try:
            # ep.value looks like 'ttkbootstrap_icons_fa.provider:FontAwesomeFontProvider'
            module_path = ep.value.split(":", 1)[0]
            parts = module_path.split(".")
            if len(parts) >= 2:
                base_pkg = ".".join(parts[:2])
            else:
                base_pkg = parts[0]
            items.append((ep.name, base_pkg))
        except Exception:
            continue
    return items


def run_quick_for(base_pkg: str) -> bool:
    """Import `<base_pkg>.tools.generate_assets:default_main` and run it.

    Returns True if succeeded, False otherwise.
    """
    try:
        mod = importlib.import_module(f"{base_pkg}.tools.generate_assets")
        func = getattr(mod, "default_main", None)
        if not callable(func):
            return False
        func()
        return True
    except Exception:
        return False


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build assets for all installed ttkbootstrap-icons providers using recommended presets.")
    parser.add_argument(
        "--only",
        nargs="*",
        help="Provider names to include (match entry point names, e.g., 'fa', 'ion', 'remix').",
    )
    parser.add_argument("--dry-run", action="store_true", help="List providers without running them.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    found = discover_provider_packages()
    if args.only:
        names = set(args.only)
        found = [(name, base) for (name, base) in found if name in names]

    if not found:
        print("No external providers discovered. Ensure provider packages are installed.")
        return 1

    print("Discovered providers:")
    for name, base in found:
        print(f" - {name} ({base})")

    if args.dry_run:
        return 0

    ok = True
    for name, base in found:
        print(f"\n[{name}] Building using default preset...")
        success = run_quick_for(base)
        if success:
            print(f"[{name}] Done")
        else:
            print(f"[{name}] Failed (no quick builder or error)")
            ok = False
    return 0 if ok else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

