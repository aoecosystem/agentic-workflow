---
description: Generate the System Architecture HTML from the approved Scope of Work. Refuses unless Stage is SOW_APPROVED.
---

Run the `build-architecture` skill. Verify Stage is `SOW_APPROVED`
first. Read `deliverables/scope-of-work/<slug>-sow.html` (Phase 1.5
Service Architecture, Phase 2 modules, Phase 4 data flow, Phase 5
events) and the empty `deliverables/architecture/template.html`
template. Generate the 7-section architecture HTML with a Mermaid
flowchart that compiles, classDef layer colors, and `&nbsp;` padded
nodes. Save to `deliverables/architecture/<slug>-architecture.html`
v1.0 and transition Stage to `ARCHITECTURE_DRAFT`. Present
`/review-architecture` and `/approve-architecture` next.
