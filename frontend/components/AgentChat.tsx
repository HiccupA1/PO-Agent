"use client";

import { useState } from "react";

import type { AcceptanceCriteriaOutput, AgentResponse, AgentTask } from "../lib/api";
import { runAgent } from "../lib/api";
import { TracePanel } from "./TracePanel";

const taskOptions: AgentTask[] = [
  "draft_acceptance_criteria",
  "decompose_epic",
  "check_dor"
];

const sampleInputs = [
  "As a customer, I want to reset my password so that I can regain access to my account.",
  "Build invoice approval flow for finance team.",
  "Users should receive notifications when purchase orders are delayed."
];

function isAcceptanceCriteriaOutput(
  output: AgentResponse["final_output"]
): output is AcceptanceCriteriaOutput {
  return typeof output !== "string" && "acceptance_criteria" in output;
}

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

  function renderOutput() {
    if (!result) {
      return <p className="muted">Run the agent to generate a draft output.</p>;
    }

    if (!isAcceptanceCriteriaOutput(result.final_output)) {
      return (
        <>
          <pre>{result.final_output}</pre>
          <p className="review">
            Human review required: {result.human_review_required ? "Yes" : "No"}
          </p>
        </>
      );
    }

    const output = result.final_output;

    return (
      <div className="structured-output">
        <div className="story-block">
          <h3>Rewritten User Story</h3>
          <p>{output.rewritten_user_story}</p>
        </div>

        <div className="review-banner">
          <span>{output.human_review_required ? "Review Required" : "Review Optional"}</span>
          <p>{output.review_reason}</p>
        </div>

        <div className="dor-block">
          <div>
            <h3>Definition of Ready</h3>
            <p className="score">{output.definition_of_ready.score}%</p>
          </div>
          <div className="dor-columns">
            <div>
              <strong>Passed</strong>
              <ul>
                {output.definition_of_ready.passed.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <strong>Needs Work</strong>
              <ul>
                {output.definition_of_ready.failed.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <section>
          <h3>Acceptance Criteria</h3>
          <div className="criteria-list">
            {output.acceptance_criteria.map((criterion) => (
              <article className="criteria-card" key={criterion.id}>
                <strong>
                  {criterion.id}: {criterion.title}
                </strong>
                <p>
                  <b>Given</b> {criterion.given}
                </p>
                <p>
                  <b>When</b> {criterion.when}
                </p>
                <p>
                  <b>Then</b> {criterion.then}
                </p>
              </article>
            ))}
          </div>
        </section>

        <OutputList title="Edge Cases" items={output.edge_cases} />
        <OutputList title="Non-Functional Requirements" items={output.non_functional_requirements} />
        <OutputList title="Assumptions" items={output.assumptions} />
        <OutputList title="Clarification Questions" items={output.clarification_questions} />
      </div>
    );
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

        <label htmlFor="sample">Load sample</label>
        <select
          id="sample"
          defaultValue=""
          onChange={(event) => {
            if (event.target.value) {
              setInput(event.target.value);
            }
          }}
        >
          <option value="">Choose a sample input</option>
          {sampleInputs.map((sample, index) => (
            <option key={sample} value={sample}>
              Sample {index + 1}
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
        {renderOutput()}
      </section>

      <TracePanel trace={result?.trace ?? []} />
    </div>
  );
}

function OutputList({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section>
      <h3>{title}</h3>
      <ul className="output-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
