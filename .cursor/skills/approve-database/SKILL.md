---
name: approve-database
description: Lock the Database Diagram and transition Stage from DATABASE_DRAFT to DATABASE_APPROVED. Verifies Mermaid `erDiagram` compiles, every relationship in Section 3 has matching entities in Section 2, every SoW Phase 3 table appears, cover-sub replaced. Updates `state/SESSION-STATE.md`, appends audit log. Trigger on `/approve-database`.
---

# Skill: approve-database

**Trigger:** `/approve-database`

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


## Stage gate

1. Read `SESSION-STATE.md`. Locate `Stage:` and `Slug:`.
2. If `Stage` is not `DATABASE_DRAFT`, refuse with the uniform message:
   > "Approve is only valid from `DATABASE_DRAFT`. Current stage: `<STAGE>`.
   > Run `/status` to see the next valid commands. To reach
   > `DATABASE_DRAFT`, run `/build-database` (after the architecture is approved)."
   Leave Stage unchanged.

---

## Quality gate (BLOCKING)

Read `deliverables/database/<slug>-database.html` and the approved
`<slug>-scope-of-work.html`. Verify:

1. **All 6 sections present and non-empty.**
2. **No raw unfilled placeholders.** A `<span class="ph">` is acceptable
   when its inner text starts with `TBD` or `{{TBD` — that's an explicit
   "to be decided" marker the user has acknowledged. Only unfilled blanks
   like `{{COLUMN_NAME}}`, `{{TODO}}`, `{{FILL_THIS}}`, or `{{PROJECT_NAME}}`
   fail the gate. Every placeholder is either replaced with a real value
   or explicitly marked `TBD`.
3. **Cover-sub replaced.** Project name appears, not `{{PROJECT_NAME}}`.
4. **SoW coverage.** Every entity / table from SoW Phase 3 appears in
   Section 2 Entity Definitions.
5. **Relationship integrity.** Every relationship in Section 3
   references entities that exist in Section 2 (no dangling FKs).
6. **Mermaid `erDiagram` compiles.** No syntax errors. Field names use
   `snake_case`. Cardinality lines use valid syntax (`||--o{{`,
   `}}o--||`, `}}o--o{{`).
7. **Primary keys defined.** Every entity has at least one PK column.

If any check fails, list every failing item, leave Stage at
`DATABASE_DRAFT`, recommend `/review-database <N>`.

---

## Transition

1. Update `SESSION-STATE.md`:
   - `Stage:` → `DATABASE_APPROVED`
   - `Last skill:` → `approve-database`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /build-infrastructure to draft the Infrastructure Diagram.`
   - Artifacts: mark database approved with version + date.
2. Append audit log:
   ```
   <ISO>  approve-database  DATABASE_DRAFT → DATABASE_APPROVED  v<X> locked
   ```

---

## Confirm + hand off

```
Database approved. v<X> locked.

Next valid commands:

  /build-infrastructure     Draft the Infrastructure Diagram.
  /review-database          Re-open for edits.
```

Stop. Do NOT auto-trigger.

---

## Rules

- Read-only on database HTML during approval.
- Single source of truth = `SESSION-STATE.md`.
