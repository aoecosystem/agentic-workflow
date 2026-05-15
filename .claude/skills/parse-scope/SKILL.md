---
name: parse-scope
description: Generate (or regenerate) TASKS.md from a filled-in state/SCOPE.md, with one executable task block per unit of work grouped by feature, dependency edges, agent assignments, traceability refs, attempt budget, acceptance criteria, and optional design fields. Runs a ReqOps pre-pass when .pipeline/sow.md or inputs/ SOW is present. Trigger when the user says "parse scope", "generate tasks", "break this scope into tasks", or asks for a task list from a completed SCOPE.md. This skill is the sole writer of TASKS.md.
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

**Purpose:** Read `state/SCOPE.md` and generate a structured `state/TASKS.md` with one task block per unit of work, grouped by feature, with dependencies, agent assignments, MCP URLs, files, and acceptance criteria. When SOW sources exist (prefer `inputs/`), run a ReqOps requirements pass first so Builder/QA criteria are SOW-grounded and testable.

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
- `state/SESSION-STATE.md` — locate `Architecture style:` field (one of `monolith`, `hybrid`, `microservices`, `polyglot-microservices`, `serverless`). This is a **HARD CONTRACT** — every task's `Files to create/modify:` paths must conform to the matching style profile.
- `deliverables/architecture/styles/<style>.md` — **HARD CONTRACT**. Read this profile's "Folder structure" section. Every file path you emit in TASKS.md must sit under a folder declared by this profile. Memorize:
  - The FE/BE split (e.g. `apps/api/` + `apps/web/` for monolith — never combined)
  - The ORM folder convention (Prisma → `prisma/`, Drizzle → `drizzle/`, TypeORM/Sequelize/Kysely/MikroORM → `database/`)
  - Root-level `infra/` (compose, docker, scripts, environments)
  - Role-based app naming (`apps/api/`, NOT `apps/<slug>-api/`)
  - For component files: `components/<feature>/<Concern>.tsx` granularity (Header → HeaderNav.tsx + HeaderLogo.tsx + HeaderUserMenu.tsx; Footer → FooterLinks.tsx + FooterSocial.tsx; Profile page → ProfileAvatar.tsx + ProfilePersonalInfo.tsx + ProfileUpdatePassword.tsx)
- `state/SCOPE.md` — full content. Pay special attention to:
  - **Section 3 Tech Stack** — every task block must record the resolved frontend / backend / ORM choices in its `Stack:` field.
  - **Section 5 Feature Breakdown** including every Phase 4 API endpoint and Phase 7 Page Inventory row.
  - **Section 8 Page Inventory** — every page must appear in at least one UI task.
  - **Section 9 Database Schemas** — every entity must appear in TASK-001 (schema task) or a feature-specific schema task.
  - **Section 12 Design Language** — UI tasks reference this for visual style, palette, font pairing, component library, and component decomposition rules.
- `state/TASKS.md` — check if tasks already exist (ask user before overwriting).
- `memory/ARCHITECTURE.md` — if it exists, use its module map to assign file paths.
- `memory/STACK-GUIDANCE.md` — if it exists, use it to keep tasks aligned with the chosen stack's architecture, UI, and testing conventions.
- `memory/PAGES.md` — if it exists, the authoritative page inventory; cross-check against SCOPE §8.
- `inputs/` SOW/requirements docs — supplemental ReqOps source only.
- `.pipeline/sow.md` — fallback ReqOps source if inputs/SCOPE SOW is unavailable.
- `.pipeline/requirements.md`, `.pipeline/features-list.md`, `.pipeline/system-design-provided.md`, `.pipeline/features/requirements/` — supplemental if present.

**Failure modes:** if SESSION-STATE has no `Architecture style:` field, refuse with "Architecture style missing — re-run /build-scope-of-work to lock Phase 9". If `deliverables/architecture/styles/<style>.md` does not exist, halt — never improvise a folder structure.

### Step 2 — ReqOps pre-pass (when SOW sources exist)

If SOW sources exist in `inputs/`, `state/SCOPE.md`, or `.pipeline/sow.md`:
1. For each feature detected in `state/SCOPE.md` section 5, run ReqOps logic (see `reqops` skill) and create/update:
   - `.pipeline/features/requirements/<feature-id>-<feature-slug>-requirements.md`
2. Enforce ReqOps source precedence (`inputs/` SOW first, then `state/SCOPE.md`, then `.pipeline/sow.md` fallback) over lower-precedence pipeline docs.
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
- `[ ]` Lint and typecheck pass
- `[ ]` Behavior matches mapped scope items (screens/endpoints/models/flow transitions) for this task
- `[ ]` All files declared in `Files to create/modify:` sit under folders declared by `deliverables/architecture/styles/<style>.md` (no improvised top-level folders, no slug-prefixed app names, no combined FE+BE folder)

**For API tasks (every task that adds or modifies an HTTP endpoint), the AC baseline tightens — vague "happy + one error" is not sufficient. Every endpoint MUST have explicit test cases for:**
- `[ ]` `200`/`201` success path with a representative valid payload
- `[ ]` `401` Unauthorized when the route is protected (omitted only if route is documented public in SCOPE.md)
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
- Architecture style: <monolith | hybrid | microservices | polyglot-microservices | serverless>     ← from SESSION-STATE
- Stack: { frontend: <name>, backend: <name>, orm: <name>, db: <name> }                            ← from SoW Phase 6 / SCOPE §3
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
  - [ ] Every entity from SCOPE.md §9 Database Schemas exists with all columns + types + constraints
  - [ ] Every relationship from SCOPE.md §9 is wired in the schema
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
   - (b) Mark the item explicitly out-of-scope (requires updating SCOPE.md), or
   - (c) Re-run `import-docs` if the missing items reveal that SCOPE.md itself is incomplete.

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
   <ISO>  parse-scope  SCOPE_PARSED → TASKS_GENERATED  <N> tasks generated
   ```

3. Tell user: *"<N> tasks generated. Next: run `/approve-tasks` to audit, then `/start-build` to begin parallel build."*
