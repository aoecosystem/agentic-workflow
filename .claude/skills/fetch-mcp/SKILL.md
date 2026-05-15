---
name: fetch-mcp
description: Fetch machine-readable context from MCP URLs (Figma fallback, OpenAPI/Swagger, custom JSON/YAML/Markdown), normalize it for implementation, and cache concise artifacts under memory/mcp-cache/ with Fetched/TTL hours/Source hash headers. Trigger when Builder or figma-plugin-ingest needs a non-Figma-plugin source, when the user runs `/refresh-mcp` or says "refresh mcp", "refetch mcp", or when a task's MCP URL cache has expired per TTL table. Always writes normalized artifacts — never raw dumps.
---

# Skill: Fetch MCP

**Triggered by:** Builder (or `figma-plugin-ingest` fallback) when a task has a non-empty `MCP URL:` field

**Purpose:** Fetch machine-readable context (Figma/OpenAPI/custom), normalize it for implementation, and cache concise artifacts in `memory/mcp-cache/` for Builders and QA.

---

## Steps

### Step 1 — Check cache first (with freshness check)

Before fetching anything:
1. Determine cache filenames:
   - Core cache: `memory/mcp-cache/{feature-slug}-{type}.md`
   - Design artifact cache (if Figma): `memory/mcp-cache/{feature-slug}-design-artifacts.md`
2. If core cache exists and is non-empty:
   - Read the `Fetched:` header timestamp.
   - Compute age against the TTL table below.
   - If fresh: reuse. If stale: treat as missing and refetch.
3. If task requests a forced refresh (trigger phrase `refresh mcp`, or task
   has `Force refresh: true`), refetch and overwrite regardless of age.
4. If cache is missing or stale, continue to Step 2.
5. If the source URL in the task block differs from the cache header
   `Source URL:`, treat the cache as stale even if within TTL.

#### Cache TTL table

| Source type | TTL | Rationale |
|-------------|-----|-----------|
| Figma | 24 hours | design often iterates during build |
| OpenAPI / Swagger | 24 hours | API contracts drift less but still drift |
| Plugin artifacts (Figma) | 24 hours | matched to Figma TTL |
| Custom MCP | 12 hours | conservative default; override per task |

Any cache older than TTL is refetched. Any cache mismatched against task
URL is refetched. Cache files older than 30 days are refetched regardless
of other state.

### Step 2 — Identify source type

From URL/pattern:

| URL pattern | Type | Expected extraction |
|------------|------|---------------------|
| `figma.com/file/...` or `figma.com/design/...` | Figma file | frame map, components, tokens, constraints, breakpoints, state matrix |
| `figma.com/...node-id=...` | Figma node | focused node/component data + variants + local tokens |
| `*.openapi.json`, `*/openapi.json`, `*/swagger.json` | OpenAPI | endpoints, request/response schemas, auth requirements |
| custom MCP URL | custom | server-provided structures relevant to task scope |

### Step 3 — Fetch source payload

**Figma:**
- Primary: use official `plugin-figma-figma` MCP server.
- Call `get_design_context` and `get_metadata` for file/node scope.
- If node ID provided, prioritize node subtree and parent style references.
- Fallback only on primary failure: use Framelink MCP path to avoid blocking.

**OpenAPI:**
- Fetch and parse JSON/YAML.
- Extract only feature-relevant paths/tags.

**Custom:**
- Call MCP tool and keep scoped subset relevant to task.

If fetch fails:
- Mark task `blocked`.
- Record exact URL and error in task notes.
- Stop.

### Step 4 — Normalize extraction (codegen-grade)

Do not store raw payloads. Produce normalized sections.

#### For Figma (required sections)
1. **Frame hierarchy**
   - screen/frame names and node IDs
   - parent-child hierarchy
2. **Component inventory**
   - component names, variants, key props, instance usage
3. **Constraints and responsive hints**
   - auto-layout direction/spacing rules
   - min/max behavior and alignment constraints
   - breakpoint-relevant layout notes
4. **Token map**
   - colors (name/value/usage)
   - typography (family/size/weight/line-height)
   - spacing/radius/shadow/elevation
5. **State matrix**
   - required states by component: default, hover, focus, disabled, loading, error, empty (if present)
6. **Interaction notes**
   - critical interaction behavior referenced in design
7. **Asset references**
   - named icons/images used by the feature

#### Optional plugin artifact protocol
If task or scope includes plugin exports:
1. Read artifact links/paths from `Plugin export` fields.
2. Parse code snippets/CSS/token files.
3. Classify each fragment:
   - `compatible`: can be merged into scaffold
   - `partial`: useful structure only
   - `rejected`: incompatible quality/stack mismatch
4. Store classification in design artifact cache.
5. Add `Plugin artifact refs` entry path so Builder and QA can consume it.

#### For OpenAPI/custom
Keep existing endpoint/type extraction with feature scoping.

### Step 5 — Write cache files

Write normalized output to:
- `memory/mcp-cache/{feature-slug}-{type}.md`

If Figma, also write:
- `memory/mcp-cache/{feature-slug}-design-artifacts.md`
  - component hierarchy
  - token/state/breakpoint summaries
  - plugin artifact classification (if present)
- `memory/mcp-cache/{feature-slug}-plugin-artifacts.md`
  - artifact sources
  - compatibility classification
  - merge recommendations for target stack

Header format:
```markdown
# MCP Cache: [Feature] — [Type]
Fetched: [ISO-8601 timestamp, e.g. 2026-04-17T15:32:11Z]
TTL hours: [from TTL table]
Source URL: [url]
Source hash: [sha256 of the URL + any node-id params]
Mode: normalized
```

The `Source hash` makes URL-change detection trivial: any mismatch between
the hash in the header and the task block's current URL triggers a refetch.

### Step 6 — Confirm handoff

Return concise handoff message:
- cache files created/updated
- key sections available (tokens, states, breakpoints, components)
- whether plugin artifacts were merged, partial, or rejected
- extraction path used (official server vs fallback)

---

## Do not include

- Full raw payload dumps
- unrelated frames/endpoints
- binary blobs or opaque asset IDs without semantic names
- plugin code fragments that conflict with stack conventions

---

## Output

Implementation-ready MCP caches that Builders and the `figma-plugin-ingest` skill can consume directly.
