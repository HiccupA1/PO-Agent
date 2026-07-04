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


class TraceStep(BaseModel):
    step: int
    type: str
    message: str
    tool_name: str | None = None
    metadata: dict[str, Any] | None = None


class AcceptanceCriteriaItem(BaseModel):
    id: str
    title: str
    given: str
    when: str
    then: str


class DefinitionOfReadyResult(BaseModel):
    score: int
    passed: list[str]
    failed: list[str]


class AcceptanceCriteriaOutput(BaseModel):
    rewritten_user_story: str
    acceptance_criteria: list[AcceptanceCriteriaItem]
    edge_cases: list[str]
    non_functional_requirements: list[str]
    assumptions: list[str]
    clarification_questions: list[str]
    definition_of_ready: DefinitionOfReadyResult
    human_review_required: bool
    review_reason: str


class InvestCheck(BaseModel):
    independent: bool
    negotiable: bool
    valuable: bool
    estimable: bool
    small: bool
    testable: bool
    notes: list[str]


class DecomposedUserStory(BaseModel):
    id: str
    title: str
    user_story: str
    persona: str
    goal: str
    business_value: str
    acceptance_criteria_preview: list[str]
    priority: Literal["High", "Medium", "Low"]
    estimated_complexity: Literal["S", "M", "L"]
    dependencies: list[str]
    risks: list[str]
    invest_check: InvestCheck


class ReleaseSlice(BaseModel):
    name: str
    stories: list[str]
    rationale: str


class EpicDecompositionOutput(BaseModel):
    epic_summary: str
    decomposed_user_stories: list[DecomposedUserStory]
    release_slices: list[ReleaseSlice]
    open_questions: list[str]
    human_review_required: bool
    review_reason: str


class DORPassedCheck(BaseModel):
    check: str
    reason: str


class DORFailedCheck(BaseModel):
    check: str
    reason: str
    recommendation: str


class DORCheckOutput(BaseModel):
    item_summary: str
    dor_score: int
    status: Literal["Ready", "Needs Refinement", "Not Ready"]
    passed_checks: list[DORPassedCheck]
    failed_checks: list[DORFailedCheck]
    risk_flags: list[str]
    recommended_next_actions: list[str]
    human_review_required: bool
    review_reason: str


class AgentRunResponse(BaseModel):
    task: AgentTask
    final_output: str | AcceptanceCriteriaOutput | EpicDecompositionOutput | DORCheckOutput
    trace: list[TraceStep]
    human_review_required: bool
    review_reason: str | None = None


TraceEvent = TraceStep
