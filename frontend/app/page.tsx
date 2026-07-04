import { AgentChat } from "../components/AgentChat";
import { BacklogPreview } from "../components/BacklogPreview";
import { ToolExplorer } from "../components/ToolExplorer";

export default function Home() {
  return (
    <main>
      <header className="page-header">
        <p>Interview POC</p>
        <h1>PO Agent - Product Owner Backlog Architect</h1>
      </header>

      <div className="page-grid">
        <AgentChat />
        <BacklogPreview />
      </div>

      <ToolExplorer />
    </main>
  );
}
