---
description: Generate TASKS.md from SCOPE.md (sole writer of TASKS.md)
---

Run the `parse-scope` skill. Read `state/SCOPE.md` (and `.pipeline/features/requirements/` if `reqops` ran first), then generate or regenerate `state/TASKS.md` with one executable task block per unit of work, grouped by feature, with dependency edges, traceability refs, agent assignments, attempt budget, acceptance criteria, and design fields where applicable. $ARGUMENTS
