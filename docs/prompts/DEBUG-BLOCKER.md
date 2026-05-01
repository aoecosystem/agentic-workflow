# Debug a blocked task

**When to use:** A task is `blocked` and the blocker reason isn't
self-explanatory. You want a focused diagnosis without unblocking
everything else.

---

## Prompt

```
TASK-{ID} is blocked. Read its full task block in TASKS.md, including
QA notes, Attempts, and Attempt log. Also read:
  - The relevant feature section in SCOPE.md
  - memory/ARCHITECTURE.md
  - memory/DECISIONS.md
  - Any MCP cache file referenced in the task block

Diagnose the blocker. Return:

1. **Root cause** — one sentence describing what is actually preventing
   progress (not just the surface symptom).
2. **Evidence** — file:line references or specific quote from the task
   block / scope / cache that proves the root cause.
3. **Resolution path** — three options ordered cheapest first:
     a. quick fix (no scope change, no design rework)
     b. medium fix (minor SCOPE.md tweak or MCP refresh)
     c. structural fix (delta-scope, redesign, drop the feature)
4. **Recommendation** — which option to pick and why.
5. **Side effects** — any task IDs that would be unblocked or affected
   by the recommended option.

Do not modify TASKS.md or any code. Only produce the diagnosis.
```

## Tips

- If the diagnosis recommends a SCOPE.md change, run `delta scope`
  next, not `parse scope`.
- If it recommends `refresh mcp`, do that before retrying the build —
  Builders should not pull from a stale cache after an upstream change.
- If a task has hit `Max attempts`, the blocker is now an
  `attempt-budget-exhausted` block — the diagnosis should suggest
  scope reduction, not another retry.
