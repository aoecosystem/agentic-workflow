---
name: approve-build
description: Lock the completed build and transition Stage from BUILD_COMPLETE to BUILD_APPROVED. Verifies all tasks done (no blocked, no needs-fix), QA notes resolved, no orphan files in apps/. Updates SESSION-STATE/SESSION-STATE.md, appends audit log. Trigger on `/approve-build`.
---

# Skill: approve-build

**Trigger:** `/approve-build`

**Purpose:** Run the build quality gate and lock the completed build.
Unlocks `/verify-build` (final lint + types + tests gate).

---

## Manual-edit detection (RUN FIRST)

Compute SHA-256 of every artifact in `SESSION-STATE/SESSION-STATE.md` Artifacts
list (HTMLs + state files + apps/ files). Compare to stored hashes. On
drift, halt and ask user before proceeding (per AGENTS.md Manual Edit
Protocol).

---

## Stage gate

1. Read `SESSION-STATE/SESSION-STATE.md`. Locate `Stage:`.
2. If `Stage` is not `BUILD_COMPLETE`, refuse:
   > "Approve is only valid from `BUILD_COMPLETE`. Current: `<STAGE>`.
   > Run `/status` for next valid commands. To reach `BUILD_COMPLETE`,
   > the build must finish all tasks."
   Leave Stage unchanged.

---

## Quality gate (BLOCKING)

Read `SESSION-STATE/TASKS.md` and verify:

1. **All tasks `done`.** No `pending`, `in-progress`, `in-review`,
   `needs-fix`, or `blocked` tasks remain.
2. **No QA red flags.** No tasks have unresolved QA notes.
3. **All acceptance criteria checked.** Every `[ ]` is now `[x]`.
4. **Code in `../apps/` matches architecture style.** Folder structure
   in apps/ follows `CONTEXT/architecture-styles/<style>.md` pattern.
5. **No orphan files in apps/.** Every file in apps/ traces back to a
   task in TASKS.md (no rogue files).
6. **No empty modules.** Every service/module folder in apps/ contains
   actual code, not just placeholder files.

If any fails, list every failing item, leave Stage at `BUILD_COMPLETE`,
recommend `/show-status` to see open tasks or rollback.

---

## Transition

1. Update `SESSION-STATE/SESSION-STATE.md`:
   - `Stage:` → `BUILD_APPROVED`
   - `Last skill:` → `approve-build`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /verify-build for final lint + types + tests gate.`
2. Append audit log:
   ```
   <ISO>  approve-build  BUILD_COMPLETE → BUILD_APPROVED  <N> tasks done, <M> files in apps/
   ```

---

## Confirm + hand off

```
Build approved. All <N> tasks done.

Next valid commands:

  /verify-build
    Run project-wide lint + types + tests + security + observability.

  /show-status
    Inspect final task report.
```

Stop. Do NOT auto-trigger `/verify-build`.

---

## Rules

- Read-only on TASKS.md and apps/ during approval.
- Never auto-advance.
- Quality gate failures listed explicitly per item.
