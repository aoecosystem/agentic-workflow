---
name: import-docs
description: Read user-uploaded documents from DOCMENTS/ (PDF, Word, HTML, Markdown) and auto-generate all 5 project HTML documents. Alternative entry point to /start-interview — use when you already have a brief or requirements document. Trigger on `/import-docs`.
---

# Skill: import-docs

**Trigger:** `/import-docs`

**Purpose:** Alternative entry point to `/start-interview`. The user drops
their existing brief, SOW, requirements doc, or any reference document into
`DOCMENTS/` — Claude reads it, extracts project information, and
auto-generates all 5 HTML documents without an interview.

---

## Step 0 — Route by current Stage

Read `SESSION-STATE/SESSION-STATE.md`.

| Stage | Action |
|-------|--------|
| `INIT` or missing | Proceed to Step 1 |
| `DOCS_DRAFT` | *"Documents already exist. Drop new files into DOCMENTS/ and reply **reimport** to overwrite, or use /review-* to edit sections."* |
| `DOCS_COMPLETE` | *"Docs phase complete. Use /parse-scope to generate tasks."* |
| Any build stage | *"Build already in progress. Run /reset to start fresh."* |

---

## Step 1 — Scan DOCMENTS/ for uploaded files

List all files in `DOCMENTS/`.

**Supported formats:**
| Format | How Claude reads it |
|--------|---------------------|
| `.pdf` | Read directly with the Read tool |
| `.docx` / `.doc` | Convert via `pandoc input.docx -o input-converted.md` then read. If pandoc not available, tell user to export to PDF or Markdown |
| `.html` | Read directly |
| `.md` / `.txt` | Read directly |

**Ignore** the 5 blank template files:
`project-brief.html`, `scope-of-work.html`, `architecture.html`,
`database.html`, `infrastructure.html`

Also ignore: `designs/` folder, `<slug>-*.html` filled outputs.

If **no user files found** after filtering:
> "No documents found in DOCMENTS/. Drop your brief, requirements, or
> any project document (PDF, Word, HTML, Markdown) into the DOCMENTS/
> folder and run /import-docs again."

Stop.

---

## Step 2 — Read all documents in full

Read every supported file before extracting anything.

While reading, build a source ledger:
- `file`: filename
- `type`: brief / SOW / requirements / system-design / flow-spec / other
- `trust`: authoritative / supplemental / reference
- `key_sections`: goals, features, architecture, flows, stack, integrations, out-of-scope

When multiple files conflict — the most detailed/specific source wins. Note conflicts as `INFERRED:`.

---

## Step 3 — Extract project information

Map document content to the 13 brief sections + downstream doc needs:

| Target | Extract |
|--------|---------|
| Project name, description, target audience | Section 1 |
| Problem + solution | Section 2 |
| Platforms + architecture style | Section 3 |
| User roles | Section 4 |
| Features (grouped by role) | Section 5 |
| Core business processes / flows | Section 6 |
| Business model | Section 7 |
| Integrations (payments, SMS, email, maps…) | Section 8 |
| Special requirements (offline, real-time, compliance…) | Section 9 |
| Out of scope (Phase 1) | Section 10 |
| Design / brand | Section 11 |
| Timeline + team | Section 12 |
| Tech stack, architecture style | Architecture doc |
| Data models, entities, relationships | Database doc |
| Environments, providers, CI/CD | Infrastructure doc |

Mark anything not found in the source as `TBD`.

**Architecture style:** derive from the document if mentioned
(monolith / hybrid / microservices / serverless). Default to `monolith` if
not specified. Then read `CONTEXT/architecture-styles/<style>.md` — it
shapes the generated documents.

**Derive slug** from the project name (kebab-case).

---

## Step 4 — Show extraction summary and confirm

Before writing anything, show:

```
Extraction summary:

  Project:      <name> (<slug>)
  Source files: <N> file(s) read
  Platforms:    <list>
  Style:        <architecture style>
  Roles:        <list>
  Features:     <count> features found
  Integrations: <list>
  Out of scope: <list>
  TBD fields:   <count> fields not found in documents

Gaps found:
  1. [HIGH] <gap description>
  2. [MEDIUM] <gap description>

Ready to generate all 5 documents? Reply yes to proceed,
or tell me what to correct first.
```

On **yes** → Step 5.
On correction → update and re-show summary.

---

## Step 5 — Write the brief

Fill `DOCMENTS/project-brief.html` template by replacing every
`<span class="ph">{{...}}</span>` with extracted values. Mark unfound
fields as `TBD`. Replace `{{PROJECT_NAME}}` with the slug.

Save to `DOCMENTS/<slug>-project-brief.html` v1.0.

Update `SESSION-STATE/SESSION-STATE.md`:
- `Stage:` → `BRIEF_APPROVED`
- Slug, Architecture style
- Artifacts: brief v1.0 + SHA-256 hash + today's date
- Audit log: `<ISO>  import-docs  INIT → BRIEF_APPROVED  wrote <slug>-project-brief.html v1.0`

Print: `✓ Project Brief written.`

---

## Step 6 — Auto-generate remaining 4 documents

Same sequence as `start-interview` Step 5. Execute in order:

**6a. Scope of Work**
Read brief + `DOCMENTS/scope-of-work.html` template + `CONTEXT/architecture-styles/<style>.md`
→ `DOCMENTS/<slug>-scope-of-work.html` v1.0
Print: `✓ Scope of Work`

**6b. System Architecture**
Read SoW + `DOCMENTS/architecture.html` + `CONTEXT/architecture-styles/<style>.md`
→ `DOCMENTS/<slug>-system-architecture.html` v1.0
Print: `✓ System Architecture`

**6c. Database Diagram**
Read Architecture Section 8 + `DOCMENTS/database.html`
→ `DOCMENTS/<slug>-database-diagram.html` v1.0
Print: `✓ Database Diagram`

**6d. Infrastructure Diagram**
Read Architecture Section 9 + `DOCMENTS/infrastructure.html`
→ `DOCMENTS/<slug>-infrastructure-diagram.html` v1.0
Print: `✓ Infrastructure Diagram`

---

## Step 7 — Transition and hand off

Update `SESSION-STATE/SESSION-STATE.md`:
- `Stage:` → `DOCS_DRAFT`
- All 5 artifacts with hashes
- Audit log: `<ISO>  import-docs  BRIEF_APPROVED → DOCS_DRAFT  4 docs auto-generated`

Print:

```
All 5 documents generated from your uploaded files.

  DOCMENTS/<slug>-project-brief.html
  DOCMENTS/<slug>-scope-of-work.html
  DOCMENTS/<slug>-system-architecture.html
  DOCMENTS/<slug>-database-diagram.html
  DOCMENTS/<slug>-infrastructure-diagram.html

Open them in your browser to review. TBD fields are marked in yellow.

To fill in any gaps:
  /review-brief <N>          edit brief section N
  /review-scope-of-work <N>
  /review-architecture <N>

When satisfied:
  /approve-docs
```

---

## Rules

- Never read blank template files as source content.
- Mark all gaps as `TBD` — never invent project details.
- All 5 documents must be written before Stage transitions to `DOCS_DRAFT`.
- If pandoc conversion fails, continue with other readable files and note the unconverted file.
- Templates in DOCMENTS/ are read-only — always write to `<slug>-*.html`.
