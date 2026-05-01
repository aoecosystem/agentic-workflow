---
name: approve-infrastructure
description: Final approval — lock the Infrastructure Diagram and transition Stage from INFRASTRUCTURE_DRAFT to INFRASTRUCTURE_APPROVED, then immediately to COMPLETE. Verifies Mermaid topology compiles, all brief Section 8 integrations appear, providers selected for critical fields, environments listed. Updates `state/SESSION-STATE.md`, appends audit log, prints completion summary. Trigger on `/approve-infrastructure`.
---

# Skill: approve-infrastructure

**Trigger:** `/approve-infrastructure`

**Purpose:** Run infrastructure quality gate, transition to
`INFRASTRUCTURE_APPROVED`, then to `COMPLETE`. This is the final
approval in the foundations pipeline.

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
2. If `Stage` is not `INFRASTRUCTURE_DRAFT`, refuse with the uniform message:
   > "Approve is only valid from `INFRASTRUCTURE_DRAFT`. Current stage: `<STAGE>`.
   > Run `/status` to see the next valid commands. To reach
   > `INFRASTRUCTURE_DRAFT`, run `/build-infrastructure` (after the database is approved)."
   Leave Stage unchanged.

---

## Quality gate (BLOCKING)

Read `deliverables/infrastructure/<slug>-infrastructure.html` and the
approved brief + SoW. Verify:

1. **All 9 sections present and non-empty.**
2. **No raw unfilled placeholders in critical fields** (Section 2 providers,
   Section 3 DB / cache / storage providers, Section 5 integrations).
   Other fields may be marked `TBD` (with `<span class="ph">TBD ...</span>` or
   `<span class="ph">{{TBD ...}}</span>` — both forms acceptable for non-critical
   fields). Critical fields must have a concrete provider chosen — `TBD provider`
   is NOT acceptable for the database engine, primary CDN, or hosting compute.
3. **Cover-sub replaced.** Project name shown, not `{{PROJECT_NAME}}`.
4. **Environments coverage.** Section 1 lists at least Local, Dev,
   Staging, Production.
5. **Integration coverage.** Every integration from brief Section 8
   appears in Section 5 External Services AND as a node in Section 9
   topology diagram.
6. **Mermaid `flowchart` compiles.** Subgraphs balanced, arrows valid,
   `classDef` and `linkStyle` syntactically correct, all node IDs
   referenced exist.

If any check fails, list every failing item, leave Stage at
`INFRASTRUCTURE_DRAFT`, recommend `/review-infrastructure <N>`.

---

## Transition (DOUBLE)

This skill performs two transitions in sequence:

1. **First transition:** `INFRASTRUCTURE_DRAFT` → `INFRASTRUCTURE_APPROVED`.
   Append audit log:
   ```
   <ISO>  approve-infrastructure  INFRASTRUCTURE_DRAFT → INFRASTRUCTURE_APPROVED  v<X> locked
   ```

2. **Second transition (immediate):** `INFRASTRUCTURE_APPROVED` → `COMPLETE`.
   Update `SESSION-STATE.md`:
   - `Stage:` → `COMPLETE`
   - `Last skill:` → `approve-infrastructure`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Foundations complete. All 5 documents approved.`
   - Artifacts list: mark infrastructure as approved + final.
   Append audit log:
   ```
   <ISO>  approve-infrastructure  INFRASTRUCTURE_APPROVED → COMPLETE  all 5 documents approved
   ```

---

## Completion summary

Print a friendly summary of what was produced:

```
Foundations complete.

All 5 documents approved:

  ✓ Project Brief             deliverables/brief/<slug>-brief.html (v<X>)
  ✓ Scope of Work             deliverables/scope-of-work/<slug>-sow.html (v<X>)
  ✓ System Architecture       deliverables/architecture/<slug>-architecture.html (v<X>)
  ✓ Database Diagram          deliverables/database/<slug>-database.html (v<X>)
  ✓ Infrastructure Diagram    deliverables/infrastructure/<slug>-infrastructure.html (v<X>)

The foundations workflow is finished. The 5 HTMLs are ready to use
however you'd like — share with the team, print to PDF, hand off to
the build engine in a separate repo, etc.

Re-open any document with /review-<name>. Run /status anytime to see
the current state.
```

Stop. Do NOT auto-trigger anything. The project is done.

---

## Rules

- Read-only on infrastructure HTML during approval.
- Two-step transition (APPROVED → COMPLETE) happens atomically in one
  skill invocation.
- Single source of truth = `SESSION-STATE.md`.
- No file copies, no cross-repo writes.
