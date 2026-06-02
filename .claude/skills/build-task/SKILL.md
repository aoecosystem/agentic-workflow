---
name: build-task
description: Implement exactly one task from TASKS.md end to end — consume Figma/codegen artifacts, fetch MCP context when needed, write the vertical slice, run local verification (lint, typecheck, tests, acceptance, design fidelity, security, observability), enforce attempt budget, and hand off to QA. Trigger when Orchestrator assigns a task to Builder, or when the user says "build this task", "build TASK-XX", or "continue the current task". One task per run; never spans features silently.
---

## Stage gate (RUN FIRST)

1. Read `SESSION-STATE/SESSION-STATE.md`. Locate `Stage:`.
2. Refuse unless Stage is `TASKS_APPROVED` or `BUILDING`. Message:
   > "build-task is only valid from `TASKS_APPROVED` or `BUILDING`. Current: `<STAGE>`. Run `/approve-tasks` first, then `/start-build` to enter BUILDING."
3. Refuse if the task ID provided does not exist in `SESSION-STATE/TASKS.md`.

# Skill: Build Task

**Triggered by:** Orchestrator assigning a task to a Builder agent

**Purpose:** Implement one task from `SESSION-STATE/TASKS.md` completely — consume unified Figma ingest/codegen artifacts when present, fetch MCP context if needed, implement the vertical slice, run verification, and hand off to QA.

---

## Steps

### Step 1 — Read context

Before writing any code:
1. Read the task block from `SESSION-STATE/TASKS.md` (full block including acceptance criteria). **Extract these fields if present** — they OVERRIDE the SESSION-STATE defaults for this task:
   - `Architecture style:` — task-local style (one of monolith / hybrid / microservices / polyglot-microservices / serverless)
   - `Stack:` — task-local stack choices `{ frontend, backend, orm, db }`
   - `Folder root:` — task-local folder root (e.g. `apps/api/prisma/`, `apps/web/src/features/booking/`)
   These fields are written by `parse-scope` and are the AUTHORITATIVE source. Only fall back to SESSION-STATE if a field is absent or `inherited`.
2. Read the 5 deliverable HTMLs — the relevant feature section only.
3. Read `SESSION-STATE/SESSION-STATE.md` — note the `Architecture style:` field (monolith / hybrid / microservices / polyglot-microservices / serverless). This is the FALLBACK only when the task block doesn't specify. Otherwise the task block wins.
4. Read `CONTEXT/architecture-styles/<style>.md` — start with the **Quick reference card** at the top (everything you need for 95% of tasks); read deeper sections only if the task is scaffold or non-standard. The **Folder structure** section is a HARD CONTRACT. Every file you create or move must land at the path declared by this profile. If the file doesn't fit any declared folder, stop and surface a question — never invent a new top-level folder. Note especially:
   - **FE/BE split rules** (e.g. `apps/api/` vs `apps/web/` for monolith — never combined)
   - **ORM folder convention** — for monolith with Prisma → `apps/api/prisma/`, with Drizzle → `apps/api/drizzle/`, with TypeORM/Sequelize/Kysely/MikroORM → `apps/api/database/`
   - **`infra/` location is style-dependent:**
     - `monolith` / `hybrid` → `apps/infra/` (inside `apps/`, next to `api/` and `web/`)
     - `microservices` / `polyglot-microservices` / `serverless` → root-level `infra/` (cluster-wide / IaC concerns)
   - **No slug-prefixed app folders** — `apps/api/`, NOT `apps/<slug>-api/`
   - **`packages/` is conditional:** monolith → NOT created; hybrid → empty until first extraction; microservices / polyglot → required (proto, events, types); serverless → required (db, auth, events)
5. Read `memory/ARCHITECTURE.md` — find project-specific overrides on top of the style profile.
6. Read `memory/PATTERNS.md` — identify which patterns apply to this task.
7. Read `memory/DECISIONS.md` — note any past decisions that constrain this task.
8. Read `memory/STACK-GUIDANCE.md` when it exists — use it for stack-specific architecture, state, UI, and testing defaults.
9. If present, read task fields: `Design source`, `Codegen artifact`, `Design checklist`, `Visual baseline refs`, `Plugin artifact refs`.
10. If present, read the product-context addendum: `User value`, `User flow`, `Functional notes`, `Edge cases`, and `Test cases`.
11. **For ANY UI task** (component, page, layout, styling, form, modal, table, chart, navigation, etc.), invoke the `ui-ux-pro-max` skill before planning. Use it to:
    - Pick / confirm the visual style (from 67 styles — glassmorphism / minimalism / bento grid / dark mode / etc.) consistent with the project's chosen design language in the SoW
    - Pick / confirm the color palette (from 96 palettes) — never hardcode arbitrary colors
    - Pick / confirm the font pairing (from 57 pairings) — heading + body
    - Read the relevant UX guidelines for the element being built (e.g. forms, modals, tables) — including accessibility, touch targets, focus states, error feedback
    - For charts: pick the right chart type (from 25 types) for the data being shown
    Record the design choices in the task's `QA notes:` so reviewers and downstream tasks reuse them.

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
8. **If the task is a new feature or bug fix**, invoke the **`tdd-guide`** Claude Code subagent (via the Task tool with `subagent_type: tdd-guide`) to draft the test cases FIRST. Implement to pass them. This is the TDD discipline Claude Code ships with — use it instead of re-inventing.

Do not start writing code until this plan is clear.

### Step 6 — Implement in vertical slice order

Build in this order (skip layers not applicable to the task):

1. **Data model / types** — define TypeScript types, Zod schemas, or ORM model first. Everything else depends on these.
2. **Database layer** — migrations or schema changes if this task touches the DB.
3. **Service layer** — business logic with no HTTP or UI concerns.
4. **API layer** — route handlers, input validation, error responses.
5. **UI layer** — screens, components, hooks. If codegen artifact exists, implement scaffold first, then behavior wiring. Preserve token/state/breakpoint constraints from artifact.
6. **Tests** — write tests for each layer touched. Happy path + error cases. Co-locate with code OR in `test/{unit, e2e?}/` for `apps/web/` (per v2.2 standard layout) OR in `test/{integration, e2e?, unit}/` for `apps/api/`. Use the style profile's standard, not arbitrary plural `tests/`.

**Rules during implementation:**
- Read any existing file before editing it.
- **Folder placement is non-negotiable** — every new file MUST sit at a path declared by `CONTEXT/architecture-styles/<style>.md` → Folder structure. If unsure, re-read that section. Never dump everything into a single combined folder (e.g. `apps/<slug>/`) when the style requires a FE/BE split.
- **ORM folder respects the chosen ORM** — Prisma → `prisma/`, Drizzle → `drizzle/`, TypeORM/Sequelize/Kysely/MikroORM → `database/`. Do not hardcode `prisma/` if the project uses a different ORM.
- **First task of the build phase** scaffolds the workspace: root `package.json`, `pnpm-workspace.yaml` (or equivalent), `tsconfig.base.json`, shared `biome.json` (or `eslint.config.mjs`), and the style-correct `infra/` skeleton (`apps/infra/` for monolith+hybrid; root `infra/` for microservices+polyglot+serverless) — so subsequent tasks have somewhere to land.
- **UI tasks follow `ui-ux-pro-max` HARD RULES** — these are not suggestions:
    - **Accessibility (CRITICAL):** color contrast ≥ 4.5:1 for normal text, visible focus rings on every interactive element, descriptive `alt` text, `aria-label` for icon-only buttons, tab order matches visual order, `<label htmlFor>` on every form field
    - **Touch & interaction (CRITICAL):** minimum 44×44px touch targets, `cursor-pointer` on clickable elements, disable buttons during async operations, error feedback near the problem
    - **Layout & responsive (HIGH):** `<meta name="viewport" content="width=device-width, initial-scale=1">`, minimum 16px body text on mobile, no horizontal scroll, content reflows below 360px
    - **Typography & color (MEDIUM):** use the chosen palette and font pairing as CSS variables / Tailwind tokens — NEVER hardcode hex colors or pixel font sizes inline. The first UI task scaffolds these tokens; every later UI task imports them.
    - **Performance (HIGH):** WebP / responsive images with `srcset`, `loading="lazy"`, respect `prefers-reduced-motion`, reserve space for async content to prevent layout shift
- **Frontend-stack-specific rules** — read the relevant `data/stacks/<stack>.md` reference inside the `ui-ux-pro-max` skill folder for the project's chosen frontend (React / Next.js / Vue / Svelte / SwiftUI / React Native / Flutter / Tailwind / shadcn-ui).
- **Component architecture (frontend tasks) — HARD CONTRACT, no exceptions:**
    - **Component self-containment.** Static UI data (nav items, footer link groups, FAQ rows, dropdown options, social icons, hero feature lists, etc.) lives **inside the component file that renders it**. Pages must NOT pass static arrays as props. Translation is the only allowed external dependency — components call `t('header.nav.home')` directly, with i18n keys living in the locale files, not in a prop array. Pages only pass **dynamic** data (the authenticated user, fetched API/DB content, route state) as props — never static UI scaffolding.
    - **No `.map()` for static lists.** If the list is fixed at build time (nav, footer columns, FAQ, social, language switcher, etc.), render each item directly as JSX. `.map()` is reserved for dynamic data from API/DB/store. A static `const items = [...]; items.map(...)` pattern is a violation — replace it with explicit JSX per item.
    - **One concern per file.** Page files orchestrate sections only; they do NOT contain the JSX for those sections. Split pages by **logic boundary**, not by visual chunk. Example: profile page → `components/profile/ProfileAvatar.tsx`, `components/profile/ProfilePersonalInfo.tsx`, `components/profile/ProfileUpdatePassword.tsx`, `components/profile/ProfileDeleteAccount.tsx`. Header gets its own folder if it contains sub-pieces (logo, nav, language switcher, user menu) — each in its own file.
    - **File size budget.** Component files target 50–200 lines. Past ~200 lines or two unrelated logic concerns in one file → split immediately. The Step 7 quality gate enforces this.
    - **Anti-pattern (FAIL the gate):** `<Header items={navItems} />` where `navItems` is a static array defined in the page or a `data.ts` file. Correct: `<Header />` and the nav items are inside `Header.tsx` rendered as explicit JSX with `t()` calls.
- Follow patterns from `memory/PATTERNS.md` exactly.
- Follow `memory/STACK-GUIDANCE.md` when present; treat it as the stack-specific implementation playbook for this project.
- Use the tech stack specified in the 5 deliverable HTMLs — do not introduce new dependencies without noting it.
- Handle all error paths. See the 5 deliverable HTMLs NFR section for expected error shape.
- No `TODO` comments. If something is incomplete, the task is not done.
- No `any` types without a documented reason in a comment.
- For Figma-driven mobile/app layouts, treat device chrome in design previews as non-app scaffolding. Implement the inner content layout only unless acceptance criteria explicitly require shell chrome.
- Reuse only `compatible` plugin fragments from `Plugin artifact refs`; treat `partial` output as hints and document any rejected fragments that would otherwise affect fidelity.

### Step 7 — Run verification gates

Run all gates from `01-verification.mdc` and `04-design-fidelity.mdc` when UI is involved:

1. **Lint** — run linter on all modified files (`biome check` or `eslint`). Fix all errors.
2. **Typecheck** — run `tsc --noEmit` (or equivalent). Fix all errors.
3. **Tests** — run tests scoped to changed files. All must pass.
4. **Acceptance criteria self-check** — go through every `[ ]` item in the task block. Verify each one is satisfied. Check them: `[x]`.

4b. **Claude Code code review (REQUIRED for every task that writes code).** Invoke the **`code-reviewer`** Claude Code subagent via the Task tool: `subagent_type: code-reviewer`. Pass it: the list of files changed, the diff scope, and the task's `User flow` + `Edge cases` so the review is task-grounded. The subagent reports CRITICAL / HIGH / MEDIUM / LOW issues. Fix every CRITICAL + HIGH before proceeding. MEDIUM are fixed when possible (note in `QA notes:` if intentionally deferred with a follow-up task ID). LOW are surfaced in `QA notes:` but don't block.

4c. **Security review (REQUIRED for tasks touching auth, secrets, API endpoints with user input, payment, file uploads, or any external surface).** Invoke the **`security-reviewer`** Claude Code subagent via the Task tool: `subagent_type: security-reviewer`. Same hand-off pattern. Any CRITICAL/HIGH finding blocks the task. Secret leaks (hardcoded keys, tokens, passwords in code) are auto-rejected at this gate.
5. **Design checklist self-check (UI only)** — validate token usage, state parity, and responsive requirements from `Design checklist`.
   - **AND** run the `ui-ux-pro-max` quality gate. Walk every CRITICAL + HIGH rule:
     - [ ] Accessibility: every interactive element has visible focus, 4.5:1 contrast, alt/aria where needed, keyboard tab order matches visual order
     - [ ] Touch: every clickable area ≥ 44×44px, `cursor-pointer` on clickables, disabled state during async
     - [ ] Layout: viewport meta present, ≥ 16px body on mobile, no horizontal scroll at 360–768–1024–1440px
     - [ ] Typography & color: ZERO hardcoded hex / pixel sizes — all values resolve to design tokens (CSS vars / Tailwind theme / shadcn tokens)
     - [ ] Performance: images optimized + lazy where below the fold; `prefers-reduced-motion` respected; layout shift prevented
     - [ ] Style consistency: visual style matches the one chosen in the SoW (no mixing minimalism + claymorphism in the same page)
     - [ ] Component self-containment: ZERO static data arrays passed as props. Pages pass only dynamic data + translation keys. Static lists (nav / footer / FAQ / social / dropdown options) live inside the component that renders them, with each item as explicit JSX (no `.map()` over a build-time array)
     - [ ] One concern per file: every logical section sits in its own file under `components/<feature>/<Concern>.tsx`. No file exceeds ~200 lines. Pages orchestrate components — they do not embed section JSX
   - **Failing ANY checkbox = task fails the gate.** Same severity as a failed lint or test — fix before proceeding to Step 8.
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

Update the task block in `SESSION-STATE/TASKS.md`:
```
- Status: in-review
```

Update the progress table counts.

### Step 10 — Pick up next task

After marking `in-review`, immediately check the Builder's assigned chain in `SESSION-STATE/TASKS.md` for the next `pending` task with all dependencies met. If found, start Step 1 for it without waiting for QA to finish the current task.

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
