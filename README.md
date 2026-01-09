# Ghost Game - Python Client/Server

## Installation

1. Install Python 3.10+
2. Install uv (if not already installed):
   ```bash
   pip install uv
   # Or via script:
   # curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Install dependencies:
   ```bash
   uv sync
   # Or manually:
   uv add "flet[all]"
   ```

## Usage

### Server
Run the server first. It will start the TCP server on port 5000 and the Admin Dashboard.
```bash
python3 server/main.py
```

### Client
Run the client (you can run multiple instances).
```bash
python3 client/main.py
```
