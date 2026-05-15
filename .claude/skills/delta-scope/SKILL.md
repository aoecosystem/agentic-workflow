---
name: delta-scope
description: Detect scope changes after TASKS.md already has tasks and produce a reviewable delta (TASK-DELTA-XX, pending-task edits, obsolete archive) instead of silently re-planning. Trigger when the user says "delta scope", "rescope", "SCOPE changed", or when SCOPE.md/inputs/ are edited while TASKS.md has tasks in any status other than all-pending. Never edit done or in-progress tasks silently.
---

# Skill: Delta Scope

**Trigger:** User says `delta scope` / `rescope` (or uses the `/delta-scope` slash command), or `state/SCOPE.md` / `inputs/` changes while `state/TASKS.md` already has tasks other than `pending`.

**Purpose:** Detect what changed in the scope of work after tasks have already been generated (or built), and produce a reviewable delta rather than silently re-planning. The workflow must never drop done work or duplicate active work because the spec moved.

---

## When to run

Run this skill when any of these is true:

- `state/SCOPE.md` was edited after `parse scope` produced `state/TASKS.md`.
- A new or updated document was added to `inputs/` after `import docs` was last run.
- A user explicitly says `delta scope`, `rescope`, or "scope changed".
- Orchestrator detects that `state/SCOPE.md`'s modification time is newer than the last `state/TASKS.md` generation timestamp.

Do not run this skill on the first-ever pass. For the first pass use `parse scope` or `reqops`.

---

## Inputs

- Current `state/SCOPE.md` (after change)
- Current `state/TASKS.md` (with per-task statuses)
- Last snapshot of SCOPE-derived requirements (if any) in `.pipeline/features/requirements/`
- `memory/ARCHITECTURE.md`, `memory/PATTERNS.md`, `memory/DECISIONS.md` for reality check

Optional:
- Git working directory for diff (skipped when version control is disabled).
- User-provided change summary ("I added a referral feature, removed admin panel").

---

## Steps

### Step 1 — Build the "before" and "after" requirement maps

1. Read the current `state/SCOPE.md`. Extract a normalized feature map
   (name, screens, endpoints, data models, NFRs, dependencies, MCP URLs).
2. Read existing per-feature requirement files under
   `.pipeline/features/requirements/` to reconstruct the last-known state.
   If those do not exist, derive the "before" map from `state/TASKS.md` task
   blocks (feature group + screens/endpoints/models referenced).
3. Produce two structured maps keyed by feature.

### Step 2 — Compute the diff

For each feature, classify every item into one of:

- `ADDED` — in `after` but not in `before`
- `REMOVED` — in `before` but not in `after`
- `CHANGED` — same identifier but different definition (new endpoint body,
  new required field, new state transition, different auth expectation, etc.)
- `UNCHANGED` — identical

Diff at the level of:
- features
- screens / pages
- API endpoints (path + method as key)
- data models (entity name as key, fields diffed)
- NFRs (key + value)
- feature dependencies

### Step 3 — Map the diff to existing tasks

For each `ADDED`, `REMOVED`, `CHANGED` item, locate affected tasks in
`state/TASKS.md` using:

- traceability refs (`TR-SCR-XX`, `TR-API-XX`, `TR-MOD-XX`, `TR-FLOW-XX`,
  `TR-NFR-XX`)
- feature group name
- `Files to create/modify:` overlap

Label each impacted task with an impact class:

- `IMPACT-ADD` — new task needed for an added requirement
- `IMPACT-MODIFY` — existing task acceptance criteria / files must change
- `IMPACT-OBSOLETE` — existing task is no longer in scope
- `IMPACT-DEP-RECHECK` — dependency graph must be re-derived

### Step 4 — Classify by task status

Combine impact class with current status to decide the safe action:

| Current status | Impact | Action |
|----------------|--------|--------|
| `pending` | `IMPACT-MODIFY` | Edit task in place; no new task needed |
| `pending` | `IMPACT-OBSOLETE` | Remove the task block, note rationale |
| `in-progress` / `in-review` / `needs-fix` | any | Do not edit the task silently. Surface to user. |
| `done` | `IMPACT-MODIFY` | Create a `TASK-DELTA-XX` follow-up task referencing the original task |
| `done` | `IMPACT-OBSOLETE` | Do not delete. Create a `TASK-REMOVE-XX` task to decommission the feature. |
| any | `IMPACT-ADD` | Draft a new task block using the parse-scope template |
| any | `IMPACT-DEP-RECHECK` | Flag for Orchestrator; do not auto-edit the graph |

### Step 5 — Produce a human-reviewable delta report

Before writing anything to `state/TASKS.md`, emit a report in chat:

```
Delta report (SCOPE.md change at <timestamp>)

Added:
- Feature X: 2 new screens, 1 endpoint, 1 model
  → new TASK-DELTA-101, TASK-DELTA-102

Changed:
- Feature Y: endpoint POST /items now requires idempotency key
  → impacts TASK-014 (status: done) → create TASK-DELTA-103
  → impacts TASK-018 (status: in-progress) → OUTSTANDING: surface to user

Removed:
- Feature Z decommissioned
  → create TASK-REMOVE-201
  → done task TASK-022 stays in history

Dependency recheck:
- Feature Y now depends on Feature A (was independent)
  → re-run orchestrator dep graph

Outstanding (blocked on user):
- TASK-018 is in-progress but its spec changed. Pause the builder?
```

Do not edit `state/TASKS.md` until the user confirms.

### Step 6 — Apply the delta (after confirmation)

After user confirmation:

1. Append new `TASK-DELTA-XX` blocks using the `parse-scope` template.
   Each delta task carries:
   - `Source delta:` — one-line diff summary
   - `Origin task:` — original task ID if any
   - `Depends on:` — updated dependencies
2. Edit `pending` task blocks in place for `IMPACT-MODIFY`.
3. Mark `IMPACT-OBSOLETE` pending tasks with status `obsolete` and move them
   to an `## Archive` section at the bottom of `state/TASKS.md`.
4. For `done` tasks impacted by a change, never edit them. Link them from
   the corresponding `TASK-DELTA-XX` via `Origin task:` so history remains
   clean.
5. Re-run `scripts/update-task-counts.py` to refresh the progress table.
6. Trigger `reqops` on any feature with a substantive requirement change so
   `.pipeline/features/requirements/<feature>-requirements.md` is updated
   with a new Change Log entry.

### Step 7 — Handoff

After applying the delta:

- Orchestrator re-reads `state/TASKS.md` and rebuilds the dependency graph.
- Any `in-progress` or `in-review` task flagged in Step 5 as "outstanding"
  stays paused until the user resolves its disposition (continue / pause /
  cancel).

---

## Output

A reviewed, user-confirmed delta applied to `state/TASKS.md`:
- new `TASK-DELTA-XX` blocks for added / modified-after-done work
- in-place edits for pending tasks
- `obsolete` archive for removed pending tasks
- untouched history for `done` tasks
- refreshed dependency graph ready for `resume build`
