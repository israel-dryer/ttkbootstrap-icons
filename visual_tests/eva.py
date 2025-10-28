import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_eva import EvaIcon

app = tk.Tk()

# outline style
p_frame = ttk.LabelFrame(app, text="fill")
p_frame.pack(padx=10, pady=10, fill='x', expand=True)

a_plain = EvaIcon("archive")
ttk.Label(p_frame, image=a_plain.image, compound="left", text="default").pack(padx=10, pady=10, side='left')

a2_plain = EvaIcon("archive-fill")
ttk.Label(p_frame, image=a2_plain.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

a3_plain = EvaIcon("archive", style="fill")
ttk.Label(p_frame, image=a3_plain.image, compound="left", text="style as param").pack(padx=10, pady=10, side='left')

# fill style
pw_frame = ttk.LabelFrame(app, text="outline")
pw_frame.pack(padx=10, pady=10, fill='x', expand=True)

a4_plain = EvaIcon("archive-outline")
ttk.Label(pw_frame, image=a4_plain.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

a5_plain = EvaIcon("archive", style="outline")
ttk.Label(pw_frame, image=a5_plain.image, compound="left", text="style as param").pack(padx=10, pady=10, side='left')

app.mainloop()
