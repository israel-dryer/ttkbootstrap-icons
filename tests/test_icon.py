"""Tests for `Icon` — construction, a name that cannot be drawn, and Tk lifecycle."""

from __future__ import annotations

import pytest

from tkinter_icons.icon import Icon, create_transparent_icon
from tkinter_icons.providers import NO_ICON
from tkinter_icons.render import RenderOptions


class TestConstruction:
    def test_bare_icon_points_at_a_pack_class(self, provider):
        """With packs installed, the error steers you to the right class."""
        Icon.cleanup()
        with pytest.raises(RuntimeError, match="pack's icon class"):
            Icon("anything")

    def test_with_no_packs_it_explains_the_install(self, monkeypatch):
        Icon.cleanup()
        monkeypatch.setattr("tkinter_icons.packs.installed_packs", lambda: [])
        with pytest.raises(RuntimeError, match=r'tkinter-icons\[bootstrap\]'):
            Icon("anything")

    def test_icon_holds_its_own_set(self, icon_set, sample_name):
        icon = Icon(sample_name, 24, "#123456")
        assert icon.icon_set is icon_set
        assert icon.name == sample_name
        assert icon.color == "#123456"

    def test_rendered_size_reports_the_snapped_size(self, icon_set, sample_name):
        assert Icon(sample_name, 15).rendered_size == 16
        assert Icon(sample_name, 16).rendered_size == 16

    def test_per_icon_options_override_the_set(self, icon_set, sample_name):
        options = RenderOptions(pad_factor=0.4)
        assert Icon(sample_name, 24, options=options).options is options
        assert Icon(sample_name, 24).options is icon_set.options

    def test_repr_is_informative(self, icon_set, sample_name):
        text = repr(Icon(sample_name, 24, "red"))
        assert sample_name in text and "24" in text and "red" in text


class TestRenderPil:
    """`render_pil` is the headless entry point — no Tk root involved."""

    def test_renders_without_a_root(self, icon_set, sample_name):
        img = Icon.render_pil(sample_name, 24, "#000000")
        assert img.size == (24, 24)
        assert img.getchannel("A").getbbox() is not None

    def test_unknown_name_raises(self, icon_set):
        with pytest.raises(KeyError, match="definitely-not-an-icon"):
            Icon.render_pil("definitely-not-an-icon", 24, "#000000")

    def test_explicit_icon_set_wins(self, provider, icon_set, sample_name):
        img = Icon.render_pil(sample_name, 24, "#000000", icon_set=icon_set)
        assert img.size == (24, 24)

    def test_without_any_set_it_explains_itself(self, sample_name):
        Icon.cleanup()
        with pytest.raises(RuntimeError, match="Initialize a provider"):
            Icon.render_pil(sample_name)

    def test_to_pil_matches_render_pil(self, icon_set, sample_name):
        icon = Icon(sample_name, 24, "#00ff00")
        assert icon.to_pil().tobytes() == Icon.render_pil(sample_name, 24, "#00ff00").tobytes()


class TestAGlyphThatCannotBeDrawnRaises:
    """There is no policy to soften this, and there was one until 5.1.0.

    `on_missing` was never a designed feature. 4.0.x returned
    `Icon._get_transparent(self.size)` for any name its map did not have — no
    option, no warning — and the 5.0.0 rework kept that as the default while
    adding `"warn"` and `"raise"` as opt-ins, so the option existed to escape
    the old behavior rather than to offer a choice anyone wanted.

    Nothing ever set it. Not the browser, not the placement census over 178,584
    renders, not the docs extensions that render every pack's previews — the
    bulk renderers the option was justified by. They cannot reach it: they
    iterate names that come out of the glyph map, so a name the map lacks is
    not a case they have. What the default did produce is a transparent square
    that is indistinguishable from an icon that drew, which is how #140 went
    unnoticed across two releases.
    """

    def test_the_headless_path_raises(self, icon_set):
        with pytest.raises(KeyError, match="nope"):
            Icon.render_pil("nope", 16, "#000000")

    def test_there_is_no_policy_left_to_read(self):
        """Removed, not re-defaulted — leaving it readable is the worse half.

        An attribute still present and still read would be a policy; one
        present and unread would be a lie. It is neither. Note what this
        cannot pin: Python happily lets a caller *create* `Icon.on_missing`,
        since `__slots__` governs instances and not the class, so a line left
        over from 5.0.x assigns cleanly and does nothing. Catching that means
        a metaclass, which is more machinery than the setting ever justified;
        the changelog says to delete the line instead.
        """
        assert not hasattr(Icon, "on_missing")

    def test_the_sentinel_is_still_a_blank_and_not_a_failure(self, icon_set):
        """`NO_ICON` is the one blank anyone asks for, and it is asked for."""
        image = Icon.render_pil(NO_ICON, 16, "#000000")
        assert image.getchannel("A").getbbox() is None


@pytest.mark.gui
class TestBothEntryPointsAnswerAMissingNameIdentically:
    """The regression test for the divergence this library keeps growing.

    #115 was `render_pil` raising where the constructor did not. #140 was the
    font check landing in one lookup and not the other. The third was the
    policy itself: `_render` read it off `Icon` with the class named literally
    while `render_pil` read it off `cls`, so a policy set on a pack subclass
    was honored headlessly and ignored by the widget path. Removing the policy
    removed the state they could disagree about, and both now build the error
    from one module-level function — but the property worth pinning is the
    behavior, not the refactor, since it is the behavior that regressed twice.
    """

    def test_the_widget_path_raises_what_the_headless_path_raises(self, root, icon_set):
        with pytest.raises(KeyError) as headless:
            Icon.render_pil("nope", 16, "#000000")
        with pytest.raises(KeyError) as widget:
            Icon("nope", 16, "#000000").image
        assert str(widget.value) == str(headless.value)


class TestProviderSwitching:
    def test_initialize_returns_the_active_set(self, provider):
        assert Icon.initialize_with_provider(provider).id.startswith(provider.name)

    def test_repeat_initialize_is_a_no_op(self, provider):
        assert Icon.initialize_with_provider(provider) is Icon.initialize_with_provider(provider)

    def test_existing_icons_keep_their_own_set(self, registry, provider, icon_set, sample_name):
        """Switching providers must not repoint icons already created."""
        other = next(
            (registry.get_provider(n) for n in registry.names() if n != provider.name), None
        )
        if other is None:
            pytest.skip("only one provider installed")

        icon = Icon(sample_name, 24)
        Icon.initialize_with_provider(other)
        assert icon.icon_set is icon_set
        assert icon.to_pil().size == (24, 24)


@pytest.mark.gui
class TestTkLifecycle:
    def test_image_is_rendered_lazily(self, root, icon_set, sample_name):
        icon = Icon(sample_name, 24)
        assert icon._img is None
        assert icon.image is not None
        assert icon._img is not None

    def test_identical_icons_share_one_image(self, root, icon_set, sample_name):
        assert Icon(sample_name, 24, "black").image is Icon(sample_name, 24, "black").image

    def test_different_colors_do_not_share(self, root, icon_set, sample_name):
        assert Icon(sample_name, 24, "black").image is not Icon(sample_name, 24, "red").image

    def test_clear_cache_forces_a_redraw(self, root, icon_set, sample_name):
        first = Icon(sample_name, 24, "black").image
        Icon.clear_cache()
        assert Icon(sample_name, 24, "black").image is not first

    def test_transparent_placeholders_are_cached(self, root):
        assert create_transparent_icon(16) is create_transparent_icon(16)
        assert create_transparent_icon(16) is not create_transparent_icon(24)

    def test_cache_info_counts_images(self, root, icon_set, sample_name):
        Icon.clear_cache()
        Icon(sample_name, 24, "black").image
        Icon(sample_name, 32, "black").image
        assert Icon.cache_info()["images"] == 2

    def test_destroying_the_root_drops_its_cache(self, root, icon_set, sample_name):
        """A PhotoImage belongs to its interpreter, so its cache dies with it."""
        import tkinter

        Icon.clear_cache()
        Icon(sample_name, 24, "black").image
        assert Icon.cache_info()["images"] == 1

        root.destroy()
        try:
            root.update()
        except tkinter.TclError:
            pass
        assert Icon.cache_info()["images"] == 0

    def test_images_are_not_reused_across_interpreters(self, icon_set, sample_name):
        """A handle from a destroyed interpreter must never be handed out again."""
        import tkinter

        # Tk 8.6 cannot reliably build a fresh interpreter once one has already
        # been created and destroyed in the same process — it intermittently
        # fails reloading the ttk themes. That is a Tk limitation, not something
        # this library controls, and it can strike either root here depending on
        # what ran earlier in the session.
        def _new_root():
            try:
                root = tkinter.Tk()
            except tkinter.TclError as exc:
                pytest.skip(f"Tk refused another interpreter: {exc}")
            root.withdraw()
            return root

        first = _new_root()
        Icon(sample_name, 24, "black").image
        first.destroy()

        second = _new_root()
        try:
            # Would raise "image doesn't exist" if the dead handle were reused.
            image = Icon(sample_name, 24, "black").image
            tkinter.Label(second, image=image)
        finally:
            second.destroy()

    def test_no_root_gives_a_useful_error(self, icon_set, sample_name):
        import tkinter

        if tkinter._default_root is not None:
            pytest.skip("a root is already live in this session")
        with pytest.raises(RuntimeError, match="render_pil"):
            Icon(sample_name, 24).image
