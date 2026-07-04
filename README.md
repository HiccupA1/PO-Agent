# PO Agent - Product Owner Backlog Architect

PO Agent is an interview-ready proof-of-concept showing how an autonomous Product Owner Agent can turn product context, epics, stakeholder notes, and backlog ideas into structured agile outputs.

## Why This Is Agentic

The project models a simple agent loop: understand the requested Product Owner task, load product context, call MCP-style mock tools, produce a structured output, record a trace, and mark where human review is required.

## Problem It Solves

Technical Product Owners often spend too much time during sprint-zero and backlog refinement turning messy context into acceptance criteria, decomposed stories, and readiness checks. PO Agent demonstrates how an AI assistant can accelerate those repetitive structuring tasks while keeping the PO in control.

## Current Phase

Phase 0: foundational scaffold and mock agent behavior. No paid APIs, real LLM calls, authentication, or database are required yet.

## Planned Stack

- FastAPI backend
- Next.js frontend
- Python agent service modules
- MCP-style mock tools
- Local JSON or in-memory mock storage
- Future Claude Agent SDK, Jira MCP, Microsoft Graph MCP, Teams, SharePoint, and audit logging integrations

## Setup

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend exposes:

- `GET /health`
- `POST /agent/run`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

By default, the frontend expects the backend at `http://localhost:8000`.

## What Works Now

- Draft acceptance criteria from a story or note
- Decompose an epic into mock INVEST-style stories
- Check Definition of Ready readiness
- Return observable agent trace steps
- Show a local backlog preview

## Future Integrations

- Real LLM-backed reasoning
- Jira MCP tool integration
- Microsoft Graph, Teams, and SharePoint MCP tools
- Backlog scoring and prioritization
- Persistent audit logging
- Human-in-the-loop approval workflows
