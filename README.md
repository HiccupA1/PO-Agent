# PO Agent - Product Owner Backlog Architect

PO Agent is an interview-ready proof-of-concept showing how an autonomous Product Owner Agent can turn product context, epics, stakeholder notes, and backlog ideas into structured agile outputs.

## Why This Is Agentic

The project models a simple agent loop: understand the requested Product Owner task, load product context, call MCP-style mock tools, produce a structured output, record a trace, and mark where human review is required.

## Problem It Solves

Technical Product Owners often spend too much time during sprint-zero and backlog refinement turning messy context into acceptance criteria, decomposed stories, and readiness checks. PO Agent demonstrates how an AI assistant can accelerate those repetitive structuring tasks while keeping the PO in control.

## Current Phase

Phase 5B: Gemini provider integration is implemented. The app supports structured Product Owner workflows, registry-based mock tools, optional LLM-assisted runtime mode, Gemini/OpenAI-compatible provider adapters, safe fallback to deterministic mock mode, runtime metadata, lightweight audit summaries, and human review checkpoints. No paid APIs, real LLM calls, authentication, or database are required for local demo mode.

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

From the project root, you can also use:

```powershell
.\scripts\start-backend.ps1
```

If Windows has a stale process holding port `8000`, start on another port:

```powershell
.\scripts\start-backend.ps1 -Port 8001
```

After editing `backend/.env`, restart the backend process so the running server picks up the new local configuration.

The backend exposes:

- `GET /health`
- `POST /agent/run`
- `GET /tools`
- `POST /tools/run`
- `GET /llm/status`
- `GET /llm/debug-config`

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
- Decompose an epic into 4 to 6 INVEST-style user stories
- Generate release slices for MVP, later enhancements, and operational/admin work
- Check Definition of Ready with structured pass/fail analysis and recommendations
- Prioritize backlog items using a RICE + Risk + Readiness scoring model
- Highlight quick wins, high-risk items, blocked items, and recommended sprint candidates
- List MCP-style mock tool manifests
- Run registered mock tools through a debug endpoint and frontend Tool Explorer
- Select mock or LLM-assisted runtime mode
- Fall back to deterministic mock output when provider config is missing or malformed
- Return observable agent trace steps
- Show a local backlog preview

## Runtime Modes

Mock mode is the default. It is deterministic, local, and uses rule-based templates so demos work without an API key.

LLM mode is optional. When requested, the backend asks the configured provider, such as Gemini, to generate a fresh Product Owner response from the user input, workflow name, product context, backlog context, and tool results. The deterministic template output is prepared only as a fallback candidate and is not included in the Gemini prompt.

If provider configuration is missing, Gemini times out, provider output is malformed, or schema validation fails, the agent returns the deterministic fallback and records that fallback in trace and response metadata.

Environment variables:

```env
LLM_MODE=mock
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
LLM_TIMEOUT_SECONDS=30
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash
GEMINI_TIMEOUT_SECONDS=120
```

### Gemini Setup

Mock mode is still the default. To test Gemini locally, create `backend/.env` yourself and keep it out of Git:

```env
LLM_MODE=llm
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-local-gemini-key-here
GEMINI_MODEL=gemini-3.1-flash-lite
GEMINI_TIMEOUT_SECONDS=120
```

Supported Gemini model values for this project:

- `gemini-3.5-flash`
- `gemini-3.1-flash-lite`

Never commit API keys. `backend/.env` is ignored by Git and must stay local. Gemini keys are read by the backend only and are never exposed to frontend code. Switch models by changing `GEMINI_MODEL` in `backend/.env`.

Use `GET /llm/status` to confirm the active provider, model, timeout, configured state, and fallback state. Use `GET /llm/debug-config` only for safe local diagnostics; it reports whether a Gemini key is present without returning the key.

Runtime metadata is included in every `/agent/run` response:

```json
{
  "mode_requested": "llm",
  "mode_used": "llm",
  "provider": "gemini",
  "provider_configured": true,
  "generation_source": "llm",
  "fallback_used": false,
  "fallback_reason": null
}
```

`runtime.generation_source` explains what produced the final answer:

- `mock`: deterministic local template output
- `llm`: Gemini/provider-generated output
- `fallback`: deterministic output returned because the provider was unavailable or invalid

`runtime.fallback_used` shows whether the fallback path was used.

## MCP-Style Tool Layer

Current tools are mock implementations, but they follow an adapter and manifest style that can be replaced later by real Jira, SharePoint, Teams, Microsoft Graph, or audit tools.

Each registered tool exposes:

- tool name
- display name
- description
- input schema
- output schema
- `execute(input)` behavior

The agent uses `ToolRegistry` instead of calling Jira or SharePoint classes directly. This keeps the agent workflow stable while future real MCP integrations replace mock implementations behind the same tool names.

Tool debug endpoints:

```http
GET /tools
POST /tools/run
```

Example `/tools/run` payload:

```json
{
  "tool_name": "mock_jira.search_backlog",
  "input": {
    "query": "purchase order",
    "limit": 5
  }
}
```

## Example Acceptance Criteria Input

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

## Example Epic Demo Flow

1. Enter a vague epic such as `Improve procurement experience.`
2. The agent identifies likely personas and workflow assumptions.
3. The agent decomposes the epic into INVEST-style stories.
4. The agent checks each story for independence, value, size, and testability.
5. The agent creates release slices for MVP, later enhancement, and operational/admin work.
6. The agent flags human review for unresolved assumptions and enterprise workflow decisions.

## Example DoR Check

Input:

```json
{
  "task": "check_dor",
  "input": "As a finance manager, I want to approve or reject purchase orders so that procurement spend is controlled.",
  "context": {}
}
```

Output summary:

- DoR score and Ready / Needs Refinement / Not Ready status
- Passed readiness checks
- Failed checks with recommendations
- Risk flags and recommended next actions
- Human review reason

## Example Prioritization Demo Flow

1. Paste a backlog item list.
2. The agent scores each item using reach, impact, confidence, effort, risk reduction, and readiness.
3. The agent ranks the backlog by weighted score.
4. The agent highlights quick wins, high-risk items, and blockers.
5. The agent recommends sprint candidates.
6. The trace shows the scoring workflow and human review checkpoint.

Scoring model:

- Reach: 20%
- Impact: 25%
- Confidence: 15%
- Effort: 15%, inverted so higher effort reduces score
- Risk reduction: 10%
- Readiness: 15%

## Future Integrations

- Real LLM-backed reasoning
- Jira MCP tool integration
- Microsoft Graph, Teams, and SharePoint MCP tools
- Persistent audit logging
- Claude Agent SDK adapter
- Human-in-the-loop approval workflows
