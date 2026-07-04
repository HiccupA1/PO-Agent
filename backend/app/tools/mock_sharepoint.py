import json
from pathlib import Path
from typing import Any

from app.tools.mcp_base import MCPBaseTool


def _load_product_context() -> dict[str, Any]:
    data_path = Path(__file__).resolve().parents[1] / "data" / "sample_product_context.json"
    return json.loads(data_path.read_text(encoding="utf-8"))


class MockSharePointGetProductContextTool(MCPBaseTool):
    tool_name = "mock_sharepoint.get_product_context"
    display_name = "Mock SharePoint Product Context"
    description = "Returns mock product context as if it came from SharePoint."
    input_schema = {"topic": "string", "context": "object"}
    output_schema = {"context": "object"}

    def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        context = _load_product_context()
        context.update(tool_input.get("context", {}))
        if tool_input.get("topic"):
            context["requested_topic"] = tool_input["topic"]
        return {"context": context}


class MockSharePointSearchStakeholderNotesTool(MCPBaseTool):
    tool_name = "mock_sharepoint.search_stakeholder_notes"
    display_name = "Mock SharePoint Stakeholder Notes Search"
    description = "Returns deterministic stakeholder notes for backlog refinement topics."
    input_schema = {"query": "string", "limit": "integer"}
    output_schema = {"notes": "array"}

    def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        query = str(tool_input.get("query", "product backlog"))
        limit = int(tool_input.get("limit", 3))
        notes = [
            {
                "title": "Procurement refinement notes",
                "summary": "Stakeholders want approval clarity, auditability, and fewer delayed purchase orders.",
            },
            {
                "title": "Finance governance notes",
                "summary": "Finance needs threshold-based approval and visibility into exceptions.",
            },
            {
                "title": "Delivery team concerns",
                "summary": "The team wants dependencies and readiness gaps visible before sprint planning.",
            },
        ]
        return {"notes": notes[:limit], "query": query}


class MockSharePointTool(MockSharePointGetProductContextTool):
    def run(self, payload: dict[str, Any]) -> dict[str, Any]:  # Backward-compatible shape.
        return self.execute(payload)["context"]
