"""
Icon Previewer for ttkbootstrap-icons

Minimal, provider-driven previewer UI.
"""

import atexit
import tkinter as tk
import webbrowser
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon
from ttkbootstrap_icons.bootstrap import BootstrapFontProvider
from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons.registry import ProviderRegistry, load_external_providers


class SimpleIconGrid:
    def __init__(self, parent, provider, icon_names, icon_size=32, icon_color="black", icon_style=None, on_select=None):
        self.parent = parent
        self.provider = provider
        self.icon_size = icon_size
        self.icon_color = icon_color
        self.icon_style = icon_style
        self.all_icon_names = list(icon_names)
        self.filtered = list(icon_names)
        self.on_select = on_select  # Callback for icon selection

        self.canvas = tk.Canvas(parent, width=700, height=480, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self._on_scrollbar)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both")
        self.scrollbar.pack(side="right", fill="y")

        self.item_w = 60
        self.item_h = 60
        self.gap = 10
        self.cols = max(1, (700 + self.gap) // (self.item_w + self.gap))

        # Virtualization state
        self.visible_items: dict[int, tuple[list[int], object]] = {}

        self.canvas.bind("<Configure>", self._on_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        self._update_scroll_region()
        self._render_visible()

    def _on_scrollbar(self, *args):
        # Proxy to canvas yview, then render visible rows
        try:
            self.canvas.yview(*args)
        finally:
            self._render_visible()

    def _update_scroll_region(self):
        total = len(self.filtered)
        rows = (total + self.cols - 1) // self.cols
        height = rows * (self.item_h + self.gap) + self.gap
        self.canvas.configure(scrollregion=(0, 0, 700, height))

    def _on_configure(self, event=None):
        self._render_visible()

    def _on_mousewheel(self, event):
        if getattr(event, 'num', None) == 4:
            self.canvas.yview_scroll(-1, "units")
        elif getattr(event, 'num', None) == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._render_visible()
        return "break"

    def _render_visible(self):
        y_top = self.canvas.canvasy(0)
        y_bottom = self.canvas.canvasy(self.canvas.winfo_height())
        first_row = max(0, int(y_top / (self.item_h + self.gap)) - 1)
        last_row = int(y_bottom / (self.item_h + self.gap)) + 2

        first_idx = first_row * self.cols
        last_idx = min(len(self.filtered), last_row * self.cols)

        # Remove offscreen items
        to_remove = [idx for idx in self.visible_items.keys() if idx < first_idx or idx >= last_idx]
        for idx in to_remove:
            items, _icon = self.visible_items.pop(idx)
            for it in items:
                self.canvas.delete(it)

        # Add newly visible items
        for idx in range(first_idx, last_idx):
            if idx in self.visible_items:
                continue
            if idx >= len(self.filtered):
                break
            name = self.filtered[idx]
            r = idx // self.cols
            c = idx % self.cols
            x = self.gap + c * (self.item_w + self.gap) + self.item_w // 2
            y = self.gap + r * (self.item_h + self.gap) + self.item_h // 2
            canvas_items = []
            try:
                Icon.initialize_with_provider(self.provider, style=self.icon_style)
                resolved_name = self.provider.resolve_icon_name(name, style=self.icon_style)
                icon_obj = Icon(resolved_name, size=self.icon_size, color=self.icon_color)
                img = self.canvas.create_image(x, y, image=icon_obj.image)
                canvas_items.append(img)

                def _make_select_handler(icon_name: str):
                    def _handler(event=None):
                        try:
                            if self.on_select:
                                self.on_select(icon_name)
                        except Exception:
                            pass

                    return _handler

                self.canvas.tag_bind(img, "<Button-1>", _make_select_handler(name))
                self.canvas.tag_bind(img, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(img, "<Leave>", lambda e: self.canvas.config(cursor=""))
            except Exception:
                txt = self.canvas.create_text(
                    x, y, text=f"Error\n{name}", width=self.item_w - 10, font=("Arial", 8), fill="red")
                canvas_items.append(txt)
                icon_obj = None
            self.visible_items[idx] = (canvas_items, icon_obj)

    def change_icon_set(self, provider, icon_names):
        self.provider = provider
        self.all_icon_names = list(icon_names)
        self.filtered = list(icon_names)
        Icon._cache.clear()
        for items, _ in list(self.visible_items.values()):
            for it in items:
                self.canvas.delete(it)
        self.visible_items.clear()
        self._update_scroll_region()
        self._render_visible()

    def filter(self, text):
        t = (text or "").lower().strip()
        if not t:
            self.filtered = list(self.all_icon_names)
        else:
            self.filtered = [n for n in self.all_icon_names if t in n.lower()]
        for items, _ in list(self.visible_items.values()):
            for it in items:
                self.canvas.delete(it)
        self.visible_items.clear()
        self.canvas.yview_moveto(0)
        self._update_scroll_region()
        self._render_visible()

    def update_icon_settings(self, size, color):
        self.icon_size = size
        self.icon_color = color
        Icon._cache.clear()
        for items, _ in list(self.visible_items.values()):
            for it in items:
                self.canvas.delete(it)
        self.visible_items.clear()
        self._render_visible()

    def update_style(self, style):
        self.icon_style = style
        Icon._cache.clear()
        for items, _ in list(self.visible_items.values()):
            for it in items:
                self.canvas.delete(it)
        self.visible_items.clear()
        self._render_visible()


class IconPreviewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TTkBootstrap Icons Browser")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)
        atexit.register(Icon.cleanup)

        self.icon_data = self._load_icon_data()
        self.current_icon_set = "bootstrap"
        self.current_style = None
        self.current_size = 32
        self.current_color = "black"
        self.selected_icon = None

        self._build_ui()

    def _load_icon_data(self):
        providers = {"bootstrap": BootstrapFontProvider()}
        registry = ProviderRegistry()
        load_external_providers(registry)
        for name in registry.names():
            prov = registry.get_provider(name)
            if prov and name not in providers:
                providers[name] = prov

        data = {}
        for name, provider in providers.items():
            try:
                idx = provider.build_display_index()
                names_by_style = idx.get("names_by_style", {})

                data[name] = {
                    "provider": provider,
                    "names_by_style": names_by_style,
                    "has_styles": idx.get("has_styles", False),
                    "styles": list(idx.get("styles", [])),
                    "default_style": idx.get("default_style"),
                    "display": provider.display_name,
                }
            except Exception:
                continue

        return data

    def _build_info_panel(self):
        provider_frame = ttk.LabelFrame(self.info_panel, text="Font Provider", padding=10)
        provider_frame.pack(fill="x", pady=(0, 10))

        self.provider_name_label = ttk.Label(provider_frame, text="", font=("Arial", 10, "bold"))
        self.provider_name_label.pack(anchor="w")

        # Combined version + icon count line
        self.provider_version_label = ttk.Label(provider_frame, text="", foreground="gray", font=("Arial", 9))
        self.provider_version_label.pack(anchor="w")

        # Links section
        self.links_spacer = ttk.Frame(provider_frame, height=24)
        self.links_spacer.pack(fill="x")

        self.links_title_label = ttk.Label(provider_frame, text="Links:", font=("Arial", 9, "bold"))
        self.links_title_label.pack(anchor="w")

        self.links_container = ttk.Frame(provider_frame)
        self.links_container.pack(fill="x")

        # Homepage and License links (clickable)
        self.provider_homepage_link = tk.Label(
            self.links_container,
            text="",
            fg="#0066cc",
            cursor="hand2",
            font=("Arial", 9, "underline"),
        )
        # Small icon for homepage link
        try:
            self._home_icon = BootstrapIcon("house", size=14, style="fill")
            self.provider_homepage_link.config(image=self._home_icon.image, compound="left")
            self.provider_homepage_link.image = self._home_icon.image
        except Exception:
            self._home_icon = None
        self.provider_homepage_link.pack(anchor="w", pady=(2, 0))

        self.provider_license_link = tk.Label(
            self.links_container,
            text="",
            fg="#0066cc",
            cursor="hand2",
            font=("Arial", 9, "underline"),
        )
        # Small icon for license link
        try:
            self._license_icon = BootstrapIcon("file-earmark-text", size=14, style="fill")
            self.provider_license_link.config(image=self._license_icon.image, compound="left")
            self.provider_license_link.image = self._license_icon.image
        except Exception:
            self._license_icon = None
        self.provider_license_link.pack(anchor="w")

        preview_frame = ttk.LabelFrame(self.info_panel, text="Preview", padding=10)
        preview_frame.pack(fill="x", pady=(0, 10))

        self.icon_preview_label = ttk.Label(preview_frame, text="", font=("Arial", 160))
        self.icon_preview_label.pack(pady=10)

        details_frame = ttk.LabelFrame(self.info_panel, text="Details", padding=10)
        details_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(details_frame, text="Name:", font=("Arial", 9, "bold")).pack(anchor="w")
        self.icon_name_label = ttk.Label(details_frame, text="", font=("Arial", 9), foreground="#0066cc")
        self.icon_name_label.pack(anchor="w", pady=(0, 8))

        ttk.Label(details_frame, text="Unicode:", font=("Arial", 9, "bold")).pack(anchor="w")
        self.icon_code_label = ttk.Label(details_frame, text="", font=("Courier", 9))
        self.icon_code_label.pack(anchor="w")

        self.copy_button = ttk.Button(self.info_panel, text="Copy Name", command=self._copy_icon_name, state="disabled")
        self.copy_button.pack(fill="x", pady=(10, 0))

        self._update_info_panel(None)

    def _update_info_panel(self, icon_name):
        provider_data = self.icon_data[self.current_icon_set]
        provider = provider_data["provider"]

        self.provider_name_label.config(text=provider.display_name)
        version_text = f"v{provider.icon_version}" if provider.icon_version else "Version: N/A"
        names_by_style = provider_data.get("names_by_style", {})
        if self.current_style and self.current_style in names_by_style:
            icon_count = len(names_by_style[self.current_style])
        elif names_by_style:
            first_style = next(iter(names_by_style.keys()))
            icon_count = len(names_by_style[first_style])
        else:
            icon_count = 0
        meta_text = f"{version_text}  •  {icon_count:,} icons"
        self.provider_version_label.config(text=meta_text)
        # Ensure legacy count label remains hidden
        try:
            if self.provider_count_label.winfo_ismapped():
                self.provider_count_label.pack_forget()
        except Exception:
            pass

        # Update homepage link visibility and binding
        homepage = getattr(provider, "homepage", None)
        if homepage:
            self.provider_homepage_link.config(text="Homepage")
            # Rebind to ensure latest URL
            try:
                self.provider_homepage_link.unbind("<Button-1>")
            except Exception:
                pass
            self.provider_homepage_link.bind("<Button-1>", lambda e, url=homepage: webbrowser.open(url))
            if not self.provider_homepage_link.winfo_ismapped():
                self.provider_homepage_link.pack(anchor="w", pady=(2, 0))
        else:
            self.provider_homepage_link.config(text="")
            try:
                self.provider_homepage_link.unbind("<Button-1>")
            except Exception:
                pass
            if self.provider_homepage_link.winfo_ismapped():
                self.provider_homepage_link.pack_forget()

        # Update license link visibility and binding
        license_url = getattr(provider, "license_url", None)
        if license_url:
            self.provider_license_link.config(text="License")
            try:
                self.provider_license_link.unbind("<Button-1>")
            except Exception:
                pass
            self.provider_license_link.bind("<Button-1>", lambda e, url=license_url: webbrowser.open(url))
            if not self.provider_license_link.winfo_ismapped():
                self.provider_license_link.pack(anchor="w")
        else:
            self.provider_license_link.config(text="")
            try:
                self.provider_license_link.unbind("<Button-1>")
            except Exception:
                pass
            if self.provider_license_link.winfo_ismapped():
                self.provider_license_link.pack_forget()

        # Show or hide the links section title (and spacer) depending on availability
        try:
            has_any_link = bool(homepage) or bool(license_url)
            if has_any_link:
                if not self.links_spacer.winfo_ismapped():
                    self.links_spacer.pack(fill="x")
                if not self.links_title_label.winfo_ismapped():
                    self.links_title_label.pack(anchor="w")
            else:
                if self.links_title_label.winfo_ismapped():
                    self.links_title_label.pack_forget()
                if self.links_spacer.winfo_ismapped():
                    self.links_spacer.pack_forget()
        except Exception:
            pass

        if icon_name:
            try:
                Icon.initialize_with_provider(provider, style=self.current_style)
                resolved_name = provider.resolve_icon_name(icon_name, style=self.current_style)
                large_icon = Icon(resolved_name, size=160, color=self.current_color)
                self.icon_preview_label.config(image=large_icon.image)
                self.icon_preview_label.image = large_icon.image
            except Exception:
                self.icon_preview_label.config(image="", text="✕")

            self.icon_name_label.config(text=icon_name)

            try:
                Icon.initialize_with_provider(provider, style=self.current_style)
                resolved_name = provider.resolve_icon_name(icon_name, style=self.current_style)
                glyph_val = Icon._icon_map.get(resolved_name)
                if glyph_val is not None:
                    if isinstance(glyph_val, int):
                        code_hex = f"U+{glyph_val:04X}"
                    else:
                        code_hex = f"U+{ord(glyph_val):04X}"
                    self.icon_code_label.config(text=code_hex)
                else:
                    self.icon_code_label.config(text="N/A")
            except Exception:
                self.icon_code_label.config(text="N/A")

            self.copy_button.config(state="normal")
        else:
            self.icon_preview_label.config(image="", text="Select an icon")
            self.icon_name_label.config(text="—")
            self.icon_code_label.config(text="—")
            self.copy_button.config(state="disabled")

    def _copy_icon_name(self):
        if self.selected_icon:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.selected_icon)
            original_text = self.copy_button.cget("text")
            self.copy_button.config(text="✓ Copied!")
            self.root.after(1500, lambda: self.copy_button.config(text=original_text))

    def _on_icon_select(self, icon_name):
        self.selected_icon = icon_name
        self._update_info_panel(icon_name)

    def _build_ui(self):
        control = ttk.Frame(self.root, padding=10)
        control.pack(side="top", fill="x")

        row = ttk.Frame(control)
        row.pack(fill="x")

        ttk.Label(row, text="Icon Set:", width=10).pack(side="left", padx=(0, 5))
        self.icon_set_map = {v.get("display", k): k for k, v in self.icon_data.items()}
        displays = sorted(self.icon_set_map.keys(), key=str.casefold)
        self.icon_set_var = tk.StringVar(
            value=(next(
                (d for d, k in self.icon_set_map.items() if k == self.current_icon_set),
                displays[0] if displays else "")))
        icon_combo = ttk.Combobox(row, textvariable=self.icon_set_var, values=displays, state="readonly", width=20)
        icon_combo.pack(side="left", padx=(0, 10), fill='x', expand=True)
        icon_combo.bind("<<ComboboxSelected>>", self._on_icon_set_change)

        ttk.Label(row, text="Style:").pack(side="left", padx=(0, 5))
        self.style_var = tk.StringVar()
        self.style_combo = ttk.Combobox(row, textvariable=self.style_var, state="disabled", width=15)
        self.style_combo.pack(side="left", padx=(0, 10))
        self.style_combo.bind("<<ComboboxSelected>>", self._on_style_change)

        ttk.Label(row, text="Size:").pack(side="left", padx=(0, 5))
        self.size_var = tk.IntVar(value=self.current_size)
        size_spin = ttk.Spinbox(
            row, from_=16, to=128, textvariable=self.size_var, width=8, command=self._on_settings_change)
        size_spin.pack(side="left", padx=(0, 10))
        self.size_var.trace_add("write", self._on_settings_change)

        ttk.Label(row, text="Color:").pack(side="left", padx=(0, 5))
        self.color_var = tk.StringVar(value=self.current_color)
        self.color_var.trace_add("write", self._on_settings_change)

        preset_frame = ttk.Frame(row)
        preset_frame.pack(side="left")
        for c in ["black", "#0d6efd", "#dc3545", "#198754", "#fd7e14"]:
            btn = tk.Button(
                preset_frame, text="", bg=c, width=2, height=1, relief="flat",
                command=lambda col=c: self.color_var.set(col))
            btn.pack(side="left", padx=2)

        row2 = ttk.Frame(control)
        row2.pack(fill="x", pady=(6, 0))
        ttk.Label(row2, text="Search:", width=10).pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row2, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", fill="x", expand=True)
        self.search_var.trace_add("write", self._on_search_change)

        main_content = ttk.Frame(self.root)
        main_content.pack(fill="both", expand=True, padx=10, pady=(6, 10))

        grid_frame = ttk.Frame(main_content)
        grid_frame.pack(side="left", fill="both", expand=True)

        self.info_panel = ttk.Frame(main_content, width=350)
        self.info_panel.pack(side="right", fill="y", padx=(10, 0))
        self.info_panel.pack_propagate(False)  # Maintain fixed width
        self._build_info_panel()

        initial = self.icon_data[self.current_icon_set]
        styles = initial.get("styles", [])
        default_style = initial.get("default_style")
        if styles:
            self.style_combo.configure(state="readonly", values=styles)
            self.style_var.set(default_style or styles[0])
            self.current_style = self.style_var.get()
        else:
            self.style_combo.configure(state="disabled", values=[])
            self.style_var.set("")
            self.current_style = None

        names_by_style = initial.get("names_by_style", {})
        if self.current_style and self.current_style in names_by_style:
            names = list(names_by_style[self.current_style].keys())
        elif names_by_style:
            first_style = next(iter(names_by_style.keys()))
            names = list(names_by_style[first_style].keys())
        else:
            names = []

        self.grid = SimpleIconGrid(
            grid_frame, initial["provider"], names, self.current_size, self.current_color, self.current_style,
            on_select=self._on_icon_select)

        if names:
            self._on_icon_select(names[0])

    def _on_icon_set_change(self, event=None):
        disp = self.icon_set_var.get()
        new_set = self.icon_set_map.get(disp, self.current_icon_set)
        if new_set == self.current_icon_set:
            return
        self.current_icon_set = new_set
        data = self.icon_data[new_set]

        styles = data.get("styles", [])
        default_style = data.get("default_style")
        if styles:
            self.style_combo.configure(state="readonly", values=styles)
            self.style_var.set(default_style or styles[0])
            self.current_style = self.style_var.get()
        else:
            self.style_combo.configure(state="disabled", values=[])
            self.style_var.set("")
            self.current_style = None

        # Get icon names for the current style
        names_by_style = data.get("names_by_style", {})
        if self.current_style and self.current_style in names_by_style:
            names = list(names_by_style[self.current_style].keys())
        elif names_by_style:
            first_style = next(iter(names_by_style.keys()))
            names = list(names_by_style[first_style].keys())
        else:
            names = []

        self.grid.change_icon_set(data["provider"], names)
        self.grid.update_style(self.current_style)

        # Select the first icon in the new set
        if names:
            self._on_icon_select(names[0])

    def _on_search_change(self, *args):
        self.grid.filter(self.search_var.get())

    def _on_settings_change(self, *args):
        try:
            size = max(16, min(128, int(self.size_var.get())))
        except Exception:
            size = self.current_size
        self.current_size = size
        self.current_color = self.color_var.get()
        self.grid.update_icon_settings(size, self.current_color)

    def _on_style_change(self, event=None):
        self.current_style = self.style_var.get() or None
        data = self.icon_data[self.current_icon_set]

        # Get icon names for the current style
        names_by_style = data.get("names_by_style", {})
        if self.current_style and self.current_style in names_by_style:
            names = list(names_by_style[self.current_style].keys())
        elif names_by_style:
            first_style = next(iter(names_by_style.keys()))
            names = list(names_by_style[first_style].keys())
        else:
            names = []

        self.grid.change_icon_set(data["provider"], names)
        self.grid.update_style(self.current_style)

        # Select the first icon in the new style
        if names:
            self._on_icon_select(names[0])


def main():
    from ttkbootstrap_icons import BootstrapIcon
    root = tk.Tk()
    app_icon = BootstrapIcon("grid-3x3-gap-fill", color="#2F6FED")
    root.iconphoto(True, app_icon.image)
    IconPreviewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
