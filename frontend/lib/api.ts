export type AgentTask =
  | "draft_acceptance_criteria"
  | "decompose_epic"
  | "check_dor";

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

export type AgentResponse = {
  task: AgentTask;
  final_output: string | AcceptanceCriteriaOutput;
  trace: TraceEvent[];
  human_review_required: boolean;
  review_reason?: string | null;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function runAgent(task: AgentTask, input: string): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE_URL}/agent/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      task,
      input,
      context: {}
    })
  });

  if (!response.ok) {
    throw new Error("Agent request failed.");
  }

  return response.json();
}
