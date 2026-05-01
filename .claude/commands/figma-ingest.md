---
description: Plugin-first Figma extraction for UI tasks (tokens, screens, states, assets, scaffolds)
---

Run the `figma-plugin-ingest` skill. For each UI task in `state/TASKS.md` with a Figma MCP URL, fetch complete design context via the `plugin-figma-figma` MCP (screens, typography, colors, spacing/radius/shadow, assets, variant matrix, responsive behavior), parse any plugin-exported codegen artifacts, generate stack-mapped UI scaffolds, and auto-inject design fields into the task block. Mark tasks `blocked` if the target node is only a device-preview wrapper or if required design buckets are missing. $ARGUMENTS
