# Audit TASKS.md

**When to use:** `parse scope` finished and `TASKS.md` is sitting with
every task `pending`. Run this before `start build` to catch planning
mistakes early.

---

## Prompt

```
Read TASKS.md and SCOPE.md.

Audit the generated task list against five lenses:

1. **Coverage** — for each feature in SCOPE.md section 5, list the task
   IDs that cover it. Flag any feature with zero tasks, or with task
   coverage that obviously misses a screen / endpoint / model.

2. **Dependency order** — does the dependency graph respect real
   constraints? Specifically:
     - Scaffold (TASK-000) before everything.
     - DB schema before any task that reads/writes that schema.
     - Auth before any task that requires authenticated routes.
     - API task before its consuming UI task.
   Flag violations with task IDs.

3. **Parallelism** — list the independent chains the orchestrator could
   run in parallel. Flag any chain that is artificially serial because
   of a shared file that could be split (e.g. one big types.ts that
   blocks five features).

4. **Acceptance criteria realism** — pick three random tasks. For each,
   answer: could a senior Builder finish this in one focused session
   and could QA actually verify these criteria objectively? If no, say
   what to tighten.

5. **Inferred / blocked items** — list every task that has 'INFERRED:'
   in its notes, or that should probably be 'blocked' until the user
   provides missing info (MCP URL, design source, ambiguous spec).

Return:
  - Coverage matrix (feature → task IDs)
  - List of dependency-order violations with proposed fixes
  - List of independent chains
  - 3-task realism check
  - List of items needing user input before build starts

Do not edit TASKS.md. I'll apply edits or rerun parse-scope.
```

## Tips

- If the audit surfaces dependency-order issues, **fix `SCOPE.md` first
  and rerun `parse scope`** rather than hand-editing tasks. Tasks are
  derived state.
- If the audit flags missing MCP URLs for UI features, add them to
  `SCOPE.md` and rerun `parse scope` before `start build`.
