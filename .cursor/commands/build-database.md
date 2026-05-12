---
description: Generate the Database Diagram HTML from the approved Architecture + SoW. Refuses unless Stage is ARCHITECTURE_APPROVED.
---

Run the `build-database` skill. Verify Stage is
`ARCHITECTURE_APPROVED` first. Read `<slug>-scope-of-work.html`
(especially Phase 3 Database Schemas), `<slug>-system-architecture.html`,
and `deliverables/database/template.html` template. Generate the
6-section database HTML: Schema Overview, Entity Definitions (one
block per entity with column tables), Relationships, Indexes,
Migration & Versioning, ERD Mermaid diagram. Save to
`deliverables/database/<slug>-database.html` v1.0 and transition
Stage to `DATABASE_DRAFT`. Present `/review-database` and
`/approve-database` next.
