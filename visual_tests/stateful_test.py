import ttkbootstrap as tb
from ttkbootstrap_icons import BootstrapIcon


app = tb.Window()

btn = tb.Button(app, text="Click Me", bootstyle="outline")
BootstrapIcon("house").map(btn)
btn.pack()


btn = tb.Checkbutton(app, text="Click Me", bootstyle="outline-toolbutton")
BootstrapIcon("house").map(btn)
btn.pack()


app.mainloop()