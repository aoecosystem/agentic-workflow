---
description: Lock the completed build. Transitions Stage from BUILD_COMPLETE to BUILD_APPROVED.
---

Run the `approve-build` skill. Refuse unless Stage is `BUILD_COMPLETE`.
Verify all tasks `done`, no QA red flags, all acceptance criteria
checked, code in apps/ matches architecture style, no orphan files. On
success, transition to `BUILD_APPROVED` and present `/verify-build`
next. On failure, list every failing item.
