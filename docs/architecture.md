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

## MCP-Style Mock Tools

The backend defines a minimal `MCPTool` interface with a `run` method. Each mock tool follows that shape:

- `MockJiraTool` returns sample backlog items.
- `MockSharePointTool` returns sample product context.
- `MockAuditLogTool` records trace events in memory.

These tools are intentionally local and deterministic so the project can run without paid APIs.

## Human-In-The-Loop Checkpoint

Every agent response includes `human_review_required: true`. This keeps the Product Owner accountable for final backlog quality and demonstrates where future approval workflows can be added.
