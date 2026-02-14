# BeroChat

A multi-user chat application built with Python. Supports public group chat and private messaging with both GUI (CustomTkinter) and CLI interfaces.

## Features

- **Public & Private Messaging** - Group chat and direct messages
- **Real-time Updates** - Live user list and message delivery
- **Dual Clients** - Modern GUI or lightweight CLI
- **Custom Protocol** - TCP-based with message serialization
- **Multi-threaded Server** - Handles concurrent connections

## Quick Start

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run server:**
```bash
python src/server/server.py
```

**Run client (choose one):**
```bash
# GUI version
python src/client_ui/client.py

# CLI version  
python src/client_cli/client.py
```

## Tech Stack

- Python 3.8+
- Socket programming (TCP)
- Threading for concurrency
- CustomTkinter for UI
- Pickle for serialization

## Architecture

- **Server** - Single-threaded accept loop, multi-threaded client handlers, in-memory message storage
- **Clients** - Separate send/receive threads, custom protocol parsing

## Protocol

3-part message format:
1. Length header (128 bytes)
2. Metadata string (message type + info)
3. Pickled message content

See [PROTOCOL.md](docs/PROTOCOL.md) for details.