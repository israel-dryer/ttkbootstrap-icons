import json
import re
import sys
from pathlib import Path

import mkdocs_gen_files
try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
    tomllib = None

# Root directories
PKG_ROOT = Path("packages")
DEST_ROOT = Path("providers")

# Map package folder names to provider doc filenames in docs/providers/
PACKAGE_TO_DOC = {
    "tkinter-icons-bs": "bootstrap.md",
    "tkinter-icons-devicon": "devicon.md",
    "tkinter-icons-eva": "eva.md",
    "tkinter-icons-fa": "font-awesome-6-free.md",
    "tkinter-icons-fluent": "fluent-system-icons.md",
    "tkinter-icons-fluent-reg": "fluent-system-icons-regular.md",
    "tkinter-icons-gmi": "google-material-icons.md",
    "tkinter-icons-ion": "ion.md",
    "tkinter-icons-lucide": "lucide.md",
    "tkinter-icons-mat": "material-design-icons.md",
    "tkinter-icons-meteocons": "meteocons.md",
    "tkinter-icons-remix": "remix.md",
    "tkinter-icons-rpga": "rgpa.md",
    "tkinter-icons-simple": "simple.md",
    "tkinter-icons-typicons": "typicons.md",
    "tkinter-icons-weather": "weather.md",
}


def main() -> None:
    for pkg_name, dest_name in PACKAGE_TO_DOC.items():
        src = PKG_ROOT / pkg_name / "README.md"
        dest = DEST_ROOT / dest_name
        dest_base = dest.stem

        if not src.is_file():
            # README missing — create a small stub so nav links resolve.
            title = dest.stem.replace("-", " ").title()
            stub = (
                f"# {title}\n\n"
                f"This page is generated from `{src.as_posix()}`.\n\n"
                "The README was not found at build time. Once it exists, this page will include its contents."
            )
            with mkdocs_gen_files.open(dest.as_posix(), "w") as fd:
                fd.write(stub)
            mkdocs_gen_files.set_edit_path(dest.as_posix(), src.as_posix())
            print(f"[gen-files] Created stub providers/{dest_name} (missing {src})")
            continue

        # Do not write README into virtual docs anymore; committed files exist under docs/providers.
        # Still compute asset path for image copying below.
        asset_rel_dir = f"assets/{dest_base}"
        print(f"[gen-files] Providers page committed on disk: providers/{dest_name}")

        # Copy screenshot asset if present
        for img_src in [
            PKG_ROOT / pkg_name / "browser.png",
            PKG_ROOT / pkg_name / "docs" / "browser.png",
        ]:
            if img_src.is_file():
                img_dest = DEST_ROOT / asset_rel_dir / "browser.png"
                with mkdocs_gen_files.open(img_dest.as_posix(), "wb") as fd:
                    fd.write(img_src.read_bytes())
                print(f"[gen-files]   + copied image to providers/{asset_rel_dir}/browser.png")
                break


    # Generate Providers overview table into the Overview page (index.md)
    try:
        _generate_providers_table()
    except Exception as exc:
        print(f"[gen-files] Skipped providers table generation: {exc}")

    try:
        _generate_api_pages()
    except Exception as exc:
        print(f"[gen-files] Skipped API pages generation: {exc}")


def _count_glyphs_in_package(pkg_dir: Path) -> int:
    """Count unique glyphs across all glyphmap*.json files in a provider package src folder."""
    json_dir = None
    # find the top-level package directory under src/
    src_dir = pkg_dir / "src"
    if not src_dir.is_dir():
        return 0
    candidates = [p for p in src_dir.iterdir() if p.is_dir() and p.name.startswith("tkinter_icons_")]
    if not candidates:
        return 0
    json_dir = candidates[0]
    names: set[str] = set()
    for j in json_dir.glob("glyphmap*.json"):
        try:
            data = json.loads(j.read_text(encoding="utf-8"))
            for k in data.keys():
                names.add(str(k))
        except Exception:
            continue
    return len(names)


def _get_icon_version_from_provider(pkg_dir: Path) -> str | None:
    """Attempt to read icon version by importing the provider class per pyproject entry point.

    Falls back to None if unavailable.
    """
    if not tomllib:
        return None
    pyproj = pkg_dir / "pyproject.toml"
    try:
        data = tomllib.loads(pyproj.read_text(encoding="utf-8"))
        eps = data.get("project", {}).get("entry-points", {}).get("tkinter_icons.providers", {})
        if not eps:
            return None
        # Add src to sys.path for import
        sys.path.insert(0, str((pkg_dir / "src").resolve()))
        for _name, target in eps.items():
            try:
                mod_path, cls_name = target.split(":", 1)
                module = __import__(mod_path, fromlist=[cls_name])
                ProviderCls = getattr(module, cls_name)
                prov = ProviderCls()
                return getattr(prov, "icon_version", None)
            except Exception:
                continue
    except Exception:
        return None
    return None


def _generate_providers_table() -> None:
    """Append/replace a Providers table in Overview (index.md)."""
    index_src = Path("docs/index.md")
    try:
        original = index_src.read_text(encoding="utf-8")
    except Exception:
        original = ""

    # Build rows: (name, link, package, version, count, downloads_badge)
    # Display names map matching nav
    name_map = {
        "tkinter-icons-bs": "Bootstrap Icons",
        "tkinter-icons-devicon": "Devicon",
        "tkinter-icons-eva": "Eva",
        "tkinter-icons-fa": "Font Awesome 6 (free)",
        "tkinter-icons-fluent": "Fluent System Icons",
        "tkinter-icons-fluent-reg": "Fluent System Icons (Regular)",
        "tkinter-icons-gmi": "Google Material Icons",
        "tkinter-icons-ion": "Ion Icons",
        "tkinter-icons-lucide": "Lucide",
        "tkinter-icons-mat": "Material Design Icons",
        "tkinter-icons-meteocons": "Meteocons",
        "tkinter-icons-remix": "Remix Icons",
        "tkinter-icons-rpga": "RPG Awesome",
        "tkinter-icons-simple": "Simple Icons",
        "tkinter-icons-typicons": "Typicons",
        "tkinter-icons-weather": "Weather Icons",
    }

    rows = []

    for pkg_name, doc_name in PACKAGE_TO_DOC.items():
        disp = name_map.get(pkg_name, pkg_name)
        pkg_dir = Path("packages") / pkg_name
        icon_count = _count_glyphs_in_package(pkg_dir)
        version = _get_icon_version_from_provider(pkg_dir) or "-"
        pepy_name = pkg_name
        row = (
            f"| [{disp}](providers/{doc_name}) | `{pkg_name}` | {version} | {icon_count:,} | "
            f"[![](https://static.pepy.tech/badge/{pepy_name})](https://pepy.tech/project/{pepy_name}) |"
        )
        rows.append(row)

    # Clean table: no extra headings or blank lines; caller preserves '## Providers' heading
    table = (
        "| Name | Package | Version | Icons | Downloads |\n"
        "|:--|:--|:--|--:|:--|\n"
        + "\n".join(rows)
        + "\n"
    )

    # Replace or append under a Providers heading placeholder.
    # If index has a '## Providers' heading, replace content from it to next '##'.
    new_content = original
    marker = "## Providers"
    if marker in original:
        start = original.find(marker)
        end = original.find("\n## ", start + len(marker))
        if end == -1:
            end = len(original)
        # Keep the existing heading but replace following content with our table
        head = original[:start]
        heading_line_end = original.find("\n", start)
        if heading_line_end == -1:
            heading_line_end = start + len(marker)
        heading = original[start:heading_line_end]
        tail = original[end:]
        new_content = head + heading + "\n\n" + table + "\n" + tail.lstrip("\n")
    else:
        # Append at the end
        new_content = original.rstrip() + "\n\n" + table

    with mkdocs_gen_files.open("index.md", "w") as fd:
        fd.write(new_content)
    mkdocs_gen_files.set_edit_path("index.md", index_src.as_posix())


def _generate_api_pages() -> None:
    """Generate mkdocstrings API pages for providers (core handled by docs/api/core.md)."""
    api_path = Path("api")

    # Providers
    for pkg_name, _doc in PACKAGE_TO_DOC.items():
        slug = pkg_name.replace("tkinter-icons-", "")
        module = f"tkinter_icons_{slug.replace('-', '_')}"
        display = slug.title() if slug != "fa" else "Font Awesome"
        # Provide nicer names when possible
        name_map = {
            "bs": "Bootstrap Icons",
            "fa": "Font Awesome",
            "gmi": "Google Material Icons",
            "ion": "Ion Icons",
            "remix": "Remix Icon",
            "fluent": "Fluent System Icons",
            "fluent-reg": "Fluent System Icons (Regular)",
            "simple": "Simple Icons",
            "weather": "Weather Icons",
            "lucide": "Lucide",
            "mat": "Material Design Icons",
            "eva": "Eva",
            "rpga": "RPG Awesome",
            "devicon": "Devicon",
            "typicons": "Typicons",
            "meteocons": "Meteocons",
        }
        display = name_map.get(slug, display)
        content = (
            f"# {display} API\n\n"
            f"::: {module}.icon\n"
            "    options:\n"
            "      show_root_heading: true\n"
            "      members: true\n"
            "      inherited_members: true\n"
            "      show_source: false\n\n"
            f"::: {module}.provider\n"
            "    options:\n"
            "      show_root_heading: true\n"
            "      members: true\n"
            "      inherited_members: true\n"
            "      show_source: false\n"
        )
        with mkdocs_gen_files.open((api_path / f"{slug}.md").as_posix(), "w") as fd:
            fd.write(content)


# Run at import time; mkdocs-gen-files executes this script
# in a non-__main__ context, so do not guard with __name__ check.
main()
