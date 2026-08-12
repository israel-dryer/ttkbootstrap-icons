#!/usr/bin/env python
"""Capture the docs screenshots that cannot be generated from the renderer.

Most images in the docs are drawn at build time by `docs/_ext/render_figures.py`
and `pack_showcase.py`, so they cannot go stale. Three cannot be: they show real
widgets in a real window, which is the whole point of the pages they sit on.
Those pages carried no image at all until this existed — including
`getting-started/quickstart`, the first page a new user reads.

Screenshots do go stale, so the answer is to make retaking them one command
rather than a careful afternoon. Each window below is built from the code its
page actually publishes; if an example changes, change it here too and re-run.

    python .github/scripts/capture_screenshots.py            # all available
    python .github/scripts/capture_screenshots.py quickstart # just one

This needs a desktop session and cannot run in CI. It is deliberately not wired
into any workflow: a headless runner would produce either a crash or a black
rectangle, and a black rectangle is the kind of failure that gets committed.

`ttkbootstrap` is **not** installed in the working tree on purpose, so its two
captures are skipped unless you run this from a throwaway environment that has
it. That is the same pattern the docs examples are verified with.
"""

from __future__ import annotations

import argparse
import ctypes
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ASSETS = REPO / "docs" / "assets"

#: Ink used where an example hard-codes a color, matching the docs' own teal.
TEAL = "#0F766E"

#: Let the window manager compose and draw before the grab. Without it the
#: capture can catch a half-drawn frame, which looks like a rendering bug in a
#: library whose whole subject is rendering.
SETTLE_SECONDS = 0.6


def make_dpi_aware() -> None:
    """Match Tk's pixels to the screen's, so the grab lands on the window.

    Under a scaled display an unaware process is told a smaller virtual screen
    and then stretched, so `GetWindowRect` and Tk's own geometry disagree and
    the capture comes out cropped or offset.
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):  # pragma: no cover - not Windows, or pre-8.1
        pass


def window_bounds(root) -> tuple[int, int, int, int]:
    """The window's on-screen rectangle, including its frame.

    Prefers DWM's extended frame bounds. `GetWindowRect` reports a rectangle
    that includes the invisible resize border on Windows 10 and later, which
    puts several pixels of desktop down each side of the capture.
    """
    try:
        handle = int(root.wm_frame(), 16)
    except (ValueError, AttributeError, ctypes.ArgumentError):
        handle = None

    if handle:
        rect = ctypes.create_string_buffer(16)
        # DWMWA_EXTENDED_FRAME_BOUNDS = 9
        if ctypes.windll.dwmapi.DwmGetWindowAttribute(
            ctypes.c_void_p(handle), 9, rect, 16
        ) == 0:
            left, top, right, bottom = (
                int.from_bytes(rect[i * 4:i * 4 + 4], "little", signed=True)
                for i in range(4)
            )
            return left, top, right, bottom

    # Fallback: the client area only, which is still a usable picture.
    root.update_idletasks()
    x, y = root.winfo_rootx(), root.winfo_rooty()
    return x, y, x + root.winfo_width(), y + root.winfo_height()


def capture(root, out: Path) -> None:
    """Draw, settle, grab, and write a PNG."""
    from PIL import ImageGrab

    root.update_idletasks()
    root.update()
    root.attributes("-topmost", True)
    root.update()
    time.sleep(SETTLE_SECONDS)
    root.update()

    image = ImageGrab.grab(bbox=window_bounds(root), all_screens=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(f"wrote {out.relative_to(REPO)}  {image.size[0]}x{image.size[1]}")


def quickstart(out: Path) -> None:
    """`getting-started/quickstart` — exactly the example that page opens with."""
    import tkinter as tk
    from tkinter import ttk

    from tkinter_icons import MaterialIcon

    root = tk.Tk()
    root.title("Quickstart")
    home = MaterialIcon("home", size=24, color=TEAL)
    ttk.Button(root, text="Home", image=home.image, compound="left").pack(
        padx=20, pady=20, expand=True
    )
    # The example packs one small button, which gives a window too narrow to
    # show its own title bar text and half the width of the other captures.
    # Sized so the set reads as one thing, which is what the issue asked for.
    root.geometry("320x140")
    capture(root, out)
    root.destroy()


def tkinter_ttk(out: Path) -> None:
    """`integrations/tkinter-ttk` — its button, menu and treeview examples, composed.

    Composed rather than reproduced line for line: the page teaches each widget
    in its own snippet, and one window has to hold them all. The icons, sizes
    and colors are the page's; the layout is not, because the page has none.

    The menu is drawn as a menubar rather than posted open: an open menu is an
    OS-drawn popup outside the window's own rectangle, so it would fall outside
    the capture on some systems and overlap the tree on others.
    """
    import tkinter as tk
    from tkinter import ttk

    from tkinter_icons import LucideIcon

    root = tk.Tk()
    root.title("tkinter and ttk")
    icons = {
        "save": LucideIcon("save", size=16, color="#212529"),
        "new": LucideIcon("file-plus", size=16, color="#212529"),
        "open": LucideIcon("folder-open", size=16, color="#212529"),
        "quit": LucideIcon("log-out", size=16, color="#212529"),
        "folder": LucideIcon("folder", size=16, color="#f0ad4e"),
        "document": LucideIcon("file-text", size=16, color="#6c757d"),
        "close": LucideIcon("x", size=16, color="#212529"),
    }

    menu = tk.Menu(root)
    file_menu = tk.Menu(menu, tearoff=False)
    file_menu.add_command(label="New", image=icons["new"].image, compound="left")
    file_menu.add_command(label="Open", image=icons["open"].image, compound="left")
    file_menu.add_separator()
    file_menu.add_command(label="Quit", image=icons["quit"].image, compound="left")
    menu.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu)

    bar = ttk.Frame(root, padding=(12, 12, 12, 6))
    bar.pack(fill="x")
    ttk.Button(bar, text="Save", image=icons["save"].image, compound="left").pack(side="left")
    ttk.Button(bar, image=icons["close"].image, width=3).pack(side="left", padx=(8, 0))
    ttk.Label(bar, text="Documents", image=icons["folder"].image, compound="left").pack(
        side="left", padx=(16, 0)
    )

    tree = ttk.Treeview(root, columns=("size",), height=5)
    tree.heading("#0", text="Name")
    tree.heading("size", text="Size")
    tree.column("size", width=90, anchor="e")
    tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    src = tree.insert("", "end", text="src", image=icons["folder"].image, open=True)
    tree.insert(src, "end", text="main.py", image=icons["document"].image, values=("2.1 kB",))
    tree.insert(src, "end", text="render.py", image=icons["document"].image, values=("11.4 kB",))
    docs = tree.insert("", "end", text="docs", image=icons["folder"].image, open=True)
    tree.insert(docs, "end", text="index.rst", image=icons["document"].image, values=("1.3 kB",))

    root.geometry("420x244")
    capture(root, out)
    root.destroy()


def ttkbootstrap_theme(out: Path, theme: str) -> None:
    """`integrations/ttkbootstrap` — one mapped icon, under one theme.

    Called twice, and the pair is the page's whole argument: the same icon,
    no color argument anywhere, following the theme through a light/dark
    switch. A single capture would show a button and prove nothing.
    """
    import ttkbootstrap as ttk

    from tkinter_icons import LucideIcon

    # The theme name alone: "ttkbootstrap — bootstrap-dark" truncates to
    # "bootstrap-..." in the title bar, which tells a reader nothing about
    # which of the pair they are looking at.
    app = ttk.App(title=theme, theme=theme)
    check = LucideIcon("check", size=16)
    button = ttk.Button(app, text="Approve", bootstyle="success")
    button.pack(padx=24, pady=(24, 8))
    check.map(button)

    save = LucideIcon("save", size=16)
    secondary = ttk.Button(app, text="Save draft", bootstyle="secondary")
    secondary.pack(padx=24, pady=(0, 24))
    save.map(secondary)

    # Wide enough for the title bar to say which theme this is — the pair is
    # only an argument if a reader can tell them apart — and matching the
    # other captures' width so the set reads as one thing.
    app.geometry("320x150")
    capture(app, out)
    app.destroy()


def pysimplegui(out: Path) -> None:
    """`integrations/pysimplegui` — a small window that looks like an application.

    A hero image should show what the library makes possible, not label its
    own parts: an earlier version captioned the rows "IconButton" and
    "to_data() bytes", which taught nothing a picture can carry — bytes are
    not a visible thing. So this is just a plausible little file browser, and
    every icon in it happens to come through one bridge or the other.

    PySimpleGUI is not a dependency of this project, so this is skipped like
    the ttkbootstrap pair unless it is installed.
    """
    import PySimpleGUI as sg

    from tkinter_icons import BootstrapIcon
    from tkinter_icons.extensions.psg import IconButton

    sg.theme("DarkBlue3")
    text = sg.theme_text_color()
    muted = "#9fb0c4"
    accent = "#7ec8e3"

    def image(name, color=None, size=16):
        return sg.Image(data=BootstrapIcon(name, size, color or text).to_data(), pad=(6, 3))

    def row(icon, label, color, meta):
        return [image(icon, color), sg.Text(label, size=(18, 1)),
                sg.Text(meta, text_color=muted, size=(8, 1), justification="right")]

    toolbar = [
        IconButton("New", icon=BootstrapIcon("plus-lg", 16), key="-NEW-"),
        IconButton("Save", icon=BootstrapIcon("floppy", 16), key="-SAVE-"),
        IconButton(
            "Delete",
            icon=BootstrapIcon("trash", 16),
            reactive_states={"hover": "#f0918d", "pressed": "#d9534f"},
            key="-DELETE-",
        ),
        sg.Push(),
        IconButton("", icon=BootstrapIcon("gear", 16), compound="none", key="-PREFS-"),
    ]

    layout = [
        toolbar,
        [sg.HorizontalSeparator()],
        row("folder-fill", "assets", "#f5c46b", "4 items"),
        row("file-earmark-text", "report.md", text, "12 kB"),
        row("file-earmark-image", "diagram.png", accent, "84 kB"),
        row("star-fill", "notes.md", "#f5c46b", "3 kB"),
        [sg.HorizontalSeparator()],
        [image("check-circle-fill", "#8fd694", 14),
         sg.Text("Synced a moment ago", text_color=muted)],
    ]

    window = sg.Window(
        "Files", layout, finalize=True, use_ttk_buttons=True,
        # Not `text`: the title bar and taskbar are drawn by the OS, not on
        # the theme's background, so the theme's foreground colour is the wrong
        # one there — white on a light title bar is invisible.
        icon=BootstrapIcon("folder-fill", 32, "#d9922e").to_data(),
    )
    # Disabled without a caption saying so: the greyed glyph is the point.
    window["-DELETE-"].update(disabled=True)
    window.refresh()
    # Width set, height left to the content: sizing both leaves dead space under
    # the last row, sizing neither leaves the toolbar cramped.
    root = window.TKroot
    root.update_idletasks()
    root.geometry(f"420x{root.winfo_reqheight()}")
    window.refresh()
    capture(window.TKroot, out)
    window.close()


SHOTS = {
    "quickstart": lambda: quickstart(ASSETS / "quickstart_button.png"),
    "tkinter-ttk": lambda: tkinter_ttk(ASSETS / "tkinter_ttk_widgets.png"),
    "pysimplegui": lambda: pysimplegui(ASSETS / "pysimplegui_icons.png"),
    "ttkbootstrap-dark": lambda: ttkbootstrap_theme(
        ASSETS / "ttkbootstrap_dark.png", "bootstrap-dark"
    ),
    "ttkbootstrap-light": lambda: ttkbootstrap_theme(
        ASSETS / "ttkbootstrap_light.png", "bootstrap-light"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("names", nargs="*", choices=[*SHOTS, []], default=list(SHOTS))
    args = parser.parse_args()

    make_dpi_aware()
    failed = []
    for name in args.names or list(SHOTS):
        try:
            SHOTS[name]()
        except ImportError as exc:
            print(f"skipped {name}: {exc}", file=sys.stderr)
        except Exception as exc:  # pragma: no cover - a capture is manual anyway
            print(f"FAILED {name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            failed.append(name)
    if failed:
        print(f"\n{len(failed)} capture(s) failed: {failed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
