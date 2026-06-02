# Claude Code — agentic-workflow

> **Read this file completely before doing anything else.**
> Then follow the reading order below. No exceptions.

---

## What this repo does

`agentic-workflow` is the **full project engine**. It runs the complete lifecycle:
idea → 5 documents → generated code → verified → ready to deploy.

**Two phases. Two entry points for the docs phase.**

```
DOCS PHASE — pick one entry:

  /start-interview  →  13 questions, one at a time → 5 docs auto-generated
  /import-docs      →  drop PDF/Word/HTML/MD into DOCMENTS/ → 5 docs auto-generated

  Both end at DOCS_COMPLETE with the same 5 HTML documents.

BUILD PHASE
  /parse-scope    →  reads 5 docs → SESSION-STATE/TASKS.md
  /approve-tasks  →  locks task graph
  /start-build    →  parallel orchestrator + builders + QA → APPS/
  /verify-build   →  lint + types + tests → VERIFIED
```

---

## MANDATORY: Read these files at the start of EVERY session

Hard contract. Do not skip or reorder.

```
1. CLAUDE.md                              ← this file (already reading)
2. AGENTS.md                              ← full pipeline contract, both phases,
                                             quality gates, manual-edit protocol
3. SESSION-STATE/SESSION-STATE.md         ← current Stage + audit log
                                             Offer to resume if mid-pipeline
4. CONTEXT/ai-workflow-rules.md           ← how to build incrementally
5. CONTEXT/code-standards.md             ← code + document quality standards

IF Stage is DOCS_DRAFT or DOCS_COMPLETE — also read:
6. DOCMENTS/<slug>-project-brief.html
7. DOCMENTS/<slug>-scope-of-work.html
8. DOCMENTS/<slug>-system-architecture.html
9. DOCMENTS/<slug>-database-diagram.html
10. DOCMENTS/<slug>-infrastructure-diagram.html

IF Stage is TASKS_APPROVED or later — also read:
11. SESSION-STATE/TASKS.md

IF MEMEORIES/ files exist — read them for cross-session context:
12. MEMEORIES/ARCHITECTURE.md
13. MEMEORIES/PATTERNS.md
14. MEMEORIES/DECISIONS.md
15. MEMEORIES/STACK-GUIDANCE.md
16. MEMEORIES/PAGES.md

ALWAYS skim the 5 blank templates so you know their section structure:
- DOCMENTS/project-brief.html
- DOCMENTS/scope-of-work.html
- DOCMENTS/architecture.html
- DOCMENTS/database.html
- DOCMENTS/infrastructure.html

Architecture style (read when generating docs):
- CONTEXT/architecture-styles/monolith.md      ← default
- CONTEXT/architecture-styles/hybrid.md
- CONTEXT/architecture-styles/microservices.md
- CONTEXT/architecture-styles/serverless.md
- CONTEXT/architecture-styles/polyglot-microservices.md
```

**Never start an interview, generate a document, write code, or approve
anything without completing this reading order first.**

---

## Folder layout

```
agentic-workflow/
├── CLAUDE.md                       ← you are here (read first)
├── AGENTS.md                       ← full agent contract (read second)
├── README.md                       ← human-facing overview
│
├── DOCMENTS/                       ← 5 blank templates + filled outputs per project
│   ├── project-brief.html          ← blank template (read-only to Claude)
│   ├── scope-of-work.html          ← blank template (read-only to Claude)
│   ├── architecture.html           ← blank template (read-only to Claude)
│   ├── database.html               ← blank template (read-only to Claude)
│   ├── infrastructure.html         ← blank template (read-only to Claude)
│   ├── designs/                    ← UI screenshots / Figma exports (human-uploaded)
│   └── <slug>-*.html               ← filled outputs (written by skills)
│
├── CONTEXT/                        ← workflow rules + project context + style profiles
│   ├── ai-workflow-rules.md        ← how to build — read every session
│   ├── code-standards.md           ← quality standards — read every session
│   ├── architecture-styles/        ← all 5 architecture style profiles
│   │   ├── monolith.md             ← default (most projects)
│   │   ├── hybrid.md
│   │   ├── microservices.md
│   │   ├── serverless.md
│   │   └── polyglot-microservices.md
│   ├── project-overview.md         ← current project description (human-authored)
│   ├── progress-tracker.md         ← current progress (human-updated)
│   ├── architecture-context.md     ← architecture decisions for current project
│   ├── ui-ux-context.md            ← design context for current project
│   └── feature-specs/              ← per-feature spec files (01-xxx.md, 02-xxx.md …)
│
├── SESSION-STATE/                  ← per-project auto-state (BOTH phases)
│   ├── SESSION-STATE.md            ← Stage + audit log + artifact hashes
│   ├── TASKS.md                    ← generated task graph (build phase)
│   └── ARCHIVED/                   ← session snapshots on /reset
│
├── MEMEORIES/                      ← curated cross-session knowledge (QA-written)
│   ├── ARCHITECTURE.md
│   ├── PATTERNS.md
│   ├── DECISIONS.md
│   ├── STACK-GUIDANCE.md
│   ├── PAGES.md
│   └── contracts/                  ← API contracts (OpenAPI / gRPC / GraphQL)
│
├── APPS/                           ← generated source code (builders write here)
│
└── .claude/
    ├── skills/                     ← skill files (Claude Code executes these)
    └── commands/                   ← slash command definitions
```

**Template files are read-only.** Never edit the 5 blank `DOCMENTS/*.html` templates.
Always copy to `DOCMENTS/<slug>-*.html` and write there.

**Generated code lives in `APPS/`**, never inside agentic-workflow itself.

---

## Pipeline stages (8 total)

| Stage | Phase | Meaning | Next action |
|-------|-------|---------|------------|
| `INIT` | Docs | Fresh start | `/start-project` |
| `INTERVIEW` | Docs | In-progress interview | Offer resume or fresh start |
| `BRIEF_DRAFT` | Docs | Brief written | `/review-brief <N>` or `/approve-brief` |
| `BRIEF_APPROVED` | Docs | Brief locked, auto-build triggered | Wait or re-run `/approve-brief` |
| `DOCS_COMPLETE` | Docs→Build | All 5 docs approved | `/parse-scope` |
| `TASKS_GENERATED` | Build | TASKS.md generated | `/approve-tasks` |
| `TASKS_APPROVED` | Build | Task graph locked | `/start-build` |
| `BUILDING` | Build | Parallel build in progress | `/show-status` |
| `BUILD_COMPLETE` | Build | All tasks done | `/approve-build` |
| `BUILD_APPROVED` | Build | Build locked | `/verify-build` |
| `VERIFIED` | Build | Lint + types + tests pass | `/package-release` |
| `READY_TO_DEPLOY` | Done | Project complete | Ship it |

---

## Commands

```
ENTRY + STATUS
  /start-interview        ← guided: 13 questions → 5 docs auto-generated
  /import-docs            ← drop PDF/Word/HTML/MD into DOCMENTS/ → 5 docs auto-generated
  /status                 show current stage + next valid commands
  /reset                  archive session → INIT

DOCS PHASE — REVIEW  [Stage: DOCS_DRAFT — all 5 docs ready, open in browser]
  /review-brief <N>
  /review-scope-of-work <N>
  /review-architecture <N>
  /review-database <N>
  /review-infrastructure <N>
  /approve-docs           quality-gate all 5 docs → DOCS_COMPLETE

BUILD PHASE
  /parse-scope            SESSION-STATE/TASKS.md from 5 docs
  /approve-tasks          lock task graph → TASKS_APPROVED
  /reqops                 derive per-feature requirements
  /delta-scope            re-plan when scope changes
  /api-contract           generate OpenAPI / tRPC / GraphQL contracts
  /figma-ingest           fetch Figma design context
  /refresh-mcp            force re-fetch MCP cache
  /start-build            TASKS_APPROVED → BUILDING
  /resume-build           continue interrupted build
  /show-status            TASKS.md status counts
  /qa-only                run QA on in-review tasks only
  /approve-build          BUILD_COMPLETE → BUILD_APPROVED
  /verify-build           BUILD_APPROVED → VERIFIED
  /package-release        VERIFIED → READY_TO_DEPLOY

ADVANCED (regenerate a single doc from scratch)
  /build-scope-of-work
  /build-architecture
  /build-database
  /build-infrastructure
```

After every command, remind the user of the **next valid commands**.

---

## Architecture style system

The user picks an architecture style in Section 3 of the interview:
`monolith` | `hybrid` | `microservices` | `serverless` | `polyglot-microservices`

Every `build-*` skill (docs phase) AND every code-generation skill (build phase)
reads `CONTEXT/architecture-styles/<style>.md` before generating. The style file
controls: folder structure, tech stack defaults, DB approach, communication style,
Mermaid diagram patterns.

**Always read the style file before generating any document or code.**
Default to `monolith` if not set.

---

## Document generation rules (docs phase)

When auto-generating during `/approve-brief`:

1. **Scope of Work** — reads brief → `DOCMENTS/scope-of-work.html` template
2. **System Architecture** — reads SoW → `DOCMENTS/architecture.html` + `CONTEXT/architecture-styles/<style>.md`
3. **Database Diagram** — reads Architecture Section 8 → `DOCMENTS/database.html`
4. **Infrastructure Diagram** — reads Architecture Section 9 → `DOCMENTS/infrastructure.html`

Each step feeds the next. Never skip or reorder.

---

## Build phase rules

When running `/start-build`:
- Orchestrator reads `SESSION-STATE/TASKS.md` + all 5 approved docs
- Each builder reads its task spec + `CONTEXT/feature-specs/<N>-*.md` if present
- Builders write code to `APPS/<sub-app>/`
- QA validates each task before marking done
- Memory files in `MEMEORIES/` are updated by QA after tasks complete

---

## Manual edit detection (applies to every skill)

Before reading or writing any `<slug>-*.html` or `APPS/` artifact:

1. Compute SHA-256 of the file on disk
2. Compare to stored hash in `SESSION-STATE/SESSION-STATE.md`
3. If different → halt and ask: **Accept** (bump version + audit log) / **Show diff** / **Cancel**
4. Never silently overwrite a manually edited file

---

## Interaction style

Audience: **product managers** — not engineers.

- One question per turn during interviews. Never dump the whole brief.
- Restate each answer in one sentence before asking the next.
- Plain language. No engineering jargon unless the user opens that door.
- Never invent details. Mark unknowns as `TBD` in HTML.
- Always show a diff preview before saving any HTML edit.
- After every command, print the next valid commands for the current stage.

---

## What this repo does NOT do

- Does not modify project-foundations — it only consumes its output docs
- Does not commit or push code without explicit user instruction
- Does not auto-advance stages without user confirmation
