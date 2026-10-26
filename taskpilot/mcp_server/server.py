"""
TaskPilot MCP Server

A Model Context Protocol (MCP) server that exposes TaskPilot's task management
capabilities as tools. Any MCP-compatible client (Kiro, Claude Desktop, etc.)
can connect to this server and manage tasks through natural language or direct
tool calls.

This server provides:
- Task CRUD operations (create, read, update, delete)
- Task filtering and search
- Task statistics/summary
- Integration with TaskPilot's agentic capabilities
"""

import json
import asyncio
from datetime import datetime
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
)

# --- In-memory task store (shared state) ---
TASKS: list[dict] = []
_next_id = 1

# --- MCP Server Instance ---
server = Server("taskpilot-mcp")


# ============================================================
# TOOLS - Actions the MCP client can perform
# ============================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return all available tools."""
    return [
        Tool(
            name="create_task",
            description="Create a new task/todo item. Returns the created task with its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title or description"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority level (default: medium)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Optional due date in YYYY-MM-DD format"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags/categories for the task"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks. Optionally filter by status, priority, or tags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by task status (default: all)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filter by priority level"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Filter by a specific tag"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_task",
            description="Get details of a specific task by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to retrieve"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update an existing task's title, priority, due date, or tags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in YYYY-MM-DD format"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New list of tags (replaces existing)"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as done"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task permanently by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="search_tasks",
            description="Search tasks by keyword in title or tags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword to find in task titles or tags"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="task_summary",
            description="Get a summary/statistics of all tasks (total, completed, pending, by priority).",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool and return the result."""
    global _next_id

    if name == "create_task":
        task = {
            "id": _next_id,
            "title": arguments["title"],
            "done": False,
            "priority": arguments.get("priority", "medium"),
            "due_date": arguments.get("due_date"),
            "tags": arguments.get("tags", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "completed_at": None,
        }
        TASKS.append(task)
        _next_id += 1
        return [TextContent(type="text", text=json.dumps(task, indent=2))]

    elif name == "list_tasks":
        filtered = TASKS[:]

        status = arguments.get("status", "all")
        if status == "pending":
            filtered = [t for t in filtered if not t["done"]]
        elif status == "completed":
            filtered = [t for t in filtered if t["done"]]

        priority = arguments.get("priority")
        if priority:
            filtered = [t for t in filtered if t.get("priority") == priority]

        tag = arguments.get("tag")
        if tag:
            filtered = [t for t in filtered if tag in t.get("tags", [])]

        if not filtered:
            return [TextContent(type="text", text=json.dumps({"message": "No tasks found matching criteria.", "tasks": []}, indent=2))]

        return [TextContent(type="text", text=json.dumps({"total": len(filtered), "tasks": filtered}, indent=2))]

    elif name == "get_task":
        task_id = arguments["task_id"]
        for task in TASKS:
            if task["id"] == task_id:
                return [TextContent(type="text", text=json.dumps(task, indent=2))]
        return [TextContent(type="text", text=json.dumps({"error": f"Task with ID {task_id} not found"}))]

    elif name == "update_task":
        task_id = arguments["task_id"]
        for task in TASKS:
            if task["id"] == task_id:
                if "title" in arguments:
                    task["title"] = arguments["title"]
                if "priority" in arguments:
                    task["priority"] = arguments["priority"]
                if "due_date" in arguments:
                    task["due_date"] = arguments["due_date"]
                if "tags" in arguments:
                    task["tags"] = arguments["tags"]
                return [TextContent(type="text", text=json.dumps({"message": f"Task '{task['title']}' updated!", "task": task}, indent=2))]
        return [TextContent(type="text", text=json.dumps({"error": f"Task with ID {task_id} not found"}))]

    elif name == "complete_task":
        task_id = arguments["task_id"]
        for task in TASKS:
            if task["id"] == task_id:
                task["done"] = True
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                return [TextContent(type="text", text=json.dumps({"message": f"Task '{task['title']}' marked as done!", "task": task}, indent=2))]
        return [TextContent(type="text", text=json.dumps({"error": f"Task with ID {task_id} not found"}))]

    elif name == "delete_task":
        task_id = arguments["task_id"]
        for i, task in enumerate(TASKS):
            if task["id"] == task_id:
                removed = TASKS.pop(i)
                return [TextContent(type="text", text=json.dumps({"message": f"Task '{removed['title']}' deleted!", "task": removed}, indent=2))]
        return [TextContent(type="text", text=json.dumps({"error": f"Task with ID {task_id} not found"}))]

    elif name == "search_tasks":
        query = arguments["query"].lower()
        results = [
            t for t in TASKS
            if query in t["title"].lower() or query in [tag.lower() for tag in t.get("tags", [])]
        ]
        return [TextContent(type="text", text=json.dumps({"query": arguments["query"], "results": results, "count": len(results)}, indent=2))]

    elif name == "task_summary":
        total = len(TASKS)
        completed = sum(1 for t in TASKS if t["done"])
        pending = total - completed
        by_priority = {
            "high": sum(1 for t in TASKS if t.get("priority") == "high"),
            "medium": sum(1 for t in TASKS if t.get("priority") == "medium"),
            "low": sum(1 for t in TASKS if t.get("priority") == "low"),
        }
        summary = {
            "total_tasks": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%",
            "by_priority": by_priority,
        }
        return [TextContent(type="text", text=json.dumps(summary, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


# ============================================================
# RESOURCES - Data the MCP client can read
# ============================================================


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="taskpilot://tasks/all",
            name="All Tasks",
            description="Complete list of all tasks in TaskPilot",
            mimeType="application/json",
        ),
        Resource(
            uri="taskpilot://tasks/summary",
            name="Task Summary",
            description="Statistics and summary of task status",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    if uri == "taskpilot://tasks/all":
        return json.dumps({"total": len(TASKS), "tasks": TASKS}, indent=2)
    elif uri == "taskpilot://tasks/summary":
        total = len(TASKS)
        completed = sum(1 for t in TASKS if t["done"])
        return json.dumps({
            "total_tasks": total,
            "completed": completed,
            "pending": total - completed,
        }, indent=2)
    else:
        return json.dumps({"error": f"Unknown resource: {uri}"})


# ============================================================
# ENTRY POINT
# ============================================================


async def main():
    """Run the MCP server via stdio transport."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
