from fastapi import APIRouter
from taskpilot.schemas.agent_schema import AgentRequest, AgentResponse
from taskpilot.agent.agent import run_agent

router = APIRouter()


@router.post("/agent/chat", response_model=AgentResponse)
def chat_with_agent(request: AgentRequest):
    """
    Send a message to TaskPilot.
    The agent decides whether to use tools or just respond.

    Examples:
    - "Add a task: buy groceries" → uses create_task tool
    - "Show my tasks" → uses list_tasks tool
    - "Mark task 1 as done" → uses complete_task tool
    - "Hello!" → just responds, no tools
    """
    result = run_agent(request.message)
    return AgentResponse(
        response=result["response"],
        tools_used=result["tools_used"]
    )
