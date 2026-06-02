---
description: Archive the current foundations session and reset Stage to INIT. Choose soft (keep HTMLs) or hard (move HTMLs to archive). Never permanently deletes data.
---

Run the `reset` skill. Read `SESSION-STATE/SESSION-STATE.md` to see
the current Slug + Stage + artifacts on disk. If Stage is already
`INIT`, short-circuit with "nothing to reset". Otherwise show the user
options 1 (soft), 2 (hard), 3 (cancel). On confirm, archive
`SESSION-STATE.md` to `SESSION-STATE/ARCHIVED/<slug>-<timestamp>.md`,
optionally move `<slug>-*.html` files to a sibling archive folder
(hard reset only), then overwrite `SESSION-STATE.md` with a fresh
INIT template carrying one audit log line:
`<ISO>  reset  <PREV_STAGE> → INIT  archived previous session as <filename>`.

Never auto-trigger `/start-project` after reset — let the user run it.
