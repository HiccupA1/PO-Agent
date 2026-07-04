# PO Agent - Product Owner Backlog Architect

PO Agent is an interview-ready proof-of-concept showing how an autonomous Product Owner Agent can turn product context, epics, stakeholder notes, and backlog ideas into structured agile outputs.

## Why This Is Agentic

The project models a simple agent loop: understand the requested Product Owner task, load product context, call MCP-style mock tools, produce a structured output, record a trace, and mark where human review is required.

## Problem It Solves

Technical Product Owners often spend too much time during sprint-zero and backlog refinement turning messy context into acceptance criteria, decomposed stories, and readiness checks. PO Agent demonstrates how an AI assistant can accelerate those repetitive structuring tasks while keeping the PO in control.

## Current Phase

Phase 1: Acceptance Criteria Drafting Agent is implemented with structured output, rule-based Definition of Ready scoring, traceable mock tool use, and a human review checkpoint. No paid APIs, real LLM calls, authentication, or database are required yet.

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
.\.venv\Scripts\Activate.ps1
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

- Draft structured acceptance criteria from a story or feature note
- Rewrite raw feature descriptions into user story format
- Generate edge cases, non-functional requirements, assumptions, and clarification questions
- Score Definition of Ready readiness
- Decompose an epic into mock INVEST-style stories
- Check Definition of Ready readiness
- Return observable agent trace steps
- Show a local backlog preview

## Example

Input:

```json
{
  "task": "draft_acceptance_criteria",
  "input": "Build invoice approval flow for finance team.",
  "context": {}
}
```

Output summary:

- Rewritten user story for a finance approver
- 4 to 5 Given/When/Then acceptance criteria
- Invoice approval edge cases
- Auditability and performance non-functional requirements
- Definition of Ready score
- Human review reason and checkpoint

## Future Integrations

- Real LLM-backed reasoning
- Jira MCP tool integration
- Microsoft Graph, Teams, and SharePoint MCP tools
- Backlog scoring and prioritization
- Persistent audit logging
- Human-in-the-loop approval workflows
