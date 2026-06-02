# Stack Guidance

<!--
Generated after `import docs` once the project stack is known.
Purpose: give Builders stack-specific senior defaults before implementation starts.

Update when:
- `SCOPE.md` tech stack or architecture changes materially
- a confirmed project-wide stack convention should be locked in for future tasks

Keep this file concise and reusable:
- architecture defaults
- folder/module conventions
- state/data/API conventions
- UI conventions
- testing expectations
- anti-patterns to avoid
-->

## Status

- Source of truth: derived from `SCOPE.md` sections 2 and 3
- Current state: placeholder template
- If this file still says placeholder after `import docs`, regenerate it before `parse scope` or `start build`

## Stack summary

- Frontend:
- Backend:
- Database:
- Auth:
- Styling:
- Testing:

## Architectural defaults

- Prefer the simplest layered structure that matches the declared stack.
- Keep transport/UI concerns separate from business logic and persistence.
- Reuse project-level patterns before introducing stack-specific abstractions.

## File and module conventions

- Place files according to `memory/ARCHITECTURE.md`.
- Follow the dominant conventions of the detected stack for naming, composition, and module boundaries.

## Data, state, and API guidance

- Validate inputs at boundaries.
- Keep shared contracts/types close to the domain layer that owns them.
- Model loading, success, empty, and error states explicitly.

## UI and UX guidance

- Prefer composition over large monolithic screens/components/widgets.
- Reuse design tokens and shared UI primitives when available.
- Preserve accessibility and semantic behavior expected by the stack/platform.

## Testing guidance

- Cover the happy path and at least one meaningful edge/error path per touched unit.
- Prefer tests that verify behavior and contracts over implementation details.

## Avoid

- Stack-inappropriate abstractions added without a strong reason.
- Hardcoded visual or architectural values when project conventions already define them.
- Silent error handling.
