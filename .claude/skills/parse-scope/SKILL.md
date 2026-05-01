---
name: parse-scope
description: Generate (or regenerate) TASKS.md from a filled-in state/SCOPE.md, with one executable task block per unit of work grouped by feature, dependency edges, agent assignments, traceability refs, attempt budget, acceptance criteria, and optional design fields. Runs a ReqOps pre-pass when .pipeline/sow.md or docs/ SOW is present. Trigger when the user says "parse scope", "generate tasks", "break this scope into tasks", or asks for a task list from a completed SCOPE.md. This skill is the sole writer of TASKS.md.
---

## Stage gate (RUN FIRST)

1. Read `state/SESSION-STATE.md`. Locate `Stage:`.
2. If `Stage` is not `SCOPE_PARSED`, refuse with:
   > "Parse-scope is only valid from `SCOPE_PARSED`. Current: `<STAGE>`.
   > Run `/import-docs` first to populate `state/SCOPE.md`."
   Leave Stage unchanged.
3. If `Stage` is `TASKS_GENERATED` and user wants to re-run, that's
   allowed (regeneration); transition stays at `TASKS_GENERATED`.

---

## Manual-edit detection (RUN BEFORE FILE OPERATIONS)

Compute SHA-256 of `state/SCOPE.md` and `memory/STACK-GUIDANCE.md`.
Compare to stored hashes. On drift, ask user before proceeding.

---

# Skill: Parse Scope

**Trigger:** User says `parse scope` (or uses the `/parse-scope` slash command)

**Purpose:** Read `state/SCOPE.md` and generate a structured `state/TASKS.md` with one task block per unit of work, grouped by feature, with dependencies, agent assignments, MCP URLs, files, and acceptance criteria. When SOW sources exist (prefer `docs/`), run a ReqOps requirements pass first so Builder/QA criteria are SOW-grounded and testable.

Primary objective: generate implementation-ready tasks that are traceable to `state/SCOPE.md` feature-by-feature and flow-by-flow, with zero invented scope and zero orphan requirements.

---

## Non-negotiable quality gates

Before presenting a draft, all of the following must be true:

1. **Scope fidelity:** Every generated task maps to a real feature, screen, endpoint, model, NFR, or dependency from source docs.
2. **Traceability:** Every screen/page, endpoint, and data model listed in `state/SCOPE.md` section 5 appears in at least one task (directly or via shared contract task).
3. **Flow integrity:** User flows in `state/SCOPE.md` are preserved in task ordering and dependencies (entry -> action -> outcome).
4. **No task bloat:** Do not create generic filler tasks ("refactor", "cleanup", "misc") unless explicitly required by source scope.
5. **Execution realism:** Each task should represent a meaningful vertical unit a senior Builder can complete in one focused session.

If any gate fails, revise task decomposition before showing user.

---

## Steps

### Step 1 — Read inputs

Read these files before generating anything:
- `docs/` SOW/requirements docs — if present, this is the preferred ReqOps source
- `state/SCOPE.md` — full content
- `state/TASKS.md` — check if tasks already exist (ask user before overwriting)
- `memory/ARCHITECTURE.md` — if it exists, use its module map to assign file paths
- `memory/STACK-GUIDANCE.md` — if it exists, use it to keep tasks aligned with the chosen stack's architecture, UI, and testing conventions
- `.pipeline/sow.md` — fallback ReqOps source if docs/SCOPE SOW is unavailable
- `.pipeline/requirements.md` — if present
- `.pipeline/features-list.md` — if present
- `.pipeline/system-design-provided.md` — if present
- `.pipeline/features/requirements/` — if present, for existing feature dependencies and conflicts

### Step 2 — ReqOps pre-pass (when SOW sources exist)

If SOW sources exist in `docs/`, `state/SCOPE.md`, or `.pipeline/sow.md`:
1. For each feature detected in `state/SCOPE.md` section 5, run ReqOps logic (see `reqops` skill) and create/update:
   - `.pipeline/features/requirements/<feature-id>-<feature-slug>-requirements.md`
2. Enforce ReqOps source precedence (`docs/` SOW first, then `state/SCOPE.md`, then `.pipeline/sow.md` fallback) over lower-precedence pipeline docs.
3. Record contradictions as `GAP-XX` in the requirements file (never silently resolve).
4. If no authoritative SOW source is found, continue with `state/SCOPE.md` generation only and note that ReqOps grounding was unavailable.

If no ReqOps output files exist:
- Continue with standard `state/SCOPE.md`-driven task generation.

### Step 3 — Identify feature groups

From `state/SCOPE.md` section 5 (Feature Breakdown):
- Extract each named feature as a group.
- Note its dependencies on other features.
- Note its MCP URL if provided.
- Build a feature inventory table with:
  - `feature_name`
  - `screens/pages`
  - `api_endpoints`
  - `data_models`
  - `design refs` (Figma node IDs, plugin export, token source)
  - `depends_on`

Also build a flow inventory (if flow details exist):
- `role`
- `entry point`
- `ordered steps`
- `state transitions`
- `edge/error states`
- `timers/rate limits`

Also identify these mandatory implicit tasks (always add them):
- **TASK-000: Project scaffold** — install dependencies, set up config files, folder structure, dev script. No dependencies. Assign to `orchestrator`.
- **TASK-001: Database schema** — create all data models and migrations from every feature's "Data Models" section. Depends on TASK-000. Assign to `builder-1`.

### Step 4 — Generate tasks per feature

For each feature, create tasks using this decomposition order:

1. **Contract and data ownership**
   - schema/model ownership, DTO/contracts, auth boundaries
2. **Behavior slice tasks**
   - API behaviors by endpoint cluster and lifecycle stage
   - UI behaviors by flow stage (not random screen buckets)
3. **Integration slice**
   - cross-role transitions and status changes
4. **Verification in-task**
   - tests remain inside each implementation task (not stand-alone "test-only" tasks unless scope explicitly requires a dedicated test harness)

Preferred task shapes per feature:
- Backend-only feature: 1-2 tasks
- UI-only feature: 1-3 tasks (split by meaningful flow stage)
- Full-stack feature: 2-5 tasks
- Large multi-role lifecycle feature: 4-7 tasks

Do not exceed these ranges unless justified by explicit complexity in scope; if exceeding, explain why in draft summary.

**Rules:**
- Each task must have exactly one feature group.
- A task must not span two feature groups.
- If a feature has both API and UI, create two tasks: one API task, one UI task. UI depends on API.
- Prefer vertical slices with an explicit server/client contract. When a feature spans backend, web, and mobile, generate linked tasks that name the shared contract and identify which task owns each surface.
- Keep task scope small — a Builder should be able to complete one task in one session.
- Add product-context sections for user-facing feature tasks so the Builder understands who the task serves, how the flow should work, and what behavior matters most.
- For UI tasks with Figma context, include design fields in the task block:
  - `Design source`
  - `Codegen artifact`
  - `Visual baseline refs`
  - `Screen MCP URLs`
  - `Design checklist`
  - `Plugin artifact refs`
  - `Asset refs`
- Do not create tasks for undocumented assumptions. If required behavior is implied but not explicit, include it under task notes with `INFERRED:` and add a clarification gap.

### Step 4.5 — Enforce source-to-task traceability

Create a temporary traceability map before drafting output:

- `TR-SCR-XX` for every screen/page in each feature
- `TR-API-XX` for every endpoint
- `TR-MOD-XX` for every model/entity
- `TR-FLOW-XX` for every major flow transition
- `TR-NFR-XX` for each explicit NFR constraint used by tasks

Assign each trace ID to at least one task ID.

Hard rule:
- No trace ID left unassigned.
- No task without at least one trace ID.

If any trace item cannot be assigned, mark it as a blocker/gap and surface before writing `state/TASKS.md`.

### Step 5 — Assign agent slots

Assign Builder agents based on feature group independence:
- Features with no dependency between them → different Builders
- Features that share a data model or API → same Builder, sequential order
- Use dynamic Builder IDs (`builder-1`, `builder-2`, ..., `builder-N`)
- Do not cap Builder count at 3; parallelism is determined by independent chains

Scaffold and schema tasks always use `orchestrator` or `builder-1`.


### Step 5.5 — Map UI tasks to Page IDs

For every UI task you generate:

1. Read `memory/PAGES.md` (or `state/SCOPE.md` section 8 if PAGES.md is empty).
2. For each screen/page the task implements, attach the corresponding
   `Page ID` from the inventory.
3. Add a `Page IDs:` field to the task block:
   ```
   - Page IDs:
     - auth-login
     - auth-signup
   ```
4. The UI task's `Files to create/modify` should also follow page-id
   conventions where useful (e.g.
   `apps/web/src/screens/auth-login.tsx`).

Page IDs flow through every UI artifact: Figma frame names, screenshot
filenames, Claude Design HTML files, generated component file names.
This keeps cross-source design lookup unambiguous.

---

### Step 6 — Write acceptance criteria (Builder + QA ready)

For each task, write 3–6 acceptance criteria items as checkboxes. Derive them from:
- The feature's screen descriptions (UI renders correctly, user can do X)
- The feature's API endpoints (correct inputs/outputs, error handling)
- The project's NFRs in `state/SCOPE.md` (auth required, validation, error format)
- ReqOps requirements file for that feature if available in `.pipeline/features/requirements/`

Every task must have at minimum:
- `[ ]` The primary function works end-to-end
- `[ ]` Error paths are handled (invalid input, auth failure, not found)
- `[ ]` Tests cover happy path + at least one error case
- `[ ]` Lint and typecheck pass
- `[ ]` Behavior matches mapped scope items (screens/endpoints/models/flow transitions) for this task

Additional task-specific requirements:
- UI tasks with `Design source: Figma` must include an acceptance item requiring implementation traceability to the linked `*-codegen.md` file map, or a documented `GAP-XX` in `QA notes:` explaining why a scaffold file/widget was intentionally not implemented.
- API-backed client tasks must include an acceptance item verifying authenticated requests use the feature's canonical client path and document expected `401` handling when the route is protected.
- Cross-platform features should include at least one acceptance item that references the shared contract between backend and client tasks (response shape, auth expectations, empty/error behavior, or DTO note).

If ReqOps output exists, acceptance criteria should inherit:
- MoSCoW priority intent (at least `[Must]` coverage captured in task ACs)
- explicit NFR checks (security/performance/accessibility where applicable)
- dependency constraints and out-of-scope boundaries
- ambiguity flags (`GAP-XX` / `A-XX`) as blockers or clarifying notes

### Step 6b — Add builder-facing product context

For user-facing feature tasks, add a concise product-context addendum before `Files to create/modify:`. This is additive only; do not remove any existing task fields.

Use these sections when the feature behavior is visible to end users or depends on specific product expectations:
- `User value:` — 1-3 sentences explaining what users can do and any intentional scope boundary.
- `User flow:` — ordered steps showing how the user enters the flow, sees results, and exits or continues.
- `Functional notes:` — implementation-shaping facts such as searchable fields, ranking, storage behavior, pagination, dependencies, deferred scope, or contract assumptions.
- `Edge cases:` — explicit fallback/error/empty-state conditions the Builder and QA must account for.
- `Test cases:` — concrete behaviors to verify, written as numbered functional checks. These should complement, not replace, checklist-style acceptance criteria.

Keep the sections concise and grounded in `state/SCOPE.md` or ReqOps output. Do not invent product behavior that is not stated or strongly implied by the source material.

Flow-specific requirement:
- `User flow` must include explicit step transitions (screen/action/outcome) and reference at least one edge case from source when provided.

### Step 6c — Dependency and flow validation

Before drafting:
- Verify task dependency order mirrors user flow and lifecycle constraints from source docs.
- Verify cross-role transitions are represented by explicit dependent tasks (example: booking requested -> tutor decision -> payment/status update).
- Verify auth/security-sensitive tasks are sequenced before protected flow tasks.

If dependency graph does not preserve flow reality, regenerate task ordering.

### Step 7 — Draft TASKS.md

Write the full `state/TASKS.md` in this format:

```markdown
# Tasks

## Build progress
| Total | Done | In review | In progress | Needs fix | Blocked | Pending |
|-------|------|-----------|-------------|-----------|---------|---------|
| N | 0 | 0 | 0 | 0 | 0 | N |

---

## TASK-000
- Feature group: Scaffold
- Title: Initialize project structure
- Depends on: none
- Assigned agent: orchestrator
- MCP URL: none
- Contract refs:
  - Backend owner: none
  - Web owner: none
  - Mobile owner: none
  - Integration status: not-started
- Files to create/modify:
  - package.json
  - tsconfig.json
  - [list all config files]
- Acceptance criteria:
  - [ ] Project installs and runs with no errors
  - [ ] TypeScript compiles with zero errors
  - [ ] Linting passes
  - [ ] Test runner is configured and a placeholder test passes
- QA notes:
- Attempts: 0
- Max attempts: 3
- Attempt log:
- Status: pending

---

## TASK-001
- Feature group: Database
- Title: Create database schema and migrations
- Depends on: TASK-000
- Assigned agent: builder-1
- MCP URL: none
- Contract refs:
  - Backend owner: TASK-001
  - Web owner: none
  - Mobile owner: none
  - Integration status: not-started
- Files to create/modify:
  - [ORM schema file or migration files]
- Acceptance criteria:
  - [ ] All data models from SCOPE.md are defined
  - [ ] Migrations run cleanly on a fresh database
  - [ ] TypeScript types generated/defined for all models
- QA notes:
- Attempts: 0
- Max attempts: 3
- Attempt log:
- Status: pending

---

[one block per task. Every task must include Attempts / Max attempts / Attempt log.]
```

For user-facing feature tasks, insert this addendum before `Files to create/modify:`:

```markdown
- User value: Users can search for nail art content using keywords across captions, tags, usernames, and salon names. Recent searches are saved locally for quick access. AI image-recognition search is out of scope for this phase.
- User flow:
  1. User opens the search entry point.
  2. User enters a search term.
  3. Matching results are shown.
  4. User opens a result to view full details.
  5. Recent searches are saved and shown for quick reuse.
- Functional notes:
  - Search endpoint supports query params and pagination.
  - Search indexes captions, tags, salon names, and usernames.
  - Recent searches are stored locally per device.
  - Ranking/relevance logic should prioritize the most useful matches first.
- Edge cases:
  - No results -> show a clear empty state with helpful guidance.
  - Very short query -> return relevant results or prompt for a more specific query.
- Test cases:
  1. Verify search returns results for caption matches.
  2. Verify search returns results for tag matches.
  3. Verify search returns results for salon name matches.
  4. Verify search returns results for username matches.
  5. Verify recent searches are saved and displayed.
  6. Verify the no-results state renders correctly.
  7. Verify paginated search remains performant.
```

For UI tasks, include this design section after `MCP URL`:

```markdown
- Design source: Figma
- Codegen artifact: none
- Visual baseline refs: none
- Screen MCP URLs: none
- Design checklist:
  - [ ] token usage fidelity
  - [ ] typography fidelity
  - [ ] asset parity by screen
  - [ ] state parity
  - [ ] responsive parity
  - [ ] accessibility parity
  - [ ] no duplicate device chrome (status bar, notch, home indicator)
- Plugin artifact refs: none
- Asset refs: none
```

For feature tasks that span multiple clients or a backend/client contract, include this section after `MCP URL`:

```markdown
- Contract refs:
  - Backend owner: TASK-00X | none
  - Web owner: TASK-00Y | none
  - Mobile owner: TASK-00Z | none
  - Integration status: not-started | partial | complete
```

Also include traceability in each task block:

```markdown
- Traceability refs:
  - TR-SCR-XX
  - TR-API-XX
  - TR-MOD-XX
  - TR-FLOW-XX
  - TR-NFR-XX
```

Only include IDs that apply to the task.

### Step 8 — Present and confirm

Before writing `state/TASKS.md`:
1. Show the user a summary: total tasks, tasks per feature group, Builder assignments, estimated parallelism.
2. Show coverage summary:
   - screens mapped / total
   - endpoints mapped / total
   - models mapped / total
   - major flow transitions mapped / total
3. List any inferred items and unresolved gaps.
4. If coverage is incomplete, do not ask for write confirmation yet.
5. If complete, ask: "Does this look correct? Reply 'yes' to write state/TASKS.md, or tell me what to adjust."
6. Only write the file after the user confirms.

### Step 9 — Update progress table

After writing `state/TASKS.md`, update the Build progress table at the top: set Total = N, Pending = N, all others = 0.

---

## Output

A complete `state/TASKS.md` ready for `start build`, with stronger Builder/QA acceptance criteria informed by ReqOps feature requirements when available.

---

## Stage transition (ON SAVE)

After writing `state/TASKS.md`:

1. Update `state/SESSION-STATE.md`:
   - `Stage:` → `TASKS_GENERATED`
   - `Last skill:` → `parse-scope`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /approve-tasks (recommended audit) then /start-build.`
   - Artifacts list: mark `state/TASKS.md` with task count + hash.
2. Append audit log:
   ```
   <ISO>  parse-scope  SCOPE_PARSED → TASKS_GENERATED  <N> tasks generated
   ```

3. Tell user: *"<N> tasks generated. Next: run `/approve-tasks` to audit, then `/start-build` to begin parallel build."*
