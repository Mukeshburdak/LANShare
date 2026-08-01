import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import threading

from client.sender import send_file
from gui.progress import ProgressWindow

PLACEHOLDER = "Receiver IP Address"


def browse():
    filename = filedialog.askopenfilename()

    if filename:
        path.delete(0, tk.END)
        path.insert(0, filename)


def clear_placeholder(event):
    if receiver_ip.get() == PLACEHOLDER:
        receiver_ip.delete(0, tk.END)


def send():
    file = path.get()
    ip = receiver_ip.get()

    if file == "" or ip == "" or ip == PLACEHOLDER:
        messagebox.showerror(
            "Error",
            "Select a file and enter the receiver's IP address."
        )
        return

    send_btn.config(state="disabled")
    progress_win = ProgressWindow()
    progress_win.window.title("Sending...")

    last_percent = [-1]

    def on_progress(sent, total):
        percent = (sent / total) * 100 if total else 0
        if int(percent) == last_percent[0] and sent < total:
            return
        last_percent[0] = int(percent)
        window.after(0, progress_win.update, percent)

    def worker():
        try:
            send_file(file, ip, progress_callback=on_progress)
            window.after(0, lambda: messagebox.showinfo(
                "Success", "File sent successfully."
            ))
        except Exception as e:
            error_message = str(e)
            window.after(0, lambda: messagebox.showerror("Error", error_message))
        finally:
            window.after(0, progress_win.close)
            window.after(0, lambda: send_btn.config(state="normal"))

    threading.Thread(target=worker, daemon=True).start()


def open_send_window():

    global path
    global receiver_ip
    global window
    global send_btn

    window = tk.Toplevel()

    window.title("Send File")

    window.geometry("500x200")

    receiver_ip = tk.Entry(window, width=40)
    receiver_ip.pack(pady=10)
    receiver_ip.insert(0, PLACEHOLDER)
    receiver_ip.bind("<FocusIn>", clear_placeholder)

    path = tk.Entry(window, width=40)
    path.pack()

    browse_btn = tk.Button(
        window,
        text="Browse",
        command=browse
    )

    browse_btn.pack(pady=5)

    send_btn = tk.Button(
        window,
        text="Send",
        command=send
    )

    send_btn.pack(pady=10)
