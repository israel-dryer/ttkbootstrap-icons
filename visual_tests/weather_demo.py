import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_weather import WeatherIcon


def main():
    root = tk.Tk()
    root.title("Weather Icons Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = WeatherIcon("day-sunny", size=64, color="#ffbf00")
    ttk.Label(root, text="day-sunny", image=i0.image, compound="left").pack(**opts)

    i1 = WeatherIcon("cloud", size=64, color="#748ffc")
    ttk.Label(root, text="cloud", image=i1.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

