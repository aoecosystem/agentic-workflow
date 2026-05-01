# deliverables/

The 5 HTML documents and design assets generated during the docs phase.
Each sub-folder holds one type of deliverable.

## Layout

```
deliverables/
├── brief/                          ← Project Brief
│   ├── template.html               (read-only scaffold)
│   └── <slug>-brief.html           (filled, created by /start-project)
├── scope-of-work/                  ← Scope of Work
│   ├── template.html               (read-only scaffold)
│   └── <slug>-sow.html             (filled, created by /build-scope-of-work)
├── architecture/                   ← System Architecture
│   ├── template.html               (read-only scaffold)
│   ├── <slug>-architecture.html    (filled, created by /build-architecture)
│   └── styles/                     ← architecture style profiles (4 files)
│       ├── monolith.md hybrid.md microservices.md serverless.md
│       └── _schema.md README.md
├── database/                       ← Database Diagram
│   ├── template.html               (read-only scaffold)
│   └── <slug>-database.html        (filled, created by /build-database)
├── infrastructure/                 ← Infrastructure Diagram
│   ├── template.html               (read-only scaffold)
│   └── <slug>-infrastructure.html  (filled, created by /build-infrastructure)
└── designs/                        ← UI screenshots / Figma exports
    └── <page-id>.png/jpg/html      (human-uploaded)
```

## File naming convention

- **Templates** (read-only) are always named `template.html` inside their type folder. The folder name disambiguates.
- **Filled deliverables** use `<slug>-<type>.html` where `<slug>` is the kebab-case project name.
- **Designs** use `<page-id>.<ext>` matching the Page Inventory IDs in the SoW.

## Owned by

| Folder | Created by | Edited by |
|---|---|---|
| `brief/<slug>-brief.html` | `/start-project` | `/review-brief` |
| `scope-of-work/<slug>-sow.html` | `/build-scope-of-work` | `/review-scope-of-work` |
| `architecture/<slug>-architecture.html` | `/build-architecture` | `/review-architecture` |
| `architecture/styles/*.md` | (snapshot — read-only) | (manual edit, propagates to all build skills) |
| `database/<slug>-database.html` | `/build-database` | `/review-database` |
| `infrastructure/<slug>-infrastructure.html` | `/build-infrastructure` | `/review-infrastructure` |
| `designs/<page-id>.*` | human upload | human upload |

## Hash tracking

Every filled deliverable carries a SHA-256 hash in `state/SESSION-STATE.md`.
Manual edits are detected via hash drift on next skill run. See
`AGENTS.md` → Manual Edit Protocol for details.
