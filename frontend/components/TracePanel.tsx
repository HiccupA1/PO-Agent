import type { TraceEvent } from "../lib/api";

type TracePanelProps = {
  trace: TraceEvent[];
};

export function TracePanel({ trace }: TracePanelProps) {
  return (
    <section className="panel">
      <h2>Agent Trace</h2>
      {trace.length === 0 ? (
        <p className="muted">Trace steps will appear after the agent runs.</p>
      ) : (
        <ol className="trace-list">
          {trace.map((event) => (
            <li key={event.step}>
              <span>{event.step}</span>
              <div>
                <strong>{event.type}</strong>
                <p>{event.message}</p>
                {event.tool_name ? <small>{event.tool_name}</small> : null}
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
