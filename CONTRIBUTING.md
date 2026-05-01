# Contributing

Thanks for improving the agentic-workflow template. This guide describes how
to make changes safely without breaking the agent contract that drives
parallel Builders, the QA gate, and the memory layer.

---

## Golden rules

1. **Never break trigger phrases.** Every phrase in `AGENTS.md` is part of the
   public contract. Add new triggers freely; do not rename or remove existing ones.
2. **Skills come in triplicate.** Every skill under `.claude/skills/` must
   have identical twins under `.cursor/skills/` (Cursor) and `.agent/skills/`
   (Antigravity). Verify byte-equality inline by reading each copy and comparing
   contents (or via SHA-256 / md5 hash). The rule is the verifier — no
   external script.
3. **Status transitions are sacred.** Do not introduce new task statuses or
   change existing transitions in `03-subagents.mdc` without a major version bump.
4. **Single-writer principle.** Only the listed writer agent updates a given
   file or section. See `07-concurrency.mdc`.
5. **Memory edits go through QA.** `ARCHITECTURE.md`, `PATTERNS.md`, and
   `DECISIONS.md` are written only by QA after a task moves to `done`.

---

## Common change types

### Adding a new skill

1. Create `.claude/skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`).
2. Run inline mirror verification (read each copy + compare) to mirror to `.cursor/skills/<name>/` and `.agent/skills/<name>/`
   (or copy by hand and verify with inline hash check).
3. If the skill is user-triggered, add a slash command at `.claude/commands/<name>.md`.
4. Add the trigger phrase to the table in `AGENTS.md` and `CLAUDE.md`.
5. Update `README.md` file map and `CHANGELOG.md`.

### Adding a new rule

1. Create the rule under `.cursor/rules/NN-<name>.mdc` with `alwaysApply: true`
   (canonical source for rules).
2. Run inline mirror verification (read each copy + compare) to mirror to `.agent/rules/` (Antigravity).
3. Mirror the rule's substance into the relevant section of `CLAUDE.md` and
   `GEMINI.md` if the override matters there.
4. Reference the rule in any skill that depends on it.

### Adding a new memory file

1. Add it under `memory/`.
2. Document its writer in the table inside `02-memory.mdc` and `CLAUDE.md`.
3. Update the reading-order list in `AGENTS.md` so agents read it at session start.

### Adding documentation

- User-facing how-to → `docs/guides/`
- Agent operational playbook → `docs/playbooks/`
- Reference material or worked example → `docs/reference/`

---

## Pre-merge checklist

- [ ] `.claude/skills/`, `.cursor/skills/`, `.agent/skills/` all in sync (inline hash check).
- [ ] `.cursor/rules/` and `.agent/rules/` in sync (inline hash check).
- [ ] `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` triggers and reading order match.
- [ ] No status transitions, slash commands, or skill names were renamed.
- [ ] `CHANGELOG.md` updated with the change under `[Unreleased]`.
- [ ] If a file moved, every reference to it across `README.md`, `AGENTS.md`,
      `CLAUDE.md`, skill files, and other docs is updated.
- [ ] Examples and snippets in `memory/PATTERNS.md` still compile / lint.
- [ ] `python3 scripts/update-task-counts.py` still runs cleanly when
      `state/TASKS.md` exists.

---

## What a "minor" PR looks like

Adding a `troubleshooting` doc:

```
docs/playbooks/TROUBLESHOOTING.md             # new file
README.md                                      # add link in file map
CHANGELOG.md                                   # entry under [Unreleased]
```

Three files, no behavior change, zero risk.

## What a "major" PR looks like

Renaming `parse-scope` to `plan-tasks`:

```
.claude/skills/parse-scope/                    # rename
.cursor/skills/parse-scope/                    # rename
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
ls .claude/skills/ .cursor/skills/

# 2. Verify trigger tables still align
grep -A 1 'Trigger phrases' AGENTS.md CLAUDE.md

# 3. Verify no broken doc links
grep -rE 'docs/[A-Za-z0-9_/-]+\.md' README.md AGENTS.md CLAUDE.md docs/

# 4. Verify the progress-table script still parses
python3 scripts/update-task-counts.py --dry-run 2>/dev/null || true
```

If any step surfaces a broken reference, fix it before merging.
