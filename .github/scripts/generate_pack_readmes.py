"""Generate the sixteen pack READMEs from the pack catalog and the live providers.

These files are the PyPI landing page for sixteen distributions, and they were the
last surface still teaching the pre-#69 idiom — `pip install tkinter-icons-lucide`
and `from tkinter_icons_lucide import LucideIcon` — because sixteen hand-written
copies of the same page go stale together and nothing checked them.

So everything factual is generated: the install command from `Pack.install_command`,
the class name from `Pack.export_names`, the styles and the upstream version and the
glyph count from the pack's own provider, and the sample glyph from `pack_showcase`'s
`SHOWCASE` table — the same table the docs build renders previews from, which fails
the build if a curated name stops resolving. One source, two outputs.

The only hand-written part is the intro paragraph under the H1, which is preserved
verbatim across regeneration. If you want to say something about a pack, say it there.

Usage::

    python .github/scripts/generate_pack_readmes.py            # write
    python .github/scripts/generate_pack_readmes.py --check    # verify, write nothing

`--check` is what CI runs: it fails if any README differs from what this script would
write, which is what stops the next drift from being silent.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "docs" / "_ext"))

DOCS = "https://tkinter-icons.readthedocs.io/en/latest"

#: Sample widget text per pack, so the quick start reads like a real button rather
#: than a glyph name. Falls back to the icon name when a pack is not listed.
SAMPLE_LABEL: dict[str, str] = {
    "bootstrap": "Home",
    "devicon": "Python",
    "eva": "Home",
    "fluent": "Home",
    "fluent-regular": "Home",
    "fontawesome": "Home",
    "google-material": "Home",
    "ionicons": "Home",
    "lucide": "Home",
    "material": "Home",
    "meteocons": "Forecast",
    "remix": "Home",
    "rpg-awesome": "Inventory",
    "simple": "Sign in with GitHub",
    "typicons": "Home",
    "weather": "Forecast",
}


def hand_written_intro(path: Path) -> str:
    """Return the prose between the H1 and the first badge, link, or `##` heading.

    Preserved across regeneration. Everything below it is generated, so this is the
    one place a pack can say something a table cannot.
    """
    if not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    out: list[str] = []
    seen_h1 = False
    for line in lines:
        if line.startswith("# "):
            seen_h1 = True
            continue
        if not seen_h1:
            continue
        if line.startswith("##") or line.startswith("[![") or line.strip() == "---":
            break
        out.append(line)
    return "\n".join(out).strip()


def render(pack, provider, showcase: list[str], glyphs: int) -> str:
    cls = pack.export_names[0]
    sample = showcase[0]
    label = SAMPLE_LABEL.get(pack.extra, sample)
    styles = provider.style_list or ()
    version = provider.icon_version or "—"

    parts: list[str] = []
    parts.append(f"# {pack.distribution}\n")

    intro = hand_written_intro(REPO / "packages" / pack.distribution / "README.md")
    if intro:
        parts.append(intro + "\n")

    parts.append(
        f"[![PyPI](https://img.shields.io/pypi/v/{pack.distribution}.svg)]"
        f"(https://pypi.org/project/{pack.distribution}/)\n"
        f"[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)\n"
    )

    parts.append(
        f"**{provider.display_name}** — {glyphs:,} icons, upstream v{version}. "
        f"One of sixteen icon packs for "
        f"[`tkinter-icons`](https://pypi.org/project/tkinter-icons/).\n"
    )

    parts.append("---\n")
    parts.append("## Install\n")
    parts.append(
        "This pack is an extra of `tkinter-icons`, so you install and import one name:\n"
    )
    parts.append(f"```bash\n{pack.install_command}\n```\n")
    parts.append(
        f"Installing `{pack.distribution}` directly also works and pulls in the base "
        f"package, but the extra is the supported form — it is what the error messages, "
        f"the documentation, and the other fifteen packs all use.\n"
    )

    parts.append("---\n")
    parts.append("## Quick start\n")
    style_arg = f', style="{provider.default_style}"' if styles else ""
    parts.append(
        "```python\n"
        "import tkinter as tk\n"
        f"from tkinter_icons import {cls}\n"
        "\n"
        "root = tk.Tk()\n"
        "\n"
        f'icon = {cls}("{sample}", size=24, color="#333"{style_arg})\n'
        f'tk.Button(root, image=icon.image, text="{label}", compound="left").pack()\n'
        "\n"
        "root.mainloop()\n"
        "```\n"
    )
    if len(pack.export_names) > 1:
        others = ", ".join(f"`{n}`" for n in pack.export_names[1:])
        parts.append(
            f"`{cls}` is also exported as {others}; both spellings resolve to the same class.\n"
        )

    parts.append("---\n")
    parts.append("## Styles\n")
    if styles:
        listed = "\n".join(
            f"- `{s}`" + (" (default)" if s == provider.default_style else "") for s in styles
        )
        parts.append(f"{provider.display_name} ships {len(styles)} styles:\n")
        parts.append(listed + "\n")
        parts.append(
            "Pass one as `style=`, or put it in the name — "
            f'`{cls}("{sample}", style="{styles[0]}")` and `{cls}("{sample}-{styles[0]}")` '
            "are the same icon.\n"
        )
    else:
        parts.append("This pack ships a single font with no style variants, so there is no `style` argument.\n")

    parts.append("---\n")
    parts.append("## Browse the icons\n")
    parts.append(
        f"Every glyph in this pack, rendered by the library itself:\n"
        f"<{DOCS}/packs/{pack.extra}.html>\n"
    )
    parts.append("Or run the browser that ships with the base package:\n")
    parts.append("```bash\ntkinter-icons\n```\n")
    parts.append("Use **Copy Name** there to copy an icon name straight into your code.\n")

    parts.append("---\n")
    parts.append("## License and attribution\n")
    # Deliberately "see", not "reproduced here". Every pack ships a `LICENSES/` file,
    # but eight of them hold a summary and a link rather than the upstream text -
    # a known gap recorded in THIRD-PARTY-NOTICES.md. Generating "reproduced in this
    # package" would have asserted something false on sixteen PyPI pages at once.
    parts.append(
        f"- **Upstream:** {provider.display_name} — <{provider.homepage}>\n"
        f"- **Upstream license:** <{provider.license_url}> — see `LICENSES/` in this package\n"
        f"- **Wrapper license:** MIT © Israel Dryer\n"
    )

    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify without writing")
    args = ap.parse_args()

    import pack_showcase as ps

    from tkinter_icons.packs import KNOWN_PACKS

    stale: list[str] = []
    for pack in KNOWN_PACKS:
        try:
            provider = ps.provider_for(pack)
        except Exception as exc:  # a pack that is not installed cannot be generated
            print(f"error: {pack.extra}: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        showcase = ps.showcase_for(pack.extra, provider.default_style)
        text = render(pack, provider, showcase, ps.glyph_count(provider))
        path = REPO / "packages" / pack.distribution / "README.md"
        current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
        if current == text:
            continue
        if args.check:
            stale.append(str(path.relative_to(REPO)))
        else:
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")

    if stale:
        print("error: these READMEs differ from what the generator produces:", file=sys.stderr)
        for s in stale:
            print(f"  {s}", file=sys.stderr)
        print("Run: python .github/scripts/generate_pack_readmes.py", file=sys.stderr)
        return 1
    print("all sixteen pack READMEs are up to date" if args.check else "done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
