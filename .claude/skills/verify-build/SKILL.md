---
name: verify-build
description: Run project-wide verification on the approved build. Lint, typecheck, unit + integration tests, security audit, observability checks. Transitions Stage from BUILD_APPROVED to VERIFIED on success. Refuses if any gate fails — outputs specific failures to fix. Trigger on `/verify-build`.
---

# Skill: verify-build

**Trigger:** `/verify-build`

**Purpose:** Run project-wide verification on the build in `../apps/`.
On success, transition Stage to `VERIFIED`. On failure, list the
specific gates that failed.

---

## Manual-edit detection (RUN FIRST)

Compute SHA-256 of files in apps/ that were last touched by the build.
Compare to stored hashes. On drift, halt and ask user before proceeding.

---

## Stage gate

1. Read `SESSION-STATE/SESSION-STATE.md`. Locate `Stage:`.
2. If `Stage` is not `BUILD_APPROVED`, refuse:
   > "Verify is only valid from `BUILD_APPROVED`. Current: `<STAGE>`.
   > Run `/approve-build` first (after build completes)."
   Leave Stage unchanged.

---

## Verification gates (ALL BLOCKING)

Run these against `../apps/<sub-app>/` (or each microservice for
microservices architecture):

### 1. Lint

- Tool detection (in order of preference per stack):
  - **TS / JS:** **Biome** (`biome check`) is the default since v2.2. Fall back to ESLint + Prettier only if the SoW Phase 6 explicitly picked them OR `.eslintrc*` exists without `biome.json`.
  - **Python:** Ruff (default) or Pylint / Flake8.
  - **Go:** `golangci-lint`.
  - **Rust:** `cargo clippy`.
  - **Kotlin:** `ktlint`.
  - **Swift:** `SwiftLint`.
- Pass criteria: zero errors. Warnings only if pre-existing and
  unrelated to recent changes.
- Failure: list every error with file + line.

### 2. Typecheck

- Tool: `tsc --noEmit` / `mypy --strict` / equivalent
- Pass criteria: zero type errors.
- Failure: list every type error with file + line.

### 2b. Native build (NO TYPECHECK-ONLY VERIFICATION)

Typecheck is necessary but not sufficient. The project must produce a
runnable build artifact, not just compile clean.

- Tool: whichever the project declares (`npm run build`, `next build`,
  `cargo build --release`, `go build ./...`, `npx expo export ...`,
  `python -m build`).
- Pass criteria: exit 0, output artifact exists, no module-resolution
  or runtime errors during build.
- For services with an entry point, also run a 1-second smoke start
  (`node dist/<entry>` / `python -m <entry> --help`) and check exit
  status. Crash on import = fail.
- Failure: print the build command's stderr tail (last 30 lines) and
  the missing/invalid artifact path.

If the project declares no build command, halt with:
```
ERROR: the 5 deliverable HTMLs Sec 3 (Tech stack) does not declare a build
command. /verify-build cannot certify a project that cannot build.
Add the build command and re-run.
```

### 2c. Deferred-work scan (NO "WE'LL FIX LATER" CERTIFICATIONS)

Scan the build tree for unlinked deferred-language markers introduced
by the agent during this build. Reject verification if any are found
without a linked follow-up task.

Patterns rejected (without a `TASK-XXX` reference on the same or
adjacent line):

- `TODO` / `FIXME` / `HACK` / `XXX` in any file under `../apps/`
- `@ts-ignore` / `@ts-expect-error` with no reason comment
- Acceptance-criteria checkboxes whose code is behind a feature flag
  defaulted to `false`

Allowed:
- `// TODO(TASK-099): wire live API` — links to a follow-up.
- `// @ts-expect-error – upstream type fixed in TASK-101` — has reason.

Failure output:
```
Deferred-work scan: ✗ 4 unlinked markers
  apps/web/src/auth.ts:12   TODO: handle refresh — no task link
  apps/api/src/booking.ts:88  @ts-ignore — no reason / no task link
  apps/mobile/screens/home.tsx:45  FIXME: layout — no task link
  apps/api/src/payment.ts:201  // good enough for now
```

This is a hard gate. Even one unlinked marker fails the verification.

### 3. Unit tests

- Pass criteria: every unit test green. Coverage ≥ 70% on critical paths.
- Failure: list failing tests with names.

### 4. Integration tests

- Pass criteria: every integration test green.
- Failure: list failing tests with names + error excerpt.

### 5. Security audit

- `npm audit` / `pip-audit` / `cargo audit` — no high or critical CVEs.
- Secrets scan — no `.env`, no API keys, no private keys checked in.
- Auth boundary check — every protected route has `requireAuth` middleware.

### 6. Observability checks

- Structured logging on every error path.
- Correlation IDs threaded through requests.
- Metrics emitted on key transitions (login, payment, etc.).
- Tracing spans on cross-service calls (microservices/serverless only).

---

## Reporting

Print a verification report:

```
Verification report — <slug> v<version>

  Lint:           ✓ 0 errors / <N> warnings
  Typecheck:      ✓ 0 errors
  Native build:   ✓ <command> exit 0 / artifact: <path>
  Deferred scan:  ✓ 0 unlinked TODO / FIXME / @ts-ignore
  Unit tests:     ✓ <N>/<N> passed (<M>% coverage)
  Integration:    ✓ <N>/<N> passed
  Security:       ✓ 0 CVEs / 0 secrets / auth boundaries verified
  Observability:  ✓ logging / metrics / tracing all wired

Result: VERIFIED
```

If any gate fails, list specifics:

```
Verification FAILED:

  Lint:           ✗ 3 errors
    - apps/web/src/auth.ts:42  no-unused-vars
    - apps/web/src/booking.ts:108  prefer-const
    - apps/api/src/payment.ts:55  consistent-return

  Typecheck:      ✗ 1 error
    - apps/api/src/booking.ts:67  Type 'string' is not assignable to 'BookingStatus'

  Unit tests:     ✗ 2/45 failed
  ...

Stage stays at BUILD_APPROVED. Fix and re-run /verify-build.
```

---

## Transition (on success only)

1. Update `SESSION-STATE/SESSION-STATE.md`:
   - `Stage:` → `VERIFIED`
   - `Last skill:` → `verify-build`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /package-release for final delivery, OR deploy directly from ../apps/.`
2. Append audit log:
   ```
   <ISO>  verify-build  BUILD_APPROVED → VERIFIED  lint+types+nativebuild+deferred+tests+security+observability all pass
   ```

---

## Confirm + hand off

```
Build verified. All gates passed.

Next valid commands:

  /package-release
    Generate release notes + bundle for deployment.

  (or deploy directly from ../apps/<sub-app>/)
```

Stop.

---

## Rules

- Read-only — verification never modifies code.
- Every gate is BLOCKING — no skip, no shortcut.
- Failure must be specific (file + line where possible).
