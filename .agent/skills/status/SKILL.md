---
name: status
description: Read state/SESSION-STATE.md and print the current pipeline stage, what artifacts exist, and the next valid commands. Pure read-only — never modifies any file. Use whenever the user asks "where am I", "what's next", or runs the `/status` slash command.
---

# Status — Pipeline Stage Reporter

A read-only skill. Reads `state/SESSION-STATE.md`, prints a
clean summary of where the project is in the foundations pipeline,
what's been done, and what command the user can run next.

## Manual-edit detection (REPORT ONLY — read-only skill)

This skill never writes. But it must still detect drift and surface it
to the user as part of the status output.

For each artifact in the Artifacts list:
1. Compute current SHA-256 of the file on disk (if it exists).
2. Compare to stored hash.
3. If different, include a warning line in the output:
   ```
   ⚠ Manual edit detected: <file>
     stored sha256: <stored>
     current sha256: <current>
     Run /review-<name> or /approve-<name> to accept and bump version.
   ```

Never bump versions, append audit log entries, or modify any file from
this skill. Drift acceptance is the responsibility of the next
write-skill the user runs.

---


## When this skill runs

- User runs `/status`
- User asks any of: "where am I", "what's next", "what stage", "what's done"
- Any other skill wants to remind the user of the next step

## Inputs

- `state/SESSION-STATE.md` (read-only)

## Outputs

A chat message in this format:

```
**Project:** <slug>
**Stage:** <STAGE_NAME>
**Last action:** <last skill name> at <timestamp>

**Artifacts**
- [x] Project Brief — v1.1, approved 2026-04-28
- [x] Scope of Work — v1.0, draft
- [ ] System Architecture — not started
- [ ] Database Diagram — not started
- [ ] Infrastructure Diagram — not started

**Next available commands**
- /review-scope-of-work <section>   (request edits to a SoW section)
- /approve-scope-of-work            (lock the SoW, unlock diagrams)

**Resume hint:** <one-line hint from the file>
```

## Behavior rules

1. **Read-only.** Never write to `SESSION-STATE.md` or any other file.
2. **No project loaded** (file missing or `Stage: INIT`): print
   > "No active foundations session. Run `/start-project` to begin."
3. **Always show next commands based on Stage** using this lookup:

| Stage | Next valid commands |
|-------|---------------------|
| INIT | `/start-project` |
| INTERVIEW | (continue answering — interview is in progress) |
| BRIEF_DRAFT | `/review-brief <section>`, `/approve-brief` |
| BRIEF_APPROVED | `/build-scope-of-work`, `/review-brief <section>` (re-opens) |
| SOW_DRAFT | `/review-scope-of-work <section>`, `/approve-scope-of-work` |
| SOW_APPROVED | `/build-architecture`, `/review-scope-of-work <section>` (re-opens) |
| ARCHITECTURE_DRAFT | `/review-architecture`, `/approve-architecture` |
| ARCHITECTURE_APPROVED | `/build-database`, `/review-architecture` (re-opens) |
| DATABASE_DRAFT | `/review-database`, `/approve-database` |
| DATABASE_APPROVED | `/build-infrastructure`, `/review-database` (re-opens) |
| INFRASTRUCTURE_DRAFT | `/review-infrastructure`, `/approve-infrastructure` |
| INFRASTRUCTURE_APPROVED | (transitioning to COMPLETE — usually shown as COMPLETE immediately) |
| COMPLETE | "All 5 documents approved. Foundations complete." |

4. **Reversibility note:** when an `*_APPROVED` stage is shown, always
   include the matching `/review-*` command as a valid next step so the
   user knows they can re-open if needed.
5. **Tone.** Concise. No bullet points beyond what's shown above. No
   commentary. Output the block, end.

## Quality gates

- Output uses the exact section headers shown above (`**Project:**`,
  `**Stage:**`, etc.) so other skills can parse it if needed.
- Stage name printed in CAPS to match the file.
- Timestamps preserved as written in the file (don't reformat).
- File path of any artifact is omitted from the chat output (keep it
  visually clean) — but the artifact name and version are shown.

## Edge cases

- **`SESSION-STATE.md` exists but is malformed** (missing `Stage:` line):
  print "Session file is corrupted. Reset by deleting `state/SESSION-STATE.md` and running `/start-project`."
- **Stage value not in the valid enum:** treat as malformed.
- **Audit log empty:** still proceed; just omit "Last action" line.
