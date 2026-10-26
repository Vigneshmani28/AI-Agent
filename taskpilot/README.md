# TaskPilot - Agentic AI Task Manager

A simple agentic AI application that manages your tasks using natural language.

## What Makes This "Agentic"?

Unlike a chatbot that just talks, TaskPilot **takes action**:

| You say... | Agent does... |
|---|---|
| "Add a task: buy groceries" | Calls `create_task` tool → saves it |
| "What's on my list?" | Calls `list_tasks` tool → shows them |
| "Mark task 1 as done" | Calls `complete_task` tool → updates it |
| "Tell me a joke" | No tool needed → just responds |

## The Agent Loop (ReAct Pattern)

```
User: "Add buy milk to my tasks"
  → Agent THINKS: "I need the create_task tool"
  → Agent ACTS: create_task(title="buy milk")
  → Agent OBSERVES: {"id": 1, "title": "buy milk", "done": false}
  → Agent RESPONDS: "Done! I've added 'buy milk' to your tasks."
```

## Quick Start

```bash
cd taskpilot
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Run:
```bash
python -m taskpilot.main
```

Open: http://localhost:8002/docs

## Try It

POST `/api/v1/agent/chat`:
```json
{ "message": "Add a task: finish the report by Friday" }
```

POST `/api/v1/agent/chat`:
```json
{ "message": "Show me all my tasks" }
```

POST `/api/v1/agent/chat`:
```json
{ "message": "Mark task 1 as complete" }
```

## Project Structure

```
taskpilot/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── core/
│   └── config.py           # App settings
├── agent/
│   ├── agent.py            # The Agent brain (ReAct loop)
│   └── tools.py            # Tools the agent can call
├── api/
│   └── v1/
│       └── agent_controller.py  # REST endpoint
├── schemas/
│   └── agent_schema.py     # Request/Response models
└── mcp_server/             # MCP Server (NEW)
    ├── server.py           # MCP tool/resource definitions
    ├── requirements.txt    # MCP dependencies
    └── README.md           # MCP server docs
```

## MCP Server

TaskPilot also ships with an **MCP (Model Context Protocol) Server** that exposes task management tools to any MCP-compatible AI client (Kiro, Claude Desktop, Cursor, etc.).

See [`mcp_server/README.md`](mcp_server/README.md) for setup and usage.

See [`MCP_SERVER_BUILD_GUIDE.md`](MCP_SERVER_BUILD_GUIDE.md) for a complete guide on how to build MCP servers.

See [`README_UPDATES.md`](README_UPDATES.md) for the full changelog.
