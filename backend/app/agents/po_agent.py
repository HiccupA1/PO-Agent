from app.schemas.agent import AcceptanceCriteriaOutput, AgentRunRequest, AgentRunResponse, TraceStep
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
        self._record_audit(request, trace, human_review_required)

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

        self._record_audit(request, trace, output.human_review_required)

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
    ) -> None:
        self.audit_log.run(
            {
                "task": request.task,
                "input_preview": request.input,
                "human_review_required": human_review_required,
                "trace_step_count": len(trace),
            }
        )
