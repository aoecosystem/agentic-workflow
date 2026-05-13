# Changelog

All notable changes to the agentic-workflow template are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.2.0] — Node.js standards + token-efficient profiles

Standards release. Adds a "Quick reference card" to every architecture
style profile, locks down Node.js project structure conventions
(folders + tech defaults), and adjusts `infra/` placement per style.

### Added

- **Quick reference card** at the top of every architecture style profile.
  Builders read ~30 lines (folder tree + tech defaults table) for 95%
  of tasks. Saves ~200 tokens per build-task invocation.
- **Standard `apps/api/` layout** in `monolith.md` (Fastify default):
  `src/{server.ts, app.ts, config/, plugins/, modules/, middleware/,
  events/, jobs/, lib/, utils/, types/, <orm-folder>/}` with consistent
  per-module shape (`*.routes.ts`, `*.service.ts`, `*.schema.ts`,
  `*.repo.ts`, `*.test.ts`).
- **Standard `apps/web/` layout** across all 5 profiles:
  `src/`, `public/`, `docs/`, `test/{unit, e2e?}/`. `test/e2e/` is
  added when SoW Page Inventory has ≥3 multi-step flows OR style is
  microservices / polyglot-microservices.
- **Tech defaults tables** in every profile so the agent picks the
  same lighter / faster stack each time: Fastify (vs Express), Drizzle
  (vs Prisma), Pino, Zod, BullMQ, Next.js + Tailwind + shadcn/ui,
  TanStack Query, Zustand, Vitest, Playwright, Biome, pnpm.
  Serverless adds Hono on Cloudflare Workers + Neon.

### Changed

- **`infra/` placement is now style-dependent:**
  - `monolith` / `hybrid` → `apps/infra/` (inside `apps/`, next to
    `api/` and `web/`). Dev orchestration lives next to the apps it
    orchestrates.
  - `microservices` / `polyglot-microservices` / `serverless` → root
    `infra/` (cluster-wide k8s, mesh, gateway, IaC).
- **`packages/` is now conditional:**
  - `monolith` → NOT created by default (use `apps/shared/` if FE+BE
    share TS types).
  - `hybrid` → empty until first extraction (created at extraction
    time as `packages/ports/`, `packages/events/`, `packages/proto/`).
  - `microservices` / `polyglot-microservices` → required
    (`packages/{proto,events,types,ui}`).
  - `serverless` → required (`packages/{db,auth,events}`).
- **`build-task` Step 1** reads the Quick reference card first,
  full profile only for scaffold or non-standard tasks.
- **`parse-scope` TASK-000 template** updated: `Files to create/modify`
  no longer hardcodes root `infra/`; acceptance criteria call out the
  style-correct `infra/` location and conditional `packages/`.
- **Biome over ESLint+Prettier** as default linter (10-15× faster,
  one tool, drop two dev deps). ESLint+Prettier remain as alternatives
  if the SoW picks them.

### Removed

- `GEMINI.md` — duplicated `AGENTS.md` content with no unique value.
  Antigravity reads `.agent/` natively; the 94-line bootstrap pointer
  was noise.

### Rationale

Two test runs (`sitora-tours`, `saas-email`) produced different
folder layouts and tech picks because:
1. The agent had no quick canonical reference — it re-derived the
   structure from the full profile each time (lossy on long contexts).
2. Tech picks were free-form per task instead of locked at the SoW.
3. `infra/` was always at root, but for `monolith` projects the
   orchestration concerns are app-local, not cluster-level.
4. `packages/` was created unconditionally, but a single-team
   monolith has no use for it.

v2.2 removes all four sources of drift.

---

## [2.1.0] — Pipeline fidelity + triple-mirror completion

Reliability release. Tracked back from two real-world runs (sitora-tours,
saas-email) that produced different folder layouts for the same engine.
Root causes: data flow gaps and an incomplete triple-mirror.

### Fixed

- **`import-docs` now actually reads the 5 HTML deliverables.** Previously
  only read `inputs/*.md` and `docs/*` raw files, so SoW Phase 4 endpoints,
  Phase 7 Page Inventory, Phase 6 Tech Stack, Phase 9 Design Language,
  and the architecture / database / infrastructure HTMLs were never
  propagated into SCOPE.md. Caused "API partly worked", "features
  missed", "different folders each run", "design not classic web pages".
  Tier 1 (5 HTMLs) is now canonical; Tier 2 (markdown) is fallback only.
- **`parse-scope` now reads Architecture style and propagates it.** Reads
  `state/SESSION-STATE.md → Architecture style:` and `deliverables/architecture/styles/<style>.md`
  as HARD CONTRACTS. Every task block now carries `Architecture style:`,
  `Stack:`, `Folder root:` fields. Refuses to save if any task path
  doesn't conform to the style's folder structure.
- **Coverage gate in `parse-scope` Step 8.** Refuses to save TASKS.md
  unless 100% of SoW Phase 4 endpoints, Phase 7 pages, Phase 3 entities,
  Phase 5 events, Phase 5.5 processes, Brief §8 integrations are mapped
  to at least one task.
- **Tighter API acceptance criteria.** Baseline AC for API tasks now
  requires explicit `200/201` + `401` (when protected) + `403` (when
  role-gated) + `4xx` validation + `404` (path params) + `5xx` test
  cases. "Happy + one error" is no longer sufficient.
- **UI acceptance criteria locked.** Component self-containment
  (no static arrays as props, no `.map()` over static literals, one
  concern per file ≤200 LOC, design tokens only) baked into every UI
  task block.
- **Triple-mirror completed for commands.** 33 commands now mirrored
  byte-identical across `.claude/commands/`, `.cursor/commands/`,
  `.agent/commands/`. Previously only `.claude/commands/` existed —
  Cursor and Antigravity had zero slash-command access.
- **`ui-ux-pro-max` drift reconciled.** `.cursor/` had no frontmatter
  (so auto-trigger broken); `.agent/` had stale "50 styles" metadata
  from pre-v2. All three trees now byte-identical (v2 with 67 styles
  / 96 palettes / 57 font pairings).
- **`INSTRUCTIONS.md` created.** CLAUDE.md mandates reading it on every
  session start; previously the file didn't exist.
- **Docs hygiene.** Removed `/audit-tasks` references from README
  (orphan command — `/approve-tasks` is the real audit). Updated
  `28 skills, 29 commands` count to `33 skills, 33 commands` across
  README / CLAUDE.md / AGENTS.md.

### Why this matters

The user's complaints — "different folders each run, methods confused,
commands not found, features missed, design not classic, API partly
worked" — all trace to the same root cause: data from the 5 HTML
deliverables never reached the build phase, and Cursor/Antigravity
had no commands at all. Both are fixed now. Same engine, same input,
same output, every time.

---

## [2.0.0] — Workspace-aware architecture profiles + UI design intelligence

Released 2026-05-12. Major upgrade based on the sitora-tours real-world
run.

### Added

- **Workspace monorepo as default** across all 4 architecture style
  profiles (`monolith`, `hybrid`, `microservices`, `serverless`).
  `pnpm-workspace.yaml` + per-app `package.json` + `tsconfig.base.json`
  at root.
- **New 5th style: `polyglot-microservices.md`.** Multi-language
  microservices (Node + Go + Python + Java + Rust) with `go.work`,
  `pyproject.toml + uv.lock`, `Cargo.toml`, `settings.gradle.kts`,
  buf-based contract codegen, language-baseline docs, uniform Makefile
  targets per service.
- **Component self-containment rule** across all 5 style profiles.
  Static UI data (nav, footer, FAQ, dropdown options, social icons)
  lives INSIDE the rendering component; pages never pass static
  arrays as props; no `.map()` over build-time literals; one concern
  per file under `components/<feature>/<Concern>.tsx`; ≤200 lines
  per file.
- **`ui-ux-pro-max` skill** installed via `npx uipro-cli init` — 67
  visual styles, 96 color palettes, 57 font pairings, 99 UX guidelines,
  25 chart types, 13 frontend stacks.
- **Hard UI quality gate in `build-task` Step 7.** CRITICAL/HIGH
  ui-ux-pro-max rules (accessibility 4.5:1 contrast, 44×44 touch
  targets, viewport meta, design tokens only) block task handoff
  like a failing test.
- **Design language locked in SoW Phase 9** — visual style, color
  palette, font pairing, component library, chart types chosen ONCE
  and treated as a hard contract by every later UI task.
- **HARD-REJECT QA gate (Step 6e)** for component-architecture
  violations: static arrays as props, `.map()` over static literals,
  page files with inline section JSX, files past size budget.

### Changed

- **Folder structure rules** in every style profile clarify FE/BE
  split (`apps/api/` + `apps/web/`, never combined), root-level
  `infra/`, ORM-aware folder naming (Prisma → `prisma/`, Drizzle →
  `drizzle/`, others → `database/`), role-based app names
  (NOT slug-prefixed).
- **`build-task` Step 1** now treats `deliverables/architecture/styles/<style>.md`
  as a HARD CONTRACT — every file placed must sit under a folder
  declared by the profile.

---

## [1.0.0] — Initial release

First public release of the agentic-workflow engine — a unified
project pipeline that spans the docs phase (5 HTML deliverables:
Project Brief, Scope of Work, System Architecture, Database Diagram,
Infrastructure Diagram) and the build phase (multi-agent orchestrator
+ builders + QA loop generating code in `../apps/`).

### Architecture

- **Single state machine** spanning 21 stages from `INIT` to
  `READY_TO_DEPLOY`, with explicit `/approve-*` gates between every
  phase. The agent never auto-advances.
- **One repo, two phases** — agentic-workflow is the superset of
  project-foundations; one source of truth (`state/SESSION-STATE.md`)
  carries the project from idea to verified, ready-to-deploy code.
- **Triple-mirror skills** — every skill is byte-identical across
  `.claude/`, `.cursor/`, and `.agent/` IDE trees, verified inline by
  md5 (no external sync script).
- **Architecture styles** — `monolith` / `hybrid` / `microservices` /
  `serverless` profile files shape every build skill's output.
- **Manual edit protocol** — SHA-256 hash tracking on every artifact.
  Manual edits are detected, surfaced, and reconciled (accept + bump
  version + audit log) before any skill writes.

### Skills (32 total)

**Docs phase (16):** brief interview, build-/review-/approve- triplets
for scope-of-work, architecture, database, infrastructure; status,
reset, start-project router.

**Build phase (12):** import-docs, parse-scope, delta-scope, reqops,
api-contract, figma-plugin-ingest, fetch-mcp, orchestrate, build-task,
qa, approve-tasks, approve-build, verify-build, package-release.

### Quality gates

- **Clarifying-questions loop** in `import-docs` — HIGH / MEDIUM / LOW
  severity buckets with a hard 95% accuracy gate before any file is
  written. Eliminates fabricated values from under-specified briefs.
- **Native runtime build** in `qa` (Step 4b) and `verify-build`
  (Gate 2b) — typecheck-only approvals are rejected. The project's
  declared build command must exit 0 and produce a runnable artifact.
- **Scaffold-task sub-rule** in `qa` — TASK-000 / MOD-00 cannot be
  approved on green tests + lint alone; the build artifact must
  start.
- **Deferred-language detection** in `qa` (Step 6d) and `verify-build`
  (Gate 2c) — unlinked `TODO` / `FIXME` / `@ts-ignore` /
  "we'll fix later" / placeholder-flag-off ACs are rejected unless a
  follow-up task is referenced by ID.
- **App-shell routing guard** auto-task (`TASK-000A`) emitted by
  `orchestrate` immediately after scaffold completes. No feature
  builder runs until the app shell is verified to boot, navigate, and
  handle 404 + auth-gated routes cleanly.

### Folder layout

```
agentic-workflow/
├── deliverables/        ← 5 HTML deliverables (brief, scope-of-work,
│                          architecture, database, infrastructure,
│                          designs) + architecture-style profiles
├── inputs/              ← optional: raw PDFs / docs to ingest
├── state/               ← SESSION-STATE.md + SCOPE.md + TASKS.md
│                          (single source of truth across both phases)
├── memory/              ← architecture, patterns, decisions,
│                          stack-guidance, pages, contracts, mcp-cache
├── docs/                ← framework docs + prompts
├── .claude/skills/      ← Claude Code skills + slash commands
├── .cursor/skills/      ← Cursor mirror
└── .agent/skills/       ← Antigravity mirror
```

Generated code lives in `../apps/<sub-app>/` (sibling level), never
inside `agentic-workflow/`.
