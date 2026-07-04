const backlogItems = [
  {
    id: "POA-101",
    title: "Draft acceptance criteria from a raw user story",
    status: "Ready for refinement",
    priority: "High"
  },
  {
    id: "POA-102",
    title: "Decompose a customer onboarding epic",
    status: "Discovery",
    priority: "Medium"
  },
  {
    id: "POA-103",
    title: "Check backlog item readiness before sprint planning",
    status: "Draft",
    priority: "Medium"
  }
];

export function BacklogPreview() {
  return (
    <section className="panel">
      <h2>Backlog Preview</h2>
      <div className="backlog-list">
        {backlogItems.map((item) => (
          <article key={item.id} className="backlog-item">
            <div>
              <strong>{item.id}</strong>
              <p>{item.title}</p>
            </div>
            <small>
              {item.status} | {item.priority}
            </small>
          </article>
        ))}
      </div>
    </section>
  );
}
