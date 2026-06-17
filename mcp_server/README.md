# TaskPilot MCP Server

A **Model Context Protocol (MCP)** server that exposes TaskPilot's task management capabilities as tools for any MCP-compatible AI client (Kiro, Claude Desktop, Cursor, etc.).

## What is This?

This MCP server wraps TaskPilot's core task management functionality into the MCP standard, allowing AI assistants to directly create, manage, and query tasks without going through the REST API.

```
┌─────────────────┐       stdio        ┌──────────────────────┐
│  MCP Client     │◄──────────────────►│  TaskPilot MCP Server │
│  (Kiro, Claude) │   JSON-RPC 2.0     │  (this server)        │
└─────────────────┘                    └──────────────────────┘
```

## Available Tools

| Tool | Description |
|------|-------------|
| `create_task` | Create a new task with title, priority, due date, and tags |
| `list_tasks` | List all tasks with optional filters (status, priority, tag) |
| `get_task` | Get details of a specific task by ID |
| `update_task` | Update a task's title, priority, due date, or tags |
| `complete_task` | Mark a task as completed |
| `delete_task` | Delete a task permanently |
| `search_tasks` | Search tasks by keyword in title or tags |
| `task_summary` | Get statistics (total, completed, pending, by priority) |

## Available Resources

| Resource URI | Description |
|---|---|
| `taskpilot://tasks/all` | Complete list of all tasks |
| `taskpilot://tasks/summary` | Task statistics summary |

## Quick Start

### 1. Install Dependencies

```bash
cd taskpilot/mcp_server
pip install -r requirements.txt
```

### 2. Test the Server Locally

```bash
python -m taskpilot.mcp_server.server
```

The server communicates via **stdio** (stdin/stdout) using JSON-RPC 2.0 — it won't print anything visible. It's designed to be launched by an MCP client.

### 3. Configure in Kiro

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "taskpilot": {
      "command": "python",
      "args": ["-m", "taskpilot.mcp_server.server"],
      "cwd": "d:/Projects/AITraining",
      "disabled": false,
      "autoApprove": ["create_task", "list_tasks", "get_task", "search_tasks", "task_summary"]
    }
  }
}
```

### 4. Configure in Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "taskpilot": {
      "command": "python",
      "args": ["-m", "taskpilot.mcp_server.server"],
      "cwd": "d:/Projects/AITraining"
    }
  }
}
```

## Tool Usage Examples

### Create a Task

```json
{
  "tool": "create_task",
  "arguments": {
    "title": "Finish the quarterly report",
    "priority": "high",
    "due_date": "2026-06-01",
    "tags": ["work", "reports"]
  }
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Finish the quarterly report",
  "done": false,
  "priority": "high",
  "due_date": "2026-06-01",
  "tags": ["work", "reports"],
  "created_at": "2026-05-29 14:30",
  "completed_at": null
}
```

### List Pending High-Priority Tasks

```json
{
  "tool": "list_tasks",
  "arguments": {
    "status": "pending",
    "priority": "high"
  }
}
```

### Search Tasks

```json
{
  "tool": "search_tasks",
  "arguments": {
    "query": "report"
  }
}
```

### Get Task Summary

```json
{
  "tool": "task_summary",
  "arguments": {}
}
```

**Response:**
```json
{
  "total_tasks": 5,
  "completed": 2,
  "pending": 3,
  "completion_rate": "40.0%",
  "by_priority": {
    "high": 2,
    "medium": 2,
    "low": 1
  }
}
```

## Architecture

```
mcp_server/
├── __init__.py         # Package marker
├── server.py           # MCP server implementation (tools + resources)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

The server uses:
- **`mcp` SDK** — Official Python MCP library
- **stdio transport** — Communication via stdin/stdout (standard for local MCP servers)
- **In-memory storage** — Tasks persist for the lifetime of the server process

## Notes

- Tasks are stored in-memory. They reset when the server restarts.
- The server is stateless between restarts — ideal for development and demos.
- For production use, you'd swap the in-memory store for a database (SQLite, PostgreSQL, etc.).
- The server runs as a subprocess managed by the MCP client — you don't need to start it manually.
