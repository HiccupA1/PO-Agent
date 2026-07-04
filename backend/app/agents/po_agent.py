from app.schemas.agent import AgentRunRequest, AgentRunResponse, TraceEvent
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
        trace: list[TraceEvent] = []

        self.trace_service.add(
            trace,
            "plan",
            f"Agent identified the task as '{request.task}' and selected a deterministic mock workflow.",
        )

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
            "checkpoint",
            "Human review is required before using this output in a real backlog.",
        )

        for event in trace:
            self.audit_log.run({"event": event.model_dump()})

        return AgentRunResponse(
            task=request.task,
            final_output=final_output,
            trace=trace,
            human_review_required=human_review_required,
        )
