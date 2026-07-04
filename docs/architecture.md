# Architecture

## High-Level Architecture

PO Agent uses a small full-stack layout:

- Next.js frontend for task selection, input, output, trace display, and backlog preview
- FastAPI backend for health checks and agent execution
- Python agent module for workflow orchestration
- MCP-style mock tools for Jira, SharePoint, and audit logging
- Local JSON sample data for backlog and product context

## Flow

1. The user selects a task and provides backlog context in the frontend.
2. The frontend posts to `POST /agent/run`.
3. The FastAPI route passes the request to the Product Owner Agent.
4. The agent creates a plan trace, loads product context, calls mock Jira data, generates deterministic output, and records audit events.
5. The backend returns the final output, trace, and human review flag.

## Phase 1 Acceptance Criteria Flow

For `draft_acceptance_criteria`, the agent now follows a clearer workflow:

1. Plan the backlog drafting task.
2. Parse whether the input already looks like a user story.
3. Load product context through the mock SharePoint tool.
4. Check related sample backlog items through the mock Jira tool.
5. Generate structured acceptance criteria, edge cases, non-functional requirements, assumptions, and clarification questions.
6. Evaluate Definition of Ready readiness with deterministic scoring rules.
7. Flag a human review checkpoint and record an audit summary.

## MCP-Style Mock Tools

The backend defines a minimal `MCPTool` interface with a `run` method. Each mock tool follows that shape:

- `MockJiraTool` returns sample backlog items.
- `MockSharePointTool` returns sample product context.
- `MockAuditLogTool` records run summaries in memory and a gitignored `local_data/audit_log.json` file.

These tools are intentionally local and deterministic so the project can run without paid APIs.

## Why This Is Agentic

The product is agentic because the backend does more than transform text in a single step. It plans the task, calls mock tools for context, evaluates readiness, produces structured backlog artifacts, records observable trace steps, and flags human review before the output can be treated as delivery-ready.

## Human-In-The-Loop Checkpoint

The acceptance criteria workflow computes whether human review is required and always includes a review reason. This keeps the Product Owner accountable for final backlog quality and demonstrates where future approval workflows can be added.
