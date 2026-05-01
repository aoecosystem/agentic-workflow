# Refine SCOPE.md

**When to use:** `SCOPE.md` is filled but feels rough — you want a senior
review pass before running `parse scope`.

---

## Prompt

```
Read SCOPE.md end to end.

Act as a senior product architect. Produce a refinement report covering:

1. **Clarity** — sentences or sections that are vague, ambiguous, or
   open to multiple interpretations. Quote them and propose tighter
   wording.
2. **Completeness** — missing detail that would force the Builder to
   guess. Specifically check: auth boundary, error contract, NFRs,
   feature dependencies, deployment target.
3. **Consistency** — places where Section 2 (Architecture) contradicts
   Section 3 (Tech Stack), or where a feature in Section 5 implies a
   stack choice not declared in Section 3.
4. **Feature shape** — features that are too coarse (one block doing
   five things) or too fine (one feature for what's really three lines
   in another feature).
5. **Out-of-scope hygiene** — things implied by features that should
   be moved to Section 6 to prevent scope creep.

Return a punch list of ≤ 12 items, each:
  - file:line reference (or section name)
  - issue
  - proposed fix (concrete wording, not "consider revising")

Do not edit SCOPE.md. Just produce the report. I'll apply the changes
myself.
```

## Tips

- Run this **before** `parse scope`. After tasks exist, scope changes
  must go through `delta scope`.
- Use the punch-list output to guide your edits, then re-run this prompt
  for a second pass if the first surfaced major gaps.
