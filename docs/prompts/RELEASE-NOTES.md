# Release notes from completed build

**When to use:** Every task in `TASKS.md` is `done`. You want a polished,
client-facing summary of what shipped.

---

## Prompt

```
The build is complete. Read TASKS.md and memory/.

Produce a release-notes document for {AUDIENCE: client / stakeholder /
internal team}. Tone: modern, professional, not technical-jargon-heavy
unless the audience is engineers.

Structure:

1. **Headline** — one sentence describing what was delivered.
2. **What's live** — group completed tasks by feature. For each feature:
     - one-line user-facing summary (what the user can now do)
     - notable technical decisions worth surfacing (auth choice,
       data model, integrations)
3. **What's deferred** — anything in 'Out of Scope' or any 'obsolete'
   task from delta-scope. Frame as deliberate, not missing.
4. **How to run it** — commands to start the project (read from
   memory/ARCHITECTURE.md and the apps/ scaffold). Include dev,
   build, and test commands.
5. **Known limitations** — anything noted in QA notes that should be
   communicated, but is not a bug.
6. **Next steps** — 2-3 suggested follow-ups based on deferred items
   and out-of-scope notes.

Length: roughly one page. No bullet-spam — use prose where it reads
better.

Output as a markdown file content I can save as
RELEASE-NOTES-{DATE}.md. Do not invent features that aren't backed by a
'done' task in TASKS.md.
```

## Variants

- For internal Slack/Discord summaries: ask for a 5-line version with
  emoji, link to the full notes.
- For changelog entries: ask the same prompt but constrained to the
  format used in your `apps/CHANGELOG.md`.
