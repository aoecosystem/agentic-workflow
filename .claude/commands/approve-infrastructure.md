---
description: Final approval. Locks Infrastructure and moves the project to COMPLETE.
---

Run the `approve-infrastructure` skill. Refuse unless Stage is
`INFRASTRUCTURE_DRAFT`. Verify the quality gate: all 9 sections
present, no raw `{{...}}` in critical fields (providers,
integrations), cover-sub replaced, environments cover at least
Local/Dev/Staging/Prod, every brief Section 8 integration appears in
Section 5 and Section 9 topology, Mermaid `flowchart` compiles. On
success, transition Stage in two steps: INFRASTRUCTURE_DRAFT →
INFRASTRUCTURE_APPROVED → COMPLETE, append two audit log lines, and
print the completion summary listing all 5 approved documents. On
failure, list every failing item.

The project is done after this skill runs. No auto-trigger.
