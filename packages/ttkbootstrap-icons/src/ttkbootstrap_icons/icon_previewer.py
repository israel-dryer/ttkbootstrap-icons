"""
Icon Previewer for ttkbootstrap-icons

Minimal, provider-driven previewer UI.
"""

import atexit
import json
import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons.providers import BuiltinBootstrapProvider
from ttkbootstrap_icons.registry import ProviderRegistry, load_external_providers


class SimpleIconGrid:
    def __init__(self, parent, icon_class, icon_names, icon_size=32, icon_color="black", icon_style=None):
        self.parent = parent
        self.icon_class = icon_class
        self.icon_size = icon_size
        self.icon_color = icon_color
        self.icon_style = icon_style
        self.all_icon_names = list(icon_names)
        self.filtered = list(icon_names)

        self.canvas = tk.Canvas(parent, width=830, height=480, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self._on_scrollbar)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both")
        self.scrollbar.pack(side="right", fill="y")

        self.item_w = 120
        self.item_h = 100
        self.gap = 18
        self.cols = max(1, (830 + self.gap) // (self.item_w + self.gap))

        # Virtualization state
        self.visible_items: dict[int, tuple[list[int], object]] = {}

        self.canvas.bind("<Configure>", self._on_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down

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
        self.canvas.configure(scrollregion=(0, 0, 830, height))

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
            y = self.gap + r * (self.item_h + self.gap) + self.gap
            canvas_items = []
            try:
                try:
                    icon_obj = self.icon_class(name, size=self.icon_size, color=self.icon_color, style=self.icon_style)
                except TypeError:
                    icon_obj = self.icon_class(name, size=self.icon_size, color=self.icon_color)
                img = self.canvas.create_image(x, y, image=icon_obj.image)
                txt = self.canvas.create_text(x, y + self.icon_size // 2 + 20, text=name, width=self.item_w - 10, font=("Arial", 8), fill="#333")
                canvas_items.extend([img, txt])
                # Click-to-copy handlers
                def _make_copy_handler(display_name: str, text_item: int):
                    def _handler(event=None):
                        root = self.canvas.winfo_toplevel()
                        try:
                            root.clipboard_clear()
                            root.clipboard_append(display_name)
                            # flash highlight
                            self.canvas.itemconfig(text_item, fill="#0d6efd", font=("Arial", 8, "bold"))
                            self.canvas.after(200, lambda: self.canvas.itemconfig(text_item, fill="#333", font=("Arial", 8)))
                        except Exception:
                            pass
                    return _handler
                self.canvas.tag_bind(img, "<Button-1>", _make_copy_handler(name, txt))
                self.canvas.tag_bind(txt, "<Button-1>", _make_copy_handler(name, txt))
                # Hover cursor
                self.canvas.tag_bind(img, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(img, "<Leave>", lambda e: self.canvas.config(cursor=""))
                self.canvas.tag_bind(txt, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(txt, "<Leave>", lambda e: self.canvas.config(cursor=""))
            except Exception:
                txt = self.canvas.create_text(x, y, text=f"Error\n{name}", width=self.item_w - 10, font=("Arial", 8), fill="red")
                canvas_items.append(txt)
                icon_obj = None
            self.visible_items[idx] = (canvas_items, icon_obj)

    def change_icon_set(self, icon_class, icon_names):
        self.icon_class = icon_class
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
        self.root.title("ttkbootstrap-icons Previewer")
        atexit.register(Icon.cleanup)

        self.icon_data = self._load_icon_data()
        self.current_icon_set = "bootstrap"
        self.current_style = None
        self.current_size = 64
        self.current_color = "black"

        self._build_ui()

    def _load_icon_data(self):
        # Providers: built-in + discovered
        providers = {"bootstrap": BuiltinBootstrapProvider()}
        registry = ProviderRegistry()
        load_external_providers(registry)
        for name in registry.names():
            prov = registry.get_provider(name)
            if prov and name not in providers:
                providers[name] = prov

        def make_icon_class(provider):
            prov_name = getattr(provider, "name", "").lower()

            class _ProviderIcon(Icon):
                def __init__(self, name: str, size: int = 64, color: str = "black", style=None):
                    Icon.initialize_with_provider(provider, style=style)
                    resolved = name
                    low = (name or "").lower()
                    sty = (style or "").lower() if style else None

                    if prov_name == "bootstrap":
                        if name != "none":
                            if sty == "fill":
                                if not low.endswith("-fill"):
                                    cand = f"{name}-fill"
                                    if cand in Icon._icon_map:
                                        resolved = cand
                            else:
                                if low.endswith("-fill"):
                                    base = name[:-5]
                                    if base in Icon._icon_map:
                                        resolved = base
                    elif prov_name == "eva":
                        if name != "none":
                            if low.endswith("-outline"):
                                resolved = name
                            elif low.endswith("-fill"):
                                base = name[:-5]
                                if base in Icon._icon_map:
                                    resolved = base
                            elif sty == "outline":
                                cand = f"{name}-outline"
                                if cand in Icon._icon_map:
                                    resolved = cand
                            else:
                                if name in Icon._icon_map:
                                    resolved = name
                    elif prov_name == "fluent":
                        if name != "none":
                            style_sfx = None
                            if sty in ("regular", "filled", "light"):
                                style_sfx = sty
                            full = name if low.startswith("ic-fluent-") else f"ic-fluent-{name}"
                            lf = full.lower()
                            if not lf.endswith(("-regular", "-filled", "-light")) and style_sfx:
                                full = f"{full}-{style_sfx}"
                                lf = full.lower()
                            stem = full
                            for suf in ("-regular", "-filled", "-light"):
                                if stem.lower().endswith(suf):
                                    stem = stem[: -len(suf)]
                                    break
                            def has_num(seg: str) -> bool:
                                # Consider a size segment only if the last token matches known sizes
                                if '-' not in seg:
                                    return False
                                tail = seg.rsplit('-', 1)[-1]
                                return tail in {"16", "20", "24", "28", "32", "48"}
                            if not has_num(stem) and style_sfx:
                                base_no_prefix = stem[len("ic-fluent-"):] if stem.lower().startswith("ic-fluent-") else stem
                                avail_sizes = []
                                prefix = f"ic-fluent-{base_no_prefix}-"
                                suffix = f"-{style_sfx}"
                                for k in Icon._icon_map.keys():
                                    if k.startswith(prefix) and k.endswith(suffix):
                                        mid = k[len(prefix): -len(suffix)]
                                        if mid.isdigit():
                                            try:
                                                avail_sizes.append(int(mid))
                                            except Exception:
                                                pass
                                if avail_sizes:
                                    preferred = [24, 20, 16, 28, 32, 48]
                                    pick = next((p for p in preferred if p in avail_sizes), None)
                                    if pick is None:
                                        pick = sorted(avail_sizes)[0]
                                    full = f"{stem}-{pick}{full[len(stem):]}"
                            resolved = full
                    elif prov_name == "devicon":
                        if name != "none" and sty:
                            if not low.endswith(f"-{sty}"):
                                cand = f"{name}-{sty}"
                                if cand in Icon._icon_map:
                                    resolved = cand
                    elif prov_name == "remix":
                        if name != "none" and sty in ("line", "fill"):
                            if not low.endswith(f"-{sty}"):
                                cand = f"{name}-{sty}"
                                if cand in Icon._icon_map:
                                    resolved = cand

                    super().__init__(resolved, size, color)

            return _ProviderIcon

        data = {}
        for name, provider in providers.items():
            try:
                # Require provider-supplied display index (no fallback)
                idx = provider.build_display_index()

                data[name] = {
                    "class": make_icon_class(provider),
                    "names": idx.get("names", []),
                    "names_by_style": idx.get("names_by_style", {}),
                    "display_names_by_style": idx.get("display_names_by_style", {}),
                    "styles": idx.get("styles", []),
                    "style_labels": idx.get("style_labels", idx.get("styles", [])),
                    "display": provider.display_name(),
                    "default_style": idx.get("default_style"),
                }
            except Exception:
                continue

        return data

    def _build_ui(self):
        control = ttk.Frame(self.root, padding=10)
        control.pack(side="top", fill="x")

        row = ttk.Frame(control)
        row.pack(fill="x")

        ttk.Label(row, text="Icon Set:").pack(side="left", padx=(0, 5))
        self.icon_set_map = {v.get("display", k): k for k, v in self.icon_data.items()}
        displays = sorted(self.icon_set_map.keys(), key=str.casefold)
        self.icon_set_var = tk.StringVar(value=(next((d for d, k in self.icon_set_map.items() if k == self.current_icon_set), displays[0] if displays else "")))
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
        size_spin = ttk.Spinbox(row, from_=16, to=128, textvariable=self.size_var, width=8, command=self._on_settings_change)
        size_spin.pack(side="left", padx=(0, 10))
        self.size_var.trace_add("write", self._on_settings_change)

        ttk.Label(row, text="Color:").pack(side="left", padx=(0, 5))
        self.color_var = tk.StringVar(value=self.current_color)
        color_entry = ttk.Entry(row, textvariable=self.color_var, width=12)
        color_entry.pack(side="left", padx=(0, 10))
        self.color_var.trace_add("write", self._on_settings_change)

        # Color presets
        preset_frame = ttk.Frame(row)
        preset_frame.pack(side="left")
        for c in ["black", "#0d6efd", "#dc3545", "#198754", "#fd7e14"]:
            btn = tk.Button(preset_frame, text="", bg=c, width=2, height=1, relief="flat", command=lambda col=c: self.color_var.set(col))
            btn.pack(side="left", padx=2)

        row2 = ttk.Frame(control)
        row2.pack(fill="x", pady=(6, 0))
        ttk.Label(row2, text="Search:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row2, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", fill="x", expand=True)
        self.search_var.trace_add("write", self._on_search_change)

        # Info: click to copy
        info = ttk.Label(control, text="Click any icon to copy its name", foreground="gray", font=("Arial", 8), anchor="center")
        info.pack(fill="x", padx=10, pady=(6, 0), expand=True)

        grid_frame = ttk.Frame(self.root)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(6, 10))

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
        names = initial.get("names", [])
        if self.current_style:
            dnb = initial.get("display_names_by_style") or initial.get("names_by_style") or {}
            names = dnb.get(self.current_style, names)

        self.grid = SimpleIconGrid(grid_frame, initial["class"], names, self.current_size, self.current_color, self.current_style)

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
        names = data.get("names", [])
        if self.current_style:
            dnb = data.get("display_names_by_style") or data.get("names_by_style") or {}
            names = dnb.get(self.current_style, names)
        self.grid.change_icon_set(data["class"], names)
        self.grid.update_style(self.current_style)

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
        names = data.get("names", [])
        if self.current_style:
            dnb = data.get("display_names_by_style") or data.get("names_by_style") or {}
            names = dnb.get(self.current_style, names)
        self.grid.change_icon_set(data["class"], names)
        self.grid.update_style(self.current_style)


def main():
    root = tk.Tk()
    app = IconPreviewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
