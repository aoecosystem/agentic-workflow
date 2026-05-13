# Agents

This file defines how AI agents behave inside the **agentic-workflow**
repo. Read at the start of every session.

It is the agent contract. Claude Code reads it via `CLAUDE.md` at
session start.

> **Scope:** agentic-workflow is the **full project engine**. It runs the
> complete lifecycle from initial idea → 5 documents → generated code →
> verified, ready to deploy. It is a **superset** of project-foundations
> (which only does the docs phase).

---

## Architecture: superset pipeline (docs phase + build phase)

The pipeline runs through TWO phases sharing one state file:

```
═══════ DOCS PHASE (foundations work) ═══════

INIT
  └─ /start-project (smart router) → INTERVIEW → BRIEF_DRAFT ⇄ BRIEF_APPROVED
                                                  → SOW_DRAFT ⇄ SOW_APPROVED
                                                  → ARCHITECTURE_DRAFT ⇄ ARCHITECTURE_APPROVED
                                                  → DATABASE_DRAFT ⇄ DATABASE_APPROVED
                                                  → INFRASTRUCTURE_DRAFT ⇄ INFRASTRUCTURE_APPROVED
                                                      ↓
                                                  DOCS_COMPLETE

═══════ BUILD PHASE (engine work) ═══════

DOCS_COMPLETE
  └─ /import-docs    → SCOPE_PARSED         (populates state/SCOPE.md from 5 HTMLs)
  └─ /parse-scope    → TASKS_GENERATED ⇄ TASKS_APPROVED
  └─ /start-build    → BUILDING            (parallel orchestrator + builders + QA)
                       ↓ (all tasks done)
                      BUILD_COMPLETE ⇄ BUILD_APPROVED
  └─ /verify-build   → VERIFIED            (lint + types + tests pass)
                       ↓
                      READY_TO_DEPLOY      (project complete)
```

Every transition requires an **explicit user command**. The agent NEVER
auto-advances. `⇄` = re-openable via matching `/review-*` command.

**One state file** (`state/SESSION-STATE.md`) tracks both phases. Hash
tracking + audit log spans the whole journey.

---

## Architecture style

Brief Section 3.2 captures the project's architecture style:
`monolith` | `hybrid` | `microservices` | `serverless`. Every
`build-*` skill (docs phase) AND every code-generation skill (build
phase) reads `deliverables/architecture/styles/<style>.md` to shape its
output: folder structure, tech stack defaults, database approach,
communication style, Mermaid diagram patterns. Default = `monolith`.

To change style mid-project: run `/review-brief 3` (in docs phase) or
update `state/SCOPE.md` Architecture section (in build phase). Then
re-build downstream docs/tasks to pick up the change.

---

## Slash commands (33 skills, 33 commands)

### Docs phase commands (foundations pipeline)

| Command | Stage transition |
|---------|------------------|
| `/start-project` | Smart router — INIT → INTERVIEW → BRIEF_DRAFT, OR routes by current Stage |
| `/status` | (read-only — no transition) |
| `/reset` | `<ANY>` → INIT (archives current session) |
| `/review-brief <N>` | BRIEF_DRAFT/APPROVED → BRIEF_DRAFT |
| `/approve-brief` | BRIEF_DRAFT → BRIEF_APPROVED |
| `/build-scope-of-work` | BRIEF_APPROVED → SOW_DRAFT |
| `/review-scope-of-work <N>` | SOW_DRAFT/APPROVED → SOW_DRAFT |
| `/approve-scope-of-work` | SOW_DRAFT → SOW_APPROVED |
| `/build-architecture` | SOW_APPROVED → ARCHITECTURE_DRAFT |
| `/review-architecture` | ARCHITECTURE_DRAFT/APPROVED → ARCHITECTURE_DRAFT |
| `/approve-architecture` | ARCHITECTURE_DRAFT → ARCHITECTURE_APPROVED |
| `/build-database` | ARCHITECTURE_APPROVED → DATABASE_DRAFT |
| `/review-database` | DATABASE_DRAFT/APPROVED → DATABASE_DRAFT |
| `/approve-database` | DATABASE_DRAFT → DATABASE_APPROVED |
| `/build-infrastructure` | DATABASE_APPROVED → INFRASTRUCTURE_DRAFT |
| `/review-infrastructure` | INFRASTRUCTURE_DRAFT/APPROVED → INFRASTRUCTURE_DRAFT |
| `/approve-infrastructure` | INFRASTRUCTURE_DRAFT → INFRASTRUCTURE_APPROVED → DOCS_COMPLETE |

### Build phase commands (engine pipeline)

| Command | Skill | Stage transition |
|---------|-------|------------------|
| `/import-docs` | import-docs | DOCS_COMPLETE → SCOPE_PARSED |
| `/parse-scope` | parse-scope | SCOPE_PARSED → TASKS_GENERATED |
| `/delta-scope` | delta-scope | (re-plan when SCOPE changes after tasks exist) |
| `/reqops` | reqops | (derive per-feature requirements) |
| `/api-contract` | api-contract | (generate OpenAPI / tRPC / GraphQL) |
| `/figma-ingest` | figma-plugin-ingest | (fetch design context) |
| `/refresh-mcp` | fetch-mcp / figma-plugin-ingest | (force re-fetch ignoring TTL) |
| `/start-build` | orchestrate | TASKS_APPROVED → BUILDING |
| `/resume-build` | orchestrate | (resume scheduler from current state) |
| `/show-status` | (inline) | Summarize TASKS.md status counts |
| `/qa-only` | qa | (run QA on `in-review` tasks only) |
| `/scope-interview` | scope-interview | (fallback Q&A when no foundations docs) |

After every command, the agent reminds the user of the next valid
commands (or runs the `status` skill internally).

---

## Manual Edit Protocol (HARD CONTRACT)

Users can — and are expected to — open any filled artifact (HTML or
code) and edit it directly. Manual edits are a **first-class workflow
event**, not an error.

### Hash tracking

Every artifact the agent writes records a SHA-256 hash in
`state/SESSION-STATE.md` Artifacts list:

```
- [x] deliverables/brief/<slug>-brief.html  v1.1  sha256:a1b2c3...  approved 2026-05-02
- [x] state/SCOPE.md  v1.0  sha256:d4e5f6...  parsed 2026-05-02
- [x] ../apps/web/src/screens/auth-login.tsx  v1.0  sha256:g7h8i9...  in-review 2026-05-02
```

### Detection step (FIRST step of every artifact-touching skill)

1. Compute SHA-256 of the file currently on disk.
2. Read the stored hash from `state/SESSION-STATE.md`.
3. Branch:
   - **Stored empty + file missing** → first save. Proceed; record hash after writing.
   - **Stored empty + file exists** → user-created. Treat as drift; ask accept/cancel.
   - **Stored hash + file missing** → user deleted. Halt and ask: restore / reset stage / cancel.
   - **Hashes match** → proceed.
   - **Hashes differ** → manual edit. Ask accept (bump version + audit) / show diff / cancel.

### Read-only skills (status, show-status)

Detect drift but only **report** — never bump version, never write,
never append audit log.

### Direct edits to `state/SESSION-STATE.md`

Meta-state, not an artifact. Hash protocol does NOT cover it. Skills
validate on read: `Stage:` must be in valid enum; slug must be
kebab-case; stored hashes must parse as `sha256:<hex>`. If invalid,
refuse with a clear error. Recommended manual reset: delete
`state/SESSION-STATE.md` and run `/start-project` (or use `/reset`).

### Placeholder vs TBD convention

Two forms can appear inside `<span class="ph">` or text fields:

- **Unfilled placeholder** (FAILS approve gates): `{{COLUMN_NAME}}`,
  `{{TODO}}`, `{{FILL_THIS}}`, `{{PROJECT_NAME}}`. Agent expected to replace.
- **Explicit TBD marker** (PASSES approve gates): text starting with
  `TBD` or `{{TBD ...}}`. User has acknowledged value not decided yet.

`/approve-*` skills check the prefix. Some critical fields require
concrete values, not TBDs (e.g. infrastructure providers).

---

## Reading order at session start

1. `AGENTS.md` (this file) — full agent contract.
2. `README.md` — what's in the repo.
3. `INSTRUCTIONS.md` — step-by-step user guide.
4. `state/SESSION-STATE.md` — read first to know current Stage.
5. `state/SCOPE.md` — what's being built (only if past DOCS_COMPLETE).
6. `state/TASKS.md` — task list and status (only during build phase).
7. `memory/ARCHITECTURE.md`, `PATTERNS.md`, `DECISIONS.md`,
   `STACK-GUIDANCE.md`, `PAGES.md` — curated cross-session knowledge.
8. `deliverables/architecture/styles/<style>.md` — chosen architecture style rules.
9. Any filled `<slug>-*.html` if mid-docs-phase.

Skip files that don't exist yet.

---

## Sub-agent roles (build phase only)

Docs phase = single agent (same as project-foundations).
Build phase = multi-agent.

| Role | Count | Writes code? | Marks done? | Marks in-review? |
|------|-------|--------------|-------------|------------------|
| Orchestrator | 1 | No | No | No |
| Builder | Dynamic (1 per independent ready chain) | Yes | No | Yes |
| QA | 1 shared | No (fix notes only) | Yes | No |

### Valid task status transitions

```
pending → in-progress     (Builder picks up task)
in-progress → in-review   (Builder finishes, verification passes)
in-progress → blocked     (Builder hits blocker)
in-review → done          (QA approves)
in-review → needs-fix     (QA rejects)
in-review → blocked       (attempt budget exhausted)
needs-fix → in-progress   (Builder picks up fix)
blocked → pending         (blocker resolved)
blocked → in-progress     (Builder resumes)
pending → obsolete        (only via delta-scope)
```

### File ownership

Each Builder owns the files in its assigned tasks. No other Builder
may edit those files while the task is `in-progress` or `needs-fix`.
Shared scaffolding (`types/`, `config/`, `memory/`) is created by
the first Builder that needs it, read-only for others until that
task is `done`.

### Concurrency (single-writer principle)

For each shared file, exactly one agent type writes a given section.

| File / Section | Writer |
|----------------|--------|
| `state/TASKS.md` task block body | Builder owning task (in-progress / needs-fix) |
| `state/TASKS.md` `Status:` field | Builder (to in-progress/in-review/blocked), QA (to done/needs-fix) |
| `state/TASKS.md` `QA notes:` | Builder handoff + QA rejection (append-only within task) |
| `memory/ARCHITECTURE.md`, `PATTERNS.md`, `DECISIONS.md` | QA after `done` |
| `memory/STACK-GUIDANCE.md` | `import-docs` skill only |
| `memory/mcp-cache/*` | `fetch-mcp` / `figma-plugin-ingest` only |
| `state/SESSION-STATE.md` | Read-modify-write by every skill (each skill re-reads before writing) |

---

## Verification gates

### Docs phase `/approve-*` quality gates

Each `/approve-*` skill runs blocking checks before transitioning. See
project-foundations conventions:
- All sections present (real value or explicit `TBD`)
- No raw unfilled `{{...}}` placeholders
- Mermaid diagrams compile (where applicable)
- Service codes match across phases
- Cover-sub replaced with real project name

### Build phase task gates (Builder before in-review, QA during review)

All four must pass:

1. **Lint** — zero errors; warnings only if pre-existing and unrelated.
2. **Typecheck** — zero type errors. `tsc --noEmit` or equivalent.
3. **Tests** — happy path + at least one error/edge case per unit.
4. **Acceptance criteria** — every `[ ]` item checked `[x]`.

Plus security gate (secrets scan, dependency audit, auth boundary,
input validation, output hygiene, CSP/CORS/cookies) and observability
gate (structured logging, error reporting, metrics, tracing).

---

## File-write rules

| Path | Writable by agent? |
|------|-------------------|
| Empty templates (`*-template.html`, `system-architecture.html`, etc.) | NO — read-only scaffolds |
| `scope-of-work/<slug>-*.html` | YES — docs phase skills |
| `deliverables/architecture/<slug>-*.html` | YES — docs phase skills |
| `deliverables/<slug>-*.html` | YES — docs phase skills |
| `state/SESSION-STATE.md` | YES — every skill (read-modify-write) |
| `state/SCOPE.md` | YES — `import-docs` skill only |
| `state/TASKS.md` | YES — `parse-scope` (sole writer) + status updates by Builders/QA |
| `state/archived/*` | YES — write-once snapshots when /reset runs |
| `memory/ARCHITECTURE.md`, `PATTERNS.md`, `DECISIONS.md`, `PAGES.md` | YES — QA after task `done` |
| `memory/STACK-GUIDANCE.md` | YES — `import-docs` only |
| `memory/contracts/*` | YES — `api-contract` skill only |
| `memory/mcp-cache/*` | YES — `fetch-mcp` / `figma-plugin-ingest` only |
| `../apps/<sub-app>/` | YES — Builders write here |
| `deliverables/architecture/styles/*.md` | NO — snapshot from foundations, read-only |
| `deliverables/designs/<page-id>.png/jpg/html` | NO — humans drop UI screenshots |
| `INSTRUCTIONS.md`, `README.md`, `CLAUDE.md`, `AGENTS.md` | NO — repo documentation |
| `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE` | NO — repo governance |

---

## Project layout

This `agentic-workflow/` repo is the build engine, not the build target.
Every project follows a three-sibling layout:

```
<project-name>/
├── project-foundations/   (optional — standalone docs-only repo)
├── agentic-workflow/      (this repo — engine, rules, skills, state, memory)
└── apps/                  (ALL generated code lives here)
    └── <sub-app>/         (per-deploy unit, structure depends on architecture style)
```

**Builders write code only inside `../apps/`** (relative to this repo
root). Never create `src/`, `web/`, `api/`, `package.json`, or any
project source tree at the root of `agentic-workflow/` itself.

`memory/ARCHITECTURE.md` paths are interpreted relative to `apps/`.
When the architecture map says `src/api/`, the actual filesystem path
is `apps/<sub-app>/src/api/`.

All verification gates (lint, typecheck, tests) execute against
`../apps/`, not against `agentic-workflow/`.

---

## Slug convention

Kebab-case identifier for the project. Examples: `bron-go`, `acme-crm`,
`medbook-uz`. Stable for the project's lifetime. Used as prefix for all
filled artifacts:

```
deliverables/brief/<slug>-brief.html
deliverables/scope-of-work/<slug>-sow.html
deliverables/architecture/<slug>-architecture.html
deliverables/database/<slug>-database.html
deliverables/infrastructure/<slug>-infrastructure.html
state/SCOPE.md (no slug — one project per repo)
state/TASKS.md (no slug)
```

If user provides a name with spaces or capitals, agent auto-converts
to kebab-case and confirms before saving.

---

## Reversibility

Approvals are reversible. Running `/review-*` on an `*_APPROVED` stage
moves it back to `*_DRAFT`. Downstream stages stay valid until the user
re-runs the next `/build-*` (or `/parse-scope` / `/start-build` for the
build phase) to pick up the change. Every re-open is recorded in the
audit log.

---

## Interaction style

- One question per turn during interviews. Never paste the whole interview.
- Restate each answer briefly before moving on (signals listening).
- Plain language. Audience: project managers and product owners (may
  read code but use this for documentation + automation).
- Never invent details. Mark unknowns as `TBD`.
- Always preview a diff inline before saving any HTML or code edit.

---

## Quality philosophy

| Lever | How it works here |
|---|---|
| **Stage gates** | Every skill refuses if `state/SESSION-STATE.md` Stage doesn't match expected. |
| **Quality gates** | Every `/approve-*` runs blocking checks. |
| **Manual edit detection** | SHA-256 hash drift caught before any operation. |
| **Reversibility** | Re-open any approved stage with `/review-*`. |
| **Audit log** | Every state transition appended (append-only). |
| **Single source of truth** | `state/SESSION-STATE.md` for state; `memory/*` for curated knowledge. |
| **No auto-advance** | Every transition needs an explicit user command. |
| **Triple-mirror inline verification** | Agent verifies byte-equality on every skill edit. |
