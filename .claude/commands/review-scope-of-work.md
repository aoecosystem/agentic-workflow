---
description: Edit a specific phase of the Scope of Work. Bumps version, writes audit log. Re-opens an approved SoW if Stage is SOW_APPROVED.
---

Run the `review-scope-of-work` skill. Verify Stage is `DOCS_DRAFT` or
`DOCS_DRAFT`; if APPROVED, warn that this re-opens the SoW and
confirm. Show the 10-phase menu (or jump to the phase passed as an
argument), apply the change, bump version, save, append audit log.
Loop until the user runs `/approve-scope-of-work` or types `exit`.

Universal services S1-S6 must remain intact in Phase 2.
