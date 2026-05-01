---
name: approve-scope-of-work
description: Lock the Scope of Work and transition the pipeline from SOW_DRAFT to SOW_APPROVED. Verifies the SoW quality gate (Page Inventory has at least one row per platform from brief, no raw `{{...}}` placeholders, universal services S1-S6 intact), updates `state/SESSION-STATE.md`, appends audit log, prints next valid commands. Trigger on `/approve-scope-of-work`. Refuses if the gate fails.
---

# Skill: approve-scope-of-work

**Trigger:** `/approve-scope-of-work`

**Purpose:** Run the SoW quality gate, then transition the pipeline
from `SOW_DRAFT` to `SOW_APPROVED`. Unlocks `/build-architecture`.

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
2. If `Stage` is not `SOW_DRAFT`, refuse with the uniform message:
   > "Approve is only valid from `SOW_DRAFT`. Current stage: `<STAGE>`.
   > Run `/status` to see the next valid commands. To reach
   > `SOW_DRAFT`, run `/build-scope-of-work` (after the brief is approved)."
   Leave Stage unchanged.

---

## Quality gate (BLOCKING)

Read `deliverables/scope-of-work/<slug>-sow.html` and `deliverables/brief/<slug>-brief.html`. Verify:

1. **All required phases present.** Phase 1 through Phase 10 all have
   non-empty bodies. Phase 5.5 (Critical Flows) is required only when
   brief Section 6 has processes — when present, it lives as a
   `<h1>Phase 5.5: Critical Flows</h1>` block between Phase 5 and Phase 6.
2. **No raw unfilled placeholders.** A `<span class="ph">` is acceptable
   when its inner text starts with `TBD` or `{{TBD` — that's an explicit
   "to be decided" marker the user has acknowledged. Only unfilled blanks
   like `{{COLUMN_NAME}}`, `{{TODO}}`, `{{FILL_THIS}}`, or `{{PROJECT_NAME}}`
   fail the gate. Every placeholder is either replaced with a real value
   or explicitly marked `TBD`.
3. **Page Inventory coverage.** Phase 7 Page Inventory has at least
   one row per platform listed in brief Section 3 (mobile, web-public,
   web-admin, etc.). A web-only project is exempt from mobile rows.
4. **Universal services intact.** Phase 2 still contains all 6
   universal service blocks (S1 Identity, S2 Notification, S3
   Messages, S4 Audit, S5 Analytics, S6 Payment).
5. **Slug + project name match.** Cover-sub shows the project name
   (not literal `{{PROJECT_NAME}}`); slug in artifacts list matches
   `SESSION-STATE.md`.

If any check fails, list every failing item, leave the stage at
`SOW_DRAFT`, and recommend `/review-scope-of-work <phase>` to fix.

If all checks pass, continue.

---

## Transition

1. Update `SESSION-STATE.md`:
   - `Stage:` → `SOW_APPROVED`
   - `Last skill:` → `approve-scope-of-work`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /build-architecture to draft the System Architecture.`
   - Artifacts list: mark scope-of-work as approved with version + date.
2. Append audit log:
   ```
   <ISO>  approve-scope-of-work  SOW_DRAFT → SOW_APPROVED  v<X> locked
   ```

---

## Confirm + hand off

Print:

```
Scope of Work approved. v<X> locked.

Next valid commands:

  /build-architecture
    Draft the System Architecture from the approved SoW.

  /review-scope-of-work <phase>
    Re-open the SoW for further edits (reverts to SOW_DRAFT).
```

Stop. Do NOT auto-trigger.

---

## Rules

- Read-only on SoW HTML during approval — never edit it here.
- Single source of truth for stage = `SESSION-STATE.md`.
- Never auto-advance to `/build-architecture`.
- Quality gate failures are surfaced explicitly per item.
