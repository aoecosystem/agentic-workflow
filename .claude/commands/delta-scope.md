---
description: Re-plan when SCOPE.md changes after TASKS.md already has tasks in any non-pending state
---

Run the `delta-scope` skill. Compute the before/after requirement maps, classify each change (ADDED / REMOVED / CHANGED / UNCHANGED), map impacts to existing tasks, produce a human-reviewable delta report with `TASK-DELTA-XX` / `TASK-REMOVE-XX` proposals, and wait for user confirmation before editing `SESSION-STATE/TASKS.md`. Never silently edit `done` or `in-progress` tasks. $ARGUMENTS
