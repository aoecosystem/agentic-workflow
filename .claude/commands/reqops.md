---
description: Derive SOW-traceable per-feature requirements under CONTEXT/feature-specs/
---

Run the `reqops` skill. Read SOW from `state/SCOPE.md` (with `DOCMENTS/<slug>-scope-of-work.html` as fallback), produce dev-ready feature requirements with MoSCoW-tagged Given/When/Then ACs, NFRs, edge cases, and change logs. Save one file per feature at `CONTEXT/feature-specs/<feature-id>-<slug>-requirements.md`. Do NOT write `SESSION-STATE/TASKS.md` — tell the user to run `/parse-scope` afterwards. $ARGUMENTS
