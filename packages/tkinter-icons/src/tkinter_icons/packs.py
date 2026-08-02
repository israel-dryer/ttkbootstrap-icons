"""The catalogue of icon packs, and the guidance shown when one is missing.

`tkinter-icons` is one library, but its icon packs are separate
distributions — each carries its own font, and bundling sixteen of them would
cost every user tens of megabytes for glyphs they will never draw. Extras hide
that split, so a pack is installed as part of the library rather than as a
package the user has to know the name of::

    pip install "tkinter-icons[material]"

Nothing ships with the base install: it is the renderer, and it has no glyphs
of its own until a pack is added. This module is the single source of truth for
which packs exist and how to install them, so every error message, the browser,
and the docs all describe them the same way.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Iterator, Optional

REPO_URL = "https://github.com/israel-dryer/tkinter-icons"

#: Read the Docs, matching `ttkbootstrap`. `/en/latest/` rather than
#: `/en/stable/` for the same reason ttkbootstrap uses it: `latest` resolves
#: from the first build onward, where `stable` 404s until a release tag has been
#: built and activated — and this URL is printed by `no_packs_message()`, which
#: is the one link a user who cannot yet draw an icon is given.
DOCS_URL = "https://tkinter-icons.readthedocs.io/en/latest"

#: Where someone with no pack installed is sent to pick one. The sixteen sets
#: serve disjoint purposes, so the useful answer is a comparison rather than a
#: list of install commands - which is why this points at the docs and not here.
PACKS_DOC_URL = f"{DOCS_URL}/packs.html"


@dataclass(frozen=True)
class Pack:
    """One installable icon pack.

    Attributes:
        extra: The extra to install it with, as in `tkinter-icons[extra]`.
        distribution: The underlying PyPI distribution name.
        module: The importable module it provides.
        icon_class: The icon class as named in `module`.
        provider: The provider name it registers under, used by the registry
            and the `generate_metrics` tool.
        label: Human-readable name of the upstream icon set.
        alias: The name this class is exported as from `tkinter_icons`.
            The packs grew inconsistent short names (`MatIcon`, `FAIcon`,
            `GMatIcon`), so the base package offers a spelled-out one that
            matches the extra. Equal to `icon_class` where that was already
            the natural name.
    """

    extra: str
    distribution: str
    module: str
    icon_class: str
    provider: str
    label: str
    alias: str = ""

    def __post_init__(self):
        if not self.alias:
            object.__setattr__(self, "alias", self.icon_class)

    @property
    def export_names(self) -> tuple[str, ...]:
        """Every name this pack's icon class is reachable by from the base.

        Both spellings are exported so existing code that imported the short
        name keeps working after switching to the single import root.
        """
        if self.alias == self.icon_class:
            return (self.icon_class,)
        return (self.alias, self.icon_class)

    @property
    def install_command(self) -> str:
        """The pip command that installs this pack.

        Quoted because most shells treat unquoted brackets as globs — zsh
        fails outright on `pip install tkinter-icons[material]`.
        """
        return f'pip install "tkinter-icons[{self.extra}]"'

    @property
    def import_statement(self) -> str:
        """The recommended import line for this pack's icon class.

        Uses the single import root so the name installed is the name
        imported. `from {self.module} import {self.icon_class}` also works.
        """
        return f"from tkinter_icons import {self.alias}"

    @property
    def is_installed(self) -> bool:
        """Whether this pack's module can be imported."""
        try:
            return importlib.util.find_spec(self.module) is not None
        except (ImportError, ValueError):
            return False


KNOWN_PACKS: tuple[Pack, ...] = (
    Pack("bootstrap", "tkinter-icons-bs", "tkinter_icons_bs",
         "BootstrapIcon", "bootstrap", "Bootstrap Icons"),
    Pack("devicon", "tkinter-icons-devicon", "tkinter_icons_devicon",
         "DevIcon", "devicon", "Devicon", alias="DeviconIcon"),
    Pack("eva", "tkinter-icons-eva", "tkinter_icons_eva",
         "EvaIcon", "eva", "Eva Icons"),
    Pack("fluent", "tkinter-icons-fluent", "tkinter_icons_fluent",
         "FluentIcon", "fluent", "Fluent System Icons"),
    Pack("fluent-regular", "tkinter-icons-fluent-reg", "tkinter_icons_fluent_reg",
         "FluentRegularIcon", "fluent-regular", "Fluent System Icons (Regular)"),
    Pack("fontawesome", "tkinter-icons-fa", "tkinter_icons_fa",
         "FAIcon", "fontawesome", "Font Awesome 6 (Free)", alias="FontAwesomeIcon"),
    Pack("google-material", "tkinter-icons-gmi", "tkinter_icons_gmi",
         "GMatIcon", "gmi", "Google Material Icons", alias="GoogleMaterialIcon"),
    Pack("ionicons", "tkinter-icons-ion", "tkinter_icons_ion",
         "IonIcon", "ion", "Ion Icons"),
    Pack("lucide", "tkinter-icons-lucide", "tkinter_icons_lucide",
         "LucideIcon", "lucide", "Lucide Icons"),
    Pack("material", "tkinter-icons-mat", "tkinter_icons_mat",
         "MatIcon", "mat", "Material Design Icons", alias="MaterialIcon"),
    Pack("meteocons", "tkinter-icons-meteocons", "tkinter_icons_meteocons",
         "MeteoIcon", "meteocons", "Meteocons", alias="MeteoconsIcon"),
    Pack("remix", "tkinter-icons-remix", "tkinter_icons_remix",
         "RemixIcon", "remix", "Remix Icon"),
    Pack("rpg-awesome", "tkinter-icons-rpga", "tkinter_icons_rpga",
         "RPGAIcon", "rpga", "RPG Awesome", alias="RpgAwesomeIcon"),
    Pack("simple", "tkinter-icons-simple", "tkinter_icons_simple",
         "SimpleIcon", "simple", "Simple Icons"),
    Pack("typicons", "tkinter-icons-typicons", "tkinter_icons_typicons",
         "TypiconsIcon", "typicons", "Typicons"),
    Pack("weather", "tkinter-icons-weather", "tkinter_icons_weather",
         "WeatherIcon", "weather", "Weather Icons"),
)

#: Export name to the pack that provides it, covering both the friendly alias
#: and the pack's own class name.
PACK_BY_EXPORT: dict[str, Pack] = {
    name: pack for pack in KNOWN_PACKS for name in pack.export_names
}


def find_pack(key: str) -> Optional[Pack]:
    """Look up a pack by any of the names it goes by.

    Accepts the extra, the distribution, the module, or the provider name, so
    a user who knows the pack by any of those gets the same answer.

    Args:
        key: Extra, distribution, module, or provider name.

    Returns:
        The matching `Pack`, or `None`.
    """
    needle = key.strip().lower().replace("_", "-")
    for pack in KNOWN_PACKS:
        candidates = {
            pack.extra,
            pack.distribution,
            pack.module.replace("_", "-"),
            pack.provider,
        }
        if needle in candidates:
            return pack
    return None


def installed_packs() -> list[Pack]:
    """Return every known pack that is importable in this environment."""
    return [pack for pack in KNOWN_PACKS if pack.is_installed]


def iter_pack_lines(packs: Optional[tuple[Pack, ...]] = None, limit: Optional[int] = None) -> Iterator[str]:
    """Yield `extra — label` lines for display in help text."""
    chosen = packs if packs is not None else KNOWN_PACKS
    for pack in chosen[:limit]:
        yield f"  {pack.extra:<16} {pack.label}"


def no_packs_message() -> str:
    """Guidance for an environment with no icon pack installed at all."""
    suggestions = (find_pack("bootstrap"), find_pack("fontawesome"), find_pack("material"))
    lines = [
        "No icon packs are installed, so no icons can be drawn.",
        "",
        "tkinter-icons is the renderer; the glyphs come from packs you add as extras:",
    ]
    commands = [(pack.install_command, pack.label) for pack in suggestions if pack]
    # `default` matters: this runs from Icon.__init__'s error path, so an empty
    # list - which is what renaming one of those three extras would produce -
    # must not replace the guidance with a ValueError from max().
    width = max((len(command) for command, _ in commands), default=0)
    lines += [f"  {command:<{width}}  # {label}" for command, label in commands]
    lines += ["", f"Choosing among all {len(KNOWN_PACKS)} packs: {PACKS_DOC_URL}"]
    return "\n".join(lines)


def missing_pack_message(key: str) -> str:
    """Guidance for a specific pack that was asked for but is not installed.

    Args:
        key: Whatever name the caller used for the pack.

    Returns:
        A message naming the extra to install, or listing the valid packs when
        `key` matches nothing known.
    """
    pack = find_pack(key)
    if pack is None:
        known = "\n".join(iter_pack_lines())
        return f"Unknown icon pack '{key}'.\n\nAvailable packs:\n{known}"

    installed = installed_packs()
    message = [
        f"The {pack.label} pack is not installed.",
        "",
        f"  {pack.install_command}",
        "",
        f"Then: {pack.import_statement}",
    ]
    if installed:
        names = ", ".join(p.extra for p in installed)
        message += ["", f"Currently installed: {names}"]
    return "\n".join(message)


__all__ = [
    "DOCS_URL",
    "KNOWN_PACKS",
    "PACKS_DOC_URL",
    "REPO_URL",
    "Pack",
    "find_pack",
    "installed_packs",
    "iter_pack_lines",
    "missing_pack_message",
    "no_packs_message",
]
