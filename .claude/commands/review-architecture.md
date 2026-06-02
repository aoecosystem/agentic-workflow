---
description: Edit a section of the System Architecture. Bumps version, writes audit log. Re-opens an approved architecture if Stage is ARCHITECTURE_APPROVED.
---

Run the `review-architecture` skill. Verify Stage is
`DOCS_DRAFT` or `DOCS_DRAFT`; if APPROVED, warn
and confirm re-open. Show the 7-section menu (or jump to the section
passed as argument), apply the change, bump version, save, append
audit log. Universal services S1-S6 must remain in Section 2.
Mermaid block must remain syntactically valid after Section 7 edits.
Loop until `/approve-architecture` or `exit`.
