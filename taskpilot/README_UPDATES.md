# TaskPilot — Updates & Changelog

## v2.0 — MCP Server Integration (2026-05-29)

### What's New

TaskPilot now includes a dedicated **MCP (Model Context Protocol) Server** that exposes task management as standardized tools for any MCP-compatible AI client.

### New Files Added

```
taskpilot/
├── mcp_server/
│   ├── __init__.py             # Package marker
│   ├── server.py               # MCP server implementation
│   ├── requirements.txt        # MCP-specific dependencies
│   └── README.md               # MCP server documentation
├── MCP_SERVER_BUILD_GUIDE.md   # Complete guide to building MCP servers
└── README_UPDATES.md           # This file
```

### New Capabilities via MCP

| Tool | Description |
|------|-------------|
| `create_task` | Create tasks with title, priority, due date, and tags |
| `list_tasks` | List/filter tasks by status, priority, or tag |
| `get_task` | Get a specific task by ID |
| `update_task` | Update task properties |
| `complete_task` | Mark a task as done |
| `delete_task` | Delete a task |
| `search_tasks` | Search tasks by keyword |
| `task_summary` | Get task statistics |

### Enhanced Features (vs original tools)

The MCP server extends the original TaskPilot tools with:

- **Priority levels** — `low`, `medium`, `high`
- **Due dates** — Track deadlines
- **Tags** — Categorize tasks with labels
- **Search** — Find tasks by keyword
- **Filtering** — Filter by status, priority, or tag
- **Statistics** — Completion rates and priority breakdown
- **Resources** — MCP resources for reading task data

### How to Use

#### Option 1: Configure in Kiro

Add to `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "taskpilot": {
      "command": "python",
      "args": ["-m", "taskpilot.mcp_server.server"],
      "cwd": "d:/Projects/AITraining",
      "disabled": false,
      "autoApprove": ["list_tasks", "get_task", "search_tasks", "task_summary"]
    }
  }
}
```

#### Option 2: Use with Claude Desktop

Edit `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`) and add an `mcpServers` entry next to any existing keys:

```json
{
  "mcpServers": {
    "taskpilot": {
      "command": "/absolute/path/to/python3",
      "args": ["-m", "taskpilot.mcp_server.server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/folder-containing-taskpilot"
      }
    }
  }
}
```

Replace the two placeholders for your machine:

- `command` — the full path of the Python that has `mcp<2` installed. Find it with `which python3` (or `pyenv which python3`). Claude Desktop does not load your shell, so a bare `python` often fails.
- `PYTHONPATH` — the folder that **contains** the `taskpilot/` directory (not `taskpilot/` itself).

Then quit Claude Desktop completely (Cmd+Q) and reopen it.

> The server uses the `mcp` 1.x API, so install it with `pip install "mcp<2"`.

### Install New Dependencies

```bash
pip install mcp pydantic
```

Or from the MCP server's requirements:

```bash
pip install -r taskpilot/mcp_server/requirements.txt
```

### Architecture Overview

```
Before (v1):
  User → REST API → Agent (ReAct Loop) → Tools → In-Memory Store

After (v2 — adds MCP path):
  User → REST API → Agent (ReAct Loop) → Tools → In-Memory Store
  AI Client → MCP Server (stdio) → Tools → In-Memory Store
```

The MCP server runs as a **separate process** from the FastAPI app. Each has its own in-memory task store. For shared state, you'd connect both to a database.

### Migration Notes

- **No breaking changes** — The original REST API and agent loop work exactly as before
- **Additive only** — The MCP server is a new, independent component
- **Separate process** — MCP server doesn't affect the FastAPI app's performance
- **Optional** — You can use TaskPilot without the MCP server

### What's Next (Roadmap)

- [ ] Shared database between REST API and MCP server (SQLite)
- [ ] Task due date reminders via MCP prompts
- [ ] Subtasks and task dependencies
- [ ] SSE transport for remote MCP connections
- [ ] Authentication for multi-user support
