"""
TOOLS - The "hands" of the agent.

TaskPilot's tools let the agent manage tasks:
- Create tasks
- List all tasks
- Mark tasks as complete
- Delete tasks

The agent DECIDES which tool to call based on what the user says.
"""

import json
from datetime import datetime

# --- In-memory task store (simple for demo) ---
TASKS: list[dict] = []
_next_id = 1


# --- TOOL DEFINITIONS (what we tell the LLM is available) ---

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task/todo item",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title/description"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks with their status",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed by its ID number",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as done"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its ID number",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]


# --- TOOL IMPLEMENTATIONS ---

def create_task(title: str) -> str:
    """Create a new task."""
    global _next_id
    task = {
        "id": _next_id,
        "title": title,
        "done": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    TASKS.append(task)
    _next_id += 1
    return json.dumps(task)


def list_tasks() -> str:
    """List all tasks."""
    if not TASKS:
        return json.dumps({"message": "No tasks yet!", "tasks": []})
    return json.dumps({"total": len(TASKS), "tasks": TASKS})


def complete_task(task_id: int) -> str:
    """Mark a task as done."""
    for task in TASKS:
        if task["id"] == task_id:
            task["done"] = True
            return json.dumps({"message": f"Task '{task['title']}' marked as done!", "task": task})
    return json.dumps({"error": f"Task with ID {task_id} not found"})


def delete_task(task_id: int) -> str:
    """Delete a task."""
    for i, task in enumerate(TASKS):
        if task["id"] == task_id:
            removed = TASKS.pop(i)
            return json.dumps({"message": f"Task '{removed['title']}' deleted!", "task": removed})
    return json.dumps({"error": f"Task with ID {task_id} not found"})


# --- TOOL REGISTRY ---

TOOL_REGISTRY = {
    "create_task": create_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool by name with given arguments."""
    if tool_name not in TOOL_REGISTRY:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    tool_fn = TOOL_REGISTRY[tool_name]
    return tool_fn(**arguments)
