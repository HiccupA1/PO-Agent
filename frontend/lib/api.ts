export type AgentTask =
  | "draft_acceptance_criteria"
  | "decompose_epic"
  | "check_dor"
  | "prioritize_backlog";

export type TraceEvent = {
  step: number;
  type: string;
  message: string;
  tool_name?: string | null;
  metadata?: Record<string, unknown> | null;
};

export type AcceptanceCriteriaItem = {
  id: string;
  title: string;
  given: string;
  when: string;
  then: string;
};

export type DefinitionOfReadyResult = {
  score: number;
  passed: string[];
  failed: string[];
};

export type AcceptanceCriteriaOutput = {
  rewritten_user_story: string;
  acceptance_criteria: AcceptanceCriteriaItem[];
  edge_cases: string[];
  non_functional_requirements: string[];
  assumptions: string[];
  clarification_questions: string[];
  definition_of_ready: DefinitionOfReadyResult;
  human_review_required: boolean;
  review_reason: string;
};

export type InvestCheck = {
  independent: boolean;
  negotiable: boolean;
  valuable: boolean;
  estimable: boolean;
  small: boolean;
  testable: boolean;
  notes: string[];
};

export type DecomposedUserStory = {
  id: string;
  title: string;
  user_story: string;
  persona: string;
  goal: string;
  business_value: string;
  acceptance_criteria_preview: string[];
  priority: "High" | "Medium" | "Low";
  estimated_complexity: "S" | "M" | "L";
  dependencies: string[];
  risks: string[];
  invest_check: InvestCheck;
};

export type ReleaseSlice = {
  name: string;
  stories: string[];
  rationale: string;
};

export type EpicDecompositionOutput = {
  epic_summary: string;
  decomposed_user_stories: DecomposedUserStory[];
  release_slices: ReleaseSlice[];
  open_questions: string[];
  human_review_required: boolean;
  review_reason: string;
};

export type DORPassedCheck = {
  check: string;
  reason: string;
};

export type DORFailedCheck = {
  check: string;
  reason: string;
  recommendation: string;
};

export type DORCheckOutput = {
  item_summary: string;
  dor_score: number;
  status: "Ready" | "Needs Refinement" | "Not Ready";
  passed_checks: DORPassedCheck[];
  failed_checks: DORFailedCheck[];
  risk_flags: string[];
  recommended_next_actions: string[];
  human_review_required: boolean;
  review_reason: string;
};

export type ScoringWeights = {
  reach: number;
  impact: number;
  confidence: number;
  effort: number;
  risk_reduction: number;
  readiness: number;
};

export type ScoringModel = {
  name: string;
  description: string;
  weights: ScoringWeights;
};

export type RankedBacklogItem = {
  rank: number;
  id: string;
  title: string;
  description: string;
  reach: number;
  impact: number;
  confidence: number;
  effort: number;
  risk_reduction: number;
  readiness: number;
  weighted_score: number;
  priority: "High" | "Medium" | "Low";
  rationale: string;
  tradeoffs: string[];
  dependencies: string[];
  recommended_next_action: string;
};

export type PrioritizationOutput = {
  prioritization_summary: string;
  scoring_model: ScoringModel;
  ranked_items: RankedBacklogItem[];
  quick_wins: string[];
  high_risk_items: string[];
  blocked_items: string[];
  recommended_sprint_candidates: string[];
  human_review_required: boolean;
  review_reason: string;
};

export type AgentResponse = {
  task: AgentTask;
  final_output:
    | string
    | AcceptanceCriteriaOutput
    | EpicDecompositionOutput
    | DORCheckOutput
    | PrioritizationOutput;
  trace: TraceEvent[];
  human_review_required: boolean;
  review_reason?: string | null;
  runtime: AgentRuntimeMetadata;
};

export type RuntimeMode = "mock" | "llm";

export type AgentRuntimeMetadata = {
  mode_requested: string;
  mode_used: string;
  provider: string;
  model?: string | null;
  timeout_seconds?: number | null;
  provider_configured: boolean;
  generation_source: "mock" | "llm" | "fallback";
  fallback_used: boolean;
  fallback_reason?: string | null;
};

export type LLMStatus = {
  mode: string;
  provider: string;
  model?: string;
  timeout_seconds?: number | null;
  available: boolean;
  configured: boolean;
  fallback_used: boolean;
  fallback_reason?: string | null;
  message: string;
};

export type ToolManifest = {
  tool_name: string;
  display_name: string;
  description: string;
  input_schema: Record<string, string>;
  output_schema: Record<string, string>;
};

export type ToolRunResponse = {
  tool_name: string;
  output: Record<string, unknown>;
  trace: TraceEvent[];
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function runAgent(
  task: AgentTask,
  input: string,
  runtimeMode: RuntimeMode = "mock"
): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE_URL}/agent/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      task,
      input,
      context: {},
      runtime: {
        mode: runtimeMode
      }
    })
  });

  if (!response.ok) {
    throw new Error("Agent request failed.");
  }

  return response.json();
}

export async function getLLMStatus(): Promise<LLMStatus> {
  const response = await fetch(`${API_BASE_URL}/llm/status`);

  if (!response.ok) {
    throw new Error("LLM status request failed.");
  }

  return response.json();
}

export async function listTools(): Promise<ToolManifest[]> {
  const response = await fetch(`${API_BASE_URL}/tools`);

  if (!response.ok) {
    throw new Error("Tool manifest request failed.");
  }

  const data = await response.json();
  return data.tools;
}

export async function runTool(
  toolName: string,
  input: Record<string, unknown>
): Promise<ToolRunResponse> {
  const response = await fetch(`${API_BASE_URL}/tools/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      tool_name: toolName,
      input
    })
  });

  if (!response.ok) {
    throw new Error("Tool execution failed.");
  }

  return response.json();
}
