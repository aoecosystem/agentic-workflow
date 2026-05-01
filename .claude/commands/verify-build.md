---
description: Run project-wide lint + typecheck + tests + security + observability gates. Transitions BUILD_APPROVED to VERIFIED on success.
---

Run the `verify-build` skill. Refuse unless Stage is `BUILD_APPROVED`.
Run all 6 gates against `../apps/`: lint, typecheck, unit tests,
integration tests, security audit, observability checks. Print a
verification report. On full success, transition to `VERIFIED`. On any
failure, list specifics with file + line and leave Stage at
`BUILD_APPROVED`.
