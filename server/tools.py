"""MCP tools: actions the client can invoke with arguments.

FastMCP builds each tool's JSON schema from the type hints and uses the
docstring as its description.
"""

from fastmcp import FastMCP

from server.config import PROJECT_ROOT, safe_path


def echo(text: str) -> str:
    """Echo back the input text."""
    return f"Echo: {text}"


def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    file_path = safe_path(PROJECT_ROOT, path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Successfully wrote to {path}"


def register(mcp: FastMCP) -> None:
    """Register every tool in this module on the server."""
    mcp.tool(echo)
    mcp.tool(write_file)
