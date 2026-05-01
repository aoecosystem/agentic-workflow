# inputs/

Drop your project's source documents here, then run `start project`.
The agent will fill the **canonical artifacts** below before any other
work begins.

## Canonical artifacts (the workflow's source of truth)

```
inputs/
├── project-brief.md       ← high-level vision, audience, features (filled)
└── scope-of-work.md       ← detailed architecture, stack, feature breakdown (filled)
```

Empty scaffolds for both live in `templates/` at the repo root.

## How the canonical artifacts get filled

The workflow has two paths and they both end at the same place:

```
Path A — you have written sources       Path B — only an idea
─────────────────────────────────       ──────────────────────
inputs/<your-files>.{pdf,docx,md,html}   "interview me"
        │                                       │
        ▼                                       ▼
"import docs"                             "interview me" finishes
extracts content into                     writes to
inputs/project-brief.md  ─────────────►  inputs/project-brief.md
inputs/scope-of-work.md                   inputs/scope-of-work.md
        │                                       │
        ▼                                       ▼
"import docs" populates SCOPE.md  ◄──────  "import docs"
"parse scope" generates TASKS.md
"start build" runs the build
```

This folder is the canonical user-input drop zone, separate from `docs/`
which holds framework documentation only.

## Supported files

| File type | Notes |
|-----------|-------|
| `.pdf` | Read directly. |
| `.docx` / `.doc` | Requires `pandoc` (`brew install pandoc`) or save as PDF. |
| `.txt` / `.md` | Read directly. |
| `.html` | Read directly (e.g. exports from `project-foundations`). |

## What to put here

- **Scope of Work** — produced from `project-foundations/scope-of-work-template.html`.
- **Project Brief** — produced from `project-foundations/project-brief-template.html`.
- **System design doc** — architecture, stack, models, API contracts.
- **Requirements doc** — user stories, NFRs, acceptance criteria.

You can drop any combination — `import docs` reads everything in this folder
and merges the content into `SCOPE.md`.

## Naming conventions

Files containing any of these in their name are prioritized by the importer:
`scope-of-work`, `sow`, `requirements`, `prd`, `spec`, `system-design`.

Examples:
```
inputs/
  bron-go-scope-of-work.html
  bron-go-system-design.pdf
  bron-go-requirements.md
```

## Read order (`import docs`)

1. `inputs/project-brief.md` + `inputs/scope-of-work.md` — canonical
   filled artifacts. If both exist, the importer reads them directly.
2. Raw user files in `inputs/` — extracted into the two canonical
   artifacts above before populating `SCOPE.md`.
3. `docs/` — legacy fallback (kept for backwards compatibility).

## After import

The importer fills `SCOPE.md` and generates `memory/STACK-GUIDANCE.md`.
It will not overwrite `SCOPE.md` without your confirmation.
