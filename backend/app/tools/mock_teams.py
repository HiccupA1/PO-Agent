from typing import Any

from app.tools.mcp_base import MCPBaseTool


class MockTeamsGetRecentFeedbackTool(MCPBaseTool):
    tool_name = "mock_teams.get_recent_feedback"
    display_name = "Mock Teams Recent Feedback"
    description = "Returns deterministic Teams-style feedback snippets for backlog context."
    input_schema = {"channel": "string", "topic": "string", "limit": "integer"}
    output_schema = {"feedback": "array"}

    def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        topic = str(tool_input.get("topic", "backlog refinement"))
        limit = int(tool_input.get("limit", 3))
        feedback = [
            {
                "author": "Finance stakeholder",
                "message": f"For {topic}, approval rules and audit visibility are the biggest concerns.",
            },
            {
                "author": "Procurement lead",
                "message": "Delayed purchase orders should surface early enough for teams to act.",
            },
            {
                "author": "Delivery lead",
                "message": "Stories need dependencies and testable acceptance criteria before sprint planning.",
            },
        ]
        return {"feedback": feedback[:limit]}
