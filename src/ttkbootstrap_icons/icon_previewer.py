"""
Icon Previewer for ttkbootstrap-icons

A GUI application to browse and preview Bootstrap and Lucide icons with
virtual scrolling for performance.
"""

import atexit
import json
import math
import tkinter as tk
from importlib.resources import files
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon, LucideIcon
from ttkbootstrap_icons.icon import Icon


class VirtualIconGrid:
    """Virtual scrolling grid for displaying icons efficiently."""

    def __init__(self, parent, icon_class, icon_names, icon_size=32, icon_color="black"):
        self.parent = parent
        self.icon_class = icon_class
        self.all_icon_names = icon_names
        self.filtered_icons = icon_names.copy()
        self.icon_size = icon_size
        self.icon_color = icon_color

        # Grid configuration
        self.gap = 18  # Gap between icons
        self.item_width = 120  # Width of each icon cell
        self.item_height = 100  # Height of each icon cell
        self.canvas_width = 700  # Fixed canvas width
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
                icon_obj = self.icon_class(icon_name, size=self.icon_size, color=self.icon_color)

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
        self.current_size = 32
        self.current_color = "black"

        # Build UI
        self._build_ui()

    def _load_icon_data(self):
        """Load icon names from JSON files."""
        assets = files("ttkbootstrap_icons.assets")

        # Load Bootstrap icons
        bootstrap_json = json.loads(
            assets.joinpath("bootstrap.json").read_text(encoding="utf-8")
        )
        bootstrap_names = sorted(bootstrap_json.keys())

        # Load Lucide icons
        lucide_json = json.loads(assets.joinpath("lucide.json").read_text(encoding="utf-8"))
        lucide_names = sorted(lucide_json.keys())

        return {
            "bootstrap": {"class": BootstrapIcon, "names": bootstrap_names},
            "lucide": {"class": LucideIcon, "names": lucide_names},
        }

    def _build_ui(self):
        """Build the user interface."""
        # Top control panel
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side="top", fill="x")

        # Row 1: Icon Set, Size, Color, and Color Presets
        row1 = ttk.Frame(control_frame)
        row1.pack(fill="x", pady=(0, 5))

        ttk.Label(row1, text="Icon Set:", width=10).pack(side="left", padx=(0, 5))

        self.icon_set_var = tk.StringVar(value="bootstrap")
        icon_set_combo = ttk.Combobox(
            row1,
            textvariable=self.icon_set_var,
            values=["bootstrap", "lucide"],
            state="readonly",
            width=15,
        )

        icon_set_combo.pack(side="left", padx=(0, 20))
        icon_set_combo.bind("<<ComboboxSelected>>", self._on_icon_set_change)

        # Status label
        self.status_var = tk.StringVar(value="")
        status_label = ttk.Label(row1, textvariable=self.status_var, foreground="gray", font=("Arial", 8), anchor='w')
        status_label.pack(side="left", fill='x', expand=True)

        ttk.Label(row1, text="Size:").pack(side="left", padx=(0, 5))

        self.size_var = tk.IntVar(value=32)
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
        initial_data = self.icon_data[self.current_icon_set]
        self.grid = VirtualIconGrid(
            grid_frame,
            initial_data["class"],
            initial_data["names"],
            self.current_size,
            self.current_color,
        )

        # Update status
        self._update_status()

    def _on_icon_set_change(self, event=None):
        """Handle icon set change."""
        new_set = self.icon_set_var.get()
        if new_set != self.current_icon_set:
            self.current_icon_set = new_set
            data = self.icon_data[new_set]
            self.grid.change_icon_set(data["class"], data["names"])
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
