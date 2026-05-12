# Agentic Workflow

The **full project engine**. One repo that takes a project from initial
idea → 5 polished documents → generated, verified code → ready to deploy.

```
Step 1  Interview          →  5 polished HTML docs (Brief, SoW,
                              Architecture, Database, Infrastructure)
Step 2  Import + Parse     →  state/SCOPE.md + state/TASKS.md
Step 3  Build              →  generated code in ../apps/
Step 4  Verify             →  lint + types + tests pass
                            ↓
                            READY_TO_DEPLOY
```

A single agent steps through the docs phase. Multi-agent (orchestrator
+ builders + QA) handles the build phase. **One state file** spans both
phases. Every transition requires explicit `/approve-*` confirmation.

---

## Two related repos — pick the one that fits

| Repo | Use when |
|---|---|
| **`project-foundations`** | You only want the 5 docs (no code generation). Lighter, standalone. |
| **`agentic-workflow`** (this) | You want docs + code generation, full pipeline. **Superset** of foundations. |

Both share the same docs pipeline. agentic-workflow adds the build engine on top.

---

## Quick start

```bash
git clone <repo-url> my-project
cd my-project/agentic-workflow
```

Open the folder in **Claude Code**, **Cursor**, or **Google Antigravity**.
The agent reads `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` automatically.

Run:

```
/start-project
```

`/start-project` is a **smart router**. It reads `state/SESSION-STATE.md`
and routes you to the right next step. From a fresh INIT, it walks you
through the 13-section brief interview.

Run `/status` at any time to see where you are and what's valid next.

---

## The full pipeline

```
INIT
 │
 │  /start-project (smart router — works in both phases)
 ▼
INTERVIEW  ── 13 sections, one question at a time
 ▼
BRIEF_DRAFT  ── /review-brief <N> (loop) ── /approve-brief
 ▼
BRIEF_APPROVED ── /build-scope-of-work
 ▼
SOW_DRAFT  ── /review-scope-of-work <N> (loop) ── /approve-scope-of-work
 ▼
SOW_APPROVED ── /build-architecture
 ▼
ARCHITECTURE_DRAFT  ── /review-architecture (loop) ── /approve-architecture
 ▼
ARCHITECTURE_APPROVED ── /build-database
 ▼
DATABASE_DRAFT  ── /review-database (loop) ── /approve-database
 ▼
DATABASE_APPROVED ── /build-infrastructure
 ▼
INFRASTRUCTURE_DRAFT  ── /review-infrastructure (loop) ── /approve-infrastructure
 ▼
─── DOCS_COMPLETE ───  ← all 5 HTML deliverables approved
 │
 │  (continue to build phase, OR stop here if docs-only)
 │
 │  /import-docs
 ▼
SCOPE_PARSED ── /parse-scope
 ▼
TASKS_GENERATED ── /approve-tasks (recommended audit) ── /start-build
 ▼
BUILDING ── (orchestrator + builders + QA loop, parallel)
 ▼
BUILD_COMPLETE  ── /verify-build
 ▼
VERIFIED  ── (lint + types + tests pass)
 ▼
READY_TO_DEPLOY  ← project complete
```

---

## Step-by-step guide

### Step 1 — Interview (Stage: INIT → INTERVIEW → BRIEF_DRAFT)

Run `/start-project`. The agent walks through 13 sections, one question
per turn. Answer in plain language. Restate-and-confirm each answer.

The 13 sections:

1. Project Basics (name, type, market, languages, currency)
2. Problem and Solution
3. **Platform & Architecture** (3.1 platforms, **3.2 architecture style**)
4. Roles
5. Business Features (10–20)
6. Business Process (1–3 critical flows)
7. Business Model
8. Integrations
9. Special Requirements
10. Out of Scope
11. Design & Branding
12. Timeline & Team
13. Instructions for AI Agent (auto-filled)

After all 13, type `save` to write `deliverables/brief/<slug>-brief.html`.

### Step 2 — Architecture style (the most important question)

Section 3.2 asks you to pick one of four profiles:

| Style | When to pick | What you get |
|---|---|---|
| **monolith** (default) | Small/medium project, single team, ship fast | One app, one deploy, one DB. Internal modules. |
| **hybrid** (recommended for ~70%) | "We want microservices someday" | Modular monolith with extraction-ready boundaries. |
| **microservices** | Large team, real distributed-system needs | DB per service, **Kafka required**, gateway in front. |
| **serverless** | Spiky traffic, JAMstack, edge | Functions on Lambda/Workers/Vercel. |

Each style is a real file in `deliverables/architecture/styles/<style>.md`.
Open it to see the exact folder structure, tech stack, DB approach, and
diagram patterns you'll get.

**Default = `monolith`.** Pick monolith when in doubt. Change later via
`/review-brief 3` and re-build downstream documents.

### Step 3 — Approve the brief

```
/review-brief 6   ← edit one section
/approve-brief    ← run quality gate, lock the brief
```

The quality gate checks: all 13 sections present, no raw `{{...}}`
placeholders, slug + cover replaced. If it fails, fix what it lists,
then re-approve.

### Step 4 — Generate the rest of the docs

```
/build-scope-of-work     /approve-scope-of-work
/build-architecture      /approve-architecture
/build-database          /approve-database
/build-infrastructure    /approve-infrastructure   ← FINAL → DOCS_COMPLETE
```

Each `/build-*` reads the previous approved doc and generates the next.
Each `/approve-*` runs a blocking quality gate. After
`/approve-infrastructure`, you have all 5 HTML deliverables. Stop here
if docs were your only goal.

### Step 5 — Import + parse (Docs phase → Build phase)

```
/import-docs    ← parses 5 HTMLs into state/SCOPE.md
/parse-scope    ← generates state/TASKS.md from SCOPE.md
```

Optional review:

```
/approve-tasks  ← runs the senior-style task-graph audit (acceptance criteria,
                  dependency order, file ownership, no orphan / circular deps)
                  and transitions Stage → TASKS_APPROVED on success
```

### Step 6 — Build

```
/start-build
```

Orchestrator dispatches tasks to builders in parallel (respecting
dependencies). Each builder writes code to `../apps/<sub-app>/`,
following the chosen architecture style's folder pattern. QA reviews
each finished task with full lint + types + tests + acceptance criteria
gate.

Watch progress:

```
/show-status   ← TASKS.md status counts
/status        ← stage + progress + blocked tasks + pages without designs
```

### Step 7 — Verify and ship

When all tasks are `done`:

```
/verify-build   ← project-wide lint + types + tests + security + observability
                  → VERIFIED → READY_TO_DEPLOY
```

Code lives in `../apps/`, ready to deploy.

---

## Manual edits — fix things directly in your editor

You know HTML or code? Edit any artifact directly. The workflow tracks
SHA-256 hashes in `state/SESSION-STATE.md`. Next time you run any skill,
the agent detects drift and asks:

```
I notice you manually edited apps/web/src/screens/auth-login.tsx since
the last save.
  Stored hash:  sha256:a1b2c3...
  Current hash: sha256:x9y8z7...

How would you like to handle this?
  1. Accept your edits (bump version, audit-log)
  2. Show me the diff first
  3. Cancel
```

Type `1` and the agent acknowledges your changes officially. Same
protocol for HTML deliverables AND for code in `../apps/`.

---

## Re-opening, resuming, resetting

| Action | Command |
|---|---|
| Edit an approved stage | `/review-<stage>` (re-opens to `*_DRAFT`) |
| Resume after closing IDE mid-flow | Just run `/start-project` — smart router resumes from current Stage |
| Start fresh | `/reset` — soft (archive state) / hard (also archive HTMLs + code) / cancel |
| Check progress at any time | `/status` |

`/reset` always preserves audit trail in `state/archived/`.

---

## Architecture styles — folder structure differences

| Style | Folder pattern in apps/ |
|---|---|
| **monolith** | `apps/<slug>/src/services/<name>/` (one package, one Dockerfile) |
| **hybrid** | `apps/<slug>/services/<name>/` with `ports.ts` interfaces (one package, extraction-ready) |
| **microservices** | `services/<name>/{src,prisma,Dockerfile,kubernetes}/` (independent deploys) |
| **serverless** | `apps/<slug>/functions/<feature>-<action>/` (per-function deploy) |

See each `deliverables/architecture/styles/<style>.md` file for full details.

---

## Folder layout

```
agentic-workflow/                      ← this repo
├── deliverables/scope-of-work/                     ← Brief + SoW (templates + filled)
│   ├── project-brief-template.html         (read-only)
│   ├── scope-of-work-template.html         (read-only)
│   ├── <slug>-project-brief.html           (filled)
│   └── <slug>-scope-of-work.html           (filled)
├── deliverables/architecture/               ← Architecture (template + filled + styles)
│   ├── system-architecture.html            (read-only)
│   ├── <slug>-system-architecture.html     (filled)
│   └── styles/                             ← architecture style files
│       ├── monolith.md hybrid.md microservices.md serverless.md
│       └── _schema.md README.md
├── deliverables/                  ← Database + Infrastructure
│   ├── database-diagram.html               (read-only)
│   ├── infrastructure-diagram.html         (read-only)
│   ├── <slug>-database-diagram.html        (filled)
│   └── <slug>-infrastructure-diagram.html  (filled)
├── deliverables/designs/                    ← UI screenshots (human-uploaded)
│   └── <page-id>.png/jpg/html
├── inputs/                            ← optional: import SoW from elsewhere
├── state/                             ← per-project auto-state
│   ├── SESSION-STATE.md                    (Stage + audit log + hashes)
│   ├── SCOPE.md                            (parsed from docs)
│   ├── TASKS.md                            (generated)
│   └── archived/                           (snapshots on /reset)
├── memory/                            ← QA-curated cross-session knowledge
│   ├── ARCHITECTURE.md PATTERNS.md DECISIONS.md
│   ├── STACK-GUIDANCE.md PAGES.md
│   ├── contracts/                          (API contracts)
│   └── mcp-cache/                          (cached design context)
├── docs/                              ← framework docs + prompts/
├── AGENTS.md / CLAUDE.md / GEMINI.md  ← agent bootstrap
├── README.md                          ← this file (overview + step-by-step)
├── .claude/skills/, .claude/commands/ ← Claude Code
├── .cursor/skills/, .cursor/rules/    ← Cursor mirror
└── .agent/skills/, .agent/rules/      ← Antigravity mirror
```

Generated code lives at the **sibling level** in `../apps/`, never
inside agentic-workflow:

```
<project-name>/
├── project-foundations/   ← optional standalone docs-only repo
├── agentic-workflow/      ← this repo (full engine)
└── apps/                  ← generated code (sibling)
```

---

## Slash command reference (33 skills, 33 commands)

```
ENTRY + STATUS
  /start-project          (universal smart router — both phases)
  /status                 (show current stage + next valid commands)
  /reset                  (archive current session, reset to INIT)

DOCS PHASE — BRIEF
  /review-brief <section>           (edit one section, bumps version)
  /approve-brief                    (run quality gate, lock)

DOCS PHASE — SCOPE OF WORK
  /build-scope-of-work              (generate from approved brief)
  /review-scope-of-work <phase>     (edit one phase)
  /approve-scope-of-work            (run quality gate, lock)

DOCS PHASE — ARCHITECTURE
  /build-architecture               (generate from approved SoW)
  /review-architecture              (edit one section)
  /approve-architecture             (run quality gate, lock)

DOCS PHASE — DATABASE
  /build-database                   (generate from approved architecture)
  /review-database                  (edit one section)
  /approve-database                 (run quality gate, lock)

DOCS PHASE — INFRASTRUCTURE
  /build-infrastructure             (generate from approved database)
  /review-infrastructure            (edit one section)
  /approve-infrastructure           (FINAL of docs phase → DOCS_COMPLETE)

BUILD PHASE
  /import-docs                      (DOCS_COMPLETE → SCOPE_PARSED)
  /parse-scope                      (generates state/TASKS.md)
  /delta-scope                      (re-plan when SCOPE changes)
  /reqops                           (per-feature requirements)
  /api-contract                     (OpenAPI / gRPC / GraphQL)
  /figma-ingest                     (fetch design context)
  /refresh-mcp                      (force re-fetch MCP cache)
  /start-build                      (run orchestrator + builders + QA)
  /resume-build                     (continue scheduler)
  /show-status                      (TASKS.md status counts)
  /qa-only                          (run QA on in-review tasks)
  /scope-interview                  (fallback Q&A when no foundations docs)
```

---

## Tips for high-quality output

- **Be specific.** Vague briefs → vague SoWs → vague tasks → vague code.
- **Mark unknowns as TBD.** Agent doesn't invent.
- **Approve sequentially, fix early.** Catching issues at the brief
  stage is far cheaper than catching them after `/start-build` runs.
- **Use `/status` often.** When in doubt about the next command, ask.
- **Trust the gates.** If `/approve-architecture` says "Mermaid syntax
  error on line 47", fix it — the diagram won't render otherwise.

---

## Key properties

- **One agent + smart router** for the docs phase. **Multi-agent** for the build phase.
- **Stage-gated.** Every skill refuses if pipeline isn't in the expected stage.
- **Reversible.** Re-open any approved stage with `/review-*`. Audit-logged.
- **Resumable.** Every meaningful turn writes progress to `state/SESSION-STATE.md`.
- **Triple-mirrored.** All 33 skills + 33 commands byte-identical across `.claude/`, `.cursor/`, `.agent/`. Verified inline by the agent.
- **Manual-edit safe.** Edit any HTML or code file — agent detects via SHA-256 hash and asks before overwriting.

---

## What this engine does NOT do

- It does not deploy your code (you do that after `READY_TO_DEPLOY`).
- It does not call MCP servers without explicit `/refresh-mcp` or `/figma-ingest`.
- It does not auto-edit your code without going through stage transitions.
- It does not invent project details — only fills `TBD` where you said `TBD`.

When the project reaches `READY_TO_DEPLOY`, the `../apps/` folder
contains your complete project. Test it, ship it, iterate.

---

## Why this exists

Most projects fail in the gap between "we agreed on the plan" and
"we have working code." This engine closes that gap. It captures the
plan in 5 documents, then generates, verifies, and tests the code that
implements those documents — with explicit human gates at every
transition so nothing slips through silently.

For docs-only use cases, use `project-foundations` (lighter, standalone).
For end-to-end project building, this is the engine.
