---
description: Generate the Scope of Work HTML from the approved Project Brief. Refuses unless Stage is BRIEF_APPROVED.
---

Run the `build-scope-of-work` skill. Verify Stage is `BRIEF_APPROVED`
in `state/SESSION-STATE.md` before doing anything. Read
`deliverables/brief/<slug>-brief.html` and expand it into the
canonical 10-phase Scope of Work using `scope-of-work-template.html`
as the structural reference. Universal services S1-S6 stay intact;
project services start at S7. Phase 5.5 derives from brief Section 6.
Phase 7 Page Inventory generated last.

Save to `deliverables/scope-of-work/<slug>-sow.html` v1.0 and transition
Stage to `SOW_DRAFT`. Present `/review-scope-of-work <phase>` and
`/approve-scope-of-work` as next valid commands.
