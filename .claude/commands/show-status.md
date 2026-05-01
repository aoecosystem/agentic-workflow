---
description: Summarize TASKS.md status counts and surface any blocked tasks
---

Read `state/TASKS.md`. Run `scripts/update-task-counts.py` if the Build progress table looks stale. Output a terse summary:

- total tasks by status (pending, in-progress, in-review, done, needs-fix, blocked, obsolete)
- any `blocked` tasks with their blocker reason
- any task with `Attempts >= Max attempts` still unresolved
- next ready tasks (pending with satisfied `Depends on:`)

Do not change any file. Do not invoke Builder or QA. $ARGUMENTS
