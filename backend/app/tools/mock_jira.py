import json
from pathlib import Path
from typing import Any

from app.tools.mcp_base import MCPTool


class MockJiraTool(MCPTool):
    name = "mock_jira"
    description = "Returns sample backlog items as if they came from Jira."

    def run(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        data_path = Path(__file__).resolve().parents[1] / "data" / "sample_backlog.json"
        return json.loads(data_path.read_text(encoding="utf-8"))
