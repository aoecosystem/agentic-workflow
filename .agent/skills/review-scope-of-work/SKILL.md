---
name: review-scope-of-work
description: Iterative section-by-section editor for a previously generated Scope of Work. Reads `state/SESSION-STATE.md`, refuses unless Stage is SOW_DRAFT or SOW_APPROVED, lets the user pick a phase, applies the change, bumps version, writes audit log. If Stage is SOW_APPROVED, this re-opens it back to SOW_DRAFT. Trigger when the user says "/review-scope-of-work", "review sow", "edit sow", "update scope of work". Do NOT trigger if no filled SoW exists.
---

# Skill: review-scope-of-work

**Trigger:** `/review-scope-of-work <phase>` or "review sow" / "edit sow"

**Purpose:** Let the user iteratively edit specific phases of the
Scope of Work without re-generating the whole document. Each save
bumps the file version and appends an audit log line.

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

1. Read `state/SESSION-STATE.md`. Locate the `Stage:` value.
2. If `Stage:` is not one of `SOW_DRAFT` or `SOW_APPROVED`, refuse:
   > "SoW review is only valid in stages SOW_DRAFT or SOW_APPROVED.
   > Current stage: `<STAGE>`. Run `/status` for next steps."
3. If `Stage: SOW_APPROVED`, warn:
   > "The Scope of Work is currently approved. Reviewing will re-open
   > it (SOW_APPROVED → SOW_DRAFT). Downstream documents (architecture,
   > database, infrastructure) stay on disk but should be re-built
   > afterward to pick up the change. Continue? (yes / no)"
   On `no`, stop. On `yes`, proceed.

---

## Pre-flight

1. From `SESSION-STATE.md` Header, get the active `Slug:`.
2. Open `deliverables/scope-of-work/<slug>-sow.html` and read it.
3. If the file does not exist, halt and tell the user to run
   `/build-scope-of-work` first.

---

## Show phase menu

Present the 10 phases (plus 5.5) as a numbered menu:

```
Which phase do you want to edit?

   1. Project Overview
   2. Project Modules
   3. Database Schemas
   4. API Endpoints
   5. Event-Driven Architecture
   5.5 Critical Flows
   6. Technology Stack
   7. UI/UX Foundation + Page Inventory
   8. Development Approach and Steps
   9. Folder Structures and CI/CD
   10. Extended Modules and Operational Specs

Reply with a number or the phase name.
```

If the user passed a phase argument (e.g. `/review-scope-of-work 7`),
skip the menu and jump straight to that phase.

---

## Edit one phase at a time

1. Read that phase's current content from the filled HTML.
2. Show it inline as readable text.
3. Ask: *"What would you like to change in this phase?"*
4. Apply the change in memory. Preserve every CSS class and table
   structure — only the content inside tags is edited.
5. Show a one-paragraph diff summary, e.g.:
   ```
   Phase 7 — UI/UX Foundation:
     - Added 3 new pages to Page Inventory (admin-roles, admin-audit-log, admin-billing)
     - Removed mobile rows from web-only pages
   ```
6. Ask: *"Save this change? (yes / no / show me the phase again)"*

---

## Save and update state

On confirmation:

1. Write updated HTML back to `deliverables/scope-of-work/<slug>-sow.html`.
2. Bump the version (`v1.0` → `v1.1`).
3. Update `SESSION-STATE.md`:
   - `Stage:` → `SOW_DRAFT` (re-opens if it was approved).
   - `Last skill:` → `review-scope-of-work`
   - `Last update:` → ISO timestamp.
   - Artifacts list: mark scope-of-work as draft with new version.
4. Append audit log line:
   ```
   <ISO>  review-scope-of-work  <FROM> → SOW_DRAFT  phase <N> revised, v<X> → v<Y>
   ```
5. Confirm:
   ```
   Saved. Phase <N> updated. SoW version v<NEW>.
   ```

---

## Loop or hand off

After save, show the phase menu again **plus**:

```
Or move on:

   /approve-scope-of-work
     Lock the SoW and unlock /build-architecture.

   exit
     Finish this review session.
```

Loop until the user picks `/approve-scope-of-work` or `exit`.
Never auto-trigger.

---

## Rules

- Templates (`scope-of-work-template.html`) are read-only.
- One phase per edit. Break up multi-phase requests.
- Always show the diff summary before save.
- Universal services S1-S6 must remain intact in Phase 2.
- Cover section never edited via this skill — only phase content.
