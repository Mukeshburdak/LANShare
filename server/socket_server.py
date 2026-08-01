"""
Core TCP socket server for LANShare.

Handles accepting incoming connections and receiving files, including
metadata parsing, checksum verification, and transfer history logging.
This module contains the canonical receive-side logic; client/receiver.py
re-exports it for backward compatibility with the rest of the app.
"""

import os
import socket
import struct
import threading
import traceback

from utils.config import HOST, PORT, BUFFER_SIZE, SAVE_FOLDER
from utils.checksum import calculate_checksum
from utils.logger import log_line

try:
    from database.db import add_history
except Exception:
    # Database is optional; server should still work without it.
    def add_history(*args, **kwargs):
        pass

CHECKSUM_LEN = 64  # length of a sha256 hex digest


def receive_exact(sock, size):
    """Receive exactly `size` bytes from the socket, or return None on EOF."""
    data = bytearray()
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)


def safe_filename(filename):
    """Strip any directory components to prevent path traversal attacks."""
    filename = os.path.basename(filename.replace("\\", "/"))
    return filename if filename else "unnamed_file"


def unique_path(save_dir, filename):
    """Return a path that doesn't collide with an existing file."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(save_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(save_dir, f"{base}({counter}){ext}")
        counter += 1
    return candidate


def handle_client(conn, addr, save_dir, progress_callback=None, status_callback=None):
    """Receive a single file from an already-accepted connection."""
    filename = None
    filesize = 0
    try:
        # ---- Metadata ----
        header = receive_exact(conn, 4)
        if header is None:
            return
        filename_length = struct.unpack("!I", header)[0]

        raw_name = receive_exact(conn, filename_length)
        if raw_name is None:
            return
        filename = safe_filename(raw_name.decode("utf-8", errors="replace"))

        size_data = receive_exact(conn, 8)
        if size_data is None:
            return
        filesize = struct.unpack("!Q", size_data)[0]

        checksum_data = receive_exact(conn, CHECKSUM_LEN)
        expected_checksum = checksum_data.decode("ascii") if checksum_data else None

        save_path = unique_path(save_dir, filename)

        if status_callback:
            status_callback(f"Receiving '{filename}' from {addr[0]}...")
        log_line(f"Receiving '{filename}' ({filesize} bytes) from {addr[0]}")

        # ---- File data ----
        received = 0
        with open(save_path, "wb") as f:
            while received < filesize:
                chunk = conn.recv(min(BUFFER_SIZE, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                if progress_callback:
                    progress_callback(received, filesize)

        if received != filesize:
            if status_callback:
                status_callback(f"Transfer of '{filename}' interrupted.")
            log_line(
                f"Transfer of '{filename}' interrupted: received {received} of "
                f"{filesize} bytes from {addr[0]}"
            )
            add_history(filename, filesize, addr[0], HOST, "FAILED")
            return

        # ---- Integrity check ----
        if expected_checksum:
            actual_checksum = calculate_checksum(save_path)
            if actual_checksum != expected_checksum:
                if status_callback:
                    status_callback(f"Checksum mismatch for '{filename}'!")
                log_line(f"Checksum mismatch for '{filename}' from {addr[0]}")
                add_history(filename, filesize, addr[0], HOST, "CHECKSUM_FAILED")
                return

        if status_callback:
            status_callback(f"Received '{filename}' successfully.")
        log_line(f"Received '{filename}' successfully ({filesize} bytes) from {addr[0]}")
        add_history(filename, filesize, addr[0], HOST, "SUCCESS")

    except Exception as e:
        error_type = type(e).__name__
        if status_callback:
            status_callback(f"Error receiving from {addr[0]}: {error_type}: {e}")
        log_line(f"ERROR receiving '{filename}' from {addr[0]}: {error_type}: {e}")
        log_line(traceback.format_exc())
        if filename:
            add_history(filename, filesize, addr[0], HOST, "ERROR")
    finally:
        conn.close()


def start_server(host=HOST, port=PORT, save_dir=SAVE_FOLDER,
                  progress_callback=None, status_callback=None,
                  stop_event=None):
    """
    Start listening for incoming file transfers.

    Each connection is handled on its own thread so multiple senders
    (or repeated transfers) don't block one another. Pass a
    threading.Event as stop_event to allow graceful shutdown.
    """
    os.makedirs(save_dir, exist_ok=True)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    server.settimeout(1.0)  # allows periodic stop_event checks

    if status_callback:
        status_callback(f"Listening on port {port}...")
    log_line(f"Server started, listening on {host}:{port}")

    try:
        while stop_event is None or not stop_event.is_set():
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue

            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, save_dir, progress_callback, status_callback),
                daemon=True
            )
            client_thread.start()
    finally:
        server.close()


if __name__ == "__main__":
    start_server(status_callback=print, progress_callback=lambda r, t: None)
