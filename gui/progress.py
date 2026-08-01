import tkinter as tk
from tkinter.ttk import Progressbar


class ProgressWindow:

    def __init__(self):

        self.window = tk.Toplevel()

        self.window.title("Transfer Progress")

        self.bar = Progressbar(
            self.window,
            orient="horizontal",
            length=300,
            mode="determinate"
        )

        self.bar.pack(pady=20)

        self.label = tk.Label(
            self.window,
            text="0 %"
        )

        self.label.pack()

    def update(self, value):

        self.bar["value"] = value

        self.label.config(
            text=f"{value:.2f}%"
        )

    def close(self):

        self.window.destroy()
