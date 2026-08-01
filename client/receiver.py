"""
Backward-compatible entry point for the receiver.

The actual socket-accept / file-write logic lives in
server/socket_server.py. This module just re-exports start_server so
other parts of the app (e.g. gui/receive_page.py) can keep importing
from client.receiver unchanged.
"""

from server.socket_server import start_server, handle_client, safe_filename

if __name__ == "__main__":
    start_server(status_callback=print)
