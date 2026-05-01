# system-architecture/styles/

Architecture styles. The user picks one in brief Section 3, and every
`build-*` skill reads the matching style to shape its output.

## Files

| File | Architecture style | Best fit |
|------|--------------------|----------|
| `monolith.md` | Single deploy, single DB, all features in one repo | Small/medium projects, single team, fast time-to-ship |
| `hybrid.md` | Modular monolith with extraction-ready boundaries | Most projects — start as monolith, ready to extract services later |
| `microservices.md` | Independent services, DB per service, Kafka required | Large projects, multiple teams, real distributed-system needs |
| `serverless.md` | Functions on AWS Lambda / Cloudflare Workers / Vercel | Spiky traffic, pay-per-request, JAMstack |
| `_schema.md` | Required structure every style must follow | Reference for adding new styles |

## How it works

1. The user picks an architecture style during the `/start-project` interview.
2. The choice is saved in brief Section 3 and `SESSION-STATE.md`.
3. When `/build-scope-of-work` (and the 3 diagram skills) run, they read
   `system-architecture/styles/<style>.md` and apply its rules to the generated output:
   - Phase 6 Tech Stack auto-includes the style's required infrastructure
   - Phase 9 Folder Structure follows the style's pattern
   - Phase 3 Database approach matches the style (single vs per-service)
   - Phase 5 Events approach matches (in-process vs Kafka/RabbitMQ)
   - The Mermaid diagrams in `<slug>-system-architecture.html`,
     `<slug>-database-diagram.html`, and `<slug>-infrastructure-diagram.html`
     all follow the style's diagram convention.

## Default

If the user picks nothing, the brief template defaults to `monolith` —
the safest, simplest, most common choice.

## Adding a new style

1. Read `_schema.md` — every style must have the same 6 sections in
   the same order so the build skills can parse them.
2. Copy `monolith.md` → your new style name (e.g. `web3.md`).
3. Edit each section for your architecture style.
4. Add it to the choice list in `scope-of-work/project-brief-template.html`
   Section 3 "Architecture style" field.
5. Test by running `/start-project` and picking your new style.

Profiles are NOT triple-mirrored across `.claude/.cursor/.agent/` — they
live once at the repo root and are read by skills in all three trees.
