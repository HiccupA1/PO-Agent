from typing import Any

from app.tools.mcp_base import MCPBaseTool
from app.tools.mock_audit_log import MockAuditLogRecordEventTool
from app.tools.mock_jira import MockJiraCreateStoryPreviewTool, MockJiraSearchBacklogTool
from app.tools.mock_sharepoint import MockSharePointGetProductContextTool, MockSharePointSearchStakeholderNotesTool
from app.tools.mock_teams import MockTeamsGetRecentFeedbackTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, MCPBaseTool] = {}

    def register(self, tool: MCPBaseTool) -> None:
        self._tools[tool.tool_name] = tool

    def list_tools(self) -> list[dict[str, Any]]:
        return [tool.manifest() for tool in self._tools.values()]

    def get(self, tool_name: str) -> MCPBaseTool:
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' is not registered.")
        return self._tools[tool_name]

    def execute(self, tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
        return self.get(tool_name).execute(tool_input)


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(MockJiraSearchBacklogTool())
    registry.register(MockJiraCreateStoryPreviewTool())
    registry.register(MockSharePointGetProductContextTool())
    registry.register(MockSharePointSearchStakeholderNotesTool())
    registry.register(MockTeamsGetRecentFeedbackTool())
    registry.register(MockAuditLogRecordEventTool())
    return registry
