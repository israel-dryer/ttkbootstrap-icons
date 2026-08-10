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

**Tk's absence is tolerated, and every real use imports at the point of use.**
`__init__.py` imports this module, so an unguarded `import tkinter` made
`import tkinter_icons` fail outright wherever Tk is absent — and on Linux
`tkinter` is a distro package (`python3-tk`) rather than part of a pip install,
so the environments the headless guide is written for are exactly the ones that
lack it. That put Tk in front of `render_glyph` and `Icon.render_pil`, neither
of which touches it. `PIL.ImageTk` does `import tkinter` itself, so guarding
`tkinter` alone would have achieved nothing.

Everything Tk-facing still fails the same way it always did, just later:
`.image` needs a root and says so, and on a machine with no Tk the point-of-use
imports raise `ImportError` naming `tkinter` rather than the program dying on
its first line.
"""

from __future__ import annotations

import warnings
from abc import ABC
from typing import Any, ClassVar, Literal, Mapping, Optional

from PIL import Image

try:
    # Imported eagerly *when Tk is present* rather than hidden behind
    # `TYPE_CHECKING`, so that the names stay introspectable. `from __future__
    # import annotations` makes every hint a string, and anything that resolves
    # them - `typing.get_type_hints`, which is what Sphinx autodoc calls - looks
    # them up in this module's globals. A `TYPE_CHECKING`-only import leaves
    # them undefined at runtime, so that lookup raises `NameError` and the
    # resolution fails for the *whole module*: the docs then lost `MissingPolicy`
    # and the ttk aliases too, not just the Tk names.
    #
    # Narrow on purpose, and the `else` is what makes it narrow. Only the
    # absence of Tk is tolerated here; a `PIL` broken some other way still
    # raises, from this import or from the point-of-use imports below, where
    # the message names what actually failed. Sharing one `try` would set
    # `tkinter = None` for a Pillow built without a usable `ImageTk` — a
    # machine that *has* Tk — and the fallback would then be lying about which
    # dependency is missing.
    import tkinter
except ImportError:  # pragma: no cover - exercised in a subprocess, see tests
    # No Tk on this machine. Nothing on the pure-PIL path needs these; they
    # stand in for annotations so the module still imports, and every real use
    # re-imports at the point of use and raises there. `PIL.ImageTk` imports
    # `tkinter` itself, so it cannot load either and there is nothing to try.
    tkinter = None  # type: ignore[assignment]
    PhotoImage = Any  # type: ignore[misc, assignment]
else:
    from PIL.ImageTk import PhotoImage

from .iconset import (
    IconSet,
    clear_icon_sets,
    get_icon_set,
    icon_set_id,
    registered_icon_sets,
)
from .providers import NO_ICON, BaseFontProvider
from .render import RenderOptions, clear_font_cache, render_glyph, snap_size
from .stateful_icon_mixin import StatefulIconMixin

#: What to do when a name reaches an icon set that has no glyph for it.
#:
#: This is a data-integrity policy, not a typo policy. A name a pack cannot
#: resolve raises from every entry point, so what gets here is a name that was
#: handed straight to a set without being resolved — the base `Icon`, or
#: `render_pil` with an explicit `icon_set` — or a set whose glyph map really
#: is inconsistent with the names built from it.
#:
#: That distinction is what `icons-and-names` described from the start and the
#: code did not honor, which is why #117 had to delete the sentence. #115 built
#: the behavior instead, so the original scope is true again.
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

        import tkinter

        try:
            root.bind("<Destroy>", _on_destroy, add=True)
        except tkinter.TclError:  # pragma: no cover - root already going away
            pass


def _interp_id(widget: tkinter.Misc) -> int:
    """Return a stable id for the Tk interpreter behind `widget`."""
    return id(widget.tk)


def _require_root() -> tkinter.Misc:
    """Return the current default Tk root, or explain why there isn't one.

    The `import` is here rather than at module scope so that reaching the
    pure-PIL path never needs Tk installed. This function is on the widget
    path only — every caller is about to make a `PhotoImage`.
    """
    import tkinter

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

    #: What to do about a name that reaches an icon set the set cannot draw.
    #:
    #: `"raise"` is the default, and it is the default so that this path agrees
    #: with the one almost every user is on. A pack class already raises
    #: `ValueError` for a name it cannot resolve — `MaterialIcon("nope")` has
    #: never returned a blank square — but a name handed straight to a set,
    #: which is what the base `Icon` and an explicit `icon_set=` do, used to
    #: come back fully transparent. Two entry points answering one question two
    #: ways is the defect this class keeps having (#115, #140), and a silent
    #: blank is the half of it that nothing reports.
    #:
    #: `"warn"` and `"transparent"` remain for callers that must keep going
    #: across a whole set of names rather than stop at the first bad one.
    on_missing: ClassVar[MissingPolicy] = "raise"

    #: The provider a pack's icon class draws from, set by that class. It is
    #: what lets `render_pil` work as a classmethod on a pack: without it,
    #: `MaterialIcon.render_pil("home")` depends on some *other* call having
    #: initialized a provider first, and raises in a fresh process. `None` on
    #: `Icon` itself, which has no pack of its own.
    provider_class: ClassVar[Optional[type[BaseFontProvider]]] = None

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
        style: Optional[str] = None,
        *,
        icon_set: Optional[IconSet] = None,
        options: Optional[RenderOptions] = None,
    ) -> Image.Image:
        """Render a glyph to a PIL image without needing a Tk root.

        The way in for anything that wants pixels rather than a widget image —
        exporting a PNG, compositing, or testing the renderer headlessly.

        Called on a pack's icon class this needs nothing set up first — the
        pack supplies its own provider, so `MaterialIcon.render_pil("home")`
        draws a Material icon in a fresh process and takes the same friendly
        names and the same `style` the constructor does. Called on `Icon`
        itself, or with an explicit `icon_set`, `name` must already be a glyph
        name and there is no provider to resolve a style against.

        Two different failures live here, and they are answered differently.
        A name the pack cannot resolve is the caller's mistake, so it raises,
        exactly as the constructor does. A name that resolves — or is handed
        straight to a set, which is what `Icon` and an explicit `icon_set` do —
        and then turns out to have no glyph means the set's data is
        inconsistent, and that is what `on_missing` is the policy for.

        Args:
            name: Icon name. Resolved through the pack's provider when called
                on a pack class with no explicit `icon_set`; otherwise taken as
                an already-resolved glyph name.
            size: Pixel size.
            color: Foreground color.
            style: Which of the pack's styles to draw from, or `None` to work
                it out from the name — see
                `BaseFontProvider.candidate_styles`.
            icon_set: Which set to draw from. Defaults to the pack's own, then
                to the active one.
            options: Overrides of the set's render options.

        Returns:
            A square RGBA image. Fully transparent only if the name reached a
            set that cannot draw it and `on_missing` has been set to
            `"transparent"` or `"warn"` — either because the set's glyph map
            has no entry for it, or because the entry names a codepoint the
            set's font does not contain. Under the default policy that case
            raises instead.

        Raises:
            RuntimeError: If no icon set is given, the class has no provider,
                and none is initialized.
            ValueError: If the pack cannot resolve `name`, if `name`
                contradicts `style`, or if `style` is given where there is no
                provider to resolve it against.
            KeyError: If the name reaches a set that cannot draw it, under the
                default `on_missing` of `"raise"`.
        """
        resolving = icon_set is None and cls.provider_class is not None
        if style is not None and not resolving:
            raise ValueError(
                f"style={style!r} needs a provider to resolve against. Call render_pil on a "
                f"pack's icon class without an explicit icon_set, e.g. "
                f"MaterialIcon.render_pil(name, style={style!r})."
            )

        if resolving:
            provider = cls.provider_class()
            # One call, so the style the set is built from and the glyph looked
            # up in it cannot come from two different readings of the name.
            # A `ValueError` from here propagates: an unresolvable name means
            # this pack has no such icon under any style, which is the same
            # mistake the constructor raises on and not something `on_missing`
            # was written to paper over.
            resolved_style, name = provider.resolve_icon(name, style)
            icon_set = get_icon_set(provider, resolved_style)

        # `is None`, not `or`. An `IconSet` is sized, so a set that can draw
        # nothing is falsy, and `or` would quietly discard the caller's set and
        # fall back to whichever one loaded last.
        if icon_set is None:
            icon_set = cls._icon_set_current
        if icon_set is None:
            raise RuntimeError("No icon set available. Initialize a provider first.")

        glyph = None if name == NO_ICON else icon_set.glyph(name)
        if glyph is None:
            # `NO_ICON` is a blank on purpose and never a missing name, so it
            # skips the policy rather than passing through it. It used to reach
            # `_report_missing` and come back transparent only because that was
            # the default; the sentinel raised for anyone who set `"raise"`.
            if name != NO_ICON:
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
        """Apply the `on_missing` policy for a name `icon_set` cannot draw.

        Both reasons land here, but they say different things. A name the glyph
        map never had is a name; a name the map advertises at a codepoint the
        font does not contain is a fault in the data, and saying so is the
        difference between a user checking their spelling and a user filing the
        bug that is actually there.

        Which data, though, depends on where the set came from. Blaming "the
        icon pack" is right for a set `get_icon_set` built from a provider and
        wrong for one the caller assembled and passed as `icon_set=` — a case
        `render_pil`'s own docstring anticipates — where it would send someone
        to file a bug against a pack that was never involved.
        """
        if cls.on_missing == "transparent":
            return
        character = icon_set.glyphs.get(name)
        if character:
            # Every codepoint is spelled out rather than just the first. A glyph
            # map yields one character per name, but an `IconSet` built by hand
            # is free to hold more, and a diagnostic must not itself raise.
            codepoints = " ".join(f"U+{ord(char):04X}" for char in character)
            source = (
                "the icon pack's glyph map"
                if registered_icon_sets().get(icon_set.id) is icon_set
                else "this icon set's glyph map"
            )
            message = (
                f"Icon '{name}' is mapped to {codepoints} in icon set "
                f"'{icon_set.id}', but that set's font does not contain "
                f"{'that codepoint' if len(character) == 1 else 'all of those codepoints'}, "
                f"so there is nothing to draw. This is a fault in {source} "
                f"rather than in the name you asked for."
            )
        else:
            message = f"Icon '{name}' is not in icon set '{icon_set.id}'."
        if cls.on_missing == "raise":
            raise KeyError(message)
        warnings.warn(message, stacklevel=3)

    @classmethod
    def _get_transparent(cls, size: int) -> PhotoImage:
        """Return a cached transparent placeholder for the current interpreter."""
        from PIL.ImageTk import PhotoImage

        root = _require_root()
        cache = cls._cache_for(root)
        photo = cache.transparent.get(size)
        if photo is None:
            photo = PhotoImage(image=Image.new("RGBA", (size, size), (255, 255, 255, 0)))
            cache.transparent[size] = photo
        return photo

    def _render(self) -> PhotoImage:
        """Render this icon, reusing an identical image when one exists."""
        from PIL.ImageTk import PhotoImage

        root = _require_root()
        cache = Icon._cache_for(root)

        icon_set = self._icon_set
        key: _CacheKey = (icon_set.id, self.name, self.size, self.color, hash(self._options))
        cached = cache.images.get(key)
        if cached is not None:
            return cached

        if self.name == NO_ICON:
            # Deliberately blank, not missing — as in `render_pil`.
            return Icon._get_transparent(self.rendered_size)

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
