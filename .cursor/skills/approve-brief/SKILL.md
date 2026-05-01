---
name: approve-brief
description: Lock the Project Brief and transition the pipeline from BRIEF_DRAFT to BRIEF_APPROVED. Verifies the brief quality gate (all 13 sections present, no raw `{{...}}` placeholders left), updates `state/SESSION-STATE.md`, appends an audit log line, and prints the next valid commands. Trigger on `/approve-brief`. Refuses if the gate fails — reports what's missing.
---

# Skill: approve-brief

**Trigger:** `/approve-brief`

**Purpose:** Run the brief quality gate, then transition the pipeline
stage from `BRIEF_DRAFT` to `BRIEF_APPROVED`. Unlocks
`/build-scope-of-work`.

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

1. Read `state/SESSION-STATE.md`. Locate `Stage:` and `Slug:`.
2. If `Stage` is not `BRIEF_DRAFT`, refuse with the uniform message:
   > "Approve is only valid from `BRIEF_DRAFT`. Current stage: `<STAGE>`.
   > Run `/status` to see the next valid commands. To reach
   > `BRIEF_DRAFT`, run `/start-project` (complete the interview to reach BRIEF_DRAFT)."
   Leave Stage unchanged.
3. Otherwise proceed.

---

## Quality gate (BLOCKING)

Read `deliverables/brief/<slug>-brief.html` and verify:

1. All 13 sections are present and have content (real value or
   explicit `TBD`).
2. No raw unfilled placeholders remain — search for any
   `<span class="ph">{{...}}</span>` whose inner text still starts with
   `{{`. Every placeholder must have been replaced or intentionally
   marked `TBD`.
3. Slug in the file matches the slug in `SESSION-STATE.md`.
4. Cover section shows the project name (cover-sub is not literal
   `{{PROJECT_NAME}}`).

If any check fails, list **every** failing item to the user, leave
the stage at `BRIEF_DRAFT`, and recommend `/review-brief <N>` to fix.
Do NOT transition.

If all checks pass, continue.

---

## Transition

1. Update `SESSION-STATE.md`:
   - `Stage:` → `BRIEF_APPROVED`
   - `Last skill:` → `approve-brief`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /build-scope-of-work to generate the SoW.`
   - Artifacts list: mark project-brief as approved with the current
     version and today's date.
2. Append a line to the audit log:
   ```
   <ISO>  approve-brief  BRIEF_DRAFT → BRIEF_APPROVED  v<X> locked
   ```

Always overwrite the whole `SESSION-STATE.md` (small, structured).
The audit log is the only append-only section.

---

## Confirm + hand off

Print:

```
Brief approved. v<X> locked.

Next valid commands:

  /build-scope-of-work
    Generate the Scope of Work from the approved brief.

  /review-brief <section>
    Re-open the brief for further edits (reverts to BRIEF_DRAFT).
```

Stop. Do NOT auto-trigger anything.

---

## Rules

- Read-only on the brief HTML — never edit it during approval.
- Single source of truth for stage = `SESSION-STATE.md`.
- Never auto-advance to `/build-scope-of-work` — the user must run it.
- Quality gate failures are surfaced explicitly with file references.
