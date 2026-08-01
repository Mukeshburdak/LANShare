import socket
import threading

DISCOVERY_PORT = 5001
MESSAGE = "LANSHARE_DISCOVERY"


def discovery_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("", DISCOVERY_PORT))

    while True:
        data, addr = server.recvfrom(1024)

        if data.decode() == MESSAGE:
            server.sendto(socket.gethostname().encode(), addr)


def start_discovery_server():
    thread = threading.Thread(target=discovery_server, daemon=True)
    thread.start()


def discover_devices():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.settimeout(2)

    client.sendto(MESSAGE.encode(), ("<broadcast>", DISCOVERY_PORT))

    devices = []

    while True:
        try:
            data, addr = client.recvfrom(1024)
            devices.append((data.decode(), addr[0]))
        except socket.timeout:
            break

    return devices