from typing import Any

from app.tools.mcp_base import MCPTool


class MockAuditLogTool(MCPTool):
    name = "mock_audit_log"
    description = "Stores trace events in memory for this process."

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = payload.get("event", {})
        self.events.append(event)
        return {"recorded": True, "count": len(self.events)}
