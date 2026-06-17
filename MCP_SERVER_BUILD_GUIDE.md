# How to Build an MCP Server — Complete Guide

A step-by-step guide on how the TaskPilot MCP Server was built, and how you can build your own MCP server for any application.

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Why Build an MCP Server?](#why-build-an-mcp-server)
3. [Prerequisites](#prerequisites)
4. [Step 1: Understand the MCP Architecture](#step-1-understand-the-mcp-architecture)
5. [Step 2: Set Up the Project](#step-2-set-up-the-project)
6. [Step 3: Define Your Tools](#step-3-define-your-tools)
7. [Step 4: Implement Tool Handlers](#step-4-implement-tool-handlers)
8. [Step 5: Add Resources (Optional)](#step-5-add-resources-optional)
9. [Step 6: Wire Up the Server Entry Point](#step-6-wire-up-the-server-entry-point)
10. [Step 7: Test Your Server](#step-7-test-your-server)
11. [Step 8: Configure in an MCP Client](#step-8-configure-in-an-mcp-client)
12. [Best Practices](#best-practices)
13. [Common Patterns](#common-patterns)
14. [Troubleshooting](#troubleshooting)

---

## What is MCP?

**Model Context Protocol (MCP)** is an open standard that lets AI assistants (like Kiro, Claude, Cursor) connect to external tools and data sources through a unified interface.

Think of it like USB for AI — one standard protocol, many different tools.

```
┌──────────────┐                    ┌──────────────────┐
│  AI Client   │  ← MCP Protocol → │  Your MCP Server │
│  (Kiro)      │   (JSON-RPC 2.0)  │  (Your App)      │
└──────────────┘                    └──────────────────┘
```

### MCP Concepts

| Concept | What It Is | Example |
|---------|-----------|---------|
| **Tools** | Actions the AI can perform | `create_task`, `send_email` |
| **Resources** | Data the AI can read | `taskpilot://tasks/all` |
| **Prompts** | Pre-built prompt templates | `summarize_tasks` |
| **Transport** | How client/server communicate | stdio, SSE, HTTP |

---

## Why Build an MCP Server?

- **Universal access**: Any MCP client can use your tools (not locked to one AI)
- **Separation of concerns**: Your app logic stays separate from AI integration
- **Composability**: Clients can combine multiple MCP servers
- **Standardized**: No custom API integration needed per client

---

## Prerequisites

- Python 3.10+
- `pip` package manager
- Basic understanding of async Python

Install the MCP SDK:

```bash
pip install mcp
```

---

## Step 1: Understand the MCP Architecture

An MCP server has three main components:

```
MCP Server
├── Tools       → Functions the AI can CALL (like API endpoints)
├── Resources   → Data the AI can READ (like GET endpoints)
└── Transport   → HOW the communication happens (stdio/SSE)
```

**Communication flow:**

```
1. Client connects to server (via stdio or network)
2. Client asks: "What tools do you have?" → server responds with tool list
3. Client calls a tool: "create_task with title='Buy milk'" → server executes
4. Server returns the result → client uses it in conversation
```

---

## Step 2: Set Up the Project

Create your project structure:

```
your_mcp_server/
├── __init__.py
├── server.py           # Main server file
└── requirements.txt    # Dependencies
```

**requirements.txt:**
```
mcp>=1.0.0
pydantic>=2.0.0
```

Install:
```bash
pip install -r requirements.txt
```

---

## Step 3: Define Your Tools

Tools are the core of your MCP server. Each tool needs:
- A **name** (unique identifier)
- A **description** (helps the AI understand when to use it)
- An **input schema** (JSON Schema defining parameters)

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("my-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_task",
            description="Create a new task/todo item",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level"
                    }
                },
                "required": ["title"]
            }
        ),
        # ... more tools
    ]
```

### Tips for Good Tool Definitions

- **Descriptions matter**: The AI uses them to decide WHEN to call your tool
- **Be specific**: "Create a new task with a title and optional priority" > "Create task"
- **Use enums**: Constrain values where possible (`"enum": ["low", "medium", "high"]`)
- **Mark required fields**: Only mark truly required params as required

---

## Step 4: Implement Tool Handlers

The `call_tool` handler executes when the AI invokes a tool:

```python
from mcp.types import TextContent

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to the right handler."""

    if name == "create_task":
        # Your business logic here
        task = create_task(
            title=arguments["title"],
            priority=arguments.get("priority", "medium")
        )
        return [TextContent(type="text", text=json.dumps(task, indent=2))]

    elif name == "list_tasks":
        tasks = get_all_tasks()
        return [TextContent(type="text", text=json.dumps(tasks, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
```

### Key Rules

1. **Always return `list[TextContent]`** — even for errors
2. **Return JSON** — structured data is easier for the AI to interpret
3. **Handle missing arguments gracefully** — use `.get()` with defaults
4. **Return meaningful errors** — don't crash, return error messages

---

## Step 5: Add Resources (Optional)

Resources let the AI READ data without calling a tool:

```python
from mcp.types import Resource

@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="myapp://data/summary",
            name="Data Summary",
            description="Overview of all data",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "myapp://data/summary":
        return json.dumps(get_summary())
    return json.dumps({"error": "Unknown resource"})
```

---

## Step 6: Wire Up the Server Entry Point

The entry point starts the server with stdio transport:

```python
import asyncio
from mcp.server.stdio import stdio_server

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Why stdio?

- **Simple**: No network configuration needed
- **Secure**: Only the parent process can communicate
- **Standard**: All MCP clients support it
- **Managed**: The client starts/stops the server automatically

---

## Step 7: Test Your Server

### Option A: Test with MCP Inspector

```bash
pip install mcp-inspector
mcp-inspector python -m your_mcp_server.server
```

### Option B: Test with a Simple Script

```python
import subprocess
import json

# Start the server
proc = subprocess.Popen(
    ["python", "-m", "your_mcp_server.server"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Send an initialize request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0.0"}
    }
}

proc.stdin.write(json.dumps(request).encode() + b"\n")
proc.stdin.flush()

# Read response
response = proc.stdout.readline()
print(json.loads(response))
```

### Option C: Test by Configuring in Kiro

The fastest way — just add it to your MCP config and try calling the tools.

---

## Step 8: Configure in an MCP Client

### Kiro Configuration

Create/edit `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "taskpilot": {
      "command": "python",
      "args": ["-m", "taskpilot.mcp_server.server"],
      "cwd": "/path/to/your/project",
      "disabled": false,
      "autoApprove": ["list_tasks", "get_task", "search_tasks", "task_summary"]
    }
  }
}
```

### Claude Desktop Configuration

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "taskpilot": {
      "command": "python",
      "args": ["-m", "taskpilot.mcp_server.server"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### Configuration Fields

| Field | Description |
|-------|-------------|
| `command` | The executable to run (`python`, `node`, `uvx`, etc.) |
| `args` | Command-line arguments |
| `cwd` | Working directory for the server process |
| `env` | Environment variables to pass |
| `disabled` | Set `true` to temporarily disable |
| `autoApprove` | Tools that don't need user confirmation |

---

## Best Practices

### 1. Tool Design

- **One tool = one action** — don't combine create + update into one tool
- **Descriptive names** — `create_task` not `ct` or `new`
- **Good descriptions** — the AI reads these to decide what to call
- **Validate inputs** — check required fields, validate formats

### 2. Error Handling

```python
# GOOD: Return structured errors
return [TextContent(type="text", text=json.dumps({"error": "Task not found", "task_id": 42}))]

# BAD: Raise exceptions (crashes the server)
raise ValueError("Task not found")
```

### 3. Response Format

```python
# GOOD: Structured JSON with context
return [TextContent(type="text", text=json.dumps({
    "message": "Task created successfully",
    "task": {"id": 1, "title": "Buy milk", "done": False}
}, indent=2))]

# BAD: Plain text (harder for AI to parse)
return [TextContent(type="text", text="Task created")]
```

### 4. Security

- **Don't expose secrets** in tool responses
- **Validate all inputs** before processing
- **Limit scope** — only expose what's needed
- **Use autoApprove wisely** — only for read-only tools

### 5. Performance

- Keep tool execution fast (< 5 seconds ideally)
- For long operations, return a status/ID and let the client poll
- Don't block the event loop with synchronous I/O

---

## Common Patterns

### Pattern: CRUD Operations

```python
# Standard CRUD tool set for any entity
tools = [
    "create_<entity>",   # POST
    "get_<entity>",      # GET by ID
    "list_<entities>",   # GET all (with filters)
    "update_<entity>",   # PATCH
    "delete_<entity>",   # DELETE
]
```

### Pattern: Database-Backed Storage

```python
import sqlite3

DB_PATH = "tasks.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# In your tool handler:
async def call_tool(name, arguments):
    if name == "create_task":
        db = get_db()
        db.execute("INSERT INTO tasks (title, priority) VALUES (?, ?)",
                   (arguments["title"], arguments.get("priority", "medium")))
        db.commit()
        # ...
```

### Pattern: External API Integration

```python
import httpx

async def call_tool(name, arguments):
    if name == "get_weather":
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://api.weather.com/{arguments['city']}")
            return [TextContent(type="text", text=resp.text)]
```

### Pattern: Connecting to Your Existing REST API

```python
import httpx

BASE_URL = "http://localhost:8002/api/v1"

async def call_tool(name, arguments):
    if name == "create_task":
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{BASE_URL}/agent/chat",
                                     json={"message": f"Create task: {arguments['title']}"})
            return [TextContent(type="text", text=resp.text)]
```

---

## Troubleshooting

### Server won't start

```
Error: No module named 'mcp'
```
**Fix:** `pip install mcp`

### Client can't connect

- Check the `cwd` path is correct
- Check `python` is in your PATH (or use full path like `C:/Python311/python.exe`)
- Check for syntax errors: `python -c "import taskpilot.mcp_server.server"`

### Tools not showing up

- Verify `list_tools()` returns tools (not an empty list)
- Check the MCP client logs for connection errors
- Restart the MCP server from the client

### Tool calls failing

- Check `arguments` dict has the expected keys
- Add logging: `print(f"DEBUG: {name} called with {arguments}", file=sys.stderr)`
- stderr output won't interfere with the JSON-RPC protocol on stdout

### Debugging Tips

```python
import sys

# Log to stderr (won't break stdio protocol)
print(f"[DEBUG] Tool called: {name}", file=sys.stderr)
print(f"[DEBUG] Arguments: {arguments}", file=sys.stderr)
```

---

## Full Minimal Example

Here's the smallest possible working MCP server:

```python
"""Minimal MCP Server — 30 lines"""
import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("minimal-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="hello",
            description="Say hello to someone",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name to greet"}
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "hello":
        return [TextContent(type="text", text=f"Hello, {arguments['name']}! 👋")]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

---

## What's Next?

- **Add persistence**: Swap in-memory store for SQLite or PostgreSQL
- **Add authentication**: Validate API keys or tokens
- **Add prompts**: Pre-built prompt templates for common workflows
- **Publish**: Package as a pip-installable module or Docker container
- **SSE transport**: For remote/networked deployments instead of stdio

---

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Example MCP Servers](https://github.com/modelcontextprotocol/servers)
