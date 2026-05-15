---
name: api-contract
description: Generate or update a shared API contract artifact (OpenAPI YAML, tRPC schema, or GraphQL SDL) under memory/contracts/<feature>.<ext> so backend, web, and mobile Builders implement against a single source of truth and never desynchronize. Trigger when the user says "generate contract", "api contract", "sync contract", or when a full-stack feature task block has `Contract refs` with `Integration status: not-started`. Choice of contract format is auto-detected from SCOPE.md tech stack and feature endpoint syntax.
---

## Stage gate (RUN FIRST)

1. Read `state/SESSION-STATE.md`. Locate `Stage:`.
2. Refuse unless Stage is `SCOPE_PARSED`, `TASKS_GENERATED`, `TASKS_APPROVED`, `BUILDING`, or later. Message:
   > "api-contract requires SCOPE.md or TASKS.md to read endpoint specs. Current Stage: `<STAGE>`. Run `/parse-scope` first."

---

# Skill: API Contract

**Trigger:** User says `generate contract`, `api contract`, or
`sync contract`. May also be triggered by Orchestrator before fanning
out parallel Builders on a feature with both backend and frontend tasks.

**Purpose:** Produce a single, machine-readable API contract for each
full-stack feature so backend and frontend Builders implement against
the same definitions. Prevents response-shape and auth-expectation
drift between parallel chains.

---

## Inputs

- `state/SCOPE.md` Section 5 (Feature Breakdown) — endpoint list and data
  models per feature.
- `memory/STACK-GUIDANCE.md` — declared API style (REST, tRPC, GraphQL).
- `state/TASKS.md` — `Contract refs` field on each task, indicating which task
  owns the backend or client surface.
- Optional: existing `memory/contracts/<feature>.<ext>` (will be merged,
  not overwritten).

---

## Format selection

Detect contract format using this priority:

| Signal | Format chosen |
|--------|---------------|
| `STACK-GUIDANCE.md` declares tRPC | tRPC TypeScript schema |
| `STACK-GUIDANCE.md` declares GraphQL | GraphQL SDL (`.graphql`) |
| `STACK-GUIDANCE.md` declares gRPC | Protobuf (`.proto`) |
| Otherwise (REST default) | OpenAPI 3.1 (`.yaml`) |
| User-explicit override in trigger ("api contract as openapi") | User's choice |

If the stack is ambiguous, default to OpenAPI 3.1.

---

## Steps

### Step 1 — Read context

1. Read `state/SCOPE.md` Section 5 entirely.
2. Read `memory/STACK-GUIDANCE.md` (skip if placeholder).
3. Read `state/TASKS.md` and collect all task blocks where `Contract refs`
   field has `Backend owner`, `Web owner`, or `Mobile owner`.
4. Read `memory/PATTERNS.md` for existing API handler shapes.

### Step 2 — Group by feature

For each feature in `state/SCOPE.md` Section 5:

- List its endpoints (REST verb + path, or tRPC procedure name).
- Map each endpoint to its task ID via `state/TASKS.md`.
- Collect the data models the endpoints reference.
- Note the auth boundary (public vs authenticated) per endpoint.

Skip features with zero endpoints.

### Step 3 — Generate the contract

For each feature, write `memory/contracts/<feature-slug>.<ext>`.

#### OpenAPI 3.1 (default REST)

The header MUST include:
- `openapi: 3.1.0`
- `info.title`, `info.version`, `info.description` (auto-generated note + last sync timestamp + stack)
- `paths` for every endpoint
- `components.schemas` for every data model
- `components.responses` with `ValidationError` (400) and `Unauthorized` (401)
- `components.securitySchemes` with `bearerAuth` (JWT)

Every authenticated endpoint must reference `bearerAuth: []` in `security`.
Public endpoints must reference `security: []` explicitly.

#### tRPC schema

Output `memory/contracts/<feature-slug>.ts` with:
- Zod schemas for every model.
- Procedure input and output schemas.
- A `<feature>Contract` exported object listing all procedures with
  their input/output schemas and `auth: 'required' | 'public'` flag.

#### GraphQL SDL

Output `memory/contracts/<feature-slug>.graphql` with:
- One `type` declaration per data model.
- Public + authenticated queries under `type Query`.
- Mutations under `type Mutation` with `@auth` directive when needed.

### Step 4 — Reconcile with existing contract

If `memory/contracts/<feature-slug>.<ext>` already exists:

1. Read it.
2. Identify any model or endpoint that exists in the file but no longer
   exists in `state/SCOPE.md` — mark as deprecated with a header comment, do
   not delete. The user must run `delta scope` to formally remove.
3. Identify new models or endpoints in `state/SCOPE.md` not yet in the file —
   add them.
4. For changed types: write the new shape and add a comment noting the
   change. Surface the change to the user in the run summary.

Never silently overwrite an existing contract. Always summarize the diff.

### Step 5 — Update task blocks

For every task referenced by this contract:

- If its `Contract refs.Integration status` is `not-started`, change it
  to `partial` and add a comment in `QA notes:`:
  ```
  Contract artifact ready: memory/contracts/<feature-slug>.<ext>
  ```
- If `partial`, leave as-is.
- Do NOT change to `complete` — that requires both backend and client
  Builders to mark integration tested. Only QA flips that.

### Step 6 — Show summary

Print to chat:

```
Generated contracts:
  memory/contracts/<feature-1>.yaml  (3 endpoints, 2 models)
  memory/contracts/<feature-2>.yaml  (1 endpoint, 1 model)

Updated 5 task blocks (Integration status: not-started → partial).

Builders consuming these contracts:
  TASK-003 (backend, auth)
  TASK-004 (web, auth login screen)
  TASK-007 (mobile, auth flow)

Next: kick off `start build` (or `resume build`).
```

Stop. Do not auto-trigger build.

---

## Rules

- Contracts are agent-maintained. Builders read them. Builders never
  edit `memory/contracts/*` by hand — the skill is the sole writer.
- Contracts must be valid for their format. Run a syntax check before
  saving (e.g. `python3 -c "import yaml; yaml.safe_load(open(p))"` for
  OpenAPI; `tsc --noEmit` for tRPC if available).
- Never invent endpoints not in `state/SCOPE.md`. If `state/SCOPE.md` is missing
  detail, surface a `GAP:` note in the contract header instead of
  guessing.
- Auth defaults: any endpoint not explicitly marked public in
  `state/SCOPE.md` is treated as authenticated.
- Error envelope defaults to `{ error: string, code: string }` unless
  `state/SCOPE.md` Section 7 declares otherwise.
- One file per feature. Do not collapse multiple features into a
  monolithic contract — that defeats parallel Builder isolation.

---

## Output

One contract artifact per feature in `memory/contracts/`, with task
blocks in `state/TASKS.md` updated to reference them. Diff summary printed to
the user.
