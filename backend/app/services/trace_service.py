from app.schemas.agent import TraceEvent


class TraceService:
    def add(
        self,
        trace: list[TraceEvent],
        event_type: str,
        message: str,
        tool_name: str | None = None,
    ) -> None:
        trace.append(
            TraceEvent(
                step=len(trace) + 1,
                type=event_type,
                message=message,
                tool_name=tool_name,
            )
        )
