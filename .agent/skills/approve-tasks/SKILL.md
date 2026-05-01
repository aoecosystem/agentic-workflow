---
name: approve-tasks
description: Run the tasks quality gate and lock TASKS.md before building. Verifies every task has acceptance criteria, dependency order is valid, file ownership is unambiguous, no orphan dependencies, no circular dependencies. Transitions Stage from TASKS_GENERATED to TASKS_APPROVED. Trigger on `/approve-tasks`. Refuses if the gate fails.
---

# Skill: approve-tasks

**Trigger:** `/approve-tasks`

**Purpose:** Run the task graph quality gate, then transition Stage from
`TASKS_GENERATED` to `TASKS_APPROVED`. Unlocks `/start-build`.

---

## Manual-edit detection (RUN FIRST)

Before any operation, follow the **Manual Edit Protocol** in `AGENTS.md`:
compute SHA-256 of `state/TASKS.md` and `state/SCOPE.md`, compare to
stored hashes. On drift, ask the user to accept (bump version + audit
log) or cancel before proceeding.

---

## Stage gate

1. Read `state/SESSION-STATE.md`. Locate `Stage:`.
2. If `Stage` is not `TASKS_GENERATED`, refuse:
   > "Approve is only valid from `TASKS_GENERATED`. Current: `<STAGE>`.
   > Run `/status` for next valid commands. To reach `TASKS_GENERATED`,
   > run `/parse-scope` (after `/import-docs` populates state/SCOPE.md)."
   Leave Stage unchanged.

---

## Quality gate (BLOCKING)

Read `state/TASKS.md`. Verify:

1. **Every task has acceptance criteria.** Each task block contains at
   least one `[ ]` checkbox under "Acceptance:".
2. **Every task has Status: pending.** No tasks should already be in
   progress before approval.
3. **No orphan dependencies.** Every `Depends-on:` reference points to
   a real task ID.
4. **No circular dependencies.** Build the dep graph and verify it's a
   DAG (no cycles).
5. **No ambiguous file ownership.** Each file path appears in at most
   one task's "Files:" section.
6. **All tasks have a builder hint** (`Builder: <hint>`) — orchestrator
   uses this to decide which builder picks it up.
7. **Architecture style consistency.** Tasks reference folder structure
   matching `deliverables/architecture/styles/<style>.md` (no monolith
   tasks if architecture is microservices, etc.).

If any check fails, list every failing item, leave Stage at
`TASKS_GENERATED`, recommend manual edits or `/parse-scope` regeneration.

---

## Transition

1. Update `state/SESSION-STATE.md`:
   - `Stage:` → `TASKS_APPROVED`
   - `Last skill:` → `approve-tasks`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /start-build to begin parallel build with orchestrator + builders + QA.`
   - Artifacts list: mark `state/TASKS.md` approved with date.
2. Append audit log:
   ```
   <ISO>  approve-tasks  TASKS_GENERATED → TASKS_APPROVED  <N> tasks locked
   ```

---

## Confirm + hand off

```
TASKS.md approved. <N> tasks locked.

Next valid commands:

  /start-build
    Begin parallel build with Orchestrator + Builders + QA loop.

  /parse-scope (re-run)
    Re-open the task graph for revision (reverts to TASKS_GENERATED).
```

Stop. Do NOT auto-trigger `/start-build`.

---

## Rules

- Read-only on TASKS.md during approval.
- Never auto-advance to `/start-build`.
- Quality gate failures listed explicitly per item.
