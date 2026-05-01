---
name: reset
description: Archive the current foundations session and reset Stage to INIT, ready to start a brand-new project. Asks the user to choose between soft reset (archive `SESSION-STATE.md` only, keep `<slug>-*.html` files on disk) or hard reset (also move all filled HTMLs into the archive folder). Always preserves audit trail in `state/archived/` — never permanently deletes data. Triggers: "/reset", "reset project", "start over", "clear state".
---

# Skill: reset

**Trigger:** `/reset` or "reset project" / "start over" / "clear state"

**Purpose:** Cleanly archive the current foundations session and reset
`Stage:` to `INIT`, ready to start a brand-new project. Always preserves
the audit trail by moving (never deleting) into `state/archived/`.

---

## Special note: this skill does NOT run Manual-edit detection

Most artifact-touching skills run hash-drift detection FIRST (per
AGENTS.md → Manual Edit Protocol). `/reset` is a meta operation that
intentionally discards / archives current state — bumping versions
would be pointless. Instead, this skill computes the current hash of
every artifact at archive time and records it in the archive metadata
so historical state stays auditable. If drift is detected, it just
prints a one-line note and archives the current on-disk content as-is.

---

## Pre-flight

1. Read `state/SESSION-STATE.md`. Extract:
   - Current `Slug:`
   - Current `Stage:`
   - The Artifacts list (which `<slug>-*.html` files exist on disk).
2. Compute SHA-256 of each existing artifact for the archive record.
3. Ensure `state/archived/` exists. Create if missing.
4. **If `Stage: INIT`** (nothing to reset), short-circuit:
   > "Already at INIT — nothing to reset. Run `/start-project` to begin."
   Then exit.

---

## Show plan and ask user

Print a summary:

```
Reset foundations workflow?

Current state:
  Slug:  <slug>
  Stage: <STAGE>

Artifacts on disk:
  ✓ deliverables/brief/<slug>-brief.html (<state>, v<X>)
  ✓ deliverables/scope-of-work/<slug>-sow.html (<state>, v<X>)
  ... (only show files that actually exist)

Choose:
  1. Soft reset — archive SESSION-STATE.md only; keep HTML files on disk
                  (good if you want to reference the project later)
  2. Hard reset — archive SESSION-STATE.md + move all <slug>-*.html files
                  to state/archived/<slug>-files-<timestamp>/
  3. Cancel — no changes

Reply: 1 / 2 / 3
```

---

## Option 1 — Soft reset

1. Copy `state/SESSION-STATE.md` →
   `state/archived/<slug>-<ISO-timestamp>.md`.
2. Append a footer to the archive file:
   ```
   <!-- Archived by /reset (soft) at <ISO> -->
   <!-- Hashes at archive time:
        <slug>-project-brief.html  sha256:<hash>
        <slug>-scope-of-work.html  sha256:<hash>
        ... -->
   ```
3. Overwrite `state/SESSION-STATE.md` with the empty INIT
   template (see "Empty INIT template" section below).
4. Print:
   > "Soft reset complete.
   >  Archive: `state/archived/<slug>-<timestamp>.md`
   >  HTML files left on disk under their original folders.
   >  Run `/start-project` to begin a new project."

---

## Option 2 — Hard reset

Steps 1-3 same as soft reset, plus:

4. Create `state/archived/<slug>-files-<ISO-timestamp>/`.
5. Move every `<slug>-*.html` that exists from:
   - `deliverables/brief/<slug>-brief.html`
   - `deliverables/scope-of-work/<slug>-sow.html`
   - `deliverables/architecture/<slug>-architecture.html`
   - `deliverables/database/<slug>-database.html`
   - `deliverables/infrastructure/<slug>-infrastructure.html`
   into the new archive folder. Use `mv` (move, not copy).
6. Print:
   > "Hard reset complete.
   >  State archive:  `state/archived/<slug>-<timestamp>.md`
   >  Files archive:  `state/archived/<slug>-files-<timestamp>/`
   >  Working folders cleaned.
   >  Run `/start-project` to begin a new project."

---

## Option 3 — Cancel

Print: *"Reset cancelled. State unchanged."* Exit. No file changes.

---

## Empty INIT template (used when overwriting SESSION-STATE.md)

The fresh `SESSION-STATE.md` matches the canonical schema in
`state/README.md`. Header / Stage machine block / Artifacts
list / etc. all reset to empty.

The new audit log gets exactly one line — the reset transition:

```
- <ISO>  reset  <PREV_STAGE> → INIT  archived previous session as <archive-filename>
```

This way the audit trail is continuous: the previous session is fully
preserved in the archive file, and the new session starts with a
record of where it came from.

Set:
- `Slug:` empty
- `Stage:` `INIT`
- `Last skill:` `reset`
- `Last update:` ISO timestamp
- `Resume hint:` `Run /start-project to begin a new project.`
- All Artifacts back to `(not yet built)` with no hashes.
- All Captured answers cleared.
- Interview progress cleared.

---

## Hand off

After printing the success message, stop. Do NOT auto-trigger
`/start-project` — let the user run it explicitly.

---

## Rules

- Never permanently delete files. Always archive via copy/move.
- Never run reset silently. Always confirm with options 1/2/3.
- Archive filenames use ISO 8601 timestamps in the format
  `<slug>-YYYY-MM-DDTHH-MM-SS.md` (colons converted to dashes for
  filesystem compatibility).
- Soft reset is the safe default — recommend it in the prompt.
- If the user pipes / passes `1` or `soft` as an argument
  (`/reset 1` or `/reset soft`), still confirm by re-printing the
  plan and waiting for explicit yes.
- The audit log of the previous session is preserved verbatim in
  the archive file — do not edit it.
- Files in `state/archived/` are never deleted by any skill.
