# Project instructions for Claude Code

This file is read at session start by Claude Code when the
**agentic-workflow** repo is open. It bootstraps Claude with the
right context so the user can run the full project lifecycle —
docs phase + build phase — through a unified slash-command set.

> **Scope:** agentic-workflow is the **full project engine**. Unlike
> project-foundations (which only authors 5 HTML docs), this repo runs
> the entire lifecycle from initial idea → 5 documents → generated code
> → verified, ready to deploy.

---

## Session start (mandatory)

Before responding to any command, in this order:

1. Read `AGENTS.md` — full role contract, both pipelines, slash command map, quality gates.
2. Read `README.md` — what's in the repo.
3. Read `INSTRUCTIONS.md` — full step-by-step user guide.
4. Read `state/SESSION-STATE.md` — its `Stage:` field tells you exactly
   where the project is. If mid-pipeline, offer to resume from the last
   checkpoint instead of restarting.
5. If past `DOCS_COMPLETE`: read `state/SCOPE.md`.
6. If `Stage: BUILDING` or later: read `state/TASKS.md`.
7. Read `memory/ARCHITECTURE.md`, `PATTERNS.md`, `DECISIONS.md`,
   `STACK-GUIDANCE.md`, `PAGES.md`.
8. Skim the 5 empty templates in `deliverables/scope-of-work/`, `deliverables/architecture/`,
   `deliverables/` to know section structures.
9. If a filled `<slug>-*.html` already exists for the active stage, read
   it too.

---

## Architecture: superset of foundations

The repo runs as ONE pipeline that spans TWO phases sharing one state file:

**Docs phase** (single agent, same as project-foundations):
- `/start-project` walks the user through 13-section brief interview
- Pipeline: INIT → INTERVIEW → BRIEF/SOW/ARCHITECTURE/DATABASE/INFRASTRUCTURE → DOCS_COMPLETE
- Each phase has draft → approved transitions with quality gates

**Build phase** (multi-agent: orchestrator + builders + QA):
- `/import-docs` extracts SCOPE.md from the 5 approved HTMLs
- `/parse-scope` generates TASKS.md
- `/start-build` runs the parallel build loop
- Pipeline: DOCS_COMPLETE → SCOPE_PARSED → TASKS_GENERATED → BUILDING → BUILD_COMPLETE → VERIFIED → READY_TO_DEPLOY

Every stage transition requires an explicit user command. The agent
NEVER auto-advances. See `AGENTS.md` for the full state diagram and
quality gates.

---

## Architecture styles

Brief Section 3.2 captures the project's architecture style — one of
`monolith` | `hybrid` | `microservices` | `serverless`. Every
`build-*` skill (docs phase) AND every code-generation skill (build
phase) reads `deliverables/architecture/styles/<style>.md` to shape its
output: folder structure, tech stack defaults, database approach,
communication style, Mermaid diagram patterns. Default = `monolith`.

See `deliverables/architecture/styles/README.md` for the full guide.

---

## Manual edits are welcome (and detected)

Users may open any filled `<slug>-*.html` OR any code file under
`../apps/` and edit it directly. The workflow tracks a SHA-256 hash of
every artifact in `state/SESSION-STATE.md`. Before any skill reads or
writes an artifact, it computes the current hash and compares to the
stored one — if they differ, the agent halts and asks the user to
accept (bump version + audit log) or cancel.

See `AGENTS.md` → "Manual Edit Protocol" for the full contract.

---

## Triple-mirror rule for skills + rules

Whenever you edit a SKILL.md under `.claude/skills/<name>/`, you MUST
update the matching files at `.cursor/skills/<name>/SKILL.md` and
`.agent/skills/<name>/SKILL.md` in the same turn so all three IDE
trees stay byte-identical. **Verify inline by reading and comparing
each copy** (or via SHA-256 hash).

Same applies to `.cursor/rules/*.mdc` and `.agent/rules/*.mdc`.

This is a hard contract. Half-mirrored edits cause inconsistent
behavior across IDEs that is hard to debug. The rule is the verifier —
no external script.

---

## Available slash commands (28 skills, 29 commands)

Quick reference — see `AGENTS.md` for full table with stage transitions:

```
ENTRY + STATUS
  /start-project          (universal smart router — works in BOTH phases)
  /status                 (show current stage + next valid commands)
  /reset                  (archive current session, reset to INIT)

DOCS PHASE — BRIEF
  /review-brief <section>
  /approve-brief

DOCS PHASE — SCOPE OF WORK
  /build-scope-of-work
  /review-scope-of-work <phase>
  /approve-scope-of-work

DOCS PHASE — ARCHITECTURE
  /build-architecture
  /review-architecture
  /approve-architecture

DOCS PHASE — DATABASE
  /build-database
  /review-database
  /approve-database

DOCS PHASE — INFRASTRUCTURE
  /build-infrastructure
  /review-infrastructure
  /approve-infrastructure

BUILD PHASE
  /import-docs              (DOCS_COMPLETE → SCOPE_PARSED)
  /parse-scope              (generates TASKS.md from SCOPE.md)
  /delta-scope              (re-plan when SCOPE changes)
  /reqops                   (derive per-feature requirements)
  /api-contract             (generate API contracts)
  /figma-ingest             (fetch design context)
  /refresh-mcp              (force re-fetch MCP cache)
  /start-build              (run orchestrator + builders + QA loop)
  /resume-build             (continue scheduler)
  /show-status              (TASKS.md status counts)
  /qa-only                  (run QA on in-review tasks)
  /scope-interview          (fallback Q&A when no foundations docs)
```

After every command finishes, Claude must remind the user of the
**next valid commands** for the new stage (or run the `status` skill
internally).

---

## File and folder conventions

```
agentic-workflow/                          ← this repo
├── deliverables/scope-of-work/                         ← Brief + SoW templates AND filled outputs
├── deliverables/architecture/                   ← Architecture template + filled
│   └── styles/                            ← 4 architecture-style profile files
├── deliverables/                      ← Database + Infrastructure diagrams
├── deliverables/designs/                        ← UI screenshots / Figma exports (human-uploaded)
├── inputs/                                ← optional: import SoW from elsewhere
├── state/                                 ← per-project auto-state
│   ├── SESSION-STATE.md                   ← Stage + audit log + hashes (BOTH phases)
│   ├── SCOPE.md                           ← parsed from foundations docs
│   ├── TASKS.md                           ← generated task graph
│   └── archived/                          ← snapshots on /reset
├── memory/                                ← curated cross-session knowledge
│   ├── ARCHITECTURE.md / PATTERNS.md / DECISIONS.md / STACK-GUIDANCE.md / PAGES.md
│   ├── contracts/                         ← API contracts (OpenAPI / gRPC / GraphQL)
│   └── mcp-cache/                         ← cached design context
├── docs/                                  ← framework docs + prompts/
├── .claude/skills/, .claude/commands/     ← Claude Code skills + slash commands
├── .cursor/skills/, .cursor/rules/        ← Cursor mirror
└── .agent/skills/, .agent/rules/          ← Antigravity mirror
```

Builders write code to `../apps/<sub-app>/` (sibling level).

Rules:

- **Empty templates are read-only to Claude.** Never edit the empty
  scaffolds (`*-template.html`, `system-architecture.html`,
  `database-diagram.html`, `infrastructure-diagram.html`). They must
  remain empty.
- **Filled outputs live alongside their templates**, prefixed with the
  slug. Slug = kebab-case project name from the interview.
- **UI screenshots** go in `deliverables/designs/<page-id>.png/jpg/html`.
  Page IDs come from the SoW Page Inventory.
- **State** lives in `state/SESSION-STATE.md` and is auto-managed by
  skills — humans rarely edit it.
- **Memory** lives in `memory/*.md` and is QA-curated.
- **Generated code** lives in `../apps/`, never inside agentic-workflow.
- **Never commit secrets or `.env` values.**

---

## Interaction style

Audience: **product managers** (may know programming but use this for
documentation + automation, not coding). Tone matters.

- One question per turn during interviews. Never paste the whole brief.
- Restate each answer briefly before moving on.
- Plain language by default. Engineering jargon only when the user
  opens that door first.
- Never invent details. Mark unknowns as `TBD`.
- Markdown answers fine in chat, but the deliverable is HTML (docs phase)
  or code (build phase).
- Always preview a diff inline before saving any HTML or code edit.

---

## What this repo DOES (vs project-foundations)

| Capability | project-foundations | agentic-workflow |
|---|---|---|
| Docs interview | ✓ | ✓ (same skills, copied) |
| 5 HTML deliverables | ✓ | ✓ |
| Architecture styles | ✓ | ✓ |
| `/import-docs` to extract SCOPE.md | — | ✓ |
| `/parse-scope` to generate TASKS.md | — | ✓ |
| Multi-agent build loop (orchestrator + builders + QA) | — | ✓ |
| Code generation in `apps/` | — | ✓ |
| API contracts | — | ✓ |
| Figma / MCP cache | — | ✓ |
| Build verification (lint + types + tests) | — | ✓ |

agentic-workflow is the **full pipeline**. project-foundations stays
as a standalone repo for users who only want docs.

---

## Project layout reminder

When this repo is part of a multi-folder project setup:

```
<project-name>/
├── project-foundations/   ← optional standalone docs-only repo
├── agentic-workflow/      ← this repo (full engine)
└── apps/                  ← generated source code (sibling level)
```
