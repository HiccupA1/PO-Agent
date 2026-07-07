"use client";

import { useEffect, useState } from "react";

import type {
  AcceptanceCriteriaOutput,
  AgentRuntimeMetadata,
  AgentResponse,
  AgentTask,
  DORCheckOutput,
  EpicDecompositionOutput,
  InvestCheck,
  LLMStatus,
  PrioritizationOutput,
  RuntimeMode
} from "../lib/api";
import { getLLMStatus, runAgent } from "../lib/api";
import { TracePanel } from "./TracePanel";

const taskOptions: AgentTask[] = [
  "draft_acceptance_criteria",
  "decompose_epic",
  "check_dor",
  "prioritize_backlog"
];

const sampleInputs = [
  "As a customer, I want to reset my password so that I can regain access to my account.",
  "Build invoice approval flow for finance team.",
  "Users should receive notifications when purchase orders are delayed.",
  "Build purchase order approval system for enterprise procurement teams.",
  "Improve procurement experience.",
  "As a finance manager, I want to approve or reject purchase orders so that procurement spend is controlled.",
  "Prioritize these:\n1. Add purchase order approval workflow\n2. Add supplier onboarding form\n3. Add delayed PO notification\n4. Add invoice matching dashboard\n5. Add admin audit log export"
];

function isAcceptanceCriteriaOutput(
  output: AgentResponse["final_output"]
): output is AcceptanceCriteriaOutput {
  return typeof output !== "string" && "acceptance_criteria" in output;
}

function isEpicDecompositionOutput(
  output: AgentResponse["final_output"]
): output is EpicDecompositionOutput {
  return typeof output !== "string" && "decomposed_user_stories" in output;
}

function isDORCheckOutput(output: AgentResponse["final_output"]): output is DORCheckOutput {
  return typeof output !== "string" && "dor_score" in output;
}

function isPrioritizationOutput(
  output: AgentResponse["final_output"]
): output is PrioritizationOutput {
  return typeof output !== "string" && "ranked_items" in output;
}

export function AgentChat() {
  const [task, setTask] = useState<AgentTask>("draft_acceptance_criteria");
  const [input, setInput] = useState(
    "As a user, I want to reset my password so that I can regain account access without contacting support."
  );
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runtimeMode, setRuntimeMode] = useState<RuntimeMode>("mock");
  const [llmStatus, setLlmStatus] = useState<LLMStatus | null>(null);

  useEffect(() => {
    getLLMStatus()
      .then(setLlmStatus)
      .catch(() => setLlmStatus(null));
  }, []);

  async function handleRun() {
    setIsRunning(true);
    setError(null);

    try {
      const response = await runAgent(task, input, runtimeMode);
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
      if (isEpicDecompositionOutput(result.final_output)) {
        return <EpicDecompositionView output={result.final_output} />;
      }

      if (isDORCheckOutput(result.final_output)) {
        return <DORCheckView output={result.final_output} />;
      }

      if (isPrioritizationOutput(result.final_output)) {
        return <PrioritizationView output={result.final_output} />;
      }

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
        <div className="runtime-panel">
          <h2>Runtime</h2>
          <p className="muted">
            Mock mode is deterministic and local. LLM-assisted mode attempts a provider call and falls back safely.
          </p>
          <label htmlFor="runtime">Mode</label>
          <select
            id="runtime"
            value={runtimeMode}
            onChange={(event) => setRuntimeMode(event.target.value as RuntimeMode)}
          >
            <option value="mock">mock</option>
            <option value="llm">llm-assisted</option>
          </select>
          {llmStatus ? (
            <small>
              {llmStatus.message} Provider: {llmStatus.provider || "mock"}. Model:{" "}
              {llmStatus.model || "n/a"}. Timeout: {llmStatus.timeout_seconds ?? "n/a"}s.
              Configured: {llmStatus.configured ? "Yes" : "No"}.
            </small>
          ) : (
            <small>LLM status unavailable until the backend is running.</small>
          )}
        </div>

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
        {result ? <RuntimeMetadataView runtime={result.runtime} /> : null}
        {renderOutput()}
      </section>

      <TracePanel trace={result?.trace ?? []} />
    </div>
  );
}

function RuntimeMetadataView({ runtime }: { runtime: AgentRuntimeMetadata }) {
  return (
    <div className="runtime-result">
      <span>Requested: {runtime.mode_requested}</span>
      <span>Used: {runtime.mode_used}</span>
      <span>Source: {runtime.generation_source}</span>
      <span>Provider: {runtime.provider}</span>
      {runtime.model ? <span>Model: {runtime.model}</span> : null}
      {runtime.timeout_seconds ? <span>Timeout: {runtime.timeout_seconds}s</span> : null}
      <span>Provider configured: {runtime.provider_configured ? "Yes" : "No"}</span>
      <span>Fallback: {runtime.fallback_used ? "Yes" : "No"}</span>
      {runtime.fallback_reason ? <span>{runtime.fallback_reason}</span> : null}
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

function EpicDecompositionView({ output }: { output: EpicDecompositionOutput }) {
  return (
    <div className="structured-output">
      <div className="story-block">
        <h3>Epic Summary</h3>
        <p>{output.epic_summary}</p>
      </div>

      <ReviewBanner required={output.human_review_required} reason={output.review_reason} />

      <section>
        <h3>User Stories</h3>
        <div className="story-card-list">
          {output.decomposed_user_stories.map((story) => (
            <article className="story-card" key={story.id}>
              <div className="story-card-header">
                <div>
                  <strong>
                    {story.id}: {story.title}
                  </strong>
                  <p>{story.user_story}</p>
                </div>
                <div className="badge-row">
                  <span className="badge">{story.priority}</span>
                  <span className="badge">Size {story.estimated_complexity}</span>
                </div>
              </div>

              <div className="detail-grid">
                <div>
                  <small>Persona</small>
                  <p>{story.persona}</p>
                </div>
                <div>
                  <small>Business Value</small>
                  <p>{story.business_value}</p>
                </div>
              </div>

              <OutputList title="Acceptance Criteria Preview" items={story.acceptance_criteria_preview} />
              <OutputList title="Dependencies" items={story.dependencies} />
              <OutputList title="Risks" items={story.risks} />
              <InvestChecklist invest={story.invest_check} />
            </article>
          ))}
        </div>
      </section>

      <section>
        <h3>Release Slices</h3>
        <div className="slice-list">
          {output.release_slices.map((slice) => (
            <article className="slice-card" key={slice.name}>
              <strong>{slice.name}</strong>
              <p>{slice.rationale}</p>
              <small>{slice.stories.join(", ")}</small>
            </article>
          ))}
        </div>
      </section>

      <OutputList title="Open Questions" items={output.open_questions} />
    </div>
  );
}

function DORCheckView({ output }: { output: DORCheckOutput }) {
  return (
    <div className="structured-output">
      <div className="story-block">
        <h3>Item Summary</h3>
        <p>{output.item_summary}</p>
      </div>

      <ReviewBanner required={output.human_review_required} reason={output.review_reason} />

      <div className="dor-block">
        <div className="dor-score-row">
          <div>
            <h3>Definition of Ready</h3>
            <p className="score">{output.dor_score}%</p>
          </div>
          <span className={`status-badge status-${output.status.toLowerCase().replace(" ", "-")}`}>
            {output.status}
          </span>
        </div>
      </div>

      <section>
        <h3>Passed Checks</h3>
        <div className="check-list">
          {output.passed_checks.map((item) => (
            <article className="check-card passed" key={item.check}>
              <strong>{item.check}</strong>
              <p>{item.reason}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h3>Failed Checks</h3>
        <div className="check-list">
          {output.failed_checks.map((item) => (
            <article className="check-card failed" key={item.check}>
              <strong>{item.check}</strong>
              <p>{item.reason}</p>
              <small>{item.recommendation}</small>
            </article>
          ))}
        </div>
      </section>

      <OutputList title="Risk Flags" items={output.risk_flags} />
      <OutputList title="Recommended Next Actions" items={output.recommended_next_actions} />
    </div>
  );
}

function ReviewBanner({ required, reason }: { required: boolean; reason: string }) {
  return (
    <div className="review-banner">
      <span>{required ? "Review Required" : "Review Optional"}</span>
      <p>{reason}</p>
    </div>
  );
}

function InvestChecklist({ invest }: { invest: InvestCheck }) {
  const checks = [
    { label: "Independent", passed: invest.independent },
    { label: "Negotiable", passed: invest.negotiable },
    { label: "Valuable", passed: invest.valuable },
    { label: "Estimable", passed: invest.estimable },
    { label: "Small", passed: invest.small },
    { label: "Testable", passed: invest.testable }
  ];

  return (
    <section>
      <h3>INVEST Check</h3>
      <div className="invest-grid">
        {checks.map((check) => (
          <span className={check.passed ? "invest-pass" : "invest-warn"} key={check.label}>
            {check.label}
          </span>
        ))}
      </div>
      <OutputList title="INVEST Notes" items={invest.notes} />
    </section>
  );
}

function PrioritizationView({ output }: { output: PrioritizationOutput }) {
  const weights = output.scoring_model.weights;
  const weightEntries = [
    ["Reach", weights.reach],
    ["Impact", weights.impact],
    ["Confidence", weights.confidence],
    ["Effort", weights.effort],
    ["Risk Reduction", weights.risk_reduction],
    ["Readiness", weights.readiness]
  ];

  return (
    <div className="structured-output">
      <div className="story-block">
        <h3>Prioritization Summary</h3>
        <p>{output.prioritization_summary}</p>
      </div>

      <ReviewBanner required={output.human_review_required} reason={output.review_reason} />

      <section className="scoring-model">
        <h3>{output.scoring_model.name}</h3>
        <p>{output.scoring_model.description}</p>
        <div className="weight-grid">
          {weightEntries.map(([label, value]) => (
            <span key={label}>
              <strong>{value}%</strong>
              {label}
            </span>
          ))}
        </div>
      </section>

      <section>
        <h3>Ranked Backlog</h3>
        <div className="ranked-list">
          {output.ranked_items.map((item) => (
            <article className="ranked-card" key={item.id}>
              <div className="ranked-header">
                <div>
                  <strong>
                    #{item.rank} {item.title}
                  </strong>
                  <p>{item.rationale}</p>
                </div>
                <div className="score-pill">
                  <span>{item.weighted_score}</span>
                  <small>{item.priority}</small>
                </div>
              </div>

              <div className="metric-grid">
                <Metric label="Reach" value={item.reach} />
                <Metric label="Impact" value={item.impact} />
                <Metric label="Confidence" value={item.confidence} />
                <Metric label="Effort" value={item.effort} />
                <Metric label="Risk Reduction" value={item.risk_reduction} />
                <Metric label="Readiness" value={item.readiness} suffix="%" />
              </div>

              <OutputList title="Tradeoffs" items={item.tradeoffs} />
              <OutputList title="Dependencies" items={item.dependencies} />
              <div className="next-action">
                <strong>Recommended next action</strong>
                <p>{item.recommended_next_action}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <div className="summary-grid">
        <OutputList title="Quick Wins" items={output.quick_wins} />
        <OutputList title="High-Risk Items" items={output.high_risk_items} />
        <OutputList title="Blocked Items" items={output.blocked_items} />
        <OutputList title="Recommended Sprint Candidates" items={output.recommended_sprint_candidates} />
      </div>
    </div>
  );
}

function Metric({ label, value, suffix = "" }: { label: string; value: number; suffix?: string }) {
  return (
    <div>
      <small>{label}</small>
      <strong>
        {value}
        {suffix}
      </strong>
    </div>
  );
}
