"""Tk-facing icon objects, layered over the pure-PIL renderer.

`Icon` binds a glyph to a Tk `PhotoImage`. The drawing itself lives in
`tkinter_icons.render` and the per-provider data in
`tkinter_icons.iconset`, so anything that does not need a widget — tests,
asset pipelines, exporting an icon to a PNG — can skip this module entirely and
call `render_glyph` or `Icon.render_pil`.

Image caching is scoped to the Tk interpreter that created the images. A
`PhotoImage` belongs to the interpreter it was made in, so caching them
globally hands out dead handles once a root is destroyed and another is created
— which is what happens in test suites and in apps that use more than one root.
Each interpreter gets its own cache, dropped when its root is destroyed.
"""

from __future__ import annotations

import tkinter
import warnings
from abc import ABC
from typing import Any, ClassVar, Literal, Mapping, Optional

from PIL import Image
from PIL.ImageTk import PhotoImage

from .iconset import IconSet, clear_icon_sets, get_icon_set, icon_set_id
from .providers import BaseFontProvider
from .render import RenderOptions, clear_font_cache, render_glyph, snap_size
from .stateful_icon_mixin import StatefulIconMixin

#: What to do when an icon name is not in its set. Providers normally raise
#: during name resolution, so this only catches glyphs that resolve but are
#: absent from the loaded glyphmap.
MissingPolicy = Literal["transparent", "warn", "raise"]

_CacheKey = tuple[str, str, int, str, int]


class _InterpreterCache:
    """Rendered images belonging to one Tk interpreter.

    Holds the icon images and transparent placeholders created in a single
    interpreter, and is discarded wholesale when that interpreter's root window
    is destroyed.
    """

    __slots__ = ("images", "transparent", "_bound")

    def __init__(self) -> None:
        self.images: dict[_CacheKey, PhotoImage] = {}
        self.transparent: dict[int, PhotoImage] = {}
        self._bound = False

    def clear(self) -> None:
        self.images.clear()
        self.transparent.clear()

    def bind_root(self, root: tkinter.Misc) -> None:
        """Drop this cache when `root` is destroyed, once per interpreter."""
        if self._bound:
            return
        self._bound = True

        def _on_destroy(event, _root=root):
            # <Destroy> reaches a toplevel's bindings for its children too;
            # only the root's own destruction retires the interpreter.
            if event.widget is _root:
                Icon._retire_interpreter(_interp_id(_root))

        try:
            root.bind("<Destroy>", _on_destroy, add=True)
        except tkinter.TclError:  # pragma: no cover - root already going away
            pass


def _interp_id(widget: tkinter.Misc) -> int:
    """Return a stable id for the Tk interpreter behind `widget`."""
    return id(widget.tk)


def _require_root() -> tkinter.Misc:
    """Return the current default Tk root, or explain why there isn't one."""
    root = tkinter._default_root  # type: ignore[attr-defined]
    if root is None:
        raise RuntimeError(
            "No Tk root window exists yet. Create a tkinter.Tk() (or ttkbootstrap.Window) "
            "before building icon images.\n"
            "To render without a display, use Icon.render_pil(...) which returns a PIL image."
        )
    return root


def create_transparent_icon(size: int = 16) -> PhotoImage:
    """Return a cached fully transparent square image of `size` pixels."""
    return Icon._get_transparent(size)


class Icon(StatefulIconMixin, ABC):
    """A font glyph rendered to a Tk-compatible image.

    Provider packages subclass this and resolve friendly names to glyph names
    before delegating here, so you normally construct `BootstrapIcon`,
    `FontAwesomeIcon`, and so on rather than `Icon` itself.

    Rendering is lazy: the image is drawn on first access to `image`, so icons
    can be built before a Tk root exists. Identical icons share one image.

    Attributes:
        name: The resolved glyph name within the icon set.
        size: Requested pixel size. The rendered image may be one pixel larger
            when odd sizes are snapped even — see `RenderOptions.snap_even`.
        color: Foreground color.
        on_missing: Class-level policy for names absent from the icon set.
    """

    __slots__ = ("name", "size", "color", "_img", "_icon_set", "_options")

    on_missing: ClassVar[MissingPolicy] = "transparent"

    _icon_set_current: ClassVar[Optional[IconSet]] = None
    _caches: ClassVar[dict[int, _InterpreterCache]] = {}

    def __init__(
        self,
        name: str,
        size: int = 24,
        color: str = "black",
        *,
        options: Optional[RenderOptions] = None,
    ):
        """Create an icon.

        Args:
            name: Resolved glyph name in the active icon set.
            size: Pixel size.
            color: Foreground color, in any form Pillow accepts.
            options: Per-icon overrides of the provider's render options.

        Raises:
            RuntimeError: If no provider has been initialized.
        """
        icon_set = Icon._icon_set_current
        if icon_set is None:
            from .packs import installed_packs, no_packs_message

            if installed_packs():
                raise RuntimeError(
                    "No icon pack is active. Use a pack's icon class rather than Icon directly, "
                    "e.g. `from tkinter_icons import MaterialIcon`."
                )
            raise RuntimeError(no_packs_message())

        self.name = name
        self.size = size
        self.color = color
        self._icon_set = icon_set
        self._options = options or icon_set.options
        self._img: Optional[PhotoImage] = None
        super().__init__()

    # -----------------------------
    # Public surface
    # -----------------------------

    @property
    def image(self) -> PhotoImage:
        """The Tk-compatible image, rendered on first access."""
        if self._img is None:
            self._img = self._render()
        return self._img

    @property
    def icon_set(self) -> IconSet:
        """The icon set this icon draws from."""
        return self._icon_set

    @property
    def options(self) -> RenderOptions:
        """The render options in effect for this icon."""
        return self._options

    @property
    def rendered_size(self) -> int:
        """The image's actual pixel size, after even-snapping."""
        return snap_size(self.size, snap_even=self._options.snap_even)

    def to_pil(self) -> Image.Image:
        """Render this icon to a PIL image, bypassing Tk entirely."""
        return self.render_pil(
            self.name, self.size, self.color,
            icon_set=self._icon_set, options=self._options,
        )

    @classmethod
    def render_pil(
        cls,
        name: str,
        size: int = 24,
        color: str = "black",
        *,
        icon_set: Optional[IconSet] = None,
        options: Optional[RenderOptions] = None,
    ) -> Image.Image:
        """Render a glyph to a PIL image without needing a Tk root.

        The way in for anything that wants pixels rather than a widget image —
        exporting a PNG, compositing, or testing the renderer headlessly.

        Args:
            name: Resolved glyph name.
            size: Pixel size.
            color: Foreground color.
            icon_set: Which set to draw from. Defaults to the active one.
            options: Overrides of the set's render options.

        Returns:
            A square RGBA image; fully transparent if `name` is not in the set.

        Raises:
            RuntimeError: If no icon set is given and none is initialized.
        """
        icon_set = icon_set or cls._icon_set_current
        if icon_set is None:
            raise RuntimeError("No icon set available. Initialize a provider first.")

        glyph = icon_set.glyph(name)
        if glyph is None:
            cls._report_missing(name, icon_set)
            snapped = snap_size(size, snap_even=(options or icon_set.options).snap_even)
            return Image.new("RGBA", (snapped, snapped), (0, 0, 0, 0))

        return render_glyph(
            glyph, size, color,
            font_key=icon_set.font_key,
            font_bytes=icon_set.font_bytes,
            ink=icon_set.ink(name),
            options=options or icon_set.options,
        )

    @classmethod
    def initialize_with_provider(cls, provider: BaseFontProvider, style: str | None = None) -> IconSet:
        """Make a provider's style the active icon set.

        Icon sets are cached, so switching back and forth between providers
        costs nothing after the first load and does not disturb icons already
        created — each icon holds its own set.

        Args:
            provider: The provider to load.
            style: Style name, or `None` for the provider's default.

        Returns:
            The now-active `IconSet`.
        """
        set_id = icon_set_id(provider, style)
        current = Icon._icon_set_current
        if current is not None and current.id == set_id:
            return current

        icon_set = get_icon_set(provider, style)
        Icon._icon_set_current = icon_set
        return icon_set

    @classmethod
    def clear_cache(cls) -> None:
        """Drop every rendered image, keeping loaded fonts and icon sets.

        Call after changing something that affects how icons look — a theme
        change, for instance — to force a redraw on next use.
        """
        for cache in cls._caches.values():
            cache.clear()

    @classmethod
    def cache_info(cls) -> Mapping[str, int]:
        """Return current cache sizes, for debugging and tests."""
        from .iconset import registered_icon_sets

        return {
            "interpreters": len(cls._caches),
            "images": sum(len(c.images) for c in cls._caches.values()),
            "transparent": sum(len(c.transparent) for c in cls._caches.values()),
            "icon_sets": len(registered_icon_sets()),
        }

    @classmethod
    def cleanup(cls) -> None:
        """Release every cached image, font, and icon set.

        Not required for correctness — nothing is written to disk and caches
        are dropped with their interpreter — but useful to reclaim memory in a
        long-running process that has finished with icons.
        """
        for cache in cls._caches.values():
            cache.clear()
        cls._caches.clear()
        cls._icon_set_current = None
        clear_icon_sets()
        clear_font_cache()

    # -----------------------------
    # Internals
    # -----------------------------

    @classmethod
    def _cache_for(cls, root: tkinter.Misc) -> _InterpreterCache:
        """Return the image cache for `root`'s interpreter, creating it if new."""
        key = _interp_id(root)
        cache = cls._caches.get(key)
        if cache is None:
            cache = _InterpreterCache()
            cls._caches[key] = cache
            cache.bind_root(root.winfo_toplevel() if root.master else root)
        return cache

    @classmethod
    def _retire_interpreter(cls, interp_id: int) -> None:
        """Discard the cache for an interpreter whose root has been destroyed."""
        cache = cls._caches.pop(interp_id, None)
        if cache is not None:
            cache.clear()

    @classmethod
    def _report_missing(cls, name: str, icon_set: IconSet) -> None:
        """Apply the `on_missing` policy for a name absent from `icon_set`."""
        if cls.on_missing == "transparent":
            return
        message = f"Icon '{name}' is not in icon set '{icon_set.id}'."
        if cls.on_missing == "raise":
            raise KeyError(message)
        warnings.warn(message, stacklevel=3)

    @classmethod
    def _get_transparent(cls, size: int) -> PhotoImage:
        """Return a cached transparent placeholder for the current interpreter."""
        root = _require_root()
        cache = cls._cache_for(root)
        photo = cache.transparent.get(size)
        if photo is None:
            photo = PhotoImage(image=Image.new("RGBA", (size, size), (255, 255, 255, 0)))
            cache.transparent[size] = photo
        return photo

    def _render(self) -> PhotoImage:
        """Render this icon, reusing an identical image when one exists."""
        root = _require_root()
        cache = Icon._cache_for(root)

        icon_set = self._icon_set
        key: _CacheKey = (icon_set.id, self.name, self.size, self.color, hash(self._options))
        cached = cache.images.get(key)
        if cached is not None:
            return cached

        if icon_set.glyph(self.name) is None:
            Icon._report_missing(self.name, icon_set)
            return Icon._get_transparent(self.rendered_size)

        photo = PhotoImage(image=self.to_pil())
        cache.images[key] = photo
        return photo

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r} size={self.size} color={self.color!r}>"

    def __str__(self) -> str:
        return str(self.image)


__all__ = ["Icon", "MissingPolicy", "create_transparent_icon"]
