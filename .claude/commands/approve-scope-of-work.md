---
description: Run the SoW quality gate and lock it. Transitions Stage from SOW_DRAFT to SOW_APPROVED.
---

Run the `approve-scope-of-work` skill. Refuse unless Stage is
`SOW_DRAFT`. Verify the quality gate: all 10 phases present, no raw
`{{...}}`, Page Inventory has rows for every platform from brief
Section 3, universal services S1-S6 intact, slug + cover match. On
success, transition Stage to `SOW_APPROVED`, append audit log, and
present `/build-architecture` as the next command. On failure, list
every failing item and leave Stage at `SOW_DRAFT`.

Never auto-trigger `/build-architecture`.
