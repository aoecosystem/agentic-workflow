---
name: qa
description: Verify a completed task against its acceptance criteria and verification gates (lint, typecheck, tests, acceptance parity, design fidelity for UI tasks, security, observability). Approve (mark done) or reject (mark needs-fix) with specific, actionable notes. Trigger when Orchestrator moves a task to in-review, when the user says "qa this task", "review TASK-XX", or "qa only". Never silently edits code; only writes verdicts and task status updates.
---

# Skill: QA

**Triggered by:** Orchestrator when a task moves to `in-review`

**Purpose:** Verify a completed task against its acceptance criteria, verification gates, and (for UI tasks) design fidelity checks. Approve (mark `done`) or reject (mark `needs-fix`) with specific, actionable notes.

---

## Steps

### Step 1 — Read the task

Read the full task block from `state/TASKS.md`:
- Task ID, title, feature group
- Files to create/modify
- Acceptance criteria (all checklist items)
- Product-context addendum when present: `User value`, `User flow`, `Functional notes`, `Edge cases`, `Test cases`
- QA notes written by the Builder

### Step 2 — Read relevant context

- `state/SCOPE.md` — the relevant feature section (screens, endpoints, models, NFRs)
- `memory/PATTERNS.md` — patterns that should have been followed
- `memory/DECISIONS.md` — decisions that constrain this task
- The MCP cache file for this feature if one exists (`memory/mcp-cache/{feature-slug}-*.md`)
- If task has `Design source: Figma`, `Codegen artifact`, `Visual baseline refs`, or `Plugin artifact refs`, also read those fields and linked artifacts.

### Step 3 — Run Gate 1: Lint

Run the project linter on all files listed in `Files to create/modify`.

- Zero errors: required.
- Warnings: flag any new warnings introduced by this task (pre-existing warnings are acceptable).
- If lint is not configured: note it, skip, record in QA notes.

### Step 4 — Run Gate 2: Typecheck

Run `tsc --noEmit` (or equivalent) on the full project.

- Zero type errors: required.
- Check for `@ts-ignore` or `as any` added by this task. Each must have a documented reason in a comment. If not: reject.

### Step 4b — Run Gate 2.5: Native runtime build (NO TYPECHECK-ONLY APPROVALS)

Typecheck alone is not sufficient evidence that the code runs. QA must
also execute the project's native build / start command and observe a
clean exit. Examples (use whichever the project declares):

| Stack | Required command | Pass criteria |
|-------|------------------|---------------|
| Node + TypeScript service | `npm run build` then `node dist/<entry>` for one second | exit 0, no thrown error in the first 1s |
| Next.js | `npm run build` | exit 0, no module-resolution / runtime errors |
| React Native (Expo) | `npx expo export --platform <ios\|android> --output-dir /tmp/qa-build` | exit 0 |
| Python service | `python -c "import <package>"` + `python -m <entry> --help` | exit 0, imports resolve |
| Rust | `cargo build --release` | exit 0 |
| Go | `go build ./...` | exit 0 |

Rules:
- A green typecheck with a failing native build = **reject**.
- "Tests pass" is not a substitute. Tests can mock the entry path that
  breaks at runtime (missing env, wrong file path, broken bundler config).
- For scaffold tasks specifically (TASK-000 / scaffold module), the
  native build is the dominant acceptance signal — see Step 6 sub-rule.

If the project does not declare a build command, halt and ask the user
to declare one in `state/SCOPE.md` Sec 3 (Tech stack) before proceeding.
Do NOT skip this gate silently.

### Step 5 — Run Gate 3: Tests

Run tests scoped to the feature:
- All pre-existing tests must still pass.
- All new tests introduced by this task must pass.
- Check test coverage for the task's acceptance criteria:
  - Happy path covered?
  - Error/edge cases covered? (invalid input, auth failure, not found, server error)
  - If coverage is clearly insufficient: reject with a note on what's missing.

### Step 6 — Review Gate 4: Acceptance criteria

Go through every `[ ]` item in the task's acceptance criteria:

For each item:
1. Verify it is satisfied by reading the code and/or running the relevant check.
2. Check it `[x]` if satisfied.
3. If not satisfied: note it in the rejection.

Additional logic review:
- Are error responses in the format specified by `state/SCOPE.md` NFRs?
- Are auth-required routes actually protected?
- Are there hardcoded values that should be config or env vars?
- Is any required validation missing?
- Does the UI match the MCP cache (if applicable)? Key checks: component names, required props, primary layout structure.
- If `Codegen artifact` exists, does the implemented file/widget structure match the codegen file map? Reject if scaffolded elements are missing or restructured without a documented `GAP-XX` in `QA notes:`.
- If `Contract refs` or task acceptance criteria define a backend/client contract, does this task implement or consume the expected contract without placeholder-only behavior?
- If the task includes `User flow`, `Edge cases`, or `Test cases`, does the implementation and verification actually cover those documented behaviors, not just the checklist summary?
- **Scaffold-task sub-rule:** if the task is the project scaffold (TASK-000 or any task in MOD-00 / scaffold module), the acceptance criteria MUST include "native build runs cleanly" and that AC must have been verified by Step 4b. Do not approve a scaffold task on green tests + lint alone — the build artifact must exist and start.

### Step 6b — Design fidelity checks (UI tasks only)

Run this step when the task includes:
- `Design source: Figma`, or
- `Codegen artifact`, or
- `Visual baseline refs`, or
- `Plugin artifact refs`

Validate:
- Token integrity: color/type/spacing/radius/shadow use defined tokens/classes where available.
- State parity: required states are implemented (default, hover, focus, disabled, loading, error, empty when applicable).
- Responsive fidelity: layout behavior at expected breakpoints matches artifacts/checklist.
- Accessibility parity: semantic structure, labels, keyboard focus visibility, and expected accessible names.
- Visual baseline parity: if baseline refs exist, compare key screens/states and reject major layout/token/state drift.
- Device-chrome exclusion: status bar, notch, home indicator, or other device preview chrome is not duplicated inside the implemented UI unless the task explicitly scopes app-shell chrome.

If design checks fail, reject with explicit notes (file path + location + observed mismatch + expected token/state/ref).

### Step 6c — Integration checks (API-backed tasks)

Run this step when the task implements or consumes an API-backed screen, route, or shared contract.

Validate:
- Protected routes or screens send authenticated requests through the canonical client path used by the feature, not a legacy or bypassed HTTP path.
- The task documents and verifies expected `401` handling for protected routes using live or mocked server behavior.
- Placeholder-only UI (`coming soon`, static untappable rows, fake success state) is rejected unless the task explicitly scopes it and names the successor task that replaces it.

### Step 6e — Component architecture checks (UI tasks — HARD REJECT)

Run this step for every UI task (any file under `apps/web/`, `apps/admin/`, `apps/<frontend>/`, `packages/ui/`, or files matching `*.tsx`, `*.vue`, `*.svelte`).

These checks mirror the HARD CONTRACT in `deliverables/architecture/styles/<style>.md` → "Component file organization" and `build-task` Step 6. Reject the task if ANY of the following appears:

**1. Static data passed as props (REJECT)**

Scan the diff for components that receive arrays the page itself defined as a static literal. Examples that MUST be rejected:

```tsx
// page.tsx (or any page-level file)
const navItems = [
  { href: '/', label: 'Home' },
  { href: '/products', label: 'Products' },
  { href: '/about', label: 'About' },
];
return <Header items={navItems} />;        // ← REJECT
```

```tsx
// Anywhere in a page
const faqs = [...];
return <Faq questions={faqs} />;            // ← REJECT
```

```tsx
// Importing a static data module and forwarding it as a prop
import { footerLinks } from '@/data/footer';
return <Footer links={footerLinks} />;      // ← REJECT
```

The fix QA must request: move the array INSIDE the receiving component (`Header.tsx`, `Faq.tsx`, `Footer.tsx`) and call the page as `<Header />` / `<Faq />` / `<Footer />` with no props (or only dynamic props).

**Allowed (do NOT reject):**
- Dynamic data from `useQuery`, `await fetch()`, server component `await db...`, route loader, or props that originated from such a source: `<ProductGrid products={products} />` on `/products` page where `products` came from a fetch.
- Translation keys / locale objects (i18n is the only allowed external dependency).
- Auth context (`<UserMenu user={user} />` where `user` came from session).

**2. `.map()` over a static literal (REJECT)**

Scan for `.map(` on the same scope where the array is defined as a static literal in the component or imported from a `data.ts` module. Render each item as explicit JSX instead.

```tsx
// REJECT
const links = [{ href: '/', label: 'Home' }, ...];
return <ul>{links.map(l => <li><a href={l.href}>{l.label}</a></li>)}</ul>;
```

```tsx
// CORRECT
return (
  <ul>
    <li><a href="/">{t('nav.home')}</a></li>
    <li><a href="/products">{t('nav.products')}</a></li>
    <li><a href="/about">{t('nav.about')}</a></li>
  </ul>
);
```

`.map()` is allowed only when the source array is dynamic (API/DB/store/user input).

**3. Page file contains section JSX directly (REJECT)**

Page files (e.g. `ProductsPage.tsx`, `ProfilePage.tsx`, `app/products/page.tsx`) must orchestrate components only. If a page file contains the JSX for a section (header markup inline, FAQ markup inline, profile-avatar markup inline, etc.) instead of `<Header />`, `<Faq />`, `<ProfileAvatar />`, reject and request the section be extracted to its own file under `components/<feature>/`.

**4. File size budget (REJECT past hard ceiling)**

- Soft target: 50–200 lines per component file. Past 200 lines, the Builder must justify it in `QA notes:` (e.g. "single complex form, splitting would fragment one logic concern"). Without justification → reject.
- Hard ceiling: 400 lines. Past 400 lines → reject unconditionally with a list of suggested split points.
- Multiple unrelated logic concerns in one file (e.g. `ProfilePage.tsx` containing avatar update + password change + delete account inline) → reject regardless of line count.

**5. Component file naming and folder placement (REJECT)**

- Each logical concern lives in its own file under `components/<feature>/<Concern>.tsx` (or framework equivalent — `.vue`, `.svelte`).
- Names match the concern: `ProfileAvatar.tsx`, NOT `ProfileSection1.tsx` / `Avatar.tsx` (when ambiguous) / `Component.tsx`.
- No "kitchen sink" files — `components.tsx` containing 5 unrelated components is a reject.

**Rejection format for this gate:**
```
REJECTED. Component architecture violations.
1. apps/web/src/app/page.tsx:14 — `<Header items={navItems} />` passes static
   array as prop. Move `navItems` inside `apps/web/src/components/header/HeaderNav.tsx`
   and render as explicit JSX with `t('nav.<key>')` calls. Page should call
   `<Header />` with no items prop.
2. apps/web/src/components/Footer.tsx:38 — `.map()` over static literal `socials`.
   Render each <SocialIcon> as explicit JSX.
3. apps/web/src/app/profile/page.tsx:1-247 — page contains avatar + password
   + delete-account JSX inline. Split into:
     components/profile/ProfileAvatar.tsx
     components/profile/ProfilePersonalInfo.tsx
     components/profile/ProfileUpdatePassword.tsx
     components/profile/ProfileDeleteAccount.tsx
   ProfilePage.tsx should orchestrate only.
```

These rejections have the same severity as a failing test — there is no "we'll refactor later" path. The Builder must split before re-submitting.

### Step 6d — Deferred-language detection (NO "WE'LL FIX LATER" APPROVALS)

Scan the task block, the diff of changed files, and the Builder's
`QA notes:` for deferred-language patterns. Reject the task if any of
these appear without an explicit follow-up task ID linked from the
deferral:

- `TODO` / `FIXME` / `HACK` / `XXX` added by this task with no linked
  task ID (a comment like `// TODO(TASK-042): swap mock for live API`
  is fine; a bare `// TODO: fix this later` is not).
- `// @ts-ignore` / `// @ts-expect-error` without a one-line reason
  comment immediately above OR below the suppression.
- Phrases in `QA notes:` like "deferred", "we'll fix later",
  "follow-up", "in a future task", "punt for now", "good enough" — any
  of these must be backed by either:
  (a) a follow-up task that already exists in `state/TASKS.md`
      (referenced by ID, e.g. `TASK-099`), OR
  (b) a `Depends on:` link from the next task that explicitly absorbs
      the deferred work.
- Acceptance criteria items checked `[x]` whose code path is gated by
  a feature flag set to `false` (i.e. the AC is technically present
  but inactive). Treat as unchecked unless the flag flip is itself
  scoped in this task.

If any of the above is found, reject with:
```
REJECTED. Deferred-language found.
1. <file>:<line> — "<phrase>" — must link to a follow-up task or be
   resolved before approval.
```

This rule has no severity threshold — even a single unlinked TODO is
grounds for rejection. The point is to keep the build artifact a true
representation of done work, not a bag of "we'll get to it" notes.

### Step 7a — Approve

If all gates pass, design checks pass (when applicable), and all criteria are checked:

1. Mark all `[ ]` items `[x]` in the task block.
2. Mark task `done`:
   ```
   - Status: done
   ```
3. Update the progress table in `state/TASKS.md`.
4. Update `memory/` files (per `02-memory.mdc`):
   - `memory/ARCHITECTURE.md` — add new modules/files/flows.
   - `memory/PATTERNS.md` — append any new reusable pattern.
   - `memory/DECISIONS.md` — append any significant decision.
5. Report to Orchestrator: "TASK-XXX approved."

### Step 7b — Reject

If any gate fails or any criteria item is not satisfied:

0. Check the attempt budget. Read `Attempts:` and `Max attempts:` (default 3).
   - If this rejection would put `Attempts` at or above `Max attempts`, do
     not move the task back to `needs-fix`. Instead mark it `blocked` with
     `QA notes: BLOCKED. Type: attempt-budget-exhausted. Last rejection: ...`
     and surface to the user for direction (scope cut, data/fixture supply,
     or explicit budget increase).
   - Otherwise continue with the normal rejection flow.
1. Write specific rejection notes under `QA notes:` in the task block. Format:
   ```
   REJECTED.
   1. [file path]:[line] — [what is wrong] — [what is expected]
   2. [test file] — [what test is missing] — [what it should cover]
   3. [criteria item] — [why it is not satisfied]
   ```
   For UI fidelity failures, include:
   - observed mismatch
   - expected token/state/baseline reference
   - suggested correction
2. Uncheck any `[x]` items that were incorrectly self-checked by the Builder.
3. Mark task `needs-fix`:
   ```
   - Status: needs-fix
   ```
4. Update the progress table.
5. Do NOT update `memory/` files.
6. Report to Orchestrator: "TASK-XXX rejected. See QA notes."

---

## Rejection note standards

Rejection notes must be:
- **Specific**: file path + line number where relevant.
- **Actionable**: describe exactly what needs to change, not just what is wrong.
- **Scoped**: do not add scope beyond the task's acceptance criteria. Do not request refactors unrelated to the task.

Vague notes are not acceptable:
- Bad: "Tests are insufficient."
- Good: "src/tests/auth.test.ts — no test for 401 response from POST /auth/login. Add a test that sends invalid credentials and asserts the response is 401 with body `{ error: 'invalid_credentials' }`."

---

## What QA does NOT do

- Does not implement fixes — Builder does that.
- Does not add features beyond the task scope.
- Does not update `memory/` on a rejected task.
- Does not approve a task with failing lint, typecheck, or tests under any circumstances.

---

## Output

Task marked `done` with memory updated, or task marked `needs-fix` with specific rejection notes for the Builder.
