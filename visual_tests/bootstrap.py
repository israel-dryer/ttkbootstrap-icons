import tkinter as tk
from tkinter import ttk
from ttkbootstrap_icons import BootstrapIcon

app = tk.Tk()

# plain style
p_frame = ttk.LabelFrame(app, text="normal")
p_frame.pack(padx=10, pady=10, fill='x', expand=True)

a_plain = BootstrapIcon("house", color="red")
ttk.Label(p_frame, image=a_plain.image, compound="left").pack(padx=10, pady=10, side='left')

a2_plain = BootstrapIcon("house-fill", color="green")
ttk.Label(p_frame, image=a2_plain.image, compound="image").pack(padx=10, pady=10, side='left')

app.mainloop()