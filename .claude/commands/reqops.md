---
description: Derive SOW-traceable per-feature requirements under .pipeline/features/requirements/
---

Run the `reqops` skill. Read SOW from `state/SCOPE.md` (with `.pipeline/sow.md` as fallback), produce dev-ready feature requirements with MoSCoW-tagged Given/When/Then ACs, NFRs, edge cases, and change logs. Save one file per feature at `.pipeline/features/requirements/<feature-id>-<slug>-requirements.md`. Do NOT write `state/TASKS.md` — tell the user to run `/parse-scope` afterwards. $ARGUMENTS
