import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_devicon import DevIcon

app = tk.Tk()

# plain style
p_frame = ttk.LabelFrame(app, text="plain")
p_frame.pack(padx=10, pady=10, fill='x', expand=True)

a_plain = DevIcon("apple", color="red")
ttk.Label(p_frame, image=a_plain.image, compound="left", text="default").pack(padx=10, pady=10, side='left')

a2_plain = DevIcon("apple-plain", color="green")
ttk.Label(p_frame, image=a2_plain.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

a3_plain = DevIcon("apple", style="plain", color="blue")
ttk.Label(p_frame, image=a3_plain.image, compound="left", text="style as param").pack(padx=10, pady=10, side='left')

# plain-wordmark style
pw_frame = ttk.LabelFrame(app, text="plain-wordmark")
pw_frame.pack(padx=10, pady=10, fill='x', expand=True)

a2_plain = DevIcon("android-plain-wordmark", color="green")
ttk.Label(pw_frame, image=a2_plain.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

a3_plain = DevIcon("android", style="plain-wordmark", color="blue")
ttk.Label(pw_frame, image=a3_plain.image, compound="left", text="style as param").pack(padx=10, pady=10, side='left')

# original style
o_frame = ttk.LabelFrame(app, text="original")
o_frame.pack(padx=10, pady=10, fill='x', expand=True)

a2_plain = DevIcon("carbon-original", color="green")
ttk.Label(o_frame, image=a2_plain.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

a3_plain = DevIcon("carbon", style="original", color="blue")
ttk.Label(o_frame, image=a3_plain.image, compound="left", text="style as param").pack(padx=10, pady=10, side='left')

# original wordmark style
ow_frame = ttk.LabelFrame(app, text="original-workmark")
ow_frame.pack(padx=10, pady=10, fill='x', expand=True)

a2_plain = DevIcon("coffeescript-original-wordmark", color="green")
ttk.Label(ow_frame, image=a2_plain.image, compound="left", text="style in name").pack(padx=10, pady=10, side='left')

a3_plain = DevIcon("coffeescript", style="original-wordmark", color="blue")
ttk.Label(ow_frame, image=a3_plain.image, compound="left", text="style as param").pack(padx=10, pady=10, side='left')

app.mainloop()
