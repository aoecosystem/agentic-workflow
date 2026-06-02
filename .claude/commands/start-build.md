---
description: Kick off the Orchestrator scheduler loop (Builder + QA) from TASKS.md
---

Run the `orchestrate` skill. Read `SESSION-STATE/TASKS.md`, build the dependency graph, identify ready chains, fan out independent feature groups to parallel Builder runs, and run the continuous scheduler loop (Builder → QA → next task) until every task is `done` or explicitly blocked on human input. Respect concurrency rules: single-writer per shared file, file ownership per Builder, and the Orchestrator safety-net integrity checks every tick. $ARGUMENTS
