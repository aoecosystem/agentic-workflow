---
name: start-project
description: Universal smart router for the agentic-workflow pipeline. Reads `state/SESSION-STATE.md` and routes the user to the right next step based on current Stage. Spans BOTH docs phase (foundations) and build phase (engine). Trigger when the user says "start project", "begin", "new project", "where do I start", "what's next", or runs `/start-project`.
---

# Skill: start-project (smart router for docs + build)

**Trigger:** `/start-project` or "start project" / "begin" / "new project" / "what's next"

**Purpose:** Read `state/SESSION-STATE.md` and route the user to the right
next action based on current Stage. This is the **single entry point**
for the entire pipeline — docs phase (foundations) AND build phase (engine).

This skill never builds or writes deliverables itself — only routes.
The actual work happens in the skill it routes to.

---

## Routing logic (FIRST STEP, ALWAYS)

1. Read `state/SESSION-STATE.md`. Locate the `Stage:` field.
2. Branch based on Stage:

### Branch A — Docs phase (foundations pipeline)

| Current Stage | Next action / route |
|---|---|
| `INIT` (or file missing) | Start **brief interview** — walk user through 13 sections, write `<slug>-brief.html`, transition to `BRIEF_DRAFT`. |
| `INTERVIEW` | Resume the interview from the last checkpoint (read Captured answers, jump to next unanswered question). |
| `BRIEF_DRAFT` | Tell user: run `/review-brief <N>` to edit, or `/approve-brief` to lock. |
| `BRIEF_APPROVED` | Tell user: run `/build-scope-of-work` to generate the SoW. |
| `SOW_DRAFT` | Tell user: run `/review-scope-of-work <phase>` to edit, or `/approve-scope-of-work` to lock. |
| `SOW_APPROVED` | Tell user: run `/build-architecture` to generate the System Architecture HTML. |
| `ARCHITECTURE_DRAFT` | Tell user: run `/review-architecture` to edit, or `/approve-architecture` to lock. |
| `ARCHITECTURE_APPROVED` | Tell user: run `/build-database` to generate the Database Diagram HTML. |
| `DATABASE_DRAFT` | Tell user: run `/review-database` to edit, or `/approve-database` to lock. |
| `DATABASE_APPROVED` | Tell user: run `/build-infrastructure` to generate the Infrastructure Diagram HTML. |
| `INFRASTRUCTURE_DRAFT` | Tell user: run `/review-infrastructure` to edit, or `/approve-infrastructure` to lock (this advances to DOCS_COMPLETE). |
| `INFRASTRUCTURE_APPROVED` | Auto-transitioned to DOCS_COMPLETE by `/approve-infrastructure` — should not stay in this stage. If observed, tell user: run `/parse-scope` to start the build phase. |

### Branch B — Build phase (engine pipeline)

| Current Stage | Next action / route |
|---|---|
| `DOCS_COMPLETE` | Tell user: run `/parse-scope` to generate `state/TASKS.md` directly from the 5 approved HTMLs. |
| `TASKS_GENERATED` | Tell user: run `/approve-tasks` to audit and lock the task graph. |
| `TASKS_APPROVED` | Tell user: run `/start-build` to kick off the orchestrator + builders + QA loop. |
| `BUILDING` | Tell user: build is in progress. Run `/show-status` for task progress; `/resume-build` to continue if interrupted; `/qa-only` to run QA on any `in-review` tasks. |
| `BUILD_COMPLETE` | Tell user: run `/approve-build` to lock the completed build (human approval gate). |
| `BUILD_APPROVED` | Tell user: run `/verify-build` for the final automated gate (lint + types + tests + native runtime). |
| `VERIFIED` | Tell user: run `/package-release` to produce release artifacts. |
| `READY_TO_DEPLOY` | Tell user: project is complete. Code lives at `../apps/`. Deploy from there. |

---

## Brief interview (only when Stage = INIT)

When Stage is `INIT`, this skill becomes the **brief interview** — same
13-section interview as the project-foundations `start-project` skill.

1. Read `deliverables/brief/template.html` end-to-end.
2. Update `state/SESSION-STATE.md`: `Stage: INTERVIEW`, audit log line.
3. Walk through the 13 sections one question per turn. Restate each
   answer briefly before asking the next.
4. After Section 1 (Project Basics), derive a kebab-case slug from
   project name and confirm with user.
5. After Section 3.2, ask for **Architecture style**:
   `monolith` | `hybrid` | `microservices` | `polyglot-microservices` | `serverless`. Default
   `monolith`. Briefly explain each option in plain language. Note for
   `polyglot-microservices`: only pick this when one or two services
   have genuinely different runtime needs (heavy compute, ML, real-time)
   that a single language can't serve well — otherwise prefer plain
   `microservices`.
6. After all 13 sections, show summary, ask `save`.
7. On save: write `deliverables/brief/<slug>-brief.html` v1.0,
   transition Stage to `BRIEF_DRAFT`, append audit log.

See `deliverables/brief/template.html` for the 13 sections.

---

## Resumability

If `Stage: INTERVIEW` (interview interrupted):

> "I see an in-progress interview for `<slug>` paused at section `<N>`.
> Reply 'continue' to pick up there, or 'fresh' to archive and start over."

- On `continue`: read `Captured answers` and jump to next unanswered question.
- On `fresh`: copy current SESSION-STATE.md to `state/archived/<slug>-<ISO>.md`,
  reset to `INIT`, restart interview.

---

## Manual-edit detection

Before routing or interviewing, this skill MUST check for hash drift on
any artifact in the Artifacts list per the **Manual Edit Protocol** in
`AGENTS.md`. If drift detected, halt and offer accept / show diff /
cancel options.

---

## Stage transitions written by this skill

- `INIT → INTERVIEW`  (when starting fresh interview)
- `INTERVIEW → BRIEF_DRAFT`  (when interview saves successfully)
- All others: this skill only **reports** next steps; the actual transition
  happens in the destination skill (`/approve-brief`, `/parse-scope`, etc.).

---

## Hand off

After routing, print the recommended command and stop. Never
auto-trigger the next step — the user must run it explicitly.

---

## Rules

- One question per turn during interviews.
- Templates are read-only. Only `deliverables/<type>/<slug>-*.html` is writable here (where `<type>` is brief / scope-of-work / architecture / database / infrastructure).
- Mark unknowns as `TBD`. Never invent.
- Slug is stable for the project's lifetime.
- HTML output preserves all CSS classes from the template.
- After save, remind user of next valid commands.
- Read-modify-write `state/SESSION-STATE.md` every meaningful turn.
- Audit log is append-only.
