# LANShare

A lightweight peer-to-peer file transfer tool for local networks, built with Python and Tkinter. Send files directly between two computers on the same LAN — no internet, no cloud, no size limits beyond your disk.

## Features

- **Direct P2P transfer** over raw TCP sockets — no server or account required
- **Simple GUI** for sending and receiving, built with Tkinter
- **Live progress bar** during transfers
- **SHA-256 checksum verification** on every transfer to detect corruption
- **Safe file handling** — sanitizes incoming filenames (prevents path traversal) and auto-renames on collisions instead of overwriting
- **Transfer history** logged to a local SQLite database
- **Persistent logging** (`lanshare.log`) for diagnosing failed transfers, even when run without a console window
- **Non-blocking** — transfers run on background threads so the GUI stays responsive
- **Concurrent receiving** — the receiver can accept multiple incoming connections without blocking

## How it works

1. On the receiving machine, open the app and click **Receive File** → **Start Receiver**. It starts listening on port `5000`.
2. On the sending machine, click **Send File**, browse to a file, enter the receiver's LAN IP address, and click **Send**.
3. The sender computes a SHA-256 checksum, sends the filename/size/checksum as metadata, then streams the file in 1MB chunks.
4. The receiver verifies the checksum after the full file arrives and logs the result.

## Project Structure

```
LANShare/
├── client/
│   ├── sender.py        # Sends a file to a receiver over TCP
│   └── receiver.py       # Thin wrapper re-exporting the server module
├── server/
│   └── socket_server.py  # Core socket accept/receive logic, checksum verification
├── gui/
│   ├── main.py            # Main app window
│   ├── send_page.py       # Send File window
│   ├── receive_page.py    # Receive File window
│   └── progress.py        # Progress bar widget
├── utils/
│   ├── config.py          # Network/port/buffer settings
│   ├── checksum.py        # SHA-256 helpers
│   ├── logger.py          # Persistent log file writer
│   ├── compressor.py       # (optional) compression helpers
│   ├── encryption.py       # (optional) AES helpers
│   └── discovery.py        # (optional) LAN discovery helpers
├── database/
│   └── db.py               # SQLite transfer history
├── run.py                  # Entry point
└── requirements.txt
```

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt` (`tqdm`, `pycryptodome`)

## Installation

```bash
git clone https://github.com/Mukeshburdak/LANShare.git
cd LANShare
pip install -r requirements.txt
```

## Usage

```bash
python run.py
```

Run this on both the sending and receiving machine. Make sure both devices are on the same local network, and that your firewall allows the app through (you'll typically get a Windows Firewall prompt the first time you start the receiver — allow it).

## Roadmap / Ideas

- [ ] Wire in AES encryption for the actual file transfer (currently unused, and the default mode needs hardening before use)
- [ ] Wire in zip compression before sending
- [ ] Auto-discovery of receivers on the LAN (`utils/discovery.py` groundwork already exists)
- [ ] Multi-file / folder transfers
- [ ] Cross-platform packaged executables

## License

MIT