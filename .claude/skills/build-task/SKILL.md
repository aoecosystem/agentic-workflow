---
name: build-task
description: Implement exactly one task from TASKS.md end to end — consume Figma/codegen artifacts, fetch MCP context when needed, write the vertical slice, run local verification (lint, typecheck, tests, acceptance, design fidelity, security, observability), enforce attempt budget, and hand off to QA. Trigger when Orchestrator assigns a task to Builder, or when the user says "build this task", "build TASK-XX", or "continue the current task". One task per run; never spans features silently.
---

# Skill: Build Task

**Triggered by:** Orchestrator assigning a task to a Builder agent

**Purpose:** Implement one task from `state/TASKS.md` completely — consume unified Figma ingest/codegen artifacts when present, fetch MCP context if needed, implement the vertical slice, run verification, and hand off to QA.

---

## Steps

### Step 1 — Read context

Before writing any code:
1. Read the task block from `state/TASKS.md` (full block including acceptance criteria).
2. Read `state/SCOPE.md` — the relevant feature section only.
3. Read `memory/ARCHITECTURE.md` — find where new files should live.
4. Read `memory/PATTERNS.md` — identify which patterns apply to this task.
5. Read `memory/DECISIONS.md` — note any past decisions that constrain this task.
6. Read `memory/STACK-GUIDANCE.md` when it exists — use it for stack-specific architecture, state, UI, and testing defaults.
7. If present, read task fields: `Design source`, `Codegen artifact`, `Design checklist`, `Visual baseline refs`, `Plugin artifact refs`.
8. If present, read the product-context addendum: `User value`, `User flow`, `Functional notes`, `Edge cases`, and `Test cases`.

### Step 2 — Mark task in-progress and check attempt budget

Before flipping status:

1. Read the task block's `Attempts:` and `Max attempts:` fields. Default
   `Max attempts:` to `3` if missing.
2. If `Attempts >= Max attempts`, do not start. Mark `Status: blocked` with
   `QA notes: BLOCKED. Type: attempt-budget-exhausted. Need: user direction
   (increase budget, scope cut, or cancel task).` and surface to Orchestrator.
3. Otherwise, increment `Attempts` by 1 and append a one-line entry to
   `Attempt log:` with the timestamp and a short intent ("Implementing
   from scratch", "Fixing QA rejection 2").

Then update the task block:
```
- Status: in-progress
```

### Step 3 — Fetch MCP context (if MCP URL present)

If the task block has a non-empty `MCP URL:` field:
1. Check `memory/mcp-cache/` for an existing cache file for this feature (naming: `{feature-slug}-{type}.md`).
2. If cache exists → read it. Skip fetching.
3. If no cache → run the `fetch-mcp` skill with the URL. Wait for it to write the cache file.
4. Read the cache file before implementing UI or API work.

### Step 4 — Resolve Figma ingest/codegen input (UI tasks)

If the task is a UI task and includes `Codegen artifact:`:
1. Read the artifact file in `memory/mcp-cache/`.
2. Treat artifact file map and component tree as the source implementation skeleton.
3. Do not replace scaffold structure unless artifact conflicts with explicit acceptance criteria.
4. Track any intentional divergence from the file map as `GAP-XX` in `QA notes:` with the missing scaffold file/widget and reason.
5. If artifact is missing or invalid, mark task `blocked` with exact file/problem and request `figma ingest` rerun.

If the task is a UI task and has `Design source: Figma` but missing `Codegen artifact` or `Screen MCP URLs`, request `figma ingest` before implementation.
If the task is a UI task and has Figma URL but no `Plugin artifact refs`, request `figma ingest` before implementation.

### Step 5 — Plan the implementation

Before writing any file:
1. List every file to be created or modified (must match the task block's `Files to create/modify` list).
2. For each file: one sentence describing what changes.
3. Identify which patterns from `memory/PATTERNS.md` apply.
4. Note which guidance from `memory/STACK-GUIDANCE.md` applies (architecture, state/data flow, UI composition, testing defaults, anti-patterns).
5. If the task has UI: note which MCP/design artifact context applies (component names, layout tokens, props, state matrix, breakpoints).
6. If the task has `Contract refs`, identify the backend/client contract this task is expected to implement or consume and which other task owns the adjacent surfaces.
7. Translate `User flow`, `Functional notes`, and `Edge cases` into implementation checkpoints so the task is built around the intended user outcome, not just the file list.

Do not start writing code until this plan is clear.

### Step 6 — Implement in vertical slice order

Build in this order (skip layers not applicable to the task):

1. **Data model / types** — define TypeScript types, Zod schemas, or ORM model first. Everything else depends on these.
2. **Database layer** — migrations or schema changes if this task touches the DB.
3. **Service layer** — business logic with no HTTP or UI concerns.
4. **API layer** — route handlers, input validation, error responses.
5. **UI layer** — screens, components, hooks. If codegen artifact exists, implement scaffold first, then behavior wiring. Preserve token/state/breakpoint constraints from artifact.
6. **Tests** — write tests for each layer touched. Happy path + error cases. Co-locate with code or in `tests/` per project convention.

**Rules during implementation:**
- Read any existing file before editing it.
- Follow patterns from `memory/PATTERNS.md` exactly.
- Follow `memory/STACK-GUIDANCE.md` when present; treat it as the stack-specific implementation playbook for this project.
- Use the tech stack specified in `state/SCOPE.md` — do not introduce new dependencies without noting it.
- Handle all error paths. See `state/SCOPE.md` NFR section for expected error shape.
- No `TODO` comments. If something is incomplete, the task is not done.
- No `any` types without a documented reason in a comment.
- For Figma-driven mobile/app layouts, treat device chrome in design previews as non-app scaffolding. Implement the inner content layout only unless acceptance criteria explicitly require shell chrome.
- Reuse only `compatible` plugin fragments from `Plugin artifact refs`; treat `partial` output as hints and document any rejected fragments that would otherwise affect fidelity.

### Step 7 — Run verification gates

Run all gates from `01-verification.mdc` and `04-design-fidelity.mdc` when UI is involved:

1. **Lint** — run linter on all modified files. Fix all errors.
2. **Typecheck** — run `tsc --noEmit` (or equivalent). Fix all errors.
3. **Tests** — run tests scoped to changed files. All must pass.
4. **Acceptance criteria self-check** — go through every `[ ]` item in the task block. Verify each one is satisfied. Check them: `[x]`.
5. **Design checklist self-check (UI only)** — validate token usage, state parity, and responsive requirements from `Design checklist`.
6. **Codegen traceability self-check (UI with codegen)** — confirm every file/widget in scope maps back to the codegen file map, or add a `GAP-XX` note explaining the divergence.
7. **Product-context self-check** — confirm the implementation covers the documented `User flow`, `Edge cases`, and `Test cases`, or document any scope-bound omission clearly in `QA notes:`.

If any gate fails: fix it before proceeding. Do not hand off with failing gates.

### Step 8 — Write QA handoff note

In the task block under `QA notes:`, write a brief note:
- What was built (files created/modified, summary of approach)
- Which MCP cache was used (if any)
- Which codegen artifact was used (if any)
- Which plugin artifact refs were used (if any)
- Which patterns were followed
- Any non-obvious decisions made during implementation
- A 3-line mapping:
  - `Codegen file map -> files changed`
  - `Primary Figma node -> implemented screen`
  - `Device chrome excluded -> yes/no with reason`
- Which compatible plugin fragments were used and which planned scaffold gaps were documented as `GAP-XX`
- Confirmation that all gates pass

### Step 9 — Mark task in-review

Update the task block in `state/TASKS.md`:
```
- Status: in-review
```

Update the progress table counts.

### Step 10 — Pick up next task

After marking `in-review`, immediately check the Builder's assigned chain in `state/TASKS.md` for the next `pending` task with all dependencies met. If found, start Step 1 for it without waiting for QA to finish the current task.

---

## Blocked task protocol

If at any step the Builder hits a blocker:
1. Mark task `blocked`.
2. Write the specific reason under `QA notes:` (e.g. "MCP URL returned 404", "SCOPE.md does not specify error format for this endpoint", "TASK-002 is not done and this task depends on its types").
3. Update progress table.
4. Stop work on this task. Move to the next unblocked task in the chain if one exists.
5. Surface the block to the Orchestrator.

---

## Output

Task marked `in-review` with all verification gates passing and QA handoff note written.
