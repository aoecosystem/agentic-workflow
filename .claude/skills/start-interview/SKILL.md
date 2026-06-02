---
name: start-interview
description: Single entry point — asks 13 interview questions one at a time, writes the Project Brief, then automatically generates all 4 remaining documents (SoW, Architecture, Database, Infrastructure). When done, all 5 HTML documents are ready in DOCMENTS/. Trigger on `/start-interview`.
---

# Skill: start-interview

**Trigger:** `/start-interview`

**Purpose:** One command. Ask questions. All 5 documents ready.

The user runs `/start-interview` once. Claude asks 13 sections of
questions, one question per turn. When the last section is confirmed,
Claude writes the brief and immediately generates all 4 remaining
documents automatically — no further commands needed.

---

## Step 0 — Route by current Stage

Read `MEMEORIES/SESSION-STATE.md`.

| Stage | Action |
|-------|--------|
| `INIT` or file missing | Start fresh interview (→ Step 1) |
| `INTERVIEW` | Offer to resume: *"Interview in progress for `<slug>`, paused at section `<N>`. Reply **continue** to pick up, or **restart** to begin fresh."* |
| `BRIEF_DRAFT` | *"Brief is written but documents haven't been generated yet. Reply **generate** to auto-generate all 4 documents now, or **review** to edit the brief first."* |
| `DOCS_DRAFT` | *"All 5 documents are already ready in DOCMENTS/. Use /review-* to edit any section, or /approve-docs to finalize."* |
| `COMPLETE` | *"Project is complete. Run /reset to start a new project."* |

---

## Step 1 — Read templates

Before asking the first question:

1. Read `DOCMENTS/project-brief.html` end-to-end — know every section,
   placeholder, and table cell.
2. Read `MEMEORIES/SESSION-STATE.md` — set `Stage: INTERVIEW`.
3. Greet the user in one sentence, then ask **Section 1 Question 1**.

Opening message (friendly, concise):

> "Let's set up your project. I'll ask you a few questions and generate
> all 5 documents automatically when we're done.
>
> **Section 1 — Project Basics**
> What is the name of your project?"

---

## Step 2 — Interview (13 sections, one question at a time)

**Rules:**
- One question per turn. Wait for the answer before asking the next.
- Restate the answer in one sentence before moving on.
- Plain language — no engineering jargon unless the user uses it first.
- Never invent details. If the user says "I don't know" → mark `TBD`.
- After every confirmed answer, update `MEMEORIES/SESSION-STATE.md`
  (checkpoint — so resume works across sessions).

**The 13 sections:**

### Section 1 — Project Basics
Ask: project name, one-line description, target audience, primary language,
additional languages (or "English only"), currency, region/country.

Derive slug from project name (kebab-case). Confirm with user before saving.

### Section 2 — Problem & Solution
Ask: what problem does this solve? How does the product solve it?

### Section 3 — Platform & Architecture
Ask:
- Which platforms? (web app / mobile app / admin panel / API — can be multiple)
- Architecture style? Explain options simply:
  - **Monolith** — one backend, simple, fast to build (default for most projects)
  - **Hybrid** — monolith now, can split later (good if expecting growth)
  - **Microservices** — separate services per domain (complex, only for large teams)
  - **Serverless** — functions on cloud (good for variable traffic, no server management)
- Communication style? (REST / GraphQL / tRPC — default REST)

Default to **monolith** if unsure. Read `CONTEXT/architecture-styles/<style>.md`
after the user confirms — it shapes all downstream documents.

### Section 4 — User Roles
Ask: what types of users exist beyond the standard USER / ADMIN / SUPER_ADMIN?
Any custom roles? Multi-role users?

### Section 5 — Features
Ask: list the main features, grouped by who uses them. Aim for 10–20 features.
Prompt: "What can a regular user do? What can an admin do?"

### Section 6 — Core Business Process
Ask: walk me through the main workflow step by step (e.g. "user signs up →
creates a booking → pays → gets confirmation"). Capture 1–3 critical flows.

### Section 7 — Business Model
Ask: how does the product make money? (subscription / per-transaction /
freemium / free / TBD)

### Section 8 — Integrations
Ask: any third-party services? (payments, SMS, email, maps, video, analytics, etc.)

### Section 9 — Special Requirements
Ask: any special technical needs? (offline support, real-time features,
accessibility requirements, compliance like GDPR, performance targets)

### Section 10 — Out of Scope (Phase 1)
Ask: what is explicitly NOT being built in the first version?

### Section 11 — Design & Branding
Ask: do you have a design? (Figma link / screenshots / "Claude will design it" /
"no design yet"). Any brand colors, logo, font preferences?

### Section 12 — Timeline & Team
Ask (optional — mark TBD if unknown): target launch date, team size,
rough budget range.

### Section 13 — AI Agent Instructions
Auto-fill this section with the standard AI workflow instructions.
Do NOT ask the user about this section.

---

## Step 3 — Show brief summary and confirm

After all 12 user sections are answered, show a compact summary:

```
Here's your project summary:

  Project:     <name> (<slug>)
  Platforms:   <list>
  Style:       <architecture style>
  Users:       <roles>
  Key features: <5-6 bullet points>
  Integrations: <list>
  Out of scope: <list>

Ready to generate all 5 documents? Reply yes to proceed,
or tell me what to change.
```

On **yes** → proceed to Step 4.
On change request → edit the specific answer and re-show the summary.

---

## Step 4 — Write the brief

Fill `DOCMENTS/project-brief.html` by replacing every
`<span class="ph">{{...}}</span>` with real values from the interview.
Mark unknowns as `TBD`. Replace `{{PROJECT_NAME}}` with the slug.

Save to `DOCMENTS/<slug>-project-brief.html` v1.0.

Update `MEMEORIES/SESSION-STATE.md`:
- `Stage:` → `BRIEF_APPROVED`
- Artifacts: add brief as approved v1.0 + SHA-256 hash + today's date
- Audit log: `<ISO>  start-interview  INTERVIEW → BRIEF_APPROVED  wrote <slug>-project-brief.html v1.0`

Print one line: `✓ Project Brief written.`

---

## Step 5 — Auto-generate all 4 documents

Execute in sequence. Print one line per step. No user input needed.

**Print before starting:**
```
Generating your documents — this takes about a minute...
```

### 5a. Scope of Work
- Read approved brief + `DOCMENTS/scope-of-work.html` template
- Read `CONTEXT/architecture-styles/<style>.md` for style rules
- Generate all 10 phases — derive from brief answers
- Save to `DOCMENTS/<slug>-scope-of-work.html` v1.0
- Print: `✓ Scope of Work`

### 5b. System Architecture
- Read SoW (just generated) + `DOCMENTS/system-architecture.html` template
- Read `CONTEXT/architecture-styles/<style>.md`
- Generate all 9 sections (1-7 architecture, 8 DB schema, 9 infrastructure)
- Save to `DOCMENTS/<slug>-system-architecture.html` v1.0
- Print: `✓ System Architecture`

### 5c. Database Diagram
- Read Architecture Section 8 (entities already defined)
- Read `DOCMENTS/database-diagram.html` template
- Generate all 6 sections — entities must match Architecture Section 8 exactly
- Save to `DOCMENTS/<slug>-database-diagram.html` v1.0
- Print: `✓ Database Diagram`

### 5d. Infrastructure Diagram
- Read Architecture Section 9 (infra already defined)
- Read `DOCMENTS/infrastructure-diagram.html` template
- Generate all 9 sections — topology must match Architecture Section 9.6 exactly
- Save to `DOCMENTS/<slug>-infrastructure-diagram.html` v1.0
- Print: `✓ Infrastructure Diagram`

---

## Step 6 — Transition and hand off

Update `MEMEORIES/SESSION-STATE.md`:
- `Stage:` → `DOCS_DRAFT`
- `Resume hint:` → `All 5 documents ready. Review in browser or run /approve-docs.`
- Artifacts: add all 4 generated docs as draft v1.0 with hashes
- Audit log: `<ISO>  start-interview  BRIEF_APPROVED → DOCS_DRAFT  4 docs auto-generated`

Print final message:

```
All 5 documents are ready. Open them in your browser to review:

  DOCMENTS/<slug>-project-brief.html
  DOCMENTS/<slug>-scope-of-work.html
  DOCMENTS/<slug>-system-architecture.html
  DOCMENTS/<slug>-database-diagram.html
  DOCMENTS/<slug>-infrastructure-diagram.html

Each document has collapsible sections — click a heading to expand.

To edit any section:
  /review-scope-of-work <N>
  /review-architecture <N>
  /review-database <N>
  /review-infrastructure <N>

When satisfied with everything:
  /approve-docs
```

---

## Error handling

If any document generation step fails (e.g. can't parse SoW):
1. Print the specific error.
2. Leave Stage at `BRIEF_APPROVED`.
3. Tell the user: *"Brief is saved. Run /start-interview again to retry
   document generation, or run /approve-brief to retry manually."*

---

## Rules

- One question per turn. Never ask multiple questions at once.
- Never invent project details. TBD is always acceptable.
- All 5 documents must be written before Stage transitions to DOCS_DRAFT.
- Each document feeds the next — never skip or reorder steps 5a-5d.
- Templates in DOCMENTS/ are read-only — always write to `<slug>-*.html`.
