---
description: Read uploaded documents from DOCMENTS/ (PDF, Word, HTML, Markdown) and auto-generate all 5 project HTML documents. Alternative to /start-interview when you already have a brief or requirements document.
---

Run the `import-docs` skill.

Check `SESSION-STATE/SESSION-STATE.md` first — if docs already exist,
offer to reimport or use /review-* instead.

Scan `DOCMENTS/` for user-uploaded files (PDF, .docx, .doc, .html, .md).
Ignore the 5 blank templates. If no files found, tell the user to drop
their brief or requirements document into DOCMENTS/ and retry.

Read all files, extract project info, show an extraction summary with
gaps, confirm with user, then auto-generate all 5 HTML documents in
sequence: Brief → Scope of Work → Architecture → Database → Infrastructure.

End result: all 5 documents ready in DOCMENTS/, Stage → DOCS_DRAFT.
