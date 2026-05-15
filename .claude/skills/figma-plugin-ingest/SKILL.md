---
name: figma-plugin-ingest
description: Plugin-first Figma-to-code prep. Fetch full design context via the plugin-figma-figma MCP (tokens, assets, screens, states, variants, responsive behavior), merge any plugin-exported codegen artifacts, produce stack-mapped UI scaffolds, and auto-inject design fields on UI tasks in state/TASKS.md. Trigger when the user runs `/figma-ingest` or says "figma ingest", "design codegen", or when a UI task has a Figma MCP URL and needs design context before Builder can start. Never treat device-preview wrappers as implementation-ready context; fetch the concrete leaf content frame or mark the task blocked.
---

# Skill: Figma Ingest (Unified)

**Trigger:** User says `figma ingest` (or legacy alias `design codegen`)

**Purpose:** Single source of truth for Figma-to-code prep. Fetch full design context from `plugin-figma-figma`, extract tokens/assets/screens/states, merge plugin codegen artifacts, generate implementation-ready UI scaffolds, and populate task design fields in `state/TASKS.md`.

---

## Inputs

- One or more UI tasks in `state/TASKS.md` with a Figma `MCP URL`
- Optional feature metadata from the 5 deliverable HTMLs (node IDs, plugin export links, token source)
- Target stack from the 5 deliverable HTMLs tech stack section
- Optional selected task ID for targeted ingest

---

## URL parsing rules

For Figma URLs, extract:
- `fileKey` from `/design/{fileKey}/...` or `/board/{fileKey}/...`
- `nodeId` from `node-id=` query (convert `-` to `:` when needed)
- If branch URL is used (`/design/{fileKey}/branch/{branchKey}/...`), use `branchKey` as file key

If `node-id` is missing for screen-level tasks, mark task `blocked` and request explicit node IDs.

---

## Steps

### Step 1 — Select tasks to ingest

1. Read `state/TASKS.md`.
2. Select UI tasks with a Figma MCP URL (or explicit task requested by user).
3. Skip tasks already containing fresh artifact fields unless forced refresh requested.

### Step 2 — Fetch official Figma context (required)

Use `plugin-figma-figma` first:
1. `get_design_context` using `fileKey` + `nodeId` (or best available selection)
2. `get_metadata` for component/token/state hierarchy
3. Optional helpers as needed:
   - screenshot retrieval for visual baseline refs
   - figjam retrieval if design info lives there

Only if official server fails, fallback to existing secondary path (`fetch-mcp` fallback logic). If both fail, mark task `blocked` with the exact URL and error.


### Step 2.5 — Frame name lookup by Page ID (preferred)

When a UI task carries a `Page ID` (from `memory/PAGES.md`), prefer
matching the Figma frame by **frame name = page ID** before falling
back to numeric node ID lookup.

1. Call `get_metadata` to list all frame names in the file.
2. For each task's page ID, find the frame whose name (case-insensitive,
   ignoring whitespace) equals the page ID.
3. If found → use that frame as the implementation target. Record both
   the page ID and the resolved node ID in the cache file.
4. If not found → fall back to the explicit `Figma node IDs` field
   from the 5 deliverable HTMLs. If that is also missing, mark the task `blocked`
   with: "Figma frame for page-id `<page-id>` not found. Either rename
   the frame in Figma to `<page-id>` or supply an explicit node ID in the 5 deliverable HTMLs."

Frame-name lookup is the canonical join key. Designers are encouraged
to name their frames with page IDs so the workflow stays decoupled
from Figma's internal numeric IDs (which change when frames are
duplicated).

---

### Step 3 — Extract complete design buckets (non-optional)

Extract and normalize all of the following:

1. **Screen inventory**
   - all target screens/frames with node IDs
   - canonical screen names for task use
   - classify each node as `content frame` or `device preview`
   - when a device preview wraps app content, record the inner content frame that should drive implementation
2. **Typography**
   - families, sizes, weights, line-heights, letter spacing, token/variable bindings
3. **Color system**
   - semantic colors, aliases, raw values, token/variable bindings
4. **Spacing, radius, shadows/elevation**
   - full token map + usage hints
5. **Assets**
   - icons/images/illustrations per screen with stable names and usage notes
6. **Component + variant matrix**
   - variants, required props, interactive states
7. **Responsive behavior**
   - breakpoints, auto-layout constraints, per-screen adaptation rules
8. **Content map**
   - key text strings or placeholders needed for accurate UI scaffold

If any required bucket is missing for a target screen, mark task `blocked` with missing frame/node IDs and requested follow-up.
If a selected node is only a sparse parent/section outline or only a device preview wrapper, do not treat it as implementation-ready context. Fetch the concrete leaf screen node(s) or mark the task `blocked` with the required node IDs.

### Step 4 — Parse plugin/code artifacts

If plugin-generated assets are available from scope/task:
- Parse code snippets, style exports, token JSON, component mappings
- Classify each artifact:
  - `compatible`: directly reusable in target stack
  - `partial`: structural hints only
  - `rejected`: poor quality or incompatible

Never trust plugin output blindly. Normalize and validate first.

### Step 5 — Generate unified artifacts (design + codegen)

Create deterministic normalized output per feature:

1. **Design structure**
   - frame hierarchy + node IDs
   - content-frame vs device-preview classification
   - component tree + variants/props
2. **Token map**
   - colors, typography, spacing, radius, shadows
3. **Interaction/state matrix**
   - default/hover/focus/disabled/loading/error/empty
4. **Responsive constraints**
   - breakpoints and layout behavior
5. **Assets manifest**
   - assets per screen and expected placement/size constraints
6. **Plugin artifact report**
   - compatible/partial/rejected classifications
7. **UI code scaffold**
   - file map for implementation
   - component skeletons with stack-mapped token bindings
   - screen composition skeletons preserving Figma hierarchy for content frames only
   - notes for fidelity-critical constraints

The scaffold must prioritize Figma parity and reuse accepted plugin-codegen fragments when compatible with project stack. Never recreate status bars, home indicators, phone shells, or other device preview chrome as app widgets unless the task explicitly scopes app-shell chrome.

### Step 6 — Write cache artifacts

Write:
- `memory/mcp-cache/{feature-slug}-figma.md`
- `memory/mcp-cache/{feature-slug}-codegen.md`
- `memory/mcp-cache/{feature-slug}-plugin-artifacts.md`
- `memory/mcp-cache/{feature-slug}-assets.md`

Each file must include:
- source URL
- node refs
- fetch timestamp
- resolved target stack

### Step 7 — Auto-inject task fields

For each processed UI task, update or append these fields:
- `Design source: Figma (plugin-figma-figma)`
- `Codegen artifact: memory/mcp-cache/{feature-slug}-codegen.md`
- `Visual baseline refs: fileKey=..., nodeId=..., frame=...`
- `Screen MCP URLs:`
  - `ScreenName: https://www.figma.com/design/{fileKey}/...?...node-id={node-id}`
- `Design checklist:`
  - token usage fidelity
  - typography fidelity
  - asset parity by screen
  - state parity
  - responsive parity
  - accessibility parity
  - no duplicate device chrome (status bar, notch, home indicator)
- `Plugin artifact refs: memory/mcp-cache/{feature-slug}-plugin-artifacts.md (compatible|partial|rejected)`
- `Asset refs: memory/mcp-cache/{feature-slug}-assets.md`

Field updates must be merge-only for design fields. Do not overwrite task title, dependency, assignee, or status.

### Step 8 — Quality gates before handoff

Before marking ingest complete, verify:
1. Every target screen has a node ID and a screen-level MCP URL entry.
2. Every implementation target resolves to a concrete leaf content frame, not only a sparse section or device preview wrapper.
3. Token maps include color + typography + spacing + radius + shadow.
4. Asset manifest is present and linked from task fields.
5. Codegen artifact includes a concrete file map and component/screen scaffold.
6. Plugin artifact classification is present with clear accepted/rejected rationale.
7. Device preview chrome is identified and excluded from implementation scaffolds unless explicitly required by scope.

If any check fails, do not silently proceed; mark task `blocked` with exact missing pieces.

### Step 9 — Handoff contract

After task enrichment:
1. Confirm all required fields exist in the task.
2. Notify orchestrator this task is ready for Builder.
3. If extraction is incomplete, mark task `blocked` with exact missing nodes/artifacts.

---

## Output

UI tasks with complete Figma extraction, stack-mapped codegen scaffolds, screen MCP URL mappings, and validated task fields ready for Builder and QA.
