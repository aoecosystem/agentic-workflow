# Changelog

All notable changes to the agentic-workflow template are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
