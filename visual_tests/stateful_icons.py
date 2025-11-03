import ttkbootstrap as tb
from ttkbootstrap_icons import BootstrapIcon

app = tb.Window("Stateful Icons Demo", themename="flatly")

theme = tb.StringVar(value="flatly")

def toggle_theme():
    global theme
    if theme.get() == "flatly":
        app.style.theme_use("darkly")
        theme.set("darkly")
    else:
        app.style.theme_use("flatly")

        theme.set("flatly")

frm = tb.Frame(app, padding=16)
frm.pack(fill='both', expand=True)

lf1 = tb.Labelframe(frm, text="Standard Buttons with stateful icon", padding=16)
lf1.pack(side='top', fill='x', pady=(16, 8))

btn = tb.Button(lf1, text="Bookmark", compound="right", bootstyle="link")
btn.pack(side='left', padx=16)
BootstrapIcon("bookmark-fill", size=16).map(btn)

btn = tb.Button(lf1, text="Add to cart", compound="right")
btn.pack(side='left')
BootstrapIcon("cart-plus-fill", size=16).map(btn)

btn = tb.Button(lf1, text="Settings", compound="left", bootstyle="outline")
btn.pack(side='left', padx=16)
BootstrapIcon("gear-fill", size=24).map(btn)

btn = tb.Button(lf1, text="Settings", compound="right", state="disabled")
btn.pack(side='left', padx=16)
BootstrapIcon("gear-fill", size=16).map(btn)

lf2 = tb.Labelframe(frm, text="Stateful Icon-Only buttons", padding=16)
lf2.pack(side='top', fill='x', pady=8)

btn = tb.Button(lf2, bootstyle="link", compound="image")
btn.pack(side='left', padx=16)
BootstrapIcon("bookmark-fill").map(btn)

btn = tb.Button(lf2, compound="image")
btn.pack(side='left')
BootstrapIcon("power").map(btn)

btn = tb.Button(lf2, bootstyle="outline", compound="image")
btn.pack(side='left', padx=16)
BootstrapIcon("bluetooth").map(btn)

btn = tb.Button(lf2, state="disabled", compound="image")
btn.pack(side='left', padx=16)
BootstrapIcon("bell-fill").map(btn)

lf3 = tb.Labelframe(frm, text="Stateful toggle buttons", padding=16)
lf3.pack(side='top', fill='x', pady=8)

btn = tb.Checkbutton(lf3, bootstyle="label", text="Bookmark")
btn.pack(side='left', padx=16)
BootstrapIcon("bookmark").map(btn, statespec=[("selected", {"name": "bookmark-fill", "color": "red"})])

btn = tb.Checkbutton(lf3, text="Microphone", bootstyle="success-label")
btn.pack(side='left')
BootstrapIcon("mic-mute-fill").map(btn, statespec=[("selected", {"name": "mic-fill"})])

btn = tb.Checkbutton(lf3, bootstyle="info-label", compound="image")
btn.pack(side='left', padx=16)
BootstrapIcon("chevron-down").map(btn, statespec=[("selected", {"name": "chevron-right"})])

btn = tb.Checkbutton(lf3, bootstyle="outline-toolbutton", textvariable=theme, command=toggle_theme)
btn.pack(side='left', padx=16)
BootstrapIcon("sun").map(btn, statespec=[
    ("hover !selected", {"name": "sun"}),
    ("hover selected", {"name": "moon"}),
    ("selected", {"name": "moon"})
])

btn = tb.Checkbutton(lf3, bootstyle="label", text="Custom Switch")
btn.pack(side='left', padx=16)
BootstrapIcon("circle").map(btn, statespec=[
    ("selected", {"name": "check-circle-fill"}),
])


app.mainloop()