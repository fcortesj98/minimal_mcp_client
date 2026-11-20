# Minimal MCP Client-Server Example

A minimal client–server pair built with the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). A small **FastMCP server** exposes one example of each MCP primitive, and an interactive **Python client** connects to it over STDIO so you can see how a client discovers and uses them:

| Primitive | What it is | Example in this project |
|-----------|------------|-------------------------|
| **Tools** | Actions the client can invoke | `echo`, `write_file` |
| **Resources** | Data the client reads by URI | `file://resources/{filename}` (a template that serves any file in `resources/`) |
| **Prompts** | Reusable templates for LLM instructions | `review_file` |

The client starts the server as a subprocess and talks JSON-RPC over the server's stdin/stdout. No network setup is needed.

## Project structure

```
mcp_client_lab/
├── server/                 # FastMCP server
│   ├── __main__.py         # entry point: python -m server
│   ├── app.py              # creates the server and registers everything
│   ├── config.py           # server name, paths, safe-path helper
│   ├── tools.py            # echo, write_file
│   ├── resources.py        # file://resources/{filename}
│   └── prompts.py          # review_file
├── client/                 # MCP client
│   ├── __main__.py         # entry point: python -m client
│   ├── mcp_client.py       # MCPClient: STDIO connection + one method per MCP operation
│   └── cli.py              # interactive command loop
├── resources/              # files exposed as MCP resources
└── requirements.txt
```

To add a primitive, write a function in the matching server module and add it to that module's `register()` function. To add a client command, write a `cmd_*` function in `client/cli.py` and add one line to `COMMANDS`.

## Setup

Requires Python 3.10+ (the lab uses 3.11).

```bash
python3.11 -m venv mcp_client_env
source mcp_client_env/bin/activate        # Windows: mcp_client_env\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the following from the project folder:

```bash
python -m client
```

The client launches the bundled server automatically. To connect to a different server script, pass its path: `python -m client path/to/other_server.py`.

```
✓ Connected to MCP server (server logs: server.log)

=== MCP Client ===
Commands: tools | call | resources | read | prompts | prompt | history | help | quit
```

| Command | What it does |
|---------|--------------|
| `tools` | List the server's tools and their arguments |
| `call` | Invoke a tool (asks for the name and a JSON object of arguments) |
| `resources` | List resource templates |
| `read` | Read a resource by URI |
| `prompts` | List prompt templates and their arguments |
| `prompt` | Render a prompt template with arguments |
| `history` | Show the operations that succeeded this session |
| `help` / `quit` | Show help / exit (Ctrl+C and Ctrl+D also exit) |

### Example session

```
> call
  Tool name: echo
  Arguments as JSON, e.g. {"text": "hello"}: {"text": "Hello MCP!"}
  Result: Echo: Hello MCP!

> call
  Tool name: write_file
  Arguments as JSON, e.g. {"text": "hello"}: {"path": "test.txt", "content": "Hello from MCP client!"}
  Result: Successfully wrote to test.txt

> read
  URI: file://resources/project_info.txt

Project Name: MCP Client Lab
Version: 1.0.0
...

> prompt
  Prompt name: review_file
  Arguments as JSON, e.g. {"text": "hello"}: {"filename": "test.txt"}

--- Prompt: Generate a prompt to review a file's contents. ---
user: Please review the file 'test.txt' and provide:
...
```

Any file you drop into `resources/` can be read right away (for example, `file://resources/notes.txt`) without changing the server code. That is how the resource template works.

### Notes

- **Arguments must be valid JSON** with double quotes. Press Enter on an empty line to send no arguments.
- **File access is sandboxed.** `write_file` only writes inside the project folder, and resources are only read from `resources/`. Paths with `../` are rejected.
- **Server output goes to `server.log`.** The server's stdout carries the JSON-RPC messages, so its banner, logs and errors are written to `server.log` to keep the client's terminal clean. If something fails on the server side, check that file.

## Acknowledgements

Built as part of the IBM RAG and Agentic AI Professional Certificate, offered by IBM through Coursera. The certificate covers LangChain, LangGraph, RAG pipelines, vector databases, multimodal AI, and agentic frameworks such as CrewAI, AG2, BeeAI, and the Model Context Protocol. Model access is provided by IBM watsonx.ai.
