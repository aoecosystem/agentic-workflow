---
description: Generate or update OpenAPI / tRPC / GraphQL contract artifacts under memory/contracts/ so backend and client Builders share a single source of truth.
---

Run the `api-contract` skill. For every full-stack feature in
`state/SCOPE.md`, generate a contract artifact in
`memory/contracts/<feature-slug>.<ext>`. Format auto-detected from
`memory/STACK-GUIDANCE.md`:

- REST → OpenAPI 3.1 YAML
- tRPC → TypeScript schema
- GraphQL → SDL
- gRPC → Protobuf

Update `Contract refs.Integration status` on related task blocks. Do
not change to `complete` — only QA does that.

Print a diff summary (added / changed / deprecated) before stopping.
