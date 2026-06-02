---
description: Force-refetch MCP context ignoring TTL (Figma / OpenAPI / custom)
---

Run `fetch-mcp` (or `figma-plugin-ingest` for Figma URLs) with `Force refresh: true`. Ignore cache TTL, refetch the source, recompute the Source hash, and rewrite the artifact in `MEMEORIES/mcp-cache/`. Use this when a design or API source has changed but the cache is still within TTL. $ARGUMENTS
