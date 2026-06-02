# Architecture

<!-- Agent-maintained. Updated after every completed task. Do not edit manually during a build. -->

## Project layout note

All paths in this file are interpreted **relative to `apps/`**, not to the
`agentic-workflow/` repo root. The actual filesystem location of any
module mentioned here is:

```
<project-root>/apps/<sub-app>/<path>
```

Example: `src/api/` in this document means
`<project-root>/apps/<sub-app>/src/api/` on disk. See
`deliverables/architecture/styles/<style>.md` for the full convention.

---

## Module map

<!-- Added by agent after scaffold task. Example:
src/
  api/          → API route handlers
  db/           → Database client and migrations
  models/       → Shared TypeScript types and Zod schemas
  services/     → Business logic (no HTTP concerns)
  ui/
    components/ → Reusable UI components
    screens/    → Page-level components
  utils/        → Shared utility functions
  tests/        → Test files mirroring src/ structure
-->

Default structure for generated projects:

- `src/api/` → transport layer handlers/controllers only
- `src/services/` → business logic and orchestration
- `src/models/` → domain types and validation schemas
- `src/db/` → persistence adapters, queries, migrations
- `src/ui/components/` → reusable UI building blocks
- `src/ui/screens/` → route/page-level composition
- `src/tests/` → test files mirroring source layout

---

## Data flow

<!-- High-level description of how data moves through the system. Added after scaffold + first feature. -->

Preferred request flow:

- `UI -> api -> services -> db`
- `db/services -> api -> UI` (no raw DB objects leaked to UI)
- Validation happens at API boundaries before service calls.

---

## Auth flow

<!-- Summarize how authentication works once implemented. -->

Auth pattern (when applicable):

- Public auth endpoints issue session/token artifacts.
- Protected endpoints enforce auth in API layer before business logic.
- Services receive verified actor/context, not raw credentials.

---

## Key boundaries

<!-- What must NOT cross module boundaries. E.g. "UI components must not import directly from db/" -->

- UI code must not import directly from `src/db/`.
- DB layer must not depend on UI modules.
- Services should not perform transport concerns (HTTP response shaping).
- API handlers should remain thin and delegate domain logic to services.
