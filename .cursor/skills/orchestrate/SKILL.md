---
name: orchestrate
description: Read TASKS.md, build a dependency graph, fan out independent feature groups to parallel Builder/QA runs, and run a continuous scheduler loop until all tasks are done or explicitly blocked on human input. Trigger when the user says "start build", "resume build", "run the build", "kick off orchestration", or asks to resume work after tasks are generated. Owns scheduling and transitions — does not write code itself; delegates to build-task and qa skills.
---

## Stage gate (RUN FIRST)

1. Read `state/SESSION-STATE.md`. Locate `Stage:`.
2. Branch:
   - If `Stage` is `TASKS_APPROVED`: this is the start of the build.
     Transition to `BUILDING` immediately, append audit log.
   - If `Stage` is `BUILDING`: this is a resume — pick up where
     scheduler left off, no Stage change.
   - If `Stage` is anything else: refuse with:
     > "Orchestrator runs from `TASKS_APPROVED` (start) or `BUILDING`
     > (resume). Current: `<STAGE>`. Run `/approve-tasks` first."

---

# Skill: Orchestrate

**Trigger:** User says `start build` or `resume build`

**Purpose:** Read `state/TASKS.md`, build a dependency graph, run unified Figma ingest prep for UI tasks, fan out independent feature groups to parallel Builder agents, and run a continuous scheduler loop (Builder + QA) until all tasks are `done` or blocked on human input.

---

## Steps

### Step 1 — Read current state

Read:
- `state/TASKS.md` — full task list with statuses
- `memory/ARCHITECTURE.md` — existing module map
- `memory/DECISIONS.md` — past decisions

### Step 2 — Validate preconditions

Before starting:
- Confirm `state/TASKS.md` exists and has at least one task block.
- Confirm the scaffold task (TASK-000) exists.
- If `start build`: scaffold task must be `pending` or `done`.
- If `resume build`: load current in-flight state (`in-progress`, `in-review`, `needs-fix`) and all dependency-ready `pending` tasks.
- If any task is `blocked`: surface it to the user immediately before proceeding.
- For any dependency-ready UI task, do not allow Builder start until `Codegen artifact`, `Screen MCP URLs`, and `Design checklist` are populated. If any are missing, run `figma-plugin-ingest` first or leave the task blocked.

### Step 3 — Build dependency graph

For each task:
1. Parse its `Depends on:` field.
2. Build a directed graph: task → depends on → tasks.
3. Identify the critical path (longest chain of dependencies).
4. Identify all tasks with no unmet dependencies = "ready" tasks.

### Step 4 — Group into Builder chains

From the ready tasks:
1. Group tasks that share files or have dependency edges → one Builder chain.
2. Assign one Builder slot per independent chain using dynamic IDs (`builder-1`, `builder-2`, ..., `builder-N`).
3. Do not hard-cap parallel Builders. Create as many Builder sub-agents as independent ready chains.
4. Scaffold and schema tasks always run first under `builder-1` (or orchestrator) before other Builders start.

Print the assignment before starting:
```
Build plan:
  builder-1: TASK-000 (scaffold) → TASK-001 (schema) → TASK-003 (auth API) → TASK-004 (auth UI)
  builder-2: TASK-005 (items API) → TASK-006 (items UI)
  builder-3: TASK-007 (dashboard UI)
  QA: reviews in-review tasks as they arrive
```

### Step 5 — Execute scaffold first (if pending)

If TASK-000 (scaffold) is `pending`:
- Run `build-task` skill for TASK-000 first.
- Do not start any other Builder until TASK-000 is `done` (QA approved).

### Step 5b — Auto-emit app-shell routing guard task (TASK-000A)

The moment TASK-000 (scaffold) finishes QA and moves to `done`,
orchestrator MUST insert a follow-up task `TASK-000A — App-shell
routing guard` into `state/TASKS.md` if it does not already exist. No
feature task may be assigned until TASK-000A is also `done`.

This guard task closes the most common failure mode in agentic builds:
the project compiles, tests pass, but the actual app shell crashes on
boot because the router, layout, or entry component is misconfigured.
We catch it once, here, before fanning out N parallel feature Builders.

#### TASK-000A template (insert verbatim into state/TASKS.md)

```markdown
## TASK-000A — App-shell routing guard

- Status: pending
- Assignee: builder-1
- Depends on: TASK-000
- Files to create/modify: (varies by stack — entry / router / layout files only)
- Attempts: 0
- Max attempts: 3

**Description:**
Verify the app shell loads end-to-end on the configured platform(s).
The shell must render the default route, navigate to at least one
secondary route, and mount the global layout without runtime errors.

**Acceptance criteria:**
- [ ] Native build runs cleanly (see verify-build Gate 2b).
- [ ] App shell renders the default route on a real start (`npm run dev` /
      `expo start --no-dev` / equivalent) — no console errors in the
      first 5 seconds.
- [ ] Navigation from default route to one secondary route works
      (router resolves, layout switches, no crash).
- [ ] Global error boundary / 404 page exists and is reachable.
- [ ] Auth-gated route returns the unauthenticated state cleanly (no
      blank screen, no infinite redirect loop).

**Test cases:**
1. Start the app. Default route renders. Capture console: zero errors.
2. Navigate to one secondary route. Layout switches. No crash.
3. Visit an unknown path. 404 / not-found page renders.
4. Visit an auth-gated route while logged out. Unauthenticated state
   renders (login redirect or "please sign in" page).

**QA notes:** (Builder fills in)
```

#### Rules

- Insert TASK-000A only ONCE per project. If a row already exists,
  skip — do not duplicate.
- TASK-000A is owned by `builder-1` (same Builder that owned the
  scaffold) — context continuity beats parallelism here.
- Other Builders stay idle until TASK-000A reaches `done`. Treat any
  attempt to schedule a feature task before TASK-000A is `done` as a
  scheduler bug.
- The `Files to create/modify:` list is the entry / router / global
  layout files only. The Builder MUST NOT modify feature code in this
  task.

After TASK-000A reaches `done`, proceed to Step 6 (fan out feature
Builders).

### Step 6 — Fan out Builders

Once scaffold is `done`:
- For ready UI tasks with Figma MCP URL and missing artifact fields, run `figma-plugin-ingest` first.
- Treat missing `Codegen artifact`, missing `Screen MCP URLs`, empty `Design checklist`, or screen targets that resolve only to sparse section/device-preview context as ingest blockers, not Builder work.
- If ingest fails, mark the task `blocked` with the exact failing URL/error (no secondary design skill fallback).
- Launch every ready Builder chain as a parallel sub-agent using Cursor's Task tool.
- Each Builder receives: its chain of task IDs and the instruction to follow `build-task` skill.
- Builders work in parallel. Each Builder processes its tasks sequentially within its chain.
- Keep a registry of active Builder IDs and their current chain ownership for reassignment.

### Step 7 — Monitor and route (continuous)

After fanning out, run this loop continuously until exit condition is met:
1. Re-read `state/TASKS.md` on every loop tick (and after every status change).
2. Route all `in-review` tasks to QA immediately.
   - For UI tasks with design artifacts, `qa` also runs design fidelity checks.
3. Route each `needs-fix` task back to its owning Builder chain first; if owner is unavailable, assign to an idle/new Builder.
4. Detect all `pending` tasks whose dependencies are now satisfied.
   - If an idle Builder exists, assign the task/chain.
   - If no idle Builder exists and the task is independent, spawn a new Builder sub-agent.
5. When a task moves to `blocked`, surface blocker details immediately.
6. After each reassignment, keep polling; do not stop after one completed task.

Loop exit conditions:
- **Complete:** every task is `done`.
- **Paused by user/session:** leave statuses as-is; do not reset ownership.
- **Blocked:** remaining non-done tasks are all `blocked` or blocked-by-dependency; report blockers and wait for user input.

### Step 8 — Update progress table

After every status change, update the Build progress table at the top of `state/TASKS.md`:
- Recount each status column.
- Preferred helper: `python3 scripts/update-task-counts.py`

### Step 9 — Completion

When all tasks are `done`:
1. Print a completion summary:
   ```
   Build complete.
   Total tasks: N
   Features built: [list]
   Run the project and verify manually if needed.
   ```
2. Do not modify any files after this point.

---

## resume build behavior

If triggered by `resume build`:
- Do not restart from scratch.
- Preserve all existing task statuses and ownership where possible.
- Resume all active tasks (`in-progress`, `in-review`, `needs-fix`) first.
- Also schedule all dependency-ready `pending` tasks in parallel.
- Re-enter the same continuous scheduler loop from Step 7 until completion or new blockers.

---

## Output

All tasks progressed to `done` through parallel Builder + QA execution.

---

## Stage transitions written by this skill

- **On start** (TASKS_APPROVED → BUILDING): when scheduler first launches.
  ```
  <ISO>  orchestrate  TASKS_APPROVED → BUILDING  scheduler started, <N> ready chains
  ```

- **On all-tasks-done** (BUILDING → BUILD_COMPLETE): when every task in
  `state/TASKS.md` has Status: `done` (no pending/in-progress/in-review/
  needs-fix/blocked remain).
  ```
  <ISO>  orchestrate  BUILDING → BUILD_COMPLETE  all <N> tasks done
  ```

After transitioning to `BUILD_COMPLETE`, tell user:
*"Build complete. Run `/approve-build` to lock, then `/verify-build`."*

---

## Manual-edit detection during build

Builders write to `../apps/<sub-app>/` files. After each task moves to
`in-review`, the orchestrator records SHA-256 of every file written by
that task in the Artifacts list. The next time any skill runs, manual
edits are detected per the Manual Edit Protocol.
