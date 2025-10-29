# Test and validate the provider icon styles

import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon

app = tk.Tk()


# outline style
outline_frame = ttk.LabelFrame(app, text="outline")
outline_frame.pack(padx=10, pady=10, fill='x', expand=True)

# --- default
a1 = BootstrapIcon("house")
ttk.Label(outline_frame, image=a1.image, compound="left", text="default").pack(padx=10, pady=10, side='left')

# --- style in name (this fails because it is not valid.. but it should
a2 = BootstrapIcon("house-outline")
ttk.Label(outline_frame, image=a2.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

# --- style as property
a3 = BootstrapIcon("house", style="outline")
ttk.Label(outline_frame, image=a3.image, compound="left", text="style as property").pack(padx=10, pady=10, side='left')

# fill style
fill_frame = ttk.LabelFrame(app, text="fill")
fill_frame.pack(padx=10, pady=10, fill='x', expand=True)

# --- style in name (this fails because it is not valid.. but it should
a2 = BootstrapIcon("house-fill")
ttk.Label(fill_frame, image=a2.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

# --- style as property
a3 = BootstrapIcon("house", style="fill")
ttk.Label(fill_frame, image=a3.image, compound="left", text="style as property").pack(padx=10, pady=10, side='left')

app.mainloop()
