# Build Plan

## Phase 0: Scaffold and Mock Agent - Complete

Created the local full-stack scaffold, deterministic agent workflow, mock tools, trace output, and sample data.

## Phase 1: Acceptance Criteria Drafting - Complete

Implemented structured acceptance criteria drafting for `draft_acceptance_criteria`.

Current capabilities:

- Rewrites raw feature descriptions into user story format
- Generates Given/When/Then acceptance criteria
- Adds edge cases, non-functional requirements, assumptions, and clarification questions
- Scores Definition of Ready readiness
- Shows agent trace steps for planning, mock tool calls, evaluation, output, and human review
- Records lightweight audit summaries locally

## Phase 2: Epic Decomposition and DoR Checks - Complete

Implemented structured epic decomposition and Definition of Ready analysis.

Current capabilities:

- Decomposes vague epics and feature ideas into 4 to 6 user stories
- Adds persona, goal, business value, acceptance criteria preview, priority, complexity, dependencies, and risks
- Runs INVEST checks for each generated story
- Creates release slices for MVP, later enhancement, and operational/admin work
- Scores Definition of Ready across persona, goal, value, criteria, dependencies, edge cases, non-functional needs, testability, scope, and ambiguity
- Returns passed checks, failed checks, recommendations, risk flags, and human review reasons

## Phase 3: Backlog Scoring and Prioritization - Complete

Implemented deterministic backlog scoring and prioritization.

Current capabilities:

- Parses pasted backlog lists, vague product goals, or mock Jira fallback data
- Scores reach, impact, confidence, effort, risk reduction, and readiness
- Ranks backlog items with high, medium, and low priority labels
- Identifies quick wins, high-risk items, blocked items, and sprint candidates
- Records prioritization-specific audit metadata
- Renders prioritization results in the frontend

## Phase 4: MCP-Style Integration Layer - Implemented

Implemented a registry-based MCP-style mock tool layer.

Current capabilities:

- Defines a common MCP-style base tool interface with manifests and `execute`
- Registers Jira, SharePoint, Teams, and audit mock tools
- Exposes `GET /tools` and `POST /tools/run`
- Refactors agent workflows to call tools through `ToolRegistry`
- Adds tool trace metadata for tool name, input summary, output summary, and status
- Adds a frontend Tool Explorer for manifests and simple tool execution

## Phase 5: Real LLM / Claude Agent SDK Adapter

Replace deterministic mock behavior with a production-grade agent loop, stronger observability, review checkpoints, and deployment-ready controls.

## Phase 6: Demo Polish and Interview Walkthrough

Create a guided demo script, polished sample data, and a concise enterprise AI narrative for interviews.
