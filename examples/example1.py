import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon

root = tb.Window()

solid = FAIcon("atom", style="solid")
regular = FAIcon("calendar", style="regular")
brand = FAIcon("github", style="brands")

b1 = tb.Button(root, text="Solid", compound="left")
b1.pack(padx=10, pady=10)
solid.map(b1)

b2 = tb.Button(root, text="Regular", compound="left")
b2.pack(padx=10, pady=10)
regular.map(b2)

b3 = tb.Button(root, text="Brand", compound="left")
b3.pack(padx=10, pady=10)
brand.map(b3)

root.mainloop()