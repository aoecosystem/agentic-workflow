---
description: Edit a section of the Database Diagram. Bumps version, writes audit log. Re-opens an approved database if Stage is DATABASE_APPROVED.
---

Run the `review-database` skill. Verify Stage is `DOCS_DRAFT` or
`DOCS_DRAFT`; if APPROVED, warn and confirm re-open. Show the
6-section menu (or jump to the section passed as argument), apply the
change, bump version, save, append audit log. Mermaid `erDiagram`
must remain syntactically valid after Section 6 edits. Loop until
`/approve-database` or `exit`.
