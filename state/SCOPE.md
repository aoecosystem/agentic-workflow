# Project Scope

<!--
INSTRUCTIONS
============
Fill in every section below. The more detail you provide, the better the generated tasks.
Sections marked [REQUIRED] must be filled before running "parse scope".
Sections marked [OPTIONAL] improve task quality but can be left blank.

Delete these instruction comments when done.
-->

---

## 1. Project Overview [REQUIRED]

**Name:**
<!-- e.g. "TaskFlow" -->

**Description:**
<!-- 1–2 sentences: what does this product do and who is it for? -->

**Goals:**
<!-- Bullet list of 3–5 outcomes you want after the project is built. -->
-
-
-

---

## 2. System Architecture [REQUIRED]

<!--
Describe the high-level structure. Answer:
- Is it a monolith, monorepo, or separate frontend/backend repos?
- How does the frontend communicate with the backend? (REST, GraphQL, tRPC, etc.)
- Where is data stored? (PostgreSQL, MongoDB, SQLite, etc.)
- How is auth handled? (JWT, sessions, OAuth, third-party like Clerk/Auth0)
- Any third-party services? (Stripe, SendGrid, S3, etc.)
- Where does it deploy? (Vercel, Railway, AWS, self-hosted, etc.)

A paragraph or bullet list is fine. No need for a diagram.
-->

**Frontend:**

**Backend:**

**Database:**

**Auth:**

**Third-party services:**

**Deployment target:**

---

## 3. Tech Stack [REQUIRED]

<!--
One entry per layer. Be specific about versions only if it matters.
Example: Frontend: React 18 + TypeScript, Vite, Tailwind CSS, React Query
-->

| Layer | Technology |
|-------|-----------|
| Frontend | |
| Backend | |
| Database | |
| ORM / Query layer | |
| Auth | |
| Styling | |
| Testing | |
| CI / CD | |

---

## 4. MCP URLs [OPTIONAL — add per feature in section 5, or list globally here]

<!--
Paste URLs for external references the agent should fetch before building:
- Figma file URL → agent fetches component structure, layout, tokens
- OpenAPI / Swagger URL → agent fetches endpoint shapes
- Custom MCP server URL → agent fetches whatever that server exposes

Format:
- Design system: https://figma.com/file/...
- API spec: https://api.myapp.com/openapi.json
-->

| Type | URL | Used by feature |
|------|-----|----------------|
| Design (Figma) | | |
| API spec (OpenAPI) | | |
| Component library | | |
| Design token source | | |
| Plugin export (optional) | | |

---

## 5. Feature Breakdown [REQUIRED]

<!--
One block per feature. Copy-paste the template below for each feature.
The agent uses this to generate one or more tasks per feature.

Feature dependencies tell the orchestrator what must be built first.
MCP URL here overrides the global table above for this feature.
-->

---

### Feature: [Name]

**Description:**
<!-- What does this feature do? Who uses it? -->

**Screens / Pages:**
<!--
List each screen. For each: name + what the user can do on it.
  - Login screen: user enters email + password, submits, sees error or redirects
  - Dashboard: shows list of items, can filter, click to open detail
-->
-

**API Endpoints:**
<!--
  - POST /auth/login — body: { email, password } → returns { token, user }
  - GET /items — query: { page, filter } → returns { items[], total }
-->
-

**Data Models:**
<!--
  - User: id, email, passwordHash, createdAt
  - Item: id, title, ownerId, status, createdAt
-->
-

**MCP URL:**
<!-- Leave blank if none. -->

**Figma node IDs (optional):**
<!-- e.g. 12:44 (Login screen), 18:5 (Primary Button component) -->

**Plugin export link/path (optional):**
<!-- URL or repo path to plugin-generated code/design tokens -->

**Design system token source (optional):**
<!-- e.g. "Figma styles in Design System v2" or tokens.json URL -->

**Depends on features:**
<!-- e.g. "Project scaffold, Auth" or "none" -->

---

### Feature: [Name]

**Description:**

**Screens / Pages:**
-

**API Endpoints:**
-

**Data Models:**
-

**MCP URL:**

**Figma node IDs (optional):**

**Plugin export link/path (optional):**

**Design system token source (optional):**

**Depends on features:**

---

<!-- Add more feature blocks as needed by copying the template above -->

---

## 6. Out of Scope [OPTIONAL]

<!--
Explicitly list what is NOT being built to prevent the agent from inventing extras.
  - Admin panel
  - Mobile app
  - Multi-tenancy
-->
-

---

## 7. Non-Functional Requirements [OPTIONAL]

<!--
Any hard constraints the agent must follow when building.
-->

**Performance:**
<!-- e.g. "List pages must load in < 1s on 3G" -->

**Accessibility:**
<!-- e.g. "WCAG 2.1 AA for all UI components" -->

**Security / Auth rules:**
<!-- e.g. "All API routes except /auth/* require a valid JWT" -->

**Error handling:**
<!-- e.g. "All API errors return { error: string, code: string }; UI shows toast on failure" -->

**Other:**
