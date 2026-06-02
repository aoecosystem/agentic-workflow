# Profile schema (HARD CONTRACT)

Every style file in this folder MUST contain these 6 sections in this
order. Skills parse styles by section heading, so the heading text and
order matter.

---

# Profile: <name>

## Description

One paragraph (3-5 sentences) explaining the architecture style in plain
language. Audience: project manager, not just engineer. Include a one-line
summary of "best fit" use cases.

## Default tech additions

A bullet list of infrastructure / dependencies the style auto-injects
into the SoW Phase 6 Tech Stack and Infrastructure Section 5.

Format:
- **Category:** specific tool (default) | alternative options — purpose

Example:
- **Message broker:** Kafka (default) | RabbitMQ — async event delivery between services
- **Cache:** Redis (required) — session cache + rate limiting

## Folder structure

A code block showing the per-project folder layout (under `apps/<slug>/`
or wherever the build engine writes code). Use indentation, comments
inline. This is what `build-scope-of-work` puts into Phase 9 of the SoW.

## Database approach

A short paragraph + rules describing:
- How many DBs (one shared / one per service / serverless DB)
- Foreign key rules (allowed within service / forbidden across services)
- Migration tool defaults
- Cross-service data sharing pattern (FK / ID-only / API call)

## Communication style

How services / modules talk to each other:
- Sync: direct import / REST / gRPC / GraphQL
- Async: in-process EventEmitter / Kafka / RabbitMQ / SNS+SQS / EventBridge
- Boundary discipline: loose / strict-via-interfaces / network-only

## Mermaid diagram patterns

Conventions for the 3 diagram HTMLs:
- **System architecture diagram** — how to group services in subgraphs
- **Database diagram** — single ERD or grouped-by-service
- **Infrastructure diagram** — what nodes appear (broker, cache, gateway, etc.)

Specific syntax conventions (subgraph names, classDef colors, linkStyle
for async edges) so all 3 diagrams in a project look consistent.

---

## Naming rules

- File name: lowercase, no spaces, kebab-case if multi-word — e.g.
  `monolith.md`, `microservices.md`, `serverless.md`, `web3.md`.
- The `# Profile: <name>` heading at the top must match the filename.
- All 6 sections are required even if a section is short.

## Read order

`build-*` skills read the style in order: Description → Tech additions
→ Folder structure → DB approach → Comm style → Mermaid patterns. Don't
change the section order or skills will fail to find what they need.
