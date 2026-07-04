export type AgentTask =
  | "draft_acceptance_criteria"
  | "decompose_epic"
  | "check_dor";

export type TraceEvent = {
  step: number;
  type: string;
  message: string;
  tool_name?: string | null;
};

export type AgentResponse = {
  task: AgentTask;
  final_output: string;
  trace: TraceEvent[];
  human_review_required: boolean;
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
