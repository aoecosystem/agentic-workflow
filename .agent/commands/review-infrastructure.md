---
description: Edit a section of the Infrastructure Diagram. Bumps version, writes audit log. Re-opens if Stage is INFRASTRUCTURE_APPROVED or COMPLETE.
---

Run the `review-infrastructure` skill. Verify Stage is
`INFRASTRUCTURE_DRAFT`, `INFRASTRUCTURE_APPROVED`, or `COMPLETE`. If
the latter two, warn the user that re-opening will revert the
project from COMPLETE state. Show the 9-section menu (or jump to the
section passed as argument), apply the change, bump version, save,
append audit log. Mermaid `flowchart` must remain syntactically valid
after Section 9 edits. Loop until `/approve-infrastructure` or
`exit`.
