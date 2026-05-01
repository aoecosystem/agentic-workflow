---
name: review-database
description: Iterative section-by-section editor for the Database Diagram. Reads `state/SESSION-STATE.md`, refuses unless Stage is DATABASE_DRAFT or DATABASE_APPROVED, lets the user pick one of the 6 sections, applies the change, bumps version, writes audit log. If Stage is DATABASE_APPROVED, re-opens to DATABASE_DRAFT. Trigger on "/review-database", "review database", "edit database".
---

# Skill: review-database

**Trigger:** `/review-database <section>` or "edit database"

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

1. Read `SESSION-STATE.md`.
2. If `Stage` is not `DATABASE_DRAFT` or `DATABASE_APPROVED`, refuse.
3. If `DATABASE_APPROVED`, warn re-open will revert to DATABASE_DRAFT.
   Downstream (infrastructure) should be re-built afterward.

---

## Pre-flight

1. Read `deliverables/database/<slug>-database.html`.

---

## Show section menu

```
Which section do you want to edit?

   1. Schema Overview
   2. Entity Definitions
   3. Relationships
   4. Indexes Strategy
   5. Migration & Versioning
   6. ERD — Visual Diagram

Reply with a number (1-6) or section name.
```

Skip the menu if the user passed a section number.

---

## Edit one section

1. Read current content; show inline.
2. Ask what to change.
3. Apply in memory; preserve CSS classes.
4. Show diff summary.
5. Ask to save (yes / no / show me again).

For Section 6 (Mermaid ERD): if the user adds or renames an entity in
Section 2, also offer to update the ERD block to match.

---

## Save and update state

1. Write updated HTML.
2. Bump version (`v1.0` → `v1.1`).
3. Update `SESSION-STATE.md`:
   - `Stage:` → `DATABASE_DRAFT`
   - `Last skill:` → `review-database`
   - `Last update:` → ISO timestamp
4. Append audit log:
   ```
   <ISO>  review-database  <FROM> → DATABASE_DRAFT  section <N> revised, v<X> → v<Y>
   ```

---

## Loop or hand off

```
Edit another section? (number 1-6 or name)

Or move on:
   /approve-database     Lock and unlock /build-infrastructure.
   exit                  Finish review.
```

Never auto-trigger.

---

## Rules

- Templates read-only.
- One section per edit.
- Mermaid `erDiagram` must remain syntactically valid after Section 6 edits.
