"""Builds the FastMCP server and registers all primitives on it."""

import logging

from fastmcp import FastMCP

from server import prompts, resources, tools
from server.config import SERVER_NAME


def create_server() -> FastMCP:
    """Create the server with its tools, resources and prompts."""
    # Keep FastMCP's INFO logs out of the way of the client's output.
    logging.getLogger("fastmcp").setLevel(logging.WARNING)

    mcp = FastMCP(SERVER_NAME)
    tools.register(mcp)
    resources.register(mcp)
    prompts.register(mcp)
    return mcp
