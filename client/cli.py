"""Interactive command loop for MCPClient.

Each command is a small async function registered in COMMANDS. The help text
and the banner are generated from that table, so adding a command is one
function plus one line.
"""

import json
from collections.abc import Awaitable, Callable

from client.mcp_client import MCPClient

# --- input / output helpers -------------------------------------------------


def ask(label: str) -> str:
    return input(f"  {label}: ").strip()


def ask_json(label: str) -> dict:
    """Read a JSON object from the user. An empty line means no arguments."""
    raw = ask(f'{label} as JSON, e.g. {{"text": "hello"}}')
    return json.loads(raw) if raw else {}


def text_of(content) -> str:
    """Return the text of an MCP content block (text, image, ...)."""
    return getattr(content, "text", None) or f"<{content.type} content>"


# --- tools ------------------------------------------------------------------


async def cmd_tools(client: MCPClient) -> None:
    for tool in await client.list_tools():
        args = ", ".join(tool.inputSchema.get("properties", {}))
        print(f"  • {tool.name}: {tool.description} (args: {args or 'none'})")


async def cmd_call(client: MCPClient) -> None:
    name = ask("Tool name")
    result = await client.call_tool(name, ask_json("Arguments"))
    label = "Tool error" if result.isError else "Result"
    for content in result.content:
        print(f"  {label}: {text_of(content)}")


# --- resources --------------------------------------------------------------


async def cmd_resources(client: MCPClient) -> None:
    templates = await client.list_resource_templates()
    if not templates:
        print("  No resources available")
    for template in templates:
        print(f"  • {template.name}")
        print(f"    URI template: {template.uriTemplate}")


async def cmd_read(client: MCPClient) -> None:
    result = await client.read_resource(ask("URI"))
    for content in result.contents:
        print(f"\n{text_of(content)}")


# --- prompts ----------------------------------------------------------------


async def cmd_prompts(client: MCPClient) -> None:
    for prompt in await client.list_prompts():
        args = ", ".join(arg.name for arg in prompt.arguments or [])
        print(f"  • {prompt.name}: {prompt.description} (args: {args or 'none'})")


async def cmd_prompt(client: MCPClient) -> None:
    name = ask("Prompt name")
    result = await client.get_prompt(name, ask_json("Arguments"))
    print(f"\n--- Prompt: {result.description} ---")
    for message in result.messages:
        print(f"{message.role}: {text_of(message.content)}")


# --- utilities --------------------------------------------------------------


async def cmd_history(client: MCPClient) -> None:
    if not client.history:
        print("  No operations yet")
    for i, (operation, name) in enumerate(client.history, 1):
        print(f"  {i}. {operation}: {name}")


async def cmd_help(client: MCPClient) -> None:
    print("\n  Available commands:")
    for name, (description, _) in COMMANDS.items():
        print(f"    {name:<10} {description}")
    print(f"    {'quit':<10} Exit the client\n")


Command = Callable[[MCPClient], Awaitable[None]]

COMMANDS: dict[str, tuple[str, Command]] = {
    "tools": ("List available tools", cmd_tools),
    "call": ("Invoke a tool", cmd_call),
    "resources": ("List resource templates", cmd_resources),
    "read": ("Read a resource by URI", cmd_read),
    "prompts": ("List prompt templates", cmd_prompts),
    "prompt": ("Get a rendered prompt", cmd_prompt),
    "history": ("Show operations run this session", cmd_history),
    "help": ("Show this help message", cmd_help),
}

# --- main loop --------------------------------------------------------------


async def run_repl(client: MCPClient) -> None:
    """Read commands until the user types quit (or presses Ctrl+C / Ctrl+D)."""
    print("\n=== MCP Client ===")
    print("Commands: " + " | ".join([*COMMANDS, "quit"]) + "\n")

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd in ("quit", "exit"):
            break
        if not cmd:
            continue
        if cmd not in COMMANDS:
            print("  Unknown command (type 'help')")
            continue

        _, handler = COMMANDS[cmd]
        try:
            await handler(client)
        except json.JSONDecodeError:
            print("  Error: Invalid JSON format")
            print('  Hint: Use double quotes, e.g. {"text": "hello"}')
        except Exception as e:
            print(f"  Error: {e}")
            if "not found" in str(e).lower():
                print("  Hint: Check the tool/prompt name or the resource URI")
