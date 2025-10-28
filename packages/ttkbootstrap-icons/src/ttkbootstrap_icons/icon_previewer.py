"""
Icon Previewer for ttkbootstrap-icons

A GUI application to browse and preview Bootstrap and Lucide icons with
virtual scrolling for performance.
"""

import atexit
import importlib
import json
import math
import os
import sys
import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon
from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons.providers import (
    BuiltinBootstrapProvider,
)
from ttkbootstrap_icons.registry import ProviderRegistry, load_external_providers


class VirtualIconGrid:
    """Virtual scrolling grid for displaying icons efficiently."""

    def __init__(self, parent, icon_class, icon_names, icon_size=32, icon_color="black", icon_style=None):
        self.parent = parent
        self.icon_class = icon_class
        self.all_icon_names = icon_names
        self.filtered_icons = icon_names.copy()
        self.icon_size = icon_size
        self.icon_color = icon_color
        self.icon_style = icon_style

        # Grid configuration
        self.gap = 18  # Gap between icons
        self.item_width = 120  # Width of each icon cell
        self.item_height = 100  # Height of each icon cell
        self.canvas_width = 830  # Fixed canvas width
        self.canvas_height = 480  # Fixed canvas height

        # Calculate columns
        self.columns = max(1, (self.canvas_width + self.gap) // (self.item_width + self.gap))

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            parent,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            highlightthickness=0,
        )
        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self._on_scrollbar)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=False)
        self.scrollbar.pack(side="right", fill="y")

        # Virtual scrolling state
        self.visible_items = {}  # {index: (canvas_items, icon_obj)}
        self.first_visible_row = 0
        self.last_visible_row = 0

        # Bind events
        self.canvas.bind("<Configure>", self._on_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down

        # Initial render
        self._update_scroll_region()
        self._render_visible_items()

    def _on_scrollbar(self, *args):
        """Handle scrollbar movement."""
        self.canvas.yview(*args)
        self._render_visible_items()

    def _on_configure(self, event):
        """Handle canvas resize."""
        self._render_visible_items()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows/Mac
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._render_visible_items()
        return "break"

    def _update_scroll_region(self):
        """Update the canvas scroll region based on filtered icons."""
        total_icons = len(self.filtered_icons)
        total_rows = math.ceil(total_icons / self.columns)
        total_height = total_rows * (self.item_height + self.gap) + self.gap

        self.canvas.configure(scrollregion=(0, 0, self.canvas_width, total_height))

    def _render_visible_items(self):
        """Render only the visible icons (virtual scrolling)."""
        # Get visible area
        y_top = self.canvas.canvasy(0)
        y_bottom = self.canvas.canvasy(self.canvas_height)

        # Calculate visible rows
        first_row = max(0, int(y_top / (self.item_height + self.gap)) - 1)
        last_row = min(
            math.ceil(len(self.filtered_icons) / self.columns),
            int(y_bottom / (self.item_height + self.gap)) + 2,
        )

        # Calculate visible item indices
        first_idx = first_row * self.columns
        last_idx = min(len(self.filtered_icons), last_row * self.columns)

        # Remove items that are no longer visible
        to_remove = []
        for idx in self.visible_items:
            if idx < first_idx or idx >= last_idx:
                canvas_items, icon_obj = self.visible_items[idx]
                for item in canvas_items:
                    self.canvas.delete(item)
                to_remove.append(idx)

        for idx in to_remove:
            del self.visible_items[idx]

        # Add newly visible items
        for idx in range(first_idx, last_idx):
            if idx >= len(self.filtered_icons):
                break

            if idx in self.visible_items:
                continue

            icon_name = self.filtered_icons[idx]
            row = idx // self.columns
            col = idx % self.columns

            # Calculate position
            x = self.gap + col * (self.item_width + self.gap) + self.item_width // 2
            y = self.gap + row * (self.item_height + self.gap) + self.gap

            # Create icon
            try:
                # Pass style if supported by the icon class
                try:
                    icon_obj = self.icon_class(
                        icon_name, size=self.icon_size, color=self.icon_color, style=self.icon_style
                    )
                except TypeError:
                    icon_obj = self.icon_class(
                        icon_name, size=self.icon_size, color=self.icon_color
                    )

                # Create canvas items
                img_item = self.canvas.create_image(x, y, image=icon_obj.image)
                text_item = self.canvas.create_text(
                    x,
                    y + self.icon_size // 2 + 20,
                    text=icon_name,
                    width=self.item_width - 10,
                    font=("Arial", 8),
                    fill="#333",
                )

                # Make clickable - copy icon name to clipboard
                def make_click_handler(name, txt_item):
                    def handler(event):
                        self.canvas.master.master.clipboard_clear()
                        self.canvas.master.master.clipboard_append(name)
                        # Visual feedback - capture txt_item as default arg to avoid closure issue
                        self.canvas.itemconfig(txt_item, fill="#0d6efd", font=("Arial", 8, "bold"))
                        self.canvas.after(
                            200, lambda item=txt_item: self.canvas.itemconfig(
                                item, fill="#333", font=("Arial", 8)))

                    return handler

                self.canvas.tag_bind(img_item, "<Button-1>", make_click_handler(icon_name, text_item))
                self.canvas.tag_bind(text_item, "<Button-1>", make_click_handler(icon_name, text_item))

                # Cursor change on hover
                self.canvas.tag_bind(img_item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(img_item, "<Leave>", lambda e: self.canvas.config(cursor=""))
                self.canvas.tag_bind(text_item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(text_item, "<Leave>", lambda e: self.canvas.config(cursor=""))

                self.visible_items[idx] = ([img_item, text_item], icon_obj)

            except Exception as e:
                # If icon fails to load, show error
                text_item = self.canvas.create_text(
                    x,
                    y,
                    text=f"Error\n{icon_name}",
                    width=self.item_width - 10,
                    font=("Arial", 8),
                    fill="red",
                )
                self.visible_items[idx] = ([text_item], None)

    def filter_icons(self, search_text):
        """Filter icons by search text."""
        search_text = search_text.lower().strip()
        if not search_text:
            self.filtered_icons = self.all_icon_names.copy()
        else:
            self.filtered_icons = [
                name for name in self.all_icon_names if search_text in name.lower()
            ]

        # Clear all visible items
        for idx in list(self.visible_items.keys()):
            canvas_items, icon_obj = self.visible_items[idx]
            for item in canvas_items:
                self.canvas.delete(item)
            del self.visible_items[idx]

        # Reset scroll and update
        self.canvas.yview_moveto(0)
        self._update_scroll_region()
        self._render_visible_items()

    def update_icon_settings(self, size, color):
        """Update icon size and color."""
        self.icon_size = size
        self.icon_color = color

        # Clear cache to force re-render with new settings
        Icon._cache.clear()

        # Clear all visible items
        for idx in list(self.visible_items.keys()):
            canvas_items, icon_obj = self.visible_items[idx]
            for item in canvas_items:
                self.canvas.delete(item)
            del self.visible_items[idx]

        # Re-render
        self._render_visible_items()

    def update_style(self, style):
        """Update icon style variant (if provider supports it)."""
        self.icon_style = style
        Icon._cache.clear()
        for idx in list(self.visible_items.keys()):
            canvas_items, icon_obj = self.visible_items[idx]
            for item in canvas_items:
                self.canvas.delete(item)
            del self.visible_items[idx]
        self._render_visible_items()

    def change_icon_set(self, icon_class, icon_names):
        """Change the icon set being displayed."""
        self.icon_class = icon_class
        self.all_icon_names = icon_names
        self.filtered_icons = icon_names.copy()

        # Clear cache
        Icon._cache.clear()

        # Clear all visible items
        for idx in list(self.visible_items.keys()):
            canvas_items, icon_obj = self.visible_items[idx]
            for item in canvas_items:
                self.canvas.delete(item)
            del self.visible_items[idx]

        # Reset and render
        self.canvas.yview_moveto(0)
        self._update_scroll_region()
        self._render_visible_items()


class IconPreviewerApp:
    """Main application for previewing icons."""

    def __init__(self, root):
        self.root = root
        self.root.title("ttkbootstrap-icons Previewer")
        self.root.resizable(False, False)

        # Register cleanup
        atexit.register(Icon.cleanup)

        # Load icon data
        self.icon_data = self._load_icon_data()

        # Current settings
        self.current_icon_set = "bootstrap"
        self.current_size = 64
        self.current_color = "black"

        # Build UI
        self._build_ui()

    def _load_icon_data(self):
        """Discover providers and load icon names dynamically."""

        def extract_names(glyphmap):
            def dedup(names_iterable):
                # Remove prefixed aliases if a stripped version exists
                names = [str(x) for x in names_iterable]
                prefixes = [
                    "ion-ios-",
                    "ion-md-",
                    "ion-android-",
                    "ion-",
                    "ra-",
                    "wi-",
                    "mdi-",
                    "si-",
                    "simple-icons-",
                ]
                name_set = set(names)
                result = []
                for n in sorted(name_set):
                    low = n.lower()
                    skip = False
                    for p in prefixes:
                        if low.startswith(p):
                            stripped = low[len(p) :]
                            # If the stripped version exists (exactly), prefer it
                            if stripped in name_set:
                                skip = True
                                break
                    if not skip:
                        result.append(n)
                return sorted(result)

            if isinstance(glyphmap, dict):
                # Dict of codepoints or dict of dicts
                sample = next(iter(glyphmap.values())) if glyphmap else None
                if isinstance(sample, dict):
                    return dedup(glyphmap.keys())
                return dedup(glyphmap.keys())
            if isinstance(glyphmap, list):
                # List of dicts with "name"
                names = [g.get("name") for g in glyphmap if isinstance(g, dict) and g.get("name")]
                return dedup({n for n in names if n})
            return []

        def make_icon_class(provider):
            # Capture provider style capabilities
            try:
                supported_styles = set(provider.list_styles())  # type: ignore[attr-defined]
            except Exception:
                supported_styles = set()

            # Heuristic: providers with a single font but style-encoded names
            # should append style suffix to base names (e.g., Devicon)
            has_multi_fonts = hasattr(provider, "styles")
            # Some multi-font providers also encode style in glyph names (e.g., Fluent)
            multi_font_suffix_providers = {"fluent"}

            class _ProviderIcon(Icon):
                def __init__(self, name: str, size: int = 64, color: str = "black", style=None):
                    # Initialize renderer with provider/style
                    Icon.initialize_with_provider(provider, style=style)
                    resolved = name
                    if name != "none" and style and supported_styles:
                        lowered = name.lower()
                        prov_name = getattr(provider, "name", "").lower()
                        mp = Icon._icon_map
                        # Single-font providers: manage suffix resolution smartly
                        if not has_multi_fonts:
                            if prov_name == "eva":
                                # Eva fill often uses base name; outline uses -outline
                                if style == "fill":
                                    if lowered.endswith("-fill"):
                                        resolved = name
                                    elif name in mp:
                                        resolved = name
                                    elif f"{name}-fill" in mp:
                                        resolved = f"{name}-fill"
                                else:  # outline
                                    if lowered.endswith("-outline"):
                                        resolved = name
                                    elif f"{name}-outline" in mp:
                                        resolved = f"{name}-outline"
                                    elif name in mp:
                                        resolved = name
                            else:
                                # Default: append suffix if missing
                                if not any(lowered.endswith("-" + s) for s in supported_styles):
                                    resolved = f"{name}-{style}"
                        # Some multi-font providers encode style suffix in glyph names (e.g., Fluent)
                        elif prov_name in multi_font_suffix_providers:
                            if not any(lowered.endswith("-" + s) for s in supported_styles):
                                resolved = f"{name}-{style}"
                    super().__init__(resolved, size, color)

            return _ProviderIcon

        # Seed with built-in providers
        providers = {
            "bootstrap": BuiltinBootstrapProvider(),
            
        }

        # Load external providers via entry points
        registry = ProviderRegistry()
        load_external_providers(registry)
        for name in registry.names():
            prov = registry.get_provider(name)
            if prov and name not in providers:
                providers[name] = prov

        # Dev fallback: attempt to import known providers directly if not installed
        # If running from a monorepo, add each provider's src dir to sys.path
        try:
            repo_packages_dir = os.path.join(os.getcwd(), "packages")
            if os.path.isdir(repo_packages_dir):
                for entry in os.listdir(repo_packages_dir):
                    src_path = os.path.join(repo_packages_dir, entry, "src")
                    if os.path.isdir(src_path) and src_path not in sys.path:
                        sys.path.insert(0, src_path)
        except Exception:
            pass
        dev_candidates = [
            ("fa", "ttkbootstrap_icons_fa.provider", "FontAwesomeFontProvider"),
            ("ion", "ttkbootstrap_icons_ion.provider", "IonFontProvider"),
            ("remix", "ttkbootstrap_icons_remix.provider", "RemixFontProvider"),
            ("fluent", "ttkbootstrap_icons_fluent.provider", "FluentFontProvider"),
            ("simple", "ttkbootstrap_icons_simple.provider", "SimpleFontProvider"),
            ("mat", "ttkbootstrap_icons_mat.provider", "MaterialFontProvider"),
            ("weather", "ttkbootstrap_icons_weather.provider", "WeatherFontProvider"),
            ("gmi", "ttkbootstrap_icons_gmi.provider", "GoogleMaterialProvider"),
            ("devicon", "ttkbootstrap_icons_devicon.provider", "DeviconFontProvider"),
            ("rpga", "ttkbootstrap_icons_rpga.provider", "RPGAFontProvider"),
            ("eva", "ttkbootstrap_icons_eva.provider", "EvaFontProvider"),
        ]
        for name, mod_path, cls_name in dev_candidates:
            if name in providers:
                continue
            try:
                mod = importlib.import_module(mod_path)
                ProviderCls = getattr(mod, cls_name)
                providers[name] = ProviderCls()
            except Exception:
                continue

        # Build data map
        data = {}
        for name, provider in providers.items():
            try:
                # Collect base names once
                _, glyphmap_text = provider.load_assets()
                glyphmap = json.loads(glyphmap_text)
                all_names = extract_names(glyphmap)
                if not all_names:
                    continue

                styles: list[str] = []
                style_labels: list[str] = []
                default_style = None
                # Probe for styles if the provider supports them
                if hasattr(provider, "list_styles"):
                    try:
                        styles = provider.list_styles()  # type: ignore[attr-defined]
                    except Exception:
                        styles = []
                if hasattr(provider, "get_default_style"):
                    try:
                        default_style = provider.get_default_style()  # type: ignore[attr-defined]
                    except Exception:
                        default_style = None
                # Show styles exactly as they should be used as parameters
                # Use raw style identifiers for display to avoid casing confusion
                if styles:
                    style_labels = list(styles)

                # Build names per style to avoid preview errors when a style limits coverage
                names_by_style = {}
                display_names_by_style = {}
                has_multi_fonts = hasattr(provider, "styles")
                if styles:
                    if has_multi_fonts:
                        # Query provider per style to get exact coverage
                        for s in styles:
                            try:
                                _, gm_text = provider.load_assets(style=s)
                                gm = json.loads(gm_text)
                                names_by_style[s] = extract_names(gm)
                            except Exception:
                                names_by_style[s] = []
                            # For display, prefer base names without the style suffix if present
                            base_names = []
                            suffix = "-" + s
                            for n in names_by_style[s]:
                                if n.lower().endswith(suffix):
                                    base_names.append(n[: -len(suffix)])
                                else:
                                    base_names.append(n)
                            display_names_by_style[s] = sorted(set(base_names))
                    else:
                        # Single font; build per-style lists. Some sets (e.g., Eva) use base name for a style.
                        prov_name = getattr(provider, "name", "").lower()
                        lowered_all = [n.lower() for n in all_names]
                        set_all = set(lowered_all)
                        for s in styles:
                            if prov_name == "eva" and s == "fill":
                                # Fill: include names that either end with -fill or have no -outline suffix
                                names = [
                                    n for n in all_names if n.lower().endswith("-fill") or not n.lower().endswith("-outline")
                                ]
                            else:
                                names = [n for n in all_names if n.lower().endswith("-" + s)]
                            names_by_style[s] = sorted(set(names))
                            # For display, show base names only
                            base_names = []
                            suffix = "-" + s
                            for n in names_by_style[s]:
                                ln = n.lower()
                                if prov_name == "eva" and s == "fill" and not ln.endswith("-fill"):
                                    base_names.append(n)
                                elif ln.endswith(suffix):
                                    base_names.append(n[: -len(suffix)])
                            display_names_by_style[s] = sorted(set(base_names))

                data[name] = {
                    "class": make_icon_class(provider),
                    "names": all_names,
                    "names_by_style": names_by_style,
                    "display_names_by_style": display_names_by_style,
                    "styles": styles,
                    "style_labels": style_labels,
                    "display": provider.display_name(),
                    "default_style": default_style,
                }
            except Exception:
                # Ignore providers that fail to load
                pass

        return data

    def _build_ui(self):
        """Build the user interface."""
        # Top control panel
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side="top", fill="x")

        # Row 1: Icon Set, Size, Color, and Color Presets
        row1 = ttk.Frame(control_frame)
        row1.pack(fill="x", pady=(10, 5))

        ttk.Label(row1, text="Icon Set:", width=10).pack(side="left", padx=(0, 5))

        # Build mapping of display name -> internal key, and sort by display name
        self.icon_set_map = {v.get("display", k): k for k, v in self.icon_data.items()}
        sorted_displays = sorted(self.icon_set_map.keys(), key=str.casefold)
        # Ensure the combobox reflects the current icon set's display name
        current_display = None
        try:
            current_display = next(d for d, key in self.icon_set_map.items() if key == self.current_icon_set)
        except StopIteration:
            current_display = sorted_displays[0] if sorted_displays else ""
        self.icon_set_var = tk.StringVar(value=current_display)
        icon_set_combo = ttk.Combobox(
            row1,
            textvariable=self.icon_set_var,
            values=sorted_displays,
            state="readonly",
            width=15,
        )

        icon_set_combo.pack(side="left", padx=(0, 20), fill='x', expand=True)
        icon_set_combo.bind("<<ComboboxSelected>>", self._on_icon_set_change)

        # Style selection (conditionally enabled)
        ttk.Label(row1, text="Style:").pack(side="left", padx=(0, 5))
        self.style_var = tk.StringVar()
        self.style_combo = ttk.Combobox(row1, textvariable=self.style_var, state="disabled", width=15)
        self.style_combo.pack(side="left", padx=(0, 20))
        self.style_combo.bind("<<ComboboxSelected>>", self._on_style_change)

        ttk.Label(row1, text="Size:").pack(side="left", padx=(0, 5))

        self.size_var = tk.IntVar(value=64)
        size_spinbox = ttk.Spinbox(
            row1, from_=16, to=128, textvariable=self.size_var, width=8, command=self._on_settings_change
        )
        size_spinbox.pack(side="left", padx=(0, 20))
        self.size_var.trace_add("write", self._on_settings_change)

        ttk.Label(row1, text="Color:").pack(side="left", padx=(0, 5))

        self.color_var = tk.StringVar(value="black")
        color_entry = ttk.Entry(row1, textvariable=self.color_var, width=15)
        color_entry.pack(side="left", padx=(0, 10))
        self.color_var.trace_add("write", self._on_settings_change)

        # Add some preset colors
        preset_frame = ttk.Frame(row1)
        preset_frame.pack(side="left")

        preset_colors = [
            ("Black", "black"),
            ("Blue", "#0d6efd"),
            ("Red", "#dc3545"),
            ("Green", "#198754"),
            ("Orange", "#fd7e14"),
        ]

        for name, color in preset_colors:
            btn = tk.Button(
                preset_frame,
                text="",
                bg=color,
                width=2,
                height=1,
                relief="flat",
                command=lambda c=color: self.color_var.set(c),
            )
            btn.pack(side="left", padx=2)

        # Row 2: Search
        row2 = ttk.Frame(control_frame)
        row2.pack(fill="x", pady=(0, 5))

        ttk.Label(row2, text="Search:", width=10).pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row2, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", fill="x", expand=True)
        self.search_var.trace_add("write", self._on_search_change)

        # Status label (icon count) to the right of search
        self.status_var = tk.StringVar(value="")
        status_label = ttk.Label(
            row2,
            textvariable=self.status_var,
            foreground="gray",
            font=("Arial", 8),
            anchor="e",
        )
        status_label.pack(side="right", padx=(10, 0))

        # Row 3: Info and Status
        row3 = ttk.Frame(control_frame)
        row3.pack(fill="x")

        # Info label (left)
        info_label = ttk.Label(
            row3, text="💡 Click any icon to copy its name", foreground="gray", font=("Arial", 8), anchor="center")
        info_label.pack(side="left", fill='x', expand=True)

        # Icon grid
        grid_frame = ttk.Frame(self.root)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create virtual grid
        # Pick initial set
        initial_data = self.icon_data[self.current_icon_set]
        # Configure style control for initial set
        styles = initial_data.get("styles", [])
        style_labels = initial_data.get("style_labels", [])
        # Build style label -> style id map for current set
        self.style_label_map = dict(zip(style_labels, styles)) if styles else {}
        default_style = initial_data.get("default_style")
        if styles:
            values = style_labels or styles
            self.style_combo.configure(state="readonly", values=values)
            default_label = None
            if default_style and style_labels:
                try:
                    default_label = style_labels[styles.index(default_style)]
                except Exception:
                    default_label = None
            self.style_var.set(default_label or (values[0] if values else ""))
            self.current_style = self.style_label_map.get(self.style_var.get(), self.style_var.get())
        else:
            self.style_combo.configure(state="disabled", values=[])
            self.style_var.set("")
            self.current_style = None
        display_names = initial_data["names"]
        if self.current_style:
            if initial_data.get("display_names_by_style"):
                display_names = initial_data["display_names_by_style"].get(self.current_style, [])
            elif initial_data.get("names_by_style"):
                display_names = initial_data["names_by_style"].get(self.current_style, [])
        self.grid = VirtualIconGrid(
            grid_frame,
            initial_data["class"],
            display_names,
            self.current_size,
            self.current_color,
            self.current_style,
        )

        # Update status
        self._update_status()

    def _on_icon_set_change(self, event=None):
        """Handle icon set change."""
        new_set_display = self.icon_set_var.get()
        new_set = self.icon_set_map.get(new_set_display, self.current_icon_set)
        if new_set != self.current_icon_set:
            self.current_icon_set = new_set
            data = self.icon_data[new_set]
            # Update styles UI
            styles = data.get("styles", [])
            style_labels = data.get("style_labels", [])
            self.style_label_map = dict(zip(style_labels, styles)) if styles else {}
            default_style = data.get("default_style")
            if styles:
                values = style_labels or styles
                self.style_combo.configure(state="readonly", values=values)
                default_label = None
                if default_style and style_labels:
                    try:
                        default_label = style_labels[styles.index(default_style)]
                    except Exception:
                        default_label = None
                self.style_var.set(default_label or (values[0] if values else ""))
                self.current_style = self.style_label_map.get(self.style_var.get(), self.style_var.get())
            else:
                self.style_combo.configure(state="disabled", values=[])
                self.style_var.set("")
                self.current_style = None

            display_names = data["names"]
            if self.current_style:
                if data.get("display_names_by_style"):
                    display_names = data["display_names_by_style"].get(self.current_style, [])
                elif data.get("names_by_style"):
                    display_names = data["names_by_style"].get(self.current_style, [])
            self.grid.change_icon_set(data["class"], display_names)
            # Apply style to grid
            self.grid.update_style(self.current_style)
            self.search_var.set("")  # Clear search
            self._update_status()

    def _on_search_change(self, *args):
        """Handle search text change."""
        search_text = self.search_var.get()
        self.grid.filter_icons(search_text)
        self._update_status()

    def _on_settings_change(self, *args):
        """Handle size or color change."""
        try:
            size = self.size_var.get()
            color = self.color_var.get()

            # Validate
            if size < 16:
                size = 16
            if size > 128:
                size = 128

            self.current_size = size
            self.current_color = color

            # Debounce updates (only update after short delay)
            if hasattr(self, "_update_timer"):
                self.root.after_cancel(self._update_timer)

            self._update_timer = self.root.after(
                300, lambda: self.grid.update_icon_settings(size, color)
            )

        except (ValueError, tk.TclError):
            pass  # Ignore invalid values during typing

    def _on_style_change(self, event=None):
        label = self.style_var.get()
        style = self.style_label_map.get(label, label) or None
        self.current_style = style
        # Also filter names to only those valid for this style to avoid errors
        data = self.icon_data.get(self.current_icon_set, {})
        names = data.get("names", [])
        if style:
            if data.get("display_names_by_style"):
                names = data["display_names_by_style"].get(style, [])
            elif data.get("names_by_style"):
                names = data["names_by_style"].get(style, [])
        self.grid.change_icon_set(data.get("class"), names)
        self.grid.update_style(style)
        self._update_status()

    def _update_status(self):
        """Update status label."""
        total = len(self.grid.all_icon_names)
        filtered = len(self.grid.filtered_icons)

        if filtered == total:
            self.status_var.set(f"{total} icons")
        else:
            self.status_var.set(f"{filtered} of {total} icons")


def main():
    """Run the icon previewer application."""
    root = tk.Tk()
    icon = BootstrapIcon("grid-3x2-gap-fill", size=16)
    root.iconphoto(True, icon.image)
    IconPreviewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()



