---
name: approve-architecture
description: Lock the System Architecture and transition the pipeline from ARCHITECTURE_DRAFT to ARCHITECTURE_APPROVED. Verifies Mermaid compiles, every SoW service appears in the diagram, cover-sub replaced, no raw `{{...}}` placeholders. Updates `state/SESSION-STATE.md`, appends audit log, prints next valid commands. Trigger on `/approve-architecture`.
---

# Skill: approve-architecture

**Trigger:** `/approve-architecture`

**Purpose:** Run architecture quality gate, transition to
`ARCHITECTURE_APPROVED`, unlock `/build-database`.

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
2. If `Stage` is not `ARCHITECTURE_DRAFT`, refuse with the uniform message:
   > "Approve is only valid from `ARCHITECTURE_DRAFT`. Current stage: `<STAGE>`.
   > Run `/status` to see the next valid commands. To reach
   > `ARCHITECTURE_DRAFT`, run `/build-architecture` (after the SoW is approved)."
   Leave Stage unchanged.

---

## Quality gate (BLOCKING)

Read `deliverables/architecture/<slug>-architecture.html` and the
approved `<slug>-scope-of-work.html`. Verify:

1. **All 7 sections present and non-empty.**
2. **No raw unfilled placeholders.** A `<span class="ph">` is acceptable
   when its inner text starts with `TBD` or `{{TBD` — that's an explicit
   "to be decided" marker the user has acknowledged. Only unfilled blanks
   like `{{COLUMN_NAME}}`, `{{TODO}}`, `{{FILL_THIS}}`, or `{{PROJECT_NAME}}`
   fail the gate. Every placeholder is either replaced with a real value
   or explicitly marked `TBD`.
3. **Cover-sub replaced.** Cover shows the project name, not literal
   `{{PROJECT_NAME}}`.
4. **Service coverage.** Every service in SoW Phase 1.5 / Phase 2 also
   appears as a row in Section 2 Service Inventory AND as a node in
   Section 7 Mermaid diagram.
5. **Mermaid compiles.** The flowchart block has no syntax errors —
   matched subgraphs, valid arrow syntax, valid `classDef` and
   `linkStyle` lines, all node IDs referenced exist.
6. **Universal services intact.** S1-S6 still present in Section 2.

If any check fails, list every failing item, leave Stage at
`ARCHITECTURE_DRAFT`, recommend `/review-architecture <N>`.

---

## Transition

1. Update `SESSION-STATE.md`:
   - `Stage:` → `ARCHITECTURE_APPROVED`
   - `Last skill:` → `approve-architecture`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /build-database to draft the Database Diagram.`
   - Artifacts list: mark architecture as approved with version + date.
2. Append audit log:
   ```
   <ISO>  approve-architecture  ARCHITECTURE_DRAFT → ARCHITECTURE_APPROVED  v<X> locked
   ```

---

## Confirm + hand off

```
Architecture approved. v<X> locked.

Next valid commands:

  /build-database
    Draft the Database Diagram from the approved architecture + SoW.

  /review-architecture
    Re-open for further edits (reverts to ARCHITECTURE_DRAFT).
```

Stop. Do NOT auto-trigger.

---

## Rules

- Read-only on the architecture HTML during approval.
- Quality gate failures surfaced explicitly per item.
- Single source of truth = `SESSION-STATE.md`.
