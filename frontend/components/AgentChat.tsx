"use client";

import { useState } from "react";

import type { AgentResponse, AgentTask } from "../lib/api";
import { runAgent } from "../lib/api";
import { TracePanel } from "./TracePanel";

const taskOptions: AgentTask[] = [
  "draft_acceptance_criteria",
  "decompose_epic",
  "check_dor"
];

export function AgentChat() {
  const [task, setTask] = useState<AgentTask>("draft_acceptance_criteria");
  const [input, setInput] = useState(
    "As a user, I want to reset my password so that I can regain account access without contacting support."
  );
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setIsRunning(true);
    setError(null);

    try {
      const response = await runAgent(task, input);
      setResult(response);
    } catch {
      setError("Could not reach the backend. Confirm FastAPI is running on port 8000.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="agent-grid">
      <section className="panel control-panel">
        <label htmlFor="task">Task</label>
        <select
          id="task"
          value={task}
          onChange={(event) => setTask(event.target.value as AgentTask)}
        >
          {taskOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>

        <label htmlFor="input">Input</label>
        <textarea
          id="input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={8}
        />

        <button type="button" onClick={handleRun} disabled={isRunning || !input.trim()}>
          {isRunning ? "Running..." : "Run Agent"}
        </button>
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="panel output-panel">
        <h2>Output</h2>
        {result ? (
          <>
            <pre>{result.final_output}</pre>
            <p className="review">
              Human review required: {result.human_review_required ? "Yes" : "No"}
            </p>
          </>
        ) : (
          <p className="muted">Run the agent to generate a draft output.</p>
        )}
      </section>

      <TracePanel trace={result?.trace ?? []} />
    </div>
  );
}
