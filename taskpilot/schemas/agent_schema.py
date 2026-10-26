from pydantic import BaseModel


class AgentRequest(BaseModel):
    message: str


class ToolUsed(BaseModel):
    tool: str
    input: dict
    output: dict


class AgentResponse(BaseModel):
    response: str
    tools_used: list[ToolUsed]
