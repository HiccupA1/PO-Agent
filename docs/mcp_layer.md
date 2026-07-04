# MCP-Style Layer

## What MCP-Style Means Here

In this project, MCP-style means the PO Agent talks to external capabilities through named tools with manifests and structured inputs/outputs. The implementation is local and mock-only, but the shape is intentionally close to how real tool adapters would be exposed.

Each tool provides:

- `tool_name`
- `display_name`
- `description`
- `input_schema`
- `output_schema`
- `execute(input)`

## Why Mock Tools For Now

Phase 4 is about architecture readiness, not external system access. Mock tools keep the project runnable locally and avoid paid APIs, authentication, and environment setup while still demonstrating tool planning, execution, traceability, and governance.

## Replacing Mock Tools Later

A real Jira MCP or Microsoft Graph MCP adapter could replace a mock tool by keeping the same manifest and `execute` contract. For example:

- `mock_jira.search_backlog` can become a Jira issue search adapter.
- `mock_sharepoint.get_product_context` can become a SharePoint document or page lookup.
- `mock_teams.get_recent_feedback` can become a Teams channel feedback search.
- `mock_audit_log.record_event` can become persistent enterprise audit logging.

The agent should not need to change if the tool name, input shape, and output shape remain compatible.

## Tool Lifecycle

1. Agent plans the workflow.
2. Agent selects a tool by name.
3. `ToolRegistry` executes the tool.
4. The tool returns structured output.
5. The trace records tool name, input summary, output summary, and status.
6. The agent uses the result to produce the final Product Owner artifact.

This keeps the Product Owner workflow explainable and makes future integration work more contained.
