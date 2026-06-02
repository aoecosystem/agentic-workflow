# Project Session State

<!--
Auto-managed by all skills. Humans rarely edit this file.
To start fresh: delete this file or set Stage to INIT (or run /reset).

This file is the single source of truth for:
  - which pipeline stage the project is in (docs phase OR build phase)
  - which artifacts are drafted / approved / built
  - what command the user can run next
  - audit log of every state transition
-->

## Header

- **Slug:** <!-- e.g. bookspot — kebab-case project identifier -->
- **Stage:** INIT
- **Architecture style:** <!-- monolith / hybrid / microservices / serverless -->
- **Last skill:** <!-- name of the skill that last wrote this file -->
- **Last update:** <!-- ISO 8601 timestamp -->
- **Resume hint:** Run /start-project to begin (smart router — picks the right next step).

## Stage machine

```
═══════ DOCS PHASE (foundations pipeline) ═══════

INIT
  └─ /start-project ──→ INTERVIEW ──→ BRIEF_DRAFT ⇄ BRIEF_APPROVED
                                      ──→ SOW_DRAFT ⇄ SOW_APPROVED
                                      ──→ ARCHITECTURE_DRAFT ⇄ ARCHITECTURE_APPROVED
                                          ↓
                                      DOCS_COMPLETE   ← 3 HTMLs approved

═══════ BUILD PHASE (engine pipeline) ═══════

DOCS_COMPLETE
  └─ /parse-scope ──→ TASKS_GENERATED ⇄ TASKS_APPROVED
  └─ /start-build ──→ BUILDING
                       ↓ (orchestrator + builders + QA loop, parallel)
                       ↓ (all tasks reach `done`)
                      BUILD_COMPLETE ⇄ BUILD_APPROVED
  └─ /verify-build ──→ VERIFIED  (lint + types + tests pass)
                       ↓
                      READY_TO_DEPLOY  ← project ready
```

`⇄` = re-openable via the matching `/review-*` command.

**Valid stages:**

```
DOCS PHASE:                         BUILD PHASE:
INIT                                DOCS_COMPLETE
INTERVIEW                           TASKS_GENERATED
BRIEF_DRAFT                         TASKS_APPROVED
BRIEF_APPROVED                      BUILDING
SOW_DRAFT                           BUILD_COMPLETE
SOW_APPROVED                        BUILD_APPROVED
ARCHITECTURE_DRAFT                  VERIFIED
ARCHITECTURE_APPROVED               READY_TO_DEPLOY
```

**Reversibility:** any `*_APPROVED` stage can be re-opened by running the
matching `/review-*` command. The stage moves back to `*_DRAFT` and the
event is recorded in the audit log. Downstream stages remain valid until
the user re-runs the next `/build-*` to pick up the change.

**No auto-advance:** every transition requires an explicit user command.

## Artifacts

Tracks which deliverables exist on disk and their approval status.
Each line carries the file's current SHA-256 hash so the agent can
detect manual edits between runs.

Format: `- [status] <path>  v<version>  sha256:<hash>  <state> <date>`

When an artifact does not exist yet, omit the hash and version:
`- [ ] <path>  (not yet built)`

### Docs phase artifacts (3 HTMLs from foundations pipeline)

- [ ] DOCMENTS/<slug>-project-brief.html  (not yet built)
- [ ] DOCMENTS/<slug>-scope-of-work.html  (not yet built)
- [ ] DOCMENTS/<slug>-system-architecture.html  (not yet built — includes DB schema + infrastructure)

### Build phase artifacts

- [ ] SESSION-STATE/TASKS.md  (not yet generated)
- [ ] APPS/<slug>/  (not yet scaffolded)

## Audit log

<!--
Append-only. One line per state transition.
Format:  YYYY-MM-DDTHH:MM:SSZ  <SKILL>  <FROM> → <TO>  <NOTE>

Examples:
- 2026-05-02T10:00:00Z  start-project           INIT → INTERVIEW
- 2026-05-02T10:30:00Z  start-project           INTERVIEW → BRIEF_DRAFT       wrote <slug>-project-brief.html v1.0
- 2026-05-02T11:00:00Z  approve-brief           BRIEF_DRAFT → BRIEF_APPROVED  v1.0 locked
- 2026-05-02T13:00:00Z  approve-architecture  ARCHITECTURE_DRAFT → DOCS_COMPLETE  all 3 docs approved
- 2026-05-02T13:30:00Z  parse-scope           DOCS_COMPLETE → TASKS_GENERATED  42 tasks
- 2026-05-02T14:00:00Z  start-build             TASKS_APPROVED → BUILDING
- 2026-05-02T18:00:00Z  orchestrate             BUILDING → BUILD_COMPLETE  all tasks done
- 2026-05-02T18:15:00Z  verify-build            BUILD_APPROVED → VERIFIED  lint+types+tests pass
-->

<!-- The audit log is empty until /start-project runs for the first time. -->

## Interview progress

<!-- Only meaningful during the INTERVIEW stage. Reset/cleared on transition to BRIEF_DRAFT. -->

- **Current section:** —
- **Sections completed:** —
- **Sections remaining:** —
- **Last question asked:** —

## Captured answers

<!-- Populated during the INTERVIEW stage by start-project. -->

## Build progress

<!-- Populated during BUILDING stage by orchestrate. Updated after every task transition. -->

- **Total tasks:** —
- **Done:** —
- **In progress:** —
- **In review:** —
- **Needs fix:** —
- **Blocked:** —
- **Pending:** —

## Notes

<!-- Free-form scratch space. -->
