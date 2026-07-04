"use client";

import { useEffect, useMemo, useState } from "react";

import type { ToolManifest, ToolRunResponse } from "../lib/api";
import { listTools, runTool } from "../lib/api";

export function ToolExplorer() {
  const [tools, setTools] = useState<ToolManifest[]>([]);
  const [selectedTool, setSelectedTool] = useState("");
  const [toolInput, setToolInput] = useState('{\n  "query": "purchase order",\n  "limit": 5\n}');
  const [result, setResult] = useState<ToolRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    listTools()
      .then((toolList) => {
        setTools(toolList);
        setSelectedTool(toolList[0]?.tool_name ?? "");
      })
      .catch(() => setError("Could not load tool manifests. Confirm the backend is running."));
  }, []);

  const selectedManifest = useMemo(
    () => tools.find((tool) => tool.tool_name === selectedTool),
    [selectedTool, tools]
  );

  async function handleRunTool() {
    setIsRunning(true);
    setError(null);

    try {
      const parsedInput = JSON.parse(toolInput) as Record<string, unknown>;
      const response = await runTool(selectedTool, parsedInput);
      setResult(response);
    } catch {
      setError("Tool run failed. Check that the input is valid JSON and the backend is running.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <section className="panel tool-explorer">
      <div className="tool-header">
        <div>
          <h2>MCP-Style Tool Explorer</h2>
          <p className="muted">Mock tool manifests and a small debug runner.</p>
        </div>
      </div>

      <div className="tool-grid">
        <div className="tool-list">
          {tools.map((tool) => (
            <button
              className={tool.tool_name === selectedTool ? "tool-button active" : "tool-button"}
              key={tool.tool_name}
              type="button"
              onClick={() => setSelectedTool(tool.tool_name)}
            >
              {tool.display_name}
            </button>
          ))}
        </div>

        <div className="tool-detail">
          {selectedManifest ? (
            <>
              <h3>{selectedManifest.display_name}</h3>
              <p>{selectedManifest.description}</p>
              <small>{selectedManifest.tool_name}</small>

              <div className="schema-grid">
                <SchemaBlock title="Input Schema" schema={selectedManifest.input_schema} />
                <SchemaBlock title="Output Schema" schema={selectedManifest.output_schema} />
              </div>

              <label htmlFor="tool-input">Tool input</label>
              <textarea
                id="tool-input"
                rows={6}
                value={toolInput}
                onChange={(event) => setToolInput(event.target.value)}
              />
              <button type="button" disabled={!selectedTool || isRunning} onClick={handleRunTool}>
                {isRunning ? "Running Tool..." : "Run Tool"}
              </button>
            </>
          ) : (
            <p className="muted">Tool manifests will appear here.</p>
          )}

          {error ? <p className="error">{error}</p> : null}
          {result ? (
            <div className="tool-result">
              <h3>Tool Output</h3>
              <pre>{JSON.stringify(result.output, null, 2)}</pre>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function SchemaBlock({ title, schema }: { title: string; schema: Record<string, string> }) {
  return (
    <div className="schema-block">
      <strong>{title}</strong>
      <ul>
        {Object.entries(schema).map(([key, value]) => (
          <li key={key}>
            {key}: {value}
          </li>
        ))}
      </ul>
    </div>
  );
}
