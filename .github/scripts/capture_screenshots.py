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
    """`integrations/pysimplegui` — both bridges in one window.

    The page's argument is that there are two ways in and they are not
    interchangeable, so the capture has to show both: `IconButton` where the
    icon sits beside text and reacts, and `to_data()` bytes on the elements
    that take an encoded image and never react. One row of each.

    PySimpleGUI is not a dependency of this project, so this is skipped like
    the ttkbootstrap pair unless it is installed.
    """
    import PySimpleGUI as sg

    from tkinter_icons import BootstrapIcon
    from tkinter_icons.extensions.psg import IconButton

    sg.theme("DarkBlue3")
    # Only the bytes need a color: an IconButton takes the button's own. And
    # the color comes from the theme rather than being typed in, which is what
    # the page teaches, so the code it publishes had better not contradict it.
    text = sg.theme_text_color()
    on_button = sg.theme_button_color_text()

    layout = [
        [sg.Text("IconButton — icon beside text, follows the button")],
        [
            IconButton("Save", icon=BootstrapIcon("floppy", 16), key="-SAVE-"),
            IconButton(
                "Delete",
                icon=BootstrapIcon("trash", 16),
                reactive_states={"hover": "#f0918d", "pressed": "#d9534f",
                                 "disabled": {"name": "trash-fill", "color": "#7c8a99"}},
                key="-DELETE-",
            ),
            # compound="none" because there is no text: the default reserves
            # room for a label that is not there, ~70 px of it on a ttk button.
            IconButton("", icon=BootstrapIcon("gear", 16), compound="none",
                       key="-PREFS-"),
        ],
        [sg.Text("to_data() bytes — no deferral, no subclass, no reacting")],
        [
            sg.Image(data=BootstrapIcon("house", 16, text).to_data()),
            sg.Text("Dashboard"),
            sg.Push(),
            sg.Button(image_data=BootstrapIcon("bell", 16, on_button).to_data(), key="-BELL-"),
        ],
    ]

    # ttk buttons, because `hover` above is a state a tk.Button does not have
    # — asking for it there warns, correctly, and the page says why.
    window = sg.Window("PySimpleGUI", layout, finalize=True, size=(420, 190),
                       use_ttk_buttons=True,
                       icon=BootstrapIcon("gear", 32, text).to_data())
    # The disabled state is half of what the Delete button demonstrates, so
    # show it rather than describing it in the caption.
    window["-DELETE-"].update(disabled=True)
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
