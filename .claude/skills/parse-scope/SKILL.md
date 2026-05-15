---
name: parse-scope
description: Generate (or regenerate) state/TASKS.md by reading the 5 approved HTML deliverables directly (brief, scope-of-work, architecture, database, infrastructure). Produces one executable task block per unit of work grouped by feature, with dependency edges, agent assignments, traceability refs, attempt budget, acceptance criteria, and optional design fields. Also emits memory/STACK-GUIDANCE.md and memory/PAGES.md as side effects. Trigger when the user says "parse scope", "generate tasks", "break the deliverables into tasks", or runs /parse-scope. This skill is the sole writer of TASKS.md.
---

## Stage gate (RUN FIRST)

1. Read `state/SESSION-STATE.md`. Locate `Stage:`.
2. Refuse unless Stage is `DOCS_COMPLETE` or `TASKS_GENERATED` (re-run). Message:
   > "parse-scope is only valid from `DOCS_COMPLETE` or `TASKS_GENERATED`. Current: `<STAGE>`. Complete the docs phase first (run `/status` to see the next required approval)."
3. If `Stage` is `TASKS_GENERATED` and the user wants to re-run, that's allowed (regeneration); transition stays at `TASKS_GENERATED`.

---

## Manual-edit detection (RUN BEFORE FILE OPERATIONS)

Compute SHA-256 of the 5 deliverable HTMLs and `memory/STACK-GUIDANCE.md` (if present). Compare to stored hashes in SESSION-STATE artifacts list. On drift, ask user before proceeding.

---

# Skill: Parse Scope

**Trigger:** User says `parse scope` (or uses the `/parse-scope` slash command).

**Purpose:** Read the 5 approved HTML deliverables and generate `state/TASKS.md` with one executable task block per unit of work, grouped by feature, with dependencies, agent assignments, MCP URLs, files, and acceptance criteria. **There is no intermediate SCOPE.md** — the 5 HTMLs are the source of truth, TASKS.md is the planning output.

Primary objective: generate implementation-ready tasks that are traceable to the 5 HTMLs feature-by-feature and flow-by-flow, with zero invented scope and zero orphan requirements.

Side effects:
- Writes `memory/STACK-GUIDANCE.md` (stack-specific architecture / state / UI / testing defaults derived from SoW Phase 6 + Phase 9).
- Writes `memory/PAGES.md` (page inventory copied verbatim from SoW Phase 7).

---

## Non-negotiable quality gates

Before presenting a draft, all of the following must be true:

1. **Scope fidelity:** Every generated task maps to a real feature, screen, endpoint, model, NFR, or dependency from the 5 HTMLs.
2. **Traceability:** Every page (SoW Phase 7), endpoint (SoW Phase 4), and data model (Database HTML §2) appears in at least one task (directly or via shared contract task).
3. **Flow integrity:** Business processes from SoW Phase 5.5 (if present) and User flows from brief §6 are preserved in task ordering and dependencies (entry → action → outcome).
4. **No task bloat:** Do not create generic filler tasks ("refactor", "cleanup", "misc") unless explicitly required by source scope.
5. **Execution realism:** Each task should represent a meaningful vertical unit a senior Builder can complete in one focused session.

If any gate fails, revise task decomposition before showing user.

---

## Steps

### Step 1 — Read inputs (the 5 HTMLs are the source of truth)

Read these files before generating anything. Resolve `<slug>` from `state/SESSION-STATE.md` → `Slug:`:

**A. State + architecture profile (HARD CONTRACT):**

- `state/SESSION-STATE.md` — locate `Architecture style:` field (one of `monolith`, `hybrid`, `microservices`, `polyglot-microservices`, `serverless`). Drives every task's folder placement.
- `deliverables/architecture/styles/<style>.md` — **HARD CONTRACT** Folder structure section. Memorize:
  - The FE/BE split (e.g. `apps/api/` + `apps/web/` for monolith — never combined)
  - The ORM folder convention (Prisma → `prisma/`, Drizzle → `drizzle/`, TypeORM/Sequelize/Kysely/MikroORM → `database/`)
  - **`infra/` location is STYLE-DEPENDENT:**
    - `monolith` / `hybrid` → `apps/infra/` (inside `apps/`, next to `api/` and `web/`)
    - `microservices` / `polyglot-microservices` / `serverless` → root-level `infra/`
  - Role-based app naming (`apps/api/`, NOT `apps/<slug>-api/`)
  - Component decomposition (Header → HeaderNav.tsx + HeaderLogo.tsx + HeaderUserMenu.tsx; etc.)

**B. The 5 approved HTML deliverables (source of truth — read each end-to-end):**

| # | File | Extract |
|---|---|---|
| 1 | `deliverables/brief/<slug>-brief.html` | §1 vision, §2 target users, §3 platforms + architecture style, §4 multi-role flag, §5 features, §6 business processes, §8 integrations, §9 NFRs, §10 success metrics, §11 out of scope, §12 design preferences, **§13 AI Generation Instructions** (execution rules applied to every task) |
| 2 | `deliverables/scope-of-work/<slug>-sow.html` | Phase 1 service inventory, Phase 2 module breakdown, Phase 3 database schemas, **Phase 4 API endpoints (every row → ≥1 task)**, Phase 5 events, Phase 5.5 business processes (when present), **Phase 6 tech stack** (resolves `Stack:` field in every task), **Phase 7 page inventory (every row → ≥1 UI task)**, Phase 8 quality criteria, **Phase 9 folder structure + design language** |
| 3 | `deliverables/architecture/<slug>-architecture.html` | §1 overview, §2 service inventory, §3 layered architecture, §4 data flow, §5 module boundaries, §6 cross-cutting concerns, §7 Mermaid diagram (verbatim for ERD-aware tasks) |
| 4 | `deliverables/database/<slug>-database.html` | §1 schema overview, **§2 entity definitions (every entity → TASK-001 or feature-specific schema task)**, §3 relationships, §4 indexes strategy, §5 migration & versioning, §6 ERD Mermaid (verbatim) |
| 5 | `deliverables/infrastructure/<slug>-infrastructure.html` | §1 environments, §2 hosting & compute, §3 db/storage/cache, §4 network & domains, §5 external services & integrations, §6 security & secrets (env vars → TASK-000 AC), §7 backup & DR, §8 CI/CD pipeline, §9 topology Mermaid (verbatim) |

**C. Supplemental (read if present, don't fail if missing):**

- `state/TASKS.md` — check if tasks already exist (ask user before overwriting).
- `memory/ARCHITECTURE.md`, `memory/PATTERNS.md`, `memory/DECISIONS.md` — cross-session knowledge.
- `memory/STACK-GUIDANCE.md` — this skill REWRITES it (side effect).
- `memory/PAGES.md` — this skill REWRITES it (side effect).
- `.pipeline/features/requirements/*.md` — ReqOps output (run `reqops` first if you want this layer).

**Failure modes:**
- If SESSION-STATE has no `Architecture style:` field → refuse with "Architecture style missing — re-run `/build-scope-of-work` to lock Phase 9".
- If `deliverables/architecture/styles/<style>.md` does not exist → halt; never improvise a folder structure.
- If any of the 5 HTMLs is missing → halt with the exact path. Stage `DOCS_COMPLETE` should guarantee all 5 exist; missing implies state inconsistency.

### Step 2 — ReqOps pre-pass (optional)

If `.pipeline/features/requirements/*.md` files already exist (from a prior `/reqops` run):
1. Read each one and use its per-feature ACs as the seed for generated task acceptance criteria.
2. Record contradictions between requirements files and the 5 HTMLs as `GAP-XX` notes (never silently resolve).

If no ReqOps output files exist:
- Continue with HTML-driven task generation. This is the default path.

### Step 3 — Identify feature groups

From SoW Phase 2 (modules) + Phase 4 (endpoints) + Phase 7 (pages):
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

1. Read `memory/PAGES.md` (or SoW Phase 7 (Page Inventory) if PAGES.md is empty).
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
- The project's NFRs in `the 5 HTMLs` (auth required, validation, error format)
- ReqOps requirements file for that feature if available in `.pipeline/features/requirements/`

Every task must have at minimum:
- `[ ]` The primary function works end-to-end
- `[ ]` Error paths are handled (invalid input, auth failure, not found)
- `[ ]` Lint and typecheck pass
- `[ ]` Behavior matches mapped scope items (screens/endpoints/models/flow transitions) for this task
- `[ ]` All files declared in `Files to create/modify:` sit under folders declared by `deliverables/architecture/styles/<style>.md` (no improvised top-level folders, no slug-prefixed app names, no combined FE+BE folder)

**For API tasks (every task that adds or modifies an HTTP endpoint), the AC baseline tightens — vague "happy + one error" is not sufficient. Every endpoint MUST have explicit test cases for:**
- `[ ]` `200`/`201` success path with a representative valid payload
- `[ ]` `401` Unauthorized when the route is protected (omitted only if route is documented public in the 5 HTMLs)
- `[ ]` `403` Forbidden when role-based authorization applies (e.g. tutor-only endpoint called by parent)
- `[ ]` `4xx` validation failure (`400` or `422`) for each constrained input field
- `[ ]` `404` Not Found when the resource is a path parameter (e.g. `/bookings/:id`)
- `[ ]` `500` or domain-specific 5xx surface for at least one internal failure path (e.g. DB unavailable, downstream timeout)

**For UI tasks (every task that creates or modifies a page or component), the AC baseline includes the component-architecture HARD CONTRACT:**
- `[ ]` No static data arrays passed as props — static UI data (nav items, footer links, FAQ rows, dropdown options) lives INSIDE the component that renders it
- `[ ]` No `.map()` over build-time-static literals — each static item rendered as explicit JSX (translation keys via `t()` are the only allowed external dependency)
- `[ ]` One concern per file: pages orchestrate components only; section JSX lives in `components/<feature>/<Concern>.tsx` files, each ≤200 lines
- `[ ]` Design tokens used everywhere — zero hardcoded hex colors or pixel font sizes

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

Keep the sections concise and grounded in `the 5 HTMLs` or ReqOps output. Do not invent product behavior that is not stated or strongly implied by the source material.

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
- Architecture style: <monolith | hybrid | microservices | polyglot-microservices | serverless>     ← from SESSION-STATE
- Stack: { frontend: <name>, backend: <name>, orm: <name>, db: <name> }                            ← from SoW Phase 6
- Folder root: workspace                                                                            ← scaffold writes at repo root
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
  - pnpm-workspace.yaml
  - tsconfig.base.json
  - biome.json                                 ← OR eslint.config.mjs if the SoW picked ESLint
  - apps/api/                                  ← role-based, NEVER apps/<slug>-api/
  - apps/web/                                  ← role-based, NEVER apps/<slug>-web/
  - [infra path depends on style — see acceptance criteria]
  - [other config files declared by deliverables/architecture/styles/<style>.md]
- Acceptance criteria:
  - [ ] Project installs and runs with no errors
  - [ ] TypeScript compiles with zero errors
  - [ ] Linting passes (Biome `check` or ESLint, whichever the SoW picked)
  - [ ] Test runner (Vitest by default) is configured and a placeholder test passes
  - [ ] Folder layout exactly matches `deliverables/architecture/styles/<style>.md` Folder structure section — no improvised top-level folders, no slug-prefixed app names, no combined FE+BE folder
  - [ ] `infra/` lives at the STYLE-CORRECT location:
        - monolith / hybrid → `apps/infra/` (inside `apps/`, next to `api/` and `web/`)
        - microservices / polyglot-microservices / serverless → ROOT-LEVEL `infra/`
  - [ ] `packages/` only exists if the style requires it:
        - monolith → NOT created (use `apps/shared/` if FE+BE share TS types)
        - hybrid → empty (created at first extraction)
        - microservices / polyglot-microservices → `packages/{proto,events,types,ui}` created
        - serverless → `packages/{db,auth,events}` created
  - [ ] `apps/web/` follows the standard layout: `src/`, `public/`, `docs/`, `test/{unit, e2e?}/` — `test/e2e/` only when SoW Page Inventory has ≥3 multi-step flows OR style is microservices / polyglot-microservices (e2e is mandatory there)
- QA notes:
- Attempts: 0
- Max attempts: 3
- Attempt log:
- Status: pending

---

## TASK-001
- Feature group: Database
- Title: Create database schema and migrations
- Architecture style: <inherited from SESSION-STATE>
- Stack: { orm: <Prisma | Drizzle | TypeORM | Sequelize | Kysely | MikroORM>, db: <Postgres | MySQL | ...> }
- Folder root: apps/api/<orm-folder>/         ← prisma/ | drizzle/ | database/ depending on ORM
- Depends on: TASK-000
- Assigned agent: builder-1
- MCP URL: none
- Contract refs:
  - Backend owner: TASK-001
  - Web owner: none
  - Mobile owner: none
  - Integration status: not-started
- Files to create/modify:
  - apps/api/prisma/schema.prisma              ← when ORM = Prisma; otherwise drizzle/schema.ts or database/entities/*
  - apps/api/prisma/migrations/                ← respect chosen ORM CLI conventions
- Acceptance criteria:
  - [ ] Every entity from the 5 HTMLs §9 Database Schemas exists with all columns + types + constraints
  - [ ] Every relationship from the 5 HTMLs §9 is wired in the schema
  - [ ] Migrations run cleanly on a fresh database
  - [ ] TypeScript types generated/defined for all models (when ORM supports it)
  - [ ] ORM folder placed correctly (Prisma → `prisma/`, Drizzle → `drizzle/`, others → `database/`)
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

### Step 8 — Present, run coverage gate, confirm

Before writing `state/TASKS.md`:

1. **Show summary:** total tasks, tasks per feature group, Builder assignments, estimated parallelism.

2. **Run HARD COVERAGE GATE — refuse to save TASKS.md if any item fails.** Each source-of-truth item must be assigned to ≥1 task; gaps below 100% are P0 blockers, not warnings:

   | Source of truth | Required mapping | If less than 100% |
   |---|---|---|
   | **SoW Phase 4 endpoints** (every row of every endpoint table) | each endpoint → at least one task with that endpoint in `Files to create/modify:` or `Functional notes:` | **REFUSE TO SAVE**. List missing endpoints. "API partly worked" symptom. |
   | **SoW Phase 7 Page Inventory** (every page row) | each page → at least one UI task with the matching `Page IDs:` field | **REFUSE TO SAVE**. List missing pages. "Features missed" symptom. |
   | **SoW Phase 3 / Database §2 entities** (every entity) | each entity → in TASK-001 (schema) or a feature-specific schema task | **REFUSE TO SAVE**. List missing entities. |
   | **SoW Phase 5 events** (when present) | each event → at least one producer task AND at least one consumer task | **REFUSE TO SAVE**. List orphan events. |
   | **SoW Phase 5.5 business processes** (when present) | each process → ordered task sequence preserving the transition (e.g. booking pending → tutor accepts → payment) | **REFUSE TO SAVE**. List unmapped flows. |
   | **Brief §8 third-party integrations** (Stripe, SendGrid, Twilio, S3, Cloudinary, etc.) | each integration → at least one task with the integration name in `Functional notes:` | **REFUSE TO SAVE**. Integrations silently dropped is "features missed". |
   | **Architecture style folder structure** | every task's `Files to create/modify:` paths must conform to `deliverables/architecture/styles/<style>.md` Folder structure | **REFUSE TO SAVE**. List offending paths + the rule they break. |
   | **Component decomposition** (UI tasks) | no task creates a page file >200 lines or assigns multiple unrelated concerns to one component file | **REFUSE TO SAVE**. List offending tasks; require splitting before save. |

   Show coverage like:
   ```text
   Coverage gate:
     SoW Phase 4 endpoints:  47 / 47 mapped       ✓
     SoW Phase 7 pages:      23 / 23 mapped       ✓
     SoW Phase 3 entities:   18 / 18 mapped       ✓
     SoW Phase 5 events:      9 / 9 mapped        ✓
     Brief §8 integrations:   4 / 5 mapped        ✗ FAIL  (missing: Twilio SMS)
     Style folder paths:    142 / 142 conform     ✓
     Component budgets:      ALL ≤200 lines       ✓
   GATE: FAIL — refusing to save TASKS.md until Twilio SMS is mapped to a task.
   ```

3. **Show coverage details:**
   - screens mapped / total
   - endpoints mapped / total
   - models mapped / total
   - major flow transitions mapped / total
   - integrations mapped / total

4. **List inferred items and unresolved gaps.**

5. **If the coverage gate failed, do not ask for write confirmation.** Tell the user exactly which items are unmapped and offer to:
   - (a) Add a task for each missing item, or
   - (b) Mark the item explicitly out-of-scope (requires updating the 5 HTMLs), or
   - (c) Re-run `import-docs` if the missing items reveal that the 5 HTMLs itself is incomplete.

6. **If the gate passed, ask:** "Coverage is 100% across all source-of-truth items. Reply 'yes' to write state/TASKS.md, or tell me what to adjust."

7. Only write the file after the user confirms AND the coverage gate passes.

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
   <ISO>  parse-scope  DOCS_COMPLETE → TASKS_GENERATED  <N> tasks generated
   ```

3. Tell user: *"<N> tasks generated. Next: run `/approve-tasks` to audit, then `/start-build` to begin parallel build."*
