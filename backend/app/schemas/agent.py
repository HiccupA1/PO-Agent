from typing import Any, Literal

from pydantic import BaseModel, Field


AgentTask = Literal[
    "draft_acceptance_criteria",
    "decompose_epic",
    "check_dor",
]


class AgentRunRequest(BaseModel):
    task: AgentTask
    input: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)


class TraceEvent(BaseModel):
    step: int
    type: str
    message: str
    tool_name: str | None = None


class AgentRunResponse(BaseModel):
    task: AgentTask
    final_output: str
    trace: list[TraceEvent]
    human_review_required: bool
