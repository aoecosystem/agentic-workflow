# .pipeline/

Internal working directory used by the `reqops` and `parse-scope` skills.
Pre-created so those skills do not fail silently on first run.

## Subfolders (created on demand)

```
.pipeline/
├── sow.md                              ← optional fallback SOW source
├── requirements.md                     ← cross-feature requirement notes
├── features-list.md                    ← inventory of detected features
├── system-design-provided.md           ← extracted system design
├── features/
│   └── requirements/
│       └── <feature-id>-<slug>-requirements.md
└── drafts/                             ← agent scratch (gitignored)
```

## Owned by

| Path | Writer skill |
|------|--------------|
| `sow.md` | `reqops` (fallback only) |
| `features-list.md` | `reqops` |
| `system-design-provided.md` | `reqops` |
| `requirements.md` | `reqops` |
| `features/requirements/*.md` | `reqops` |
| `drafts/*` | any (transient, gitignored) |

`TASKS.md` is **not** written here — that is owned by the `parse-scope` skill
at the repo root.

## When this folder fills up

Normally only when you ran `reqops` or `parse scope` with a SOW source. If
you never run `reqops` and your SOW is in `inputs/` or `SCOPE.md`, this
folder may stay empty — that is fine.

## Cleanup

Safe to delete the contents at any time. The next `reqops` / `parse scope`
run will regenerate whatever it needs.
