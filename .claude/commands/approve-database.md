---
description: Run the database quality gate and lock it. Transitions Stage from DATABASE_DRAFT to DATABASE_APPROVED.
---

Run the `approve-database` skill. Refuse unless Stage is
`DATABASE_DRAFT`. Verify the quality gate: all 6 sections present, no
raw `{{...}}`, cover-sub replaced, every SoW Phase 3 table appears in
Section 2, every relationship references existing entities, Mermaid
`erDiagram` compiles, every entity has a PK. On success, transition
to `DATABASE_APPROVED`, append audit log, present
`/build-infrastructure` next. On failure, list every failing item.
