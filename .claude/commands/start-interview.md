---
description: Start the project interview. Ask 13 sections of questions one at a time, then automatically generate all 5 documents. One command — everything ready when done.
---

Run the `start-interview` skill.

Check `MEMEORIES/SESSION-STATE.md` first:
- INIT or missing → start the interview from Section 1
- INTERVIEW → offer to resume or restart
- BRIEF_DRAFT → offer to generate documents or review brief
- DOCS_DRAFT → remind user all documents are ready
- COMPLETE → offer to reset for a new project

Interview flow: ask one question per turn, restate each answer, save
progress to SESSION-STATE.md after every section. After all 13 sections
are confirmed, write the brief and auto-generate all 4 remaining
documents in sequence (SoW → Architecture → Database → Infrastructure).

End result: all 5 HTML files in DOCMENTS/ ready to open in a browser.
