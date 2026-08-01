import socket
import os
import struct
import traceback
from tqdm import tqdm

from utils.config import PORT, BUFFER_SIZE
from utils.checksum import calculate_checksum
from utils.logger import log_line

try:
    from database.db import add_history
except Exception:
    def add_history(*args, **kwargs):
        pass


def send_file(file_path, server_ip, port=PORT, progress_callback=None):
    """
    Send a file to a receiver listening at server_ip:port.

    progress_callback(bytes_sent, total_bytes), if provided, is called
    after every chunk so a GUI can render live progress.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    sent = 0

    print("Calculating checksum...")
    checksum = calculate_checksum(file_path)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("Connecting to receiver...")
        client.connect((server_ip, port))
        print("Connected!")
        log_line(f"Connected to {server_ip}:{port}, sending '{filename}' ({filesize} bytes)")

        # ----------------------------
        # Send Metadata
        # ----------------------------
        filename_bytes = filename.encode("utf-8")

        client.sendall(struct.pack("!I", len(filename_bytes)))  # filename length
        client.sendall(filename_bytes)                          # filename
        client.sendall(struct.pack("!Q", filesize))              # filesize
        client.sendall(checksum.encode("ascii"))                 # sha256 checksum (64 chars)

        print(f"Sending: {filename}")
        print(f"Size: {filesize / (1024 * 1024):.2f} MB")

        progress = tqdm(
            total=filesize,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        )

        # ----------------------------
        # Send File
        # ----------------------------
        with open(file_path, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break

                client.sendall(data)
                sent += len(data)
                progress.update(len(data))

                if progress_callback:
                    progress_callback(sent, filesize)

        progress.close()
        print("\nTransfer Completed Successfully!")
        log_line(f"Sent '{filename}' successfully ({sent} bytes) to {server_ip}:{port}")

        add_history(filename, filesize, socket.gethostname(), server_ip, "SUCCESS")

    except Exception as e:
        error_type = type(e).__name__
        log_line(
            f"ERROR sending '{filename}' to {server_ip}:{port}: {error_type}: {e} "
            f"(sent {sent} of {filesize} bytes)"
        )
        log_line(traceback.format_exc())
        add_history(filename, filesize, socket.gethostname(), server_ip, "FAILED")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    path = input("Enter file path: ").strip()
    ip = input("Enter receiver IP: ").strip()
    send_file(path, ip)
