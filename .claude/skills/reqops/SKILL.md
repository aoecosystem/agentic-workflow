---
name: reqops
description: ReqOps requirements specialist. Reads scope from the 5 deliverable HTMLs (the canonical post-import-docs surface) with DOCMENTS/<slug>-scope-of-work.html as fallback and produces dev-ready, SOW-traceable feature requirements under CONTEXT/feature-specs/<feature-id>-<slug>-requirements.md with user stories, Given/When/Then acceptance criteria (MoSCoW-tagged), NFRs, edge cases, test cases, smart checklist, and change logs. Trigger when the user says "reqops", "derive requirements", "generate requirements from SCOPE.md", or runs parse-scope with the ReqOps pre-pass. Does NOT write SESSION-STATE/TASKS.md — parse-scope owns that.
---

## Stage gate (RUN FIRST)

1. Read `SESSION-STATE/SESSION-STATE.md`. Locate `Stage:`.
2. Refuse unless Stage is `DOCS_COMPLETE`, `TASKS_GENERATED`, `TASKS_APPROVED`, or later. Message:
   > "reqops requires the 5 HTMLs to be approved. Current Stage: `<STAGE>`. Complete the docs phase first."

---

# Skill: ReqOps

**Trigger:** User says `reqops`, or `parse scope` runs with ReqOps pre-pass enabled.

**Purpose:** Read scope from the 5 deliverable HTMLs, derive implementation-ready requirements, and generate/update `SESSION-STATE/TASKS.md` so Builder/QA can execute against concrete user outcomes.

---

## Authoritative input order

Read in this precedence order:

1. the 5 deliverable HTMLs (authoritative — approved at Stage `DOCS_COMPLETE`)
2. `DOCMENTS/<slug>-scope-of-work.html` (rarely-used legacy fallback)
3. `CONTEXT/feature-specs/` / `DOCMENTS/<slug>-scope-of-work.html` / `DOCMENTS/<slug>-system-architecture.html` (optional support context)
4. `CONTEXT/feature-specs/` files for other features (optional dependency context)

Conflict rule:
- If any lower-precedence file conflicts with the selected SOW source, SOW wins.
- Record the conflict as `GAP-XX` with file path + contradiction summary.

Hard stop:
- If no usable SOW source exists in the 5 deliverable HTMLs or `DOCMENTS/<slug>-scope-of-work.html`, stop and emit exactly:
  - `ERROR: Scope of work not found. ReqOps AI cannot proceed without an authoritative SOW source in SCOPE.md or DOCMENTS/<slug>-scope-of-work.html.`

---

## Process

### Step 1 — Anchor to SOW

Read the chosen SOW source fully and isolate passages that define the target feature.
Every requirement and acceptance criterion must be traceable back to SOW text.

When sourcing from the 5 deliverable HTMLs:
- Read the 5 deliverable HTMLs end-to-end.
- Prioritize files with names like `scope-of-work`, `sow`, `requirements`, `prd`, or `spec`.
- Build one normalized feature map before generating outputs.

### Step 2 — Gather context and contradictions

Read remaining context files (if they exist):
- capture constraints and NFRs affecting the feature
- capture contradictions against SOW as `GAP-XX`
- do not silently resolve conflicts

### Step 3 — Define actors, goals, dependencies

Identify:
- actors/roles using exact SOW vocabulary
- intended outcome
- upstream blockers and downstream impact

### Step 4 — Set explicit scope boundary

Produce:
- in-scope boundaries
- out-of-scope boundaries
- unresolved adjacent scope as assumptions or gaps

### Step 5 — Draft verifiable requirements

Write feature requirements with:
- User Story
- Description with SOW traceability bullets
- Out of Scope list
- Feature dependencies
- Functional ACs (Given/When/Then, MoSCoW tagged)
- Non-functional ACs grouped by category
- Functional Notes (rules, constraints, assumptions, data/state, integrations, gaps)
- User Flow (ordered user journey)
- Edge Cases (explicit no-result/invalid/auth/performance fallback behavior where applicable)
- Test Cases (numbered checks mapped to AC coverage)
- Smart Checklist mapped to AC coverage
- Definition of Done
- Change Log

### Step 6 — Produce requirements (TASKS.md is owned by parse-scope)

ReqOps writes only requirement files, not `SESSION-STATE/TASKS.md`.

`SESSION-STATE/TASKS.md` generation is owned exclusively by the `parse-scope` skill. This
keeps task-file ownership unambiguous when a user chains `reqops` and
`parse scope`.

What ReqOps does in this step:

1. Write / update one requirement file per feature in
   `CONTEXT/feature-specs/<feature-id>-<feature-slug>-requirements.md`.
2. Populate the sections listed in the Template (User Story, Description,
   Out of Scope, Feature Dependencies, ACs, NFRs, Functional Notes, Smart
   Checklist, DoD, Change Log).
3. Ensure every AC carries a ReqOps ID (e.g. `[SD-01]`, `[AC-02]`) so
   `parse-scope` can emit these IDs into task acceptance criteria.
4. Emit a summary in chat telling the user to run `parse scope` next if
   they want task blocks generated or updated from the new requirements.

If a requirement file already exists:
- Increment the version, append a Change Log entry, preserve history.
- Do not overwrite silently.

ReqOps does not touch `SESSION-STATE/TASKS.md`.

### Step 7 — Validate before save

Do not save until these checks pass:
- every AC maps to SOW reference
- every SOW feature constraint is represented by AC(s)
- every AC has at least one checklist/test mapping
- every `[Must]` AC has P0-level checklist coverage
- unresolved ambiguity is flagged as `GAP-XX` or `A-XX`
- no implementation-level HOW decisions unless SOW explicitly mandates them
- dependency and downstream impact sections are populated (or explicitly "None identified.")
- generated/updated `SESSION-STATE/TASKS.md` includes product-context addendum for user-facing tasks
- generated/updated `SESSION-STATE/TASKS.md` includes files, dependencies, and acceptance criteria that are executable by Builder/QA

---

## Output file rules

Save only to:
- `CONTEXT/feature-specs/<feature-id>-<feature-slug>-requirements.md`

`SESSION-STATE/TASKS.md` is owned by `parse-scope` and is not written by ReqOps.

Update behavior:
- If the requirements file exists, do not overwrite silently.
- Increment version and append Change Log.
- Update only changed sections and preserve history.

Requirements output is one file per feature. Running `parse scope` after
`reqops` will generate / update `SESSION-STATE/TASKS.md` from those requirements.

---

## Template

Use this exact section order:

1. Header metadata (Feature, SOW ref, ID, Version, Status, Date, Extends spec)
2. User Story
3. Description (+ SOW traceability bullets)
4. Out of Scope
5. Feature Dependencies (Upstream + Downstream)
6. Acceptance Criteria
   - Functional (Given/When/Then + MoSCoW)
   - Non-functional by category (Performance, Security, Accessibility, Reliability, Compliance)
7. Functional Notes
   - Business Rules
   - Constraints & Assumptions
   - Data & State
   - Integration Points
   - SOW Gaps
8. Smart Checklist (AC-referenced)
9. Definition of Done
10. Change Log

---

## Guardrails

- SOW is law. Do not invent requirements.
- Define WHAT, not HOW.
- Every AC must include MoSCoW tag.
- Smart Checklist must cover functional, edge/error, security, and performance concerns where applicable.
- Always include Out of Scope entries.
- Always record open ambiguity as `GAP-XX` (not silent defaults).
- Use exact SOW terminology for roles/entities/states/actions.
- ReqOps is complete when the per-feature requirement files are written and
  validated. `SESSION-STATE/TASKS.md` generation is a separate step performed by
  `parse-scope`.
