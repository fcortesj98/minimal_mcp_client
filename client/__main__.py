"""Entry point: `python -m client [server_script.py]`.

Without an argument the client launches the bundled server (`python -m server`).
"""

import argparse
import asyncio

from client.cli import run_repl
from client.mcp_client import MCPClient, server_params


async def main(server_script: str | None) -> None:
    async with MCPClient() as client:
        await client.connect(server_params(server_script))
        print("✓ Connected to MCP server (server logs: server.log)")
        await run_repl(client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minimal interactive MCP client.")
    parser.add_argument(
        "server_script",
        nargs="?",
        help="Python file of an MCP server to launch (default: the bundled server)",
    )
    try:
        asyncio.run(main(parser.parse_args().server_script))
    except KeyboardInterrupt:
        print("\nExiting...")
