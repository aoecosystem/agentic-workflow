# Contributing

Thanks for improving the agentic-workflow template. This guide describes how
to make changes safely without breaking the agent contract that drives
parallel Builders, the QA gate, and the memory layer.

---

## Golden rules

1. **Never break trigger phrases.** Every phrase in `AGENTS.md` is part of the
   public contract. Add new triggers freely; do not rename or remove existing ones.
2. **Status transitions are sacred.** Do not introduce new task statuses or
   change existing transitions without a major version bump.
3. **Single-writer principle.** Only the listed writer agent updates a given
   file or section.
4. **Memory edits go through QA.** `ARCHITECTURE.md`, `PATTERNS.md`, and
   `DECISIONS.md` are written only by QA after a task moves to `done`.

---

## Common change types

### Adding a new skill

1. Create `.claude/skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`).
2. If the skill is user-triggered, add a slash command at `.claude/commands/<name>.md`.
3. Add the trigger phrase to the table in `AGENTS.md` and `CLAUDE.md`.
4. Update `README.md` file map and `CHANGELOG.md`.

### Adding a new memory file

1. Add it under `memory/`.
2. Document its writer in `CLAUDE.md`.
3. Update the reading-order list in `AGENTS.md` so agents read it at session start.

### Adding documentation

- User-facing how-to → `docs/`
- Agent operational playbook → `docs/prompts/`
- Architecture-style profiles → `deliverables/architecture/styles/`

---

## Pre-merge checklist

- [ ] `AGENTS.md` and `CLAUDE.md` triggers and reading order match.
- [ ] No status transitions, slash commands, or skill names were renamed.
- [ ] `CHANGELOG.md` updated with the change under the new version.
- [ ] If a file moved, every reference to it across `README.md`, `AGENTS.md`,
      `CLAUDE.md`, skill files, and other docs is updated.
- [ ] Examples and snippets in `memory/PATTERNS.md` still compile / lint.

---

## What a "minor" PR looks like

Adding a troubleshooting doc:

```
docs/TROUBLESHOOTING-<topic>.md                # new file
README.md                                      # add link in file map
CHANGELOG.md                                   # entry under the new version
```

Three files, no behavior change, zero risk.

## What a "major" PR looks like

Renaming `parse-scope` to `plan-tasks`:

```
.claude/skills/parse-scope/                    # rename
.claude/commands/parse-scope.md                # rename
AGENTS.md                                      # update triggers + tables
CLAUDE.md                                      # update triggers + tables
README.md                                      # update everywhere
docs/**                                        # update every reference
CHANGELOG.md                                   # major version bump entry
```

Always avoid major changes unless the new name materially clarifies the workflow.

---

## Testing your change

Manual check before opening a PR:

```bash
# 1. Verify skills are still discoverable
ls .claude/skills/

# 2. Verify trigger tables still align
grep -A 1 'Trigger phrases' AGENTS.md CLAUDE.md

# 3. Verify no broken doc links
grep -rE 'docs/[A-Za-z0-9_/-]+\.md' README.md AGENTS.md CLAUDE.md docs/
```

If any step surfaces a broken reference, fix it before merging.
