# Pages

<!--
Agent-maintained. Single source of truth for the project's page inventory.
Mirrors `SCOPE.md` Section 8 (Page Inventory) plus implementation status.

The page ID is the universal join key:
  - Figma frame name MUST equal the page ID (or be linked via node ID)
  - Screenshot filename MUST be <page-id>.png|jpg
  - Claude Design HTML export MUST be <page-id>.html

Writers:
  - `import-docs` / `scope-interview`: initial generation from SCOPE.md section 8
  - `delta-scope`: when pages are added, removed, or renamed
  - `qa`: flips `Implemented: yes` and writes the `Task` ID after the UI task is `done`

Builders read this BEFORE creating any new page to confirm the page ID,
platform, and auth boundary.
-->

## Index

| Page ID | Page Name | Platform | Auth | Implemented | Task | Notes |
|---------|-----------|----------|------|-------------|------|-------|
<!-- (empty — generated on `import docs` or `scope interview`) -->

---

## Conventions

- **Page ID format:** `<feature-slug>-<screen-slug>`, kebab-case, stable.
- **Platform:** `web` | `mobile` | `both`.
- **Auth:** `public` | `private`.
- **Implemented:** `no` (default), `yes` (set by QA on `done`).
- **Task:** the TASK-XX ID that implemented this page.
- **Notes:** short free-text — design source path, route, or anything reviewers should know.

## Rename rule

Page IDs are stable. To rename a page, run `delta scope` — it will:
1. Mark the old ID as `obsolete`.
2. Create the new ID alongside.
3. Surface every artifact that referenced the old ID (Figma frames,
   screenshot files, codegen caches, task blocks) so you can update them
   in one pass.
