---
description: Run the tasks quality gate and lock TASKS.md before /start-build. Transitions Stage from TASKS_GENERATED to TASKS_APPROVED.
---

Run the `approve-tasks` skill. Refuse unless Stage is `TASKS_GENERATED`.
Verify acceptance criteria present, no orphan/circular dependencies, no
ambiguous file ownership, all tasks `pending`. On success, transition
to `TASKS_APPROVED` and present `/start-build` next. On failure, list
every failing item.
