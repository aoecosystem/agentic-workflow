---
description: Edit a specific section of the Project Brief. Bumps version, writes audit log. Re-opens an approved brief if Stage is BRIEF_APPROVED.
---

Run the `review-brief` skill. Verify Stage is `BRIEF_DRAFT` or
`BRIEF_APPROVED` first; if APPROVED, warn the user that this re-opens
the brief and confirm before proceeding. Show the 13-section menu (or
jump straight to the section the user passed as an argument), apply
the requested change, bump the file version (v1.0 → v1.1), save, and
append an audit log line in `SESSION-STATE.md`. Loop until the user
runs `/approve-brief` or types `exit`.

Templates are read-only. Only `DOCMENTS/<slug>-brief.html`
is editable.
