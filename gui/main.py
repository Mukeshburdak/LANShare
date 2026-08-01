import tkinter as tk

from gui.send_page import open_send_window
from gui.receive_page import open_receive_window


root = tk.Tk()

root.title("LANShare")

root.geometry("400x250")

root.resizable(False, False)


title = tk.Label(
    root,
    text="LANShare",
    font=("Arial", 22, "bold")
)

title.pack(pady=20)


send_btn = tk.Button(
    root,
    text="Send File",
    width=20,
    height=2,
    command=open_send_window
)

send_btn.pack(pady=10)


receive_btn = tk.Button(
    root,
    text="Receive File",
    width=20,
    height=2,
    command=open_receive_window
)

receive_btn.pack()
