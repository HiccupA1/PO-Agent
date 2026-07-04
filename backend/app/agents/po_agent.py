from app.schemas.agent import (
    AcceptanceCriteriaOutput,
    AgentRunRequest,
    AgentRunResponse,
    DORCheckOutput,
    EpicDecompositionOutput,
    PrioritizationOutput,
    TraceStep,
)
from app.services.llm_service import MockLLMService
from app.services.trace_service import TraceService
from app.tools.registry import ToolRegistry, create_default_tool_registry


class ProductOwnerAgent:
    def __init__(self, tool_registry: ToolRegistry | None = None) -> None:
        self.llm = MockLLMService()
        self.trace_service = TraceService()
        self.tool_registry = tool_registry or create_default_tool_registry()

    def run(self, request: AgentRunRequest) -> AgentRunResponse:
        trace: list[TraceStep] = []

        if request.task == "draft_acceptance_criteria":
            return self._run_acceptance_criteria(request, trace)
        if request.task == "decompose_epic":
            return self._run_epic_decomposition(request, trace)
        if request.task == "check_dor":
            return self._run_dor_check(request, trace)
        if request.task == "prioritize_backlog":
            return self._run_prioritization(request, trace)

        self.trace_service.add(trace, "plan", f"Agent identified the task as '{request.task}'.")

        product_context = self._execute_tool(
            trace,
            "mock_sharepoint.get_product_context",
            {"context": request.context, "topic": request.task},
            "Loaded product context using mock SharePoint MCP tool.",
        )["context"]

        backlog_items = self._execute_tool(
            trace,
            "mock_jira.search_backlog",
            {"query": request.input or request.task, "limit": 5},
            "Retrieved sample backlog items using mock Jira MCP tool.",
        )["items"]

        final_output = self.llm.generate(
            task=request.task,
            user_input=request.input,
            product_context=product_context,
            backlog_items=backlog_items,
        )
        self.trace_service.add(
            trace,
            "output",
            "Produced a deterministic draft output for Product Owner review.",
        )

        human_review_required = True
        self.trace_service.add(
            trace,
            "human_review",
            "Human review is required before using this output in a real backlog.",
        )

        review_reason = "Mock output should be reviewed by a Product Owner before backlog use."
        self._record_audit(
            request=request,
            trace=trace,
            human_review_required=human_review_required,
            output_type="text",
        )

        return AgentRunResponse(
            task=request.task,
            final_output=final_output,
            trace=trace,
            human_review_required=human_review_required,
            review_reason=review_reason,
        )

    def _run_acceptance_criteria(
        self,
        request: AgentRunRequest,
        trace: list[TraceStep],
    ) -> AgentRunResponse:
        self.trace_service.add(
            trace,
            "plan",
            "Agent received backlog drafting task and selected the acceptance criteria workflow.",
            metadata={"task": request.task},
        )
        self.trace_service.add(
            trace,
            "evaluation",
            "Parsed story intent and checked whether the input already follows user story format.",
            metadata={"input_preview": request.input[:80]},
        )

        product_context = self._execute_tool(
            trace,
            "mock_sharepoint.get_product_context",
            {"context": request.context, "topic": "acceptance criteria"},
            "Loaded product context using mock SharePoint MCP tool.",
        )["context"]

        backlog_items = self._execute_tool(
            trace,
            "mock_jira.search_backlog",
            {"query": request.input, "limit": 5},
            "Checked related backlog items using mock Jira MCP tool.",
        )["items"]

        output = self.llm.generate(
            task=request.task,
            user_input=request.input,
            product_context=product_context,
            backlog_items=backlog_items,
        )
        if not isinstance(output, AcceptanceCriteriaOutput):
            raise TypeError("Expected structured acceptance criteria output.")

        self.trace_service.add(
            trace,
            "evaluation",
            "Evaluated Definition of Ready using deterministic readiness rules.",
            metadata={"dor_score": output.definition_of_ready.score},
        )
        self.trace_service.add(
            trace,
            "output",
            "Generated structured acceptance criteria, edge cases, non-functional requirements, and clarification questions.",
            metadata={"acceptance_criteria_count": len(output.acceptance_criteria)},
        )
        self.trace_service.add(
            trace,
            "human_review",
            "Flagged human review checkpoint before backlog commitment.",
            metadata={"review_reason": output.review_reason},
        )

        self._record_audit(
            request=request,
            trace=trace,
            human_review_required=output.human_review_required,
            output_type="acceptance_criteria",
            readiness_score=output.definition_of_ready.score,
        )

        return AgentRunResponse(
            task=request.task,
            final_output=output,
            trace=trace,
            human_review_required=output.human_review_required,
            review_reason=output.review_reason,
        )

    def _run_epic_decomposition(
        self,
        request: AgentRunRequest,
        trace: list[TraceStep],
    ) -> AgentRunResponse:
        self.trace_service.add(
            trace,
            "plan",
            "Agent received epic decomposition task and selected the INVEST story slicing workflow.",
            metadata={"task": request.task},
        )
        self.trace_service.add(
            trace,
            "evaluation",
            "Parsed epic intent and checked for vague or assumption-heavy wording.",
            metadata={"input_preview": request.input[:80]},
        )

        product_context = self._execute_tool(
            trace,
            "mock_sharepoint.get_product_context",
            {"context": request.context, "topic": "epic decomposition"},
            "Loaded product context using mock SharePoint MCP tool.",
        )["context"]

        backlog_items = self._execute_tool(
            trace,
            "mock_jira.search_backlog",
            {"query": request.input, "limit": 5},
            "Checked related backlog using mock Jira MCP tool.",
        )["items"]
        self.trace_service.add(
            trace,
            "evaluation",
            "Identified likely personas, workflow roles, and approval touchpoints.",
        )

        output = self.llm.generate(
            task=request.task,
            user_input=request.input,
            product_context=product_context,
            backlog_items=backlog_items,
        )
        if not isinstance(output, EpicDecompositionOutput):
            raise TypeError("Expected structured epic decomposition output.")

        self.trace_service.add(
            trace,
            "output",
            "Decomposed epic into INVEST-style user stories.",
            metadata={"generated_stories": len(output.decomposed_user_stories)},
        )
        self.trace_service.add(
            trace,
            "evaluation",
            "Ran INVEST checks for each generated story.",
            metadata={
                "stories_needing_split": [
                    story.id for story in output.decomposed_user_stories if not story.invest_check.small
                ]
            },
        )
        self.trace_service.add(
            trace,
            "output",
            "Created release slices for MVP, later enhancement, and operational/admin work.",
            metadata={"release_slices": [slice.name for slice in output.release_slices]},
        )
        self.trace_service.add(
            trace,
            "human_review",
            "Flagged human review checkpoint for assumptions, dependencies, and approval policy validation.",
            metadata={"review_reason": output.review_reason},
        )

        self._record_audit(
            request=request,
            trace=trace,
            human_review_required=output.human_review_required,
            output_type="epic_decomposition",
            generated_story_count=len(output.decomposed_user_stories),
        )

        return AgentRunResponse(
            task=request.task,
            final_output=output,
            trace=trace,
            human_review_required=output.human_review_required,
            review_reason=output.review_reason,
        )

    def _run_dor_check(
        self,
        request: AgentRunRequest,
        trace: list[TraceStep],
    ) -> AgentRunResponse:
        self.trace_service.add(
            trace,
            "plan",
            "Agent received readiness check task and selected the Definition of Ready workflow.",
            metadata={"task": request.task},
        )
        self.trace_service.add(
            trace,
            "evaluation",
            "Parsed backlog item for persona, goal, value, scope, and testability signals.",
            metadata={"input_preview": request.input[:80]},
        )

        self._execute_tool(
            trace,
            "mock_sharepoint.search_stakeholder_notes",
            {"query": request.input, "limit": 2},
            "Searched stakeholder notes using mock SharePoint MCP tool.",
        )

        output = self.llm.generate(
            task=request.task,
            user_input=request.input,
            product_context={},
            backlog_items=[],
        )
        if not isinstance(output, DORCheckOutput):
            raise TypeError("Expected structured DoR check output.")

        self.trace_service.add(
            trace,
            "evaluation",
            "Evaluated deterministic Definition of Ready criteria.",
            metadata={"passed": len(output.passed_checks), "failed": len(output.failed_checks)},
        )
        self.trace_service.add(
            trace,
            "evaluation",
            "Calculated readiness score and status.",
            metadata={"dor_score": output.dor_score, "status": output.status},
        )
        self.trace_service.add(
            trace,
            "evaluation",
            "Identified missing information and risk flags.",
            metadata={"risk_flags": output.risk_flags},
        )
        self.trace_service.add(
            trace,
            "output",
            "Recommended next refinement actions.",
            metadata={"next_action_count": len(output.recommended_next_actions)},
        )
        self.trace_service.add(
            trace,
            "human_review",
            "Flagged human review checkpoint for readiness decision.",
            metadata={"review_reason": output.review_reason},
        )

        self._record_audit(
            request=request,
            trace=trace,
            human_review_required=output.human_review_required,
            output_type="definition_of_ready",
            readiness_score=output.dor_score,
        )

        return AgentRunResponse(
            task=request.task,
            final_output=output,
            trace=trace,
            human_review_required=output.human_review_required,
            review_reason=output.review_reason,
        )

    def _run_prioritization(
        self,
        request: AgentRunRequest,
        trace: list[TraceStep],
    ) -> AgentRunResponse:
        self.trace_service.add(
            trace,
            "plan",
            "Agent received prioritization task and selected the RICE + Risk + Readiness workflow.",
            metadata={"task": request.task},
        )

        input_items = [line for line in request.input.splitlines() if line.strip()]
        self.trace_service.add(
            trace,
            "evaluation",
            "Parsed backlog items from user input or prepared to use mock Jira fallback.",
            metadata={"input_line_count": len(input_items), "uses_mock_fallback": not bool(request.input.strip())},
        )

        product_context = self._execute_tool(
            trace,
            "mock_sharepoint.get_product_context",
            {"context": request.context, "topic": "backlog prioritization"},
            "Loaded product context using mock SharePoint MCP tool.",
        )["context"]

        backlog_items = self._execute_tool(
            trace,
            "mock_jira.search_backlog",
            {"query": request.input or "product owner backlog", "limit": 5},
            "Retrieved related backlog metadata using mock Jira MCP tool.",
        )["items"]

        output = self.llm.generate(
            task=request.task,
            user_input=request.input,
            product_context=product_context,
            backlog_items=backlog_items,
        )
        if not isinstance(output, PrioritizationOutput):
            raise TypeError("Expected structured prioritization output.")

        self.trace_service.add(
            trace,
            "evaluation",
            "Applied RICE + Risk + Readiness scoring model to each backlog item.",
            metadata={"ranked_item_count": len(output.ranked_items)},
        )
        self.trace_service.add(
            trace,
            "output",
            "Ranked backlog items by weighted score.",
            metadata={"top_ranked_item": output.ranked_items[0].title if output.ranked_items else None},
        )
        self.trace_service.add(
            trace,
            "evaluation",
            "Identified quick wins, high-risk items, and blocked items.",
            metadata={
                "quick_wins": output.quick_wins,
                "high_risk_items": output.high_risk_items,
                "blocked_items": output.blocked_items,
            },
        )
        self.trace_service.add(
            trace,
            "output",
            "Recommended sprint candidates based on score, readiness, and blocker status.",
            metadata={"recommended_sprint_candidates": output.recommended_sprint_candidates},
        )
        self.trace_service.add(
            trace,
            "human_review",
            "Flagged Product Owner review checkpoint for prioritization assumptions and tradeoffs.",
            metadata={"review_reason": output.review_reason},
        )

        self._record_audit(
            request=request,
            trace=trace,
            human_review_required=output.human_review_required,
            output_type="backlog_prioritization",
            ranked_item_count=len(output.ranked_items),
            top_ranked_item=output.ranked_items[0].title if output.ranked_items else None,
            quick_win_count=len(output.quick_wins),
            blocked_item_count=len(output.blocked_items),
        )

        return AgentRunResponse(
            task=request.task,
            final_output=output,
            trace=trace,
            human_review_required=output.human_review_required,
            review_reason=output.review_reason,
        )

    def _record_audit(
        self,
        request: AgentRunRequest,
        trace: list[TraceStep],
        human_review_required: bool,
        output_type: str,
        readiness_score: int | None = None,
        generated_story_count: int | None = None,
        ranked_item_count: int | None = None,
        top_ranked_item: str | None = None,
        quick_win_count: int | None = None,
        blocked_item_count: int | None = None,
    ) -> None:
        self.tool_registry.execute(
            "mock_audit_log.record_event",
            {
                "task": request.task,
                "input_preview": request.input,
                "output_type": output_type,
                "human_review_required": human_review_required,
                "trace_step_count": len(trace),
                "readiness_score": readiness_score,
                "generated_story_count": generated_story_count,
                "ranked_item_count": ranked_item_count,
                "top_ranked_item": top_ranked_item,
                "quick_win_count": quick_win_count,
                "blocked_item_count": blocked_item_count,
            }
        )

    def _execute_tool(
        self,
        trace: list[TraceStep],
        tool_name: str,
        tool_input: dict,
        message: str,
    ) -> dict:
        try:
            output = self.tool_registry.execute(tool_name, tool_input)
            status = "success"
        except Exception as exc:
            output = {"error": str(exc)}
            status = "error"
            self.trace_service.add(
                trace,
                "tool",
                message,
                tool_name=tool_name,
                metadata={
                    "tool_name": tool_name,
                    "input_summary": self._summarize_payload(tool_input),
                    "output_summary": str(exc),
                    "status": status,
                },
            )
            raise

        self.trace_service.add(
            trace,
            "tool",
            message,
            tool_name=tool_name,
            metadata={
                "tool_name": tool_name,
                "input_summary": self._summarize_payload(tool_input),
                "output_summary": self._summarize_payload(output),
                "status": status,
            },
        )
        return output

    def _summarize_payload(self, payload: dict) -> str:
        parts: list[str] = []
        for key, value in payload.items():
            if isinstance(value, list):
                parts.append(f"{key}: {len(value)} item(s)")
            elif isinstance(value, dict):
                parts.append(f"{key}: object with {len(value)} field(s)")
            elif value is None:
                parts.append(f"{key}: none")
            else:
                parts.append(f"{key}: {str(value)[:80]}")
        return "; ".join(parts) if parts else "empty"
