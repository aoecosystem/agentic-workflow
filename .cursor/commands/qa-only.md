---
description: Run the QA skill on every in-review task (no Builder activity)
---

Run the `qa` skill on every task currently in `in-review`. Verify acceptance criteria, lint, typecheck, tests, design fidelity (for UI tasks with Figma refs), security, and observability. Approve (`done`) or reject (`needs-fix`) with file/line-specific notes. Do not start new builds. $ARGUMENTS
