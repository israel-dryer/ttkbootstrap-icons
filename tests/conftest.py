"""Shared fixtures.

Most tests exercise the renderer through `Icon.render_pil`, which needs no
display. The few that cover Tk-level behavior — image caching, destroy
handling — are marked `gui` and skip automatically where no display exists.
"""

from __future__ import annotations

import pytest

from tkinter_icons.icon import Icon
from tkinter_icons.iconset import clear_icon_sets
from tkinter_icons.registry import ProviderRegistry, load_external_providers
from tkinter_icons.render import clear_font_cache


def pytest_configure(config):
    config.addinivalue_line("markers", "gui: requires a Tk display")


@pytest.fixture(scope="session")
def registry() -> ProviderRegistry:
    """Every icon provider installed in this environment."""
    reg = ProviderRegistry()
    load_external_providers(reg)
    return reg


@pytest.fixture(scope="session")
def provider(registry):
    """A provider to render with, preferring Bootstrap when it is installed."""
    for name in ("bootstrap", *sorted(registry.names())):
        found = registry.get_provider(name)
        if found is not None:
            return found
    pytest.skip("no icon provider installed")


@pytest.fixture
def icon_set(provider):
    """The active icon set for `provider`'s default style."""
    return Icon.initialize_with_provider(provider)


@pytest.fixture
def sample_name(icon_set) -> str:
    """A glyph name that exists in the active set."""
    return next(iter(sorted(icon_set.glyphs)))


@pytest.fixture(autouse=True)
def _reset_state():
    """Keep cache state from leaking between tests."""
    yield
    Icon.cleanup()
    clear_icon_sets()
    clear_font_cache()


@pytest.fixture
def root():
    """A Tk root window, skipped when no display is available."""
    tkinter = pytest.importorskip("tkinter")
    try:
        window = tkinter.Tk()
    except tkinter.TclError as exc:  # pragma: no cover - headless CI
        pytest.skip(f"no display available: {exc}")
    window.withdraw()
    try:
        yield window
    finally:
        try:
            window.destroy()
        except tkinter.TclError:
            pass
