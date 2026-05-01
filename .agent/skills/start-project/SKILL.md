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
| `INIT` (or file missing) | Start **brief interview** — walk user through 13 sections, write `<slug>-project-brief.html`, transition to `BRIEF_DRAFT`. (Same behavior as project-foundations' start-project.) |
| `INTERVIEW` | Resume the interview from the last checkpoint (read Captured answers, jump to next unanswered question). |
| `BRIEF_DRAFT` | Tell user: run `/review-brief <N>` to edit, or `/approve-brief` to lock. |
| `BRIEF_APPROVED` | Tell user: run `/build-scope-of-work` to generate the SoW. |
| `SOW_DRAFT` / `SOW_APPROVED` / `ARCHITECTURE_*` / `DATABASE_*` / `INFRASTRUCTURE_*` | Tell user the next valid command for that stage (use the `/status` skill internally). |

### Branch B — Build phase (engine pipeline)

| Current Stage | Next action / route |
|---|---|
| `DOCS_COMPLETE` | Tell user: run `/import-docs` to extract `state/SCOPE.md` from the 5 approved HTMLs. |
| `SCOPE_PARSED` | Tell user: run `/parse-scope` (or `parse scope`) to generate `state/TASKS.md`. |
| `TASKS_GENERATED` / `TASKS_APPROVED` | Tell user: run `/start-build` to begin building. Or `/audit-tasks` first if they want a sanity review. |
| `BUILDING` | Tell user: build is in progress. Run `/show-status` to see task progress, `/resume-build` to continue if paused. |
| `BUILD_COMPLETE` / `BUILD_APPROVED` | Tell user: run `/verify-build` for final QA gate. |
| `VERIFIED` | Tell user: run `/package-release` (or skip if not used). |
| `READY_TO_DEPLOY` | Tell user: project is complete. They can deploy from `../apps/`. |

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
   `monolith` | `hybrid` | `microservices` | `serverless`. Default
   `monolith`. Briefly explain each option in plain language.
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
  happens in the destination skill (`/approve-brief`, `/import-docs`, etc.).

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
