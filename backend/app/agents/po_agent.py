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
from app.tools.mock_audit_log import MockAuditLogTool
from app.tools.mock_jira import MockJiraTool
from app.tools.mock_sharepoint import MockSharePointTool


class ProductOwnerAgent:
    def __init__(self) -> None:
        self.llm = MockLLMService()
        self.trace_service = TraceService()
        self.audit_log = MockAuditLogTool()
        self.jira = MockJiraTool()
        self.sharepoint = MockSharePointTool()

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

        product_context = self.sharepoint.run({"context": request.context})
        self.trace_service.add(
            trace,
            "tool",
            "Loaded product context from the mock SharePoint tool.",
            tool_name=self.sharepoint.name,
        )

        backlog_items = self.jira.run({"task": request.task})
        self.trace_service.add(
            trace,
            "tool",
            "Retrieved sample backlog items from the mock Jira tool.",
            tool_name=self.jira.name,
        )

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

        product_context = self.sharepoint.run({"context": request.context})
        self.trace_service.add(
            trace,
            "tool",
            "Loaded product context using mock SharePoint tool.",
            tool_name=self.sharepoint.name,
            metadata={"product_name": product_context.get("product_name")},
        )

        backlog_items = self.jira.run({"task": request.task})
        self.trace_service.add(
            trace,
            "tool",
            "Checked related backlog items using mock Jira tool.",
            tool_name=self.jira.name,
            metadata={"related_items": [item.get("id") for item in backlog_items[:3]]},
        )

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

        product_context = self.sharepoint.run({"context": request.context})
        self.trace_service.add(
            trace,
            "tool",
            "Loaded product context from mock SharePoint tool.",
            tool_name=self.sharepoint.name,
            metadata={"product_name": product_context.get("product_name")},
        )

        backlog_items = self.jira.run({"task": request.task})
        self.trace_service.add(
            trace,
            "tool",
            "Checked related backlog from mock Jira tool.",
            tool_name=self.jira.name,
            metadata={"related_items": [item.get("id") for item in backlog_items[:3]]},
        )
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

        product_context = self.sharepoint.run({"context": request.context})
        self.trace_service.add(
            trace,
            "tool",
            "Loaded product context using mock SharePoint tool.",
            tool_name=self.sharepoint.name,
            metadata={"product_name": product_context.get("product_name")},
        )

        backlog_items = self.jira.run({"task": request.task})
        self.trace_service.add(
            trace,
            "tool",
            "Retrieved related backlog metadata using mock Jira tool.",
            tool_name=self.jira.name,
            metadata={"mock_backlog_count": len(backlog_items)},
        )

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
        self.audit_log.run(
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
