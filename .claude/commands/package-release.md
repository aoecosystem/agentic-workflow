---
description: Final stage. Generate release notes, transition VERIFIED to READY_TO_DEPLOY.
---

Run the `package-release` skill. Refuse unless Stage is `VERIFIED`.
Read state/SCOPE.md + TASKS.md + the SoW + STACK-GUIDANCE. Generate a
polished `state/RELEASE-NOTES-v<version>.md`. Show user inline, ask to
save. On save, transition Stage to `READY_TO_DEPLOY`. The pipeline is
complete after this.
