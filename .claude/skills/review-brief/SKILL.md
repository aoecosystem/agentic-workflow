---
name: review-brief
description: Iterative section-by-section editor for a previously filled Project Brief. Reads `SESSION-STATE/SESSION-STATE.md`, refuses unless Stage is BRIEF_DRAFT or BRIEF_APPROVED, lets the user pick a section, applies the change, bumps version, writes audit log. If Stage is BRIEF_APPROVED, this re-opens it back to BRIEF_DRAFT (reversibility). Trigger when the user says "/review-brief", "review the brief", "edit my brief", "update brief". Do NOT trigger if no filled brief exists.
---

# Skill: review-brief

**Trigger:** `/review-brief <section>` or "review the brief" / "edit my brief"

**Purpose:** Let the user iteratively edit specific sections of a previously
filled Project Brief without restarting the interview. Each save bumps the
file version and appends an audit log line in `SESSION-STATE.md`.

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


## Stage gate (read SESSION-STATE.md first)

1. Read `SESSION-STATE/SESSION-STATE.md`. Locate the `Stage:` value.
2. If `Stage:` is not one of `BRIEF_DRAFT` or `BRIEF_APPROVED`, refuse:
   > "Brief review is only valid in stages BRIEF_DRAFT or BRIEF_APPROVED.
   > Current stage: `<STAGE>`. Run `/status` to see what's valid next."
3. If `Stage: BRIEF_APPROVED`, warn the user and confirm:
   > "The brief is currently approved. Reviewing will re-open it
   > (BRIEF_APPROVED → BRIEF_DRAFT). Downstream documents stay on disk
   > but should be re-built with `/build-scope-of-work` afterward to
   > pick up the change. Continue? (yes / no)"
   On `no`, stop. On `yes`, proceed.

---

## Pre-flight

1. From `SESSION-STATE.md` Header, get the active `Slug:`.
2. Open `DOCMENTS/<slug>-project-brief.html` and read it
   end-to-end so you know what's filled and what's `TBD`.
3. If the file does not exist, halt and tell the user to run
   `/start-project` first.

---

## Show section menu

Present the 13 sections as a numbered menu:

```
Which section do you want to edit?

   1. Project Basics
   2. Problem and Solution
   3. Platform
   4. Roles (Beyond Default)
   5. Business Features
   6. Business Process
   7. Business Model
   8. Integrations
   9. Special Requirements
   10. Out of Scope (Phase 1 / MVP)
   11. Design & Branding
   12. Timeline & Team
   13. Instructions for AI Agent

Reply with a number (1-13) or the section name.
```

If the user already provided a section number on the command line
(e.g. `/review-brief 6`), skip the menu and jump straight to that
section.

---

## Edit one section at a time

Once the user picks a section:

1. Read that section's current content from the filled HTML.
2. Show it inline as readable text (not raw HTML).
3. Ask: *"What would you like to change in this section?"*
4. Apply the change in memory:
   - Preserve all HTML structure and CSS classes — only edit content
     inside existing tags.
5. Show a one-paragraph diff summary:
   ```
   Section 6 — Business Process:
     - Renamed phase 4 from "PAYMENT" to "CHECKOUT"
     - Added a new "REFUND" alt-path row
   ```
6. Ask: *"Save this change? (yes / no / show me the section again)"*

Iterate within the chosen section until the user is satisfied.

---

## Special handling for Section 3.2 (Architecture style)

Section 3.2 is special — it's the architecture style choice
(`monolith` / `hybrid` / `microservices` / `serverless`). Changing it
invalidates downstream documents because they were generated against
the old style.

When the user picks Section 3 to edit:

1. Ask first which sub-section they want to change:
   - 3.1 Platform surfaces (mobile / web / API)
   - 3.2 Architecture style + communication style

2. If they pick **3.2**, before saving the change:
   a. Read `SESSION-STATE.md` Artifacts list. Find any artifact whose
      state is `*_APPROVED` or `*_DRAFT` AND that depends on the
      style (SoW, architecture, database, infrastructure HTMLs).
   b. If any exist, warn the user explicitly:

      > "Heads up — changing the architecture style will make these
      >  downstream documents stale:
      >    - <slug>-scope-of-work.html (SOW_APPROVED)
      >    - <slug>-system-architecture.html (ARCHITECTURE_DRAFT)
      >    - ...
      >
      >  These won't be deleted, but they were generated against the
      >  OLD style (`<old>`). To get documents that match the NEW
      >  style (`<new>`), you'll need to:
      >    1. /build-scope-of-work          (regenerates SoW)
      >    2. /build-architecture           (regenerates architecture)
      >    3. /build-database               (regenerates database)
      >    4. /build-infrastructure         (regenerates infrastructure)
      >
      >  Continue with the architecture style change? (yes / no)"

   c. On `yes`: apply the change, save, bump version, append audit log
      with the note `architecture style: <old> → <new>`.
   d. On `no`: cancel the edit, leave the brief unchanged.

3. If they pick **3.1**, proceed normally — platform changes don't
   invalidate the architecture style.

This warning prevents the silent-drift bug where a user changes
style but downstream documents still reflect the old architecture.

---

---

## Save and update state

On user confirmation:

1. Write the updated HTML back to `DOCMENTS/<slug>-project-brief.html`.
2. Bump the file version (in the cover-meta or version comment): e.g.
   `v1.0` → `v1.1`. Always increment minor by 1 per save.
3. Update `SESSION-STATE.md`:
   - Set `Stage: BRIEF_DRAFT` (if it was BRIEF_APPROVED, this is the
     re-open transition).
   - Set `Last skill: review-brief` and `Last update: <ISO timestamp>`.
   - Update the Artifacts list with the new version + draft status.
   - Append a line to the audit log:
     ```
     <ISO>  review-brief  <FROM> → BRIEF_DRAFT  section <N> revised, v<X> → v<Y>
     ```
4. Confirm to the user:
   ```
   Saved. Section <N> updated. Brief version v<NEW>.
   ```

---

## Loop or hand off

After save, re-show the section menu **plus** the next valid commands:

```
Edit another section?
   (reply with a number 1-13 or section name)

Or move on:

   /approve-brief
     Lock the brief and unlock /build-scope-of-work.

   exit
     Finish this review session.
```

If the user picks another section → loop.
If the user types `/approve-brief` or `exit` → stop. Do not auto-trigger.

---

## Rules

- Templates (`DOCMENTS/project-brief.html`) are
  read-only. Only the filled `<slug>-project-brief.html` is editable.
- One section per edit. Break it up if the user asks for changes in
  multiple sections.
- Always show the change summary before saving.
- Mark new unknowns as `TBD`, not made-up values.
- Always overwrite, never append (HTML is replaced atomically).
- Audit log in `SESSION-STATE.md` is append-only.
