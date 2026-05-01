---
name: review-infrastructure
description: Iterative section-by-section editor for the Infrastructure Diagram. Reads `state/SESSION-STATE.md`, refuses unless Stage is INFRASTRUCTURE_DRAFT, INFRASTRUCTURE_APPROVED, or COMPLETE, lets the user pick one of the 9 sections, applies the change, bumps version, writes audit log. If Stage is INFRASTRUCTURE_APPROVED or COMPLETE, this re-opens to INFRASTRUCTURE_DRAFT. Trigger on "/review-infrastructure", "review infrastructure", "edit infrastructure".
---

# Skill: review-infrastructure

**Trigger:** `/review-infrastructure <section>` or "edit infrastructure"

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


## Stage gate

1. Read `SESSION-STATE.md`.
2. If `Stage` is not `INFRASTRUCTURE_DRAFT`, `INFRASTRUCTURE_APPROVED`,
   or `COMPLETE`, refuse.
3. If `INFRASTRUCTURE_APPROVED` or `COMPLETE`, warn re-open:
   > "Infrastructure is currently approved (or project is COMPLETE).
   > Reviewing will re-open it (→ INFRASTRUCTURE_DRAFT). The project
   > will leave COMPLETE state. Continue? (yes / no)"

---

## Pre-flight

1. Read `deliverables/infrastructure/<slug>-infrastructure.html`.

---

## Show section menu

```
Which section do you want to edit?

   1. Environments
   2. Hosting & Compute
   3. Database, Storage & Cache
   4. Network & Domains
   5. External Services & Integrations
   6. Security & Secrets
   7. Backup & Disaster Recovery
   8. CI / CD Pipeline
   9. Topology — Visual Diagram

Reply with a number (1-9) or section name.
```

Skip menu if user passed a section number.

---

## Edit one section

1. Read current content; show inline.
2. Ask what to change.
3. Apply in memory; preserve CSS classes.
4. Show diff summary.
5. Ask to save.

For Section 9 (Mermaid topology): if the user adds an integration in
Section 5, offer to add a node in the topology block to match.

---

## Save and update state

1. Write updated HTML.
2. Bump version (`v1.0` → `v1.1`).
3. Update `SESSION-STATE.md`:
   - `Stage:` → `INFRASTRUCTURE_DRAFT`
   - `Last skill:` → `review-infrastructure`
   - `Last update:` → ISO timestamp
4. Append audit log:
   ```
   <ISO>  review-infrastructure  <FROM> → INFRASTRUCTURE_DRAFT  section <N> revised, v<X> → v<Y>
   ```

---

## Loop or hand off

```
Edit another section? (number 1-9 or name)

Or move on:
   /approve-infrastructure   Final approval — moves project to COMPLETE.
   exit                      Finish review.
```

Never auto-trigger.

---

## Rules

- Templates read-only.
- One section per edit.
- Mermaid `flowchart` must remain valid after Section 9 edits.
