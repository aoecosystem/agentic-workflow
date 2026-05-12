---
description: Walk the user through a structured Q&A and auto-generate Project Brief + Scope of Work in inputs/. Use when no SOW exists yet.
---

Run the `scope-interview` skill. Walk through the section-by-section
interview (identity, vision, features, stack, constraints, design),
then derive both `inputs/<slug>-project-brief.md` and
`inputs/<slug>-scope-of-work.md` in markdown.

Output is markdown only — no HTML, no PDF — to keep token costs low.

After saving, tell the user to run `import docs` next.
