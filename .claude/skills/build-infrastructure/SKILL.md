---
name: build-infrastructure
description: Generate the Infrastructure Diagram HTML from the approved Database + Architecture + SoW. Reads `state/SESSION-STATE.md` and refuses unless `Stage: DATABASE_APPROVED`. Reads `deliverables/scope-of-work/<slug>-sow.html` (especially Phase 6 Tech Stack and Phase 9 Folder Structures) plus brief Section 8 Integrations, then writes `deliverables/infrastructure/<slug>-infrastructure.html` and transitions Stage to INFRASTRUCTURE_DRAFT. Trigger on "/build-infrastructure", "build infrastructure", "generate infrastructure diagram".
---

# Skill: build-infrastructure

**Trigger:** `/build-infrastructure`

**Purpose:** Read approved SoW + Architecture + Database, draft the
Infrastructure Diagram HTML matching the canonical 9-section
structure, save it under
`deliverables/infrastructure/<slug>-infrastructure.html`, transition
Stage to `INFRASTRUCTURE_DRAFT`.

---

## Manual-edit detection (RUN FIRST — before everything else)

Before any file operation, run the **Manual Edit Protocol** defined in
`AGENTS.md`. Briefly:

1. Compute SHA-256 of every artifact this skill will read.
2. Compare to the stored hash in `SESSION-STATE.md` Artifacts list.
3. If hashes differ, halt and ask the user to:
   - Accept (bump version, append `manual-edit` audit log line, then proceed)
   - Show diff first
   - Cancel (exit immediately)
4. Only after drift is resolved (or no drift exists), continue with the
   stage gate and the rest of this skill.

Stage does NOT change on a manual-edit accept — it stays where it was.

---


## Stage gate (BLOCKING)

1. Read `SESSION-STATE.md`. Locate `Stage:` and `Slug:`.
2. If `Stage` is not `DATABASE_APPROVED`:
   > "Building infrastructure requires `Stage: DATABASE_APPROVED`.
   > Current: `<STAGE>`. Run `/approve-database` first."
3. If file already exists, warn before overwriting.

---

## Architecture style awareness (READ THIS BEFORE GENERATING)

The brief Section 3.2 contains an "Architecture style" choice (one of:
`monolith` | `hybrid` | `microservices` | `polyglot-microservices` | `serverless`). Before
generating output, this skill MUST:

1. Read the brief Section 3.2 to find the chosen style.
2. Read `deliverables/architecture/styles/<style>.md` end-to-end.
3. Apply the style's rules to the generated output in the relevant
   phases / sections (see "Style application points" below).

If the brief has no architecture style set (legacy briefs from before
this feature), default to `monolith` and add a TBD note in the SoW
Phase 1.5 saying "Architecture style was not specified in the brief —
defaulted to monolith. Run /review-brief 3 to set explicitly."

### Style application points (skill-specific)

- **Section 2 Hosting & Compute:** apply style's "Default tech additions" — providers come pre-loaded based on style.
- **Section 3 Database, Storage & Cache:** style dictates whether to show one DB row (monolith/hybrid) or N DB rows (microservices, one per service).
- **Section 5 External Services & Integrations:** style auto-adds Kafka, Redis, gateway entries for microservices/serverless (these become required rows, not TBD).
- **Section 9 Topology — Visual Diagram:** style's "Mermaid diagram patterns → Infrastructure diagram" convention. Microservices topology has gateway + service mesh + Kafka cluster nodes; monolith has one box per layer.

### Universal rule

The style is the **single source of truth** for architecture-specific
output. Do NOT duplicate style content inside this skill. Always
re-read the style file at runtime so changes to the style flow
through automatically.

---

---

## Pre-flight

1. Read `deliverables/scope-of-work/<slug>-sow.html`. Extract:
   - Phase 6 Tech Stack — Frontend, Backend, Database, Integrations,
     Infrastructure rows.
   - Phase 8 Development Approach — environments table.
   - Phase 9 Folder Structures + GitHub Actions stubs.
   - Phase 10.7 Non-Functional Requirements (security, observability).
2. Read `<slug>-project-brief.html` Section 8 (Integrations) and
   Section 11 (Domain).
3. Read `<slug>-system-architecture.html` for service list.
4. Read `<slug>-database-diagram.html` for storage type (Postgres, etc.)
5. Read `deliverables/infrastructure/template.html` for template.

---

## Generation rules

### 1. Environments
- Local, Development, Staging, Production rows minimum.
- Each row: URL pattern (use brief domain), DB name, purpose.
- More environments only if SoW Phase 8 listed them.

### 2. Hosting & Compute
- Web Frontend, Backend API, Mobile build distribution, Background
  Workers — pull providers from SoW Phase 6 Infrastructure.

### 3. Database, Storage & Cache
- Primary DB engine + provider (from SoW Phase 6).
- Object storage provider (from brief Section 8).
- Cache provider.
- Search provider if applicable.

### 4. Network & Domains
- Apex domain + subdomain plan from brief Section 11.
- DNS provider, CDN, SSL strategy.
- Rate limiting / DDoS protection.

### 5. External Services & Integrations
- One row per integration from brief Section 8 (payment, SMS, email,
  maps, video, analytics, error tracking).
- Provider, purpose, auth method (API key / webhook secret / OAuth).

### 6. Security & Secrets
- Secret manager (Vault, Doppler, AWS Secrets Manager, env files).
- Rotation policy.
- IAM strategy.
- TLS / encryption at rest.

### 7. Backup & Disaster Recovery
- DB backup frequency + retention.
- Object storage versioning.
- RTO / RPO targets.
- Restore procedure.

### 8. CI / CD Pipeline
- Universal pipeline rules from template.
- Branch protection rules.
- Rollback strategy.
- Deploy gates.

### 9. Topology — Visual Diagram
- Mermaid `flowchart TB` block.
- Subgraphs: Client, Edge/CDN, Compute, Data Layer, External Services.
- Service nodes use `&nbsp;` padding and layer `classDef` colors
  (matching the template's existing palette).
- Solid arrows for sync; dashed (`-.->`) with `linkStyle` orange for
  webhooks / async events.
- Mermaid must compile.

---

## HTML fidelity

- Preserve every CSS class from the template.
- Cover-sub replaced with the project name.
- Keep print toolbar at bottom-center.
- Mark unknowns as `TBD`.

---

## Show draft + save

Summary line: provider count per layer, integrations covered,
environments listed.

List `TBD` items.

Ask: *"Ready to save?"* Iterate until `save`.

On save:

1. Write `deliverables/infrastructure/<slug>-infrastructure.html` v1.0.
2. Update `SESSION-STATE.md`:
   - `Stage:` → `INFRASTRUCTURE_DRAFT`
   - `Last skill:` → `build-infrastructure`
   - `Last update:` → ISO timestamp
   - `Resume hint:` → `Run /review-infrastructure or /approve-infrastructure.`
   - Artifacts: mark infrastructure as draft v1.0.
3. Append audit log:
   ```
   <ISO>  build-infrastructure  DATABASE_APPROVED → INFRASTRUCTURE_DRAFT  wrote <slug>-infrastructure-diagram.html v1.0
   ```

---

## Hand off

```
Saved: deliverables/infrastructure/<slug>-infrastructure.html (v1.0)

What's next?

  /review-infrastructure       Edit a specific section.
  /approve-infrastructure      Run quality gate. This is the FINAL approval.
                               Approving moves the project to COMPLETE.
```

Stop. Do NOT auto-trigger.

---

## Rules

- Templates read-only.
- Mermaid `flowchart` must compile.
- Every brief Section 8 integration must appear in Section 5 + topology.
- Mark unknowns as `TBD`.
