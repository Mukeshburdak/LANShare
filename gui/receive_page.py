import tkinter as tk
from tkinter import scrolledtext
import threading
import datetime

from client.receiver import start_server
from gui.progress import ProgressWindow

stop_event = None
progress_win = None
_last_percent = -1


def append_log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_box.config(state="normal")
    log_box.insert(tk.END, f"[{timestamp}] {message}\n")
    log_box.see(tk.END)
    log_box.config(state="disabled")


def start():
    global stop_event, _last_percent

    if stop_event is not None:
        # Server already running for this window.
        return

    stop_event = threading.Event()
    _last_percent = -1
    append_log("Starting receiver...")
    start_btn.config(state="disabled")

    def on_status(message):
        window.after(0, append_log, message)

    def on_progress(received, total):
        global progress_win, _last_percent

        percent = (received / total) * 100 if total else 0

        # Only schedule a GUI update when the percentage actually moves,
        # instead of once per chunk (which can be thousands of times for
        # a large file and floods Tkinter's event queue).
        if progress_win is not None and int(percent) == _last_percent and received < total:
            return
        _last_percent = int(percent)

        def update():
            global progress_win
            if progress_win is None:
                progress_win = ProgressWindow()
                progress_win.window.title("Receiving...")
            progress_win.update(percent)
            if received >= total and progress_win is not None:
                progress_win.close()
                progress_win = None

        window.after(0, update)

    def worker():
        start_server(
            status_callback=on_status,
            progress_callback=on_progress,
            stop_event=stop_event
        )

    threading.Thread(target=worker, daemon=True).start()


def open_receive_window():

    global window
    global log_box
    global start_btn
    global stop_event

    stop_event = None

    window = tk.Toplevel()

    window.title("Receiver")

    window.geometry("420x260")

    start_btn = tk.Button(
        window,
        text="Start Receiver",
        command=start
    )

    start_btn.pack(pady=8)

    log_box = scrolledtext.ScrolledText(
        window,
        height=10,
        state="disabled",
        wrap="word"
    )
    log_box.pack(fill="both", expand=True, padx=8, pady=8)

    append_log("Waiting for Sender...")

    def on_close():
        global stop_event
        if stop_event is not None:
            stop_event.set()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)
