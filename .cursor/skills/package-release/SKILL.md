---
name: package-release
description: Final stage. Generate release notes from the verified build, bundle artifacts (optional), and transition Stage from VERIFIED to READY_TO_DEPLOY. Reads state/SCOPE.md, state/TASKS.md, deliverables/scope-of-work/<slug>-sow.html. Writes a polished release note. Trigger on `/package-release`.
---

# Skill: package-release

**Trigger:** `/package-release`

**Purpose:** Wrap up the build. Generate release notes, optionally
bundle deployment artifacts, transition Stage to `READY_TO_DEPLOY`.

---

## Manual-edit detection (RUN FIRST)

Compute SHA-256 of all artifacts. Compare to stored hashes. On drift,
halt before proceeding.

---

## Stage gate

1. Read `state/SESSION-STATE.md`. Locate `Stage:`.
2. If `Stage` is not `VERIFIED`, refuse:
   > "Package is only valid from `VERIFIED`. Current: `<STAGE>`.
   > Run `/verify-build` first."

---

## Generate release notes

Read:
- `state/SCOPE.md` — feature list
- `state/TASKS.md` — completed task summary
- `deliverables/scope-of-work/<slug>-sow.html` — phases + acceptance criteria

Generate `state/RELEASE-NOTES-v<version>.md` with sections:

```
# Release v<version> — <project name>

## Summary
<one-paragraph overview pulled from SCOPE.md>

## Features delivered
<list grouped by service/module, pulled from completed tasks>

## Tech stack
<from STACK-GUIDANCE.md>

## Deployment notes
- Architecture style: <monolith/hybrid/microservices/serverless>
- Code path: ../apps/<sub-app>/
- Required infrastructure: <pulled from infrastructure deliverable>
- Required secrets: <list of env vars needed>
- Build command: <e.g. npm run build>
- Deploy command: <e.g. docker build + push>

## Quality gates passed
- ✓ Lint
- ✓ Typecheck
- ✓ Unit tests (<coverage>%)
- ✓ Integration tests
- ✓ Security audit
- ✓ Observability wired

## Manual edits in this build
<from audit log filtered to manual-edit entries>

## Acceptance summary
<final task counts: <N> done, 0 pending/blocked>
```

Show the user the draft release notes inline. Ask: *"Save? (yes / edit / cancel)"*

On `yes`:
1. Write `state/RELEASE-NOTES-v<version>.md`
2. Update `state/SESSION-STATE.md`:
   - `Stage:` → `READY_TO_DEPLOY`
   - `Last skill:` → `package-release`
   - `Last update:` → ISO timestamp
   - Artifacts list: mark release notes
3. Append audit log:
   ```
   <ISO>  package-release  VERIFIED → READY_TO_DEPLOY  release notes v<version> generated
   ```

---

## Hand off

```
Release packaged. Project is READY_TO_DEPLOY.

Final artifacts:
  ✓ ../apps/<sub-app>/                      (verified code)
  ✓ deliverables/                            (5 HTMLs)
  ✓ state/SCOPE.md, state/TASKS.md           (parsed)
  ✓ state/RELEASE-NOTES-v<version>.md        (just generated)

Deploy from ../apps/ using your platform of choice.
```

Stop. The pipeline is complete. The agent does NOT deploy automatically.

---

## Rules

- Read-only on apps/ — packaging never modifies code.
- Release notes are markdown, polished, client-ready.
- Single-source-of-truth: pull facts from existing artifacts, never invent.
