---
description: Smart router — reads state/SESSION-STATE.md and routes to the right next action based on current Stage (works in BOTH docs and build phases).
---

Run the `start-project` skill. Read `state/SESSION-STATE.md` first.

If Stage is `INIT` (or file missing), walk the user through the 13-section
brief interview (foundations docs phase). Save brief and transition to
`BRIEF_DRAFT`.

If Stage is `INTERVIEW`, resume from the last captured answer.

For any other Stage (docs phase or build phase), inspect Stage and tell
the user the right next valid command (use `/status` internally if helpful).

Never auto-trigger the next step — the user must run it explicitly.
