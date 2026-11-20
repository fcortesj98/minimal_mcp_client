"""MCP resources: read-only data the client fetches by URI.

`file://resources/{filename}` is a resource *template*: one definition exposes
every file in the resources/ folder. When the client asks for
`file://resources/notes.txt`, FastMCP extracts filename="notes.txt" and calls
`read_resource_file("notes.txt")`.
"""

from fastmcp import FastMCP

from server.config import RESOURCES_DIR, safe_path

RESOURCE_TEMPLATE = "file://resources/{filename}"


def read_resource_file(filename: str) -> str:
    """Read a file from the resources directory."""
    file_path = safe_path(RESOURCES_DIR, filename)
    if not file_path.is_file():
        return f"File not found: {filename}"
    return file_path.read_text(encoding="utf-8")


def register(mcp: FastMCP) -> None:
    """Register every resource in this module on the server."""
    mcp.resource(RESOURCE_TEMPLATE)(read_resource_file)
