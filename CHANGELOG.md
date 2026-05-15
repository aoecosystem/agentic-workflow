# Changelog

All notable changes to the agentic-workflow template are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.6.0] — Engine integrity: stage machine + cross-skill contracts

Critical reliability release. A 4-dimensional audit (command wiring,
stage machine, cross-skill data flow, regression check) found the
engine had structural bugs that explained the user's "confused"
real-world runs. v2.6 fixes them.

### Fixed — P0 (the docs→build handoff was broken)

- **`approve-infrastructure` now transitions to `DOCS_COMPLETE`, not `COMPLETE`.** Previously the docs-phase final approval emitted `COMPLETE` but `import-docs` and `parse-scope` required `DOCS_COMPLETE` — meaning **the build phase could never start**. The two halves of the engine literally did not connect. This single bug explains every "I approved infrastructure but nothing happens" report.
- **`import-docs` Tier 1 table cited wrong section numbers** for architecture/database/infrastructure HTMLs (claimed §3/§4/§5 etc., actual templates have §2/§3/§6/§7/§9). Rewrote with verified section addresses; added a 13th SCOPE row for brief §13 (AI Generation Instructions).
- **`build-task` and `qa` now read task-block `Architecture style:` / `Stack:` / `Folder root:` fields** (v2.2 wrote them; the readers ignored them). `build-task` Step 1 now prefers task-block values over SESSION-STATE; `qa` Step 1 checks file paths conform to `Folder root:`.
- **`build-architecture`, `build-database`, `build-infrastructure` now support `polyglot-microservices`** (the 5th style was added to `build-scope-of-work` in v2.0 but the 3 downstream skills still only listed 4). Polyglot SoWs no longer generate malformed downstream HTMLs.
- **`verify-build` now knows Biome** (the v2.2 default linter). Previously only listed ESLint, causing Biome-clean codebases to fail the final gate spuriously.

### Fixed — P1 (significant inconsistencies)

- **AGENTS.md and CLAUDE.md command tables now include `/approve-tasks`, `/approve-build`, `/verify-build`, `/package-release`** — all 4 existed as files but were missing from the canonical command lists.
- **CLAUDE.md command-list summary now also lists those 4 commands** and the stale "28 skills, 29 commands" header was already corrected to 33/33 in v2.2.
- **4 skill descriptions gained slash-form triggers** (`figma-plugin-ingest`, `fetch-mcp`, `orchestrate`, `qa`) — auto-trigger from `/figma-ingest`, `/refresh-mcp`, `/start-build`, `/qa-only`, `/resume-build` now works.
- **`start-project` smart router** now has explicit routing rows for every docs-phase AND build-phase stage (was only complete for docs phase).
- **`INSTRUCTIONS.md` now includes `/approve-build`** between `/start-build` and `/verify-build` (was missing — user following the guide would hit `/verify-build` refusal).
- **`parse-scope` Step 1** now explicitly reads SCOPE §3 / §4 / §5 / §6 / §7 / §8 / §9 / §10 / §11 / §12 / §13 (previously only §3/§5/§8/§9/§12 — dropping MCP URLs, NFRs, Out-of-Scope, Infrastructure).
- **`parse-scope` Step 1** infra/ phrasing fixed: now style-dependent (apps/infra/ for monolith+hybrid; root infra/ for microservices+polyglot+serverless) instead of unconditional "root-level infra/".
- **Stage gates added to 5 lax skills**: `build-task`, `qa`, `delta-scope`, `reqops`, `api-contract` previously had no stage gate and could run at INIT (which would have made them silently wrong). Each now refuses outside its valid stage window.
- **`AGENTS.md` Triple-mirror verification row removed** (v2.3 deleted the mirror trees; the row described a contract that no longer existed).

### Fixed — P2

- `build-task` test convention now references `test/{unit, e2e?}/` (v2.2 standard) instead of stale plural `tests/`.
- `.claude/settings.local.json` stale `.cursor/` / `.agent/` allowlist entries removed.
- `review-infrastructure` no longer accepts the orphan `COMPLETE` stage as a workaround for the P0-1 bug — uses `DOCS_COMPLETE` correctly now.

### Why this matters

Three structural problems explained every "confused run" report:
1. **Stage machine had a missing link** — `COMPLETE` vs `DOCS_COMPLETE` mismatch made the docs→build handoff fail silently.
2. **Cross-skill fields were aspirational, not enforced** — v2.2 wrote `Stack:` / `Architecture style:` / `Folder root:` to every task block but build-task and qa never read them.
3. **Import-docs Tier 1 was documented but didn't match template reality** — section numbers in the mapping table were wrong, so the v2.1 fix didn't actually extract everything.

All three are fixed. The engine now does what the docs say it does.

---

## [2.5.0] — Remove docs/ folder; inputs/ becomes single drop zone

Tidy release. The `docs/` folder held reference material that duplicated
what skills already enforce. Removing it.

### Removed

- `docs/` folder (8 files, 36 KB):
  - `TROUBLESHOOTING.md` — `/status` + `/reset` cover the same recovery paths
  - `BLOCKER-PLAYBOOK.md` — already inlined in `build-task` "Blocked task protocol"
  - `prompts/AUDIT-TASKS.md` — `/approve-tasks` runs this automatically
  - `prompts/REFINE-SCOPE.md` — `/delta-scope` does this
  - `prompts/DEBUG-BLOCKER.md` — duplicate of `BLOCKER-PLAYBOOK.md`
  - `prompts/RELEASE-NOTES.md` — covered by `/package-release`
  - 2 READMEs (just folder explainers)

### Changed

- **`inputs/` is now the single drop zone** for raw source documents. Previously
  the workflow had two: `inputs/` (preferred) and `docs/` (legacy fallback).
  Now there's just one.
- `import-docs` skill + command: removed Tier 2 `docs/` fallback path.
- `reqops` skill + command: SOW source precedence is now `inputs/` → `state/SCOPE.md`
  → `.pipeline/sow.md`.
- `parse-scope` skill: same precedence update.
- `scope-interview` + `delta-scope`: removed `docs/` references.
- `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `inputs/README.md`,
  `memory/ARCHITECTURE.md`: removed references to the removed folder.

### Rationale

Every file in `docs/` was either (a) duplicated by an active skill, or
(b) reference material for a manual workflow the agent automates. The
folder added ~36 KB of cognitive load with zero runtime impact.
`inputs/` already serves the legacy-migration drop-zone role, so the
two-drop-zone model collapses to one.

---

## [2.4.0] — Leverage Claude Code's built-in subagents

Workflow native to Claude Code. The build + QA flow now delegates to
Claude Code's stock subagents instead of re-implementing them inline.

### Changed

- **`build-task` Step 5** — new step 8: invoke the **`tdd-guide`**
  Claude Code subagent for every new-feature or bug-fix task to draft
  tests FIRST. Implement to pass them. Use the discipline Claude Code
  ships with instead of describing it inline.
- **`build-task` Step 7** — Gates 4b + 4c:
  - **4b: code review** via the **`code-reviewer`** subagent (Task tool
    `subagent_type: code-reviewer`). REQUIRED for every task that writes
    code. CRITICAL/HIGH blocks task handoff.
  - **4c: security review** via the **`security-reviewer`** subagent.
    REQUIRED when the task touches auth, secrets, API endpoints with
    user input, payment, file uploads, or external surfaces. Any
    CRITICAL/HIGH blocks. Hardcoded secrets are auto-rejected.
- **`qa` Step 5b** — new gate: fan out **`code-reviewer` + `security-reviewer`**
  in parallel via the Task tool (single message with two Task calls
  for concurrency, not serial). Merge findings, dedupe by file:line,
  apply severity rule (CRITICAL/HIGH reject; MEDIUM requires
  follow-up task ID; LOW annotate only). Subagent name is cited in
  rejection notes.
- **`orchestrate` Step 6** — Builder fan-out is now explicit: each
  Builder is a Claude Code subagent launched via the **Task tool with
  `subagent_type: general-purpose`**. Multiple Task calls in a single
  message run concurrently; sequential Task calls run serially. Same
  pattern for QA fan-out.

### Why

Claude Code ships specialized subagents (`code-reviewer`,
`security-reviewer`, `tdd-guide`) with calibrated prompts and tool
restrictions for their domain. Re-implementing the same logic inline
in qa / build-task duplicated effort and lost calibration. Delegating
to the stock subagents:

1. Halves wall-clock time on review (parallel Task calls instead of
   serial inline checks).
2. Inherits Claude Code's ongoing subagent improvements automatically.
3. Makes rejection notes more specific (subagent attribution helps the
   user see which gate failed).

### Migration note

No state file changes. The first build run on v2.4 will simply route
through the subagents — verdicts arrive faster and rejection notes
get the subagent attribution.

---

## [2.3.0] — Claude-only (drop Cursor + Antigravity mirrors)

Consolidation release. The triple-mirror across `.claude/`, `.cursor/`,
`.agent/` added complexity without payoff for a Claude-only user.
Everything Cursor- and Antigravity-related is removed.

### Removed

- `.cursor/` tree (skills + commands + rules) — 99 files.
- `.agent/` tree (skills + commands + rules) — 99 files.
- Triple-mirror contract documentation in `CLAUDE.md`, `AGENTS.md`,
  `README.md`, `CONTRIBUTING.md`, `docs/TROUBLESHOOTING.md`.
- "Cursor / Antigravity" mentions in `README.md`, `AGENTS.md`,
  `INSTRUCTIONS.md`, `docs/prompts/README.md`, `orchestrate/SKILL.md`.
- `GEMINI.md` references (file itself was already removed in v2.2.0).

### Why

The user runs exclusively Claude Code. Maintaining byte-identical
mirrors for IDEs that aren't used was pure overhead — every skill edit
required three writes + sha256 verification. Audit data showed the
mirrors had drifted in past releases despite the contract (the
ui-ux-pro-max skill had three different versions before v2.1.0
reconciliation). Single source of truth at `.claude/` is simpler.

### Migration note

If you ever need to add Cursor or Antigravity back, the skill files at
`.claude/skills/<name>/SKILL.md` are the canonical source — copy them
to the new tool's expected location. The byte-equality contract no
longer applies.

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
