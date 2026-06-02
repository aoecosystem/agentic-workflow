# Decisions

<!-- Agent-maintained. One entry per decision that should not be re-litigated.
     Format: ## Decision title → Context, choice made, reason. -->

---

<!-- Example:

## Auth token storage
Context: Needed to decide where to store JWT on the client.
Decision: HttpOnly cookie, not localStorage.
Reason: Prevents XSS token theft. Matches security NFR in SCOPE.md.

-->

## QA-only done transition
Context: Multiple agents can modify task states during build execution.
Decision: Only QA agent can move tasks to `done`; builders stop at `in-review`.
Reason: Prevents self-approval and keeps acceptance checks enforced.

## Verification gates are mandatory before handoff
Context: Builders and QA need a shared quality bar before status transitions.
Decision: Lint, typecheck, and scoped tests must pass before `in-review` handoff.
Reason: Reduces rework loops and catches regressions before QA deep review.
