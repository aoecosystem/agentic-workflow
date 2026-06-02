---
description: Generate the Scope of Work HTML from the approved Project Brief. Refuses unless Stage is BRIEF_APPROVED.
---

Run the `build-scope-of-work` skill. Verify Stage is `BRIEF_APPROVED`
in `SESSION-STATE/SESSION-STATE.md` before doing anything. Read
`DOCMENTS/<slug>-brief.html` and expand it into the
canonical 10-phase Scope of Work using `scope-of-work-template.html`
as the structural reference. Universal services S1-S6 stay intact;
project services start at S7. Phase 5.5 derives from brief Section 6.
Phase 7 Page Inventory generated last.

Save to `DOCMENTS/<slug>-sow.html` v1.0 and transition
Stage to `DOCS_DRAFT`. Present `/review-scope-of-work <phase>` and
`/approve-scope-of-work` as next valid commands.
