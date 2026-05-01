---
description: Run the brief quality gate and lock the brief. Transitions Stage from BRIEF_DRAFT to BRIEF_APPROVED.
---

Run the `approve-brief` skill. Read `SESSION-STATE.md` and refuse
unless Stage is `BRIEF_DRAFT`. Verify the quality gate: all 13
sections present, no raw `{{...}}` placeholders, slug + cover match.
On success, transition Stage to `BRIEF_APPROVED`, append audit log,
and present `/build-scope-of-work` as the next command. On failure,
list every failing item and leave Stage at `BRIEF_DRAFT`.

Never auto-trigger `/build-scope-of-work`.
