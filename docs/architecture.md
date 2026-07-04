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

## Phase 2 Epic Decomposition Flow

For `decompose_epic`, the agent now mimics a Product Owner refinement workflow:

1. Plan the decomposition task.
2. Parse the epic for intent, vagueness, and approval/compliance signals.
3. Load product context through the mock SharePoint tool.
4. Check related sample backlog items through the mock Jira tool.
5. Identify likely personas, workflow roles, and approval touchpoints.
6. Decompose the epic into INVEST-style user stories.
7. Run INVEST checks for each story.
8. Create release slices for MVP, later enhancement, and operational/admin work.
9. Flag human review for assumptions, dependencies, and policy decisions.

## Phase 2 Definition of Ready Flow

For `check_dor`, the agent evaluates whether a backlog item is ready for sprint planning:

1. Parse the item for persona, goal, value, acceptance criteria, dependencies, edge cases, non-functional needs, testability, scope, and ambiguity.
2. Score the item from 0 to 100.
3. Classify it as Ready, Needs Refinement, or Not Ready.
4. Return passed checks, failed checks, risk flags, and next actions.
5. Add a human review checkpoint when readiness is incomplete or risk is present.

## Phase 3 Prioritization Flow

For `prioritize_backlog`, the agent supports pasted backlog lists, vague product goals, or empty input. Empty input falls back to mock Jira backlog items.

1. Plan the prioritization task.
2. Parse backlog items from user input or load mock Jira backlog.
3. Load product context through the mock SharePoint tool.
4. Retrieve related backlog metadata through the mock Jira tool.
5. Apply the RICE + Risk + Readiness scoring model.
6. Rank backlog items by weighted score.
7. Identify quick wins, high-risk items, and blocked items.
8. Recommend sprint candidates.
9. Flag Product Owner review for scoring assumptions and tradeoffs.

The scoring model differs from simple LLM output because it is deterministic and explainable. Each item receives visible scores for reach, impact, confidence, effort, risk reduction, and readiness. Higher effort reduces the final score, while stronger value, risk reduction, and readiness raise it.

## MCP-Style Tool Architecture

Phase 4 introduces a cleaner MCP-style abstraction for external tools. Each tool exposes a manifest and an `execute(input)` method:

- `tool_name`
- `display_name`
- `description`
- `input_schema`
- `output_schema`
- `execute(input)`

The `ToolRegistry` registers available tools, lists manifests, gets tools by name, and executes a tool by name. Agent workflows call the registry rather than importing Jira, SharePoint, Teams, or audit implementations directly.

Registered mock tools:

- `mock_jira.search_backlog`
- `mock_jira.create_story_preview`
- `mock_sharepoint.get_product_context`
- `mock_sharepoint.search_stakeholder_notes`
- `mock_teams.get_recent_feedback`
- `mock_audit_log.record_event`

The mock tools make the local demo feel like an enterprise workflow without needing paid APIs or real system access. Jira stands in for related backlog context, SharePoint stands in for product context, Teams stands in for stakeholder feedback, and audit logging stands in for governance and observability.

## Tool Manifest and Debug Endpoints

`GET /tools` returns registered tool manifests for UI and debugging. `POST /tools/run` executes a selected mock tool and returns output plus a one-step tool trace. The frontend Tool Explorer uses both endpoints.

This is useful for interviews because it shows that tools are discoverable, typed, and executable through a common layer instead of being hidden helper functions.

## Why This Is Agentic

The product is agentic because the backend does more than transform text in a single step. It plans the task, selects tools through a registry, calls mock tools for context, evaluates readiness and INVEST quality, produces structured backlog artifacts, records observable trace steps, and flags human review before the output can be treated as delivery-ready.

## Technical Product Owner Value

Technical Product Owners need to explain why one backlog item should move before another. Phase 3 turns prioritization into a visible decision aid by exposing scores, tradeoffs, dependencies, blockers, and sprint candidate recommendations. The PO still owns the decision, but the agent reduces the manual comparison work.

## Why Traceability Matters

Enterprise AI workflows need more than a final answer. Product Owners, delivery leads, and governance reviewers need to see which task was selected, which tools were used, which checks passed or failed, and why human review was requested. The trace panel demonstrates that observable chain of work in a simple local form.

## Human-In-The-Loop Checkpoint

The acceptance criteria workflow computes whether human review is required and always includes a review reason. This keeps the Product Owner accountable for final backlog quality and demonstrates where future approval workflows can be added.
