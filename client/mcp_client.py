"""MCPClient: connects to an MCP server over STDIO and exposes its primitives.

Connection flow:
    StdioServerParameters -> stdio_client (launches the server subprocess)
    -> ClientSession (JSON-RPC over stdin/stdout) -> initialize() (handshake)
"""

import sys
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_LOG = PROJECT_ROOT / "server.log"


def server_params(server_script: str | None = None) -> StdioServerParameters:
    """Describe how to launch the server.

    With no script, runs the bundled server (`python -m server`). Otherwise
    runs the given Python file. `sys.executable` keeps the same virtualenv.
    """
    args = [server_script] if server_script else ["-m", "server"]
    return StdioServerParameters(command=sys.executable, args=args, cwd=PROJECT_ROOT)


class MCPClient:
    """Thin wrapper around an MCP ClientSession.

    Use it as an async context manager so the session and the server
    subprocess are always closed, even on errors.
    """

    def __init__(self) -> None:
        self._exit_stack = AsyncExitStack()
        self._session: ClientSession | None = None
        self.history: list[tuple[str, str]] = []  # successful (operation, name)

    # --- lifecycle ---------------------------------------------------------

    async def connect(self, params: StdioServerParameters) -> None:
        """Launch the server, open a session and run the MCP handshake.

        The server's stderr (banner, logs, tracebacks) goes to server.log so it
        doesn't mix with the CLI output. stdout is reserved for JSON-RPC.
        """
        errlog = self._exit_stack.enter_context(SERVER_LOG.open("w", encoding="utf-8"))
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(params, errlog=errlog)
        )
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._session.initialize()

    async def close(self) -> None:
        """Close the session and stop the server subprocess."""
        await self._exit_stack.aclose()

    async def __aenter__(self) -> "MCPClient":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._session

    # --- tools (actions) ---------------------------------------------------

    async def list_tools(self) -> list[types.Tool]:
        return (await self.session.list_tools()).tools

    async def call_tool(self, name: str, arguments: dict) -> types.CallToolResult:
        result = await self.session.call_tool(name, arguments)
        if not result.isError:  # tool failures come back as results, not exceptions
            self.history.append(("tool", name))
        return result

    # --- resources (data) --------------------------------------------------

    async def list_resource_templates(self) -> list[types.ResourceTemplate]:
        return (await self.session.list_resource_templates()).resourceTemplates

    async def read_resource(self, uri: str) -> types.ReadResourceResult:
        result = await self.session.read_resource(uri)
        self.history.append(("resource", uri))
        return result

    # --- prompts (LLM guidance) --------------------------------------------

    async def list_prompts(self) -> list[types.Prompt]:
        return (await self.session.list_prompts()).prompts

    async def get_prompt(self, name: str, arguments: dict) -> types.GetPromptResult:
        result = await self.session.get_prompt(name, arguments)
        self.history.append(("prompt", name))
        return result
