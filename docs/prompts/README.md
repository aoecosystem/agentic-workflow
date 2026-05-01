# prompts/

Reusable prompt snippets you can paste into Claude Code, Cursor, or any
chat with this repo's context loaded. Each prompt is a self-contained
markdown file with the prompt body and a short header explaining when to
use it.

## Index

| File | Use when |
|------|----------|
| [`REFINE-SCOPE.md`](REFINE-SCOPE.md) | `SCOPE.md` is filled but feels rough — you want a senior pass for clarity, missing detail, and consistency. |
| [`AUDIT-TASKS.md`](AUDIT-TASKS.md) | `TASKS.md` is generated and you want a sanity review before `start build` — coverage, dependency order, parallelism. |
| [`RELEASE-NOTES.md`](RELEASE-NOTES.md) | The build is `done` — you want a polished, client-facing release note from the completed task list. |
| [`DEBUG-BLOCKER.md`](DEBUG-BLOCKER.md) | A task is `blocked` and you need a focused diagnosis without restarting the whole build. |

## How to use

1. Open the prompt file you want.
2. Replace any `{...}` placeholders with your specifics.
3. Paste into chat. The agent has full repo context already.

Each prompt is intentionally short — they assume the agent has already
read `CLAUDE.md`, `SCOPE.md`, `TASKS.md`, and `memory/` at session start.
