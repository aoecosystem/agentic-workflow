---
name: import-docs
description: Read scope/system-design/requirements documents from docs/ (PDF, Word, Markdown, TXT), extract a high-fidelity app-flow-aware SCOPE.md, and generate memory/STACK-GUIDANCE.md. Trigger when the user says "import docs", "ingest my spec", drops PDFs/docx files into docs/ and wants SCOPE populated, or asks to extract project scope from uploaded documents. Do NOT trigger when SCOPE.md is already filled and the user wants to generate tasks (use parse-scope for that).
---

## Stage gate (RUN FIRST)

1. Read `state/SESSION-STATE.md`. Locate `Stage:`.
2. If `Stage` is not `DOCS_COMPLETE`, refuse with:
   > "Import-docs is only valid from `DOCS_COMPLETE`. Current: `<STAGE>`.
   > Run `/status` for next valid commands. To reach `DOCS_COMPLETE`,
   > complete all 5 docs phase approvals first."
   Leave Stage unchanged.

---

## Manual-edit detection (RUN BEFORE FILE OPERATIONS)

Before reading any artifact, run the **Manual Edit Protocol** in
`AGENTS.md`. Compute SHA-256 of all 5 deliverables, compare to stored
hashes, ask user to accept on drift.

---

# Skill: Import Docs

**Trigger:** User says `import docs` (or uses the `/import-docs` slash command)

**Purpose:** Read one or more requirement/design documents from `docs/`, extract high-fidelity project scope plus end-to-end app flow details, draft a production-ready `state/SCOPE.md`, and generate `memory/STACK-GUIDANCE.md` after user confirmation.

This skill must produce SOW quality that is execution-ready for `parse scope` and `start build`, not a vague summary.

---

## Quality bar (non-negotiable)

When source docs include user journeys, flows, or screen specs:

1. Capture role-based app flow (Parent/Tutor/Admin, etc.) explicitly.
2. Capture screen-level actions in `Element -> Action -> Destination` form (table or bullet).
3. Capture lifecycle transitions and timers (expirations, lockouts, deadlines, retries).
4. Capture error/empty/edge states for each critical flow.
5. Preserve source-grounded details; mark assumptions as `INFERRED:` when unavoidable.

---

## Supported formats

| Format | How it's read |
|--------|---------------|
| `.pdf` | Read directly |
| `.docx` | Convert first (see Step 1) |
| `.doc` | Convert first (see Step 1) |
| `.txt` / `.md` | Read directly |

---

## Steps

### Step 0 — Resolve canonical input artifacts

Before scanning raw uploaded documents, check for the canonical filled-in
artifacts:

- `inputs/project-brief.md`
- `inputs/scope-of-work.md`

Resolution rules:

1. If **both** canonical files exist and are filled (not just template
   placeholders), use them directly as the authoritative source. Skip
   raw-doc scanning.
2. If **only one** of the two exists, use what's there and synthesize
   the missing one from the other plus any raw docs in `inputs/`.
3. If **neither** exists but raw docs are present (PDF, docx, html,
   md), extract content from those raw docs and write
   `inputs/project-brief.md` + `inputs/scope-of-work.md` first
   (using the structure from `templates/project-brief.md` and
   `templates/scope-of-work.md`). Show drafts for confirmation
   before saving.
4. If **neither** canonical files nor raw docs exist, halt and tell
   the user to either:
   - run `interview me` to fill them through Q&A, or
   - drop source documents into `inputs/`.

After this step, the rest of the skill operates on
`inputs/project-brief.md` + `inputs/scope-of-work.md` as the source of
truth, never on raw docs directly.

---

### Step 1 — Scan input sources and prepare readable files

Resolve the input source in this order:

1. `inputs/` — preferred drop zone for new projects.
2. `docs/` — legacy fallback for backwards compatibility.

If both folders contain files, treat `inputs/` as authoritative; `docs/`
files are read only when `inputs/` is empty. List the chosen source in the
review draft so the user knows which folder was used.

If both are empty:
- Tell user to place documents in `inputs/`, then rerun `import docs`.
- Stop.

If `.docx` / `.doc` files exist in the chosen source:
- Check `pandoc --version`.
- If available, convert each file to markdown alongside the original:
  ```bash
  pandoc inputs/input.docx -o inputs/input-converted.md
  ```
- If not available, tell user to export to PDF or install pandoc
  (`brew install pandoc`), then continue with other readable files.

### Step 2 — Read all sources before extracting

Read every readable file in full before drafting anything.

Build a source ledger while reading:
- `source_type`: scope-of-work, system-design, app-flow, API spec, design notes
- `trust_level`: authoritative, supplemental, ambiguous
- `key_sections_found`: goals, architecture, stack, features, flows, endpoints, models, NFRs

### Step 3 — Normalize extracted information

Map content to `state/SCOPE.md` sections and also build an internal `Flow Matrix` for quality checks.

#### 3A) SCOPE mapping

| SCOPE section | Extract from docs |
|---------------|-------------------|
| 1. Project Overview | summary, outcomes, target users |
| 2. System Architecture | frontend/backend/db/auth/services/deploy |
| 3. Tech Stack | framework/library/tooling choices |
| 4. MCP URLs | Figma, OpenAPI, plugin export, design tokens |
| 5. Feature Breakdown | capabilities, screens, endpoints, models, dependencies |
| 6. Out of Scope | exclusions, future phases |
| 7. Non-Functional Requirements | performance, security, accessibility, error conventions |

#### 3B) Flow Matrix (required when flow content exists)

For each role and major journey, extract:
- `entry_points` (login, signup, deep link, admin portal)
- `ordered_screens`
- `actions` (button/link/system events)
- `destinations` (next screens/states)
- `state_logic` (pending, approved, declined, expired, locked, etc.)
- `time_rules` (OTP expiry, lockout windows, response deadlines)
- `payment_or_status_lifecycle` (if applicable)
- `edge_cases` (no results, no availability, failed payment, expired token)

If flow details are absent, note this in gaps explicitly.

### Step 4 — Draft `state/SCOPE.md` with app-flow-aware feature blocks

Keep `state/SCOPE.md` template structure intact. Replace placeholders with extracted content only.

For each feature, produce concrete, implementation-ready blocks:

```markdown
### Feature: [Source-grounded feature name]

**Description:**
[What this feature does, who uses it, and important business rules.]

**Screens / Pages:**
- [Screen]: [Primary action] -> [Destination]
- [Screen]: [Primary action] -> [Destination]

**API Endpoints:**
- [METHOD] [path] — auth: [public/protected], input: [...], output: [...], errors: [...]

**Data Models:**
- [Entity]: [key fields + important status enums]

**MCP URL:**
[URL or blank]

**Figma node IDs (optional):**
[IDs if present]

**Plugin export link/path (optional):**
[link/path if present]

**Design system token source (optional):**
[source if present]

**Depends on features:**
[feature dependencies or none]
```

Feature splitting guidance:
- Split by user-facing vertical flow (e.g., `Auth`, `Parent Booking`, `Tutor Session Execution`, `Admin Review`).
- Do not collapse unrelated role flows into one mega-feature if dependencies differ.
- When an action changes status across actors (e.g. parent books -> tutor accepts), include that transition in the relevant feature description.

### Step 4.5 — Add explicit app-flow evidence in the draft response

Before any file write, include a concise `Flow coverage report` in chat:
- Roles found
- Total screens found
- Cross-role transitions captured
- Critical timers/rules captured
- Known missing flow data

Also include one compact lifecycle snippet for each critical cross-role flow (booking, approval, payout, etc.).

Example:
```text
Flow coverage report:
- Roles: Parent, Tutor, Admin
- Screens captured: 42
- Cross-role transitions: booking pending -> accepted/declined/timeout
- Timers captured: OTP 5m, login lockout 15m, tutor response 24h
- Missing: cancellation policy not fully specified for tutor-side edge cases
```

### Step 5 — Flag gaps and ambiguities (structured)

After drafting, report gaps with severity:

```text
Gaps found:
1. [HIGH] Auth strategy unclear: JWT vs session cookie not specified.
2. [MEDIUM] Feature "Dashboard" has screens but no endpoint contracts.
3. [MEDIUM] Tutor approval flow missing rejection-retry behavior.
4. [LOW] No Figma node IDs provided for key screens.
```

Rules:
- Ask specific questions, not generic "please clarify".
- If conflicting sources exist, cite both and recommend which to treat as source of truth.

### Step 5.5 — Clarifying-questions loop (95% accuracy gate, RUN BEFORE ANY WRITE)

This is a hard gate. No file is written (no `state/SCOPE.md`, no
`memory/STACK-GUIDANCE.md`, no `inputs/*.md`) until the loop exits with
>= 95% accuracy. "Accuracy" here means: every required field across
SCOPE sections 1-7 is either (a) sourced from the input docs, or (b)
explicitly confirmed by the user, or (c) marked `TBD` with the user's
acknowledgement.

#### Severity buckets (derived from Step 5 gaps)

| Bucket | Definition | Loop behavior |
|--------|------------|---------------|
| **HIGH** | Missing answer would make Builders fabricate scope or block downstream stages (e.g. architecture style, primary user, deployment target, auth strategy, primary platform) | Must be answered. Halt write until resolved. |
| **MEDIUM** | Missing answer is recoverable but causes rework if wrong (e.g. third-party integrations, secondary languages, payment provider, search backend) | Must be answered OR explicitly marked `TBD` with user acknowledgement. |
| **LOW** | Cosmetic / preference-level gaps (e.g. brand color, error-page copy, default empty-state illustrations) | Default values applied; user notified once. |

#### Loop steps

1. **Batch all HIGH gaps into one message.** Use a numbered list, one
   question per line. Include the source-doc citation (or "not in
   sources") so the user knows why you're asking.
2. **Wait for the user's reply.** Parse each numbered answer back to
   the matching gap. If any HIGH gap is left unanswered or the answer
   is itself ambiguous ("up to you", "whatever you recommend"), re-ask
   only the unresolved ones - do not proceed.
3. **Repeat** for MEDIUM gaps, with one tweak: a literal `TBD` answer
   is acceptable for MEDIUM. Record the field as `TBD` in the eventual
   draft so it surfaces during `/parse-scope`.
4. **Apply defaults** for LOW gaps without asking. Print a single
   "Defaults applied" block at the end so the user can override
   inline.

#### Accuracy calculation

Before exiting the loop, compute:

```
total_required_fields    = N           (sum of fields across SCOPE Sections 1-7)
fields_with_source       = a           (sourced from input docs)
fields_user_confirmed    = b           (answered in HIGH/MEDIUM batches)
fields_marked_tbd        = c           (explicit TBD in MEDIUM)
fields_defaulted_low     = d           (LOW defaults applied)

accuracy = (a + b + c + d) / N
```

Loop exits only when `accuracy >= 0.95` AND every HIGH gap is closed.
If `accuracy < 0.95`, surface the still-open fields and re-ask. Never
silently fall back to fabricated values.

#### Output of this step

A single internal worksheet (in chat, not yet written to disk):

```text
Clarifying-questions worksheet:
  HIGH resolved:   8 / 8
  MEDIUM resolved: 5 / 6  (1 marked TBD: "third-party email provider")
  LOW defaulted:   3 / 3
  Accuracy:        16 / 17 = 94.1%   <- below gate, re-ask MEDIUM-6
```

When this worksheet shows >= 95% AND zero open HIGH, proceed to Step 6.
Until then, do NOT proceed.

### Step 6 — Confirm before saving

Show user:
1. Extraction summary (`features`, `screens`, `endpoints`, `models`, `roles`).
2. Flow coverage report (Step 4.5).
3. Gap list (Step 5).
4. Ask for explicit confirmation to write files.

Do not write `state/SCOPE.md` or `memory/STACK-GUIDANCE.md` until user confirms.

### Step 7 — Write `state/SCOPE.md`

After user confirmation:
1. Write final `state/SCOPE.md`.
2. Generate `memory/STACK-GUIDANCE.md` from confirmed `state/SCOPE.md` sections 2 and 3.
3. Tell user what was written and what gaps still need manual input.

### Step 7.5 — Generate `memory/STACK-GUIDANCE.md`

Required sections:
- `## Status`
- `## Stack summary`
- `## Architectural defaults`
- `## File and module conventions`
- `## Data, state, and API guidance`
- `## UI and UX guidance`
- `## Testing guidance`
- `## Avoid`

Rules:
- Use declared stack only (no invented frameworks).
- Provide stack-specific defaults (not generic advice).
- Keep it concise, operational, reusable.
- If stack detail is incomplete, state what must be filled before build.

---

## Multi-document precedence

When multiple docs overlap:
- `scope/SOW` is primary for goals, business scope, out-of-scope.
- `system design` is primary for architecture, contracts, data shape.
- `app flow` is primary for role journeys, screen transitions, state behavior.
- `figma` / design sources are primary for screen naming and visual hierarchy.

If contradictions remain unresolved, report them in gaps and do not silently merge conflicting facts.

---

## App-flow extraction examples (for consistency)

Use this style when source material supports it:

```markdown
**Screens / Pages:**
- Login: User submits credentials -> Role-based Home or error state.
- OTP Verification: User enters 6-digit code -> Profile Setup on success.
- Pending Tutor Response: Payment authorized -> waits up to 24h for tutor action.
```

```markdown
**API Endpoints:**
- POST /auth/login — auth: public, input: { email, password }, output: { token, role }, errors: invalid_credentials, account_locked
- POST /bookings/:id/accept — auth: tutor, input: none, output: { status: "confirmed" }, errors: booking_not_found, booking_expired
```

```text
Lifecycle snippet:
booking_created -> pending_tutor_confirmation -> confirmed | declined | auto_cancelled
```

Use `INFERRED:` prefix only when deriving a missing detail from strong context.

---

### Step 7.6 — Derive Page Inventory (runs LAST, after sections 1-7 + stack guidance)

After SCOPE.md sections 1-7 are saved and `memory/STACK-GUIDANCE.md`
has been generated, derive section 8 (Page Inventory) automatically.

Pages depend on which features, services, APIs, data models, AND stack
exist — so this step must run last. Never write Page Inventory before
the SOW body and stack guidance are stable.

1. **Detect project type** from sections 2 (architecture) + 3 (stack)
   + deployment target:
   - mobile → React Native / Flutter / Swift / Kotlin / Expo, OR
              App Store / Play Store / Expo Go.
   - web    → Next.js / React / Vue / Svelte / Angular, OR
              Vercel / Netlify / Cloudflare / Railway / self-hosted.
   - both   → both signals present.

2. **Generate one row per user-facing screen**, with five columns:
   - **Page ID** — `<feature-slug>-<screen-slug>`, kebab-case.
   - **Page Name** — human-readable.
   - **Platform** — web / mobile / both.
   - **Auth** — public / private.
   - **Description** — one short sentence.

3. **Skip platform-irrelevant pages** (no mobile rows for web-only
   projects, etc.).

4. **Write to:**
   - `state/SCOPE.md` section 8 (the rendered table).
   - `memory/PAGES.md` index (same rows + `Implemented: no` and empty
     `Task` columns).

5. Show the table to the user inline. Confirm before writing.

Page IDs become the universal join key for design artifacts. Designers
should name their Figma frames with the same IDs, and screenshot /
Claude Design exports should use `<page-id>.{png,jpg,html}` filenames.

---

## Output

1. Draft review response with extraction summary, flow coverage report, and structured gaps.
2. Confirmed write to `state/SCOPE.md`.
3. Updated `memory/STACK-GUIDANCE.md`.

---

## Stage transition (ON SAVE)

After successfully writing `state/SCOPE.md` and populating
`memory/STACK-GUIDANCE.md`:

1. Update `state/SESSION-STATE.md`:
   - `Stage:` → `SCOPE_PARSED`
   - `Last skill:` → `import-docs`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /parse-scope to generate state/TASKS.md.`
   - Artifacts list: mark `state/SCOPE.md` and `memory/STACK-GUIDANCE.md` with hashes.
2. Append audit log:
   ```
   <ISO>  import-docs  DOCS_COMPLETE → SCOPE_PARSED  populated SCOPE.md from 5 deliverables
   ```

3. Tell user: *"Next: run `/parse-scope` to generate the task graph."*
