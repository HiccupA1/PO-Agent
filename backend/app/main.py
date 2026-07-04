from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.po_agent import ProductOwnerAgent
from app.core.config import settings
from app.schemas.agent import AgentRunRequest, AgentRunResponse

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ProductOwnerAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "po-agent"}


@app.post("/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    return agent.run(request)
