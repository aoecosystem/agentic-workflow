---
name: build-scope-of-work
description: Generate a filled Scope of Work HTML from a previously approved Project Brief. Reads `state/SESSION-STATE.md` and refuses unless `Stage: BRIEF_APPROVED`. Reads `deliverables/brief/<slug>-brief.html` and `scope-of-work-template.html`, then writes `deliverables/scope-of-work/<slug>-sow.html` and transitions stage to SOW_DRAFT. Trigger when the user says "/build-scope-of-work", "build scope of work", "generate sow". Do NOT trigger before the brief is approved.
---

# Skill: build-scope-of-work

**Trigger:** `/build-scope-of-work` or "build scope of work" / "generate sow"

**Purpose:** Read the approved Project Brief, expand it into a complete
Scope of Work HTML matching the canonical Phase 1-10 structure, save
it under `deliverables/scope-of-work/<slug>-sow.html`, and transition the
pipeline stage to `SOW_DRAFT`.

---

## Manual-edit detection (RUN FIRST — before everything else)

Before any file operation, run the **Manual Edit Protocol** defined in
`AGENTS.md`. Briefly:

1. Compute SHA-256 of every artifact this skill will read.
2. Compare to the stored hash in `SESSION-STATE.md` Artifacts list.
3. If hashes differ, halt and ask the user to:
   - Accept (bump version, append `manual-edit` audit log line, then proceed)
   - Show diff first
   - Cancel (exit immediately)
4. Only after drift is resolved (or no drift exists), continue with the
   stage gate and the rest of this skill.

Stage does NOT change on a manual-edit accept — it stays where it was.

---


## Stage gate (BLOCKING)

1. Read `state/SESSION-STATE.md`. Locate `Stage:` and `Slug:`.
2. If `Stage:` is not `BRIEF_APPROVED`, refuse:
   > "Building the SoW requires `Stage: BRIEF_APPROVED`. Current
   > stage: `<STAGE>`. Run `/approve-brief` first (or `/status` to
   > see what's valid)."
3. If a `<slug>-scope-of-work.html` already exists and `Stage:` is
   somehow `BRIEF_APPROVED` (re-open scenario), warn:
   > "An existing SoW will be regenerated and overwritten. Continue?
   > (yes / no)"

---

## Architecture style awareness (READ THIS BEFORE GENERATING)

The brief Section 3.2 contains an "Architecture style" choice (one of:
`monolith` | `hybrid` | `microservices` | `serverless`). Before
generating output, this skill MUST:

1. Read the brief Section 3.2 to find the chosen style.
2. Read `deliverables/architecture/styles/<style>.md` end-to-end.
3. Apply the style's rules to the generated output in the relevant
   phases / sections (see "Style application points" below).

If the brief has no architecture style set (legacy briefs from before
this feature), default to `monolith` and add a TBD note in the SoW
Phase 1.5 saying "Architecture style was not specified in the brief —
defaulted to monolith. Run /review-brief 3 to set explicitly."

### Style application points (skill-specific)

- **Phase 1.5 Service Architecture:** use the style's Description as the architectural rationale paragraph.
- **Phase 2 Modules:** structure modules according to style's Folder structure (monolith = `src/services/<name>/`, hybrid/microservices = `services/<name>/`, serverless = `functions/<feature>-<action>/`).
- **Phase 3 Database Schemas:** apply style's Database approach (single DB for monolith/hybrid, per-service DB for microservices, NoSQL/serverless DB for serverless).
- **Phase 4 API Endpoints:** match style's Communication style (single API tree for monolith, per-service APIs + gateway for microservices, per-function URLs for serverless).
- **Phase 5 Event-Driven Architecture:** apply style's events approach (in-process for monolith, in-process-with-Kafka-naming for hybrid, Kafka required for microservices, EventBridge/SNS for serverless).
- **Phase 6 Tech Stack:** auto-inject the style's "Default tech additions" — these become required rows in the Integrations and Infrastructure tables.
- **Phase 9 Folder Structures:** copy the style's Folder structure block verbatim (replacing `<slug>` placeholders) into Phase 9.

### Universal rule

The style is the **single source of truth** for architecture-specific
output. Do NOT duplicate style content inside this skill. Always
re-read the style file at runtime so changes to the style flow
through automatically.

---

---

## Pre-flight

1. Read `deliverables/brief/<slug>-brief.html` end-to-end.
   Extract every section's values into memory.
2. Read `deliverables/scope-of-work/template.html` for structure
   (Phase 1-10).
3. Note the brief version (e.g. `v1.2`) — it will be referenced in
   the SoW cover-meta as the source.

---

## Mapping brief → SoW

Every brief section feeds at least one SoW phase:

| Brief section | SoW destination |
|---|---|
| 1 Project Basics | Cover, Phase 1 [P1.S1] metadata, [P1.S2] Application Type, [P1.S5] Service Architecture overview |
| 2 Problem and Solution | Phase 1 [P1.S1] Problem & Solution Statements |
| 3 Platform | Phase 1 [P1.S2] Application Type, Phase 7 Role × Platform Access Matrix |
| 4 Roles | Phase 1 [P1.S4] Roles Approach, RBAC roles in Phase 2 S1 Identity-Service |
| 5 Business Features | Phase 2 Modules (split per service S7+) |
| 6 Business Process | Phase 5.5 Critical Flows (added as `<h1>Phase 5.5: Critical Flows</h1>` block between Phase 5 and Phase 6 — conditional, only when brief Section 6 has processes) |
| 7 Business Model | Phase 1 [P1.S3] Commercialization Model |
| 8 Integrations | Phase 6 Tech Stack — Integrations row |
| 9 Special Requirements | Phase 10 Non-Functional Requirements sub-section |
| 10 Out of Scope | Phase 10 Risks, Assumptions, Out of Scope sub-section |
| 11 Design & Branding | Phase 7 UI/UX Foundation |
| 12 Timeline & Team | Phase 8 Development Approach |

---

## Depth expectations

The output must be **client-ready** — depth comparable to a
professional fixed-bid proposal, not a structural skeleton. Apply
these minimum bars per phase:

### Phase 1 — Project Overview
The template uses `<h2>` sub-sections numbered 1-5 with IDs `[P1.S1]`
through `[P1.S5]`. Match the template structure exactly.

- [P1.S1] Problem and Solution: each statement is **2-4 sentences**.
- [P1.S2] Application Type table: every row filled (real value or `TBD`).
- [P1.S3] Commercialization Model: all revenue streams from brief Section 7.
- [P1.S4] Roles Approach: every role from brief Section 4 with a
  one-sentence description and explicit role hierarchy.
- [P1.S5] Service Architecture: full S1-S6 + S7+ inventory table.

### Phase 2 — Project Modules
- Universal services S1-S6 retained verbatim from the template.
- Project services S7+ derived from brief Section 5 features.
- For each service: an `<h2>` block. For each module within a service:
  - **Rules** — 3-6 bulleted invariants
  - **User Features** table — `Feature ID | Description`, naming
    `<SERVICE>-<MODULE>-NN`
  - **System Behaviors** table — `Behavior ID | Description`, naming
    `<SERVICE>-<MODULE>-S0N`

### Phase 3 — Database Schemas
- Universal schemas S1-S6 retained.
- For each new service: tables with fields, types, PK, FK, indexes.

### Phase 4 — API Endpoints
- For every module in every service: table with
  `Method | Path | Auth | Purpose`.
- Standard API response format block.

### Phase 5 — Event-Driven Architecture
- Standard Event Payload structure.
- Event Catalog grouped per service:
  `Event name | Producer | Consumers | Payload summary`.
- Consumer Rules block.

### Phase 5.5 — Critical Flows (CONDITIONAL — only when brief Section 6 has processes)

Insert as a new `<h1>Phase 5.5: Critical Flows</h1>` block between
Phase 5 and Phase 6 in the SoW HTML. The base template does not include
this block — the skill creates it on demand.

- One flow block per process from brief Section 6.
- Each flow: Flow ID, Trigger, Outcome, Modules involved, Roles,
  vertical variants if any.
- Role × Phase matrix using brief's exact phase names as the join key.
- State machine: explicit transitions with illegal-transition notes.
- Timers table.
- Vertical config table when applicable.
- System Behavior IDs per matrix row.

### Phase 6 — Technology Stack
- Frontend, Backend, Database & Storage, Integrations,
  Infrastructure, Testing, Monitoring — each a table.

### Phase 7 — UI/UX Foundation + Page Inventory
- Role × Platform Access Matrix.
- UI/UX Design Principles table.
- Interaction Patterns table.
- Branding Placeholders from brief Section 11.2.
- **Page Inventory [P7.PI]** generated last. Group by role
  (Public+Auth, USER, custom roles, ADMIN). Each row uses page-id
  convention `<feature-slug>-<screen-slug>` in kebab-case.
  Five columns: `Page ID | Page Name | Platform | Auth | Description`.
  Auto-skip platform-irrelevant pages.

### Phase 8 — Development Approach and Steps
- Development Approach bullets.
- Environments table.
- Git Workflow.
- CI/CD pipeline summary.
- Development Steps ordered list.
- Acceptance Criteria block.

### Phase 9 — Folder Structures and CI/CD
- Backend, Frontend Web, (Frontend Mobile if Section 3 includes it),
  Infrastructure folder structures.
- GitHub Actions YAML stubs.
- Required GitHub Secrets list.

### Phase 10 — Extended Modules and Operational Specs
- Operational patterns relevant to the project.
- 10.7 Non-Functional Requirements from brief Section 9.
- 10.8 Compliance.
- 10.9 Risks, Assumptions, Out of Scope from brief Section 10.
- 10.10 Pre-Launch Branding & Setup Checklist.

---

## Generation rules

- Universal services S1-S6 stay intact in Phase 2.
- Project services start at S7.
- Mark anything not in the brief as `<span class="ph">{{TBD}}</span>`
  with a short note. Never invent.

## Tone and language

- Modern, professional, client-ready.
- Active voice.
- One-sentence-per-bullet.
- No jargon the brief did not introduce.

## HTML fidelity

- Preserve every CSS class from the template.
- Cover-sub replaced with the project name (not literal `{{PROJECT_NAME}}`).
- All metadata tables use `<table class="brief">`.
- Behavior matrices use `<table class="brief brief-roles">`.

---

## Show draft

After generating in memory, show:

- One-line summary (number of services, modules, endpoints, pages).
- List of `TBD` items the human should fill before approval.

Ask:

> "Ready to save? Reply 'save' to write
> `deliverables/scope-of-work/<slug>-sow.html`, or tell me what to
> change first."

Iterate until the user replies `save`.

---

## Save + stage transition

1. Write the file to `deliverables/scope-of-work/<slug>-sow.html` at
   version `v1.0`.
2. Update `SESSION-STATE.md`:
   - `Stage:` → `SOW_DRAFT`
   - `Last skill:` → `build-scope-of-work`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /review-scope-of-work <N> to edit, or /approve-scope-of-work to lock.`
   - Artifacts list: mark scope-of-work as draft v1.0.
3. Append audit log:
   ```
   <ISO>  build-scope-of-work  BRIEF_APPROVED → SOW_DRAFT  wrote <slug>-scope-of-work.html v1.0
   ```
4. Confirm:
   ```
   Saved: deliverables/scope-of-work/<slug>-sow.html (v1.0)
   Open in your browser to review:
     file:///<absolute-path>/deliverables/scope-of-work/<slug>-sow.html
   ```

---

## Hand off

After saving, present:

```
What's next?

  /review-scope-of-work <phase>
    Edit a specific phase. Iterative.

  /approve-scope-of-work
    Run the SoW quality gate and lock it. Unlocks /build-architecture.
```

Stop. Do NOT auto-trigger.

---

## Rules

- Templates (`scope-of-work-template.html`) are read-only.
- Only `deliverables/scope-of-work/<slug>-sow.html` is writable here.
- Universal services S1-S6 must remain intact.
- Mark unknowns as `TBD`. Never invent.
- After save, remind the user of the two follow-up options.
