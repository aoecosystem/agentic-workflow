---
name: review-architecture
description: Iterative section-by-section editor for the System Architecture HTML. Reads `SESSION-STATE/SESSION-STATE.md`, refuses unless Stage is ARCHITECTURE_DRAFT or ARCHITECTURE_APPROVED, lets the user pick one of the 7 sections, applies the change, bumps version, writes audit log. If Stage is ARCHITECTURE_APPROVED, this re-opens it back to ARCHITECTURE_DRAFT. Trigger when the user says "/review-architecture", "review architecture", "edit architecture".
---

# Skill: review-architecture

**Trigger:** `/review-architecture <section>` or "edit architecture"

**Purpose:** Edit specific sections of the System Architecture without
regenerating the whole document. Each save bumps version and appends
audit log.

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

1. Read `SESSION-STATE/SESSION-STATE.md`. Locate `Stage:` and `Slug:`.
2. If `Stage` is not `DOCS_DRAFT` or `DOCS_DRAFT`:
   > "Architecture review is only valid in stages ARCHITECTURE_DRAFT
   > or ARCHITECTURE_APPROVED. Current stage: `<STAGE>`."
3. If `Stage: DOCS_DRAFT`, warn and confirm re-open:
   > "Architecture is currently approved. Reviewing will re-open it
   > (ARCHITECTURE_APPROVED → ARCHITECTURE_DRAFT). Downstream documents
   > (database, infrastructure) stay on disk but should be re-built
   > afterward to pick up the change. Continue? (yes / no)"

---

## Pre-flight

1. Read `DOCMENTS/<slug>-system-architecture.html`. If it
   doesn't exist, halt and tell the user to run `/build-architecture`.

---

## Show section menu

```
Which section do you want to edit?

   1. Architecture Overview
   2. Service Inventory
   3. Layered Architecture
   4. Data Flow
   5. Module Boundaries & Contracts
   6. Cross-Cutting Concerns
   7. Architecture — Visual Diagram

Reply with a number (1-7) or the section name.
```

If the user passed a section as argument (`/review-architecture 7`),
skip the menu.

---

## Edit one section

1. Read that section's current content.
2. Show inline as readable text.
3. Ask: *"What would you like to change?"*
4. Apply in memory. Preserve all CSS classes.
5. Show diff summary, e.g.:
   ```
   Section 7 — Visual Diagram:
     - Added S11 (Reviews) to flowchart
     - Connected S11 → S2 (Notification) via async event
   ```
6. Ask: *"Save? (yes / no / show me again)"*

---

## Save and update state

On confirmation:

1. Write updated HTML back to
   `DOCMENTS/<slug>-system-architecture.html`.
2. Bump version (`v1.0` → `v1.1`).
3. Update `SESSION-STATE.md`:
   - `Stage:` → `DOCS_DRAFT`
   - `Last skill:` → `review-architecture`
   - `Last update:` → ISO timestamp
   - Artifacts list: mark architecture as draft with new version.
4. Append audit log:
   ```
   <ISO>  review-architecture  <FROM> → ARCHITECTURE_DRAFT  section <N> revised, v<X> → v<Y>
   ```

---

## Loop or hand off

```
Edit another section?
   (number 1-7 or name)

Or move on:

   /approve-architecture     Lock and unlock /build-database.
   exit                      Finish review session.
```

Loop until `/approve-architecture` or `exit`. Never auto-trigger.

---

## Rules

- Templates are read-only.
- One section per edit.
- Always show diff summary before save.
- Section 7 changes must keep the Mermaid block syntactically valid.
- Universal services S1-S6 cannot be removed from Section 2.
