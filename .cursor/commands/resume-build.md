---
description: Resume the Orchestrator scheduler loop from the current task states
---

Run the `orchestrate` skill in resume mode. Re-read `state/TASKS.md` and pick up where the last session left off: `needs-fix` → Builder, `in-review` → QA, ready `pending` → Builder, blocked → surface. Respect attempt budgets (`Attempts` / `Max attempts`) and the concurrency rules. $ARGUMENTS
