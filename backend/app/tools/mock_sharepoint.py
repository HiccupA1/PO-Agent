import json
from pathlib import Path
from typing import Any

from app.tools.mcp_base import MCPTool


class MockSharePointTool(MCPTool):
    name = "mock_sharepoint"
    description = "Returns sample product context as if it came from SharePoint."

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        data_path = Path(__file__).resolve().parents[1] / "data" / "sample_product_context.json"
        context = json.loads(data_path.read_text(encoding="utf-8"))
        context.update(payload.get("context", {}))
        return context
