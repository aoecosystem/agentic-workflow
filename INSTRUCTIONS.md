# agentic-workflow — step-by-step user guide

Welcome. This file is the human-facing walkthrough for running a project
through the agentic-workflow engine. Claude reads it at session start
so the agent already knows the lifecycle; you can read it any time to
remind yourself what the next command should be.

> **At a glance:** the engine runs in two phases — a **docs phase**
> that produces 5 HTML deliverables and a **build phase** that produces
> working code under `../apps/`. Every stage transition needs an
> explicit slash command. Nothing auto-advances.

See `AGENTS.md` for the full state diagram and command reference.
See `README.md` for the architecture overview.

---

## Quick orientation

```
agentic-workflow/                   ← you are here
├── deliverables/                   ← 5 HTML deliverables live here
│   ├── brief/                      ← Section 1: Project Brief
│   ├── scope-of-work/              ← Section 2: Scope of Work
│   ├── architecture/               ← Section 3: System Architecture
│   ├── database/                   ← Section 4: Database Diagram
│   ├── infrastructure/             ← Section 5: Infrastructure Diagram
│   └── designs/                    ← UI screenshots / Figma exports
├── state/                          ← auto-state, rarely human-edited
│   ├── SESSION-STATE.md            ← the brain — Stage + audit log
│   ├── SCOPE.md                    ← parsed from the 5 HTMLs
│   └── TASKS.md                    ← generated build tasks
├── memory/                         ← cross-session knowledge
├── inputs/                         ← optional: drop existing SoW docs here
└── ../apps/                        ← generated source code lives at sibling level
```

---

## Lifecycle commands (use in order)

### Phase 1 — Docs phase (5 HTML deliverables)

1. `/start-project` — universal smart router. Always start here. It
   reads `state/SESSION-STATE.md` and routes you to the next valid
   command based on current Stage.
2. **Brief interview** (13 sections, one question per turn) → produces
   `deliverables/brief/<slug>-brief.html` → Stage: `BRIEF_DRAFT`.
3. `/review-brief <section>` — edit any section. Bumps version.
4. `/approve-brief` — locks the brief → Stage: `BRIEF_APPROVED`.
5. `/build-scope-of-work` → fills the SoW HTML → `SOW_DRAFT`.
6. `/review-scope-of-work <phase>` then `/approve-scope-of-work` →
   `SOW_APPROVED`.
7. `/build-architecture` → fills architecture HTML → `ARCHITECTURE_DRAFT`.
   Then `/review-architecture` + `/approve-architecture` →
   `ARCHITECTURE_APPROVED`.
8. `/build-database` → fills database HTML → `DATABASE_DRAFT`. Then
   `/review-database` + `/approve-database` → `DATABASE_APPROVED`.
9. `/build-infrastructure` → fills infrastructure HTML →
   `INFRASTRUCTURE_DRAFT`. Then `/review-infrastructure` +
   `/approve-infrastructure` → `INFRASTRUCTURE_APPROVED` →
   immediately advances to **`DOCS_COMPLETE`**.

At any stage you can run `/status` to see exactly where you are and
which commands are valid next.

### Phase 2 — Build phase (generated code)

10. `/import-docs` — reads all 5 approved HTMLs and writes
    `state/SCOPE.md` + `memory/STACK-GUIDANCE.md` → `SCOPE_PARSED`.
11. `/parse-scope` — generates `state/TASKS.md` from SCOPE.md, runs the
    coverage gate (every SoW Phase 4 endpoint, Phase 7 page, Phase 3
    entity must map to ≥1 task) → `TASKS_GENERATED`.
12. `/approve-tasks` — senior-style task graph audit (acceptance
    criteria, dependency order, file ownership, no orphan deps) →
    `TASKS_APPROVED`.
13. `/start-build` — runs the orchestrator + builder + QA loop in
    parallel until all tasks are `done` → `BUILD_COMPLETE`.
14. `/verify-build` — final lint + typecheck + tests → `VERIFIED`.
15. `/package-release` → `READY_TO_DEPLOY`.

If you have existing SoW docs and want to skip the interview, drop them
in `inputs/` and run `/import-docs` directly (Tier 2 fallback path).

### Utility commands

- `/status` — read-only, prints current stage + next valid commands.
- `/show-status` — task progress table (Total / Done / In review / etc.).
- `/reset` — archive current session, start over.
- `/delta-scope` — re-plan when SCOPE.md changes.
- `/figma-ingest` — fetch design context from a Figma URL.
- `/refresh-mcp` — force re-fetch MCP cache.
- `/api-contract` — generate OpenAPI / gRPC / GraphQL contracts.
- `/qa-only` — run QA on any tasks currently `in-review`.
- `/resume-build` — continue the orchestrator after an interruption.

---

## Conventions to know

- **One question per turn** during interviews — the agent will not
  paste the whole brief at once.
- **Manual edits are welcome.** You can open any filled HTML or any
  generated code file and edit it directly. The agent hashes every
  artifact and will detect drift on the next read — it asks before
  overwriting.
- **`<slug>`** is the kebab-case project name from the brief
  interview. Every filled deliverable is prefixed with it
  (`my-project-brief.html`, etc.).
- **Empty templates are read-only.** `*-template.html` files stay
  empty so they can be reused for the next project.
- **Generated code lives in `../apps/`**, never inside this repo.
- **Never commit secrets or `.env` values.**

---

## Five-minute quickstart

1. Open Claude Code.
2. `cd` into this repo.
3. Type `/start-project`.
4. Answer the brief questions one at a time.
5. Approve each artifact as it's generated (`/approve-<thing>`).
6. After `INFRASTRUCTURE_APPROVED`, type `/import-docs` then
   `/parse-scope` then `/approve-tasks` then `/start-build`.
7. Watch the build progress table fill in. When `VERIFIED`, your code
   is at `../apps/` ready to deploy.

If at any point you're lost, type `/status` — it always tells you
what's valid right now.

---

## Where to ask for help

- `/status` — almost always answers "what should I do next".
- `AGENTS.md` — full role contract and command map.
- `README.md` — architecture and design rationale.
- `CHANGELOG.md` — what changed between releases.
