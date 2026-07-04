import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.tools.mcp_base import MCPTool


class MockAuditLogTool(MCPTool):
    name = "mock_audit_log"
    description = "Stores run summaries in memory and local JSON for this process."

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.log_path = Path(__file__).resolve().parents[3] / "local_data" / "audit_log.json"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "task": payload.get("task", "unknown"),
            "input_preview": str(payload.get("input_preview", ""))[:120],
            "human_review_required": bool(payload.get("human_review_required", True)),
            "trace_step_count": int(payload.get("trace_step_count", 0)),
        }
        self.events.append(record)
        self._append_local_record(record)
        return {"recorded": True, "count": len(self.events)}

    def _append_local_record(self, record: dict[str, Any]) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        existing: list[dict[str, Any]] = []
        if self.log_path.exists():
            existing = json.loads(self.log_path.read_text(encoding="utf-8"))
        existing.append(record)
        self.log_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
