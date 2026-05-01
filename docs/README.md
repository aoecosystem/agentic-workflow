# docs/

Reference material that complements the top-level docs (`README.md`,
`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`).

## Files

| File | Use when |
|---|---|
| `BLOCKER-PLAYBOOK.md` | A build task is `blocked` and you need a deterministic recovery path. |
| `TROUBLESHOOTING.md` | Something behaves unexpectedly — check the FAQ before opening an issue. |
| `prompts/` | Reusable manual-paste prompts for senior-level review (audit tasks, refine scope, debug blocker, generate release notes). |

## What goes elsewhere

- **Project drop zone for foundations docs** → `inputs/` (not here).
- **Per-project state** → `state/SESSION-STATE.md`, `state/SCOPE.md`, `state/TASKS.md`.
- **Curated cross-session knowledge** → `memory/`.
- **Filled deliverables** → `deliverables/scope-of-work/`, `deliverables/architecture/`, `deliverables/`.

## Adding a new doc

If it's:
- A **playbook** for a recurring agent procedure → put it here flat (no subfolder).
- A **manual prompt** for the user → `docs/prompts/<NAME>.md`.
- An **example walkthrough** → put it here flat, named `EXAMPLE-<flow>.md`.
- **User-facing how-to** → extend the main `README.md` instead (single source of truth).
