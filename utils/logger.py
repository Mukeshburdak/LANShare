import os
import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lanshare.log")


def log_line(message):
    """Append a timestamped line to lanshare.log so nothing gets lost,
    even when the app is launched without a visible console (e.g. via
    a double-clicked .pyw/.exe or pythonw)."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # logging should never crash a transfer
