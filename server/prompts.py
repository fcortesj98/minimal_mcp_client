"""MCP prompts: reusable templates the client renders with arguments.

The rendered text is meant to be sent to an LLM; this lab only displays it.
"""

from fastmcp import FastMCP


def review_file(filename: str) -> str:
    """Generate a prompt to review a file's contents."""
    return f"""Please review the file '{filename}' and provide:

1. A summary of its contents
2. Key points or sections
3. Any suggestions for improvement
4. Overall quality assessment

Use the appropriate tools to read the file if needed."""


def register(mcp: FastMCP) -> None:
    """Register every prompt in this module on the server."""
    mcp.prompt(review_file)
