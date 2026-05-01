---
description: Run the architecture quality gate and lock it. Transitions Stage from ARCHITECTURE_DRAFT to ARCHITECTURE_APPROVED.
---

Run the `approve-architecture` skill. Refuse unless Stage is
`ARCHITECTURE_DRAFT`. Verify the quality gate: all 7 sections present,
no raw `{{...}}`, cover-sub replaced, every SoW Phase 2 service
appears in Section 2 inventory and Section 7 Mermaid diagram,
universal S1-S6 intact, Mermaid compiles. On success, transition to
`ARCHITECTURE_APPROVED`, append audit log, present `/build-database`
next. On failure, list every failing item.
