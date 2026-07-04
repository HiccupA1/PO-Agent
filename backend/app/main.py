from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.po_agent import ProductOwnerAgent
from app.core.config import settings
from app.schemas.agent import AgentRunRequest, AgentRunResponse, ToolListResponse, ToolRunRequest, ToolRunResponse, TraceStep
from app.tools.registry import create_default_tool_registry

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tool_registry = create_default_tool_registry()
agent = ProductOwnerAgent(tool_registry=tool_registry)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "po-agent"}


@app.post("/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    return agent.run(request)


@app.get("/tools", response_model=ToolListResponse)
def list_tools() -> ToolListResponse:
    return ToolListResponse(tools=tool_registry.list_tools())


@app.post("/tools/run", response_model=ToolRunResponse)
def run_tool(request: ToolRunRequest) -> ToolRunResponse:
    output = tool_registry.execute(request.tool_name, request.input)
    return ToolRunResponse(
        tool_name=request.tool_name,
        output=output,
        trace=[
            TraceStep(
                step=1,
                type="tool",
                message=f"Executed {request.tool_name}",
                metadata={
                    "tool_name": request.tool_name,
                    "input_summary": _summarize_payload(request.input),
                    "output_summary": _summarize_payload(output),
                    "status": "success",
                },
            )
        ],
    )


def _summarize_payload(payload: dict) -> str:
    parts = []
    for key, value in payload.items():
        if isinstance(value, list):
            parts.append(f"{key}: {len(value)} item(s)")
        elif isinstance(value, dict):
            parts.append(f"{key}: object with {len(value)} field(s)")
        else:
            parts.append(f"{key}: {str(value)[:60]}")
    return "; ".join(parts) if parts else "empty input"
