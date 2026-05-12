---
description: Generate the Infrastructure Diagram HTML from the approved Database + Architecture + SoW. Refuses unless Stage is DATABASE_APPROVED.
---

Run the `build-infrastructure` skill. Verify Stage is
`DATABASE_APPROVED` first. Read `<slug>-scope-of-work.html` (Phase 6
Tech Stack, Phase 8 environments, Phase 9 folder structure, Phase
10.7 NFRs), brief Section 8 Integrations, plus the architecture and
database diagrams. Generate the 9-section infrastructure HTML:
Environments, Hosting & Compute, Database/Storage/Cache, Network &
Domains, External Services, Security & Secrets, Backup & DR, CI/CD,
Topology Mermaid diagram. Save to
`deliverables/infrastructure/<slug>-infrastructure.html` v1.0 and
transition Stage to `INFRASTRUCTURE_DRAFT`. Present
`/review-infrastructure` and `/approve-infrastructure` next.
