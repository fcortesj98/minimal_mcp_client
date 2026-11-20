"""Entry point: `python -m server` starts the server on STDIO (FastMCP's default)."""

from server.app import create_server

if __name__ == "__main__":
    create_server().run()
