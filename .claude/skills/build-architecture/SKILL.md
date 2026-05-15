---
name: build-architecture
description: Generate the System Architecture HTML from the approved Scope of Work. Reads `state/SESSION-STATE.md` and refuses unless `Stage: SOW_APPROVED`. Reads `deliverables/scope-of-work/<slug>-sow.html` (especially Phase 2 Service Inventory and Phase 4 Data Flow) and the empty `deliverables/architecture/template.html` template, then writes `deliverables/architecture/<slug>-architecture.html` and transitions Stage to ARCHITECTURE_DRAFT. Trigger when the user says "/build-architecture", "build architecture", "generate architecture".
---

# Skill: build-architecture

**Trigger:** `/build-architecture`

**Purpose:** Read the approved Scope of Work, draft a complete System
Architecture HTML matching the canonical 7-section structure, save it
under `deliverables/architecture/<slug>-architecture.html`, and
transition the pipeline stage to `ARCHITECTURE_DRAFT`.

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
2. If `Stage` is not `SOW_APPROVED`, refuse:
   > "Building architecture requires `Stage: SOW_APPROVED`. Current
   > stage: `<STAGE>`. Run `/approve-scope-of-work` first."
3. If `<slug>-system-architecture.html` already exists, warn:
   > "Existing architecture file will be regenerated and overwritten.
   > Continue? (yes / no)"

---

## Architecture style awareness (READ THIS BEFORE GENERATING)

The brief Section 3.2 contains an "Architecture style" choice (one of:
`monolith` | `hybrid` | `microservices` | `polyglot-microservices` | `serverless`). Before
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

- **Section 1 Architecture Overview:** lead with the style's Description as the architectural rationale.
- **Section 2 Service Inventory:** treat each service per the style's communication style (modules for monolith, deployable units for microservices, functions for serverless).
- **Section 7 Visual Diagram:** use the style's "Mermaid diagram patterns → System architecture diagram" convention. Different styles produce visibly different diagrams:
  - monolith: flat services inside one Domain subgraph
  - hybrid: services as separate nodes with extraction-ready visual hint
  - microservices: each service in its own subgraph + Kafka bus + gateway
  - serverless: API Gateway → functions → event bus → DB cylinders

### Universal rule

The style is the **single source of truth** for architecture-specific
output. Do NOT duplicate style content inside this skill. Always
re-read the style file at runtime so changes to the style flow
through automatically.

---

---

## Pre-flight

1. Read `deliverables/scope-of-work/<slug>-sow.html` end-to-end. Extract:
   - Phase 1.5 Service Architecture (S1-Sn inventory)
   - Phase 2 module structure (services + their modules)
   - Phase 4 API endpoint patterns (data flow shape)
   - Phase 6 Tech Stack (transport choices, framework)
   - Phase 5 Event-Driven Architecture (async edges)
2. Read `deliverables/architecture/template.html` for structure.
3. Read brief `<slug>-project-brief.html` Section 1 for project name
   to populate cover-sub.

---

## Generation rules

Fill every section of the template with content derived from the SoW:

### 1. Architecture Overview
- 4-6 architecture decisions (e.g. "Modular monolith for Phase 1",
  "Event-driven boundaries between services", "Postgres + Redis split").
- Each decision is one sentence with a brief rationale.

### 2. Service Inventory
- One row per service from SoW Phase 1.5: code (S1..Sn), name, type
  (Universal | Project), one-line purpose.
- Universal services (S1-S6) preserved verbatim.

### 3. Layered Architecture
- Keep the universal layer rules from the template.
- Add a project-specific note if the SoW uses an unusual transport
  pattern (e.g. tRPC, GraphQL).

### 4. Data Flow
- Step-by-step request flow from client → API → service → repository
  → database.
- Reference real example endpoints from SoW Phase 4.

### 5. Module Boundaries & Contracts
- One sub-section per service. List each module with its boundary
  rule (what it owns, what it never touches).
- Reference Phase 2 module IDs.

### 6. Cross-Cutting Concerns
- Auth, logging, error handling, observability, caching, i18n.
- Pull specifics from SoW Phase 6 (Tech Stack) and Phase 7 (UI).

### 7. Architecture — Visual Diagram
- Mermaid `flowchart TB` block matching the existing layered structure
  (Client → API Gateway → Domain → Data + External nested).
- Service nodes use `&nbsp;` padding and the layer `classDef` colors.
- One node per service from Section 2 (S1..Sn).
- Solid arrows for sync calls; dashed (`-.->`) for async events.
- `linkStyle` for event edges (orange dashed).
- Mermaid block must compile.

---

## HTML fidelity

- Preserve every CSS class from the template.
- Cover: replace cover-sub `{{PROJECT_NAME}}` with the real project name.
- Keep print toolbar at bottom-center.
- Mark unknowns as `TBD` with a short comment, never invent.

---

## Show draft

After generating in memory:

- One-line summary (services included, modules covered, async events
  highlighted).
- List of `TBD` items the human should review.

Ask:

> "Ready to save? Reply 'save' to write
> `deliverables/architecture/<slug>-architecture.html`, or tell me
> what to change first."

Iterate until `save`.

---

## Save + stage transition

1. Write to `deliverables/architecture/<slug>-architecture.html` v1.0.
2. Update `SESSION-STATE.md`:
   - `Stage:` → `ARCHITECTURE_DRAFT`
   - `Last skill:` → `build-architecture`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /review-architecture or /approve-architecture.`
   - Artifacts list: mark architecture as draft v1.0.
3. Append audit log:
   ```
   <ISO>  build-architecture  SOW_APPROVED → ARCHITECTURE_DRAFT  wrote <slug>-system-architecture.html v1.0
   ```

---

## Hand off

```
Saved: deliverables/architecture/<slug>-architecture.html (v1.0)

What's next?

  /review-architecture
    Edit a specific section.

  /approve-architecture
    Run the architecture quality gate and lock it. Unlocks /build-database.
```

Stop. Do NOT auto-trigger.

---

## Rules

- Templates are read-only.
- Universal services S1-S6 stay intact.
- Mermaid block must compile (no syntax errors).
- Mark unknowns as `TBD`.
