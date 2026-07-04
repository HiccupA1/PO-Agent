import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.tools.mcp_base import MCPBaseTool


class MockAuditLogRecordEventTool(MCPBaseTool):
    tool_name = "mock_audit_log.record_event"
    display_name = "Mock Audit Log Event Recorder"
    description = "Stores run summaries in memory and local JSON for this process."
    input_schema = {
        "task": "string",
        "input_preview": "string",
        "output_type": "string",
        "human_review_required": "boolean",
        "trace_step_count": "integer",
    }
    output_schema = {"recorded": "boolean", "count": "integer"}

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.log_path = Path(__file__).resolve().parents[3] / "local_data" / "audit_log.json"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "task": payload.get("task", "unknown"),
            "input_preview": str(payload.get("input_preview", ""))[:120],
            "output_type": payload.get("output_type", "unknown"),
            "human_review_required": bool(payload.get("human_review_required", True)),
            "trace_step_count": int(payload.get("trace_step_count", 0)),
            "readiness_score": payload.get("readiness_score"),
            "generated_story_count": payload.get("generated_story_count"),
            "ranked_item_count": payload.get("ranked_item_count"),
            "top_ranked_item": payload.get("top_ranked_item"),
            "quick_win_count": payload.get("quick_win_count"),
            "blocked_item_count": payload.get("blocked_item_count"),
        }
        self.events.append(record)
        self._append_local_record(record)
        return {"recorded": True, "count": len(self.events)}

    def _append_local_record(self, record: dict[str, Any]) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        existing: list[dict[str, Any]] = []
        if self.log_path.exists():
            try:
                existing = json.loads(self.log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []
        existing.append(record)
        self.log_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


class MockAuditLogTool(MockAuditLogRecordEventTool):
    pass
