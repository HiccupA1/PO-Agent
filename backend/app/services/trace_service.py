from typing import Any

from app.schemas.agent import TraceStep

class TraceService:
    def add(
        self,
        trace: list[TraceStep],
        event_type: str,
        message: str,
        tool_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        trace.append(
            TraceStep(
                step=len(trace) + 1,
                type=event_type,
                message=message,
                tool_name=tool_name,
                metadata=metadata,
            )
        )
