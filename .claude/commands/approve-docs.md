---
description: Run quality gates on all 4 generated documents (SoW, Architecture, Database, Infrastructure) and transition Stage from DOCS_DRAFT to DOCS_COMPLETE.
---

Run the `approve-docs` skill. Read `SESSION-STATE/SESSION-STATE.md` and
refuse unless Stage is `DOCS_DRAFT`.

Quality-gate all 4 documents:
- `DOCMENTS/<slug>-scope-of-work.html` — all 10 phases, no raw placeholders
- `DOCMENTS/<slug>-system-architecture.html` — all 9 sections, 3 Mermaid blocks compile
- `DOCMENTS/<slug>-database-diagram.html` — all 6 sections, ERD compiles
- `DOCMENTS/<slug>-infrastructure-diagram.html` — all 9 sections, topology compiles

If any gate fails — list failures grouped by document, leave Stage at
DOCS_DRAFT, recommend the matching /review-* command.

If all pass — transition Stage to DOCS_COMPLETE, mark all artifacts
approved, append audit log, print completion summary.
