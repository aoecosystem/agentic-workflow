# Project instructions for Antigravity

This file is read by Google Antigravity when the **agentic-workflow**
repo is open. It is a thin bootstrap — the full agent contract lives in
`AGENTS.md`, which Antigravity also reads natively.

---

## Read first

1. `AGENTS.md` — full role contract, both pipelines, slash command map, quality gates.
2. `README.md` and `INSTRUCTIONS.md`.
3. `state/SESSION-STATE.md` — read first to determine current Stage.
4. `state/SCOPE.md` (if past DOCS_COMPLETE) and `state/TASKS.md` (if BUILDING).
5. `memory/ARCHITECTURE.md`, `PATTERNS.md`, `DECISIONS.md`, `STACK-GUIDANCE.md`, `PAGES.md`.
6. The 5 empty templates in `deliverables/scope-of-work/`, `deliverables/architecture/`, `deliverables/`.

---

## Architecture: superset (docs + build)

agentic-workflow runs the full project lifecycle in ONE repo:

- **Docs phase** (single agent): `/start-project` walks user through 13-section interview, generates 5 HTMLs (Brief, SoW, Architecture, Database, Infrastructure). Same as project-foundations.
- **Build phase** (multi-agent): `/import-docs` parses docs into SCOPE.md, `/parse-scope` generates TASKS.md, `/start-build` runs orchestrator + builders + QA loop. Generates code in `../apps/`.

Both phases share one state file (`state/SESSION-STATE.md`). Every
transition requires an explicit user command. The agent NEVER
auto-advances. See `AGENTS.md` for the full state diagram.

---

## Architecture styles

Brief Section 3.2 captures the architecture style (monolith / hybrid /
microservices / serverless). Every `build-*` skill (docs phase) and
every code-generation skill (build phase) reads
`deliverables/architecture/styles/<style>.md` and applies its rules. See
`deliverables/architecture/styles/README.md` for the full guide.

Manual edits to artifact files (HTML or code) are welcomed and detected
via SHA-256 hash tracking in `state/SESSION-STATE.md`. Before any
artifact operation, every skill compares stored vs current hash and
halts to ask the user if drift is detected. See `AGENTS.md` → "Manual
Edit Protocol" for details.

---

## Skill discovery + triple-mirror rule

Antigravity auto-discovers skills under `.agent/skills/<name>/SKILL.md`
and rules under `.agent/rules/*.mdc`. The same skill set lives under
`.claude/skills/` and `.cursor/skills/`.

When you edit any skill or rule, you MUST update all matching files
across the three IDE trees in the same turn. Verify inline by reading
each copy and comparing contents (or via SHA-256 hash). The rule is the
verifier — no external script.

---

## Slash commands

Quick reference — see `AGENTS.md` for full stage-transition table:

```
ENTRY + STATUS
  /start-project    (universal smart router for both phases)
  /status           /reset

DOCS PHASE
  /review-brief    /approve-brief
  /build-scope-of-work    /review-scope-of-work    /approve-scope-of-work
  /build-architecture     /review-architecture     /approve-architecture
  /build-database         /review-database         /approve-database
  /build-infrastructure   /review-infrastructure   /approve-infrastructure

BUILD PHASE
  /import-docs            /parse-scope             /delta-scope
  /reqops                 /api-contract            /figma-ingest
  /refresh-mcp            /start-build             /resume-build
  /show-status            /qa-only                 /scope-interview
```

After every command, the agent reminds the user of the next valid
commands (or runs the `status` skill internally).

---

## Antigravity-specific overrides

None currently. If a future Antigravity capability requires behavior
different from the cross-tool default, document it in this section.
Until then, defer to `AGENTS.md`.
