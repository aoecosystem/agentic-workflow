---
name: build-database
description: Generate the Database Diagram HTML from the approved Architecture + SoW. Reads `state/SESSION-STATE.md` and refuses unless `Stage: ARCHITECTURE_APPROVED`. Reads `deliverables/scope-of-work/<slug>-sow.html` (especially Phase 3 Database Schemas) plus `deliverables/architecture/<slug>-architecture.html`, then writes `deliverables/database/<slug>-database.html` and transitions Stage to DATABASE_DRAFT. Trigger on "/build-database", "build database", "generate database diagram".
---

# Skill: build-database

**Trigger:** `/build-database`

**Purpose:** Read approved SoW + Architecture, draft the Database
Diagram HTML matching the canonical 6-section structure, save it
under `deliverables/database/<slug>-database.html`, transition
Stage to `DATABASE_DRAFT`.

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

1. Read `SESSION-STATE.md`. Locate `Stage:` and `Slug:`.
2. If `Stage` is not `ARCHITECTURE_APPROVED`:
   > "Building database requires `Stage: ARCHITECTURE_APPROVED`.
   > Current: `<STAGE>`. Run `/approve-architecture` first."
3. If a `<slug>-database-diagram.html` already exists, warn before
   overwriting.

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

- **Section 1 Schema Overview + Section 2 Entity Definitions:** apply style's Database approach. For monolith/hybrid, a single shared schema; for microservices, separate `<h2>Service: <name></h2>` blocks with NO cross-service FKs.
- **Section 3 Relationships:** monolith allows cross-module FKs; hybrid replaces them with ID-only references; microservices forbids cross-service relations entirely.
- **Section 6 Visual ERD:** style's "Mermaid diagram patterns → Database diagram" convention. For DynamoDB-style serverless, use a table layout instead of `erDiagram`.

### Universal rule

The style is the **single source of truth** for architecture-specific
output. Do NOT duplicate style content inside this skill. Always
re-read the style file at runtime so changes to the style flow
through automatically.

---

---

## Pre-flight

1. Read `deliverables/scope-of-work/<slug>-sow.html`. Extract:
   - Phase 3 Database Schemas (per-service tables with fields,
     types, PK, FK, indexes).
   - Phase 5 events (which entities are referenced).
2. Read `deliverables/architecture/<slug>-architecture.html` for
   service structure.
3. Read `deliverables/database/template.html` for template structure.
4. Read brief `<slug>-project-brief.html` Section 1 for project name.

---

## Generation rules

### 1. Schema Overview
- One row per entity from SoW Phase 3: number, entity name, service
  code (S1..Sn), one-line purpose.
- Group by service for readability.

### 2. Entity Definitions
- One block per entity grouped under `<h2>Service: <name></h2>`.
- Each entity uses `<div class="entity">` with header + table:
  `Column | Type | Constraints | Notes`.
- Always include `id uuid PK default gen_random_uuid()` as row 1.
- Include `created_at`, `updated_at` timestamptz on every entity that
  needs them.
- Foreign keys noted as `FK→<other_table>.id`.

### 3. Relationships
- One row per FK: `<from_entity>.<column> → <to_entity>.<column>`,
  with cardinality (1:1, 1:N, N:M).
- Group by referenced entity.

### 4. Indexes Strategy
- Keep universal rules from template (index FKs, selective WHERE
  columns, composite, partial).
- Add per-entity index list referencing real query patterns from
  SoW Phase 4 endpoints.

### 5. Migration & Versioning
- Tool (Prisma migrate / Knex / Flyway) — pull from SoW Phase 6.
- Naming convention.
- Rollback policy.
- Seed data approach.

### 6. ERD — Visual Diagram
- Mermaid `erDiagram` block.
- One `ENTITY {{...}}` block per table from Section 2 with `snake_case`
  field names.
- Every FK from Section 3 → one relationship line with correct
  cardinality (`||--o{{`, `}}o--||`, `}}o--o{{`).
- Mark PK / FK / UK on relevant columns.
- Group related entities by service.
- Mermaid must compile.

---

## HTML fidelity

- Preserve every CSS class from the template (`entity`, `entity-header`,
  `entity-table`, `mermaid-host`, etc.).
- Cover-sub replaced with the project name.
- Keep print toolbar at bottom-center.
- Mark unknowns as `TBD`.

---

## Show draft + save

After generating in memory:

- One-line summary (entity count, relationship count, services covered).
- List of `TBD` items.

Ask: *"Ready to save?"* Iterate until `save`.

On save:

1. Write `deliverables/database/<slug>-database.html` v1.0.
2. Update `SESSION-STATE.md`:
   - `Stage:` → `DATABASE_DRAFT`
   - `Last skill:` → `build-database`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /review-database or /approve-database.`
   - Artifacts: mark database as draft v1.0.
3. Append audit log:
   ```
   <ISO>  build-database  ARCHITECTURE_APPROVED → DATABASE_DRAFT  wrote <slug>-database-diagram.html v1.0
   ```

---

## Hand off

```
Saved: deliverables/database/<slug>-database.html (v1.0)

What's next?

  /review-database         Edit a specific section.
  /approve-database        Run quality gate and unlock /build-infrastructure.
```

Stop. Do NOT auto-trigger.

---

## Rules

- Templates read-only.
- Mermaid `erDiagram` must compile.
- Every SoW Phase 3 table must appear as an entity.
- Mark unknowns as `TBD`.
