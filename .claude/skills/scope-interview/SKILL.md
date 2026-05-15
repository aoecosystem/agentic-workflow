---
name: scope-interview
description: Interview the user section-by-section to fill a Project Brief from scratch when no SOW or written documents exist, then auto-derive a Scope of Work in markdown into inputs/ ready for `import docs`. Trigger when the user says "interview me", "scope interview", "no docs", "let's start a new project", or otherwise indicates they have an idea but no written SOW. Do NOT trigger when inputs/ already contains usable source documents — recommend `import docs` instead.
---

# Skill: Scope Interview

**Trigger:** User says `interview me` or `scope interview` (also: "no docs",
"let's scope this", "I have an idea but no document").

**Purpose:** Walk the user through a structured Q&A to capture project
intent when no Scope of Work exists yet. Produce two markdown artifacts in
`inputs/` so the rest of the workflow (`import docs` → `parse scope` →
`start build`) runs unchanged.

**Outputs (markdown, not HTML or PDF — token-efficient):**
- `inputs/project-brief.md` — interview answers, structured.
- `inputs/scope-of-work.md` — derived SOW, ready for `import docs`.

---

## Pre-flight checks

Before starting the interview, verify:

1. `inputs/` exists. If not, create it.
2. List files in `inputs/`. If usable source documents are
   already present (`.pdf`, `.docx`, `.md`, `.html`), STOP and tell the
   user:
   > "I see existing documents in `inputs/`. Did you want
   > to run `import docs` instead? Reply 'yes' to import them, or
   > 'continue interview' to start a fresh interview."
3. If `state/SCOPE.md` is already filled (Project Overview has a name and
   description), STOP and tell the user:
   > "`state/SCOPE.md` already has content. Running `scope interview` will
   > eventually overwrite it. Reply 'continue' to proceed, or
   > 'cancel' to stop."

---

## Interview structure

Ask **one section at a time, one question per turn.** Wait for the user's
answer before moving on. Never flood the user with all questions at once.

After each answer, restate it back briefly (one sentence) and ask the
next question. This builds confidence the agent is listening.

### Section 1 — Project identity

Q1. "What's the name of the project? Use a short slug (e.g. `bron-go`,
`acme-crm`)."
Q2. "In one or two sentences, what does this product do, and who is it
for?"

### Section 2 — Vision

Q3. "What's the core problem you're solving? What does the user struggle
with today that this product fixes?"
Q4. "What's the desired outcome? When this product exists, what does the
user's life look like?"
Q5. "Who is the primary user? Be specific (role, context, what they
care about)."

### Section 3 — Core features (one at a time)

Q6. "List the top 3-7 features the user can do with this product. Just
names for now; we'll detail them next."

Then for **each** named feature:

Q7a. "Feature: {name}. Walk me through what the user does. Start to
finish, in plain English."
Q7b. "What screens or pages does this feature need?"
Q7c. "What data does this feature read or write? Just names — User,
Item, Order, etc. We'll model fields later."

### Section 4 — Stack and architecture

Q8. "Do you have a preferred tech stack? (e.g. Next.js + Postgres,
React Native + tRPC.) If unsure, say 'recommend' and I'll suggest one
based on the features."
Q9. "Where will this run? (Vercel, Railway, AWS, self-hosted, mobile
app stores.)"
Q10. "Authentication: do users sign in? If yes, how? (email/password,
Google OAuth, magic link, none.)"
Q11. "Any third-party services you already know you'll need? (Stripe,
SendGrid, S3, Twilio, etc.) If none yet, say 'none'."

### Section 5 — Constraints and non-goals

Q12. "Hard constraints: anything the product MUST do or MUST NOT do?
(e.g. WCAG accessibility, sub-1s load on 3G, must work offline.)"
Q13. "Out of scope: what should we NOT build in this phase? (e.g.
admin panel, mobile app, multi-tenancy.)"
Q14. "Timeline expectation: rough target — days, weeks, months?"

### Section 6 — Design

Q15. "Do you have any design references? Options:
  - Figma file URL → say 'figma' and paste it
  - Screenshots / sketches → say 'images' (you'll attach them later)
  - No design yet → say 'none' (the workflow will generate UI scaffolds)"

---

## Step — Show the brief draft

After Section 6 ends, generate `inputs/project-brief.md` IN MEMORY
(don't write yet) using this structure:

```markdown
# Project Brief — <Project Name>

## 1. Identity
- Name: <name>
- Slug: <slug>
- One-line description: <one-line>

## 2. Vision
- Problem: <Q3>
- Desired outcome: <Q4>
- Primary user: <Q5>

## 3. Core Features
### Feature: <Name>
- User flow: <Q7a>
- Screens: <Q7b>
- Data touched: <Q7c>

(repeat per feature)

## 4. Stack
- Preferred stack: <Q8>
- Deployment target: <Q9>
- Authentication: <Q10>
- Third-party services: <Q11>

## 5. Constraints
- Hard constraints: <Q12>
- Out of scope: <Q13>
- Timeline: <Q14>

## 6. Design
- Design source: <Q15>
```

Show it to the user inline. Ask:

> "Here's your project brief. Reply 'save' to write it to
> `inputs/project-brief.md`, or tell me what to change."

Iterate on user feedback until they reply `save`. Then write the file.

---

## Step — Derive the Scope of Work

Once the brief is saved, automatically derive an SOW from it. Do not ask
new questions. The SOW should expand on the brief by inferring obvious
details and structuring them in the format `import docs` expects.

Generate `inputs/scope-of-work.md` IN MEMORY using this structure:

```markdown
# Scope of Work — <Project Name>

## 1. Project Overview
- Name: <name>
- Description: <one-line + 1-2 sentence elaboration>
- Goals:
  - <derived from desired outcome>
  - <derived from problem>
  - <derived from primary user>

## 2. System Architecture
- Frontend: <inferred from stack + features>
- Backend: <inferred from stack>
- Database: <inferred from stack>
- Auth: <inferred from Q10>
- Third-party services: <inferred from Q11>
- Deployment target: <inferred from Q9>

## 3. Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | <stack frontend> |
| Backend | <stack backend> |
| Database | <stack database> |
| ORM / Query layer | <best-fit ORM for stack> |
| Auth | <derived> |
| Styling | <best-fit styling for stack> |
| Testing | <best-fit testing for stack> |
| CI / CD | <best-fit CI for deployment target> |

## 4. MCP URLs
| Type | URL | Used by feature |
|------|-----|----------------|
| Design (Figma) | <Q15 if figma> | <feature names> |

## 5. Feature Breakdown

### Feature: <Name>
- Description: <user flow expanded>
- Screens / Pages:
  - <Q7b items, each with a one-line action description>
- API Endpoints:
  - <inferred from Q7c data + flow verbs>
- Data Models:
  - <Q7c entities with inferred fields>
- MCP URL: <if Figma reference applies>
- Depends on features: <derived from logical order>

(repeat per feature)

## 6. Out of Scope
- <Q13 items>

## 7. Non-Functional Requirements
- Performance: <Q12 if mentioned>
- Accessibility: <Q12 if mentioned>
- Security: <derived from Q10 auth choice>
- Error handling: <default — { error: string, code: string } unless overridden>
- Other: <Q12 leftovers>
```

Show it to the user inline. Ask:

> "Here's the auto-derived Scope of Work. Reply 'save' to write it to
> `inputs/scope-of-work.md`, or tell me what to change."

Iterate on user feedback until they reply `save`. Then write the file.

---


### Section 7 — Page Inventory (auto-derived, runs LAST)

After the user confirms the SOW draft, derive the Page Inventory
automatically. Do **not** ask the user new questions — infer from the
features, stack, and deployment target already captured.

Steps:

1. **Detect project type** from the stack and deployment target:
   - mobile  → React Native / Flutter / Swift / Kotlin / Expo, OR App
              Store / Play Store / Expo Go in deployment.
   - web     → Next.js / React / Vue / Svelte / Angular, OR Vercel /
              Netlify / Cloudflare / Railway / self-hosted.
   - both    → both signals present.

2. **Generate page IDs** in `<feature-slug>-<screen-slug>` kebab-case
   format. Stable for the project lifetime.

3. **Skip platform-irrelevant pages**:
   - Web-only project → omit mobile-specific rows (no onboarding
     carousel, no native splash).
   - Mobile-only project → omit marketing pages, focus on app screens.
   - Cross-platform → include both, mark each row's platform.

4. **Auth boundary**: derive from feature description — `public` for
   landing/auth/marketing, `private` for everything that requires sign-in.

5. **Description**: one short sentence per page.

Render as `## 8. Page Inventory` in `inputs/scope-of-work.md` with the
five-column table:

| Page ID | Page Name | Platform | Auth | Description |

Show the table to the user inline. Ask:

> "Here's the auto-derived Page Inventory. Reply 'save' to write it,
> or tell me which pages to add, remove, or rename."

After save, the page IDs become the universal join key for design
artifacts (Figma frame names, screenshot filenames, Claude Design
HTML files).

---

## Step — Hand off

After both files are saved:

1. Confirm the artifacts:
   ```
   Saved:
     inputs/project-brief.md
     inputs/scope-of-work.md
   ```
2. Tell the user the next command:
   > "Now run `import docs` and I'll fill `state/SCOPE.md` from these. Then
   > `parse scope` to generate tasks, and `start build` when you're
   > ready."
3. Stop. Do NOT auto-run `import docs` — let the user trigger it.

---

## Rules

- One question per turn. Never paste the whole interview at once.
- Never invent answers. If the user says "I don't know" for a section,
  mark it as `INFERRED:` in the brief with your best guess plus a note
  asking them to revisit.
- Markdown only. No HTML, no PDF — those waste tokens on round-trips.
- Save files only after explicit `save` confirmation. Always show
  drafts inline first.
- Stack inference must be conservative. Default to popular,
  well-supported choices: Next.js + TypeScript + Postgres for web,
  React Native + Expo + tRPC for mobile, Node.js + Fastify + Postgres
  for API-only.
- If the user has design assets (Figma URL, screenshots), record the
  reference but defer detailed ingestion to `figma ingest` later.

---


## Templates

Copy structure from:
- `templates/project-brief.md`
- `templates/scope-of-work.md`

These are the canonical empty scaffolds. Do not modify them. Save the
filled versions to `inputs/project-brief.md` and `inputs/scope-of-work.md`.

## Output

Two markdown files in `inputs/`, ready for `import docs`. The user is
told the next trigger to run.
