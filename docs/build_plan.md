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

## Phase 2: Epic Decomposition and DoR Checks - Implemented

Implemented structured epic decomposition and Definition of Ready analysis.

Current capabilities:

- Decomposes vague epics and feature ideas into 4 to 6 user stories
- Adds persona, goal, business value, acceptance criteria preview, priority, complexity, dependencies, and risks
- Runs INVEST checks for each generated story
- Creates release slices for MVP, later enhancement, and operational/admin work
- Scores Definition of Ready across persona, goal, value, criteria, dependencies, edge cases, non-functional needs, testability, scope, and ambiguity
- Returns passed checks, failed checks, recommendations, risk flags, and human review reasons

## Phase 3: Backlog Scoring and Prioritization

Add scoring for value, risk, urgency, dependency load, and readiness.

## Phase 4: MCP-Style Integration Layer

Integrate Jira MCP, Microsoft Graph MCP, Teams, SharePoint, and persistent audit logging behind the existing tool abstraction.

## Phase 5: Real LLM / Claude Agent SDK Adapter

Replace deterministic mock behavior with a production-grade agent loop, stronger observability, review checkpoints, and deployment-ready controls.
