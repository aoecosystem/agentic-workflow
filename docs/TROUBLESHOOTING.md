# Troubleshooting

Common failure modes and how to recover. Read top-down — the
earliest-stage issues are at the top.

---

## Setup and discovery

### Skills are not discovered by Claude Code

**Symptom:** typing `/` doesn't show `/parse-scope`, `/start-build`, etc.
or the agent says "no skill matches that trigger".

**Likely cause:** the working directory is not the repo root, or skill
folder names were renamed.

**Fix:**
1. Confirm you opened the **`agentic-workflow/`** folder, not the
   parent project root.
2. Run `ls .claude/skills/` — there should be 33 folders.
3. Restart Claude Code so it re-scans.

---

## Importing source documents

### `import docs` says no input found

**Cause:** files are in the wrong folder, or have an unsupported
extension.

**Fix:**
- Drop your sources in `inputs/` (preferred) or `docs/` (legacy fallback).
- Supported: `.pdf`, `.docx`, `.doc` (with pandoc), `.txt`, `.md`, `.html`.
- Run `import docs` again.

---

### `import docs` extracted shallow content

**Symptom:** the resulting `SCOPE.md` is generic, with placeholders or
missing flow detail.

**Cause:** the source files lacked the structure to extract (a brief
that has no architecture, no endpoints, no models).

**Fix:** open `SCOPE.md` and complete the missing sections by hand.
The validator (manual SCOPE.md review) will tell you what's blocking.

---

## Task generation

### `parse scope` says preconditions fail

**Cause:** `SCOPE.md` has unfilled required sections.

**Fix:** run manual SCOPE.md review and fix every issue it reports. Then re-run
`parse scope`.

---

### `TASKS.md` looks wrong (missing scaffold, no DB task, etc.)

**Cause:** `SCOPE.md` did not declare the full architecture or stack.

**Fix:** as long as every task is still `pending`, it is **safe** to
edit `SCOPE.md` and rerun `parse scope`. Once any task is `in-progress`
or `done`, switch to `delta scope` to avoid clobbering history.

---

## UI / Figma flow

### A UI task immediately becomes `blocked` after `figma ingest`

**Common cause:** the linked Figma node is a device preview wrapper
(iPhone frame, status bar, notch) not the actual leaf content frame.

**Fix:**
1. Open the Figma file.
2. Pick the inner content frame, copy its `node-id`.
3. Update `MCP URL` for that task in `TASKS.md`.
4. Run `figma ingest` again, or `refresh mcp` to force a refetch.

---

### Codegen artifact in cache is stale after design change

**Cause:** TTL not yet expired, so Builder is reading the old version.

**Fix:** `refresh mcp` ignores the TTL and rewrites the cache.

---

## Build loop

### A task fails QA repeatedly

**Symptom:** `Attempts` grows toward `Max attempts` without resolution.

**Fix workflow:**
1. Read the latest `QA notes:` block — they should cite specific files
   and lines.
2. If notes are vague, that's a QA quality issue — surface to user.
3. If notes are clear but the Builder keeps missing the same point,
   the spec or pattern is probably ambiguous. Use
   `prompts/DEBUG-BLOCKER.md`.
4. When `Attempts >= Max attempts`, the task auto-blocks with type
   `attempt-budget-exhausted`. Choose: scope cut, increase budget,
   or cancel.

---

### Two Builders fight over the same file

**Symptom:** orchestrator safety-net error: "in-progress tasks share a
file".

**Cause:** `parse scope` did not split tasks correctly, or two features
declared the same file in `Files to create/modify`.

**Fix:**
1. Stop the build (`qa only` to drain in-review queue).
2. Edit `SCOPE.md` to clarify ownership.
3. `delta scope` to re-plan the affected tasks.

---

## Memory and references

### A skill complains it can't find `architecture.md`

**Cause:** old reference using lowercase. After the case-rename pass,
all canonical paths are uppercase: `memory/ARCHITECTURE.md`.

**Fix:** if it's a custom skill or doc you authored, search for the
lowercase form and update.

---

### `memory/STACK-GUIDANCE.md` is still the placeholder

**Cause:** `import docs` was never run, or finished without confirming.

**Fix:** rerun `import docs` and confirm the review draft, or pick a
template manually:

```bash
cp memory/stack-guidance-templates/NEXTJS-PRISMA-POSTGRES.md \
   memory/STACK-GUIDANCE.md
```

---

## Project layout

### Generated code ended up inside `agentic-workflow/`

**Cause:** the Builder didn't honor the `../apps/` rule. This is a
contract violation.

**Fix:**
1. `git status` — see what was created where it shouldn't be.
2. Move it to `../apps/<sub-app>/` manually.
3. Mark the task `needs-fix` with a note pointing to the
   `Project layout` section in `CLAUDE.md` and
   `docs/guides/PROJECT-LAYOUT.md`.
4. Builder retries.

---

## Last-resort recovery

If the workflow state feels corrupted:

```bash
# 1. Backup TASKS.md and memory/
cp TASKS.md TASKS.md.bak
cp -r memory memory.bak

# 2. Run sanity checks
#    - state freshness: read state/SESSION-STATE.md and confirm Stage matches expected
#    - task counts: run /show-status

# 3. If issues persist, stash everything except SCOPE.md and rerun
#    parse scope from a clean state.
```

Never delete `memory/DECISIONS.md` — it's your audit trail of why
things were built the way they were.
